# Super Looper — Pioneer, Settler, Town Planner and Organizational Structure

Reference for the Pioneer-Settler-Town Planner (PST) model, organizational design aligned to evolution, and the OODA loop.

## The Pioneer-Settler-Town Planner Model

One of Wardley's most important contributions to organizational design: matching organizational archetype to the evolutionary stage of the work.

### The Three Types

#### Pioneers
**Purpose**: Explore genesis-stage opportunities

**Characteristics:**
- Tolerant of failure and ambiguity
- Strong exploratory instincts
- Often unconventional thinkers
- Work best with minimal process
- Create entirely new things (often poorly implemented)

**What they produce**: Prototypes, experiments, proof-of-concepts that are often ugly but functional

**What they should NOT do**: Run commodity operations (wastes talent), maintain existing systems (deeply frustrating), follow rigid process (kills creativity)

**Metrics**: Number of experiments run, learning per failure, novel concepts generated

#### Settlers
**Purpose**: Develop custom-built work into products

**Characteristics:**
- Can work with pioneers' rough creations and make them usable
- Understand both the genesis stage and the product stage
- Strong at synthesizing and clarifying
- Build bridges between the rough and the reliable

**What they produce**: Productized versions of pioneer discoveries, working software, documented practices

**What they should NOT do**: Explore freely (needs more focus than pioneers), run commodity operations (too much creativity for that)

**Metrics**: Products shipped, practices documented, pioneer work brought to production quality

#### Town Planners
**Purpose**: Industrialize products into scalable, reliable commodity services

**Characteristics:**
- Deep appreciation for process, consistency, and reliability
- Frustrated by ambiguity and change
- Excellent at optimization and scale
- Find meaning in stability and predictability

**What they produce**: Scalable, reliable, cost-efficient commodity services

**What they should NOT do**: Explore or experiment (actively harmful at this stage), attempt to differentiate commodity components (waste of effort)

**Metrics**: Reliability (uptime, error rates), efficiency (cost per unit), consistency

### The Key Insight
These are not just personality types — they represent different **aptitudes and attitudes** that are genuinely incompatible when applied to the wrong evolutionary stage:
- Put a Pioneer in charge of commodity operations: chaos, unreliability, high cost
- Put a Town Planner in charge of genesis exploration: bureaucracy kills the exploration
- Put either in the Settler role: either too rough (Pioneer) or too rigid (Town Planner)

## Why Most Organizations Are Structured Wrong

Most organizations use one structure for all evolutionary stages:
- "We're agile" → applies pioneer-style practices to commodity operations (inefficiency)
- "We have rigorous governance" → applies town-planner practices to genesis work (kills innovation)
- "We run everything as a product" → appropriate for Product stage, wrong for others

The result: innovators frustrated in bureaucratic organizations; operators frustrated in chaotic "innovative" organizations.

## The Three-Speed Organization

To run all three evolutionary stages simultaneously, you need three speeds:

```
Speed 1: Pioneer (Unstructured)
  ─ Genesis work ─
  High autonomy, high tolerance for failure
  ↓
Speed 2: Settler (Semi-structured)
  ─ Custom → Product work ─
  Defined processes, but room for craft
  ↓
Speed 3: Town Planner (Structured)
  ─ Product → Commodity work ─
  Process-driven, SLA-governed, efficient
```

**The organizational challenge**: Running all three simultaneously requires different management approaches, different metrics, and different cultures — in the same organization.

## The Flow Between Types

PST is not just three static groups — it's a system with flow:

```
Pioneers → create rough new things
    ↓
Settlers → take Pioneer discoveries and productize them
    ↓
Town Planners → take Settler products and industrialize them
    ↓
(freed-up Pioneers can now explore the next layer)
```

This is the Amazon model:
- AWS Lambda was pioneered by small teams
- Productized and made reliable (settler phase)
- Now runs at industrial scale with SLAs (town planner phase)
- Freed resources are now exploring the next genesis opportunity

## The Theft Problem

In practice, the most valuable people in each group are "stolen" by other groups:

**Pioneers steal Settlers**: "Come help us build this exciting new thing"
- Result: Settler's products never get productized properly
- The transition from custom to product is perpetually stuck

**Settlers steal Town Planners**: "We need someone reliable to make this work"
- Result: Nothing gets industrialized; commodity operations remain custom-built
- Expensive and unreliable commodity operations

**Town Planners pull Settlers**: "We need process around this"
- Result: Products get over-processed before they're ready
- Innovation slowed by premature optimization

**Solution**: Make the PST structure explicit and protect each group's work.

## The Conway's Law Connection

Conway's Law: "Organizations which design systems are constrained to produce designs which are copies of the communication structures of those organizations."

**Wardley's extension**: The communication structure should match the evolutionary stage:
- Genesis work: small, autonomous teams with minimal communication overhead
- Product work: product teams with clear interfaces
- Commodity work: service teams with SLAs and defined interfaces

If you want to build a commodity service but your team is structured like a pioneer group, you'll get an unreliable, expensive service. The structure must match the work.

## Financial Analysis Tools for PST Decisions

### Options Analysis
When deciding between strategic variants (e.g., in-house build vs. platform adoption), use options analysis comparing:

| Factor | In-house Variant | Platform/Utility Variant |
|--------|-----------------|--------------------------|
| Probability of success | Typically lower (custom complexity) | Typically higher (proven) |
| Total investment required | Higher upfront | Lower upfront, ongoing OPEX |
| Total potential return | Higher if successful | Lower ceiling, more predictable |
| Opportunity loss | Miss platform ecosystem benefits | Miss full margin capture |
| Net benefit/loss | Scenario-dependent | Scenario-dependent |
| Expected return | Probability × Net benefit | Probability × Net benefit |

**Warning**: Standard financial models contain bias toward **present value** — they systematically undervalue future optionality, which maps are specifically designed to reveal.

### The Sunk Cost Distinction
A critical insight for in-house vs. utility decisions:

- **In-house infrastructure**: Refactoring creates direct financial returns because you're reducing your own cost basis
- **Utility consumption model**: Refactoring your code to use the utility efficiently creates direct cost savings

This sounds obvious, but many organizations apply in-house thinking to utility consumption decisions (treating utility subscriptions like capital assets) or vice versa.

### Business Model Canvas as Final Verification
After completing map analysis and options analysis, use the Business Model Canvas as a final validation step:
- Does the selected strategic variant have a coherent business model?
- Is the value proposition achievable given the landscape?
- Are the revenue streams viable given where components are evolving?

The Canvas is downstream from the map — it validates the chosen path, not the other way around.

## Multiple Inertia Types (Detailed)

Chapter 16 identifies more granular inertia sources than the basic categories:

1. **Investment in knowledge capital** (skills and expertise built around current approach)
2. **Changes to governance** (processes and approval structures built around current model)
3. **Loss of political capital** (relationships and influence built on defending current position)
4. **Loss of social capital** (vendor and partner relationships dependent on current model)
5. **Data reinforcing past success** (metrics and KPIs that make the old model look good)
6. **Resistance from rewards/culture systems** (compensation tied to current approach)

**Tactics for managing each:**
- Acknowledge achievements (validates knowledge capital without endorsing the old path)
- Provide future relevance paths (skills translation, retraining)
- Create new political structures around the new approach
- Manage vendor relationships through the transition with advance notice and support

## The OODA Loop in Strategy

The OODA Loop (Observe-Orient-Decide-Act) from Col. John Boyd explains both how fast organizations win and why slow organizations lose.

```
Observe → Orient → Decide → Act → (repeat)
    ↑__________________________________|
```

### Observe
Collect information about the landscape:
- Market signals
- Competitor movements
- Technology evolution
- Customer behavior changes

**Maps improve this step**: A map gives you a structured way to observe what matters.

### Orient
Make sense of what you've observed:
- What patterns are visible?
- What does this mean for our position?
- How does this change what we thought we knew?

**Maps improve this step dramatically**: Without a map, orientation is ad hoc and biased. With a map, orientation is structured and challengeable.

This is the most critical step and the one where most organizations fail.

### Decide
Choose a course of action:
- What moves are available?
- Which move best addresses the observed patterns?
- What are the risks?

**Maps inform this step**: Gameplay is visible on maps; without maps, decisions are based on incomplete models.

### Act
Execute the decision:
- Move quickly
- Maintain orientation as you act (the landscape changes as you move)
- Prepare for the next OODA cycle

### Winning with OODA
Boyd's insight: the winner is not the one who makes the best single decision — it's the one who cycles through OODA **faster** than the opponent.

The opponent who is still in "Decide" when you're already into your second "Act" cycle is perpetually behind.

**Maps accelerate OODA** by:
- Making "Orient" faster (you have a shared mental model)
- Making "Decide" faster (gameplay is pre-mapped for likely scenarios)
- Enabling "Act" with confidence (you understand why you're doing what you're doing)

## Organizational Design Using PST

### Mapping Your Organization to PST
1. List all major activities/teams
2. For each, identify the evolutionary stage of their primary work
3. Assess whether the current organizational structure, culture, and metrics match the stage
4. Identify mismatches

### Designing the Transition
Moving from a single-speed to a three-speed organization:
1. Identify the natural pioneers, settlers, and town planners (they already exist)
2. Create explicit space for each type
3. Define the flow between types (how does pioneer work become settler work?)
4. Protect each group from being stolen by the others
5. Create metrics appropriate to each stage

#### The PST Parallel: Kent Beck's 3X
Kent Beck's 3X model independently arrived at a similar structure:
- **Explore**: Uncertain territory, experimentation (= Pioneer)
- **Expand**: Scaling what works (= Settler)
- **Extract**: Optimization at scale (= Town Planner)

The independent convergence on similar models suggests PST describes something real about how organizations must function across evolutionary stages.

## Leadership for PST Organizations
Each group needs different leadership:
- **Pioneer leaders**: Create safety for experimentation and failure
- **Settler leaders**: Drive the transition from rough to reliable
- **Town Planner leaders**: Maintain the reliability and efficiency machine

A leader who excels at one type will often be destructive to another.
