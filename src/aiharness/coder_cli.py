"""Thin CLI composing the coder->cleaner pipeline graph.

Mirrors the ``aiharness-hello`` / ``aiharness-llm`` CLI shape: exit codes
``0`` success, ``1`` usage, ``4`` runtime. It composes the library graph and
never holds business logic (constitution Principle I).
"""

from __future__ import annotations

import json
import sys
from collections.abc import Sequence

from aiharness.agents import cleaner as cleaner_agents
from aiharness.agents import coder as coder_agents
from aiharness.agents import repo as repo_scm
from aiharness.agents.clean_code_policy import read_clean_code_policy
from aiharness.agents.repo_runner import run_repo_pipeline
from aiharness.graphs.coder_cleaner import build_coder_cleaner_graph
from aiharness.nodes import llm as llm_nodes

_USAGE = (
    "usage: aiharness-code [--provider openrouter|opencode] "
    "[--model NAME] [--format text|json] "
    "[--repo <local-path> [--branch NAME] [--file RELPATH]] <task>"
)

_PROVIDER_KEY_ENV = {
    "openrouter": "OPENROUTER_API_KEY",
    "opencode": "OPENCODE_GO_API_KEY",
}

_VALUE_FLAGS = (
    "--provider", "--model", "--format", "--repo", "--branch", "--file", "--context"
)


def _parse(argv: list[str]) -> tuple[dict[str, str], list[str]]:
    options: dict[str, str] = {}
    positions: list[str] = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in _VALUE_FLAGS:
            if i + 1 >= len(argv):
                raise ValueError(f"{arg} requires a value")
            value = argv[i + 1]
            if arg == "--context":
                options["contexts"] = _join_ctx(options.get("contexts", ""), value)
            else:
                options[arg[2:]] = value
            i += 2
        elif any(arg.startswith(f"{f}=") for f in _VALUE_FLAGS):
            name, _, value = arg.partition("=")
            if name == "--context":
                options["contexts"] = _join_ctx(options.get("contexts", ""), value)
            else:
                options[name[2:]] = value
            i += 1
        else:
            positions.append(arg)
            i += 1
    return options, positions


def _join_ctx(existing: str, value: str) -> str:
    """Join context paths with commas, tolerating repeated/`=` forms."""
    return ",".join(part for part in [existing, value] if part)


def _build_graph(provider: str, model: str | None):
    coder_chat = coder_agents.default_chat(provider, model)
    cleaner_chat = cleaner_agents.default_chat(provider, model)
    return build_coder_cleaner_graph(
        coder_chat=coder_chat,
        cleaner_chat=cleaner_chat,
        provider=provider,
        model=model,
        # Honor the clean-code skill (SKILL.md) when present; else bundled policy.
        cleaner_policy=read_clean_code_policy(),
    )


def _run_repo_mode(options: dict[str, str], provider: str, task: str) -> int:
    """Run repo mode (worktrees + commit->merge). Returns exit code."""
    try:
        result = run_repo_pipeline(
            options["repo"],
            options.get("branch", "HEAD"),
            task,
            options.get("file") or "",
            provider=provider,
            model=options.get("model"),
            context_files=_context_list(options),
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        print(_USAGE, file=sys.stderr)
        return 1
    except repo_scm.RepoError as exc:
        print(f"error: repo: {exc}", file=sys.stderr)
        return 4
    except Exception as exc:  # noqa: BLE001 - CLI boundary -> exit 4
        print(f"error: pipeline failed: {exc}", file=sys.stderr)
        return 4

    if options.get("format", "text") == "json":
        print(json.dumps(result.as_dict()))
    else:
        print(
            f"cleaner branch {result.branch_b} commit {result.commit_b[:8]} "
            f"cleaned {len(result.cleaned_files)} file(s): "
            f"{', '.join(result.cleaned_files)}"
        )
        print(f"see: worktree {result.worktree_b}")
    return 0


def _context_list(options: dict[str, str]) -> list[str]:
    """Split the accumulated ``--context`` list into repo-relative paths."""
    raw = options.get("contexts", "")
    return [p for p in (raw.split(",") if raw else []) if p.strip()]


def main(argv: Sequence[str] | None = None) -> int:
    raw_args = list(sys.argv[1:] if argv is None else argv)

    try:
        options, positionals = _parse(raw_args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        print(_USAGE, file=sys.stderr)
        return 1

    provider = options.get("provider", "openrouter")
    if provider not in _PROVIDER_KEY_ENV:
        print(f"error: unsupported provider {provider!r}", file=sys.stderr)
        print(_USAGE, file=sys.stderr)
        return 1

    if len(positionals) != 1:
        print("error: expected exactly one <task> argument", file=sys.stderr)
        print(_USAGE, file=sys.stderr)
        return 1
    task = positionals[0]

    if not llm_nodes.provider_api_key(provider):
        print(
            f"error: no API key configured for provider {provider!r}; "
            f"set {_PROVIDER_KEY_ENV[provider]} in your .env",
            file=sys.stderr,
        )
        return 4

    if options.get("repo"):
        return _run_repo_mode(options, provider, task)
    return _run_text_mode(
        provider, options.get("model"), task, options.get("format", "text")
    )


def _run_text_mode(provider: str, model: str | None, task: str, fmt: str) -> int:
    """Execute text mode: compose the graph over a task string. Returns exit code."""
    try:
        graph = _build_graph(provider, model)
        result = graph.invoke({"task": task})
    except ValueError:
        print("error: <task> must be non-empty", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 - CLI boundary maps failures to exit 4
        print(f"error: pipeline failed: {exc}", file=sys.stderr)
        return 4

    if fmt == "json":
        print(
            json.dumps(
                {
                    "task": task,
                    "coder_output": result["coder_output"],
                    "cleaner_output": result["cleaner_output"],
                    "model": model or provider,
                }
            )
        )
    else:
        print(result["cleaner_output"])
    return 0

if __name__ == "__main__":
    sys.exit(main())
