# TASK-002 — Parse hello CLI argv with argparse, no behavior change

## Goal

Replace the hand-rolled `while` loop in `_parse_format`
(`src/agentcrew/cli.py`) with `argparse`, keeping every observable behavior
identical.

## Context

Pure refactor to remove bespoke parsing. The existing contract tests
(`tests/contract/test_hello_world_cli.py`) pin the behaviors that must not
change: optional leading `hello` verb, `--format` anywhere (space and `=`
forms), exit codes 0/1/4, stdout/stderr discipline.

## Acceptance Criteria

- [ ] All existing tests pass unchanged (no test edits allowed for behavior).
- [ ] Manual spot-checks behave identically: `hello` verb, `--format` in any
  position, missing value, `bogus` provider-style misuse, empty text.
- [ ] `--help` output comes from argparse and mentions `<text>` and `--format`.
- [ ] `.\scripts\verify.ps1` passes; no new dependency.

## Constraints

- Do not change exit codes, output shapes, or error messages beyond what
  argparse generates for `--help` / malformed flags (document any such delta
  in the commit message).
- Minimal diff outside `cli.py`; no unrelated rewrites.
