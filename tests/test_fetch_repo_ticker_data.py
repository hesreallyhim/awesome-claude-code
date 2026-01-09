#!/usr/bin/env python3
"""Tests for repo ticker data fetching utilities."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest
import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

import scripts.ticker.fetch_repo_ticker_data as fetch_repo_ticker_data  # noqa: E402


class DummyResponse:
    """Minimal response stub for requests.get."""

    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"status {self.status_code}")

    def json(self) -> dict:
        return self._payload


def test_load_previous_data_missing_file(tmp_path: Path) -> None:
    assert fetch_repo_ticker_data.load_previous_data(tmp_path / "missing.csv") == {}


def test_load_previous_data_reads_csv(tmp_path: Path) -> None:
    path = tmp_path / "previous.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["full_name", "stars", "watchers", "forks"])
        writer.writeheader()
        writer.writerow({"full_name": "owner/repo", "stars": "5", "watchers": "2", "forks": "1"})

    data = fetch_repo_ticker_data.load_previous_data(path)
    assert data == {"owner/repo": {"stars": 5, "watchers": 2, "forks": 1}}


def test_calculate_deltas_with_previous() -> None:
    repos = [{"full_name": "owner/repo", "stars": 10, "watchers": 5, "forks": 3}]
    previous = {"owner/repo": {"stars": 7, "watchers": 2, "forks": 1}}
    result = fetch_repo_ticker_data.calculate_deltas(repos, previous)
    assert result[0]["stars_delta"] == 3
    assert result[0]["watchers_delta"] == 3
    assert result[0]["forks_delta"] == 2


def test_calculate_deltas_new_repo_with_prior_snapshot() -> None:
    repos = [{"full_name": "owner/new", "stars": 4, "watchers": 3, "forks": 2}]
    previous = {"owner/old": {"stars": 1, "watchers": 1, "forks": 1}}
    result = fetch_repo_ticker_data.calculate_deltas(repos, previous)
    assert result[0]["stars_delta"] == 4
    assert result[0]["watchers_delta"] == 3
    assert result[0]["forks_delta"] == 2


def test_calculate_deltas_no_previous_baseline() -> None:
    repos = [{"full_name": "owner/new", "stars": 4, "watchers": 3, "forks": 2}]
    result = fetch_repo_ticker_data.calculate_deltas(repos, {})
    assert result[0]["stars_delta"] == 0
    assert result[0]["watchers_delta"] == 0
    assert result[0]["forks_delta"] == 0


def test_save_to_csv_writes_output(tmp_path: Path) -> None:
    output_path = tmp_path / "data" / "repo-ticker.csv"
    repos = [
        {
            "full_name": "owner/repo",
            "stars": 10,
            "watchers": 5,
            "forks": 2,
            "stars_delta": 1,
            "watchers_delta": 0,
            "forks_delta": 2,
            "url": "https://github.com/owner/repo",
        }
    ]

    fetch_repo_ticker_data.save_to_csv(repos, output_path)

    with output_path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["full_name"] == "owner/repo"
    assert rows[0]["stars_delta"] == "1"


def test_fetch_repos_maps_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    token = "token"
    payload = {
        "items": [
            {
                "full_name": "owner/repo",
                "stargazers_count": 10,
                "watchers_count": 5,
                "forks_count": 2,
                "html_url": "https://github.com/owner/repo",
            }
        ]
    }
    captured_url: str | None = None
    captured_params: dict[str, str | int] | None = None
    captured_headers: dict[str, str] | None = None
    captured_timeout: int | None = None

    def fake_get(url, params=None, headers=None, timeout=None):
        nonlocal captured_url, captured_params, captured_headers, captured_timeout
        captured_url = url
        captured_params = params
        captured_headers = headers
        captured_timeout = timeout
        return DummyResponse(payload)

    monkeypatch.setattr(fetch_repo_ticker_data.requests, "get", fake_get)

    repos = fetch_repo_ticker_data.fetch_repos(token)
    assert repos == [
        {
            "full_name": "owner/repo",
            "stars": 10,
            "watchers": 5,
            "forks": 2,
            "url": "https://github.com/owner/repo",
        }
    ]
    assert captured_url == "https://api.github.com/search/repositories"
    assert captured_headers is not None
    assert captured_params is not None
    assert captured_headers["Authorization"] == f"Bearer {token}"
    assert captured_params["per_page"] == 100
    assert captured_timeout == 30


def test_fetch_repos_request_error_exits(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(*_args, **_kwargs):
        raise requests.exceptions.RequestException("boom")

    monkeypatch.setattr(fetch_repo_ticker_data.requests, "get", fake_get)
    with pytest.raises(SystemExit):
        fetch_repo_ticker_data.fetch_repos("token")


def test_main_missing_token_exits(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with pytest.raises(SystemExit):
        fetch_repo_ticker_data.main()
