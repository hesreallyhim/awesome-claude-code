---
name: train-skill
description: Train a new AI agent skill through iterative learning. Attempts the task, observes results, saves the successful workflow to a reusable skill file.
disable-model-invocation: true
---

# Train a New Skill

Learn a new skill using iterative training: attempt → observe → document → test → iterate.

## Arguments
`$ARGUMENTS` = name of the skill to learn (e.g., "linkedin-messaging", "github-release")

## Training Protocol

### Step 1 — First Attempt
Try to execute the task described by `$ARGUMENTS` without any prior skill file.
- Use browser automation (`scripts/browser.js`) if it's a web task
- Use CLI tools if it's a command-line task
- Note **everything**: selectors, timing, errors, what worked

### Step 2 — Document the Workflow
Create a skill file: `skills/$ARGUMENTS-skill.md`

Use this template:
```markdown
# [Name] Skill

## Purpose
[One-line description]

## Prerequisites
- [Tool/access required]

## Selectors Reference (browser skills only)
- **[Element]**: `[CSS selector]`

## Workflows

### [Primary Workflow]
1. [Exact step with selector/command]
2. [Next step]
3. [Verification step]

## Code Snippets

### [Snippet Name]
\`\`\`javascript
// Working code
\`\`\`

## Troubleshooting
- **[Issue]**: [Solution]

## Training Log
- Attempt 1: [Date] — [Result]
- Attempt 2: [Date] — [Result]
```

### Step 3 — Test the Skill
Run the task again using ONLY the documented skill file.
- Read `skills/$ARGUMENTS-skill.md`
- Follow the workflow exactly
- Target: complete in under 60 seconds
- If it fails, go back to Step 2

### Step 4 — Iterate
Repeat Steps 2-3 until:
- The skill executes reliably (3 consecutive successes)
- Execution time is under 60 seconds
- All edge cases are documented in Troubleshooting

## Example
```
/train-skill twitter-thread
```
This will attempt to learn how to post a Twitter thread, then save the workflow.
