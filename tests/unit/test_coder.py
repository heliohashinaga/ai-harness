"""Unit tests for the coder node (stubbed model, no network)."""

import pytest

from aiharness.agents.coder import build_coder_node


def _node():
    code = "def add(a, b):\n    return a + b"
    return build_coder_node(chat=lambda _p: code, model="stub")


def test_coder_wires_task_to_coder_output():
    node = _node()
    out = node({"task": "write an add function"})
    assert out["coder_output"] == "def add(a, b):\n    return a + b"


def test_coder_is_language_agnostic():
    # A non-Python task is just text passed through the stub -> no language assumption.
    node = _node()
    out = node({"task": "export a React form component"})
    assert out["coder_output"].startswith("def add")


def test_generate_code_passes_context():
    seen: list[str] = []

    def spy(prompt: str) -> str:
        seen.append(prompt)
        return "code"

    from aiharness.agents.coder import generate_code

    generate_code("task", spy, context="CUSTOM-CONTEXT")
    assert seen and "CUSTOM-CONTEXT" in seen[0]


def test_coder_rejects_blank_task():
    node = _node()
    try:
        node({"task": "   "})
    except ValueError:
        return
    raise AssertionError("blank task should raise ValueError")


def test_coder_returns_partial_update_only():
    node = _node()
    out = node({"task": "x", "coder_output": "", "error": None})
    # Node returns only the key it changes.
    assert set(out.keys()) == {"coder_output"}


def test_coder_builds_offline_and_fails_only_on_invoke(monkeypatch):
    for var in ("OPENROUTER_API_KEY", "OPENCODE_GO_API_KEY", "OPENAI_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    # No chat configured: building the node must not require credentials;
    # the coder has no pass-through mode, so invoking fails instead.
    node = build_coder_node(model="stub")
    with pytest.raises(Exception, match="credentials"):
        node({"task": "x", "coder_output": "", "error": None})