"""Unit tests for the project clean-code skill (offline, no network)."""

from pathlib import Path

import pytest

from aiharness.agents.clean_code_policy import (
    CLEAN_CODE_POLICY,
    read_clean_code_policy,
)

pytestmark = pytest.mark.unit

SKILL = Path(__file__).resolve().parents[2] / "skills" / "clean-code" / "SKILL.md"


def test_project_skill_file_exists():
    assert SKILL.is_file(), "skills/clean-code/SKILL.md must exist (005 candidate)"


def test_project_skill_loads_semantic_policy():
    body = read_clean_code_policy(source=SKILL)
    lower = body.lower()
    assert "intent-revealing" in lower
    assert "ruff" in lower  # boundary: formatting stays with the formatter


def test_coder_prompt_carries_skill_as_context():
    from aiharness.agents.coder import generate_code

    seen: list[str] = []
    policy = read_clean_code_policy(source=SKILL)
    generate_code("task", lambda p: (seen.append(p), "code")[1], context=policy)
    assert seen and "intent-revealing" in seen[0].lower()


def test_read_policy_strips_frontmatter(tmp_path):
    f = tmp_path / "SKILL.md"
    f.write_text("---\nname: clean-code\n---\nApply good names.", encoding="utf-8")
    assert read_clean_code_policy(source=f) == "Apply good names."


def _bullets(text: str) -> list[str]:
    """Semantic bullet lines, normalized for comparison."""
    return [
        " ".join(line[1:].split())
        for line in text.splitlines()
        if line.strip().startswith("-")
    ]


def test_bundled_fallback_covers_skill_standards():
    """Every fallback bullet must exist in the live SKILL.md.

    The skill file may grow docs, but the bundled fallback can never go
    stale silently: drift fails here, deterministically.
    """
    body = " ".join(read_clean_code_policy(source=SKILL).split())
    missing = [b for b in _bullets(CLEAN_CODE_POLICY) if b not in body]
    assert not missing, f"fallback stale, missing from SKILL.md: {missing}"
