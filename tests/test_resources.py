"""Tests for the recommendation → CSV pipeline: issue-form parsing, validation,
and CSV append (new 12-column schema)."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from resources import parse_issue_form as pif  # noqa: E402
from resources import resource_utils  # noqa: E402

ISSUE_BODY = """### Display Name

My Tool

### Category

Status Lines

### Sub-Category

_No response_

### Link

https://github.com/me/tool

### Author Name

Me

### Author Link

https://github.com/me

### Description

A genuinely useful status line resource for Claude Code.
"""

CSV_HEADER = (
    "ID,Display Name,Category,Sub-Category,Link,Author Name,Author Link,"
    "Active,Date Added,Last Checked,Description,Stale\n"
)


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #
def test_parse_issue_body_maps_fields() -> None:
    data = pif.parse_issue_body(ISSUE_BODY)
    assert data["display_name"] == "My Tool"
    assert data["category"] == "Status Lines"
    assert data["subcategory"] == ""  # "_No response_" -> blank
    assert data["link"] == "https://github.com/me/tool"
    assert data["author_name"] == "Me"
    assert data["author_link"] == "https://github.com/me"
    assert data["description"].startswith("A genuinely useful")


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #
def test_validate_accepts_well_formed() -> None:
    ok, errors, _ = pif.validate_parsed_data(pif.parse_issue_body(ISSUE_BODY))
    assert ok and errors == []


def test_validate_flags_missing_required() -> None:
    data = pif.parse_issue_body(ISSUE_BODY)
    del data["author_link"]
    ok, errors, _ = pif.validate_parsed_data(data)
    assert not ok and any("author_link" in e for e in errors)


def test_validate_rejects_unknown_category() -> None:
    data = pif.parse_issue_body(ISSUE_BODY)
    data["category"] = "Bogus"
    ok, errors, _ = pif.validate_parsed_data(data)
    assert not ok and any("Invalid category" in e for e in errors)


def test_validate_requires_https_link() -> None:
    data = pif.parse_issue_body(ISSUE_BODY)
    data["link"] = "http://insecure.example"
    ok, errors, _ = pif.validate_parsed_data(data)
    assert not ok and any("https" in e for e in errors)


def test_validate_description_length_bounds() -> None:
    data = pif.parse_issue_body(ISSUE_BODY)
    data["description"] = "short"
    ok, errors, _ = pif.validate_parsed_data(data)
    assert not ok and any("too short" in e for e in errors)


# --------------------------------------------------------------------------- #
# CSV append
# --------------------------------------------------------------------------- #
def test_append_to_csv_writes_new_schema(tmp_path: Path) -> None:
    csv_path = tmp_path / "t.csv"
    csv_path.write_text(CSV_HEADER, encoding="utf-8")
    resource = {
        "id": "statusline-deadbeef",
        "display_name": "My Tool",
        "category": "Status Lines",
        "subcategory": "",
        "link": "https://github.com/me/tool",
        "author_name": "Me",
        "author_link": "https://github.com/me",
        "description": "desc, with a comma",
    }
    assert resource_utils.append_to_csv(resource, csv_path=csv_path)

    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    assert len(rows) == 1
    row = rows[0]
    assert row["ID"] == "statusline-deadbeef"
    assert row["Link"] == "https://github.com/me/tool"
    assert row["Active"] == "TRUE"
    assert row["Stale"] == "FALSE"
    assert row["Date Added"] and row["Last Checked"]  # defaulted to now
    assert row["Description"] == "desc, with a comma"  # comma survives quoting


def test_duplicate_check_detects_existing_link(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    csv_path = tmp_path / "t.csv"
    csv_path.write_text(
        CSV_HEADER
        + "statusline-1,Existing,Status Lines,,https://github.com/me/tool,Me,https://github.com/me,TRUE,,,d,FALSE\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(pif, "CSV_PATH", csv_path)
    warnings = pif.check_for_duplicates({"link": "https://github.com/me/tool", "display_name": "New"})
    assert any("already exists" in w for w in warnings)


# --- render-layer XSS / injection from foreign issue-form fields ---------------
import importlib.util  # noqa: E402


def _load_formatter():
    """The formatter module has a hyphenated filename, so load it by path (same
    way generate_readme.py does)."""
    path = BASE / "resources" / "awesome-list-entry-formatter.py"
    spec = importlib.util.spec_from_file_location("awesome_formatter", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


_fmt = _load_formatter()


def test_format_entry_escapes_html_in_text_fields() -> None:
    """Display Name / Description are foreign fields; they must render as text,
    not as live <script>/<img onerror=...> HTML."""
    row = {
        "Display Name": "Tool <script>alert(1)</script>",
        "Link": "https://github.com/me/tool",
        "Author Name": "me",
        "Author Link": "https://github.com/me",
        "Description": "<img src=x onerror=alert(document.domain)>",
    }
    out = _fmt.format_entry(row)
    assert "<script>" not in out
    assert "<img src=x onerror" not in out          # the injected tag is neutralized
    assert "&lt;script&gt;" in out
    assert "&lt;img src=x onerror" in out


def test_parse_github_rejects_crafted_link_no_badge() -> None:
    """A Link whose repo segment carries an attribute-injection payload must not
    produce a badge <img> (the sharp vector: breaking out of src="...")."""
    assert _fmt.parse_github('https://github.com/o/r"onerror=alert(1)') is None
    row = {
        "Display Name": "x",
        "Link": 'https://github.com/o/r"onerror=alert(1)',
        "Author Name": "",
        "Author Link": "",
        "Description": "a perfectly safe description",
    }
    out = _fmt.format_entry(row)
    assert "<img" not in out            # no badge tag emitted at all
    assert "img.shields.io" not in out


def test_parse_github_accepts_normal_link() -> None:
    assert _fmt.parse_github("https://github.com/me/tool") == ("me", "tool")
    assert _fmt.parse_github("https://github.com/me/tool.git") == ("me", "tool")


def test_validate_rejects_link_with_injection_chars() -> None:
    data = {
        "display_name": "X",
        "category": "Status Lines",
        "link": 'https://github.com/o/r"onerror=alert(1)',
        "author_name": "me",
        "author_link": "https://github.com/me",
        "description": "a perfectly valid description",
    }
    ok, errors, _ = pif.validate_parsed_data(data)
    assert not ok
    assert any("forbidden characters" in e for e in errors)
