# The Scenario — Worked Examples and Case Studies

Reference for applying Wardley Mapping to real scenarios, including walkthroughs of historical and hypothetical cases.

## How to Use a Scenario

Scenarios teach mapping by example. For each scenario:
1. Understand the landscape (the map)
2. Identify the climatic patterns at work
3. Identify the gameplay available to each player
4. Analyze what happened or what should happen

## Scenario 1: The Kodak Story

### The Landscape (circa 1990)
Kodak's value chain:
```
[Consumer]
    │
[Memories/Photos]
    │
[Photo Processing Service]──[Film Camera]
    │                              │
[Film Processing Lab]         [Photographic Film]
    │                              │
[Chemicals & Equipment]       [Silver Halide Chemistry]
```

At this time:
- Film camera: Product stage (Kodak dominant)
- Photographic film: Product → Commodity
- Photo processing: Product (Kodak owned many labs)

### The Climatic Pattern
Digital imaging existed at Genesis/Custom stage since the 1970s. Kodak's own scientists invented the digital camera in 1975.

**What the map showed:**
- Digital sensors would evolve from Custom → Product → Commodity
- When they did, the entire chemical film chain would become obsolete
- The user need (memories/photos) remained constant — the components serving it were changing

### The Gameplay Available to Kodak
1. **Accelerate the transition**: Own the digital photography space before competitors
2. **Platform play**: Become the platform for digital photo sharing/printing
3. **Harvest and exit**: Maximize returns from film while building a new business
4. **Defend**: Protect the film business (chosen option)

### What Happened
Kodak chose to defend. Reasons:
- Film was 70%+ gross margins; digital cameras had thin margins
- Film processing labs were billion-dollar investments
- Sales team was incentivized on film sales
- Management believed "digital is a complement, not a replacement"

**Inertia factors:**
- Financial: Film margins funded everything
- Organizational: Entire business built around chemical processes
- Cultural: Kodak's identity was film photography

**Result**: Kodak filed for bankruptcy in 2012. Digital photography commoditized the entire value chain below photo sharing.

**Lesson**: The map showed the future clearly. Inertia prevented action.

## Scenario 2: Amazon Web Services

### The Landscape (circa 2003)
Amazon needed to build reliable, scalable infrastructure for amazon.com. They built it:
```
[Amazon Retail Customers]
    │
[Product Catalog & Purchase Experience]
    │
[Order Management]──[Inventory]
    │
[Compute Infrastructure]──[Storage]──[Database]
    │
[Physical Servers]──[Networking]──[Power]
```

### The Insight
Amazon's engineering team noticed:
- They had built reliable, scalable compute at Custom stage
- Every other company was building the same components at Custom stage
- They were building it better (because their scale forced better solutions)

**The map showed**: Compute was evolving toward commodity. Amazon had a head start.

### The Gameplay
**Commoditize a complement + ecosystem play:**
1. Build the commodity compute utility (AWS)
2. Offer it to everyone, not just amazon.com
3. Use ILC: Let others build on top of AWS; observe what they build; commoditize the most valuable services
4. Create ecosystem lock-in through data, tooling, and network effects

### The Execution
- 2006: AWS launches with S3 (storage) and EC2 (compute)
- 2007–2010: Developer adoption accelerates; the ecosystem grows
- 2012–2015: AWS adds dozens of services (observing what developers built and commoditizing it)
- 2015–2020: AWS becomes the dominant cloud platform; AWS revenue dwarfs Amazon Retail operating income

### What Competitors Did Wrong
- Microsoft: Held back Azure to protect Windows Server licensing (inertia)
- Oracle: Refused to support cloud databases that competed with their core product (inertia)
- IBM: Built Softlayer as a hosting service, not understanding the utility model

**Lesson**: The gameplay was visible to anyone who mapped the landscape. The winners were those without the inertia to act.

## Scenario 3: The Taxi Industry vs. Uber

### The Pre-Uber Landscape
```
[Passenger]
    │
[Transportation Service]
    │
[Dispatcher]──[Licensed Driver]──[Licensed Vehicle]
    │
[Radio Communication System]
```

- Licensed driver + vehicle: Custom (scarce, regulated)
- Radio dispatch: Custom → Product
- Transportation service: Product (taxis)

### The Climatic Pattern
- Smartphones: evolving from Custom → Product (2007–2012)
- GPS: Product → Commodity
- Payment processing: Product → Commodity
- Mapping data: Product → Commodity (Google Maps API)

### Uber's Map (circa 2009)
Uber looked at the same landscape and saw:
- The enabling components (smartphone, GPS, payment, maps) were all commoditizing
- When all four were commodity utilities, the dispatcher + licensed driver + licensed vehicle model could be disrupted
- The "moat" around taxis was regulatory, not technological

### The Gameplay
**Exploit commoditized components + exploit regulatory inertia:**
1. Build on top of commodity smartphone, GPS, payment, and maps
2. Create a platform connecting drivers and passengers directly (eliminating dispatcher)
3. Use regulatory arbitrage — move faster than regulators can respond
4. Network effects: more drivers → faster pickups → more customers → more drivers

### Taxi Industry Response
The taxi industry tried to use regulatory defense (a classic incumbent move). It worked in some cities and failed in others.

**Why regulatory defense failed in most places:**
- Uber's user experience was dramatically better (Doctrine: focus on user needs)
- Regulatory capture was inconsistent across cities
- The underlying technology couldn't be un-invented

**Lesson**: When multiple enabling components commoditize simultaneously, disruption is fast and wide. The incumbent's inertia (regulatory licenses, physical infrastructure, dispatch systems) was their doom, not their protection.

## Scenario 4: Enterprise Software

### The SAP/Oracle Landscape (circa 2005)
```
[Enterprise Customer (CFO)]
    │
[Financial Reporting]──[ERP Processes]
    │
[SAP/Oracle Software]
    │
[On-Premise Servers]──[Database]──[Integration Layer]
    │
[Hardware]──[Network]──[Power]
```

- SAP/Oracle software: Product (dominant, high margins)
- On-premise infrastructure: Custom → Product
- Integration: Custom (extremely expensive and sticky)

### The Evolution
- Cloud compute: Commodity (2010+)
- SaaS delivery model: Product → Commodity (Salesforce pioneered)
- Modern databases: Product → Commodity

### New Map (2010–2020)
The landscape redrawn:
- Workday replaces SAP HR on cloud infrastructure
- Salesforce commoditizes CRM
- Coupa/Ariba compete on procurement
- ServiceNow commoditizes ITSM

**The climatic pattern**: Each SaaS vendor is commoditizing a previously Custom/Product component of the SAP/Oracle bundle.

### The Gameplay
**Unbundle + commoditize:** Attack individual components of the bundle rather than the whole. Each specialist SaaS player is more focused than SAP/Oracle can be.

**SAP/Oracle inertia:**
- Existing customer base paying maintenance fees (financial inertia)
- On-premise integration that took years to build (customer inertia)
- Sales force compensated on license deals (organizational inertia)
- "Your data is safer on-premise" narrative (cultural inertia)

**Result**: SAP and Oracle are adapting but from a position of constant catch-up. Their margins are compressed; their maintenance revenue is declining.

## Applying the Scenario Approach to Your Own Context

### Step 1: Map the Current Landscape
Draw your actual value chain. Be honest about where components sit evolutionarily.

### Step 2: Identify Climatic Patterns in Play
- What is currently evolving in your landscape?
- What is at the Custom→Product transition (commoditizing in 2–5 years)?
- Where do competitors have high inertia?

### Step 3: Identify Available Gameplay
Given the map, what moves are available?
- Attack competitor inertia?
- Open source a component?
- Build on top of a commoditizing component?
- Ecosystem play?

### Step 4: Model the Future Landscape
Draw the map as it will likely look in 3–5 years based on the climatic patterns.

### Step 5: Work Backward
Given the future map, what needs to happen now?
- What capabilities need to be built?
- What investments need to be made?
- What needs to be stopped?

## The Scenario Planning Framework

For each scenario, structure your analysis:

| Element | Questions |
|---------|---------|
| **Current landscape** | Where is everything on the map? |
| **Climatic patterns** | What is evolving, and in which direction? |
| **Inertia** | Where are the incumbents most stuck? |
| **Gameplay** | What moves are available? |
| **Counter-moves** | How will competitors respond? |
| **Timing** | When should you act? |
| **Risk** | What could go wrong with this analysis? |
