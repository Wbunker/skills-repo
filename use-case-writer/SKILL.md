---
name: use-case-writer
description: Use case writing expertise based on Alistair Cockburn's framework. Use when writing, reviewing, or teaching use cases — drafting actors and goals, choosing goal levels, filling out the fully-dressed template, writing main success scenarios and extensions, modeling include/extend relationships, choosing formats, or assessing completeness. Covers Cockburn's complete methodology from "The Mini-Book on Use Cases."
---

# Use Case Writer

Based on *The Mini-Book on Use Cases* by Alistair Cockburn.

## The Use Case Mental Model

```
┌─────────────────────────────────────────────────────────────┐
│                      SYSTEM BOUNDARY                         │
│                                                             │
│   Primary Actor ──► [Use Case: Achieve Goal]                │
│        │                    │                               │
│        │              Main Success Scenario                  │
│        │              + Extensions (alt flows)              │
│        │                                                     │
│   Stakeholders ◄── [Postcondition: goal satisfied]          │
└─────────────────────────────────────────────────────────────┘

Goal levels (altitude):
  ☁  Cloud/Summary  — spans multiple user sessions or EBPs
  ≋  Sea-level      — one Elementary Business Process (EBP)  ← target
  ✦  Sub-function   — step inside a sea-level use case
```

## Quick Reference

| Task | Load |
|------|------|
| What is a use case, system boundary, actors, goals, purpose | [foundations.md](references/foundations.md) |
| Goal altitude (cloud/sea-level/subfunction), EBP test, boss test | [goal-levels.md](references/goal-levels.md) |
| Full use case template — all fields explained and populated | [structure-template.md](references/structure-template.md) |
| Writing the main success scenario and extensions (alternate flows) | [scenarios.md](references/scenarios.md) |
| Include, extend, and generalization relationships | [relationships.md](references/relationships.md) |
| Format choices: fully dressed, casual, one-line, brief | [formats.md](references/formats.md) |
| Finding use cases, actors, goals; completeness checks and review | [finding-reviewing.md](references/finding-reviewing.md) |

## Reference Files

| File | Chapters | Topics |
|------|----------|--------|
| `foundations.md` | 1–2 | Use case definition, purpose, system boundary, actors (primary/secondary/offstage), goals, stakeholder interests |
| `goal-levels.md` | 3 | Goal altitude metaphor, cloud/summary, sea-level/user-goal, subfunction/fish, EBP test, boss test, choosing the right level |
| `structure-template.md` | 4 | Fully dressed template: title, scope, level, primary actor, stakeholders & interests, preconditions, postconditions, main success scenario, extensions, technology/frequency notes |
| `scenarios.md` | 5 | Step-writing guidelines, action-response format, main success scenario rules, extension numbering, condition-action format, error extensions |
| `relationships.md` | 6 | Include (factored behavior), extend (optional behavior), generalization (abstract use cases and actors), when to use each |
| `formats.md` | 7 | Fully dressed vs. casual vs. brief vs. one-line, format selection heuristics, conversation-style use cases, index cards |
| `finding-reviewing.md` | 8–9 | Stakeholder interviews, actor-goal listing, scope verification, completeness heuristics (stakeholder coverage, CRUD check, boss test), review checklist |

## Core Decision Trees

### Which format should I use?

```
How well do you understand the use case?
├── Still exploring / early discovery → One-line or Brief
├── Understood, low-risk, minor use case → Casual
└── High-risk, complex, or architectural → Fully Dressed

Is this use case the primary driver of design?
├── Yes → Fully Dressed
└── No → Casual or Brief
```

### Is this the right goal level?

```
Apply the EBP test:
"Can one person, at one time, in one place,
 complete this as a response to a business event,
 leaving the business in a stable state?"
├── Yes → Sea-level (right level for a primary use case)
├── Too large (spans sessions/days/people) → Raise to Summary
└── Too small (a click, a field, a step) → Lower to Sub-function
```

### How do I name a use case?

```
Format: [Verb] + [Object] (from primary actor's perspective)
Good:   "Place Order", "Register Patient", "Transfer Funds"
Bad:    "Order Management", "Patient Registration System", "The Transfer Screen"
        ↑ noun phrases      ↑ system perspective              ↑ UI reference

Apply the boss test: if primary actor's boss asked
"What were you doing all day?" and the actor answered
with this use case title, would the boss be satisfied?
```

## Behavior

When asked to write a use case:
1. Identify the primary actor and their goal (sea-level, from their perspective).
2. Identify stakeholders and their interests.
3. Ask: what is the main success scenario (happy path, no conditions, just numbered steps)?
4. Ask: what can go wrong at each step? → those become extensions.
5. Choose format based on risk/complexity (default to casual for drafts, fully dressed for complex/architectural cases).
6. Review against the completeness checklist in `finding-reviewing.md`.

When reviewing a use case:
- Apply the EBP test to verify goal level.
- Check that each step is from actor OR system perspective (not both).
- Check that extensions cover the most important failure modes.
- Verify preconditions are actually checked before the use case starts.
