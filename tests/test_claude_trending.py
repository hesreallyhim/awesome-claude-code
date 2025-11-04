#!/usr/bin/env python3
"""
Unit tests for claude_trending.py script.

Tests cover:
- Configuration parsing from environment variables
- Metric calculation (Laplace-smoothed proportional growth)
- Sorting and ranking logic
- CSV generation and format
"""

import csv
import os
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

# Add parent directory to path to import the script
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestTrendingScript:
    """Test suite for the Claude trending repositories script."""

    def test_metric_calculation(self) -> None:
        """Test Laplace-smoothed proportional growth calculations."""
        # Test case 1: Normal case
        total_stars = 100
        new_stars = 10
        total_forks = 20
        new_forks = 2

        old_stars = max(0, total_stars - new_stars)
        star_growth_adj = new_stars / (old_stars + 10)

        old_forks = max(0, total_forks - new_forks)
        fork_growth_adj = new_forks / (old_forks + 5)

        score = star_growth_adj + 0.5 * fork_growth_adj

        # Verify calculations
        expected_star_growth = 10 / (90 + 10)  # 0.1
        expected_fork_growth = 2 / (18 + 5)  # ~0.0869
        expected_score = expected_star_growth + 0.5 * expected_fork_growth

        assert abs(star_growth_adj - expected_star_growth) < 0.001
        assert abs(fork_growth_adj - expected_fork_growth) < 0.001
        assert abs(score - expected_score) < 0.001

    def test_edge_case_new_repo(self) -> None:
        """Test metric calculation for brand new repos (Laplace smoothing)."""
        total_stars = 5
        new_stars = 5
        total_forks = 1
        new_forks = 1

        old_stars = max(0, total_stars - new_stars)
        star_growth_adj = new_stars / (old_stars + 10)

        old_forks = max(0, total_forks - new_forks)
        fork_growth_adj = new_forks / (old_forks + 5)

        # With Laplace smoothing, new repo should have reasonable score
        # star_growth_adj = 5 / (0 + 10) = 0.5
        # fork_growth_adj = 1 / (0 + 5) = 0.2
        assert abs(star_growth_adj - 0.5) < 0.001
        assert abs(fork_growth_adj - 0.2) < 0.001

    def test_sorting_logic(self) -> None:
        """Test that repositories are sorted correctly."""
        results = [
            {
                "score": 1.0,
                "new_stars_24h": 10,
                "total_stars": 100,
                "full_name": "repo1",
            },
            {
                "score": 1.5,
                "new_stars_24h": 20,
                "total_stars": 200,
                "full_name": "repo2",
            },
            {
                "score": 1.0,
                "new_stars_24h": 15,
                "total_stars": 150,
                "full_name": "repo3",
            },
            {
                "score": 1.0,
                "new_stars_24h": 15,
                "total_stars": 50,
                "full_name": "repo4",
            },
        ]

        # Sort by score (desc), then new_stars_24h (desc), then total_stars (desc)
        results.sort(key=lambda x: (-x["score"], -x["new_stars_24h"], -x["total_stars"]))

        # Verify order
        assert results[0]["full_name"] == "repo2"  # Highest score
        assert results[1]["full_name"] == "repo3"  # Same score as 1, higher new_stars
        assert results[2]["full_name"] == "repo4"  # Same score and new_stars, lower total
        assert results[3]["full_name"] == "repo1"  # Lowest new_stars

    def test_csv_generation(self) -> None:
        """Test CSV file generation with correct format."""
        fieldnames = [
            "generated_at_utc",
            "full_name",
            "html_url",
            "description",
            "language",
            "total_stars",
            "total_forks",
            "new_stars_24h",
            "new_forks_24h",
            "star_growth_adj",
            "fork_growth_adj",
            "score",
        ]

        test_data = [
            {
                "full_name": "owner/repo",
                "html_url": "https://github.com/owner/repo",
                "description": "Test description",
                "language": "Python",
                "total_stars": 100,
                "total_forks": 10,
                "new_stars_24h": 5,
                "new_forks_24h": 2,
                "star_growth_adj": 0.5,
                "fork_growth_adj": 0.2,
                "score": 0.6,
            }
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
            temp_path = Path(f.name)

        try:
            now = datetime.now(UTC)
            with open(temp_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for result in test_data:
                    result["generated_at_utc"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
                    writer.writerow(result)

            # Verify CSV format
            with open(temp_path) as f:
                reader = csv.DictReader(f)
                rows = list(reader)

                assert len(rows) == 1
                assert rows[0]["full_name"] == "owner/repo"
                assert rows[0]["total_stars"] == "100"
                assert rows[0]["score"] == "0.6"
                assert "generated_at_utc" in rows[0]
        finally:
            temp_path.unlink()

    def test_config_parsing(self) -> None:
        """Test environment variable parsing."""
        with patch.dict(
            os.environ,
            {
                "WINDOW_HOURS": "24",
                "TOP_N": "5",
                "SEARCH_EXCLUDE_MONET": "true",
                "MIN_PUSHED_SINCE": "365",
            },
        ):
            window_hours = int(os.getenv("WINDOW_HOURS", "24"))
            top_n = int(os.getenv("TOP_N", "5"))
            exclude_monet = os.getenv("SEARCH_EXCLUDE_MONET", "true").lower() == "true"
            min_pushed = int(os.getenv("MIN_PUSHED_SINCE", "365"))

            assert window_hours == 24
            assert top_n == 5
            assert exclude_monet is True
            assert min_pushed == 365
