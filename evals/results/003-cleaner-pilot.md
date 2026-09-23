# 003 — cleaner pilot results

model=deepseek-v4-flash provider=opencode

- P1 A coder-only: PASS (all hidden tests pass) calls=1 latency=1258ms cleaner_changed=False
- P1 B coder+cleaner: PASS (all hidden tests pass) calls=2 latency=30277ms cleaner_changed=True
- P2 A coder-only: PASS (all hidden tests pass) calls=1 latency=1937ms cleaner_changed=False
- P2 B coder+cleaner: PASS (all hidden tests pass) calls=2 latency=48546ms cleaner_changed=True
- P3 A coder-only: PASS (all hidden tests pass) calls=1 latency=2119ms cleaner_changed=False
- P3 B coder+cleaner: PASS (all hidden tests pass) calls=2 latency=6809ms cleaner_changed=True

## Verdict: REJECT cleaner as default

Correctness: A 3/3, B 3/3 — delta zero. The cleaner rewrote code every time
(`cleaner_changed=True`) without fixing or breaking anything observable.
Cost: 2x LLM calls and 3–25x latency per task for no measured gain.
The `coder -> cleaner` graph stays an opt-in experiment, not the backbone.

## Infra findings (blocked then fixed during this run)

1. Repo opencode path was dead: every call failed with MissingSessionID
   (HTTP 400). Fixed in `src/agentcrew/nodes/llm.py` — send
   `x-opencode-session` (per-client UUID) via `default_headers` for the
   opencode provider. Suite still 72 passed.
2. `.env` model `muse-spark-1.3-contributor` returns 503 upstream
   ("Endpoint is unavailable"); pilot used explicit `deepseek-v4-flash`.
   `.env` left untouched — owner's call.

## Limits

Pilot only (N=3, one run each, default temperature). A larger N or harder
tasks (where coder output is buggy) could show cleaner value — that would be
experiment 004 with a pre-registered buggy-output set. Until then: rejected.
