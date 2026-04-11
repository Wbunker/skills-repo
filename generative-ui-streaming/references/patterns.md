# Generative UI Patterns
## Three Approaches, Ecosystem Frameworks, When to Use Each

---

## The Three Patterns

### Open-Ended (What This Skill Covers in Depth)

Agent generates arbitrary HTML/CSS/JS inside a tool call argument. The system intercepts streaming JSON and renders the HTML fragment live.

**Pros:** Maximum flexibility; complex interactive widgets; Claude handles layout decisions
**Cons:** Inconsistent styling without enforced design tokens; security boundary requires care; hardest to implement

**Use when:** Custom calculators, games, data visualizations, dashboards with complex interactivity, anything Claude needs to design from scratch.

**Implementation:** See [architecture.md](architecture.md), [frontend.md](frontend.md), [tool-schemas.md](tool-schemas.md)

---

### Declarative (Structured JSON → Your Components)

Agent returns a JSON specification that describes UI elements. Your renderer maps the spec to your own styled components.

```
Claude outputs:
{
  "type": "dashboard",
  "components": [
    { "type": "metric-card", "label": "Revenue", "value": "$42,000", "trend": "+12%" },
    { "type": "bar-chart", "title": "Monthly Sales", "data": [...] }
  ]
}

Your renderer maps:
{ "type": "metric-card" } → <MetricCard label="Revenue" value="$42,000" trend="+12%" />
```

**Pros:** Perfect brand consistency (your components, your styles); validated output (schema validation before render); works in any framework (React, Vue, Svelte, native); safer than arbitrary HTML
**Cons:** Limited to components you've defined; requires upfront component library investment; less flexibility for novel layouts

**Use when:** You have an existing component library; brand consistency is critical; you need multi-framework support; you want validated output.

**Vercel json-render** (13K stars, Jan 2026) is the leading implementation:
- Define component catalog with Zod schemas
- AI generates JSON within those schemas
- Renderer validates, then maps to your actual components
- Supports React, Vue, Svelte, Solid, React Native from one definition
- Renders progressively as the model streams

```ts
// Define catalog
const catalog = {
  MetricCard: z.object({
    label: z.string(),
    value: z.string(),
    trend: z.string().optional()
  }),
  BarChart: z.object({
    title: z.string(),
    data: z.array(z.object({ label: z.string(), value: z.number() }))
  })
};

// AI generates within these schemas, renderer validates before display
```

---

### Static (Agent Selects Pre-Built Components)

Agent picks from a fixed set of pre-built components and populates their data. The agent never controls layout or styling.

```
Agent says: "use the SalesChart component with this data: [...]"
Your system renders: <SalesChart data={...} />   // your full-fidelity component
```

**Pros:** Highest visual quality (hand-crafted components); maximum control; zero styling inconsistency risk; agents can't produce malformed UI
**Cons:** Can only do what you've pre-built; requires agents to learn your component vocabulary; limited flexibility

**Use when:** Mission-critical UI surfaces; regulated industries; existing design system with high-fidelity components; you know the full set of UI patterns you need.

**CopilotKit / AG-UI `useFrontendTool`:**
```tsx
useFrontendTool({
  name: "show_sales_chart",
  description: "Display a bar chart of sales data",
  parameters: z.object({
    data: z.array(z.object({ month: z.string(), revenue: z.number() })),
    title: z.string()
  }),
  render: ({ data, title }) => <SalesChart data={data} title={title} />
});
```

The agent calls `show_sales_chart` with data; your React component renders it. The agent never sees or controls the component's HTML.

---

## Comparison Table

| | Open-Ended | Declarative | Static |
|---|---|---|---|
| Agent controls | Everything | Layout spec | Only data |
| Your control | Design tokens only | Component library | Full component |
| Consistency | Variable (needs tokens) | Good | Perfect |
| Flexibility | Unlimited | Medium | Fixed |
| Implementation | Most complex | Medium | Simplest |
| Security risk | Highest | Low | None |
| Best for | Novel/creative UI | Flexible bounded UI | Known UI patterns |

---

## AG-UI Protocol (Emerging Standard)

AG-UI (Agent-User Interaction Protocol) is an open protocol for bidirectional real-time streaming between agents and UIs, developed by CopilotKit with LangGraph and CrewAI.

It standardizes what sausi-7 implemented custom:

| Event | What it carries |
|-------|----------------|
| `TEXT_MESSAGE_CONTENT` | Streaming text deltas |
| `TOOL_CALL_START` | Tool name + ID |
| `TOOL_CALL_ARGS_DELTA` | Partial JSON arguments (enables arg pre-fill) |
| `TOOL_CALL_END` | Tool call complete |
| `STATE_DELTA` | Agent state updates |
| `RUN_FINISHED` | Stream complete |

**Unique capability:** `TOOL_CALL_ARGS_DELTA` allows the UI to pre-fill form fields as Claude is still generating the tool arguments. Example: a flight search form starts populating as Claude figures out the destination, before the full tool call is assembled.

**Use AG-UI when:** Building a new agentic product from scratch; need interoperability with LangGraph/CrewAI agents; want a maintained protocol rather than custom SSE implementation.

**Use custom SSE when:** Simpler stack; tighter control; don't need the full AG-UI feature set.

---

## Framework Selection Guide

```
What are you building?
├── Embedding UI generation in an existing product
│   ├── Have a component library → Declarative (json-render or AG-UI useFrontendTool)
│   └── Need novel layouts → Open-ended (this skill's approach)
├── Building a new AI-first product from scratch
│   ├── Need LangGraph/CrewAI integration → AG-UI + CopilotKit
│   └── Simple stack → Custom SSE (sausi-7 approach)
├── Using Next.js / Vercel
│   ├── AI SDK RSC streamUI → Note: RSC development is paused; use AI SDK UI instead
│   └── Vercel json-render → Declarative, multi-framework, Zod-validated
└── Prototyping / exploring
    └── claude.ai Artifacts panel → No code needed; built-in
```

---

## Vercel AI SDK (AI SDK UI vs AI SDK RSC)

**AI SDK UI** (stable, recommended for production):
- `useChat` hook handles streaming, history management
- Works with any backend (OpenAI, Anthropic, etc.)
- No React Server Components required

```tsx
const { messages, input, handleSubmit } = useChat({
  api: '/api/chat',
});
```

**AI SDK RSC** (experimental, development paused as of 2025):
- `streamUI` / `useUIState` — stream React Server Components directly
- Not recommended for new production projects
- Migrate existing RSC implementations to AI SDK UI

---

## Production Considerations

**Rate limiting** — Widget generation is expensive (Claude writes 100-400 lines of code per widget). Rate limit `/chat` to prevent abuse.

**Session management** — The conversation history grows with every turn. After ~20 turns with multiple widgets, history can exceed 50K tokens. Implement a summarization step or sliding window.

**Error recovery** — Partial widgets (Claude interrupted mid-stream) may render broken HTML. Always wrap `runScripts()` in try/catch. On error, show the last good render.

**Widget sandboxing** — The open-ended approach injects arbitrary HTML into your page DOM. Mitigate with:
- CSP headers (CDN allowlist)
- No `eval()` or `new Function()` in widget context
- Consider iframes for full sandboxing (loses CSS variable inheritance, requires postMessage)

**Token costs** — A complex interactive widget costs $0.05-0.30 per generation with Claude Opus 4.6. Cache common widgets server-side by hashing the user's request.

**Streaming cutoff** — If the user navigates away mid-stream, the SSE connection closes but the server's `generate()` coroutine keeps running (burning tokens). Detect client disconnect with request lifecycle hooks and cancel the API stream.

```python
# FastAPI disconnect detection
async def generate():
    try:
        async with client.messages.stream(...) as stream:
            async for event in stream:
                if await request.is_disconnected():
                    break
                # ... yield events
    except asyncio.CancelledError:
        pass  # Client disconnected
```
