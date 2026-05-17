# Use Case Formats
## Chapter 7: Fully Dressed, Casual, Brief, One-Line

---

## The Four Formats

Cockburn defines four formats that differ in how much structure and detail they contain. All are legitimate; the right choice depends on the use case's risk, complexity, and maturity.

| Format | Structure | When to Use |
|--------|-----------|-------------|
| **One-line** | Title only | Discovery and scoping; early lists |
| **Brief** | 1–2 paragraph summary | Low-risk use cases; backlog items |
| **Casual** | Informal paragraphs with actor/system flow | Understood, moderate-complexity cases |
| **Fully Dressed** | Complete template with all fields | High-risk, complex, or architectural cases |

---

## One-Line Format

Just the use case title. Used for:
- **Actor-goal lists** during initial discovery
- **Scope discussions** — what's in vs. what's out
- **Index/table of use cases** for a system

```
UC-01 Place Order
UC-02 Track Shipment
UC-03 Return Item
UC-04 Manage Product Catalog
UC-05 Process Refund
```

No narrative, no steps. The list is the artifact.

**One-line use cases are not "incomplete"** — for the discovery phase, they are exactly right. Do not flesh them out before you understand the system.

---

## Brief Format

A short (1–2 paragraph) prose summary of the use case: what happens in the main success scenario and the most important failure cases.

```
UC-01 Place Order (Brief)

The customer selects items, enters shipping and payment details,
and submits the order. The system validates payment, reserves
inventory, records the order, and sends a confirmation.

Main failures: payment declined (customer retries or cancels);
item out of stock (customer adjusts cart or cancels).
```

**Use Brief when:**
- The use case is low-risk and well-understood
- You need a backlog item with enough detail to estimate and discuss
- The team will work out the details during implementation
- You don't need a formal specification or contract

Brief format maps naturally to a user story + a few acceptance criteria.

---

## Casual Format

A use case written in informal prose, organized by actor and system turns, without the full template structure. More detail than Brief, less overhead than Fully Dressed.

```
UC-01 Place Order (Casual)

Primary Actor: Customer
Goal: Customer completes purchase of selected items

The customer reviews their cart and proceeds to checkout.
The system displays shipping options and estimated delivery dates.
The customer selects a shipping method and enters payment details.
The system validates the payment and reserves the inventory.
The customer confirms the order; the system records it and sends confirmation.

If payment fails: system tells the customer without disclosing the reason;
customer can retry with a different method or cancel.

If an item goes out of stock during checkout: system informs customer;
customer can remove the item or cancel.
```

**Use Casual when:**
- The use case is moderately complex
- The team understands the domain and doesn't need every field spelled out
- You want to communicate behavior without the overhead of the full template
- You're writing for developers who will ask questions as they go

---

## Fully Dressed Format

The complete template with all fields. See structure-template.md for the full field reference and annotated example.

**Use Fully Dressed when:**
- The use case drives significant architectural decisions
- The use case is high-risk (financial, medical, legal, safety-critical)
- Multiple teams or contractors must implement from the specification
- You need a contractual basis for what the system must do
- The domain is complex and stakeholder interests are non-obvious
- You are writing for a client who will sign off on requirements

Fully Dressed is **not the default** — it's the format for cases where the overhead is justified by the risk or complexity.

---

## Conversation-Style Use Cases

Cockburn also describes a more conversational format for discovery sessions: **each step is an actor-system dialogue pair**.

```
Conversation-style:

CUSTOMER: I want to place an order for these items.
SYSTEM: Here are your items, shipping options, and total.
CUSTOMER: I'll take standard shipping and pay by credit card [provides details].
SYSTEM: Payment authorized. Order #12345 confirmed. Confirmation sent.
```

This format is useful for:
- **Walkthroughs with domain experts** who aren't comfortable with formal notation
- **Workshop facilitation** to discover steps collaboratively
- **Early drafts** before converting to numbered steps

Convert conversation-style to numbered steps once the flow is validated.

---

## Index Cards

For physical workshops, Cockburn recommends writing use cases on index cards (3×5 or 5×8):

```
┌─────────────────────────────────┐
│ UC-01 Place Order               │
│ Actor: Customer                 │
│                                 │
│ 1. Customer selects items       │
│ 2. Enters shipping + payment    │
│ 3. System validates + records   │
│ 4. System sends confirmation    │
│                                 │
│ Alt: Payment fails → retry      │
│ Alt: Out of stock → adjust cart │
└─────────────────────────────────┘
```

Index cards work well for:
- CRC-style discovery workshops
- Prioritization exercises (physically move cards)
- Early scope definition sessions
- Collocated teams

---

## Format Selection Heuristics

```
How well do you understand this use case?
├── Not yet — just discovered it → One-line
├── Roughly understood → Brief or Casual
└── Fully understood → Casual or Fully Dressed

How high is the risk if this is wrong?
├── Low (supporting feature, low traffic, easily changed) → Brief or Casual
└── High (financial, medical, legal, contract, architecture) → Fully Dressed

Who is the audience?
├── Developers on the same team → Casual
├── Multiple teams / contractors → Fully Dressed
├── Domain experts in a workshop → Conversation-style or Casual
└── Executives / product review → Brief

How stable is the scope?
├── Actively changing, early discovery → One-line or Brief
├── Stable enough to implement → Casual or Fully Dressed
```

---

## Common Mistakes with Formats

| Mistake | Problem | Fix |
|---------|---------|-----|
| Writing every use case fully dressed | Waste of time; most cases don't need it | Reserve fully dressed for high-risk cases |
| Never writing anything beyond one-line | No specification exists; developers guess | Promote important cases to at least casual |
| Mixing formats inconsistently | Stakeholders don't know what's specified | Agree on format per use case, track it |
| Writing casual and calling it fully dressed | Missing fields creates false confidence | Use the template; fill all fields or acknowledge gaps |
| Starting fully dressed before understanding the domain | Template traps you into premature detail | Start one-line; promote as understanding grows |
