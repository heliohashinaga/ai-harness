"""Contract tests for the aicrew-code CLI (graph mocked, no network)."""

import json

import pytest

from aicrew import coder_cli
from aicrew.nodes import llm as llm_nodes

pytestmark = pytest.mark.contract


@pytest.fixture
def fake_key(monkeypatch):
    monkeypatch.setattr(llm_nodes, "provider_api_key", lambda provider: "sk-dummy")


@pytest.fixture
def fake_graph(monkeypatch):
    class _FakeGraph:
        def invoke(self, state):
            return {"coder_output": "raw", "cleaner_output": "cleaned"}

    monkeypatch.setattr(coder_cli, "_build_graph", lambda *a, **k: _FakeGraph())


def test_cli_prints_cleaned_code_exit_zero(fake_key, fake_graph, capsys):
    assert coder_cli.main(["write an add function"]) == 0
    assert capsys.readouterr().out == "cleaned\n"


def test_cli_json_output(fake_key, fake_graph, capsys):
    assert coder_cli.main(["x", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["coder_output"] == "raw"
    assert payload["cleaner_output"] == "cleaned"


@pytest.mark.parametrize(
    "argv",
    [
        [],  # missing task
        ["--provider", "bogus", "x"],  # unsupported provider
    ],
)
def test_cli_usage_errors_exit_one(argv, capsys):
    assert coder_cli.main(argv) == 1
    assert capsys.readouterr().out == ""


def test_cli_missing_key_returns_hint_exit_four(monkeypatch, capsys):
    monkeypatch.setattr(llm_nodes, "provider_api_key", lambda provider: "")
    assert coder_cli.main(["x"]) == 4
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "OPENROUTER_API_KEY" in captured.err


def test_cli_node_failure_exit_four(fake_key, monkeypatch, capsys):
    class _Boom:
        def invoke(self, state):
            raise RuntimeError("boom")

    monkeypatch.setattr(coder_cli, "_build_graph", lambda *a, **k: _Boom())
    assert coder_cli.main(["x"]) == 4
    assert capsys.readouterr().out == ""


class _FakeRepoResult:
    branch_b = "agent/cleaner-xyz"
    commit_b = "a" * 40
    cleaned_files = ["code.py"]
    worktree_b = "/tmp/wt/cleaner-xyz"

    def as_dict(self):
        return {
            "branch_b": self.branch_b,
            "commit_b": self.commit_b,
            "cleaned_files": self.cleaned_files,
            "worktree_b": self.worktree_b,
        }


@pytest.fixture
def fake_repo(monkeypatch):
    monkeypatch.setattr(llm_nodes, "provider_api_key", lambda provider: "sk-dummy")
    monkeypatch.setattr(
        coder_cli, "run_repo_pipeline", lambda *a, **k: _FakeRepoResult()
    )


def test_repo_mode_text_exit_zero(fake_repo, capsys):
    argv = ["--repo", "/tmp/repo", "--branch", "main", "--file", "code.py", "t"]
    assert coder_cli.main(argv) == 0
    out = capsys.readouterr().out
    assert "cleaner-xyz" in out
    assert "code.py" in out


def test_repo_mode_json(fake_repo, capsys):
    argv = ["--repo", "/tmp/repo", "--file", "a.py", "t", "--format", "json"]
    assert coder_cli.main(argv) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["branch_b"] == "agent/cleaner-xyz"


def test_repo_mode_usage_error_exit_one(fake_repo, monkeypatch, capsys):
    def _raise(_r, _b, _t, _f, **k):
        raise ValueError("target file must be non-empty")

    monkeypatch.setattr(coder_cli, "run_repo_pipeline", _raise)
    assert coder_cli.main(["--repo", "/tmp/repo", "task"]) == 1
    assert capsys.readouterr().out == ""