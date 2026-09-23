"""Frozen buggy-output set for experiment 004 (cleaner retest).

Executable copy of `evals/004-protocol.md` (same md <-> code split as
003-protocol.md <-> run_003.py). All samples are frozen constants — no LLM
in the loop. Grading follows the exec/eval style of `run_003.grade`.
"""

import pytest

pytestmark = pytest.mark.unit

FIB_CHECKS = [
    "fib(0)==0",
    "fib(1)==1",
    "fib(2)==1",
    "fib(10)==55",
    "fib(20)==6765",
]

DEDUP_CHECKS = [
    "dedup([3,1,3,2,1])==[3,1,2]",
    "dedup([])==[]",
    "dedup('abac')==['a','b','c']",
]

CHUNKS_CHECKS = [
    "chunks([1,2,3,4,5],2)==[[1,2],[3,4],[5]]",
    "chunks([],3)==[]",
    "chunks([1],1)==[[1]]",
]

# (case id, function name, buggy code, hidden checks, documented failing check)
TRIPLES = [
    (
        "B1",
        "fib",
        "def fib(n):\n"
        "    a, b = 1, 1\n"
        "    for _ in range(n):\n"
        "        a, b = b, a + b\n"
        "    return a\n",
        FIB_CHECKS,
        "fib(0)==0",
    ),
    (
        "B2",
        "fib",
        "def fib(n):\n"
        "    if n <= 1:\n"
        "        return n\n"
        "    return fib(n - 1) + fib(n - 3)\n",
        FIB_CHECKS,
        "fib(2)==1",
    ),
    (
        "B3",
        "dedup",
        "def dedup(items):\n"
        "    seen = set()\n"
        "    out = []\n"
        "    for x in reversed(list(items)):\n"
        "        if x not in seen:\n"
        "            seen.add(x)\n"
        "            out.append(x)\n"
        "    return out\n",
        DEDUP_CHECKS,
        "dedup([3,1,3,2,1])==[3,1,2]",
    ),
    (
        "B4",
        "dedup",
        "def dedup(items):\n"
        "    return list(dict.fromkeys(items)) if items else None\n",
        DEDUP_CHECKS,
        "dedup([])==[]",
    ),
    (
        "B5",
        "chunks",
        "def chunks(lst, n):\n"
        "    return [lst[i:i + n] for i in range(0, len(lst) - len(lst) % n, n)]\n",
        CHUNKS_CHECKS,
        "chunks([1,2,3,4,5],2)==[[1,2],[3,4],[5]]",
    ),
    (
        "B6",
        "chunks",
        "def chunks(lst, n):\n"
        "    if not lst:\n"
        "        return [[]]\n"
        "    return [lst[i:i + n] for i in range(0, len(lst), n)]\n",
        CHUNKS_CHECKS,
        "chunks([],3)==[]",
    ),
]

# Reference solutions proving each hidden-test set is satisfiable.
REFERENCE = {
    "fib": (
        "def fib(n):\n"
        "    a, b = 0, 1\n"
        "    for _ in range(n):\n"
        "        a, b = b, a + b\n"
        "    return a\n",
        FIB_CHECKS,
    ),
    "dedup": (
        "def dedup(items):\n"
        "    seen = set()\n"
        "    out = []\n"
        "    for x in items:\n"
        "        if x not in seen:\n"
        "            seen.add(x)\n"
        "            out.append(x)\n"
        "    return out\n",
        DEDUP_CHECKS,
    ),
    "chunks": (
        "def chunks(lst, n):\n"
        "    return [lst[i:i + n] for i in range(0, len(lst), n)]\n",
        CHUNKS_CHECKS,
    ),
}


def _namespace(code: str) -> dict:
    ns: dict = {}
    exec(compile(code, "<frozen>", "exec"), ns)  # noqa: S102 - frozen fixtures
    return ns


def _check_passes(ns: dict, check: str) -> bool:
    try:
        return bool(eval(check, dict(ns)))  # noqa: S307 - frozen fixtures
    except Exception:  # noqa: BLE001 - any error means the check fails
        return False


@pytest.mark.parametrize(
    ("case_id", "name", "code", "checks", "failing"), TRIPLES
)
def test_buggy_sample_fails_its_documented_check(
    case_id, name, code, checks, failing
):
    ns = _namespace(code)
    assert name in ns, f"{case_id}: function {name!r} not defined"
    assert failing in checks, f"{case_id}: documented check not in hidden set"
    assert not _check_passes(ns, failing), (
        f"{case_id}: documented check {failing!r} unexpectedly passes — "
        "sample is not buggy"
    )


def test_buggy_set_has_at_least_five_triples():
    assert len(TRIPLES) >= 5


@pytest.mark.parametrize(("name", "case"), list(REFERENCE.items()))
def test_hidden_checks_are_satisfiable(name, case):
    code, checks = case
    ns = _namespace(code)
    assert name in ns
    failed = [c for c in checks if not _check_passes(ns, c)]
    assert not failed, f"{name}: reference fails {failed} — hidden tests impossible"
