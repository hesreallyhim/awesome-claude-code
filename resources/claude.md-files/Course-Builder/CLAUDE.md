# Course Builder Development Guide

## Project Overview

Course Builder is a real-time multiplayer CMS (Content Management System) designed specifically for building and deploying developer education products. This monorepo contains multiple applications and shared packages that work together to provide a comprehensive platform for creating, managing, and delivering educational content.

### Main Features
- Content management for courses, modules, and lessons
- Video processing pipeline with transcription
- AI-assisted content creation and enhancement
- Real-time collaboration for content creators
- Authentication and authorization
- Payment processing and subscription management
- Progress tracking for students

### Key Technologies
- **Framework**: Next.js (App Router)
- **Language**: TypeScript
- **Monorepo**: Turborepo with PNPM workspaces
- **Database**: Drizzle ORM with MySQL/PlanetScale
- **Authentication**: NextAuth.js
- **Styling**: Tailwind CSS
- **API**: tRPC for type-safe API calls
- **Real-time**: PartyKit/websockets for collaboration
- **Event Processing**: Inngest for workflows and background jobs
- **Media**: Mux for video processing, Deepgram for transcription
- **AI**: OpenAI/GPT for content assistance
- **Payments**: Stripe integration

## Repository Structure

### Apps (`/apps`)
- `ai-hero`: Main application focused on AI-assisted learning
- `astro-party`: An Astro-based implementation
- `course-builder-web`: The main Course Builder web application
- `egghead`: Integration with egghead.io platform
- `epic-react`: Specific implementation for React courses
- `go-local-first`: Implementation with local-first capabilities

### Packages (`/packages`)
- **Core Functionality**:
  - `core`: Framework-agnostic core library
  - `ui`: Shared UI components based on Radix/shadcn
  - `adapter-drizzle`: Database adapter for Drizzle ORM
  - `next`: Next.js specific bindings
  - `commerce-next`: Commerce components and functionality

- **Utility Packages**:
  - `utils-ai`: AI-related utilities
  - `utils-auth`: Authentication and authorization utilities
  - `utils-aws`: AWS service utilities
  - `utils-browser`: Browser-specific utilities (cookies, etc.)
  - `utils-core`: Core utilities like `guid`
  - `utils-email`: Email-related utilities
  - `utils-file`: File handling utilities
  - `utils-media`: Media processing utilities
  - `utils-resource`: Resource filtering and processing utilities
  - `utils-search`: Search functionality utilities
  - `utils-seo`: SEO utilities
  - `utils-string`: String manipulation utilities
  - `utils-ui`: UI utilities like `cn`

### Other Directories
- `cli`: Command-line tools for project bootstrapping
- `docs`: Documentation including shared utilities guide
- `instructions`: Detailed instructions for development tasks
- `plop-templates`: Templates for code generation

## Command Reference

### Build Commands
- `pnpm build:all` - Build all packages and apps
- `pnpm build` - Build all packages (not apps)
- `pnpm build --filter="ai-hero"` - Build specific app
- `pnpm dev:all` - Run dev environment for all packages/apps
- `pnpm dev` - Run dev environment for packages only

### Testing
- `pnpm test` - Run all tests
- `pnpm test --filter="@coursebuilder/utils-file"` - Test specific package
- `pnpm test:watch` - Run tests in watch mode
- `cd packages/package-name && pnpm test` - Run tests for specific package
- `cd packages/package-name && pnpm test src/path/to/test.test.ts` - Run a single test file
- `cd packages/package-name && pnpm test:watch src/path/to/test.test.ts` - Watch single test file

### Linting and Formatting
- `pnpm lint` - Run linting on all packages/apps
- `pnpm format:check` - Check formatting without changing files
- `pnpm format` - Format all files using Prettier
- `pnpm typecheck` - Run TypeScript type checking
- `pnpm manypkg fix` - Fix dependency version mismatches and sort package.json files

Use `--filter="APP_NAME"` to run commands for a specific app

## Code Generation and Scaffolding

### Creating New Utility Packages
Use the custom Plop template to create new utility packages:

```bash
# Create a new utility package using the template
pnpm plop package-utils <domain> <utilityName> <functionName> "<utilityDescription>"

# Example:
pnpm plop package-utils browser cookies getCookies "Browser cookie utility"

# With named parameters:
pnpm plop package-utils -- --domain browser --utilityName cookies --functionName getCookies --utilityDescription "Browser cookie utility"
```

This will create a properly structured package with:
- Correct package.json with exports configuration
- TypeScript configuration
- Basic implementation with proper TSDoc comments
- Test scaffolding

### Working with Utility Packages

#### Adding Dependencies
When updating package.json files to add dependencies:
1. Use string replacement with Edit tool to add dependencies
2. Maintain alphabetical order of dependencies
3. Don't replace entire sections, just add the new line

Example of proper package.json edit:
```
"@coursebuilder/utils-media": "1.0.0",
"@coursebuilder/utils-seo": "1.0.0",

// Replace with:
"@coursebuilder/utils-media": "1.0.0",
"@coursebuilder/utils-resource": "1.0.0", // New line added here
"@coursebuilder/utils-seo": "1.0.0",
```

#### Framework Compatibility
When creating utility packages that interact with framework-specific libraries:
1. Keep framework-specific dependencies (React, Next.js, etc.) as peer dependencies
2. For utilities that use third-party libraries (like Typesense, OpenAI), provide adapters rather than direct implementations
3. Be careful with libraries that might conflict with framework internals
4. Test builds across multiple apps to ensure compatibility

## Code Style
- **Formatting**: Single quotes, no semicolons, tabs (width: 2), 80 char line limit
- **Imports**: Organized by specific order (React → Next → 3rd party → internal)
- **File structure**: Monorepo with apps in /apps and packages in /packages
- **Package Manager**: PNPM (v8.15.5+)
- **Testing Framework**: Vitest

### Conventional Commits
We use conventional commits with package/app-specific scopes:
- Format: `<type>(<scope>): <description>`
- Types: `feat`, `fix`, `refactor`, `style`, `docs`, `test`, `chore`
- Scopes:
  - App codes: `aih` (ai-hero), `egh` (egghead), `eweb` (epic-web)
  - Packages: `utils-email`, `core`, `ui`, `mdx-mermaid`, etc.

Examples:
- `fix(egh): convert SanityReference to SanityArrayElementReference`
- `style(mdx-mermaid): make flowcharts nicer`
- `refactor(utils): implement SEO utility package with re-export pattern`
- `feat(utils-email): create email utilities package with sendAnEmail`

## Common Patterns

### Dependency Management
When adding dependencies to packages in the monorepo, ensure that:
1. All packages use consistent dependency versions
2. Dependencies in package.json files are sorted alphabetically

If you encounter linting errors related to dependency versions or sorting:
```bash
# Fix dependency version mismatches and sort package.json files
pnpm manypkg fix
```

### Re-export Pattern for Backward Compatibility
When creating shared utility packages, use the re-export pattern to maintain backward compatibility:

```typescript
// In /apps/app-name/src/utils/some-utility.ts
// Re-export from the shared package
export { someUtility } from '@coursebuilder/utils-domain/some-utility'
```

This preserves existing import paths throughout the codebase while moving the implementation to a shared package.

#### Important: Avoid Object.defineProperty for Re-exports
Do NOT use `Object.defineProperty(exports, ...)` for re-exports as this can cause conflicts with framework internals, especially with Next.js and tRPC:

```typescript
// DON'T DO THIS - can cause "Cannot redefine property" errors in build
Object.defineProperty(exports, 'someFunction', {
  value: function() { /* implementation */ }
})

// INSTEAD DO THIS - standard export pattern
export function someFunction() { /* implementation */ }
```

These conflicts typically manifest as "Cannot redefine property" errors during build and are difficult to debug. They occur because the build process may try to define the same property multiple times through different bundling mechanisms.

### TSDoc Comments for Utilities
Always include comprehensive TSDoc comments for utility functions:

```typescript
/**
 * Brief description of what the function does
 * 
 * Additional details if needed
 * 
 * @param paramName - Description of the parameter
 * @returns Description of the return value
 * 
 * @example
 * ```ts
 * // Example usage code
 * const result = myFunction('input')
 * ```
 */
```

### App Directory Structure Pattern
Most apps follow this general directory structure:
- `src/app` - Next.js App Router pages and layouts
- `src/components` - React components
- `src/lib` - Domain-specific business logic
- `src/utils` - Utility functions
- `src/db` - Database schema and queries
- `src/server` - Server-side functions and API routes
- `src/hooks` - React hooks
- `src/trpc` - tRPC router and procedures

### Database Schema
Most applications use Drizzle ORM with a schema in `src/db/schema.ts` that typically includes:
- Users and authentication
- Content resources (courses, modules, lessons)
- Progress tracking
- Purchases and subscriptions

### Auth Pattern
Authentication usually follows this pattern:
- NextAuth.js for authentication providers
- CASL ability definitions for authorization
- Custom middleware for route protection
