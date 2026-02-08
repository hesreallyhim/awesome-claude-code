# Debug Error

Force the diagnostic flow on an error provided in `$ARGUMENTS`.

## Behavior

Activate the **Error Diagnosis Mode** from the Coding-With-Claude CLAUDE.md:

1. **Read** the files referenced in the error (never guess at contents)
2. **Ask** for missing context: what changed, what was expected, what was tried
3. **Hypothesize** -- state what you think is wrong and why, before touching code
4. **Verify** -- confirm the hypothesis by reading more code or running a diagnostic
5. **Fix** -- apply the minimal change that addresses the root cause
6. **Confirm** -- re-run the failing command/test
7. **Explain** -- ROOT CAUSE / FIX / PREVENTION summary

This command exists as an explicit trigger. The same behavior runs automatically when Claude detects a stack trace, error message, or test failure in your message.
