# Better for Less — Efficiency, Government, and the Public Sector

Reference for applying Wardley Mapping to efficiency drives, government contexts, and better-for-less strategies.

## The Efficiency Opportunity

Wardley Mapping's most concrete near-term benefit is often identifying efficiency opportunities: places where organizations are spending money building commodity components that should be bought or rented.

The "better for less" imperative: deliver better outcomes while spending less, by:
1. Eliminating waste (building what should be bought)
2. Removing duplication (many teams building the same component)
3. Using evolution to guide build/buy decisions
4. Freeing resources for actual differentiation

## The Waste Map

### Finding Waste with Maps
When you map your value chain, waste becomes visible:

**Type 1 Waste: Building Commodities**
Components at Product or Commodity stage that you're building as Custom:
- Internal email systems (should use Gmail/Outlook)
- Custom CRM (should use Salesforce or equivalent)
- Bespoke logging infrastructure (should use Datadog/Splunk)
- Hand-rolled authentication (should use Cognito/Auth0)

**Cost**: Typically 5–20x the cost of the commodity alternative, plus ongoing maintenance burden.

**How to find it**: For every custom-built component on your map, ask "could I buy or rent this?"

**Type 2 Waste: Duplication**
Multiple teams building the same component:
- 15 different authentication systems across 15 business units
- 6 different deployment pipelines
- 4 different analytics platforms

**Cost**: N × the cost of one solution, plus integration overhead, plus inconsistent security/reliability.

**How to find it**: Compare maps across teams/divisions. Identical components should appear only once.

**Type 3 Waste: Misapplied Effort**
Applying premium engineering talent to commodity components:
- Senior engineers maintaining legacy systems that should be modernized
- PhD data scientists building rule-based systems when ML libraries exist
- Architecture teams designing infrastructure that cloud providers have commoditized

**Cost**: Opportunity cost — those people could be building differentiating capabilities.

## The Build/Buy/Outsource Decision Framework

Maps make build/buy/outsource decisions explicit:

| Evolutionary Stage | Default Decision | Exception |
|-------------------|-----------------|-----------|
| **Genesis** | Build (nobody else has it) | Buy if pioneer startup has it |
| **Custom** | Build or buy from specialists | Outsource if not strategic |
| **Product** | Buy (usually) | Build if it's your core differentiator |
| **Commodity** | Buy/Rent/Consume as utility | Never build (almost never) |

### The Strategic Importance Modifier
Even at Commodity stage, you might build if the component is:
- Core to your competitive position
- Not available at sufficient quality/scale
- Subject to regulatory requirements that commodities don't meet

But be honest: most organizations over-classify components as "strategically important" to justify building them. Map review helps challenge this.

### The "Never Build This" List
Components that should never be built:
- Email infrastructure
- Basic authentication/identity
- Standard payment processing
- Network infrastructure
- Standard logging and monitoring
- Basic cloud compute/storage
- Standard CI/CD tooling
- Common security tools (firewalls, antivirus)

Every dollar spent building these is a dollar not spent on genuine differentiation.

## Applying Maps to Cost Reduction

### The Efficiency Map Review Process
1. Create or review your current state map
2. Identify all Custom-built components
3. For each Custom-built component, ask: "what evolutionary stage is this really at?"
4. For components that are actually Product or Commodity, estimate the cost difference
5. Prioritize migration based on cost difference and migration complexity

### The Portfolio Rationalization
Use maps to rationalize technology portfolios:
- Map all existing systems and components
- Identify evolutionary stage of each
- Identify which serve the same user need (candidates for consolidation)
- Identify which can be replaced by commodity alternatives

Government agencies that have done this exercise typically find they have dozens of overlapping systems serving similar purposes — all being maintained as Custom when commodity alternatives exist.

## Wardley Mapping in Government

### Why Government is Different
Government organizations differ from commercial enterprises in important ways:
- **No market exit**: Failed government services cannot simply be shut down
- **Regulatory constraints**: Many decisions require legislative or regulatory approval
- **Monopoly provision**: Often no competitive pressure driving efficiency
- **Political timescales**: Investment decisions made on 4–5 year political cycles, not 1–2 year commercial cycles
- **Multiple principals**: Serve citizens, elected officials, regulators, other departments simultaneously
- **Risk aversion**: Failure has political consequences; this creates extreme inertia

### What the Map Tells Government
A government technology map typically shows:
- Many components at Custom stage that commercial equivalents are at Commodity
- Heavy duplication across departments
- Significant lock-in to legacy vendors
- Long tail of small, expensive custom systems

### The GDS (Government Digital Service) Example
The UK's GDS applied mapping-informed thinking to government IT:
1. Mapped government services and their underlying components
2. Found massive duplication across departments
3. Created shared commodity components (Government as a Platform)
4. GOV.UK: single, commodity-quality web presence replacing thousands of departmental sites
5. GovNotify, Pay, Verify: shared commodity components replacing N custom implementations

**Results**: Significantly lower cost per service, dramatically better user experience, faster delivery.

### The Government Inertia Problem
Government has all the same inertia as commercial organizations, plus:
- **Procurement inertia**: Existing vendor relationships and frameworks
- **Political inertia**: Ministers invested in announcing projects
- **Departmental inertia**: Each department protects its own systems
- **Skills inertia**: Civil service skills built around managing (not building) technology

**Map insight**: Government's inertia is especially dense in IT because:
- IT is not the core function of government
- Technology decisions are made by people without technology background
- Long contracts lock in approaches for 5–10 years

### Applying PST to Government
Government IT historically runs almost entirely as Custom/Product work with Town Planner governance applied to everything — including the work that needs Pioneer approaches:
- New services need Pioneer exploration (experimentation, failure tolerance)
- Get governed as Town Planner projects (requirements documents, committees, sign-offs)
- Result: innovation is stifled; commodity thinking is applied to non-commodity work

**The fix**: Create explicit spaces for Pioneer work within government (innovation labs, digital transformation units) and protect them from standard procurement and governance.

## The Efficiency Investment Paradox

Sometimes investing more now saves more later:

### The Commoditization Investment
Spending £X to move a Custom component to commodity saves £Y per year forever:
- One-time cost: migration and transition
- Ongoing saving: commodity service vs. custom maintenance

**Map-based calculation:**
- Current cost of custom: £500k/year
- Commodity alternative: £50k/year
- Migration cost: £200k
- Payback period: <6 months

This is almost always the right investment — but requires overcoming the inertia of the team that owns the custom component.

### The Shared Service Investment
Building one good shared component costs N × the cost of N bad custom versions:
- 10 departments each running custom authentication: 10 × £200k = £2M/year
- One shared commodity authentication service: £300k/year + £500k build
- Savings: £1.7M/year after Year 1

The math is simple. The politics are hard.

## The "Better for Less" Roadmap

Using maps to create a prioritized efficiency roadmap:

1. **Inventory** (map everything): Know what you have
2. **Classify** (evolution stage): Know where each thing is
3. **Identify waste** (commodity built as custom, duplication): Know where to save
4. **Quantify** (cost of current vs. commodity alternative): Know how much to save
5. **Prioritize** (by savings ÷ complexity of change): Know what to do first
6. **Plan transitions** (manage inertia): Know how to do it
7. **Reinvest savings** (into genuine differentiation): Know what to do with the savings
