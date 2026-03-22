# Azure Hybrid Benefit & Spot VMs — Capabilities Reference
For CLI commands, see [hybrid-spot-cli.md](hybrid-spot-cli.md).

## Azure Hybrid Benefit (AHB)

**Purpose**: Apply existing on-premises Microsoft and Linux software licenses to Azure resources, eliminating the license cost component from Azure billing. One of the highest-impact cost optimization levers for organizations with existing license investments.

---

## Windows Server Hybrid Benefit

Apply Software Assurance (SA)-covered Windows Server licenses to Azure VMs, eliminating the Windows OS license cost from the Azure VM price.

### How It Works

- Each 2-core Windows Server license pack (Standard or Datacenter edition) → 2 Azure vCPUs covered
- **Standard edition**: each license covers up to 1 VM with up to 2 vCPUs (2-core = 2 vCPU coverage); can be used for Azure OR on-premises, not both simultaneously
- **Datacenter edition**: unlimited virtualization rights — use the same license on-premises AND in Azure; highly valuable for large fleets

### Discount Impact

| Scenario | Discount |
|---|---|
| Windows Server license cost removed | ~40–50% reduction in VM cost (Windows license is a significant component) |
| Standard_D4s_v5 Windows (PAYG) vs AHB | ~$87/month → ~$55/month (typical East US; varies by VM family) |

### Key Rules

- Requires **Software Assurance (SA)** or subscription coverage on Windows Server licenses
- Can be applied/removed at any time — dynamic; no redeployment required
- **Normalize cores**: Azure VMs with <8 vCPUs require minimum 8-core license packs (normalize to 8)
- **Datacenter edition** provides maximum flexibility: use same licenses on-premises and Azure

---

## SQL Server Hybrid Benefit

Apply SQL Server licenses with Software Assurance to Azure SQL services, replacing the license cost component.

### Coverage

| SQL Server License | Azure SQL Benefit |
|---|---|
| **SQL Server Standard** (per core) | Azure SQL Database General Purpose, Azure SQL Managed Instance General Purpose |
| **SQL Server Enterprise** (per core) | Azure SQL Database Business Critical, Azure SQL Managed Instance Business Critical; OR 4x SQL Standard coverage for General Purpose |
| **SQL Server Developer/Express** | No AHB coverage (these editions have no license cost to apply) |

### Discount Impact

| Comparison | Discount |
|---|---|
| SQL MI GP (4 vCores) PAYG vs AHB | ~$750/month → ~$350/month (approx. 55% savings on compute+license component) |
| SQL DB BC (4 vCores) PAYG vs AHB (Enterprise) | ~$1,800/month → ~$800/month |

### SQL Server + Azure Reservations Stack

Combine AHB + Reserved Capacity for maximum savings:
- AHB removes license cost
- Reserved Capacity removes ~40% from compute cost
- Combined savings: up to **80%** vs full PAYG with OS/SQL license included

---

## Linux Hybrid Benefit (RHEL and SLES)

Apply existing Red Hat Enterprise Linux (RHEL) or SUSE Linux Enterprise Server (SLES) subscriptions to Azure VMs.

### RHEL (Red Hat)

- Bring existing RHEL subscriptions from on-premises to Azure
- Requires **Red Hat Cloud Access** program enrollment
- License type: `RHEL_BYOS` (Bring Your Own Subscription)
- After applying AHB: pay Azure compute cost only; Red Hat subscription handles support and updates via Red Hat Satellite or Red Hat Insights
- Red Hat Update Infrastructure (RHUI) continues to work for package updates in Azure

### SUSE Linux Enterprise

- Bring existing SLES subscriptions from on-premises to Azure
- Requires **SUSE Public Cloud Program** enrollment
- License type: `SLES_BYOS`
- After applying AHB: pay Azure compute cost only; SUSE subscription handles support

### Ubuntu Pro on Azure

- Not AHB (different program); Ubuntu Pro is a separate Azure offering with extended security maintenance
- Converts Ubuntu LTS VMs to Ubuntu Pro (5 years of security patching + compliance tools)

---

## AHB for AKS (Windows Node Pools)

Apply Windows Server AHB to Windows node pools in AKS clusters.

- Removes Windows Server license cost from Windows AKS node VMs
- Applied at the node pool level: `az aks nodepool add --os-type Windows --enable-node-public-ip false --windows-os-disk-size-gb 128`
- Enable AHB: `az aks nodepool update --enable-windows-ahb`
- Estimated savings: same as VM-level AHB (~40-50% reduction in Windows node cost)

---

## AHB for Azure Stack HCI

Apply existing Windows Server Datacenter licenses (with SA) to Azure Stack HCI nodes:
- Eliminates the Windows Server host OS cost on HCI nodes
- Azure Stack HCI is billed per physical core; AHB reduces the OS component
- Enables running unlimited Windows Server VMs on the HCI cluster with covered licenses

---

## Spot Virtual Machines

**Purpose**: Access Azure's excess compute capacity at up to 90% discount vs PAYG pricing, in exchange for the possibility of eviction when Azure needs the capacity back.

---

## How Spot VMs Work

| Aspect | Description |
|---|---|
| **Pricing** | Up to 90% discount vs PAYG; spot price fluctuates based on Azure region capacity supply/demand |
| **Eviction** | Azure may evict (stop/deallocate) Spot VMs with **30-second notice** when capacity is needed |
| **Eviction types** | Capacity: Azure needs capacity back; Price: spot price exceeds your max price cap |
| **Availability** | No SLA; no guaranteed capacity; not suitable for SLA-sensitive production workloads |

---

## Eviction Policies

| Policy | What Happens on Eviction | Disk | Cost |
|---|---|---|---|
| **Deallocate** | VM stopped and deallocated; disk preserved; can manually restart when capacity returns | Preserved | Disk storage still billed |
| **Delete** | VM and all disks deleted on eviction; state lost | Deleted | No disk cost after eviction |

**Recommendation**: Use `Delete` for stateless batch workloads (no disk cost accumulation). Use `Deallocate` if you need to preserve disk state and restart later.

---

## Max Price Configuration

| Max Price Setting | Behavior |
|---|---|
| `-1` | Evict only when Azure needs capacity (price-based eviction disabled); recommended for most scenarios |
| `Positive value` | Evict when spot price exceeds max price (e.g., $0.05/hour); provides cost ceiling |
| Not set (default) | Same as `-1` behavior |

**Best practice**: Set `--max-price -1` to avoid unnecessary price-based evictions. Monitor cost via Cost Management if needed.

---

## Spot in VM Scale Sets (VMSS)

- Create a VMSS with Spot priority; all instances in the set are Spot VMs
- **Mixed pools**: VMSS supports mixing On-Demand (base capacity) + Spot (additional burst) instances
  - `--priority Spot` on the main scale set
  - Fallback policy: `Deallocate` or `Delete`
- **Overprovisioning**: VMSS can provision more instances than requested, terminate extras, to handle Spot availability issues
- **Automatic repair**: detect and replace unhealthy instances (even if evicted)

---

## Spot Node Pools in AKS

Run Spot VMs as AKS node pools for cost-effective batch or fault-tolerant workloads.

### Configuration

```bash
az aks nodepool add \
  --resource-group myRG \
  --cluster-name myAKSCluster \
  --name spotpool \
  --priority Spot \
  --eviction-policy Delete \
  --spot-max-price -1 \
  --enable-cluster-autoscaler \
  --min-count 0 \
  --max-count 20
```

### Spot Node Pool Behavior

- Spot nodes automatically tainted: `kubernetes.azure.com/scalesetpriority=spot:NoSchedule`
- Workloads must tolerate the taint to be scheduled on Spot nodes
- AKS cluster autoscaler handles Spot availability: scales to other node pools if Spot capacity unavailable
- Use `nodeAffinity` with `PreferredDuringSchedulingIgnoredDuringExecution` to prefer Spot but fall back to On-Demand

```yaml
# Pod toleration and affinity for Spot node pools
tolerations:
- key: kubernetes.azure.com/scalesetpriority
  operator: Equal
  value: spot
  effect: NoSchedule
affinity:
  nodeAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 1
      preference:
        matchExpressions:
        - key: kubernetes.azure.com/scalesetpriority
          operator: In
          values:
          - spot
```

---

## Spot VM Best Practices

| Practice | Description |
|---|---|
| **Checkpoint state frequently** | Write progress to durable storage (Azure Blob, Table) so evicted workloads can resume |
| **Use eviction notification** | Azure sends `SIGTERM` 30 seconds before eviction; use this window to save state or checkpoint |
| **Design for idempotency** | Workloads must be safely restartable without producing duplicates or corrupt state |
| **Use Eviction Policy Delete** | Avoid accumulated disk storage costs from deallocated Spot VMs |
| **Test with actual evictions** | Use Azure Instance Metadata Service (IMDS) to simulate eviction in testing |
| **Mix Spot + On-Demand** | Use VMSS or AKS with mixed pools: stable base on On-Demand, burst on Spot |
| **Monitor eviction rate** | Track metric `Evicted VMs` in Azure Monitor to understand regional Spot availability |

---

## Dev/Test Pricing

Available to Visual Studio subscribers and Dev/Test Azure subscriptions.

| Feature | Description |
|---|---|
| **Windows VMs** | Pay Linux PAYG rates for Windows VM compute (license included for free) |
| **SQL Server VMs** | Significant discounts on SQL Server license in VMs |
| **No SLA** | Dev/Test subscriptions have no SLA guarantee |
| **Scope** | Applies to: VMs, App Service, SQL Database, HDInsight, Logic Apps, API Management, Service Fabric, AKS |

**Activation**: Create an Azure subscription of type "Dev/Test" via the Visual Studio subscriber portal (my.visualstudio.com).

---

## B-Series Burstable VMs

Credit-based CPU bursting — similar to AWS T-series instances. Ideal for workloads with low average CPU but occasional spikes.

| Feature | Description |
|---|---|
| **CPU credits** | Accumulate credits during low CPU periods; spend credits during bursts |
| **Base CPU** | Each B-series VM has a baseline CPU % (e.g., Standard_B2s = 40% baseline for 2 vCPUs) |
| **Max burst** | 100% of vCPU capacity during burst (while credits available) |
| **Credit rate** | Credits earned = baseline% × vCPU count per hour |

### B-Series SKUs

| SKU | vCPU | RAM | Baseline CPU% | Max CPU% | Use Case |
|---|---|---|---|---|---|
| Standard_B1s | 1 | 1 GB | 10% | 100% | Very light workloads, micro-services |
| Standard_B2s | 2 | 4 GB | 40% | 200% | Dev environments, low-traffic APIs |
| Standard_B4ms | 4 | 16 GB | 40% | 400% | Dev databases, build agents |
| Standard_B8ms | 8 | 32 GB | 40% | 800% | Staging environments |
| Standard_B16ms | 16 | 64 GB | 40% | 1600% | Larger dev/staging workloads |

**Cost comparison**: B2s is typically ~30–40% cheaper than D2s_v5 for equivalent RAM/vCPU — significant savings for dev/test fleets.

**Do not use B-series for**: consistently high CPU workloads (credits deplete and VM throttled to baseline), latency-sensitive applications, production databases.
