# 002 — Baseline: single-agent runs on the frozen task set (LEVEL 2)

Date: 2026-09-22/23. Model: this session as operator + one provider draft
(`deepseek-v4-flash` via OpenCode Go) for TASK-003. Frozen set:
TASK-000, TASK-001, TASK-002, TASK-003. Gate ends at 72 passed, ruff green.

## Per-task

| Task | Attempts | Provider tokens | Latency (model) | Caught by |
|---|---|---|---|---|
| 000 `--dry-run` | 2 | 0 (operator) | — | complexity gate (main 12 > 10) → extracted `_emit_output` |
| 001 invalid `--format` | 1 | 0 (operator) | — | — |
| 002 argparse refactor | 1 | 0 (operator) | — | — (72 passed, zero test edits) |
| 003 `error_rate` | 2 | 2152 (236+1916) | 89 s | unit test (`run_id` kwarg) → fixed without new call |

## Aggregate (the numbers 003+ must beat)

- `task_success`: 4/4 (100%)
- `first_attempt_success`: 2/4 (50%)
- `retry_rate`: 2/4, both resolved by **deterministic feedback alone**
- `regression_rate`: 0 (suite grew 65 → 72, never shrank)
- provider tokens total: 2152; retries cost 0 extra tokens
- cost: OpenCode Go subscription (no per-token meter surfaced in usage payload)

## Reading

Every failure was caught by the cheap evaluator (tests, complexity gate),
never by a second LLM pass. A `cleaner`/`reviewer` layer must therefore show
it catches failures this gate misses — otherwise it is pure tax. That is the
test for experiment 003 (`coder -> cleaner` graph).
