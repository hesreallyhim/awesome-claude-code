"""Tests for the informal submission detection module."""

from __future__ import annotations

from scripts.resources.detect_informal_submission import (
    Action,
    calculate_confidence,
    count_template_field_matches,
    sanitize_output,
)


class TestCountTemplateFieldMatches:
    """Tests for template field label detection."""

    def test_no_matches(self) -> None:
        """No template field labels in text."""
        text = "This is a regular issue about something."
        assert count_template_field_matches(text) == 0

    def test_single_match(self) -> None:
        """Single template field label detected."""
        text = "Display Name: My Awesome Tool"
        assert count_template_field_matches(text) == 1

    def test_multiple_matches(self) -> None:
        """Multiple template field labels detected."""
        text = """
        Display Name: My Tool
        Category: Agent Skills
        Primary Link: https://github.com/example/repo
        Author Name: John Doe
        """
        assert count_template_field_matches(text) == 4

    def test_case_insensitive(self) -> None:
        """Template field matching is case-insensitive."""
        text = "DISPLAY NAME: test\nPRIMARY LINK: https://example.com"
        assert count_template_field_matches(text) == 2


class TestCalculateConfidence:
    """Tests for confidence score calculation."""

    def test_empty_input(self) -> None:
        """Empty title and body should return no action."""
        result = calculate_confidence("", "")
        assert result.action == Action.NONE
        assert result.confidence == 0.0

    def test_high_confidence_template_fields(self) -> None:
        """3+ template field labels should trigger high confidence."""
        body = """
        Display Name: My Tool
        Category: Tooling
        Primary Link: https://github.com/example/repo
        Author Name: Jane
        License: MIT
        Description: A great tool for Claude Code users.
        """
        result = calculate_confidence("New resource submission", body)
        assert result.action == Action.CLOSE
        assert result.confidence >= 0.6

    def test_high_confidence_strong_signals(self) -> None:
        """Clear submission language should trigger high confidence."""
        result = calculate_confidence(
            "Please add my tool to the list",
            "Check out this awesome plugin I made: https://github.com/user/repo",
        )
        assert result.action == Action.CLOSE
        assert result.confidence >= 0.6

    def test_medium_confidence_partial_signals(self) -> None:
        """Partial signals should trigger medium confidence (warn only)."""
        # 3 medium signals (0.15 each) = 0.45, which is WARN territory
        result = calculate_confidence(
            "Interesting project",
            "Here's a skill at github.com/user/repo under MIT license",
        )
        assert result.action == Action.WARN
        assert 0.4 <= result.confidence < 0.6

    def test_low_confidence_bug_report(self) -> None:
        """Bug reports should not trigger any action."""
        result = calculate_confidence(
            "Bug: validation script crashes",
            "When I try to run the validation, I get an error. The problem is with the parser.",
        )
        assert result.action == Action.NONE
        assert result.confidence < 0.4

    def test_low_confidence_question(self) -> None:
        """Pure questions should not trigger any action."""
        result = calculate_confidence(
            "How does the validation work?",
            "What is the process for reviewing submissions? I want to understand.",
        )
        assert result.action == Action.NONE
        assert result.confidence < 0.4

    def test_negative_signals_reduce_score(self) -> None:
        """Negative signals should reduce the confidence score."""
        # This has a URL (medium signal) but also bug language (negative)
        result = calculate_confidence(
            "My tool is broken",
            "The plugin at github.com/user/repo is not working and has an error.",
        )
        # The negative signals should counteract the positive ones
        assert result.confidence < 0.6

    def test_feature_request_no_action(self) -> None:
        """Feature requests should not trigger action."""
        result = calculate_confidence(
            "Feature request: add dark mode",
            "It would be nice if the README had a dark mode toggle.",
        )
        assert result.action == Action.NONE

    def test_combined_signals(self) -> None:
        """Multiple strong signals should result in high confidence."""
        result = calculate_confidence(
            "Recommend new plugin",
            """
            I created this awesome plugin that should be added to the list.
            Check out github.com/user/cool-plugin
            It has MIT license.
            """,
        )
        assert result.action == Action.CLOSE
        assert len(result.matched_signals) >= 3

    def test_score_clamped_to_one(self) -> None:
        """Score should never exceed 1.0."""
        # Lots of positive signals
        body = """
        Display Name: tool
        Category: Skills
        Primary Link: https://github.com/a/b
        Author Name: x
        License: MIT
        Description: test
        I recommend this submission. Please add this new plugin.
        I built this tool and created it myself.
        Check out this awesome skill for agent workflows.
        """
        result = calculate_confidence("Please add my new tool submission", body)
        assert result.confidence <= 1.0

    def test_score_clamped_to_zero(self) -> None:
        """Score should never go below 0.0."""
        # Lots of negative signals, no positive
        result = calculate_confidence(
            "Bug: How do I fix this error?",
            "The problem is not working. It's broken and failed. What is wrong?",
        )
        assert result.confidence >= 0.0


class TestMatchedSignals:
    """Tests for matched signal reporting."""

    def test_strong_signals_labeled(self) -> None:
        """Strong signals should be labeled in matched_signals."""
        result = calculate_confidence("Please add my tool", "I recommend this submission")
        strong_signals = [s for s in result.matched_signals if s.startswith("strong:")]
        assert len(strong_signals) > 0

    def test_medium_signals_labeled(self) -> None:
        """Medium signals should be labeled in matched_signals."""
        result = calculate_confidence("Test", "https://github.com/user/repo")
        medium_signals = [s for s in result.matched_signals if s.startswith("medium:")]
        assert len(medium_signals) > 0

    def test_negative_signals_labeled(self) -> None:
        """Negative signals should be labeled in matched_signals."""
        result = calculate_confidence("Bug report", "This has an error and is broken")
        negative_signals = [s for s in result.matched_signals if s.startswith("negative:")]
        assert len(negative_signals) > 0

    def test_template_fields_labeled(self) -> None:
        """Template field matches should be labeled in matched_signals."""
        result = calculate_confidence("Test", "Display Name: X\nCategory: Y")
        template_signals = [s for s in result.matched_signals if s.startswith("template-fields:")]
        assert len(template_signals) == 1


class TestEdgeCases:
    """Edge case tests."""

    def test_url_with_bug_language(self) -> None:
        """URL mention with bug language should not trigger action."""
        result = calculate_confidence(
            "Issue with repo",
            "The plugin at github.com/user/repo crashes with an error",
        )
        # Bug language should neutralize the URL signal
        assert result.action in (Action.NONE, Action.WARN)

    def test_partial_template_fields(self) -> None:
        """1-2 template fields should give medium confidence at most."""
        result = calculate_confidence("", "Display Name: test\nDescription: something")
        # 2 fields = 0.4 score, which is exactly at medium threshold
        assert result.action in (Action.NONE, Action.WARN)

    def test_license_mention_alone(self) -> None:
        """License mention alone should not trigger high confidence."""
        result = calculate_confidence("Question about MIT", "Is this MIT licensed?")
        assert result.action == Action.NONE

    def test_category_mention_in_question(self) -> None:
        """Category mention in a question context should not trigger."""
        result = calculate_confidence(
            "How do hooks work?",
            "What is the difference between agent skills and hooks?",
        )
        assert result.action == Action.NONE


class TestSanitizeOutput:
    """Tests for output sanitization (security)."""

    def test_removes_newlines(self) -> None:
        """Newlines should be replaced to prevent output injection."""
        result = sanitize_output("line1\nline2\nline3")
        assert "\n" not in result
        assert result == "line1 line2 line3"

    def test_removes_carriage_returns(self) -> None:
        """Carriage returns should be replaced."""
        result = sanitize_output("line1\r\nline2")
        assert "\r" not in result
        assert "\n" not in result

    def test_removes_null_bytes(self) -> None:
        """Null bytes should be removed."""
        result = sanitize_output("before\0after")
        assert "\0" not in result
        assert result == "beforeafter"

    def test_preserves_normal_text(self) -> None:
        """Normal text should pass through unchanged."""
        normal = "This is a normal string with spaces and punctuation!"
        assert sanitize_output(normal) == normal

    def test_handles_empty_string(self) -> None:
        """Empty string should return empty string."""
        assert sanitize_output("") == ""

    def test_injection_attempt_via_newline(self) -> None:
        """Simulated injection attempt should be neutralized."""
        # An attacker might try to inject a fake output variable
        malicious = "legitimate\nmalicious_var=evil_value"
        result = sanitize_output(malicious)
        assert "malicious_var=evil_value" in result  # Content preserved
        assert "\n" not in result  # But newline removed
        assert result == "legitimate malicious_var=evil_value"
