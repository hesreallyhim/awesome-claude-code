<!--lint disable remark-lint:awesome-badge-->

<!-- Responsive Logo with Theme Support -->
<div align="center">
  
  <!-- Same ASCII art for all screen sizes, just scales down on mobile -->
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./assets/logo-dark.svg">
    <img src="./assets/logo-light.svg" alt="Awesome Claude Code" width="100%" style="max-width: 900px;">
  </picture>
  
</div>

<!-- Generated with https://github.com/denvercoder1/readme-typing-svg -->

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&pause=1000&color=F7080D&random=true&width=435&lines=Fumigating...;Gallivanting...;Matriculating...;Toodleedoodling...;Goo-goo-g'joob-ing...;Excaliburating...;Canoodling...;Doing+the+humpty+dance...;Shiver-me-timbers-ing...;Becoming+sentient...;Opening+the+pod+bay+doors...;Rimraf-ing;23-skidoo-ing)](https://git.io/typing-svg)

<!--lint enable remark-lint:awesome-badge-->

[![Awesome](https://awesome.re/badge-flat2.svg)](https://awesome.re)

# [Awesome Claude Code](https://github.com/hesreallyhim/awesome-claude-code) 🤝 [Awesome Claude Code Agents](https://github.com/hesreallyhim/awesome-claude-code-agents)

<!--lint enable remark-lint:awesome-badge-->

<!--lint disable double-link-->

This is a curated list of slash-commands, `CLAUDE.md` files, CLI tools, and other resources and guides for enhancing your [Claude Code](https://docs.anthropic.com/en/docs/claude-code) workflow, productivity, and vibes.

<!--lint enable double-link-->

Claude Code is a cutting-edge CLI-based coding assistant and agent released by [Anthropic](https://www.anthropic.com/) that you can access in your terminal or IDE. It is a rapidly evolving tool that offers a number of powerful capabilities, and allows for a lot of configuration, in a lot of different ways. Users are actively working out best practices and workflows. It is the hope that this repo will help the community share knowledge and understand how to get the most out of Claude Code.

### Announcements

- 2025-08-16  

(i) So much happening with Claude Code these days, it is genuinely hard to keep up! Since my last post, let's see... Opus 4.1; status lines; output styles; more sub agents; (plugins??); background shells; lions; tigers... wait sorry that's something else. Anyway, I'm glad to announce that besides some annoying bot messages and small glitches, the new resource submission workflow seems to be working really solidly. It's so much easier for everyone, so if you'd like to contribute to this community resource, make sure you are up to date on [`CONTRIBUTING.md`](../CONTRIBUTING.md) - I will no longer be accepting _resource submission_ PRs (there may be other cases where a PR is appropriate), but you can now submit something to the list without even cloning the repo or knowing how to spell "git". Just head over to the new resource submission [Issue Template](https://github.com/hesreallyhim/awesome-claude-code/issues/new?template=submit-resource.yml) and you'll be done in no time. If you have a PR open, please try to open it as an issue instead, although I will of course get through existing PR's before switching over entirely.

(ii) I started a new section for Status Lines, and will soon open up another one for Output Styles hopefully. *WE WANT TO SEE YOUR STATUS LINES!* Definitely will be prioritizing those items in the short term. I've sadly been neglecting the awesome-claude-code-agents repo due to Claude Code's impressively rapid release cycle, but I haven't forgotten about it, rest assured.

(iii) Still hoping to organize some friendly competition as soon as time allows.

(iv) Considering imposing some more constraints on submissions, in particular I may decide to have your repo (if it is a repo) evaluated by a State-of-the-art language model, primarily for security, and not for awesomeness, as it's getting hard to keep up with all the great stuff coming in while still doing due diligence to make sure that this is not a home for malware or otherwise insecure resources.

(v) Check out some of the latest entries below, and start shipping your status lines! Even small entries are totally welcome, it doesn't have to be a Picasso - if it fits on a single line, that makes it even easier to compose it with another awesome resource.

## This Week's Additions ✨

> Resources added in the past 7 days

[`ccapi`](https://github.com/4xian/claude-auto-api) &nbsp; by &nbsp; [4xian](https://github.com/4xian)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Claude Code configuration management tool fast switching between multiple addresses multiple API_KEYs multiple AUTH_TOKENs and multiple models; with delay testing and automatic optimal line switching functions

[`cchistory`](https://github.com/eckardt/cchistory) &nbsp; by &nbsp; [eckardt](https://github.com/eckardt)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Like the shell history command but for your Claude Code sessions. Easily list all Bash or "Bash-mode" (`!`) commands Claude Code ran in a session for reference.

[`Happy Coder`](https://github.com/slopus/happy) &nbsp; by &nbsp; [GrocerPublishAgent](https://peoplesgrocers.com/en/projects)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Spawn and control multiple Claude Codes in parallel from your phone or desktop. Happy Coder runs Claude Code on your hardware, sends push notifications when Claude needs more input or permission, and costs nothing.


## Contents

▪&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Workflows & Knowledge Guides](#workflows--knowledge-guides-)  
▪&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Tooling](#tooling-)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▫&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[IDE Integrations](#ide-integrations)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▫&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Usage Monitors](#usage-monitors)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▫&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Orchestrators](#orchestrators)  
▪&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Statusline](#statusline-)  
▪&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Hooks](#hooks-)  
▪&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Slash-Commands](#slash-commands-)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▫&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Version Control & Git](#version-control--git)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▫&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Code Analysis & Testing](#code-analysis--testing)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▫&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Context Loading & Priming](#context-loading--priming)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▫&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Documentation & Changelogs](#documentation--changelogs)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▫&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[CI / Deployment](#ci--deployment)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▫&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Project & Task Management](#project--task-management)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▫&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Miscellaneous](#miscellaneous)  
▪&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[CLAUDE.md Files](#claudemd-files-)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▫&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Language-Specific](#language-specific)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▫&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Domain-Specific](#domain-specific)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▫&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Project Scaffolding & MCP](#project-scaffolding--mcp)  
▪&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Official Documentation](#official-documentation-%EF%B8%8F)  

<br>

## Workflows & Knowledge Guides 🧠

> A **workflow** is a tightly coupled set of Claude Code-native resources that facilitate specific projects

[`Blogging Platform Instructions`](https://github.com/cloudartisan/cloudartisan.github.io/tree/main/.claude/commands) &nbsp; by &nbsp; [cloudartisan](https://github.com/cloudartisan)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;CC-BY-SA-4.0  
Provides a well-structured set of commands for publishing and maintaining a blogging platform, including commands for creating posts, managing categories, and handling media files.

[`ClaudeLog`](https://claudelog.com) &nbsp; by &nbsp; [InventorBlack](https://www.reddit.com/user/inventor_black/)    
A comprehensive knowledge base with detailed breakdowns of advanced [mechanics](https://claudelog.com/mechanics/you-are-the-main-thread/) including [CLAUDE.md best practices](https://claudelog.com/mechanics/claude-md-supremacy), practical technique guides like [plan mode](https://claudelog.com/mechanics/plan-mode), [ultrathink](https://claudelog.com/faqs/what-is-ultrathink/), [sub-agents](https://claudelog.com/mechanics/task-agent-tools/), [agent-first design](https://claudelog.com/mechanics/agent-first-design/) and [configuration guides](https://claudelog.com/configuration).

[`Context Priming`](https://github.com/disler/just-prompt/tree/main/.claude/commands) &nbsp; by &nbsp; [disler](https://github.com/disler)    
Provides a systematic approach to priming Claude Code with comprehensive project context through specialized commands for different project scenarios and development contexts.

[`Laravel TALL Stack AI Development Starter Kit`](https://github.com/tott/laravel-tall-claude-ai-configs) &nbsp; by &nbsp; [tott](https://github.com/tott)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Transform your Laravel TALL (Tailwind, AlpineJS, Laravel, Livewire) stack development with comprehensive Claude Code configurations that provide intelligent assistance, systematic workflows, and domain expert consultation.

[`n8n_agent`](https://github.com/kingler/n8n_agent/tree/main/.claude/commands) &nbsp; by &nbsp; [kingler](https://github.com/kingler)    
Amazing comprehensive set of comments for code analysis, QA, design, documentation, project structure, project management, optimization, and many more.

[`Project Bootstrapping and Task Management`](https://github.com/steadycursor/steadystart/tree/main/.claude/commands) &nbsp; by &nbsp; [steadycursor](https://github.com/steadycursor)    
Provides a structured set of commands for bootstrapping and managing a new project, including meta-commands for creating and editing custom slash-commands.

[`Project Management, Implementation, Planning, and Release`](https://github.com/scopecraft/command/tree/main/.claude/commands) &nbsp; by &nbsp; [scopecraft](https://github.com/scopecraft)    
Really comprehensive set of commands for all aspects of SDLC.

[`Project Workflow System`](https://github.com/harperreed/dotfiles/tree/master/.claude/commands) &nbsp; by &nbsp; [harperreed](https://github.com/harperreed)    
A set of commands that provide a comprehensive workflow system for managing projects, including task management, code review, and deployment processes.

[`Shipping Real Code w/ Claude`](https://diwank.space/field-notes-from-shipping-real-code-with-claude) &nbsp; by &nbsp; [Diwank](https://github.com/creatorrr)    
A detailed blog post explaining the author's process for shipping a product with Claude Code, including CLAUDE.md files and other interesting resources.

[`Simone`](https://github.com/Helmi/claude-simone) &nbsp; by &nbsp; [Helmi](https://github.com/Helmi)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
A broader project management workflow for Claude Code that encompasses not just a set of commands, but a system of documents, guidelines, and processes to facilitate project planning and execution.

[`Slash-commands megalist`](https://github.com/wcygan/dotfiles/tree/d8ab6b9f5a7a81007b7f5fa3025d4f83ce12cc02/claude/commands) &nbsp; by &nbsp; [wcygan](https://github.com/wcygan)    
A pretty stunning list (88 at the time of this post!) of slash-commands ranging from agent orchestration, code review, project management, security, documentation, self-assessment, almost anything you can dream of.

<br>

## Tooling 🧰

> **Tooling** denotes applications that are built on top of Claude Code and consist of more components than slash-commands and `CLAUDE.md` files

[`ccapi`](https://github.com/4xian/claude-auto-api) &nbsp; by &nbsp; [4xian](https://github.com/4xian)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Claude Code configuration management tool fast switching between multiple addresses multiple API_KEYs multiple AUTH_TOKENs and multiple models; with delay testing and automatic optimal line switching functions

[`ccexp`](https://github.com/nyatinte/ccexp) &nbsp; by &nbsp; [nyatinte](https://github.com/nyatinte)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Interactive CLI tool for discovering and managing Claude Code configuration files and slash commands with a beautiful terminal UI.

[`cchistory`](https://github.com/eckardt/cchistory) &nbsp; by &nbsp; [eckardt](https://github.com/eckardt)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Like the shell history command but for your Claude Code sessions. Easily list all Bash or "Bash-mode" (`!`) commands Claude Code ran in a session for reference.

[`cclogviewer`](https://github.com/Brads3290/cclogviewer) &nbsp; by &nbsp; [Brad S.](https://github.com/Brads3290)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
A humble but handy utility for viewing Claude Code `.jsonl` conversation files in a pretty HTML UI.

[`Claude Code Templates`](https://github.com/davila7/claude-code-templates) &nbsp; by &nbsp; [Daniel Avila](https://github.com/davila7)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Incredibly awesome collection of resources from every category in this list, presented with a neatly polished UI, great features like usage dashboard, analytics, and everything from slash commands to hooks to agents. An awesome companion for this awesome list.

[`Claude Composer`](https://github.com/possibilities/claude-composer) &nbsp; by &nbsp; [Mike Bannister](https://github.com/possibilities)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;Unlicense  
A tool that adds small enhancements to Claude Code.

[`Claude Hub`](https://github.com/claude-did-this/claude-hub) &nbsp; by &nbsp; [Claude Did This](https://github.com/claude-did-this)    
A webhook service that connects Claude Code to GitHub repositories, enabling AI-powered code assistance directly through pull requests and issues. This integration allows Claude to analyze repositories, answer technical questions, and help developers understand and improve their codebase through simple @mentions.

[`claude-code-tools`](https://github.com/pchalasani/claude-code-tools) &nbsp; by &nbsp; [Prasad Chalasani](https://github.com/pchalasani)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
A collection of awesome tools, including tmux integrations, better session management, hooks that enhance security - a really well-done set of Claude Code enhancers, especially for tmux users.

[`claudekit`](https://github.com/carlrannaberg/claudekit) &nbsp; by &nbsp; [Carl Rannaberg](https://github.com/carlrannaberg)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Impressive CLI toolkit providing auto-save checkpointing, code quality hooks, specification generation and execution, and 20+ specialized subagents including oracle (gpt-5), code-reviewer (6-aspect deep analysis), ai-sdk-expert (Vercel AI SDK), typescript-expert and many more for Claude Code workflows.

[`Container Use`](https://github.com/dagger/container-use) &nbsp; by &nbsp; [dagger](https://github.com/dagger)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;Apache-2.0  
Development environments for coding agents. Enable multiple agents to work safely and independently with your preferred stack.

[`tweakcc`](https://github.com/Piebald-AI/tweakcc) &nbsp; by &nbsp; [Piebald-AI](https://github.com/Piebald-AI)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Command-line tool to customize your Claude Code styling.


### IDE Integrations

[`Claude Code Chat`](https://marketplace.visualstudio.com/items?itemName=AndrePimenta.claude-code-chat) &nbsp; by &nbsp; [andrepimenta](https://github.com/andrepimenta)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;&copy;  
An elegant and user-friendly Claude Code chat interface for VS Code.

[`claude-code-ide.el`](https://github.com/manzaltu/claude-code-ide.el) &nbsp; by &nbsp; [manzaltu](https://github.com/manzaltu)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;GPL-3.0  
claude-code-ide.el integrates Claude Code with Emacs, like Anthropic’s VS Code/IntelliJ extensions. It shows ediff-based code suggestions, pulls LSP/flymake/flycheck diagnostics, and tracks buffer context. It adds an extensible MCP tool support for symbol refs/defs, project metadata, and tree-sitter AST queries.

[`claude-code.el`](https://github.com/stevemolitor/claude-code.el) &nbsp; by &nbsp; [stevemolitor](https://github.com/stevemolitor)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;Apache-2.0  
An Emacs interface for Claude Code CLI.

[`claude-code.nvim`](https://github.com/greggh/claude-code.nvim) &nbsp; by &nbsp; [greggh](https://github.com/greggh)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
A seamless integration between Claude Code AI assistant and Neovim.

[`crystal`](https://github.com/stravu/crystal) &nbsp; by &nbsp; [stravu](https://github.com/stravu)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
A full-fledged desktop application for orchestrating, monitoring, and interacting with Claude Code agents.


### Usage Monitors

[`CC Usage`](https://github.com/ryoppippi/ccusage) &nbsp; by &nbsp; [ryoppippi](https://github.com/ryoppippi)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Handy CLI tool for managing and analyzing Claude Code usage, based on analyzing local Claude Code logs. Presents a nice dashboard regarding cost information, token consumption, etc.

[`ccflare`](https://github.com/snipeship/ccflare) &nbsp; by &nbsp; [snipeship](https://github.com/snipeship)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Claude Code usage dashboard with a web-UI that would put Tableau to shame. Thoroughly comprehensive metrics, frictionless setup, detailed logging, really really nice UI.

[`Claude Code Usage Monitor`](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor) &nbsp; by &nbsp; [Maciek-roboblog](https://github.com/Maciek-roboblog)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
A real-time terminal-based tool for monitoring Claude Code token usage. It shows live token consumption, burn rate, and predictions for token depletion. Features include visual progress bars, session-aware analytics, and support for multiple subscription plans.

[`viberank`](https://github.com/sculptdotfun/viberank) &nbsp; by &nbsp; [nikshepsvn](https://github.com/nikshepsvn)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
A community-driven leaderboard tool that enables developers to visualize, track, and compete based on their Claude Code usage statistics. It features robust data analytics, GitHub OAuth, data validation, and user-friendly CLI/web submission methods.


### Orchestrators

[`Claude Code Flow`](https://github.com/ruvnet/claude-code-flow) &nbsp; by &nbsp; [ruvnet](https://github.com/ruvnet)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
This mode serves as a code-first orchestration layer, enabling Claude to write, edit, test, and optimize code autonomously across recursive agent cycles.

[`Claude Squad`](https://github.com/smtg-ai/claude-squad) &nbsp; by &nbsp; [smtg-ai](https://github.com/smtg-ai)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;AGPL-3.0  
Claude Squad is a terminal app that manages multiple Claude Code, Codex (and other local agents including Aider) in separate workspaces, allowing you to work on multiple tasks simultaneously.

[`Claude Swarm`](https://github.com/parruda/claude-swarm) &nbsp; by &nbsp; [parruda](https://github.com/parruda)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Launch Claude Code session that is connected to a swarm of Claude Code Agents.

[`Claude Task Master`](https://github.com/eyaltoledano/claude-task-master) &nbsp; by &nbsp; [eyaltoledano](https://github.com/eyaltoledano)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;NOASSERTION  
A task management system for AI-driven development with Claude, designed to work seamlessly with Cursor AI.

[`Claude Task Runner`](https://github.com/grahama1970/claude-task-runner) &nbsp; by &nbsp; [grahama1970](https://github.com/grahama1970)    
A specialized tool to manage context isolation and focused task execution with Claude Code, solving the critical challenge of context length limitations and task focus when working with Claude on complex, multi-step projects.

[`Happy Coder`](https://github.com/slopus/happy) &nbsp; by &nbsp; [GrocerPublishAgent](https://peoplesgrocers.com/en/projects)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Spawn and control multiple Claude Codes in parallel from your phone or desktop. Happy Coder runs Claude Code on your hardware, sends push notifications when Claude needs more input or permission, and costs nothing.

[`TSK - AI Agent Task Manager and Sandbox`](https://github.com/dtormoen/tsk) &nbsp; by &nbsp; [dtormoen](https://github.com/dtormoen)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
A Rust CLI tool that lets you delegate development tasks to AI agents running in sandboxed Docker environments. Multiple agents work in parallel, returning git branches for human review.

<br>

## Statusline 📊

> **Statusline** configurations and customizations for Claude Code's status bar functionality

[`ccstatusline`](https://github.com/sirmalloc/ccstatusline) &nbsp; by &nbsp; [sirmalloc](https://github.com/sirmalloc)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
A highly customizable status line formatter for Claude Code CLI that displays model info, git branch, token usage, and other metrics in your terminal.

[`claude-powerline`](https://github.com/Owloops/claude-powerline) &nbsp; by &nbsp; [Owloops](https://github.com/Owloops)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
A vim-style powerline statusline for Claude Code with real-time usage tracking, git integration, custom themes, and more

<br>

## Hooks 🪝

> **Hooks** are a brand new API for Claude Code that allows users to activate commands and run scripts at different points in Claude's agentic lifecycle.

**[Experimental]** - The resources listed in this section have not been fully vetted and may not work as expected, given the bleeding-edge nature of Claude Code hooks. Nevertheless, I wished to include them at least as a source of inspiration and to explore this unknown terrain. YMMV!

[`CC Notify`](https://github.com/dazuiba/CCNotify) &nbsp; by &nbsp; [dazuiba](https://github.com/dazuiba)    
CCNotify provides desktop notifications for Claude Code, alerting you to input needs or task completion, with one-click jumps back to VS Code and task duration display.

[`cchooks`](https://github.com/GowayLee/cchooks) &nbsp; by &nbsp; [GowayLee](https://github.com/GowayLee)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
A lightweight Python SDK with a clean API and good documentation; simplifies the process of writing hooks and integrating them into your codebase, providing a nice abstraction over the JSON configuration files.

[`claude-code-hooks-sdk`](https://github.com/beyondcode/claude-hooks-sdk) &nbsp; by &nbsp; [beyondcode](https://github.com/beyondcode)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
A Laravel-inspired PHP SDK for building Claude Code hook responses with a clean, fluent API. This SDK makes it easy to create structured JSON responses for Claude Code hooks using an expressive, chainable interface.

[`claude-hooks`](https://github.com/johnlindquist/claude-hooks) &nbsp; by &nbsp; [John Lindquist](https://github.com/johnlindquist)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
A TypeScript-based system for configuring and customizing Claude Code hooks with a powerful and flexible interface.

[`Linting, testing, and notifications (in go)`](https://github.com/Veraticus/nix-config/tree/main/home-manager/claude-code/hooks) &nbsp; by &nbsp; [Josh Symonds](https://github.com/Veraticus)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Nice set of hooks for enforcing code quality (linting, testing, notifications), with a nice configuration setup as well.

[`TDD Guard`](https://github.com/nizos/tdd-guard) &nbsp; by &nbsp; [Nizar Selander](https://github.com/nizos)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
A hooks-driven system that monitors file operations in real-time and blocks changes that violate TDD principles.

[`TypeScript Quality Hooks`](https://github.com/bartolli/claude-code-typescript-hooks) &nbsp; by &nbsp; [bartolli](https://github.com/bartolli)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Quality check hook for Node.js TypeScript projects with TypeScript compilation. ESLint auto-fixing, and Prettier formatting. Uses SHA256 config caching for <5ms validation performance during real-time editing.

<br>

## Slash-Commands 🔪

### Version Control & Git

[`/analyze-issue`](https://github.com/jerseycheese/Narraitor/blob/feature/issue-227-ai-suggestions/.claude/commands/analyze-issue.md) &nbsp; by &nbsp; [jerseycheese](https://github.com/jerseycheese)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Fetches GitHub issue details to create comprehensive implementation specifications, analyzing requirements and planning structured approach with clear implementation steps.

[`/bug-fix`](https://github.com/danielscholl/mvn-mcp-server/blob/main/.claude/commands/bug-fix.md) &nbsp; by &nbsp; [danielscholl](https://github.com/danielscholl)    
Streamlines bug fixing by creating a GitHub issue first, then a feature branch for implementing and thoroughly testing the solution before merging.

[`/commit`](https://github.com/evmts/tevm-monorepo/blob/main/.claude/commands/commit.md) &nbsp; by &nbsp; [evmts](https://github.com/evmts)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Creates git commits using conventional commit format with appropriate emojis, following project standards and creating descriptive messages that explain the purpose of changes.

[`/commit-fast`](https://github.com/steadycursor/steadystart/blob/main/.claude/commands/2-commit-fast.md) &nbsp; by &nbsp; [steadycursor](https://github.com/steadycursor)    
Automates git commit process by selecting the first suggested message, generating structured commits with consistent formatting while skipping manual confirmation and removing Claude co-Contributorship footer

[`/create-pr`](https://github.com/toyamarinyon/giselle/blob/main/.claude/commands/create-pr.md) &nbsp; by &nbsp; [toyamarinyon](https://github.com/toyamarinyon)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;Apache-2.0  
Streamlines pull request creation by handling the entire workflow: creating a new branch, committing changes, formatting modified files with Biome, and submitting the PR.

[`/create-pull-request`](https://github.com/liam-hq/liam/blob/main/.claude/commands/create-pull-request.md) &nbsp; by &nbsp; [liam-hq](https://github.com/liam-hq)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;Apache-2.0  
Provides comprehensive PR creation guidance with GitHub CLI, enforcing title conventions, following template structure, and offering concrete command examples with best practices.

[`/create-worktrees`](https://github.com/evmts/tevm-monorepo/blob/main/.claude/commands/create-worktrees.md) &nbsp; by &nbsp; [evmts](https://github.com/evmts)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Creates git worktrees for all open PRs or specific branches, handling branches with slashes, cleaning up stale worktrees, and supporting custom branch creation for development.

[`/fix-github-issue`](https://github.com/jeremymailen/kotlinter-gradle/blob/master/.claude/commands/fix-github-issue.md) &nbsp; by &nbsp; [jeremymailen](https://github.com/jeremymailen)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;Apache-2.0  
Analyzes and fixes GitHub issues using a structured approach with GitHub CLI for issue details, implementing necessary code changes, running tests, and creating proper commit messages.

[`/fix-issue`](https://github.com/metabase/metabase/blob/master/.claude/commands/fix-issue.md) &nbsp; by &nbsp; [metabase](https://github.com/metabase)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;NOASSERTION  
Addresses GitHub issues by taking issue number as parameter, analyzing context, implementing solution, and testing/validating the fix for proper integration.

[`/fix-pr`](https://github.com/metabase/metabase/blob/master/.claude/commands/fix-pr.md) &nbsp; by &nbsp; [metabase](https://github.com/metabase)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;NOASSERTION  
Fetches and fixes unresolved PR comments by automatically retrieving feedback, addressing reviewer concerns, making targeted code improvements, and streamlining the review process.

[`/husky`](https://github.com/evmts/tevm-monorepo/blob/main/.claude/commands/husky.md) &nbsp; by &nbsp; [evmts](https://github.com/evmts)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Sets up and manages Husky Git hooks by configuring pre-commit hooks, establishing commit message standards, integrating with linting tools, and ensuring code quality on commits.

[`/pr-review`](https://github.com/arkavo-org/opentdf-rs/blob/main/.claude/commands/pr-review.md) &nbsp; by &nbsp; [arkavo-org](https://github.com/arkavo-org)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Reviews pull request changes to provide feedback, check for issues, and suggest improvements before merging into the main codebase.

[`/update-branch-name`](https://github.com/giselles-ai/giselle/blob/main/.claude/commands/update-branch-name.md) &nbsp; by &nbsp; [giselles-ai](https://github.com/giselles-ai)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;Apache-2.0  
Updates branch names with proper prefixes and formats, enforcing naming conventions, supporting semantic prefixes, and managing remote branch updates.


### Code Analysis & Testing

[`/check`](https://github.com/rygwdn/slack-tools/blob/main/.claude/commands/check.md) &nbsp; by &nbsp; [rygwdn](https://github.com/rygwdn)    
Performs comprehensive code quality and security checks, featuring static analysis integration, security vulnerability scanning, code style enforcement, and detailed reporting.

[`/clean`](https://github.com/Graphlet-AI/eridu/blob/main/.claude/commands/clean.md) &nbsp; by &nbsp; [Graphlet-AI](https://github.com/Graphlet-AI)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;Apache-2.0  
Addresses code formatting and quality issues by fixing black formatting problems, organizing imports with isort, resolving flake8 linting issues, and correcting mypy type errors.

[`/code_analysis`](https://github.com/kingler/n8n_agent/blob/main/.claude/commands/code_analysis.md) &nbsp; by &nbsp; [kingler](https://github.com/kingler)    
Provides a menu of advanced code analysis commands for deep inspection, including knowledge graph generation, optimization suggestions, and quality evaluation.

[`/optimize`](https://github.com/to4iki/ai-project-rules/blob/main/.claude/commands/optimize.md) &nbsp; by &nbsp; [to4iki](https://github.com/to4iki)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Analyzes code performance to identify bottlenecks, proposing concrete optimizations with implementation guidance for improved application performance.

[`/repro-issue`](https://github.com/rzykov/metabase/blob/master/.claude/commands/repro-issue.md) &nbsp; by &nbsp; [rzykov](https://github.com/rzykov)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;NOASSERTION  
Creates reproducible test cases for GitHub issues, ensuring tests fail reliably and documenting clear reproduction steps for developers.

[`/tdd`](https://github.com/zscott/pane/blob/main/.claude/commands/tdd.md) &nbsp; by &nbsp; [zscott](https://github.com/zscott)    
Guides development using Test-Driven Development principles, enforcing Red-Green-Refactor discipline, integrating with git workflow, and managing PR creation.

[`/tdd-implement`](https://github.com/jerseycheese/Narraitor/blob/feature/issue-227-ai-suggestions/.claude/commands/tdd-implement.md) &nbsp; by &nbsp; [jerseycheese](https://github.com/jerseycheese)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Implements Test-Driven Development by analyzing feature requirements, creating tests first (red), implementing minimal passing code (green), and refactoring while maintaining tests.


### Context Loading & Priming

[`/context-prime`](https://github.com/elizaOS/elizaos.github.io/blob/main/.claude/commands/context-prime.md) &nbsp; by &nbsp; [elizaOS](https://github.com/elizaOS)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Primes Claude with comprehensive project understanding by loading repository structure, setting development context, establishing project goals, and defining collaboration parameters.

[`/initref`](https://github.com/okuvshynov/cubestat/blob/main/.claude/commands/initref.md) &nbsp; by &nbsp; [okuvshynov](https://github.com/okuvshynov)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Initializes reference documentation structure with standard doc templates, API reference setup, documentation conventions, and placeholder content generation.

[`/load-llms-txt`](https://github.com/ethpandaops/xatu-data/blob/master/.claude/commands/load-llms-txt.md) &nbsp; by &nbsp; [ethpandaops](https://github.com/ethpandaops)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Loads LLM configuration files to context, importing specific terminology, model configurations, and establishing baseline terminology for AI discussions.

[`/load_coo_context`](https://github.com/Mjvolk3/torchcell/blob/main/.claude/commands/load_coo_context.md) &nbsp; by &nbsp; [Mjvolk3](https://github.com/Mjvolk3)    
References specific files for sparse matrix operations, explains transform usage, compares with previous approaches, and sets data formatting context for development.

[`/load_dango_pipeline`](https://github.com/Mjvolk3/torchcell/blob/main/.claude/commands/load_dango_pipeline.md) &nbsp; by &nbsp; [Mjvolk3](https://github.com/Mjvolk3)    
Sets context for model training by referencing pipeline files, establishing working context, and preparing for pipeline work with relevant documentation.

[`/prime`](https://github.com/yzyydev/AI-Engineering-Structure/blob/main/.claude/commands/prime.md) &nbsp; by &nbsp; [yzyydev](https://github.com/yzyydev)    
Sets up initial project context by viewing directory structure and reading key files, creating standardized context with directory visualization and key documentation focus.

[`/rsi`](https://github.com/ddisisto/si/blob/main/.claude/commands/rsi.md) &nbsp; by &nbsp; [ddisisto](https://github.com/ddisisto)    
Reads all commands and key project files to optimize AI-assisted development by streamlining the process, loading command context, and setting up for better development workflow.


### Documentation & Changelogs

[`/add-to-changelog`](https://github.com/berrydev-ai/blockdoc-python/blob/main/.claude/commands/add-to-changelog.md) &nbsp; by &nbsp; [berrydev-ai](https://github.com/berrydev-ai)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Adds new entries to changelog files while maintaining format consistency, properly documenting changes, and following established project standards for version tracking.

[`/create-docs`](https://github.com/jerseycheese/Narraitor/blob/feature/issue-227-ai-suggestions/.claude/commands/create-docs.md) &nbsp; by &nbsp; [jerseycheese](https://github.com/jerseycheese)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Analyzes code structure and purpose to create comprehensive documentation detailing inputs/outputs, behavior, user interaction flows, and edge cases with error handling.

[`/docs`](https://github.com/slunsford/coffee-analytics/blob/main/.claude/commands/docs.md) &nbsp; by &nbsp; [slunsford](https://github.com/slunsford)    
Generates comprehensive documentation that follows project structure, documenting APIs and usage patterns with consistent formatting for better user understanding.

[`/explain-issue-fix`](https://github.com/hackdays-io/toban-contribution-viewer/blob/main/.claude/commands/explain-issue-fix.md) &nbsp; by &nbsp; [hackdays-io](https://github.com/hackdays-io)    
Documents solution approaches for GitHub issues, explaining technical decisions, detailing challenges overcome, and providing implementation context for better understanding.

[`/update-docs`](https://github.com/Consiliency/Flutter-Structurizr/blob/main/.claude/commands/update-docs.md) &nbsp; by &nbsp; [Consiliency](https://github.com/Consiliency)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Reviews current documentation status, updates implementation progress, reviews phase documents, and maintains documentation consistency across the project.


### CI / Deployment

[`/release`](https://github.com/kelp/webdown/blob/main/.claude/commands/release.md) &nbsp; by &nbsp; [kelp](https://github.com/kelp)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Manages software releases by updating changelogs, reviewing README changes, evaluating version increments, and documenting release changes for better version tracking.

[`/run-ci`](https://github.com/hackdays-io/toban-contribution-viewer/blob/main/.claude/commands/run-ci.md) &nbsp; by &nbsp; [hackdays-io](https://github.com/hackdays-io)    
Activates virtual environments, runs CI-compatible check scripts, iteratively fixes errors, and ensures all tests pass before completion.


### Project & Task Management

[`/create-command`](https://github.com/scopecraft/command/blob/main/.claude/commands/create-command.md) &nbsp; by &nbsp; [scopecraft](https://github.com/scopecraft)    
Guides Claude through creating new custom commands with proper structure by analyzing requirements, templating commands by category, enforcing command standards, and creating supporting documentation.

[`/create-jtbd`](https://github.com/taddyorg/inkverse/blob/main/.claude/commands/create-jtbd.md) &nbsp; by &nbsp; [taddyorg](https://github.com/taddyorg)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;AGPL-3.0  
Creates Jobs-to-be-Done frameworks that outline user needs with structured format, focusing on specific user problems and organizing by job categories for product development.

[`/create-prd`](https://github.com/taddyorg/inkverse/blob/main/.claude/commands/create-prd.md) &nbsp; by &nbsp; [taddyorg](https://github.com/taddyorg)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;AGPL-3.0  
Generates comprehensive product requirement documents outlining detailed specifications, requirements, and features following standardized document structure and format.

[`/create-prp`](https://github.com/Wirasm/claudecode-utils/blob/main/.claude/commands/create-prp.md) &nbsp; by &nbsp; [Wirasm](https://github.com/Wirasm)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Creates product requirement plans by reading PRP methodology, following template structure, creating comprehensive requirements, and structuring product definitions for development.

[`/do-issue`](https://github.com/jerseycheese/Narraitor/blob/feature/issue-227-ai-suggestions/.claude/commands/do-issue.md) &nbsp; by &nbsp; [jerseycheese](https://github.com/jerseycheese)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Implements GitHub issues with manual review points, following a structured approach with issue number parameter and offering alternative automated mode for efficiency.

[`/project_hello_w_name`](https://github.com/disler/just-prompt/blob/main/.claude/commands/project_hello_w_name.md) &nbsp; by &nbsp; [disler](https://github.com/disler)    
Creates customizable greeting components with name input, demonstrating argument passing, component reusability, state management, and user input handling.

[`/todo`](https://github.com/chrisleyva/todo-slash-command/blob/main/todo.md) &nbsp; by &nbsp; [chrisleyva](https://github.com/chrisleyva)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
A convenient command to quickly manage project todo items without leaving the Claude Code interface, featuring due dates, sorting, task prioritization, and comprehensive todo list management.


### Miscellaneous

[`/five`](https://github.com/TuckerTucker/tkr-portfolio/blob/main/.claude/commands/five.md) &nbsp; by &nbsp; [TuckerTucker](https://github.com/TuckerTucker)    
Applies the "five whys" methodology to perform root cause analysis, identify underlying issues, and create solution approaches for complex problems.

[`/fixing_go_in_graph`](https://github.com/Mjvolk3/torchcell/blob/main/.claude/commands/fixing_go_in_graph.md) &nbsp; by &nbsp; [Mjvolk3](https://github.com/Mjvolk3)    
Focuses on Gene Ontology annotation integration in graph databases, handling multiple data sources, addressing graph representation issues, and ensuring correct data incorporation.

[`/mermaid`](https://github.com/GaloyMoney/lana-bank/blob/main/.claude/commands/mermaid.md) &nbsp; by &nbsp; [GaloyMoney](https://github.com/GaloyMoney)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;NOASSERTION  
Generates Mermaid diagrams from SQL schema files, creating entity relationship diagrams with table properties, validating diagram compilation, and ensuring complete entity coverage.

[`/review_dcell_model`](https://github.com/Mjvolk3/torchcell/blob/main/.claude/commands/review_dcell_model.md) &nbsp; by &nbsp; [Mjvolk3](https://github.com/Mjvolk3)    
Reviews old Dcell implementation files, comparing with newer Dango model, noting changes over time, and analyzing refactoring approaches for better code organization.

[`/use-stepper`](https://github.com/zuplo/docs/blob/main/.claude/commands/use-stepper.md) &nbsp; by &nbsp; [zuplo](https://github.com/zuplo)    
Reformats documentation to use React Stepper component, transforming heading formats, applying proper indentation, and maintaining markdown compatibility with admonition formatting.

<br>

## CLAUDE.md Files 📂

> **`CLAUDE.md` files** are files that contain important guidelines and context-specfic information or instructions that help Claude Code to better understand your project and your coding standards

### Language-Specific

[`AI IntelliJ Plugin`](https://github.com/didalgolab/ai-intellij-plugin/blob/main/CLAUDE.md) &nbsp; by &nbsp; [didalgolab](https://github.com/didalgolab)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;Apache-2.0  
Provides comprehensive Gradle commands for IntelliJ plugin development with platform-specific coding patterns, detailed package structure guidelines, and clear internationalization standards.

[`AWS MCP Server`](https://github.com/alexei-led/aws-mcp-server/blob/main/CLAUDE.md) &nbsp; by &nbsp; [alexei-led](https://github.com/alexei-led)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Features multiple Python environment setup options with detailed code style guidelines, comprehensive error handling recommendations, and security considerations for AWS CLI interactions.

[`DroidconKotlin`](https://github.com/touchlab/DroidconKotlin/blob/main/CLAUDE.md) &nbsp; by &nbsp; [touchlab](https://github.com/touchlab)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;Apache-2.0  
Delivers comprehensive Gradle commands for cross-platform Kotlin Multiplatform development with clear module structure and practical guidance for dependency injection.

[`EDSL`](https://github.com/expectedparrot/edsl/blob/main/CLAUDE.md) &nbsp; by &nbsp; [expectedparrot](https://github.com/expectedparrot)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Offers detailed build and test commands with strict code style enforcement, comprehensive testing requirements, and standardized development workflow using Black and mypy.

[`Giselle`](https://github.com/giselles-ai/giselle/blob/main/CLAUDE.md) &nbsp; by &nbsp; [giselles-ai](https://github.com/giselles-ai)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;Apache-2.0  
Provides detailed build and test commands using pnpm and Vitest with strict code formatting requirements and comprehensive naming conventions for code consistency.

[`HASH`](https://github.com/hashintel/hash/blob/main/CLAUDE.md) &nbsp; by &nbsp; [hashintel](https://github.com/hashintel)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;NOASSERTION  
Features comprehensive repository structure breakdown with strong emphasis on coding standards, detailed Rust documentation guidelines, and systematic PR review process.

[`Inkline`](https://github.com/inkline/inkline/blob/main/CLAUDE.md) &nbsp; by &nbsp; [inkline](https://github.com/inkline)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;NOASSERTION  
Structures development workflow using pnpm with emphasis on TypeScript and Vue 3 Composition API, detailed component creation process, and comprehensive testing recommendations.

[`JSBeeb`](https://github.com/mattgodbolt/jsbeeb/blob/main/CLAUDE.md) &nbsp; by &nbsp; [mattgodbolt](https://github.com/mattgodbolt)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;GPL-3.0  
Provides development guide for JavaScript BBC Micro emulator with build and testing instructions, architecture documentation, and debugging workflows.

[`Lamoom Python`](https://github.com/LamoomAI/lamoom-python/blob/main/CLAUDE.md) &nbsp; by &nbsp; [LamoomAI](https://github.com/LamoomAI)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;Apache-2.0  
Serves as reference for production prompt engineering library with load balancing of AI Models, API documentation, and usage patterns with examples.

[`LangGraphJS`](https://github.com/langchain-ai/langgraphjs/blob/main/CLAUDE.md) &nbsp; by &nbsp; [langchain-ai](https://github.com/langchain-ai)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Offers comprehensive build and test commands with detailed TypeScript style guidelines, layered library architecture, and monorepo structure using yarn workspaces.

[`Metabase`](https://github.com/metabase/metabase/blob/master/CLAUDE.md) &nbsp; by &nbsp; [metabase](https://github.com/metabase)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;NOASSERTION  
Details workflow for REPL-driven development in Clojure/ClojureScript with emphasis on incremental development, testing, and step-by-step approach for feature implementation.

[`SG Cars Trends Backend`](https://github.com/sgcarstrends/backend/blob/main/CLAUDE.md) &nbsp; by &nbsp; [sgcarstrends](https://github.com/sgcarstrends)    
Provides comprehensive structure for TypeScript monorepo projects with detailed commands for development, testing, deployment, and AWS/Cloudflare integration.

[`SPy`](https://github.com/spylang/spy/blob/main/CLAUDE.md) &nbsp; by &nbsp; [spylang](https://github.com/spylang)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Enforces strict coding conventions with comprehensive testing guidelines, multiple code compilation options, and backend-specific test decorators for targeted filtering.

[`TPL`](https://github.com/KarpelesLab/tpl/blob/master/CLAUDE.md) &nbsp; by &nbsp; [KarpelesLab](https://github.com/KarpelesLab)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Details Go project conventions with comprehensive error handling recommendations, table-driven testing approach guidelines, and modernization suggestions for latest Go features.


### Domain-Specific

[`AVS Vibe Developer Guide`](https://github.com/Layr-Labs/avs-vibe-developer-guide/blob/master/CLAUDE.md) &nbsp; by &nbsp; [Layr-Labs](https://github.com/Layr-Labs)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Structures AI-assisted EigenLayer AVS development workflow with consistent naming conventions for prompt files and established terminology standards for blockchain concepts.

[`Comm`](https://github.com/CommE2E/comm/blob/master/CLAUDE.md) &nbsp; by &nbsp; [CommE2E](https://github.com/CommE2E)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;BSD-3-Clause  
Serves as a development reference for E2E-encrypted messaging applications with code organization architecture, security implementation details, and testing procedures.

[`Course Builder`](https://github.com/badass-courses/course-builder/blob/main/CLAUDE.md) &nbsp; by &nbsp; [badass-courses](https://github.com/badass-courses)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Enables real-time multiplayer capabilities for collaborative course creation with diverse tech stack integration and monorepo architecture using Turborepo.

[`Cursor Tools`](https://github.com/eastlondoner/cursor-tools/blob/main/CLAUDE.md) &nbsp; by &nbsp; [eastlondoner](https://github.com/eastlondoner)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Creates a versatile AI command interface supporting multiple providers and models with flexible command options and browser automation through "Stagehand" feature.

[`Guitar`](https://github.com/soramimi/Guitar/blob/master/CLAUDE.md) &nbsp; by &nbsp; [soramimi](https://github.com/soramimi)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;GPL-2.0  
Serves as development guide for Guitar Git GUI Client with build commands for various platforms, code style guidelines for contributing, and project structure explanation.

[`Network Chronicles`](https://github.com/Fimeg/NetworkChronicles/blob/legacy-v1/CLAUDE.md) &nbsp; by &nbsp; [Fimeg](https://github.com/Fimeg)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Presents detailed implementation plan for AI-driven game characters with technical specifications for LLM integration, character guidelines, and service discovery mechanics.

[`Note Companion`](https://github.com/different-ai/note-companion/blob/master/CLAUDE.md) &nbsp; by &nbsp; [different-ai](https://github.com/different-ai)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Provides detailed styling isolation techniques for Obsidian plugins using Tailwind with custom prefix to prevent style conflicts and practical troubleshooting steps.

[`Pareto Mac`](https://github.com/ParetoSecurity/pareto-mac/blob/main/CLAUDE.md) &nbsp; by &nbsp; [ParetoSecurity](https://github.com/ParetoSecurity)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;GPL-3.0  
Serves as development guide for Mac security audit tool with build instructions, contribution guidelines, testing procedures, and workflow documentation.

[`SteadyStart`](https://github.com/steadycursor/steadystart/blob/main/CLAUDE.md) &nbsp; by &nbsp; [steadycursor](https://github.com/steadycursor)    
Clear and direct instructives about style, permissions, Claude's "role", communications, and documentation of Claude Code sessions for other team members to stay abreast.


### Project Scaffolding & MCP

[`Basic Memory`](https://github.com/basicmachines-co/basic-memory/blob/main/CLAUDE.md) &nbsp; by &nbsp; [basicmachines-co](https://github.com/basicmachines-co)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;AGPL-3.0  
Presents an innovative AI-human collaboration framework with Model Context Protocol for bidirectional LLM-markdown communication and flexible knowledge structure for complex projects.

[`claude-code-mcp-enhanced`](https://github.com/grahama1970/claude-code-mcp-enhanced/blob/main/CLAUDE.md) &nbsp; by &nbsp; [grahama1970](https://github.com/grahama1970)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Provides detailed and emphatic instructions for Claude to follow as a coding agent, with testing guidance, code examples, and compliance checks.

[`Perplexity MCP`](https://github.com/Family-IT-Guy/perplexity-mcp/blob/main/CLAUDE.md) &nbsp; by &nbsp; [Family-IT-Guy](https://github.com/Family-IT-Guy)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;ISC  
Offers clear step-by-step installation instructions with multiple configuration options, detailed troubleshooting guidance, and concise architecture overview of the MCP protocol.

<br>

## Official Documentation 🏛️

> Links to some of Anthropic's terrific documentation and resources regarding Claude Code

<!--lint disable double-link-->

[`Anthropic Documentation`](https://docs.anthropic.com/en/docs/claude-code) &nbsp; by &nbsp; [Anthropic](https://github.com/anthropics)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;&copy;  
The official documentation for Claude Code, including installation instructions, usage guidelines, API references, tutorials, examples, loads of information that I won't list individually. Like Claude Code, the documentation is frequently updated.

[`Anthropic Quickstarts`](https://github.com/anthropics/anthropic-quickstarts/blob/main/CLAUDE.md) &nbsp; by &nbsp; [Anthropic](https://github.com/anthropics)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Offers comprehensive development guides for three distinct AI-powered demo projects with standardized workflows, strict code style guidelines, and containerization instructions.

[`Claude Code GitHub Actions`](https://github.com/anthropics/claude-code-action/tree/main/examples) &nbsp; by &nbsp; [Anthropic](https://github.com/anthropics)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Official GitHub Actions integration for Claude Code with examples and documentation for automating AI-powered workflows in CI/CD pipelines.


## Contributing 🌻

### 🚀 **[Submit a new resource here!](https://github.com/hesreallyhim/awesome-claude-code/issues/new?template=submit-resource.yml)**

It's easy! Just click the link above and fill out the form. No Git knowledge required - our automated system handles everything for you.

**We especially welcome:**

- Proven, effective resources that follow best practices and may even be in use in production
- Innovative, creative, or experimental workflows that push the boundaries of Claude Code's capabilities
- Additional libraries and tooling that are built on top of Claude Code
- Applications of Claude Code outside of the traditional "coding assistant" context (CI/CD, testing, documentation, dev-ops, etc.)

See [CONTRIBUTING.md](CONTRIBUTING.md) for the complete submission guide and review process.

For suggestions about the repository itself, please [open a general issue](https://github.com/hesreallyhim/awesome-claude-code/issues/new).

This project is released with a [Contributor Code of Conduct](code-of-conduct.md). By participating, you agree to abide by its terms.

### A note about licenses

Because simply listing a hyperlink does not qualify as redistribution, the license of the original source is not relevant to its inclusion. However, for posterity and convenience, we do host copies of all resources whose license permits it. Therefore, please include information about the resource's license. Additionally, take note: _if you do not include a LICENSE in your GitHub repo, then by default it is fully copyrighted and redistribution is not allowed_. So, if you are intending to make an open source project, it's critical to pick from one of the many available open source licenses. This is just a reminder that without a LICENSE, your project is not open source (it's merely source-code-available) - it may of course still be included on this list, but this notice is to inform readers about the default rules regarding GitHub and LICENSE files. See [here](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository) for more details.
