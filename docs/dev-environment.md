# Development Environment

> Machine-specific paths, commands, and safety rules for working on the `telegrapher` package locally.

**When to update this file:** After changing the venv path, adding new dev commands, changing test counts, or discovering a new pitfall.

---

## Environment Setup

**Project root:** `C:\Users\mikea\SCRIPTS\telegrapher_py`

| Component | Location | Purpose |
|-----------|----------|---------|
| Python venv | `C:\Users\mikea\SCRIPTS\telegrapher_py\.venv` (Python 3.12.4 from conda base) | Package, tests, lint, type checking |
| Bootstrapping interpreter | `C:\Users\mikea\anaconda3\python.exe` | Used to create `.venv` only |
| Model cache | `~/.cache/telegrapher/` (default) | Downloaded HF Hub weights, compress/expand caches |

---

## Common Commands (exact copy-paste)

```bash
# Run the full test suite
"C:/Users/mikea/SCRIPTS/telegrapher_py/.venv/Scripts/python.exe" -m pytest tests/ -v

# Run tests with coverage
"C:/Users/mikea/SCRIPTS/telegrapher_py/.venv/Scripts/python.exe" -m pytest tests/ --cov=src/telegrapher --cov-report=term-missing

# Run a single test file
"C:/Users/mikea/SCRIPTS/telegrapher_py/.venv/Scripts/python.exe" -m pytest tests/test_<module>.py -v

# Lint
"C:/Users/mikea/SCRIPTS/telegrapher_py/.venv/Scripts/python.exe" -m ruff check src/ tests/

# Format
"C:/Users/mikea/SCRIPTS/telegrapher_py/.venv/Scripts/python.exe" -m ruff format src/ tests/

# Type check
"C:/Users/mikea/SCRIPTS/telegrapher_py/.venv/Scripts/python.exe" -m mypy src/telegrapher

# Build the wheel (release)
"C:/Users/mikea/SCRIPTS/telegrapher_py/.venv/Scripts/python.exe" -m build

# CLI entry point (after editable install)
"C:/Users/mikea/SCRIPTS/telegrapher_py/.venv/Scripts/tg.exe" --help
"C:/Users/mikea/SCRIPTS/telegrapher_py/.venv/Scripts/tg.exe" compress sample.txt --level L3
```

## Initial Setup (already done — record kept for reproduction)

```powershell
& "C:\Users\mikea\anaconda3\python.exe" -m venv "C:\Users\mikea\SCRIPTS\telegrapher_py\.venv"
& "C:\Users\mikea\SCRIPTS\telegrapher_py\.venv\Scripts\python.exe" -m pip install --upgrade pip
& "C:\Users\mikea\SCRIPTS\telegrapher_py\.venv\Scripts\python.exe" -m pip install -e "C:\Users\mikea\SCRIPTS\telegrapher_py[dev]"
```

---

## Bash Command Safety

Every bash command request should be accompanied by an exact explanation of what the command is doing and what it is attempting to accomplish. Every bash command should be reviewed to make sure it does no harm.

---

## Known Pitfalls

- Running `python -m pytest` without the full venv path triggers the Windows Store alias on this machine — always use the absolute venv path.
- (Add new pitfalls here as they're discovered.)

---

## Git Worktrees

Claude Code may create git worktrees at `.claude/worktrees/<name>/`. These are isolated copies of the repo — useful for parallel exploration without touching the main working tree.

**Key rule when running in a worktree:**
- Tests can run from a Python worktree because the venv resolves packages by import path, not by working directory. Use the same absolute venv path as above; just `cd` into the worktree first.
