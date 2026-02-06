---
name: run-skill
description: Execute a previously trained skill. Reads the skill file from skills/ and follows its documented workflow step-by-step.
disable-model-invocation: true
---

# Run a Trained Skill

Execute a skill from the `skills/` directory by reading and following its workflow.

## Arguments
`$ARGUMENTS` = skill name (without `-skill.md` suffix)

## Process

1. **Load skill**: Read `skills/$ARGUMENTS-skill.md`
   - If not found, list available skills in `skills/` and suggest using `/train-skill`

2. **Check prerequisites**: Verify every prerequisite listed in the skill file
   - Are the required tools installed?
   - Is browser logged in (for web skills)?
   - Are API keys configured (if needed)?

3. **Execute workflow**: Follow each step in the "Workflows" section EXACTLY
   - Use the documented CSS selectors
   - Use the documented code snippets
   - Respect the documented timing/delays

4. **Verify**: Check the skill's success criteria
   - Take a screenshot if it's a browser task
   - Log the result

5. **Update**: If the workflow needed any adjustments:
   - Update the skill file with corrections
   - Add a new entry to the Training Log

## Available Skills
Run `ls skills/*.md` to see all trained skills. Common ones:
- `/run-skill x` — Post on X (Twitter)
- `/run-skill linkedin` — Post on LinkedIn
- `/run-skill github` — Publish to GitHub
- `/run-skill research` — Research trending topics
- `/run-skill coding` — Create a coding project
- `/run-skill video-editing` — Create a Remotion video
- `/run-skill promo` — Promote content across platforms

## Error Handling
- If a step fails, check the skill's Troubleshooting section first
- If still failing, update the skill with the new information
- Never silently skip a failed step — always report it
