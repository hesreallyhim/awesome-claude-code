# Act

Work through the task list using a RED-GREEN-REFACTOR cycle.

## Behavior

1. **Find the task list.** Check for `todos.md` or `todo.md` in the project root. If neither exists, ask the user what to work on.

2. **Select the first unchecked item.**

3. **Plan the implementation.** Share a brief plan before writing code:
   - What files will be changed
   - What the approach is
   - Any risks or questions

4. **Implement the change:**
   - Write the minimal code to make it work (GREEN)
   - Run tests to verify
   - Refactor if the code is unclear, but only after tests pass (REFACTOR)

5. **Check off the item** in the task list.

6. **Run linting/formatting** on changed files (pre-commit cleanup).

7. **Commit** with a clear conventional commit message describing the change.

8. **Move to the next item** or ask the user if they want to continue.

## Rules

- One task at a time. Don't batch multiple tasks into one commit.
- Tests must pass before checking off a task.
- If a task is too big, break it into smaller sub-tasks in the task list.
- If stuck, explain what's blocking and ask for guidance instead of guessing.
