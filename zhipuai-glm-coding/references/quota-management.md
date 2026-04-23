---
name: zhipuai-glm-quota-management
description: Quota management strategies for Z.ai GLM Coding Plan — understanding 5-hour cycles, peak/off-peak multipliers, model cost tiers, prompt counting, and tactics to maximize throughput on Lite/Pro/Max plans.
type: reference
---

# Z.ai GLM Coding Plan — Quota Management

## How Quotas Work

### 5-Hour Rolling Window
Quota resets every 5 hours from the start of each cycle (not on a fixed clock). When you hit the limit:
- Wait for the 5-hour window to reset
- Switch to a lower-cost model (GLM-4.7 if you were on GLM-5.1)
- Route simpler tasks to GLM-4.5-Air

### Weekly Cap
Weekly limit = 5× the per-5-hour limit.

| Plan | Per 5 Hours | Per Week | Web Searches/Month |
|------|------------|---------|-------------------|
| Lite | ~80 | ~400 | 100 |
| Pro | ~400 | ~2,000 | 1,000 |
| Max | ~1,600 | ~8,000 | 4,000 |

---

## What Counts as a "Prompt"

**One prompt = one user query.** But each prompt typically triggers **15–20 model invocations** under the hood (tool calls, self-reviews, plan steps). This means:

- Max plan's 1,600 prompt budget ≈ 24,000–32,000 actual model calls per 5-hour window
- Long agentic sessions (GLM-5.1 working for 1+ hours autonomously) can consume many prompts quickly
- Monitor actual usage at https://z.ai/manage-apikey/rate-limits

---

## Peak vs. Off-Peak Multipliers

Advanced models (GLM-5.1 and GLM-5-Turbo) consume extra quota during peak hours:

| Time Window | Quota Multiplier |
|-------------|----------------|
| 14:00–18:00 UTC+8 (peak) | 3× |
| All other hours (off-peak) | 2× (1× through April 2026) |
| GLM-4.7 / GLM-4.5-Air | 1× always |

**UTC+8 peak in other timezones:**
- UTC: 06:00–10:00
- US Eastern: 02:00–06:00 (EST) / 01:00–05:00 (EDT)
- US Pacific: 23:00–03:00 (PST) / 22:00–02:00 (PDT)
- Europe Central: 07:00–11:00 (CET) / 08:00–12:00 (CEST)

**Practical implication for Max plan with GLM-5.1 at peak:**
- Effective prompts: 1,600 / 3 = ~533 prompt equivalents
- Off-peak (post-April): 1,600 / 2 = ~800 prompt equivalents
- Off-peak (promotional 1×): full 1,600 prompts

---

## Cost-Effective Model Selection

### The 80/20 Rule
- Use **GLM-4.7** for ~80% of tasks (debug, refactor, implement, write tests) — 1× quota, excellent results
- Use **GLM-5.1** only for genuinely complex tasks — architecture, long-horizon agents, hard bugs
- Use **GLM-4.5-Air** for trivial tasks — quick lookups, simple edits, routing

### Hybrid Strategy (when mixing Claude Max + GLM)
- Reserve Claude Opus/Sonnet for tasks requiring Anthropic-specific features or integrations
- Use GLM-4.7 as the workhorse for volume coding tasks
- GLM plan gives ~3× the effective usage volume of Claude Max alone at lower cost

---

## Quota Monitoring

### OpenCode Plugin
A community plugin `opencode-glm-quota` provides real-time quota monitoring, model usage tracking, and MCP tools usage stats:
- https://github.com/guyinwonder168/opencode-glm-quota

### Manual Check
Visit https://z.ai/manage-apikey/rate-limits while logged in to see current usage and limits.

### Claude Code
No built-in quota display, but `/status` shows active model. Watch for 429 errors as a quota signal.

---

## Tactics for Max Plan Users

1. **Run heavy agentic sessions off-peak** — outside 14:00-18:00 UTC+8 saves 33-67% of quota
2. **Don't over-provision to GLM-5.1** — GLM-4.7 handles 90% of real coding tasks at 1× cost
3. **Batch related tasks into one long session** — each new session restart counts as a new prompt
4. **Use GLM-4.5-Air in Haiku slot** — Claude Code uses Haiku for simple routing; keeping it at 4.5-Air preserves budget
5. **Interleaved Thinking retains context** — less need to re-explain architecture; fewer redundant prompts
6. **Vision calls share prompt pool** — avoid heavy screenshot analysis loops; prefer text descriptions when possible
7. **Web Search budget is monthly** — 4,000 searches/month on Max; don't burn them on routine lookups

---

## Concurrency Limitation

The GLM Coding Plan (including paid tiers) enforces **1 concurrent in-flight request**. This means:
- Parallel agentic pipelines that send simultaneous requests will fail
- Design sequential tool-call chains rather than parallel fan-out architectures
- In multi-agent setups, use a queue/semaphore pattern

This is a known limitation documented in community issue trackers and is not specific to any one tier.
