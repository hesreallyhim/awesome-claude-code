#!/usr/bin/env python3
"""
Unit tests for append_to_csv in resource_utils.py.

Tests cover:
- append_to_csv function with all columns including release metadata
- CSV column alignment
- Default values for new resources
"""

import csv
import sys
import tempfile
from collections.abc import Generator
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# Add parent directory to path to import the script
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.resources.resource_utils import append_to_csv  # noqa: E402


@pytest.fixture
def temp_csv() -> Generator[Path, None, None]:
    """Create a temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
        temp_path = Path(f.name)
        # Write header row matching the actual CSV structure
        writer = csv.writer(f)
        writer.writerow(
            [
                "ID",
                "Display Name",
                "Category",
                "Sub-Category",
                "Primary Link",
                "Secondary Link",
                "Author Name",
                "Author Link",
                "Active",
                "Date Added",
                "Last Modified",
                "Last Checked",
                "License",
                "Description",
                "Removed From Origin",
                "Stale",
                "Repo Created",
                "Latest Release",
                "Release Version",
                "Release Source",
            ]
        )
    yield temp_path
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def sample_resource_data() -> dict[str, str]:
    """Sample resource data for testing."""
    return {
        "id": "test-resource-001",
        "display_name": "Test Resource",
        "category": "Tooling",
        "subcategory": "General",
        "primary_link": "https://example.com/test",
        "secondary_link": "https://example.com/secondary",
        "author_name": "Test Author",
        "author_link": "https://github.com/testauthor",
        "license": "MIT",
        "description": "A test resource for unit testing",
    }


def set_csv_path(monkeypatch: pytest.MonkeyPatch, path: Path | str) -> None:
    """Force append_to_csv to write to a specific path."""
    monkeypatch.setattr("scripts.resources.resource_utils.os.path.join", lambda *args: str(path))


def test_append_to_csv_adds_all_columns(
    temp_csv: Path, sample_resource_data: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that append_to_csv adds a row with all 20 columns."""
    set_csv_path(monkeypatch, temp_csv)

    # Append the resource
    result = append_to_csv(sample_resource_data)
    assert result is True

    # Read back the CSV and verify
    with open(temp_csv, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert len(header) == 20, f"Expected 20 columns in header, got {len(header)}"

        # Read the data row
        data_row = next(reader)
        assert len(data_row) == 20, f"Expected 20 columns in data row, got {len(data_row)}"

        # Verify specific column values
        assert data_row[0] == sample_resource_data["id"]
        assert data_row[1] == sample_resource_data["display_name"]
        assert data_row[2] == sample_resource_data["category"]
        assert data_row[3] == sample_resource_data["subcategory"]
        assert data_row[4] == sample_resource_data["primary_link"]
        assert data_row[5] == sample_resource_data["secondary_link"]
        assert data_row[6] == sample_resource_data["author_name"]
        assert data_row[7] == sample_resource_data["author_link"]
        assert data_row[8] == "TRUE"  # Active default
        assert data_row[12] == sample_resource_data["license"]
        assert data_row[13] == sample_resource_data["description"]
        assert data_row[14] == "FALSE"  # Removed From Origin default
        assert data_row[15] == "FALSE"  # Stale default
        assert data_row[16] == ""  # Repo Created default
        assert data_row[17] == ""  # Latest Release default
        assert data_row[18] == ""  # Release Version default
        assert data_row[19] == ""  # Release Source default


def test_append_to_csv_default_values(
    temp_csv: Path, sample_resource_data: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that append_to_csv uses correct default values."""
    set_csv_path(monkeypatch, temp_csv)

    # Append the resource
    result = append_to_csv(sample_resource_data)
    assert result is True

    # Read back and check defaults
    with open(temp_csv, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        data_row = next(reader)

        # Check default values
        assert data_row[8] == "TRUE", "Active should default to TRUE"
        assert data_row[10] == "", "Last Modified should default to empty"
        assert data_row[14] == "FALSE", "Removed From Origin should default to FALSE"
        assert data_row[15] == "FALSE", "Stale should default to FALSE"
        assert data_row[16] == "", "Repo Created should default to empty"
        assert data_row[17] == "", "Latest Release should default to empty"
        assert data_row[18] == "", "Release Version should default to empty"
        assert data_row[19] == "", "Release Source should default to empty"


def test_append_to_csv_with_removed_from_origin_true(
    temp_csv: Path, sample_resource_data: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that append_to_csv respects removed_from_origin when provided."""
    sample_resource_data["removed_from_origin"] = "TRUE"

    set_csv_path(monkeypatch, temp_csv)

    # Append the resource
    result = append_to_csv(sample_resource_data)
    assert result is True

    # Read back and verify
    with open(temp_csv, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        data_row = next(reader)

        assert data_row[14] == "TRUE", "Removed From Origin should be TRUE when provided"


def test_append_to_csv_date_fields(
    temp_csv: Path, sample_resource_data: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that append_to_csv sets date fields correctly."""
    set_csv_path(monkeypatch, temp_csv)

    # Capture the current time window
    before_time = datetime.now()
    result = append_to_csv(sample_resource_data)
    after_time = datetime.now()

    assert result is True

    # Read back and check date fields
    with open(temp_csv, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        data_row = next(reader)

        # Parse the date fields
        date_added = datetime.strptime(data_row[9], "%Y-%m-%d:%H-%M-%S")
        last_checked = datetime.strptime(data_row[11], "%Y-%m-%d:%H-%M-%S")

        # Verify dates are within the expected time window (account for second precision)
        # The strptime loses microseconds, so we need to compare at second precision
        assert (
            before_time.replace(microsecond=0)
            <= date_added
            <= after_time.replace(microsecond=0) + timedelta(seconds=1)
        ), "Date Added should be current time"
        assert (
            before_time.replace(microsecond=0)
            <= last_checked
            <= after_time.replace(microsecond=0) + timedelta(seconds=1)
        ), "Last Checked should be current time"


def test_append_to_csv_handles_csv_error(
    sample_resource_data: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that append_to_csv handles file write errors gracefully."""
    # Point to a non-writable location
    set_csv_path(monkeypatch, "/invalid/path/to/csv.csv")

    # Should return False on error
    result = append_to_csv(sample_resource_data)
    assert result is False


def test_append_to_csv_preserves_existing_data(
    temp_csv: Path, sample_resource_data: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that append_to_csv appends without modifying existing rows."""
    # Add an existing row first
    with open(temp_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "existing-001",
                "Existing Resource",
                "Hooks",
                "General",
                "https://existing.com",
                "",
                "Existing Author",
                "https://github.com/existing",
                "TRUE",
                "2025-01-01:00-00-00",
                "",
                "2025-01-01:00-00-00",
                "Apache-2.0",
                "An existing resource",
                "FALSE",
                "FALSE",
                "",
                "",
                "",
                "",
            ]
        )

    set_csv_path(monkeypatch, temp_csv)

    # Append new resource
    result = append_to_csv(sample_resource_data)
    assert result is True

    # Verify both rows exist
    with open(temp_csv, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

        assert len(rows) == 3, "Should have header + 2 data rows"
        assert rows[1][0] == "existing-001", "Existing row should be preserved"
        assert rows[2][0] == sample_resource_data["id"], "New row should be appended"
