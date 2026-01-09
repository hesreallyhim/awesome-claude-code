#!/usr/bin/env python3
"""Tests for ticker SVG generation functions."""

import sys
from pathlib import Path

# Add repo root to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.ticker.generate_ticker_svg import truncate_repo_name  # noqa: E402


def test_truncate_repo_name_short():
    """Test that short names are not truncated."""
    assert truncate_repo_name("short-name") == "short-name"
    assert truncate_repo_name("a") == "a"
    assert truncate_repo_name("") == ""


def test_truncate_repo_name_exactly_20():
    """Test that names exactly 20 characters are not truncated."""
    name_20_chars = "12345678901234567890"
    assert len(name_20_chars) == 20
    assert truncate_repo_name(name_20_chars) == name_20_chars


def test_truncate_repo_name_long():
    """Test that long names are truncated with ellipsis."""
    long_name = "very-long-repository-name-that-exceeds-twenty-chars"
    result = truncate_repo_name(long_name)
    assert result == "very-long-repository..."
    assert len(result) == 23  # 20 chars + "..."


def test_truncate_repo_name_custom_length():
    """Test truncation with custom max length."""
    name = "this-is-a-long-name"
    result = truncate_repo_name(name, max_length=10)
    assert result == "this-is-a-..."
    assert len(result) == 13  # 10 chars + "..."


def test_truncate_repo_name_preserves_beginning():
    """Test that truncation preserves the beginning of the name."""
    name = "claude-code-infrastructure-showcase"
    result = truncate_repo_name(name)
    assert result.startswith("claude-code-infrastr")
    assert result.endswith("...")


def test_truncate_repo_name_edge_cases():
    """Test edge cases for truncation."""
    # Name exactly one character longer than max
    name_21_chars = "123456789012345678901"
    assert len(name_21_chars) == 21
    result = truncate_repo_name(name_21_chars)
    assert result == "12345678901234567890..."

    # Very long name
    very_long = "a" * 100
    result = truncate_repo_name(very_long)
    assert len(result) == 23  # 20 chars + "..."
    assert result == "a" * 20 + "..."
