"""Unit tests for the offline LangChain metrics callback handler."""

import pytest

from aiharness.nodes.hello_world import build_hello_world_node
from aiharness.telemetry import MetricsCallbackHandler

pytestmark = pytest.mark.unit


def test_records_a_single_chain_run():
    node = build_hello_world_node()
    handler = MetricsCallbackHandler()
    node.invoke("Ada", config={"callbacks": [handler]})

    assert handler.count_runs() == 1
    run = handler.runs[0]
    assert run.type == "chain"
    assert run.input == "Ada"
    assert run.output == {"input": "Ada", "greeting": "Hello, Ada!"}
    assert run.error is None
    assert run.latency_ms > 0
    assert handler.errors == []


def test_records_multiple_runs_and_latency_stats():
    node = build_hello_world_node()
    handler = MetricsCallbackHandler()
    for text in ["world", "Ada", "CI"]:
        node.invoke(text, config={"callbacks": [handler]})

    assert handler.count_runs() == 3
    latencies = [run.latency_ms for run in handler.runs]
    assert all(value > 0 for value in latencies)
    assert handler.avg_latency_ms() == pytest.approx(sum(latencies) / len(latencies))
    assert handler.errors == []


def test_empty_handler_stats():
    handler = MetricsCallbackHandler()
    assert handler.count_runs() == 0
    assert handler.avg_latency_ms() is None
    assert handler.runs == []
    assert handler.errors == []


def test_error_rate_no_runs_returns_none():
    handler = MetricsCallbackHandler()
    assert handler.error_rate() is None


def test_error_rate_all_ok_returns_zero():
    handler = MetricsCallbackHandler()
    handler.on_chain_start({}, {}, run_id="a")
    handler.on_chain_end({}, run_id="a")
    assert handler.error_rate() == 0.0


def test_error_rate_mixed_returns_fraction():
    handler = MetricsCallbackHandler()
    handler.on_chain_start({}, {}, run_id="a")
    handler.on_chain_end({}, run_id="a")
    handler.on_chain_start({}, {}, run_id="b")
    handler.on_chain_error(ValueError("boom"), run_id="b")
    assert handler.error_rate() == 0.5