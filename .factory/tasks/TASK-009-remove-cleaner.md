# TASK-009 — Remove the cleaner (keep coder-only default)

## Goal

Delete the `cleaner` second hop so the codebase matches the measured
verdicts (003/004/005: cleaner rejected as default, skill opt-in).
`aiharness-code` and repo mode become coder-only; `--clean` disappears.

## Context

`cleaner.py` is already off by default (`cleaner_chat=None` pass-through,
`--clean` opt-in). Removal is now pure deletion + rewiring, no behavior
change for default runs. Historical evidence stays in
`evals/results/003-*.md`, `004-*.md`, `005-*.md` (frozen records, untouched).

## Acceptance Criteria

- [ ] No `cleaner` reference remains in `src/` (agent, graph, CLI, models).
- [ ] `aiharness-code <task>` runs the coder node directly (no graph with a
  pass-through node); `--clean` flag removed from `_USAGE`/`_parse`.
- [ ] `run_repo_pipeline` uses a single worktree/branch (coder only);
  `RepoRunResult` drops `branch_b`/`commit_b`/`cleaned_files` (or maps them
  to the coder identities — decide in implementation, document in commit).
- [ ] `evals/run_003.py`, `run_004.py` archived (e.g. `evals/archive/`) since
  they import the deleted node; `evals/results/*` kept verbatim.
- [ ] `tests/` updated: delete/merge `test_cleaner.py`, cleaner branches in
  `test_repo_runner.py`, cleaner halves of contract tests; suite green.
- [ ] `.\scripts\verify.ps1` passes (ruff + pytest + complexity gate ≤ 10).
- [ ] `docs/architecture.md` + `evals/benchmark.md` note the removal
  (one line each: cleaner deleted per TASK-009, skill stays opt-in).

## Constraints

- `clean_code_policy.py` + `skills/clean-code/SKILL.md` STAY (the skill is
  a coder prompt pack, independent of the cleaner hop — see exp 005).
- Keep the deletion in one commit, after a green baseline run.
- Minimal diff outside the cleaner seam; no unrelated rewrites.

## Suggested phases (operator order)

1. Baseline: `verify.ps1` green, commit checkpoint.
2. `coder_cli.py`: call coder node directly; drop `--clean`, `_build_graph`
   cleaner wiring.
3. `repo_runner.py`: single worktree; simplify `RepoRunResult`.
4. Delete `agents/cleaner.py`, `graphs/coder_cleaner.py`; prune
   `nodes/models.py` (`CleanerOutput`, `TaskState.cleaner_output`).
5. Archive `evals/run_003.py`, `run_004.py`; update tests; docs one-liners.
6. `verify.ps1` green; inspect `git diff`; commit.
