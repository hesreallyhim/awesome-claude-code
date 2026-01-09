#!/usr/bin/env python3
"""Tests for validate_links helpers and URL validation."""

from __future__ import annotations

import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import scripts.validation.validate_links as validate_links  # noqa: E402


class DummyResponse:
    """Minimal response stub for requests.head."""

    def __init__(self, status_code: int, headers: dict[str, str] | None = None) -> None:
        self.status_code = status_code
        self.headers = headers or {}


def test_parse_last_modified_date_variants() -> None:
    iso_value = "2024-06-01T12:34:56Z"
    parsed = validate_links.parse_last_modified_date(iso_value)
    assert parsed is not None
    assert parsed.tzinfo is not None
    assert parsed.year == 2024

    fallback_value = "2024-06-01:12-34-56"
    fallback_parsed = validate_links.parse_last_modified_date(fallback_value)
    assert fallback_parsed is not None
    assert fallback_parsed.year == 2024

    assert validate_links.parse_last_modified_date("") is None
    assert validate_links.parse_last_modified_date("not-a-date") is None


def test_is_stale_threshold() -> None:
    now = datetime.now(UTC)
    fresh = now - timedelta(days=validate_links.STALE_DAYS - 1)
    stale = now - timedelta(days=validate_links.STALE_DAYS + 1)
    assert validate_links.is_stale(fresh) is False
    assert validate_links.is_stale(stale) is True


def test_ensure_stale_column_adds_defaults() -> None:
    fieldnames, rows = validate_links.ensure_stale_column(["A"], [{"A": "1"}])
    assert validate_links.STALE_HEADER_NAME in fieldnames
    assert rows[0][validate_links.STALE_HEADER_NAME] == ""


def test_apply_overrides_sets_and_locks_fields() -> None:
    row = {
        validate_links.ID_HEADER_NAME: "res-1",
        validate_links.ACTIVE_HEADER_NAME: "TRUE",
        validate_links.LICENSE_HEADER_NAME: "NOT_FOUND",
        validate_links.LAST_CHECKED_HEADER_NAME: "",
        validate_links.LAST_MODIFIED_HEADER_NAME: "",
        "Description": "Old description",
    }
    overrides = {
        "res-1": {
            "active": "FALSE",
            "license": "MIT",
            "last_checked": "2024-01-01:00-00-00",
            "last_modified": "2024-01-02:00-00-00",
            "description": "New description",
            "skip_validation": True,
            "notes": "ignored",
            "active_locked": True,
        }
    }

    updated, locked_fields, skip_validation = validate_links.apply_overrides(row, overrides)
    assert skip_validation is True
    assert locked_fields == {
        "active",
        "license",
        "last_checked",
        "last_modified",
        "description",
    }
    assert updated[validate_links.ACTIVE_HEADER_NAME] == "FALSE"
    assert updated[validate_links.LICENSE_HEADER_NAME] == "MIT"
    assert updated[validate_links.LAST_CHECKED_HEADER_NAME] == "2024-01-01:00-00-00"
    assert updated[validate_links.LAST_MODIFIED_HEADER_NAME] == "2024-01-02:00-00-00"
    assert updated["Description"] == "New description"


def test_header_int_parsing() -> None:
    assert validate_links._header_int({"X": 5}, "X") == 5
    assert validate_links._header_int({"X": "10"}, "X") == 10
    assert validate_links._header_int({"X": b"12"}, "X") == 12
    assert validate_links._header_int({"X": "bad"}, "X") == 0
    assert validate_links._header_int({}, "missing") == 0


def test_get_committer_date_from_response_prefers_commit_info() -> None:
    data = [
        {
            "commit": {
                "committer": {"date": "2024-05-01T00:00:00Z"},
                "author": {"date": "2024-04-01T00:00:00Z"},
            }
        }
    ]
    assert validate_links.get_committer_date_from_response(data) == "2024-05-01T00:00:00Z"


def test_get_committer_date_from_response_falls_back_to_author() -> None:
    data = [{"commit": {"author": {"date": "2024-04-01T00:00:00Z"}}}]
    assert validate_links.get_committer_date_from_response(data) == "2024-04-01T00:00:00Z"


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://www.npmjs.com/package/left-pad", ("npm", "left-pad")),
        ("https://pypi.org/project/requests/", ("pypi", "requests")),
        ("https://crates.io/crates/serde", ("crates", "serde")),
        ("https://formulae.brew.sh/formula/wget", ("homebrew", "wget")),
        ("https://github.com/owner/repo", ("github-releases", "owner/repo")),
        ("https://example.com", (None, None)),
    ],
)
def test_detect_package_info(url: str, expected: tuple[str | None, str | None]) -> None:
    assert validate_links.detect_package_info(url) == expected


def test_get_latest_release_info_for_github(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_latest_release(owner: str, repo: str):
        return "2024-01-01:00-00-00", "v1.0.0"

    monkeypatch.setattr(validate_links, "get_github_latest_release", fake_latest_release)
    release_date, version, source = validate_links.get_latest_release_info(
        "https://github.com/owner/repo"
    )
    assert release_date == "2024-01-01:00-00-00"
    assert version == "v1.0.0"
    assert source == "github-releases"

    release_date, version, source = validate_links.get_latest_release_info("https://example.com")
    assert (release_date, version, source) == (None, None, None)


def test_validate_url_non_github_success(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_head(*args, **kwargs):
        return DummyResponse(200)

    monkeypatch.setattr(validate_links.requests, "head", fake_head)

    ok, status, license_info, last_modified = validate_links.validate_url("https://example.com")
    assert ok is True
    assert status == 200
    assert license_info is None
    assert last_modified is None


def test_validate_url_non_github_client_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_head(*args, **kwargs):
        return DummyResponse(404)

    monkeypatch.setattr(validate_links.requests, "head", fake_head)

    ok, status, _, _ = validate_links.validate_url("https://example.com/missing")
    assert ok is False
    assert status == 404


def test_validate_url_non_github_retries_on_server_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    responses = iter([DummyResponse(500), DummyResponse(200)])

    def fake_head(*args, **kwargs):
        return next(responses)

    monkeypatch.setattr(validate_links.requests, "head", fake_head)
    monkeypatch.setattr(validate_links.random, "uniform", lambda *_: 0)
    monkeypatch.setattr(validate_links.time, "sleep", lambda *_: None)

    ok, status, _, _ = validate_links.validate_url("https://example.com", max_retries=2)
    assert ok is True
    assert status == 200


def test_validate_url_github_file_enriches_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_request(api_url: str, params: dict[str, object] | None = None):
        return 200, {}, {"ok": True}

    monkeypatch.setattr(validate_links, "github_request_json_paced", fake_request)
    monkeypatch.setattr(validate_links, "get_github_license", lambda *_: "MIT")
    monkeypatch.setattr(
        validate_links,
        "get_github_last_modified",
        lambda *_: "2024-05-01:00-00-00",
    )

    ok, status, license_info, last_modified = validate_links.validate_url(
        "https://github.com/owner/repo/blob/main/README.md"
    )
    assert ok is True
    assert status == 200
    assert license_info == "MIT"
    assert last_modified == "2024-05-01:00-00-00"


def test_validate_url_github_rate_limit_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    reset_at = str(int(time.time()))
    responses = iter(
        [
            (403, {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": reset_at}, None),
            (200, {}, {"ok": True}),
        ]
    )

    def fake_request(api_url: str, params: dict[str, object] | None = None):
        return next(responses)

    sleep_calls: list[float] = []

    def fake_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    monkeypatch.setattr(validate_links, "github_request_json_paced", fake_request)
    monkeypatch.setattr(validate_links.time, "sleep", fake_sleep)
    monkeypatch.setattr(validate_links, "get_github_license", lambda *_: None)
    monkeypatch.setattr(validate_links, "get_github_last_modified", lambda *_: None)

    ok, status, _, _ = validate_links.validate_url("https://github.com/owner/repo")
    assert ok is True
    assert status == 200
    assert len(sleep_calls) == 1
