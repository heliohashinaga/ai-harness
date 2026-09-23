# TASK-005 — Experiment 004: cleaner retest on frozen buggy outputs

## Goal

Run the pre-registered experiment 004: feed each frozen buggy sample from
`evals/004-protocol.md` to the cleaner (coder output fixed, no coder call),
grade the cleaned code against the same hidden tests, and record the verdict
per the protocol's verdict rule.

## Context

TASK-004 froze 6 buggy triples (B1–B6); the executable copy is `TRIPLES` in
`tests/unit/test_buggy_cases_004.py`. `evals/run_003.py` is the pattern for
the runner (real provider chat, `LANGSMITH_TRACING=false`, results skeleton
to `evals/results/`). Model/provider: explicit `deepseek-v4-flash` via
opencode (the `.env` default returned 503 upstream in 003 — noted, not
changed).

## Acceptance Criteria

- [ ] `evals/run_004.py` invokes the real cleaner node
  (`build_cleaner_node` + provider chat) once per frozen sample, no coder
  call, reusing `TRIPLES` as the single executable copy (no third copy of
  the data).
- [ ] `evals/results/004-cleaner-retest.md` records per-sample
  fixed/still-broken/broke-passing-checks plus latency, and applies the
  pre-registered verdict rule (majority fixed, nothing broken → promote;
  otherwise 003 verdict stands).
- [ ] `.\scripts\verify.ps1` passes (ruff + pytest); no new dependency.
  Network failures degrade to recorded ERRORs, never to a fake verdict.

## Constraints

- Do not edit `evals/004-protocol.md`, the frozen triples, or the 003
  hidden tests.
- Follow `run_003.py` structure (env guard, `extract`, per-case run,
  results file). Minimal diff.
