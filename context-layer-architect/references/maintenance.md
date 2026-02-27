# Maintaining the Context Layer

Keep your compression accurate as code evolves.

---

## Table of Contents

1. [Why Maintenance Matters](#why-maintenance-matters)
2. [The Sync Process](#the-sync-process)
3. [What Triggers Updates](#what-triggers-updates)
4. [Leaf-First Updates](#leaf-first-updates)
5. [Preventing Drift](#preventing-drift)
6. [The Reinforcement Loop](#the-reinforcement-loop)
7. [Automation Options](#automation-options)

---

## Why Maintenance Matters

Without maintenance, **drift** creeps in—nodes that describe how code *used to* work.

Drift is compression rot. Stale nodes aren't signal anymore. They're noise that actively misleads.

**Symptoms of drift:**
- Agents follow instructions that don't apply anymore
- Agents look for files that don't exist
- Agents miss files that do exist
- Agents use deprecated patterns
- You keep correcting the same misunderstanding

**The good news:** Maintenance can be lightweight. 5-10 minutes per significant PR when done manually.

---

## The Sync Process

On every merge to main:

1. **Detect** which files changed
2. **Identify** which nodes cover those changes
3. **For each affected node** (leaf-first, working up):
   - Read the diff and existing node
   - Re-summarize if behavior changed
   - Propose updates
4. **Human reviews and merges**

### Example Flow

```
PR: Refactored payment validation

Changed files:
- payment/validators/amount.ts
- payment/validators/card.ts
- payment/PaymentService.ts

Affected nodes:
1. payment/validators/CLAUDE.md (if exists)
2. payment/CLAUDE.md
3. Possibly services/CLAUDE.md

Check each node:
- Does the node mention anything that changed?
- Would an agent reading this node be misled?
- Are there new patterns to capture?
```

---

## What Triggers Updates

Not every code change requires a node update.

**Update when:**
- New patterns or conventions introduced
- Invariants change
- Public contracts change
- New gotchas discovered
- Existing node would mislead

**Skip when:**
- Implementation details change but contracts don't
- Bug fixes that don't change patterns
- Refactors that don't change responsibilities

### The "Would It Mislead?" Test

For each change, ask:

> "If an agent read the current node and worked on this code, would it make a mistake?"

If yes → update. If no → leave it.

---

## Leaf-First Updates

When code changes, update nodes **leaf-first**, working up the tree.

**Why:** Parent nodes summarize children. Updating a parent before its children means summarizing stale content.

```
Change in payment/validators/amount.ts

Update order:
1. payment/validators/CLAUDE.md (if exists)
2. payment/CLAUDE.md
3. services/CLAUDE.md
4. Root CLAUDE.md (only if system-wide impact)
```

Most changes only affect leaf nodes. The hierarchy localizes maintenance burden.

---

## Preventing Drift

### Treat Nodes Like Code

- Review them in PRs that change covered areas
- Add "update CLAUDE.md" to PR checklist
- Include nodes in code review scope

### Periodic Audits

Monthly or quarterly:
- Read a sample of nodes alongside the code they cover
- Check for stale references
- Verify invariants still hold
- Remove outdated content

### Trust Agent Feedback

If agents keep getting something wrong:
- The node might be stale
- The node might be missing context
- The node might be misleading

Agent mistakes are signals about the layer's health.

---

## The Reinforcement Loop

When agents use the layer, they surface what's missing:

- **Edge cases:** Contradictions, undocumented patterns
- **Proposed updates:** Refined pitfalls, corrected invariants
- **Questions:** Things the node should have answered

Feed learnings back into the layer. Future agents start from a better baseline.

```
Code changes
    ↓
Nodes updated
    ↓
Agents use updated context
    ↓
Agents surface what's missing
    ↓
Learnings feed back into nodes
    ↓
Better context for next change
    ↓
(repeat)
```

**Your codebase becomes a reinforcement learning environment.** Agents get fine-tuned through better context, not expensive model training.

---

## Automation Options

### Manual (5-10 min per PR)

After merging significant changes:
1. Review which nodes might be affected
2. Read diff alongside node
3. Update if node would mislead

Start here to learn the patterns.

### Semi-Automated

Build a script that:
1. Detects changed files on merge
2. Maps them to covering nodes
3. Generates PR with suggested updates
4. Human reviews and merges

Catches drift you'd otherwise miss.

### Fully Automated

Agent monitors merges, proposes updates, runs through CI. Human approves.

The endgame—but start manual, automate when you understand patterns.

---

## Capturing Tribal Knowledge Incrementally

Don't try to capture everything upfront. Capture as you go:

### During Work

When you explain something to an agent that it should have known:

```
"That's good context. Should I add this to the [area] CLAUDE.md?"
```

### After Incidents

When something breaks:

```
"What should agents know to avoid this in the future?"
```

### After Decisions

When architecture changes:

```
"This decision affects how agents should work in [area].
Should I update the context layer?"
```

### Session-End Prompt

At end of significant work:

```
"Based on this session, I noticed:
- [Pattern discovered]
- [Gotcha encountered]
- [Constraint explained]

Should any of these go in the context layer?"
```

---

## Signs You're Doing It Right

**Positive indicators:**
- Agents find relevant files on first try
- Fewer "I couldn't find X" moments
- New team members (human or agent) productive faster
- Agents respect existing patterns
- Rarely correct the same misunderstanding twice

**The compound effect:**
- Each task leaves the layer slightly better
- Agent performance improves over weeks/months
- Onboarding time drops
- Institutional knowledge survives turnover

---

## The Audit Log

Track layer health in `.claude/layer-audit.md`:

```markdown
# Context Layer Audit Log

## 2024-03-15 - Quarterly Review

### Metrics
- Nodes: 12
- Total tokens: ~8,400
- Average node: 70 lines

### Health Check
- ✅ Root under 60 lines
- ✅ No generic advice found
- ⚠️ payment/CLAUDE.md references deleted file
- ⚠️ Missing node for new analytics/ area

### Actions Taken
- Fixed stale reference in payment/CLAUDE.md
- Created analytics/CLAUDE.md
- Compressed billing/CLAUDE.md (120 → 85 lines)

### Open Items
- [ ] Interview platform team about new caching layer
- [ ] Capture rate limiting patterns after next incident review

---

## 2024-02-01 - Initial Build
...
```

Track improvements over time. Celebrate compression gains.
