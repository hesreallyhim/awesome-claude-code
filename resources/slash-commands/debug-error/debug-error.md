# Debug Error

Systematically diagnose and fix an error instead of blindly guessing at solutions.

## Why This Exists

Pasting an error message and saying "fix this" fails because:
- The error message is a **symptom**, not the cause
- Claude doesn't know what you changed recently, what you already tried, or what the code is supposed to do
- Without that context, Claude often makes changes that suppress the error but don't fix the root issue

This command enforces a diagnostic process: gather context, form a hypothesis, verify, then fix.

## When to Use

- You hit an error (stack trace, build failure, test failure, unexpected behavior)
- You've been going in circles trying to fix something
- Claude made a change that broke something and you want a systematic recovery

## Process

When the user invokes `/debug-error $ARGUMENTS`, do the following:

### Step 1: Gather the Facts

Collect these pieces of information. Read files and ask the user as needed:

| Fact | How to Get It |
|------|---------------|
| **The exact error** | User provides stack trace, error message, or screenshot |
| **When it started** | Ask: "Did this work before? What changed?" or check `git diff` / `git log --oneline -10` |
| **What was expected** | Ask: "What should have happened instead?" |
| **What was already tried** | Ask: "Have you tried anything to fix it? What happened?" |
| **The failing code** | Read the file(s) referenced in the stack trace |
| **Related context** | Read imports, configs, tests, or dependencies that the failing code touches |

IMPORTANT: Actually read the files mentioned in the error. Do not guess at their contents.

### Step 2: Form a Hypothesis

Based on the facts, state your hypothesis clearly:

```
HYPOTHESIS: The error occurs because [specific cause] in [specific location].
This explains the error because [reasoning].
```

If you have multiple plausible hypotheses, rank them by likelihood and test the most likely one first.

### Step 3: Verify Before Fixing

Before making changes, verify your hypothesis:
- Add a diagnostic print/log statement, or
- Read additional code to confirm the path, or
- Check if the issue exists in tests, or
- Run the code with a minimal reproduction

State what you checked and what you found.

### Step 4: Apply the Minimal Fix

Make the smallest change that addresses the root cause. Do NOT:
- Refactor surrounding code
- Add "defensive" error handling everywhere
- Change things unrelated to the error
- Suppress the error without fixing the cause

### Step 5: Verify the Fix

- Run the failing command/test again
- Check that no new errors were introduced
- If the project has tests, run them

### Step 6: Explain What Happened

Give the user a brief summary:

```
ROOT CAUSE: [what was actually wrong]
FIX: [what was changed and why]
PREVENTION: [how to avoid this in the future, if applicable]
```

## Tips for the User

When you paste an error, include:
1. The **full** error/stack trace (not just the last line)
2. The **command** you ran to trigger it
3. What **changed recently** (even "I don't know" is useful context)

The more of this you provide upfront, the fewer roundtrips it takes to fix.
