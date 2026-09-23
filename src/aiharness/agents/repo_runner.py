"""Repo mode runner: the coder operates on a local repo via a worktree.

Orchestrates the local workflow (no remote): resolve repo+branch, give the
coder its own worktree (commit cA). The worktree is left in a temp dir for
inspection and can be cleaned via ``repo.cleanup``.

Single worktree, single commit, coder-only (second hop removed in TASK-009).
"""

from __future__ import annotations

import tempfile
import time
from pathlib import Path

from aiharness.agents import coder as coder_agents
from aiharness.agents import repo as repo_scm
from aiharness.agents.explorer import build_explorer_coder
from aiharness.nodes.models import Chat


def _read_context(
    scm, worktree, context_files: list[str] | None
) -> str:
    """Read repo reference files and format them as coder context."""
    if not context_files:
        return ""
    blocks: list[str] = []
    for rel in context_files:
        blocks.append(f"### {rel}\n" + scm.read_file(worktree, rel))
    return "\n\n".join(blocks)


class RepoRunResult:
    """Outcome of a repo-mode run (worktree/branch/commit identities)."""

    def __init__(
        self,
        repo: str,
        branch: str,
        branch_a: str,
        commit_c: str,
        file_paths: list[str],
        worktree_a: str,
    ) -> None:
        self.repo = repo
        self.branch = branch
        self.branch_a = branch_a
        self.commit_c = commit_c
        self.file_paths = file_paths
        self.worktree_a = worktree_a

    def as_dict(self) -> dict:
        return {
            "repo": self.repo,
            "branch": self.branch,
            "branch_a": self.branch_a,
            "commit_c": self.commit_c,
            "file_paths": self.file_paths,
            "worktree_a": self.worktree_a,
        }


def run_repo_pipeline(
    repo_path: str | Path,
    branch: str,
    task: str,
    target_file: str,
    *,
    coder_chat: Chat | None = None,
    provider: str = "openrouter",
    model: str | None = None,
    base_dir: Path | None = None,
    context_files: list[str] | None = None,
) -> RepoRunResult:
    """Run the coder on a local repo in its own worktree (coder-only)."""
    root, base = repo_scm.resolve_repo(repo_path, branch)
    if not target_file.strip():
        raise ValueError("target file must be non-empty")
    # Input validation mirrors the text-mode blank-task rule.
    if not task.strip():
        raise ValueError("task must be non-empty")

    ts = str(int(time.time() * 1000))
    branch_a = f"agent/coder-{ts}"

    worktrees_root = base_dir or Path(tempfile.mkdtemp(prefix="aiharness-repo-"))
    worktree_a = worktrees_root / f"coder-{ts}"

    # --- coder ---
    repo_scm.create_worktree(root, worktree_a, branch_a, base)
    if coder_chat is not None:
        context = _read_context(repo_scm, root, context_files)
        code = coder_agents.generate_code(task, coder_chat, context)
    else:
        # Real run: use an agent that explores the repo itself (SwarmForge-like).
        explorer = build_explorer_coder(
            root,
            provider=provider,
            model=model,
            target_file=target_file,
            context_files=context_files,
        )
        code = explorer(task)
    repo_scm.write_file(worktree_a, target_file, code)
    commit_c = repo_scm.commit(worktree_a, [target_file], f"agent(coder): {task}")

    return RepoRunResult(
        repo=str(root),
        branch=base,
        branch_a=branch_a,
        commit_c=commit_c,
        file_paths=[target_file],
        worktree_a=str(worktree_a),
    )
