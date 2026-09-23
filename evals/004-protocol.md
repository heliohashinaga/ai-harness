# 004 Protocol — cleaner retest on frozen buggy outputs (pre-registered)

Follows from 003 (cleaner rejected as default: 3/3 vs 3/3, coder had nothing
to fix). This protocol freezes the buggy-output set the retest will run
against. Frozen before running experiment 004.

Hidden tests are reused **verbatim** from `003-protocol.md` (P1–P3 checks) —
they are not edited to favor any candidate. Buggy samples are frozen
constants; the executable copy lives in
`tests/unit/test_buggy_cases_004.py` (same md ↔ code split as
003-protocol.md ↔ `run_003.py`).

## Triples

- **B1 (fib, wrong base init):** task = P1 prompt.
  Buggy:
  ```python
  def fib(n):
      a, b = 1, 1
      for _ in range(n):
          a, b = b, a + b
      return a
  ```
  Hidden: `fib(0)==0`, `fib(1)==1`, `fib(2)==1`, `fib(10)==55`,
  `fib(20)==6765`. Documented failure: `fib(0)==0` (returns 1).

- **B2 (fib, wrong recurrence):** task = P1 prompt.
  Buggy:
  ```python
  def fib(n):
      if n <= 1:
          return n
      return fib(n - 1) + fib(n - 3)
  ```
  Hidden: same P1 set. Documented failure: `fib(2)==1` (returns 0).

- **B3 (dedup, keeps last occurrence):** task = P2 prompt.
  Buggy:
  ```python
  def dedup(items):
      seen = set()
      out = []
      for x in reversed(list(items)):
          if x not in seen:
              seen.add(x)
              out.append(x)
      return out
  ```
  Hidden: `dedup([3,1,3,2,1])==[3,1,2]`, `dedup([])==[]`,
  `dedup('abac')==['a','b','c']`.
  Documented failure: `dedup([3,1,3,2,1])==[3,1,2]` (returns `[1,2,3]`).

- **B4 (dedup, None on empty):** task = P2 prompt.
  Buggy:
  ```python
  def dedup(items):
      return list(dict.fromkeys(items)) if items else None
  ```
  Hidden: same P2 set. Documented failure: `dedup([])==[]` (returns `None`).

- **B5 (chunks, drops remainder):** task = P3 prompt.
  Buggy:
  ```python
  def chunks(lst, n):
      return [lst[i:i + n] for i in range(0, len(lst) - len(lst) % n, n)]
  ```
  Hidden: `chunks([1,2,3,4,5],2)==[[1,2],[3,4],[5]]`, `chunks([],3)==[]`,
  `chunks([1],1)==[[1]]`.
  Documented failure: `chunks([1,2,3,4,5],2)==[[1,2],[3,4],[5]]`
  (returns `[[1,2],[3,4]]`).

- **B6 (chunks, [[]] on empty):** task = P3 prompt.
  Buggy:
  ```python
  def chunks(lst, n):
      if not lst:
          return [[]]
      return [lst[i:i + n] for i in range(0, len(lst), n)]
  ```
  Hidden: same P3 set. Documented failure: `chunks([],3)==[]`
  (returns `[[]]`).

## Verdict rule (for experiment 004)

Feed each buggy sample to the cleaner (coder output fixed, no coder call)
and grade the cleaned code against the same hidden tests. Promote the
cleaner to default only if it fixes a clear majority of the 6 without
breaking the already-passing checks. Otherwise the 003 verdict stands.
