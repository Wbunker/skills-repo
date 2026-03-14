# To Infinity and Beyond — Evolution of Practices and Appropriate Methods

Reference for how management practices evolve alongside technology, and choosing the right method for the right evolutionary stage.

## The Central Problem: No Universal Method Works

Every management methodology has advocates who claim universal applicability:
- "Agile works for everything"
- "Lean is the answer"
- "Six Sigma solves all quality problems"
- "OKRs fix all alignment problems"

Maps reveal why this is wrong: **the appropriate method depends on the evolutionary stage of the work**.

## The Methods Matrix

Different evolutionary stages require fundamentally different approaches:

| Stage | Appropriate Methods | Inappropriate Methods |
|-------|--------------------|-----------------------|
| **Genesis** | Agile, Lean Startup, FIRE, experimentation | Six Sigma, Prince2, detailed specs |
| **Custom** | Agile, skilled craftsmanship, iterative | Lean Startup (too exploratory), Six Sigma |
| **Product** | Agile, Scrum, product management practices | Six Sigma (too rigid), complete agility |
| **Commodity** | Six Sigma, ITIL, Lean Operations, SRE | Agile (too unstructured for reliability) |

### Why Applying the Wrong Method Fails

**Applying Agile to Commodity Operations:**
- Agile assumes change and experimentation are valuable
- Commodity operations need stability and predictability
- Agile-managed power plants would be terrifying
- Agile-managed financial settlement systems would be unstable

**Applying Six Sigma to Genesis Work:**
- Six Sigma assumes you know what good looks like (you're reducing variance)
- Genesis work is about discovering what good looks like
- Six Sigma kills the experimentation that genesis requires
- The very unpredictability of genesis work is a signal you're doing it right

**Applying ITIL to Product Development:**
- ITIL was designed for commodity IT service management
- Applied to product development, it creates bureaucratic overhead
- Change management processes slow innovation velocity

## The Practice Evolution Chart

Management practices themselves evolve on the same axis:

### Genesis Practices (Novel, Emerging)
- Practices for new, experimental work
- Often ad hoc, poorly documented, not widely taught
- High variance in quality
- Examples: early CI/CD (2008), early Agile (1995), early SRE (2000s)

### Custom Practices (Specialist, Skill-Based)
- Better defined but still requires expertise to apply
- Not yet packaged as a product
- Significant variation in how different organizations implement
- Examples: DevOps (2010s), modern SRE, Platform Engineering (now)

### Product Practices (Packaged, Teachable)
- Defined frameworks, certifications, books
- Can be trained and implemented at scale
- Still some differentiation between good and bad implementations
- Examples: Scrum, SAFe, ITIL v3, ISO standards

### Commodity Practices (Table Stakes, Universal)
- Everyone does it; not doing it is a failure
- No competitive advantage from adoption
- Advantage comes from how well you implement it
- Examples: Source control (Git), basic security practices, continuous integration basics

## Wardley's Six Types of Management Doctrine

Wardley categorizes management approaches by the type of uncertainty they're designed for:

### 1. Exploration (Genesis)
**For**: Finding new things that work in uncertain territory
**Methods**: Lean Startup, FIRE, A/B testing, prototyping
**Focus**: Learning and discovery
**Failure mode**: Not failing fast enough; spending too long on things that don't work

### 2. Agility (Custom)
**For**: Building things you understand but haven't built before
**Methods**: Agile, Scrum, XP
**Focus**: Rapid iteration, responding to change
**Failure mode**: Scope creep, velocity without direction

### 3. Lean (Product)
**For**: Improving efficiency of known processes
**Methods**: Lean, Kanban, flow optimization
**Focus**: Waste elimination, flow efficiency
**Failure mode**: Optimizing the wrong thing

### 4. Six Sigma (Commodity)
**For**: Reducing variance in well-understood processes
**Methods**: Six Sigma, DMAIC, statistical process control
**Focus**: Defect reduction, consistency
**Failure mode**: Applied to processes that aren't yet understood

### 5. Resilience Engineering (Commodity Infrastructure)
**For**: Maintaining reliability in complex, interconnected systems
**Methods**: SRE, chaos engineering, blameless post-mortems
**Focus**: Learning from failures before they cause outages
**Failure mode**: False security from compliance without actual resilience

### 6. Governance (All Stages)
**For**: Alignment between teams and organizational goals
**Methods**: OKRs, strategic alignment processes
**Focus**: Ensuring autonomy without chaos
**Failure mode**: Treating governance as control rather than alignment

## The Method Selection Framework

When choosing a method, ask:

### Step 1: What stage is this work in?
Use the evolution axis to categorize the work.

### Step 2: What type of uncertainty am I dealing with?
| Uncertainty Type | Appropriate Approach |
|-----------------|---------------------|
| **What to build** (unknowns unknown) | Exploration |
| **How to build well** (known unknowns) | Agility |
| **How to build efficiently** (known knowns) | Lean |
| **How to build consistently** (minimize variance) | Six Sigma |

### Step 3: What does success look like here?
- If success = learning → exploration methods
- If success = shipping → agility methods
- If success = throughput → lean methods
- If success = reliability → six sigma / SRE methods

### Step 4: What failure modes does this method have?
All methods have blind spots. Know them before applying.

## The Continuous Delivery Evolution

Continuous delivery (CD) illustrates practice evolution perfectly:

**2005**: CD is Genesis — a few Google/Amazon engineers experimenting with deploying many times per day.

**2010**: CD is Custom — ThoughtWorks consulting on it; Jez Humble's book published; requires skilled specialists.

**2015**: CD is Product — Jenkins, CircleCI, Travis CI; packaged tools; CTO blogs about it.

**2020**: CD is transitioning to Commodity — GitHub Actions, built-in to most platforms; not doing it is unusual.

**2024**: Basic CI/CD is Commodity; advanced deployment practices (feature flags, progressive delivery) are Product → Commodity.

The appropriate management response to CD has changed at each stage:
- 2005: Experiment, fail, learn
- 2010: Hire specialists, invest in tools
- 2015: Choose a product, implement it
- 2020: Just use what's in your platform; focus energy elsewhere

## The Anti-Pattern: Method Cargo Culting

Organizations observe successful companies using a method and copy the method without understanding the landscape that made the method appropriate.

**Example**: Company A succeeds with aggressive experimentation culture. Company B copies the "experimentation culture." But Company B's core product is commodity infrastructure (stability and reliability matter most). The experimentation culture creates instability and unpredictability.

**The fix**: Map the landscape first. Ask "are we in the same evolutionary stage as the company we're copying?"

## Mixing Methods

Advanced organizations run multiple methods simultaneously:
- R&D: Exploration/Lean Startup
- Product development: Agile/Scrum
- Platform operations: Lean + SRE
- Core commodity infrastructure: Six Sigma + ITIL

The challenge is managing the interfaces between these different modes without creating friction or confusion.

**Solution**: Make the method zones explicit. Show on the org chart which teams use which methods and why. Don't pretend one method works everywhere.

## Organizational Implications

### Hiring for Methods
Hire people who are comfortable with the methods appropriate for their role:
- Pioneers need comfort with ambiguity and failure
- Product engineers need agility and communication skills
- Platform engineers need reliability engineering mindset
- Infrastructure specialists need operational discipline

Hiring a pioneer mindset for commodity operations creates suffering for the person and unreliability for the system.

### Training for Methods
Train people in the methods appropriate for their current work. Don't train your entire organization in Agile if half of them run commodity infrastructure.

### Metrics Aligned to Methods
- Exploration: experiments run, learnings per sprint, pivot speed
- Agility: velocity, lead time, deployment frequency
- Lean: flow efficiency, cycle time, WIP
- Six Sigma: defect rate, variance, MTBF
