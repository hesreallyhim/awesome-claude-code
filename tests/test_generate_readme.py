#!/usr/bin/env python3
"""Tests for README generation functions."""

import os
import sys
import unittest
from datetime import datetime

# Add the scripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from generate_readme import parse_resource_date


class TestParseResourceDate(unittest.TestCase):
    """Test cases for the parse_resource_date function."""

    def test_parse_date_only_format(self):
        """Test parsing YYYY-MM-DD format."""
        result = parse_resource_date("2025-08-07")
        expected = datetime(2025, 8, 7)
        self.assertEqual(result, expected)

    def test_parse_date_with_timestamp_format(self):
        """Test parsing YYYY-MM-DD:HH-MM-SS format."""
        result = parse_resource_date("2025-08-07:18-26-57")
        expected = datetime(2025, 8, 7, 18, 26, 57)
        self.assertEqual(result, expected)

    def test_parse_with_whitespace(self):
        """Test parsing with leading/trailing whitespace."""
        result = parse_resource_date("  2025-08-07  ")
        expected = datetime(2025, 8, 7)
        self.assertEqual(result, expected)

    def test_parse_empty_string(self):
        """Test parsing empty string returns None."""
        result = parse_resource_date("")
        self.assertIsNone(result)

    def test_parse_none(self):
        """Test parsing None returns None."""
        result = parse_resource_date(None)
        self.assertIsNone(result)

    def test_parse_invalid_format(self):
        """Test parsing invalid date format returns None."""
        invalid_formats = [
            "2025/08/07",  # Wrong separator
            "07-08-2025",  # Wrong order
            "2025-13-01",  # Invalid month
            "2025-08-32",  # Invalid day
            "not-a-date",  # Complete nonsense
            "2025-08-07 18:26:57",  # Space instead of colon
        ]

        for invalid_date in invalid_formats:
            with self.subTest(invalid_date=invalid_date):
                result = parse_resource_date(invalid_date)
                self.assertIsNone(result, f"Expected None for invalid date: {invalid_date}")

    def test_parse_various_timestamps(self):
        """Test parsing various valid timestamp formats."""
        test_cases = [
            ("2025-08-05:11-48-39", datetime(2025, 8, 5, 11, 48, 39)),
            ("2025-07-29:18-37-05", datetime(2025, 7, 29, 18, 37, 5)),
            ("2025-08-07:00-00-00", datetime(2025, 8, 7, 0, 0, 0)),
            ("2025-12-31:23-59-59", datetime(2025, 12, 31, 23, 59, 59)),
        ]

        for date_string, expected in test_cases:
            with self.subTest(date_string=date_string):
                result = parse_resource_date(date_string)
                self.assertEqual(result, expected, f"Failed to parse: {date_string}")

    def test_date_comparison(self):
        """Test that parsed dates can be compared correctly."""
        date1 = parse_resource_date("2025-08-07")
        date2 = parse_resource_date("2025-08-05")
        date3 = parse_resource_date("2025-08-07:18-26-57")

        self.assertTrue(date1 > date2)
        self.assertTrue(date3 > date1)  # Same date but with time
        self.assertFalse(date2 > date1)


if __name__ == "__main__":
    unittest.main()
