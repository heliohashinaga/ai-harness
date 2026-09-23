# Minimal harness over fixed swarm

We run one Agent Session per Task (model + repo tools + task), verified by a separate deterministic-first Evaluator with bounded retry. New roles (planner, reviewer, swarm) enter only when a benchmark proves quality/cost gain.

## Considered Options

- **Fixed pipeline (current coder -> cleaner graph):** always runs cleaner after coder, even when no gain. Simple to demo, but taxes every task and bakes in the assumption that two LLM passes beat one.
- **Full swarm (planner/worker/tester/security/cleaner):** expressive on paper, but each hop fragments context, adds competing instructions, and hides which layer actually helped. Rejected as default; kept as LEVEL 4+ experiments.

## Consequences

- The existing `coder_cleaner` graph becomes one experiment in `evals/`, not the architecture. `AGENTS.md` swarm vision needs a rewrite to "minimal first, swarm on evidence".
- Every harness change must report success rate + cost, not just quality.
