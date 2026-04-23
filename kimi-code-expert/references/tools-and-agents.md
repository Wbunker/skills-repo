# Kimi Tool Use and Agents

## Function Calling

### Tool Definition

```json
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "Get current weather for a location",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {"type": "string", "description": "City name"},
        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
      },
      "required": ["location"]
    },
    "strict": true
  }
}
```

**Name constraint:** `^[a-zA-Z_][a-zA-Z0-9-_]{2,63}$`  
**Max tools per request:** 128  
**`strict: true` (default):** Model output must match the JSON schema exactly.  
**`strict: false`:** Only guarantees valid JSON — no schema enforcement.

### Agentic Loop Pattern

```python
async def agent_loop(client, messages, tools):
    while True:
        response = client.chat.completions.create(
            model="kimi-k2.6",
            messages=messages,
            tools=tools,
        )
        msg = response.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            return msg.content  # Final answer

        for call in msg.tool_calls:
            result = execute_tool(call.function.name, call.function.arguments)
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result),
            })
```

**Key:** Do not specify tools in the system prompt — let the model decide autonomously.

---

## Official Built-In Tools (12 total, all free)

Accessed via semantic URIs `moonshot/{tool-name}:latest`. Invoke via `POST /formulas/{FORMULA_URI}/fibers`.

| Tool | URI | Description |
|---|---|---|
| `web-search` | `moonshot/web-search:latest` | Real-time internet search |
| `fetch` | `moonshot/fetch:latest` | Extract URL content as Markdown |
| `code_runner` | `moonshot/code_runner:latest` | Python execution sandbox |
| `quickjs` | `moonshot/quickjs:latest` | JavaScript execution (sandboxed) |
| `excel` | `moonshot/excel:latest` | Analyze Excel and CSV files |
| `rethink` | `moonshot/rethink:latest` | Intelligent reasoning consolidation |
| `memory` | `moonshot/memory:latest` | Persistent cross-session storage |
| `date` | `moonshot/date:latest` | Date/time processing |
| `convert` | `moonshot/convert:latest` | Unit + currency conversions |
| `base64` | `moonshot/base64:latest` | Encoding/decoding |
| `random-choice` | `moonshot/random-choice:latest` | Random selection |
| `mew` | `moonshot/mew:latest` | Novelty/greeting function |

Tool results appear in `context.output` (standard) or `context.encrypted_output` (protected tools like web-search). Pass encrypted output directly to the model.

---

## Web Search (`$web_search`)

The `$web_search` builtin is declared as a builtin_function (not a regular function) and handled differently:

```python
tools = [
    {
        "type": "builtin_function",
        "function": {"name": "$web_search"},
    }
]
```

**Workflow:**
1. Submit query with `$web_search` in tools
2. Model responds `finish_reason=tool_calls`
3. Return `tool_call.function.arguments` **unchanged** back as `role=tool` message
4. Model generates final answer with `finish_reason=stop`

**Pricing:** $0.005 per successful call (when `finish_reason=tool_calls`).  
**Restriction:** Thinking must be **disabled** when using `$web_search`.

---

## Agent Swarm (Research Preview)

Parallel multi-agent orchestration at `kimi.com/agent-swarm`. Scales to 300 concurrent sub-agents.

**Demonstrated tasks:**
- 5 quantitative trading strategies across 100 assets → McKinsey-style PowerPoint + spreadsheets
- Single astrophysics paper → 40-page research report + 20,000-entry dataset + 14 charts
- 100 job listings → 100 customized resumes (100 concurrent sub-agents)

**Agent SDK:** Python, Node.js, Go at `github.com/MoonshotAI/kimi-agent-sdk`

---

## Agent System Prompt Engineering

Effective agent prompts include:
- Business role and goal definition
- Explicit output format (structure, charts, language requirements)
- Data sourcing standards
- Edge case handling rules

Example research agent prompt components: language consistency requirement, chart specification (matplotlib style), source citation standards, output section structure.

---

## Gotchas

- `tool_choice="required"` not supported — prompt-engineer instead
- `functions` parameter not supported — use `tools` only
- Don't include tool guidance in system prompt when using official tools — it interferes with autonomous tool selection
- web-search and thinking cannot be used simultaneously on kimi-k2.6
- For tool calling in thinking mode: include full `reasoning_content` from prior turns in context
