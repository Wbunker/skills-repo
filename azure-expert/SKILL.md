---
name: azure-expert
description: >
  Deep Microsoft Azure expertise for architecture, implementation, troubleshooting, and best
  practices across the full Azure service catalog (200+ services). Use when the user asks about:
  designing or reviewing Azure architectures, selecting Azure services for a use case, implementing
  Azure infrastructure (Bicep, ARM Templates, Terraform), IAM and security policies (Entra ID, RBAC,
  Azure Policy), cost optimization, migration to Azure, serverless patterns, container orchestration
  (AKS, Container Apps), data pipelines and analytics (Synapse, Data Factory, Event Hubs, Databricks),
  networking (VNet, Front Door, ExpressRoute, Azure Firewall), machine learning on Azure (Azure OpenAI,
  Azure Machine Learning, AI Foundry, AI Services), compliance and governance, or any specific Azure
  service (Virtual Machines, Azure Blob Storage, Azure SQL, Cosmos DB, etc.). Also use for Azure
  Well-Architected Framework reviews and Azure certification study guidance (AZ-900, AZ-104, AZ-305,
  AZ-400, etc.).
---

# Azure Expert

## Core Approach

1. Clarify requirements (workload type, scale, latency, budget, compliance, existing stack, hybrid/on-prem connectivity)
2. Select services using the **service selection principles** below
3. Design with the Azure Well-Architected Framework pillars in mind
4. Provide concrete implementation guidance (Bicep preferred; ARM Templates or Terraform if specified)
5. Call out trade-offs, costs, and operational complexity honestly

## Service Selection Principles

- **Managed over self-managed** unless control/cost trade-off clearly favors self-managed
- **Serverless first** for unpredictable or spiky workloads (Azure Functions, Container Apps, Cosmos DB serverless, Azure SQL Hyperscale Serverless)
- **Right-size the database**: relational → Azure SQL / PostgreSQL Flexible Server, key-value/document → Cosmos DB, cache → Azure Cache for Redis, analytics → Synapse Analytics
- **Avoid over-engineering**: a simple Service Bus + Azure Functions pattern beats a full event mesh for most use cases
- **Region and zone strategy**: always design for zone-redundant deployments; multi-region only when RTO/RPO demands it; use paired regions for DR

## Reference Files

Reference files use a **2-tier system**: load a domain index first to identify the specific namespace file needed, then load only that namespace file.

When a query touches multiple namespaces and context is limited, prioritize loading higher-ranked namespaces first — see [namespace-priority.md](references/namespace-priority.md) for the ranked list and criteria.

**Tier 1 — Domain indexes** (load to navigate to the right namespace):

| Domain Index | Load when... |
|---|---|
| [services-catalog.md](references/services-catalog.md) | User asks "what Azure service does X", service comparison, full catalog overview |
| [compute.md](references/compute.md) | Virtual Machines, VM Scale Sets, App Service, Azure Functions, AKS, Container Instances, Batch, Azure Spring Apps |
| [storage.md](references/storage.md) | Blob Storage, Azure Files, Managed Disks, Data Lake Storage Gen2, Azure Backup, Azure NetApp Files |
| [database.md](references/database.md) | Azure SQL, SQL Managed Instance, Cosmos DB, Azure Database for PostgreSQL/MySQL, Azure Cache for Redis, Table Storage |
| [networking.md](references/networking.md) | VNet, Load Balancer, Application Gateway, Front Door, CDN, ExpressRoute, VPN Gateway, Azure Firewall, Bastion, Private Link, DNS, DDoS Protection, Traffic Manager, NAT Gateway |
| [security-iam.md](references/security-iam.md) | Microsoft Entra ID, RBAC, Managed Identity, Key Vault, Defender for Cloud, Sentinel, Azure Policy, Management Groups, Privileged Identity Management |
| [ml-ai.md](references/ml-ai.md) | Azure OpenAI Service, Azure Machine Learning, Azure AI Foundry, AI Services (Vision, Speech, Language, Document Intelligence, Translator, Face) |
| [analytics.md](references/analytics.md) | Azure Synapse Analytics, Azure Data Factory, Event Hubs, Stream Analytics, Azure Databricks, Microsoft Purview, Power BI Embedded, Data Share |
| [management-devops.md](references/management-devops.md) | Azure Monitor, Log Analytics, Application Insights, Azure DevOps, GitHub Actions with Azure, Bicep, ARM Templates, Azure Advisor, Azure Policy |
| [serverless-integration.md](references/serverless-integration.md) | Azure Functions, Logic Apps, API Management, Service Bus, Event Grid, Azure Relay, Durable Functions |
| [containers.md](references/containers.md) | AKS, Azure Container Apps, Azure Container Registry, Container Instances, Azure Arc |
| [cost-optimization.md](references/cost-optimization.md) | Azure Reservations, Savings Plans, Azure Advisor, Microsoft Cost Management, Azure Hybrid Benefit, spot/preemptible VMs |
| [developer-tools.md](references/developer-tools.md) | Azure CLI, Azure PowerShell, Cloud Shell, Azure Portal, Visual Studio Code Azure extensions, Azure DevTest Labs |
| [iot.md](references/iot.md) | IoT Hub, IoT Edge, Azure Digital Twins, Event Hubs (IoT ingestion), Device Provisioning Service, RTOS |
| [media-services.md](references/media-services.md) | Azure Media Services, Video Indexer, Azure CDN for media |
| [migration-transfer.md](references/migration-transfer.md) | Azure Migrate, Azure Database Migration Service, Azure Data Box, Storage Migration Service, Azure Arc |
| [business-applications.md](references/business-applications.md) | Microsoft 365 integrations, Power Platform (Power Apps/Automate/BI), Dynamics 365, Azure Communication Services |
| [end-user-computing.md](references/end-user-computing.md) | Azure Virtual Desktop, Windows 365, Remote Desktop Services |
| [front-end-web-mobile.md](references/front-end-web-mobile.md) | Static Web Apps, Azure App Service, Azure Notification Hubs, Azure Spatial Anchors, Azure PlayFab |
| [healthcare.md](references/healthcare.md) | Azure Health Data Services (FHIR, DICOM, MedTech), Azure Health Bot, Text Analytics for health |
| [game-technology.md](references/game-technology.md) | Azure PlayFab, Azure gaming architecture (AKS for multiplayer, Cosmos DB for leaderboards) |

**Tier 2 — Namespace files**: Each domain index lists specific namespace files (e.g., `compute/vms-capabilities.md`, `compute/vms-cli.md`). Load only the namespace file(s) relevant to the user's question.

## Azure Well-Architected Framework Quick Reference

| Pillar | Key Questions |
|---|---|
| Reliability | Zone-redundant? Multi-region DR? Backup/restore tested? Auto-healing? Circuit breakers? |
| Security | Least privilege? Managed Identity over service principals? Private Endpoints? Encryption at rest/transit? Zero Trust? |
| Cost Optimization | Reservations/Savings Plans? Azure Hybrid Benefit? Right-sizing? Advisor recommendations? Autoscale? |
| Operational Excellence | IaC (Bicep)? CI/CD with Azure DevOps or GitHub Actions? Structured logging to Log Analytics? Runbooks? |
| Performance Efficiency | Right SKU? Caching (Redis)? CDN (Front Door)? Autoscale? Zone-local data access? |
| Sustainability | Efficient VM sizes? Autoscale to zero? Data lifecycle policies? Spot/Preemptible for interruptible work? |

## Common Architecture Patterns

**Web Application**: Azure Front Door → App Service or AKS → Azure SQL or Cosmos DB → Blob Storage (static assets)

**Event-Driven**: Event Grid → Azure Functions → Service Bus (with DLQ) → downstream services

**Data Lake**: ADLS Gen2 (raw/processed/curated) → Data Factory ETL → Synapse Analytics → Power BI

**ML Platform**: ADLS Gen2 → Azure ML (training) → Azure ML Endpoints or Azure OpenAI → API Management

**Microservices**: AKS → Internal Load Balancer → Azure SQL per service → Service Bus for async

**Batch Processing**: Blob Storage event trigger → Azure Functions or Azure Batch → results to Blob/Synapse

**Real-Time Streaming**: Event Hubs → Stream Analytics or Databricks → Cosmos DB/Synapse/ADLS Gen2

## Bicep Conventions

Prefer Bicep for IaC examples unless the user specifies ARM JSON or Terraform:

```bicep
// Prefer Bicep over ARM JSON; use modules for reusable patterns
// Use param with @allowed/@minLength/@maxLength decorators for validation
// Use targetScope = 'subscription' or 'managementGroup' for policy/RBAC assignments
// Store sensitive values in Key Vault; reference with keyVaultRef in param files
// Use Azure Verified Modules (AVM) from registry.terraform.io or Bicep registry
// Prefer user-assigned managed identity over service principals for workload identity
// Tag all resources with environment, owner, cost-center using a tags module
```
