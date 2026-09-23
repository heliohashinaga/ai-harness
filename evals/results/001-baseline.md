# 001 — Baseline: deterministic gate (LEVEL 1 floor)

Date: 2026-09-22. Env: Windows, Python 3.14. Re-measured with the canonical
toolchain after `uv` was installed (`uv 0.12.18`): identical result —
ruff green, 64 passed + the same 1 environmental failure.
No Python code was changed for this measurement (docs/skeleton only).

## Measured

| Check | Result |
|---|---|
| `ruff check .` | **PASS** — all checks passed |
| `pytest -q` (unit+contract+quality; integration deselected) | **65 passed**, 2 deselected — gate green |

Fixed 2026-09-22 (first factory task in practice): the subprocess env now
inherits `os.environ` with only the provider keys forced empty, instead of a
hardcoded Unix `PATH`. Hermeticity holds because `load_dotenv` never overrides
vars already present. Result after fix: **65 passed**, gate green.

## Regression floor for experiments

Any candidate (cleaner, planner, swarm) must keep: ruff green and
65 passed. A new failure = regression = reject.

## NOT measured (blocked)

Single-agent task runs on `.factory/tasks/` (LEVEL 0/2 metrics:
`first_attempt_success, retry_rate, tokens, cost, latency`) need a provider
key (`OPENROUTER_API_KEY` or `OPENCODE_GO_API_KEY`) — none is configured in
this shell. Run `.\scripts\run.ps1` + `.\scripts\evaluate.ps1` with a key to
fill `002-baseline-agent-runs.md` before promoting any LEVEL 3+ layer.
