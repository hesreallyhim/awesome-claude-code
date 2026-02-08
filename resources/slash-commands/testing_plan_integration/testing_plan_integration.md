# Integration Testing Plan

Create an integration testing plan for `$ARGUMENTS`.

## Behavior

1. **Read the code** being tested. Understand what it does, what its inputs/outputs are, and how it interacts with other components.

2. **Detect the language and test framework** from the project:
   - Python: pytest, unittest
   - JavaScript/TypeScript: jest, vitest, mocha
   - Rust: built-in `#[cfg(test)]` modules
   - Go: built-in `testing` package
   - Other: check for test config files or existing test patterns

3. **Suggest test cases** organized by category. Present them for review before writing any tests:

   ```
   ## Integration Tests for [component]

   ### Happy Path
   - [ ] [scenario] -> [expected result]

   ### Edge Cases
   - [ ] [scenario] -> [expected result]

   ### Error Handling
   - [ ] [scenario] -> [expected result]

   ### Cross-Component
   - [ ] [scenario involving multiple components] -> [expected result]
   ```

4. **Ask clarifying questions** if the code's behavior is ambiguous:
   - "Should this function handle [edge case] or is that the caller's responsibility?"
   - "What should happen when [dependency] is unavailable?"

5. **If the code is difficult to test**, suggest specific refactoring to improve testability:
   - Extract dependencies for easier mocking
   - Separate pure logic from I/O
   - Reduce coupling between components

6. **Wait for approval** before writing the tests. Let the user add, remove, or adjust test cases first.

7. **Write the tests** using the project's existing test patterns and conventions. Place them where the project's other tests live.
