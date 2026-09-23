# Philosophy

1. **Simplicity first.** The simplest harness that reliably solves the task wins. Complexity must be justified by measurement.
2. **Every component is removable.** Each harness piece encodes a bet about what the model can't do. Bets expire as models improve — delete before adding.
3. **Humans steer, agents execute.** Humans define Task + acceptance. Agents inspect, implement, test, iterate.
4. **Repository is the system of record.** Code, tests, docs, git history. No vector DB, no memory server at LEVEL 0-2.
5. **Context is scarce.** Give a map, not a dump. The agent retrieves; the harness doesn't flood.
6. **Evidence over claims.** No success without build + tests + diff + acceptance proof. Default status is FAIL.
7. **Evaluation before orchestration.** No second agent without a measured failure mode it fixes.
8. **Prefer deterministic feedback.** Compiler/linter/test > LLM judge. LLM evaluator only for non-deterministic properties, from fresh context, read-only.
9. **Controlled autonomy.** LEVEL 0 single agent → 1 deterministic evaluator → 2 retry → 3 skills → 4+ planner/multi-agent. No skipping without evidence.
10. **Measure quality/cost.** Tokens, latency, cost per task alongside pass rate. A 20x-cost harness needs a 20x reason.
