# Use Case Relationships
## Chapter 6: Include, Extend, and Generalization

---

## Overview

Use case relationships allow you to model **shared behavior** (include), **optional behavior** (extend), and **specialization** (generalization) between use cases and actors. They are represented on use case diagrams with stereotyped arrows.

```
Use Case A ──────«include»──────► Use Case B
                                  (B always runs when A runs)

Use Case C ◄─────«extend»──────  Use Case D
                                  (D optionally extends C under a condition)

Use Case E ◄──────△───────────── Use Case F
                                  (F is a specialization of E)
```

**Caution:** Overusing relationships (especially `«extend»`) is a common mistake that makes diagrams unreadable and use cases hard to understand. Use them sparingly and only when they genuinely clarify the design.

---

## Include «include»

### What It Means

Use case A **includes** use case B when A always calls B as part of its execution — B's behavior is a **mandatory, factored-out piece** of A's behavior.

```
Place Order ──«include»──► Authorize Payment
Renew Subscription ──«include»──► Authorize Payment
Change Payment Method ──«include»──► Authorize Payment
```

**Include = mandatory delegation.** Every instance of A will execute B.

### When to Use Include

Use `«include»` when:
1. **The same sub-sequence appears in 3+ use cases** and you want a single place to specify it
2. **The sub-sequence is complex enough** to deserve its own document
3. **Different teams own** the included behavior (e.g., security team owns authentication)

Do NOT use `«include»` just because a developer factored the code into a function. Use cases describe business behavior, not code structure.

### How to Reference in the Use Case Text

In the main success scenario, reference the included use case explicitly:

```
Main Success Scenario:
  ...
  5. System performs UC-07 Authorize Payment.
  6. System records order.
  ...
```

The included use case (UC-07) is written as its own standalone fully-dressed use case.

### The Included Use Case is a Sub-function

Included use cases are typically at the **sub-function level** (✦) — they exist to serve a higher-level goal, not as standalone EBPs.

---

## Extend «extend»

### What It Means

Use case D **extends** use case C when D represents **optional, conditional behavior** that augments C under specific circumstances.

```
Place Order ◄──«extend»── Apply Coupon Code
Place Order ◄──«extend»── Apply Loyalty Points
Checkout ◄──«extend»── Request Gift Wrapping
```

**Extend = optional insertion.** D inserts its behavior into C at defined extension points, but only when the extension condition is met.

### When to Use Extend — and When NOT To

Use `«extend»` only when:
1. The extending behavior is **genuinely optional** (C succeeds without it)
2. The extended use case (C) **should not know about** D — C is stable, D adds variation
3. The extension is a **separately specifiable feature** (different team, separate delivery, optional module)

**Prefer extensions (alternate flows)** inside the use case text over `«extend»` relationships in most cases. The `«extend»` relationship is for:
- **Plug-in modules** that add to a stable base
- **Variations delivered by different teams** at different times
- **Features that the base use case explicitly shouldn't know about**

Do NOT use `«extend»` to show:
- Alternate flows (use extensions in the use case text instead)
- Error handling (also use extensions in the use case text)
- Every optional step (over-modeling)

### Extension Points

The extended use case (C) may declare **extension points** — named locations in its scenario where extensions can insert themselves:

```
USE CASE: Place Order
Extension Points:
  pricing: after step 4 (total calculated)
  payment: after step 5 (payment method selected)
```

The extending use case (D) specifies which extension point it targets.

---

## Generalization

### For Use Cases

Use case generalization means use case F is a **specialization** of abstract use case E. F inherits all of E's behavior and overrides or extends parts of it.

```
        Authenticate User  (abstract)
              △
      ┌───────┴──────────┐
  Login with        Login with
  Password          Biometrics
```

Use case generalization is **rare and often misapplied**. Use it only when:
- The parent use case is genuinely abstract (never instantiated directly)
- Multiple specializations share most behavior but differ in specific steps
- The variation is a business-level variation, not a technical implementation detail

Most perceived needs for use case generalization are better handled with technology/data variation lists in the template.

### For Actors

Actor generalization is more common and useful:

```
      User (abstract)
         △
    ┌────┴────────────┐
  Customer        Administrator
```

Actor generalization shows that Customer and Administrator share common interactions with the system (anything User can do), but each has additional, distinct interactions. Use cases written for User apply to both.

**Example:**
- "View Account Details" has primary actor: User
- "Place Order" has primary actor: Customer
- "Manage User Accounts" has primary actor: Administrator

Both Customer and Administrator inherit use cases from User.

---

## Choosing the Right Relationship

```
Do multiple use cases share a mandatory common sub-sequence?
├── Yes, and it's complex/reusable → «include»
└── No → don't force it; keep steps inline

Is a behavior optional/conditional in one use case?
├── Frequently co-occurring, same team → extension (alternate flow) in text
├── Optional plug-in, separate team, or separate delivery → «extend»
└── Error handling → always extension in text, never «extend»

Is a use case a variant of another?
├── Same steps, different data/technology → variation list in template
├── Genuinely different behavior sharing a common abstraction → generalization
└── Just looks similar → separate use cases, no relationship needed
```

---

## Diagram Usage

Use case diagrams (UML) show:
- System boundary (rectangle)
- Actors (stick figures) outside the boundary
- Use cases (ellipses) inside the boundary
- Associations (lines) between actors and use cases
- Relationships («include», «extend», generalization) between use cases

**Use diagrams for:**
- Overview and scope communication
- Showing actor access to use cases
- Summarizing a complex system at a glance

**Don't use diagrams to:**
- Replace use case text — the diagram is a summary, not a specification
- Document every «extend» and «include» — too much noise
- Show flow or sequence — use sequence diagrams for that

**Rule of thumb:** A use case diagram with more than 15–20 use cases is trying to say too much. Consider subsystem diagrams or just list use cases textually.
