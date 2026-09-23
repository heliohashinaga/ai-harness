# TASK-000 — Example task

## Goal

Add a `--dry-run` flag to `agentcrew-hello` that prints without side effects.

## Context

Operators want to preview the command before it runs.

## Acceptance Criteria

- [ ] `--dry-run` prints the planned output and changes nothing.
- [ ] Existing behavior without the flag is unchanged.
- [ ] Automated tests cover the new flag.
- [ ] `scripts/verify.ps1` passes; no new dependency.

## Constraints

- Follow existing CLI patterns in `src/agentcrew/cli.py`.
- Minimal diff; no unrelated rewrites.
