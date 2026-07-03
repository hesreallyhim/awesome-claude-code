"""Essential coverage for the Awesome Claude Code README generator.

Scope is deliberately lean. The headline guarantee is that `make generate` is
idempotent while the CSV is held constant; the remaining tests pin the other
contract points (fail-closed validation, alphabetical ordering, Active filter,
badge formatting, GitHub anchor slugs, TOC/heading consistency).

Run:  venv/bin/python -m pytest -q   (or `make test`)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

import generate_readme as gen  # noqa: E402

fmt = gen.formatter


def _load() -> tuple[list[dict], list[dict]]:
    return gen.load_config(), gen.load_active_rows()


# --------------------------------------------------------------------------- #
# Idempotency (the headline guarantee)
# --------------------------------------------------------------------------- #
def test_render_is_idempotent_with_constant_csv() -> None:
    categories, rows = _load()
    template = gen.TEMPLATE_PATH.read_text(encoding="utf-8")
    first = gen.render_readme(template, rows, categories)
    second = gen.render_readme(template, rows, categories)
    assert first == second


def test_make_generate_writes_identical_output_on_rerun() -> None:
    """End-to-end: running generation twice leaves README.md byte-identical."""
    original = gen.OUTPUT_PATH.read_text(encoding="utf-8")
    try:
        gen.main()
        first = gen.OUTPUT_PATH.read_bytes()
        gen.main()
        second = gen.OUTPUT_PATH.read_bytes()
        assert first == second
    finally:
        gen.OUTPUT_PATH.write_text(original, encoding="utf-8")


# --------------------------------------------------------------------------- #
# Fail-closed validation
# --------------------------------------------------------------------------- #
def test_unknown_active_category_fails_closed() -> None:
    categories, _ = _load()
    bad = [{"ID": "x-1", "Category": "Bogus Category", "Active": "TRUE", "Display Name": "X"}]
    with pytest.raises(SystemExit) as exc:
        gen.validate_categories(bad, categories)
    assert exc.value.code == 1


def test_real_csv_categories_match_config() -> None:
    """Guards against drift between the CSV and config.yaml."""
    categories, rows = _load()
    gen.validate_categories(rows, categories)  # must not raise


# --------------------------------------------------------------------------- #
# Ordering, filtering
# --------------------------------------------------------------------------- #
def test_entries_alphabetical_within_each_category() -> None:
    categories, rows = _load()
    body = gen.build_list(rows, categories)
    for section in re.split(r"^## ", body, flags=re.M)[1:]:
        names = re.findall(r"^- \[([^\]]+)\]", section, flags=re.M)
        assert names == sorted(names, key=str.casefold)


def test_inactive_rows_are_excluded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    csv_text = (
        "ID,Display Name,Category,Sub-Category,Link,Author Name,Author Link,"
        "Active,Date Added,Last Checked,Description,Stale\n"
        "a-1,Alpha,Status Lines,,https://github.com/o/alpha,O,https://github.com/o,TRUE,,,desc,FALSE\n"
        "b-2,Beta,Status Lines,,https://github.com/o/beta,O,https://github.com/o,FALSE,,,desc,FALSE\n"
    )
    csv_path = tmp_path / "t.csv"
    csv_path.write_text(csv_text, encoding="utf-8")
    monkeypatch.setattr(gen, "CSV_PATH", csv_path)
    names = [r["Display Name"] for r in gen.load_active_rows()]
    assert names == ["Alpha"]


# --------------------------------------------------------------------------- #
# Entry formatting / badges
# --------------------------------------------------------------------------- #
def test_format_entry_github_has_hard_break_and_four_badges() -> None:
    row = {
        "Display Name": "Foo",
        "Link": "https://github.com/owner/repo",
        "Author Name": "Bob",
        "Author Link": "https://github.com/bob",
        "Description": "Does things.",
    }
    bullet, badge_line = fmt.format_entry(row).split("\n")
    assert bullet == "- [Foo](https://github.com/owner/repo) by [Bob](https://github.com/bob) - Does things.  "
    assert bullet.endswith("  ")  # CommonMark hard break
    for token in (
        "created-at/owner/repo",
        "last-commit/owner/repo",
        "license/owner/repo",
        "stars/owner/repo",
    ):
        assert token in badge_line


def test_format_entry_non_github_has_no_badge_line() -> None:
    row = {
        "Display Name": "Vid",
        "Link": "https://youtu.be/abc",
        "Author Name": "A",
        "Author Link": "",
        "Description": "d",
    }
    out = fmt.format_entry(row)
    assert "\n" not in out
    assert out == "- [Vid](https://youtu.be/abc) by A - d"


def test_parse_github() -> None:
    assert fmt.parse_github("https://github.com/o/r") == ("o", "r")
    assert fmt.parse_github("https://github.com/o/r.git") == ("o", "r")
    assert fmt.parse_github("https://github.com/o/r/tree/main/x") == ("o", "r")
    assert fmt.parse_github("https://youtu.be/x") is None


# --------------------------------------------------------------------------- #
# GitHub anchor slugs + TOC consistency
# --------------------------------------------------------------------------- #
def test_github_slug_quirks() -> None:
    assert gen.github_slug("Status Lines") == "status-lines"
    assert gen.github_slug("Design & UI/UX") == "design--uiux"
    assert gen.github_slug("Documentation, Knowledge & Learning") == "documentation-knowledge--learning"
    assert (
        gen.github_slug("Remote Control, Notifications & Voice I/O")
        == "remote-control-notifications--voice-io"
    )


def test_toc_anchors_resolve_to_headings() -> None:
    categories, rows = _load()
    toc = gen.build_toc(rows, categories)
    body = gen.build_list(rows, categories)
    anchors = re.findall(r"\]\(#([^)]+)\)", toc)
    heading_slugs = {gen.github_slug(h) for h in re.findall(r"^#{2,3} (.+)$", body, flags=re.M)}
    assert anchors  # non-empty
    for anchor in anchors:
        assert anchor in heading_slugs
