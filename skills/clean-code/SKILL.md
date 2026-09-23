---
name: clean-code
description: |
  Semantic clean-code standards for generated code: intent-revealing names,
  small single-purpose functions, honest comments, no dead code.
  Formatting is explicitly out of scope (ruff owns it).
---

# Clean Code Skill (project)

Apply when a Task is a refactor, when the complexity gate fails, or when the
Verdict flags naming/cohesion. Do NOT apply formatting by hand — run `ruff`.

## Standards (semantic only)

- Use descriptive, intent-revealing names; keep a consistent vocabulary.
- Keep functions small and doing one thing; extract the rest;
  prefer early returns.
- Keep comments for WHY (intent, trade-offs), not for restating code.
- Remove redundant comments, commented-out blocks, and dead code.
- If in doubt, prefer the smaller, safer change.

## Boundary

Formatting (`ruff`) is deterministic and stays outside this skill.
Behavior changes are out of scope — same language, same observable results.
