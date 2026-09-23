"""Unit tests for project skills (offline, no network)."""

from importlib import resources

import pytest

from aiharness.skills import read_skill

pytestmark = pytest.mark.unit


def test_packaged_skill_file_exists():
    skill_file = resources.files("aiharness.skills") / "clean-code" / "SKILL.md"
    assert skill_file.is_file(), "packaged clean-code SKILL.md must ship"


def test_skill_loads_semantic_policy():
    body = read_skill("clean-code")
    lower = body.lower()
    assert "intent-revealing" in lower
    assert "ruff" in lower  # boundary: formatting stays with the formatter


def test_coder_prompt_carries_skill_as_context():
    from aiharness.agents.coder import generate_code

    seen: list[str] = []
    policy = read_skill("clean-code")
    generate_code("task", lambda p: (seen.append(p), "code")[1], context=policy)
    assert seen and "intent-revealing" in seen[0].lower()


def test_read_skill_strips_frontmatter(tmp_path):
    f = tmp_path / "SKILL.md"
    f.write_text("---\nname: clean-code\n---\nApply good names.", encoding="utf-8")
    assert read_skill("clean-code", source=f) == "Apply good names."


def test_missing_skill_fails_loudly():
    with pytest.raises(FileNotFoundError):
        read_skill("no-such-skill")
