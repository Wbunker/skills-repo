# MCP — Authentication, Security, and Common Mistakes

## OAuth 2.1 for Remote MCP Servers

Authorization is **optional** but SHOULD be implemented for HTTP-based transports. stdio servers SHOULD NOT use this spec; they retrieve credentials from the environment.

### Standards Used

- OAuth 2.1 (draft-ietf-oauth-v2-1-13)
- OAuth 2.0 Authorization Server Metadata (RFC 8414)
- OAuth 2.0 Dynamic Client Registration (RFC 7591)
- OAuth 2.0 Protected Resource Metadata (RFC 9728)
- OAuth Client ID Metadata Documents (draft-ietf-oauth-client-id-metadata-document-00)

### Roles

- **MCP Server** = OAuth 2.1 Resource Server
- **MCP Client** = OAuth 2.1 Client
- **Authorization Server** = separate entity that issues tokens (may be co-hosted)

### High-Level Flow

```
1. Client → MCP Server: unauthenticated request
2. MCP Server → Client: 401 Unauthorized
   WWW-Authenticate: Bearer resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource"
3. Client → MCP Server: GET resource metadata URL
4. MCP Server → Client: Protected Resource Metadata JSON (includes authorization_servers)
5. Client discovers Authorization Server metadata (RFC 8414 / OIDC Discovery)
6. Client registers (or uses pre-registered credentials / Client ID Metadata Document)
7. Client → Auth Server: Authorization request (with PKCE + resource parameter)
8. Auth Server → User: Login/consent
9. Auth Server → Client: Authorization code
10. Client → Auth Server: Token request (with code_verifier)
11. Auth Server → Client: Access token (+ optional refresh token)
12. Client → MCP Server: Request with Authorization: Bearer <token>
13. MCP Server validates token, processes request
```

### Protected Resource Metadata Discovery

Servers MUST implement one of:
1. `WWW-Authenticate` header with `resource_metadata` URL (on 401 response)
2. Well-known URI: `https://example.com/.well-known/oauth-protected-resource` or `https://example.com/.well-known/oauth-protected-resource/mcp`

Example 401 response:
```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource",
                         scope="files:read"
```

### Client Registration Approaches (priority order)

1. **Pre-registered credentials** — hardcoded or user-entered client_id
2. **Client ID Metadata Documents** — client hosts JSON at an HTTPS URL used as client_id
3. **Dynamic Client Registration (RFC 7591)** — for backwards compat

**Client ID Metadata Document example:**
```json
{
  "client_id": "https://app.example.com/oauth/client-metadata.json",
  "client_name": "My MCP Client",
  "client_uri": "https://app.example.com",
  "redirect_uris": ["http://127.0.0.1:3000/callback"],
  "grant_types": ["authorization_code"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "none"
}
```
The `client_id` MUST match the URL exactly. Authorization server fetches and validates this document.

Authorization server indicates support via:
```json
{"client_id_metadata_document_supported": true}
```

### PKCE (Required)

All MCP clients MUST use PKCE with `S256` code challenge method:
```
code_verifier = random 43-128 char string
code_challenge = BASE64URL(SHA256(code_verifier))
```
If authorization server metadata lacks `code_challenge_methods_supported`, clients MUST refuse to proceed.

### Resource Parameter (Required)

Clients MUST include `resource` parameter in auth + token requests:
```
&resource=https%3A%2F%2Fmcp.example.com
```
This binds tokens to a specific MCP server, preventing misuse across services.

### Token Usage

```http
GET /mcp HTTP/1.1
Host: mcp.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
MCP-Protocol-Version: 2025-03-26
```

Rules:
- Token in `Authorization: Bearer` header on EVERY request
- NEVER in URI query string
- MCP servers MUST validate token audience (was it issued for THIS server?)
- MCP servers MUST NOT accept tokens issued for other services
- MCP servers MUST NOT pass through client tokens to upstream APIs (confused deputy)

### Scope Handling

Initial scope selection priority:
1. Use `scope` from `WWW-Authenticate` 401 header if provided
2. Use all scopes in `scopes_supported` from Protected Resource Metadata
3. Omit `scope` if `scopes_supported` undefined

**Insufficient scope (runtime):**
```http
HTTP/1.1 403 Forbidden
WWW-Authenticate: Bearer error="insufficient_scope",
                         scope="files:write",
                         resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource"
```

Client response: compute union of previously requested scopes + new required scopes → re-authorize.

### Refresh Tokens

- Clients MUST keep refresh tokens confidential in transit and storage
- Include `refresh_token` in `grant_types` client metadata
- May add `offline_access` to scope if AS supports it
- Protected resource servers SHOULD NOT include `offline_access` in scope challenges

### Error Codes

| Status | Meaning |
|--------|---------|
| 401 | Authorization required or token invalid |
| 403 | Insufficient scope |
| 400 | Malformed authorization request |

### Security Considerations

1. **DNS rebinding prevention:** Validate `Origin` header; bind local servers to 127.0.0.1
2. **Token theft:** Use short-lived tokens; rotate refresh tokens for public clients
3. **All auth server endpoints MUST use HTTPS**
4. **All redirect URIs MUST be localhost or HTTPS**
5. **Exact redirect URI matching** against pre-registered values
6. **State parameter:** Clients SHOULD use and verify state to prevent CSRF
7. **SSRF:** Authorization servers should protect against SSRF when fetching Client ID Metadata Documents

---

## Common Mistakes and Gotchas

### 1. Schema Validation Failures

**Problem:** Tool call rejected with `-32602 Invalid params`.

**Causes:**
- Extra properties not in `inputSchema` (add `"additionalProperties": false` if strict)
- Wrong type (string instead of number, etc.)
- Missing required field
- `null` where a value is required

**Fix:** Always validate against the tool's `inputSchema` before calling. When defining schemas, be explicit about required vs optional.

### 2. Transport Mismatches

**Problem:** Connection refused, 405 Method Not Allowed, or silent failures.

**Causes:**
- Trying HTTP transport against a stdio-only server
- Trying old HTTP+SSE against a Streamable HTTP server (or vice versa)
- Missing `Accept: application/json, text/event-stream` header
- Missing `MCP-Protocol-Version` header on requests after init

**Fix:**
- stdio servers: must be launched as subprocess
- Streamable HTTP: POST to single endpoint; include correct Accept and version headers
- To detect old vs new: try POST; if 405/404, try GET for SSE stream

### 3. Tool Naming Conventions

**Bad:** `get`, `query`, `do`, `run` (too generic)  
**Bad:** `GetWeatherCurrentConditionsForCity` (too verbose)  
**Good:** `get_weather`, `weather_current`, `calculator_arithmetic`

Rules:
- Lowercase with underscores (snake_case) preferred
- Descriptive but concise
- Names are unique within a server
- The `name` used in `tools/call` MUST exactly match the `name` from `tools/list`

### 4. Error Code Confusion

MCP has TWO error mechanisms for tools:

**Protocol errors** (JSON-RPC `error` field) — for infrastructure problems:
```json
{"error": {"code": -32602, "message": "Unknown tool: foo"}}
```
The LLM does NOT see these directly.

**Tool execution errors** (`isError: true` in result) — for business logic failures:
```json
{"result": {"content": [{"type": "text", "text": "File not found"}], "isError": true}}
```
The LLM DOES see these and can self-correct.

**Rule:** Use `isError: true` for things the LLM should know about (API failures, bad inputs, logic errors). Use protocol errors only for protocol/infrastructure failures (unknown tool name, invalid JSON, etc.).

### 5. Initialize Sequence Errors

- MUST NOT send any requests (except ping) before `initialize` completes
- MUST send `notifications/initialized` after receiving initialize response
- `initialize` MUST NOT be in a JSON-RPC batch
- Protocol version mismatch → disconnect

### 6. Capability Negotiation Mistakes

**Problem:** Calling a method the other side didn't advertise.

**Fix:** Check capabilities before using features:
- Only call `resources/subscribe` if server declared `"resources": {"subscribe": true}`
- Only call `sampling/createMessage` if client declared `"sampling": {}`
- Only send `notifications/tools/list_changed` if server declared `"tools": {"listChanged": true}`

### 7. Resource URI Pitfalls

- URIs must be valid per RFC 3986
- `file://` URIs for local files (not just `/path/to/file`)
- Don't use `https://` URIs for resources the client can't fetch directly
- Resource not found error code: `-32002` (not `-32601`)

### 8. Sampling Security

Servers that use `sampling/createMessage` can request arbitrary LLM calls. This is a significant trust escalation. Clients MUST:
- Show requests to users before forwarding
- Show responses before returning to server
- Allow users to deny requests

### 9. Streamable HTTP: Session Management

- After init, always include `Mcp-Session-Id` header if server provided one
- `404` response means session expired → start a new initialize
- Send `DELETE` to MCP endpoint when done to clean up server-side state
- Each `Mcp-Session-Id` should be cryptographically random (UUID, JWT, hash)

### 10. JSON Syntax in Config Files

Claude Code's `.mcp.json` and `~/.claude.json` are strict JSON:
- No trailing commas
- No comments
- All strings double-quoted
- Validate with a JSON linter before restarting

### 11. Tool Output Token Limits

Claude Code warns when MCP tool output exceeds 10,000 tokens. If your tool returns large data (file contents, search results), either:
- Paginate results
- Return summaries + offer resource links for full content
- Set `MAX_MCP_OUTPUT_TOKENS` env var for higher limit

### 12. Windows stdio + npx

On native Windows (not WSL), npx can't be executed directly:
```bash
# Wrong — causes "Connection closed"
claude mcp add myserver -- npx -y @some/package

# Correct
claude mcp add myserver -- cmd /c npx -y @some/package
```

### 13. Scope Changes in Claude Code

Old versions used different scope names:
- "project" scope is now called "local" (stored in ~/.claude.json)
- "global" scope is now called "user" (stored in ~/.claude.json)
- New "project" scope = `.mcp.json` in project root (shared with team)

---

## MCP Inspector (Development Tool)

```bash
# Install and run
npx -y @modelcontextprotocol/inspector

# Or with a specific server
npx @modelcontextprotocol/inspector python server.py

# Connect in browser at http://127.0.0.1:6274
```

Use the inspector to:
- Test tool calls interactively
- Browse resources
- Inspect protocol messages
- Validate server responses

---

## Reference: All Protocol Methods

### Server-side (client → server)
- `initialize` — start handshake
- `tools/list` — discover tools
- `tools/call` — invoke a tool
- `resources/list` — discover resources
- `resources/templates/list` — discover resource templates
- `resources/read` — read a resource
- `resources/subscribe` — subscribe to resource changes
- `resources/unsubscribe` — unsubscribe
- `prompts/list` — discover prompts
- `prompts/get` — get a prompt with arguments
- `completion/complete` — argument autocompletion
- `ping` — liveness check
- `logging/setLevel` — set log level

### Client-side (server → client)
- `sampling/createMessage` — request LLM completion
- `elicitation/create` — request user input
- `roots/list` — get filesystem roots
- `ping` — liveness check

### Notifications (no response expected)
- `notifications/initialized` — client ready (client → server)
- `notifications/cancelled` — cancel in-flight request (either direction)
- `notifications/progress` — progress update (either direction)
- `notifications/tools/list_changed` — tools updated (server → client)
- `notifications/resources/list_changed` — resources updated (server → client)
- `notifications/resources/updated` — specific resource changed (server → client)
- `notifications/prompts/list_changed` — prompts updated (server → client)
- `notifications/roots/list_changed` — roots changed (client → server)
- `notifications/message` — log message (server → client)
