"""Stable resource IDs: {category-prefix}-{sha1(link)[:8]}.

Matches the scheme used to bootstrap the CSV, so a
re-submission of the same link yields the same ID. Hashing the link (not the name)
means a renamed resource keeps its ID.
"""

from __future__ import annotations

import hashlib

from resources.categories import category_prefixes


def generate_resource_id(display_name: str, link: str, category: str) -> str:
    prefix = category_prefixes().get(category, "res")
    digest = hashlib.sha1(link.strip().encode("utf-8")).hexdigest()[:8]
    return f"{prefix}-{digest}"
