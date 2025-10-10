# Create Hook Command

Analyze the project, suggest practical hooks, and create them with proper testing.

## Your Task (/create-hook)

1. **Analyze environment** - Detect tooling and existing hooks
2. **Suggest hooks** - Based on your project configuration
3. **Configure hook** - Ask targeted questions and create the script
4. **Test & validate** - Ensure the hook works correctly

## Your Workflow

### 1. Environment Analysis & Suggestions

Automatically detect the project tooling and suggest relevant hooks:

**When TypeScript is detected (`tsconfig.json`):**

- PostToolUse hook: "Type-check files after editing"
- PreToolUse hook: "Block edits with type errors"

**When Prettier is detected (`.prettierrc`, `prettier.config.js`):**

- PostToolUse hook: "Auto-format files after editing"
- PreToolUse hook: "Require formatted code"

**When ESLint is detected (`.eslintrc.*`):**

- PostToolUse hook: "Lint and auto-fix after editing"
- PreToolUse hook: "Block commits with linting errors"

**When package.json has scripts:**

- `test` script → "Run tests before commits"
- `build` script → "Validate build before commits"

**When a git repository is detected:**

- PreToolUse/Bash hook: "Prevent commits with secrets"
- PostToolUse hook: "Security scan on file changes"

**Decision Tree:**

```
Project has TypeScript? → Suggest type checking hooks
Project has formatter? → Suggest formatting hooks
Project has tests? → Suggest test validation hooks
Security sensitive? → Suggest security hooks
+ Scan for additional patterns and suggest custom hooks based on:
  - Custom scripts in package.json
  - Unique file patterns or extensions
  - Development workflow indicators
  - Project-specific tooling configurations
```

### 2. Hook Configuration

Start by asking: **"What should this hook do?"** and offer relevant suggestions from your analysis.

Then understand the context from the user's description and **only ask about details you're unsure about**:

1. **Trigger timing**: When should it run?
   - `PreToolUse`: Before file operations (can block)
   - `PostToolUse`: After file operations (feedback/fixes)
   - `UserPromptSubmit`: Before processing requests
   - Other event types as needed

2. **Tool matcher**: Which tools should trigger it? (`Write`, `Edit`, `Bash`, `*` etc)

3. **Scope**: `global`, `project`, or `project-local`

4. **Response approach**:
   - **Exit codes only**: Simple (exit 0 = success, exit 2 = block in PreToolUse)
   - **JSON response**: Advanced control (blocking, context, decisions)
   - Guide based on complexity: simple pass/fail → exit codes, rich feedback → JSON

5. **Blocking behavior** (if relevant): "Should this stop operations when issues are found?"
   - PreToolUse: Can block operations (security, validation)
   - PostToolUse: Usually provide feedback only

6. **Claude integration** (CRITICAL): "Should Claude Code automatically see and fix issues this hook detects?"
   - If YES: Use `additionalContext` for error communication
   - If NO: Use `suppressOutput: true` for silent operation

7. **Context pollution**: "Should successful operations be silent to avoid noise?"
   - Recommend YES for formatting, routine checks
   - Recommend NO for security alerts, critical errors

8. **File filtering**: "What file types should this hook process?"

### 3. Hook Creation

You should:

- **Create hooks directory**: `~/.claude/hooks/` or `.claude/hooks/` based on scope
- **Generate script**: Create hook script with:
  - Proper shebang and executable permissions
  - Project-specific commands (use detected config paths)
  - Comments explaining the hook's purpose
- **Update settings**: Add hook configuration to appropriate settings.json
- **Use absolute paths**: Avoid relative paths to scripts and executables. Use `$CLAUDE_PROJECT_DIR` to reference project root
- **Offer validation**: Ask if the user wants you to test the hook

**Key Implementation Standards:**

- Read JSON from stdin (never use argv)
- Use top-level `additionalContext`/`systemMessage` for Claude communication
- Include `suppressOutput: true` for successful operations
- Provide specific error counts and actionable feedback
- Focus on changed files rather than entire codebase
- Support common development workflows

**⚠️ CRITICAL: Input/Output Format**

This is where most hook implementations fail. Pay extra attention to:

- **Input**: Reading JSON from stdin correctly (not argv)
- **Output**: Using correct top-level JSON structure for Claude communication
- **Documentation**: Consulting official docs for exact schemas when in doubt

### 4. Testing & Validation

**CRITICAL: Test both happy and sad paths:**

**Happy Path Testing:**

1. **Test expected success scenario** - Create conditions where hook should pass
   - _Examples_: TypeScript (valid code), Linting (formatted code), Security (safe commands)

**Sad Path Testing:** 2. **Test expected failure scenario** - Create conditions where hook should fail/warn

- _Examples_: TypeScript (type errors), Linting (unformatted code), Security (dangerous operations)

**Verification Steps:** 3. **Verify expected behavior**: Check if it blocks/warns/provides context as intended

**Example Testing Process:**

- For a hook preventing file deletion: Create a test file, attempt the protected action, and verify the hook prevents it

**If Issues Occur, you should:**

- Check hook registration in settings
- Verify script permissions (`chmod +x`)
- Test with simplified version first
- Debug with detailed hook execution analysis

## Hook Templates

### Type Checking (PostToolUse)

```
#!/usr/bin/env node
// Read stdin JSON, check .ts/.tsx files only
// Run: npx tsc --noEmit --pretty
// Output: JSON with additionalContext for errors
```

### Auto-formatting (PostToolUse)

```
#!/usr/bin/env node
// Read stdin JSON, check supported file types
// Run: npx prettier --write [file]
// Output: JSON with suppressOutput: true
```

### Security Scanning (PreToolUse)

```bash
#!/bin/bash
# Read stdin JSON, check for secrets/keys
# Block if dangerous patterns found
# Exit 2 to block, 0 to continue
```

_Complete templates available at: https://docs.claude.com/en/docs/claude-code/hooks#examples_

## Quick Reference

**📖 Official Docs**: https://docs.claude.com/en/docs/claude-code/hooks.md

**Common Patterns:**

- **stdin input**: `JSON.parse(process.stdin.read())`
- **File filtering**: Check extensions before processing
- **Success response**: `{continue: true, suppressOutput: true}`
- **Error response**: `{continue: true, additionalContext: "error details"}`
- **Block operation**: `exit(2)` in PreToolUse hooks

**Hook Types by Use Case:**

- **Code Quality**: PostToolUse for feedback and fixes
- **Security**: PreToolUse to block dangerous operations
- **CI/CD**: PreToolUse to validate before commits
- **Development**: PostToolUse for automated improvements

**Hook Execution Best Practices:**

- **Hooks run in parallel** according to official documentation
- **Design for independence** since execution order isn't guaranteed
- **Plan hook interactions carefully** when multiple hooks affect the same files

## Success Criteria

✅ **Hook created successfully when:**

- Script has executable permissions
- Registered in correct settings.json
- Responds correctly to test scenarios
- Integrates properly with Claude for automated fixes
- Follows project conventions and detected tooling

**Result**: The user gets a working hook that enhances their development workflow with intelligent automation and quality checks.
