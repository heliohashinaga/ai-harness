# TASK-008 — Minor hardening: lazy coder + non-str-tolerant cleaner

## Goal

Two leftovers from the cleaner review (previous session):
1. `build_coder_node(chat=None)` builds the LLM client at *build* time and
   blows up without credentials — the error should surface at *invoke*
   time (the coder has no pass-through mode, but building the graph
   offline should work).
2. `clean_code_text` handles `chat` exceptions, but if `chat` returns a
   non-`str` (e.g. `None`), the `None` escapes the fail-safe and breaks
   `CleanerOutput` validation.

## Context

- `src/aiharness/agents/coder.py`: `effective = ... default_chat(...)` in
  the builder body; `coder_node` uses `effective`.
- `src/aiharness/agents/cleaner.py`: `clean_code_text` returns
  `chat(...)` directly inside the `try`.
- Test pattern: `tests/unit/test_cleaner.py`
  (`test_cleaner_builds_offline_without_credentials` with
  `monkeypatch.delenv`).

## Acceptance Criteria

- [ ] `build_coder_node()` without `chat` builds without credentials; the
  (keyless) failure happens on invoke, not on build. A keyless test
  proves both behaviors.
- [ ] `clean_code_text` (and the node) with a `chat` returning
  `None`/non-`str` returns the input code unchanged. A test proves it.
- [ ] `.\scripts\verify.ps1` passes; no new dependency.

## Constraints

- Minimal diff; no unrelated rewrites.
- `default_chat` keeps existing (CLI/runners use it directly).
