# Workflow

## 1. Write the Task

`.factory/tasks/042-slug.md`:

```md
# TASK-042 — <short goal>

## Goal / Context
...

## Acceptance Criteria
- [ ] observable behavior 1
- [ ] observable behavior 2
- [ ] `.\scripts\verify.ps1` passes, no new dependency

## Constraints
- Follow existing patterns, minimal diff.
```

If acceptance isn't checkable, rewrite the task. That's the job, not more agents.

## 2. Run

```powershell
.\scripts\run.ps1 .factory/tasks/042-slug.md        # agent inspects → edits → tests
.\scripts\verify.ps1                                 # deterministic gate
.\scripts\evaluate.ps1 .factory/tasks/042-slug.md    # verdict + feedback
```

Commit at checkpoints (a task DONE, a decision recorded) — never mid-attempt.

Agent rules (full text in `agents/agent.md`): understand implementation, find tests, follow patterns; then run tests, inspect diff, prove each criterion.

## 3. Verdict loop

```text
while not PASS and attempts < 3:
    implement() → verify() → evaluate()
    on FAIL: append Verdict feedback to .factory/state/current.md, retry
after 3 FAILs → HUMAN REVIEW
```

All criteria start FAIL. Only evidence flips them to PASS.
