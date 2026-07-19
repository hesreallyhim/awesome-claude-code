"""CSV append + PR body helpers for the new 12-column schema.

Schema (THE_RESOURCES_TABLE_NEW.csv):
  ID, Display Name, Category, Sub-Category, Link, Author Name, Author Link,
  Active, Date Added, Last Checked, Description, Stale
"""

from __future__ import annotations

import csv
import io
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = REPO_ROOT / "THE_RESOURCES_TABLE_NEW.csv"

# Column positions in the canonical 12-column schema (see docstring above).
(
    COL_ID,
    COL_DISPLAY,
    COL_CATEGORY,
    COL_SUBCATEGORY,
    COL_LINK,
    COL_AUTHOR_NAME,
    COL_AUTHOR_LINK,
    COL_ACTIVE,
    COL_DATE_ADDED,
    COL_LAST_CHECKED,
    COL_DESCRIPTION,
    COL_STALE,
) = range(12)
N_COLS = 12


# --------------------------------------------------------------------------- #
# In-place, line-oriented row edits (shared by move_resource / update_resource)
#
# These rewrite only the one row that changes; every other line stays byte-for-byte
# identical (no global re-quoting, no EOL churn). They intentionally treat one CSV
# record as one physical line — true for this dataset — and fail closed on any row
# that isn't exactly N_COLS columns (i.e. a value spanning multiple lines).
# --------------------------------------------------------------------------- #
def split_eol(line: str) -> tuple[str, str]:
    """Return (content, line-ending) so the ending survives a rewrite verbatim."""
    for eol in ("\r\n", "\n", "\r"):
        if line.endswith(eol):
            return line[: -len(eol)], eol
    return line, ""


def serialize_row(fields: list[str], eol: str = "\n") -> str:
    """CSV-encode one row (QUOTE_MINIMAL) and reattach the given line ending."""
    buf = io.StringIO()
    csv.writer(buf, lineterminator="").writerow(fields)
    return buf.getvalue() + eol


def read_lines(csv_path: Path | None = None) -> list[str]:
    return (csv_path or CSV_PATH).read_text(encoding="utf-8").splitlines(keepends=True)


def write_lines(lines: list[str], csv_path: Path | None = None) -> None:
    (csv_path or CSV_PATH).write_text("".join(lines), encoding="utf-8")


def find_row_indices(lines: list[str], *, id: str = "", link: str = "") -> list[int]:
    """Indices (into `lines`) of data rows matching `id` or `link`; skips header/blank.

    Raises ValueError on a row that isn't N_COLS columns (multi-line value): callers
    should refuse rather than corrupt such a row.
    """
    out: list[int] = []
    for i, line in enumerate(lines[1:], start=1):  # skip header
        content, _ = split_eol(line)
        if not content.strip():
            continue
        fields = next(csv.reader([content]))
        if len(fields) != N_COLS:
            raise ValueError(f"row {i + 1} has {len(fields)} columns (expected {N_COLS}); may span multiple lines")
        if (id and fields[COL_ID] == id) or (link and fields[COL_LINK].strip() == link.strip()):
            out.append(i)
    return out


def _value_map(data: dict[str, str], now: str) -> dict[str, str]:
    return {
        "ID": data.get("id", ""),
        "Display Name": data.get("display_name", ""),
        "Category": data.get("category", ""),
        "Sub-Category": data.get("subcategory", ""),
        "Link": data.get("link", ""),
        "Author Name": data.get("author_name", ""),
        "Author Link": data.get("author_link", ""),
        "Active": data.get("active", "TRUE"),
        "Date Added": data.get("date_added", now),
        "Last Checked": data.get("last_checked", now),
        "Description": data.get("description", ""),
        "Stale": data.get("stale", "FALSE"),
    }


def append_to_csv(data: dict[str, str], csv_path: Path | None = None) -> bool:
    """Append one resource row, honoring the existing header order."""
    path = csv_path or CSV_PATH
    try:
        with path.open(encoding="utf-8", newline="") as f:
            headers = next(csv.reader(f), None)
    except OSError as e:
        print(f"Error reading CSV header: {e}")
        return False
    if not headers:
        print("Error reading CSV header: missing header row")
        return False

    now = datetime.now().strftime("%Y-%m-%d:%H-%M-%S")
    value_map = _value_map(data, now)
    missing = [key for key in value_map if key not in headers]
    if missing:
        print(f"Error: CSV header missing columns {', '.join(missing)}")
        return False

    row = {header: value_map.get(header, "") for header in headers}
    try:
        with path.open("a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=headers, lineterminator="\n").writerow(row)
        return True
    except OSError as e:
        print(f"Error writing to CSV: {e}")
        return False


def generate_pr_content(data: dict[str, str]) -> str:
    """Render the PR body for an approved submission."""
    subcategory = data.get("subcategory") or "N/A"
    author = data.get("author_name", "")
    author_link = data.get("author_link", "")
    author_md = f"[{author}]({author_link})" if author_link else author
    return f"""### Resource Information

- **Display Name**: {data.get("display_name", "")}
- **Category**: {data.get("category", "")}
- **Sub-Category**: {subcategory}
- **Link**: {data.get("link", "")}
- **Author**: {author_md}

### Description

{data.get("description", "")}
"""
