# 005 — clean-code skill results

model=deepseek-v4-flash provider=opencode (1 call both sides; skill is prompt pack)

skill_source=skills/clean-code/SKILL.md chars=715

- P1 A coder-only: PASS (all hidden tests pass) calls=1 latency=3611ms ruff=True
- P1 B coder+skill: PASS (all hidden tests pass) calls=1 latency=3219ms ruff=True
- P2 A coder-only: PASS (all hidden tests pass) calls=1 latency=1141ms ruff=True
- P2 B coder+skill: PASS (all hidden tests pass) calls=1 latency=19769ms ruff=True
- P3 A coder-only: PASS (all hidden tests pass) calls=1 latency=12423ms ruff=True
- P3 B coder+skill: PASS (all hidden tests pass) calls=1 latency=1981ms ruff=True

Correctness A 3/3, B 3/3.
## Verdict: PROMOTE skill to default-on for the coder (correctness held, flat cost; per 005-protocol rule).

## Operator readability check (2026-09-23)

Re-ran P1/P2 capturing full outputs: A and B byte-identical (fib loop a,b; dedup seen/result). No naming/structure delta on this trivial set - ceiling effect.

## Verdict (final, per 005-protocol rule): skill stays OPT-IN - correctness held (3/3 vs 3/3, flat 1-call cost, ruff all-true) but no readability win shown. Load only on refactors, complexity-gate failures, or Verdict-flagged naming. Runner auto-line above is superseded by this note.
