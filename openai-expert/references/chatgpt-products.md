# ChatGPT Products

## Plans (April 2026)

| Plan | Key Features |
|------|-------------|
| Free | GPT-5.4 Mini, limited messages, web search, image upload |
| Go | Expanded usage, faster responses |
| Plus | Full model access, Memory, all tools |
| Pro | Highest usage limits, o3-pro access |
| Business | Team workspace, admin tools, no training on data |
| Team | Collaborative workspace, advanced models, DALL-E, Advanced Data Analysis |
| Enterprise | SSO, unlimited context, admin controls, audit logs, private data residency |
| Edu | Enterprise-level features for academic institutions |

Note: As of February 2026, every active ChatGPT model belongs to the GPT-5 family. GPT-4 series and o-series models are retired in the consumer product (still available via API).

---

## Projects

Smart workspaces that group related chats together with:
- Uploaded reference files that persist across chats in the project
- Custom instructions specific to the project
- ChatGPT stays on-topic and retains context across sessions

Useful for: ongoing work streams, research projects, codebases.

---

## Canvas

A collaborative document/code editing surface within ChatGPT.

- Available to all users (Free and Paid) on GPT-4o by default
- Python code execution available inside Canvas
- Can be enabled for custom GPTs by the GPT creator
- Edit documents and code collaboratively with the model in a side-by-side panel

---

## Memory

Cross-session persistent memory. Stores facts the user shares across conversations.

- Available to Plus users globally; Europe/Korea rolling out
- Users can view, edit, and delete individual memory items
- Memory is referenced automatically in future conversations
- Can be disabled per-conversation or globally

---

## GPTs (Custom Assistants)

User-buildable specialized assistants with custom instructions, tools, and knowledge.

- Enterprise/Edu users can select any model (GPT-4o, o3, o4-mini, etc.)
- Canvas can be enabled for a GPT by its creator
- Can be shared within an organization or published publicly
- GPTs can have: custom system prompts, uploaded knowledge files, web browsing, code execution, image generation, API actions

---

## ChatGPT Search

Web search integration that retrieves live results with cited sources.

- Powered by the same model used for `web_search_preview` in the API
- GPT-4o search preview: 90% SimpleQA benchmark
- GPT-4o mini search preview: 88% SimpleQA benchmark
- Sources cited inline in responses

---

## Agent Mode (formerly Operator)

Autonomous web/computer agent built into ChatGPT.

**History:**
- January 2025: Launched as "Operator" (research preview, ChatGPT Pro only, US)
- July 2025: Absorbed into ChatGPT as "Agent Mode"

**Access:** Pro, Plus, and Team users via the tools dropdown in the composer.

**How it works:**
- Powered by CUA (Computer-Using Agent) model
- Combines GPT-4o vision with reinforcement learning
- "Sees" via screenshots, interacts via mouse/keyboard simulation
- Works in a browser without requiring custom API integrations

**Benchmarks:**
- OSWorld (full computer use): 38.1%
- WebArena (web tasks): 58.1%
- WebVoyager (web tasks): 87%

**Example tasks:** managing calendars, planning meals, competitive analysis, creating slide decks, form filling, multi-step web research.
