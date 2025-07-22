# Giselle Development Guide

## Build, Test, and Lint Commands
- Build all: `pnpm build`
- Build specific packages: `pnpm build-sdk`, `pnpm build-data-type`
- Type checking: `pnpm check-types`
- Type check packages with modified files: `pnpm -F <modified files packagename> check-types`
- Format code: `pnpm format`
- Development: `pnpm dev` (playground), `pnpm dev:studio.giselles.ai` (studio)
- Run tests: `pnpm -F <package> test` or `cd <directory> && vitest`
- Run specific test: `cd <directory> && vitest <file.test.ts>`
- Lint: `cd <directory> && biome check --write .`
- Format modified files: `pnpm biome check --write [filename]`

## Critical Requirements
- MUST run `pnpm biome check --write [filename]` after EVERY code modification
- MUST run `pnpm -F [packagename in file] check-types` to validate type safety of packages with modified files
- All code changes must be formatted using Biome before being committed
- All code changes must pass type checking in their respective packages before being committed

## Code Style Guidelines
- Use Biome for formatting with tab indentation and double quotes
- Follow organized imports pattern (enabled in biome.json)
- Use TypeScript for type safety; avoid `any` types
- Use functional components with React hooks
- Use Next.js patterns for web applications
- Follow package-based architecture for modularity
- Use async/await for asynchronous code rather than promises
- Error handling: use try/catch blocks and propagate errors appropriately
- Tests should follow `*.test.ts` naming pattern and use Vitest

## Naming Conventions
- **Files**: Use kebab-case for all filenames (e.g., `user-profile.ts`)
- **Components**: Use PascalCase for React components and classes (e.g., `UserProfile`)
- **Variables**: Use camelCase for variables, functions, and methods (e.g., `userEmail`)
- **Boolean Variables and Functions**: Use prefixes like `is`, `has`, `can`, `should` for clarity:
  - For variables: `isEnabled`, `hasPermission` (not `status`)
  - For functions: `isTriggerRequiringCallsign()`, `hasActiveSubscription()` (not `requiresCallsign()` or `checkActive()`)
- **Function Naming**: Use verbs or verb phrases that clearly indicate purpose (e.g., `calculateTotalPrice()`, not `process()`)
- **Consistency**: Follow these conventions throughout the codebase

## Language Support
- This project's core members include non-native English speakers
- Please correct grammar in commit messages, code comments, and pull request comments
- Rewrite user input when necessary to ensure clear communication
