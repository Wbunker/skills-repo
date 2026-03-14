# Finding a Path — Value Chains and Map Construction

Reference for building Wardley Maps: user needs, value chains, components, and anchors.

## The Anatomy of a Wardley Map

A Wardley Map has two axes:

```
 Visible to User
        ↑
        │   [User]
        │     │
        │   [Need]
        │     │
        │ [Component A]──[Component B]
        │     │
        │ [Component C]
        │
        │
Invisible
to User ─────────────────────────────────→
                                        Evolved
   Genesis    Custom   Product    Commodity
```

### Y-Axis: Visibility (Value Chain)
- **Top**: visible to the user (what they directly interact with)
- **Bottom**: invisible infrastructure (what enables the user-visible components)
- Position on Y-axis represents dependency/visibility, not importance

### X-Axis: Evolution
- **Left (Genesis)**: new, uncertain, poorly understood
- **Right (Commodity)**: mature, well-defined, utility-like
- All components evolve from left to right over time (this is a law, not a choice)

## Step 1: Identify the User and Their Needs

### Start with the Anchor: The User
Every map starts with a user. The user is the anchor — everything else on the map exists to serve user needs.

**Questions to ask:**
- Who is our user?
- What do they need from us?
- What does success look like for them?

### Identifying True Needs
Users often express desires, not needs. Distinguish between:
- **Desire**: "I want a faster horse" (Henry Ford apocrypha)
- **Need**: "I need to get from A to B faster"

### Multiple Users
Most businesses have multiple user types:
- Customers (external)
- Employees (internal)
- Partners / ecosystem participants
- Regulators

Map each user's value chain separately, then look for commonalities.

## Step 2: Build the Value Chain

### What is a Value Chain?
A chain of dependencies that delivers value to the user. Each component on the map has:
- Components it depends on (below it)
- Components that depend on it (above it)

### Example: Tea Shop Value Chain
```
[Customer]
    │
[Cup of Tea]
    │
[Tea]─────[Hot Water]─────[Kettle]─────[Power]
                │
              [Cup]
```

Every item in this chain is a component. Every arrow is a dependency.

### Rules for Value Chains
1. Start at the top with the user
2. Work downward — what does each component need to exist?
3. Be specific — "IT infrastructure" is too vague; break it down
4. Include everything that is needed, even if you don't currently provide it
5. Stop when you reach true commodities (electricity, the internet, etc.)

## Step 3: Assess Evolution

For each component, ask: **where is it on the evolutionary axis?**

### The Four Stages of Evolution

| Stage | Characteristics | Examples |
|-------|----------------|---------|
| **Genesis** | Novel, uncertain, poorly understood, expensive, unreliable, requires specialists | Generative AI (2022–2024), early blockchain, first smartphones |
| **Custom Built** | Better understood, still requires skill to build, not widely available | Custom ML models, bespoke integrations |
| **Product** | Available as a product, can be bought off the shelf, competitive differentiation possible | Most SaaS software, cloud databases |
| **Commodity/Utility** | Standardized, widely available, price-driven, no differentiation | Electricity, internet connectivity, email |

### How to Assess Evolution Stage
Ask these questions:
1. **How well understood is the component?** (Genesis = poorly; Commodity = completely)
2. **How many suppliers exist?** (Genesis = almost none; Commodity = many)
3. **Is it described with unique or standardized language?** (Genesis = novel; Commodity = defined standards)
4. **Is it bought or built?** (Genesis = built; Commodity = bought)
5. **How certain is its future?** (Genesis = uncertain; Commodity = predictable)

### Evolution is Not Adoption
Evolution ≠ how widely adopted a technology is.
- The internet was a commodity before most businesses used it
- A technology can be a commodity in one industry and genesis in another

## Step 4: Draw the Map

### Positioning Components
- Y-axis position: how visible is this to the user? (higher = more visible)
- X-axis position: what evolutionary stage? (left = genesis, right = commodity)

### Connecting Components
Draw arrows from each component to its dependencies. Arrows point down (toward dependencies).

### Example Map: Online Retailer
```
High Visibility
        │
    [Customer]
        │
  [Purchase Experience]
        │         │
[Product Catalog] [Payment Processing]
        │              │
[Inventory System] [Payment Gateway]
        │
[Warehouse Management]
        │
[Logistics]──────[Data Center]
        │              │
[Delivery Trucks] [Electricity]

Low Visibility
    Genesis          Custom        Product      Commodity
```

## Common Mapping Mistakes

### Mistake 1: Mapping Activities Instead of Components
Wrong: "Customer service" (activity)
Right: "Customer service platform" (component with an evolutionary stage)

### Mistake 2: Too Much Detail Too Early
Start with 5–15 components. Add detail as understanding grows.

### Mistake 3: Positioning by Adoption, Not Evolution
"Everyone uses cloud, so it must be commodity" — cloud infrastructure IS a commodity; specific cloud services may not be.

### Mistake 4: Confusing Y-Axis with Importance
Low on the Y-axis does not mean unimportant. Power generation is at the bottom but is essential.

### Mistake 5: Making It Perfect First Time
Maps are wrong. That's fine. The value is in the thinking, iteration, and conversation.

## The Language of Maps

### Components
Things that appear on a map. Can be:
- **Activities** (things you do): processing an order, customer support
- **Practices** (how you do things): agile development, lean operations
- **Data** (information used): customer records, product catalogue
- **Knowledge** (understanding): domain expertise, research

### Dependencies
Arrows between components showing what depends on what. Dependencies flow downward on the map.

### Anchors
The user(s) and their needs are anchors — they define what goes on the map.

### Movement
Arrows that show the direction of evolution. All components move left to right over time.

## Why This Matters

The map is a communication tool. It enables:
- **Shared understanding** — everyone sees the same landscape
- **Common language** — debates become about position, not opinion
- **Decision-making** — build vs. buy decisions become obvious
- **Anticipation** — you can see what will evolve and plan ahead

> "A map is not the territory, but it is enormously useful for navigating the territory."
