# DeepSeek Tool Use & Function Calling

## Table of Contents
- [Basic Tool Call Flow](#basic-tool-call-flow)
- [Tool Definition Schema](#tool-definition-schema)
- [Complete Multi-turn Example](#complete-multi-turn-example)
- [Parallel Tool Calls](#parallel-tool-calls)
- [Tool Choice Control](#tool-choice-control)
- [JSON Mode](#json-mode)
- [Strict Mode (Beta)](#strict-mode-beta)
- [Thinking Mode + Tools](#thinking-mode--tools)
- [Gotchas](#gotchas)

---

## Basic Tool Call Flow

```
1. User sends message + tools array
2. Model returns tool_calls (no content yet)
3. Your code executes the function
4. Append tool result to messages
5. Model returns final natural language response
```

---

## Tool Definition Schema

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, e.g. 'Austin, TX'"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit"
                    }
                },
                "required": ["city"]
            }
        }
    }
]
```

---

## Complete Multi-turn Example

```python
from openai import OpenAI
import json

client = OpenAI(api_key="sk-...", base_url="https://api.deepseek.com")

def get_weather(city: str, unit: str = "celsius") -> str:
    # Your actual implementation here
    return json.dumps({"city": city, "temp": 22, "unit": unit, "condition": "sunny"})

messages = [{"role": "user", "content": "What's the weather in Austin?"}]

# Round 1: model requests tool call
response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

msg = response.choices[0].message

if msg.tool_calls:
    # Append assistant message with tool_calls
    messages.append({
        "role": "assistant",
        "content": msg.content,
        "tool_calls": [tc.model_dump() for tc in msg.tool_calls]
    })

    # Execute each tool call and append results
    for tc in msg.tool_calls:
        fn_name = tc.function.name
        fn_args = json.loads(tc.function.arguments)

        if fn_name == "get_weather":
            result = get_weather(**fn_args)

        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": result
        })

    # Round 2: model generates final answer
    final = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=messages,
        tools=tools
    )
    print(final.choices[0].message.content)
```

---

## Parallel Tool Calls

The model can return multiple `tool_calls` in a single response. Process all of them before sending the next request:

```python
if msg.tool_calls:
    messages.append({"role": "assistant", "content": msg.content,
                     "tool_calls": [tc.model_dump() for tc in msg.tool_calls]})

    # Execute ALL tool calls (can be parallelized)
    for tc in msg.tool_calls:
        result = dispatch_tool(tc.function.name, json.loads(tc.function.arguments))
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": json.dumps(result)
        })
    # Then send all results together in the next request
```

---

## Tool Choice Control

```python
tool_choice="auto"       # Model decides whether to call tools (default)
tool_choice="none"       # Disable tool calling for this request
tool_choice="required"   # Force model to call at least one tool

# Force a specific function:
tool_choice={
    "type": "function",
    "function": {"name": "get_weather"}
}
```

---

## JSON Mode

Force the model to return valid JSON (without defining tools):

```python
response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[
        {"role": "system", "content": "Return only valid JSON."},
        {"role": "user", "content": "Extract name and age from: 'John is 30 years old'"}
    ],
    response_format={"type": "json_object"}
)
# response.choices[0].message.content is guaranteed to be valid JSON
```

---

## Strict Mode (Beta)

Strict mode enforces JSON schema compliance on function arguments — the model will not deviate from the schema.

**Enable:** Use `base_url="https://api.deepseek.com/beta"` and add `"strict": true` to each function.

```python
client_beta = OpenAI(api_key="sk-...", base_url="https://api.deepseek.com/beta")

tools_strict = [
    {
        "type": "function",
        "function": {
            "name": "create_user",
            "strict": True,                          # Enable strict mode
            "description": "Create a new user",
            "parameters": {
                "type": "object",
                "additionalProperties": False,        # Required in strict mode
                "properties": {
                    "username": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "age": {"type": "integer"},
                    "role": {"type": "string", "enum": ["admin", "user", "viewer"]}
                },
                "required": ["username", "email", "age", "role"]  # ALL properties required
            }
        }
    }
]
```

**Strict mode schema requirements:**
- Every `object` must have `"additionalProperties": false`
- Every `object` must list all its properties in `"required"`
- Supported types: `object`, `string`, `number`, `integer`, `boolean`, `array`, `enum`, `anyOf`, `$ref`/`$def`
- String supports `pattern` (regex) and `format` (`email`, `hostname`, `ipv4`, `ipv6`, `uuid`)
- String does **not** support `minLength`/`maxLength` in strict mode
- Array does **not** support `minItems`/`maxItems` in strict mode

---

## Thinking Mode + Tools

Tool use works in thinking mode (supported from DeepSeek-V3.2+). The critical rule is **reasoning_content must be passed back** when there are tool calls:

```python
response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=messages,
    tools=tools,
    extra_body={"thinking": {"type": "enabled"}}
)

msg = response.choices[0].message

if msg.tool_calls:
    # MUST include reasoning_content in the assistant message
    messages.append({
        "role": "assistant",
        "content": msg.content,
        "reasoning_content": msg.reasoning_content,  # Do not omit!
        "tool_calls": [tc.model_dump() for tc in msg.tool_calls]
    })
    # ... append tool results, then continue
```

Without tool calls in the same turn, omit `reasoning_content` from the history.

---

## Gotchas

- Always append **all** tool results before sending the next request — partial results cause errors.
- Tool `content` must be a string, not a dict. Use `json.dumps(result)` if returning structured data.
- Strict mode is on the `/beta` endpoint only — using `strict: true` on the production endpoint is silently ignored.
- In strict mode, all object properties must be in `required`. Optional fields must use `anyOf: [{type: "X"}, {type: "null"}]`.
- The model does not execute functions — your code is responsible for dispatch and execution.
- `tool_call_id` in the tool response must exactly match the `id` from the model's `tool_calls` entry.
