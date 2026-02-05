# Coding With Claude -- Automatic Structured Development

## How This Works

You don't need to invoke any commands. Just talk naturally. Claude will automatically detect what kind of help you need and apply the right workflow. Think of it as a coding partner who always asks the right follow-up questions before jumping in.

There are five automatic behaviors and one optional planning flow you can trigger when you want it.

---

## Auto-Detect Behaviors (Always On)

### 1. Vague Request Detection

When your message is a coding request but is missing critical context, Claude will **pause and ask clarifying questions** before writing any code.

**Triggers:** Requests that are missing 2+ of these: specific files, current behavior, desired behavior, acceptance criteria.

**What Claude does:**
- Reads any files or code you mentioned to ground the questions in your actual codebase
- Asks only about what's missing (not a generic questionnaire)
- Asks at most 3 targeted questions per round
- After getting answers, restates the request as a structured spec for confirmation:

```
Got it. Here's what I'll do:
- Goal: [one sentence]
- Files: [specific paths]
- Change: [current behavior] -> [desired behavior]
- Done when: [acceptance criteria]

Good to go?
```

**Examples of what triggers this:**

| You say | What's missing | Claude asks |
|---------|---------------|-------------|
| "add user auth" | Everything | "What kind of auth? Which routes need it? Is there an existing user model?" |
| "fix the login bug" | Which bug, expected behavior | "What happens when you try to log in? What should happen? Any error message?" |
| "make this faster" | What's slow, how slow, target | "Which operation is slow? How long does it take now? What's acceptable?" |
| "refactor the API" | Which part, what's wrong with it, what better looks like | "Which endpoints? What's the problem -- readability, performance, structure?" |

**What does NOT trigger this** (Claude proceeds directly):
- "The `calculateTotal` function in `src/cart.ts` returns 0 when the cart has items with discounts. It should sum `item.price * item.quantity` after applying the discount percentage. Here's the function: [paste]"
- Requests that name files, describe the problem, and state the expected outcome

### 2. Error Diagnosis Mode

When your message contains an error (stack trace, build failure, test failure, runtime exception), Claude will **automatically diagnose before fixing**.

**Triggers:** Messages containing stack traces, error messages, tracebacks, build/test output with failures.

**What Claude does (in order):**

1. **Read** the files referenced in the error -- no guessing at contents
2. **Ask for missing context** if needed:
   - "Did this work before? What changed recently?"
   - "What command triggered this?"
   - "Have you already tried anything?"
3. **State a hypothesis** before making changes:
   ```
   HYPOTHESIS: [what I think is wrong and why]
   Let me verify this by checking [specific thing]...
   ```
4. **Verify** the hypothesis (read more code, check config, run a diagnostic)
5. **Apply the minimal fix** -- smallest change that addresses the root cause
6. **Run the test/command again** to confirm the fix works
7. **Explain what happened:**
   ```
   ROOT CAUSE: [what was actually wrong]
   FIX: [what changed]
   PREVENTION: [how to avoid this, if relevant]
   ```

**What Claude will NOT do in this mode:**
- Guess at file contents without reading them
- Refactor surrounding code while fixing the bug
- Add defensive error handling unrelated to the issue
- Suppress the error without fixing the cause
- Make multiple speculative changes at once

### 3. Scope Check

When your message asks for multiple unrelated things at once, Claude will **split them and confirm priority**.

**Triggers:** Requests that combine 2+ unrelated changes (e.g., "add feature X, fix bug Y, and update the docs").

**What Claude does:**
```
I see a few separate things here:
1. [Feature X] -- new functionality
2. [Bug Y] -- fix
3. [Docs update] -- documentation

I'll work through these one at a time so each gets proper attention.
Starting with #2 (the bug fix) since it's blocking. Sound right?
```

Then works through each as its own cycle: understand -> implement -> test -> commit.

### 4. Pre-Commit Cleanup

After implementing changes and before committing, Claude will **automatically clean up**.

**Triggers:** Claude is about to commit, or the user says "commit", "ship it", "looks good", etc.

**What Claude does (in order):**

1. **Detect the project's tooling** by checking for config files:
   - Python: `pyproject.toml`, `setup.cfg`, `.flake8` -> ruff/black/isort/mypy/flake8 as configured
   - JavaScript/TypeScript: `package.json`, `.eslintrc`, `biome.json` -> eslint/prettier/biome/tsc as configured
   - Rust: `Cargo.toml` -> `cargo fmt`, `cargo clippy`
   - Go: `go.mod` -> `go fmt`, `go vet`
   - Other: check for `.editorconfig`, Makefile lint targets, or CI config for hints
2. **Run the formatter** on changed files only (not the whole codebase)
3. **Run the linter** on changed files only
4. **Run type checking** if the project has it configured
5. **Run tests** related to the changed files
6. **Fix any issues found** -- formatting auto-fixes applied silently, lint/type errors fixed and explained
7. **Only then commit** with a clean diff

Claude will NOT skip this process. If tests fail, Claude fixes them before committing. If it can't fix something, it tells the user what's wrong instead of committing broken code.

### 5. Test Awareness

When Claude is about to implement a change that touches logic (not just formatting, comments, or config), it will **think about tests first**.

**Triggers:** Any implementation that modifies function behavior, adds new functions, or changes data flow.

**What Claude does:**

1. **Check if tests exist** for the code being changed
2. **If tests exist:** run them first to establish a baseline, then run again after changes
3. **If no tests exist and the change is non-trivial:** briefly note what should be tested:
   ```
   Note: there are no tests for this function. After the change,
   you may want to add tests for [specific behaviors]. Want me to
   write them?
   ```
4. **Don't block on this** -- it's a suggestion, not a gate. If the user says "just do it", proceed without tests.

This works for any language. Claude detects the test framework from the project structure (pytest, jest, cargo test, go test, etc.) and runs accordingly.

---

## On-Demand: Plan & Build Mode

When you have a feature that's bigger than a one-shot change, say **"let's plan this"** (or any variation: "plan this out", "break this down", "let's think through this first") and Claude will switch into a structured planning flow.

**Phase 1 -- Understand:** Explore the codebase, ask up to 3 clarifying questions.

**Phase 2 -- Mini-PRD:**
```markdown
## Feature: [Name]
**Problem:** [what's missing or broken]
**Solution:** [what we're building]
**In scope:** [specific items]
**Out of scope:** [explicitly excluded]
**Key decisions:** [tech choices, patterns to follow]
```

**Phase 3 -- Task Breakdown:** Numbered checklist where each task is small, testable, and names the files it touches. Tests are interleaved with implementation, not bolted on at the end.

```markdown
## Tasks
- [ ] 1. [task] -- `src/file.ts`
- [ ] 2. [task] -- `src/other.ts`
- [ ] 3. Write tests for [behavior] -- `tests/file.test.ts`
- [ ] 4. [task] -- `src/file.ts`
- [ ] 5. Integration test -- `tests/integration.test.ts`
- [ ] 6. Run full test suite, fix regressions
```

**Phase 4 -- Test Plan:** Define test cases before writing code.

```markdown
## Tests
- [ ] [function] handles [normal case] -> [expected]
- [ ] [function] handles [edge case] -> [expected]
- [ ] [end-to-end scenario] -> [expected]
- [ ] Manual: [how to verify by hand]
```

**Phase 5 -- Execute:** Work through tasks one at a time. One task, one commit. After each task: run tests, check it off, commit.

The user can say "go" at any phase to skip ahead to implementation, or "adjust" to change the plan.

---

## Principles (Always Active)

### Read Before Write
Never modify a file without reading it first. Check for existing patterns before inventing new ones.

### Incremental Delivery
One logical change per commit. Run tests after every change, not at the end. If a task feels too big, break it down further.

### Minimal Changes
Don't refactor while debugging. Don't add features beyond what was asked. Don't add error handling for impossible scenarios. Three similar lines of code are better than a premature abstraction.

### Tests Prove It Works
"It works" means tests pass, not "I think it's fine." Define what done looks like before starting.

---

## Supporting Commands (Optional)

These slash commands are available if you want to explicitly trigger a workflow:

| Command | What It Does |
|---------|-------------|
| `/structure-request` | Force the clarification flow on your next message |
| `/plan-feature` | Jump straight into Plan & Build mode |
| `/debug-error` | Force the diagnostic flow on an error |
| `/commit` | Structured commit with conventional format |
| `/review <file>` | Code review checklist |
| `/clean` | Fix linting/formatting/type errors |

You never *need* these -- the auto-detect behaviors cover the same ground. They're there for when you want to be explicit.
