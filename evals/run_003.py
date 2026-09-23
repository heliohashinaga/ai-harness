"""Pilot runner for evals/003: coder-only (A) vs coder+cleaner (B).

Uses the REAL graph code with provider chats. Writes a results skeleton to
evals/results/003-cleaner-pilot.md for the operator to finalize.
Offline parts (extraction, exec, hidden tests) are deterministic; LLM calls
are not — this is a pilot (N=3, one run each), not a significance test.
"""

from __future__ import annotations

import os
import re
import time

os.environ["LANGSMITH_TRACING"] = "false"

from agentcrew.agents.cleaner import default_chat as cleaner_default_chat  # noqa: E402
from agentcrew.agents.coder import default_chat as coder_default_chat  # noqa: E402
from agentcrew.graphs.coder_cleaner import build_coder_cleaner_graph  # noqa: E402

MODEL = "deepseek-v4-flash"
PROVIDER = "opencode"

PROMPTS = {
    "P1": (
        "write a python function fib(n) that returns the nth fibonacci "
        "number (0-indexed: fib(0)=0, fib(1)=1). Return ONLY the code."
    ),
    "P2": (
        "write a python function dedup(items) that returns a list with "
        "duplicates removed, preserving first-occurrence order. "
        "Return ONLY the code."
    ),
    "P3": (
        "write a python function chunks(lst, n) that splits a list into "
        "chunks of size n; the last chunk may be shorter; n>=1. "
        "Return ONLY the code."
    ),
}

CHECKS = {
    "P1": (
        "fib",
        ["fib(0)==0", "fib(1)==1", "fib(2)==1", "fib(10)==55", "fib(20)==6765"],
    ),
    "P2": (
        "dedup",
        [
            "dedup([3,1,3,2,1])==[3,1,2]",
            "dedup([])==[]",
            "dedup('abac')==['a','b','c']",
        ],
    ),
    "P3": (
        "chunks",
        [
            "chunks([1,2,3,4,5],2)==[[1,2],[3,4],[5]]",
            "chunks([],3)==[]",
            "chunks([1],1)==[[1]]",
        ],
    ),
}


def extract(code: str) -> str:
    m = re.search(r"```(?:python)?\s*(.*?)```", code, re.S)
    return (m.group(1) if m else code).strip()


def grade(pid: str, code: str) -> tuple[bool, str]:
    name, asserts = CHECKS[pid]
    ns: dict = {}
    try:
        exec(compile(extract(code), "<gen>", "exec"), ns)  # noqa: S102 - eval pilot
    except Exception as exc:  # noqa: BLE001
        return False, f"exec failed: {type(exc).__name__}: {exc}"
    if name not in ns:
        return False, f"function {name!r} not defined"
    glb = dict(ns)
    for check in asserts:
        try:
            assert eval(check, glb)  # noqa: S307 - eval pilot
        except Exception as exc:  # noqa: BLE001
            return False, f"{check} -> {type(exc).__name__}: {exc}"
    return True, "all hidden tests pass"


def run(pid: str, with_cleaner: bool) -> dict:
    coder_chat = coder_default_chat(PROVIDER, MODEL)
    cleaner_chat = cleaner_default_chat(PROVIDER, MODEL) if with_cleaner else None
    graph = build_coder_cleaner_graph(
        coder_chat=coder_chat, cleaner_chat=cleaner_chat, provider=PROVIDER, model=MODEL
    )
    state = {
        "task": PROMPTS[pid],
        "coder_output": "",
        "cleaner_output": "",
        "error": None,
    }
    t0 = time.perf_counter()
    out = graph.invoke(state)
    latency_ms = int((time.perf_counter() - t0) * 1000)
    final = out.get("cleaner_output", "")
    ok, detail = grade(pid, final)
    return {
        "ok": ok,
        "detail": detail,
        "latency_ms": latency_ms,
        "calls": 2 if with_cleaner else 1,
        "changed": out.get("coder_output", "") != final,
        "output": extract(final)[:600],
    }


def main() -> None:
    lines = [
        "# 003 — cleaner pilot results",
        "",
        f"model={MODEL} provider={PROVIDER}",
        "",
    ]
    for pid in ("P1", "P2", "P3"):
        for cfg, with_cleaner in (("A coder-only", False), ("B coder+cleaner", True)):
            try:
                r = run(pid, with_cleaner)
                status = "PASS" if r["ok"] else "FAIL"
                lines.append(
                    f"- {pid} {cfg}: {status} ({r['detail']}) "
                    f"calls={r['calls']} latency={r['latency_ms']}ms "
                    f"cleaner_changed={r['changed']}"
                )
            except Exception as exc:  # noqa: BLE001
                lines.append(f"- {pid} {cfg}: ERROR {type(exc).__name__}: {exc}")
    lines.append("")
    lines.append("## Outputs (truncated, operator: finalize verdict)")
    path = os.path.join("evals", "results", "003-cleaner-pilot.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
