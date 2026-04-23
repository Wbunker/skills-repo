---
name: zhipuai-glm-cli-and-agents
description: CLI invocation, direct API usage (curl/Python), non-interactive Claude Code with GLM backend, sub-agent model configuration, tool calling, streaming, and multi-agent orchestration patterns on the Z.ai GLM Coding Plan.
type: reference
---

# Z.ai GLM — CLI Invocation & Agent Communication

## API Endpoints

| Format | Endpoint |
|--------|----------|
| Native Z.ai | `https://api.z.ai/api/paas/v4/chat/completions` |
| OpenAI-compatible | `https://api.z.ai/v1/chat/completions` |
| Anthropic-compatible | `https://api.z.ai/api/anthropic` |

Authentication: `Authorization: Bearer <your-z.ai-api-key>` on all endpoints.

---

## Direct curl Invocation

### Basic completion (OpenAI-compatible endpoint)
```bash
curl -s https://api.z.ai/v1/chat/completions \
  -H "Authorization: Bearer $ZAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "GLM-4.7",
    "messages": [
      {"role": "system", "content": "You are a senior software engineer."},
      {"role": "user", "content": "Write a Python function to parse ISO 8601 dates."}
    ],
    "temperature": 1.0,
    "max_tokens": 4096
  }' | jq '.choices[0].message.content'
```

### Streaming (SSE)
```bash
curl -sN https://api.z.ai/v1/chat/completions \
  -H "Authorization: Bearer $ZAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "GLM-4.7",
    "messages": [{"role": "user", "content": "Implement a binary search in Go."}],
    "stream": true,
    "temperature": 1.0
  }'
# -N disables curl buffering — required for SSE streams
# Parse: each line starting with "data:" contains a JSON chunk; stream ends at data: [DONE]
```

### With thinking/reasoning mode
```bash
curl -s https://api.z.ai/v1/chat/completions \
  -H "Authorization: Bearer $ZAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "GLM-5.1",
    "messages": [{"role": "user", "content": "Design a distributed rate limiter."}],
    "thinking": {"type": "enabled"},
    "temperature": 1.0,
    "max_tokens": 8192
  }'
```

---

## Official Python SDK (`zai`)

```bash
pip install zai
```

### Basic usage
```python
from zai import ZaiClient

client = ZaiClient(api_key="your-z.ai-api-key")

response = client.chat.completions.create(
    model="GLM-4.7",
    messages=[{"role": "user", "content": "Refactor this function for clarity."}],
    temperature=1.0,
    max_tokens=4096
)
print(response.choices[0].message.content)
```

### Streaming
```python
stream = client.chat.completions.create(
    model="GLM-4.7",
    messages=[{"role": "user", "content": "Implement a Fibonacci generator."}],
    stream=True,
    temperature=1.0
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Thinking/reasoning mode
```python
response = client.chat.completions.create(
    model="GLM-5.1",
    messages=[{"role": "user", "content": "Debug this race condition."}],
    thinking={"type": "enabled"},
    temperature=1.0,
    max_tokens=8192
)
```

### Via OpenAI SDK (drop-in)
```python
from openai import OpenAI

client = OpenAI(
    api_key="your-z.ai-api-key",
    base_url="https://api.z.ai/v1"
)

response = client.chat.completions.create(
    model="GLM-4.7",
    messages=[{"role": "user", "content": "Write unit tests for this module."}],
    temperature=1.0
)
```

---

## Tool Calling (Function Calling)

Standard OpenAI-compatible schema. Supported on `GLM-4.6`, `GLM-4.7`, `GLM-5`.

```python
from openai import OpenAI

client = OpenAI(api_key="your-key", base_url="https://api.z.ai/v1")

tools = [
    {
        "type": "function",
        "function": {
            "name": "run_tests",
            "description": "Execute the test suite and return results",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_path": {"type": "string", "description": "Path to test file or directory"},
                    "verbose":   {"type": "boolean", "default": False}
                },
                "required": ["test_path"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="GLM-4.7",
    messages=[{"role": "user", "content": "Run the auth tests and summarize failures."}],
    tools=tools,
    tool_choice="auto"
)

if response.choices[0].message.tool_calls:
    for call in response.choices[0].message.tool_calls:
        print(f"Tool: {call.function.name}")
        print(f"Args: {call.function.arguments}")
```

### Streaming tool calls
```python
response = client.chat.completions.create(
    model="GLM-4.7",
    messages=[{"role": "user", "content": "Check the weather in Beijing."}],
    tools=tools,
    stream=True,
    tool_stream=True   # enables streaming of tool call parameters
)

for chunk in response:
    if not chunk.choices:
        continue
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="", flush=True)
    if delta.tool_calls:
        for tc in delta.tool_calls:
            # accumulate streamed JSON arguments
            pass
```

`tool_stream=True` reduces latency by streaming tool argument JSON as it's generated rather than buffering the full call.

---

## Non-Interactive Claude Code (CLI Automation)

Claude Code supports non-interactive mode via `-p` flag — useful for scripts, CI, and agent-to-agent pipelines.

### One-shot task
```bash
# Using native claude with GLM env vars pre-set
ANTHROPIC_AUTH_TOKEN=$ZAI_API_KEY \
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic \
API_TIMEOUT_MS=3000000 \
claude -p "Add docstrings to all public functions in src/api.py"
```

### Using the `z`/`glm` community wrapper
Two community projects provide `z` and `glm` as drop-in wrappers:

**geoh/z.ai-powered-claude-code** — installs `z` and `glm` commands:
```bash
bash scripts/install.sh   # Linux/macOS
# Windows: .\scripts\install.ps1

z "Implement the pagination feature described in JIRA-123"
glm --model opus "Refactor the auth module for testability"
z -p "Run the test suite and fix all failures"   # non-interactive
```

**ankurkakroo2/claude-code-glm-setup** — adds `glm` shell function:
```bash
glm -p "what is 2+2"           # non-interactive single prompt
glm --debug api                # enables API request logging
```

Both wrappers use `--settings ~/.claude/glm-settings.json` to inject Z.ai credentials without touching the default Claude config.

---

## Sub-Agent Model Configuration

When Claude Code spawns sub-agents (background tasks, parallel tool execution), you can control which GLM model they use independently of the main model.

### `.zai.json` config (geoh wrapper)
```json
{
  "apiKey": "your-z.ai-key",
  "opusModel":    "GLM-5.1",
  "sonnetModel":  "GLM-4.7",
  "haikuModel":   "GLM-4.5-Air",
  "subagentModel": "GLM-4.7",
  "defaultModel": "opus",
  "enableThinking": "true",
  "reasoningEffort": "high"
}
```

**`subagentModel`** — the model used for sub-agent tasks. Recommended: `GLM-4.7` (1× quota cost) to prevent sub-agents from burning through advanced model budget while the main agent uses GLM-5.1.

### Per-project config
Place `.zai.json` in a project root to override global settings for that project:
```json
{
  "defaultModel": "sonnet",
  "subagentModel": "GLM-4.5-Air",
  "reasoningEffort": "medium"
}
```

Config search order (first found wins): `./.zai.json` → `$ZAI_CONFIG_PATH` → `~/.config/zai/config.json` → `~/.zai.json`

### Env var override (highest priority)
```bash
export ZAI_API_KEY="your-key"   # overrides apiKey in any config file
```

---

## Agent-to-Agent Patterns

### Pattern: Orchestrator + Worker agents
The 1-concurrent-request limit means true parallel fan-out won't work. Use a serial dispatch queue:

```python
import time
from openai import OpenAI

client = OpenAI(api_key="your-key", base_url="https://api.z.ai/v1")

def glm_call(prompt, model="GLM-4.7"):
    """Single agent call — serialize these, don't parallelize."""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0
    )
    return response.choices[0].message.content

# Orchestrator plans, then dispatches workers serially
plan = glm_call("Break this task into 3 subtasks: implement OAuth login", model="GLM-5.1")
results = []
for subtask in parse_subtasks(plan):
    result = glm_call(subtask, model="GLM-4.7")   # workers use cheaper model
    results.append(result)
    time.sleep(0.5)   # optional: be gentle on rate limits
```

### Pattern: Shell script agent loop
```bash
#!/usr/bin/env bash
# Non-interactive agentic loop — each step fed to next
set -e

CONTEXT="Fix all failing tests in ./tests/"

# Step 1: analyze
ANALYSIS=$(ANTHROPIC_AUTH_TOKEN=$ZAI_API_KEY \
           ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic \
           API_TIMEOUT_MS=3000000 \
           claude -p "Analyze: $CONTEXT. List specific failures.")

# Step 2: fix based on analysis
ANTHROPIC_AUTH_TOKEN=$ZAI_API_KEY \
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic \
API_TIMEOUT_MS=3000000 \
claude -p "Given this analysis: $ANALYSIS — fix the failures."
```

### Pattern: Claude Code as sub-agent caller
Within a Claude Code session backed by GLM, you can spawn Claude Code subprocesses pointed at the same Z.ai backend:

```python
import subprocess

result = subprocess.run(
    ["claude", "-p", "Implement the data validation layer"],
    env={
        **os.environ,
        "ANTHROPIC_AUTH_TOKEN": os.getenv("ZAI_API_KEY"),
        "ANTHROPIC_BASE_URL":   "https://api.z.ai/api/anthropic",
        "API_TIMEOUT_MS":       "3000000"
    },
    capture_output=True, text=True, timeout=300
)
print(result.stdout)
```

---

## LiteLLM Integration (Multi-Provider Orchestration)

LiteLLM provides a unified interface for routing across providers. Prefix Z.ai models with `zai/`:

```python
import litellm

# Route to Z.ai GLM
response = litellm.completion(
    model="zai/GLM-4.7",
    messages=[{"role": "user", "content": "Implement error handling."}],
    api_key=os.getenv("ZAI_API_KEY")
)

# Fallback: try GLM-5.1 first, fall back to GLM-4.7
response = litellm.completion(
    model="zai/GLM-5.1",
    messages=[{"role": "user", "content": "Solve this hard bug."}],
    api_key=os.getenv("ZAI_API_KEY"),
    fallbacks=["zai/GLM-4.7"]
)
```

---

## Reasoning Effort Levels (geoh wrapper)

The `reasoningEffort` field in `.zai.json` maps to model thinking depth:

| Value | Use Case |
|-------|---------|
| `auto` | Let model decide |
| `low` | Simple tasks, fast response |
| `medium` | Balanced (default) |
| `high` | Complex reasoning, architecture |
| `max` | Maximum — most quota intensive |

---

## Windows Notes

| Shell | Wrapper | Limitations |
|-------|---------|------------|
| Git Bash | `z` / `glm` | Full functionality, status line works |
| PowerShell | `z.ps1` / `glm.ps1` | Core features, no status line |
| CMD | `z.cmd` / `glm.cmd` | Core features, no status line |

Status line requires bash + stdin piping. On Windows, use Git Bash for full experience.

Requires `jq` installed and on PATH for JSON processing in wrapper scripts.
