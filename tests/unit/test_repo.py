"""Unit tests for the local SCM layer (offline, against temp git repos)."""

import subprocess
from pathlib import Path

import pytest

from aiharness.agents import repo as scm


def _init_repo(tmp_path: Path) -> Path:
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


def _wt_dir(tmp_path: Path, name: str) -> Path:
    return tmp_path / f".wt-{name}"


def test_resolve_repo_rejects_unknown_branch(tmp_path):
    repo = _init_repo(tmp_path)
    with pytest.raises(scm.RepoError):
        scm.resolve_repo(repo, "nope")


def test_create_worktree_and_commit_returns_sha(tmp_path):
    repo = _init_repo(tmp_path)
    wt = scm.create_worktree(repo, _wt_dir(tmp_path, "a"), "agent/coder-x", "main")
    scm.write_file(wt, "code.py", "x = 1\n")
    sha = scm.commit(wt, ["code.py"], "add code")
    assert len(sha) == 40
    assert scm.read_file(wt, "code.py") == "x = 1\n"


def test_cleaner_worktree_merges_coder_commit(tmp_path):
    repo = _init_repo(tmp_path)
    wt_a = scm.create_worktree(repo, _wt_dir(tmp_path, "a"), "agent/coder-x", "main")
    scm.write_file(wt_a, "code.py", "x = 1\n")
    scm.commit(wt_a, ["code.py"], "coder")
    wt_b = scm.create_worktree(
        repo, _wt_dir(tmp_path, "b"), "agent/cleaner-x", "agent/coder-x"
    )
    # B derives from branch A, so the coder's file is already present.
    assert scm.read_file(wt_b, "code.py") == "x = 1\n"
    scm.write_file(wt_b, "code.py", "x = 1  # cleaned\n")
    scm.commit(wt_b, ["code.py"], "cleaner")
    assert scm.read_file(wt_b, "code.py") == "x = 1  # cleaned\n"


@pytest.mark.parametrize("bad", ["../escape.txt", "/abs.txt", "a/../../x"])
def test_path_escape_is_rejected(tmp_path, bad):
    _init_repo(tmp_path)
    wt = _wt_dir(tmp_path, "a")
    with pytest.raises(scm.RepoError):
        scm.read_file(wt, bad)
    with pytest.raises(scm.RepoError):
        scm.write_file(wt, bad, "boom")


def test_cleanup_removes_worktree(tmp_path):
    repo = _init_repo(tmp_path)
    wt = scm.create_worktree(repo, _wt_dir(tmp_path, "a"), "agent/coder-x", "main")
    assert wt.exists()
    scm.cleanup(repo, wt)
    assert not wt.exists()