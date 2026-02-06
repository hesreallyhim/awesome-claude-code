# AI Agent System

> Autonomous AI agent built with **Claude Code** that learns skills, automates browsers, creates videos, and promotes content — all without OpenClaw.

Inspired by the [All About AI](https://youtube.com/@AllAboutAI) video series on training AI agent skills with Claude Code.

## What This Does

A complete, self-contained agent system that can autonomously:

1. **Research** trending topics on X, GitHub, Hacker News
2. **Code** a complete project from scratch
3. **Publish** it to GitHub with proper commits
4. **Create** an explainer video using Remotion
5. **Promote** across X and LinkedIn

All orchestrated through Claude Code **skills**, **subagents**, and **hooks**.

## Architecture

```
ai-agent-system/
├── .claude/                    # Claude Code configuration
│   ├── settings.json           # Hooks + permissions
│   ├── skills/                 # 8 slash commands
│   │   ├── train-skill/        # /train-skill — iterative learning
│   │   ├── run-skill/          # /run-skill — execute a skill
│   │   ├── full-pipeline/      # /full-pipeline — end-to-end
│   │   ├── browse/             # /browse — browser navigation
│   │   ├── create-video/       # /create-video — Remotion rendering
│   │   ├── post-x/             # /post-x — tweet posting
│   │   ├── post-linkedin/      # /post-linkedin — LinkedIn posting
│   │   └── publish-github/     # /publish-github — GitHub push
│   └── agents/                 # 6 custom subagents
│       ├── researcher.md       # Trending topics + brainstorming
│       ├── coder.md            # Full-stack project creation
│       ├── publisher.md        # Git + GitHub operations
│       ├── video-creator.md    # Remotion video specialist
│       ├── promoter.md         # Cross-platform posting
│       └── skill-trainer.md    # Iterative skill learning
├── skills/                     # 8 trained skills (knowledge base)
│   ├── x-skill.md             # X/Twitter automation
│   ├── linkedin-skill.md      # LinkedIn automation
│   ├── github-skill.md        # GitHub CLI workflows
│   ├── video-editing-skill.md # Remotion + FFmpeg
│   ├── screen-recording-skill.md
│   ├── coding-skill.md        # Project creation templates
│   ├── research-skill.md      # Multi-platform research
│   └── promo-skill.md         # Content promotion
├── scripts/                    # Automation scripts
│   ├── browser.js             # Chrome CDP automation
│   ├── screenshot.js          # Quick screenshots
│   ├── record-demo.js         # Demo video recording
│   ├── setup.sh               # One-time setup
│   ├── run-pipeline.sh        # Pipeline orchestrator
│   ├── test-agent.js          # System verification
│   └── hooks/                 # Event hooks
│       ├── pre-bash.sh        # Safety: block dangerous commands
│       ├── post-edit.sh       # Logging + auto-linting
│       ├── post-bash.sh       # Command history
│       └── notify.sh          # Desktop notifications
├── src/                        # Remotion video project
│   ├── compositions/          # 3 video types
│   │   ├── ExplainerVideo.tsx # Animated sections
│   │   ├── DemoVideo.tsx      # Screenshot walkthrough
│   │   └── ShortVideo.tsx     # Vertical social clip
│   └── components/            # Reusable components
│       ├── Title.tsx          # Animated title card
│       ├── SectionCard.tsx    # Content sections
│       ├── CodeBlock.tsx      # Typing code animation
│       ├── Caption.tsx        # Subtitle overlays
│       └── Transition.tsx     # Slide transitions
├── config/.env.example         # Environment template
├── output/                     # Generated content
├── CLAUDE.md                   # Project instructions
└── package.json
```

## Quick Start

```bash
# 1. Setup
cd ai-agent-system
npm run setup

# 2. Open Claude Code
claude

# 3. Use slash commands
/train-skill youtube-scraping      # Learn a new skill
/run-skill research                # Execute the research skill
/full-pipeline AI dashboard        # Run the full pipeline
/browse https://github.com/trending
/create-video explainer "My Project"
```

## Skill Training Workflow

The core concept: skills are **learned iteratively**, not hardcoded.

```
1. ATTEMPT → Try the task blind
2. OBSERVE → Note what works / fails
3. DOCUMENT → Save to skills/[name]-skill.md
4. TEST → Re-run using only the skill file
5. ITERATE → Refine until reliable (<60s execution)
```

## Full Pipeline

The end-to-end autonomous pipeline:

```
/full-pipeline AI-powered terminal dashboard
```

This triggers:
1. **researcher** subagent scans X, GitHub, HN for trends
2. **coder** subagent builds the project
3. **publisher** subagent pushes to GitHub
4. **video-creator** subagent renders an explainer video
5. **promoter** subagent posts on X and LinkedIn

## Hooks

| Event | Script | Purpose |
|-------|--------|---------|
| Before Bash | `pre-bash.sh` | Block dangerous commands |
| After Write/Edit | `post-edit.sh` | Log changes + auto-lint |
| After Bash | `post-bash.sh` | Command history |
| Notifications | `notify.sh` | Desktop alerts |

## Technologies

| Component | Technology |
|-----------|-----------|
| Agent Runtime | Claude Code (skills, subagents, hooks) |
| Browser Automation | Puppeteer-core + Chrome CDP |
| Video Creation | Remotion (React-based) |
| Video Processing | FFmpeg |
| Version Control | Git + GitHub CLI |

## Requirements

- Node.js 18+
- Chrome or Chromium (for browser skills)
- FFmpeg (for video skills)
- `gh` CLI (for GitHub skills)
- Claude Code CLI

## License

MIT
