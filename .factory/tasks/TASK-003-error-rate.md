# TASK-003 — Add error-rate helper to MetricsCallbackHandler

## Goal

Add an `error_rate()` helper to `MetricsCallbackHandler`
(`src/agentcrew/telemetry.py`) returning the fraction of runs that errored,
with a unit test.

## Context

The handler already tracks `runs` and `errors` and exposes `count_runs()`
and `avg_latency_ms()`. Consumers have no one-call way to get the error
fraction.

## Acceptance Criteria

- [ ] `error_rate()` returns `None` when no runs recorded, else
  `len(errors) / len(runs)` as a float in `[0.0, 1.0]`.
- [ ] Unit test covers: no runs → `None`; all-ok → `0.0`; mixed → correct
  fraction (drive via `on_chain_start/end/error` like existing tests).
- [ ] Existing telemetry tests pass unchanged.
- [ ] `.\scripts\verify.ps1` passes; no new dependency.

## Constraints

- Follow the existing style in `telemetry.py` (dataclass, helpers).
- Minimal diff; no unrelated rewrites.
