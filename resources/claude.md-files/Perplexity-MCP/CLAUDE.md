# Perplexity MCP Server Guide

## Quick Start
1. **Install Dependencies**: `npm install`
2. **Set API Key**: Add to `.env` file or use environment variable:
   ```
   PERPLEXITY_API_KEY=your_api_key_here
   ```
3. **Run Server**: `node server.js`

## Claude Desktop Configuration
Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "perplexity": {
      "command": "node",
      "args": [
        "/absolute/path/to/perplexity-mcp/server.js"
      ],
      "env": {
        "PERPLEXITY_API_KEY": "your_perplexity_api_key"
      }
    }
  }
}
```

## NPM Global Installation
Run: `npm install -g .`

Then configure in Claude Desktop:
```json
{
  "mcpServers": {
    "perplexity": {
      "command": "npx",
      "args": [
        "perplexity-mcp"
      ],
      "env": {
        "PERPLEXITY_API_KEY": "your_perplexity_api_key"
      }
    }
  }
}
```

## NVM Users
If using NVM, you must use absolute paths to both node and the script:
```json
{
  "mcpServers": {
    "perplexity": {
      "command": "/Users/username/.nvm/versions/node/v16.x.x/bin/node",
      "args": [
        "/Users/username/path/to/perplexity-mcp/server.js"
      ],
      "env": {
        "PERPLEXITY_API_KEY": "your_perplexity_api_key"
      }
    }
  }
}
```

## Available Tools
- **perplexity_ask**: Send a single question to Perplexity
  - Default model: `llama-3.1-sonar-small-128k-online`
- **perplexity_chat**: Multi-turn conversation with Perplexity 
  - Default model: `mixtral-8x7b-instruct`

## Troubleshooting
- Check logs with `cat ~/.claude/logs/perplexity.log`
- Ensure your API key is valid and has not expired
- Validate your claude_desktop_config.json format
- Add verbose logging with the `DEBUG=1` environment variable

## Architecture
- Built with the MCP protocol
- Communication via stdio transport
- Lightweight proxy to Perplexity API