---
name: full-pipeline
description: Execute the full autonomous content pipeline from research to promotion. Chains all skills together into one end-to-end workflow.
disable-model-invocation: true
---

# Full Autonomous Pipeline

Run the complete content creation pipeline end-to-end.

## Arguments
`$ARGUMENTS` = optional topic/idea (if empty, research step will find one)

## Pipeline Stages

### Stage 1 — Research (use researcher subagent)
Read `skills/research-skill.md` then:
1. Scan X trending, GitHub trending, Hacker News front page
2. Identify hot topics in AI / coding / developer tools
3. Generate 3 project ideas (simple, medium, complex)
4. Select the best one based on:
   - Viral potential (will people share it?)
   - Technical feasibility (can we build it in <1 hour?)
   - Content potential (is it video-worthy?)
5. Save research report to `output/logs/research-YYYY-MM-DD.md`

### Stage 2 — Code (use coder subagent)
Read `skills/coding-skill.md` then:
1. Create a new project directory
2. Initialize with the right tech stack
3. Implement core features (keep it focused — MVP only)
4. Add README.md with clear usage instructions
5. Add .gitignore and .env.example
6. Test locally — ensure it runs without errors
7. Take a screenshot of the running app

### Stage 3 — Publish (use publisher subagent)
Read `skills/github-skill.md` then:
1. `git init` and commit all files
2. `gh repo create` (public, with description)
3. `git push` to GitHub
4. Verify the repo is live
5. Note the GitHub URL for promotion

### Stage 4 — Video (use video-creator subagent)
Read `skills/video-editing-skill.md` then:
1. Plan video: title card → what it does → demo → how it works → CTA
2. Create/update Remotion composition with the project details
3. Include code snippets, screenshots, and animated text
4. Render to `output/videos/`
5. Generate a thumbnail
6. Optionally add voiceover (if TTS API is configured)

### Stage 5 — Promote (use promoter subagent)
Read `skills/promo-skill.md` then:
1. Create X post (short, punchy, with video or screenshot)
2. Create LinkedIn post (professional, longer)
3. Post on X first (video natively, GitHub link in reply)
4. Post on LinkedIn
5. Log post URLs

## Orchestration Rules
- **Sequential**: Each stage must complete before the next starts
- **Checkpoints**: Save progress after each stage to `output/logs/pipeline.log`
- **Failures**: If a stage fails, report the error and stop (don't skip)
- **Timing**: Log start/end times for performance tracking

## Example
```
/full-pipeline AI-powered terminal dashboard

/full-pipeline
# (auto-discovers a topic via research)
```
