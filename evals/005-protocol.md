# 005 Protocol — does the clean-code skill earn a place? (pilot, N=3)

Frozen before running. Unlike 003 (`coder -> cleaner`, 2 calls), the skill is
a **prompt pack in the same call** (1 call both sides), so cost is flat — the
question is only correctness + readability.

- **A (baseline):** coder with default prompt (`build_coder_prompt(task)`).
- **B (candidate):** same coder, prompt + project skill
  (`skills/clean-code/SKILL.md` body via `read_clean_code_policy()` passed as
  `context`). Cost: still 1 LLM call.

Model: `deepseek-v4-flash`, provider `opencode` (same as 003/004 for
comparability). Real coder code (`build_coder_node`), stubbed in unit tests.

## Prompts (frozen, verbatim from 003)

- **P1:** "write a python function fib(n) that returns the nth fibonacci number (0-indexed: fib(0)=0, fib(1)=1). Return ONLY the code."
- **P2:** "write a python function dedup(items) that returns a list with duplicates removed, preserving first-occurrence order. Return ONLY the code."
- **P3:** "write a python function chunks(lst, n) that splits a list into chunks of size n; the last chunk may be shorter; n>=1. Return ONLY the code."

## Hidden tests (frozen, verbatim from 003)

- P1: fib(0)==0, fib(1)==1, fib(2)==1, fib(10)==55, fib(20)==6765
- P2: dedup([3,1,3,2,1])==[3,1,2], dedup([])==[], dedup('abac')==['a','b','c']
- P3: chunks([1,2,3,4,5],2)==[[1,2],[3,4],[5]], chunks([],3)==[], chunks([1],1)==[[1]]

## Grading (deterministic first)

1. Hidden tests per output (exec + eval, same as `run_003.py`).
2. `ruff check` on each output (formatting/hygiene must not regress).
3. Readability noted by operator (names, dead comments) — informational only,
   never overrides hidden tests.

## Verdict rule

Promote the skill to default-on for the coder only if B correctness >= A
(no regressions on hidden tests) AND B shows a readability win (clearer
names/structure) at flat cost (1 call each). Same-or-worse → stays opt-in
(refactor tasks, complexity-gate failures, Verdict-flagged naming).
