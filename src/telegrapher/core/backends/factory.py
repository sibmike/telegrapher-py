"""Factory that resolves user model arguments into a `Backend` instance.

Picks a runner based on (a) explicit user request, (b) installed extras,
(c) host environment. See DD-001 for the resolution order.
"""
from __future__ import annotations

from telegrapher.core.backends.base import Backend, InstallError, Runner
from telegrapher.core.backends.local import LocalBackend
from telegrapher.core.backends.runners.mock import MockRunner
from telegrapher.core.config import DEFAULT_MODEL


def _make_runner(model: str, *, runner: str | None) -> Runner:
    """Instantiate a Runner for `model` using the requested or auto-picked backend.

    `runner` accepts: "mock", "vllm", "llama-cpp", or None for auto-pick.
    """
    if runner == "mock":
        # Tests inject their own MockRunner instances directly via
        # `LocalBackend.from_runners(...)`. This branch exists for parity and
        # is rarely the right entry point; it returns an empty MockRunner.
        return MockRunner(identity=f"mock:{model}")

    if runner == "vllm":
        return _load_vllm_runner(model)

    if runner == "llama-cpp":
        return _load_llama_cpp_runner(model)

    if runner is not None:
        raise ValueError(
            f"Unknown runner {runner!r}. Use 'vllm', 'llama-cpp', 'mock', or None."
        )

    # Auto-pick: prefer GPU (vllm) when available, fall back to llama.cpp.
    try:
        return _load_vllm_runner(model)
    except InstallError:
        pass
    try:
        return _load_llama_cpp_runner(model)
    except InstallError:
        pass
    raise InstallError(
        "No runner available. Install one of: "
        "`pip install telegrapher[gpu]` (CUDA + vLLM) or "
        "`pip install telegrapher[cpu]` (llama.cpp / GGUF)."
    )


def _load_vllm_runner(model: str) -> Runner:
    """Load the VLLMRunner. Phase 6 — currently raises `InstallError`."""
    raise InstallError(
        "VLLMRunner is not yet implemented. Will arrive in v0.1 Phase 6 once "
        "fine-tuned weights are available. For now use `runner='mock'` (tests) "
        "or pass an explicit `Runner` instance to `LocalBackend.from_runners`."
    )


def _load_llama_cpp_runner(model: str) -> Runner:
    """Load the LlamaCppRunner. Phase 6 — currently raises `InstallError`."""
    raise InstallError(
        "LlamaCppRunner is not yet implemented. Will arrive in v0.1 Phase 6 once "
        "fine-tuned weights are available. For now use `runner='mock'` (tests) "
        "or pass an explicit `Runner` instance to `LocalBackend.from_runners`."
    )


def get_backend(
    *,
    model: str | None = None,
    model_in: str | None = None,
    model_out: str | None = None,
    runner: str | None = None,
) -> Backend:
    """Resolve user model arguments into a concrete `Backend`.

    Same constructor contract as `Telegrapher`:
    - Pass `model=` for one bidirectional model used both ways.
    - Pass `model_in=` and `model_out=` for two unidirectional models.
    - Pass nothing to use the package default model.

    `runner` overrides auto-detection. Useful for tests (`runner="mock"`).
    """
    if model is not None and (model_in is not None or model_out is not None):
        raise ValueError(
            "`model` and `model_in`/`model_out` are mutually exclusive."
        )
    if (model_in is None) != (model_out is None):
        raise ValueError(
            "When using two unidirectional models, both `model_in` and "
            "`model_out` must be provided."
        )

    if model_in is not None and model_out is not None:
        if model_in == model_out:
            shared = _make_runner(model_in, runner=runner)
            return LocalBackend.from_runners(bidi=shared)
        return LocalBackend.from_runners(
            compressor=_make_runner(model_in, runner=runner),
            expander=_make_runner(model_out, runner=runner),
        )

    chosen = model or DEFAULT_MODEL
    return LocalBackend.from_runners(bidi=_make_runner(chosen, runner=runner))
