#!/usr/bin/env python3
"""Quick test of the refactored get_last_resource_name method."""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from scripts.submit_resource import ResourceSubmitter

# Create an instance
submitter = ResourceSubmitter(debug=True)

# Test the method
result = submitter.get_last_resource_name()
print(f"\nLast resource name: {result}")

# Test slugify
if result:
    slug = submitter.slugify(result)
    print(f"Slugified: {slug}")
