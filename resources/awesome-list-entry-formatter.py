"""List Entry Formatter

Turns a single CSV row (see THE_RESOURCES_TABLE_NEW.csv) into an Awesome-formatted
markdown entry, complete with live Shields.io badges for GitHub-hosted resources.
The orchestrator generate_readme.py imports format_entry() from this module.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

# A github owner/repo segment. Anything outside this set (quotes, angle brackets,
# spaces) in a submitted Link could break out of the badge <img src="..."> and
# inject HTML attributes/handlers, so a non-matching link simply gets NO badge.
_GH_SEGMENT = re.compile(r"^[A-Za-z0-9._-]+$")


def _md_text(value: str) -> str:
    """Escape HTML-tag characters in a foreign (submitted) field before it lands
    in the rendered markdown/HTML, so a description/name can't inject a live
    <script>/<img onerror=...> element. Ampersand first so we don't double-escape.
    Quotes are left as-is: without '<' you cannot open a tag in text context."""
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# Shields.io endpoints, in display order. (key, alt-text, url-template)
_BADGE_SPECS: list[tuple[str, str, str]] = [
    ("created", "created", "https://img.shields.io/github/created-at/{owner}/{repo}"),
    ("last_commit", "last-commit", "https://img.shields.io/github/last-commit/{owner}/{repo}"),
    ("license", "license", "https://img.shields.io/github/license/{owner}/{repo}"),
    ("stars", "stars", "https://img.shields.io/github/stars/{owner}/{repo}"),
]

# Neutral, monochrome styling so the list reads black-and-white instead of a wall
# of shields-default colors: dark-grey label, medium-grey message, white text.
_BADGE_STYLE = "style=flat-square&labelColor=2b2b2b&color=6b6b6b"


def parse_github(url: str) -> tuple[str, str] | None:
    """Return (owner, repo) for a github.com repo URL, else None.

    Tolerates trailing slashes, .git suffixes, and deeper paths (e.g.
    /tree/main/...) by taking the first two path segments.
    """
    parsed = urlparse(url.strip())
    if parsed.netloc.lower().removeprefix("www.") != "github.com":
        return None
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    # Reject anything that isn't a clean owner/repo — a crafted Link like
    # https://github.com/o/r"onerror=alert(1) would otherwise be interpolated
    # raw into the badge <img src="...">. No badge is safer than an injected one.
    if not (_GH_SEGMENT.match(owner) and _GH_SEGMENT.match(repo)):
        return None
    return owner, repo


def generate_shields_badges(owner: str, repo: str) -> dict[str, str]:
    """Return shields.io badge <img> tags keyed by type.

    Keys: created, last_commit, license, stars.
    """
    badges: dict[str, str] = {}
    for key, alt, url_tmpl in _BADGE_SPECS:
        url = url_tmpl.format(owner=owner, repo=repo)
        badges[key] = f'<img src="{url}?{_BADGE_STYLE}" alt="{alt}">'
    return badges


def _author_md(name: str, link: str) -> str:
    """Return [name](link) when a link is present, else plain name.

    The author name is a foreign field, so it is HTML-escaped; the link's scheme
    is validated upstream (parse_issue_form) but we still neutralize any stray
    angle brackets defensively.
    """
    name = _md_text(name.strip())
    link = link.strip().replace("<", "%3C").replace(">", "%3E")
    if not name:
        return ""
    return f"[{name}]({link})" if link else name


def format_entry(row: dict[str, str]) -> str:
    """Render one CSV row as an Awesome-list markdown entry."""
    # Display Name / Description come from submitted issue forms — escape them so
    # they render as text, never as live HTML. The Link's scheme is validated at
    # submission time; angle brackets are neutralized defensively for the md target.
    name = _md_text(row["Display Name"].strip())
    link = row["Link"].strip().replace("<", "%3C").replace(">", "%3E")
    description = _md_text(row.get("Description", "").strip())
    author = _author_md(row.get("Author Name", ""), row.get("Author Link", ""))

    by = f" by {author}" if author else ""
    dash = f" - {description}" if description else ""
    bullet = f"- [{name}]({link}){by}{dash}"

    parsed = parse_github(link)
    if parsed is None:
        return bullet

    badges = generate_shields_badges(*parsed)
    # Badges only, no prose labels: each shields badge already renders its own
    # label ("created" / "last commit" / "license" / "stars"), so a "Created:"/
    # "Stars:" prefix just duplicates it. Join with two non-breaking spaces for a
    # small margin between badges — GitHub's markdown sanitizer strips inline
    # `style`, so &nbsp; is the reliable way to add horizontal spacing.
    badge_line = "&nbsp;&nbsp;".join(
        badges[key] for key in ("created", "last_commit", "license", "stars")
    )
    # Two trailing spaces = a CommonMark hard break, so the badge line renders on
    # its own line under the bullet (a single newline is only a soft break in a
    # GitHub README file, which would otherwise collapse onto the description).
    return f"{bullet}  \n{badge_line}"
