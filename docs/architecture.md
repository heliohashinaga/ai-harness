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
| **Agent Session** | `agents/agent.md` + `src/agentcrew/` tools | Single model, repo tools (`rg`, `git`, `pytest`, `ruff`). No roles. |
| **Evaluator** | `agents/evaluator.md` + `scripts/verify` | Build, tests, lint, diff, acceptance checklist. Read-only, fresh context. |
| **State** | `.factory/state/current.md` + git | Task id, status, last Verdict. Git is the memory. |

## What does NOT exist at V1

Coordinator, planner, swarm, message bus, LangGraph pipeline, vector DB, Redis/Postgres, memory server. The current `START → coder → cleaner → END` graph is demoted to an experiment, not the backbone.

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
