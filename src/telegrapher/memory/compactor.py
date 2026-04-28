"""ConversationCompactor — TE-backed buffered memory with an eviction ladder.

Behavior contract (PS-001):

- New turns enter as natural-language `Message`s.
- While total token count stays below `max_tokens`, nothing else happens.
- On overflow, the eviction loop runs in three passes, in order:
    1. Compress the oldest *uncompressed* turn to TE at the configured level.
    2. If everything is already compressed, re-compress the oldest TE turn at
       the next-higher level (L1 → L3 → L5).
    3. If everything is already at L5, drop the oldest turn.
- The loop repeats until total tokens <= `max_tokens` or the buffer is empty.

`messages()` returns the current buffer; if `expand_on_load=True`, compressed
turns are decoded back to natural language on the way out.
"""
from __future__ import annotations

from telegrapher import Telegrapher
from telegrapher.core.config import validate_level
from telegrapher.core.metrics import count_tokens
from telegrapher.memory.types import Message

_LEVEL_LADDER: dict[str, str | None] = {"L1": "L3", "L3": "L5", "L5": None}

_default_telegrapher: Telegrapher | None = None


def _get_default_telegrapher() -> Telegrapher:
    """Lazy-cached default Telegrapher.

    Created on first use so multiple `ConversationCompactor()` instances
    that don't supply their own `telegrapher=` argument all share one
    backend (and therefore one model load) within a process.
    """
    global _default_telegrapher
    if _default_telegrapher is None:
        _default_telegrapher = Telegrapher()
    return _default_telegrapher


class ConversationCompactor:
    """Token-budgeted conversation memory backed by Telegraph English."""

    def __init__(
        self,
        *,
        level: str = "L3",
        max_tokens: int = 4000,
        expand_on_load: bool = False,
        telegrapher: Telegrapher | None = None,
    ) -> None:
        """
        Args:
            level: Initial compression level applied to evicted NL turns.
            max_tokens: Token budget. Buffer is trimmed below this on every add.
            expand_on_load: If True, `messages()` decodes TE turns back to NL
                before returning. Default False (callers handing the buffer to
                a TE-aware model save tokens by leaving turns compressed).
            telegrapher: Backend used for compress/expand. If omitted, a
                lazy-cached default Telegrapher is shared across instances.
        """
        validate_level(level)
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive.")
        self._level = level
        self._max_tokens = max_tokens
        self._expand_on_load = expand_on_load
        self._tg = telegrapher  # lazy: only resolved when actually compressing
        self._messages: list[Message] = []

    # -- mutations ----------------------------------------------------------

    def add_user_message(self, content: str) -> None:
        self._add(Message(role="user", content=content))

    def add_ai_message(self, content: str) -> None:
        self._add(Message(role="ai", content=content))

    def add_system_message(self, content: str) -> None:
        self._add(Message(role="system", content=content))

    def _add(self, message: Message) -> None:
        self._messages.append(message)
        self._evict_until_under_budget()

    def clear(self) -> None:
        self._messages.clear()

    # -- accessors ----------------------------------------------------------

    def messages(self) -> list[Message]:
        """Return a copy of the current buffer.

        If `expand_on_load=True`, compressed turns are decoded back to NL
        before being returned. The buffer itself is not mutated.
        """
        if not self._expand_on_load:
            return list(self._messages)
        out: list[Message] = []
        for m in self._messages:
            if m.is_compressed:
                out.append(
                    Message(
                        role=m.role,
                        content=self._telegrapher().expand(m.content),
                        is_compressed=False,
                        compression_level=None,
                    )
                )
            else:
                out.append(m)
        return out

    def token_count(self) -> int:
        """Tokens currently held in the buffer (using the metrics encoder)."""
        return sum(count_tokens(m.content) for m in self._messages)

    def compression_ratio(self) -> float:
        """Ratio of original tokens to current buffer tokens.

        For uncompressed messages the contribution to numerator and denominator
        is equal — they cancel out. Returns 1.0 when nothing has been
        compressed yet, > 1.0 once eviction has done work.
        """
        current = self.token_count()
        if current == 0:
            return 1.0
        original = sum(self._original_tokens(m) for m in self._messages)
        return original / current

    def _original_tokens(self, m: Message) -> int:
        if not m.is_compressed:
            return count_tokens(m.content)
        return count_tokens(self._telegrapher().expand(m.content))

    # -- eviction -----------------------------------------------------------

    def _telegrapher(self) -> Telegrapher:
        if self._tg is None:
            self._tg = _get_default_telegrapher()
        return self._tg

    def _evict_until_under_budget(self) -> None:
        while self._messages and self.token_count() > self._max_tokens:
            if self._compress_oldest_nl():
                continue
            if self._recompress_oldest_te():
                continue
            # Pass 3: drop the oldest message.
            self._messages.pop(0)

    def _compress_oldest_nl(self) -> bool:
        for m in self._messages:
            if not m.is_compressed:
                m.content = self._telegrapher().compress(m.content, level=self._level)
                m.is_compressed = True
                m.compression_level = self._level
                return True
        return False

    def _recompress_oldest_te(self) -> bool:
        for m in self._messages:
            if m.is_compressed:
                next_level = _LEVEL_LADDER.get(m.compression_level or "L1")
                if next_level is None:
                    continue
                tg = self._telegrapher()
                m.content = tg.compress(tg.expand(m.content), level=next_level)
                m.compression_level = next_level
                return True
        return False
