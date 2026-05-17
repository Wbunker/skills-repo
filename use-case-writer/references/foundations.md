# Use Case Foundations
## Chapters 1–2: What Is a Use Case, Actors, Goals, System Boundary

---

## What Is a Use Case?

A use case captures **a contract between the stakeholders of a system about its behavior** in response to a goal triggered by one of its actors.

Cockburn's concise definition: *"A use case captures a set of instances of a system's behavior; each instance is a sequence of actions taken by actors and the system to achieve a goal of value to a primary actor."*

Three essential properties:
1. **Triggered by an actor pursuing a goal** — something must start it
2. **Delivers value to a stakeholder** — someone benefits from completion
3. **Leaves the system in a stable state** — postcondition holds after success or failure

### What a Use Case Is NOT

| Not a use case | Why |
|----------------|-----|
| A screen or UI flow | Use cases are implementation-independent |
| A data model | Use cases capture behavior, not structure |
| A functional specification | Use cases are goal-driven, not feature-driven |
| A test case | They may inform tests but aren't test scripts |
| A process map (all flows on one diagram) | Each use case focuses on one goal |

---

## The System Boundary

The **system boundary** (also called scope) separates what the system does from what actors do. Everything inside is the system's responsibility; everything outside is an actor.

### Choosing the Right Scope

Scope should match the system you are designing:
- **Enterprise scope** — spans multiple applications, departments
- **Application scope** — one deployable system
- **Component scope** — a subsystem or service

The scope affects which use cases appear. "Place Order" is a use case for an e-commerce application; for an enterprise system it might be a sub-function of "Fulfill Customer Request."

### Drawing the Boundary

Ask: *"Who/what will we build? Who/what will we connect to?"*
- Build: inside the boundary
- Connect to: outside (actors)

Ambiguous elements (e.g., a shared database) should be placed inside the boundary if your team designs and operates it.

---

## Actors

An **actor** is anyone or anything that has behavior — a person, organization, or external system that interacts with the system under discussion.

### Three Categories of Actors

| Type | Definition | Example |
|------|-----------|---------|
| **Primary actor** | Initiates the use case to achieve a goal; the system serves this actor | Customer placing an order |
| **Supporting actor** | Provides services to the system during the use case | Payment gateway, tax service |
| **Offstage stakeholder** | Has interests in the use case outcome but doesn't participate directly | Tax authority, auditor, regulatory body |

### Key Distinctions

**Primary vs. supporting**: Ask *"Who wants this goal?"* — that actor is primary. The actor the system calls to get help is supporting.

**Persons vs. roles**: Use cases are written to roles (Customer, Administrator, Clerk), not named individuals. A person may play multiple roles.

**Human vs. system actors**: External systems can be actors. A billing system that triggers "Charge Account" at month-end is an actor.

### Finding Actors

Ask:
- Who uses the system directly?
- Who provides inputs or receives outputs?
- Who administers the system?
- What external systems integrate with this one?
- Who benefits from the system's outputs (even if they don't interact directly)?
- Who needs the system to work in a specific regulatory or compliance way?

---

## Goals

A **goal** is what the primary actor wants to achieve — a desire to reach a certain state or get something done. Goals are the most important concept in use case writing.

### Goal Properties

- **Goal of the primary actor**, not the system — "Place Order," not "Accept Order"
- **Named as a verb phrase** — action + object: "Renew Subscription," "Generate Report"
- **At the right level of abstraction** — not too big, not too small (see goal-levels.md)
- **Delivers a measurable outcome** — the actor can tell when it's done

### Stakeholder Interests

Every use case satisfies the primary actor's goal AND protects the interests of other stakeholders:

- A customer placing an order wants to get the goods.
- The company wants payment.
- The tax authority wants applicable taxes collected.
- The warehouse wants a pick list.

Listing stakeholder interests early prevents use cases that satisfy the primary actor while ignoring everyone else. Extensions and postconditions often exist to protect offstage stakeholders.

---

## Why Use Cases?

Use cases are valuable because they:
1. **Focus on user goals**, not system features — avoids building things nobody needs
2. **Expose stakeholder conflicts** — multiple interests made explicit
3. **Are implementation-independent** — survive technology changes
4. **Scale from sketch to specification** — same format from napkin to contract
5. **Generate test cases** — each scenario is a test scenario

### Use Cases vs. User Stories

| Dimension | User Story | Use Case |
|-----------|------------|----------|
| Size | Small (one sprint) | Any size |
| Extensions | Not standard | Built in |
| Stakeholders | Usually primary only | All stakeholders explicit |
| Detail | Low by default | Scalable |
| Best for | Agile backlog management | Complex interactions, safety-critical |

Use cases and user stories complement each other: user stories surface scope; use cases specify behavior. A use case may spawn many user stories.
