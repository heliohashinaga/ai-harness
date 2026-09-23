"""Unit tests for the repo-mode runner (worktrees + commit->merge, stubbed chats)."""

import subprocess

from aicrew.agents import repo as scm
from aicrew.agents.repo_runner import run_repo_pipeline


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


def test_repo_pipeline_coder_then_cleaner_commits(tmp_path):
    repo = _init_repo(tmp_path)
    worktrees = tmp_path / "wt"
    result = run_repo_pipeline(
        repo,
        "main",
        "add a sum function",
        "code.py",
        coder_chat=lambda _p: "def add(x, y):\n    return x + y",
        cleaner_chat=lambda _p: "def add(a, b):  # cleaned\n    return a + b",
        base_dir=worktrees,
    )
    assert result.branch == "main"
    assert result.branch_a.startswith("agent/coder-")
    assert result.branch_b.startswith("agent/cleaner-")
    assert result.file_paths == ["code.py"]
    assert result.cleaned_files == ["code.py"]
    # cleaner worktree holds the CLEANED version (its own branch B)
    cleaned = "def add(a, b):  # cleaned\n    return a + b"
    assert scm.read_file(result.worktree_b, "code.py") == cleaned
    # coder worktree still holds the RAW version (intact, reversible)
    raw = "def add(x, y):\n    return x + y"
    assert scm.read_file(result.worktree_a, "code.py") == raw
    # commit_c and commit_b differ (cleaner actually changed the file)
    assert result.commit_c != result.commit_b


def test_repo_pipeline_cleaner_failure_fails_gracefully(tmp_path):
    repo = _init_repo(tmp_path)
    result = run_repo_pipeline(
        repo,
        "main",
        "task",
        "code.py",
        coder_chat=lambda _p: "x = 1\n",
        cleaner_chat=lambda _p: (_ for _ in ()).throw(RuntimeError("boom")),
        base_dir=tmp_path / "wt",
    )
    # Cleaner couldn't refine -> code passes through unchanged.
    assert scm.read_file(result.worktree_b, "code.py") == "x = 1\n"


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
        cleaner_chat=lambda _p: "code",
        base_dir=tmp_path / "wt",
        context_files=["SPEC.md"],
    )
    assert seen and "Entity name is Document" in seen[0]