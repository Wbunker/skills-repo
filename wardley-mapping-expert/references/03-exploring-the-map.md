# Exploring the Map — Evolution, Characteristics, and Reading Maps

Reference for the evolution axis, characteristics of each stage, and how to interpret what a map tells you.

## The Evolution Axis in Depth

Evolution is the most important and misunderstood concept in Wardley Mapping.

### The Fundamental Law
> Every component evolves from genesis through custom-built and product to commodity, driven by supply and demand competition.

This is not a prediction. It is an observed pattern that holds across industries, technologies, and time periods. You cannot stop it — only use it or ignore it.

### Why Evolution Happens
1. **Competition**: Once something valuable exists, others copy and improve it
2. **Demand**: As more people use something, it becomes better understood
3. **Supply**: More suppliers emerge, driving standardization and price competition
4. **Efficiency**: Commoditization enables scale and further reduces cost

### Evolution is Uneven
- Different industries evolve at different rates
- Regulatory environments can slow evolution
- Network effects can accelerate it
- A component can evolve quickly in one geographic market and slowly in another

## The Four Stages — Detailed Characteristics

### Stage I: Genesis

**What it looks like:**
- First appearance of something novel
- Poorly defined, experimental, unstable
- High failure rate, rapid change
- Requires deep expertise to work with
- Expensive and scarce

**Organizational response needed:**
- Exploration, experimentation
- Tolerance for failure
- Small, specialized teams
- Pioneer mindset (cowboys, not process)

**Examples across domains:**
- Technology: Generative AI (2022), early internet (1993), first databases (1970s)
- Business practices: Agile (1990s), DevOps (2008)
- Products: First smartphones (2007), first electric vehicles (2000s)

**Signals that something is in Genesis:**
- Academic papers and research prototypes
- No standards or standards wars
- Small community of practitioners
- "It will never work" reactions from mainstream

### Stage II: Custom Built

**What it looks like:**
- Better understood but still specialized
- Built by craftspeople with domain knowledge
- Artisanal, not industrial
- Emerging patterns but not yet standardized
- Still expensive, but for skill not scarcity

**Organizational response needed:**
- Skilled specialists
- Project-based work
- Learning and documentation
- Settler mindset (farmers, not cowboys)

**Examples:**
- Custom software development for non-standard needs
- Bespoke consulting approaches
- Hand-crafted data pipelines before modern tooling

**Signals:**
- "Builds not buys" is normal
- Skills are rare and valuable
- Multiple incompatible approaches exist
- Case studies and best practices emerge

### Stage III: Product (+ Rental)

**What it looks like:**
- Available as standardized products
- Can be purchased off-shelf
- Features and competition drive differentiation
- Marketing and brand matter
- Price competition begins

**Organizational response needed:**
- Product management thinking
- Feature development and roadmaps
- Customer success and support
- Town Planner mindset (industrialization)

**Examples:**
- Commercial databases (Oracle, SQL Server)
- CRM software (Salesforce)
- Cloud services with feature differentiation (S3 in 2006–2015)

**Signals:**
- Multiple competing products exist
- Feature comparison websites appear
- Industry analysts cover it (Gartner Magic Quadrant)
- "Best practices" become well-documented

### Stage IV: Commodity / Utility

**What it looks like:**
- Standardized, interchangeable
- Price is the primary differentiator
- Operational excellence matters most
- Treated as infrastructure — expected to just work
- High volume, low margin

**Organizational response needed:**
- Process optimization
- Ruthless efficiency
- SLAs and reliability focus
- No innovation — just delivery

**Examples:**
- Electricity (utility)
- Basic cloud compute (AWS EC2 by 2015)
- Email (SMTP)
- HTTP/TCP/IP protocols
- Paper, steel, shipping containers

**Signals:**
- Price transparency and race-to-the-bottom pricing
- Standards bodies define the space
- "Why would you build your own?" is the common question
- Open source versions exist and are widely used

## Reading a Map: What to Look For

### Pattern 1: The Mismatch
When a component is in one evolutionary stage but is being treated as if it were in another.

**Example:**
- Treating a commodity like a custom-built (building your own email server when Gmail exists) → waste
- Treating a genesis component like a commodity (applying rigid process to AI experimentation) → kills innovation

### Pattern 2: The Bottleneck
A component that is still in Genesis or Custom-Built but is critical to delivering user value. This component will:
- Slow everything that depends on it
- Be expensive and uncertain
- Require specialist attention

**Strategic implication**: Accelerate its evolution or find a workaround.

### Pattern 3: The Opportunity
A component that is evolving toward commodity but where most competitors are still treating it as custom-built.

**Strategic implication**: Move faster than competitors to commoditize — use the commodity, don't build the custom.

### Pattern 4: The Inertia Zone
Components that *should* have evolved but haven't, usually because:
- Existing players have invested in the current stage
- Regulatory barriers
- Network effects protecting the status quo

**Strategic implication**: This is where disruption happens.

### Pattern 5: Co-evolution
When a component evolves, the practices and data around it also evolve.

**Example:**
- Compute evolving to commodity → DevOps practices evolve → Infrastructure as Code emerges
- Payment processing evolving → FinTech practices evolve → New business models emerge

## The Characteristics Grid

Use this grid to assess where a component sits:

| Characteristic | Genesis | Custom | Product | Commodity |
|---------------|---------|--------|---------|-----------|
| **Market** | Unformed | Forming | Growing | Mature |
| **Knowledge** | Novel | Emerging | Defined | Well-known |
| **Suppliers** | Very few | Few | Many | Very many |
| **Standards** | None | Competing | Emerging | Established |
| **Failure** | Expected | High | Medium | Low |
| **Management** | Exploration | Project | Product | Process |
| **Finance** | R&D | Investment | Revenue | Cost |
| **Users** | Innovators | Early adopters | Mainstream | Laggards |

## The Pace of Evolution

### What Accelerates Evolution
- **Competition**: More players → faster standardization
- **Open source**: Removes proprietary barriers to adoption
- **Regulation**: Sometimes forces standardization
- **Crisis**: War, pandemic, major disruption forces rapid evolution
- **Network effects**: More users → more value → more adoption

### What Slows Evolution
- **Inertia**: Incumbents defending existing positions
- **Regulation**: Can protect non-commodity stages
- **Complexity**: High switching costs slow adoption of new approaches
- **Capital intensity**: Large physical infrastructure slows change
- **Lack of competition**: Monopolies can forestall evolution

## Evolution vs. Diffusion of Innovation

Wardley's evolution axis is **not** the same as Rogers' diffusion of innovation curve.

- Diffusion (Rogers): describes adoption rates in a population
- Evolution (Wardley): describes the maturity of the component itself

A component can be adopted by 90% of businesses and still not be a commodity if it lacks standardization, pricing transparency, and utility-like characteristics.

## The Map as a Conversation Tool

The map's value is not in being correct — it's in being a shared artifact that enables better conversations:

1. **Challenge assumptions**: "You've put X in Custom-Built — why not Product? There are three vendors."
2. **Reveal disagreements**: People placing the same component in different stages have different mental models
3. **Force specificity**: "We need to improve our platform" becomes "We need to move component X from Custom to Product"
4. **Enable prioritization**: Resources go to components where evolution is happening fastest or where you have competitive opportunity

## Key Insight: The Map Tells You What to Do

Once you can see where components are on the map:
- **Genesis/Custom**: Build it yourself, or at minimum manage it closely
- **Product**: Buy or build depending on strategic importance
- **Commodity**: Buy or rent — never build

The corollary: the most common strategic mistake is building commodity components that should be bought, and buying differentiated components that should be owned.
