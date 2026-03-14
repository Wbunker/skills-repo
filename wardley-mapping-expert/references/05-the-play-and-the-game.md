# The Play and the Game — Climatic Patterns and Gameplay

Reference for climatic patterns (predictable environmental changes) and gameplay (strategic moves).

## Two Layers of Strategy

After doctrine (universal practices), strategy operates in two layers:

1. **Climatic Patterns** — Changes in the landscape you cannot stop, only anticipate
2. **Gameplay** — Moves you make deliberately to shape the landscape in your favor

Understanding climatic patterns tells you *what will happen*. Gameplay tells you *what to do about it*.

## Climatic Patterns

Climatic patterns are predictable patterns that affect the landscape regardless of what any individual player does.

> "Climate is what you expect; weather is what you get."

### Pattern 1: Everything Evolves
- All components evolve from genesis to commodity, driven by competition
- You cannot stop evolution — only delay it at great cost
- Fighting evolution is the single most common and costly strategic mistake

**Implication**: Identify where your components are evolving and plan ahead.

### Pattern 2: Characteristics Change
As components evolve, their characteristics change fundamentally:
- Genesis → Custom: from novel to better-understood
- Custom → Product: from scarce to purchasable
- Product → Commodity: from differentiating to table stakes

**Implication**: Management practices that worked at one stage fail at the next.

### Pattern 3: No Choice on Evolution
Individual companies do not decide whether a component evolves. The market decides.
- Refusing to adopt cloud computing doesn't stop cloud from becoming the standard
- Building your own when the market commoditizes is always more expensive

**Implication**: Accept that you will need to move with evolution. Plan for the transition.

### Pattern 4: Past Success Breeds Inertia
Organizations most successful with current approaches have the most to lose from evolution and the most resistance to change.

**Implication**: Incumbents are reliable victims of disruption. Disruption is predictable.

### Pattern 5: Inertia Increases as Components Evolve
The closer to commodity, the more infrastructure and process has built up around it. This makes change harder.

**Implication**: Evolution creates inertia; inertia creates opportunity for disruptors.

### Pattern 6: No Single Method Works Everywhere
Different evolutionary stages require different management approaches. There is no universal best practice that applies to all contexts.

**Implication**: Applying one method everywhere (e.g., "we do agile") is always wrong.

### Pattern 7: Components Can Co-Evolve
When a component evolves, related components often evolve with it (practices, data, business models).

**Example**: Cloud compute commoditizing → DevOps practices evolve → CI/CD tools commoditize → Infrastructure as Code becomes standard.

**Implication**: Look for chains of co-evolution that will create new opportunities and threats.

### Pattern 8: Supply and Demand Competition Drives Evolution
- More players in a space → more competition → faster commoditization
- Open source dramatically accelerates commoditization by removing proprietary barriers

**Implication**: If you want to commoditize a space (to undermine a competitor's advantage), open source it.

### Pattern 9: Efficiency Enables Innovation
When components become commodity utilities, they enable new innovations on top of them.

**The Stack**:
```
New Genesis (made possible by commodity below)
    ↑
Commodity (e.g., cloud compute)
    ↑
Previous Innovation (that enabled cloud)
```

**Implication**: Commoditization of one layer releases innovation energy into the layer above.

### Pattern 10: Higher Order Systems Create New Sources of Worth
As components commoditize, new higher-order activities become possible — creating new value chains and new sources of competitive advantage.

**Example**: When electricity became a utility, an entire economy of appliances and industries became possible.

## Gameplay — Strategic Moves

Gameplay consists of deliberate moves in the landscape. Unlike doctrine (always do this), gameplay is contextual — the right move depends on what the map shows.

### Category 1: Accelerating Evolution

#### Open Source
**When**: A component is in the product stage and competitors depend on it for revenue.
**Move**: Open source the component to accelerate commoditization, destroying the competitor's position.
**Mechanism**: A strong enough open source community drives a component from product to commodity.
**Example**: Google open-sourced Android to commoditize the mobile OS layer.

#### Open Data
**When**: Data in a domain is locked up in proprietary silos, slowing ecosystem development.
**Move**: Release datasets openly to accelerate evolution and market formation.

### Category 2: Decelerating Evolution (Defensive)

#### Fear, Uncertainty, and Doubt (FUD)
**When**: A competitor is about to move to a more evolved form.
**Move**: Strategically introduce concerns about stability, security, or readiness of the evolved form.
**Risk**: Delays the inevitable and creates inertia in your own organization; temporary at best.

#### Patent Ring-Fencing
**When**: You have a strong patent portfolio in an evolving space.
**Move**: Use patents to prevent competitors from building in your space, slowing their evolution.
**Warning**: Creates enemies and regulatory risk; delays evolution but cannot stop it.

### Category 3: Ecosystem Plays

#### ILC — Innovate, Leverage, Commoditize
The most powerful long-term ecosystem strategy (Amazon's core play):
1. **Innovate**: Let ecosystem partners build new things on your platform
2. **Leverage**: Observe what gets traction; learn at ecosystem scale
3. **Commoditize**: Absorb successful innovations as platform features; price at utility

**Why it's devastating**: You get free R&D from ecosystem partners, then eat their business models.

#### External Pioneer Model
**When**: You want genesis-stage innovation without the internal cost and failure rate.
**Move**: Push your pioneers *outside* the organization — let other companies be your innovation sensing engine by experimenting on your platform.
**Mechanism**: Other companies take the risk; you observe what works.

#### Meta-Data Monitoring
**When**: You have a large platform with many ecosystem members.
**Move**: Track consumption patterns across ecosystem services (without examining internal data) to identify emerging patterns.
**This provides**: A future-sensing capability respecting privacy and security constraints.

#### Multiple Meta-Data Sources
**When**: Running an ILC play.
**Move**: Create multiple touchpoints (billing engines, app stores, component libraries, brokerage services) to gather signals about which ecosystem innovations are gaining traction.

#### Marketplace Creation
**When**: A space has few suppliers and users face lock-in risk.
**Move**: Deliberately create a competitive marketplace of providers, reducing customer dependency and accelerating commodity formation.

#### Certification System
**When**: Creating an open ecosystem with multiple providers.
**Move**: Create standardized testing suites to certify compliant providers, maintaining portability without preventing competition.

#### Platform Expansion
**When**: Building an ecosystem platform.
**Move**: Progressively add new utility components to the platform, building attractiveness through breadth rather than monolithic lock-in.

### Category 4: Positional Plays

#### Land Grab
**When**: A genesis-stage component will become critical.
**Move**: Move fast to establish position before it's obvious to everyone.
**Risk**: High — genesis-stage bets often fail.

#### Tower and Moat
**When**: You have a unique capability or utility position.
**Move**: Build a platform (tower) around the capability, then create ecosystem lock-in (moat) through integrations, data, and switching costs.
**Example**: Salesforce's AppExchange — CRM is the tower; the ecosystem is the moat.

#### Exploit Inertia
**When**: Competitors are locked into a component that is evolving toward commodity.
**Move**: Move to the commodity version faster than they can. Their inertia becomes your advantage.

#### Sensing Engines
**When**: You operate at commodity scale and generate large data.
**Move**: Use data from commodity operations to sense future patterns and anticipate user needs.
**Example**: Amazon using purchase history to anticipate what customers will want next.

### Category 5: Attacking Plays

#### Value-Based Service Pricing
**When**: You operate above a commodity layer and create measurable user value.
**Move**: Price on percentage of value created (not cost), enabling premium capture on utility infrastructure.

#### Price War as Demand Driver
**When**: You can absorb a price war that your competitors cannot.
**Move**: Use aggressive pricing to increase demand beyond any single competitor's capacity, fragmenting market control.
**Mechanism**: Forces demand elasticity beyond competitor capacity, creating fragmentation.

#### Supplier Fragmentation
**When**: A critical infrastructure component is dominated by a single supplier.
**Move**: Deliberately cultivate multiple competing suppliers to prevent monopolistic control.

#### Upstream Open Sourcing
**When**: A foundational technology layer needs to exist as a commodity before you can build your play above it.
**Move**: Release the foundation as open source to catalyze market formation in that layer.

#### Undermining Barriers to Entry
**When**: A competitor relies on a proprietary component to maintain market position.
**Move**: Fund or develop an open alternative that removes the barrier.

#### Constraint Exploitation
**When**: Competitors have dependencies that will constrain their movement (data center capacity, skilled labor, component availability).
**Move**: Position to benefit when those constraints emerge.

### Category 6: Defensive Plays

#### Harvesting
**When**: A component in your portfolio is evolving toward commodity.
**Move**: Maximize returns while transitioning to the next thing. Stop investing in innovation; extract value.

#### Defensive Regulation
**When**: Evolution threatens your position faster than you can adapt.
**Move**: Lobby for regulations that slow evolution or create barriers to competitors.
**Warning**: Delays the inevitable and creates massive internal inertia; use sparingly.

#### Acquisition Path Preparation
**When**: You've built utility infrastructure that larger platform companies will need.
**Move**: Position your technology as indispensable infrastructure for acquirers; build toward exit.

### Category 7: Cultural/Purpose Plays

#### Purpose Articulation and Rallying Cry
**When**: You need organizational alignment for a long, difficult transition.
**Move**: Create a moral imperative — a vision of the future that motivates beyond financial metrics.
**Mechanism**: Purpose creates resilience through difficult War-phase transitions.

#### Catchphrase Branding
**When**: Communicating complex value propositions internally or externally.
**Move**: Use memorable, emotionally resonant language to align culture and communicate strategy.

### Category 8: Technical Plays

#### Pioneer, Settler, Town Planner (PST)
Organize your organization around the evolutionary stage of your work:
- **Pioneers**: Explore genesis-stage opportunities (accept high failure rates)
- **Settlers**: Develop custom-built work into products (productize pioneer discoveries)
- **Town Planners**: Run product/commodity work at scale (industrialize settler products)

More on PST in Chapter 16.

## The First-Mover to Industrialization + Fast Follower Combination

A powerful combined play:
- Be **first to standardize** (industrialize) a key component
- Then be a **fast follower** to successful innovations that emerge in the ecosystem built on that standard

First-mover infrastructure advantage + fast-follower discovery economics. Amazon's playbook.

## Combining Gameplay

Sophisticated strategy combines multiple plays simultaneously:

### Example: Amazon's Strategy
1. Commoditize compute (open source Linux, build AWS)
2. ILC with developer ecosystem (AWS marketplace)
3. Sensing engine (purchase data → recommendation engine → new products)
4. Exploit inertia of enterprise IT (move faster than Oracle and IBM can react)
5. Two-sided market (marketplace between sellers and buyers)

The map shows where each play fits and how they reinforce each other.

## Reading the Game

### How to Identify Available Gameplay
1. Map your landscape
2. Identify components nearing evolutionary stage transitions
3. Identify competitor inertia
4. Identify open source opportunities
5. Identify ecosystem plays
6. Consider which moves your competitors can and cannot counter

### The Counter-Move Problem
Every play has potential counter-plays. Good gameplay anticipates:
- How competitors will respond
- How to make your position counter-resistant
- Which plays cannot be countered (commoditization is usually unstoppable)

### The Tempo Advantage
Moving at the right time matters as much as the move itself:
- Too early: market not ready, no ecosystem
- Too late: competitor has already established position
- Maps help you see when timing is right

## Common Gameplay Mistakes

### 1. Playing Defense When Offense is Available
Defending an evolving position costs more and more. Better to offensively move to the next stage.

### 2. Ignoring Ecosystem Effects
Ecosystems amplify positions. Failing to play ecosystem-aware strategy leaves value on the table.

### 3. Open-Sourcing Your Differentiators
Only commoditize things that you don't need as differentiators. Open-sourcing your core advantage destroys your position.

### 4. Not Anticipating Co-Evolution
When you make a move, anticipate what will co-evolve as a result and plan for the next move.

### 5. Single-Move Thinking
The best strategies involve multiple moves planned in sequence, with contingencies for how competitors respond.
