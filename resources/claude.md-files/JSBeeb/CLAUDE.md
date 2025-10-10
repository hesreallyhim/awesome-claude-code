# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Test Commands

- `npm start` - Start development server (IMPORTANT: Never run this command directly; ask the user to start the server
  as needed)
- `npm run build` - Build production version
- `npm run lint` - Run ESLint
- `npm run lint-fix` - Run ESLint with auto-fix
- `npm run format` - Run Prettier
- `npm run test` - Run all tests
- `npm run test:unit` - Run unit tests
- `npm run test:integration` - Run integration tests
- `npm run test:cpu` - Run CPU compatibility tests
- `npm run ci-checks` - Run linting checks for CI
- `vitest run tests/unit/test-gzip.js` - Run a single test file

### Code Coverage

- `npm run coverage:unit` - Run unit tests with coverage
- `npm run coverage:all-tests` - Run all tests with coverage
- Coverage reports are generated in the `coverage` directory
- HTML report includes line-by-line coverage visualization

## Code Style Guidelines

- **Formatting**: Uses Prettier, configured in package.json
- **Linting**: ESLint with eslint-config-prettier integration
- **Modules**: ES modules with import/export syntax (type: "module")
- **JavaScript Target**: ES2020 with strict null checks
- **Error Handling**: Use try/catch with explicit error messages that provide context about what failed
- **Naming**: camelCase for variables and functions, PascalCase for classes
- **Imports**: Group by source (internal/external) with proper separation
- **Documentation**: Use JSDoc for public APIs and complex functions, add comments for non-obvious code
- **Error Messages**: Use consistent, specific error messages (e.g., "Track buffer overflow" instead of "Overflow in disc building")

## Test Organization

- **Test Consolidation**: All tests for a specific component should be consolidated in a single test file.
  For example, all tests for `emulator.js` should be in `test-emulator.js` - do not create separate test files
  for different aspects of the same component.
- **Test Structure**: Use nested describe blocks to organize tests by component features
- **Test Isolation**: When mocking components in tests, use `vi.spyOn()` with `vi.restoreAllMocks()` in
  `afterEach` hooks rather than global `vi.mock()` to prevent memory leaks and test pollution
- **Memory Management**: Avoid global mocks that can leak between tests and accumulate memory usage over time
- **Test philosophy**
  - Mock as little as possible: Try and rephrase code not to require it.
  - Try not to rely on internal state: don't manipulate objects' inner state in tests
  - Use idiomatic vitest assertions (expect/toBe/toEqual) instead of node assert

## Project-Specific Knowledge

- **Never commit code unless asked**: Very often we'll work on code and iterate. After you think it's complete, let me
  check it before you commit.

### Code Architecture

- **General Principles**:
  - Follow the existing code style and structure
  - Use `const` and `let` instead of `var`
  - Avoid global variables; use module scope
  - Use arrow functions for callbacks
  - Prefer template literals over string concatenation
  - Use destructuring for objects and arrays when appropriate
  - Use async/await for asynchronous code instead of callbacks or promises
  - Minimise special case handling - prefer explicit over implicit behaviour
  - Consider adding tests first before implementing features
- **When simplifying existing code**

  - Prefer helper functions for repetitive operations (like the `appendParam` function)
  - Remove unnecessary type checking where types are expected to be correct
  - Replace complex conditionals with more readable alternatives when possible
  - Ensure simplifications don't break existing behavior or assumptions
  - Try and modernise the code to use ES6+ features where possible

- Prefer helper functions for repetitive operations (like the `appendParam` function)
- Remove unnecessary type checking where types are expected to be correct
- Replace complex conditionals with more readable alternatives when possible
- Ensure simplifications don't break existing behavior or assumptions

- **Constants and Magic Numbers**:

  - Local un-exported properties should be used for shared constants
  - Local constants should be used for temporary values
  - Always use named constants instead of magic numbers in code
  - Use PascalCase for module-level constants (e.g., `const MaxHfeTrackPulses = 3132;`)
  - Prefer module-level constants over function-local constants for shared values
  - Define constants at the beginning of functions or at the class/module level as appropriate
  - Add comments explaining what the constant represents, especially for non-obvious values

- **Pre-commit Hooks**:
  - The project uses lint-staged with ESLint
  - Watch for unused variables and ensure proper error handling
  - YOU MUST NEVER bypass git commit hooks on checkins. This leads to failures in CI later on

### Git Workflow

- When creating branches with Claude, use the `claude/` prefix (e.g., `claude/fix-esm-import-error`)
