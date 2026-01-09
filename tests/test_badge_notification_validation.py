#!/usr/bin/env python3
"""
Security validation tests for badge notification system
Tests that dangerous inputs are REJECTED, not sanitized
"""

import sys
from pathlib import Path

import pytest

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from scripts.badges.badge_notification_core import BadgeNotificationCore  # noqa: E402


def test_dangerous_input_rejection() -> None:
    """Test that dangerous inputs are rejected, not modified"""
    print("Testing Dangerous Input Rejection...")

    # Test cases that should be REJECTED
    dangerous_inputs = [
        ("<script>alert('XSS')</script>", "HTML script tag"),
        ("</textarea><script>alert('XSS')</script>", "Script with closing tag"),
        ("<img src=x onerror=alert('XSS')>", "Image with onerror"),
        ("<iframe src='evil.com'></iframe>", "Iframe injection"),
        ("javascript:alert('XSS')", "JavaScript protocol"),
        ("data:text/html,<script>alert('XSS')</script>", "Data protocol"),
        ("vbscript:msgbox('XSS')", "VBScript protocol"),
        ("<svg onload=alert('XSS')>", "SVG with event handler"),
        ("Test onclick=alert('XSS')", "Inline event handler"),
        ("file:///etc/passwd", "File protocol"),
        ("Test\x00with null", "Null byte injection"),
        ("Test" + chr(7) + "bell", "Control character"),
    ]

    for payload, description in dangerous_inputs:
        is_safe, reason = BadgeNotificationCore.validate_input_safety(payload, "test_field")
        assert not is_safe, f"Failed to reject: {description}"
        assert reason, f"No reason provided for rejection: {description}"
        print(f"  ✓ Rejected: {description} - Reason: {reason}")


def test_safe_input_acceptance() -> None:
    """Test that legitimate inputs are accepted"""
    print("\nTesting Safe Input Acceptance...")

    # Test cases that should be ACCEPTED
    safe_inputs = [
        ("Claude Code Tools", "Normal project name"),
        ("A tool for enhancing productivity", "Normal description"),
        ("Project-Name_123", "Name with special chars"),
        ("Version 2.0 (Beta)", "Parentheses and dots"),
        ("# Best Practices Guide", "Markdown heading in plain text"),
        ("Use `code` blocks", "Backticks in description"),
        ("Email: user@example.com", "Email address"),
        ("https://github.com/owner/repo", "GitHub URL"),
        ("Line 1\nLine 2\nLine 3", "Multi-line text"),
        ("Unicode: 你好 мир 🚀", "Unicode characters"),
    ]

    for payload, description in safe_inputs:
        is_safe, reason = BadgeNotificationCore.validate_input_safety(payload, "test_field")
        assert is_safe, f"Incorrectly rejected safe input: {description}. Reason: {reason}"
        print(f"  ✓ Accepted: {description}")


def test_length_limit_enforcement() -> None:
    """Test that overly long inputs are rejected"""
    print("\nTesting Length Limit Enforcement...")

    # Very long input (over 5000 chars)
    long_input = "A" * 5001
    is_safe, reason = BadgeNotificationCore.validate_input_safety(long_input, "test_field")
    assert not is_safe, "Failed to reject overly long input"
    assert "exceeds maximum length" in reason, f"Wrong rejection reason: {reason}"
    print("  ✓ Rejected input over 5000 characters")

    # Input at the limit should be accepted
    limit_input = "A" * 5000
    is_safe, reason = BadgeNotificationCore.validate_input_safety(limit_input, "test_field")
    assert is_safe, "Incorrectly rejected input at length limit"
    print("  ✓ Accepted input at 5000 character limit")


def test_case_insensitive_detection() -> None:
    """Test that dangerous patterns are detected case-insensitively"""
    print("\nTesting Case-Insensitive Detection...")

    case_variants = [
        ("JAVASCRIPT:alert('XSS')", "Uppercase protocol"),
        ("JaVaScRiPt:alert('XSS')", "Mixed case protocol"),
        ("<SCRIPT>alert('XSS')</SCRIPT>", "Uppercase tags"),
        ("<ScRiPt>alert('XSS')</ScRiPt>", "Mixed case tags"),
        ("ONCLICK=alert('XSS')", "Uppercase event handler"),
    ]

    for payload, description in case_variants:
        is_safe, reason = BadgeNotificationCore.validate_input_safety(payload, "test_field")
        assert not is_safe, f"Failed to reject: {description}"
        print(f"  ✓ Rejected: {description}")


@pytest.mark.usefixtures("github_stub")
def test_issue_creation_with_validation() -> None:
    """Test that issue creation fails with dangerous inputs"""
    print("\nTesting Issue Creation with Validation...")

    notifier = BadgeNotificationCore("fake_token")

    # Test with dangerous resource name
    try:
        notifier.create_issue_body("<script>alert('XSS')</script>", "Normal description")
        raise AssertionError("Should have raised ValueError for dangerous resource name")
    except ValueError as e:
        assert "Security validation failed" in str(e)
        print("  ✓ Issue creation blocked for dangerous resource name")

    # Test with dangerous description
    try:
        notifier.create_issue_body("Normal Name", "javascript:alert('XSS')")
        raise AssertionError("Should have raised ValueError for dangerous description")
    except ValueError as e:
        assert "Security validation failed" in str(e)
        print("  ✓ Issue creation blocked for dangerous description")

    # Test with safe inputs (should not raise)
    try:
        body = notifier.create_issue_body("Safe Project", "A safe description")
        assert "Safe Project" in body, "Original text should be in output"
        assert "A safe description" in body, "Original description should be in output"
        print("  ✓ Issue creation allowed for safe inputs")
    except ValueError as e:
        raise AssertionError(f"Should not have raised ValueError for safe inputs: {e}") from e


@pytest.mark.usefixtures("github_stub")
def test_notification_creation_flow() -> None:
    """Test the full notification creation flow with validation"""
    print("\nTesting Full Notification Creation Flow...")

    notifier = BadgeNotificationCore("fake_token")

    # Test that dangerous inputs result in failed notification
    result = notifier.create_notification_issue(
        repo_url="https://github.com/owner/repo",
        resource_name="<script>alert('XSS')</script>",
        description="Normal description",
    )

    assert not result["success"], "Should have failed with dangerous input"
    assert "Security validation failed" in result["message"], (
        f"Wrong error message: {result['message']}"
    )
    print("  ✓ Notification creation blocked for dangerous input")


def run_all_tests() -> bool:
    """Run all validation tests"""
    print("=" * 60)
    print("Badge Notification Validation Test Suite")
    print("=" * 60)

    try:
        test_dangerous_input_rejection()
        test_safe_input_acceptance()
        test_length_limit_enforcement()
        test_case_insensitive_detection()
        test_issue_creation_with_validation()
        test_notification_creation_flow()

        print("\n" + "=" * 60)
        print("✅ All validation tests passed!")
        print("=" * 60)
        return True

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
