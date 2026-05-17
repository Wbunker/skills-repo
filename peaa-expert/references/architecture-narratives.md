# Architecture Narratives — PEAA Part 1

## Chapter 1: Layering

Layering is the primary architectural technique in enterprise applications. Each layer has a distinct responsibility and depends only on layers below it.

**Classic 3-Layer Architecture**
1. **Presentation** — UI logic, HTTP handling, HTML rendering
2. **Domain** — Business rules, validations, calculations
3. **Data Source** — DB interaction, messaging, external services

**Benefits**
- Each layer can be understood without knowing the others
- Layers can be swapped (e.g., replace UI without touching domain)
- Reduces dependencies; layers form natural subsystems

**Costs**
- Cascading changes when behavior spans layers
- Performance overhead from layer traversal
- Risk of anemic layers (logic leaks up/down)

**Fowler's Guidance**
- Keep domain logic in the domain layer, not in SQL procedures or UI controllers
- Don't skip layers — the discipline is the benefit
- "The domain layer is the heart of the system"

---

## Chapter 2: Organizing Domain Logic

Three primary approaches to organizing domain logic, reflecting different amounts of OO modeling:

### Transaction Script
Business logic organized as a set of procedures, one per user transaction or system operation. Each script coordinates inputs, executes logic, and writes results.

- **When to use**: Simple domains; CRUD-heavy applications; small teams; quick time-to-market
- **Risk**: Duplication grows as domain grows; logic scattered across scripts
- **Works well with**: Table Data Gateway, Row Data Gateway

### Domain Model
An object model of the domain incorporating both data and behavior. Objects collaborate to execute business rules.

- **When to use**: Complex business rules; rich domain concepts; long-lived applications
- **Requires**: Data Mapper for persistence independence (usually); ORM framework
- **Risk**: Higher upfront complexity; O/R impedance mismatch

### Table Module
A single object handles all business logic for all rows in a database table. Usually works with a Record Set.

- **When to use**: Moderate complexity; table-centric thinking; systems built on Record Set infrastructure (COM+, .NET DataSet)
- **Trade-off**: Less expressive than Domain Model for complex relationships; simpler than Domain Model setup

### Service Layer
A boundary layer that defines application operations, coordinates domain objects, and manages transactions. Not a substitute for domain logic — it delegates to domain objects.

- **When to use**: Multiple client types (web UI + API + batch); transaction demarcation needs
- **Pattern**: Thin service methods that delegate to domain objects vs. thick "script-style" services
- **Fowler's advice**: Prefer thinner service layer; push logic into domain objects

---

## Chapter 3: Mapping to Relational Databases

The O/R impedance mismatch is the central challenge. Key decisions:

### Architectural Patterns for Data Source
- **Table Data Gateway** — best with Transaction Script / Table Module; one gateway per table
- **Row Data Gateway** — one object per row; good with Transaction Script
- **Active Record** — one class per table; mixes data access and domain logic; good for simple Domain Model
- **Data Mapper** — full separation; best for rich Domain Model; most complex

### Behavioral Issues
- **Unit of Work**: Track all changes in a transaction; flush at commit. Avoids double writes and missed writes.
- **Identity Map**: Cache loaded objects by primary key. Prevents loading the same row twice, ensures object identity.
- **Lazy Load**: Defer loading associated objects until accessed. Four implementations: Lazy Initialization, Virtual Proxy, Value Holder, Ghost.

### Structural Mapping
- **Identity Field**: Store DB primary key in domain object
- **Foreign Key Mapping**: Association → foreign key column
- **Association Table Mapping**: Many-to-many → link table
- **Dependent Mapping**: Parent object maps its dependent child
- **Embedded Value**: Value Object stored in parent's columns
- **Serialized LOB**: Object graph serialized to BLOB/CLOB — simple but opaque to SQL

### Inheritance Mapping
Three approaches, each with trade-offs:

| Strategy | Table structure | SQL simplicity | Normalization |
|---|---|---|---|
| Single Table Inheritance | One table, all classes | Simple queries | Poor; many nulls |
| Class Table Inheritance | One table per class in hierarchy | Joins needed | Good |
| Concrete Table Inheritance | One table per concrete class | No joins for leaf queries | Duplication |

**Fowler's default**: Single Table Inheritance for simple hierarchies; Class Table Inheritance when normalization matters.

### Metadata Mapping
Drive O/R mapping via configuration (XML, annotations) instead of hand-coded mapper methods. Enables generic mapping code; foundation for ORMs.

- **Query Object**: Programmatic query construction; translates to SQL at runtime
- **Repository**: Collection-like interface to domain objects; encapsulates query construction; preferred for Domain Model

---

## Chapter 4: Web Presentation

Core responsibility: receive HTTP request, invoke domain logic, produce HTTP response (usually HTML).

### MVC Separation
Always separate **Model** (domain), **View** (rendering), **Controller** (input handling). Never put domain logic in views or controllers.

### Input Controller Patterns
- **Page Controller**: One controller per page/action. Simple; easy to understand. Preferred for most sites.
- **Front Controller**: Single entry point; dispatches to handlers. Better when navigation logic is complex or many cross-cutting concerns exist (auth, logging).

### View Patterns
- **Template View**: HTML with embedded markers/tags (JSP, Thymeleaf, Razor). Most common; risk of logic creep into templates.
- **Transform View**: XSLT-style transformation from domain XML to HTML. Good for multiple output formats.
- **Two Step View**: Step 1 — domain data → logical page structure; Step 2 — logical page → HTML. Enables consistent site-wide rendering changes in one place.

### Application Controller
Handles screen flow and application state (wizards, multi-step forms, workflow screens). Separates navigation logic from page controllers.

---

## Chapter 5: Concurrency

Enterprise applications face two kinds of concurrency: **system transactions** (DB-level) and **business transactions** (multi-request user sessions).

### System Transaction Isolation
Standard DB transaction isolation levels (read uncommitted → serializable). Higher isolation = fewer anomalies, more contention.

### Business Transaction Concurrency
User sessions span multiple HTTP requests but cannot hold a DB transaction open that long. Two strategies:

- **Optimistic Offline Lock**: Allow concurrent editing; detect conflict at save time (compare version stamp). Good for low-conflict scenarios.
- **Pessimistic Offline Lock**: Acquire a lock before editing; prevent conflicts. Good for high-conflict or costly-conflict scenarios.
- **Coarse-Grained Lock**: Lock a cluster of related objects (e.g., Customer + all Addresses) with one lock.
- **Implicit Lock**: Framework or base class acquires locks automatically; prevents forgetting to lock.

### Patterns for Consistency
- Version number / timestamp on each record (Optimistic)
- Lock table with lock owner + expiry (Pessimistic)
- Always prefer Optimistic when conflicts are rare; Pessimistic when conflicts are common or correction cost is high

---

## Chapter 6: Session State

HTTP is stateless. Three places to store conversational state:

| Pattern | Storage | Scalability | DB load |
|---|---|---|---|
| Client Session State | Cookie / hidden field / URL | High (no server state) | None |
| Server Session State | Server memory / serialized | Medium (sticky sessions or distributed cache) | Low |
| Database Session State | DB table | High | Higher |

**Fowler's guidance**:
- Client Session State: simple, but limited size; security risk if unencrypted
- Server Session State: familiar, but clustering is hard
- Database Session State: most robust for clustering; adds DB load; prefer committed data over pending

**Stateless server preference**: Push toward stateless by passing session context explicitly or keeping state in the database.

---

## Chapter 7: Distribution Strategies

**The fundamental rule**: Don't distribute. A single process is vastly simpler than a distributed system.

When distribution is unavoidable (different security domains, teams, deployment units):

- **Minimize remote calls**: Network round-trips dominate performance. Batch data into coarse calls.
- **Remote Facade**: Present a coarse-grained interface to a fine-grained domain model. Clients call few, chunky remote methods; the facade delegates to domain objects.
- **Data Transfer Object**: Carry data between processes in one object. Serialize entire graphs; avoid chatty interfaces.

**Do not use a distributed object design** (many fine-grained remote objects). This was a major architectural mistake of the EJB era.

**When to distribute**:
- Different deployment units with different release cycles
- Different security domains (e.g., DMZ)
- True physical separation requirement

**Prefer**: Monolith with in-process calls; distribute only at explicit system boundaries.

---

## Chapter 8: Putting It All Together

Fowler's guidance for choosing patterns:

### Starting Point Decision Tree
1. **How complex is the domain logic?**
   - Simple → Transaction Script
   - Moderate → Table Module (if tooling supports it) or Domain Model
   - Complex → Domain Model

2. **What data source pattern?**
   - Transaction Script → Table Data Gateway (one per table)
   - Table Module → Table Data Gateway
   - Domain Model (simple) → Active Record
   - Domain Model (complex) → Data Mapper

3. **What web presentation?**
   - Simple → Page Controller + Template View
   - Complex navigation → Front Controller
   - Multiple output formats → Transform View

4. **What session strategy?**
   - Stateless preferred; Client Session State for small data; Database Session State for clusters

5. **Distribution?**
   - Resist it. If needed: Remote Facade + Data Transfer Object at boundaries.

### Common Combinations
- **CRUD app**: Transaction Script + Table Data Gateway + Page Controller + Template View
- **Medium complexity**: Domain Model + Active Record + Page Controller + Template View
- **Rich domain**: Domain Model + Data Mapper + Repository + Service Layer + Front Controller
- **Legacy integration**: Remote Facade + Data Transfer Object at integration boundary
