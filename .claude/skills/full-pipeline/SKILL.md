---
name: full-pipeline
description: Execute the full autonomous content creation pipeline - research, code, record, edit, publish, promote. This is the end-to-end workflow.
disable-model-invocation: true
---

# Full Autonomous Pipeline

Run the complete content creation pipeline from research to promotion.

## Pipeline Steps

### Step 1: Research
Read `claude-agent/skills/research-skill.md` and execute:
- Scan trending topics on X, GitHub, Hacker News
- Identify a hot topic relevant to AI/coding
- Brainstorm 3 project ideas
- Select the best one based on viral potential and feasibility

### Step 2: Code the Project
Read `claude-agent/skills/coding-skill.md` and execute:
- Create the project from scratch
- Implement core features
- Add proper README and documentation
- Test locally to ensure it works
- Follow the code quality checklist

### Step 3: Publish to GitHub
Read `claude-agent/skills/github-skill.md` and execute:
- Initialize git repository
- Create GitHub repo
- Push code with proper commit messages
- Verify repo is accessible

### Step 4: Create Explainer Video
Read `claude-agent/skills/video-editing-skill.md` and execute:
- Plan video structure (title, sections, conclusion)
- Create Remotion composition
- Add animated title, code demos, transitions
- Render to MP4

### Step 5: Record Demo (if applicable)
Read `claude-agent/skills/screen-recording-skill.md` and execute:
- Record the running application
- Capture key interactions
- Save recording for video inclusion

### Step 6: Promote
Read `claude-agent/skills/promo-skill.md` and execute:
- Post on X with video/GIF + GitHub link
- Post on LinkedIn with longer description
- Monitor initial engagement

## Usage

```
/full-pipeline

# Or with a specific topic:
/full-pipeline AI-powered code review tool
```

## Important Notes

- Read ALL relevant skill files before starting each step
- Each step should complete before moving to the next
- If a step fails, check the skill's troubleshooting section
- Update skill files with any new learnings
- Total expected time: 30-60 minutes for the full pipeline
