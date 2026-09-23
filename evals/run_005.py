"""Runner for evals/005: coder-only (A) vs coder+clean-code-skill (B).

Both configs cost 1 LLM call — the skill is a prompt pack inside the coder
prompt (``context=``), a single coder node. Uses the REAL coder
node with provider chats. Writes the measured record plus the verdict to
``evals/results/005-clean-code-skill.md``.

Offline parts (extraction, exec, hidden tests, ruff) are deterministic;
LLM calls are not — this is a pilot (N=3, one run each), not a significance
test. Skill text comes from the project file when present
(``skills/clean-code/SKILL.md`` via ``read_clean_code_policy()``), else the
bundled ``CLEAN_CODE_POLICY`` constant.
"""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
import time
from pathlib import Path

os.environ["LANGSMITH_TRACING"] = "false"

from aiharness.agents.clean_code_policy import read_clean_code_policy  # noqa: E402
from aiharness.agents.coder import build_coder_node  # noqa: E402
from aiharness.agents.coder import default_chat as coder_default_chat  # noqa: E402
from aiharness.nodes import llm as llm_nodes  # noqa: E402

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


def ruff_ok(code: str) -> bool:
    with tempfile.NamedTemporaryFile(
        "w", suffix=".py", delete=False, encoding="utf-8"
    ) as fh:
        fh.write(extract(code) + "\n")
        path = fh.name
    try:
        proc = subprocess.run(
            ["uv", "run", "ruff", "check", path],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return proc.returncode == 0
    except Exception:  # noqa: BLE001 - ruff failure counts as not-ok
        return False
    finally:
        os.unlink(path)


def run(pid: str, skill_context: str | None) -> dict:
    from aiharness.agents.coder import generate_code

    chat = coder_default_chat(PROVIDER, MODEL)
    t0 = time.perf_counter()
    if skill_context:
        code = generate_code(PROMPTS[pid], chat, context=skill_context)
    else:
        node = build_coder_node(chat=chat, provider=PROVIDER, model=MODEL)
        code = node({"task": PROMPTS[pid]})["coder_output"]
    latency_ms = int((time.perf_counter() - t0) * 1000)
    ok, detail = grade(pid, code)
    return {
        "ok": ok,
        "detail": detail,
        "latency_ms": latency_ms,
        "calls": 1,
        "ruff": ruff_ok(code),
        "output": extract(code)[:600],
    }


def main() -> None:
    lines = [
        "# 005 — clean-code skill results",
        "",
        f"model={MODEL} provider={PROVIDER} (1 call both sides; skill is prompt pack)",
        "",
    ]
    if not llm_nodes.provider_api_key(PROVIDER):
        lines.append(
            f"ERROR: no provider API key for {PROVIDER!r}; "
            "no LLM ran, no verdict. Set the key and re-run."
        )
    else:
        try:
            skill_text = read_clean_code_policy()
            skill_src = "skills/clean-code/SKILL.md" if (
                Path("skills/clean-code/SKILL.md").is_file()
            ) else "bundled CLEAN_CODE_POLICY"
        except Exception as exc:  # noqa: BLE001 - record, never fake
            lines.append(f"ERROR loading skill: {type(exc).__name__}: {exc}")
            skill_text = ""
            skill_src = "load-failed"
        lines.append(f"skill_source={skill_src} chars={len(skill_text)}")
        lines.append("")
        if skill_text:
            wins = {"A": 0, "B": 0}
            regressions: list[str] = []
            for pid in ("P1", "P2", "P3"):
                results = {}
                for cfg, ctx in (("A coder-only", None), ("B coder+skill", skill_text)):
                    try:
                        results[cfg] = run(pid, ctx)
                    except Exception as exc:  # noqa: BLE001
                        lines.append(
                            f"- {pid} {cfg}: ERROR {type(exc).__name__}: {exc}"
                        )
                        continue
                for cfg in ("A coder-only", "B coder+skill"):
                    r = results.get(cfg)
                    if r is None:
                        continue
                    status = "PASS" if r["ok"] else "FAIL"
                    key = "A" if cfg.startswith("A ") else "B"
                    wins[key] += r["ok"]
                    lines.append(
                        f"- {pid} {cfg}: {status} ({r['detail']}) "
                        f"calls=1 latency={r['latency_ms']}ms ruff={r['ruff']}"
                    )
                ra, rb = results.get("A coder-only"), results.get("B coder+skill")
                if ra and rb and ra["ok"] and not rb["ok"]:
                    regressions.append(pid)
            lines.append("")
            lines.append(f"Correctness A {wins['A']}/3, B {wins['B']}/3.")
            if wins["B"] >= wins["A"] and not regressions:
                lines.append(
                    "## Verdict (auto): correctness held at flat cost; "
                    "OPERATOR readability check required before any "
                    "promote (per 005-protocol rule). Default: stays OPT-IN."
                )
            else:
                lines.append(
                    "## Verdict: skill stays OPT-IN (refactors, "
                    "complexity-gate failures, Verdict-flagged naming; "
                    "per 005-protocol rule)."
                )
    path = os.path.join("evals", "results", "005-clean-code-skill.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
