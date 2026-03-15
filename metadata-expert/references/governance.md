# Metadata Governance and Quality
## Chapters 7–8: Governance Models, Stewardship, Policies, Metadata Quality

---

## What Is Metadata Governance?

Metadata governance is the set of **policies, processes, roles, and standards** that ensure metadata is accurate, complete, consistent, and used appropriately. It answers:
- *Who is accountable for each piece of metadata?*
- *How do we ensure metadata stays accurate over time?*
- *What standards must metadata conform to?*
- *How do we resolve conflicts between competing definitions?*

Without governance, metadata degrades: definitions drift, ownership becomes unclear, and the catalog becomes unreliable. **Ungoverned metadata is worse than no metadata** because it creates false confidence.

---

## Governance Models

### Centralized Governance
```
Central Data Governance Team
├── Owns all metadata standards
├── Maintains the business glossary
├── Reviews and approves all term changes
└── Enforces quality through central tooling

Pros: Consistent, controlled, single source of truth
Cons: Bottleneck, disconnected from domain knowledge, slow
Best for: Small organizations, regulated environments needing strict control
```

### Federated Governance
```
Central Governance Team
├── Sets standards, policies, and frameworks
├── Provides tooling and templates
└── Audits compliance

Domain Stewards (Finance, Sales, HR, Product...)
├── Own their domain's metadata
├── Maintain domain glossary terms
└── Comply with central standards

Pros: Scalable, domain-expert driven, faster
Cons: Requires coordination, risk of inconsistency
Best for: Large enterprises with multiple distinct data domains
```

### Data Mesh Governance (Federated Computational)
```
Platform Team: Provides self-serve metadata infrastructure
Domain Teams: Treat metadata as part of their data product
Governance: Encoded in platform policy rather than manual review

Principles:
- Each domain publishes metadata as part of their data product contract
- Standards are enforced programmatically, not through committees
- Discoverability is a first-class product requirement

Pros: Highly scalable, governance by design
Cons: Requires mature platform and standardization investment
Best for: Data mesh organizations
```

---

## Stewardship Framework

### The Stewardship Accountability Hierarchy

```
Data Owner (Executive)
├── Accountable for data quality and appropriate use
├── Approves data policies and classification decisions
└── Signs off on governance frameworks

  Data Steward (Business)
  ├── Maintains business glossary and data definitions
  ├── Resolves business meaning disputes
  ├── Validates that data meets business expectations
  └── Reports data quality issues to owner

    Technical Data Steward (Engineering)
    ├── Maintains schema documentation
    ├── Manages lineage and profile metadata
    └── Implements technical governance controls

      Data Consumer (Everyone)
      ├── Uses data appropriately per policies
      ├── Reports anomalies and quality issues
      └── Provides feedback to improve metadata
```

### Stewardship Assignment Patterns

**By Domain**: Each business domain has a steward who owns all metadata for that domain
- Sales steward owns: customer, opportunity, order metadata
- Finance steward owns: revenue, cost, GL metadata

**By Asset Type**: Different stewards for different asset categories
- Glossary steward: owns term definitions
- Data dictionary steward: owns physical column documentation
- Lineage steward: owns process and pipeline metadata

**By Sensitivity**: Additional stewards for sensitive data categories
- PII steward: oversees all personally identifiable data
- Financial data steward: oversees regulated financial records

### Making Stewardship Sustainable
Common failure modes:
- Stewardship is an unfunded "extra" role — no dedicated time
- Stewards lack authority to enforce standards
- Rotation without knowledge transfer
- No tooling to help stewards work efficiently

Solutions:
- **Allocated time**: Stewardship should be 10–20% of the role, formally recognized
- **Authority**: Stewards must be able to reject ungoverned data publication
- **Tooling**: Catalog workflows that route curation tasks to stewards
- **Recognition**: Include metadata quality in performance reviews

---

## Metadata Policies

### What Metadata Policies Cover

| Policy Area | Example Policy |
|-------------|----------------|
| **Completeness** | "All production tables must have a description and business owner before publication" |
| **Naming standards** | "Columns storing dates must end in `_dt`; timestamps in `_ts`" |
| **Classification** | "All datasets touching PII must be classified Confidential within 5 business days of creation" |
| **Retention** | "Pipeline run logs retained 2 years; PII access logs retained 7 years" |
| **Review cadence** | "Business glossary terms must be reviewed annually; flagged if not reviewed in 13 months" |
| **Lineage** | "Any pipeline modifying a Confidential dataset must document full column lineage" |
| **Change management** | "Breaking schema changes require 30-day notice period with impact analysis" |

### Policy Enforcement Levels

| Level | Approach | Example |
|-------|----------|---------|
| **Hard gate** | Blocks action if policy violated | Cannot publish table without an owner |
| **Soft gate** | Warns but allows with justification | Warns if description is missing; requires reason to proceed |
| **Audit** | Allows but logs violation | Records that table published without classification |
| **Reporting** | Surfaces violations in dashboards | Weekly report of unclassified assets |

---

## Metadata Quality

### The Six Dimensions of Metadata Quality

**1. Completeness**
Are all required metadata attributes populated?
```
Measurement: % of mandatory fields populated across all assets
Example: 72% of tables have a description; target: 90%
Fix: Identify ungoverned assets; assign stewards; enforce completion gates
```

**2. Accuracy**
Does the metadata correctly describe the data?
```
Measurement: % of metadata validated against actual data or expert review
Example: 15 columns described as "customer email" that actually hold internal IDs
Fix: Profiling-based validation; steward review cycles; cross-system reconciliation
```

**3. Timeliness**
Is the metadata current?
```
Measurement: % of metadata reviewed/updated within its required review period
Example: 34% of glossary terms not reviewed in 18+ months
Fix: Automated staleness alerts; steward review workflows with deadlines
```

**4. Consistency**
Is the same concept described consistently across systems?
```
Measurement: % of equivalent concepts using the same terminology and definitions
Example: "Customer" defined differently in CRM, ERP, and analytics glossaries
Fix: Federated glossary with authoritative source; cross-system reconciliation
```

**5. Accessibility**
Can the right people find and access the metadata they need?
```
Measurement: Search success rate; time-to-find metrics; % of assets discoverable
Example: 60% of data assets are not discoverable in the catalog
Fix: Catalog crawling; tagging; improved search relevance
```

**6. Fitness for Purpose**
Is the metadata adequate for its intended use? (Olesen-Bagneux's key insight)
```
Measurement: User satisfaction; task completion rates; metadata-triggered trust failures
Example: Technical metadata complete but no business context for self-service analytics
Fix: Match metadata curation effort to use case requirements
```

### Metadata Quality Scoring

A simple scoring framework:

```
Asset Score = Σ (dimension_weight × dimension_score) / Σ weights

Example weights:
  Completeness:    25%
  Accuracy:        25%
  Timeliness:      20%
  Consistency:     15%
  Accessibility:   10%
  Fitness:          5%

Example asset score:
  fact_orders: (25×0.95 + 25×0.90 + 20×0.70 + 15×0.85 + 10×0.90 + 5×0.80) / 100
             = (23.75 + 22.50 + 14.00 + 12.75 + 9.00 + 4.00) / 100
             = 86.0 / 100 = 86%
```

### Metadata Quality Dashboard KPIs

| KPI | Target | Measure |
|-----|--------|---------|
| % tables with description | > 90% | Catalog scan |
| % tables with business owner | 100% | Catalog scan |
| % glossary terms reviewed in 12 months | > 85% | Glossary audit |
| % datasets classified by sensitivity | 100% | Policy engine |
| % pipelines with SLA defined | > 80% | Pipeline registry |
| Orphan metadata rate | < 5% | Metadata linkage analysis |
| Catalog search success rate | > 75% | User behavior analytics |

---

## Governance Anti-Patterns

| Anti-Pattern | Problem | Better Approach |
|--------------|---------|-----------------|
| **Governance by committee only** | Slow, bureaucratic; no execution | Empower stewards with authority and tooling |
| **Metadata police** | Creates adversarial culture; people hide data | Governance as enablement, not enforcement |
| **Perfect before publishing** | Nothing gets published | "Good enough" thresholds; iterative improvement |
| **IT owns governance** | Business meaning defined by engineers | Business stewardship for meaning; IT for technical |
| **One-time audit** | Metadata degrades immediately after | Continuous governance with automated monitoring |
| **No stewardship for derived data** | Downstream assets have no owners | Explicitly assign stewardship for all data products |
| **Governance without authority** | Policies exist but aren't enforced | Stewards must have escalation paths and real authority |

---

## Data Classification as Governance Metadata

Classification is governance metadata that drives access control, handling requirements, and retention:

```
Classification Schema:
─────────────────────────────────────────────────
PUBLIC         Available externally; no restrictions
INTERNAL       Employee use only; standard controls
CONFIDENTIAL   Restricted access; need-to-know basis
RESTRICTED     Highest sensitivity; regulatory controls
  ├── PII       Personal Identifiable Information
  ├── PHI       Protected Health Information (HIPAA)
  └── PCI       Payment Card Industry data

Assignment Process:
1. Data arrives in platform
2. Automated scanner checks for patterns (SSN, email, card #)
3. Steward reviews and confirms classification
4. Classification applied as metadata tag
5. Access controls enforced based on tag
6. Reviewed annually or on data change
```
