# Server Architecture
## FastAPI SSE Server, Tool Call Interception, Partial JSON Parser

---

## Full Server Implementation

```python
# server.py
import json
from pathlib import Path
import anthropic
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from tools import TOOLS
from system import SYSTEM_PROMPT

app = FastAPI()
client = anthropic.AsyncAnthropic()
GUIDELINES_DIR = Path(__file__).parent / "guidelines"


# ── Partial JSON Parser ────────────────────────────────────────────────────
def extract_widget_code(partial_json: str) -> str | None:
    """
    Extract widget_code from mid-stream (invalid) JSON.
    Claude streams tool arguments token by token — JSON is incomplete.
    Fast path: valid JSON. Slow path: manual string walk.
    """
    try:
        return json.loads(partial_json).get("widget_code")
    except json.JSONDecodeError:
        pass

    key = '"widget_code"'
    idx = partial_json.find(key)
    if idx == -1:
        return None

    rest = partial_json[idx + len(key):]
    colon = rest.find(':')
    if colon == -1:
        return None

    rest = rest[colon + 1:].lstrip()
    if not rest.startswith('"'):
        return None

    content = rest[1:]  # skip opening quote
    result = []
    i = 0
    while i < len(content):
        c = content[i]
        if c == '\\' and i + 1 < len(content):
            n = content[i + 1]
            escapes = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\',
                       '"': '"', '/': '/', 'b': '\b', 'f': '\f'}
            result.append(escapes.get(n, n))
            i += 2
        elif c == '"':
            break
        else:
            result.append(c)
            i += 1

    return ''.join(result) if result else None


def get_guidelines(modules: list[str]) -> str:
    """Lazy-load guideline markdown files on demand."""
    parts = []
    core = GUIDELINES_DIR / "core.md"
    if core.exists():
        parts.append(core.read_text())
    for module in modules:
        path = GUIDELINES_DIR / f"{module}.md"
        if path.exists():
            parts.append(path.read_text())
    return "\n\n---\n\n".join(parts)


def sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


# ── Request Schema ─────────────────────────────────────────────────────────
class Message(BaseModel):
    role: str
    content: str

class ChatBody(BaseModel):
    messages: list[Message]


# ── Main SSE Endpoint ──────────────────────────────────────────────────────
@app.post("/chat")
async def chat(body: ChatBody):
    async def generate():
        messages = [{"role": m.role, "content": m.content} for m in body.messages]

        while True:  # loop handles multi-turn tool use
            active_tool_calls: dict[int, dict] = {}
            current_text = ""

            try:
                async with client.messages.stream(
                    model="claude-opus-4-6",
                    max_tokens=8096,
                    system=SYSTEM_PROMPT,
                    tools=TOOLS,
                    messages=messages,
                ) as stream:

                    async for event in stream:

                        # New tool call block starting
                        if event.type == "content_block_start":
                            block = event.content_block
                            if block.type == "tool_use":
                                active_tool_calls[event.index] = {
                                    "id": block.id,
                                    "name": block.name,
                                    "partial_json": "",
                                }

                        elif event.type == "content_block_delta":
                            delta = event.delta

                            if delta.type == "text_delta":
                                current_text += delta.text
                                yield sse({"type": "text", "text": delta.text})

                            elif delta.type == "input_json_delta":
                                tc = active_tool_calls.get(event.index)
                                if tc:
                                    tc["partial_json"] += delta.partial_json
                                    # Stream partial HTML as it arrives
                                    if tc["name"] == "show_widget":
                                        html = extract_widget_code(tc["partial_json"])
                                        if html and len(html) > 15:
                                            yield sse({"type": "widget_delta", "html": html})

                    final_msg = await stream.get_final_message()

            except Exception as e:
                yield sse({"type": "error", "text": str(e)})
                return

            # Build assistant turn for conversation history
            assistant_content = []
            if current_text:
                assistant_content.append({"type": "text", "text": current_text})
            for block in final_msg.content:
                if block.type == "tool_use":
                    assistant_content.append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    })

            # If no tool use, we're done
            if final_msg.stop_reason != "tool_use":
                yield sse({"type": "done"})
                break

            # Process tool results and loop
            messages.append({"role": "assistant", "content": assistant_content})
            tool_results = []

            for block in final_msg.content:
                if block.type != "tool_use":
                    continue

                if block.name == "load_guidelines":
                    modules = block.input.get("modules", [])
                    content = get_guidelines(modules)
                    yield sse({"type": "status", "text": f"Loading {', '.join(modules)} guidelines..."})
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": content,
                    })

                elif block.name == "show_widget":
                    html = block.input.get("widget_code", "")
                    title = block.input.get("title", "widget").replace("_", " ")
                    yield sse({"type": "widget_final", "html": html, "title": title})
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": f"Widget '{title}' rendered successfully.",
                    })

            messages.append({"role": "user", "content": tool_results})
            # Loop: Claude sees tool results and continues

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # Critical for Nginx — prevents SSE buffering
        },
    )

app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

---

## Key Architectural Decisions

### Why SSE over WebSockets?

SSE is unidirectional (server → client), which matches the streaming use case exactly. It:
- Reconnects automatically on disconnect
- Works through HTTP/2 multiplexing
- Requires no handshake protocol
- Is simpler to implement and debug

WebSockets are bidirectional — use them only if you need client → server streaming (you don't; user input is handled by regular POST requests).

### The Tool Call Interception Loop

The `while True` loop is essential. Claude's tool use requires:
1. Claude streams a response with tool calls (`stop_reason == "tool_use"`)
2. Your server executes the tools and sends results back
3. Claude continues streaming (may call more tools or generate final text)

Without the loop, Claude never gets the tool results and the widget never renders.

### Why Partial JSON Parsing?

Claude streams tool arguments as JSON fragments, token by token:
```
{"widget_code": "<style>.calc {
{"widget_code": "<style>.calc { padding: 1rem; }
{"widget_code": "<style>.calc { padding: 1rem; }</style><div
```

None of these are valid JSON. The custom parser walks the string manually to extract the `widget_code` value as it grows, enabling rendering to begin long before the JSON completes.

**The `len(html) > 15` guard** prevents sending nearly-empty strings (like just `<style>`) before any real content exists.

### Conversation History Management

The `messages` list is the full conversation history passed to every API call. It must include:
- Original user messages
- Assistant turns (including tool_use blocks)
- Tool result turns (user role with tool_result content)

Omitting tool result turns causes `anthropic.BadRequestError`.

---

## Guidelines Directory Structure

```
guidelines/
├── core.md          # Base design rules — always loaded
├── chart.md         # Chart-specific: preferred libraries, data structure patterns
├── diagram.md       # SVG/flowchart patterns
├── interactive.md   # Form, calculator, slider patterns
└── mockup.md        # UI mockup/wireframe patterns
```

Claude calls `load_guidelines(["chart"])` before building a chart. The server reads `core.md` + `chart.md` and returns them as the tool result. Claude then has full design context only when building that type of widget — not loaded on every message.

---

## Adapting to Other Frameworks

The pattern translates directly to other stacks:

**Express.js (Node)**
```js
app.post('/chat', async (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('X-Accel-Buffering', 'no');

  const stream = await anthropic.messages.stream({ ... });
  for await (const event of stream) {
    // same event handling logic
    res.write(`data: ${JSON.stringify(payload)}\n\n`);
  }
  res.end();
});
```

**Django / Flask**
Use `StreamingHttpResponse` or Flask's `stream_with_context`. Same event structure.

**Next.js API Route (App Router)**
```ts
export async function POST(req: Request) {
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      // same loop, controller.enqueue(encoder.encode(`data: ...\n\n`))
    }
  });
  return new Response(stream, {
    headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache' }
  });
}
```
