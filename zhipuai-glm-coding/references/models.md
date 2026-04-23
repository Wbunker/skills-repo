---
name: zhipuai-glm-models
description: GLM model specifications, benchmarks, context windows, architecture details, selection guidance, and pay-as-you-go pricing for Z.ai. Covers all Coding Plan models (GLM-5.1, GLM-5-Turbo, GLM-4.7, GLM-4.5-Air) plus PAYG/free models (GLM-4.7-Flash, GLM-4.5-Flash) and when to use each billing mode.
type: reference
---

# Z.ai GLM Models — Reference

## Model Lineup (April 2026)

### GLM-5.1
- **Architecture:** Dense transformer (exact params not publicly disclosed)
- **Context window:** 200K tokens
- **Quota cost:** 3× peak / 2× off-peak (1× off-peak through April 2026)
- **Key benchmarks:**
  - SWE-Bench Pro: 58.4 (ahead of GPT-5.4, Claude Opus 4.6, Gemini 3.1 Pro)
  - Long-horizon agentic tasks: designed for 8+ hour continuous operation
- **Strengths:** Complex multi-step engineering, planning + execution + testing cycles, long-horizon autonomy
- **When to use:** Architecture decisions, end-to-end feature implementation, debugging deeply nested issues, tasks where you want the model to self-review and iterate

### GLM-5-Turbo
- **Context window:** 200K tokens
- **Quota cost:** 3× peak / 2× off-peak (1× off-peak through April 2026)
- **Strengths:** Same capability tier as GLM-5.1 but optimized for throughput — faster token generation
- **When to use:** Same tasks as GLM-5.1 when speed matters more than maximum reasoning depth

### GLM-4.7
- **Architecture:** Mixture of Experts — 355B total parameters, 32B activated
- **Context window:** 205K tokens
- **Quota cost:** 1× always
- **Key benchmarks:**
  - SWE-bench: 73.8% (+5.8% over GLM-4.6)
  - SWE-bench Multilingual: 66.7% (+12.9%)
  - Terminal Bench 2.0: 41% (+16.5%)
- **Token throughput:** 55+ tokens/second
- **Strengths:** Daily coding tasks, fast iteration, multilingual projects, terminal-based workflows
- **When to use:** 80–90% of routine coding — debugging, refactoring, implementing features, writing tests

### GLM-4.5-Air
- **Architecture:** Lightweight / distilled
- **Context window:** Standard
- **Quota cost:** 1× always (maps to Haiku slot)
- **Strengths:** Fast, cheap, good for simple completions
- **When to use:** Quick lookups, simple edits, low-stakes autocomplete, routing/dispatch tasks in multi-agent pipelines

### GLM-4.5 (reference)
- **Architecture:** MoE, 355B total / 32B activated
- **Strengths:** Strong open-source baseline — language, code, multimodal vision
- **Note:** Superseded by GLM-4.7 for most coding tasks

---

## Selection Decision Tree

```
Is the task complex / multi-file / long-horizon?
├── Yes → Is quota headroom tight?
│         ├── Yes → GLM-4.7 (1× cost, still excellent)
│         └── No  → GLM-5.1 (best capability)
└── No  → Is it a quick edit / lookup?
          ├── Yes → GLM-4.5-Air (fastest, 1× cost)
          └── No  → GLM-4.7 (best daily-driver balance)
```

---

## Claude Code Model Slot Mapping

Claude Code uses three internal model tiers. Z.ai maps them:

| Claude Tier | Default Z.ai Model | Override Env Var |
|------------|-------------------|-----------------|
| Opus | GLM-4.7 | `ANTHROPIC_DEFAULT_OPUS_MODEL` |
| Sonnet | GLM-4.7 | `ANTHROPIC_DEFAULT_SONNET_MODEL` |
| Haiku | GLM-4.5-Air | `ANTHROPIC_DEFAULT_HAIKU_MODEL` |

To upgrade Opus slot to GLM-5.1:
```json
"ANTHROPIC_DEFAULT_OPUS_MODEL": "GLM-5.1"
```

---

## Model Names for API Calls

Use these exact strings in API requests:

| Model | API Name |
|-------|---------|
| GLM-5.1 | `GLM-5.1` |
| GLM-5-Turbo | `GLM-5-Turbo` |
| GLM-4.7 | `GLM-4.7` (or `glm-4-7` for some integrations) |
| GLM-4.5-Air | `GLM-4.5-Air` (or `glm-4-5-air`) |

---

## Recommended Parameters for Long-Horizon Tasks

From Zhipu benchmark configurations:
```json
{
  "temperature": 1.0,
  "top_p": 0.95
}
```

These match the settings used for SWE-Bench evaluation runs and produce the most consistent agentic behavior.

---

## Thinking / Reasoning Mode

GLM-4.7 and GLM-5.1 support **Interleaved Thinking** — the model retains reasoning across conversation turns. This means:
- Architectural decisions made early in a session persist without re-derivation
- Planning steps are visible in the response stream
- More coherent behavior on multi-step tasks than stateless reasoning

For detailed thinking mode configuration (5 modes, preserved thinking, tool-call patterns), see `capabilities.md`.

---

## Pay-As-You-Go Models

These models use your Z.ai account balance (not Coding Plan quota). Same API key, different billing.

| Model | Input | Output | Best For |
|-------|-------|--------|---------|
| **GLM-4.7-Flash** | FREE | FREE | High-volume scripts, CI pipelines, testing |
| **GLM-4.5-Flash** | FREE | FREE | Lightweight tasks, development/prototyping |
| **GLM-4.7-FlashX** | $0.07/M | — | Budget paid option with better quality |
| **GLM-4.5-X** | $2.2/M | — | Premium reasoning via PAYG |

Free models are rate-limited but don't touch your Coding Plan quota — useful for background automation or high-volume low-stakes calls running alongside your main coding sessions.

For vision, image generation, audio, and video PAYG models, see `platform-apis.md`.
