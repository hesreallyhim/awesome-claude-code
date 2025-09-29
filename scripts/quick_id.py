#!/usr/bin/env python3
"""Quick one-liner to generate a resource ID."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.category_utils import category_manager  # noqa: E402
from scripts.resource_id import generate_resource_id  # noqa: E402

if len(sys.argv) != 4:
    categories = category_manager.get_all_categories()
    print("Usage: python quick_id.py 'Display Name' 'https://link.com' 'Category'")
    print(f"Categories: {', '.join(categories)}")
    sys.exit(1)

display_name, link, category = sys.argv[1:4]
resource_id = generate_resource_id(display_name, link, category)
print(resource_id)
