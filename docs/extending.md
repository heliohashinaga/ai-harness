# Extending — earning complexity

## Levels

- **0** Single agent. **1** + deterministic evaluator. **2** + retry (max 3). **3** + Skills (opt-in prompt packs in `skills/`). Stop here for V1.
- **4** Planner. **5** Multi-agent. **6** Parallel/swarm. Only as experiments.

## Promotion rule

To promote an experiment to architecture, show in `evals/benchmark.md`:

- baseline (LEVEL 2) vs candidate on ≥ N tasks,
- Δ success rate, Δ regression, Δ cost/latency,
- why deterministic feedback or a skill couldn't fix it.

Example: `agent + evaluator = 78% vs single = 63% → keep. + planner = 77% → drop.`

## Skills, not agents

Instead of `security-agent`, add `skills/security/SKILL.md` loaded on demand
(no `skills/` dir exists yet — create it when the first skill earns its place).
Preserves context, no extra hop.

## AGENTS.md stays tiny

Goal, before/after checklist, rules (prefer existing abstractions, no new deps, no unrelated rewrites, no success claims without evidence). ~30 lines, not 1000.
