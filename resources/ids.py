"""Opaque resource IDs: a random 8-char hex token, coupled to nothing.

Minted once when a resource is added and stored verbatim in the CSV. The ID is a
surrogate handle deliberately independent of link, name, and category, so any of
those can change without the row's identity moving. Existing prefixed IDs
(``docs-…``, ``memory-…``) are grandfathered as-is; nothing derives meaning from
the prefix, and dedupe is done on the link (see ``parse_issue_form`` /
``add_resource``), never on the ID.
"""

from __future__ import annotations

import secrets


def generate_resource_id() -> str:
    """Return a fresh opaque 8-char hex ID."""
    return secrets.token_hex(4)
