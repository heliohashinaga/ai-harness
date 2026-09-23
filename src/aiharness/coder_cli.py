"""Thin CLI composing the coder node (coder-only, single LLM call).

Mirrors the ``aiharness-hello`` / ``aiharness-llm`` CLI shape: exit codes
``0`` success, ``1`` usage, ``4`` runtime. It composes the library node and
never holds business logic (constitution Principle I).

Coder-only since TASK-009 (second hop rejected as default in evals 003/004;
the clean-code skill survives as a coder prompt pack).
"""

from __future__ import annotations

import json
import sys
from collections.abc import Sequence

from aiharness.agents import coder as coder_agents
from aiharness.agents import repo as repo_scm
from aiharness.agents.repo_runner import run_repo_pipeline
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


def _run_repo_mode(options: dict[str, str], provider: str, task: str) -> int:
    """Run repo mode (single coder worktree + commit). Returns exit code."""
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
            f"coder branch {result.branch_a} commit {result.commit_c[:8]} "
            f"wrote {len(result.file_paths)} file(s): "
            f"{', '.join(result.file_paths)}"
        )
        print(f"see: worktree {result.worktree_a}")
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
    """Execute text mode: run the coder node once. Returns exit code."""
    try:
        node = coder_agents.build_coder_node(provider=provider, model=model)
        result = node({"task": task})
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
                    "model": model or provider,
                }
            )
        )
    else:
        print(result["coder_output"])
    return 0

if __name__ == "__main__":
    sys.exit(main())
