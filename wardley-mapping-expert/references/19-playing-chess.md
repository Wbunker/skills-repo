# On Playing Chess — Multi-Move Strategy and Counter-Play

Reference for advanced strategic thinking: planning multiple moves ahead, anticipating counter-moves, and building strategic sequences.

## Strategy as Chess, Not Checkers

Simple strategy: make the best move available right now.
Advanced strategy: make the move that sets up the best position for the next three moves, even if it's not the best single move.

Wardley Mapping enables chess-level thinking by:
- Making the landscape visible (you can see the whole board)
- Making trajectory visible (you can see where pieces are moving)
- Making available moves explicit (you can enumerate options)
- Making counter-moves predictable (you understand competitor inertia)

## The Planning Sequence

### Level 1: Single-Move Thinking
"We should do X because the map shows opportunity Y."

This is better than no strategic thinking but leaves value on the table.

### Level 2: Two-Move Thinking
"We should do X, which will cause Y to happen, which creates opportunity Z for us."

Most strategic planning operates here.

### Level 3: Multi-Move Thinking
"We should do X, which causes Y, which creates Z, which enables us to do W, which we use to build V."

Amazon's AWS strategy was a 5–7 move sequence planned over a decade.

### Level 4: Adaptive Multi-Move Thinking
"We should do X. If competitor A responds with P, we do Q. If they respond with R, we do S. If neither, we do T."

Game theory territory — but maps make this tractable.

## The Counter-Move Analysis

For every strategic move, ask: "What is the most effective counter-move, and can we make our move counter-resistant?"

### Mapping Competitor Options
On your map, add your key competitors. For each move you're considering:
1. Which competitor is most threatened?
2. What counter-moves are available to them?
3. What are their constraints? (inertia, existing commitments, capabilities)
4. Which counter-moves can they NOT make (due to inertia or cost)?

### The Inertia-Based Counter Analysis
Competitors with high inertia have constrained counter-options:
- They cannot cannibalize their own revenue
- They cannot alienate their existing customers
- They cannot abandon their existing partnerships
- They cannot pivot their organization quickly

Your move should ideally exploit one of these constraints.

### Example: The AWS Counter Analysis
When Amazon announced AWS in 2006, what could incumbents do?
- **IBM**: Could not respond quickly — on-premise infrastructure was core to their business model (inertia)
- **Oracle**: Could not price at utility levels — software licensing was their model (inertia)
- **HP**: Could respond with hosted services — but their sales force was optimized for hardware (organizational inertia)
- **Microsoft**: Could respond — and eventually did with Azure (but 5 years late)

Amazon's move was designed around these inertia constraints. Microsoft was the only dangerous counter, and Microsoft's inertia (Windows Server licensing) bought Amazon a 5-year head start.

## The Strategic Sequence

Building a multi-move sequence on a Wardley Map:

### Step 1: Map the Current Landscape
Current positions of all components and key players.

### Step 2: Map the 3-Year Future Landscape
Where will components be based on climatic patterns?

### Step 3: Identify the Leverage Points
Which transitions (in the 3-year horizon) create the most opportunity?

### Step 4: Sequence the Moves
What must happen first to enable later moves?
- Move A creates the position for Move B
- Move B creates the conditions for Move C
- Move C is the intended destination

### Step 5: Identify Contingencies
- If Move A doesn't work as planned, what's the pivot?
- If a competitor makes a move between A and B, how do you respond?

## Classic Multi-Move Patterns

### The Ecosystem Ladder
1. **Move 1**: Commoditize a component (make it free/cheap/open source)
2. **Move 2**: Build a platform on top of the commodity
3. **Move 3**: Attract ecosystem participants to the platform
4. **Move 4**: Apply ILC — observe what ecosystem builds, commoditize the valuable parts
5. **Move 5**: Lock in ecosystem through data and integration (moat building)

**Why it works multi-move**: Moves 1–2 lose money. Moves 3–5 generate enormous returns. Single-move thinkers stop at Move 2.

### The Talent Drain
1. **Move 1**: Build a compelling engineering environment (open source, interesting work, good culture)
2. **Move 2**: This attracts the best engineers in the industry
3. **Move 3**: Competitors lose their best engineers (or fail to attract them)
4. **Move 4**: Competitors' pace of innovation slows
5. **Move 5**: Execute on the capability advantage created

**Why it works multi-move**: The talent advantage compounds. Each generation of great engineers attracts the next generation.

### The Standards Play
1. **Move 1**: Create an open standard based on your current implementation
2. **Move 2**: Donate to a standards body or open source organization
3. **Move 3**: Competitors must now implement your standard (you have head start)
4. **Move 4**: You continue to evolve faster because you understand the standard best
5. **Move 5**: Ecosystem builds on the standard → you benefit most from ecosystem growth

**Why it works multi-move**: Your commodity becomes everyone's commodity, but you maintain the adjacent layer advantage.

## The Stepping Stones Strategy

One of Wardley's clearest multi-move examples (the Fotango story):

**Context**: A photo service (Fotango) facing disruption by digital photography.

**The Move Sequence:**
1. **Recognize the current position is failing** (photo service declining)
2. **Identify the adjacent stepping stone**: Cloud computing infrastructure was emerging — build a PaaS (Platform as a Service) called Zimki
3. **Use the stepping stone as a beachhead**: Zimki positioned Fotango in the emerging cloud platform space
4. **Target the next position**: Use the platform play to run ecosystem and brokerage services on top of emerging IaaS (Amazon's infrastructure)

*"Creating a utility service in the platform space and exposing it through APIs was a stepping stone towards running an ILC (ecosystem) like game."*

**The lesson**: Don't ask "what's the best single move?" Ask "what move creates the best *position* for the next move?"

## The Three Mapping Methods for Strategic Advantage

Chapter 19 identifies three distinct methods for using maps to create competitive moves:

### Method 1: Recombination Play
**How**: Combine industrializing components in novel ways to expand into adjacent unexplored territory.
**Risk**: High — many combinations fail. This is Pioneer work.
**When to use**: When you see multiple components commoditizing simultaneously and imagine what new activities become possible above them.

### Method 2: Breaking Constraints
**How**: Identify bottlenecks in value chains and remove them.
**Example**: Recognizing that "infrastructure itself was capital intensive" — the constraint blocking innovation. Moving to IaaS removes the capital constraint, enabling rapid iteration.
**When to use**: When the map shows a component that is blocking evolution above it (high inertia, high cost, high custom-build requirement).

### Method 3: Evolution Exploitation
**How**: Target components transitioning from product to commodity when all four conditions exist (concept, suitability, technology, attitude).
**When to use**: The most reliable method — exploit predictable product-to-utility shifts before competitors do.

## The Capital Evolution Framework

Assets become liabilities through industry evolution. Your purchasing methods must evolve with the landscape:

| Component Stage | Appropriate Purchasing Method |
|-----------------|------------------------------|
| **Genesis** (uncertain) | Venture capital / R&D investment |
| **Custom** (emerging) | Outcome-based contracts |
| **Product** (defined) | COTS (Commercial Off-The-Shelf) |
| **Commodity** (utility) | Utility pricing / consumption model |

**The Early Adopter Trap**: Early adopters of one stage become *laggards* in the next.
- Companies that adopted cloud infrastructure in 2008–2012 (early) → become laggards if they don't adopt serverless/PaaS in 2018–2022
- Each evolutionary shift requires updating your purchasing model — staying on COTS when utility pricing is available is waste

## The Policy-Over-Technology Counter-Play

A sophisticated two-part play for when technical superiority isn't enough:

**Part 1 — Open and purchase cooperation**: Open your proprietary systems and data to other nations/players, purchasing their cooperation and goodwill instead of imposing standards.

**Part 2 — Transparency campaigns**: Launch campaigns toward shareholders and consumers to create pressure that circumvents corporate inertia from the inside.

**Why it works**: Changes *structural incentives* rather than trying to convince resistant parties. The map reveals where the structural pressure points are; this play applies pressure at those points.

## The Balancing Inertia Principle

A paradoxical but important strategic insight:

- **Inertia is valuable** before an industry shifts — it prevents premature abandonment of profitable positions
- **Inertia is catastrophic** during an industry shift — it prevents necessary adaptation

The strategic challenge is maintaining *dynamic equilibrium*: enough inertia to avoid thrashing, insufficient inertia to avoid getting stuck.

Maps help by showing **when** a shift is approaching (via climatic patterns) — enabling you to plan your inertia reduction before the shift, rather than after.

## The Timing Dimension

Multi-move strategy requires understanding timing:

### Time Horizons on Maps
Draw your map with three temporal layers:
- **Now**: Current positions
- **12-18 months**: Positions after near-term evolution
- **3-5 years**: Positions after major transitions

Each layer reveals when to execute which moves.

### The Sequencing Constraint
Some moves can only happen after others:
- You cannot build a platform before the commodity it sits on exists
- You cannot exploit ecosystem data before you have an ecosystem
- You cannot exploit competitor inertia before the component has evolved past their position

**Map-based timing**: The evolution axis tells you approximately when each component will reach the stage that enables each move.

### Early vs. Late Mover Advantages
**Early mover advantages:**
- Pioneer advantage in relationships, talent, brand
- First-to-commoditize advantages (you set the commodity baseline)
- Ecosystem attraction (build before competitors create alternatives)

**Late mover advantages:**
- Learn from pioneer's mistakes
- Adopt at the inflection point (proven technology, lower risk)
- Move when the market is ready (not before)

Maps help you identify which situation you're in.

## The Defense Strategy

Not all strategy is offensive. When defending:

### Identifying Your Defensible Position
On your map, identify components where you have durable advantage:
- Components still in Genesis/Custom that you discovered (pioneer advantage)
- Data assets accumulated at commodity scale (data moat)
- Ecosystem relationships (switching costs for ecosystem members)
- Network effects (more users → more value → more users)

### Building the Moat
Moats are second-order advantages that make your primary position harder to attack:

| Moat Type | How it Works | How to Build |
|-----------|-------------|-------------|
| **Data** | Accumulated data that competitors cannot replicate | Run commodity services at scale; capture learning |
| **Network effects** | More users = more value | Platform plays; grow the user base |
| **Ecosystem lock-in** | Switching costs for partners | Deep integrations; partner investment |
| **Standards** | Owning the standard means owning the category | Open source + standards bodies |
| **Talent** | Best engineers compound capability advantages | Environment, challenge, culture |

### The Moat Timing Problem
Build moats before you need them:
- By the time a competitor attacks, it's too late to build the moat
- Moats require time to develop (data accumulates; networks grow; ecosystems deepen)

Maps help you see when attacks are coming — giving you time to strengthen moats proactively.

## Strategic Trade-offs

Every strategy involves trade-offs. Maps make them visible:

### Speed vs. Defensibility
Moving fast (pioneer advantage) often sacrifices defensibility (moats take time to build).
Maps help you see when you've been fast enough to establish position and when it's time to slow down and build moats.

### Focus vs. Optionality
Committing resources to a multi-move sequence reduces optionality (you're committed to the sequence).
Maps help you identify which sequence commitments are high-confidence (climatic patterns support them) and which are bets (depend on specific outcomes).

### Commoditize vs. Protect
Commoditizing a component you're good at creates ecosystem leverage but destroys your margins in that component.
Maps help you see whether the ecosystem play is worth the margin sacrifice.

## The Chess Grandmaster Heuristic

Grandmasters don't calculate every possible game — they pattern-match to known positions and evaluate a small number of high-value lines.

Wardley Mappers develop the same capability:
- Pattern recognition (these climatic patterns always work out this way)
- Known playbooks (these gameplay sequences work in these situations)
- Competitor modeling (this type of competitor always responds this way)
- Landscape reading (this configuration of components means...)

This pattern recognition is what separates experienced mappers from beginners — and experienced strategists from planners.
