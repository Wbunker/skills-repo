# Tool Calling with Gemma

## Overview

Gemma 4 supports function calling via a structured chat template. Correct configuration is critical — misconfigured tool calling is the most common source of loops and malformed output.

---

## llama.cpp — Required Flag

```bash
./build/bin/llama-server \
  -m gemma-4-26b-a4b-Q3_K_M.gguf \
  --jinja \        # REQUIRED — enables Jinja-based chat template for tool calling
  --flash-attn \
  --n-gpu-layers 99
```

Without `--jinja`, Gemma 4 tool calling will:
- Loop indefinitely (15,000+ token loops observed)
- Generate malformed `<tool_call>` tags
- Fail to emit `<end_of_turn>` after tool calls

The `--jinja` flag activates the model's native Jinja chat template, which handles tool-call/tool-response formatting correctly.

---

## OpenAI-Compatible Tool Calling (via llama.cpp server)

```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="not-needed"
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                    "units": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["city"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="gemma-4",
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    tools=tools,
    tool_choice="auto"
)

message = response.choices[0].message
if message.tool_calls:
    for tool_call in message.tool_calls:
        print(f"Tool: {tool_call.function.name}")
        print(f"Args: {tool_call.function.arguments}")
```

---

## Google AI Studio Tool Calling

```python
from google import genai
from google.genai import types

def get_weather(city: str) -> str:
    return f"Weather in {city}: 22°C, sunny"

client = genai.Client(api_key="YOUR_API_KEY")

response = client.models.generate_content(
    model="gemma-4-26b-a4b",
    contents="What's the weather in Paris?",
    config=types.GenerateContentConfig(
        tools=[get_weather],  # Pass Python functions directly
    ),
)
```

The Google AI SDK handles tool registration and response parsing automatically when you pass Python functions.

---

## Chat Template Format (Manual)

When constructing prompts manually, Gemma tool calls use this format:

```
<start_of_turn>user
[Available tools]
{"name": "get_weather", "description": "...", "parameters": {...}}
[End of available tools]

What's the weather in Tokyo?<end_of_turn>
<start_of_turn>model
<tool_call>
{"name": "get_weather", "arguments": {"city": "Tokyo"}}
</tool_call><end_of_turn>
<start_of_turn>tool
{"temperature": 18, "condition": "cloudy"}
<end_of_turn>
<start_of_turn>model
The weather in Tokyo is 18°C and cloudy.
```

Use `apply_chat_template` from HuggingFace tokenizers rather than constructing this manually.

---

## Thinking Tags in Agentic Tasks

When thinking/CoT is enabled, strip the `<think>...</think>` content **between turns** but **not between tool calls within the same turn**. The model needs its reasoning context when processing tool results.

```python
import re

def strip_thinking(text: str) -> str:
    """Remove thinking tags from model output before sending to user."""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
```

---

## Agentic Loop Pattern

```python
messages = [{"role": "user", "content": user_input}]

for _ in range(max_iterations):
    response = client.chat.completions.create(
        model="gemma-4",
        messages=messages,
        tools=tools,
    )
    
    message = response.choices[0].message
    
    if not message.tool_calls:
        # Final answer — done
        print(message.content)
        break
    
    # Execute tool calls
    messages.append(message)
    for tool_call in message.tool_calls:
        result = execute_tool(tool_call.function.name, tool_call.function.arguments)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(result)
        })
```

---

## Gotchas

- **`--jinja` flag is not optional** for llama.cpp agentic tasks — the most common source of looping bugs
- **OpenWebUI + llama.cpp**: Thinking tag leakage (model outputs `<think>` to user). Fix: install a community Jinja template that suppresses thinking output in tool-call context
- **Temperature matters**: Use `temperature=1.0` for Gemma 4. Lower temperatures increase the likelihood of repetitive tool call patterns
- **CUDA 13.2**: Corrupts GGUF token sampling randomly — tool responses may contain garbled tokens. Use CUDA 13.0
- **Infinite list loops**: Gemma 4 26B A4B has a known tendency to loop at list item 14+ in certain prompts. Add repetition detection (check for last N tokens repeating) and break the loop
