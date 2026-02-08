# Structure Request

Force the clarification flow on the user's next message or on `$ARGUMENTS`.

## Behavior

Activate the **Vague Request Detection** workflow from the Coding-With-Claude CLAUDE.md, even if the request would otherwise seem specific enough to proceed.

1. Identify which of these are missing: **goal, files involved, current behavior, desired behavior, constraints, acceptance criteria**
2. Read any files or code already mentioned to ground your questions in the actual codebase
3. Ask up to 3 targeted questions about what's missing (no generic questionnaires)
4. Restate the request as a structured spec:
   ```
   Got it. Here's what I'll do:
   - Goal: [one sentence]
   - Files: [specific paths]
   - Change: [current behavior] -> [desired behavior]
   - Done when: [acceptance criteria]

   Good to go?
   ```
5. Wait for confirmation before implementing

This command exists as an explicit trigger. The same behavior runs automatically when Claude detects a vague request -- this just forces it even when the request seems clear.
