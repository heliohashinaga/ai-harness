# TASK-001 — Reject invalid --format in agentcrew-hello

## Goal

`agentcrew-hello --format xml hi` currently succeeds and silently behaves as
`text`. An invalid `--format` value must be a usage error instead.

## Context

`_parse_format` in `src/agentcrew/cli.py` accepts any string; `main` only
branches on `"json"`. Existing contract tests pin the valid behaviors.

## Acceptance Criteria

- [ ] `--format` with any value other than `text` or `json` exits 1, prints
  nothing on stdout, and prints usage to stderr.
- [ ] `--format text`, `--format json`, `--format=text`, `--format=json` keep
  working exactly as today.
- [ ] Regression test covers the invalid value (both `--format xml` forms).
- [ ] `.\scripts\verify.ps1` passes; no new dependency.

## Constraints

- Follow existing CLI patterns in `src/agentcrew/cli.py`.
- Minimal diff; no unrelated rewrites.
