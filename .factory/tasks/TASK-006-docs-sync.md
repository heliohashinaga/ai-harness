# TASK-006 — Sync system-of-record docs after experiments 004/005

## Goal

Bring `README.md` and `evals/benchmark.md` back in line with measured
reality after TASK-004 (frozen buggy set), TASK-005 (experiment 004), and
the cleaner credential fix.

## Context

Stale spots (measured evidence exists, docs disagree):
- `README.md` evidence table: 001 row claims "72 passed" (measured 65 at
  the time; suite has since grown to 83); no 004 row.
- `evals/benchmark.md` queue: 002 entry still says "blocked: no key"
  (measured 2026-09-22/23: 4/4, first-attempt 50%); no 004 entry.

## Acceptance Criteria

- [ ] `README.md` evidence table: 001 row states the measured 65 passed;
  new 004 row states 0/6 fixed, 2 regressions (B2), 003 verdict stands.
- [ ] `evals/benchmark.md` queue: 002 entry states measured outcome; new
  004 entry states retest outcome and rule applied; no "blocked" claim
  remains for completed work.
- [ ] No other numbers/claims touched; `.\scripts\verify.ps1` passes
  (docs-only change: ruff + pytest green); no new dependency.

## Constraints

- Numbers must match the results files verbatim
  (`evals/results/001-baseline.md` … `004-cleaner-retest.md`).
- Minimal diff; no unrelated rewrites.
