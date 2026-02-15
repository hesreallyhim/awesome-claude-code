<!-- GENERATED FILE: do not edit directly -->
<h3 align="center">Pick Your Style:</h3>
<p align="center">
<a href="../"><img src="../assets/badge-style-awesome.svg" alt="Awesome" height="28" style="border: 2px solid #cc3366; border-radius: 4px;"></a>
<a href="README_EXTRA.md"><img src="../assets/badge-style-extra.svg" alt="Extra" height="28"></a>
<a href="README_CLASSIC.md"><img src="../assets/badge-style-classic.svg" alt="Classic" height="28"></a>
<a href="README_FLAT_ALL_AZ.md"><img src="../assets/badge-style-flat.svg" alt="Flat" height="28"></a>
</p>

<p align="center">
  <picture>
    <img src="../assets/awesome-claude-code-social-clawd-2.png" alt="Awesome Claude Code" width="600">
  </picture>
</p>

# Awesome Claude Code

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> A curated list of slash-commands, CLAUDE.md files, CLI tools, and other resources for enhancing your [Claude Code](https://docs.anthropic.com/en/docs/claude-code) workflow.

Claude Code is a CLI-based coding assistant from [Anthropic](https://www.anthropic.com/) that you can access in your terminal or IDE. This list helps the community share knowledge and best practices.

<div align="center">

<img src="../assets/repo-ticker-awesome.svg" alt="Featured Claude Code Projects" width="100%">

</div>



## Latest Additions

- [claude-rules-doctor](https://github.com/nulone/claude-rules-doctor) by [nulone](https://github.com/nulone) - CLI that detects dead `.claude/rules/` files by checking if `paths:` globs actually match files in your repo. Catches silent rule failures where renamed directories or typos in glob patterns cause rules to never apply. Features CI mode (exit 1 on dead rules), JSON output, and verbose mode showing matched files.
- [ClaudeCTX](https://github.com/foxj77/claudectx) by [John Fox](https://github.com/foxj77) - claudectx lets you switch your entire Claude Code configuration with a single command.
- [AgentSys](https://github.com/avifenesh/agentsys) by [avifenesh](https://github.com/avifenesh) - Workflow automation system for Claude with a group of useful plugins, agents, and skills. Automates task-to-production workflows, PR management, code cleanup, performance investigation, drift detection, and multi-agent code review. Includes [agnix](https://github.com/avifenesh/agnix) for linting agent configurations. Built on thousands of lines of code with thousands of tests. Uses deterministic detection (regex, AST) with LLM judgment for efficiency. Used on many production systems.
- [Auto-Claude](https://github.com/AndyMik90/Auto-Claude) by [AndyMik90](https://github.com/AndyMik90) - Autonomous multi-agent coding framework for Claude Code (Claude Agent SDK) that integrates the full SDLC - "plans, builds, and validates software for you". Features a slick kanban-style UI and a well-designed but not over-engineered agent orchestration system.
- [Claude Code Agents](https://github.com/undeadlist/claude-code-agents) by [Paul - UndeadList](https://github.com/undeadlist) - Comprehensive E2E development workflow with helpful Claude Code subagent prompts for solo devs. Run multiple auditors in parallel, automate fix cycles with micro-checkpoint protocols, and do browser-based QA. Includes strict protocols to prevent AI going rogue.
- [Claude Code Ultimate Guide](https://github.com/FlorianBruniaux/claude-code-ultimate-guide) by [Florian BRUNIAUX](https://www.linkedin.com/in/florian-bruniaux-43408b83/) - A tremendous feat of documentation, this guide covers Claude Code from beginner to power user, with production-ready templates for Claude Code features, guides on agentic workflows, and a lot of great learning materials, including quizzes and a handy "cheatsheet". Whether it's the "ultimate" guide to Claude Code will be up to the reader, but a valuable resource nonetheless (as with all documentation sites, make sure it's up to date before you bet the farm).
- [Book Factory](https://github.com/robertguss/claude-skills) by [Robert Guss](https://github.com/robertguss) - A comprehensive pipeline of Skills that replicates traditional publishing infrastructure for nonfiction book creation using specialized Claude skills.


## Contents

- [Agent Skills 🤖](#agent-skills-)
  - [General](#general)
- [Workflows & Knowledge Guides 🧠](#workflows--knowledge-guides-)
  - [General](#general-1)
  - [Ralph Wiggum](#ralph-wiggum)
- [Tooling 🧰](#tooling-)
  - [General](#general-2)
  - [IDE Integrations](#ide-integrations)
  - [Usage Monitors](#usage-monitors)
  - [Orchestrators](#orchestrators)
  - [Config Managers](#config-managers)
- [Status Lines 📊](#status-lines-)
  - [General](#general-3)
- [Hooks 🪝](#hooks-)
  - [General](#general-4)
- [Slash-Commands 🔪](#slash-commands-)
  - [General](#general-5)
  - [Version Control & Git](#version-control--git)
  - [Code Analysis & Testing](#code-analysis--testing)
  - [Context Loading & Priming](#context-loading--priming)
  - [Documentation & Changelogs](#documentation--changelogs)
  - [CI / Deployment](#ci--deployment)
  - [Project & Task Management](#project--task-management)
  - [Miscellaneous](#miscellaneous)
- [CLAUDE.md Files 📂](#claudemd-files-)
  - [Language-Specific](#language-specific)
  - [Domain-Specific](#domain-specific)
  - [Project Scaffolding & MCP](#project-scaffolding--mcp)
- [Alternative Clients 📱](#alternative-clients-)
  - [General](#general-6)
- [Official Documentation 🏛️](#official-documentation-%EF%B8%8F)
  - [General](#general-7)

## Agent Skills 🤖

> Agent skills are model-controlled configurations (files, scripts, resources, etc.) that enable Claude Code to perform specialized tasks requiring specific knowledge or capabilities.

### General

- [AgentSys](https://github.com/avifenesh/agentsys) by [avifenesh](https://github.com/avifenesh) - Workflow automation system for Claude with a group of useful plugins, agents, and skills. Automates task-to-production workflows, PR management, code cleanup, performance investigation, drift detection, and multi-agent code review. Includes [agnix](https://github.com/avifenesh/agnix) for linting agent configurations. Built on thousands of lines of code with thousands of tests. Uses deterministic detection (regex, AST) with LLM judgment for efficiency. Used on many production systems.
- [AI Agent, AI Spy](https://youtu.be/0ANECpNdt-4) by [Whittaker & Tiwari](https://signalfoundation.org/) - Members from the Signal Foundation with some really great tips and tricks on how to turn your operating system into an instrument of total surveillance, and why some companies are doing this really awesome thing. [warning: YouTube link].
- [Book Factory](https://github.com/robertguss/claude-skills) by [Robert Guss](https://github.com/robertguss) - A comprehensive pipeline of Skills that replicates traditional publishing infrastructure for nonfiction book creation using specialized Claude skills.
- [cc-devops-skills](https://github.com/akin-ozer/cc-devops-skills) by [akin-ozer](https://github.com/akin-ozer) - Immensely detailed set of skills for DevOps Engineers (or anyone who has to deploy code, really). Works with validations, generators, shell scripts and CLI tools to create high quality IaC code for about any platform you've ever struggled painfully to work with. Worth downloading even just as a source of documentation.
- [Claude Code Agents](https://github.com/undeadlist/claude-code-agents) by [Paul - UndeadList](https://github.com/undeadlist) - Comprehensive E2E development workflow with helpful Claude Code subagent prompts for solo devs. Run multiple auditors in parallel, automate fix cycles with micro-checkpoint protocols, and do browser-based QA. Includes strict protocols to prevent AI going rogue.
- [Claude Codex Settings](https://github.com/fcakyon/claude-codex-settings) by [fatih akyon](https://github.com/fcakyon) - A well-organized, well-written set of plugins covering core developer activities, such as working with common cloud platforms like GitHub, Azure, MongoDB, and popular services such as Tavily, Playwright, and more. Clear, not overly-opinionated, and compatible with a few other providers.
- [Claude Mountaineering Skills](https://github.com/dreamiurg/claude-mountaineering-skills) by [Dmytro Gaivoronsky](https://github.com/dreamiurg) - Claude Code skill that automates mountain route research for North American peaks. Aggregates data from 10+ mountaineering sources like Mountaineers.org, PeakBagger.com and SummitPost.com to generate detailed route beta reports with weather, avalanche conditions, and trip reports.
- [Codex Skill](https://github.com/skills-directory/skill-codex) by [klaudworks](https://github.com/klaudworks) - Enables users to prompt codex from claude code. Unlike the raw codex mcp server, this skill infers parameters such as model, reasoning effort, sandboxing from your prompt or asks you to specify them. It also simplifies continuing prior codex sessions so that codex can continue with the prior context.
- [Compound Engineering Plugin](https://github.com/EveryInc/compound-engineering-plugin) by [EveryInc](https://github.com/EveryInc) - A very pragmatic set of well-designed agents, skills, and commands, built around a discipline of turning past mistakes and errors into lessons and opportunities for future growth and improvement. Good documentation.
- [Context Engineering Kit](https://github.com/NeoLabHQ/context-engineering-kit) by [Vlad Goncharov](https://github.com/LeoVS09) - Hand-crafted collection of advanced context engineering techniques and patterns with minimal token footprint focused on improving agent result quality.
- [Everything Claude Code](https://github.com/affaan-m/everything-claude-code) by [Affaan Mustafa](https://github.com/affaan-m/) - Top-notch, well-written resources covering "just about everything" from core engineering domains. What's nice about this "everything-" store is most of the resources have significant standalone value and unlike some all-encompassing frameworks, although you can opt in to the author's own specific workflow patterns if you choose, the individual resources offer exemplary patterns in (just about) every Claude Code feature you can find (apologies to the Output Styles devotees).
- [Fullstack Dev Skills](https://github.com/jeffallan/claude-skills) by [jeffallan](https://github.com/jeffallan) - A comprehensive Claude Code plugin with 65 specialized skills covering full-stack development across a wide range of specific frameworks. Features 9 project workflow commands for Jira/Confluence integration and, notably, an interesting approach to context engineering via a  `/common-ground` command that surfaces Claude's hidden assumptions about your project. This is a smart thing to do.
- [read-only-postgres](https://github.com/jawwadfirdousi/agent-skills) by [jawwadfirdousi](https://github.com/jawwadfirdousi) - Read-only PostgreSQL query skill for Claude Code. Executes SELECT/SHOW/EXPLAIN/WITH queries across configured databases with strict validation, timeouts, and row limits. Supports multiple connections with descriptions for database selection.
- [Superpowers](https://github.com/obra/superpowers) by [Jesse Vincent](https://github.com/obra) - A strong bundle of core competencies for software engineering, with good coverage of a large portion of the SDLC - from planning, reviewing, testing, debugging... Well written, well organized, and adaptable. The author refers to them as "superpowers", but many of them are just consolidating engineering best practices - which sometimes does feel like a superpower when working with Claude Code.
- [Trail of Bits Security Skills](https://github.com/trailofbits/skills) by [Trail of Bits](https://github.com/trailofbits) - A very professional collection of over a dozen security-focused skills for code auditing and vulnerability detection. Includes skills for static analysis with CodeQL and Semgrep, variant analysis across codebases, fix verification, and differential code review.
- [TÂCHES Claude Code Resources](https://github.com/glittercowboy/taches-cc-resources) by [TÂCHES](https://github.com/glittercowboy) - A well-balanced, "down-to-Earth" set of sub agents, skills, and commands,  that are well-organized, easy to read, and a healthy focus on "meta"-skills/agents, like "skill-auditor", hook creation, etc. - the kind of things you can adapt to your workflow, and not the other way around.
- [Web Assets Generator Skill](https://github.com/alonw0/web-asset-generator) by [Alon Wolenitz](https://github.com/alonw0) - Easily generate web assets from Claude Code including favicons, app icons (PWA), and social media meta images (Open Graph) for Facebook, Twitter, WhatsApp, and LinkedIn. Handles image resizing, text-to-image generation, emojis, and provides proper HTML meta tags.

<br>

## Workflows & Knowledge Guides 🧠

> A workflow is a tightly coupled set of Claude Code-native resources that facilitate specific projects

### General

- [AB Method](https://github.com/ayoubben18/ab-method) by [Ayoub Bensalah](https://github.com/ayoubben18) - A principled, spec-driven workflow that transforms large problems into focused, incremental missions using Claude Code's specialized sub agents. Includes slash-commands, sub agents, and specialized workflows designed for specific parts of the SDLC.
- [Agentic Workflow Patterns](https://github.com/ThibautMelen/agentic-workflow-patterns) by [ThibautMelen](https://github.com/ThibautMelen) - A comprehensive and well-documented collection of agentic patterns from Anthropic docs, with colorful Mermaid diagrams and code examples for each pattern. Covers Subagent Orchestration, Progressive Skills, Parallel Tool Calling, Master-Clone Architecture, Wizard Workflows, and more. Also compatible with other providers.
- [Blogging Platform Instructions](https://github.com/cloudartisan/cloudartisan.github.io/tree/main/.claude/commands) by [cloudartisan](https://github.com/cloudartisan) - Provides a well-structured set of commands for publishing and maintaining a blogging platform, including commands for creating posts, managing categories, and handling media files.
- [Claude Code Documentation Mirror](https://github.com/ericbuess/claude-code-docs) by [Eric Buess](https://github.com/ericbuess) - A mirror of the Anthropic &copy; PBC documentation pages for Claude Code, updated every few hours. Can come in handy when trying to stay on top of the ever-expanding feature-set of Dr. Claw D. Code, Ph.D.
- [Claude Code Handbook](https://nikiforovall.blog/claude-code-rules/) by [nikiforovall](https://github.com/nikiforovall) - Collection of best practices, tips, and techniques for Claude Code development workflows, enhanced with distributable plugins.
- [Claude Code Infrastructure Showcase](https://github.com/diet103/claude-code-infrastructure-showcase) by [diet103](https://github.com/diet103) - A remarkably innovative approach to working with Skills, the centerpiece of which being a technique that leverages hooks to ensure that Claude intelligently selects and activates the appropriate Skill given the current context. Well-documented and adaptable to different projects and workflows.
- [Claude Code PM](https://github.com/automazeio/ccpm) by [Ran Aroussi](https://github.com/ranaroussi) - Really comprehensive and feature-packed project-management workflow for Claude Code. Numerous specialized agents, slash-commands, and strong documentation.
- [Claude Code Repos Index](https://github.com/danielrosehill/Claude-Code-Repos-Index) by [Daniel Rosehill](https://github.com/danielrosehill) - This is either the work of a prolific genius, or a very clever bot (or both), although it hardly matters because the quality is so good - an index of 75+ Claude Code repositories published by the author - and I'm not talking about slop. CMS, system design, deep research, IoT, agentic workflows, server management, personal health... If you spot the lie, let me know, otherwise please check these out.
- [Claude Code System Prompts](https://github.com/Piebald-AI/claude-code-system-prompts) by [Piebald AI](https://github.com/Piebald-AI) - All parts of Claude Code's system prompt, including builtin tool descriptions, sub agent prompts (Plan/Explore/Task), utility prompts (CLAUDE.md, compact, Bash cmd, security review, agent creation, etc.). Updated for each Claude Code version.
- [Claude Code Tips](https://github.com/ykdojo/claude-code-tips) by [ykdojo](https://github.com/ykdojo) - A nice variety of 35+ brief but information-dense Claude Code tips covering voice input, system prompt patching, container workflows for risky tasks, conversation cloning(!), multi-model orchestration with Gemini CLI, and plenty more. Nice demos, working scripts, a plugin, I'd say this probably has a little something for everyone.
- [Claude Code Ultimate Guide](https://github.com/FlorianBruniaux/claude-code-ultimate-guide) by [Florian BRUNIAUX](https://www.linkedin.com/in/florian-bruniaux-43408b83/) - A tremendous feat of documentation, this guide covers Claude Code from beginner to power user, with production-ready templates for Claude Code features, guides on agentic workflows, and a lot of great learning materials, including quizzes and a handy "cheatsheet". Whether it's the "ultimate" guide to Claude Code will be up to the reader, but a valuable resource nonetheless (as with all documentation sites, make sure it's up to date before you bet the farm).
- [Claude CodePro](https://github.com/maxritter/claude-codepro) by [Max Ritter](https://www.maxritter.net) - Professional development environment for Claude Code with spec-driven workflow, TDD enforcement, cross-session memory, semantic search, quality hooks, and modular rules integration. A bit "heavyweight" but feature-packed and has wide coverage.
- [claude-code-docs](https://github.com/costiash/claude-code-docs) by [Constantin Shafranski](https://github.com/costiash) - A mirror of the Anthropic&copy; PBC documentation site for Claude/Code, but with bonus features like full-text search and query-time updates - a nice companion to `claude-code-docs` for up-to-the-minute, fully-indexed information so that Claude Code can read about itself.
- [ClaudoPro Directory](https://github.com/JSONbored/claudepro-directory) by [ghost](https://github.com/JSONbored) - Well-crafted, wide selection of Claude Code hooks, slash commands, subagent files, and more, covering a range of specialized tasks and workflows. Better resources than your average "Claude-template-for-everything" site.
- [Context Priming](https://github.com/disler/just-prompt/tree/main/.claude/commands) by [disler](https://github.com/disler) - Provides a systematic approach to priming Claude Code with comprehensive project context through specialized commands for different project scenarios and development contexts.
- [Design Review Workflow](https://github.com/OneRedOak/claude-code-workflows/tree/main/design-review) by [Patrick Ellis](https://github.com/OneRedOak) - A tailored workflow for enabling automated UI/UX design review, including specialized sub agents, slash commands, `CLAUDE.md` excerpts, and more. Covers a broad range of criteria from responsive design to accessibility.
- [Laravel TALL Stack AI Development Starter Kit](https://github.com/tott/laravel-tall-claude-ai-configs) by [tott](https://github.com/tott) - Transform your Laravel TALL (Tailwind, AlpineJS, Laravel, Livewire) stack development with comprehensive Claude Code configurations that provide intelligent assistance, systematic workflows, and domain expert consultation.
- [Learn Claude Code](https://github.com/shareAI-lab/learn-claude-code) by [shareAI-Lab](https://github.com/shareAI-lab/) - A really interesting analysis of how coding agents like Claude Code are designed. It attempts to break an agent down into its fundamental parts and reconstruct it with minimal code. Great learning resource. Final product is a rudimentary agent with skills, sub-agents, and a todo-list in roughly a few hundred lines of Python.
- [learn-faster-kit](https://github.com/cheukyin175/learn-faster-kit) by [Hugo Lau](https://github.com/cheukyin175) - A creative educational framework for Claude Code, inspired by the "FASTER" approach to self-teaching. Ships with a variety of agents, slash commands, and tools that enable Claude Code to help you progress at your own pace, employing well-established pedagogical techniques like active learning and spaced repetition.
- [n8n_agent](https://github.com/kingler/n8n_agent/tree/main/.claude/commands) by [kingler](https://github.com/kingler) - Amazing comprehensive set of comments for code analysis, QA, design, documentation, project structure, project management, optimization, and many more.
- [Project Bootstrapping and Task Management](https://github.com/steadycursor/steadystart/tree/main/.claude/commands) by [steadycursor](https://github.com/steadycursor) - Provides a structured set of commands for bootstrapping and managing a new project, including meta-commands for creating and editing custom slash-commands.
- [Project Management, Implementation, Planning, and Release](https://github.com/scopecraft/command/tree/main/.claude/commands) by [scopecraft](https://github.com/scopecraft) - Really comprehensive set of commands for all aspects of SDLC.
- [Project Workflow System](https://github.com/harperreed/dotfiles/tree/master/.claude/commands) by [harperreed](https://github.com/harperreed) - A set of commands that provide a comprehensive workflow system for managing projects, including task management, code review, and deployment processes.
- [RIPER Workflow](https://github.com/tony/claude-code-riper-5) by [Tony Narlock](https://tony.sh) - Structured development workflow enforcing separation between Research, Innovate, Plan, Execute, and Review phases. Features consolidated subagents for context-efficiency, branch-aware memory bank, and strict mode enforcement for guided development.
- [Shipping Real Code w/ Claude](https://diwank.space/field-notes-from-shipping-real-code-with-claude) by [Diwank](https://github.com/creatorrr) - A detailed blog post explaining the author's process for shipping a product with Claude Code, including CLAUDE.md files and other interesting resources.
- [Simone](https://github.com/Helmi/claude-simone) by [Helmi](https://github.com/Helmi) - A broader project management workflow for Claude Code that encompasses not just a set of commands, but a system of documents, guidelines, and processes to facilitate project planning and execution.

### Ralph Wiggum

- [awesome-ralph](https://github.com/snwfdhmp/awesome-ralph) by [Martin Joly](https://github.com/snwfdhmp) - A curated list of resources about Ralph, the AI coding technique that runs AI coding agents in automated loops until specifications are fulfilled.
- [Ralph for Claude Code](https://github.com/frankbria/ralph-claude-code) by [Frank Bria](https://github.com/frankbria) - An autonomous AI development framework that enables Claude Code to work iteratively on projects until completion. Features intelligent exit detection, rate limiting, circuit breaker patterns, and comprehensive safety guardrails to prevent infinite loops and API overuse. Built with Bash, integrated with tmux for live monitoring, and includes 75+ comprehensive tests.
- [Ralph Wiggum Marketer](https://github.com/muratcankoylan/ralph-wiggum-marketer) by [Muratcan Koylan](https://github.com/muratcankoylan) - A Claude Code plugin that provides an autonomous AI copywriter,  integrating the Ralph loop with customized knowledge bases for market research agents. The agents do the research, Ralph writes the copy, you stay in bed. Whether or not you practice Ralph-Driven Development (RDD), I think these projects are interesting and creative explorations of general agentic patterns.
- [ralph-orchestrator](https://github.com/mikeyobrien/ralph-orchestrator) by [mikeyobrien](https://github.com/mikeyobrien) - Ralph Orchestrator implements the simple but effective "Ralph Wiggum" technique for autonomous task completion, continuously running an AI agent against a prompt file until the task is marked as complete or limits are reached. This implementation provides a robust, well-tested, and feature-complete orchestration system for AI-driven development. Also cited in the Anthropic Ralph plugin documentation.
- [ralph-wiggum-bdd](https://github.com/marcindulak/ralph-wiggum-bdd) by [marcindulak](https://github.com/marcindulak) - A standalone Bash script for Behavior-Driven Development with Ralph Wiggum Loop. In principle, while running unattended, the script can keep code and requirements in sync, but in practice it still requires interactive human supervision, so it supports both modes. The script is standalone and can be modified and committed into your project.
- [The Ralph Playbook](https://github.com/ClaytonFarr/ralph-playbook) by [Clayton Farr](https://github.com/ClaytonFarr) - A remarkably detailed and comprehensive guide to the Ralph Wiggum technique, featuring well-written theoretical commentary paired with practical guidelines and advice.

<br>

## Tooling 🧰

> Tooling denotes applications that are built on top of Claude Code and consist of more components than slash-commands and `CLAUDE.md` files

### General

- [cc-sessions](https://github.com/GWUDCAP/cc-sessions) by [toastdev](https://github.com/satoastshi) - An opinionated approach to productive development with Claude Code.
- [cc-tools](https://github.com/Veraticus/cc-tools) by [Josh Symonds](https://github.com/Veraticus) - High-performance Go implementation of Claude Code hooks and utilities. Provides smart linting, testing, and statusline generation with minimal overhead.
- [ccexp](https://github.com/nyatinte/ccexp) by [nyatinte](https://github.com/nyatinte) - Interactive CLI tool for discovering and managing Claude Code configuration files and slash commands with a beautiful terminal UI.
- [cchistory](https://github.com/eckardt/cchistory) by [eckardt](https://github.com/eckardt) - Like the shell history command but for your Claude Code sessions. Easily list all Bash or "Bash-mode" (`!`) commands Claude Code ran in a session for reference.
- [cclogviewer](https://github.com/Brads3290/cclogviewer) by [Brad S.](https://github.com/Brads3290) - A humble but handy utility for viewing Claude Code `.jsonl` conversation files in a pretty HTML UI.
- [Claude Code Templates](https://github.com/davila7/claude-code-templates) by [Daniel Avila](https://github.com/davila7) - Incredibly awesome collection of resources from every category in this list, presented with a neatly polished UI, great features like usage dashboard, analytics, and everything from slash commands to hooks to agents. An awesome companion for this awesome list.
- [Claude Composer](https://github.com/possibilities/claude-composer) by [Mike Bannister](https://github.com/possibilities) - A tool that adds small enhancements to Claude Code.
- [Claude Hub](https://github.com/claude-did-this/claude-hub) by [Claude Did This](https://github.com/claude-did-this) - A webhook service that connects Claude Code to GitHub repositories, enabling AI-powered code assistance directly through pull requests and issues. This integration allows Claude to analyze repositories, answer technical questions, and help developers understand and improve their codebase through simple @mentions.
- [Claude Session Restore](https://github.com/ZENG3LD/claude-session-restore) by [ZENG3LD](https://github.com/ZENG3LD) - Efficiently restore context from previous Claude Code sessions by analyzing session files and git history. Features multi-factor data collection across numerous Claude Code capacities with time-based filtering. Uses tail-based parsing for efficient handling of large session files up to 2GB. Includes both a CLI tool for manual analysis and a Claude Code skill for automatic session restoration.
- [claude-code-tools](https://github.com/pchalasani/claude-code-tools) by [Prasad Chalasani](https://github.com/pchalasani) - Well-crafted toolset for session continuity, featuring skills/commands to avoid compaction and recover context across sessions with cross-agent handoff between Claude Code and Codex CLI. Includes a fast Rust/Tantivy-powered full-text session search (TUI for humans, skill/CLI for agents), tmux-cli skill + command for interacting with scripts and CLI agents, and safety hooks to block dangerous commands.
- [claude-starter-kit](https://github.com/serpro69/claude-starter-kit) by [serpro69](https://github.com/serpro69) - This is a starter template repository designed to provide a complete development environment for Claude-Code with pre-configured MCP servers and tools for AI-powered development workflows. The repository is intentionally minimal, containing only configuration templates for three primary systems: Claude Code, Serena, and Task Master.
- [claudekit](https://github.com/carlrannaberg/claudekit) by [Carl Rannaberg](https://github.com/carlrannaberg) - Impressive CLI toolkit providing auto-save checkpointing, code quality hooks, specification generation and execution, and 20+ specialized subagents including oracle (gpt-5), code-reviewer (6-aspect deep analysis), ai-sdk-expert (Vercel AI SDK), typescript-expert and many more for Claude Code workflows.
- [Container Use](https://github.com/dagger/container-use) by [dagger](https://github.com/dagger) - Development environments for coding agents. Enable multiple agents to work safely and independently with your preferred stack.
- [ContextKit](https://github.com/FlineDev/ContextKit) by [Cihat Gündüz](https://github.com/Jeehut) - A systematic development framework that transforms Claude Code into a proactive development partner. Features 4-phase planning methodology, specialized quality agents, and structured workflows that help AI produce production-ready code on first try.
- [recall](https://github.com/zippoxer/recall) by [zippoxer](https://github.com/zippoxer) - Full-text search your Claude Code sessions. Run `recall` in terminal, type to search, Enter to resume. Alternative to `claude --resume`.
- [Rulesync](https://github.com/dyoshikawa/rulesync) by [dyoshikawa](https://github.com/dyoshikawa) - A Node.js CLI tool that automatically generates configs (rules, ignore files, MCP servers, commands, and subagents) for various AI coding agents. Rulesync can convert configs between Claude Code and other AI agents in both directions.
- [run-claude-docker](https://github.com/icanhasjonas/run-claude-docker) by [Jonas](https://github.com/icanhasjonas/) - A self-contained Docker runner that forwards your current workspace into a safe(r) isolated docker container, where you still have access to your Claude Code settings, authentication, ssh agent, pgp, optionally aws keys etc.
- [stt-mcp-server-linux](https://github.com/marcindulak/stt-mcp-server-linux) by [marcindulak](https://github.com/marcindulak) - A push-to-talk speech transcription setup for Linux using a Python MCP server. Runs locally in Docker with no external API calls. Your speech is recorded, transcribed into text, and then sent to Claude running in a Tmux session.
- [SuperClaude](https://github.com/SuperClaude-Org/SuperClaude_Framework) by [SuperClaude-Org](https://github.com/SuperClaude-Org) - A versatile configuration framework that enhances Claude Code with specialized commands, cognitive personas, and development methodologies, such as "Introspection" and "Orchestration".
- [tweakcc](https://github.com/Piebald-AI/tweakcc) by [Piebald-AI](https://github.com/Piebald-AI) - Command-line tool to customize your Claude Code styling.
- [Vibe-Log](https://github.com/vibe-log/vibe-log-cli) by [Vibe-Log](https://github.com/vibe-log) - Analyzes your Claude Code prompts locally (using CC), provides intelligent session analysis and actionable strategic guidance - works in the statusline and produces very pretty HTML reports as well. Easy to install and remove.
- [viwo-cli](https://github.com/OverseedAI/viwo) by [Hal Shin](https://github.com/hal-shin) - Run Claude Code in a Docker container with git worktrees as volume mounts to enable safer usage of `--dangerously-skip-permissions` for frictionless one-shotting prompts. Allows users to spin up multiple instances of Claude Code in the background easily with reduced permission fatigue.
- [VoiceMode MCP](https://github.com/mbailey/voicemode) by [Mike Bailey](https://github.com/mbailey) - VoiceMode MCP brings natural conversations to Claude Code. It supports any OpenAI API compatible voice services and installs free and open source voice services (Whisper.cpp and Kokoro-FastAPI).

### IDE Integrations

- [Claude Code Chat](https://marketplace.visualstudio.com/items?itemName=AndrePimenta.claude-code-chat) by [andrepimenta](https://github.com/andrepimenta) - An elegant and user-friendly Claude Code chat interface for VS Code.
- [claude-code-ide.el](https://github.com/manzaltu/claude-code-ide.el) by [manzaltu](https://github.com/manzaltu) - claude-code-ide.el integrates Claude Code with Emacs, like Anthropic’s VS Code/IntelliJ extensions. It shows ediff-based code suggestions, pulls LSP/flymake/flycheck diagnostics, and tracks buffer context. It adds an extensible MCP tool support for symbol refs/defs, project metadata, and tree-sitter AST queries.
- [claude-code.el](https://github.com/stevemolitor/claude-code.el) by [stevemolitor](https://github.com/stevemolitor) - An Emacs interface for Claude Code CLI.
- [claude-code.nvim](https://github.com/greggh/claude-code.nvim) by [greggh](https://github.com/greggh) - A seamless integration between Claude Code AI assistant and Neovim.
- [Claudix - Claude Code for VSCode](https://github.com/Haleclipse/Claudix) by [Haleclipse](https://github.com/Haleclipse) - A VSCode extension that brings Claude Code directly into your editor with interactive chat interface, session management, intelligent file operations, terminal execution, and real-time streaming responses. Built with Vue 3, TypeScript.

### Usage Monitors

- [CC Usage](https://github.com/ryoppippi/ccusage) by [ryoppippi](https://github.com/ryoppippi) - Handy CLI tool for managing and analyzing Claude Code usage, based on analyzing local Claude Code logs. Presents a nice dashboard regarding cost information, token consumption, etc.
- [ccflare](https://github.com/snipeship/ccflare) by [snipeship](https://github.com/snipeship) - Claude Code usage dashboard with a web-UI that would put Tableau to shame. Thoroughly comprehensive metrics, frictionless setup, detailed logging, really really nice UI.
- [ccflare -> **better-ccflare**](https://github.com/tombii/better-ccflare/) by [tombii](https://github.com/tombii) - A well-maintained and feature-enhanced fork of the glorious `ccflare` usage dashboard by @snipeship (which at the time of writing has not had an update in a few months). `better-ccflare` builds on this foundation with some performance enhancements, extended provider support, bug fixes, Docker deployment, and more.
- [Claude Code Usage Monitor](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor) by [Maciek-roboblog](https://github.com/Maciek-roboblog) - A real-time terminal-based tool for monitoring Claude Code token usage. It shows live token consumption, burn rate, and predictions for token depletion. Features include visual progress bars, session-aware analytics, and support for multiple subscription plans.
- [Claudex](https://github.com/kunwar-shah/claudex) by [Kunwar Shah](https://github.com/kunwar-shah) - Claudex - A web-based browser for exploring your Claude Code conversation history across projects. Indexes your codebase for full-text search. Nice, easy-to-navigate UI. Simple dashboard interface for high-level analytics, and multiple export options as well. (And completely local w/ no telemetry!).
- [viberank](https://github.com/sculptdotfun/viberank) by [nikshepsvn](https://github.com/nikshepsvn) - A community-driven leaderboard tool that enables developers to visualize, track, and compete based on their Claude Code usage statistics. It features robust data analytics, GitHub OAuth, data validation, and user-friendly CLI/web submission methods.

### Orchestrators

- [Auto-Claude](https://github.com/AndyMik90/Auto-Claude) by [AndyMik90](https://github.com/AndyMik90) - Autonomous multi-agent coding framework for Claude Code (Claude Agent SDK) that integrates the full SDLC - "plans, builds, and validates software for you". Features a slick kanban-style UI and a well-designed but not over-engineered agent orchestration system.
- [Claude Code Flow](https://github.com/ruvnet/claude-code-flow) by [ruvnet](https://github.com/ruvnet) - This mode serves as a code-first orchestration layer, enabling Claude to write, edit, test, and optimize code autonomously across recursive agent cycles.
- [Claude Squad](https://github.com/smtg-ai/claude-squad) by [smtg-ai](https://github.com/smtg-ai) - Claude Squad is a terminal app that manages multiple Claude Code, Codex (and other local agents including Aider) in separate workspaces, allowing you to work on multiple tasks simultaneously.
- [Claude Swarm](https://github.com/parruda/claude-swarm) by [parruda](https://github.com/parruda) - Launch Claude Code session that is connected to a swarm of Claude Code Agents.
- [Claude Task Master](https://github.com/eyaltoledano/claude-task-master) by [eyaltoledano](https://github.com/eyaltoledano) - A task management system for AI-driven development with Claude, designed to work seamlessly with Cursor AI.
- [Claude Task Runner](https://github.com/grahama1970/claude-task-runner) by [grahama1970](https://github.com/grahama1970) - A specialized tool to manage context isolation and focused task execution with Claude Code, solving the critical challenge of context length limitations and task focus when working with Claude on complex, multi-step projects.
- [Happy Coder](https://github.com/slopus/happy) by [GrocerPublishAgent](https://peoplesgrocers.com/en/projects) - Spawn and control multiple Claude Codes in parallel from your phone or desktop. Happy Coder runs Claude Code on your hardware, sends push notifications when Claude needs more input or permission, and costs nothing.
- [The Agentic Startup](https://github.com/rsmdt/the-startup) by [Rudolf Schmidt](https://github.com/rsmdt) - Yet Another Claude Orchestrator - a collection of agents, commands, etc., for shipping production code - but I like this because it's comprehensive, well-written, and one of the few resources that actually uses Output Styles! +10 points!
- [TSK - AI Agent Task Manager and Sandbox](https://github.com/dtormoen/tsk) by [dtormoen](https://github.com/dtormoen) - A Rust CLI tool that lets you delegate development tasks to AI agents running in sandboxed Docker environments. Multiple agents work in parallel, returning git branches for human review.

### Config Managers

- [claude-rules-doctor](https://github.com/nulone/claude-rules-doctor) by [nulone](https://github.com/nulone) - CLI that detects dead `.claude/rules/` files by checking if `paths:` globs actually match files in your repo. Catches silent rule failures where renamed directories or typos in glob patterns cause rules to never apply. Features CI mode (exit 1 on dead rules), JSON output, and verbose mode showing matched files.
- [ClaudeCTX](https://github.com/foxj77/claudectx) by [John Fox](https://github.com/foxj77) - claudectx lets you switch your entire Claude Code configuration with a single command.

<br>

## Status Lines 📊

> Status lines - Configurations and customizations for Claude Code's status bar functionality

### General

- [CCometixLine - Claude Code Statusline](https://github.com/Haleclipse/CCometixLine) by [Haleclipse](https://github.com/Haleclipse) - A high-performance Claude Code statusline tool written in Rust with Git integration, usage tracking, interactive TUI configuration, and Claude Code enhancement utilities.
- [ccstatusline](https://github.com/sirmalloc/ccstatusline) by [sirmalloc](https://github.com/sirmalloc) - A highly customizable status line formatter for Claude Code CLI that displays model info, git branch, token usage, and other metrics in your terminal.
- [claude-code-statusline](https://github.com/rz1989s/claude-code-statusline) by [rz1989s](https://github.com/rz1989s) - Enhanced 4-line statusline for Claude Code with themes, cost tracking, and MCP server monitoring.
- [claude-powerline](https://github.com/Owloops/claude-powerline) by [Owloops](https://github.com/Owloops) - A vim-style powerline statusline for Claude Code with real-time usage tracking, git integration, custom themes, and more.
- [claudia-statusline](https://github.com/hagan/claudia-statusline) by [Hagan Franks](https://github.com/hagan) - High-performance Rust-based statusline for Claude Code with persistent stats tracking, progress bars, and optional cloud sync. Features SQLite-first persistence, git integration, context progress bars, burn rate calculation, XDG-compliant with theme support (dark/light, NO_COLOR).

<br>

## Hooks 🪝

> Hooks are a powerful API for Claude Code that allows users to activate commands and run scripts at different points in Claude's agentic lifecycle.

### General

- [Britfix](https://github.com/Talieisin/britfix) by [Talieisin](https://github.com/Talieisin) - Claude outputs American spellings by default, which can have an impact on: professional credibility, compliance, documentation, and more. Britfix converts to British English, with a Claude Code hook for automatic conversion as files are written. Context-aware: handles code files intelligently by only converting comments and docstrings, never identifiers or string literals.
- [CC Notify](https://github.com/dazuiba/CCNotify) by [dazuiba](https://github.com/dazuiba) - CCNotify provides desktop notifications for Claude Code, alerting you to input needs or task completion, with one-click jumps back to VS Code and task duration display.
- [cchooks](https://github.com/GowayLee/cchooks) by [GowayLee](https://github.com/GowayLee) - A lightweight Python SDK with a clean API and good documentation; simplifies the process of writing hooks and integrating them into your codebase, providing a nice abstraction over the JSON configuration files.
- [Claude Code Hook Comms (HCOM)](https://github.com/aannoo/claude-hook-comms) by [aannoo](https://github.com/aannoo) - Lightweight CLI tool for real-time communication between Claude Code sub agents using hooks. Enables multi-agent collaboration with @-mention targeting, live dashboard monitoring, and zero-dependency implementation. [NOTE: At the time of posting, this resource is a little unstable - I'm sharing it anyway, because I think it's incredibly promising and creative. I hope by the time you read this, it is production-ready.].
- [claude-code-hooks-sdk](https://github.com/beyondcode/claude-hooks-sdk) by [beyondcode](https://github.com/beyondcode) - A Laravel-inspired PHP SDK for building Claude Code hook responses with a clean, fluent API. This SDK makes it easy to create structured JSON responses for Claude Code hooks using an expressive, chainable interface.
- [claude-hooks](https://github.com/johnlindquist/claude-hooks) by [John Lindquist](https://github.com/johnlindquist) - A TypeScript-based system for configuring and customizing Claude Code hooks with a powerful and flexible interface.
- [Claudio](https://github.com/ctoth/claudio) by [Christopher Toth](https://github.com/ctoth) - A no-frills little library that adds delightful OS-native sounds to Claude Code via simple hooks. It really sparks joy.
- [TDD Guard](https://github.com/nizos/tdd-guard) by [Nizar Selander](https://github.com/nizos) - A hooks-driven system that monitors file operations in real-time and blocks changes that violate TDD principles.
- [TypeScript Quality Hooks](https://github.com/bartolli/claude-code-typescript-hooks) by [bartolli](https://github.com/bartolli) - Quality check hook for Node.js TypeScript projects with TypeScript compilation. ESLint auto-fixing, and Prettier formatting. Uses SHA256 config caching for < 5ms validation performance during real-time editing.

<br>

## Slash-Commands 🔪

> "Slash Commands are customized, carefully refined prompts that control Claude's behavior in order to perform a specific task"

### General

- [/create-hook](https://github.com/omril321/automated-notebooklm/blob/main/.claude/commands/create-hook.md) by [Omri Lavi](https://github.com/omril321) - Slash command for hook creation - intelligently prompts you through the creation process with smart suggestions based on your project setup (TS, Prettier, ESLint...).
- [/linux-desktop-slash-commands](https://github.com/danielrosehill/Claude-Code-Linux-Desktop-Slash-Commands) by [Daniel Rosehill](https://github.com/danielrosehill) - A library of slash commands intended specifically to facilitate common and advanced operations on Linux desktop environments (although many would also be useful on Linux servers). Command groups include hardware benchmarking, filesystem organisation, and security posture validation.

### Version Control & Git

- [/analyze-issue](https://github.com/jerseycheese/Narraitor/blob/feature/issue-227-ai-suggestions/.claude/commands/analyze-issue.md) by [jerseycheese](https://github.com/jerseycheese) - Fetches GitHub issue details to create comprehensive implementation specifications, analyzing requirements and planning structured approach with clear implementation steps.
- [/commit](https://github.com/evmts/tevm-monorepo/blob/main/.claude/commands/commit.md) by [evmts](https://github.com/evmts) - Creates git commits using conventional commit format with appropriate emojis, following project standards and creating descriptive messages that explain the purpose of changes.
- [/commit-fast](https://github.com/steadycursor/steadystart/blob/main/.claude/commands/2-commit-fast.md) by [steadycursor](https://github.com/steadycursor) - Automates git commit process by selecting the first suggested message, generating structured commits with consistent formatting while skipping manual confirmation and removing Claude co-Contributorship footer.
- [/create-pr](https://github.com/toyamarinyon/giselle/blob/main/.claude/commands/create-pr.md) by [toyamarinyon](https://github.com/toyamarinyon) - Streamlines pull request creation by handling the entire workflow: creating a new branch, committing changes, formatting modified files with Biome, and submitting the PR.
- [/create-pull-request](https://github.com/liam-hq/liam/blob/main/.claude/commands/create-pull-request.md) by [liam-hq](https://github.com/liam-hq) - Provides comprehensive PR creation guidance with GitHub CLI, enforcing title conventions, following template structure, and offering concrete command examples with best practices.
- [/create-worktrees](https://github.com/evmts/tevm-monorepo/blob/main/.claude/commands/create-worktrees.md) by [evmts](https://github.com/evmts) - Creates git worktrees for all open PRs or specific branches, handling branches with slashes, cleaning up stale worktrees, and supporting custom branch creation for development.
- [/fix-github-issue](https://github.com/jeremymailen/kotlinter-gradle/blob/master/.claude/commands/fix-github-issue.md) by [jeremymailen](https://github.com/jeremymailen) - Analyzes and fixes GitHub issues using a structured approach with GitHub CLI for issue details, implementing necessary code changes, running tests, and creating proper commit messages.
- [/husky](https://github.com/evmts/tevm-monorepo/blob/main/.claude/commands/husky.md) by [evmts](https://github.com/evmts) - Sets up and manages Husky Git hooks by configuring pre-commit hooks, establishing commit message standards, integrating with linting tools, and ensuring code quality on commits.
- [/update-branch-name](https://github.com/giselles-ai/giselle/blob/main/.claude/commands/update-branch-name.md) by [giselles-ai](https://github.com/giselles-ai) - Updates branch names with proper prefixes and formats, enforcing naming conventions, supporting semantic prefixes, and managing remote branch updates.

### Code Analysis & Testing

- [/code_analysis](https://github.com/kingler/n8n_agent/blob/main/.claude/commands/code_analysis.md) by [kingler](https://github.com/kingler) - Provides a menu of advanced code analysis commands for deep inspection, including knowledge graph generation, optimization suggestions, and quality evaluation.
- [/optimize](https://github.com/to4iki/ai-project-rules/blob/main/.claude/commands/optimize.md) by [to4iki](https://github.com/to4iki) - Analyzes code performance to identify bottlenecks, proposing concrete optimizations with implementation guidance for improved application performance.
- [/tdd](https://github.com/zscott/pane/blob/main/.claude/commands/tdd.md) by [zscott](https://github.com/zscott) - Guides development using Test-Driven Development principles, enforcing Red-Green-Refactor discipline, integrating with git workflow, and managing PR creation.
- [/tdd-implement](https://github.com/jerseycheese/Narraitor/blob/feature/issue-227-ai-suggestions/.claude/commands/tdd-implement.md) by [jerseycheese](https://github.com/jerseycheese) - Implements Test-Driven Development by analyzing feature requirements, creating tests first (red), implementing minimal passing code (green), and refactoring while maintaining tests.

### Context Loading & Priming

- [/context-prime](https://github.com/elizaOS/elizaos.github.io/blob/main/.claude/commands/context-prime.md) by [elizaOS](https://github.com/elizaOS) - Primes Claude with comprehensive project understanding by loading repository structure, setting development context, establishing project goals, and defining collaboration parameters.
- [/initref](https://github.com/okuvshynov/cubestat/blob/main/.claude/commands/initref.md) by [okuvshynov](https://github.com/okuvshynov) - Initializes reference documentation structure with standard doc templates, API reference setup, documentation conventions, and placeholder content generation.
- [/load-llms-txt](https://github.com/ethpandaops/xatu-data/blob/master/.claude/commands/load-llms-txt.md) by [ethpandaops](https://github.com/ethpandaops) - Loads LLM configuration files to context, importing specific terminology, model configurations, and establishing baseline terminology for AI discussions.

### Documentation & Changelogs

- [/add-to-changelog](https://github.com/berrydev-ai/blockdoc-python/blob/main/.claude/commands/add-to-changelog.md) by [berrydev-ai](https://github.com/berrydev-ai) - Adds new entries to changelog files while maintaining format consistency, properly documenting changes, and following established project standards for version tracking.
- [/create-docs](https://github.com/jerseycheese/Narraitor/blob/feature/issue-227-ai-suggestions/.claude/commands/create-docs.md) by [jerseycheese](https://github.com/jerseycheese) - Analyzes code structure and purpose to create comprehensive documentation detailing inputs/outputs, behavior, user interaction flows, and edge cases with error handling.
- [/docs](https://github.com/slunsford/coffee-analytics/blob/main/.claude/commands/docs.md) by [slunsford](https://github.com/slunsford) - Generates comprehensive documentation that follows project structure, documenting APIs and usage patterns with consistent formatting for better user understanding.
- [/explain-issue-fix](https://github.com/hackdays-io/toban-contribution-viewer/blob/main/.claude/commands/explain-issue-fix.md) by [hackdays-io](https://github.com/hackdays-io) - Documents solution approaches for GitHub issues, explaining technical decisions, detailing challenges overcome, and providing implementation context for better understanding.
- [/update-docs](https://github.com/Consiliency/Flutter-Structurizr/blob/main/.claude/commands/update-docs.md) by [Consiliency](https://github.com/Consiliency) - Reviews current documentation status, updates implementation progress, reviews phase documents, and maintains documentation consistency across the project.

### CI / Deployment

- [/run-ci](https://github.com/hackdays-io/toban-contribution-viewer/blob/main/.claude/commands/run-ci.md) by [hackdays-io](https://github.com/hackdays-io) - Activates virtual environments, runs CI-compatible check scripts, iteratively fixes errors, and ensures all tests pass before completion.

### Project & Task Management

- [/create-command](https://github.com/scopecraft/command/blob/main/.claude/commands/create-command.md) by [scopecraft](https://github.com/scopecraft) - Guides Claude through creating new custom commands with proper structure by analyzing requirements, templating commands by category, enforcing command standards, and creating supporting documentation.
- [/create-plan](https://github.com/hesreallyhim/inkverse-fork/blob/preserve-claude-resources/.claude/commands/create-plan.md) by [taddyorg](https://github.com/taddyorg) - Generates comprehensive product requirement documents outlining detailed specifications, requirements, and features following standardized document structure and format. *(Removed from origin)*
- [/create-prp](https://github.com/Wirasm/claudecode-utils/blob/main/.claude/commands/create-prp.md) by [Wirasm](https://github.com/Wirasm) - Creates product requirement plans by reading PRP methodology, following template structure, creating comprehensive requirements, and structuring product definitions for development.
- [/do-issue](https://github.com/jerseycheese/Narraitor/blob/feature/issue-227-ai-suggestions/.claude/commands/do-issue.md) by [jerseycheese](https://github.com/jerseycheese) - Implements GitHub issues with manual review points, following a structured approach with issue number parameter and offering alternative automated mode for efficiency.
- [/prd-generator](https://github.com/dredozubov/prd-generator) by [Denis Redozubov](https://github.com/dredozubov) - A Claude Code plugin that generates comprehensive Product Requirements Documents (PRDs) from conversation context. Invoke `/create-prd` after discussing requirements and it produces a complete PRD with all standard sections including Executive Summary, User Stories, MVP Scope, Architecture, Success Criteria, and Implementation Phases.
- [/project_hello_w_name](https://github.com/disler/just-prompt/blob/main/.claude/commands/project_hello_w_name.md) by [disler](https://github.com/disler) - Creates customizable greeting components with name input, demonstrating argument passing, component reusability, state management, and user input handling.
- [/todo](https://github.com/chrisleyva/todo-slash-command/blob/main/todo.md) by [chrisleyva](https://github.com/chrisleyva) - A convenient command to quickly manage project todo items without leaving the Claude Code interface, featuring due dates, sorting, task prioritization, and comprehensive todo list management.

### Miscellaneous

- [/fixing_go_in_graph](https://github.com/Mjvolk3/torchcell/blob/main/.claude/commands/fixing_go_in_graph.md) by [Mjvolk3](https://github.com/Mjvolk3) - Focuses on Gene Ontology annotation integration in graph databases, handling multiple data sources, addressing graph representation issues, and ensuring correct data incorporation.
- [/review_dcell_model](https://github.com/Mjvolk3/torchcell/blob/main/.claude/commands/review_dcell_model.md) by [Mjvolk3](https://github.com/Mjvolk3) - Reviews old Dcell implementation files, comparing with newer Dango model, noting changes over time, and analyzing refactoring approaches for better code organization.
- [/use-stepper](https://github.com/zuplo/docs/blob/main/.claude/commands/use-stepper.md) by [zuplo](https://github.com/zuplo) - Reformats documentation to use React Stepper component, transforming heading formats, applying proper indentation, and maintaining markdown compatibility with admonition formatting.

<br>

## CLAUDE.md Files 📂

> `CLAUDE.md` files are files that contain important guidelines and context-specific information or instructions that help Claude Code to better understand your project and your coding standards

### Language-Specific

- [AI IntelliJ Plugin](https://github.com/didalgolab/ai-intellij-plugin/blob/main/CLAUDE.md) by [didalgolab](https://github.com/didalgolab) - Provides comprehensive Gradle commands for IntelliJ plugin development with platform-specific coding patterns, detailed package structure guidelines, and clear internationalization standards.
- [AWS MCP Server](https://github.com/alexei-led/aws-mcp-server/blob/main/CLAUDE.md) by [alexei-led](https://github.com/alexei-led) - Features multiple Python environment setup options with detailed code style guidelines, comprehensive error handling recommendations, and security considerations for AWS CLI interactions.
- [DroidconKotlin](https://github.com/touchlab/DroidconKotlin/blob/main/CLAUDE.md) by [touchlab](https://github.com/touchlab) - Delivers comprehensive Gradle commands for cross-platform Kotlin Multiplatform development with clear module structure and practical guidance for dependency injection.
- [EDSL](https://github.com/hesreallyhim/awesome-claude-code/blob/main/resources/claude.md-files/EDSL/CLAUDE.md) by [expectedparrot](https://github.com/expectedparrot) - Offers detailed build and test commands with strict code style enforcement, comprehensive testing requirements, and standardized development workflow using Black and mypy. *(Removed from origin)*
- [Giselle](https://github.com/giselles-ai/giselle/blob/main/CLAUDE.md) by [giselles-ai](https://github.com/giselles-ai) - Provides detailed build and test commands using pnpm and Vitest with strict code formatting requirements and comprehensive naming conventions for code consistency.
- [HASH](https://github.com/hashintel/hash/blob/main/CLAUDE.md) by [hashintel](https://github.com/hashintel) - Features comprehensive repository structure breakdown with strong emphasis on coding standards, detailed Rust documentation guidelines, and systematic PR review process.
- [Inkline](https://github.com/inkline/inkline/blob/main/CLAUDE.md) by [inkline](https://github.com/inkline) - Structures development workflow using pnpm with emphasis on TypeScript and Vue 3 Composition API, detailed component creation process, and comprehensive testing recommendations.
- [JSBeeb](https://github.com/mattgodbolt/jsbeeb/blob/main/CLAUDE.md) by [mattgodbolt](https://github.com/mattgodbolt) - Provides development guide for JavaScript BBC Micro emulator with build and testing instructions, architecture documentation, and debugging workflows.
- [Lamoom Python](https://github.com/LamoomAI/lamoom-python/blob/main/CLAUDE.md) by [LamoomAI](https://github.com/LamoomAI) - Serves as reference for production prompt engineering library with load balancing of AI Models, API documentation, and usage patterns with examples.
- [LangGraphJS](https://github.com/langchain-ai/langgraphjs/blob/main/CLAUDE.md) by [langchain-ai](https://github.com/langchain-ai) - Offers comprehensive build and test commands with detailed TypeScript style guidelines, layered library architecture, and monorepo structure using yarn workspaces.
- [SG Cars Trends Backend](https://github.com/sgcarstrends/backend/blob/main/CLAUDE.md) by [sgcarstrends](https://github.com/sgcarstrends) - Provides comprehensive structure for TypeScript monorepo projects with detailed commands for development, testing, deployment, and AWS/Cloudflare integration.
- [SPy](https://github.com/spylang/spy/blob/main/CLAUDE.md) by [spylang](https://github.com/spylang) - Enforces strict coding conventions with comprehensive testing guidelines, multiple code compilation options, and backend-specific test decorators for targeted filtering.
- [TPL](https://github.com/KarpelesLab/tpl/blob/master/CLAUDE.md) by [KarpelesLab](https://github.com/KarpelesLab) - Details Go project conventions with comprehensive error handling recommendations, table-driven testing approach guidelines, and modernization suggestions for latest Go features.

### Domain-Specific

- [Comm](https://github.com/CommE2E/comm/blob/master/CLAUDE.md) by [CommE2E](https://github.com/CommE2E) - Serves as a development reference for E2E-encrypted messaging applications with code organization architecture, security implementation details, and testing procedures.
- [Course Builder](https://github.com/badass-courses/course-builder/blob/main/CLAUDE.md) by [badass-courses](https://github.com/badass-courses) - Enables real-time multiplayer capabilities for collaborative course creation with diverse tech stack integration and monorepo architecture using Turborepo.
- [Guitar](https://github.com/soramimi/Guitar/blob/master/CLAUDE.md) by [soramimi](https://github.com/soramimi) - Serves as development guide for Guitar Git GUI Client with build commands for various platforms, code style guidelines for contributing, and project structure explanation.
- [Network Chronicles](https://github.com/Fimeg/NetworkChronicles/blob/legacy-v1/CLAUDE.md) by [Fimeg](https://github.com/Fimeg) - Presents detailed implementation plan for AI-driven game characters with technical specifications for LLM integration, character guidelines, and service discovery mechanics.
- [Pareto Mac](https://github.com/ParetoSecurity/pareto-mac/blob/main/CLAUDE.md) by [ParetoSecurity](https://github.com/ParetoSecurity) - Serves as development guide for Mac security audit tool with build instructions, contribution guidelines, testing procedures, and workflow documentation.
- [pre-commit-hooks](https://github.com/aRustyDev/pre-commit-hooks) by [aRustyDev](https://github.com/aRustyDev) - This repository is about pre-commit-hooks in general, but the `CLAUDE.md` and related `.claude/` documentation is exemplary. Thorough but not verbose. Unlike a lot of `CLAUDE.md`  files, it doesn't primarily consist in shouting at Claude in all-caps. Great learning resource. Also, hooks.
- [SteadyStart](https://github.com/steadycursor/steadystart/blob/main/CLAUDE.md) by [steadycursor](https://github.com/steadycursor) - Clear and direct instructives about style, permissions, Claude's "role", communications, and documentation of Claude Code sessions for other team members to stay abreast.

### Project Scaffolding & MCP

- [Basic Memory](https://github.com/basicmachines-co/basic-memory/blob/main/CLAUDE.md) by [basicmachines-co](https://github.com/basicmachines-co) - Presents an innovative AI-human collaboration framework with Model Context Protocol for bidirectional LLM-markdown communication and flexible knowledge structure for complex projects.
- [claude-code-mcp-enhanced](https://github.com/grahama1970/claude-code-mcp-enhanced/blob/main/CLAUDE.md) by [grahama1970](https://github.com/grahama1970) - Provides detailed and emphatic instructions for Claude to follow as a coding agent, with testing guidance, code examples, and compliance checks.

<br>

## Alternative Clients 📱

> Alternative Clients are alternative UIs and front-ends for interacting with Claude Code, either on mobile or on the desktop.

### General

- [Claudable](https://github.com/opactorai/Claudable) by [Ethan Park](https://www.linkedin.com/in/seongil-park/) - Claudable is an open-source web builder that leverages local CLI agents, such as Claude Code and Cursor Agent, to build and deploy products effortlessly.
- [crystal](https://github.com/stravu/crystal) by [stravu](https://github.com/stravu) - A full-fledged desktop application for orchestrating, monitoring, and interacting with Claude Code agents.

<br>

## Official Documentation 🏛️

> Links to some of Anthropic's terrific documentation and resources regarding Claude Code

### General

- [Anthropic Documentation](https://docs.claude.com/en/home) by [Anthropic](https://github.com/anthropics) - The official documentation for Claude Code, including installation instructions, usage guidelines, API references, tutorials, examples, loads of information that I won't list individually. Like Claude Code, the documentation is frequently updated.
- [Anthropic Quickstarts](https://github.com/anthropics/claude-quickstarts) by [Anthropic](https://github.com/anthropics) - Offers comprehensive development guides for three distinct AI-powered demo projects with standardized workflows, strict code style guidelines, and containerization instructions.
- [Claude Code GitHub Actions](https://github.com/anthropics/claude-code-action/tree/main/examples) by [Anthropic](https://github.com/anthropics) - Official GitHub Actions integration for Claude Code with examples and documentation for automating AI-powered workflows in CI/CD pipelines.


## Contributing [🔝](#awesome-claude-code)

### **[Recommend a new resource here!](https://github.com/hesreallyhim/awesome-claude-code/issues/new?template=recommend-resource.yml)**

Recommending a resource for the list is very simple, and the automated system handles everything for you. Please do not open a PR to submit a recommendation - the only person who is allowed to submit PRs to this repo is Claude.

Make sure that you have read the CONTRIBUTING.md document and CODE_OF_CONDUCT.md before you submit a recommendation.

For suggestions about the repository itself, please [open a repository enhancement issue](https://github.com/hesreallyhim/awesome-claude-code/issues/new?template=repository-enhancement.yml).

This project is released with a Code of Conduct. By participating, you agree to abide by its terms. And although I take strong measures to uphold the quality and safety of this list, I take no responsibility or liability for anything that might happen as a result of these third-party resources.

## Growing thanks to you
[![Stargazers over time](https://starchart.cc/hesreallyhim/awesome-claude-code.svg?variant=adaptive)](https://starchart.cc/hesreallyhim/awesome-claude-code)

## License

This list is licensed under [Creative Commons CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/) - this means you are welcome to fork, clone, copy and redistribute the list, provided you include appropriate attribution; however you are not permitted to distribute any modified versions or to use it for any commercial purposes. This is to prevent disregard for the licenses of the authors whose resources are listed here. Please note that all resources included in this list have their own license terms.


<!-- OBLIGATORY GUARD AGAINST SILLY END-OF-FILE PROBLEM -->
