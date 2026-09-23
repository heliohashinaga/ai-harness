# AGENTS.md — Minimal Harness

Goal: complete one Task per session with evidence. See `CONTEXT.md` for terms (Task, Verdict, Skill).

## Loop

1. Read `.factory/tasks/<id>.md` and `docs/workflow.md`.
2. Inspect repo, tests, patterns before editing.
3. Implement minimal diff proving each acceptance criterion.
4. Run `.\scripts\verify.ps1` (ruff + pytest + complexity gate).
5. Inspect `git diff`; leave tree green. All criteria start FAIL — flip only with proof.

## Rules

- Prefer existing abstractions; add no dependency without need.
- Keep changes scoped; repository is the system of record.
- Claim no success without build + test + diff evidence.
- Second agent/planner/memory only per `docs/extending.md` (earn via `evals/` benchmark).

## Pointers

- Why minimal: `docs/philosophy.md`, decision in `docs/adr/0001-minimal-harness-over-fixed-swarm.md`.
- Shape and layout: `docs/architecture.md`.
- Verdict format and metrics: `docs/evaluation.md`.
