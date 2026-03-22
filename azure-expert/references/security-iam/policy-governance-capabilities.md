# Azure Policy & Governance — Capabilities

## Overview

Azure governance spans policy enforcement (Azure Policy), organizational hierarchy (Management Groups), resource lifecycle management (Deployment Stacks), and data governance (Microsoft Purview). Together, these services implement guardrails that ensure compliance, cost control, and security at scale across subscriptions and teams.

---

## Azure Policy

Azure Policy is a governance service that evaluates Azure resources against rules (definitions) and enforces organizational standards. It is the primary mechanism for guardrails-as-code in enterprise Azure deployments.

### Policy Definitions

A policy definition is a JSON document that specifies a rule and an effect. Structure:

```json
{
  "properties": {
    "displayName": "Require tag on resource groups",
    "policyType": "Custom",
    "mode": "All",
    "description": "Requires the specified tag on all resource groups",
    "parameters": {
      "tagName": {
        "type": "String",
        "metadata": { "displayName": "Tag Name" }
      }
    },
    "policyRule": {
      "if": {
        "allOf": [
          { "field": "type", "equals": "Microsoft.Resources/subscriptions/resourceGroups" },
          { "field": "[concat('tags[', parameters('tagName'), ']')]", "exists": "false" }
        ]
      },
      "then": { "effect": "deny" }
    }
  }
}
```

### Policy Modes

| Mode | What It Evaluates |
|---|---|
| `All` | Resource groups and all resource types |
| `Indexed` | Only resource types that support tags and location |
| `Microsoft.Kubernetes.Data` | Kubernetes admission controller (Gatekeeper) |
| `Microsoft.KeyVault.Data` | Key Vault keys, secrets, certificates |
| `Microsoft.Network.Data` | Azure Virtual Network Manager |

### Policy Effects

Effects determine what happens when the `if` condition matches:

| Effect | When Used | Description |
|---|---|---|
| **Deny** | Enforcement | Prevents the create/update operation; returns 403 |
| **Audit** | Assessment | Allows operation; marks resource as non-compliant; logs audit event |
| **Append** | Modification | Adds fields to the request (e.g., add missing tags on create) |
| **Modify** | Modification | Add, update, or remove tags or properties; can remove existing values |
| **DeployIfNotExists (DINE)** | Remediation | If resource exists and lacks specified resource, deploy it (e.g., enable diagnostic settings) |
| **AuditIfNotExists (AINE)** | Assessment | Audit if a related resource doesn't exist (e.g., missing diagnostic settings) |
| **DenyAction** | Enforcement | Block specific delete or action operations (not create/update) |
| **Manual** | Compliance | For controls that require manual verification; no automated effect |
| **Disabled** | Testing | Policy evaluates but takes no action |

**Processing order** (multiple effects): Disabled → Append → Deny → Audit → Modify → DeployIfNotExists/AuditIfNotExists

### Policy Conditions and Fields

Common `if` conditions:

```json
// Field conditions
{ "field": "location", "equals": "eastus" }
{ "field": "location", "in": ["eastus", "westus"] }
{ "field": "location", "notIn": ["eastasia"] }
{ "field": "tags['Environment']", "exists": "true" }
{ "field": "tags['Environment']", "equals": "Production" }
{ "field": "type", "equals": "Microsoft.Compute/virtualMachines" }
{ "field": "Microsoft.Compute/virtualMachines/storageProfile.osDisk.managedDisk.storageAccountType", "equals": "Premium_LRS" }
{ "field": "kind", "equals": "StorageV2" }
{ "count": { "field": "Microsoft.Network/virtualNetworks/subnets[*]", "where": {"field": "Microsoft.Network/virtualNetworks/subnets[*].routeTable.id", "exists": "false"} }, "greater": 0 }
```

Logical operators: `allOf` (AND), `anyOf` (OR), `not`

### Policy Initiatives (Policy Sets)

An initiative groups multiple policy definitions for a common goal:
- A single assignment enforces all included definitions
- Parameters can be passed through from initiative to individual definitions
- Built-in initiatives include CIS Microsoft Azure Foundations Benchmark, NIST SP 800-53, PCI-DSS v4, HIPAA/HITRUST, ISO 27001, SOC 2, Azure Security Benchmark

### Policy Assignments

Assignments apply a definition or initiative to a scope:

| Property | Description |
|---|---|
| **Scope** | Management Group, Subscription, Resource Group, or Resource |
| **Exclusions** | Specific resources, resource groups, or subscriptions to exclude |
| **Parameters** | Override definition parameters for this assignment |
| **Non-compliance message** | Custom message shown when resource is non-compliant |
| **Enforcement mode** | `Default` (enforces deny effects) or `DoNotEnforce` (audit only, no deny) |
| **Managed Identity** | Required for DINE and Modify effects; assigned appropriate role for remediation |

### Remediation Tasks

For `DeployIfNotExists` and `Modify` effects, existing non-compliant resources require remediation:
- Create a remediation task manually or automatically trigger on compliance state change
- Remediation task uses the policy assignment's managed identity to apply changes
- Progress and errors visible in the remediation task status
- Concurrency: 10 concurrent remediation tasks per subscription

### Compliance State

| State | Description |
|---|---|
| Compliant | Resource satisfies all conditions of the policy |
| Non-compliant | Resource violates the policy rule |
| Exempt | Resource has been explicitly exempted from the policy |
| Conflict | Multiple conflicting policies apply |
| Error | Policy evaluation failed (misconfiguration) |

Compliance is evaluated:
- On resource create/update
- On policy assignment create/update
- On demand (trigger via CLI or portal)
- Every 24 hours (recurring evaluation cycle)

### Policy Exemptions

Exempt specific resources or scopes from a policy assignment without removing the assignment:
- **Waiver**: resource is known non-compliant but accepted (permanent waiver)
- **Mitigated**: compensating controls are in place outside Azure Policy scope
- Expiry date: exemptions can be time-bounded
- Exempted resources not counted in compliance percentage

---

## Management Groups

Management Groups organize Azure subscriptions into a hierarchy for policy and RBAC inheritance.

### Hierarchy

```
Root Management Group (tenant root, cannot be deleted)
├── Platform Management Group
│   ├── Identity Subscription
│   ├── Connectivity Subscription (Hub networking)
│   └── Management Subscription (Log Analytics, Backup)
├── Landing Zones Management Group
│   ├── Corp Landing Zones (MG)
│   │   ├── Corp Subscription A
│   │   └── Corp Subscription B
│   └── Online Landing Zones (MG)
│       ├── Online Subscription A
│       └── Online Subscription B
└── Sandboxes Management Group
    └── Dev Subscription
```

- Maximum depth: 6 levels (not including root)
- Maximum management groups per tenant: 10,000
- One subscription can belong to only one management group at a time
- RBAC and Policy assigned at MG scope inherit to all child MGs and subscriptions

### Azure Landing Zone (ALZ) / Cloud Adoption Framework

Microsoft prescribes a reference architecture (Azure Landing Zone):
- Policy-driven governance using policy assignments at each MG level
- **Platform MG**: policies for centralized logging, security monitoring, network hubs
- **Landing Zones MG**: workload policies for tagging, allowed regions, SKU restrictions
- **Corp/Online split**: Corp = private VNet connectivity; Online = internet-facing without hub connectivity
- Bicep/Terraform modules for automated ALZ deployment

---

## Subscription Organization Best Practices

### Tagging Strategy

Consistent tagging enables cost allocation, automation, and compliance:

| Tag | Example Values | Purpose |
|---|---|---|
| `Environment` | `Prod`, `Dev`, `Test`, `Staging` | Cost allocation, policy scope |
| `CostCenter` | `CC-1234` | Financial chargeback |
| `Owner` | `jane.smith@contoso.com` | Accountability |
| `Project` | `phoenix-v2` | Project tracking |
| `Team` | `platform-engineering` | Team accountability |
| `DataClassification` | `Public`, `Internal`, `Confidential` | Security policies |
| `Criticality` | `High`, `Medium`, `Low` | SLA and backup policies |

**Tag inheritance via Policy Modify effect**: assign initiative at subscription level to propagate required tags from subscription to resource groups, and from resource groups to resources.

---

## Azure Deployment Stacks

Deployment Stacks manage a set of related Azure resources as a single unit, with **deny assignments** that prevent unauthorized deletion or modification of managed resources. Deployment Stacks replace Azure Blueprints (deprecated).

### Key Features

- **Deny assignments**: automatically created to prevent deletion of managed resources by non-owners
- **Managed resources**: tracked as a group; lifecycle (create, update, delete) managed together
- **Detach or delete**: on stack deletion, choose to detach resources (keep) or delete resources (remove)
- **ARM/Bicep templates**: stacks use the same template format as regular deployments
- **Scopes**: Stack per resource group (`az stack group`), per subscription (`az stack sub`), or per management group (`az stack mg`)
- **Deny settings mode**: `None` (no deny), `DenyDelete` (prevent delete), `DenyWriteAndDelete` (prevent modify+delete)

### Use Cases

- Platform team deploys shared infrastructure (VNet, Key Vault, Log Analytics) as a stack; deny assignments prevent accidental deletion by app teams
- Landing Zone compliance: deploy required resources (diagnostic settings, NSG flow logs, Defender) as a stack per subscription
- Replaces Azure Blueprints which were complex and are now deprecated

---

## Microsoft Purview (Data Governance)

Microsoft Purview is a unified data governance platform for multi-cloud and on-premises data estates. It provides data catalog, data lineage, data classification, and governance policy capabilities.

### Core Capabilities

| Capability | Description |
|---|---|
| **Data Map** | Automated scanning of data sources; catalogues data assets with schema and metadata |
| **Data Catalog** | Business-friendly search and discovery of data assets; curated glossary terms |
| **Data Lineage** | Tracks data movement and transformation (from source to sink, through pipelines) |
| **Data Classification** | Automatic sensitive data discovery using built-in (PII, financial) and custom classifiers |
| **Data Policy** | Centrally manage access to data assets (Azure Storage, SQL, Azure Arc-enabled SQL) |
| **Insights** | Reports on data estate: scan coverage, asset count, classification, sensitivity labels |

### Supported Data Sources

- Azure: Azure Blob Storage, Azure Data Lake Gen1/Gen2, Azure SQL, Azure Synapse, Azure Cosmos DB, Azure SQL Managed Instance, Azure Data Factory, Azure Databricks, Azure Files
- Multi-cloud: AWS S3, Amazon RDS, GCP Storage
- On-premises: SQL Server, SAP (via self-hosted integration runtime), Oracle
- SaaS: Power BI, Salesforce

### Sensitivity Labels Integration

- Microsoft Purview Information Protection labels (formerly AIP) applied to files and database columns
- Labels: Public, Internal, Confidential, Highly Confidential (customizable)
- Labels extend to Office 365 content (Word, Excel, PowerPoint) and Azure data stores
- Policy enforcement: encryption, watermarks, and access restrictions based on labels

### Purview Governance Portal

Separate from the Azure portal; accessed via `purview.microsoft.com` or the Purview resource in Azure portal.

### Purview vs Defender for Cloud Data Security

| | Microsoft Purview | Defender for Cloud (DSPM) |
|---|---|---|
| Focus | Data governance, catalog, lineage | Security posture for data stores |
| Use case | Data discovery, classification, access governance | Identify sensitive data exposure, misconfigured storage |
| Audience | Data officers, data engineers, governance teams | Security operations, cloud security teams |
| Integration | Sentinel, Information Protection | Defender for Cloud recommendations |
