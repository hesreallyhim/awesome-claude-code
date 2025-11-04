#!/usr/bin/env python3
"""
Daily dashboard for "Claude Code" trending repositories that writes top 5 to trending.csv
and persists a snapshot for delta calculations between runs.

Growth score:
  score = STAR_WEIGHT * (stars_delta / max(prev_stars, 1))
         + FORK_WEIGHT * (forks_delta / max(prev_forks, 1))
Ties: stars_delta desc, then stars_total desc

Environment variables (all optional):
  TOP_N            default 5
  MIN_STARS_TOTAL  default 10
  STAR_WEIGHT      default 0.85
  FORK_WEIGHT      default 0.15
  GITHUB_TOKEN     required in CI (provided by Actions)

Outputs:
  - trending.csv at repo root (overwrites)
  - .github/claude-trending-snapshot.json (updated)
"""

import csv
import datetime as dt
import json
import os
import sys
import time
from typing import Any

import requests

TOP_N = int(os.environ.get("TOP_N", "5"))
MIN_STARS_TOTAL = int(os.environ.get("MIN_STARS_TOTAL", "10"))
STAR_WEIGHT = float(os.environ.get("STAR_WEIGHT", "0.85"))
FORK_WEIGHT = float(os.environ.get("FORK_WEIGHT", "0.15"))
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

# API request configuration
MAX_PAGES = 10
REQUEST_DELAY_SECONDS = 0.2
MIN_DIVISOR = 1

HEADERS = {
    "Accept": "application/vnd.github.v3+json",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

SEARCH_QUERIES = [
    "claude in:name,description,readme fork:false archived:false",
    '"claude code" in:name,description,readme fork:false archived:false',
    "topic:claude fork:false archived:false",
    "topic:claude-code fork:false archived:false",
]
SEARCH_PER_PAGE = 100
SNAPSHOT_PATH = ".github/claude-trending-snapshot.json"
CSV_PATH = "trending.csv"
SEED_REPO = "hesreallyhim/awesome-claude-code"


def iso_now():
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def gh_get(url: str, params: dict[str, Any] | None = None) -> requests.Response:
    r = requests.get(url, headers=HEADERS, params=params)
    if r.status_code == 403 and r.headers.get("X-RateLimit-Remaining") == "0":
        reset = int(r.headers.get("X-RateLimit-Reset", "0"))
        wait = max(0, reset - int(time.time()) + 1)
        print(f"Rate limit hit. Sleeping {wait}s...", file=sys.stderr)
        time.sleep(wait)
        r = requests.get(url, headers=HEADERS, params=params)
    r.raise_for_status()
    return r


def search_repos() -> list[dict[str, Any]]:
    seen = set()
    results: list[dict[str, Any]] = []
    for q in SEARCH_QUERIES:
        for page in range(1, MAX_PAGES + 1):
            r = gh_get(
                "https://api.github.com/search/repositories",
                params={"q": q, "per_page": SEARCH_PER_PAGE, "page": page},
            )
            data = r.json()
            items = data.get("items", [])
            if not items:
                break
            for it in items:
                full = it.get("full_name")
                if not full or full in seen:
                    continue
                seen.add(full)
                # filter extra noise here too
                if it.get("fork") or it.get("archived"):
                    continue
                if it.get("stargazers_count", 0) < MIN_STARS_TOTAL:
                    continue
                results.append(it)
            if len(items) < SEARCH_PER_PAGE:
                break
            time.sleep(REQUEST_DELAY_SECONDS)
    # ensure seed repo present
    if SEED_REPO not in {r["full_name"] for r in results}:
        try:
            seed = gh_get(f"https://api.github.com/repos/{SEED_REPO}").json()
            if not seed.get("fork") and not seed.get("archived"):
                results.append(seed)
        except Exception as e:
            print(f"Warning: could not add seed {SEED_REPO}: {e}", file=sys.stderr)
    return results


def load_snapshot() -> dict[str, dict[str, int]]:
    if not os.path.exists(SNAPSHOT_PATH):
        return {}
    try:
        with open(SNAPSHOT_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("repos", {})
    except Exception as e:
        print(f"Warning: failed reading snapshot: {e}", file=sys.stderr)
        return {}


def save_snapshot(current: dict[str, dict[str, int]]):
    os.makedirs(os.path.dirname(SNAPSHOT_PATH), exist_ok=True)
    with open(SNAPSHOT_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "generated_at": iso_now(),
                "repos": current,
            },
            f,
            indent=2,
        )


def safe_desc(s: str | None) -> str:
    if not s:
        return ""
    # one-line for CSV
    return s.replace("\n", " ").replace("\r", " ").strip()


def main():
    print("Searching candidate repositories…")
    items = search_repos()

    prev = load_snapshot()  # map full_name -> {stars, forks}

    scored: list[dict[str, Any]] = []
    current_map: dict[str, dict[str, int]] = {}

    for it in items:
        full = it["full_name"]
        stars_total = int(it.get("stargazers_count", 0))
        forks_total = int(it.get("forks_count", 0))
        current_map[full] = {"stars": stars_total, "forks": forks_total}

        prev_entry = prev.get(full, {"stars": 0, "forks": 0})
        prev_stars = int(prev_entry.get("stars", 0))
        prev_forks = int(prev_entry.get("forks", 0))

        stars_delta = max(0, stars_total - prev_stars)
        forks_delta = max(0, forks_total - prev_forks)

        star_prop = (stars_delta / max(prev_stars, MIN_DIVISOR)) if stars_delta > 0 else 0.0
        fork_prop = (forks_delta / max(prev_forks, MIN_DIVISOR)) if forks_delta > 0 else 0.0

        score = STAR_WEIGHT * star_prop + FORK_WEIGHT * fork_prop

        scored.append(
            {
                "full_name": full,
                "url": it.get("html_url", ""),
                "description": safe_desc(it.get("description")),
                "stars_total": stars_total,
                "forks_total": forks_total,
                "stars_delta": stars_delta,
                "forks_delta": forks_delta,
                "star_prop": star_prop,
                "fork_prop": fork_prop,
                "score": score,
            }
        )

    # rank: score desc, then stars_delta desc, then stars_total desc
    scored.sort(key=lambda x: (x["score"], x["stars_delta"], x["stars_total"]), reverse=True)
    top = scored[:TOP_N]

    # Write CSV
    today = dt.datetime.utcnow().date().isoformat()
    fieldnames = [
        "date",
        "rank",
        "full_name",
        "url",
        "description",
        "stars_total",
        "stars_delta",
        "star_prop",
        "forks_total",
        "forks_delta",
        "fork_prop",
        "score",
    ]

    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for idx, r in enumerate(top, start=1):
            row = {
                "date": today,
                "rank": idx,
                "full_name": r["full_name"],
                "url": r["url"],
                "description": r["description"],
                "stars_total": r["stars_total"],
                "stars_delta": r["stars_delta"],
                "star_prop": f"{r['star_prop']:.4f}",
                "forks_total": r["forks_total"],
                "forks_delta": r["forks_delta"],
                "fork_prop": f"{r['fork_prop']:.4f}",
                "score": f"{r['score']:.4f}",
            }
            writer.writerow(row)

    # Persist snapshot
    save_snapshot(current_map)

    print(f"Wrote {CSV_PATH} with {len(top)} rows and updated snapshot {SNAPSHOT_PATH}")


if __name__ == "__main__":
    main()
