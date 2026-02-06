---
name: train-skill
description: Train a new AI agent skill through iterative learning. Use when the agent needs to learn a new workflow by attempting it, observing results, and saving the successful workflow to a skill file.
disable-model-invocation: true
---

# Skill Training Workflow

Train a new skill using the iterative learning method:

## Process

1. **Identify the task**: What skill needs to be learned? `$ARGUMENTS`

2. **First attempt**: Try to execute the task without prior instructions
   - Observe what works and what fails
   - Note the selectors, commands, and steps that succeed
   - Record timing and any errors encountered

3. **Document the workflow**: After a successful attempt:
   - Create a new skill file in `claude-agent/skills/`
   - Use the naming convention: `[skill-name]-skill.md`
   - Include:
     - Purpose section
     - Prerequisites
     - Step-by-step workflow
     - CSS selectors / API endpoints used
     - JavaScript snippets that worked
     - Troubleshooting notes

4. **Test the skill**: Run the task again using only the documented skill
   - Target execution time: under 60 seconds
   - If it fails, update the skill file with corrections

5. **Iterate**: Repeat steps 3-4 until the skill is reliable

## Skill File Template

```markdown
# [Skill Name] Skill

## Purpose
[What this skill does]

## Prerequisites
- [Required tools/access]

## Workflows

### [Workflow Name]
\```
1. [Step 1]
2. [Step 2]
3. [Step 3]
\```

## JavaScript Snippets
[Working code]

## Troubleshooting
- [Common issue]: [Solution]
```

## Example Usage

```
/train-skill linkedin-messaging
```

This will attempt to learn LinkedIn messaging, document the successful workflow, and create `linkedin-messaging-skill.md`.
