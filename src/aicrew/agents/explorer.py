"""Repo-exploring coder: gathers repo context deterministically before generating.

A real agent loop (``create_react_agent`` + tool-calling) is unreliable across
providers/models (many don't expose ``bind_tools`` cleanly), so this "explorer"
uses a **bounded, deterministic scout**: it walks the repo (explicit ``--context``
files plus auto-conservative discovery: files in the target's directory, sibling
tests/factories, and a project/README) and injects the gathered text into the
coder prompt — giving the coder real repo context without depending on model
tool-calling. Mirrors SwarmForge's coder living in its worktree, but robustly.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from aicrew.agents import coder as coder_agents
from aicrew.agents import repo as repo_scm

Explorer = Callable[[str], str]

# Source-ish files worth including in auto-discovery.
_SOURCE_EXT = {".cs", ".py", ".ts", ".js", ".tsx", ".jsx", ".go", ".rs", ".java", ".kt"}
_SIBLING_CAP = 12           # max sibling files to pull in
_CONTEXT_CAP = 9000         # max total context chars fed to the model


def _source_siblings(root: Path, target_dir: str, target_name: str) -> list[str]:
    """Direct sibling source files of the target, up to a cap (no trailing dirs)."""
    base = root / target_dir if target_dir else root
    try:
        entries = sorted(base.iterdir())
    except OSError:
        return []
    out: list[str] = []
    for child in entries:
        if (
            child.is_file()
            and child.suffix in _SOURCE_EXT
            and child.name != target_name
        ):
            out.append(child.relative_to(root).as_posix())
            if len(out) >= _SIBLING_CAP:
                break
    return out


def _auto_discover(root: Path, target_file: str) -> list[str]:
    """Return repo-relative files likely relevant to ``target_file``."""
    target = Path(target_file)
    found = _source_siblings(root, target.parent.as_posix(), target.name)
    for candidate in ("README.md", "README", "project.md"):
        if (root / candidate).is_file() and candidate not in found:
            found.append(candidate)
    return found


def _gather_context(
    root: Path, target_file: str, context_files: list[str] | None
) -> str:
    seen: set[str] = set()
    blocks: list[str] = []
    total = 0

    def add(rel: str) -> None:
        nonlocal total
        if rel in seen:
            return
        seen.add(rel)
        try:
            content = repo_scm.read_file(root, rel)
        except (repo_scm.RepoError, OSError):
            return
        block = f"### {rel}\n{content}"
        if total + len(block) > _CONTEXT_CAP:
            return
        blocks.append(block)
        total += len(block)

    for rel in context_files or []:
        add(rel)
    for rel in _auto_discover(root, target_file):
        add(rel)
    return "\n\n".join(blocks)


def build_explorer_coder(
    root: str | Path,
    *,
    provider: str = "openrouter",
    model: str | None = None,
    target_file: str = "",
    context_files: list[str] | None = None,
) -> Explorer:
    """Return ``(task) -> code``: the coder generates after exploring the repo."""
    root = Path(root)
    chat = coder_agents.default_chat(provider, model)

    def run(task: str) -> str:
        context = _gather_context(root, target_file, context_files)
        return coder_agents.generate_code(task, chat, context)

    return run