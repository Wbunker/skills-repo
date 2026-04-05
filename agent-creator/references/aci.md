---
name: agent-computer interface design
description: How to design tools and interfaces that agents use effectively — format choices, poka-yoke patterns, testing approach
type: reference
---

# Agent-Computer Interface (ACI) Design

Tool documentation and design deserve the same prompt engineering attention as system prompts. A poorly designed tool causes more agent failures than a weak system prompt.

## Core Principle

Put yourself in the model's shoes. Is it obvious how to use this tool based only on its description and parameters? If you'd need to think carefully, so will the model.

## Format Design Rules

**Give the model room to think before committing.** Avoid formats that require knowing the answer before writing it. Example: writing a diff requires knowing the line count in the chunk header *before* the new code — this is error-prone. Writing code inside JSON requires escaping every newline and quote. Both formats cause unnecessary mistakes.

**Prefer formats the model has seen naturally on the internet.** The model writes better code in markdown fences than in JSON strings. It handles line-numbered file reads better than byte offsets.

**No formatting overhead.** If the format requires tracking a running count (lines changed, byte position, nesting depth), it will accumulate errors over long outputs. Flatten the format.

## Poka-Yoke Your Tools

Design parameters so mistakes are hard to make:

| Fragile design | Hardened design |
|----------------|-----------------|
| `filepath: string` (relative paths allowed) | `filepath: string` — must be absolute path, validated on call |
| `action: "read" \| "write" \| "delete"` | Separate `read_file`, `write_file`, `delete_file` tools |
| `limit: number` (unbounded) | `limit: number` — max 100, default 20 |
| `environment: string` (freetext) | `environment: "staging" \| "production" \| "local"` (enum) |

**The absolute filepath example** (from Anthropic's SWE-bench work): agents would make mistakes with relative paths after `cd`-ing into subdirectories. Switching to required absolute paths eliminated the error class entirely.

## Writing Effective Tool Descriptions

Think of it as a docstring for a junior developer — not just "what it does" but:
- **When to use it** (vs. similar tools)
- **Input format requirements** (date formats, ID formats, path conventions)
- **Edge cases and gotchas**
- **Example call** for non-obvious parameters

```python
# Weak description
def get_user(user_id: str) -> dict:
    """Get user data."""

# Strong description  
def get_user(user_id: str) -> dict:
    """
    Fetch a user record by ID.
    
    user_id: UUID format (e.g. "a1b2c3d4-..."). Use get_user_by_email() if you
             only have an email address. Returns None if user not found — do not
             assume a missing user is an error.
    
    Example: get_user("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    """
```

## Distinguishing Similar Tools

When an agent has multiple tools that do similar things, the descriptions must clearly delineate when to use each one:

```
read_page_interactive: Returns only interactive elements (buttons, inputs, links).
  Use first when you need to interact with the page. Smaller output than read_page_full.

read_page_full: Returns the complete accessibility tree.
  Use only when read_page_interactive is insufficient — e.g., when you need
  to read dynamic content that isn't interactive.
```

Ambiguous similar tools cause the agent to pick the wrong one consistently.

## Testing Your Tool Interface

Run 10–20 diverse example inputs and watch which mistakes repeat. Common failure signatures:

- Agent uses a tool with a plausible but wrong parameter value → description needs more constraints
- Agent calls tools in the wrong order → add ordering guidance to descriptions
- Agent makes the same format error repeatedly → switch to a format the model handles naturally
- Agent retries a failing tool call identically → the error message isn't actionable; improve it

**Invest more time in tools than the overall prompt.** For complex agents, tool design is typically the highest-leverage improvement available.
