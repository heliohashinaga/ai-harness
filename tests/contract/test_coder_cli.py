"""Contract tests for the aiharness-code CLI (coder node mocked, no network)."""

import json

import pytest

from aiharness import coder_cli
from aiharness.nodes import llm as llm_nodes

pytestmark = pytest.mark.contract


@pytest.fixture
def fake_key(monkeypatch):
    monkeypatch.setattr(llm_nodes, "provider_api_key", lambda provider: "sk-dummy")


@pytest.fixture
def fake_coder(monkeypatch):
    class _FakeCoder:
        def __call__(self, state):
            assert state["task"].strip(), "blank task must fail before the node"
            return {"coder_output": "generated"}

    monkeypatch.setattr(
        coder_cli.coder_agents, "build_coder_node", lambda **k: _FakeCoder()
    )


def test_cli_prints_coder_output_exit_zero(fake_key, fake_coder, capsys):
    assert coder_cli.main(["write an add function"]) == 0
    assert capsys.readouterr().out == "generated\n"


def test_cli_json_output(fake_key, fake_coder, capsys):
    assert coder_cli.main(["x", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["coder_output"] == "generated"
    assert "cleaner_output" not in payload


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
        def __call__(self, state):
            raise RuntimeError("boom")

    monkeypatch.setattr(
        coder_cli.coder_agents, "build_coder_node", lambda **k: _Boom()
    )
    assert coder_cli.main(["x"]) == 4
    assert capsys.readouterr().out == ""


class _FakeRepoResult:
    branch_a = "agent/coder-xyz"
    commit_c = "b" * 40
    file_paths = ["code.py"]
    worktree_a = "/tmp/wt/coder-xyz"

    def as_dict(self):
        return {
            "branch_a": self.branch_a,
            "commit_c": self.commit_c,
            "file_paths": self.file_paths,
            "worktree_a": self.worktree_a,
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
    assert "coder-xyz" in out
    assert "code.py" in out


def test_repo_mode_json(fake_repo, capsys):
    argv = ["--repo", "/tmp/repo", "--file", "a.py", "t", "--format", "json"]
    assert coder_cli.main(argv) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["branch_a"] == "agent/coder-xyz"


def test_repo_mode_usage_error_exit_one(fake_repo, monkeypatch, capsys):
    def _raise(_r, _b, _t, _f, **k):
        raise ValueError("target file must be non-empty")

    monkeypatch.setattr(coder_cli, "run_repo_pipeline", _raise)
    assert coder_cli.main(["--repo", "/tmp/repo", "task"]) == 1
    assert capsys.readouterr().out == ""
