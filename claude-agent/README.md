# Claude Agent - Autonomous AI Agent System

An autonomous AI agent system built with **Claude Code** (no OpenClaw) that can learn new skills iteratively, navigate web applications, create content, and promote across platforms.

Inspired by the [All About AI](https://youtube.com/@AllAboutAI) YouTube series on training AI agent skills.

## Architecture

```
claude-agent/
├── skills/                    # Reusable skill files (.md)
│   ├── x-skill.md            # X (Twitter) navigation & posting
│   ├── linkedin-skill.md     # LinkedIn networking & messaging
│   ├── github-skill.md       # GitHub repo management
│   ├── video-editing-skill.md # Remotion video creation
│   ├── screen-recording-skill.md # Screen capture
│   ├── coding-skill.md       # Project creation workflow
│   ├── research-skill.md     # Web research & trend analysis
│   └── promo-skill.md        # Cross-platform promotion
├── scripts/                   # Automation scripts
│   ├── browser.js             # Chrome CDP automation (Puppeteer)
│   ├── record-demo.js         # Demo recording tool
│   ├── setup.sh               # One-time setup
│   ├── run-task.sh            # Task runner
│   ├── validate-command.sh    # PreToolUse hook (safety)
│   ├── post-edit-hook.sh      # PostToolUse hook (linting/logging)
│   └── on-subagent-complete.sh # SubagentStop hook
├── src/                       # Remotion video project
│   ├── compositions/          # Video compositions (React)
│   ├── Root.tsx               # Root component
│   └── index.ts               # Entry point
├── config/                    # Configuration files
│   └── .env.example           # Environment template
└── output/                    # Generated content
```

### Claude Code Integration (`.claude/`)

```
.claude/
├── settings.json              # Hooks & permissions configuration
├── skills/                    # Claude Code slash commands
│   ├── train-skill/SKILL.md   # /train-skill - Learn new skills
│   ├── run-skill/SKILL.md     # /run-skill - Execute a skill
│   ├── full-pipeline/SKILL.md # /full-pipeline - End-to-end workflow
│   ├── browse/SKILL.md        # /browse - Browser navigation
│   └── create-video/SKILL.md  # /create-video - Video creation
└── agents/                    # Custom subagents
    ├── researcher.md          # Web research specialist
    ├── coder.md               # Full-stack coding specialist
    ├── publisher.md           # GitHub publishing specialist
    ├── video-creator.md       # Remotion video specialist
    ├── promoter.md            # Content promotion specialist
    └── skill-trainer.md       # Skill training specialist
```

## Setup

### Prerequisites
- Node.js 18+ and npm
- Chrome/Chromium browser (for browser automation)
- FFmpeg (for video editing)
- `gh` CLI (for GitHub publishing)
- Claude Code CLI

### Installation

```bash
cd claude-agent
bash scripts/setup.sh
```

Or manually:

```bash
npm install                    # Install browser automation deps
cd src && npm install && cd .. # Install Remotion deps
cp config/.env.example config/.env  # Configure environment
```

## How It Works

### Skill Training Workflow

The core concept from the videos: skills are learned iteratively.

1. **Attempt**: The agent tries a task without prior instructions
2. **Observe**: Note what works and what fails
3. **Save**: Extract the successful workflow into a skill file
4. **Test**: Verify the skill executes in under 60 seconds
5. **Iterate**: Repeat until reliable

### Using Skills in Claude Code

```bash
# Train a new skill
/train-skill linkedin-messaging

# Execute a trained skill
/run-skill x

# Run the full pipeline
/full-pipeline AI code review tool
```

### Using Subagents

Claude automatically delegates to specialized subagents:

```
Use the researcher to find trending AI topics
Use the coder to build a React dashboard
Use the publisher to push to GitHub
Use the video-creator to make an explainer video
Use the promoter to post on X and LinkedIn
```

### Hooks

The system uses Claude Code hooks for safety and automation:
- **PreToolUse**: Validates Bash commands before execution
- **PostToolUse**: Logs edits and runs linters
- **SubagentStop**: Logs pipeline progress

## Full Pipeline

The end-to-end autonomous pipeline:

```
Research → Code → Publish → Video → Promote
```

Example prompt:
```
Brainstorm a coding project about a hot AI topic.
Research X for trends. Create the code with UI.
Push to GitHub. Create an explainer video.
Post on X with the GitHub link.
Read all your skills before starting.
```

## Technologies

- **Claude Code** - AI agent runtime (skills, subagents, hooks)
- **Puppeteer** - Browser automation via CDP
- **Remotion** - React-based video creation
- **FFmpeg** - Video encoding and post-processing
- **GitHub CLI** - Repository management

## License

MIT
