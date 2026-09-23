# Benchmark — earning complexity

Baseline is LEVEL 2 (single agent + deterministic evaluator + retry, max 3).

## Task set

Fixed set (frozen for every experiment — do not edit tasks to favor a candidate):

- `TASK-000` — CLI flag (`--dry-run`), feature + test.
- `TASK-001` — bugfix (invalid `--format` rejected), regression test.
- `TASK-002` — refactor (`argparse`, no behavior change), tests unchanged.
- `TASK-003` — small helper (`error_rate`), unit test.

## Procedure

1. Run each task with the baseline; record the metrics below.
2. Run the same tasks with the candidate (e.g. +cleaner, +planner).
3. Promote the candidate only on a clear quality/cost win.

## Metrics per experiment

`task_success, first_attempt_success, retry_rate, human_rate,
regression_rate, tokens_used, cost, latency` → one file per experiment
in `evals/results/`, e.g. `001-baseline.md`.

## Candidates queue

- `001` — deterministic gate, measured 2026-09-22 (ruff green, 65 passed after the Windows subprocess-env fix).
- `002` — single-agent task runs with provider key (blocked: no key in this shell).
- `003` — `coder -> cleaner` pilot: REJECTED as default (3/3 vs 3/3, 2x calls, 3–25x latency). Stays opt-in.
- `004+` — planner, reviewer, swarm only as named experiments (a cleaner retest needs a pre-registered buggy-output set).
