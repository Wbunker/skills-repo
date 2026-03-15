# GCP Pricing & Discounts — Capabilities

## Pricing Model

GCP uses a pay-as-you-go model with no upfront commitment required (unless purchasing CUDs). Key principles:

- **Compute**: billed per second with a 1-minute minimum for most GCE instance types
- **Storage**: per-GB-month for persistent disk and Cloud Storage; tiered pricing for storage classes
- **Networking egress**: per-GB for outbound traffic to internet or other regions; ingress is free
- **Serverless**: per-request and per-GB-second (Cloud Functions, Cloud Run); generous free tiers
- **Managed services**: varied pricing (per-operation, per-unit, or capacity-based)
- **Pricing Calculator**: cloud.google.com/products/calculator for detailed cost estimates before deployment

---

## Sustained Use Discounts (SUDs)

Automatic discounts applied to GCE VMs and GKE nodes that run for a significant portion of the billing month. No commitment or opt-in required.

**How it works:**
- Discount kicks in incrementally as usage accumulates during the month
- The more of the month a VM runs, the larger the discount on that incremental usage
- At 100% of the month: up to **~30% discount** vs. on-demand price (varies by machine family)
- GCP combines VM usage across the project by inferring equivalent vCPU and memory usage

**Eligible machine families:**
- N1 (general purpose, Intel Skylake/Broadwell)
- N2 (general purpose, Intel Cascade Lake)
- N2D (general purpose, AMD EPYC)
- E2 (cost-optimized general purpose)
- C2 (compute-optimized) — **only CUDs apply, NOT SUDs**
- M1/M2 (memory-optimized) — only CUDs apply, NOT SUDs

**NOT eligible for SUDs:**
- Spot VMs / Preemptible VMs (already heavily discounted)
- A2 (NVIDIA A100 GPU instances) — use CUDs
- G2 (NVIDIA L4 GPU instances) — use CUDs
- Custom machine types outside eligible families

**Important**: SUDs do NOT stack on top of CUDs for the same resource. CUD pricing is applied first; if a resource is covered by a CUD, it does not additionally receive SUD.

---

## Committed Use Discounts (CUDs)

CUDs allow you to commit to a level of resource usage in exchange for significantly discounted prices. Two types:

| Type | Term Options | Discount Range | Covers |
|---|---|---|---|
| Resource-based CUD | 1 year or 3 year | 37% (1yr) to 55% (3yr) vs on-demand | vCPU and memory in a specific region; applies to GCE and GKE nodes |
| Spend-based CUD | 1 year or 3 year | 25% (1yr) to 35% (3yr) vs on-demand | Minimum $/hour spend commitment; covers Cloud SQL, Cloud Run, GKE Autopilot, Vertex AI training |

**Resource-based CUDs (Compute):**
- Commit to a specific number of vCPUs and GB of memory in a region
- Automatically applied to matching VM usage across the project (and optionally shared with a billing account)
- Can share CUDs across projects in a billing account (CUD sharing must be enabled)
- Machine types covered: N1, N2, N2D, E2, C2, M1, M2, A2, G2
- GPU CUDs available separately for A100/L4/T4
- TPU CUDs available for Cloud TPU pods

**Spend-based CUDs:**
- Commit to spending at least $X/hour on a specific service in a region
- Flexible — applies to whatever usage occurs up to the committed spend level
- Useful when you cannot predict exact resource amounts but know overall spend level
- Available services: Cloud SQL (per vCPU/memory), Cloud Run (per vCPU-second/memory-second), GKE Autopilot (per vCPU/memory), Vertex AI training

**CUD purchase considerations:**
- Billed whether you use the resource or not (use Recommender to right-size before committing)
- CUDs are per-region; purchase in each region where you have significant workloads
- Cannot be cancelled once purchased; can be modified (upsize) in some cases
- Review Active Assist CUD recommendations before purchasing

---

## Spot VMs (and Preemptible VMs)

**Spot VMs** are the current generation of discounted interruptible VMs. Preemptible VMs are the legacy equivalent (same pricing, slightly different behavior).

| Feature | Spot VM | Preemptible VM (legacy) |
|---|---|---|
| Discount | Up to 91% vs on-demand | Up to 91% vs on-demand |
| Max runtime | No fixed max | 24-hour max runtime |
| Preemption notice | 30 seconds | 30 seconds |
| Termination action | STOP or DELETE | Always terminated |
| Availability | Not guaranteed; varies by region/zone | Not guaranteed |

**Best use cases for Spot VMs:**
- Batch data processing jobs (Dataflow, BigQuery jobs with BQ Reservations, Spark on Dataproc)
- CI/CD build workers
- Fault-tolerant HPC workloads
- Pre-training ML jobs with checkpoint/resume (Vertex AI training with Spot)
- Rendering pipelines
- Load testing

**NOT suitable for:**
- Web servers, APIs, databases, or any latency-sensitive or stateful service
- Jobs that cannot tolerate interruption without restart logic

**Managed Instance Groups (MIGs) with Spot:**
- Use `--instance-redistribution-type=PROACTIVE` or `NONE` with Spot MIGs
- Spot mix policy: define a base % of standard VMs and target % of Spot VMs
- MIG automatically replaces preempted instances when Spot capacity becomes available
- Use stateful MIGs to preserve instance state across preemptions

---

## Free Tier (Always Free Products)

Monthly free usage that does not expire (not trial credits):

| Service | Free Tier Amount |
|---|---|
| Compute Engine | 1 e2-micro instance (us-east1, us-west1, or us-central1), 30GB HDD, 1GB egress |
| Cloud Storage | 5GB Standard storage (US regions), 1GB egress to Americas per month |
| BigQuery | 1TB of query processing per month; 10GB storage per month |
| Cloud Functions (1st gen) | 2 million invocations/month; 400,000 GB-seconds; 200,000 GHz-seconds |
| Cloud Run | 2 million requests/month; 360,000 vCPU-seconds; 180,000 GB-seconds |
| Cloud Firestore | 1GB storage; 50,000 reads; 20,000 writes; 20,000 deletes per day |
| Pub/Sub | 10GB messages per month |
| Secret Manager | 6 active secret versions; 10,000 access operations |
| Cloud Build | 120 build-minutes per day |

Free tier does not apply to resources in non-eligible regions. Org-level policies may restrict free tier usage in enterprise accounts.

---

## Egress Pricing

Understanding GCP data egress costs is critical for cost optimization:

| Traffic Type | Cost |
|---|---|
| Ingress (into GCP) | Free |
| Same zone (internal IP) | Free |
| Same region, different zones (internal IP) | $0.01/GB each direction |
| Inter-region within GCP (internal IP) | $0.01–$0.08/GB depending on regions |
| Internet egress (first 1TB/month) | ~$0.08–$0.12/GB depending on destination |
| Internet egress (1–10TB/month) | ~$0.06–$0.08/GB (tiered discount) |
| Internet egress via Cloud Interconnect | ~$0.02–$0.05/GB (significantly reduced) |
| Cloud CDN egress to internet | Tiered; cheaper than direct egress for cacheable content |

**Cost reduction strategies:**
- Use **Private Google Access** so VMs without external IPs can reach Google APIs without internet egress charges
- Use **Cloud Interconnect** (Dedicated or Partner) for high-volume on-premises-to-GCP traffic to reduce egress vs internet
- Use **Cloud CDN** for static content delivery — CDN egress is cheaper than origin egress
- Co-locate compute and data in the same region to avoid inter-region charges
- Use **VPC Service Controls** to prevent accidental exfiltration that would incur egress charges

---

## BigQuery Pricing

BigQuery has two pricing models that can be mixed:

**On-Demand (Query) Pricing:**
- $6.25 per TB of data processed (first 1TB/month free)
- Only pay for queries that run; no idle cost for storage
- Best for variable/unpredictable query workloads

**Capacity Pricing (Editions):**
| Edition | Autoscaling | Features | Price |
|---|---|---|---|
| Standard | Yes (0 to max slots) | Core SQL, BI Engine | $0.04/slot-hour |
| Enterprise | Yes | + CMEK, column-level security, Authorized Views | $0.06/slot-hour |
| Enterprise Plus | Yes | + Reserved slots with 1-year CUD, BI Acceleration | $0.10/slot-hour |

- Purchase baseline slots (committed) + enable autoscale for burst capacity
- Use **slot reservations** to allocate capacity to specific projects/teams
- 100 slots baseline is the minimum for Standard edition

**Storage Pricing:**
| Storage Class | Price |
|---|---|
| Active storage (modified in last 90 days) | $0.02/GB/month |
| Long-term storage (not modified in 90+ days) | $0.01/GB/month (auto-applied) |
| Cross-region replication | Additional per-GB-month |

**Cost optimization for BigQuery:**
- Use **columnar selection** (SELECT only needed columns) to reduce bytes processed
- **Partition tables** by date/timestamp column; use partition filters in WHERE clauses
- **Cluster tables** on high-cardinality filter columns after partitioning
- Use **materialized views** for repeated aggregation queries
- Enable **BI Engine reservation** (in-memory) to eliminate query cost for BI tools
- Use **scheduled queries** to pre-aggregate data overnight
- Use **BigQuery Omni** (multi-cloud) instead of moving data when querying AWS/Azure data

---

## Networking Service Costs

Key GCP networking services with per-request or per-GB charges:

| Service | Key Pricing Dimension |
|---|---|
| Cloud NAT | Per-hour gateway + per-GB processed |
| Cloud Armor | Per policy per month + per million requests |
| Cloud CDN | Per-GB cache egress (tiered) + per-million cache lookups |
| Global External HTTP(S) Load Balancer | Per-hour forwarding rule + per-GB processed |
| Cloud VPN | Per-tunnel-hour |
| Cloud Interconnect | Per-VLAN attachment hour + per-GB egress |
| Cloud DNS | Per-million queries + per-managed-zone-month |
| Private Service Connect | Per-endpoint + per-GB |

**Private Google Access**: enables VMs with only internal IPs to access Google APIs (Cloud Storage, BigQuery, etc.) without traversing the internet, avoiding external egress charges. Enable on subnet with `--enable-private-ip-google-access`.
