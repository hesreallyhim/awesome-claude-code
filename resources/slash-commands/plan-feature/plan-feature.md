# Plan Feature

Jump into the structured Plan & Build flow for `$ARGUMENTS`.

## Behavior

Activate the **Plan & Build Mode** from the Coding-With-Claude CLAUDE.md:

1. **Understand** -- Explore the codebase, ask up to 3 clarifying questions
2. **Mini-PRD** -- Problem, solution, in-scope, out-of-scope, key decisions
3. **Task Breakdown** -- Numbered checklist, each task names its files, tests interleaved
4. **Test Plan** -- Unit tests, integration tests, manual verification defined before code
5. **Execute** -- One task at a time, test after each, commit after each

The user can say "go" at any phase to skip ahead, or "adjust" to revise the plan.

This command exists as an explicit trigger. The same behavior activates automatically when the user says "let's plan this", "break this down", or similar.
