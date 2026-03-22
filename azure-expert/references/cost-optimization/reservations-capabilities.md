# Azure Reservations & Savings Plans — Capabilities Reference
For CLI commands, see [reservations-cli.md](reservations-cli.md).

## Commitment-Based Pricing Overview

Azure offers two commitment-based discount models that provide significant savings versus pay-as-you-go (PAYG) pricing in exchange for usage commitments.

| Model | Flexibility | Discount | Best For |
|---|---|---|---|
| **Azure Reservations** | Lower (specific service/SKU/region) | Higher (up to 72% vs PAYG) | Stable, predictable workloads with known size and region |
| **Azure Savings Plans for Compute** | Higher (any compute, any region, any OS) | Lower vs specific RI (up to 65%) | Diverse or dynamic compute with variable sizes/regions |

---

## Azure Reservations

Pre-pay for specific Azure resource capacity for 1 or 3 years in exchange for significantly discounted rates.

### Supported Services

| Service | Reservation Scope | Notes |
|---|---|---|
| **Virtual Machines (Reserved Instances)** | Instance size family, region, OS | VM size flexibility within same instance size flexibility group |
| **Azure SQL Database** | vCore model, tier, generation, region | DTU model not reservable |
| **Azure SQL Managed Instance** | vCore, generation, region | |
| **Azure Database for PostgreSQL** | vCore, generation, region | |
| **Azure Database for MySQL** | vCore, generation, region | |
| **Azure Database for MariaDB** | vCore, generation, region | |
| **Azure Cosmos DB** | Request units (RU/s), region | Provisioned throughput only |
| **Azure App Service** | Isolated v2, Premium v3 plans | Stamp fee discounts |
| **AKS** | Underlying VM reserved instances (node VMs) | Buy RI for the VM SKU used as AKS nodes |
| **Azure Redis Cache** | Cache size, region | |
| **Azure Databricks** | DBU pre-purchase (DPUs) | Applies across all workload types |
| **Azure Synapse Analytics** | Dedicated SQL pool (DWUs), region | |
| **Azure HDInsight** | Node type, region | |
| **Azure Data Factory** | Data integration units | |
| **Azure Blob Storage** | Capacity (GB), redundancy, access tier | |
| **Azure Files** | Capacity (GB), redundancy | |
| **Dedicated Hosts** | Host type, region | |
| **Azure VMware Solution** | Node type, region | |

---

### VM Reserved Instances — Deep Dive

**Discount mechanics:**
- Reservation applies automatically to matching VMs in the defined scope — no VM configuration change needed
- VM must be running or stopped (not deallocated) to consume reservation; deallocated VMs waste reservation
- Discount applied to compute cost only; OS license, storage, and networking still billed PAYG (use Azure Hybrid Benefit for OS license savings)

**Instance Size Flexibility:**
- Within the same **Instance Size Flexibility Group** (ISF), reservations apply across VM sizes proportionally
- Example: A `Standard_D4s_v5` reservation (4 vCPU) covers either one D4s_v5 OR two D2s_v5 OR four D1s_v5
- ISF flexibility is enabled by default for most VM reservations
- Exceptions: reservations for specific configurations (e.g., GPU VMs, dedicated hosts) may not have ISF

**Reservation scope options:**

| Scope | Description |
|---|---|
| **Single resource group** | Applies only to VMs in a specific resource group |
| **Single subscription** | Applies to all VMs in one subscription |
| **Shared** | Applies across all subscriptions under the same billing account/enrollment; maximizes utilization |
| **Management group** | Applies across all subscriptions in a management group (newer feature) |

---

### Exchange and Cancellation

| Action | Policy |
|---|---|
| **Exchange** | Exchange an unused/underutilized reservation for a different one before expiry; no fee; new reservation must be equal or greater value |
| **Cancellation** | Cancel anytime; refund = remaining value minus **12% early termination fee** (maximum $50,000 USD refund per 12-month rolling window) |
| **Self-service exchange/cancel** | Available in Azure portal for most reservation types |
| **Expiry** | Reservation expires at term end; set to auto-renew in portal to avoid PAYG rate resumption |

**Restrictions:**
- Some reservation types (Azure Databricks DPUs, Azure Storage) may not support exchange
- Exchanges must be for the same service type (e.g., cannot exchange VM RI for Cosmos DB RI)

---

### Reservation Purchase Recommendations

Azure provides automated recommendations based on your historical usage:

- **Azure Portal**: Reservations blade → Purchase recommendations (30-day or 7-day lookback)
- **Azure Cost Management**: Recommendations section shows potential savings and recommended quantity
- **Azure Advisor**: Cost category recommendations include "Buy Reserved Instances for consistent workloads"
- **Azure Consumption API**: `ReservationRecommendations` endpoint for programmatic recommendations

**Buying strategy:**
1. Analyze last 30 days of usage to identify consistently running VMs/services
2. Start with 1-year terms for flexibility (lower discount but less commitment risk)
3. Use shared scope for maximum flexibility across subscriptions
4. Exchange or cancel if workload changes significantly

---

### Monitoring Reservation Utilization

Low utilization means wasted spend — reservations should ideally run at 90–100% utilization.

| Tool | How to Access |
|---|---|
| **Azure portal** | Reservations blade → select reservation → Utilization % chart |
| **Cost Management** | Reservation utilization report; filter by reservation or time range |
| **Amortized cost view** | See reservation cost distributed across resources that consumed it (charge-back) |
| **Azure Monitor Alerts** | Alert when reservation utilization drops below a threshold |
| **Power BI** | Azure Cost Management Power BI connector with reservation utilization report |

---

## Azure Savings Plans for Compute

A flexible commitment-based discount that applies to a broad range of compute resources based on an hourly spend commitment.

### How It Works

- Commit to a **$/hour spend on compute** for 1 or 3 years (e.g., $10/hour)
- Azure automatically applies the Savings Plan discount rate to eligible compute usage up to the committed amount
- Usage beyond commitment is billed at PAYG rates
- No need to specify VM size, region, or OS in advance — maximum flexibility

### Eligible Resources

| Resource | Notes |
|---|---|
| **Virtual Machines** (any family, region, OS) | Most flexible RI alternative |
| **Azure Dedicated Hosts** | Host-level compute cost |
| **App Service** (Premium v3, Isolated v2) | App Service Plan compute |
| **Azure Functions Premium** | Elastic Premium plan compute |
| **Azure Container Instances** | Container instance compute |
| **AKS** | Underlying VM compute for node pools |

### Savings Plans vs Reserved VM Instances

| Criterion | Savings Plans | Reserved VM Instances |
|---|---|---|
| **Flexibility** | Any region, size, OS, service | Specific VM family, region, OS |
| **Discount** | Up to ~65% vs PAYG | Up to ~72% vs PAYG |
| **Exchange** | Not exchangeable (can cancel with fee) | Exchangeable for same service type |
| **Scope** | Subscription or shared | Single subscription, RG, or shared |
| **Best for** | Dynamic/diverse compute, migration periods | Stable, known workloads |

**Recommendation**: Use a combination — Savings Plan for flexible baseline, Reserved Instances for the stable, well-understood portion of workloads.

---

## Reservation Utilization Targets and Governance

| Practice | Description |
|---|---|
| **Monthly utilization review** | Review all reservations in Cost Management; target >85% utilization |
| **Alert on low utilization** | Azure Monitor alert when utilization < 60% triggers review |
| **Auto-renew setting** | Enable auto-renew 30 days before expiry to prevent PAYG gap |
| **Right-sizing before buying** | Use Azure Advisor right-sizing recommendations before purchasing VMs for reservation |
| **Centralized purchase** | EA/MCA billing admins purchase reservations at shared scope for maximum cross-subscription utilization |
| **Tagging post-purchase** | Tag reservations with owner, cost center, and workload for charge-back in amortized cost reports |
