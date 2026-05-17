# Writing Scenarios
## Chapter 5: Main Success Scenario and Extensions

---

## The Main Success Scenario

The main success scenario (also called the happy path or basic course) describes **what happens when everything goes right**. It is:

- A **numbered sequence** of steps
- Written with **no conditions or branches** — pure linear flow
- The simplest, most direct path from trigger to goal achieved
- Typically **3–9 steps** at sea-level (fewer means too simple; more means goal may be too large)

### The Two-Column Mental Model

Every step is either:
- **Actor action** — the primary actor (or another actor) does something
- **System response** — the system does something in response

Steps alternate perspective but each step is one or the other, not both.

```
Main Success Scenario:
  1. Customer selects items and proceeds to checkout.      ← actor
  2. System displays order summary and shipping options.   ← system
  3. Customer selects shipping method.                     ← actor
  4. System calculates and displays total with tax.        ← system
  5. Customer confirms and submits payment details.        ← actor
  6. System processes payment and records order.           ← system
  7. System sends confirmation to customer.                ← system
```

---

## Step-Writing Guidelines

### Write Steps at the Right Level of Abstraction

Each step should represent a **meaningful interaction**, not a micro-action:

| Too Low (UI-bound) | Right Level | Too High (vague) |
|--------------------|-------------|------------------|
| "Customer clicks Add to Cart button" | "Customer adds item to cart" | "Customer shops" |
| "System updates cart_items table" | "System updates cart with new item and recalculates total" | "System handles the request" |
| "User types email into input field" | "Customer enters email address" | "Customer provides info" |

**Rule:** If a step would change if you changed the UI but the business process stayed the same, the step is written at the wrong (too low) level.

### Use Active Voice, Present Tense

- ✓ "Customer selects shipping address"
- ✗ "Shipping address is selected by the customer"
- ✗ "The customer will select the shipping address"

### Name the Subject Explicitly

Never write "selects" — always say who: "Customer selects" or "System displays."

### Show Actor-System Interaction

Steps naturally alternate (actor → system → actor → system) but don't force it. A sequence of system steps is fine ("System validates, records, and notifies"). The key is clarity.

### One Action Per Step

Don't combine two distinct steps into one:
- ✗ "Customer enters address and selects shipping method"
- ✓ Step 2: "Customer enters shipping address"
- ✓ Step 3: "Customer selects shipping method"

Exception: closely coupled actions that always happen together and aren't separately meaningful.

### Avoid Implementation Details

- ✗ "System queries the `orders` table with a SELECT statement"
- ✓ "System retrieves order history for the customer"

- ✗ "System sends a POST request to the payment API"
- ✓ "System submits payment for authorization"

---

## Extensions (Alternate Flows)

Extensions capture **every way the main success scenario can diverge** — due to errors, alternate choices, or exceptional conditions. They are the most important part of use case writing for revealing system complexity.

### Extension Numbering Convention

```
[Step Number][Letter]. [Condition]:
  [Step Letter][Number]. [Response action]
  [Continue instruction]
```

- **Step Number:** the main scenario step where the divergence can occur
- **Letter:** alphabetical for multiple extensions at the same step
- **`*`:** can occur at any step (system-wide conditions)

```
Extensions:
  7a. Payment authorization fails:
    7a1. System informs customer of failure (no specific reason disclosed).
    7a2. Customer selects alternative payment method. Continue at step 5.
    7a3. If customer cancels: use case ends with cart preserved.

  7b. Payment processor is unavailable:
    7b1. System queues payment for retry.
    7b2. System notifies customer of delay and provides order reference.
    7b3. Use case ends; order in Pending Payment status.

  *a. System error or timeout at any step:
    *a1. System logs error.
    *a2. System preserves all entered data.
    *a3. System informs user of error and provides retry option.
```

### Extension Format Rules

**Condition:** State the triggering condition, not the response.
- ✓ "Payment authorization fails:"
- ✗ "System shows error message:" (that's the response, not the condition)

**Condition-Action pairs:**
```
[step-condition]. [Condition]:
  [action]. [What system/actor does]
  [action]. [Next action or continuation]
```

**Ending an extension:** Use one of:
- `Continue at step N.` — resume main scenario at a specific step
- `Use case ends.` — use case terminates (goal not achieved)
- `Use case ends successfully.` — alternate path still achieves the goal
- `Resume main scenario.` — return to the next step in sequence

### Types of Extensions to Write

| Type | Example |
|------|---------|
| **Validation failure** | "2a. Address format is invalid" |
| **Resource not available** | "8a. Item is out of stock" |
| **Authorization failure** | "7a. Payment is declined" |
| **Actor cancels** | "3a. Customer cancels the order" |
| **Timeout/system unavailability** | "*a. System is unavailable" |
| **Alternate actor choice** | "2a. Customer enters new address (vs. using saved)" |
| **Business rule violation** | "6a. Order total exceeds customer's credit limit" |
| **External system failure** | "7b. Payment processor times out" |

### Finding Extensions: The "What Can Go Wrong?" Exercise

At each main scenario step, ask:
1. **What could fail?** (validation, authorization, resource unavailability)
2. **What might the actor choose differently?** (alternate paths, cancellation)
3. **What external event could interrupt?** (timeout, external system failure)
4. **What business rule might not be satisfied?** (limits, restrictions, policies)

### Which Extensions to Include?

Not every possible failure needs documentation. Include extensions that:
- **Happen frequently enough to design for**
- **Require a non-obvious system response**
- **Have significant consequence if unhandled**
- **Represent a business rule or policy decision**

Omit extensions that:
- Are handled generically by middleware (generic 500 errors)
- Are so rare they're irrelevant to design
- Add no information beyond "retry"

### Extension Complexity

Extensions can themselves have extensions (nested alternate flows). Use sparingly; deeply nested extensions usually signal the use case is too complex and should be split.

---

## Writing Both Together: Checklist

After drafting the main success scenario and extensions:

- [ ] Main scenario has no conditions or branches
- [ ] Every step has an explicit subject (actor or system name)
- [ ] Steps are at the right abstraction level (not UI-bound, not vague)
- [ ] Each step advances toward the postcondition
- [ ] Extensions cover the most important failure modes
- [ ] Every extension ends with a clear continuation or termination
- [ ] All stakeholder interests in the postcondition are achievable from the main scenario
- [ ] The scenario can be walked through by a domain expert without software knowledge
