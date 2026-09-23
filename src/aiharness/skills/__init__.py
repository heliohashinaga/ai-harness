"""Project skills: prompt packs loaded on demand (LEVEL 3, opt-in).

Skills live INSIDE the package (``src/aiharness/skills/<name>/SKILL.md``) so
they ship in the wheel — one source of truth, no per-skill fallback constant
that can go stale. Add a new skill by adding its directory; no loader change,
no packaging change (``package-data`` covers ``*/SKILL.md``).
"""

from __future__ import annotations

import os
import re
from importlib import resources
from pathlib import Path

_FRONTMATTER = re.compile(r"^---.*?---\s*", re.S)


def read_skill(name: str, source: str | os.PathLike[str] | None = None) -> str:
    """Return the body of ``skills/<name>/SKILL.md`` without frontmatter.

    With ``source``: read that file (tests, experiments). Without: read the
    packaged skill — works from a source checkout and from an installed
    wheel alike. A missing skill raises ``FileNotFoundError`` loudly;
    there is deliberately no silent fallback to debate staleness with.
    """
    if source is not None:
        return _strip_frontmatter(Path(source).read_text(encoding="utf-8"))
    skill_file = resources.files(__package__) / name / "SKILL.md"
    return _strip_frontmatter(skill_file.read_text(encoding="utf-8"))


def _strip_frontmatter(text: str) -> str:
    return _FRONTMATTER.sub("", text, count=1).strip()
