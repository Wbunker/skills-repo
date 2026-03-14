# Getting Started — Practical Map Creation

Reference for creating your first Wardley Map, running mapping sessions, and common pitfalls.

## The Mapping Process: Step by Step

### Step 1: Define the Scope
Before drawing anything, clarify:
- **What user/customer are we mapping for?**
- **What need or journey are we mapping?**
- **What is the business context?** (new product, competitive analysis, cost reduction, etc.)

Don't try to map everything at once. Start with one user and one set of needs.

### Step 2: Identify the User and Need (Top of Chain)
Write the user at the top of a blank canvas.

**Questions:**
- Who are they? (Segment, persona, role)
- What do they need from us? (Not what they want — what they need)
- What does success look like for them?

**Example:**
```
[Enterprise IT Manager]
        │
[Reliable software deployments]
```

### Step 3: Build the Value Chain Downward
For each component identified, ask: "What does this need to exist?"

Work downward from the user need. For each component:
1. Name the component simply
2. Ask what it depends on
3. Add the dependencies below it with arrows

**Tips:**
- Don't worry about position on the X-axis yet — just get the chain right
- Include *everything* — internal capabilities, external services, physical assets
- Stop when you reach true commodities (electricity, the internet, etc.)
- Aim for 10–20 components on a first map (5 is too few, 50 is too many)

### Step 4: Position on the Evolution Axis
For each component, place it on the X-axis:

**Quick positioning test:**
| Question | Genesis | Custom | Product | Commodity |
|----------|---------|--------|---------|-----------|
| Can you buy it off-shelf? | No | Rarely | Yes | Yes, widely |
| How many suppliers? | Almost none | Few | Many | Very many |
| Is it well understood? | Poorly | Partially | Well | Completely |
| Does it have standards? | None | Competing | Some | Established |

**Don't overthink it.** Approximate is fine. Marks on a map that can be moved beat blank paper.

### Step 5: Review and Challenge

Once you have a draft map, ask:
- Does the Y-axis position (visibility to user) make sense?
- Does the X-axis position (evolution stage) make sense?
- Are the dependencies correct?
- What is missing?
- Are there any obvious mismatches? (e.g., building commodity components)

### Step 6: Look for Insights

With the map visible, ask:
- **Where are we investing?** (Which components are getting resources)
- **Does that match strategic importance?** (Are we over-investing in commodities?)
- **What is evolving?** (Which components will move right over the next 1–3 years)
- **What opportunities does that create?** (What new capabilities become possible)
- **Where are our competitors?** (Can you add them to the map)

## Running a Mapping Workshop

### Setup
- Physical: Large whiteboard, sticky notes (different colors for different teams or component types)
- Digital: Miro, Wardley Maps online editor, Excalidraw
- Time needed: 1–4 hours for a first map; 30–60 min for teams with experience
- Participants: 3–8 people; include people who know the business, technology, and user

### Workshop Agenda

**Opening (10 min):**
- Explain the two axes briefly
- Agree on the scope (which user, which need)

**Value Chain Building (30–45 min):**
- Collaboratively identify components
- Debate dependencies
- Write each component on a sticky note

**Evolution Positioning (20–30 min):**
- For each component, agree on approximate evolutionary stage
- Expect debate — disagreements reveal important assumptions

**Pattern Identification (20–30 min):**
- What stands out?
- Where is the mismatch between investment and stage?
- What is about to change?

**Action Items (15 min):**
- What decisions does this map inform?
- What needs more investigation?
- When will we revisit the map?

### Facilitation Tips
1. **Use sticky notes** — physical movement enables rethinking positions
2. **Challenge everything** — the value is in the debate, not the final artifact
3. **Avoid perfect maps** — progress beats perfection
4. **Name disagreements** — when people place components differently, capture both views
5. **Map the AS-IS first** — before mapping the desired future state
6. **Don't worry about aesthetics** — ugly maps are fine; the thinking matters

## Common Mistakes and How to Avoid Them

### Mistake 1: Starting with the Technology
**Problem**: Beginning with what you build rather than who you serve.
**Fix**: Always start with the user and work downward.

### Mistake 2: One Enormous Map
**Problem**: Trying to map an entire enterprise in one session.
**Fix**: Scope tightly — one user, one need, one value chain. You can create multiple maps.

### Mistake 3: Treating the Map as Final
**Problem**: Creating a map once and not revisiting it.
**Fix**: Maps should be living artifacts, updated as the landscape changes or your understanding improves.

### Mistake 4: The Organizational Chart Trap
**Problem**: Mapping teams and departments rather than components and capabilities.
**Fix**: Map capabilities (things), not organizational units (people).

### Mistake 5: Confusing "Visible to User" with "Important"
**Problem**: Thinking that low on the Y-axis means unimportant.
**Fix**: Remind participants that infrastructure is at the bottom because it's invisible to users, not because it's unimportant.

### Mistake 6: Binary Thinking on Evolution
**Problem**: Placing everything exactly at Genesis, Custom, Product, or Commodity.
**Fix**: The axis is continuous. Components can be between stages.

### Mistake 7: Ignoring Future Movement
**Problem**: Mapping only the current state without considering evolution.
**Fix**: Add movement arrows showing where components are heading. Use different colors or dotted arrows.

## The First Map Exercise: Coffee Shop

A beginner exercise for learning map construction:

**User**: Customer who wants coffee
**Need**: Hot, good coffee, quickly

**Components to map:**
- Cup of coffee
- Espresso shot
- Milk (steamed)
- Coffee beans
- Espresso machine
- Water
- Staff (barista)
- Payment system
- Shop lease/location
- Electricity
- Coffee supply chain

**Exercise**: Position each on the evolution axis, then ask:
- What is Gen Coffee Shop building vs. buying?
- Where is there waste?
- What is the coffee shop's actual differentiator?

## Tools for Mapping

### Physical
- Large whiteboard + markers
- Sticky notes (3 colors: user needs, components, external services)
- Camera to photograph the result

### Digital
- **Wardley Maps Online** (mapscript.net) — purpose-built text-based tool
- **Miro** — flexible, good for remote workshops
- **Excalidraw** — lightweight, sketch-like
- **draw.io / Lucidchart** — less ideal but workable
- **OnlineWardleyMaps** (app.diagrams.net variant) — specialized template

### Notation (for text-based tools like MapScript)
```
component User [0.95, 0.5]
component Cup of Tea [0.9, 0.6]
component Hot Water [0.7, 0.8]
component Tea [0.6, 0.7]
component Kettle [0.5, 0.7]
component Power [0.1, 0.95]

User -> Cup of Tea
Cup of Tea -> Hot Water
Cup of Tea -> Tea
Hot Water -> Kettle
Kettle -> Power
```

## When to Map

| Situation | Why Map? |
|-----------|---------|
| New product development | Understand what to build vs. buy |
| Competitive analysis | See where competitors are exposed |
| Cost reduction | Identify commoditizable components |
| Acquisitions | Understand what you're buying |
| Technology decisions | Avoid building commodity components |
| Strategic planning | Ground strategy in landscape reality |
| Organizational design | Align structure to evolution stages |
| Partnership decisions | Identify complementary capabilities |

## Iterating on Maps

Your first map will be wrong. That's fine. The process of correcting it is where the value comes from.

**Iteration cycle:**
1. Create draft map
2. Challenge assumptions with team
3. Research specific components (where are competitors? what's the evolution rate?)
4. Update map
5. Look for new patterns
6. Make decisions based on updated understanding
7. Revisit map when landscape changes

The map is never done — it's always approximately right, and that's enough.
