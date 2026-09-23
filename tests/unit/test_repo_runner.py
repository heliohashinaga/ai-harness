"""Unit tests for the repo-mode runner (single coder worktree, stubbed chat)."""

import subprocess

from aiharness.agents import repo as scm
from aiharness.agents.repo_runner import run_repo_pipeline


def _init_repo(tmp_path):
    subprocess.run(
        ["git", "init", "-b", "main", str(tmp_path)], check=True, capture_output=True
    )
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.email", "t@t.t"], check=True
    )
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.name", "t"], check=True
    )
    (tmp_path / "README.md").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "README.md"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-m", "init"], check=True)
    return tmp_path


def test_repo_pipeline_coder_commits_to_own_worktree(tmp_path):
    repo = _init_repo(tmp_path)
    worktrees = tmp_path / "wt"
    result = run_repo_pipeline(
        repo,
        "main",
        "add a sum function",
        "code.py",
        coder_chat=lambda _p: "def add(x, y):\n    return x + y",
        base_dir=worktrees,
    )
    assert result.branch == "main"
    assert result.branch_a.startswith("agent/coder-")
    assert result.file_paths == ["code.py"]
    raw = "def add(x, y):\n    return x + y"
    assert scm.read_file(result.worktree_a, "code.py") == raw
    assert len(result.commit_c) == 40
    assert result.as_dict()["branch_a"] == result.branch_a


def test_repo_pipeline_reads_context_files_before_coding(tmp_path):
    repo = _init_repo(tmp_path)
    (repo / "SPEC.md").write_text("Entity name is Document", encoding="utf-8")
    seen: list[str] = []

    def coder_chat(prompt: str) -> str:
        seen.append(prompt)
        return "code"

    run_repo_pipeline(
        repo,
        "main",
        "write a test",
        "new.cs",
        coder_chat=coder_chat,
        base_dir=tmp_path / "wt",
        context_files=["SPEC.md"],
    )
    assert seen and "Entity name is Document" in seen[0]
