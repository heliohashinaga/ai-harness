# TASK-004 — Pre-registered buggy-output set for cleaner retest

## Goal

Experiment 003 rejected the cleaner as default because the coder went 3/3 —
there was nothing to fix. Unblock experiment 004 with a frozen set of buggy
coder outputs (each failing ≥1 hidden test) that a cleaner retest can run
against.

## Context

`evals/003-protocol.md` froze prompts P1–P3 (fib, dedup, chunks) with hidden
tests; `evals/run_003.py` holds the executable copy (`PROMPTS`/`CHECKS`) and
the `grade()` helper. Mirror that split: the protocol md is the human record,
frozen constants in code are the executable copy. Reuse the 003 hidden tests
verbatim — do not edit them to favor any candidate.

## Acceptance Criteria

- [ ] `evals/004-protocol.md` defines N≥5 frozen (task, buggy-code,
  hidden-tests) triples, each documenting which hidden check the buggy code
  fails.
- [ ] Each buggy sample is a frozen constant (no LLM in the loop); a unit
  test execs each sample and proves it fails ≥1 of its hidden checks.
- [ ] The hidden-test sets are proven satisfiable (a reference solution
  passes each set fully).
- [ ] `.\scripts\verify.ps1` passes; no new dependency.

## Constraints

- Follow the 003 split (protocol md ↔ executable constants) and the
  `grade()` exec/eval style in `evals/run_003.py`.
- Minimal diff; no unrelated rewrites.
