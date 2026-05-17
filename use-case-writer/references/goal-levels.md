# Goal Levels
## Chapter 3: Goal Altitude, EBP Test, Boss Test

---

## The Goal Altitude Metaphor

Cockburn uses altitude (and weather metaphors) to describe how abstract or concrete a goal is. Choosing the wrong altitude is the most common use case mistake.

```
Altitude    Symbol    Name              Description
─────────   ──────    ──────────────    ─────────────────────────────────────────
Very High     ☁        Cloud             Strategic goals: "Run a profitable business"
High          ✈        Kite/Summary      Spans multiple sessions: "Become a customer"
─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ TARGET ZONE ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
Normal        ≋        Sea-level         One EBP: "Place Order", "Register Patient"
─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
Low           ✦        Fish/Sub-function Steps inside a use case: "Enter address"
Very Low      🦐        Clam/Sub-function UI interactions: "Click OK", "Select item"
```

**Sea-level is the target** for primary use cases. Higher-level use cases (summaries) provide context and overview. Sub-function use cases are implementation details, rarely documented as standalone use cases.

---

## The Elementary Business Process (EBP) Test

An **Elementary Business Process** is the fundamental unit of meaningful work at the sea-level. The EBP test determines if a goal is at the right altitude.

**The EBP Test:**
> *Can one person, at one place and time, in response to a single business event, complete this process — leaving the business in a stable, consistent state and delivering measurable value?*

Apply all five criteria:

| Criterion | Check |
|-----------|-------|
| **One person** | Not a team or department; one role performs it |
| **One place** | Not distributed across locations simultaneously |
| **One time** | Completes in one sitting, one session |
| **Business event trigger** | A real event initiates it (order received, patient arrives, deadline triggered) |
| **Stable state** | Business is left consistent after; nothing is half-done |

### EBP Examples

| Goal | EBP? | Why |
|------|------|-----|
| "Place Order" | ✓ Yes | Customer, one session, order event, stable after |
| "Fulfill Order" (pick/pack/ship over 2 days) | ✗ No | Spans multiple times/people → raise to Summary |
| "Enter Shipping Address" | ✗ No | Too small, a step within Place Order → Sub-function |
| "Become a Customer" (register + first purchase) | ✗ No | Spans multiple sessions → Summary/Kite |
| "Check Inventory" | ✗ Maybe | If standalone business value: yes; if always part of Place Order: sub-function |

---

## The Boss Test

A simpler, complementary test for naming and sizing use cases at sea-level.

**The Boss Test:**
> *If the primary actor's boss asked "What were you doing all day?" and the actor replied with this use case title, would the boss be satisfied?*

| Title | Boss Test Result |
|-------|-----------------|
| "Place Order" | ✓ Satisfied — real work done |
| "Log In" | ✗ Unsatisfied — that's not a job; it's a step |
| "Click Submit" | ✗ Unsatisfied — too small |
| "Run the Business" | ✗ Unsatisfied — too vague/large |
| "Process Monthly Payroll" | ✓ Satisfied — meaningful unit of work |

The boss test catches sub-functions masquerading as use cases (Login, Select Product) and pure infrastructure steps.

---

## Summary-Level Use Cases

Summary use cases are **above sea-level**. They show how multiple sea-level use cases fit together for a larger goal. Use them for:

- **Overview documentation** — showing scope and relationships at a glance
- **Long workflows** — "Onboard New Employee" spans many days and sea-level cases
- **Business context** — showing how the system serves strategic goals

Summary use cases in the template have `level: Summary` (or ✈ / ☁). They typically reference included sea-level cases rather than detailing every step.

**Example:**

```
Summary: Manage Customer Account
  ≋ Create Account
  ≋ Update Account Details
  ≋ Suspend Account
  ≋ Close Account
```

---

## Sub-function Use Cases

Sub-functions live below sea-level. They represent **reusable steps** extracted from multiple sea-level use cases to avoid repetition.

**Write a sub-function use case only when:**
- The same step sequence appears in 3+ sea-level use cases
- The behavior is genuinely complex enough to deserve its own document
- You want to highlight a reusable building block (authentication, logging, auditing)

**Do not write sub-function use cases for:**
- Simple single steps ("Click OK")
- Steps that only appear once
- Steps included just because a developer factored them out of code

---

## Choosing the Right Level: Decision Guide

```
Start with the primary actor's goal as stated.

Is this goal too big?
→ Signs: spans multiple sessions, needs multiple people, 
         takes days/weeks, actor can't do it in one sitting
→ Action: Decompose into 2–5 sea-level use cases; 
          document the original as a Summary

Is this goal too small?
→ Signs: fails boss test ("I just logged in all day?"),
         is a step inside a larger goal,
         delivers no business value on its own
→ Action: Make it an extension step or sub-function reference
          inside the parent sea-level use case

Is this goal at sea-level?
→ Check: Passes EBP test + Boss test
→ Document as a primary use case with full structure
```

---

## Common Altitude Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Logging in as a use case | Fails boss test; it's always a precondition or sub-function | Remove or fold into precondition |
| "Manage X" as a single use case | Too large; "manage" hides 4–6 EBPs | Split into Create X, Update X, Delete X, etc. |
| UI interactions as use cases | "Select from dropdown", "Enter email" — clam level | Make them steps inside a use case |
| Business process as single use case | Spans weeks, multiple departments | Promote to Summary; find the EBPs inside |
| CRUD blindness | Writing one use case per table, not per business goal | Ask what business event triggers each |
