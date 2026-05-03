# Qwen Agentic Patterns

## Table of Contents
- [Architecture: Why Qwen3.6 Plus Is Different](#architecture-why-qwen36-plus-is-different)
- [Long-Context Use Cases](#long-context-use-cases)
- [Always-On Chain-of-Thought](#always-on-chain-of-thought)
- [Orchestrator and Subagent Roles](#orchestrator-and-subagent-roles)
- [Cost Optimization Patterns](#cost-optimization-patterns)
- [Framework Integration](#framework-integration)
- [Gotchas](#gotchas)

---

## Architecture: Why Qwen3.6 Plus Is Different

**Hybrid linear attention + sparse MoE:**

- **Linear attention**: Context processing scales linearly (not quadratically) with sequence length. This is the architectural reason the 1M context window is practically usable — not just a number that collapses under memory pressure.
- **Sparse MoE**: Only relevant expert layers activate per forward pass. Keeps throughput high (~158 tok/s) even as total parameter count scales. This is why it's 3x faster than Claude Opus 4.6 (~53 tok/s) at comparable quality.

**Design intent (from Alibaba's "Towards Real World Agents" paper):**
- Built for agents, not retrofitted from chat
- Tool use is a base behavior, not a fine-tuned add-on
- Trained to function as orchestrator AND subagent in the same model

---

## Long-Context Use Cases

### 1. Repository-Level Coding Without Chunking

Traditional RAG: chunk code into 4–8K segments → retrieve relevant chunks → hope nothing important is missing.

With 1M context, load the full repository:

```python
import os

def load_repo_to_context(repo_path: str, extensions: list[str] = None) -> str:
    """Load all relevant source files into a single context string."""
    if extensions is None:
        extensions = ['.py', '.ts', '.js', '.go', '.rs', '.java']

    parts = []
    for root, _, files in os.walk(repo_path):
        # Skip hidden dirs, node_modules, .git, etc.
        if any(skip in root for skip in ['.git', 'node_modules', '__pycache__', '.venv']):
            continue
        for fname in files:
            if any(fname.endswith(ext) for ext in extensions):
                fpath = os.path.join(root, fname)
                relpath = os.path.relpath(fpath, repo_path)
                try:
                    content = open(fpath).read()
                    parts.append(f"# File: {relpath}\n{content}")
                except UnicodeDecodeError:
                    pass

    return "\n\n".join(parts)

repo_context = load_repo_to_context("/path/to/repo")

response = client.chat.completions.create(
    model="qwen/qwen3.6-plus",
    messages=[
        {"role": "system", "content": "You are an expert software engineer. You have access to the full repository."},
        {"role": "user", "content": f"<repository>\n{repo_context}\n</repository>\n\nFind and fix the memory leak in the connection pool."}
    ],
    max_tokens=8192
)
```

**Cost check first**: Estimate token count (`~4 chars per token`) before sending. A 500K-token repo context at long-context pricing ($1.101/M) = $0.55/request. At 10 agent loops, $5.50/task — verify this is acceptable.

### 2. Long-Session Agent Coherence

At 200K context (prior practical limit), agents forget early decisions → circular behavior, incorrect assumption resets.

At 1M context, keep the full session history in-window:

```python
session_messages = [
    {"role": "system", "content": "You are an autonomous debugging agent..."}
]

def agent_step(user_input: str) -> str:
    session_messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="qwen/qwen3.6-plus",
        messages=session_messages,
        tools=debug_tools,
        max_tokens=4096
    )

    msg = response.choices[0].message
    session_messages.append(msg)

    # Handle tool calls, append results...
    return msg.content
```

Monitor session size: `sum(len(m.get('content','')) for m in session_messages) // 4` gives a rough token estimate.

### 3. Massive Document Analysis

Documents too large for RAG infrastructure can be processed in a single inference call.

```python
# Load a large PDF/document set
with open("annual_report.txt") as f:
    document = f.read()

response = client.chat.completions.create(
    model="qwen/qwen3.6-plus",
    messages=[
        {"role": "user", "content": f"<document>\n{document}\n</document>\n\nExtract all revenue figures and summarize year-over-year trends."}
    ],
    response_format={"type": "json_object"}
)
```

Qwen3.6 Plus scores 91.2 on OmniDocBench v1.5 — best among all models tested (Claude: ~86, GPT-5.4: ~84). Especially strong on tables, charts, and mixed-format documents.

---

## Thinking Mode (Hybrid, Not Always-On)

Qwen3.6 Plus uses a **hybrid thinking mode** — thinking can be enabled or disabled per request. Default behavior depends on the provider and model configuration.

**Enable thinking:**
```python
response = client.chat.completions.create(
    model="qwen/qwen3.6-plus",
    messages=[...],
    extra_body={"enable_thinking": True}
)
```

**Disable thinking:**
```python
extra_body={"chat_template_kwargs": {"enable_thinking": False}}
```

**Preserve thinking in agent history** (reasoning stays in conversation context for multi-turn coherence):
```python
extra_body={"chat_template_kwargs": {"preserve_thinking": True}}
```

**Soft prompts in conversation:** `/think` and `/no_think` tokens can switch mode mid-conversation.

**Reasoning tokens billing:** When enabled, thinking tokens return separately before the final response and are tracked in `usage.reasoning_tokens`. Factor ~30–50% output token overhead for thinking-enabled short tasks.

**When to disable thinking:** High-volume classification, short-form JSON extraction, or latency-sensitive pipelines where reasoning overhead doesn't add value.

**When to switch to a non-thinking model:** Qwen3.5-flash or Qwen2.5-7B for maximum speed/cost on simple tasks.

---

## Orchestrator and Subagent Roles

Qwen3.6 Plus is explicitly trained for both roles. You can use the same model for the full stack:

### As Orchestrator

```python
orchestrator_prompt = """
You are an orchestrator. Break the following task into subtasks,
execute each tool call in sequence, and synthesize the results.
Do not ask for clarification — make reasonable assumptions and proceed.
"""

response = client.chat.completions.create(
    model="qwen/qwen3.6-plus",
    messages=[
        {"role": "system", "content": orchestrator_prompt},
        {"role": "user", "content": "Audit the codebase for security vulnerabilities and generate a report."}
    ],
    tools=all_available_tools
)
```

### As Subagent

```python
subagent_prompt = """
You are a specialist. Execute the following narrow task precisely.
Return only the requested output, no commentary.
"""

response = client.chat.completions.create(
    model="qwen/qwen3.6-plus",
    messages=[
        {"role": "system", "content": subagent_prompt},
        {"role": "user", "content": "Analyze this function for SQL injection vulnerabilities: [code]"}
    ]
)
```

---

## Cost Optimization Patterns

### Context Tier Management

Keep requests under 256K tokens to stay on the $0.276/M tier (vs $1.101/M for longer):

```python
CHEAP_TIER_LIMIT = 250_000  # tokens (with buffer)

def estimate_tokens(messages: list) -> int:
    total_chars = sum(len(str(m.get('content', ''))) for m in messages)
    return total_chars // 4  # rough estimate

def should_use_long_context(messages: list) -> bool:
    return estimate_tokens(messages) > CHEAP_TIER_LIMIT
```

### Model Routing

Use Qwen3.6 Plus for complex/long tasks; Qwen2.5-7B for simple/short tasks:

```python
def select_model(task_complexity: str, estimated_tokens: int) -> str:
    if task_complexity == "simple" and estimated_tokens < 8000:
        return "qwen/qwen2.5-7b-instruct"
    elif estimated_tokens > 256_000:
        return "qwen/qwen3.6-plus"  # need long-context capability
    else:
        return "qwen/qwen3.6-plus"  # standard tier
```

### Scale Economics Reference

Per the April 2026 benchmark article: A 500K-token agentic coding task run 10 times/day at 1000 tasks:
- Claude Opus 4.6: ~$25,000/day
- Qwen3.6 Plus (long-context tier): ~$5,500/day
- Savings: ~$19,500/day, with 2pp lower SWE-bench score

---

## Framework Integration

All major Python agentic frameworks work with Qwen via the OpenAI-compatible API:

**LangChain:**
```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="qwen/qwen3.6-plus", openai_api_key="...", openai_api_base="https://openrouter.ai/api/v1")
```

**LlamaIndex:**
```python
from llama_index.llms.openai import OpenAI
llm = OpenAI(model="qwen/qwen3.6-plus", api_key="...", api_base="https://openrouter.ai/api/v1")
```

**AutoGen:**
```python
config_list = [{"model": "qwen/qwen3.6-plus", "api_key": "...", "base_url": "https://openrouter.ai/api/v1"}]
```

**CrewAI / DSPy:** Use the same OpenAI provider pattern with base URL override.

---

## Gotchas

- **Long context doesn't eliminate chunking for all cases**: 1M context is the maximum; most requests still benefit from staying under 256K for cost reasons. Use the full context window only when cross-document reasoning actually requires it.
- **Always-on CoT token cost is real**: Budget ~30–50% extra output tokens for CoT overhead on short tasks. A "100-token response" from Qwen3.6 Plus may actually cost 130–150 output tokens.
- **Session history grows fast**: At 158 tok/s input processing, Qwen3.6 Plus is fast, but multi-turn agent sessions still accumulate cost. Periodically compress/summarize old context if sessions run more than 20–30 turns.
- **SWE-bench 2pp gap is meaningful for the hardest tasks**: For ambiguous distributed systems bugs, race conditions, or novel protocol implementation — Claude Opus 4.6's 80.8% vs 78.8% difference can matter in production. Use Qwen for volume; consider Claude for high-stakes one-shot difficult engineering tasks.
- **"Open weight" claim is contested**: As noted in community discussions, Qwen3.6 Plus weights are not fully open — the API model is proprietary. Qwen2.5 series are the truly open-weight models available for local deployment.
