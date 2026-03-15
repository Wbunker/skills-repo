# GCP Recommender & Active Assist — Capabilities

## Overview

**Active Assist** is Google Cloud's umbrella brand for AI-powered recommendations and insights. It uses ML models trained on anonymized usage patterns to identify cost savings, security improvements, and operational optimizations across GCP services.

The underlying technology is the **Recommender API**, which provides:
- **Recommendations**: specific, actionable suggestions (e.g., "resize this VM")
- **Insights**: analytical findings that may or may not have an associated recommendation (e.g., "this disk has been idle for 30 days")

Active Assist recommendations surface in:
- The GCP Console (inline in relevant service UIs and the Recommender Hub)
- The Recommender API (programmatic access)
- The `gcloud recommender` CLI
- Security Command Center (for security recommendations)
- Looker Studio via billing export data

---

## VM Rightsizing Recommender

**Recommender ID**: `google.compute.instance.MachineTypeRecommender`

Analyzes Compute Engine instance CPU and memory utilization over the past 8 days and recommends downsizing to a smaller machine type.

**How it works:**
- Collects CPU and memory utilization via Cloud Monitoring
- Identifies instances where observed peak utilization is well below the provisioned capacity
- Recommends a smaller machine type with sufficient headroom
- Provides estimated monthly savings

**Recommendation states:**
- `ACTIVE` — new recommendation, not yet acted on
- `CLAIMED` — someone has acknowledged intent to apply
- `SUCCEEDED` — applied successfully
- `FAILED` — attempted but failed

**Key fields in a recommendation:**
- `primaryImpact.costProjection.cost.units` — estimated monthly savings
- `content.operationGroups` — the specific change to apply (new machine type)
- `recommenderSubtype` — `CHANGE_MACHINE_TYPE`, `STOP_VM`, or `DOWNSIZE`

**Limitations:**
- Only looks at 8-day window; run recommendations after representative workload period
- Does not account for burstable workloads or upcoming traffic spikes
- Memory utilization requires Cloud Monitoring agent (or Cloud Ops agent) to be installed

---

## Idle Resource Recommenders

Multiple recommenders detect unused/idle resources that are incurring costs:

### Idle VM Recommender
**Recommender ID**: `google.compute.instance.IdleResourceRecommender`

Identifies VMs with very low CPU utilization (typically <0.03 vCPU average over 14 days) and no network activity. Recommends stopping or deleting the VM.

### Idle Persistent Disk Recommender
**Recommender ID**: `google.compute.disk.IdleResourceRecommender`

Identifies persistent disks not attached to any instance (unattached disks still incur storage charges). Recommends deletion.

### Idle IP Address Recommender
**Recommender ID**: `google.compute.address.IdleResourceRecommender`

Identifies static external IP addresses reserved but not attached to any resource (VMs, forwarding rules, etc.). Static IPs in idle state are billed at ~$0.01/hour. Recommends releasing.

### Idle Custom Image Recommender
**Recommender ID**: `google.compute.image.IdleResourceRecommender`

Identifies custom VM images not used for creating instances in 90+ days. Recommends deleting to save Image Storage costs.

### Idle Load Balancer Recommender
Identifies load balancers with no traffic. Recommends deletion.

---

## Committed Use Discount Recommender

**Recommender ID**: `google.compute.commitment.UsageCommitmentRecommender`

Analyzes GCE instance usage patterns over the past 30 days and recommends optimal CUD purchases:
- Identifies stable, consistent usage that would benefit from 1-year or 3-year commitments
- Calculates the optimal combination of CUDs to maximize savings vs on-demand cost
- Provides projected savings amount and payback period
- Takes existing CUDs into account

**Use this before purchasing any CUD** — the recommender ensures you don't over-commit or under-commit.

---

## Unattended Project Recommender

**Recommender ID**: `google.resourcemanager.projectUtilization.Recommender`

Identifies GCP projects with no activity over the past 30+ days:
- No API calls (no service usage)
- No billing (no costs generated)
- No active VMs, databases, or other resources

Recommends either:
- **Delete the project** if confirmed abandoned
- **Mark as active** if the project should be retained

Useful for organizations with many projects accumulated over time, especially development, sandbox, and proof-of-concept projects.

---

## IAM Recommender (Excess Permissions)

**Recommender ID**: `google.iam.policy.Recommender`

Analyzes Cloud Audit Logs to identify principals (users, service accounts, groups) with IAM roles granting permissions that have never been used in 90 days. Recommends replacing with a smaller, more appropriate role.

**How it works:**
- Policy Analyzer reviews recent activity (90 days) across organization/project IAM policies
- Identifies bindings where granted permissions significantly exceed observed usage
- Suggests a replacement role with just the permissions actually used (principle of least privilege)

**Example recommendation**: Replace `roles/editor` (broad write access) with `roles/cloudsql.admin` (only permissions observed being used).

**Integration**: surfaces in Security Command Center as a security finding in addition to Recommender Hub.

---

## Cloud SQL Recommender

**Recommender ID**: `google.cloudsql.instance.IdleRecommender` and `google.cloudsql.instance.OverprovisionedRecommender`

- **Idle**: identifies Cloud SQL instances with no connections or queries in 30+ days
- **Overprovisioned**: identifies instances where CPU/memory utilization is consistently low; recommends downsizing

---

## GKE Recommenders

Multiple GKE-specific recommenders:
- **Cluster version upgender**: upgrade GKE control plane and node pools to current supported versions
- **Node pool rightsizing**: resize node pools based on observed pod resource requests vs actual usage
- **Autoscaler configuration**: enable Cluster Autoscaler if not enabled on large, underutilized clusters

---

## Active Assist in the Console

**Recommender Hub** (Cloud Console > Active Assist / Recommendations):
- Aggregated view of all recommendations across all services
- Filter by category: cost, security, reliability, performance, sustainability, manageability
- Sort by potential impact (savings amount or risk level)
- One-click apply for some recommendations (VM resize, IP release)
- Track recommendation states across the organization

**Inline recommendations**: many GCP service UIs show recommendations in context (e.g., Compute Engine instance list shows a "Optimize" button for rightsizing candidates).

---

## Programmatic Recommendation Automation

**Pattern**: enumerate active recommendations → filter by threshold → auto-apply low-risk ones → notify for high-risk ones

Common automation scenarios:
1. **Auto-release idle IPs**: safe to automate; no service impact; significant savings in large environments
2. **Auto-delete unattached disks**: verify no snapshots needed first; then auto-delete after 30-day idle period
3. **Notify on VM rightsizing**: create Jira tickets or Slack alerts; require human approval before resizing production VMs
4. **Auto-claim and apply CUD recommendations**: low risk if you trust the recommendation model; verify savings projections

The Recommender API supports pagination, filtering by state, and bulk state transitions.
