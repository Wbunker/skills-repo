# OpenAI Agents SDK

Python-first framework for building multi-agent workflows. TypeScript version also available (2026).

## Install

```bash
pip install openai-agents
```

## Design Philosophy

"Enough features to be worth using, few enough primitives to learn quickly." Uses native Python features rather than new abstractions. No new concepts to learn beyond Python itself.

---

## Core Primitives

### 1. Agents

An Agent is an LLM with instructions, tools, handoffs, and guardrails.

```python
from agents import Agent, Runner

agent = Agent(
    name="Support Agent",
    instructions="You are a helpful customer support assistant.",
    model="gpt-4.1",          # optional; defaults to environment setting
    tools=[get_weather],       # function tools or hosted tools
    handoffs=[billing_agent],  # other agents to delegate to
    input_guardrails=[safety_check],
    output_guardrails=[quality_check]
)

# Synchronous run
result = Runner.run_sync(agent, "What are your business hours?")
print(result.final_output)

# Async run
result = await Runner.run(agent, "What are your business hours?")

# Streaming run
result = Runner.run_streamed(agent, "What are your business hours?")
async for event in result.stream_events():
    ...
```

---

### 2. Tools

Five categories of tools:

#### Function Tools (client-side, run locally)

```python
from agents import function_tool

@function_tool
def get_weather(city: str, unit: str = "celsius") -> str:
    """Get current weather for a city.
    
    Args:
        city: The city name to get weather for.
        unit: Temperature unit, either celsius or fahrenheit.
    """
    return f"20°{unit[0].upper()} and sunny in {city}"
```

- Schema extracted automatically from type hints and docstrings
- Supports Pydantic models and TypedDicts for complex inputs
- Supports async functions
- Configurable timeouts

#### Hosted OpenAI Tools (server-side, via OpenAIResponsesModel)

```python
from agents.tools import WebSearchTool, FileSearchTool, CodeInterpreterTool
from agents.tools import HostedMCPTool, ImageGenerationTool

agent = Agent(
    name="Research Agent",
    tools=[
        WebSearchTool(),
        FileSearchTool(vector_store_ids=["vs_abc123"], max_num_results=10),
        CodeInterpreterTool(),
        ImageGenerationTool(),
        HostedMCPTool(
            server_url="https://mcp.example.com",
            server_label="mytools"
        )
    ]
)
```

#### Agents as Tools

```python
# Expose an agent as a tool without transferring conversation control
summarizer_tool = summarizer_agent.as_tool(
    tool_name="summarize_document",
    tool_description="Summarize a long document into key points"
)

main_agent = Agent(name="Main", tools=[summarizer_tool])
```

#### Local Runtime Tools

```python
from agents.tools import ShellTool, ComputerTool, ApplyPatchTool, LocalShellTool

agent = Agent(name="Coding Agent", tools=[ShellTool(), ApplyPatchTool()])
```

#### Codex Tool (Experimental)

Delegates workspace-scoped coding tasks to Codex CLI:
```python
from agents.tools import CodexTool

tool = CodexTool(
    sandbox_mode="auto",
    working_directory="/path/to/repo",
    persist_session=True,
    web_search=True
)
```

---

### 3. Handoffs

Enable an agent to delegate to a specialized sub-agent. The conversation context transfers to the receiving agent.

```python
from agents import Agent, handoff
from pydantic import BaseModel

billing_agent = Agent(name="Billing Agent", instructions="Handle billing questions.")
refund_agent = Agent(name="Refund Agent", instructions="Process refund requests.")

# Simple handoff
triage = Agent(
    name="Triage Agent",
    handoffs=[billing_agent, refund_agent]
)
```

#### Customized handoff with metadata and callback

```python
class EscalationData(BaseModel):
    reason: str
    priority: int

async def on_escalation(ctx, input_data: EscalationData):
    # Triggered when handoff occurs — use for logging, DB writes, etc.
    await log_escalation(input_data.reason, input_data.priority)

escalation = handoff(
    agent=Agent(name="Escalation Agent"),
    tool_name_override="escalate_to_human",
    tool_description_override="Escalate complex issues to human support",
    on_handoff=on_escalation,
    input_type=EscalationData,          # structured metadata from model
    input_filter=handoff_filters.remove_all_tools,  # filter history
    is_enabled=lambda ctx, agent: ctx.context.user_tier == "premium"
)
```

**Handoff options:**
| Option | Purpose |
|--------|---------|
| `tool_name_override` | Custom name instead of `transfer_to_<agent_name>` |
| `tool_description_override` | Custom description for model to understand when to use |
| `on_handoff` | Callback on invocation (logging, data fetch, side effects) |
| `input_type` | Pydantic model for small model-generated metadata (reason, priority, language) |
| `input_filter` | Transform what history the receiving agent sees |
| `is_enabled` | Boolean or function; dynamically enable/disable |
| `nest_handoff_history` | Per-call override for conversation history nesting |

**Use `input_type` for:** small model-generated metadata (reason, language, category).
**Use `RunContextWrapper.context` for:** existing application state (user ID, session data).

**Available input filters** (`agents.extensions.handoff_filters`):
- `remove_all_tools` — strip tool calls from history before handoff

**Handoff vs. Agent as Tool:**
- Handoff: transfers conversation control; receiving agent sees full context
- Agent as Tool: orchestrator retains control; sub-agent returns result as tool output

---

### 4. Guardrails

Validation mechanisms that run in parallel with agent execution. Fail fast to avoid wasting tokens on unsafe/invalid requests.

#### Input Guardrail (checks user input before agent processes it)

```python
from agents import Agent, GuardrailFunctionOutput, input_guardrail, Runner
from pydantic import BaseModel

class HomeworkCheck(BaseModel):
    is_homework: bool
    reasoning: str

guardrail_agent = Agent(
    name="Homework Detector",
    instructions="Detect if the input is asking for homework help.",
    output_type=HomeworkCheck
)

@input_guardrail
async def no_homework_guardrail(ctx, agent, input):
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_homework,
    )

agent = Agent(
    name="Tutor Agent",
    input_guardrails=[no_homework_guardrail]
)
```

#### Tool Guardrail (runs before/after each tool invocation)

```python
from agents import tool_input_guardrail, ToolGuardrailFunctionOutput
import json

@tool_input_guardrail
def no_secrets_in_tools(data):
    args = json.loads(data.context.tool_arguments or "{}")
    if "sk-" in json.dumps(args):
        return ToolGuardrailFunctionOutput.reject_content(
            "Do not pass API keys to tools"
        )
    return ToolGuardrailFunctionOutput.allow()
```

**Execution mode:** Input guardrails run in parallel with the agent by default (better latency). They can be set to blocking (completes before agent starts) when the check must prevent any token consumption.

---

### 5. Tracing

Built-in observability. Enabled by default. Zero configuration required.

**What gets traced automatically:**
- Full `Runner.run()` call
- Each agent execution (agent span)
- Every LLM generation (generation span)
- Every tool call (function span)
- Guardrail evaluations
- Handoffs
- Audio operations (STT/TTS spans)

**Dashboard:** https://platform.openai.com/traces

```python
# Disable globally
import os
os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"

# Disable in code
from agents.tracing import set_tracing_disabled
set_tracing_disabled(True)

# Per-run: exclude sensitive data from traces
from agents import RunConfig
config = RunConfig(trace_include_sensitive_data=False)
result = await Runner.run(agent, input, run_config=config)
```

**For long-running workers** (Celery, FastAPI background tasks):
```python
from agents.tracing import flush_traces
# Call after trace context exits to ensure immediate delivery
await flush_traces()
```

**Custom processors:**
```python
from agents.tracing import add_trace_processor, set_trace_processors

# Send to additional backend alongside OpenAI
add_trace_processor(my_custom_processor)

# Replace default entirely
set_trace_processors([my_processor])
```

**External integrations** (25+ platforms): Weights & Biases, Arize-Phoenix, MLflow, Braintrust, LangSmith, Langfuse, Portkey AI, and more.

---

## Sessions (Persistent Memory)

Sessions provide memory across agent turns:
```python
from agents import Session

session = Session()
result1 = await Runner.run(agent, "My name is Alice.", session=session)
result2 = await Runner.run(agent, "What's my name?", session=session)
```

---

## Subagents (2026 — Experimental)

Orchestrator agents can spawn specialized subordinate agents for parallel, modular task decomposition. Being added to both Python and TypeScript SDK versions.

---

## vs. Claude Agent SDK (Anthropic)

| Dimension | OpenAI Agents SDK | Claude Agent SDK |
|-----------|------------------|-----------------|
| Language | Python + TypeScript | Python |
| Primary API | Responses API | Claude Messages API |
| Built-in tools | WebSearch, FileSearch, CodeInterpreter, MCP, ImageGen, Computer | Web search, file tools, computer use |
| Handoffs | First-class primitive with `handoff()` | Tool-based agent delegation |
| Guardrails | Input / Output / Tool guardrails | Safety hooks |
| Tracing | Built-in, 25+ integrations | Built-in observability |
| Subagents | Experimental 2026 | Native |
| MCP | `HostedMCPTool`, `MCPServerStdio/HTTP` | Supported |
| Model lock-in | OpenAI models (+ compatible via Chat Completions) | Anthropic Claude models |

---

## 2026 Status Notes

- Assistants API deprecated August 26, 2026 — Agents SDK + Responses API is the replacement
- OpenAI recommends migrating all Assistants API usage to Responses API before shutdown
- Agents SDK TypeScript version released 2026
