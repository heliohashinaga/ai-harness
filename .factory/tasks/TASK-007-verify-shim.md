# TASK-007 — Harden verify.ps1 against broken console-script shims

## Goal

Make `.\scripts\verify.ps1` pass deterministically again. `uv run pytest`
fails with `uv trampoline failed to canonicalize script path` because the
local `.venv/Scripts/pytest.exe` shim is a corrupt trampoline (a reinstall
regenerates a working one, but the gate must not depend on shim health).

## Context

- `scripts/verify.ps1`: `uv run ruff check .` (works — `ruff.exe` is a real
  26 MB binary) + `uv run pytest -q` (broken — `pytest.exe` is a 47 KB uv
  trampoline that fails even when invoked directly).
- Proven: `uv run python -m pytest -q` passes (83 passed, 2 deselected) —
  `python -m` bypasses console-script shims entirely.

## Acceptance Criteria

- [ ] `.\scripts\verify.ps1` runs green end-to-end with no manual
  `.venv` repair.
- [ ] The pytest step no longer depends on the `pytest.exe` shim
  (e.g. module invocation).
- [ ] Ruff step behavior unchanged; no new dependency.

## Constraints

- Minimal diff to `scripts/verify.ps1`; no unrelated rewrites.
