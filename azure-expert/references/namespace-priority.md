# Namespace Priority Ranking

Ranked by importance and usage frequency to guide which namespaces to load first when a query is ambiguous, and to inform skill maintenance prioritization.

## Ranking Criteria

Each namespace is scored on a weighted blend of five factors:

| Factor | Description |
|---|---|
| **Adoption breadth** | Estimated % of Azure subscriptions using this service |
| **Architectural centrality** | How many other services depend on or integrate with it |
| **Decision frequency** | How often architects/developers make non-trivial choices about it |
| **Market momentum** | Growth trajectory and active customer investment (2025–26) |
| **Cross-cutting leverage** | Knowing it deeply improves overall Azure proficiency |

---

## Top 30 Namespaces

| Rank | Namespace | Primary Reasoning |
|---|---|---|
| 1 | `security-iam/entra-id` | Identity foundation for every Azure resource. Entra ID (formerly Azure AD) underpins all authentication, authorization, managed identities, and conditional access — no workload exists without it. |
| 2 | `storage/blob` | Used by virtually every Azure subscription. Universal landing zone for data lakes, static websites, backups, artifacts, and VM images. Foundation of ADLS Gen2. |
| 3 | `networking/vnet` | Every production workload lives in a VNet. Subnets, NSGs, routing tables, peering, and Private Endpoints are daily architectural decisions. |
| 4 | `compute/vms` | Dominant IaaS primitive. Largest installed base; basis for VMSS, AKS node pools, and lift-and-shift migrations. |
| 5 | `compute/app-service` | Most common PaaS compute for web workloads. Drives the App Service Plan ecosystem shared by Functions, Logic Apps, and WebJobs. |
| 6 | `management-devops/monitor` | Mandatory observability plane. Azure Monitor, Log Analytics workspaces, and Application Insights are required in every production architecture. |
| 7 | `database/azure-sql` | Most common relational database. Azure SQL Database (General Purpose, Business Critical, Hyperscale) is the default OLTP store for .NET and Java workloads. |
| 8 | `database/cosmos-db` | Default globally distributed NoSQL database. Multi-model API support (SQL, MongoDB, Cassandra, Gremlin, Table) and serverless mode make it the go-to for spiky or global workloads. |
| 9 | `serverless-integration/service-bus` | Standard async enterprise messaging. Premium and Standard tiers, topics/subscriptions, dead-letter queues, and sessions cover the full messaging spectrum. |
| 10 | `management-devops/bicep-arm` | IaC backbone of Azure. Bicep is the preferred authoring format; ARM templates are the deployment substrate. Required knowledge for any Azure governance or automation role. |
| 11 | `security-iam/key-vault` | Universal secrets, certificates, and key management. Nearly every production app references Key Vault for connection strings, API keys, and TLS certificates. |
| 12 | `serverless-integration/api-management` | Standard API gateway for exposing and protecting APIs. Policies, products, and developer portal are non-trivial architectural decisions for any platform team. |
| 13 | `containers/aks` | Standard Kubernetes on Azure. Growing rapidly as organizations standardize on Kubernetes for microservices and platform engineering. |
| 14 | `ml-ai/azure-openai` | Fastest growing service by demand. Azure OpenAI is the primary enterprise entry point for GPT-4, DALL-E, Whisper, and embeddings; GenAI is the #1 architectural initiative for most organizations. |
| 15 | `networking/front-door-cdn` | Global HTTP load balancing, CDN, and WAF combined. Front Door Standard/Premium replaces legacy CDN and Traffic Manager for most new internet-facing deployments. |
| 16 | `analytics/synapse-analytics` | Unified data warehouse and lake analytics. Synapse integrates SQL pools, Spark, Data Explorer, Pipelines, and Link — covers the full analytics stack. |
| 17 | `security-iam/defender-sentinel` | Security posture management (Defender for Cloud) plus cloud-native SIEM/SOAR (Microsoft Sentinel). Required for any enterprise security or compliance architecture. |
| 18 | `serverless-integration/functions` | Core serverless runtime. HTTP, timer, and event-driven triggers; integrates with virtually every Azure service via bindings. |
| 19 | `serverless-integration/event-grid` | Standard event routing fabric. Reacts to Azure resource events and custom events; the glue between services in event-driven architectures. |
| 20 | `security-iam/policy-governance` | Compliance guardrails at scale. Azure Policy, Management Groups, and Blueprints enforce organizational standards; required for enterprise landing zones. |
| 21 | `analytics/data-factory` | Standard ETL/ELT service. 90+ connectors, data flows, and pipeline orchestration make ADF the default for data movement workloads. |
| 22 | `storage/disk` | Block storage for VMs and databases. Managed Disk types (Standard HDD/SSD, Premium SSD, Ultra Disk) and snapshot management are routine VM architecture decisions. |
| 23 | `ml-ai/azure-ml` | Complete ML platform. Teams building custom models use Azure ML for training, deployment pipelines, model registry, and MLOps. |
| 24 | `analytics/event-hubs` | Real-time streaming ingestion at scale. Kafka-compatible, partitioned, and the default IoT and telemetry ingestion gateway. |
| 25 | `management-devops/devops-pipelines` | Azure DevOps Pipelines (and GitHub Actions with Azure) are the standard CI/CD tools for Azure deployments. |
| 26 | `cost-optimization/reservations` | Azure Reservations (1yr/3yr) and Azure Savings Plans provide up to 65% discount on VMs, SQL, Cosmos DB, and other services for steady-state workloads. |
| 27 | `database/redis-cache` | Default caching layer. Azure Cache for Redis (Basic/Standard/Premium/Enterprise) is the standard in-memory cache and session store. |
| 28 | `networking/load-balancing` | Azure Load Balancer (L4) and Application Gateway (L7/WAF) sit in front of nearly every production workload — VMs, VMSS, AKS, and App Service. |
| 29 | `serverless-integration/logic-apps` | Workflow automation and B2B integration. Logic Apps Standard and Consumption tiers plus 400+ connectors cover enterprise integration patterns. |
| 30 | `containers/container-apps` | Serverless containers with built-in KEDA autoscaling. Growing rapidly as teams seek Kubernetes power without cluster management overhead. |

---

## Ranks 31–40 (Honorable Mentions)

| Rank | Namespace |
|---|---|
| 31 | `networking/expressroute-vpn` — hybrid connectivity essential but architecturally straightforward once chosen |
| 32 | `security-iam/managed-identity` — should be #1 best practice but is a concept within Entra ID namespace |
| 33 | `containers/acr` — Azure Container Registry used alongside AKS/Container Apps; decisions are relatively simple |
| 34 | `storage/adls-gen2` — ADLS Gen2 is Blob Storage + hierarchical namespace; covered largely in blob namespace |
| 35 | `analytics/databricks` — Azure Databricks dominates Spark workloads; growing fast but requires Databricks expertise |
| 36 | `networking/private-link` — Private Endpoints are now mandatory for PCI/HIPAA but decision surface is narrow |
| 37 | `compute/container-instances` — ACI is useful for burst/sidecar/init patterns but rarely the primary compute |
| 38 | `management-devops/advisor` — Azure Advisor surfaces recommendations passively; low decision surface area |
| 39 | `database/postgresql-mysql` — Azure Database for PostgreSQL Flexible Server growing as PostgreSQL dominates OSS DB choices |
| 40 | `ml-ai/ai-foundry` — Azure AI Foundry (formerly AI Studio) is the GenAI app development hub; growing rapidly |

---

## Notes on Volatility

- **ml-ai/azure-openai** (#14) is likely to move into the top 10 within 12 months as organizations move GenAI workloads from pilot to production.
- **containers/aks** (#13) and **containers/container-apps** (#30) are both rising; Container Apps may displace ACI and challenge App Service for some PaaS workloads.
- **management-devops/bicep-arm** (#10) reflects the ongoing shift from ARM JSON to Bicep as the primary IaC authoring experience.
- **security-iam** namespaces collectively remain the highest-leverage domain — Entra ID (#1), Key Vault (#11), and Policy/Governance (#20) form a security triad that appears in every architecture review.
- **analytics/synapse-analytics** (#16) faces competition from Microsoft Fabric; expect Fabric to displace Synapse in new architectures by 2027.
