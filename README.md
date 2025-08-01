<!--lint disable remark-lint:awesome-badge-->

#

<!-- [![Awesome](https://awesome.re/badge-flat2.svg)](https://awesome.re) -->

<pre style="display: inline-block; text-align: left;">
 █████┐ ██┐    ██┐███████┐███████┐ ██████┐ ███┐   ███┐███████┐
██┌──██┐██│    ██│██┌────┘██┌────┘██┌───██┐████┐ ████│██┌────┘
███████│██│ █┐ ██│█████┐  ███████┐██│   ██│██┌████┌██│█████┐
██┌──██│██│███┐██│██┌──┘  └────██│██│   ██│██│└██┌┘██│██┌──┘
██│  ██│└███┌███┌┘███████┐███████│└██████┌┘██│ └─┘ ██│███████┐
└─┘  └─┘ └──┘└──┘ └──────┘└──────┘ └─────┘ └─┘     └─┘└──────┘

 ────────────────────────────────────────────────────────────────────────────────────

 ██████┐██┐      █████┐ ██┐   ██┐██████┐ ███████┐     ██████┐ ██████┐ ██████┐ ███████┐
██┌────┘██│     ██┌──██┐██│   ██│██┌──██┐██┌────┘    ██┌────┘██┌───██┐██┌──██┐██┌────┘
██│     ██│     ███████│██│   ██│██│  ██│█████┐      ██│     ██│   ██│██│  ██│█████┐
██│     ██│     ██┌──██│██│   ██│██│  ██│██┌──┘      ██│     ██│   ██│██│  ██│██┌──┘
└██████┐███████┐██│  ██│└██████┌┘██████┌┘███████┐    └██████┐└██████┌┘██████┌┘███████┐
 └─────┘└──────┘└─┘  └─┘ └─────┘ └─────┘ └──────┘     └─────┘ └─────┘ └─────┘ └──────┘
</pre>

<!--lint enable remark-lint:awesome-badge-->

[![Awesome](https://awesome.re/badge-flat2.svg)](https://awesome.re)

# [Awesome Claude Code](https://github.com/hesreallyhim/awesome-claude-code) 🤝 [Awesome Claude Code Agents](https://github.com/hesreallyhim/awesome-claude-code-agents)

<!--lint enable remark-lint:awesome-badge-->

<!--lint disable double-link-->

This is a curated list of slash-commands, `CLAUDE.md` files, CLI tools, and other resources and guides for enhancing your [Claude Code](https://docs.anthropic.com/en/docs/claude-code) workflow, productivity, and vibes.

<!--lint enable double-link-->

Claude Code is a cutting-edge CLI-based coding assistant and agent that you can access in your terminal or IDE. It is a rapidly evolving tool that offers a number of powerful capabilities, and allows for a lot of configuration, in a lot of different ways. Users are actively working out best practices and workflows. It is the hope that this repo will help the community share knowledge and understand how to get the most out of Claude Code.

### Announcements

- 2025-07-30 - Quick Update: Still trying to iron out the submission flow (sorry for anyone that received duplicate "Congratulations!" issues). If you end up fighting any of the programmatic submission tools, just submit something that has all the necessary data, and I'll take it from there once approved. Other notes: (i) I think it would be really cool/fun to set up a "Claude Code Leaderboard", so feel free to weigh in on the [Discussion](https://github.com/hesreallyhim/awesome-claude-code/discussions/81); (ii) I'm still trying to figure out what to do about **SUB AGENTS**, and I've reached out to some of the other folks who have started similar repo's; (iii) Added a small section that will be updated with new submissions as they roll in.

## New Additions

- [`CC Notify`](https://github.com/dazuiba/CCNotify) by [dazuiba](https://github.com/dazuiba)
- [`tweakcc`](https://github.com/Piebald-AI/tweakcc) by [Piebald-AI](https://github.com/Piebald-AI)
- [`cchooks`](https://github.com/GowayLee/cchooks) by [GowayLee](https://github.com/GowayLee)

<br>

## Contents

▪&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Workflows & Knowledge Guides](#workflows--knowledge-guides-)  
▪&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Tooling](#tooling-)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▫&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[IDE Integrations](#ide-integrations)  
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
▪&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Official Documentation](#official-documentation-)  

<br>

## Workflows & Knowledge Guides 🧠

> A **workflow** is a tightly coupled set of Claude Code-native resources that facilitate specific projects

[`Blogging Platform Instructions`](https://github.com/cloudartisan/cloudartisan.github.io/tree/main/.claude/commands) &nbsp; by &nbsp; [cloudartisan](https://github.com/cloudartisan)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;CC-BY-SA-4.0  
Provides a well-structured set of commands for publishing and maintaining a blogging platform, including commands for creating posts, managing categories, and handling media files.

[`ClaudeLog`](https://claudelog.com) &nbsp; by &nbsp; [InventorBlack](https://www.reddit.com/user/inventor_black/)    
A comprehensive knowledge base with detailed breakdowns of advanced [mechanics](https://claudelog.com/mechanics/you-are-the-main-thread/) including [CLAUDE.md best practices](https://claudelog.com/mechanics/claude-md-supremacy), practical technique guides like [plan mode](https://claudelog.com/mechanics/plan-mode), [ultrathink](https://claudelog.com/faqs/what-is-ultrathink/), [sub-agents](https://claudelog.com/mechanics/task-agent-tools/), [agent-first design](https://claudelog.com/mechanics/agent-first-design/) and [configuration guides](https://claudelog.com/configuration).

[`Context Priming`](https://github.com/disler/just-prompt/tree/main/.claude/commands) &nbsp; by &nbsp; [disler](https://github.com/disler)    
Provides a systematic approach to priming Claude Code with comprehensive project context through specialized commands for different project scenarios and development contexts.

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

[`CC Usage`](https://github.com/ryoppippi/ccusage) &nbsp; by &nbsp; [ryoppippi](https://github.com/ryoppippi)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Handy CLI tool for managing and analyzing Claude Code usage, based on analyzing local Claude Code logs. Presents a nice dashboard regarding cost information, token consumption, etc.

[`ccexp`](https://github.com/nyatinte/ccexp) &nbsp; by &nbsp; [nyatinte](https://github.com/nyatinte)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Interactive CLI tool for discovering and managing Claude Code configuration files and slash commands with a beautiful terminal UI.

[`Claude Code Flow`](https://github.com/ruvnet/claude-code-flow) &nbsp; by &nbsp; [ruvnet](https://github.com/ruvnet)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
This mode serves as a code-first orchestration layer, enabling Claude to write, edit, test, and optimize code autonomously across recursive agent cycles.

[`Claude Code Usage Monitor`](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor) &nbsp; by &nbsp; [Maciek-roboblog](https://github.com/Maciek-roboblog)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
A real-time terminal-based tool for monitoring Claude Code token usage. It shows live token consumption, burn rate, and predictions for token depletion. Features include visual progress bars, session-aware analytics, and support for multiple subscription plans.

[`Claude Composer`](https://github.com/possibilities/claude-composer) &nbsp; by &nbsp; [Mike Bannister](https://github.com/possibilities)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;Unlicense  
A tool that adds small enhancements to Claude Code.

[`Claude Hub`](https://github.com/claude-did-this/claude-hub) &nbsp; by &nbsp; [Claude Did This](https://github.com/claude-did-this)    
A webhook service that connects Claude Code to GitHub repositories, enabling AI-powered code assistance directly through pull requests and issues. This integration allows Claude to analyze repositories, answer technical questions, and help developers understand and improve their codebase through simple @mentions.

[`Claude Squad`](https://github.com/smtg-ai/claude-squad) &nbsp; by &nbsp; [smtg-ai](https://github.com/smtg-ai)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;AGPL-3.0  
Claude Squad is a terminal app that manages multiple Claude Code, Codex (and other local agents including Aider) in separate workspaces, allowing you to work on multiple tasks simultaneously.

[`Claude Swarm`](https://github.com/parruda/claude-swarm) &nbsp; by &nbsp; [parruda](https://github.com/parruda)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
Launch Claude Code session that is connected to a swarm of Claude Code Agents.

[`Claude Task Master`](https://github.com/eyaltoledano/claude-task-master) &nbsp; by &nbsp; [eyaltoledano](https://github.com/eyaltoledano)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;NOASSERTION  
A task management system for AI-driven development with Claude, designed to work seamlessly with Cursor AI.

[`Claude Task Runner`](https://github.com/grahama1970/claude-task-runner) &nbsp; by &nbsp; [grahama1970](https://github.com/grahama1970)    
A specialized tool to manage context isolation and focused task execution with Claude Code, solving the critical challenge of context length limitations and task focus when working with Claude on complex, multi-step projects.

[`Container Use`](https://github.com/dagger/container-use) &nbsp; by &nbsp; [dagger](https://github.com/dagger)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;Apache-2.0  
Development environments for coding agents. Enable multiple agents to work safely and independently with your preferred stack.


### IDE Integrations

[`Claude Code Chat`](https://marketplace.visualstudio.com/items?itemName=AndrePimenta.claude-code-chat) &nbsp; by &nbsp; [andrepimenta](https://github.com/andrepimenta)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;&copy;  
An elegant and user-friendly Claude Code chat interface for VS Code.

[`claude-code.el`](https://github.com/stevemolitor/claude-code.el) &nbsp; by &nbsp; [stevemolitor](https://github.com/stevemolitor)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;Apache-2.0  
An Emacs interface for Claude Code CLI.

[`claude-code.nvim`](https://github.com/greggh/claude-code.nvim) &nbsp; by &nbsp; [greggh](https://github.com/greggh)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
A seamless integration between Claude Code AI assistant and Neovim.

[`crystal`](https://github.com/stravu/crystal) &nbsp; by &nbsp; [stravu](https://github.com/stravu)  &nbsp;&nbsp;⚖️&nbsp;&nbsp;MIT  
A full-fledged desktop application for orchestrating, monitoring, and interacting with Claude Code agents.

<br>

## Hooks 🪝

> **Hooks** are a brand new API for Claude Code that allows users to activate commands and run scripts at different points in Claude's agentic lifecycle.

**[Experimental]** - The resources listed in this section have not been fully vetted and may not work as expected, given the bleeding-edge nature of Claude Code hooks. Nevertheless, I wished to include them at least as a source of inspiration and to explore this unknown terrain. YMMV!

<br>

## Slash-Commands 🔪

<br>

## CLAUDE.md Files 📂

> **`CLAUDE.md` files** are files that contain important guidelines and context-specfic information or instructions that help Claude Code to better understand your project and your coding standards

<br>

## Official Documentation 🏛️

> Links to some of Anthropic's terrific documentation and resources regarding Claude Code

<!--lint disable double-link-->


## Contributing 🌻

Please note that this project is released with a [Contributor Code of Conduct](code-of-conduct.md). By participating in this project you agree to abide by its terms.

Regarding content, we especially welcome:

- Proven, effective resources that follow best practices and may even be in use in production.
- Innovative, creative, or experimental workflows that perhaps are still being iterated upon, but have high potential value, and push the boundaries of Claude Code's documented capabilities and use cases.
- Additional libraries and tooling that are built on top of Claude Code and offer enhanced functionality.
- Applications of Claude Code outside of the traditional "coding assistant" context, e.g., CI/CD integration, testing, documentation, dev-ops, etc.

See [CONTRIBUTING.md](CONTRIBUTING.md) for more information on how to contribute to this project. Or, fire up Claude Code and invoke the `/project:add-new-resource` command and let Claude walk you through it!

If you have any suggestions or thoughts on how to improve the repo, or how to best organize the list, feel free to start a Discussion topic. This is meant to be for the Claude Code community, and in general I prefer not to act on sole authority.

### A note about licenses

Because simply listing a hyperlink does not qualify as redistribution, the license of the original source is not relevant to its inclusion. However, for posterity and convenience, we do host copies of all resources whose license permits it. Therefore, please include information about the resource's license. Additionally, take note: _if you do not include a LICENSE in your GitHub repo, then by default it is fully copyrighted and redistribution is not allowed_. So, if you are intending to make an open source project, it's critical to pick from one of the many available open source licenses. This is just a reminder that without a LICENSE, your project is not open source (it's merely source-code-available) - it may of course still be included on this list, but this notice is to inform readers about the default rules regarding GitHub and LICENSE files. See [here](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository) for more details.
