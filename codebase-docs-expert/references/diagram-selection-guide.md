# Diagram Selection Guide
## Which Diagram Type to Use, When, and Why

This guide helps you choose the right diagram type for your goal. For full syntax,
examples, and best practices for each type, see [diagrams.md](diagrams.md).

---

## The 13 Diagram Types at a Glance

| # | Diagram Type | Shows | Good For | Mermaid Keyword |
|---|-------------|-------|----------|-----------------|
| 1 | **Context diagram** | System + everything around it | What is inside vs outside? | `C4Context` or `flowchart` |
| 2 | **Component diagram** | Major building blocks | What are the major parts? | `C4Container`, `C4Component`, or `flowchart` with subgraphs |
| 3 | **Sequence diagram** | Who talks to whom over time | What happens when the user clicks Submit? | `sequenceDiagram` |
| 4 | **State diagram** | How something changes state | What states can this object be in? | `stateDiagram-v2` |
| 5 | **ERD** | Data structure and relationships | How is the data organized? | `erDiagram` |
| 6 | **Control flow** | What happens in what order | What does this function do step by step? | `flowchart` |
| 7 | **Deployment diagram** | Where software runs | Where does this code execute? | `C4Deployment` or `flowchart` |
| 8 | **Use case diagram** | What users/actors are trying to do | Why does this software exist? | `flowchart` or actor-goal table |
| 9 | **Decision table** | Rules without hiding them in code | What exact rules drive this behavior? | Markdown table |
| 10 | **Event analysis** | Important events in the business process | What meaningful things happen? | `flowchart` or event catalog table |
| 11 | **Dependency analysis** | What depends on what | What breaks if I change this? | `flowchart` or dependency matrix |
| 12 | **CRUD matrix** | Who creates/reads/updates/deletes what data | Which service is allowed to change this? | Markdown table |
| 13 | **Class diagram** | OOP structure (inheritance, composition) | How do these classes relate? | `classDiagram` |

---

## Which Diagrams Help Most with Code Understanding?

If your goal is **"make code easier to understand"**, this is the recommended combination:

```
Must-Have (do these first)
──────────────────────────
1. Context diagram      → what the system is and what surrounds it
2. Component diagram    → what the major pieces are
3. Sequence diagram     → how they interact at runtime
4. ERD                  → how data is shaped
5. Flowchart            → how tricky logic works step by step

High Value (add these next)
───────────────────────────
6. State diagram        → how behavior changes over time (lifecycles)
7. Dependency analysis  → where coupling exists (refactoring guide)
8. Decision table       → what rules drive behavior (policy code)

Situational (add when relevant)
───────────────────────────────
9. Deployment diagram    → when infrastructure matters
10. Event analysis       → when the system is event-driven
11. Use case diagram     → when onboarding non-technical stakeholders
12. CRUD matrix          → when data ownership is unclear or contested
13. Class diagram        → when OOP inheritance/composition is complex
```

### What This Combination Gives You

| Diagram | What You Understand |
|---------|-------------------|
| Context | What the system **is** |
| Component | What the pieces **are** |
| Sequence | How the pieces **interact** |
| ERD | How the data is **shaped** |
| Flowchart | How the logic **works** |
| State | How behavior **changes over time** |
| Dependency | Where **coupling** exists |
| Decision table | What **rules** drive behavior |

---

## Simple Rule of Thumb

| You Want to Understand... | Use This |
|--------------------------|----------|
| Movement of data | Flowchart / data flow diagram |
| Interaction over time | Sequence diagram |
| Object lifecycle | State diagram |
| Database structure | ERD |
| Branching logic | Flowchart / decision tree |
| System architecture | Component diagram / C4 |
| System boundary | Context diagram |
| Infrastructure | Deployment diagram |
| Business rules | Decision table |
| Event-driven behavior | Event catalog / flow timeline |
| Coupling and change risk | Dependency matrix / graph |
| Data ownership | CRUD matrix |
| User goals and features | Use case diagram / actor-goal table |

---

## Choosing by Audience

Different stakeholders need different diagrams:

| Audience | Start With | Add If Needed |
|----------|-----------|---------------|
| **New developer** (onboarding) | Context, Component, Sequence, ERD | Dependency analysis, "Where to Look" guide |
| **Bug fixer** | Sequence (trace the flow), State (check lifecycle), Flowchart (check logic) | Decision table if rule-driven |
| **Feature developer** | Component (find the right module), Sequence (understand current flow), ERD (data changes) | Dependency analysis (what else breaks) |
| **Architect / tech lead** | Context, Component, Dependency analysis, Event analysis | CRUD matrix, Deployment |
| **Operator / SRE** | Deployment, Context (external deps), Sequence (failure flows) | Event analysis (async flows) |
| **Product manager** | Use case diagram, Context | State (for lifecycle features) |
| **Security reviewer** | Context (trust boundaries), Deployment (network), Decision table (auth rules) | CRUD matrix (data access) |

---

## Choosing by System Type

| System Type | Essential Diagrams | Less Useful |
|-------------|-------------------|-------------|
| **Monolith** | Component (L3), Flowchart, ERD, Dependency analysis | Context (simple), Deployment (single target) |
| **Microservices** | Context, Component (L2), Sequence, Event analysis, Dependency, CRUD matrix | Class diagram, Flowchart (per-service) |
| **Event-driven** | Event analysis, Sequence, State, Producer-consumer map | Flowchart (logic is in handlers) |
| **Data pipeline** | Flowchart (pipeline stages), ERD (schemas), CRUD matrix | Component, Use case |
| **Library / SDK** | Class diagram, Sequence (usage patterns), State (if stateful) | Deployment, CRUD matrix |
| **CLI tool** | Flowchart (command logic), State (if stateful), Context | Component, Deployment |
| **SaaS product** | Context, Component, Deployment, Use case, ERD, CRUD | All are relevant |

---

## Choosing by Goal

| Your Goal | Diagram Combination |
|-----------|-------------------|
| **Onboard a new developer** | Context → Component → Sequence (primary flow) → ERD → "Where to Look" guide |
| **Fix a specific bug** | Sequence (trace the broken flow) → State (check lifecycle) → Flowchart (check logic) |
| **Add a new feature** | Component (where does it go?) → Sequence (existing pattern to follow) → ERD (data changes) → Dependency (what else to update) |
| **Refactor safely** | Dependency analysis → CRUD matrix → Component (current structure) → Component (target structure) |
| **Prepare for production** | Deployment → Context (external deps) → Event analysis (async) → Decision table (business rules) |
| **Conduct architecture review** | Context → Component → Dependency → CRUD → Event analysis |
| **Write ARCHITECTURE.md** | Context → Component → Sequence (key flows) → ERD → key Decision tables |
| **Security audit** | Context (trust boundaries) → Deployment (network) → CRUD (data access) → Decision table (auth rules) |
| **Performance investigation** | Sequence (find bottleneck) → Deployment (infrastructure) → Dependency (sync vs async) |

---

## Diagram Format Decision

```
Is this for AI tools to read?
├── Yes → Use Mermaid or ASCII
│   ├── Complex diagram with many elements → Mermaid (renders visually too)
│   ├── Simple flow or quick reference → ASCII (works in any text file)
│   └── Embedding in code comment → ASCII (always readable)
│
└── No (presentation, external stakeholders)
    └── Use any visual tool (draw.io, Excalidraw, Figma)
        └── Keep source file in repo alongside exported PNG/SVG
```

**Default**: Mermaid in ` ```mermaid ` code blocks. GitHub, GitLab, and most doc sites render them automatically. AI tools read the raw syntax.

---

## Layering Diagrams for Progressive Understanding

Build understanding incrementally. Start broad, zoom in where needed:

```
Level 1: Orient (5 minutes)
  └── Context diagram → "What is this system?"

Level 2: Structure (15 minutes)
  └── Component diagram → "What are the pieces?"
  └── ERD → "What data exists?"

Level 3: Behavior (30 minutes)
  └── Sequence diagram (key flows) → "How do the pieces interact?"
  └── State diagram (key entities) → "How do things change over time?"

Level 4: Deep dive (as needed)
  └── Flowchart → "How does this specific logic work?"
  └── Decision table → "What rules drive this?"
  └── Event analysis → "What events flow through the system?"

Level 5: Analysis (for refactoring / review)
  └── Dependency analysis → "What is coupled to what?"
  └── CRUD matrix → "Who owns what data?"
  └── Deployment diagram → "Where does it all run?"
```

Not every codebase needs Level 5. Most developers working on a feature need Levels 1–3. Go deeper only when the problem requires it.
