# Coding With Claude -- Structured Development Workflow

## The Problem This Solves

If you find yourself saying things like "fix this error" or "add a feature" and getting bad results, this toolkit forces a structured workflow that gives Claude the context it needs.

## The Workflow

```
 1. CLARIFY        2. PLAN           3. IMPLEMENT       4. DEBUG
 /structure-request  /plan-feature     /act               /debug-error
  "what exactly?"    "PRD + tasks      "one task at        "diagnose,
                      + test plan"      a time"            don't guess"
                                            |
                                            v
                                       /commit
                                      "ship it"
```

### Step 1: Clarify (`/structure-request`)

Before asking Claude to build anything, run `/structure-request` with your rough idea.
It will ask targeted questions and produce a structured spec with:
- Goal, files involved, current vs. desired behavior, acceptance criteria

**Instead of:** "add user auth"
**You get:** A spec that names the files, the expected behavior, and how to verify it.

### Step 2: Plan (`/plan-feature`)

Take your structured request and run `/plan-feature` to break it into:
- A mini-PRD (problem, solution, scope, key decisions)
- A numbered task list in `todos.md`
- A test plan with unit, integration, and manual verification steps

Tests are defined before code is written, not after.

### Step 3: Implement (`/act`)

Work through the task list one item at a time using `/act`:
- Pick the next unchecked item from `todos.md`
- Plan the implementation
- Code it
- Check it off
- Commit

One task, one commit. Small, verifiable increments.

### Step 4: Debug (`/debug-error`)

When you hit an error, run `/debug-error` instead of just pasting the stack trace.
It enforces a diagnostic process:
1. Gather facts (error, recent changes, what was expected)
2. Form a hypothesis
3. Verify before fixing
4. Apply minimal fix
5. Confirm the fix works

**Instead of:** pasting an error and saying "fix this"
**You get:** a root cause analysis and a targeted fix.

## Supporting Commands

| Command | When to Use |
|---------|-------------|
| `/todo add "task"` | Add tasks to your `todos.md` backlog |
| `/todo list` | See current task status |
| `/todo next` | Get the next task to work on |
| `/commit` | Structured commit with conventional format |
| `/review <file>` | Code review checklist before merging |
| `/clean` | Fix all linting/formatting/type errors |
| `/fix-github-issue <#>` | Systematic GitHub issue resolution |

## Rules for Better Prompts (Always Apply)

### Give Context, Not Just Commands
- BAD: "fix the login bug"
- GOOD: "The login form in `src/components/Login.tsx` submits but the API returns 401. It worked before I changed the token refresh logic in `src/auth/tokens.ts`. Here's the error: [paste]"

### Name the Files
Claude works best when it knows where to look. Always mention specific files, functions, or components.

### State Expected vs. Actual
"It should do X but instead it does Y" is the single most useful sentence you can write.

### One Thing at a Time
Don't combine "add feature X, fix bug Y, and refactor Z" in one request. Each gets its own cycle.

### Show What You Tried
If you already attempted a fix, say so. "I tried adding a null check on line 42 but the error moved to line 58" saves Claude from repeating your dead ends.

## Development Principles

### Incremental Over Big-Bang
- One logical change per commit
- Run tests after every change, not at the end
- If a task feels too big, break it into smaller tasks

### Tests Are Not Optional
- Define test cases before writing code (Phase 4 of `/plan-feature`)
- Every task should be verifiable
- "It works on my machine" is not a test

### Read Before Write
- Claude must read existing code before modifying it
- Check for existing patterns before inventing new ones
- Understand the architecture before adding to it

### Minimal Fixes
- Fix the root cause, not the symptom
- Smallest change that addresses the actual problem
- Don't refactor while debugging
