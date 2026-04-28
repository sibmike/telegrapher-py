"""Message data type used by `ConversationCompactor`."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Role = Literal["user", "ai", "system"]


@dataclass
class Message:
    """A single conversation turn.

    `is_compressed` is True when `content` is Telegraph English. In that case
    `compression_level` records which level (L1/L3/L5) was used so the
    eviction ladder can step up to the next level when more room is needed.
    """

    role: Role
    content: str
    is_compressed: bool = False
    compression_level: str | None = None
