# Pick Resources

Copy a specific resource into the current project.

## Usage

```
/pick                           # Show categories
/pick slash-commands            # List commands available
/pick slash-commands/optimize   # Copy optimize command to project
/pick claude.md-files/DSPy      # Add DSPy patterns to CLAUDE.md
```

## Categories

- **slash-commands** → `.claude/commands/<name>.md`
- **claude.md-files** → Append to `CLAUDE.md`
- **workflows-knowledge-guides** → Your choice

## Steps

**If no argument:** Show categories and usage examples

**If category only:** List contents with brief descriptions
```bash
ls resources/<category>/
```

**If category/name:**
1. Find resource in `resources/<category>/<name>/`
2. Show preview (first 40 lines)
3. Ask user to confirm
4. Copy to appropriate location:
   - Commands → `.claude/commands/<name>.md`
   - CLAUDE.md files → Ask: append to CLAUDE.md or show for manual copy?
5. Confirm what was added

## Argument

$ARGUMENTS
