"""Abstract base classes for the backend layer.

`Backend` defines the verb-level interface (`compress`, `expand`,
`stream_compress`). `Runner` is the protocol concrete runners implement —
a thin `prompt -> text` adapter that knows nothing about TE or directions.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Protocol, runtime_checkable


class InstallError(RuntimeError):
    """Raised when the requested runner's optional dependency is not installed."""


@runtime_checkable
class Runner(Protocol):
    """Minimal `prompt -> text` adapter implemented by VLLMRunner, LlamaCppRunner, etc."""

    def generate(self, prompt: str, *, max_tokens: int = 2048) -> str:
        """Return the model's completion for `prompt`."""
        ...

    def stream(self, prompt: str, *, max_tokens: int = 2048) -> Iterator[str]:
        """Yield completion tokens (or chunks) as the model emits them."""
        ...

    def close(self) -> None:
        """Release model handles and free GPU/CPU resources."""
        ...


class Backend(ABC):
    """Direction-aware compression interface."""

    @abstractmethod
    def compress(self, text: str, *, level: str) -> str:
        """Compress natural-language `text` into Telegraph English at `level`."""

    @abstractmethod
    def expand(self, te: str) -> str:
        """Expand Telegraph English `te` back into natural language."""

    @abstractmethod
    def stream_compress(self, text: str, *, level: str) -> Iterator[str]:
        """Yield TE atomic lines as the model emits them.

        Implementations must guarantee complete-line output — no half-lines.
        """

    def close(self) -> None:
        """Release backend-owned resources. Default is a no-op."""
        return None
