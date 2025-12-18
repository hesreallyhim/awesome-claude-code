#!/usr/bin/env python3
"""Test for the refactored get_last_resource_name method."""

import sys
from pathlib import Path

from scripts.submit_resource import ResourceSubmitter  # type: ignore

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_get_last_resource_name() -> None:
    """Test that get_last_resource_name returns a non-empty string."""
    submitter = ResourceSubmitter(debug=True)
    result = submitter.get_last_resource_name()

    # Assert that we got a result
    assert result is not None, "get_last_resource_name should return a resource name"
    assert isinstance(result, str), "Result should be a string"
    assert len(result) > 0, "Result should not be an empty string"


def test_slugify() -> None:
    """Test that slugify properly converts resource names."""
    submitter = ResourceSubmitter(debug=True)

    # Test with known inputs
    test_cases = [
        ("Claude Desktop", "claude-desktop"),
        ("Test Resource 123", "test-resource-123"),
        ("UPPERCASE NAME", "uppercase-name"),
        ("Multiple   Spaces", "multiple-spaces"),
        ("Special!@#Characters", "specialcharacters"),
    ]

    for input_text, expected in test_cases:
        result = submitter.slugify(input_text)
        assert result == expected, (
            f"slugify('{input_text}') should return '{expected}', got '{result}'"
        )


def test_integration() -> None:
    """Test get_last_resource_name and slugify together."""
    submitter = ResourceSubmitter(debug=True)
    resource_name = submitter.get_last_resource_name()

    if resource_name:
        slug = submitter.slugify(resource_name)
        assert slug, "Slugified result should not be empty"
        assert isinstance(slug, str), "Slugified result should be a string"
        assert " " not in slug, "Slug should not contain spaces"
        assert slug.islower(), "Slug should be lowercase"


if __name__ == "__main__":
    print("Testing get_last_resource_name...")
    test_get_last_resource_name()
    print("✓ Last resource name test passed")

    print("\nTesting slugify...")
    test_slugify()
    print("✓ All slugify tests passed")

    print("\nTesting integration...")
    test_integration()
    print("✓ Integration test passed")

    print("\nAll tests passed!")
