# A Smorgasbord of the Slightly Useful — Additional Patterns and Tools

Reference for supplementary Wardley Mapping patterns, anti-patterns, and practical tools beyond the core framework.

## Additional Mapping Patterns

### The Reverse Sadie Hawkins
**Problem**: A component you depend on (at the bottom of your value chain) is about to be commoditized by someone else — turning your custom-built advantage into a commodity burden.

**Response**: Either:
1. Accelerate the commoditization yourself (own the transition)
2. Build your moat higher up the value chain before the bottom commoditizes
3. Use the commodity faster than competitors (first-mover on the evolved form)

### The Fool's Gold
**Problem**: A component appears to be at genesis (exciting, novel) but is actually at Product and heading to Commodity. You're about to invest in something that will be commodity in 2 years.

**Signal**: Multiple startups working on the same thing; VC money flowing in; rapid feature parity among competitors.

**Response**: Don't build — buy or rent. The "exciting new thing" is already commoditizing.

### The Hidden Dependency
**Problem**: Your map looks solid, but there's a critical dependency you haven't mapped that is actually at Genesis or Custom — fragile and expensive.

**Example**: Your product depends on a third-party API that is still in beta (Genesis) even though you're treating it as a reliable component.

**Response**: Audit your value chain for hidden dependencies. Map them. Identify fragile points.

### The Obsolete Anchor
**Problem**: A component on your map was once important but is now a commodity that everyone uses. You're still treating it as a differentiator and spending resources on it.

**Example**: Building a custom email system in 2020.

**Response**: Move to the commodity version; redirect resources to actual differentiators.

### The Position Trap
**Problem**: You've optimized your organization around a component's current position, but it's about to move. Your structure will be wrong before you know it.

**Example**: Building a team of 50 specialists in a technology that is about to become automated.

**Response**: Monitor evolution of all critical components; build adaptability into team structures.

## The Value Chain as a Weapon

### Constraining Competitors Through Value Chain Position
If you control a critical component in your competitors' value chains, you have significant leverage:

**Types of leverage:**
1. **Pricing leverage**: Raise the cost of a component your competitor needs
2. **Feature leverage**: Add features your competitor cannot match without your component
3. **Timing leverage**: Release capabilities before competitors can access them
4. **Ecosystem leverage**: Build dependencies in your customers' systems

**Warning**: This only works if you genuinely own a non-commodity component. Commodity components cannot be weaponized — too many alternatives exist.

### The Open Source Weapon
Commoditize a component your competitor depends on by open-sourcing your version:
- Destroys their revenue stream
- Accelerates evolution past their position
- Positions you to profit from the evolved layer above

**Classic example**: Google open-sourcing Android → Commoditized the mobile OS → Destroyed Nokia/BlackBerry's OS advantage → Ensured Google services ran on all devices.

## Mapping Data

### Data as a Component
Data belongs on maps. It has an evolutionary axis:

| Stage | Data Characteristics |
|-------|---------------------|
| Genesis | Raw, unstructured, no clear value |
| Custom | Cleaned, analyzed, some value |
| Product | Productized data products, APIs |
| Commodity | Open data, data utilities |

### Data Gravity
Large datasets are hard to move. This creates competitive advantage:
- If your platform accumulates customer data, competitors cannot easily replicate that dataset
- "Data gravity" means other services cluster around large data stores
- This is a form of inertia that can be advantageous (if you're the one with the data)

### The Data Value Chain
Map your data flows as carefully as your activity flows:
- Where does data enter your system?
- How is it transformed?
- Where does it create value?
- Who depends on your data?
- What data do you depend on?

## Mapping Practices

### Practices on the Evolution Axis
Practices (ways of working) are components too:

| Practice | Current Stage |
|----------|--------------|
| Agile | Commodity (everyone does it; it's table stakes) |
| DevOps | Product → Commodity transition |
| Platform Engineering | Custom → Product |
| SRE | Custom → Product |
| FinOps | Custom → Product |
| Chaos Engineering | Custom |
| DataOps | Genesis → Custom |

### The Practice Paradox
- A practice that is genuinely good will eventually be copied by everyone
- Once everyone does it, it's no longer a differentiator
- You must continuously evolve your practices to stay ahead

**Implication**: Never confuse "we use agile" with "we are good at execution." Agile is a commodity practice — your advantage comes from what you do with it.

## Mapping Knowledge

### Knowledge as a Component
Organizational knowledge has an evolutionary axis too:
- Genesis: Novel understanding that few people have
- Custom: Specialist knowledge available through expert consultants
- Product: Available through books, courses, certifications
- Commodity: Widely known, freely available, table stakes

### The Knowledge Advantage Window
When you have Genesis-stage knowledge, you have a temporary advantage. Plan for how to use it before it commoditizes:
1. Build products/services that exploit the knowledge
2. Publish (to establish thought leadership, attract talent)
3. Create curriculum (build ecosystem of practitioners who depend on your framework)
4. Develop proprietary data based on the knowledge (lasting advantage even after knowledge commoditizes)

## Anti-Patterns

### Anti-Pattern 1: The Swiss Army Knife Map
**Problem**: Trying to use a single map for too many purposes simultaneously.
**Fix**: Create purpose-specific maps. One map for competitive analysis; another for build/buy decisions; another for organizational design.

### Anti-Pattern 2: Mapping What Should Exist, Not What Does
**Problem**: Creating an aspirational map instead of mapping current reality.
**Fix**: Map current state first, always. Then map desired future state separately.

### Anti-Pattern 3: The Consultant's Map
**Problem**: Creating elaborate maps that look impressive but are not used for decisions.
**Fix**: Every map should inform at least one concrete decision. If it doesn't, you're map-making for its own sake.

### Anti-Pattern 4: The Consensus Paralysis
**Problem**: Requiring everyone to agree on component positions before acting.
**Fix**: Accept good-enough maps. The map is a thinking tool, not a document requiring sign-off.

### Anti-Pattern 5: Mapping in Isolation
**Problem**: One person creates a map without input from those who actually know the landscape.
**Fix**: Maps should be created collaboratively, especially for the first version.

## Useful Heuristics

### The 10x Rule
A component becomes a commodity candidate when the best commercial option is 10x cheaper or faster than building it yourself.

### The "Why Would You Build That?" Test
If more than 3 commercially viable alternatives exist for a component, you should be buying, not building.

### The Evolution Speed Indicator
Rough evolution speed indicators:
- Software: Fast (5–15 years from genesis to commodity)
- Business practices: Medium (10–20 years)
- Physical infrastructure: Slow (20–50 years)
- Regulation: Very slow (50+ years, if ever)

### The Differentiation Filter
For every component you're considering investing in, ask:
1. Does this component directly deliver value to users? (If yes: worth investment)
2. Can this component be the basis of competitive advantage? (If yes: worth investment)
3. Is this component heading toward commodity? (If yes and to both above: build a moat now; harvest later)

## The Relationship Between Maps and Business Models

Maps reveal whether a business model is sustainable:
- If your revenue depends on a component that is commoditizing, your business model has a finite life
- If your revenue depends on being the best at operating a commodity, you're competing on efficiency (thin margins, volume)
- If your revenue depends on Genesis/Custom components, you have pricing power (but also risk)

Use maps to evaluate business model resilience:
- How much of your revenue is from components that are commoditizing?
- What is your plan when those components reach commodity?
- Where will your next Genesis-stage advantage come from?
