# AWS Security Hub, Inspector & Macie — Capabilities Reference
For CLI commands, see [security-hub-inspector-macie-cli.md](security-hub-inspector-macie-cli.md).

## AWS Security Hub

**Purpose**: Aggregates security findings from GuardDuty, Inspector, Macie, IAM Access Analyzer, Firewall Manager, and third-party tools; runs automated compliance checks.

### Security Standards (Automated Checks)

| Standard | Description |
|---|---|
| **AWS Foundational Security Best Practices** | AWS-curated controls across services |
| **CIS AWS Foundations Benchmark** | Center for Internet Security benchmark controls |
| **PCI DSS** | Payment Card Industry controls |
| **NIST SP 800-53** | NIST controls for federal systems |
| **SOC 2** | Service Organization Control 2 criteria |

### Key Concepts

| Concept | Description |
|---|---|
| **Finding** | A security issue; normalized to ASFF (Amazon Security Finding Format) |
| **Control** | An automated check; PASSED/FAILED/NOT_AVAILABLE result per account/region |
| **Security score** | Percentage of passed controls; per account and aggregated |
| **Insight** | Saved grouping/filter of findings for recurring analysis |
| **Custom action** | Send findings to EventBridge for automated response |
| **Aggregation region** | Link multiple regions; view all findings in one region |

### Integration Sources

AWS native: GuardDuty, Inspector, Macie, IAM Access Analyzer, Firewall Manager, Config, Systems Manager Patch Manager, Detective

Third-party: Palo Alto, CrowdStrike, Splunk, Rapid7, Tenable, and 60+ others

---

## Amazon Inspector

**Purpose**: Automated vulnerability management scanning for EC2, ECR container images, Lambda functions, and code (CodeGuru integration).

### Scan Types

| Scan | Target | What it finds |
|---|---|---|
| **EC2 scanning** | Running instances | OS CVEs, network reachability issues |
| **ECR container scanning** | Container images in ECR | OS CVEs, programming language package CVEs |
| **Lambda scanning** | Lambda function packages | Language dependency CVEs |
| **Lambda code scanning** | Lambda code | Security code issues via CodeGuru |
| **CIS scanning** | EC2 instances | CIS Benchmark hardening failures |
| **Code security scanning** | CodePipeline integration | SAST findings |

### Finding Severity

Uses CVSS v3 scoring:
- **Critical**: 9.0–10.0
- **High**: 7.0–8.9
- **Medium**: 4.0–6.9
- **Low**: 0.1–3.9

### Key Features

- **Delegated administrator**: Centralize across org accounts
- **Suppression rules**: Suppress findings matching criteria (e.g., accepted risk)
- **SBOM export**: Export software bill of materials per resource
- **ECR enhanced scanning**: Replace basic scanning; automatically rescans when new CVEs published
- **Auto-remediation**: Integrate with SSM Patch Manager via EventBridge

---

## Amazon Macie

**Purpose**: Uses ML to automatically discover and protect sensitive data (PII, PHI, financial data, credentials) stored in S3.

### Key Features

| Feature | Description |
|---|---|
| **Automated discovery** | Continuously evaluates all S3 buckets for sensitive data exposure risk |
| **Sensitive data discovery jobs** | Target specific buckets/objects; run on schedule or one-time |
| **Managed data identifiers** | Pre-built detectors for 200+ data types: SSNs, credit cards, credentials, health data |
| **Custom data identifiers** | Regex + keywords for business-specific sensitive data |
| **Allow lists** | Exclude known-safe patterns from findings (e.g., test data) |
| **Bucket inventory** | Visibility into all S3 buckets: public access, encryption, sharing status |
| **Multi-account** | Delegated admin aggregates findings across org |

### Finding Types

| Category | Examples |
|---|---|
| **Policy findings** | Bucket made public, bucket encryption disabled, bucket shared cross-account |
| **Sensitive data findings** | PII, credentials, financial data, health information found in object |

---

## AWS Security Incident Response

**Purpose**: Centralized security incident management service providing structured triage, investigation, and response workflows — with optional engagement of the AWS Customer Incident Response Team (CIRT) for critical incidents.

### Core Concepts

| Concept | Description |
|---|---|
| **Case** | The primary incident record; tracks status, timeline, comments, attachments, and involved parties |
| **Membership** | An AWS account enrolled in Security Incident Response; required before cases can be created or managed |
| **Case Status** | Lifecycle state: `Detected` → `Triaged` → `InvestigationAndContainment` → `Eradication` → `Recovery` → `PostIncidentActivities` → `Closed` |
| **Watcher** | Internal stakeholder (e.g., legal, management) added to a case for visibility |
| **Resolver** | IR team member assigned to actively work a case |
| **SLA** | Service level agreement targets for initial triage and response times |
| **Notification** | SNS topic integration for case status change alerts |
| **Security Hub integration** | Findings from Security Hub can automatically trigger case creation |

### Incident Response Workflow

```
Security Hub finding
        │
        ▼
  Case created (auto or manual)
        │
        ▼
  Triage (severity, scope assessment)
        │
        ├─► Engage AWS CIRT (optional, for critical incidents)
        │
        ▼
  Investigation & Containment
  (CloudTrail evidence, Security Lake queries)
        │
        ▼
  Eradication → Recovery
        │
        ▼
  Post-Incident Report / Case Closed
```

### Membership and CIRT Engagement

- Accounts must **subscribe** to Security Incident Response (membership) before the service is active
- The **AWS Customer Incident Response Team (CIRT)** can be engaged for critical incidents; CIRT members are added as resolvers on the case
- Membership can be managed at the Organizations level via a delegated administrator account

### Integration with Other Services

| Service | Role in Incident Response |
|---|---|
| **AWS Security Hub** | Source of findings; can auto-create cases from high-severity findings |
| **AWS CloudTrail** | Provides API activity evidence attached to cases for investigation |
| **Amazon Security Lake** | Central OCSF-normalized data lake queried during investigation for correlated log data |
