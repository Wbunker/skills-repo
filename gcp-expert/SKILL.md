---
name: gcp-expert
description: >
  Deep Google Cloud Platform (GCP) expertise for architecture, implementation, troubleshooting,
  and best practices across the full GCP service catalog (200+ services). Use when the user asks
  about: designing or reviewing GCP architectures, selecting GCP services for a use case,
  implementing GCP infrastructure (Terraform, Deployment Manager, or Pulumi), IAM and security
  policies, cost optimization, migration to GCP, serverless patterns, container orchestration
  (GKE/Cloud Run), data pipelines and analytics (BigQuery, Dataflow, Pub/Sub), networking (VPC,
  Cloud Load Balancing, Cloud Interconnect), machine learning on GCP (Vertex AI, Gemini, AutoML),
  compliance and governance, or any specific GCP service (Compute Engine, Cloud Storage, Cloud SQL,
  Bigtable, etc.). Also use for Google Cloud Architecture Framework reviews and GCP certification
  study guidance (Associate Cloud Engineer, Professional Cloud Architect, etc.).
---

# GCP Expert

## Core Approach

1. Clarify requirements (workload type, scale, latency, budget, compliance, existing stack)
2. Select services using the **service selection principles** below
3. Design with the Google Cloud Architecture Framework pillars in mind
4. Provide concrete implementation guidance (Terraform preferred; Deployment Manager or Pulumi if specified)
5. Call out trade-offs, costs, and operational complexity honestly

## Service Selection Principles

- **Managed over self-managed** unless control/cost trade-off clearly favors self-managed
- **Serverless first** for unpredictable or spiky workloads (Cloud Run, Cloud Functions, Spanner Serverless, Firestore, BigQuery on-demand)
- **Right-size the database**: relational → Cloud SQL/AlloyDB, globally distributed → Spanner, document → Firestore, wide-column/time-series → Bigtable, analytics → BigQuery
- **Avoid over-engineering**: a simple Pub/Sub + Cloud Functions pattern beats a full event mesh for most use cases
- **Region and zone strategy**: always design for multi-zone; multi-region only when RPO/RTO demands it

## Reference Files

Reference files use a **2-tier system**: load a domain index first to identify the specific namespace file needed, then load only that namespace file.

When a query touches multiple namespaces and context is limited, prioritize loading higher-ranked namespaces first — see [namespace-priority.md](references/namespace-priority.md) for the ranked list and criteria.

**Tier 1 — Domain indexes** (load to navigate to the right namespace):

| Domain Index | Load when... |
|---|---|
| [services-catalog.md](references/services-catalog.md) | User asks "what GCP service does X", needs service comparison, or wants a full catalog overview |
| [compute.md](references/compute.md) | Compute Engine, Cloud Run, Cloud Functions, GKE, App Engine, Cloud Batch, Spot VMs, Sole-Tenant Nodes, Bare Metal Solution |
| [storage.md](references/storage.md) | Cloud Storage, Persistent Disk, Hyperdisk, Filestore, NetApp Cloud Volumes, Backup and DR Service |
| [database.md](references/database.md) | Cloud SQL, Spanner, Firestore, Bigtable, AlloyDB, Memorystore, Datastore, Database Migration Service |
| [networking.md](references/networking.md) | VPC, Cloud Load Balancing, Cloud CDN, Cloud DNS, Cloud NAT, Cloud Armor, Cloud Interconnect, Cloud VPN, Network Intelligence Center, Private Service Connect |
| [security-iam.md](references/security-iam.md) | Cloud IAM, Cloud KMS, Secret Manager, Security Command Center, BeyondCorp Enterprise, Certificate Authority Service, VPC Service Controls, Cloud DLP, Binary Authorization |
| [ml-ai.md](references/ml-ai.md) | Vertex AI, Gemini API, AutoML, Document AI, Vision AI, Natural Language AI, Translation AI, Speech-to-Text, Dialogflow, Contact Center AI |
| [analytics.md](references/analytics.md) | BigQuery, BigQuery ML, Dataflow, Dataproc, Pub/Sub, Looker, Cloud Composer, Cloud Data Fusion, Dataplex, Analytics Hub, Datastream |
| [management-devops.md](references/management-devops.md) | Cloud Monitoring, Cloud Logging, Cloud Trace, Cloud Profiler, Cloud Build, Cloud Deploy, Terraform on GCP, Config Connector, Cloud Audit Logs |
| [serverless-integration.md](references/serverless-integration.md) | Cloud Functions, Cloud Run, Eventarc, Workflows, Pub/Sub, Cloud Tasks, Cloud Scheduler, Apigee, Application Integration |
| [containers.md](references/containers.md) | GKE, GKE Autopilot, Cloud Run, Artifact Registry, Cloud Build, Cloud Deploy, Anthos/GKE Enterprise, Config Sync, Policy Controller |
| [cost-optimization.md](references/cost-optimization.md) | Committed Use Discounts, Sustained Use Discounts, Cloud Billing, Budget Alerts, Recommender, rightsizing, lifecycle policies |
| [developer-tools.md](references/developer-tools.md) | Cloud SDK, Cloud Shell, Cloud Source Repositories, Artifact Registry, Cloud Workstations, Gemini Code Assist, Firebase Studio |
| [iot.md](references/iot.md) | Pub/Sub (IoT ingestion), Edge TPU/Coral, IoT Core (deprecated 2023), IoT device patterns |
| [media-services.md](references/media-services.md) | Transcoder API, Video Intelligence API, Live Stream API, Video Stitcher API |
| [migration-transfer.md](references/migration-transfer.md) | Migrate to Virtual Machines, Migrate to Containers, Database Migration Service, Storage Transfer Service, Transfer Appliance, BigQuery Data Transfer Service |
| [business-applications.md](references/business-applications.md) | Google Workspace APIs, AppSheet, Contact Center AI, Duet AI for Google Workspace, Looker |
| [end-user-computing.md](references/end-user-computing.md) | Chrome Enterprise, Cloud Workstations, virtual desktops on GCP |
| [front-end-web-mobile.md](references/front-end-web-mobile.md) | Firebase, Google Maps Platform, Identity Platform, Cloud Endpoints, Firebase App Distribution, Firebase Test Lab |
| [healthcare.md](references/healthcare.md) | Cloud Healthcare API, FHIR, DICOM, HL7v2, Vertex AI for Healthcare, Healthcare Natural Language API, Life Sciences API |
| [game-technology.md](references/game-technology.md) | Agones (GKE game servers), Cloud Spanner for games, Open Match, Firebase game backend |

**Tier 2 — Namespace files**: Each domain index lists specific namespace files (e.g., `compute/gce-capabilities.md`, `compute/gce-cli.md`). Load only the namespace file(s) relevant to the user's question.

## Google Cloud Architecture Framework Quick Reference

| Pillar | Key Questions |
|---|---|
| System Design | Right service chosen? Scalability approach defined? Reliability patterns applied? Regional vs global load balancing appropriate for the SLA? |
| Operational Excellence | IaC via Terraform or Config Connector? CI/CD via Cloud Build and Cloud Deploy? Observability via Cloud Monitoring, Logging, and Trace? Runbooks in place? |
| Security, Privacy & Compliance | IAM least privilege? Service accounts scoped tightly per workload? CMEK encryption? VPC Service Controls for data exfiltration prevention? Compliance scope (HIPAA/PCI/FedRAMP/SOC 2)? |
| Reliability | Multi-zone deployment? SLOs defined and tracked? Error budgets in use? Chaos engineering practiced? Cloud Load Balancing health checks configured? |
| Cost Optimization | Committed Use Discounts purchased? Sustained Use Discounts leveraged? Resources rightsized? Cloud Storage lifecycle policies set? Spot/Preemptible VMs used for batch? |
| Performance Optimization | Caching strategy (Memorystore/Cloud CDN)? Right database for access pattern? Right compute shape (GCE vs Cloud Run vs GKE)? GPU/TPU provisioned for ML workloads? |

## Common Architecture Patterns

**Web Application**: Cloud Load Balancing → Cloud Run or GKE → Cloud SQL or Firestore → Cloud Storage (static assets)

**Event-Driven**: Pub/Sub → Cloud Functions or Cloud Run → Eventarc → downstream services

**Data Lake**: Cloud Storage (raw/processed/curated zones) → Dataflow ETL → BigQuery → Looker or Looker Studio

**ML Platform**: Cloud Storage → Vertex AI Training → Vertex AI Endpoints → Apigee or Cloud Endpoints

**Microservices**: GKE → Cloud Load Balancing (internal) → Cloud SQL per service → Pub/Sub for async decoupling

**Batch Processing**: Cloud Storage event trigger → Cloud Functions or Cloud Batch → results to Cloud Storage or BigQuery

**Real-Time Streaming**: Pub/Sub → Dataflow (Apache Beam) → BigQuery or Bigtable or Elasticsearch on GCE

## Terraform Conventions

Prefer Terraform for IaC examples unless the user specifies otherwise:

```hcl
# Use google provider with project/region/zone variables
# Prefer google_* resources over google_beta_* unless the feature is not yet GA
# Use modules for reusable patterns (VPC module, GKE cluster module, etc.)
# Use workspaces or separate state files per environment (dev/staging/prod)
# Use google_project_iam_member over google_project_iam_binding to avoid unintended permission drift
# Store remote state in a Cloud Storage backend with versioning enabled
# Use google_secret_manager_secret_version data source instead of hardcoding credentials
```
