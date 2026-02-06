# Claude Code AI Agent System

## Project Overview

This is a **self-contained autonomous AI agent system** built entirely with Claude Code.
It can learn new skills iteratively, navigate web applications via browser automation,
create videos with Remotion, and promote content across platforms — all without OpenClaw.

Inspired by [All About AI](https://youtube.com/@AllAboutAI) YouTube series on agent skill training.

## Architecture

```
ai-agent-system/
├── .claude/                    # Claude Code configuration
│   ├── settings.json           # Hooks, permissions, statusline
│   ├── skills/                 # Slash commands (/train-skill, /run-skill, etc.)
│   └── agents/                 # Custom subagents (researcher, coder, etc.)
├── skills/                     # Trained skill files (the agent's knowledge base)
├── scripts/                    # Automation scripts (browser, recording, hooks)
├── src/                        # Remotion video project (React-based)
├── config/                     # Environment and configuration
├── output/                     # Generated files (screenshots, videos, logs)
└── CLAUDE.md                   # This file — project instructions for Claude
```

## Skill System

Skills live in `skills/` as Markdown files. Each skill contains:
- **Purpose**: What the skill does
- **Prerequisites**: Required tools/access
- **Selectors**: CSS selectors for browser automation
- **Workflows**: Step-by-step procedures
- **Code Snippets**: Working JavaScript/Bash code
- **Troubleshooting**: Known issues and fixes

### Available Skills
| Skill | File | Description |
|-------|------|-------------|
| X (Twitter) | `skills/x-skill.md` | Post tweets, read timeline, engage |
| LinkedIn | `skills/linkedin-skill.md` | Post content, send messages, connect |
| GitHub | `skills/github-skill.md` | Create repos, push code, manage releases |
| Video Editing | `skills/video-editing-skill.md` | Remotion compositions, rendering |
| Screen Recording | `skills/screen-recording-skill.md` | FFmpeg/CDP screen capture |
| Coding | `skills/coding-skill.md` | Full project creation workflows |
| Research | `skills/research-skill.md` | Trending topics, brainstorming |
| Promotion | `skills/promo-skill.md` | Cross-platform content promotion |

### Skill Training Protocol
1. **Attempt** — Try the task blind, observe what happens
2. **Document** — Save the working workflow to a skill file
3. **Test** — Re-run using only the skill (target: <60s)
4. **Iterate** — Refine until reliable

## Slash Commands

| Command | Description |
|---------|-------------|
| `/train-skill <name>` | Learn a new skill iteratively |
| `/run-skill <name>` | Execute a trained skill |
| `/full-pipeline [topic]` | Research → Code → Publish → Video → Promote |
| `/browse <url>` | Navigate to a URL with browser automation |
| `/create-video <type> <title>` | Create a Remotion video |
| `/post-x <content>` | Post to X (Twitter) |
| `/post-linkedin <content>` | Post to LinkedIn |
| `/publish-github` | Push current project to GitHub |

## Subagents

| Agent | Model | Role |
|-------|-------|------|
| `researcher` | sonnet | Web research, trending topics, brainstorming |
| `coder` | inherit | Full-stack project creation |
| `publisher` | haiku | Git + GitHub operations |
| `video-creator` | sonnet | Remotion video composition + rendering |
| `promoter` | haiku | X / LinkedIn cross-posting |
| `skill-trainer` | inherit | Iterative skill learning |

## Hooks

| Event | Script | Purpose |
|-------|--------|---------|
| `PreToolUse(Bash)` | `scripts/hooks/pre-bash.sh` | Block dangerous commands |
| `PostToolUse(Write\|Edit)` | `scripts/hooks/post-edit.sh` | Log edits, auto-lint |
| `PostToolUse(Bash)` | `scripts/hooks/post-bash.sh` | Log command history |
| `Notification` | `scripts/hooks/notify.sh` | Desktop/terminal notifications |

## Browser Automation

All browser skills use **Puppeteer with CDP** (Chrome DevTools Protocol).
The browser module is at `scripts/browser.js` and supports:
- Launch with existing Chrome profile (pre-logged-in sessions)
- Navigate, click, type, inject text
- Take screenshots (viewport or full-page)
- Upload files
- Extract page content
- Execute arbitrary JavaScript

**Important**: The browser must be logged into target services BEFORE running skills.

## Video System

Video creation uses **Remotion** (React-based video framework):
- `src/compositions/ExplainerVideo.tsx` — Animated title + content sections
- `src/compositions/DemoVideo.tsx` — Screenshot walkthrough with captions
- `src/compositions/ShortVideo.tsx` — Short-form social media video
- `src/components/` — Reusable components (Title, CodeBlock, Caption, etc.)

Render commands:
```bash
npm run video:preview      # Preview in browser
npm run video:render       # Render explainer to MP4
npm run video:demo         # Render demo to MP4
npm run video:short        # Render short to MP4
```

## Quick Start

```bash
cd ai-agent-system
npm run setup              # Install everything
# Then open Claude Code in this directory and use the slash commands
```

## Important Rules

- Always read the relevant skill file BEFORE executing a task
- After successful execution, UPDATE the skill file with any learnings
- Use dedicated accounts for automation (not personal)
- Output files go to `output/` (screenshots, videos, logs)
- Never commit `.env` — only `.env.example`
