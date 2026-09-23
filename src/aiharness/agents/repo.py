"""Local SCM (git) layer for repo mode: worktrees, commits, merge, scoped file IO.

Local-only by design (no remote clone/push/PR). Each agent gets its own git
worktree on a dedicated branch; the cleaner consumes the coder's work by merging
the coder's commit into its own worktree (SwarmForge-style commit->merge).

All functions operate on a local git repo and are testable offline against a temp
repo. File paths are validated so no I/O escapes the worktree.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

_REPO = "ai-harness:repo"


class RepoError(RuntimeError):
    """Raised for any SCM failure or unsafe operation."""


def _run(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RepoError(f"git {args[0]} failed in {cwd}: {result.stderr.strip()}")
    return result.stdout.strip()


def git_root(path: Path) -> Path:
    """Return the repo top-level for a local working tree."""
    out = _run(path, "rev-parse", "--show-toplevel")
    return Path(out)


def resolve_repo(path: str | Path, branch: str) -> tuple[Path, str]:
    """Validate a local git repo and resolve the base branch.

    Raises ``RepoError`` if ``path`` isn't a git repo or ``branch`` doesn't
    exist locally (local-only; we never fetch).
    """
    root = git_root(Path(path).expanduser().resolve())
    refs = _run(root, "branch", "--list", branch)
    if not refs:
        # fall back to head short SHA so a detached/HEAD base still works
        if branch == "HEAD":
            return root, branch
        raise RepoError(f"branch {branch!r} does not exist in {root}")
    return root, branch


def create_worktree(
    repo: Path, worktree_dir: Path, branch: str, from_ref: str
) -> Path:
    """Create a git worktree at ``worktree_dir`` on a dedicated ``branch``.

    ``git worktree add -B <branch> <dir> <from_ref>`` creates (or resets) the
    branch at ``from_ref`` and checks it out in an isolated directory.
    """
    _run(repo, "worktree", "add", "--force", "-B", branch, str(worktree_dir), from_ref)
    return worktree_dir


def commit(worktree: Path, paths: list[str], message: str) -> str:
    """Stage only ``paths`` and commit in ``worktree``; return the commit SHA."""
    _run(worktree, "add", "--", *paths)
    _run(worktree, "commit", "-m", message)
    return _run(worktree, "rev-parse", "HEAD")


def merge(worktree: Path, sha: str) -> None:
    """Merge ``sha`` (the coder's commit) into ``worktree``'s current branch."""
    _run(worktree, "merge", "--no-edit", sha)


def cleanup(repo: Path, worktree: Path) -> None:
    """Remove a worktree (with ``--force`` so uncommitted state is droppable)."""
    _run(repo, "worktree", "remove", "--force", str(worktree))


def _safe_path(worktree: str | Path, relpath: str) -> Path:
    """Resolve ``relpath`` under ``worktree``, rejecting traversal/absolute paths."""
    worktree = Path(worktree)
    path = Path(relpath)
    if path.is_absolute() or ".." in path.parts:
        raise RepoError(f"unsafe path {relpath!r}: must be relative and not '..'")
    full = worktree / path
    try:
        resolved = full.resolve()
    except OSError as exc:  # pragma: no cover - non-existent under worktree
        raise RepoError(f"cannot resolve {relpath!r}: {exc}") from exc
    if not resolved.is_relative_to(worktree.resolve()):
        raise RepoError(f"path {relpath!r} escapes the worktree")
    return resolved


def read_file(worktree: Path, relpath: str) -> str:
    target = _safe_path(worktree, relpath)
    return target.read_text(encoding="utf-8")


def write_file(worktree: Path, relpath: str, content: str) -> None:
    target = _safe_path(worktree, relpath)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")