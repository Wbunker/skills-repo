# Azure Migrate — Capabilities Reference
For CLI commands, see [azure-migrate-cli.md](azure-migrate-cli.md).

## Azure Migrate Hub

**Purpose**: Central hub for discovering, assessing, and migrating on-premises infrastructure to Azure. Provides a unified experience across all migration tools and tracks migration progress across the project lifecycle.

### Migration Phases

```
Discover → Assess → Migrate → Optimize
```

| Phase | Azure Migrate Capability |
|---|---|
| **Discover** | Agentless appliance discovers VMs, physical servers, apps, databases, web apps |
| **Assess** | Right-sizing recommendations, cost estimates, compatibility analysis, dependency mapping |
| **Migrate** | Replicate and cutover servers; use Server Migration tool or integrated partner tools |
| **Optimize** | Post-migration cost, performance, and security recommendations via Azure Advisor |

---

## Discovery

### Azure Migrate Appliance

- Lightweight VM deployed on-premises (VMware, Hyper-V, or physical)
- **Agentless discovery**: No agents needed on source VMs; appliance reads vCenter/Hyper-V APIs
- Discovers: VM inventory, installed software/web apps/SQL instances, running processes, network connections
- Sends data to Azure Migrate project (metadata only; no workload data leaves on-premises)
- Runs continuously; refreshes inventory every 24 hours
- **Appliance sizing**: 8-core, 16 GB RAM VM; needs internet access to Azure

### Supported Source Environments

| Source | Mechanism |
|---|---|
| VMware vCenter | Agentless (vCenter API); or agent-based (Azure Site Recovery agent) |
| Hyper-V | Agentless (Hyper-V WMI provider) |
| Physical servers | Azure Migrate agent installed on each server |
| AWS EC2 instances | Treated as physical servers; agent-based |
| GCP VMs | Treated as physical servers; agent-based |

---

## Assessment

### Server Assessment

| Assessment Type | Description |
|---|---|
| **Azure VM assessment** | Recommends VM family/SKU; estimates monthly compute and storage cost |
| **Azure VMware Solution (AVS) assessment** | Recommends AVS node count, type, and estimated cost |
| **Azure SQL assessment** | Recommends Azure SQL DB / SQL MI / SQL Server on Azure VM target |
| **Azure App Service assessment** | Identifies IIS apps and assesses compatibility with Azure App Service |

### Assessment Parameters

- **Sizing criteria**: Performance-based (from collected metrics) or As on-premises (map current specs)
- **Performance history**: 1 day, 1 week, or 1 month of collected perf data
- **Percentile**: 50th, 90th, 95th, or 99th percentile of collected performance data
- **Comfort factor**: Multiplier applied to resource utilization for headroom (default: 1.3)
- **Target location**: Azure region for cost estimation
- **Reserved instances**: 1-year or 3-year RI pricing in cost estimates
- **Azure Hybrid Benefit**: Apply BYOL Windows Server / SQL Server licenses

### Dependency Analysis

| Type | How | Requirement |
|---|---|---|
| **Agentless** | Network connection data from vCenter API (VMware only) | No agent; 6-hour data refresh |
| **Agent-based** | MMA (Log Analytics agent) + Dependency agent on each VM | Works on VMware, Hyper-V, physical; richer process-level data |

- Visualize network connections between VMs in a dependency map
- Identify application groups (servers that communicate and should migrate together)
- Export dependency data for further analysis

---

## Server Migration

### Replication Approaches

| Approach | Source | Mechanism |
|---|---|---|
| **Agentless VMware migration** | VMware VMs | vSAN/vCenter snapshot-based replication; no agent on VMs |
| **Agent-based migration** | VMware, Hyper-V, Physical, AWS, GCP | Azure Site Recovery Mobility Service agent on each VM |
| **Hyper-V migration** | Hyper-V VMs | Hyper-V Replication Provider; no agent on VMs |

### Migration Process

1. **Replicate**: Initiate replication; initial copy + delta sync to Azure
2. **Test migration**: Spin up test VM in isolated VNet; validate app functionality without disrupting source
3. **Cutover**: Stop replication, boot Azure VM, update DNS/IPs; decommission source
4. **Post-migration**: Install Azure VM agent, Azure Monitor agent, set up backups

### Migration Waves

- Group servers into **migration waves** by dependency group and business priority
- Define wave order and execute sequentially (Wave 1: dev/test, Wave 2: non-critical prod, Wave 3: core prod)
- Track wave status in Azure Migrate project dashboard

---

## Azure VMware Solution (AVS) Migration

**Purpose**: Migrate VMware workloads to Azure without re-platforming. Run VMware vSphere environment natively on Azure bare-metal infrastructure.

- Migrate using **VMware HCX** (included with AVS): L2 network extension, live vMotion, bulk cold/warm migration
- AVS assessment recommends: number of nodes (AV36, AV36P, AV52), node type, external storage add-ons
- Suitable for: applications requiring VMware-specific features, mass migration without re-architecture

---

## Web App Migration Assessment

- **App Service Migration Assessment**: Discover all IIS sites on Windows servers; assess compatibility
- Checks: .NET version, custom ISAPI filters, application pool identity, shared config, 32-bit mode
- Reports readiness level and migration blockers per site
- Compatible apps migrate directly to Azure App Service via Migration Assistant GUI or automated pipeline
