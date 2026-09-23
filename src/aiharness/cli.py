"""Thin CLI that composes the aiharness hello-world node.

The CLI holds no business logic — it parses arguments, delegates to the library
node, formats output (human-readable or JSON), and maps results to exit codes.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from dotenv import load_dotenv

from aiharness.nodes.hello_world import build_hello_world_node

_USAGE = "usage: aiharness-hello [hello] <text> [--format text|json] [--dry-run]"

# Load optional LANGSMITH_* (and other) vars from a local .env if present.
# Does not override already-set environment variables. Runs before any
# LangSmith tracing is initialized so a filled .env takes effect.
load_dotenv()


def build_parser() -> argparse.ArgumentParser:
    """CLI parser: options anywhere, `hello` verb tolerated (see main)."""
    parser = argparse.ArgumentParser(
        prog="aiharness-hello",
        description="Greet <text> via the hello-world node.",
    )
    parser.add_argument(
        "positionals",
        nargs="*",
        help="optional leading 'hello' verb followed by <text>",
    )
    parser.add_argument(
        "--format",
        default="text",
        help="output format: text|json (default: text)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the planned output and change nothing",
    )
    return parser


def _emit_output(result: dict, fmt: str, dry_run: bool) -> None:
    """Print the node result honoring format and dry-run."""
    if fmt == "json":
        payload: dict = {"input": result["input"], "greeting": result["greeting"]}
        if dry_run:
            payload["dry_run"] = True
        print(json.dumps(payload))
    elif dry_run:
        print(f"dry-run: {result['greeting']}")
    else:
        print(result["greeting"])


def main(argv: Sequence[str] | None = None) -> int:
    """Run the hello-world CLI entry point and return an exit code.

    Exit codes: 0 success, 1 usage error, 4 unexpected runtime failure.
    """
    raw_args = list(sys.argv[1:] if argv is None else argv)

    try:
        args = build_parser().parse_args(raw_args)
    except SystemExit as exc:
        # argparse UX (usage errors -> 2, --help -> 0) mapped to CLI codes.
        return 1 if exc.code != 0 else 0
    fmt, positionals, dry_run = args.format, list(args.positionals), args.dry_run

    if fmt not in ("text", "json"):
        print(f"error: --format must be text|json, got {fmt!r}", file=sys.stderr)
        print(_USAGE, file=sys.stderr)
        return 1

    # Tolerate an optional leading `hello` verb.
    if positionals and positionals[0] == "hello":
        positionals = positionals[1:]

    if len(positionals) != 1:
        print("error: expected exactly one <text> argument", file=sys.stderr)
        print(_USAGE, file=sys.stderr)
        return 1

    text = positionals[0]
    node = build_hello_world_node()
    try:
        result = node.invoke(text)
    except ValueError:
        # Empty/whitespace-only input -> usage error.
        print("error: <text> must be non-empty", file=sys.stderr)
        return 1
    except Exception:  # noqa: BLE001 - CLI boundary maps unexpected failures to exit 4
        print("error: unexpected failure", file=sys.stderr)
        return 4

    _emit_output(result, fmt, dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())