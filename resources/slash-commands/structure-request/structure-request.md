# Structure Request

Turn a vague coding request into a specific, actionable prompt that Claude can execute well.

## Why This Exists

Generic requests like "fix this", "make it better", or "add a feature" fail because they lack:
- **What** specifically needs to change
- **Where** in the codebase it lives
- **Why** the change matters (what's broken or missing)
- **How** you'll know it worked (acceptance criteria)

This command forces you to fill in those gaps before Claude starts coding.

## When to Use

- You have an idea but haven't articulated it clearly yet
- You're about to paste something vague and want to sharpen it first
- You want Claude to ask the right clarifying questions instead of guessing

## Process

When the user invokes `/structure-request $ARGUMENTS`, do the following:

### Step 1: Parse the Raw Request

Read the user's input. Identify which of these are missing:

| Element | Question to Ask |
|---------|----------------|
| **Goal** | What specific outcome do you want? |
| **Location** | Which files, functions, or components are involved? |
| **Current behavior** | What happens now? (or what exists now?) |
| **Desired behavior** | What should happen instead? |
| **Constraints** | Any patterns, libraries, or approaches to follow or avoid? |
| **Acceptance criteria** | How will you verify this works? |

### Step 2: Ask Targeted Clarifying Questions

Ask ONLY about the missing elements. Do not ask about things the user already provided. Keep questions concrete:

- BAD: "Can you tell me more about what you want?"
- GOOD: "Which file contains the function you want to change? I see `auth.py` and `auth_helpers.py` in `src/auth/` -- which one?"

If the user's request mentions files or code, read those files first so your questions are grounded in reality, not hypothetical.

### Step 3: Synthesize the Structured Request

Once you have enough context, rewrite the request in this format and present it to the user for confirmation:

```markdown
## Structured Request

**Goal:** [one sentence]

**Files involved:**
- `path/to/file.py` -- [what role this file plays]

**Current behavior:**
[What happens now, or what's missing]

**Desired behavior:**
[Specific change expected]

**Constraints:**
- [Pattern to follow, library to use, etc.]

**Acceptance criteria:**
- [ ] [Testable condition 1]
- [ ] [Testable condition 2]
```

### Step 4: Confirm or Refine

Ask the user: "Does this capture what you want? I can adjust before we start implementation."

If the user says "yes" or "go" or "looks good", proceed to implementation using the structured request as your spec.

## Tips for the User

You don't need to have all the answers upfront. The point is to surface what's unclear *before* Claude writes code, not after. Even partial context ("I think it's somewhere in the auth module") is better than none.
