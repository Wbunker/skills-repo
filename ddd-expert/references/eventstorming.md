# EventStorming — Chapter 12

EventStorming is a collaborative workshop technique for rapidly exploring complex business domains. It was invented by Alberto Brandolini. Unlike requirements documents or UML diagrams, EventStorming is designed to surface **domain knowledge** and expose gaps, conflicts, and assumptions through structured conversation.

There are three workshop formats, each with a different scope and purpose.

---

## Workshop Types

| Type | Scope | Duration | Participants | Output |
|------|-------|----------|--------------|--------|
| Big Picture | Entire business domain | 4–8 hours | Broad: business, dev, UX, ops | Subdomains, bounded contexts, hotspots, domain experts identified |
| Process Modeling | One specific business process | 2–4 hours | Process owner, devs, BA | Detailed process flow, policies, actors, read models |
| Design Level | One bounded context / aggregate | 2–4 hours | Dev team + domain expert | Aggregate design, commands, events, policies, UI sketches |

---

## Notation (Sticky Note Colors)

| Color | Symbol | Meaning |
|-------|--------|---------|
| Orange | Domain Event | Something that happened in the domain; past tense verb; the core of EventStorming |
| Blue | Command | An intent or request that causes an event; imperative verb (e.g., "Place Order") |
| Yellow (small) | Actor / Person | Who issues a command; a person or role (e.g., "Customer", "Warehouse Staff") |
| Yellow (large) | Aggregate | A cluster of business objects that processes commands and produces events |
| Purple / Lilac | Policy / Reaction | "Whenever [event], then [command]" — automated reactions and business rules |
| Green | Read Model / View | Information an actor reads before deciding to issue a command |
| Pink | External System | A system outside your domain boundary (payment gateway, email service, ERP) |
| Red | Hotspot | A conflict, question, assumption, disagreement, or area of uncertainty — marked for follow-up |

**Conventions:**
- Events are written in **past tense**: "Order Placed", "Payment Failed", "Invoice Generated"
- Commands are written in **imperative**: "Place Order", "Process Payment", "Generate Invoice"
- Time flows **left to right** on the modeling surface
- The modeling surface should be as large as possible — a long wall with paper roll, or a large virtual canvas (Miro, Mural)

---

## Big Picture EventStorming

### Purpose
Explore the entire business domain to identify subdomains, bounded contexts, key events, and trouble spots. This is the highest-level workshop — depth is sacrificed for breadth.

### Participants
Invite everyone who has domain knowledge AND everyone who needs to understand the domain: business stakeholders, product managers, developers, UX designers, operations staff. Aim for 10–30 people.

### Facilitation Steps

**Step 1: Chaos (20–40 min)**
- Distribute orange sticky notes to every participant.
- Ask everyone to write down domain events — things that matter to the business.
- No order, no discussion, no critique. Dump everything on the wall.
- Prompt: "What are all the things that happen in this business that the business cares about?"

**Step 2: Enforce the timeline (20–30 min)**
- Start arranging events left-to-right in rough chronological order.
- Don't argue about perfect order — approximate is fine.
- Duplicates are OK initially; collapse them when obvious.

**Step 3: Identify Hotspots (ongoing)**
- Place red sticky notes wherever there is confusion, conflict, ambiguity, or disagreement.
- Don't try to resolve hotspots during the session — just mark them.
- Hotspots are gold: they reveal where the domain is poorly understood or contentious.

**Step 4: Add Actors and External Systems (15–20 min)**
- Add yellow (person) stickies to events that are triggered by a specific person or role.
- Add pink stickies for external systems that produce or consume events.

**Step 5: Find Pivotal Events (15 min)**
- Identify events that represent major phase transitions in the process.
- Draw vertical lines to separate phases (e.g., "Order Phase | Fulfillment Phase | Delivery Phase").
- These phase boundaries often correspond to bounded context boundaries.

**Step 6: Identify Bounded Contexts (20–30 min)**
- Look for clusters of events that use a consistent vocabulary and are owned by a consistent group of people.
- Draw boundaries (swimlanes or colored regions) around these clusters.
- Label each boundary with a candidate name for the bounded context.

**Output**: A rough map of the domain showing event flow, candidate bounded contexts, hotspots (risks/questions), and key actors. This is an input to context mapping and subdomain analysis.

---

## Process Modeling EventStorming

### Purpose
Model a specific business process in detail — understand the flow, decision points, policies, actors, and data dependencies.

### Participants
The process owner, subject matter experts for each step, and the developers who will implement it. Keep it focused: 5–12 people.

### Facilitation Steps

**Step 1: Start with events**
- Identify the key domain events in the process (start and end, then fill the middle).

**Step 2: Add Commands**
- For each event, ask: "What command triggered this event?"
- Add blue command stickies before each event.

**Step 3: Add Actors and Policies**
- For each command, ask: "Who issues this command?" → yellow actor sticky.
- For each event, ask: "Does this event automatically trigger another command?" → purple policy sticky.
  - Policy format: "Whenever [Event], [Command]" (e.g., "Whenever Payment Received, Ship Order")

**Step 4: Add Read Models**
- For each command issued by a person, ask: "What information does this person need to decide to issue this command?"
- Add green read model stickies between the read model and the command.

**Step 5: Add External Systems**
- For commands or events that involve external systems, add pink stickies.

**Step 6: Identify Hotspots**
- Mark every question, conflict, and assumption with a red hotspot sticky.

**Output**: A detailed, narrative process model showing commands, events, actors, policies, read models, and external systems. Ready for Design Level EventStorming on specific aggregates.

---

## Design Level EventStorming

### Purpose
Design the implementation of a specific bounded context — identify aggregates, commands, events, and their relationships. This is the closest EventStorming gets to implementation.

### Participants
The development team + the domain expert for this bounded context. 3–8 people.

### Facilitation Steps

**Step 1: Set the context**
- Agree on which bounded context is being designed.
- Establish the starting event (from Process Modeling output).

**Step 2: Commands and Events**
- Lay out the command → event pairs (blue → orange).
- Each pair represents a single state change.

**Step 3: Identify Aggregates**
- Group command-event pairs by the aggregate they operate on.
- Name the aggregate (large yellow sticky).
- Place commands on the left face of the aggregate, events on the right.
- Ask: "Which aggregate receives this command?" and "Which aggregate produces this event?"

**Step 4: Add Policies**
- Add purple policy stickies where events trigger further commands (automated reactions).

**Step 5: Add Read Models and UI**
- Add green read model stickies showing what data an actor needs to issue a command.
- Optionally sketch UI wireframes on white paper stickies.

**Output**: Aggregate design, command/event vocabulary, policy flows. Directly feeds into code: aggregate names, command names, event names become the ubiquitous language in the implementation.

---

## Common Patterns Found During EventStorming

**The Hotspot Cluster**: many red hotspots concentrated in one area indicates a poorly understood subdomain. This is where to invest in domain expert time before writing code.

**The Parallel Timeline**: two independent event streams that occasionally synchronize (e.g., order processing and payment processing). Often signals two separate bounded contexts with integration events at the sync points.

**The Policy Chain**: a long chain of "whenever event X, do command Y" policies. Signals a process that might benefit from a process manager rather than simple choreography.

**The External System Bottleneck**: many events and commands passing through a single external system (pink sticky). Risk: that system becomes a single point of failure or coupling point. Consider ACL.

**The Ambiguous Aggregate**: participants disagree about which aggregate handles a command. This is almost always a sign that the aggregate boundaries need more work, not that one person is wrong.

---

## Translating EventStorming Output to Code

### From Big Picture to Architecture
- Event clusters with consistent vocabulary → candidate bounded contexts
- Phase boundaries (pivotal events) → context map integration points
- Hotspot clusters → where to run deeper Process Modeling workshops

### From Process Modeling to Integration Patterns
- Policy stickies → domain events + consumers (outbox pattern needed)
- Long policy chains → consider saga or process manager
- External system integrations → ACL pattern at those boundaries

### From Design Level to Code
| EventStorming Element | Code Artifact |
|----------------------|---------------|
| Aggregate (large yellow) | Aggregate root class |
| Command (blue) | Command object + handler method on aggregate |
| Domain Event (orange) | Domain event class, raised by aggregate |
| Policy (purple) | Event handler / reaction in application or domain service |
| Read Model (green) | CQRS query model / projection |
| Actor (small yellow) | User role / authorization concern |
| External System (pink) | Anti-Corruption Layer interface |

### Naming Convention
EventStorming naturally produces the ubiquitous language:
- Command: "Place Order" → `PlaceOrder` command class, `place_order()` method
- Event: "Order Placed" → `OrderPlaced` event class
- Aggregate: "Order" → `Order` aggregate root
- Read Model: "Order Summary" → `OrderSummaryView` / `OrderSummaryProjection`

---

## Facilitation Tips

- **Use a physical space when possible** — a long wall beats a digital canvas for high-energy workshops. People move around, cluster, and debate differently in physical space.
- **The facilitator does not solve problems** — the facilitator creates the conditions for the group to surface knowledge. Resist the urge to fill in stickies yourself.
- **Protect the hotspots** — don't let the group get bogged down resolving hotspots during the session. Mark them and move on.
- **"Show, don't tell"** — when a domain expert explains something verbally, hand them a sticky and ask them to put it on the wall.
- **Watch for quiet experts** — the most knowledgeable people are often introverts. Check in with them directly.
- **Time-box each phase** — strict time-boxing keeps energy high and prevents analysis paralysis.
- **End with explicit next steps** — who owns each hotspot? What workshops come next? What goes to the dev team immediately?
