# Plan Feature

Break a feature idea into a PRD, task list, and test plan before writing any code. This is the "think before you code" command.

## Why This Exists

Jumping straight into implementation leads to:
- Building the wrong thing (misunderstood requirements)
- Missing edge cases discovered too late
- No way to tell when you're "done"
- Rework when the approach doesn't hold up

This command creates just enough planning to code confidently, without turning into a documentation exercise.

## When to Use

- You have a feature to build that involves more than one file or function
- You want a clear checklist to work through (pairs well with `/act`)
- You want test cases defined before you start coding

## Process

When the user invokes `/plan-feature $ARGUMENTS`, do the following:

### Phase 1: Understand the Feature

1. Read the user's description of the feature
2. Explore the codebase to understand:
   - Where this feature fits architecturally
   - What existing patterns to follow
   - What files/modules will be touched
3. Ask up to 3 clarifying questions if critical details are missing. Focus on:
   - Who uses this and what triggers it?
   - What are the inputs and outputs?
   - Are there existing patterns I should mirror?

### Phase 2: Write the Mini-PRD

Create a concise requirements doc (NOT a full PRD -- just enough to align on scope):

```markdown
## Feature: [Name]

### Problem
[1-2 sentences: what's missing or broken]

### Solution
[1-2 sentences: what we're building]

### Scope
**In scope:**
- [Specific thing 1]
- [Specific thing 2]

**Out of scope:**
- [Thing explicitly not included]

### Key Decisions
- [Decision 1: e.g., "Use existing auth middleware, don't create new one"]
- [Decision 2: e.g., "Store in PostgreSQL, not Redis"]
```

Present this to the user. Confirm before proceeding.

### Phase 3: Break Into Tasks

Create a numbered task list in `todos.md` (or present inline). Each task should be:
- **Small enough** to complete in one focused session
- **Testable** -- you can verify it works independently
- **Ordered** -- dependencies are respected

Format:
```markdown
## Tasks: [Feature Name]

- [ ] 1. [Task description] -- [which files]
- [ ] 2. [Task description] -- [which files]
- [ ] 3. Write tests for [specific behavior]
- [ ] 4. [Task description] -- [which files]
- [ ] 5. Integration test: [end-to-end scenario]
- [ ] 6. Run full test suite and fix regressions
```

Rules for task breakdown:
- Tests are tasks, not afterthoughts. Interleave them with implementation.
- The last task is always "run the full test suite and fix any regressions."
- Each task should name the files it touches.

### Phase 4: Define Test Cases

Before any code is written, outline the test cases:

```markdown
## Test Plan

### Unit Tests
- [ ] [Function/component] -- [what to test] -- [expected result]
- [ ] [Function/component] -- [edge case] -- [expected result]

### Integration Tests
- [ ] [Scenario description] -- [expected end-to-end result]

### Manual Verification
- [ ] [How to manually confirm it works]
```

Ask the user: "Do these test cases cover what matters to you? Anything to add?"

### Phase 5: Hand Off to Implementation

Once the user approves:
1. Write the task list to `todos.md` if it doesn't exist yet
2. Tell the user they can now use `/act` to work through the tasks one by one
3. Or start implementing the first task immediately if the user says "go"

## How This Connects to Other Commands

```
/structure-request  -->  /plan-feature  -->  /act  -->  /debug-error
  (clarify the ask)    (you are here)    (implement)   (when stuck)
                                              |
                                              v
                                         /commit
                                        (ship it)
```
