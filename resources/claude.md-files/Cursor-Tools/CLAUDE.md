This is the vibe-tools repo. Here we build a cli tool that AI agents can use to execute commands and work with other AI agents.

This repo uses pnpm as the package manager and script runner.

use pnpm dev <command> to run dev commands.

We add AI "teammates" as commands that can be asked questions.
We add "skills" as commands that can be used to execute tasks.

Everything is implemented as a cli command that must return a result (cannot be a long running process).

The released commands are documented below. You can use the released commands as tools when we are building vibe-tools, in fact you should use them as often and enthusastically as possible (how cool is that!)

Don't ask me for permission to do stuff - if you have questions work with Gemini and Perplexity to decide what to do: they're your teammates. You're a team of superhuman expert AIs, believe in yourselves! Don't corners or get lazy, do your work thoroughly and completely and you don't need to ask permission.

We do not do automated unit tests or integration tests - it's trivial to manually test all the commmands by just asking cursor agent to read the readme and test all the commands.

<logging and outputs>
There are three ways that we communicate to the caller.
console.log which goes to stdout
console.error which goes to stderr
do not use console.debug or console.warn or console.info
and yield which is streamed either to stdout (unless the --quiet flag is used) and to the file specified by --save-to (if --save-to is specified).

console.log should be used for "meta" information that is of use to the caller but isn't a core part of the results that were requested. E.g. recording which model is being used to perfom an action.

console.error should be used for error messages.

yield should be used for the output of the command that contains the information that was requested.
</logging and outputs>

<testing browser commands>
There is a test server for browser command testing and a collection of test files in tests/commands/browser/

Usage:
1. Run with: pnpm serve-test
2. Server starts at http://localhost:3000
3. Place test HTML files in tests/commands/browser/
4. Access files at http://localhost:3000/filename.html

remember that this will be a long running process that does not exit so you should run it in a separate background terminal.

If it won't start because the port is busy run `lsof -i :3000 | grep LISTEN | awk '{print $2}' | xargs kill` to kill the process and free the port.

to run test commands with latest code use `pnpm dev browser <commands>`

For interactive debugging start chrome in debug mode using:
```
open -a "Google Chrome" --args --remote-debugging-port=9222 --no-first-run --no-default-browser-check --user-data-dir="/tmp/chrome-remote-debugging"
```
note: this command will exit as soon as chrome is open so you can just execute it, it doesn't need to be run in a background task.
</testing browser commands>

---
description: Global Rule. This rule should ALWAYS be loaded
globs: *,**/*
alwaysApply: true
---
---
description: Global Rule. This rule should ALWAYS be loaded.
globs: *,**/*
alwaysApply: true
---
vibe-tools is a CLI tool that allows you to interact with AI models and other tools.
vibe-tools is installed on this machine and it is available to you to execute. You're encouraged to use it.

<vibe-tools Integration>
# Instructions
Use the following commands to get AI assistance:

**Direct Model Queries:**
`vibe-tools ask "<your question>" --provider <provider> --model <model>` - Ask any model from any provider a direct question (e.g., `vibe-tools ask "What is the capital of France?" --provider openai --model o3-mini`). Note that this command is generally less useful than other commands like `repo` or `plan` because it does not include any context from your codebase or repository. In general you should not use the ask command because it does not include any context. The other commands like `web`, `doc`, `repo`, or `plan` are usually better. If you are using it, make sure to include in your question all the information and context that the model might need to answer usefully.

**Ask Command Options:**
--provider=<provider>: AI provider to use (openai, anthropic, perplexity, gemini, modelbox, openrouter, or xai)
--model=<model>: Model to use (required for the ask command)
--reasoning-effort=<low|medium|high>: Control the depth of reasoning for supported models (OpenAI o1/o3-mini models and Claude 3.7 Sonnet). Higher values produce more thorough responses for complex questions.

**Implementation Planning:**
`vibe-tools plan "<query>"` - Generate a focused implementation plan using AI (e.g., `vibe-tools plan "Add user authentication to the login page"`)
The plan command uses multiple AI models to:
1. Identify relevant files in your codebase (using Gemini by default)
2. Extract content from those files
3. Generate a detailed implementation plan (using OpenAI o3-mini by default)

**Plan Command Options:**
--fileProvider=<provider>: Provider for file identification (gemini, openai, anthropic, perplexity, modelbox, openrouter, or xai)
--thinkingProvider=<provider>: Provider for plan generation (gemini, openai, anthropic, perplexity, modelbox, openrouter, or xai)
--fileModel=<model>: Model to use for file identification
--thinkingModel=<model>: Model to use for plan generation
--with-doc=<doc_url>: Fetch content from a document URL and include it as context for both file identification and planning (e.g., `vibe-tools plan "implement feature X following the spec" --with-doc=https://example.com/feature-spec`)

**Web Search:**
`vibe-tools web "<your question>"` - Get answers from the web using a provider that supports web search (e.g., Perplexity models and Gemini Models either directly or from OpenRouter or ModelBox) (e.g., `vibe-tools web "latest shadcn/ui installation instructions"`)
Note: web is a smart autonomous agent with access to the internet and an extensive up to date knowledge base. Web is NOT a web search engine. Always ask the agent for what you want using a proper sentence, do not just send it a list of keywords. In your question to web include the context and the goal that you're trying to acheive so that it can help you most effectively.
when using web for complex queries suggest writing the output to a file somewhere like local-research/<query summary>.md.

**Web Command Options:**
--provider=<provider>: AI provider to use (perplexity, gemini, modelbox, or openrouter)

**Repository Context:**
`vibe-tools repo "<your question>" [--subdir=<path>] [--from-github=<username/repo>] [--with-doc=<doc_url>]` - Get context-aware answers about this repository using Google Gemini (e.g., `vibe-tools repo "explain authentication flow"`). Use the optional `--subdir` parameter to analyze a specific subdirectory instead of the entire repository (e.g., `vibe-tools repo "explain the code structure" --subdir=src/components`). Use the optional `--from-github` parameter to analyze a remote GitHub repository without cloning it locally (e.g., `vibe-tools repo "explain the authentication system" --from-github=username/repo-name`). Use the optional `--with-doc` parameter to include content from a URL as additional context (e.g., `vibe-tools repo "implement feature X following the design spec" --with-doc=https://example.com/design-spec`).

**Documentation Generation:**
`vibe-tools doc [options] [--with-doc=<doc_url>]` - Generate comprehensive documentation for this repository (e.g., `vibe-tools doc --output docs.md`). Can incorporate document context from a URL (e.g., `vibe-tools doc --with-doc=https://example.com/existing-docs`).

**YouTube Video Analysis:**
`vibe-tools youtube "<youtube-url>" [question] [--type=<summary|transcript|plan|review|custom>]` - Analyze YouTube videos and generate detailed reports (e.g., `vibe-tools youtube "https://youtu.be/43c-Sm5GMbc" --type=summary`)
Note: The YouTube command requires a `GEMINI_API_KEY` to be set in your environment or .vibe-tools.env file as the GEMINI API is the only interface that supports YouTube analysis.

**GitHub Information:**
`vibe-tools github pr [number]` - Get the last 10 PRs, or a specific PR by number (e.g., `vibe-tools github pr 123`)
`vibe-tools github issue [number]` - Get the last 10 issues, or a specific issue by number (e.g., `vibe-tools github issue 456`)

**ClickUp Information:**
`vibe-tools clickup task <task_id>` - Get detailed information about a ClickUp task including description, comments, status, assignees, and metadata (e.g., `vibe-tools clickup task "task_id"`)

**Model Context Protocol (MCP) Commands:**
Use the following commands to interact with MCP servers and their specialized tools:
`vibe-tools mcp search "<query>"` - Search the MCP Marketplace for available servers that match your needs (e.g., `vibe-tools mcp search "git repository management"`)
`vibe-tools mcp run "<query>"` - Execute MCP server tools using natural language queries (e.g., `vibe-tools mcp run "list files in the current directory" --provider=openrouter`). The query must include sufficient information for vibe-tools to determine which server to use, provide plenty of context.

The `search` command helps you discover servers in the MCP Marketplace based on their capabilities and your requirements. The `run` command automatically selects and executes appropriate tools from these servers based on your natural language queries. If you want to use a specific server include the server name in your query. E.g. `vibe-tools mcp run "using the mcp-server-sqlite list files in directory --provider=openrouter"`

**Notes on MCP Commands:**
- MCP commands require `ANTHROPIC_API_KEY` or `OPENROUTER_API_KEY` to be set in your environment
- By default the `mcp` command uses Anthropic, but takes a --provider argument that can be set to 'anthropic' or 'openrouter'
- Results are streamed in real-time for immediate feedback
- Tool calls are automatically cached to prevent redundant operations
- Often the MCP server will not be able to run because environment variables are not set. If this happens ask the user to add the missing environment variables to the cursor tools env file at ~/.vibe-tools/.env

**Stagehand Browser Automation:**
`vibe-tools browser open <url> [options]` - Open a URL and capture page content, console logs, and network activity (e.g., `vibe-tools browser open "https://example.com" --html`)
`vibe-tools browser act "<instruction>" --url=<url | 'current'> [options]` - Execute actions on a webpage using natural language instructions (e.g., `vibe-tools browser act "Click Login" --url=https://example.com`)
`vibe-tools browser observe "<instruction>" --url=<url> [options]` - Observe interactive elements on a webpage and suggest possible actions (e.g., `vibe-tools browser observe "interactive elements" --url=https://example.com`)
`vibe-tools browser extract "<instruction>" --url=<url> [options]` - Extract data from a webpage based on natural language instructions (e.g., `vibe-tools browser extract "product names" --url=https://example.com/products`)

**Notes on Browser Commands:**
- All browser commands are stateless unless --connect-to is used to connect to a long-lived interactive session. In disconnected mode each command starts with a fresh browser instance and closes it when done.
- When using `--connect-to`, special URL values are supported:
  - `current`: Use the existing page without reloading
  - `reload-current`: Use the existing page and refresh it (useful in development)
  - If working interactively with a user you should always use --url=current unless you specifically want to navigate to a different page. Setting the url to anything else will cause a page refresh loosing current state.
- Multi step workflows involving state or combining multiple actions are supported in the `act` command using the pipe (|) separator (e.g., `vibe-tools browser act "Click Login | Type 'user@example.com' into email | Click Submit" --url=https://example.com`)
- Video recording is available for all browser commands using the `--video=<directory>` option. This will save a video of the entire browser interaction at 1280x720 resolution. The video file will be saved in the specified directory with a timestamp.
- DO NOT ask browser act to "wait" for anything, the wait command is currently disabled in Stagehand.

**Tool Recommendations:**
- `vibe-tools web` is best for general web information not specific to the repository. Generally call this without additional arguments.
- `vibe-tools repo` is ideal for repository-specific questions, planning, code review and debugging. E.g. `vibe-tools repo "Review recent changes to command error handling looking for mistakes, omissions and improvements"`. Generally call this without additional arguments.
- `vibe-tools plan` is ideal for planning tasks. E.g. `vibe-tools plan "Adding authentication with social login using Google and Github"`. Generally call this without additional arguments.
- `vibe-tools doc` generates documentation for local or remote repositories.
- `vibe-tools youtube` analyzes YouTube videos to generate summaries, transcripts, implementation plans, or custom analyses
- `vibe-tools browser` is useful for testing and debugging web apps and uses Stagehand
- `vibe-tools mcp` enables interaction with specialized tools through MCP servers (e.g., for Git operations, file system tasks, or custom tools)

**Running Commands:**
1. Use `vibe-tools <command>` to execute commands (make sure vibe-tools is installed globally using npm install -g vibe-tools so that it is in your PATH)

**General Command Options (Supported by all commands):**
--provider=<provider>: AI provider to use (openai, anthropic, perplexity, gemini, openrouter, modelbox, or xai). If provider is not specified, the default provider for that task will be used.
--model=<model name>: Specify an alternative AI model to use. If model is not specified, the provider's default model for that task will be used.
--max-tokens=<number>: Control response length
--save-to=<file path>: Save command output to a file (in *addition* to displaying it)
--help: View all available options (help is not fully implemented yet)
--debug: Show detailed logs and error information

**Repository Command Options:**
--provider=<provider>: AI provider to use (gemini, openai, openrouter, perplexity, modelbox, anthropic, or xai)
--model=<model>: Model to use for repository analysis
--max-tokens=<number>: Maximum tokens for response
--from-github=<GitHub username>/<repository name>[@<branch>]: Analyze a remote GitHub repository without cloning it locally
--subdir=<path>: Analyze a specific subdirectory instead of the entire repository
--with-doc=<doc_url>: Fetch content from a document URL and include it as context

**Documentation Command Options:**
--from-github=<GitHub username>/<repository name>[@<branch>]: Generate documentation for a remote GitHub repository
--provider=<provider>: AI provider to use (gemini, openai, openrouter, perplexity, modelbox, anthropic, or xai)
--model=<model>: Model to use for documentation generation
--max-tokens=<number>: Maximum tokens for response
--with-doc=<doc_url>: Fetch content from a document URL and include it as context

**YouTube Command Options:**
--type=<summary|transcript|plan|review|custom>: Type of analysis to perform (default: summary)

**GitHub Command Options:**
--from-github=<GitHub username>/<repository name>[@<branch>]: Access PRs/issues from a specific GitHub repository

**Browser Command Options (for 'open', 'act', 'observe', 'extract'):**
--console: Capture browser console logs (enabled by default, use --no-console to disable)
--html: Capture page HTML content (disabled by default)
--network: Capture network activity (enabled by default, use --no-network to disable)
--screenshot=<file path>: Save a screenshot of the page
--timeout=<milliseconds>: Set navigation timeout (default: 120000ms for Stagehand operations, 30000ms for navigation)
--viewport=<width>x<height>: Set viewport size (e.g., 1280x720). When using --connect-to, viewport is only changed if this option is explicitly provided
--headless: Run browser in headless mode (default: true)
--no-headless: Show browser UI (non-headless mode) for debugging
--connect-to=<port>: Connect to existing Chrome instance. Special values: 'current' (use existing page), 'reload-current' (refresh existing page)
--wait=<time:duration or selector:css-selector>: Wait after page load (e.g., 'time:5s', 'selector:#element-id')
--video=<directory>: Save a video recording (1280x720 resolution, timestamped subdirectory). Not available when using --connect-to
--url=<url>: Required for `act`, `observe`, and `extract` commands. Url to navigate to before the main command or one of the special values 'current' (to stay on the current page without navigating or reloading) or 'reload-current' (to reload the current page)
--evaluate=<string>: JavaScript code to execute in the browser before the main command

**Nicknames**
Users can ask for these tools using nicknames
Gemini is a nickname for vibe-tools repo
Perplexity is a nickname for vibe-tools web
Stagehand is a nickname for vibe-tools browser
If people say "ask Gemini" or "ask Perplexity" or "ask Stagehand" they mean to use the `vibe-tools` command with the `repo`, `web`, or `browser` commands respectively.

**Xcode Commands:**
`vibe-tools xcode build [buildPath=<path>] [destination=<destination>]` - Build Xcode project and report errors.
**Build Command Options:**
--buildPath=<path>: (Optional) Specifies a custom directory for derived build data. Defaults to ./.build/DerivedData.
--destination=<destination>: (Optional) Specifies the destination for building the app (e.g., 'platform=iOS Simulator,name=iPhone 16 Pro'). Defaults to 'platform=iOS Simulator,name=iPhone 16 Pro'.

`vibe-tools xcode run [destination=<destination>]` - Build and run the Xcode project on a simulator.
**Run Command Options:**
--destination=<destination>: (Optional) Specifies the destination simulator (e.g., 'platform=iOS Simulator,name=iPhone 16 Pro'). Defaults to 'platform=iOS Simulator,name=iPhone 16 Pro'.

`vibe-tools xcode lint` - Run static analysis on the Xcode project to find and fix issues.

**Additional Notes:**
- For detailed information, see `node_modules/vibe-tools/README.md` (if installed locally).
- Configuration is in `vibe-tools.config.json` (or `~/.vibe-tools/config.json`).
- API keys are loaded from `.vibe-tools.env` (or `~/.vibe-tools/.env`).
- ClickUp commands require a `CLICKUP_API_TOKEN` to be set in your `.vibe-tools.env` file.
- Available models depend on your configured provider (OpenAI, Anthropic, xAI, etc.) in `vibe-tools.config.json`.
- repo has a limit of 2M tokens of context. The context can be reduced by filtering out files in a .repomixignore file.
- problems running browser commands may be because playwright is not installed. Recommend installing playwright globally.
- MCP commands require `ANTHROPIC_API_KEY` or `OPENROUTER_API_KEY`
- **Remember:** You're part of a team of superhuman expert AIs. Work together to solve complex problems.
- **Repomix Configuration:** You can customize which files are included/excluded during repository analysis by creating a `repomix.config.json` file in your project root. This file will be automatically detected by `repo`, `plan`, and `doc` commands.

<!-- vibe-tools-version: 0.60.6 -->
</vibe-tools Integration>
