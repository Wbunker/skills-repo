---
name: context-layer-architect
description: |
  Audit, design, and build context layers (CLAUDE.md/AGENTS.md hierarchies) for codebases.

  Triggers:
  - "Audit my context layer" or "audit my CLAUDE.md files"
  - "Build a context layer" or "create a context layer"
  - "Where should I add CLAUDE.md files?"
  - "What context nodes am I missing?"
  - "Help me set up progressive disclosure for my codebase"
  - "Analyze my codebase for context engineering opportunities"
  - "What skills should I create for this codebase?"
  - "Interview me about my codebase architecture"
  - /context-layer, /audit-context, /build-context-layer

  Use when the user wants to:
  1. Audit existing CLAUDE.md/AGENTS.md files for quality and coverage
  2. Identify semantic boundaries where new nodes should be placed
  3. Discover tribal knowledge that should be captured
  4. Find opportunities for skills and hooks
  5. Restructure a bloated root node into a proper hierarchy
  6. Interview stakeholders to extract architectural knowledge
---

## Overview

Build context layers that make agents perform like senior engineers. This skill audits existing context, identifies gaps, and guides you through capturing tribal knowledge that code alone cannot express.

**Core principle:** Progressive disclosure. Load only what's needed, when it's needed. The goal is maximum signal per token—compression, not documentation.

---

## Workflow

### Phase 1: Parallel Exploration

Spin up multiple explore agents simultaneously to analyze the codebase from different angles:

```
Agent 1: Map semantic boundaries (where responsibilities shift)
Agent 2: Analyze existing CLAUDE.md/AGENTS.md files
Agent 3: Identify patterns, conventions, and architectural decisions
Agent 4: Find tribal knowledge candidates (comments, TODOs, unusual patterns)
```

**Launch these agents in parallel using the Task tool with subagent_type=Explore.**

### Phase 2: Synthesis

Combine agent findings into a structured analysis:
- Current layer coverage and gaps
- Proposed node hierarchy
- Identified compression opportunities
- Skill and hook candidates
- Open questions requiring human input

### Phase 3: Deep Interview

Interview the user in detail using AskUserQuestion about:
- Technical implementation decisions
- Historical constraints and "why" behind patterns
- Invariants and anti-patterns
- Integration quirks and tribal knowledge
- Concerns and tradeoffs

**Interview prompt:**
> Read the exploration findings and interview me in detail about literally anything: technical implementation, architectural decisions, historical constraints, invariants, concerns, tradeoffs. Ask non-obvious questions. Be thorough. Continue until complete, then generate the recommendations.

### Phase 4: Generate Recommendations

Output a comprehensive plan with:
- Node hierarchy with proposed content outlines
- Skill candidates with trigger patterns
- Hook opportunities
- Compression analysis (before/after token estimates)
- Priority order for implementation

---

## Exploration Agent Prompts

### Agent 1: Semantic Boundary Mapper

```
Analyze this codebase to identify semantic boundaries—places where responsibilities shift, contracts matter, or complexity warrants dedicated context.

Look for:
1. Major subsystems and their purposes
2. Service/module boundaries
3. Where vocabulary changes (different domain terms)
4. Integration points between components
5. Areas where different people would have expertise
6. Directories with distinct responsibilities

Output:
- List of semantic boundaries with paths
- Proposed hierarchy depth (recommend 2-3 levels max)
- Areas that DON'T need their own node (let parent cover)
- Token size estimates per area (lines of code × ~0.75)
```

### Agent 2: Existing Layer Analyzer

```
Find and analyze all CLAUDE.md and AGENTS.md files in this codebase.

For each file, assess:
1. Line count and estimated token cost
2. Signal-to-noise ratio (project-specific vs generic)
3. Coverage: what areas does it cover?
4. Contradictions with other nodes
5. Stale content (references non-existent files/patterns)
6. Content that belongs elsewhere (wrong level in hierarchy)

Identify:
- Flat ball-of-mud files that need splitting
- Duplicated content across files
- Missing downlinks between related nodes
- Generic advice that should be deleted

Output a health report with specific line numbers for issues.
```

### Agent 3: Pattern Discoverer

```
Analyze this codebase to discover patterns, conventions, and architectural decisions that should be documented in context nodes.

Look for:
1. Recurring code patterns (how are services structured? how are APIs defined?)
2. Naming conventions that differ from defaults
3. Error handling patterns
4. Testing patterns and conventions
5. Configuration patterns
6. Authentication/authorization patterns
7. Logging and observability patterns

For each pattern found:
- Where it's used (file paths)
- Whether it diverges from conventions (cognitive inertia risk)
- Example code snippet (under 20 lines)

Flag patterns that:
- An agent would likely get wrong without guidance
- Differ from what training data would suggest
- Have non-obvious "why" behind them
```

### Agent 4: Tribal Knowledge Hunter

```
Search for evidence of tribal knowledge—context that lives in people's heads but not in code.

Look for:
1. Comments mentioning incidents, bugs, or "don't touch this"
2. TODOs with context about why something exists
3. Unusual code that seems like workarounds
4. Dead-looking code that might serve hidden purposes
5. Configuration with non-obvious values
6. Integration code with external services
7. Feature flags or environment-specific logic

For each candidate:
- Location and surrounding context
- What question it raises (open question for interview)
- Why this matters for agent safety

Also search for:
- Slack/Teams links in comments
- ADR references
- Links to external documentation
- References to specific people or teams
```

---

## Interview Questions Framework

After exploration, interview the user about findings. Use AskUserQuestion tool.

### Architecture & Boundaries

- "The codebase has [X] at the boundary between [A] and [B]. What's the contract between them? What must never happen across this boundary?"
- "I see [pattern] used in [location]. Is this the canonical way to do this, or is there a better example I should point agents to?"
- "Directory [X] looks like it owns [responsibility]. What does it explicitly NOT own?"

### Historical Context

- "This code in [location] looks unusual. Is there history behind why it's structured this way?"
- "I found a reference to [incident/bug]. What should agents know to avoid repeating this?"
- "The [config value] seems arbitrary. Why that specific value?"

### Invariants & Anti-patterns

- "What operations must NEVER be performed in this area of the codebase?"
- "What's the most common mistake someone new makes when working in [area]?"
- "Are there any 'looks safe but isn't' patterns an agent might try?"

### Integration & Dependencies

- "How does [service A] communicate with [service B]? Are there retry/timeout constraints?"
- "What external dependencies does this codebase have that aren't obvious from the code?"
- "Are there any undocumented APIs or integrations an agent needs to know about?"

### Compression Opportunities

- "I'm proposing [X] as a semantic boundary. Does this match how your team thinks about the system?"
- "Should [these related things] be described together or separately?"
- "What's the minimum an agent needs to know to work safely in [area]?"

---

## Output Templates

### Node Hierarchy Proposal

```markdown
## Proposed Context Layer Structure

### Current State
- Root CLAUDE.md: [X] lines ([Y]k tokens) — [assessment]
- Existing nodes: [list with assessments]
- Coverage gaps: [list]

### Proposed Hierarchy

project/
├── CLAUDE.md (target: 50 lines)
│   └── [outline of what stays in root]
├── [area-1]/
│   └── CLAUDE.md (target: [X] lines)
│       └── [outline]
├── [area-2]/
│   ├── CLAUDE.md (target: [X] lines)
│   │   └── [outline]
│   └── [sub-area]/
│       └── CLAUDE.md (target: [X] lines)
│           └── [outline]

### Compression Analysis
| Location | Code Tokens | Node Tokens | Ratio |
|----------|-------------|-------------|-------|
| root     | N/A         | ~400        | —     |
| area-1/  | ~120k       | ~600        | 200x  |
| area-2/  | ~85k        | ~500        | 170x  |

### Implementation Order
1. [First node to create — leaf-first]
2. [Second node]
...
```

### Skill Candidates

```markdown
## Recommended Skills

### [skill-name]
**Trigger:** "[example user request]"
**Purpose:** [what it does]
**Content:** [patterns, workflows, or domain knowledge to include]
**Why a skill vs node:** [loads only when relevant, framework-specific, etc.]

### [skill-name-2]
...
```

### Hook Opportunities

```markdown
## Recommended Hooks

### Pre-commit: [name]
**Trigger:** Before committing in [areas]
**Action:** [validation, reminder, etc.]
**Prevents:** [what mistakes this catches]

### Post-edit: [name]
**Trigger:** After editing [file types/areas]
**Action:** [validation, formatting, etc.]
```

---

## Quality Checklist

Before finalizing recommendations, verify:

**For each proposed node:**
- [ ] Covers a semantic boundary, not just a folder
- [ ] Would have 30+ lines of specific content (not generic)
- [ ] Content can't be inferred from code alone
- [ ] Doesn't duplicate parent or sibling nodes
- [ ] Clear downlinks to related context

**For the overall layer:**
- [ ] Root is minimal (under 60 lines ideal, 300 max)
- [ ] Hierarchy is 2-3 levels deep (not over-engineered)
- [ ] Similar code grouped for compression efficiency
- [ ] Shared knowledge placed at LCA (Least Common Ancestor)
- [ ] No downloaded templates—all project-specific

**For identified content:**
- [ ] Commands over descriptions
- [ ] Examples over explanations
- [ ] Project-specific over generic
- [ ] "Why" over "what"

---

## Anti-Patterns to Flag

See `references/anti-patterns.md` for detailed examples.

**In existing nodes:**
- Generic advice ("write clean code", "use meaningful names")
- Detailed repo structure that will rot
- Content the linter already enforces
- Task-specific guidance in root
- Memories/session history
- Downloaded templates

**In proposed structure:**
- Nodes at every folder (over-engineering)
- Single massive root file (ball of mud)
- Duplicated facts across siblings
- Structural chunking instead of semantic

---

## File Operations: Creating & Improving Nodes

After analysis, the skill should propose concrete file operations:

### Creating New Files

When proposing a new node, output:

```markdown
## NEW FILE: [path/to/CLAUDE.md]

**Why:** [Semantic boundary justification]
**Coverage:** [What code/areas this covers]
**Token budget:** [Target line count]

### Proposed Content:

[Full draft of the CLAUDE.md file content]
```

After user approval, create the file using the Write tool.

### Improving Existing Files

When proposing improvements to existing nodes, output:

```markdown
## IMPROVE: [path/to/existing/CLAUDE.md]

### Issues Found:
1. [Line X-Y]: [Issue description]
2. [Line Z]: [Issue description]

### Proposed Changes:

**Remove** (noise/generic):
- Line X: "[content to remove]"
- Lines Y-Z: [description]

**Add** (missing context):
- [New section or content]

**Move** (wrong location):
- Lines A-B → [destination node]

**Rewrite** (improve compression):
- Current: "[current content]"
- Proposed: "[improved content]"

### After Changes:
- Current: [X] lines ([Y]k tokens)
- Proposed: [A] lines ([B]k tokens)
- Improvement: [reduction %] smaller, [quality improvement]
```

After user approval, apply changes using the Edit tool.

### Tracking Layer Evolution

Create a `.claude/layer-audit.md` file to track improvements over time:

```markdown
# Context Layer Audit Log

## [Date] - Initial Audit
- Total nodes: [X]
- Total tokens: [Y]
- Coverage gaps: [list]
- Quality score: [assessment]

### Changes Made:
- Created: [list of new files]
- Improved: [list of improved files]
- Deleted: [list of removed content]

### Open Items:
- [ ] [Pending improvement]
- [ ] [Question to resolve]

---

## [Date] - Follow-up
...
```

---

## Incremental Improvement Mode

For ongoing maintenance, support incremental improvements:

**Trigger:** "Improve my context layer" or "What can I add to my CLAUDE.md files?"

**Workflow:**
1. Quick scan of existing nodes
2. Identify top 3-5 improvement opportunities
3. Propose specific changes with before/after
4. Apply approved changes
5. Update audit log

**Focus areas for incremental improvement:**
- Newly discovered patterns (from recent work)
- Stale content (references moved/deleted files)
- Missing context (things you had to explain manually)
- Compression opportunities (verbose → concise)
- New tribal knowledge (recent incidents, decisions)

---

## Session-End Context Capture

At end of significant sessions, prompt:

```
Based on this session, should any CLAUDE.md files be updated?

I noticed:
- [Pattern used repeatedly]
- [Gotcha encountered]
- [Command run multiple times]
- [Constraint that wasn't documented]

Would you like me to add any of these to the context layer?
```

**Good candidates:**
- Gotchas discovered during the session
- Commands used repeatedly
- Patterns Claude got wrong until corrected
- Historical context explained verbally

**Bad candidates:**
- Task-specific context that won't apply again
- Explanations of just-built code
- Temporary workarounds

---

## References

- `references/anti-patterns.md` — Detailed anti-patterns with examples
- `references/node-anatomy.md` — What goes in a healthy node
- `references/compression-guide.md` — How to achieve good compression ratios
- `references/interview-guide.md` — Deep interview techniques
- `references/maintenance.md` — Keeping the layer accurate over time
