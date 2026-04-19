# MCP Core Reference

## 1. What is MCP

Model Context Protocol (MCP) is an open-source standard for connecting AI applications to external systems — data sources, tools, and workflows. Think of it as a USB-C port for AI: one standard interface that works everywhere.

**Design goals:**
- Separate context-provision from LLM interaction
- Enable composable, reusable integrations
- Support both local (stdio) and remote (HTTP) servers
- Stateful protocol with capability negotiation
- Human-in-the-loop safety for tool calls and sampling

**Broad ecosystem:** Claude, ChatGPT, VS Code Copilot, Cursor, and many others all support MCP. Build once, integrate everywhere.

---

## 2. Architecture

### Participants

```
MCP Host (AI application)
├── MCP Client 1 ──── MCP Server A (local, stdio)
├── MCP Client 2 ──── MCP Server B (local, stdio)
└── MCP Client 3 ──── MCP Server C (remote, Streamable HTTP)
```

- **MCP Host**: The AI application (e.g., Claude Code, Claude Desktop, VS Code). Owns one MCP client per server connection.
- **MCP Client**: Component inside the host that maintains a dedicated connection to one server.
- **MCP Server**: Program (local or remote) that exposes tools, resources, and/or prompts.

One host can connect to many servers. One remote server can serve many clients simultaneously. Local stdio servers typically serve one client.

### Two Protocol Layers

**Data layer** — JSON-RPC 2.0 messages defining:
- Lifecycle management (init/shutdown)
- Server primitives: tools, resources, prompts
- Client primitives: sampling, elicitation, logging
- Utility: notifications, progress, cancellation

**Transport layer** — communication channels:
- stdio (local process)
- Streamable HTTP (remote, replaces old HTTP+SSE)

---

## 3. Core Primitives

### 3.1 Tools

Tools are **model-controlled** executable functions. The LLM decides when to call them based on context.

**Tool definition fields:**
- `name` — unique identifier (e.g., `get_weather`, `calculator_arithmetic`)
- `title` — optional human-readable display name
- `description` — what it does and when to use it
- `inputSchema` — JSON Schema for parameters
- `outputSchema` — optional JSON Schema for structured output
- `annotations` — behavioral hints (see below)

**Annotations (all optional, treated as untrusted hints):**
- `readOnlyHint: true` — does not modify state
- `destructiveHint: true` — may cause irreversible changes
- `idempotentHint: true` — safe to call multiple times with same args
- `openWorldHint: true` — interacts with external systems

**Tool list request/response:**
```json
// Request
{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{"cursor":"optional"}}

// Response
{
  "jsonrpc":"2.0","id":1,
  "result":{
    "tools":[{
      "name":"get_weather",
      "title":"Weather Info",
      "description":"Get current weather for a location",
      "inputSchema":{
        "type":"object",
        "properties":{"location":{"type":"string","description":"City name or zip"}},
        "required":["location"]
      }
    }],
    "nextCursor":"next-page-cursor"
  }
}
```

**Tool call request/response:**
```json
// Request
{
  "jsonrpc":"2.0","id":2,"method":"tools/call",
  "params":{"name":"get_weather","arguments":{"location":"New York"}}
}

// Success response
{
  "jsonrpc":"2.0","id":2,
  "result":{
    "content":[{"type":"text","text":"72°F, partly cloudy"}],
    "isError":false
  }
}

// Tool-level error (NOT a protocol error — LLM sees this)
{
  "jsonrpc":"2.0","id":3,
  "result":{
    "content":[{"type":"text","text":"API rate limit exceeded"}],
    "isError":true
  }
}

// Protocol-level error (unknown tool, invalid args, etc.)
{
  "jsonrpc":"2.0","id":4,
  "error":{"code":-32602,"message":"Unknown tool: bad_tool"}
}
```

**Structured output** — when `outputSchema` is provided:
```json
{
  "result":{
    "content":[{"type":"text","text":"{\"temp\":22.5,\"conditions\":\"Cloudy\"}"}],
    "structuredContent":{"temp":22.5,"conditions":"Cloudy"}
  }
}
```
Server MUST conform to outputSchema; client SHOULD validate.

**Tool result content types:**
- `text` — plain text
- `image` — base64-encoded, with `mimeType`
- `audio` — base64-encoded, with `mimeType`
- `resource_link` — URI reference to a resource (client fetches separately)
- `resource` (embedded) — full resource inline

**Security:** Always have a human in the loop. Show tool inputs to user before calling. Prompt for confirmation on destructive operations.

**List-changed notification:**
```json
{"jsonrpc":"2.0","method":"notifications/tools/list_changed"}
```
Only sent if server declared `"tools":{"listChanged":true}` in capabilities.

---

### 3.2 Resources

Resources are **application-controlled** data sources. The host decides which to fetch and include as context. Think of them like GET endpoints.

**Resource definition fields:**
- `uri` — unique identifier (e.g., `file:///project/src/main.rs`)
- `name` — display name
- `title` — optional human-readable name
- `description` — optional
- `mimeType` — optional (e.g., `text/x-rust`, `application/json`)
- `size` — optional byte count
- `annotations` — `audience` (`["user"]`, `["assistant"]`, or both), `priority` (0.0–1.0), `lastModified` (ISO 8601)

**Capability declaration:**
```json
{"capabilities":{"resources":{"subscribe":true,"listChanged":true}}}
```

**List resources:**
```json
// Request
{"jsonrpc":"2.0","id":1,"method":"resources/list","params":{"cursor":"optional"}}

// Response
{
  "result":{
    "resources":[{
      "uri":"file:///project/src/main.rs",
      "name":"main.rs",
      "title":"Main Application File",
      "mimeType":"text/x-rust"
    }],
    "nextCursor":"next-page-cursor"
  }
}
```

**Read resource:**
```json
// Request
{"jsonrpc":"2.0","id":2,"method":"resources/read","params":{"uri":"file:///project/src/main.rs"}}

// Response — text content
{
  "result":{
    "contents":[{
      "uri":"file:///project/src/main.rs",
      "mimeType":"text/x-rust",
      "text":"fn main() {\n    println!(\"Hello world!\");\n}"
    }]
  }
}

// Response — binary content
{
  "result":{
    "contents":[{
      "uri":"file:///image.png",
      "mimeType":"image/png",
      "blob":"base64-encoded-data"
    }]
  }
}
```

**Resource templates** (parameterized URIs per RFC 6570):
```json
// Request
{"jsonrpc":"2.0","id":3,"method":"resources/templates/list"}

// Response
{
  "result":{
    "resourceTemplates":[{
      "uriTemplate":"file:///{path}",
      "name":"Project Files",
      "description":"Access files in the project directory",
      "mimeType":"application/octet-stream"
    }]
  }
}
```

**Subscriptions** (if `subscribe: true`):
```json
// Subscribe
{"jsonrpc":"2.0","id":4,"method":"resources/subscribe","params":{"uri":"file:///project/src/main.rs"}}

// Server notifies on change
{"jsonrpc":"2.0","method":"notifications/resources/updated","params":{"uri":"file:///project/src/main.rs"}}
// Client then re-reads the resource
```

**Common URI schemes:** `file://` (filesystem-like), `https://` (web, client fetches directly), `git://` (version control), custom schemes per RFC 3986.

**Error codes:** Resource not found: `-32002`; Internal error: `-32603`.

---

### 3.3 Prompts

Prompts are **user-controlled** reusable templates. Users invoke them explicitly (e.g., as slash commands). Servers expose them; clients present them to users.

**Capability declaration:**
```json
{"capabilities":{"prompts":{"listChanged":true}}}
```

**List prompts:**
```json
// Request
{"jsonrpc":"2.0","id":1,"method":"prompts/list"}

// Response
{
  "result":{
    "prompts":[{
      "name":"code_review",
      "title":"Request Code Review",
      "description":"Analyze code quality and suggest improvements",
      "arguments":[{
        "name":"code",
        "description":"The code to review",
        "required":true
      }]
    }]
  }
}
```

**Get a prompt** (with argument substitution):
```json
// Request
{
  "jsonrpc":"2.0","id":2,"method":"prompts/get",
  "params":{
    "name":"code_review",
    "arguments":{"code":"def hello():\n    print('world')"}
  }
}

// Response
{
  "result":{
    "description":"Code review prompt",
    "messages":[{
      "role":"user",
      "content":{
        "type":"text",
        "text":"Please review this Python code:\ndef hello():\n    print('world')"
      }
    }]
  }
}
```

**PromptMessage content types:** `text`, `image` (base64), `audio` (base64), `resource` (embedded).

**Error codes:** Invalid prompt name or missing required args: `-32602`; Internal: `-32603`.

---

### 3.4 Sampling

Sampling lets **servers** request LLM completions from the client's AI application. The server doesn't need its own API key; it asks the client (which controls the LLM) to generate text.

This enables agentic behaviors: servers can call LLMs for sub-tasks without coupling to a specific model provider.

**Client capability declaration:**
```json
{"capabilities":{"sampling":{}}}
```

**Server sends `sampling/createMessage`:**
```json
// Request (server → client)
{
  "jsonrpc":"2.0","id":1,"method":"sampling/createMessage",
  "params":{
    "messages":[{
      "role":"user",
      "content":{"type":"text","text":"What is the capital of France?"}
    }],
    "modelPreferences":{
      "hints":[{"name":"claude-3-sonnet"}],
      "intelligencePriority":0.8,
      "speedPriority":0.5,
      "costPriority":0.3
    },
    "systemPrompt":"You are a helpful assistant.",
    "maxTokens":100
  }
}

// Response (client → server)
{
  "result":{
    "role":"assistant",
    "content":{"type":"text","text":"The capital of France is Paris."},
    "model":"claude-3-sonnet-20240307",
    "stopReason":"endTurn"
  }
}
```

**Model preferences:**
- `hints` — ordered list of model name substrings. Client maps to best available model.
- `costPriority` — 0–1, higher = prefer cheaper
- `speedPriority` — 0–1, higher = prefer faster
- `intelligencePriority` — 0–1, higher = prefer more capable

**Security:** Human-in-the-loop MUST be possible. Clients should show requests and responses to users before forwarding.

---

### 3.5 Roots

Roots define filesystem boundaries for servers — which directories a server has access to. Servers query clients for roots to understand their scope.

**Client capability declaration:**
```json
{"capabilities":{"roots":{"listChanged":true}}}
```

**Server requests roots:**
```json
// Request (server → client)
{"jsonrpc":"2.0","id":1,"method":"roots/list"}

// Response (client → server)
{
  "result":{
    "roots":[{
      "uri":"file:///home/user/projects/myproject",
      "name":"My Project"
    }]
  }
}
```

Root URIs MUST be `file://` URIs in current spec. When roots change, the client sends:
```json
{"jsonrpc":"2.0","method":"notifications/roots/list_changed"}
```

**Use case:** A coding assistant server checks roots before accessing files, respects project boundaries, scopes file operations.

---

## 4. Protocol Lifecycle

### Initialize / Initialized Handshake

The `initialize` request MUST be the first message. It MUST NOT be part of a JSON-RPC batch.

```json
// Client → Server
{
  "jsonrpc":"2.0","id":1,"method":"initialize",
  "params":{
    "protocolVersion":"2025-03-26",
    "capabilities":{
      "roots":{"listChanged":true},
      "sampling":{}
    },
    "clientInfo":{"name":"ExampleClient","version":"1.0.0"}
  }
}

// Server → Client
{
  "jsonrpc":"2.0","id":1,
  "result":{
    "protocolVersion":"2025-03-26",
    "capabilities":{
      "logging":{},
      "prompts":{"listChanged":true},
      "resources":{"subscribe":true,"listChanged":true},
      "tools":{"listChanged":true},
      "completions":{}
    },
    "serverInfo":{"name":"ExampleServer","version":"1.0.0"},
    "instructions":"Optional instructions for the client"
  }
}

// Client → Server (after successful initialize)
{"jsonrpc":"2.0","method":"notifications/initialized"}
```

### Version Negotiation

Client sends the latest version it supports. Server responds with either:
- The same version (agreement), or
- A different version it supports

If the client doesn't support the server's version, it SHOULD disconnect.

Current stable version: `2025-03-26`  
Latest (draft): `2025-06-18`

### Capability Table

| Who | Capability | Description |
|-----|-----------|-------------|
| Client | `roots` | Provides filesystem root dirs |
| Client | `sampling` | Handles LLM sampling requests |
| Client | `experimental` | Non-standard features |
| Server | `tools` | Exposes callable tools |
| Server | `resources` | Provides readable data |
| Server | `prompts` | Provides prompt templates |
| Server | `logging` | Emits log messages |
| Server | `completions` | Argument autocompletion |
| Server | `experimental` | Non-standard features |

Sub-capabilities: `listChanged` (tools/resources/prompts), `subscribe` (resources only).

### Ping

Either party can send a ping at any time to check liveness:
```json
// Request
{"jsonrpc":"2.0","id":99,"method":"ping"}
// Response
{"jsonrpc":"2.0","id":99,"result":{}}
```

### Cancellation

Either party can cancel an in-flight request:
```json
{
  "jsonrpc":"2.0",
  "method":"notifications/cancelled",
  "params":{"requestId":5,"reason":"User cancelled"}
}
```
The receiver SHOULD stop processing and MUST NOT send a response for that request.

### Progress Tracking

Servers can report progress on long-running operations:
```json
{
  "jsonrpc":"2.0",
  "method":"notifications/progress",
  "params":{
    "progressToken":"token-from-request",
    "progress":0.5,
    "total":1.0,
    "message":"Processing step 3 of 6"
  }
}
```
Clients include `_meta.progressToken` in request params to opt in. Receiving a progress notification may reset the request timeout clock.

### Shutdown

**stdio:** Client closes the server's stdin. Waits for exit, then sends SIGTERM, then SIGKILL.

**HTTP:** Close the HTTP connection(s).

No special shutdown messages defined in the protocol.

### Timeouts

Implementations SHOULD set per-request timeouts. On timeout, send a cancellation notification and stop waiting. SDKs should allow per-request timeout configuration. Always enforce a maximum timeout regardless of progress notifications.

### Initialization Error Example
```json
{
  "jsonrpc":"2.0","id":1,
  "error":{
    "code":-32602,
    "message":"Unsupported protocol version",
    "data":{"supported":["2024-11-05"],"requested":"1.0.0"}
  }
}
```

---

## 5. Transports

### 5.1 stdio

- Client **spawns** the server as a subprocess
- Client writes JSON-RPC messages to server's **stdin**
- Server writes JSON-RPC messages to server's **stdout**
- Messages delimited by newlines; MUST NOT contain embedded newlines
- Server MAY write UTF-8 logs to **stderr** (clients may capture or ignore)
- Server MUST NOT write non-MCP content to stdout
- Auth: credentials retrieved from environment variables (not the MCP auth spec)

Best for: local tools, scripts, CLI integrations, Claude Desktop, Claude Code.

### 5.2 Streamable HTTP (current standard, replaces HTTP+SSE)

Introduced in spec version `2025-03-26`. The server operates as an independent process with a single **MCP endpoint** (e.g., `https://example.com/mcp`) supporting both POST and GET.

**Client → Server messages:** HTTP POST to MCP endpoint
- `Accept: application/json, text/event-stream` header required
- Body is one JSON-RPC request, notification, or response
- For requests, server responds with either:
  - `Content-Type: application/json` — single JSON response
  - `Content-Type: text/event-stream` — SSE stream (may include multiple server messages before the response)
- For notifications/responses, server returns `202 Accepted`

**Server → Client messages:** Client opens GET to MCP endpoint
- `Accept: text/event-stream` header required
- Server returns SSE stream for server-initiated requests/notifications
- Or `405 Method Not Allowed` if not supported

**Session management:**
1. Server MAY return `Mcp-Session-Id` header in initialize response
2. Client MUST include `Mcp-Session-Id` on all subsequent requests
3. Client SHOULD send `DELETE` to MCP endpoint with session ID when done
4. `HTTP 404` on a session ID means session expired → re-initialize

**Protocol version header:**
```
MCP-Protocol-Version: 2025-03-26
```
Required on all subsequent requests after initialization.

**Resumability:** Server MAY attach `id` to SSE events. Client uses `Last-Event-ID` header on reconnect. Server MAY replay missed events.

**Security (critical):**
- Validate `Origin` header on all connections (prevent DNS rebinding)
- Bind locally to `127.0.0.1`, not `0.0.0.0`
- Implement proper authentication for all connections

### 5.3 HTTP+SSE (deprecated, was in 2024-11-05)

Two endpoints: one for POST (client→server), one for GET (SSE stream, server→client). Replaced by Streamable HTTP. Clients wanting backwards compat: try POST first; if 4xx, try GET for the old SSE endpoint.

### 5.4 Custom Transports

Implementations MAY add custom transports. Must preserve JSON-RPC message format and lifecycle requirements.

---

## 6. JSON-RPC Message Format

All messages MUST be UTF-8 encoded JSON-RPC 2.0.

**Request:**
```json
{"jsonrpc":"2.0","id":"string-or-integer","method":"method/name","params":{...}}
```
- ID MUST NOT be null
- ID MUST be unique per session for the requestor

**Response (success):**
```json
{"jsonrpc":"2.0","id":"same-as-request","result":{...}}
```

**Response (error):**
```json
{"jsonrpc":"2.0","id":"same-as-request","error":{"code":-32602,"message":"...","data":{...}}}
```

**Notification (no response expected):**
```json
{"jsonrpc":"2.0","method":"notifications/something","params":{...}}
```
No `id` field.

**Standard error codes:**
| Code | Meaning |
|------|---------|
| -32700 | Parse error |
| -32600 | Invalid request |
| -32601 | Method not found |
| -32602 | Invalid params |
| -32603 | Internal error |
| -32002 | Resource not found (MCP-specific) |

**Batching:** Implementations MAY send batches (JSON array). MUST support receiving batches. `initialize` MUST NOT be batched.
