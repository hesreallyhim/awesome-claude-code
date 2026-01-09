#!/usr/bin/env python3
"""
Shared resource ID generation functionality.
"""

import hashlib
import sys
from pathlib import Path

from scripts.utils.repo_root import find_repo_root

REPO_ROOT = find_repo_root(Path(__file__))
sys.path.insert(0, str(REPO_ROOT))

from scripts.categories.category_utils import category_manager  # noqa: E402


def generate_resource_id(display_name: str, primary_link: str, category: str) -> str:
    """
    Generate a stable resource ID from display name, link, and category.

    Args:
        display_name: The display name of the resource
        primary_link: The primary URL of the resource
        category: The category name

    Returns:
        A resource ID in format: {prefix}-{hash}
    """
    # Get category prefix mapping
    prefixes = category_manager.get_category_prefixes()
    prefix = prefixes.get(category, "res")

    # Generate hash from display name + primary link
    content = f"{display_name}{primary_link}"
    hash_value = hashlib.sha256(content.encode()).hexdigest()[:8]

    return f"{prefix}-{hash_value}"
