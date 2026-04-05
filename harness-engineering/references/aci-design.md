# Agent-Computer Interface (ACI) Design

Source: Anthropic, "Building effective agents" (December 2024); Anthropic, "Lessons from Building Claude Code: Seeing like an Agent" (2026); Anthropic engineering blog, "Give Claude a computer" (2026)

## Table of Contents

- [Tool Format Principles](#tool-format-principles) — token positioning, training data proximity, formatting overhead
- [Poka-Yoke Your Tools](#poka-yoke-your-tools) — make mistakes structurally impossible
- [Test How the Model Uses Your Tools](#test-how-the-model-uses-your-tools)
- [When to Promote an Action to a Tool](#when-to-promote-an-action-to-a-tool) — UX / Guardrails / Concurrency / Observability / Autonomy
- [Structured Tool Output Beats Format Instructions](#structured-tool-output-beats-format-instructions)
- [Agent-Driven Context Building](#agent-driven-context-building) — Grep over RAG
- [Context Rot](#context-rot) — progressive disclosure, subagents, path-scoped rules

---

## Overview

Tool design is a first-class engineering discipline, not an afterthought. The same investment that goes into human-computer interface (HCI) design — clarity, error prevention, discoverability — belongs in the agent-computer interface (ACI).

> "We actually spent more time optimizing our tools than the overall prompt" — Anthropic, on building their SWE-bench coding agent

---

## Tool Format Principles

- **Give the model tokens to think before it writes itself into a corner.** Format outputs so the model reasons about the hard parts before committing. If a tool requires knowing a count or length before writing content, that's overhead — remove it.
- **Keep formats close to what the model has seen in training data.** Code in markdown fences is natural; code inside JSON requires extra escaping. Diffs require tracking chunk headers before writing. The closer to naturally occurring text, the fewer errors.
- **Eliminate formatting overhead.** Counting lines of code, escaping newlines, maintaining accurate offsets — these force the model to solve a clerical problem while solving the real problem. Remove them.

---

## Poka-Yoke Your Tools

Change parameter design to make mistakes structurally harder. The concrete example from Anthropic's SWE-bench implementation: the model made errors with relative filepaths after moving out of the root directory. Solution: change the tool to always require absolute filepaths. The model used absolute paths flawlessly.

This is the tool equivalent of the harness principle "mechanical constraints over instructions." Rather than instructing the model to use absolute paths, make relative paths impossible to supply.

**Apply this to every tool in the harness** — not just novel tools. Existing tools with ambiguous parameters or error-prone formats are ACI debt that compounds across every agent session.

---

## Test How the Model Uses Your Tools

Run many example inputs to see what mistakes the model makes; iterate on the tool definition until errors disappear. A good tool definition includes example usage, edge cases, input format requirements, and clear boundaries from other tools. Think of it as a docstring for a junior developer — if it would confuse a new hire, it will confuse the model.

---

## When to Promote an Action to a Tool

Not every action needs to be a dedicated tool call — bash covers most actions through composability. Promote an action to a dedicated tool when one or more of these apply:

| Reason | What it enables |
|---|---|
| **UX** | Catch and render specific actions to the user in a particular way (e.g., AskUserQuestion renders in a dedicated UI component) |
| **Guardrails** | Run validation before execution — e.g., a file edit tool can check a staleness hash to verify the file hasn't changed since the model last read it |
| **Concurrency control** | Group actions by concurrency safety — read-only tools can run in parallel; write tools need serialization |
| **Observability** | Isolate specific actions for latency and token-usage logging |
| **Autonomy** | Group by undoability — if the harness can undo an action, it can approve it more freely without human confirmation |

The autonomy axis is particularly useful for permission design: operations the harness can roll back (git-tracked writes, database transactions with rollback) can be auto-approved; operations that cannot be undone (external API calls with side effects, file deletes) require human confirmation regardless of confidence. This creates a more precise permission model than action category alone — finer-grained than "allow all file writes" or "block all shell commands."

---

## Structured Tool Output Beats Format Instructions

When you need reliable structured output from the model, create a tool — don't rely on output format instructions. Claude follows tool schemas (typed parameters, required fields) more reliably than markdown format specs. Format instructions are advisory; tool schemas are structural.

The failure mode of format instructions: Claude appends extra sentences, omits required fields, or uses a slightly different structure. Each deviation requires parsing logic or retry handling. A tool with structured parameters eliminates the deviation at the source.

The Anthropic Claude Code team tested this building the AskUserQuestion tool: (1) adding a parameter to an existing tool mixed concerns and confused Claude; (2) modifying output format instructions was unreliable; (3) a dedicated tool with structured output worked because "Claude seemed to like calling this tool." Tool adoption by the model matters — a well-designed tool the model naturally reaches for outperforms a correctly-specified tool the model underuses.

---

## Agent-Driven Context Building

As models improve, prefer giving them search tools over pre-loading context. A Grep tool lets the agent find what it needs; a RAG pipeline gives the agent what you predicted it would need.

> "As Claude gets smarter, it becomes increasingly good at building its context if it's given the right tools."
> — Anthropic, Claude Code team

Pre-loaded context (RAG injection, stuffed system prompts) reflects older model capabilities. Capable models can navigate a codebase, read files recursively, and construct their own working context if given the right search primitives. The design shift: from injecting context to giving the model the tools to retrieve context.

---

## Context Rot

Loading rarely-needed information into the system prompt creates context rot: tokens consumed on every request for content that's only occasionally relevant. The information pollutes context and can interfere with the agent's primary task.

Mitigation patterns:
- **Progressive disclosure**: link to documentation the agent can load when relevant, rather than including it upfront
- **Subagent**: route specialized queries (e.g., "how does this tool work?") to a subagent with deep expertise in that domain — keeps the main system prompt lean
- **Path-scoped rules**: in `.claude/rules/`, load domain-specific context only when Claude works in matching directories

Context rot is the system-prompt corollary to the tool count problem: both degrade performance by consuming reasoning budget on irrelevant information.
