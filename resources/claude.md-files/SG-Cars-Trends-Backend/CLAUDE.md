# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Documentation Access

When working with external libraries or frameworks, use the Context7 MCP tools to get up-to-date documentation:

1. Use `mcp__context7__resolve-library-id` to find the correct library ID for any package
2. Use `mcp__context7__get-library-docs` to retrieve comprehensive documentation and examples

This ensures you have access to the latest API documentation for dependencies like Hono, Next.js, Drizzle ORM, Vitest,
and others used in this project.

# SG Cars Trends - Developer Reference Guide

## Project-Specific CLAUDE.md Files

This repository includes directory-specific CLAUDE.md files with detailed guidance for each component:

- **[apps/api/CLAUDE.md](apps/api/CLAUDE.md)**: API service development with Hono, workflows, tRPC, and social media integration
- **[apps/web/CLAUDE.md](apps/web/CLAUDE.md)**: Web application development with Next.js 15, HeroUI, blog features, and analytics
- **[packages/database/CLAUDE.md](packages/database/CLAUDE.md)**: Database schema management with Drizzle ORM, migrations, and TypeScript integration
- **[infra/CLAUDE.md](infra/CLAUDE.md)**: Infrastructure configuration with SST v3, AWS deployment, and domain management

Refer to these files for component-specific development guidance and best practices.

## Architecture Documentation

Comprehensive system architecture documentation with visual diagrams is available in the Mintlify documentation site:

- **[apps/docs/architecture/](apps/docs/architecture/)**: Complete architecture documentation with Mermaid diagrams
  - **[system.md](apps/docs/architecture/system.md)**: System architecture overview and component relationships
  - **[workflows.md](apps/docs/architecture/workflows.md)**: Data processing workflow sequence diagrams
  - **[database.md](apps/docs/architecture/database.md)**: Database schema and entity relationships
  - **[api.md](apps/docs/architecture/api.md)**: API architecture with Hono framework structure
  - **[infrastructure.md](apps/docs/architecture/infrastructure.md)**: AWS deployment topology and domain strategy
  - **[social.md](apps/docs/architecture/social.md)**: Social media integration workflows

- **[apps/docs/diagrams/](apps/docs/diagrams/)**: Source Mermaid diagram files (`.mmd` format)

These architectural resources provide visual understanding of system components, data flows, and integration patterns for effective development and maintenance.

# SG Cars Trends Platform - Overview

## Project Overview

SG Cars Trends (v4.11.0) is a full-stack platform providing access to Singapore vehicle registration data and Certificate of
Entitlement (COE) bidding results. The monorepo includes:

- **API Service**: RESTful endpoints for accessing car registration and COE data (Hono framework)
- **Web Application**: Next.js frontend with interactive charts, analytics, and blog functionality
- **Integrated Updater**: Workflow-based data update system with scheduled jobs that fetch and process data from LTA
  DataMall (QStash workflows)
- **LLM Blog Generation**: Automated blog post creation using Google Gemini AI to analyse market data and generate
  insights
- **Social Media Integration**: Automated posting to Discord, LinkedIn, Telegram, and Twitter when new data is available
- **Documentation**: Comprehensive developer documentation using Mintlify

## Commands

### Common Commands

All commands use pnpm v10.13.1 as the package manager:

**Build Commands:**
- Build all: `pnpm build`
- Build web: `pnpm build:web`
- Build admin: `pnpm build:admin`

**Development Commands:**
- Develop all: `pnpm dev`
- API dev server: `pnpm dev:api`
- Web dev server: `pnpm dev:web`
- Admin dev server: `pnpm dev:admin`

**Testing Commands:**
- Test all: `pnpm test`
- Test watch: `pnpm test:watch`
- Test coverage: `pnpm test:coverage`
- Test API: `pnpm test:api`
- Test web: `pnpm test:web`
- Run single test: `pnpm -F @sgcarstrends/api test -- src/utils/__tests__/slugify.test.ts`

**Linting Commands:**
- Lint all: `pnpm lint` (uses Biome with automatic formatting)
- Lint API: `pnpm lint:api`
- Lint web: `pnpm lint:web`

**Start Commands:**
- Start web: `pnpm start:web`

### Blog Commands

- View all blog posts: Navigate to `/blog` on the web application
- View specific blog post: Navigate to `/blog/[slug]` where slug is the post's URL slug
- Blog posts are automatically generated via workflows when new data is processed
- Blog posts include dynamic Open Graph images and SEO metadata

### Social Media Redirect Routes

The web application includes domain-based social media redirect routes that provide trackable, SEO-friendly URLs:

- **/discord**: Redirects to Discord server with UTM tracking
- **/twitter**: Redirects to Twitter profile with UTM tracking
- **/instagram**: Redirects to Instagram profile with UTM tracking
- **/linkedin**: Redirects to LinkedIn profile with UTM tracking
- **/telegram**: Redirects to Telegram channel with UTM tracking
- **/github**: Redirects to GitHub organisation with UTM tracking

All redirects include standardized UTM parameters:

- `utm_source=sgcarstrends`
- `utm_medium=social_redirect`
- `utm_campaign={platform}_profile`

## UTM Tracking Implementation

The platform implements comprehensive UTM (Urchin Tracking Module) tracking for campaign attribution and analytics, following industry best practices:

### UTM Architecture

**API UTM Tracking** (`apps/api/src/utils/utm.ts`):
- **Social Media Posts**: Automatically adds UTM parameters to all blog links shared on social platforms
- **Parameters**: `utm_source={platform}`, `utm_medium=social`, `utm_campaign=blog`, optional `utm_content` and `utm_term`
- **Platform Integration**: Used by `SocialMediaManager` for LinkedIn, Twitter, Discord, and Telegram posts

**Web UTM Utilities** (`apps/web/src/utils/utm.ts`):
- **External Campaigns**: `createExternalCampaignURL()` for email newsletters and external marketing
- **Parameter Reading**: `useUTMParams()` React hook for future analytics implementation
- **Type Safety**: Full TypeScript support with `UTMParams` interface

### UTM Best Practices

**Follows Industry Standards**:
- `utm_source`: Platform name (e.g., "linkedin", "twitter", "newsletter")
- `utm_medium`: Traffic type (e.g., "social", "email", "referral")
- `utm_campaign`: Campaign identifier (e.g., "blog", "monthly_report")
- `utm_term`: Keywords or targeting criteria (optional)
- `utm_content`: Content variant or placement (optional)

**Internal Link Policy**:
- **No UTM on internal links**: Follows best practices by not tracking internal navigation
- **External campaigns only**: UTM parameters reserved for measuring external traffic sources
- **Social media exceptions**: External social platform posts include UTM for attribution

### Database Commands

- Run migrations: `pnpm db:migrate`
- Check pending migrations: `pnpm db:migrate:check`
- Generate migrations: `pnpm db:generate`
- Push schema: `pnpm db:push`
- Drop database: `pnpm db:drop`

### Documentation Commands

- Docs dev server: `pnpm docs:dev`
- Docs build: `pnpm docs:build`
- Check broken links: `cd apps/docs && pnpm mintlify broken-links`

### Release Commands

- Create release: `pnpm release` (runs semantic-release locally, not recommended for production)
- Manual version check: `npx semantic-release --dry-run` (preview next version without releasing)

**Note**: Semantic releases are now configured to use the "release" branch instead of "main" branch.

### Deployment Commands

**Infrastructure Deployment:**
- Deploy all to dev: `pnpm deploy:dev`
- Deploy all to staging: `pnpm deploy:staging`
- Deploy all to production: `pnpm deploy:prod`

**API Deployment:**
- Deploy API to dev: `pnpm deploy:api:dev`
- Deploy API to staging: `pnpm deploy:api:staging`
- Deploy API to production: `pnpm deploy:api:prod`

**Web Deployment:**
- Deploy web to dev: `pnpm deploy:web:dev`
- Deploy web to staging: `pnpm deploy:web:staging`
- Deploy web to production: `pnpm deploy:web:prod`

## Code Structure

- **apps/api**: Unified API service using Hono framework with integrated updater workflows
    - **src/v1**: API endpoints for data access
    - **src/lib/workflows**: Workflow-based data update system and social media integration
    - **src/lib/gemini**: LLM blog generation using Google Gemini AI
    - **src/routes**: API route handlers including workflow endpoints
    - **src/config**: Database, Redis, QStash, and platform configurations
    - **src/trpc**: Type-safe tRPC router with authentication
- **apps/web**: Next.js frontend application
    - **src/app**: Next.js App Router pages and layouts with blog functionality
    - **src/components**: React components with comprehensive tests
    - **src/actions**: Server actions for blog and analytics functionality
    - **src/utils**: Web-specific utility functions
- **apps/admin**: Administrative interface for content management (unreleased)
- **apps/docs**: Mintlify documentation site
    - **architecture/**: Complete system architecture documentation with Mermaid diagrams
    - **diagrams/**: Source Mermaid diagram files for architecture documentation
- **packages/database**: Database schema and migrations using Drizzle ORM
    - **src/db**: Schema definitions for cars, COE, posts, and analytics tables
    - **migrations**: Database migration files with version tracking
- **packages/types**: Shared TypeScript type definitions
- **packages/utils**: Shared utility functions and Redis configuration
- **packages/config**: Shared configuration utilities (currently unused)
- **infra**: SST v3 infrastructure configuration for AWS deployment

## Monorepo Build System

The project uses Turbo for efficient monorepo task orchestration:

### Key Build Characteristics
- **Dependency-aware**: Tasks automatically run in dependency order with `dependsOn: ["^build"]` and topological ordering
- **Caching**: Build outputs cached with intelligent invalidation based on file inputs
- **Parallel execution**: Independent tasks run concurrently for optimal performance
- **Environment handling**: Strict environment mode with global dependencies on `.env` files, `tsconfig.json`, and `NODE_ENV`
- **CI Integration**: Global pass-through environment variables for GitHub and Vercel tokens

### Enhanced Task Configuration
- **Build tasks**: Generate `dist/**`, `.next/**` outputs with environment variable support
- **Test tasks**: Comprehensive input tracking with topological dependencies
- **Development tasks**: `dev` and `test:watch` use `cache: false`, `persistent: true`, and interactive mode
- **Migration tasks**: Track `migrations/**/*.sql` files with environment variables for database operations
- **Deployment tasks**: Cache-disabled with environment variable support for AWS and Vercel
- **TypeScript checking**: Dedicated `typecheck` task with TypeScript configuration dependencies

### Performance Optimization
- **TUI Interface**: Enhanced terminal user interface for better development experience
- **Strict Environment Mode**: Improved security and reliability with explicit environment variable handling
- **Input Optimization**: Uses `$TURBO_DEFAULT$` for standard file tracking patterns
- **Coverage Outputs**: Dedicated `coverage/**` directories for test reports
- **E2E Outputs**: `test-results/**` and `playwright-report/**` for end-to-end test artifacts

## Dependency Management

The project uses pnpm v10.13.1 with catalog for centralized dependency version management.

### pnpm Catalog

Centralized version definitions in `pnpm-workspace.yaml` ensure consistency across all workspace packages:

```yaml
catalog:
  '@types/node': ^22.16.4
  '@types/react': 19.1.0
  '@types/react-dom': 19.1.0
  '@vitest/coverage-v8': ^3.2.4
  'date-fns': ^3.6.0
  next: ^15.4.7
  react: 19.1.0
  'react-dom': 19.1.0
  sst: ^3.17.10
  typescript: ^5.8.3
  vitest: ^3.2.4
  zod: ^3.25.76
```

### Catalog Usage

Workspace packages reference catalog versions using the `catalog:` protocol:

```json
{
  "dependencies": {
    "react": "catalog:",
    "zod": "catalog:"
  },
  "devDependencies": {
    "typescript": "catalog:",
    "vitest": "catalog:"
  }
}
```

### Catalog Benefits

- **Single source of truth**: All shared dependency versions defined in one place
- **Version consistency**: Ensures all packages use the same versions
- **Easier upgrades**: Update version once in catalog, applies everywhere
- **Type safety**: TypeScript and types packages aligned across workspace
- **Testing consistency**: Testing tools (vitest, typescript) use same versions

### Root vs Catalog

- **Root package.json dependencies**: Packages actually installed and used by root workspace (e.g., turbo, semantic-release, husky)
- **Catalog entries**: Version definitions that workspace packages reference (e.g., react, next, typescript)
- **Both can reference catalog**: Root can use `"sst": "catalog:"` to maintain version consistency

### Workspace Binaries

When packages are installed at the root level, their CLI binaries (in `node_modules/.bin`) are automatically available to all workspace packages. This means:
- Root dependencies with CLIs (e.g., `sst`, `turbo`) can be used in any workspace package's scripts
- No need to duplicate CLI tools in individual packages
- Scripts in workspace packages can invoke binaries from root installation

## Code Style

- TypeScript with strict type checking (noImplicitAny, strictNullChecks)
- **Biome**: Used for formatting, linting, and import organization
    - Double quotes for strings (enforced)
    - 2 spaces for indentation (enforced)
    - Automatic import organization (enforced)
    - Recommended linting rules enabled
    - Excludes `.claude`, `.sst`, `coverage`, `migrations`, and `*.d.ts` files
- Function/variable naming: camelCase
- Class naming: PascalCase
- Constants: UPPER_CASE for true constants
- Error handling: Use try/catch for async operations with specific error types
- Use workspace imports for shared packages: `@sgcarstrends/utils` (includes Redis), `@sgcarstrends/database`, etc.
- Path aliases: Use `@api/` for imports in API app
- Avoid using `any` type - prefer unknown with type guards
- Group imports by: 1) built-in, 2) external, 3) internal
- **Commit messages**: Use conventional commit format with SHORT, concise messages enforced by commitlint:
    - **Preferred style**: Keep messages brief and direct (e.g., `feat: add user auth`, `fix: login error`)
    - `feat: add new feature` (minor version bump)
    - `fix: resolve bug` (patch version bump)
    - `feat!: breaking change` or `feat: add feature\n\nBREAKING CHANGE: description` (major version bump)
    - `chore:`, `docs:`, `style:`, `refactor:`, `test:` (no version bump)
    - **IMPORTANT**: Keep commit messages SHORT - single line with max 50 characters preferred, 72 characters absolute maximum
    - Avoid verbose descriptions - focus on what changed, not why or how
    - **Optional scopes**: Use scopes for package-specific changes: `feat(api):`, `fix(web):`, `chore(database):`
    - **Available scopes**: `api`, `web`, `docs`, `database`, `types`, `utils`, `infra`, `deps`, `release`
    - Root-level changes (CI, workspace setup) can omit scopes: `chore: setup commitlint`
- **Spelling**: Use English (Singapore) or English (UK) spellings throughout the entire project

## Git Hooks and Development Workflow

The project uses Husky v9+ with automated git hooks for code quality enforcement:

### Pre-commit Hook
- **lint-staged**: Automatically runs `pnpm biome check --write` on staged files
- Formats code and fixes lint issues before commits
- Only processes staged files for performance

### Commit Message Hook
- **commitlint**: Validates commit messages against conventional commit format
- Enforces optional scope validation for monorepo consistency
- Rejects commits with invalid format and provides helpful error messages

### Development Workflow
- Git hooks run automatically on `git commit`
- Failed hooks prevent commits and display clear error messages
- Use `git commit -n` to bypass hooks if needed (not recommended)
- Hooks ensure consistent code style and commit message format across the team

## Testing

- Testing framework: Vitest
- Tests should be in `__tests__` directories next to implementation
- Test file suffix: `.test.ts`
- Aim for high test coverage, especially for utility functions
- Use mock data where appropriate, avoid hitting real APIs in tests
- Coverage reports generated with V8 coverage
- Test both happy and error paths
- For component tests, focus on functionality rather than implementation details

## API Endpoints

### Data Access Endpoints

- **/v1/cars**: Car registration data (filterable by month, make, fuel type)
- **/v1/coe**: COE bidding results
- **/v1/coe/pqp**: COE Prevailing Quota Premium rates
- **/v1/makes**: List of car manufacturers
- **/v1/months/latest**: Get the latest month with data

### Updater Endpoints

- **/workflows/trigger**: Trigger data update workflows (authenticated)
- **/workflow/cars**: Car data update workflow endpoint
- **/workflow/coe**: COE data update workflow endpoint
- **/linkedin**: LinkedIn posting webhook
- **/twitter**: Twitter posting webhook
- **/discord**: Discord posting webhook
- **/telegram**: Telegram posting webhook

## Environment Setup

Required environment variables (store in .env.local for local development):

- DATABASE_URL: PostgreSQL connection string
- SG_CARS_TRENDS_API_TOKEN: Authentication token for API access
- UPSTASH_REDIS_REST_URL: Redis URL for caching
- UPSTASH_REDIS_REST_TOKEN: Redis authentication token
- UPDATER_API_TOKEN: Updater service token for scheduler
- LTA_DATAMALL_API_KEY: API key for LTA DataMall (for updater service)
- GEMINI_API_KEY: Google Gemini AI API key for blog post generation

## Deployment

- AWS Region: ap-southeast-1 (Singapore)
- Architecture: arm64
- Domains: sgcarstrends.com (with environment subdomains)
- Cloudflare for DNS management
- SST framework for infrastructure

## Domain Convention

SG Cars Trends uses a standardized domain convention across services:

### API Service

- **Convention**: `<service>.<environment>.<domain>`
- **Production**: `api.sgcarstrends.com`
- **Staging**: `api.staging.sgcarstrends.com`
- **Development**: `api.dev.sgcarstrends.com`

### Web Application

- **Convention**: `<environment>.<domain>` with apex domain for production
- **Production**: `sgcarstrends.com` (main user-facing domain)
- **Staging**: `staging.sgcarstrends.com`
- **Development**: `dev.sgcarstrends.com`

### Domain Strategy

- **API services** follow strict `<service>.<environment>.<domain>` pattern for clear service identification
- **Web frontend** uses user-friendly approach with apex domain in production for optimal SEO and branding
- **DNS Management**: All domains managed through Cloudflare with automatic SSL certificate provisioning
- **Cross-Origin Requests**: CORS configured to allow appropriate domain combinations across environments

### Adding New Services

- Backend services: Follow API pattern `<service>.<environment>.sgcarstrends.com`
- Frontend services: Evaluate based on user interaction needs (apex domain vs service subdomain)

## Data Models

The platform uses PostgreSQL with Drizzle ORM for type-safe database operations:

- **cars**: Car registrations by make, fuel type, and vehicle type with strategic indexing
- **coe**: COE bidding results (quota, bids, premium by category)
- **coePQP**: Prevailing Quota Premium rates
- **posts**: LLM-generated blog posts with metadata, tags, SEO information, and analytics
- **analyticsTable**: Page views and visitor tracking for performance monitoring

### Database Configuration

The database uses **snake_case** column naming convention configured in both Drizzle config and client setup. This ensures consistent naming patterns between the database schema and TypeScript types.

*See [packages/database/CLAUDE.md](packages/database/CLAUDE.md) for detailed schema definitions, migration workflows, and TypeScript integration patterns.*

## Workflow Architecture

The integrated updater service uses a workflow-based architecture with:

### Key Components

- **Workflows** (`src/lib/workflows/`): Cars and COE data processing workflows with integrated blog generation
- **Task Processing** (`src/lib/workflows/workflow.ts`): Common processing logic with Redis-based timestamp tracking
- **Updater Core** (`src/lib/updater/`): File download, checksum verification, CSV processing, and database
  updates (with helpers under `src/lib/updater/services/`)
- **Blog Generation** (`src/lib/workflows/posts.ts`): LLM-powered blog post creation using Google Gemini AI
- **Post Management** (`src/lib/workflows/save-post.ts`): Blog post persistence with slug generation and duplicate
  prevention
- **Social Media** (`src/lib/social/*/`): Platform-specific posting functionality (Discord, LinkedIn, Telegram, Twitter)
- **QStash Integration** (`src/config/qstash.ts`): Message queue functionality for workflow execution

### Workflow Flow

1. Workflows triggered via HTTP endpoints or scheduled QStash cron jobs
2. Files downloaded and checksums verified to prevent redundant processing
3. New data inserted into database in batches
4. Updates published to configured social media platforms when data changes
5. **Blog Generation**: LLM analyzes processed data to create comprehensive blog posts with market insights
6. **Blog Publication**: Generated posts saved to database with SEO-optimized slugs and metadata
7. **Blog Promotion**: New blog posts automatically announced across social media platforms
8. Comprehensive error handling with Discord notifications for failures

### Design Principles

- Modular and independent workflows
- Checksum-based redundancy prevention
- Batch database operations for efficiency
- Conditional social media publishing based on environment and data changes

## LLM Blog Generation

The platform features automated blog post generation using Google Gemini AI to create market insights from processed
data:

### Blog Generation Process

1. **Data Analysis**: LLM analyzes car registration or COE bidding data for the latest month
2. **Content Creation**: AI generates comprehensive blog posts with market insights, trends, and analysis
3. **Structured Output**: Posts include executive summaries, data tables, and professional market analysis
4. **SEO Optimization**: Automatic generation of titles, descriptions, and structured data
5. **Duplicate Prevention**: Slug-based system prevents duplicate blog posts for the same data period

### Blog Content Features

- **Cars Posts**: Analysis of registration trends, fuel type distribution, vehicle type breakdowns
- **COE Posts**: Bidding results analysis, premium trends, market competition insights
- **Data Tables**: Markdown tables for fuel type and vehicle type breakdowns
- **Market Insights**: Professional analysis of trends and implications for car buyers
- **Reading Time**: Automatic calculation of estimated reading time
- **AI Attribution**: Clear labeling of AI-generated content with model version tracking

### Blog Publication

- **Automatic Scheduling**: Blog posts generated only when both COE bidding exercises are complete (for COE posts)
- **Social Media Promotion**: New blog posts automatically announced across all configured platforms
- **SEO Integration**: Dynamic Open Graph images, structured data, and canonical URLs
- **Content Management**: Posts stored with metadata including generation details and data source month

## Shared Package Architecture

The project uses shared packages for cross-application concerns:

### Redis Configuration (`packages/utils`)

Redis configuration is centralized in the `@sgcarstrends/utils` package to eliminate duplication:

- **Shared Redis Instance**: Exported `redis` client configured with Upstash credentials
- **Environment Variables**: Automatically reads `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN`
- **Usage Pattern**: Import via `import { redis } from "@sgcarstrends/utils"`
- **Applications**: Used by both API service (caching, workflows) and web application (analytics, view tracking)

This consolidation ensures consistent Redis configuration across all applications and simplifies environment management.

### Other Shared Utilities

- **Type Definitions**: `@sgcarstrends/types` for shared TypeScript interfaces
- **Database Schema**: `@sgcarstrends/database` for Drizzle ORM schemas and migrations
- **Utility Functions**: Date formatting, percentage calculations, and key generation utilities

## Release Process

Releases are automated using semantic-release based on conventional commits:

- **Automatic releases**: Triggered on push to main branch via GitHub Actions
- **Version format**: Uses "v" prefix (v1.0.0, v1.1.0, v2.0.0)
- **Unified versioning**: All workspace packages receive the same version bump
- **Changelog**: Automatically generated and updated
- **GitHub releases**: Created automatically with release notes

## Contribution Guidelines

- Create feature branches from main branch
- **Use conventional commit messages** following the format specified in Code Style section
- Submit PRs with descriptive titles and summaries
- Ensure CI passes (tests, lint, typecheck) before requesting review
- Maintain backward compatibility for public APIs
- Follow project spelling and commit message conventions as outlined in Code Style section
- **Use GitHub issue templates** when available - always follow established templates when creating or managing GitHub issues
