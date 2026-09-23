# Evaluation

## Order matters: cheap first

1. **Build** — `ruff check`, `pytest`, build per stack. Fail fast.
2. **Rules** — lint, typecheck, security scan, `git diff --stat` sanity (no unrelated rewrites).
3. **Acceptance** — each Task criterion mapped to a test or script output.
4. **LLM judge (optional)** — only for properties no script can check (e.g. "follows existing abstraction"). Fresh context, read-only, receives Task + diff + test results, never the agent's chain-of-thought.

## Verdict format

```yaml
verdict: FAIL
evidence:
  build: pass
  tests: "7/9 pass"
  criteria:
    - {id: idempotency, status: fail, proof: "concurrent dupes both executed"}
    - {id: regression, status: pass, proof: "pytest -q green"}
feedback: "make the key check atomic; see evals/…/repro.py"
```

## Metrics (every run)

`task_success, first_attempt_success, retry_rate, human_rate, regression_rate, tokens, cost, latency` → append to `evals/results/`. Report **quality/cost**, never quality alone.

## Evaluator separation

Coder writes; evaluator judges from a new context without write tools. This kills "I already decided I'm right" confirmation bias.
