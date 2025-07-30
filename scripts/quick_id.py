#!/usr/bin/env python3
"""Quick one-liner to generate a resource ID."""

import hashlib
import sys

if len(sys.argv) != 4:
    print("Usage: python quick_id.py 'Display Name' 'https://link.com' 'Category'")
    print(
        "Categories: Slash-Commands, Workflows & Knowledge Guides, Tooling, "
        "CLAUDE.md Files, Hooks, Official Documentation"
    )
    sys.exit(1)

prefixes = {
    "Slash-Commands": "cmd",
    "Workflows & Knowledge Guides": "wf",
    "Tooling": "tool",
    "CLAUDE.md Files": "claude",
    "Hooks": "hook",
    "Official Documentation": "doc",
}

display_name, link, category = sys.argv[1:4]
prefix = prefixes.get(category, "res")
hash_val = hashlib.sha256(f"{display_name}{link}".encode()).hexdigest()[:8]
print(f"{prefix}-{hash_val}")
