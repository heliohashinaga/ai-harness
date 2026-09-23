# Architecture — Minimal Harness

```text
HUMAN → TASK.md → AGENT SESSION → repository (inspect/edit/test)
                      → EVALUATOR (deterministic → optional LLM, fresh context, read-only)
                      → PASS → DONE | FAIL → feedback → RETRY (max 3) → HUMAN
```

## Components (only 4)

| Concept | Lives in | Notes |
|---|---|---|
| **Task** | `.factory/tasks/<id>.md` | Goal + Acceptance Criteria + Constraints. See `workflow.md`. |
| **Agent Session** | `agents/agent.md` + `src/aicrew/` tools | Single model, repo tools (`rg`, `git`, `pytest`, `ruff`). No roles. |
| **Evaluator** | `agents/evaluator.md` + `scripts/verify.ps1` | Build, tests, lint, diff, acceptance checklist. Read-only, fresh context. |
| **State** | `.factory/state/current.md` (local scratch) + versioned tasks/evaluations | Task id, status, last Verdict. Tasks and Verdicts are the versioned memory; scratch state stays out of git. |

## What does NOT exist at V1

Coordinator, planner, swarm, message bus, vector DB, Redis/Postgres, memory
server. No LangGraph pipeline as the backbone — the `START → coder → cleaner → END`
graph survives only as an opt-in experiment (see `evals/results/003-cleaner-pilot.md`).

## Layout

```text
├── CONTEXT.md
├── agents/agent.md          # coding prompt (short)
├── agents/evaluator.md      # fresh-context judging prompt (read-only)
├── .factory/{config.yaml,tasks/,evaluations/,state/current.md}
├── scripts/{run,verify,evaluate}.ps1
├── docs/{philosophy,architecture,workflow,evaluation,extending}.md
├── docs/adr/
└── evals/{benchmark.md,results/}
```
