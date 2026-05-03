# Hermes Skills System & Deep Research

## Tools vs Skills

| | Tools | Skills |
|---|---|---|
| Format | Python functions via JSON schema | Markdown documents |
| Execution | Deterministic | Agent reads and follows |
| Authorship | Human (core Python files) | Agent self-authors, humans can write too |
| Change method | Edit Python source | Create/update .md file |
| ~Count | 47 built-in | Unlimited; grows over time |

**Rule:** Never edit Python tool files for workflow changes. Create or update a skill doc instead.

---

## The Self-Authoring Loop (Closed Learning Loop)

After completing a complex task successfully, Hermes:

1. **Execute** — completes the task
2. **Evaluate** — identifies what sequence of steps, tool calls, and reasoning produced the outcome
3. **Extract** — codifies that sequence into a reusable skill document (markdown)
4. **Refine** — improves the skill during future use
5. **Retrieve** — loads the skill index; reads the relevant skill doc when a similar task recurs

Skills live in `~/.hermes/skills/`. New `.md` files appear there after successful completions.

**Compounding effect:** Nous Research benchmarks show an agent running self-created skills completed research tasks **40% faster** than a fresh instance with zero prompt tuning. Value builds over weeks, not sessions.

**Brittle point:** Markdown playbooks break when the world changes underneath them (API auth updates, DOM changes). When a skill fails, the agent re-evaluates and rewrites the skill from scratch.

---

## Skills Hub: agentskills.io

Hermes uses the **agentskills.io** open standard — skills are compatible across agents that implement the standard.

```bash
hermes skills           # Browse and install from the hub
/skills                 # Same, from inside a session
```

Community skills undergo a security scan on install. Quarantined skills go to `.hub/quarantine/` with a reason; an audit log is maintained at `.hub/audit.log`.

---

## Deep Research Architecture

When handed a complex research task, Hermes runs a structured multi-phase workflow:

### Phase 1: Strategic Planning (think_tool)

`think_tool` is a forced pause — the model must articulate a complete investigation plan before any execution:
- Map the data vectors
- Define scope and constraints
- Formulate hypotheses
- Identify required sub-agent specializations

No research starts until this plan is complete.

### Phase 2: Parallel Sub-Agent Execution (ConductResearch)

`ConductResearch` delegates specific research topics to **isolated sub-agents** running in parallel. Each sub-agent gets:
- Its own clean context window
- Isolated terminal session
- Restricted toolset matching the specific task

Examples of simultaneous specializations:
- Web scraping via headless browser
- Database queries
- Python/statistical analysis scripts
- API data collection

Sub-agents return structured JSON to the primary orchestrator.

### Phase 3: Synthesis (think_tool second pass)

After parallel work completes:
- Evaluate what came back
- Check for gaps in coverage
- Determine if objective is met
- If not met → iterate with new research vectors
- If met → call `ResearchComplete` and proceed

Predefined depth boundaries prevent infinite recursion.

### Phase 4: Report Generation

Mini-reports from sub-agents are merged by a large-context model (minimum 64K token window) into a cohesive, cited document.

---

## Hardware Reality for Local Deep Research

Running parallel sub-agents locally is GPU-intensive. Practical approach on consumer hardware:

- **Primary orchestrator:** 32B model (qwen2.5-coder:32b via Ollama)
- **Sub-agents:** Smaller quantized model (7B–14B) for routing and extraction
- **Final synthesis:** Orchestrator model again

Single-GPU setups will bottleneck on parallel research workflows — sequential execution is the fallback.

---

## Sub-Agent Config

```yaml
delegation:
  max_concurrent_children: 3     # Parallel sub-agents per batch
  max_spawn_depth: 1             # 1=flat orchestration, 2-3=nested
  orchestrator_enabled: true
  # model: "google/gemini-3-flash-preview"   # Override sub-agent model
  # provider: "openrouter"                   # Override sub-agent provider
```

Increasing `max_spawn_depth` beyond 1 enables nested orchestration (sub-agents spawning their own sub-agents), useful for very large research trees.
