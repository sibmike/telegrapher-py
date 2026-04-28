"""Phase 4 tests: ConversationCompactor — eviction ladder, accessors, ratio."""
from __future__ import annotations

from pathlib import Path

import pytest

from telegrapher import Telegrapher
from telegrapher.memory import ConversationCompactor, Message


@pytest.fixture
def tg(tmp_path: Path) -> Telegrapher:
    """Real Telegrapher backed by a MockRunner.

    `compress` returns a TE form that is shorter (fewer characters → fewer
    tokens) than the input, so eviction actually reduces the token count.
    """
    from telegrapher.core.backends.local import LocalBackend
    from telegrapher.core.backends.runners.mock import MockRunner
    from telegrapher.core.cache import DiskCache

    class ShrinkingRunner(MockRunner):
        """Returns a deterministic shorter string for any compress prompt,
        and a longer (NL-like) string for any expand prompt."""

        def generate(self, prompt: str, *, max_tokens: int = 2048) -> str:
            self.calls.append(prompt)
            if prompt.startswith("<TE_COMPRESS"):
                # Strip header/footer + drop ~70% of the body.
                body = prompt.split("\n", 1)[1].rsplit("</TE_COMPRESS>", 1)[0].strip()
                return f"TE[{body[: max(1, len(body) // 4)]}]"
            if prompt.startswith("<TE_EXPAND"):
                body = prompt.split("\n", 1)[1].rsplit("</TE_EXPAND>", 1)[0].strip()
                return f"NL[{body}]" + (" filler" * 5)  # simulate decompression
            return ""

    runner = ShrinkingRunner()
    t = Telegrapher.__new__(Telegrapher)
    t._backend = LocalBackend.from_runners(bidi=runner)
    t._cache_compress = DiskCache(root=tmp_path, namespace="compress", model_revision="t")
    t._cache_expand = DiskCache(root=tmp_path, namespace="expand", model_revision="t")
    return t


# -- construction --------------------------------------------------------------


def test_invalid_level_raises(tg: Telegrapher) -> None:
    with pytest.raises(ValueError):
        ConversationCompactor(level="L99", telegrapher=tg)


def test_nonpositive_max_tokens_raises(tg: Telegrapher) -> None:
    with pytest.raises(ValueError):
        ConversationCompactor(max_tokens=0, telegrapher=tg)
    with pytest.raises(ValueError):
        ConversationCompactor(max_tokens=-1, telegrapher=tg)


# -- happy-path no eviction ----------------------------------------------------


def test_under_budget_messages_remain_uncompressed(tg: Telegrapher) -> None:
    m = ConversationCompactor(max_tokens=10_000, telegrapher=tg)
    m.add_user_message("hello world")
    m.add_ai_message("hi there")
    msgs = m.messages()
    assert all(not msg.is_compressed for msg in msgs)
    assert [msg.role for msg in msgs] == ["user", "ai"]


# -- eviction pass 1 (compress oldest NL) -------------------------------------


def test_overflow_compresses_oldest_nl(tg: Telegrapher) -> None:
    long_passage = "word " * 500  # ~500 tokens
    m = ConversationCompactor(max_tokens=200, telegrapher=tg, level="L3")
    m.add_user_message(long_passage)
    msgs = m.messages()
    assert len(msgs) == 1
    assert msgs[0].is_compressed is True
    assert msgs[0].compression_level == "L3"


def test_eviction_processes_oldest_first(tg: Telegrapher) -> None:
    m = ConversationCompactor(max_tokens=80, telegrapher=tg)
    m.add_user_message("alpha " * 200)  # gets compressed first
    m.add_ai_message("beta " * 1)  # short, should stay NL while budget allows
    msgs = m.messages()
    # Oldest (user) is compressed, newest (ai) is kept as NL when possible.
    assert msgs[0].role == "user"
    assert msgs[0].is_compressed is True


# -- eviction pass 2 (re-compress at next level) ------------------------------


def test_recompress_walks_level_ladder(tg: Telegrapher) -> None:
    """Once everything is at L1, the ladder steps to L3 then L5.

    Budget chosen so that compressing once to L1 isn't enough but messages
    survive at higher levels — i.e., the ladder fires before pass 3 drops.
    """
    m = ConversationCompactor(max_tokens=80, telegrapher=tg, level="L1")
    for _ in range(5):
        m.add_user_message("payload " * 200)
    levels = [msg.compression_level for msg in m.messages() if msg.is_compressed]
    # Some message somewhere has been pushed beyond L1.
    assert any(level in ("L3", "L5") for level in levels)


# -- eviction pass 3 (drop oldest) --------------------------------------------


def test_buffer_drops_oldest_when_everything_at_max_level(tg: Telegrapher) -> None:
    """Even at L5 the budget may be unattainable for arbitrary inputs.

    The compactor must not loop forever — it drops the oldest turn when no
    further compression is possible.
    """
    m = ConversationCompactor(max_tokens=2, telegrapher=tg, level="L5")
    for i in range(8):
        m.add_user_message(f"msg-{i} " + ("x " * 50))
    # The buffer must have shrunk — at least one message dropped.
    assert len(m.messages()) < 8


# -- accessors -----------------------------------------------------------------


def test_token_count_decreases_after_eviction(tg: Telegrapher) -> None:
    m = ConversationCompactor(max_tokens=100, telegrapher=tg)
    m.add_user_message("word " * 500)
    assert m.token_count() <= 100


def test_compression_ratio_above_one_after_eviction(tg: Telegrapher) -> None:
    m = ConversationCompactor(max_tokens=80, telegrapher=tg)
    m.add_user_message("word " * 500)
    assert m.compression_ratio() > 1.0


def test_compression_ratio_one_when_empty(tg: Telegrapher) -> None:
    m = ConversationCompactor(max_tokens=4000, telegrapher=tg)
    assert m.compression_ratio() == 1.0


def test_compression_ratio_one_when_no_compression(tg: Telegrapher) -> None:
    m = ConversationCompactor(max_tokens=10_000, telegrapher=tg)
    m.add_user_message("hello")
    assert m.compression_ratio() == pytest.approx(1.0)


def test_clear_empties_buffer(tg: Telegrapher) -> None:
    m = ConversationCompactor(max_tokens=4000, telegrapher=tg)
    m.add_user_message("hello")
    m.add_ai_message("hi")
    m.clear()
    assert m.messages() == []
    assert m.token_count() == 0


# -- expand_on_load -----------------------------------------------------------


def test_expand_on_load_decodes_compressed_turns(tg: Telegrapher) -> None:
    m = ConversationCompactor(max_tokens=80, telegrapher=tg, expand_on_load=True)
    m.add_user_message("payload " * 500)
    msgs = m.messages()
    # Returned messages are NL even though the underlying buffer is TE.
    assert all(not msg.is_compressed for msg in msgs)
    # And the underlying buffer is unchanged (still compressed).
    assert any(internal.is_compressed for internal in m._messages)


def test_expand_on_load_off_returns_te(tg: Telegrapher) -> None:
    m = ConversationCompactor(max_tokens=80, telegrapher=tg, expand_on_load=False)
    m.add_user_message("payload " * 500)
    msgs = m.messages()
    assert any(msg.is_compressed for msg in msgs)


def test_messages_return_value_is_a_copy(tg: Telegrapher) -> None:
    m = ConversationCompactor(max_tokens=4000, telegrapher=tg)
    m.add_user_message("hello")
    snapshot = m.messages()
    snapshot.clear()
    assert len(m.messages()) == 1


# -- type -----------------------------------------------------------------------


def test_message_dataclass_defaults() -> None:
    msg = Message(role="user", content="hi")
    assert msg.is_compressed is False
    assert msg.compression_level is None
