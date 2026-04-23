---
name: zhipuai-glm-mcp-tools
description: MCP tools included in Z.ai GLM Coding Plan — Web Search, Web Reader, Zread, and Vision Understanding. Covers what each tool does, plan quotas, configuration, and effective use patterns in coding sessions.
type: reference
---

# Z.ai GLM Coding Plan — MCP Tools

All GLM Coding Plan tiers include built-in MCP (Model Context Protocol) tools that extend the model's capabilities during coding sessions. No separate MCP server setup is required — they're provisioned with your plan.

## Included MCP Tools

| Tool | What It Does | Quota |
|------|-------------|-------|
| **Web Search MCP** | Live web searches from within coding sessions | 100/1K/4K searches/month (Lite/Pro/Max) |
| **Web Reader MCP** | Fetch and read URLs, documentation pages, articles | Shares web search quota |
| **Zread MCP** | Read GitHub repos and technical reference content | Shares web search quota |
| **Vision Understanding** | Analyze screenshots, UI mockups, diagrams | Shares 5-hour prompt pool |

---

## Web Search MCP

### What It Does
Runs a live web search and injects results into the model's context. Useful for:
- Finding current library documentation
- Looking up error messages or stack traces
- Checking API changelogs
- Researching unfamiliar frameworks

### Quota
- Lite: 100 searches/month
- Pro: 1,000 searches/month
- Max: 4,000 searches/month

### Usage Pattern
The model invokes this automatically when it determines a search would help. You can also explicitly ask:
> "Search for the latest changelog for [library] and summarize breaking changes."

### Conservation Tips
- Don't trigger search loops — the model may search repeatedly if given open-ended research tasks
- Prefer providing documentation URLs directly (Web Reader is more efficient than repeated searches)
- Use searches for freshness-sensitive queries only; static knowledge doesn't need a search

---

## Web Reader MCP

### What It Does
Fetches and reads the content of a specific URL, converting it to text the model can reason over. Useful for:
- Reading official documentation pages
- Pulling in README files from GitHub
- Loading OpenAPI/Swagger specs
- Reading error pages or blog posts referenced in Stack Overflow answers

### Usage Pattern
Paste a URL and ask the model to read and apply it:
> "Read https://docs.example.com/api and implement the authentication flow."

---

## Zread MCP

### What It Does
Specialized reader for GitHub repositories and technical reference content. Can browse repo structure, read source files, and understand codebases.

### Usage Pattern
> "Using Zread, look at the source of [repo URL] and show me how they implement pagination."

### Coding Use Cases
- Understanding how a dependency works internally
- Checking if a library supports a specific feature before adding it
- Reading example implementations in open-source repos

---

## Vision Understanding

### What It Does
Accepts image input (screenshots, diagrams, UI mockups, error screenshots) and reasons about them. Useful for:
- Describing a UI that needs to be implemented
- Reading an architecture diagram and generating code
- Analyzing a screenshot of an error or test failure
- Converting a wireframe to component structure

### Quota
Vision calls share the same 5-hour prompt pool as text requests. A single vision call may consume more of the prompt budget than a text call.

### Usage Pattern in Claude Code
Pass image paths or paste images when supported by your tool. For Claude Code:
> "Here's a screenshot of the error. What's wrong?" (attach image)

### Conservation Tips
- Prefer text descriptions for simple layouts — only use Vision when visual context genuinely matters
- Don't run Vision in loops (e.g., "check each screenshot for UI issues") — it burns quota fast
- Use Vision for the initial understanding pass, then switch to text for implementation details

---

## Enabling MCP Tools in Claude Code

MCP tools provided by Z.ai are available automatically when using the GLM Coding Plan API endpoint. No additional MCP server configuration is required.

If you want to verify they're active, check the tool list in your coding session, or ask the model:
> "What tools do you have available?"

---

## Combining MCP Tools Effectively

Example workflow for implementing a feature from docs:
1. **Zread** the relevant repo to understand existing patterns
2. **Web Reader** to pull in official documentation for the API you're integrating
3. **Web Search** to check for any known issues or recent breaking changes
4. **Vision** to analyze any design mockups provided
5. Implement with GLM-4.7 for iteration speed, switch to GLM-5.1 if the problem gets complex

This combination eliminates context-switching out of the coding environment entirely.
