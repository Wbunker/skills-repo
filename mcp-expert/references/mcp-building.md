# MCP Building Reference — Servers and Clients

## Python SDK

### Installation

```bash
# Recommended: use uv
uv init my-mcp-server
cd my-mcp-server
uv add "mcp[cli]"

# Or pip
pip install "mcp[cli]"
```

Package: `mcp` on PyPI. Requires Python 3.10+.

### FastMCP (High-Level API)

FastMCP is the recommended way to build servers. It auto-generates schemas from type annotations, handles protocol details, and provides decorator-based registration.

**Minimal server:**
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My Server")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

if __name__ == "__main__":
    mcp.run()  # defaults to stdio
```

**Full example with tools, resources, and prompts:**
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Demo")

# --- Tools ---
@mcp.tool()
def get_weather(city: str, unit: str = "celsius") -> str:
    """Get weather for a city. Unit: celsius or fahrenheit."""
    # call external API here
    return f"Weather in {city}: 22 degrees {unit}"

@mcp.tool()
async def fetch_url(url: str) -> str:
    """Fetch content from a URL"""
    import httpx
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        return r.text

# --- Resources ---
@mcp.resource("config://settings")
def get_settings() -> str:
    """Application configuration"""
    return '{"theme":"dark","language":"en"}'

@mcp.resource("file://documents/{name}")
def read_document(name: str) -> str:
    """Read a document by name"""
    # read from disk
    return f"Content of {name}"

# --- Prompts ---
@mcp.prompt()
def code_review(code: str, language: str = "python") -> str:
    """Generate a code review prompt"""
    return f"Please review this {language} code and suggest improvements:\n\n{code}"

if __name__ == "__main__":
    mcp.run()  # stdio transport
```

**Running with HTTP transport:**
```python
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
    # Listens on http://localhost:8000/mcp by default
```

**Running stdio explicitly:**
```python
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Context Object

Tools and resources can receive a `Context` parameter for progress reporting, logging, and accessing session info:

```python
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession

mcp = FastMCP("Progress Demo")

@mcp.tool()
async def long_task(steps: int, ctx: Context[ServerSession, None]) -> str:
    """Run a multi-step task with progress"""
    await ctx.info(f"Starting {steps}-step task")
    for i in range(steps):
        await ctx.report_progress(
            progress=(i + 1) / steps,
            total=1.0,
            message=f"Step {i+1}/{steps}"
        )
        await ctx.debug(f"Completed step {i+1}")
    return "Done"
```

Context methods: `ctx.info()`, `ctx.debug()`, `ctx.warning()`, `ctx.error()`, `ctx.report_progress()`.

### Lifespan (Startup/Shutdown)

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from mcp.server.fastmcp import FastMCP, Context

class Database:
    @classmethod
    async def connect(cls): return cls()
    async def disconnect(self): pass
    def query(self, sql: str): return "result"

@dataclass
class AppContext:
    db: Database

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    db = await Database.connect()
    try:
        yield AppContext(db=db)
    finally:
        await db.disconnect()

mcp = FastMCP("DB Server", lifespan=app_lifespan)

@mcp.tool()
def run_query(sql: str, ctx: Context) -> str:
    """Run a database query"""
    db = ctx.request_context.lifespan_context.db
    return db.query(sql)
```

### Structured Output

FastMCP auto-generates output schemas from return type annotations:

```python
from pydantic import BaseModel

class WeatherResult(BaseModel):
    temperature: float
    conditions: str
    humidity: float

@mcp.tool()
def get_weather_data(location: str) -> WeatherResult:
    """Get structured weather data"""
    return WeatherResult(temperature=22.5, conditions="Cloudy", humidity=65.0)
```

Supported return types: Pydantic BaseModel, TypedDict, dataclasses, `dict[str, T]`, primitives (wrapped in `{"result": value}`).

### Low-Level Server API

When you need full control over the protocol:

```python
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.types as types

server = Server("low-level-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="my_tool",
            description="Does something",
            inputSchema={
                "type": "object",
                "properties": {"input": {"type": "string"}},
                "required": ["input"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "my_tool":
        return [types.TextContent(type="text", text=f"Got: {arguments['input']}")]
    raise ValueError(f"Unknown tool: {name}")

# Run stdio
import asyncio
from mcp.server.stdio import stdio_server

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, InitializationOptions(
            server_name="low-level-server",
            server_version="1.0.0",
            capabilities=server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={}
            )
        ))

asyncio.run(main())
```

### Mounting to ASGI (Streamable HTTP)

```python
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Mount

mcp = FastMCP("My Server")

# Mount at a path on an existing ASGI app
app = Starlette(routes=[
    Mount("/mcp", app=mcp.streamable_http_app()),
])
```

### Testing with MCP Inspector

```bash
# Start server, then in another terminal:
npx -y @modelcontextprotocol/inspector
# Connect to http://localhost:8000/mcp in the inspector UI
```

Or dev mode:
```bash
mcp dev server.py
```

---

## TypeScript SDK

### Installation

The TypeScript SDK is split into separate packages (v2 pre-alpha on `main`; v1.x is current stable):

```bash
# Server
npm install @modelcontextprotocol/server

# Client
npm install @modelcontextprotocol/client

# Optional middleware
npm install @modelcontextprotocol/node      # Node.js HTTP transport
npm install @modelcontextprotocol/express   # Express integration
npm install @modelcontextprotocol/hono      # Hono integration
```

**Legacy v1 (current stable):**
```bash
npm install @modelcontextprotocol/sdk
```

### McpServer — Complete Example

```typescript
import { randomUUID } from 'node:crypto';
import { McpServer, ResourceTemplate, StdioServerTransport } from '@modelcontextprotocol/server';
import { NodeStreamableHTTPServerTransport } from '@modelcontextprotocol/node';
import * as z from 'zod/v4';

const server = new McpServer(
    { name: 'my-server', version: '1.0.0' },
    { instructions: 'Call list_tables before running queries.' }
);

// --- Tools ---
server.registerTool(
    'calculate-bmi',
    {
        title: 'BMI Calculator',
        description: 'Calculate Body Mass Index',
        inputSchema: z.object({
            weightKg: z.number(),
            heightM: z.number()
        }),
        outputSchema: z.object({ bmi: z.number() })
    },
    async ({ weightKg, heightM }) => {
        const bmi = weightKg / (heightM * heightM);
        return {
            content: [{ type: 'text', text: JSON.stringify({ bmi }) }],
            structuredContent: { bmi }
        };
    }
);

// Tool with annotations
server.registerTool(
    'delete-file',
    {
        description: 'Delete a file',
        inputSchema: z.object({ path: z.string() }),
        annotations: { title: 'Delete File', destructiveHint: true, idempotentHint: true }
    },
    async ({ path }) => ({
        content: [{ type: 'text', text: `Deleted ${path}` }]
    })
);

// Tool with error handling
server.registerTool(
    'fetch-url',
    { description: 'Fetch a URL', inputSchema: z.object({ url: z.string() }) },
    async ({ url }) => {
        try {
            const res = await fetch(url);
            if (!res.ok) return {
                content: [{ type: 'text', text: `HTTP ${res.status}` }],
                isError: true
            };
            return { content: [{ type: 'text', text: await res.text() }] };
        } catch (e) {
            return {
                content: [{ type: 'text', text: `Error: ${e}` }],
                isError: true
            };
        }
    }
);

// --- Resources ---
// Static resource
server.registerResource(
    'config',
    'config://app',
    { title: 'App Config', mimeType: 'text/plain' },
    async (uri) => ({
        contents: [{ uri: uri.href, text: 'theme=dark\nlanguage=en' }]
    })
);

// Dynamic resource with template
server.registerResource(
    'user-profile',
    new ResourceTemplate('user://{userId}/profile', {
        list: async () => ({
            resources: [
                { uri: 'user://123/profile', name: 'Alice' },
                { uri: 'user://456/profile', name: 'Bob' }
            ]
        })
    }),
    { title: 'User Profile', mimeType: 'application/json' },
    async (uri, { userId }) => ({
        contents: [{ uri: uri.href, text: JSON.stringify({ userId, name: 'Example' }) }]
    })
);

// --- Prompts ---
server.registerPrompt(
    'review-code',
    {
        title: 'Code Review',
        description: 'Review code for best practices',
        argsSchema: z.object({ code: z.string(), language: z.string().default('python') })
    },
    ({ code, language }) => ({
        messages: [{
            role: 'user' as const,
            content: { type: 'text' as const, text: `Review this ${language}:\n\n${code}` }
        }]
    })
);

// --- Run with stdio ---
async function runStdio() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
}

// --- Run with Streamable HTTP ---
import express from 'express';
import { createMcpExpressApp } from '@modelcontextprotocol/express';

async function runHttp() {
    const app = express();
    app.use('/mcp', await createMcpExpressApp({
        server,
        transportFactory: () => new NodeStreamableHTTPServerTransport({
            sessionIdGenerator: () => randomUUID()
        })
    }));
    app.listen(8080);
    console.log('MCP server running at http://localhost:8080/mcp');
}
```

**Note on TypeScript structured output:** Use `type` aliases, not `interface`, for structuredContent types:
```typescript
type BmiResult = { bmi: number };    // OK — assignable
interface BmiResult { bmi: number }  // Error — no implicit index signature
```

---

## Building MCP Clients (Python)

```python
import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    def __init__(self):
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self, server_script: str):
        """Connect to a stdio MCP server"""
        command = "python" if server_script.endswith('.py') else "node"
        params = StdioServerParameters(command=command, args=[server_script])
        
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(params)
        )
        read, write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        await self.session.initialize()
        
        tools = await self.session.list_tools()
        print("Available tools:", [t.name for t in tools.tools])

    async def call_tool(self, name: str, args: dict):
        result = await self.session.call_tool(name, args)
        return result.content

    async def list_resources(self):
        response = await self.session.list_resources()
        return response.resources

    async def read_resource(self, uri: str):
        response = await self.session.read_resource(uri)
        return response.contents

    async def cleanup(self):
        await self.exit_stack.aclose()


# Full client with Anthropic API integration
from anthropic import Anthropic

class LLMClient(MCPClient):
    def __init__(self):
        super().__init__()
        self.anthropic = Anthropic()

    async def process_query(self, query: str) -> str:
        tools_resp = await self.session.list_tools()
        available_tools = [{
            "name": t.name,
            "description": t.description,
            "input_schema": t.inputSchema
        } for t in tools_resp.tools]

        messages = [{"role": "user", "content": query}]

        while True:
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=messages,
                tools=available_tools
            )

            if response.stop_reason != "tool_use":
                return response.content[0].text

            # Handle tool calls
            assistant_content = []
            tool_results = []
            for block in response.content:
                assistant_content.append(block)
                if block.type == "tool_use":
                    result = await self.session.call_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result.content
                    })

            messages.append({"role": "assistant", "content": assistant_content})
            messages.append({"role": "user", "content": tool_results})


async def main():
    client = LLMClient()
    try:
        await client.connect_to_server("server.py")
        response = await client.process_query("What's the weather in NYC?")
        print(response)
    finally:
        await client.cleanup()

asyncio.run(main())
```

**Connect to HTTP server:**
```python
from mcp.client.streamable_http import streamablehttp_client

async with streamablehttp_client("https://example.com/mcp") as (read, write, _):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()
```
