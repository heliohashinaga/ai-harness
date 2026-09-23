# Evaluation

## Order matters: cheap first

1. **Build** — `ruff check`, `pytest`, build per stack. Fail fast.
2. **Rules** — lint, typecheck and security scan when configured (today: ruff only), `git diff --stat` sanity (no unrelated rewrites).
3. **Acceptance** — each Task criterion mapped to a test or script output.
4. **LLM judge (optional)** — only for properties no script can check (e.g. "follows existing abstraction"). Fresh context, read-only, receives Task + diff + test results, never the agent's chain-of-thought.

## Verdict format

```yaml
verdict: FAIL
evidence:
  build: pass
  tests: "71 passed, 1 failed"
  criteria:
    - {id: dry-run-text, status: pass, proof: "test_cli_dry_run_text_prints_plan green"}
    - {id: quality-gate, status: fail, proof: "main complexity 12 > budget 10"}
feedback: "extract output emission into a helper to get under the budget"
```

## Metrics (every run)

`task_success, first_attempt_success, retry_rate, human_rate, regression_rate, tokens, cost, latency` → append to `evals/results/`. Report **quality/cost**, never quality alone.

## Evaluator separation

Coder writes; evaluator judges from a new context without write tools. This kills "I already decided I'm right" confirmation bias.
