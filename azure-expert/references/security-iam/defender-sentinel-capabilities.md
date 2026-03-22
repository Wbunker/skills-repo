# Microsoft Defender for Cloud & Sentinel — Capabilities

## Overview

Microsoft Defender for Cloud combines Cloud Security Posture Management (CSPM) with Cloud Workload Protection Platform (CWPP) in a single console. Microsoft Sentinel is a cloud-native SIEM (Security Information and Event Management) and SOAR (Security Orchestration, Automation, and Response) platform built on top of Azure Monitor Log Analytics.

---

## Microsoft Defender for Cloud

### Architecture

Defender for Cloud has a unified security console available in the Azure portal under "Microsoft Defender for Cloud." It consists of:

1. **CSPM** (posture management): Secure Score, recommendations, regulatory compliance
2. **CWPP** (workload protection): Defender Plans for specific resource types
3. **Multi-cloud connectivity**: AWS and GCP via cloud connectors (native integration)

### CSPM Tiers

#### Foundational CSPM (Free)

Available to all Azure customers at no cost:
- Basic security recommendations (150+ checks)
- Secure Score (basic)
- Azure Security Benchmark compliance dashboard
- Continuous assessment of resource configurations
- Email notifications for security alerts

#### Defender CSPM (Paid Tier)

Includes all Foundational features plus:
- **Attack path analysis**: visualizes how attackers could move from exposed assets to sensitive resources
- **Cloud security explorer**: query-based exploration of security risks across your cloud environment
- **Agentless scanning**: vulnerability assessment for VMs without Log Analytics agent
- **CIEM (Cloud Infrastructure Entitlement Management)**: identify over-privileged identities and unused permissions
- **Data security posture management**: sensitive data discovery in storage accounts, SQL, etc.
- **Copilot for Security integration**: AI-powered security insights
- Regulatory compliance for additional standards (beyond Azure Security Benchmark)

### Defender Plans (CWPP)

Each Defender Plan protects a specific resource type. Plans are enabled per subscription.

| Plan | What It Protects | Key Features |
|---|---|---|
| **Defender for Servers** | Azure VMs, Arc-enabled servers | MDE integration, vulnerability assessment, JIT VM access, file integrity monitoring, adaptive application controls |
| **Defender for SQL** | Azure SQL, SQL on VMs, SQL Managed Instance, Azure Synapse | Vulnerability assessment, Advanced Threat Protection (SQL injection, data exfiltration) |
| **Defender for Storage** | Azure Storage accounts | Malware scanning, sensitive data threat detection, activity anomalies |
| **Defender for Containers** | ACR images, AKS clusters, Arc-enabled Kubernetes | Image vulnerability scanning, runtime threat detection, control plane hardening |
| **Defender for App Service** | Azure App Service plans | Suspicious traffic detection, malicious file detection |
| **Defender for Key Vault** | Azure Key Vault | Unusual access patterns, access from Tor/suspicious IPs, high-volume operations |
| **Defender for Resource Manager** | ARM operations | Malicious ARM operations, Azure management plane attacks |
| **Defender for DNS** | DNS queries from Azure resources | Malicious domain communications, crypto-mining, exfiltration via DNS |
| **Defender for APIs** | Azure API Management | API-specific threat detection, unusual data volume, suspicious parameter patterns |
| **Defender for Databases** | Cosmos DB, open-source databases | Unusual query patterns, credential brute force |

### Defender for Servers Plans

| Feature | Plan 1 | Plan 2 |
|---|---|---|
| Microsoft Defender for Endpoint (MDE) integration | Yes | Yes |
| Vulnerability assessment (Qualys or MDVM) | No | Yes |
| Agentless scanning | No | Yes |
| File integrity monitoring (FIM) | No | Yes |
| Just-in-time (JIT) VM access | No | Yes |
| Adaptive application controls | No | Yes |
| Network map | No | Yes |
| Regulatory compliance reporting | No | Yes |

### Secure Score

- Numeric score (0–100%) representing the security posture of your subscriptions
- Each recommendation has a max score contribution; implementing recommendation increases score
- Recommendations grouped by security controls (e.g., "Enable MFA", "Restrict management port access")
- **Security controls**: groups of related recommendations with a combined max score
- Secure Score API: available for integration with dashboards and reporting
- **Exemptions**: mark specific resources as exempt from a recommendation (e.g., intentional configuration)

### Security Recommendations

- Severity: High, Medium, Low, Informational
- Affected resources listed per recommendation
- Remediation steps provided (manual or Quick Fix one-click remediation)
- **Remediation logic**: for some recommendations, Quick Fix button applies remediation via ARM
- **Workflow automation**: trigger Logic App on recommendation state change

### Just-in-Time (JIT) VM Access

Temporarily opens management ports (RDP 3389, SSH 22, WinRM 5985/5986) on-demand via NSG rules:

1. Admin enables JIT on a VM via Defender for Cloud
2. JIT policy created: defines allowed ports, source IPs, max duration
3. User requests access via portal, CLI, or PowerShell
4. Defender for Cloud adds temporary NSG rule (allow from user's IP to port, for duration)
5. Rule automatically removed after duration expires
6. All JIT activations logged in Activity Log and Defender alerts

**Requirements**: Defender for Servers Plan 2, Standard SKU NSG.

### Regulatory Compliance Dashboard

- Maps Azure resources to compliance frameworks: CIS, NIST SP 800-53, PCI-DSS, HIPAA, ISO 27001, SOC 2, GDPR, and more
- Shows passing/failing controls per framework
- Downloadable compliance reports (PDF)
- Custom standards can be added
- Continuous assessment — not point-in-time

### Multi-Cloud Support

- **AWS**: deploy Defender for Cloud AWS connector (CloudFormation template in AWS); enables Defender CSPM and CWPP plans for EC2, EKS, ECR, RDS, S3, Lambda
- **GCP**: deploy Defender for Cloud GCP connector; covers GKE, GCE, GCS, Cloud SQL

---

## Microsoft Sentinel

Microsoft Sentinel is a cloud-native SIEM and SOAR solution built on Log Analytics. It ingests security data from across your environment, detects threats, and enables automated response.

### Architecture

```
Data Sources (300+) → Sentinel Data Connectors → Log Analytics Workspace
                                                           │
              ┌───────────────────────────────────────────┤
              │             │              │               │
         Analytics     Workbooks      Hunting         Playbooks
         (Detection)  (Dashboards)   (Queries)        (SOAR/Logic Apps)
              │                                           │
           Incidents ──────────────────────────── Automation Rules
```

- Sentinel is a feature layer on top of a **Log Analytics workspace**; all data stored in workspace tables
- One workspace can host one Sentinel instance; dedicated workspace recommended for security data
- Data ingestion charged by GB (standard Log Analytics pricing + Sentinel add-on); commitment tiers reduce cost

### Data Connectors (300+)

| Connector Type | Examples |
|---|---|
| **Microsoft First-Party** | Microsoft 365 (Exchange, SharePoint, Teams), Microsoft Entra ID, Microsoft Defender XDR, Azure Activity, Azure Monitor, Defender for Cloud |
| **Azure Services** | Azure Firewall, Azure Key Vault, Azure DDoS, Azure Web Application Firewall |
| **Security Products (Partners)** | Palo Alto, Check Point, Cisco, F5, Fortinet, Trend Micro, Symantec, CrowdStrike |
| **Generic** | CEF via syslog, syslog, REST API, Event Hub ingestion |
| **AWS/GCP** | CloudTrail, GuardDuty, S3 access logs, GCP Security Command Center |

### Analytics Rules (Detection)

| Rule Type | Description | Latency |
|---|---|---|
| **Scheduled** | KQL query runs on a defined schedule (5 min to 14 days); generates incidents | Schedule interval |
| **NRT (Near Real-Time)** | KQL query runs every minute on new events; for high-priority detection | ~1 min |
| **Microsoft Security** | Auto-create incidents from Microsoft security product alerts (MDE, Defender for Cloud, MDO) | Near real-time |
| **Fusion** | ML-based correlation of multiple low-fidelity signals into high-confidence incidents | Near real-time |
| **Anomaly** | ML behavioral analytics; UEBA-based anomaly detection | Hours |
| **Threat Intelligence** | Match log data against Microsoft Threat Intelligence IOCs | Near real-time |

### Incidents

- Created by analytics rules when conditions match
- Include: alerts, entities (users, IPs, hosts, URLs, files), tactics (MITRE ATT&CK), evidence
- **Investigation graph**: visual timeline of entities and their relationships; pivot from incident to entity to related incidents
- **Entity behavior analytics (UEBA)**: baseline user/entity behavior; anomaly score on entities
- Incident lifecycle: New → Active → Closed (True Positive, False Positive, Benign Positive, Undetermined)
- Assignment, comments, labels, bookmarks for collaborative investigation
- **Incident tasks**: structured response steps assigned within an incident

### SOAR — Playbooks (Logic Apps)

Automated response workflows triggered by incidents, alerts, or entities:

| Trigger | Description |
|---|---|
| Microsoft Sentinel Incident | Runs when incident is created or updated |
| Microsoft Sentinel Alert | Runs on alert creation |
| Microsoft Sentinel Entity | Runs for specific entity types (user, IP, host) |

**Common automations**:
- Block IP in Azure Firewall / NSG when high-severity alert
- Disable Entra ID user account on suspicious activity
- Send Teams or Slack notification for critical incidents
- Create ServiceNow/Jira ticket for incident
- Enrich incident with Threat Intelligence lookups
- Isolate VM via Defender for Endpoint

### Automation Rules

Lightweight rules that fire before playbooks for common actions:
- Auto-assign incidents by severity/product
- Auto-close known false positives (specific rule + condition = suppress)
- Auto-change incident status or severity
- Add tags to incidents
- Trigger playbooks (from automation rule, no need to go through analytics rule)

### KQL Hunting and Workbooks

- **Hunting queries**: proactive threat hunting using KQL; save and share queries
- **Bookmarks**: mark specific query results during investigation; include in incident
- **Livestream**: run KQL query and get real-time notifications as matching events arrive
- **Notebooks**: Jupyter notebooks for advanced investigation (Python, ML)
- **Workbooks**: Azure Monitor workbooks for dashboards and visualizations; 100+ community workbooks

### Content Hub

Pre-built solutions by vendor/product containing data connectors, analytics rules, workbooks, playbooks, and hunting queries as a single installable package:
- Microsoft XDR solution, Azure Activity, MITRE ATT&CK, Zero Trust, Threat Intelligence
- Partner solutions: Cisco, Palo Alto, AWS, GCP, Okta, Cloudflare, GitHub, Atlassian

### Log Analytics Tables (Key Sentinel Tables)

| Table | Source |
|---|---|
| `SignInLogs` | Entra ID sign-in events |
| `AuditLogs` | Entra ID directory changes |
| `SecurityAlert` | Security product alerts (Defender, Sentinel) |
| `SecurityIncident` | Sentinel incidents |
| `OfficeActivity` | Microsoft 365 audit events |
| `AzureActivity` | Azure control plane operations |
| `CommonSecurityLog` | CEF format security logs (Palo Alto, Check Point, etc.) |
| `Syslog` | Linux syslog |
| `WindowsEvent` | Windows event logs |
| `AzureFirewallApplicationRule` | Azure Firewall application logs |
| `AzureFirewallNetworkRule` | Azure Firewall network logs |
| `DnsEvents` | DNS query logs |
| `StorageBlobLogs` | Azure Storage audit logs |
| `KeyVaultData` / `AZKVAuditLogs` | Key Vault audit events |

### Pricing

| Model | Details |
|---|---|
| **Pay-as-you-go** | ~$2.76/GB (varies by region); no commitment |
| **Commitment tiers** | 100 GB/day to 5,000 GB/day; discounts up to 65% vs PAYG |
| **Microsoft Sentinel free trial** | First 31 days free for new workspace |
| **Microsoft 365 E5 entitlement** | Up to 5 MB/user/day free for M365-sourced logs |
| **Auxiliary logs** | Long-retention, low-cost tier for verbose/compliance logs |
| **Basic logs** | Low-cost tier for high-volume, low-value logs (querying not free) |
