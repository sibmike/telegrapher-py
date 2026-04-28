"""Backend layer — direction routing (`Backend`) over execution (`Runner`).

See [DD-001](../../../../docs/design-docs/dd-001-backend-abstraction.md) for the
architecture. Public exports here are deliberately narrow: callers ask
`get_backend(...)` for a `Backend` and never touch concrete subclasses.
"""
from telegrapher.core.backends.base import Backend, InstallError, Runner
from telegrapher.core.backends.factory import get_backend
from telegrapher.core.backends.local import LocalBackend

__all__ = [
    "Backend",
    "InstallError",
    "LocalBackend",
    "Runner",
    "get_backend",
]
