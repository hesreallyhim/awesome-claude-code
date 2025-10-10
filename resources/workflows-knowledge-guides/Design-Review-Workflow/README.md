# Design Review Workflow

This directory contains templates and examples for implementing an automated design review system that provides feedback on front-end code changes with design implications. This workflow allows engineers to automatically run design reviews on pull requests or working changes, ensuring design consistency and quality throughout the development process.

## Concept

This workflow establishes a comprehensive methodology for automated design reviews in Claude Code, leveraging multiple advanced features to ensure world-class UI/UX standards in your codebase:

**Core Methodology:**
- **Automated Design Reviews**: Trigger comprehensive design assessments either automatically on PRs or on-demand via slash commands
- **Live Environment Testing**: Uses [Playwright MCP](https://github.com/microsoft/playwright-mcp) server integration to interact with and test actual UI components in real-time, not just static code analysis
- **Standards-Based Evaluation**: Follows rigorous design principles inspired by top-tier companies (Stripe, Airbnb, Linear), covering visual hierarchy, accessibility (WCAG AA+), responsive design, and interaction patterns

**Implementation Features:**
- **Claude Code Subagents**: Deploy specialized design review agents with pre-configured tools and prompts for consistent, thorough reviews, by taging `@agent-code-reviewer`
- **Slash Commands**: Enable instant design reviews with `/design-review` that automatically analyzes git diffs and provides structured feedback
- **CLAUDE.md Memory Integration**: Store design principles and brand guidelines in your project's CLAUDE.md file, ensuring Claude Code always references your specific design system
- **Multi-Phase Review Process**: Systematic evaluation covering interaction flows, responsiveness, visual polish, accessibility, robustness testing, and code health

This approach transforms design reviews from manual, subjective processes into automated, objective assessments that maintain consistency across your entire frontend development workflow.

## Resources

### Templates & Examples
- [Design Principles Example](./design-principles-example.md) - Sample design principles document for guiding automated reviews
- [Design Review Agent](./design-review-agent.md) - Agent configuration for automated design reviews
- [Claude.md Snippet](./design-review-claude-md-snippet.md) - Claude.md configuration snippet for design review integration
- [Slash Command](./design-review-slash-command.md) - Custom slash command implementation for on-demand design reviews

### Video Tutorial
For a detailed walkthrough of this workflow, watch the comprehensive tutorial on YouTube: [Patrick Ellis' Channel](https://www.youtube.com/watch?v=xOO8Wt_i72s)
