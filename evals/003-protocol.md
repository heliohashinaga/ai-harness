# 003 Protocol — does the cleaner earn existence? (pilot, N=3)

Frozen before running. Configs use the REAL graph code
(`build_coder_cleaner_graph`):

- **A (baseline):** coder with provider chat, `cleaner_chat=None` → cleaner
  passes code through unchanged. Cost: 1 LLM call.
- **B (candidate):** coder + cleaner, both with provider chat. Cost: 2 calls.

Model: `deepseek-v4-flash` explicit (the `.env` default
`muse-spark-1.3-contributor` returns 503 upstream — noted, not changed).
Provider: opencode. Prompts are the coder's own prompt shape (task → code only).

## Prompts (frozen)

- **P1:** "write a python function fib(n) that returns the nth fibonacci number (0-indexed: fib(0)=0, fib(1)=1). Return ONLY the code."
- **P2:** "write a python function dedup(items) that returns a list with duplicates removed, preserving first-occurrence order. Return ONLY the code."
- **P3:** "write a python function chunks(lst, n) that splits a list into chunks of size n; the last chunk may be shorter; n>=1. Return ONLY the code."

## Hidden tests (frozen, executed against each output)

- P1: fib(0)==0, fib(1)==1, fib(2)==1, fib(10)==55, fib(20)==6765
- P2: dedup([3,1,3,2,1])==[3,1,2], dedup([])==[], dedup('abac')==['a','b','c']
- P3: chunks([1,2,3,4,5],2)==[[1,2],[3,4],[5]], chunks([],3)==[], chunks([1],1)==[[1]]

## Verdict rule

Promote cleaner to default only if B beats A on correctness (hidden tests)
by a margin justifying 2x calls + latency. Same-or-worse → reject as default
(keep as opt-in experiment).
