# Built-in Server-Side Tools

All built-in tools run on OpenAI's servers alongside the model. Available in the **Responses API** only (not in Chat Completions, which only supports client-side function calling).

Used in the Agents SDK as hosted tools with `OpenAIResponsesModel`.

---

## web_search_preview

Searches the live web and includes results in model context.

```json
{"type": "web_search_preview"}
```

```python
# Responses API
response = client.responses.create(
    model="gpt-4.1",
    input="What happened in AI news this week?",
    tools=[{"type": "web_search_preview"}]
)

# Agents SDK
from agents.tools import WebSearchTool
agent = Agent(name="Researcher", tools=[WebSearchTool()])
```

**Benchmarks:**
- GPT-4o search preview: 90% SimpleQA
- GPT-4o mini search preview: 88% SimpleQA

**What it returns:** Model integrates web results inline with citations. Same model powers ChatGPT Search.

---

## file_search

Searches uploaded files via vector stores. Supports semantic (embedding) and keyword search.

```json
{
  "type": "file_search",
  "vector_store_ids": ["vs_abc123"],
  "max_num_results": 20,
  "ranking_options": {
    "ranker": "auto",
    "score_threshold": 0.0
  }
}
```

```python
# Responses API
response = client.responses.create(
    model="gpt-4.1",
    input="What does the policy say about refunds?",
    tools=[{
        "type": "file_search",
        "vector_store_ids": ["vs_abc123"],
        "max_num_results": 10
    }]
)

# Agents SDK
from agents.tools import FileSearchTool
agent = Agent(tools=[FileSearchTool(vector_store_ids=["vs_abc123"])])
```

**Setup: Creating a vector store and uploading files**

```python
# Create vector store
vs = client.vector_stores.create(name="Product Docs")

# Upload files
with open("manual.pdf", "rb") as f:
    file = client.files.create(file=f, purpose="assistants")

client.vector_stores.files.create(
    vector_store_id=vs.id,
    file_id=file.id
)
# File is auto-parsed, chunked, embedded, and indexed
```

**Limits:**
- Up to 10,000 files per vector store
- Files are auto-parsed on upload
- Supported file types: PDF, DOCX, TXT, MD, code files, and more

---

## code_interpreter

Executes Python code in a secure sandboxed container.

```json
{"type": "code_interpreter"}
```

```python
# Responses API
response = client.responses.create(
    model="gpt-4.1",
    input="Analyze this CSV and give me a summary with a chart",
    tools=[{"type": "code_interpreter"}]
)

# Agents SDK
from agents.tools import CodeInterpreterTool
agent = Agent(tools=[CodeInterpreterTool()])
```

**Capabilities:**
- Run arbitrary Python code
- Access uploaded files
- Generate matplotlib/seaborn charts
- Parse and manipulate data (pandas, numpy, etc.)
- Solve mathematical problems step by step
- Convert file formats

**Use cases:** Data analysis, complex math, image processing, generating reports, solving coding problems.

---

## computer_use_preview

Enables the model to interact with graphical user interfaces via screenshots and simulated mouse/keyboard actions.

```json
{"type": "computer_use_preview"}
```

```python
# Responses API (with CUA model)
response = client.responses.create(
    model="computer-use-preview",
    input="Open the browser and search for the latest Python release",
    tools=[{"type": "computer_use_preview"}]
)

# Agents SDK
from agents.tools import ComputerTool

class MyComputer(AsyncComputer):
    async def screenshot(self) -> str:
        # Return base64 screenshot
        ...
    async def click(self, x: int, y: int, button: str = "left"):
        ...
    # ... other methods

agent = Agent(tools=[ComputerTool(computer=MyComputer())])
```

**Benchmarks (CUA model):**
- OSWorld (full computer): 38.1%
- WebArena (web tasks): 58.1%
- WebVoyager (web tasks): 87%

**How it works:** Model receives screenshots, outputs actions (click, type, scroll, key press). No custom API integration required — works with any GUI.

**Use cases:** Browser automation, form filling, web scraping, desktop application testing, multi-step web tasks.

---

## image_generation

Generates images using `gpt-image-1` as a tool within the model's response flow.

```json
{"type": "image_generation"}
```

```python
# Responses API
response = client.responses.create(
    model="gpt-4.1",
    input="Create a logo for a coffee shop called 'Morning Brew'",
    tools=[{"type": "image_generation"}]
)

# Agents SDK
from agents.tools import ImageGenerationTool
agent = Agent(tools=[ImageGenerationTool()])
```

**Capabilities:**
- Real-time streaming of generated images (shows progress)
- Multi-turn edits (iterative refinement: "make the logo more minimalist")
- Integrated with model reasoning — model decides when to generate
- Different from standalone `/v1/images/generations` endpoint

**Distinct from DALL-E 3 endpoint:** This tool uses `gpt-image-1` and integrates seamlessly into agent/response flows with streaming and edit support.

---

## Remote MCP (Model Context Protocol)

Connect to any external MCP server and expose its tools to the model.

```json
{
  "type": "mcp",
  "server_url": "https://mcp.example.com/sse",
  "server_label": "mytools",
  "require_approval": "auto",
  "headers": {
    "Authorization": "Bearer <token>"
  },
  "allowed_tools": ["tool_one", "tool_two"]
}
```

```python
# Responses API
response = client.responses.create(
    model="gpt-4.1",
    input="Search our database for customer #1234",
    tools=[{
        "type": "mcp",
        "server_url": "https://api.mycompany.com/mcp",
        "server_label": "company_db",
        "require_approval": "never",
        "headers": {"Authorization": f"Bearer {token}"}
    }]
)

# Agents SDK
from agents.tools import HostedMCPTool
agent = Agent(tools=[
    HostedMCPTool(
        server_url="https://api.mycompany.com/mcp",
        server_label="company_db"
    )
])
```

**Transport support:** Streamable HTTP, HTTP/SSE

**`require_approval` options:**
- `"always"` (default) — every tool call requires human approval
- `"never"` — no approval needed for any tool
- `"auto"` — approval required for some tools (per-tool configuration)

**Pricing:** Pay only for tokens used in tool definitions and calls. No per-call or connection fee.

**Supported models:** GPT-4o series, GPT-4.1 series, o1, o3, o3-mini, o4-mini

**Authentication:** Pass auth headers directly in the tool config. Server does not need to be publicly accessible — headers authenticate the request.

---

## Tool Availability Summary

| Tool | Responses API | Chat Completions | Agents SDK |
|------|--------------|-----------------|-----------|
| web_search_preview | Yes | No | Yes (WebSearchTool) |
| file_search | Yes | No | Yes (FileSearchTool) |
| code_interpreter | Yes | No | Yes (CodeInterpreterTool) |
| computer_use_preview | Yes | No | Yes (ComputerTool) |
| image_generation | Yes | No | Yes (ImageGenerationTool) |
| remote MCP | Yes | No | Yes (HostedMCPTool) |
| client function calling | Yes | Yes | Yes (@function_tool) |
