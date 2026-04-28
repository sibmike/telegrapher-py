"""Concrete runner implementations.

`MockRunner` ships in core for testing. `VLLMRunner` and `LlamaCppRunner` are
behind extras and stubbed to raise `InstallError` until Phase 6 fills them in
against real fine-tuned weights.
"""
from telegrapher.core.backends.runners.mock import MockRunner

__all__ = ["MockRunner"]
