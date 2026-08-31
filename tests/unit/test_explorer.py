"""Unit tests for the repo-explorer coder's auto-discovery (offline)."""

from agentcrew.agents.explorer import _auto_discover, _gather_context


def _files(tmp_path):
    (tmp_path / "Parser.cs").write_text("class Parser {}\n", encoding="utf-8")
    d = tmp_path / "backend" / "tests"
    d.mkdir(parents=True)
    (d / "RefTests.cs").write_text("class RefTests {}\n", encoding="utf-8")
    (d / "ignore.bin").write_bytes(b"\x00")
    (tmp_path / "README.md").write_text("readme", encoding="utf-8")
    return d


def test_auto_discover_includes_source_siblings(tmp_path):
    root = tmp_path
    (root / "a.cs").write_text("a", encoding="utf-8")
    (root / "b.cs").write_text("b", encoding="utf-8")
    (root / "notes.txt").write_text("n", encoding="utf-8")
    found = _auto_discover(root, "new.cs")
    assert "a.cs" in found
    assert "b.cs" in found
    assert "notes.txt" not in found  # non-source ignored


def test_auto_discover_ignores_target_and_subdirs(tmp_path):
    root = tmp_path
    (root / "new.cs").write_text("new", encoding="utf-8")
    sub = root / "sub"
    sub.mkdir()
    (sub / "x.cs").write_text("x", encoding="utf-8")
    found = _auto_discover(root, "new.cs")
    assert "new.cs" not in found
    assert "sub/x.cs" not in found  # only direct siblings


def test_gather_context_combines_explicit_and_auto(tmp_path):
    root = tmp_path
    (root / "Parser.cs").write_text("class Parser {}", encoding="utf-8")
    (root / "Ref.cs").write_text("class Ref {}", encoding="utf-8")
    ctx = _gather_context(root, "new.cs", context_files=["Parser.cs"])
    assert "class Parser" in ctx
    assert "class Ref" in ctx  # auto-discovered sibling


def test_gather_context_skips_missing_files(tmp_path):
    ctx = _gather_context(tmp_path, "new.cs", context_files=["missing.cs"])
    assert "### missing.cs" not in ctx