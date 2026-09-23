"""Runner for evals/004: cleaner retest on frozen buggy outputs.

Feeds each frozen sample from `evals/004-protocol.md` to the REAL cleaner
node (coder output fixed, no coder call) and grades the cleaned code against
the same hidden tests. Writes the measured record plus the pre-registered
verdict to `evals/results/004-cleaner-retest.md`.

Single executable copy of the data: TRIPLES and the exec/eval graders are
imported from `tests/unit/test_buggy_cases_004.py` (no third copy).
"""

from __future__ import annotations

import importlib.util
import os
import re
import time
from pathlib import Path

os.environ["LANGSMITH_TRACING"] = "false"

from aiharness.agents.cleaner import build_cleaner_node  # noqa: E402
from aiharness.agents.cleaner import default_chat as cleaner_default_chat  # noqa: E402
from aiharness.nodes import llm as llm_nodes  # noqa: E402

MODEL = "deepseek-v4-flash"
PROVIDER = "opencode"

_CASES_PATH = (
    Path(__file__).resolve().parent.parent
    / "tests"
    / "unit"
    / "test_buggy_cases_004.py"
)


def _load_cases():
    """Import the frozen executable copy (TRIPLES + graders) from the unit test."""
    spec = importlib.util.spec_from_file_location("cases_004_frozen", _CASES_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.TRIPLES, mod._namespace, mod._check_passes


def extract(code: str) -> str:
    m = re.search(r"```(?:python)?\s*(.*?)```", code, re.S)
    return (m.group(1) if m else code).strip()


def run(case_id, code, checks, failing, cleaner, namespace, passes) -> dict:
    state = {
        "task": f"clean frozen buggy sample {case_id}",
        "coder_output": code,
        "cleaner_output": "",
        "error": None,
    }
    t0 = time.perf_counter()
    out = cleaner(state)
    latency_ms = int((time.perf_counter() - t0) * 1000)
    refined = extract(out.get("cleaner_output", ""))
    before = [c for c in checks if passes(namespace(code), c)]
    after_ns = namespace(refined)
    after = [c for c in checks if passes(after_ns, c)]
    return {
        "fixed": failing in after,
        "regressions": [c for c in before if c not in after],
        "changed": refined != code.strip(),
        "latency_ms": latency_ms,
        "output": refined[:600],
    }


def main() -> None:
    triples, namespace, passes = _load_cases()
    lines = [
        "# 004 — cleaner retest results",
        "",
        f"model={MODEL} provider={PROVIDER} (coder output fixed, no coder call)",
        "",
    ]
    if not llm_nodes.provider_api_key(PROVIDER):
        lines.append(
            f"ERROR: no provider API key for {PROVIDER!r}; "
            "no LLM ran, no verdict. Set the key and re-run."
        )
    else:
        cleaner = build_cleaner_node(
            chat=cleaner_default_chat(PROVIDER, MODEL),
            provider=PROVIDER,
            model=MODEL,
        )
        fixed = 0
        regressions: list[str] = []
        for case_id, _name, code, checks, failing in triples:
            try:
                r = run(case_id, code, checks, failing, cleaner, namespace, passes)
            except Exception as exc:  # noqa: BLE001 - record, never fake
                lines.append(f"- {case_id}: ERROR {type(exc).__name__}: {exc}")
                continue
            status = "FIXED" if r["fixed"] else "STILL-BROKEN"
            fixed += r["fixed"]
            regressions.extend(f"{case_id}:{c}" for c in r["regressions"])
            lines.append(
                f"- {case_id}: {status} (documented check "
                f"{'now passes' if r['fixed'] else 'still fails'}) "
                f"changed={r['changed']} latency={r['latency_ms']}ms "
                f"regressions={len(r['regressions'])}"
            )
        lines.append("")
        lines.append(f"Fixed {fixed}/{len(triples)}, regressions {len(regressions)}.")
        if fixed >= 4 and not regressions:
            lines.append(
                "## Verdict: PROMOTE cleaner discussion — majority fixed, "
                "nothing broken (per 004-protocol rule)."
            )
        else:
            lines.append(
                "## Verdict: 003 verdict STANDS — cleaner stays opt-in "
                "(per 004-protocol rule)."
            )
    path = os.path.join("evals", "results", "004-cleaner-retest.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
