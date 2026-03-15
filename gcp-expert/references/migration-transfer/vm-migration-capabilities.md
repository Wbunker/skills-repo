# Migrate to Virtual Machines — Capabilities

## Purpose

**Migrate to Virtual Machines** (formerly Velostrata) is a GCP-managed service that automates lift-and-shift migration of virtual machines from on-premises hypervisors and other clouds to Google Compute Engine. It performs continuous block-level replication, enabling migrations with minimal downtime and without requiring changes to the source VMs.

---

## Supported Sources

| Source Platform | Supported Versions |
|---|---|
| VMware vSphere / vCenter | vSphere 6.0, 6.5, 6.7, 7.0 |
| Microsoft Hyper-V | Windows Server 2012 R2, 2016, 2019 |
| Amazon Web Services (AWS) | EC2 instances (any region) |
| Microsoft Azure | Azure VMs |
| Physical servers | Via VMware vSphere (P2V first, then migrate) |

---

## Core Concepts

| Concept | Description |
|---|---|
| **Source** | The origin system: vCenter server, AWS account, or Azure subscription |
| **Datacenter Connector** | Agent deployed in source environment (VMware only); connects to GCP Migrate service |
| **Migrating VM** | A VM currently being migrated; has replication state |
| **Replication** | Continuous block-level sync of VM disk from source to GCP |
| **Clone Job** | Non-disruptive test clone; creates a GCE instance from replicated data without stopping the source |
| **Cutover Job** | Final migration; stops the source VM and creates the production GCE instance |
| **Wave** | A logical grouping of VMs for coordinated batch migration |
| **Utilization Report** | Analysis of source VM vCPU/memory usage to recommend GCE machine types |

---

## Migration Flow

### Phase 1: Setup
1. Create a **Migration project** in GCP (enables required APIs)
2. Deploy the **Migrate to VMs connector appliance** in the source environment:
   - VMware: deploy OVA to vCenter; configure GCP connectivity
   - AWS: no connector needed; uses AWS APIs
   - Azure: no connector needed; uses Azure APIs
3. Create a **Source** in the Migrate service pointing to vCenter/AWS/Azure
4. Run a **Utilization Data Collection** to analyze source VM performance (optional but recommended)

### Phase 2: Replicate
1. Create **Migrating VM** objects for each source VM to migrate
2. Start **replication** — initial full disk copy followed by incremental sync
   - Initial replication copies the full disk; may take hours/days for large VMs
   - After initial sync, continuous incremental replication keeps GCP copy current
3. Replication runs in the background; source VM continues running normally

### Phase 3: Test
1. Create **Clone Job** — instantiates a GCE VM from the replicated data without stopping the source
   - Clone VM is isolated (different network or firewall rules) to avoid conflicts
   - Test application functionality, connectivity, and performance
   - Delete the clone when done; replication continues
2. Verify right-sizing recommendation matches tested performance

### Phase 4: Cutover
1. Schedule a maintenance window (planned downtime)
2. Execute **Cutover Job**:
   - Source VM is stopped (or you stop it manually first)
   - Final incremental replication runs (seconds to minutes)
   - GCE VM is created in target VPC with target machine type
   - Network configuration applied (static IP mapping, firewall rules)
3. Update DNS/load balancer to point to new GCE IP
4. Verify application functionality in GCP
5. Decommission source VM after validation period

---

## Replication Details

- **Protocol**: block-level replication over HTTPS; uses GCP private endpoint for security
- **Bandwidth throttling**: configurable per datacenter connector or per migrating VM
- **Compression**: data compressed in transit
- **Encryption**: data encrypted in transit (TLS) and at rest in GCP (Google-managed or CMEK)
- **Initial replication size**: full disk size (minus zeros); typically 20-40% of allocated disk size for typical workloads
- **Incremental sync lag**: typically minutes for active VMs; near-zero lag achievable for low-change VMs

---

## Right-sizing

Migrate to VMs collects CPU, memory, and disk I/O utilization from source VMs:
- 30-day collection window recommended for accurate sizing
- Suggests GCE machine type with headroom (typically adds 20% buffer over observed peak)
- Identifies VMs that are over-provisioned (downsize opportunity)
- Identifies VMs requiring more disk IOPS (upgrade to SSD PD or Hyperdisk)

---

## Guest OS Support

**Linux:**
- RHEL 6, 7, 8, 9
- CentOS 6, 7, 8
- Ubuntu 16.04, 18.04, 20.04, 22.04
- Debian 9, 10, 11
- SLES 12, 15
- Oracle Enterprise Linux 6, 7, 8

**Windows:**
- Windows Server 2008 R2, 2012, 2012 R2, 2016, 2019, 2022

**Note**: the migration process automatically installs GCE guest environment (virtio drivers, GCE agent) on migrated VMs.

---

## Network Considerations

- **Target VPC**: configure which VPC/subnet GCE instances land in
- **IP address mapping**: can map source static IPs to GCE alias IP ranges or static IPs
- **Firewall rules**: apply GCE firewall rules; source OS firewall rules are preserved
- **Private migration network**: option to migrate over private connectivity (Cloud Interconnect or Cloud VPN) for sensitive data

---

## Google Cloud VMware Engine (GCVE) — Alternative Approach

For organizations unable or unwilling to refactor VMware workloads:
- **GCVE** runs VMware vSphere natively on dedicated GCP bare metal nodes
- No VM conversion needed; move VMs with VMware HCX (Layer 2 extension + live migration)
- Useful for licensing-constrained workloads (Windows OEM licenses, Oracle), latency-sensitive apps, VMware-dependent features
- More expensive than GCE (dedicated hardware) but lower migration complexity
- Use Migrate to VMs for eventual modernization from GCVE to GCE

---

## Migration Factory Pattern

For large-scale migrations (100+ VMs):
1. **Assess**: run utilization collection; categorize VMs by complexity and risk
2. **Wave planning**: group VMs into waves by application dependencies (migrate app tiers together)
3. **Pilot wave**: migrate 5-10 low-complexity VMs to validate process
4. **Scale**: run multiple waves in parallel; typical throughput 20-50 VMs/week per connector
5. **Cutover sprint**: schedule coordinated cutover windows for dependent application groups
