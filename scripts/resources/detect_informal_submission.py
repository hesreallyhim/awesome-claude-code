"""
Detect informal resource submissions that didn't use the issue template.

Returns a confidence score and recommended action:
- score >= 0.6: High confidence - auto-close with firm warning
- 0.4 <= score < 0.6: Medium confidence - gentle warning, leave open
- score < 0.4: Low confidence - no action

Usage:
    Set ISSUE_TITLE and ISSUE_BODY environment variables, then run:
    python -m scripts.resources.detect_informal_submission

    Outputs GitHub Actions outputs:
    - action: "none" | "warn" | "close"
    - confidence: float (0.0 to 1.0) formatted as percentage
    - matched_signals: comma-separated list of matched signals
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from enum import Enum


class Action(Enum):
    NONE = "none"
    WARN = "warn"  # Medium confidence: warn but don't close
    CLOSE = "close"  # High confidence: warn and close


@dataclass
class DetectionResult:
    confidence: float
    action: Action
    matched_signals: list[str]


# Template field labels - VERY strong indicator (from the issue form)
# Matching 3+ of these is almost certainly a copy-paste from template without using form
TEMPLATE_FIELD_LABELS = [
    "display name:",
    "category:",
    "sub-category:",
    "primary link:",
    "author name:",
    "author link:",
    "license:",
    "description:",
    "validate claims:",
    "specific task",
    "specific prompt",
    "additional comments:",
]

# Strong signals: clear intent to submit/recommend a resource
STRONG_SIGNALS: list[tuple[str, str]] = [
    (r"\b(recommend(ing)?|submit(ting)?|submission)\b", "submission language"),
    (r"\b(add|include).*\b(resource|tool|plugin)\b", "add resource request"),
    (r"\b(please add|check.?out|made this|created this|built this)\b", "creator language"),
    (
        r"\b(would be great|might be useful|could be added|should be added)\b",
        "suggestion language",
    ),
    (r"\bnew (tool|plugin|skill|hook|command)\b", "new resource mention"),
]

# Medium signals: contextual indicators
MEDIUM_SIGNALS: list[tuple[str, str]] = [
    (r"github\.com/[\w-]+/[\w-]+", "GitHub repo URL"),
    (r"\b(plugin|skill|hook|slash.?command|claude\.md)\b", "resource type mention"),
    (r"\b(agent skills?|tooling|workflows?|status.?lines?)\b", "category mention"),
    (r"\bhttps?://\S+", "contains URL"),
    (r"\bMIT|Apache|GPL|BSD|ISC\b", "license mention"),
]

# Negative signals: reduce score if these are present (likely bug/question)
NEGATIVE_SIGNALS: list[tuple[str, str]] = [
    (r"\b(bug|error|crash|broken|fix|issue|problem)\b", "bug-like language"),
    (r"\b(how (do|can|to)|what is|why does)\b", "question language"),
    (r"\b(not working|doesn't work|failed)\b", "failure language"),
]

HIGH_THRESHOLD = 0.6
MEDIUM_THRESHOLD = 0.4


def count_template_field_matches(text: str) -> int:
    """Count how many template field labels appear in the text."""
    text_lower = text.lower()
    return sum(1 for label in TEMPLATE_FIELD_LABELS if label in text_lower)


def calculate_confidence(title: str, body: str) -> DetectionResult:
    """Calculate confidence that this is an informal resource submission."""
    text = f"{title}\n{body}".lower()
    score = 0.0
    matched: list[str] = []

    # Check for template field labels (VERY strong indicator)
    # 3+ matches = almost certainly tried to copy template format
    template_matches = count_template_field_matches(text)
    if template_matches >= 3:
        # This is a near-certain match - set high score immediately
        score += 0.7
        matched.append(f"template-fields: {template_matches} matches")
    elif template_matches >= 1:
        score += 0.2 * template_matches
        matched.append(f"template-fields: {template_matches} matches")

    # Check strong signals (+0.3 each, max contribution ~0.9)
    for pattern, name in STRONG_SIGNALS:
        if re.search(pattern, text, re.IGNORECASE):
            score += 0.3
            matched.append(f"strong: {name}")

    # Check medium signals (+0.15 each)
    for pattern, name in MEDIUM_SIGNALS:
        if re.search(pattern, text, re.IGNORECASE):
            score += 0.15
            matched.append(f"medium: {name}")

    # Check negative signals (-0.2 each)
    for pattern, name in NEGATIVE_SIGNALS:
        if re.search(pattern, text, re.IGNORECASE):
            score -= 0.2
            matched.append(f"negative: {name}")

    # Clamp score to [0, 1]
    score = max(0.0, min(1.0, score))

    # Determine action based on thresholds
    if score >= HIGH_THRESHOLD:
        action = Action.CLOSE
    elif score >= MEDIUM_THRESHOLD:
        action = Action.WARN
    else:
        action = Action.NONE

    return DetectionResult(confidence=score, action=action, matched_signals=matched)


def sanitize_output(value: str) -> str:
    """Sanitize a value for safe use in GitHub Actions outputs.

    Prevents:
    - Newline injection (could add fake output variables)
    - Carriage return injection
    - Null byte injection
    """
    # Remove characters that could break GITHUB_OUTPUT format or cause injection
    return value.replace("\n", " ").replace("\r", " ").replace("\0", "")


def set_github_output(name: str, value: str) -> None:
    """Set a GitHub Actions output variable safely."""
    # Sanitize both name and value to prevent injection attacks
    safe_name = sanitize_output(name)
    safe_value = sanitize_output(value)

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"{safe_name}={safe_value}\n")
    else:
        # For local testing, just print
        print(f"::set-output name={safe_name}::{safe_value}")


def main() -> None:
    """Entry point for GitHub Actions."""
    title = os.environ.get("ISSUE_TITLE", "")
    body = os.environ.get("ISSUE_BODY", "")

    result = calculate_confidence(title, body)

    # Output results for GitHub Actions
    set_github_output("action", result.action.value)
    set_github_output("confidence", f"{result.confidence:.0%}")
    set_github_output("matched_signals", ", ".join(result.matched_signals))

    # Also print for logging
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Action: {result.action.value}")
    print(f"Matched signals: {result.matched_signals}")


if __name__ == "__main__":
    main()
