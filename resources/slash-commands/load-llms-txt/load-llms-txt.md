# Load llms.txt

Load external context from an `llms.txt` file so Claude understands a library or API you're working with.

## Usage

- `/load-llms-txt <URL>` -- fetch and load context from a specific URL
- `/load-llms-txt` -- look for an `llms.txt` in the current project root

## Behavior

1. **Fetch the file:**
   - If a URL is provided in `$ARGUMENTS`, fetch it with `curl -s`
   - If no URL is provided, check for `llms.txt` or `llms-full.txt` in the project root
   - If neither exists, tell the user: "No llms.txt found. Provide a URL or add one to your project root."

2. **Read and summarize** the contents. Typical `llms.txt` files contain:
   - Project name and description
   - API reference or key concepts
   - Code examples and patterns
   - Links to detailed docs

3. **Confirm what was loaded:**
   ```
   Loaded context for [project/library name].
   Key topics: [list main sections]
   I'll use this as reference for our conversation.
   ```

4. **Retain the context** for the rest of the conversation. When the user asks questions or requests code that relates to the loaded library, reference the `llms.txt` content for accurate patterns and API usage.

## What is llms.txt?

`llms.txt` is a convention where projects provide a plain-text summary of their documentation optimized for LLM consumption. Many open-source projects publish one at their repo root or at `https://project.dev/llms.txt`. See https://llmstxt.org for the specification.
