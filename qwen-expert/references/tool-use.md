# Qwen Tool Use & Structured Outputs

## Table of Contents
- [Function Calling](#function-calling)
- [Parallel Tool Calls](#parallel-tool-calls)
- [Structured JSON Output](#structured-json-output)
- [Tool Use in Agentic Loops](#tool-use-in-agentic-loops)
- [Gotchas](#gotchas)

---

## Function Calling

Qwen3.6 Plus treats tool use as a first-class primitive — trained into base behavior, not layered on top. Reports of fewer dropped tool call steps and more consistent JSON schemas compared to Qwen2.5 series.

### Define Tools

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_file_contents",
            "description": "Read a file from the filesystem and return its contents",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the file"
                    },
                    "encoding": {
                        "type": "string",
                        "enum": ["utf-8", "latin-1"],
                        "default": "utf-8"
                    }
                },
                "required": ["path"]
            }
        }
    }
]
```

### Full Tool Call Loop

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

messages = [{"role": "user", "content": "What's in /etc/hostname?"}]

while True:
    response = client.chat.completions.create(
        model="qwen/qwen3.6-plus",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    msg = response.choices[0].message
    messages.append(msg)  # append assistant turn

    if response.choices[0].finish_reason == "tool_calls":
        for tool_call in msg.tool_calls:
            args = json.loads(tool_call.function.arguments)
            result = call_your_function(tool_call.function.name, args)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })
    else:
        print(msg.content)
        break
```

### tool_choice Options

| Value | Behavior |
|---|---|
| `"auto"` | Model decides whether to call a tool |
| `"none"` | Never call tools; text-only response |
| `"required"` | Must call at least one tool |
| `{"type":"function","function":{"name":"..."}}` | Force a specific function |

---

## Parallel Tool Calls

Qwen3.6 Plus supports parallel tool calls in a single response (multiple `tool_calls` in one assistant message). Handle all of them before continuing:

```python
if response.choices[0].finish_reason == "tool_calls":
    # Execute all tool calls in parallel if possible
    results = {}
    for tool_call in msg.tool_calls:
        args = json.loads(tool_call.function.arguments)
        results[tool_call.id] = call_your_function(tool_call.function.name, args)

    # Append all tool results before continuing
    for tool_call in msg.tool_calls:
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(results[tool_call.id])
        })
```

---

## Structured JSON Output

### JSON Object Mode

Forces response to be valid JSON (no schema enforcement):

```python
response = client.chat.completions.create(
    model="qwen/qwen3.6-plus",
    messages=[
        {"role": "system", "content": "Respond only with valid JSON."},
        {"role": "user", "content": "Extract name and age from: John is 30 years old."}
    ],
    response_format={"type": "json_object"}
)
data = json.loads(response.choices[0].message.content)
```

### JSON Schema Mode (Structured Outputs)

Enforces a specific schema:

```python
response = client.chat.completions.create(
    model="qwen/qwen3.6-plus",
    messages=[{"role": "user", "content": "Extract person info: Alice is 25, a software engineer."}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "person",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "role": {"type": "string"}
                },
                "required": ["name", "age", "role"],
                "additionalProperties": False
            }
        }
    }
)
```

### Using `instructor` Library

`instructor` provides typed structured outputs with automatic retries:

```python
import instructor
from openai import OpenAI
from pydantic import BaseModel

client = instructor.from_openai(
    OpenAI(
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api/v1"
    )
)

class Person(BaseModel):
    name: str
    age: int
    role: str

person = client.chat.completions.create(
    model="qwen/qwen3.6-plus",
    messages=[{"role": "user", "content": "Alice is 25, a software engineer."}],
    response_model=Person
)
print(person.name, person.age)
```

---

## Tool Use in Agentic Loops

Qwen3.6 Plus is designed for both orchestrator and subagent roles:

**As orchestrator:** Receives a complex task → breaks it into subtasks → delegates to tools or specialist models → synthesizes results.

**As subagent:** Receives a narrow instruction → executes reliably with consistent tool call format.

**Framework compatibility:** LangChain, LlamaIndex, AutoGen, CrewAI all work without code changes beyond swapping `base_url` and model string.

```python
# LangChain example
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="qwen/qwen3.6-plus",
    openai_api_key=os.environ["OPENROUTER_API_KEY"],
    openai_api_base="https://openrouter.ai/api/v1"
)
```

---

## Local Inference Tool Calling

When serving Qwen3.6 or Qwen3-coder models locally, the inference backend must be configured with the correct tool-call parser:

```bash
# vLLM
vllm serve Qwen/Qwen3.6-35B-A3B \
  --enable-auto-tool-choice --tool-call-parser qwen3_coder

# SGLang
python -m sglang.launch_server ... --tool-call-parser qwen3_coder
```

Without `--tool-call-parser qwen3_coder`, tool calls may not parse correctly and will return as raw text.

---

## Gotchas

- **Maximum 20 tools per request**: DashScope enforces a 20-tool limit per API call for efficiency. Divide large toolsets across multiple agent roles if needed.
- **Always-on CoT affects tool call format**: Qwen3.6 Plus includes reasoning traces before tool calls. If parsing raw message content, look for `tool_calls` attribute on the message object rather than parsing content text.
- **All tool results must be returned before next generation**: Sending a new user message while there are unresolved `tool_calls` in the history causes errors. Always append a `tool` role message for every `tool_call.id`.
- **`json_object` mode requires system/user prompt instructing JSON**: The model won't auto-emit JSON without an explicit instruction — add `"Respond only with valid JSON"` to the system message.
- **Schema `additionalProperties: False` is required for `strict: True`**: Omitting it causes validation failures even when the output looks correct.
- **Parallel tool calls order**: Return tool results in any order (matched by `tool_call_id`), not necessarily the order they were called.
