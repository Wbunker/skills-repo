# AWS Savings Plans & Reserved Instances — Capabilities Reference
For CLI commands, see [savings-plans-ri-cli.md](savings-plans-ri-cli.md).

## Savings Plans

**Purpose**: Flexible pricing model that reduces compute costs in exchange for a commitment to a consistent amount of usage (measured in $/hour) over a 1- or 3-year term. Up to 72% savings over On-Demand.

### Plan Types

| Type | Flexibility | Discount Depth | Applies To |
|---|---|---|---|
| **Compute Savings Plans** | Any instance family, size, OS, tenancy, or region | Up to 66% | EC2, AWS Fargate, AWS Lambda |
| **EC2 Instance Savings Plans** | Specific instance family + region; flexible across size, OS, tenancy | Up to 72% (highest) | EC2 only in selected family/region |
| **SageMaker Savings Plans** | Any instance family, size, component, or region | Up to 64% | Amazon SageMaker AI |

### Commitment Mechanics

| Concept | Details |
|---|---|
| **Unit of commitment** | $/hour of compute usage |
| **Term options** | 1 year (365 days) or 3 years (1,095 days) |
| **Payment options** | All upfront, Partial upfront, No upfront |
| **Discount application** | Automatic; applied to qualifying usage up to the committed $/hr amount |
| **Overage** | Usage beyond the committed amount is billed at On-Demand rates |

### Coverage vs. Utilization

| Metric | What it measures | Goal |
|---|---|---|
| **Savings Plans coverage** | Percentage of eligible spend covered by Savings Plans | Increase to reduce On-Demand spend |
| **Savings Plans utilization** | Percentage of purchased Savings Plans commitment actually consumed | Keep high (≥80%) to avoid paying for unused commitment |

### Key Features

- **Recommendations engine** in Cost Explorer: analyzes historical usage to suggest optimal $/hr commitment
- **Savings Plans inventory**: view active plans, term, payment, commitment amount, and status
- **Budget alerts**: set alerts when coverage drops below threshold or utilization falls below a target
- **Queued Savings Plans**: schedule purchase for the start of a new commitment period
- Higher upfront payment yields greater savings; 3-year terms save more than 1-year

### When to Choose Compute vs. EC2 Instance Savings Plans

- Choose **Compute Savings Plans** when you need flexibility across regions, instance families, or workloads that include Lambda or Fargate
- Choose **EC2 Instance Savings Plans** when you have stable, predictable EC2 usage in a specific instance family and region and want maximum discount

---

## Reserved Instances

**Purpose**: Commit to use a specific instance configuration (or flexible class) for 1 or 3 years in exchange for a significant discount versus On-Demand pricing. Billing benefit applies automatically to matching running instances.

### Standard vs. Convertible

| Attribute | Standard RI | Convertible RI |
|---|---|---|
| **Discount** | Higher (up to ~72%) | Lower (up to ~54%) |
| **Flexibility** | Can modify (size, AZ, network) | Can exchange for different Convertible RI with equal or greater value |
| **Exchange** | Not allowed | Allowed — change instance family, OS, tenancy |
| **Sell on Marketplace** | Yes | Yes |
| **Cancel** | No | No |
| **Best for** | Stable, predictable workloads | Workloads likely to change configuration |

### Scope: Regional vs. Zonal

| Scope | Behavior |
|---|---|
| **Regional** | Discount applies to matching instances in any AZ in that region; instance size flexibility applies for Linux RIs |
| **Zonal** | Discount applies only in a specific AZ; provides a capacity reservation guarantee |

**Instance size flexibility** (regional Linux/Unix RIs only): a single regional Linux RI can cover multiple smaller instances of the same family, proportional to normalized units.

### Payment Options

| Option | Structure | Relative Discount |
|---|---|---|
| **All upfront** | Full payment at start, no hourly charges | Highest |
| **Partial upfront** | Portion paid upfront + discounted hourly rate | Middle |
| **No upfront** | Discounted hourly rate only, billed monthly | Lowest; requires good account standing |

### Key Features

- **RI Marketplace**: Buy/sell 3rd-party Standard RIs with remaining term; find shorter commitments or sell unused RIs
- **Convertible exchanges**: Trade one or more Convertible RIs for a new Convertible RI of equal or greater total value; no fee; can consolidate or split
- **Modifying RIs**: Change AZ, network type, or split/merge instances within the same family and region (Standard and Convertible)
- **Billing benefit**: Applied automatically to matching On-Demand usage; no action needed after purchase
- **Auto-renewal**: RIs do NOT auto-renew; after expiration, reverts to On-Demand rates
- Available for EC2, RDS, Redshift, ElastiCache, OpenSearch, MemoryDB, DynamoDB
