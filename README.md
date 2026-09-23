# ai-harness

> A minimal agent harness for software development — with measured baselines.

[![CI](https://github.com/heliohashinaga/ai-harness/actions/workflows/ci.yml/badge.svg)](https://github.com/heliohashinaga/ai-harness/actions/workflows/ci.yml)

One agent session per task, verified by evidence, extended only on measured
gain. No coordinator, no swarm, no orchestration for its own sake — see
[`docs/philosophy.md`](docs/philosophy.md) and
[`docs/adr/0001-minimal-harness-over-fixed-swarm.md`](docs/adr/0001-minimal-harness-over-fixed-swarm.md).

```text
TASK.md → AGENT (inspect → edit → test) → EVALUATOR → PASS / FAIL → retry (max 3)
```

## Getting started

```bash
# Install the project and dev tooling (uv-based).
uv sync

# Run the hello-world node via the console script.
uv run aiharness-hello "world"

# Or in Python.
uv run python -m aiharness.cli hello "world"

# Deterministic gate (lint + tests + complexity budget).
.\scripts\verify.ps1
```

Work a task per [`docs/workflow.md`](docs/workflow.md):
`.\scripts\run.ps1` → implement → `.\scripts\verify.ps1` →
`.\scripts\evaluate.ps1`. Terms in [`CONTEXT.md`](CONTEXT.md).

## Evidence, not claims

| Experiment | Result |
|---|---|
| `evals/results/001-baseline.md` | gate green: ruff clean, 65 passed (suite has since grown to 83) |
| `evals/results/002-baseline-agent-runs.md` | 4/4 tasks, first-attempt 50%, retries solved by deterministic feedback |
| `evals/results/003-cleaner-pilot.md` | cleaner **rejected** as default: 3/3 vs 3/3 at 2x calls, 3–25x latency |
| `evals/results/004-cleaner-retest.md` | cleaner retest on frozen buggy set: **0/6 fixed**, 2 regressions (B2) — 003 verdict stands, stays opt-in |

New layers (planner, reviewer, swarm) enter only by beating these numbers —
see [`evals/benchmark.md`](evals/benchmark.md) and [`docs/extending.md`](docs/extending.md).

## Code-gen CLI (opt-in experiment)

`aiharness-code` generates code from a task via the coder→cleaner graph. It is
**not** the architecture — experiment 003 showed the cleaner adds cost without
measured gain. Requires an LLM provider key in `.env` (see `.env.example`):

```bash
uv run aiharness-code "write a python function that returns the nth fibonacci number"
uv run aiharness-code --provider opencode "..." --format json
```

Note: the opencode provider needs its session header (handled in
`src/aiharness/nodes/llm.py`); if calls fail with 400/503, check
`evals/results/003-cleaner-pilot.md` for known upstream issues.

## Observability

Offline per-run metrics (latency, counts, inputs/outputs) come from
[`MetricsCallbackHandler`](src/aiharness/telemetry.py) — credential-free, no
network:

```python
from aiharness.nodes.hello_world import build_hello_world_node
from aiharness.telemetry import MetricsCallbackHandler

handler = MetricsCallbackHandler()
build_hello_world_node().invoke("world", config={"callbacks": [handler]})
print(handler.avg_latency_ms())
```

For hosted traces, token/cost dashboards, and model insights, LangSmith is an
**opt-in** integration (requires network + API key; see
[docs/langsmith.md](docs/langsmith.md)). It stays disabled by default so the
base remains offline and credential-free.

## License

MIT — see [`LICENSE`](LICENSE).
