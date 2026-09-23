"""Repo mode runner: coder and cleaner operate on a local repo via worktrees.

Orchestrates the local workflow (no remote): resolve repo+branch, give the coder
its own worktree A (commit cA), give the cleaner its own worktree B (merge cA,
clean declared files, commit cB). Worktrees are left in a temp dir for inspection
and can be cleaned via ``repo.cleanup``.
"""

from __future__ import annotations

import tempfile
import time
from collections.abc import Callable
from pathlib import Path

from aicrew.agents import cleaner as cleaner_agents
from aicrew.agents import coder as coder_agents
from aicrew.agents import repo as repo_scm
from aicrew.agents.clean_code_policy import read_clean_code_policy
from aicrew.agents.explorer import build_explorer_coder

Chat = Callable[[str], str]


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
        branch_b: str,
        commit_c: str,
        commit_b: str,
        file_paths: list[str],
        cleaned_files: list[str],
        worktree_a: str,
        worktree_b: str,
    ) -> None:
        self.repo = repo
        self.branch = branch
        self.branch_a = branch_a
        self.branch_b = branch_b
        self.commit_c = commit_c
        self.commit_b = commit_b
        self.file_paths = file_paths
        self.cleaned_files = cleaned_files
        self.worktree_a = worktree_a
        self.worktree_b = worktree_b

    def as_dict(self) -> dict:
        return {
            "repo": self.repo,
            "branch": self.branch,
            "branch_a": self.branch_a,
            "branch_b": self.branch_b,
            "commit_c": self.commit_c,
            "commit_b": self.commit_b,
            "file_paths": self.file_paths,
            "cleaned_files": self.cleaned_files,
            "worktree_a": self.worktree_a,
            "worktree_b": self.worktree_b,
        }


def run_repo_pipeline(
    repo_path: str | Path,
    branch: str,
    task: str,
    target_file: str,
    *,
    coder_chat: Chat | None = None,
    cleaner_chat: Chat | None = None,
    policy: str | None = None,
    provider: str = "openrouter",
    model: str | None = None,
    base_dir: Path | None = None,
    context_files: list[str] | None = None,
) -> RepoRunResult:
    """Run coder->cleaner on a local repo across two per-agent worktrees."""
    root, base = repo_scm.resolve_repo(repo_path, branch)
    if not target_file.strip():
        raise ValueError("target file must be non-empty")
    # Input validation mirrors the text-mode blank-task rule.
    if not task.strip():
        raise ValueError("task must be non-empty")

    ts = str(int(time.time() * 1000))
    branch_a = f"agent/coder-{ts}"
    branch_b = f"agent/cleaner-{ts}"

    worktrees_root = base_dir or Path(tempfile.mkdtemp(prefix="aicrew-repo-"))
    worktree_a = worktrees_root / f"coder-{ts}"
    worktree_b = worktrees_root / f"cleaner-{ts}"

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
    file_paths = [target_file]

    # --- cleaner ---
    repo_scm.create_worktree(root, worktree_b, branch_b, branch_a)
    repo_scm.merge(worktree_b, commit_c)  # consume coder's commit into B
    effective_policy = policy if policy is not None else read_clean_code_policy()
    cleaner = cleaner_chat or cleaner_agents.default_chat(provider, model)
    cleaned_files: list[str] = []
    for rel in file_paths:
        original = repo_scm.read_file(worktree_b, rel)
        cleaned = cleaner_agents.clean_code_text(original, cleaner, effective_policy)
        repo_scm.write_file(worktree_b, rel, cleaned)
        cleaned_files.append(rel)
    # Commit only if the cleaner actually changed something; otherwise branch B
    # keeps the coder's commit (commit_b == HEAD) — no empty commit.
    dirty = repo_scm._run(worktree_b, "status", "--porcelain", "--", *file_paths)
    if dirty:
        commit_b = repo_scm.commit(
            worktree_b, file_paths, "agent(cleaner): semantic clean code"
        )
    else:
        commit_b = repo_scm._run(worktree_b, "rev-parse", "HEAD")

    return RepoRunResult(
        repo=str(root),
        branch=base,
        branch_a=branch_a,
        branch_b=branch_b,
        commit_c=commit_c,
        commit_b=commit_b,
        file_paths=file_paths,
        cleaned_files=cleaned_files,
        worktree_a=str(worktree_a),
        worktree_b=str(worktree_b),
    )