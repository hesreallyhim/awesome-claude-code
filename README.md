<!--lint disable remark-lint:awesome-badge-->

#

<!-- [![Awesome](https://awesome.re/badge-flat2.svg)](https://awesome.re) -->

<pre>
            █████╗ ██╗    ██╗███████╗███████╗ ██████╗ ███╗   ███╗███████╗
           ██╔══██╗██║    ██║██╔════╝██╔════╝██╔═══██╗████╗ ████║██╔════╝
           ███████║██║ █╗ ██║█████╗  ███████╗██║   ██║██╔████╔██║█████╗
           ██╔══██║██║███╗██║██╔══╝  ╚════██║██║   ██║██║╚██╔╝██║██╔══╝
           ██║  ██║╚███╔███╔╝███████╗███████║╚██████╔╝██║ ╚═╝ ██║███████╗
           ╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝

 ██████╗██╗      █████╗ ██╗   ██╗██████╗ ███████╗     ██████╗ ██████╗ ██████╗ ███████╗
██╔════╝██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝    ██╔════╝██╔═══██╗██╔══██╗██╔════╝
██║     ██║     ███████║██║   ██║██║  ██║█████╗      ██║     ██║   ██║██║  ██║█████╗
██║     ██║     ██╔══██║██║   ██║██║  ██║██╔══╝      ██║     ██║   ██║██║  ██║██╔══╝
╚██████╗███████╗██║  ██║╚██████╔╝██████╔╝███████╗    ╚██████╗╚██████╔╝██████╔╝███████╗
 ╚═════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝     ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝
</pre>

<!--lint enable remark-lint:awesome-badge-->

[![Awesome](https://awesome.re/badge-flat2.svg)](https://awesome.re)

<!--lint disable double-link-->

This is a curated list of slash-commands, `CLAUDE.md` files, CLI tools, and other resources and guides for enhancing your [Claude Code](https://docs.anthropic.com/en/docs/claude-code) workflow.

<!--lint enable double-link-->

Claude Code is a cutting-edge CLI-based coding assistant and agent that you can access in your terminal or IDE. It is a rapidly evolving tool that offers a number of powerful capabilities, and allows for a lot of configuration, in a lot of different ways. Users are actively working out best practices and workflows. It is the hope that this repo will help the community share knowledge and understand how to get the most out of Claude Code.

## Contents

- [Slash-Commands](#slash-commands)
- [CLAUDE.md Files](#claudemd-files)
- [Workflows](#workflows)
- [Additional Resources](#additional-resources)
- [Official Documentation](#official-documentation)

## Slash-Commands

- [/2-commit-fast](https://github.com/steadycursor/steadystart/blob/main/.claude/commands/2-commit-fast.md) - Automates git commit process by selecting the first suggested message, generating structured commits with consistent formatting while skipping manual confirmation and removing Claude co-authorship footer.

- [/act](https://github.com/sotayamashita/dotfiles/blob/main/.claude/commands/act.md) - Generates React components with proper accessibility, creating ARIA-compliant components with keyboard navigation that follow React best practices and include comprehensive accessibility testing.

- [/add-to-changelog](https://github.com/berrydev-ai/blockdoc-python/blob/main/.claude/commands/add-to-changelog.md) - Adds new entries to changelog files while maintaining format consistency, properly documenting changes, and following established project standards for version tracking.

- [/analyze-code](https://github.com/Hkgstax/VALUGATOR/blob/main/.claude/commands/analyze-code.md) - Reviews code structure and identifies key components, mapping relationships between elements and suggesting targeted improvements for better architecture and performance.

- [/analyze-issue](https://github.com/jerseycheese/Narraitor/blob/feature/issue-227-ai-suggestions/.claude/commands/analyze-issue.md) - Fetches GitHub issue details to create comprehensive implementation specifications, analyzing requirements and planning structured approach with clear implementation steps.

- [/bug-fix](https://github.com/danielscholl/mvn-mcp-server/blob/main/.claude/commands/bug-fix.md) - Streamlines bug fixing by creating a GitHub issue first, then a feature branch for implementing and thoroughly testing the solution before merging.

- [/build-react-app](https://github.com/wmjones/wyatt-personal-aws/blob/main/.claude/commands/build-react-app.md) - Builds React applications locally with intelligent error handling, creating specific tasks for build failures and providing appropriate server commands based on build results.

- [/check](https://github.com/rygwdn/slack-tools/blob/main/.claude/commands/check.md) - Performs comprehensive code quality and security checks, featuring static analysis integration, security vulnerability scanning, code style enforcement, and detailed reporting.

- [/clean](https://github.com/Graphlet-AI/eridu/blob/main/.claude/commands/clean.md) - Addresses code formatting and quality issues by fixing black formatting problems, organizing imports with isort, resolving flake8 linting issues, and correcting mypy type errors.

- [/code_analysis](https://github.com/kingler/n8n_agent/blob/main/.claude/commands/code_analysis.md) - Provides a menu of advanced code analysis commands for deep inspection, including knowledge graph generation, optimization suggestions, and quality evaluation.

- [/commit](https://github.com/evmts/tevm-monorepo/blob/main/.claude/commands/commit.md) - Creates git commits using conventional commit format with appropriate emojis, following project standards and creating descriptive messages that explain the purpose of changes.

- [/context-prime](https://github.com/elizaOS/elizaos.github.io/blob/main/.claude/commands/context-prime.md) - Primes Claude with comprehensive project understanding by loading repository structure, setting development context, establishing project goals, and defining collaboration parameters.

- [/context_prime (NeuroVis-GoDot)](https://github.com/laportagm/NeruroVis-GoDot/blob/TheDefaultBranch/.claude/commands/context_prime.md) - Establishes specialized context for Godot Engine development projects by setting up AI as a Godot expert, defining project structure, referencing key documentation, and structuring collaboration workflow.

- [/create-command](https://github.com/scopecraft/command/blob/main/.claude/commands/create-command.md) - Guides Claude through creating new custom commands with proper structure by analyzing requirements, templating commands by category, enforcing command standards, and creating supporting documentation.

- [/create-docs](https://github.com/jerseycheese/Narraitor/tree/feature/issue-227-ai-suggestions/.claude/commands/create-docs.md) - Analyzes code structure and purpose to create comprehensive documentation detailing inputs/outputs, behavior, user interaction flows, and edge cases with error handling.

- [/create-jtbd](https://github.com/taddyorg/inkverse/blob/main/.claude/commands/create-jtbd.md) - Creates Jobs-to-be-Done frameworks that outline user needs with structured format, focusing on specific user problems and organizing by job categories for product development.

- [/create-pr](https://github.com/toyamarinyon/giselle/blob/main/.claude/commands/create-pr.md) - Streamlines pull request creation by handling the entire workflow: creating a new branch, committing changes, formatting modified files with Biome, and submitting the PR.

- [/create-prd](https://github.com/taddyorg/inkverse/blob/main/.claude/commands/create-prd.md) - Generates comprehensive product requirement documents outlining detailed specifications, requirements, and features following standardized document structure and format.

- [/create-prp](https://github.com/Wirasm/claudecode-utils/blob/main/.claude/commands/create-prp.md) - Creates product requirement plans by reading PRP methodology, following template structure, creating comprehensive requirements, and structuring product definitions for development.

- [/create-pull-request](https://github.com/liam-hq/liam/blob/main/.claude/commands/create-pull-request.md) - Provides comprehensive PR creation guidance with GitHub CLI, enforcing title conventions, following template structure, and offering concrete command examples with best practices.

- [/create-worktrees](https://github.com/evmts/tevm-monorepo/blob/main/.claude/commands/create-worktrees.md) - Creates git worktrees for all open PRs or specific branches, handling branches with slashes, cleaning up stale worktrees, and supporting custom branch creation for development.

- [/deploy](https://github.com/cloudartisan/cloudartisan.github.io/blob/main/.claude/commands/site/deploy.md) - Builds site with production settings, verifies build success, commits and pushes changes, and performs deployment checks for website publishing.

- [/do-issue](https://github.com/jerseycheese/Narraitor/blob/feature/issue-227-ai-suggestions/.claude/commands/do-issue.md) - Implements GitHub issues with manual review points, following a structured approach with issue number parameter and offering alternative automated mode for efficiency.

- [/docs](https://github.com/slunsford/coffee-analytics/blob/main/.claude/commands/docs.md) - Generates comprehensive documentation that follows project structure, documenting APIs and usage patterns with consistent formatting for better user understanding.

- [/dump](https://gist.github.com/fumito-ito/77c308e0382e06a9c16b22619f8a2f83#file-dump-md) - Dumps the current Claude Code conversation to a markdown file in `.claude/logs/` with timestamped files that include session details and preserve full conversation history.

- [/explain-issue-fix](https://github.com/hackdays-io/toban-contribution-viewer/blob/main/.claude/commands/explain-issue-fix.md) - Documents solution approaches for GitHub issues, explaining technical decisions, detailing challenges overcome, and providing implementation context for better understanding.

- [/five](https://github.com/TuckerTucker/tkr-agent-chat/blob/main/.claude/commands/five.md) - Applies the "five whys" methodology to perform root cause analysis, identify underlying issues, and create solution approaches for complex problems.

- [/fix-github-issue](https://github.com/jeremymailen/kotlinter-gradle/blob/master/.claude/commands/fix-github-issue.md) - Analyzes and fixes GitHub issues using a structured approach with GitHub CLI for issue details, implementing necessary code changes, running tests, and creating proper commit messages.

- [/fix-issue](https://github.com/metabase/metabase/blob/master/.claude/commands/fix-issue.md) - Addresses GitHub issues by taking issue number as parameter, analyzing context, implementing solution, and testing/validating the fix for proper integration.

- [/fix-pr](https://github.com/metabase/metabase/blob/master/.claude/commands/fix-pr.md) - Fetches and fixes unresolved PR comments by automatically retrieving feedback, addressing reviewer concerns, making targeted code improvements, and streamlining the review process.

- [/fixing_go_in_graph](https://github.com/Mjvolk3/torchcell/blob/main/.claude/commands/fixing_go_in_graph.md) - Focuses on Gene Ontology annotation integration in graph databases, handling multiple data sources, addressing graph representation issues, and ensuring correct data incorporation.

- [/husky](https://github.com/evmts/tevm-monorepo/blob/main/.claude/commands/husky.md) - Sets up and manages Husky Git hooks by configuring pre-commit hooks, establishing commit message standards, integrating with linting tools, and ensuring code quality on commits.

- [/implement-issue](https://github.com/cmxela/thinkube/blob/main/.claude/commands/implement-issue.md) - Implements GitHub issues following strict project guidelines, complete implementation checklists, variable naming conventions, testing procedures, and documentation requirements.

- [/implement-task](https://github.com/Hkgstax/VALUGATOR/blob/main/.claude/commands/implement-task.md) - Approaches task implementation methodically by thinking through strategy step-by-step, evaluating different approaches, considering tradeoffs, and implementing the best solution.

- [/initref](https://github.com/okuvshynov/cubestat/blob/main/.claude/commands/initref.md) - Initializes reference documentation structure with standard doc templates, API reference setup, documentation conventions, and placeholder content generation.

- [/load-llms-txt](https://github.com/ethpandaops/xatu-data/blob/master/.claude/commands/load-llms-txt.md) - Loads LLM configuration files to context, importing specific terminology, model configurations, and establishing baseline terminology for AI discussions.

- [/load_coo_context](https://github.com/Mjvolk3/torchcell/blob/main/.claude/commands/load_coo_context.md) - References specific files for sparse matrix operations, explains transform usage, compares with previous approaches, and sets data formatting context for development.

- [/load_dango_pipeline](https://github.com/Mjvolk3/torchcell/blob/main/.claude/commands/load_dango_pipeline.md) - Sets context for model training by referencing pipeline files, establishing working context, and preparing for pipeline work with relevant documentation.

- [/mermaid](https://github.com/GaloyMoney/lana-bank/blob/main/.claude/commands/mermaid.md) - Generates Mermaid diagrams from SQL schema files, creating entity relationship diagrams with table properties, validating diagram compilation, and ensuring complete entity coverage.

- [/new](https://github.com/cloudartisan/cloudartisan.github.io/blob/main/.claude/commands/projects/new.md) - Creates new blog posts with proper front matter, enforcing structure, generating standardized metadata, and following site conventions for content workflow.

- [/next-task](https://github.com/wmjones/wyatt-personal-aws/blob/main/.claude/commands/next-task.md) - Gets the next task from TaskMaster and creates a branch for it, integrating with task management systems, automating branch creation, and enforcing naming conventions.

- [/optimize](https://github.com/to4iki/ai-project-rules/blob/main/.claude/commands/optimize.md) - Analyzes code performance to identify bottlenecks, proposing concrete optimizations with implementation guidance for improved application performance.

- [/pr-review](https://github.com/arkavo-org/opentdf-rs/blob/main/.claude/commands/pr-review.md) - Reviews pull request changes to provide feedback, check for issues, and suggest improvements before merging into the main codebase.

- [/prime](https://github.com/yzyydev/AI-Engineering-Structure/blob/main/.claude/commands/prime.md) - Sets up initial project context by viewing directory structure and reading key files, creating standardized context with directory visualization and key documentation focus.

- [/project_hello_w_name](https://github.com/disler/just-prompt/blob/main/.claude/commands/project_hello_w_name.md) - Creates customizable greeting components with name input, demonstrating argument passing, component reusability, state management, and user input handling.

- [/release](https://github.com/kelp/webdown/blob/main/.claude/commands/release.md) - Manages software releases by updating changelogs, reviewing README changes, evaluating version increments, and documenting release changes for better version tracking.

- [/reminder](https://github.com/cmxela/thinkube/blob/main/.claude/commands/reminder.md) - Re-establishes project context after conversation breaks or compaction, restoring context and fixing guideline inconsistencies for complex implementations.

- [/repro-issue](https://github.com/rzykov/metabase/blob/master/.claude/commands/repro-issue.md) - Creates reproducible test cases for GitHub issues, ensuring tests fail reliably and documenting clear reproduction steps for developers.

- [/review_dcell_model](https://github.com/Mjvolk3/torchcell/blob/main/.claude/commands/review_dcell_model.md) - Reviews old Dcell implementation files, comparing with newer Dango model, noting changes over time, and analyzing refactoring approaches for better code organization.

- [/rsi](https://github.com/ddisisto/si/blob/main/.claude/commands/rsi.md) - Reads all commands and key project files to optimize AI-assisted development by streamlining the process, loading command context, and setting up for better development workflow.

- [/run-ci](https://github.com/hackdays-io/toban-contribution-viewer/blob/main/.claude/commands/run-ci.md) - Activates virtual environments, runs CI-compatible check scripts, iteratively fixes errors, and ensures all tests pass before completion.

- [/run-pre-commit](https://github.com/wmjones/wyatt-personal-aws/blob/main/.claude/commands/run-pre-commit.md) - Runs pre-commit checks with intelligent results handling, analyzing outputs, creating tasks for issue fixing, and integrating with task management systems.

- [/task-breakdown](https://github.com/Hkgstax/VALUGATOR/blob/main/.claude/commands/task-breakdown.md) - Analyzes feature requirements, identifies components and dependencies, creates manageable tasks, and sets priorities for efficient feature implementation.

- [/tdd](https://github.com/zscott/pane/blob/main/.claude/commands/tdd.md) - Guides development using Test-Driven Development principles, enforcing Red-Green-Refactor discipline, integrating with git workflow, and managing PR creation.

- [/tdd-implement](https://github.com/jerseycheese/Narraitor/blob/feature/issue-227-ai-suggestions/.claude/commands/tdd-implement.md) - Implements Test-Driven Development by analyzing feature requirements, creating tests first (red), implementing minimal passing code (green), and refactoring while maintaining tests.

- [/testing_plan_integration](https://github.com/buster-so/buster/blob/main/api/.claude/commands/testing_plan_integration.md) - Creates inline Rust-style tests, suggests refactoring for testability, analyzes code challenges, and creates comprehensive test coverage for robust code.

- [/update-branch-name](https://github.com/giselles-ai/giselle/blob/main/.claude/commands/update-branch-name.md) - Updates branch names with proper prefixes and formats, enforcing naming conventions, supporting semantic prefixes, and managing remote branch updates.

- [/update-docs](https://github.com/Consiliency/Flutter-Structurizr/blob/main/.claude/commands/update-docs.md) - Reviews current documentation status, updates implementation progress, reviews phase documents, and maintains documentation consistency across the project.

- [/use-stepper](https://github.com/zuplo/docs/blob/main/.claude/commands/use-stepper.md) - Reformats documentation to use React Stepper component, transforming heading formats, applying proper indentation, and maintaining markdown compatibility with admonition formatting.

- [/view_commands](https://github.com/cloudartisan/cloudartisan.github.io/blob/main/.claude/commands/view_commands.md) - Provides an organized directory of available project commands categorized by function, detailing post management commands, site management tools, and content creation capabilities.

## CLAUDE.md Files

- [AI IntelliJ Plugin](https://github.com/didalgolab/ai-intellij-plugin/blob/main/CLAUDE.md) - Provides comprehensive Gradle commands for IntelliJ plugin development with platform-specific coding patterns, detailed package structure guidelines, and clear internationalization standards.

- [AVS Vibe Developer Guide](https://github.com/Layr-Labs/avs-vibe-developer-guide/blob/master/CLAUDE.md) - Structures AI-assisted EigenLayer AVS development workflow with consistent naming conventions for prompt files and established terminology standards for blockchain concepts.

- [AWS MCP Server](https://github.com/alexei-led/aws-mcp-server/blob/main/CLAUDE.md) - Features multiple Python environment setup options with detailed code style guidelines, comprehensive error handling recommendations, and security considerations for AWS CLI interactions.

- [Basic Memory](https://github.com/basicmachines-co/basic-memory/blob/main/CLAUDE.md) - Presents an innovative AI-human collaboration framework with Model Context Protocol for bidirectional LLM-markdown communication and flexible knowledge structure for complex projects.

- [claude-code-mcp-enhanced](https://github.com/grahama1970/claude-code-mcp-enhanced/blob/66328d6bcc960c81ff24f6213ce5614000858698/CLAUDE.md) - Provides detailed and emphatic instructions for Claude to follow as a coding agent, with testing guidance, code examples, and compliance checks.

- [Comm](https://github.com/CommE2E/comm/blob/master/CLAUDE.md) - Serves as a development reference for E2E-encrypted messaging applications with code organization architecture, security implementation details, and testing procedures.

- [Course Builder](https://github.com/badass-courses/course-builder/blob/master/CLAUDE.md) - Enables real-time multiplayer capabilities for collaborative course creation with diverse tech stack integration and monorepo architecture using Turborepo.

- [Cursor Tools](https://github.com/eastlondoner/cursor-tools/blob/main/CLAUDE.md) - Creates a versatile AI command interface supporting multiple providers and models with flexible command options and browser automation through "Stagehand" feature.

- [DroidconKotlin](https://github.com/touchlab/DroidconKotlin/blob/main/CLAUDE.md) - Delivers comprehensive Gradle commands for cross-platform Kotlin Multiplatform development with clear module structure and practical guidance for dependency injection.

- [EDSL](https://github.com/expectedparrot/edsl/blob/main/CLAUDE.md) - Offers detailed build and test commands with strict code style enforcement, comprehensive testing requirements, and standardized development workflow using Black and mypy.

- [Giselle](https://github.com/giselles-ai/giselle/blob/main/CLAUDE.md) - Provides detailed build and test commands using pnpm and Vitest with strict code formatting requirements and comprehensive naming conventions for code consistency.

- [Guitar](https://github.com/soramimi/Guitar/blob/master/CLAUDE.md) - Serves as development guide for Guitar Git GUI Client with build commands for various platforms, code style guidelines for contributing, and project structure explanation.

- [HASH](https://github.com/hashintel/hash/blob/main/CLAUDE.md) - Features comprehensive repository structure breakdown with strong emphasis on coding standards, detailed Rust documentation guidelines, and systematic PR review process.

- [Inkline](https://github.com/inkline/inkline/blob/main/CLAUDE.md) - Structures development workflow using pnpm with emphasis on TypeScript and Vue 3 Composition API, detailed component creation process, and comprehensive testing recommendations.

- [JSBeeb](https://github.com/mattgodbolt/jsbeeb/blob/main/CLAUDE.md) - Provides development guide for JavaScript BBC Micro emulator with build and testing instructions, architecture documentation, and debugging workflows.

- [Lamoom Python](https://github.com/LamoomAI/lamoom-python/blob/main/CLAUDE.md) - Serves as reference for production prompt engineering library with load balancing of AI Models, API documentation, and usage patterns with examples.

- [LangGraphJS](https://github.com/langchain-ai/langgraphjs/blob/main/CLAUDE.md) - Offers comprehensive build and test commands with detailed TypeScript style guidelines, layered library architecture, and monorepo structure using yarn workspaces.

- [Metabase](https://github.com/metabase/metabase/blob/master/CLAUDE.md) - Details workflow for REPL-driven development in Clojure/ClojureScript with emphasis on incremental development, testing, and step-by-step approach for feature implementation.

- [MCP Engine](https://github.com/featureform/mcp-engine/blob/main/CLAUDE.md) - Enforces strict package management with comprehensive type checking rules, explicit PR description guidelines, and systematic approach to resolving CI failures.

- [Network Chronicles](https://github.com/Fimeg/NetworkChronicles/blob/main/CLAUDE.md) - Presents detailed implementation plan for AI-driven game characters with technical specifications for LLM integration, character guidelines, and service discovery mechanics.

- [Note Companion](https://github.com/different-ai/note-companion/blob/master/CLAUDE.md) - Provides detailed styling isolation techniques for Obsidian plugins using Tailwind with custom prefix to prevent style conflicts and practical troubleshooting steps.

- [Pareto Mac](https://github.com/ParetoSecurity/pareto-mac/blob/main/CLAUDE.md) - Serves as development guide for Mac security audit tool with build instructions, contribution guidelines, testing procedures, and workflow documentation.

- [Perplexity MCP](https://github.com/Family-IT-Guy/perplexity-mcp/blob/main/CLAUDE.md) - Offers clear step-by-step installation instructions with multiple configuration options, detailed troubleshooting guidance, and concise architecture overview of the MCP protocol.

- [SG Cars Trends Backend](https://github.com/sgcarstrends/backend/blob/main/CLAUDE.md) - Provides comprehensive structure for TypeScript monorepo projects with detailed commands for development, testing, deployment, and AWS/Cloudflare integration.

- [SPy](https://github.com/spylang/spy/blob/main/CLAUDE.md) - Enforces strict coding conventions with comprehensive testing guidelines, multiple code compilation options, and backend-specific test decorators for targeted filtering.

- [SteadyStart](https://github.com/steadycursor/steadystart/blob/main/CLAUDE.md) - Clear and direct instructives about style, permissions, Claude's "role", communications, and documentation of Claude Code sessions for other team members to stay abreast.

- [TPL](https://github.com/KarpelesLab/tpl/blob/master/CLAUDE.md) - Details Go project conventions with comprehensive error handling recommendations, table-driven testing approach guidelines, and modernization suggestions for latest Go features.

## Workflows

- [Blogging Platform Instructions](https://github.com/cloudartisan/cloudartisan.github.io/tree/d1ed4928b1326dcf658991e0b83387455d1b5004/.claude/commands) - Provides a well-structured set of commands for publishing and maintaining a blogging platform, including commands for creating posts, managing categories, and handling media files.

- [Claude Task Manager](https://gist.github.com/grahama1970/44a9da6a3da6769132037f06966945c2#file-00_readme-md) - Solves the critical challenge of context length limitations and task focus when working with Claude on complex projects through specialized context isolation and focused task execution.

- [Context Priming](https://github.com/disler/just-prompt/tree/main/.claude/commands) - Provides a systematic approach to priming Claude Code with comprehensive project context through specialized commands for different project scenarios and development contexts.

- [n8n_agent](https://github.com/kingler/n8n_agent/tree/main/.claude/commands) - Amazing comprehensive set of comments for code analysis, QA, design, documentation, project structure, project management, optimization, and many more.

- [Project Bootstrapping and Task Management](https://github.com/steadycursor/steadystart/tree/main/.claude/commands) - Provides a structured set of commands for bootstrapping and managing a new project, including meta-commands for creating and editing custom slash-commands.

- [Project Management, Implementation, Planning, and Release](https://github.com/scopecraft/command/tree/main/.claude/commands) - Really comprehensive set of commands for all aspects of SDLC.

- [Project Workflow System](https://github.com/harperreed/dotfiles/tree/master/.claude/commands) - A set of commands that provide a comprehensive workflow system for managing projects, including task management, code review, and deployment processes.

- [Simone](https://github.com/Helmi/claude-simone) - A broader project management workflow for Claude Code that encompasses not just a set of commands, but a system of documents, guidelines, and processes to facilitate project planning and execution.


## Wrappers

- [Claude Swarm](https://github.com/parruda/claude-swarm)  - Launch Claude Code session that is connected to a swarm of Claude Code Agents 	

- [Claude Hub](https://github.com/claude-did-this/claude-hub) -  A webhook service that connects Claude Code to GitHub repositories, enabling AI-powered code assistance directly through pull requests and issues. This integration allows Claude to analyze repositories, answer technical questions, and help developers understand and improve their codebase through simple @mentions. 

- [Claude Squad](https://github.com/smtg-ai/claude-squad) - Claude Squad is a terminal app that manages multiple Claude Code, Codex (and other local agents including Aider) in separate workspaces, allowing you to work on multiple tasks simultaneously.

- [Claude Code Flow](https://github.com/ruvnet/claude-code-flow) -  This mode serves as a code-first orchestration layer, enabling Claude to write, edit, test, and optimize code autonomously across recursive agent cycles. 

- [Claude Task Master](https://github.com/eyaltoledano/claude-task-master)  - A task management system for AI-driven development with Claude, designed to work seamlessly with Cursor AI.

- [Claude Code Router](https://github.com/musistudio/claude-code-router) -  Use Claude Code as the foundation for coding infrastructure, allowing you to decide how to interact with the model while enjoying updates from Anthropic.

- [Claude Composer](https://github.com/possibilities/claude-composer) - A tool that adds small enhancements to Claude Code

- [Container Use](https://github.com/dagger/container-use) -  Development environments for coding agents. Enable multiple agents to work safely and independently with your preferred stack.

## Additional Resources

- [CC Usage](https://github.com/ryoppippi/ccusage) - Handy CLI tool for managing and analyzing Claude Code usage, based on analyzing local Claude Code logs. Presents a nice dashboard regarding cost information, token consumption, etc. \[DISCLAIMER: Keep an eye on the Issues if you are relying on this tool for anything business-critical - the logs that track usage appear to suffer from some "double-counting" problems - this may have been resolved by the time you are reading this, but I wanted to raise awareness - it is not something only affecting this application\].

## Official Documentation

<!--lint disable double-link-->

- [Anthropic Documentation](https://docs.anthropic.com/en/docs/claude-code) - The official documentation for Claude Code, including installation instructions, usage guidelines, API references, tutorials, examples, loads of information that I won't list individually. Like Claude Code, the documentation is frequently updated.
<!--lint enable double-link-->

- [Anthropic Quickstarts](https://github.com/anthropics/anthropic-quickstarts/blob/main/CLAUDE.md) - Offers comprehensive development guides for three distinct AI-powered demo projects with standardized workflows, strict code style guidelines, and containerization instructions.

## Contributing

Please note that this project is released with a [Contributor Code of Conduct](code-of-conduct.md). By participating in this project you agree to abide by its terms.

Regarding content, we especially welcome:

- Proven, effective resources that follow best practices and may even be in use in production.
- Innovative, creative, or experimental workflows that perhaps are still being iterated upon, but have high potential value, and push the boundaries of Claude Code's documented capabilities and use cases.
- Claude Code "magic spells" - commands or workflows that seem to be especially effective.
- Applications of Claude Code outside of the traditional "coding assistant" context, e.g., CI/CD integration, testing, documentation, dev-ops, etc.

See [CONTRIBUTING.md](CONTRIBUTING.md) for more information on how to contribute to this project.
