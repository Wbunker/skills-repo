# Use Case Structure and Template
## Chapter 4: The Fully Dressed Template — All Fields Explained

---

## The Fully Dressed Template

The fully dressed format is Cockburn's most complete use case specification. Use it for complex, high-risk, or architecturally significant use cases.

```
USE CASE: [UC-##] [Verb Phrase — Actor's Goal]

Scope:           [Name of system under design]
Level:           [Summary | User Goal (Sea-level) | Sub-function]
Primary Actor:   [Who initiates this use case]

Stakeholders and Interests:
  - [Actor/Stakeholder]: [What they want from this use case]
  - [Actor/Stakeholder]: [What they want from this use case]

Preconditions:   [What must be true BEFORE this use case begins]
Postconditions:  [What is guaranteed TRUE after successful completion]
                 (also called "Success Guarantee")

Main Success Scenario:
  1. [Step — actor or system action]
  2. [Step]
  3. ...

Extensions:
  [step#][condition-letter]. [Condition that diverges]:
    [step-letter]a. [Response]
    [step-letter]b. [Continue or end]

Special Requirements:
  [Non-functional requirements specific to this use case]

Technology & Data Variations:
  [Known variations in technology, data formats, or actor types]

Frequency:       [How often this use case is triggered]
Open Issues:     [Decisions not yet made; things to resolve]
```

---

## Field-by-Field Reference

### Title

**Format:** `[UC-##] [Verb] [Object]`

- Verb + noun phrase from the **primary actor's perspective**
- Present tense, active voice
- No articles ("the", "a") unless essential
- Avoid UI references ("Click the Order button")

| Good | Bad |
|------|-----|
| Place Order | Order Management |
| Register Patient | Patient Registration Screen |
| Transfer Funds | Handle Money Movement |
| Generate Monthly Report | Reports |

### Scope

Names the system being designed. Sets the boundary. Everything "inside" the scope boundary is what the system does; everything outside is an actor.

Examples:
- "Online Retail System"
- "Hospital Patient Management System"
- "Payment Processing Service"

### Level

- **Summary (☁/✈):** Multiple EBPs, spans sessions — used for overview
- **User Goal / Sea-level (≋):** One EBP — primary target for most use cases
- **Sub-function (✦):** Below sea-level — factored reusable step

### Primary Actor

The actor who **initiates** the use case and **whose goal is being served**. One role only. If multiple roles can trigger the same use case for the same goal, list them all as primary actor.

"Customer or Guest" is acceptable if both trigger identical behavior.

### Stakeholders and Interests

List **every party with an interest** in the use case's behavior — even if they don't interact directly.

Format:  `Actor: want / protection / interest`

```
Stakeholders and Interests:
  - Customer: wants goods delivered correctly and quickly
  - Company: wants payment; wants fraud prevented
  - Warehouse: wants accurate pick list
  - Tax Authority: wants applicable taxes collected and reported
  - Credit Card Company: wants fraud prevention; wants proper authorization
```

**Why this matters:** Extensions and postconditions protecting offstage stakeholders would be missed if you only think about the primary actor. The tax authority interest reminds you to add tax calculation steps. The warehouse interest reminds you to generate a pick list.

### Preconditions

What the system (and its users) **guarantee is true** before the use case begins. The system does NOT check these at runtime — they are assumed. If the system must check a condition before proceeding, it goes in an extension, not preconditions.

```
Preconditions:
  - Customer is logged in and authenticated
  - At least one item is in the shopping cart
  - Cart totals are calculated and current
```

**Wrong:** "Customer has a credit card" (must be verified during the use case → extension)
**Right:** "Customer account exists and is active" (established before this use case starts)

### Postconditions (Success Guarantee)

What the system **guarantees is true after** the main success scenario completes. Must satisfy all stakeholder interests listed above.

```
Postconditions:
  - Order is recorded in the system with a unique order ID
  - Customer receives confirmation with order details
  - Inventory is reserved/decremented for each ordered item
  - Payment is authorized and pending capture
  - Pick list is queued for warehouse
  - Tax is calculated and will be remitted
```

One postcondition per stakeholder interest is a good cross-check.

### Main Success Scenario

The **happy path** — the simplest, most direct sequence of steps that achieves the goal when everything goes right. No conditions, no branches in the main scenario.

(See scenarios.md for step-writing guidelines.)

### Extensions

Alternate flows: what happens when something differs from the main success scenario. Numbered by the step where the divergence occurs.

(See scenarios.md for extension format and writing rules.)

### Special Requirements

Non-functional requirements specific to this use case:
- Performance ("must complete within 3 seconds for 95th percentile")
- Security ("payment data must not be logged")
- Accessibility ("must support screen readers")
- Legal/regulatory ("audit trail must be immutable")

### Technology and Data Variations

Known variations in how actors or systems interact:
- "Step 3: Customer may pay by credit card, PayPal, or gift card"
- "Step 5: Confirmation sent by email or SMS based on customer preference"
- "Actor may be human customer or automated purchasing system"

### Frequency

How often triggered:
- "Thousands of times per day, peak holiday traffic"
- "Once per patient registration, typically once per patient lifetime"
- "Monthly, on the last business day"

Drives performance, caching, and scaling decisions.

### Open Issues

Questions to resolve before the use case is final:
- "Do we support partial orders if some items are out of stock?"
- "Who approves orders over $10,000?"
- "What happens to a pending order if the customer account is suspended?"

---

## Annotated Example: Place Order

```
USE CASE: UC-01 Place Order

Scope:           Online Retail System
Level:           User Goal (Sea-level)
Primary Actor:   Customer

Stakeholders and Interests:
  - Customer: wants to purchase items and receive them reliably
  - Company: wants payment and accurate inventory management
  - Warehouse: wants accurate pick list with correct items and quantities
  - Payment Processor: wants proper authorization request; fraud protection
  - Tax Authority: wants applicable taxes computed and earmarked

Preconditions:
  - Customer is authenticated
  - Shopping cart contains at least one in-stock item

Postconditions:
  - Order is stored with unique ID; status = Pending Fulfillment
  - Customer receives order confirmation with expected delivery date
  - Inventory is reserved for all ordered items
  - Payment is authorized (not yet captured)
  - Tax is calculated and associated with the order
  - Pick list is queued for warehouse processing

Main Success Scenario:
  1. Customer reviews cart contents and totals.
  2. Customer selects shipping address (from saved addresses or enters new).
  3. Customer selects shipping method and views estimated delivery date.
  4. System displays order total including shipping and tax.
  5. Customer selects payment method and enters/confirms payment details.
  6. Customer confirms order submission.
  7. System validates payment authorization with payment processor.
  8. System reserves inventory for all items.
  9. System records order with status Pending Fulfillment.
  10. System sends order confirmation to customer.
  11. System queues pick list for warehouse.

Extensions:
  2a. Customer enters a new shipping address:
    2a1. System validates address format.
    2a2. Customer confirms or corrects address. Continue at step 3.

  7a. Payment authorization fails:
    7a1. System informs customer of failure without exposing reason.
    7a2. Customer selects a different payment method or retries. Continue at step 5.
    7a3. Customer cancels. Use case ends; cart preserved.

  8a. One or more items is out of stock:
    8a1. System notifies customer of out-of-stock items with alternatives.
    8a2. Customer removes items, selects alternatives, or cancels. Continue at step 1.

  *a. System unavailable at any step:
    *a1. System preserves cart state.
    *a2. Customer is directed to retry later. Use case ends.

Special Requirements:
  - Payment data must not be persisted in application logs.
  - Order confirmation email must be sent within 30 seconds of submission.

Technology & Data Variations:
  - Step 5: Credit card, PayPal, or store credit.
  - Step 10: Email or SMS per customer preference.

Frequency:     High volume; thousands per day; peak at evenings and holidays.
Open Issues:   - Partial fulfillment: ship available items now, remainder later?
               - Fraud scoring: when does it trigger manual review?
```
