"""
Temporary test to verify the auto-locking behavior of the refactored override system.
This test confirms that setting a field in overrides automatically locks it from validation updates.

Context: Refactored the override system so that any field set in resource-overrides.yaml
is automatically locked without needing explicit *_locked flags.
"""

import os
import sys

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from scripts.validation.validate_links import apply_overrides  # noqa: E402


def test_auto_locking():
    """Test that setting a field automatically locks it."""
    # Sample resource row
    row = {
        "ID": "test-123",
        "Display Name": "Test Resource",
        "License": "Apache-2.0",
        "Active": "TRUE",
        "Last Checked": "2025-01-01:12-00-00",
    }

    # Override config without *_locked flags (new format)
    overrides = {
        "test-123": {
            "license": "MIT",  # Should auto-lock
            "active": "FALSE",  # Should auto-lock
        }
    }

    # Apply overrides
    updated_row, locked_fields, skip_validation = apply_overrides(row, overrides)

    # Verify override values were applied
    assert updated_row["License"] == "MIT", "License override not applied"
    assert updated_row["Active"] == "FALSE", "Active override not applied"

    # Verify fields are automatically locked
    assert "license" in locked_fields, "License field not auto-locked"
    assert "active" in locked_fields, "Active field not auto-locked"

    # Verify skip_validation is False
    assert skip_validation is False, "skip_validation should be False"

    print("✅ Test passed: Fields are automatically locked when set in overrides")


def test_skip_validation_precedence():
    """Test that skip_validation has highest precedence."""
    row = {"ID": "test-456", "Display Name": "Skipped Resource"}

    overrides = {"test-456": {"skip_validation": True, "license": "MIT"}}

    updated_row, locked_fields, skip_validation = apply_overrides(row, overrides)

    # Verify skip_validation is True
    assert skip_validation is True, "skip_validation should be True"

    # Verify license was still applied and locked
    assert updated_row["License"] == "MIT", "License override not applied"
    assert "license" in locked_fields, "License field not auto-locked"

    print("✅ Test passed: skip_validation has highest precedence")


def test_legacy_locked_flags_ignored():
    """Test that legacy *_locked flags are properly ignored."""
    row = {"ID": "test-789", "License": "Apache-2.0"}

    # Override config with legacy *_locked flag (should be ignored)
    overrides = {
        "test-789": {
            "license": "MIT",
            "license_locked": True,  # Legacy flag, should be ignored
        }
    }

    updated_row, locked_fields, skip_validation = apply_overrides(row, overrides)

    # Verify override was applied
    assert updated_row["License"] == "MIT", "License override not applied"

    # Verify field is still auto-locked (from the field value, not the legacy flag)
    assert "license" in locked_fields, "License field not auto-locked"

    print("✅ Test passed: Legacy *_locked flags are properly ignored")


def test_notes_field_ignored():
    """Test that notes field doesn't cause auto-locking."""
    row = {"ID": "test-notes", "License": "MIT"}

    overrides = {"test-notes": {"notes": "This is a note"}}

    updated_row, locked_fields, skip_validation = apply_overrides(row, overrides)

    # Verify no fields are locked
    assert len(locked_fields) == 0, "Notes field should not cause auto-locking"

    print("✅ Test passed: Notes field doesn't cause auto-locking")


if __name__ == "__main__":
    print("Running override auto-lock verification tests...\n")

    test_auto_locking()
    test_skip_validation_precedence()
    test_legacy_locked_flags_ignored()
    test_notes_field_ignored()

    print("\n🎉 All verification tests passed!")
    print("The refactored override system is working correctly.")
