# Claude Code AI Agent System

## Project Overview

This is an autonomous AI agent system built with Claude Code that can learn new skills iteratively, execute complex workflows, navigate web applications, and create content — all without OpenClaw.

## Architecture

```
claude-agent/
├── skills/          # Reusable skill files (.md)
├── scripts/         # Helper scripts (browser automation, etc.)
├── src/             # Remotion video project source
├── config/          # Configuration files
└── output/          # Generated content (videos, screenshots, etc.)
```

## Key Conventions

- Skills are stored as `.md` files in `claude-agent/skills/`
- Each skill contains step-by-step workflows with CSS selectors and JS snippets
- Browser automation uses Puppeteer with Chrome DevTools Protocol (CDP)
- Video creation uses Remotion (React-based video framework)
- Always read relevant skills before executing tasks
- After successful task completion, update the skill file with the working workflow

## Skill Training Workflow

1. **Attempt** - Try the task without instructions first
2. **Observe** - Note what works and what fails
3. **Save** - Extract the successful workflow into a skill file
4. **Test** - Verify the skill executes correctly (target: <60 seconds)

## Available Skills

Check `claude-agent/skills/` for all available skills. Key skills:
- `x-skill.md` - X (Twitter) navigation and posting
- `linkedin-skill.md` - LinkedIn navigation and messaging
- `github-skill.md` - GitHub repo management and publishing
- `video-editing-skill.md` - Remotion video creation
- `screen-recording-skill.md` - Screen capture automation
- `coding-skill.md` - Code project creation workflow
- `research-skill.md` - Web research and analysis
- `promo-skill.md` - Content promotion across platforms

## Tool Permissions

When running autonomously, Claude Code should have access to:
- Bash (for running scripts, npm, ffmpeg, git)
- Read/Write/Edit (for skill files and code)
- Glob/Grep (for codebase exploration)

## Important Notes

- Use dedicated accounts for automation (not personal accounts)
- Browser must be logged into target services before running skills
- Always test skills in isolation before chaining them
- Output files go to `claude-agent/output/`
