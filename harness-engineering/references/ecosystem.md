# Harness Engineering Ecosystem

Sources: LangGraph, Microsoft Agent Framework, OpenClaw, DeepSeek-V3.2, Moonshot Kimi K2, ACE (arXiv 2510.04618)

## Table of Contents

- [When to Abandon a Framework](#when-to-abandon-a-framework) — 4 ceiling signals; minimum viable stack; abstraction quality test
- [Framework Comparison](#framework-comparison) — LangGraph / Microsoft / Qwen-Agent / OpenClaw
- [LangGraph](#langgraph) — checkpoints, explicit state machines, human-in-the-loop
- [Microsoft Agent Framework (AutoGen + Semantic Kernel)](#microsoft-agent-framework-autoGen--semantic-kernel)
- [OpenClaw](#openclaw) — SOUL.md, agent isolation, skill allowlists, routing; security note
- [oh-my-claudecode (OMC)](#oh-my-claudecode-omc) — workflow modes, skill learning, rate limit management
- [clawhip](#clawhip) — daemon-first event router; typed session.* events
- [Chinese Lab Research](#chinese-lab-research-whats-actionable) — DeepSeek context strategies; Kimi K2 interleaved thinking; ACE evolving playbooks
- [Spec-Driven Workflow Frameworks](#spec-driven-workflow-frameworks) — comparison table
- [Choosing Between Approaches](#choosing-between-approaches) — decision tree

---

## When to Abandon a Framework

Source: Octomind, "Why We No Longer Use LangChain for Building Our AI Agents" (2024)

Frameworks help early. They become liabilities when requirements grow beyond their abstractions. Concrete signals that a framework has hit its ceiling:

- **The time test**: when the team spends as much time understanding and debugging the framework as building features
- **The scope reduction signal**: when you reduce the scope of your implementation to fit what the framework allows, rather than expressing what you actually need
- **The translation tax**: when every new requirement must be "translated into framework-appropriate solutions" before it can be implemented
- **Nested abstraction depth**: when understanding how to use an API correctly requires comprehending multiple layers of abstractions built on top of each other — and debugging means reading stack traces through framework internals you didn't write

When these signals appear, the framework is costing more than it provides. The switching cost feels large; the ongoing cost of staying is larger.

**The minimum viable AI application stack** (post-framework):

Once a framework is removed, what remains? Four components cover almost all requirements:

1. **LLM client** — direct API calls (OpenAI SDK, Anthropic SDK, etc.)
2. **Tools/functions** — your own tool definitions and handlers
3. **Vector database** — for RAG (Pinecone, pgvector, Chroma, etc.)
4. **Observability platform** — tracing, evaluation, cost tracking

Everything else is either helpers around these four (chunking utilities for vector DBs, prompt templating) or standard application code (state management, caching, file I/O). You don't need a framework for standard application code.

**External agent state observability as a non-negotiable requirement:**

Octomind needed to dynamically change which tools their agents could access based on business logic and LLM output. LangChain had no mechanism for externally observing agent state, so this was impossible without framework surgery.

Any harness that cannot observe and modify agent behavior from outside the agent — without touching the agent's code — will hit this ceiling. The harness must have external visibility into agent state. This is the architectural requirement that clawhip and monitoring-as-daemon patterns address (see [guides-and-sensors.md](guides-and-sensors.md) → "Typed Agent Lifecycle Events").

**The abstraction quality test:**

A good abstraction reduces both code *and* cognitive load. An abstraction that reduces code while increasing cognitive load (more concepts to hold, more layers to understand) is net negative. Apply this test to every harness component: does removing this component make the system harder to understand? If not, remove it.

---

## Framework Comparison

| Framework | Origin | Primary strength | Best fit |
|---|---|---|---|
| **LangGraph** | LangChain | Stateful graph orchestration, checkpoints | Python teams needing explicit state machines |
| **Microsoft Agent Framework** | Microsoft (AutoGen + Semantic Kernel) | Enterprise production, dynamic multi-agent orchestration | Azure-native, enterprise deployments |
| **Qwen-Agent** | Alibaba | Open-source, MCP + function calling, code interpreter | Cost-sensitive deployments, open-weight models |
| **OpenClaw** | Steinberger / OpenAI Foundation | Consumer-grade, messaging app integration, SKILL.md system | Personal agents, multi-platform routing |

---

## LangGraph

LangGraph provides stateful, graph-based orchestration for multi-step agent workflows. Its key harness-relevant features:

**Checkpoints**: State persists at every node. If a session fails mid-task, execution can resume from the last checkpoint rather than restarting. This is an automated version of the `claude-progress.txt` pattern — the framework handles state persistence rather than the agent.

**Explicit state machines**: Workflows are defined as graphs where nodes are agent actions and edges are transitions. This makes control flow inspectable and debuggable — unlike pure ReAct loops where the agent decides its own next step.

**Human-in-the-loop support**: Built-in interrupts allow pausing execution for human review at defined points, then resuming. Critical for production workflows where certain actions require approval.

**When to use LangGraph vs. file-based handoffs**:
- LangGraph checkpoints: better when the harness infrastructure is managed by your team and you want automatic recovery
- File-based handoffs (feature_list.json + progress.txt): better when agents need to be self-sufficient in arbitrary environments without framework dependencies

The four LangChain middleware patterns (Build-Verify Loop, Context Injection, Loop Detection, Reasoning Budgeting) are covered in [middleware-patterns.md](middleware-patterns.md).

---

## Microsoft Agent Framework (AutoGen + Semantic Kernel)

Released October 2025 (public preview), targeting GA Q1 2026. Merges AutoGen's dynamic multi-agent orchestration with Semantic Kernel's production-grade infrastructure.

**Magentic orchestration**: A dedicated manager agent reads the task ledger and progress ledger, then dynamically selects which specialized agent acts next based on current context and task progress. Re-plans when progress stalls.

**Specialized agents in the default stack**:
- WebSurfer — browser automation
- FileSurfer — local file navigation
- Coder — write and execute code
- ComputerTerminal — shell operations

**Key harness design principle from Magentic-One**: The orchestrator maintains the task and progress ledgers, not the individual agents. Individual agents are stateless — they receive context from the orchestrator and return results. State management is centralized.

This contrasts with Anthropic's pattern where the coding agent manages its own state. Both work; the centralized orchestrator approach is more suitable when agents have specialized, narrow roles.

**When to use**: Azure-native deployments, enterprise environments requiring production SLAs, teams already using Semantic Kernel.

---

## OpenClaw

Open-source agent framework (247K GitHub stars as of March 2026). Uses the same SKILL.md system as this repository, making it directly relevant for skill portability.

**Architecture concepts relevant to harness design:**

**SOUL.md per agent**: Each agent has a SOUL.md file defining its personality, capabilities, and constraints — analogous to a CLAUDE.md scoped to a single agent rather than a project. Enables distinct agent personas within the same harness.

**Agent isolation**: Each agent has a dedicated workspace, isolated state directory, and separate session storage. No automatic credential or state sharing between agents. This maps to the "non-overlapping responsibilities" principle from the NLAH research (arXiv 2603.25723).

**Skill allowlists**: Per-agent skill filtering via `agents.list[].skills`. Different agents in the same harness can have different capabilities — a research agent gets web search tools; a coding agent gets file and shell tools.

**Routing**: Deterministic message routing via bindings — peer identity, parent peer, guild/role combinations. "Most-specific wins." This enables routing different types of requests to different specialized agents without LLM-based routing decisions.

**Security note**: Cisco found third-party OpenClaw skills performing data exfiltration and prompt injection without user awareness. When using community skills from any ecosystem, audit before installing. This applies equally to SKILL.md files from untrusted sources.

**When to use OpenClaw patterns**: Multi-platform agent deployment (WhatsApp, Telegram, Slack), personal assistant workflows, scenarios where skill portability (SKILL.md) across OpenClaw and Claude Code matters.

---

## oh-my-claudecode (OMC)

Source: github.com/yeachan-heo/oh-my-claudecode (Yeachan Heo, 2026)

Multi-agent orchestration layer built specifically for Claude Code, as opposed to oh-my-codex (OmX) which wraps OpenAI's Codex CLI. OMC leverages Claude Code's native agent teams feature rather than simulating it.

**Workflow modes**: `team` (canonical staged pipeline: plan → prd → exec → verify → fix loop), `autopilot` (full autonomous), `ralph` (persist until verification passes), `ulw` (maximum parallelism), `ralplan` (iterative planning consensus), `deep-interview` (socratic requirements clarification), `ultrathink` (deep reasoning).

**Key harness features**:
- **Skill learning system**: auto-extracts reusable debugging patterns into `.omc/skills/` and injects them in future sessions when the same problem signature appears — the harness builds a skill library from usage
- **Smart model routing**: Haiku for simple tasks, Opus for complex reasoning; documented 30–50% token cost savings
- **Rate limit management**: `omc wait` auto-resumes sessions when provider limits reset — treats rate limits as a recoverable lifecycle event, not a failure
- **Ephemeral tmux workers**: spawns Codex/Gemini/Claude processes on demand; workers die on task completion, eliminating idle cost
- **HUD statusline + session JSON summaries + agent replay logs**: three tiers of observability
- **Native Claude Code teams integration**: uses `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`; graceful fallback if disabled
- **19 specialized agent roles** with smart routing by complexity

**When to use**: Claude Code-native workflows where you want team orchestration, skill learning, and rate limit resilience without leaving the Claude Code ecosystem.

See [session-handoff-pattern.md](session-handoff-pattern.md) → "Skill Learning" and [middleware-patterns.md](middleware-patterns.md) → "Rate Limit Management" for the patterns OMC implements.

---

## clawhip

Source: github.com/Yeachan-Heo/clawhip (Yeachan Heo, 2026)

A daemon-first event router and notification system for agent workflows. Runs as a background service (default: `localhost:25294`) that receives typed events from multiple sources, applies routing logic, and delivers to Discord/Slack.

**Architecture**: Source layer (Git, GitHub webhooks, tmux, OMX/OMC, CLI) → MPSC queue → Dispatcher (normalizes to `session.*` events) → Router (filter-based matching) → Renderer (Discord embeds or Slack blocks) → Sink (bot or webhook).

**Key harness properties**:
- Runs entirely outside agent context windows — monitoring has zero token cost
- Normalizes heterogeneous inputs to a typed `session.*` lifecycle contract (started, blocked, handoff-needed, retry-needed, test-started, pr-created, failed, finished)
- tmux keyword watching converts unstructured terminal output into typed events without modifying the agent
- Batch dispatch aggregates CI events over a configurable window to reduce notification noise
- Separate bot token from interactive agent chat keeps CI noise out of conversation context
- OMX/OMC native bridge provides structured session metadata rather than free-text parsing
- Plugin architecture with built-in claude-code and codex adapters

**When to use**: any multi-agent workflow where you need observability, human-in-the-loop notification, or lifecycle-triggered automation without loading monitoring logic into the agents. Particularly valuable for long-running unattended sessions (overnight runs, CI pipelines) where the human is away from the terminal.

See [guides-and-sensors.md](guides-and-sensors.md) → "Typed Agent Lifecycle Events" and "Async Notification as Human-in-the-Loop Sensor" for the harness engineering patterns clawhip implements.

---

## Chinese Lab Research: What's Actionable

### DeepSeek-V3.2: Context Management at Scale

DeepSeek documented specific strategies for handling context overflow in multi-step agents (triggered when token usage exceeds 80% of context window):

| Strategy | Mechanism | Trade-off |
|---|---|---|
| **Summary** | Summarizes the overflowed trajectory | Preserves semantics, loses detail |
| **Discard-75%** | Drops first 75% of tool call history | Fast, retains recent context, loses early work |
| **Discard-all** | Resets context, discards all tool calls | Maximum headroom, agent restarts from scratch |

**Practical implication**: The 80% threshold trigger is a useful benchmark for when to intervene. In harness design, this is the point to either trigger a context reset (with structured handoff artifacts) or apply progressive compaction. Don't wait for the model to hit 100% — by then context anxiety has already set in.

DeepSeek also trained on 85,000+ complex agentic prompts across 1,800 distinct environments, suggesting robustness to varied tool-call sequences — relevant when selecting a model for a harness that requires long sequential tool use.

### Moonshot AI Kimi K2: Interleaved Thinking for Long Tool Chains

Kimi K2 introduced "interleaved thinking" — the model generates explicit reasoning steps *between* executing tool calls, rather than reasoning only at the start of a task. This enables 200–300 sequential tool calls without human intervention.

**Harness implication**: For tasks requiring very long tool call chains (scraping, multi-step research, complex code generation), models with interleaved thinking reduce the need for session decomposition. The reasoning between actions maintains coherence that would otherwise require a session reset.

This doesn't replace the session-handoff pattern for multi-day projects, but it extends how long a single session can run productively before a reset is needed.

### Agentic Context Engineering (ACE, arXiv 2510.04618)

ACE treats context as an **evolving playbook** that accumulates and refines over time, rather than a static prompt or compressed summary.

Three roles:
- **Generator**: Produces reasoning trajectories surfacing effective strategies and recurring problems
- **Reflector**: Extracts concrete insights from successes and errors across multiple iterations
- **Curator**: Integrates insights into compact delta entries using deterministic (non-LLM) logic

Results: 10.6% average improvement on agent tasks, 86.9% reduction in adaptation latency vs. baseline.

**Practical implication**: The `claude-progress.txt` handoff artifact is a manual, sequential version of what ACE automates. An ACE-style harness upgrades progress tracking from "log what happened" to "extract what was learned and update the playbook." Over multiple sessions, the agent's starting context improves rather than just growing in length.

This is most valuable for long-running projects (weeks+) where patterns repeat across sessions. The curator's non-LLM deduplication step is key — it prevents the playbook from becoming bloated while preserving useful heuristics.

---

## Spec-Driven Workflow Frameworks

A parallel ecosystem of pre-built harness implementations has emerged alongside the orchestration frameworks above. Where LangGraph and AutoGen are infrastructure for building harnesses, these frameworks ARE harnesses — packaged workflow systems you adopt rather than build.

| Framework | Stars | Harness completeness | Primary strength |
|---|---|---|---|
| **GitHub Spec Kit** | 80K | Guides only | Fastest adoption; widest agent support |
| **GSD** | 32K | Full (all 5 elements) | Wave parallelization; 10-dim plan validation; goal-backward verification |
| **Ralph Wiggum** | — | Guides + self-verify | Simplest autonomous loop; minimal overhead |
| **BMAD** | — | Full (human-in-loop) | 12+ agent personas; agile-grounded; Party Mode |
| **SPARC** | — | Full (TDD-first) | Correctness-critical; pseudocode before implementation |
| **Kiro** (Amazon) | — | Guides + hooks | IDE-native; EARS notation; agent hooks as built-in sensors |

Key distinction from orchestration frameworks: spec-driven workflow frameworks handle the **planning and decomposition layer** (guides) and optionally the **evaluation layer** (sensors). LangGraph and AutoGen handle **state persistence and routing infrastructure**.

They are composable: use GSD's planning artifacts with LangGraph checkpoints for state management. Use Ralph's loop with LangGraph's human-in-the-loop interrupts for approval gates.

See [spec-driven-workflows.md](spec-driven-workflows.md) for full methodology detail on each.

## Choosing Between Approaches

For most practitioners, the decision tree is:

1. **Greenfield, single developer, any environment** → File-based handoffs (session-handoff-pattern.md) + middleware patterns (middleware-patterns.md)
2. **Want a pre-built harness, maximum coverage** → GSD
3. **Want a pre-built harness, fast adoption** → GitHub Spec Kit (add sensors later)
4. **Fully autonomous loop, minimal overhead** → Ralph Wiggum
5. **Human-collaborative, agile team** → BMAD
6. **TDD-first, correctness-critical** → SPARC
7. **AWS-native, IDE-integrated** → Kiro
8. **Python codebase, need checkpoint recovery** → Add LangGraph for state management
9. **Azure/enterprise, multi-team** → Microsoft Agent Framework
10. **Long tool chains (200+ calls)** → Evaluate Kimi K2 or DeepSeek-V3.2 as the model; may reduce need for session decomposition
11. **Long-running project (weeks+), want improving context** → Implement ACE-style playbook evolution on top of progress tracking
12. **Multi-platform personal agent** → OpenClaw with SOUL.md per agent
