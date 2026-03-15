# Business Metadata
## Chapters 3–4: Business Glossary, Data Dictionary, Taxonomies, Ontologies, KPIs

---

## What Is Business Metadata?

Business metadata captures the **meaning, context, and governance** of data from the business perspective. It answers:
- *What does this data element mean in our organization?*
- *Who is responsible for it?*
- *How should it be used (and not used)?*
- *How does it relate to other business concepts?*

Business metadata is the hardest to create (requires human expertise), the most valuable (enables data to be trustworthy and usable), and the most neglected (typically underfunded).

---

## Business Glossary

### Purpose
A **business glossary** is the authoritative vocabulary of the organization — the single source of truth for what business terms mean.

Distinction from data dictionary:
- **Business glossary**: Business concepts and their definitions (e.g., "Active Customer")
- **Data dictionary**: Technical data elements (columns, tables) with their specifications
- **Relationship**: Glossary terms link to data dictionary entries — bridging business meaning to technical reality

### Anatomy of a Glossary Term

| Attribute | Description | Example |
|-----------|-------------|---------|
| **Term name** | The official business name | "Active Customer" |
| **Definition** | Precise, unambiguous description | "A customer who has placed at least one order in the past 12 months" |
| **Synonyms** | Aliases used informally | "Engaged customer", "Current customer" |
| **Related terms** | Links to parent/child/sibling concepts | Related to: "Customer", "Churned Customer" |
| **Steward** | Person responsible for maintaining the term | Jane Smith, Head of CRM |
| **Owner** | Business unit that owns the definition | Sales Operations |
| **Status** | Lifecycle stage | Draft / Proposed / Approved / Deprecated |
| **Linked assets** | Data elements that implement this term | `fact_orders.customer_id` (where active = last 365 days) |
| **Examples** | Concrete instances that clarify meaning | "A customer who bought in March counts as active in March" |
| **Non-examples** | Clarify boundaries | "A customer with only a wishlist is NOT active" |
| **Usage notes** | Context and constraints on use | "Used in marketing segmentation; not used in finance reports" |
| **Effective date** | When this definition became official | 2024-01-01 |

### Glossary Design Principles

1. **One definition per term**: Ambiguity destroys trust. If two business units define "revenue" differently, establish which is the organization's official definition.
2. **Definitions, not descriptions**: "A customer who bought in the last 12 months" (definition) vs. "A customer we care about" (description). Definitions are testable.
3. **Stewardship is mandatory**: Every term must have a named steward who is accountable for its accuracy.
4. **Avoid circular definitions**: "Revenue is the revenue recognized" explains nothing.
5. **Link to data**: Unlinked glossary terms are documentation; linked terms are active governance.

### Term Lifecycle

```
Proposed ──► Under Review ──► Approved ──► Published
                                               │
                                         ┌─────┴─────┐
                                         │           │
                                    Updated      Deprecated
                                    (new version)  (replaced or
                                                    retired)
```

---

## Data Dictionary

### Purpose
A **data dictionary** documents technical data elements at the column/field level. It bridges business meaning to physical implementation.

### Anatomy of a Data Dictionary Entry

| Attribute | Description | Example |
|-----------|-------------|---------|
| **Element name** | Physical name | `order_total_usd` |
| **Display name** | Human-readable name | "Order Total (USD)" |
| **Data type** | Physical type | DECIMAL(18,2) |
| **Format** | Storage/display format | Currency, 2 decimal places |
| **Business term** | Linked glossary term | "Net Order Value" |
| **Definition** | What this field contains | "Sum of line item prices after discounts, before tax" |
| **Source** | Origin system | Salesforce.Opportunity.Amount |
| **Allowable values** | Constraints | > 0.00, not null for completed orders |
| **Transformation** | Derivation logic | `SUM(line_items.price * qty) - discount` |
| **Owner/steward** | Responsibility | Finance Data Steward |
| **Classification** | Sensitivity level | PII / Confidential / Public |
| **Retention** | How long to keep | 7 years (SOX compliance) |
| **Last verified** | Quality checkpoint | 2024-06-01 |

### Data Dictionary vs. Schema Registry

| Data Dictionary | Schema Registry |
|-----------------|-----------------|
| Human-centric documentation | Machine-readable schema definitions |
| Includes business context and rules | Focuses on format and structure |
| Maintained manually + automated | Typically automated |
| Used by data consumers | Used by data producers and platforms |
| Examples: Confluence pages, catalog entries | Examples: Confluent Schema Registry, AWS Glue Catalog |

---

## Taxonomies

### Definition
A **taxonomy** is a hierarchical classification scheme that organizes concepts into a structured tree.

```
Data Classification Taxonomy
├── Confidential
│   ├── Restricted
│   │   ├── PII (Personal Identifiable Information)
│   │   │   ├── Name
│   │   │   ├── SSN/National ID
│   │   │   └── Financial account
│   │   └── PHI (Protected Health Information)
│   └── Internal
│       ├── Financial data
│       └── Strategic plans
└── Public
    ├── Marketing materials
    └── Published reports
```

### Taxonomy Design Principles
- **Single inheritance**: Each node has exactly one parent (unlike ontologies)
- **Mutually exclusive**: Items belong to exactly one category at each level
- **Collectively exhaustive**: All relevant instances can be classified
- **Stable at top, flexible at bottom**: Top-level categories rarely change; leaf nodes evolve

### Common Business Taxonomies

| Taxonomy Type | Purpose | Example |
|---------------|---------|---------|
| **Data classification** | Security and access control | Public / Internal / Confidential / Restricted |
| **Subject area** | Organizing data assets by domain | Customer / Product / Finance / HR |
| **Business entity** | Classifying business objects | Party / Transaction / Location / Product |
| **Data sensitivity** | Regulatory compliance | PII / PHI / PCI / Non-sensitive |
| **Quality tier** | Data quality classification | Gold / Silver / Bronze |

---

## Ontologies

### Definition
An **ontology** extends taxonomy by adding rich relationships between concepts. Ontologies support complex semantic reasoning, not just hierarchical classification.

```
Taxonomy (IS-A only):          Ontology (multiple relationship types):

Customer                       Customer ──── PLACES ──── Order
  └── Active Customer            │                         │
  └── Churned Customer           IS-A                   CONTAINS
  └── Prospect                   │                         │
                               Person              Order Line Item
                                 │                         │
                               HAS                     REFERENCES
                                 │                         │
                               Address                  Product
```

### Ontology vs. Taxonomy

| Aspect | Taxonomy | Ontology |
|--------|----------|---------|
| Relationships | IS-A only | Multiple types (has, uses, produces, etc.) |
| Complexity | Simple hierarchy | Rich graph |
| Reasoning | Classification | Inference and deduction |
| Maintenance | Easier | More complex |
| Use cases | Classification, filtering | Semantic search, knowledge graphs |

### When to Use Each
- **Taxonomy**: Data classification, subject area organization, sensitivity labeling
- **Ontology**: Enterprise data models, knowledge graphs, complex regulatory domains (FIBO for finance, HL7 for healthcare)

---

## KPIs and Metric Definitions

### Why Metrics Are Business Metadata
KPI and metric definitions are critical business metadata because they encode business logic, calculation rules, and organizational agreements about what "good" means.

### Anatomy of a Metric Definition

| Attribute | Description | Example |
|-----------|-------------|---------|
| **Metric name** | Official name | "Customer Churn Rate" |
| **Business question** | What decision does this inform? | "Are we retaining customers effectively?" |
| **Formula** | Precise calculation | `Churned Customers / Total Customers at Start of Period` |
| **Numerator definition** | Define the top | "Churned Customer: had active status, now inactive for >90 days" |
| **Denominator definition** | Define the bottom | "All customers active at period start" |
| **Granularity** | Level of detail | Monthly, by customer segment |
| **Filters** | Scope constraints | Excludes trial customers |
| **Source data** | Where values come from | `dim_customer`, `fact_activity` |
| **Owner** | Accountable business owner | VP of Customer Success |
| **Target/threshold** | What good looks like | < 2% monthly |
| **Calculation frequency** | When it's computed | Monthly, calculated on 1st business day |
| **Related metrics** | Connected KPIs | Net Revenue Retention, NPS |

### Common Metric Definition Problems

| Problem | Symptom | Fix |
|---------|---------|-----|
| **Ambiguous numerator** | Two teams get different churn numbers | Precisely define "churned customer" |
| **Missing denominator scope** | Numbers don't reconcile | Specify exact population and point-in-time |
| **Undefined time grain** | "Monthly" means different things | Specify calendar vs. rolling window |
| **No filter documentation** | Unexpected exclusions | Enumerate all filters and their rationale |
| **Multiple "official" versions** | Competing reports | Designate one authoritative version; mark others as variants |

---

## Stewardship Roles

### Role Definitions

| Role | Responsibility | Typical Person |
|------|---------------|----------------|
| **Data Owner** | Accountable for data quality and appropriate use; approves policies | Business executive (VP, Director) |
| **Data Steward** | Day-to-day management of business metadata; maintains definitions | Business analyst, subject matter expert |
| **Technical Steward** | Manages technical metadata; ensures data integrity | Data engineer, DBA |
| **Metadata Curator** | Enriches and maintains catalog entries | Data governance analyst |
| **Data Consumer** | Uses data; responsible for appropriate use | Analyst, scientist, developer |

### Stewardship Models

**Centralized**: Single governance team manages all metadata
- Pro: Consistent, controlled
- Con: Bottleneck, distant from business

**Federated**: Domain stewards own their metadata; central team sets standards
- Pro: Domain expertise, scalable
- Con: Requires coordination, risk of fragmentation

**Data Mesh**: Domain teams own and publish their metadata as a product
- Pro: Decentralized, domain-aligned
- Con: Requires mature platform and governance standards

---

## Business Metadata Quality

Business metadata quality degrades due to:
1. **Attrition**: Knowledge holders leave; definitions become orphaned
2. **Drift**: Business meaning changes; metadata doesn't update
3. **Proliferation**: Multiple slightly different versions accumulate
4. **Ambiguity**: Definitions are imprecise and interpreted differently

**Quality indicators for business metadata:**
- Completeness: % of data assets with a linked glossary term
- Currency: % of terms reviewed in the last 12 months
- Accountability: % of terms with a named, active steward
- Linkage: % of terms linked to at least one physical data element
