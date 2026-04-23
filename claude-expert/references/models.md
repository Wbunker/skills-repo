# Claude Model Families

## Current Models (as of April 2026)

| Model | API ID | Context | Max Output | Input / Output (per MTok) | Best for |
|---|---|---|---|---|---|
| Claude Opus 4.7 | `claude-opus-4-7` | 1M tokens | 128k | $5 / $25 | Most capable; complex reasoning; agentic coding |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | 1M tokens | 64k | $3 / $15 | Best speed/intelligence balance; production workloads |
| Claude Haiku 4.5 | `claude-haiku-4-5` | 200k tokens | 64k | $1 / $5 | Fastest; near-frontier; cost-sensitive high-volume |

## Selection Guide

| Need | Model |
|---|---|
| Complex multi-step agentic work | Opus 4.7 |
| Production default (fast + smart) | Sonnet 4.6 |
| High-volume pipelines, routing, classification | Haiku 4.5 |
| Uncertain — start here | Opus 4.7 |

## Feature Availability

| Feature | Opus 4.7 | Sonnet 4.6 | Haiku 4.5 |
|---|---|---|---|
| Thinking | Adaptive only (budget_tokens removed) | Extended or Adaptive | Extended or Adaptive |
| Context window | 1M | 1M | 200k |
| Tool use | Yes | Yes | Yes |
| Vision | Yes (3.75MP) | Yes | Yes |
| Prompt caching | Yes | Yes | Yes |
| Batch API | Yes | Yes | Yes |

**Adaptive thinking** (Opus 4.7): model decides whether to think based on task complexity; off by default — set `thinking: {type: "adaptive"}` explicitly to enable. **Extended thinking** (Sonnet 4.6, Haiku 4.5): specify `budget_tokens` explicitly — this API was removed on Opus 4.7.

**Opus 4.7 vision**: accepts images up to 2,576px on the long edge (~3.75 megapixels) — 3x the resolution of previous Claude models. ScreenSpot-Pro accuracy: 87.6% (high-res) vs 57.7% for Opus 4.6 (low-res). Unlocks dense screenshot reading, complex diagram extraction, and pixel-perfect UI reference work.

**Opus 4.7 instruction following**: takes prompts strictly and literally. Existing Opus 4.6 prompts have strong out-of-the-box performance on 4.7. Two narrow patterns need fixing: (1) implicit tool calls using soft verbs ("check", "consider") — make them explicit with MUST + named tool; (2) rules with implicit scope/exceptions ("once per conversation") — write the scope and exceptions out. See [opus-47-migration.md](opus-47-migration.md) for the full guide.

**Opus 4.7 usage cost**: consumes Claude.ai usage limits ~2x faster than Sonnet 4.6. Factor this into plan selection for high-volume or always-on workflows.

## Knowledge Cutoffs

| Model | Reliable cutoff |
|---|---|
| Opus 4.7 | January 2026 |
| Sonnet 4.6 | August 2025 |
| Haiku 4.5 | February 2025 |

## Legacy Models (still available)

| Model | API ID | Deprecation |
|---|---|---|
| Claude Opus 4.6 | `claude-opus-4-6` | Not deprecated |
| Claude Sonnet 4.5 | `claude-sonnet-4-5` | Not deprecated |
| Claude Opus 4.5 | `claude-opus-4-5` | Not deprecated |
| Claude Opus 4.1 | `claude-opus-4-1` | Not deprecated |
| Claude Sonnet 4 | `claude-sonnet-4-20250514` | June 15, 2026 |
| Claude Opus 4 | `claude-opus-4-20250514` | June 15, 2026 |
| Claude Haiku 3 | `claude-3-haiku-20240307` | April 19, 2026 |

## Programmatic Discovery

`GET /v1/models` returns all available models with `max_input_tokens`, `max_tokens`, and a `capabilities` object.

## Fast Mode

Claude Code's Fast Mode uses **the same Opus 4.6 model** with faster output generation — it does NOT switch to a cheaper model. Toggle with `/fast` in a session.

## Special Preview

**Claude Mythos Preview**: Invitation-only, defensive cybersecurity workflows (Project Glasswing). Available on Bedrock (invitation only).

## Bedrock / Vertex Model IDs

Bedrock prefixes model IDs with `anthropic.`:
- `anthropic.claude-opus-4-7`
- `anthropic.claude-sonnet-4-6`
- `anthropic.claude-haiku-4-5`

Vertex AI uses GCP-style IDs (check GCP documentation for current names).
