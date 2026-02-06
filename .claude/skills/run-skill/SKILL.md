---
name: run-skill
description: Execute a previously trained skill from the skills directory. Reads the skill file and follows its workflow.
disable-model-invocation: true
---

# Run a Trained Skill

Execute a skill from the `claude-agent/skills/` directory.

## Process

1. **Read the skill file**: Load `claude-agent/skills/$ARGUMENTS-skill.md`
2. **Check prerequisites**: Verify all required tools and access are available
3. **Execute the workflow**: Follow the documented steps exactly
4. **Report results**: Confirm success or document any issues
5. **Update skill if needed**: If the workflow needed adjustments, update the skill file

## Usage

```
/run-skill x           # Run the X (Twitter) skill
/run-skill linkedin    # Run the LinkedIn skill
/run-skill github      # Run the GitHub skill
/run-skill research    # Run the research skill
/run-skill promo       # Run the promotion skill
```

## Important

- Always read the skill file first before executing
- Follow the documented workflow step by step
- If a step fails, check the troubleshooting section in the skill file
- After execution, update the skill file if any changes were needed
