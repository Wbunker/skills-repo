# Finding Use Cases and Reviewing for Completeness
## Chapters 8–9: Discovery, Actor-Goal Lists, Completeness Heuristics, Review

---

## Finding Use Cases

Use cases are discovered, not invented. The process is iterative: identify actors, enumerate their goals, verify scope, and promote to use cases.

### Step 1: Define System Scope

Before finding use cases, establish the boundary:
- What is the system being designed? (name it — the scope field)
- What will we build vs. what will we integrate with?
- What is the business objective this system serves?

### Step 2: Identify Actors

Ask these questions about the system:
- **Who uses the system directly?** (human users in different roles)
- **Who provides data or receives output?** (may not interact via UI)
- **What external systems connect to this one?** (APIs, integrations)
- **Who administers, configures, or maintains the system?**
- **Who benefits from the system's outputs even without direct interaction?** (offstage stakeholders)
- **Who has regulatory, legal, or compliance interest?**

Produce an **actor list** with a one-line description of each actor's relationship to the system.

### Step 3: For Each Actor, List Their Goals

For each actor, ask:
- *"Why does this actor use the system? What do they want to achieve?"*
- *"What tasks does this actor need the system to help with?"*

Write each goal as a verb phrase (the use case title). Apply the boss test and EBP test to size each goal correctly (see goal-levels.md).

The result is an **actor-goal list**:

```
Actor: Customer
  ≋ Place Order
  ≋ Track Shipment
  ≋ Return Item
  ≋ Update Account Details
  ≋ Cancel Order

Actor: Warehouse Clerk
  ≋ Pick and Pack Order
  ≋ Process Return
  ≋ Report Inventory Discrepancy

Actor: Administrator
  ≋ Manage User Accounts
  ≋ Configure Shipping Rates
  ≋ View Sales Reports

Actor: Payment Processor (external system)
  ≋ [supports] Authorize Payment  (offstage — triggered by our system)
```

### Step 4: Apply the EBP Test to Each Goal

Review each goal in the actor-goal list:
- Too big → decompose into multiple sea-level goals
- Too small → fold into a step in a larger use case or note as sub-function
- Just right → this is a use case

### Step 5: Scope Verification

For each use case in the list, confirm:
- Is this system's responsibility? (inside the boundary)
- Does this serve a real actor's real goal?
- Is this worth building? (delivers business value)

Remove duplicates, merge overlapping cases, split over-sized cases.

---

## The Actor-Goal List as a Deliverable

The actor-goal list is a **lightweight, high-value deliverable** for scope discussions:

```
SYSTEM: Online Retail Platform

Sea-level Use Cases (target for specification):
  Customer:
    UC-01 Place Order
    UC-02 Track Shipment
    UC-03 Request Return
    UC-04 Manage Wishlist
    UC-05 Update Account

  Product Manager:
    UC-10 Add Product
    UC-11 Update Product Listing
    UC-12 Set Promotional Pricing

  Fulfillment Staff:
    UC-20 Process Pick List
    UC-21 Record Shipment
    UC-22 Process Return Receipt

Summary Use Cases (for context):
    UC-S1 Manage Customer Account  (contains UC-01, UC-03, UC-05)
    UC-S2 Fulfill Order            (contains UC-20, UC-21)

Out of scope:
    Accounting integration (separate system)
    Supplier portal (Phase 2)
```

This list is shareable with stakeholders for scope agreement **before** writing any detailed use cases.

---

## Completeness Heuristics

After drafting use cases, use these checks to find gaps.

### 1. Stakeholder Coverage Check

For every stakeholder listed in the system's scope:
- Is there at least one use case that serves their primary goal?
- Is there at least one use case that protects their interests (even if they're offstage)?

**Common gaps:** Regulators, auditors, and offstage stakeholders often have no use case serving their needs, even though their interests constrain system behavior.

### 2. CRUD Check

For every significant business entity in the domain, verify there are use cases covering:
- **Create** — how is this entity created?
- **Read/Retrieve** — how is this entity found and viewed?
- **Update** — how is this entity modified?
- **Delete/Archive** — how is this entity removed or closed?

**Caution:** This is a gap-finding heuristic, not a mandate. Not every entity needs all four. Use it to find missing use cases, not to generate unnecessary ones.

### 3. The Precondition Establishment Check

For every precondition in every use case, ask: *"Is there a use case that establishes this precondition?"*

```
UC-01 Place Order
  Precondition: Customer is authenticated

→ Is there a use case "Log In" or "Authenticate Customer"? 
  If yes, is it documented? If no, who handles it?
```

Unestablished preconditions reveal missing use cases or incorrect scoping.

### 4. The Extension Completion Check

For every extension in every use case, ask:
- Does the extension end with a clear continuation or termination?
- If it terminates, is the postcondition for that failure case defined?
- Are there gaps — things that could go wrong that have no extension?

### 5. Business Event Coverage

Ask: *"What business events (triggers) does this system respond to?"* Then verify each event has a use case.

Business events include:
- Time-triggered events ("month-end," "subscription renewal date")
- External actor requests ("customer places order")
- State change events ("inventory falls below reorder threshold")
- System-to-system calls ("payment processor posts settlement")

Every significant business event should have a corresponding sea-level use case.

---

## The Use Case Review Checklist

For each use case under review:

**Goal and Scope:**
- [ ] Title is a verb phrase from the primary actor's perspective
- [ ] Goal level is sea-level (passes EBP test and boss test)
- [ ] Scope (system boundary) is clearly stated
- [ ] Primary actor is named by role, not by name

**Stakeholders:**
- [ ] All interested parties are listed as stakeholders
- [ ] Each stakeholder's interest is stated
- [ ] Postconditions satisfy all listed stakeholder interests

**Structure:**
- [ ] Preconditions are things guaranteed before the use case starts (not checked inside)
- [ ] Postconditions state what is true after success
- [ ] Main success scenario has no conditions or branches
- [ ] Each step has an explicit subject (actor or system name)
- [ ] Steps are at the right abstraction level (not UI-bound, not vague)

**Extensions:**
- [ ] Extensions cover the most important failure modes
- [ ] Each extension starts with a condition, not a response
- [ ] Each extension ends with a continuation or termination
- [ ] Extension numbering is correct (step number + letter)

**Quality:**
- [ ] Steps can be walked through by a domain expert without software knowledge
- [ ] The use case makes no implementation decisions (no DB queries, no API calls)
- [ ] A domain expert agrees this is what the business does

---

## Common Discovery Anti-Patterns

| Anti-Pattern | Description | Fix |
|-------------|-------------|-----|
| **Feature decomposition** | Listing features, not goals | Ask "who wants this?" and reframe as actor goals |
| **Screen-driven use cases** | One use case per screen | Ask "what goal does this screen serve?" |
| **CRUD factory** | Generating Create/Read/Update/Delete for every table | Ask which CRUD operations represent real business events |
| **Missing offstage actors** | Forgetting regulators, auditors, system operators | Use stakeholder workshop to surface hidden interests |
| **Premature detail** | Writing fully dressed use cases before scope is agreed | Start with actor-goal list; promote incrementally |
| **Scope creep in use cases** | Adding steps that belong in a different use case | Each use case should achieve exactly one actor goal |
