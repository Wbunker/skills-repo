# Security Command Center — Capabilities

## Purpose

Security Command Center (SCC) is GCP's centralized security and risk management platform. It provides visibility into your security posture across all GCP resources, detecting threats, misconfigurations, and vulnerabilities, while providing compliance monitoring and integrations with security operations workflows. SCC is configured at the **organization level** and covers all projects within the org.

---

## Tiers

| Tier | Key Features | Pricing |
|---|---|---|
| **Standard** | Security Health Analytics (limited findings), Web Security Scanner (limited), Asset inventory, IAM policy analysis | Free |
| **Premium** | All Standard features + full Security Health Analytics, Container Threat Detection, Event Threat Detection, VM Threat Detection, Web Security Scanner (full), Compliance dashboards (CIS, PCI DSS, NIST 800-53, ISO 27001, HIPAA), Attack Path Simulation, Rapid Vulnerability Detection | Per-project pricing |
| **Enterprise** | All Premium features + Chronicle SIEM integration, Security Operations (SOAR), Gemini AI in Security, multi-cloud threat detection (AWS, Azure), toxic combination detection, risk scoring | Enterprise licensing |

---

## Core Concepts

### Finding
A security issue identified by a built-in or custom source. Findings have:
- **Category**: type of finding (e.g., `PUBLIC_BUCKET`, `OPEN_FIREWALL`, `ANOMALOUS_IAM_GRANT`)
- **Severity**: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFORMATIONAL`
- **State**: `ACTIVE` (open) or `INACTIVE` (resolved/closed)
- **Mute state**: `MUTED` or `UNMUTED`; muted findings are hidden from default views
- **Source**: which detector created it
- **Resource name**: the affected GCP resource
- **Event time**: when the finding was observed
- **Finding class**: `THREAT`, `VULNERABILITY`, `MISCONFIGURATION`, `OBSERVATION`, `POSTURE_VIOLATION`, `ERROR`

### Asset
Representation of a GCP resource within SCC. SCC maintains a near-real-time inventory of GCP resources (instances, buckets, datasets, firewall rules, service accounts, etc.) and their metadata. Assets are used for historical queries and change tracking.

### Source
A finding producer. Built-in sources (Security Health Analytics, Event Threat Detection, etc.) and custom sources (your own security scanners via the SCC API). Custom finding sources allow integration of third-party security tools.

### Security Mark
User-defined key-value labels applied to assets or findings for custom classification, grouping, and filtering. Security marks persist independently of the underlying resource's lifecycle. Example: `mark:data_classification=pii`, `mark:suppressed=true`.

### Mute Rule
A rule that automatically mutes findings matching specified criteria (resource type, category, project, etc.) so they don't appear in active finding views. Useful for accepted risks, false positives, or test environment noise. Muted findings are not deleted; they can be unmuted and reviewed.

### Notification Config
A Pub/Sub-based notification that sends SCC findings in near-real-time to a Pub/Sub topic for integration with SIEM, ticketing (Jira, PagerDuty), or custom automation. Supports filtering by finding category, severity, state, and source.

### Compliance Posture
SCC Premium maps findings to compliance framework controls:
- CIS Google Cloud Foundations Benchmark (v1.1, v1.2, v1.3, v2.0)
- PCI DSS v3.2.1
- NIST SP 800-53
- ISO 27001
- HIPAA
- NIST Cybersecurity Framework

Compliance dashboards show your current percentage compliance and list failing controls with associated findings.

---

## Built-in Detection Sources

### Security Health Analytics (SHA)
Scans GCP resource configurations for misconfigurations and policy violations. Findings include:

| Category | Example Findings |
|---|---|
| IAM | `ADMIN_SERVICE_ACCOUNT`, `SERVICE_ACCOUNT_ROLE_SEPARATION`, `KMS_KEY_NOT_ROTATED` |
| Compute | `OPEN_FIREWALL`, `OPEN_SSH_PORT`, `OPEN_RDP_PORT`, `PUBLIC_IP_ADDRESS` |
| Storage | `PUBLIC_BUCKET_ACL`, `BUCKET_LOGGING_DISABLED`, `BUCKET_POLICY_ONLY_DISABLED` |
| BigQuery | `DATASET_CMEK_DISABLED`, `DATASET_DEFAULT_ENCRYPTION_DISABLED` |
| SQL | `SSL_NOT_ENFORCED`, `PUBLIC_SQL_INSTANCE`, `SQL_NO_ROOT_PASSWORD` |
| Logging | `AUDIT_LOGGING_DISABLED`, `LOG_NOT_EXPORTED` |
| Network | `DNS_LOGGING_DISABLED`, `LOAD_BALANCER_LOGGING_DISABLED` |
| Cryptography | `KMS_KEY_NOT_ROTATED`, `KMS_PROJECT_HAS_OWNER` |

SHA runs continuously and re-scans resources when configurations change.

### Event Threat Detection (ETD)
Analyzes Cloud Logging streams in near-real-time to detect threats based on log patterns:

| Finding Category | Detection |
|---|---|
| `CREDENTIAL_ACCESS` | Anomalous service account activity, service account key access from unexpected IP |
| `DEFENSE_EVASION` | Audit log disabling, IAM policy changes hiding activity |
| `DISCOVERY` | Broad enumeration of GCP resources |
| `EXFILTRATION` | BigQuery data export to external project, Cloud Storage bucket made public |
| `IMPACT` | Cryptocurrency mining on Compute Engine, anomalous instance creation in new regions |
| `INITIAL_ACCESS` | Leaked service account key used, sensitive action from Tor exit node |
| `LATERAL_MOVEMENT` | Service account impersonation chains |
| `PERSISTENCE` | Backdoor service account created, SSH authorized key added |
| `PRIVILEGE_ESCALATION` | Service account granted broad permissions, org policy weakened |

ETD uses Google's threat intelligence (known malicious IPs, C2 infrastructure, anonymization proxies) and behavioral baselines.

### Container Threat Detection (CTD)
Monitors GKE workload runtime behavior at the kernel level without requiring an agent. Detects:
- `ADDED_BINARY_EXECUTED`: unexpected binary execution in a container
- `ADDED_LIBRARY_LOADED`: unexpected shared library loaded
- `REVERSE_SHELL`: outbound shell connection from a container
- `UNEXPECTED_CHILD_SHELL`: shell spawned as a child process of a non-shell process
- `MODIFIED_MALICIOUS_BINARY`: known malware executed in a container

### VM Threat Detection (VMTD)
Performs memory scanning of Compute Engine VMs without an agent installed on the VM:
- Detects cryptocurrency mining malware by scanning process memory
- `EXECUTION_CRYPTOMINING_HASH_MATCH`: hash of process matches known crypto miner
- `EXECUTION_CRYPTOMINING_YARA_RULE`: process memory matches YARA rule for crypto miner
- Compares running binaries against known-malicious hash databases

### Web Security Scanner
Dynamic application security testing (DAST) for applications hosted on App Engine, GKE, or Compute Engine:
- Crawls your application and tests for common vulnerabilities (OWASP Top 10)
- Detects: XSS, SQL injection, mixed content, outdated libraries, cleartext password forms, insecure cookie flags
- Requires a custom scan configuration with the target URL
- Standard tier: limited scans per week; Premium tier: unlimited

### Rapid Vulnerability Detection (RVD)
Network-based vulnerability scanning of Compute Engine VMs and GKE container images:
- Detects unpatched OS vulnerabilities, exposed services, and CVE-based findings
- No agents required; uses external scanning from Google's infrastructure

---

## Chronicle SIEM Integration (Enterprise)

Chronicle is Google's cloud-native SIEM. SCC Enterprise integrates with Chronicle to:
- Forward all SCC findings, ETD alerts, and GCP logs to Chronicle
- Normalize events to Chronicle's **Unified Data Model (UDM)**
- Write **YARA-L** detection rules for custom threat detection across normalized logs
- Build dashboards for security operations
- Use **Google Threat Intelligence** (VirusTotal, Mandiant) feeds for enrichment
- Chronicle retains data for up to 12 months by default (configurable)

### YARA-L Example (simplified)
```
rule cryptomining_outbound_connection {
  meta:
    description = "Outbound connection to known crypto pool"
  events:
    $e.metadata.event_type = "NETWORK_CONNECTION"
    $e.target.hostname = /stratum\+tcp/ nocase
    $e.principal.asset.hostname = $host
  condition:
    $e
}
```

---

## Security Operations (Enterprise)

SCC Enterprise includes a SOAR (Security Orchestration, Automation, and Response) capability:
- **Cases**: group related findings into investigatable cases
- **Playbooks**: automated response workflows triggered by finding types
- **Google Security Operations**: integrated analyst workbench combining SIEM + SOAR
- Integrations with Jira, ServiceNow, PagerDuty, and other ticketing systems
- Gemini AI assistance: explain findings, suggest remediation steps, summarize cases

---

## Attack Path Simulation (Premium)

Attack Path Simulation (APS) models how an attacker could move through your environment by chaining together findings:
- Identifies **toxic combinations**: multiple lower-severity findings that together create a critical risk
- Shows the shortest path from an external entry point to a critical asset (e.g., public bucket → service account with excessive permissions → production database)
- Assigns a **risk score** to resources based on reachability from the internet and sensitivity
- Helps prioritize remediation by impact rather than severity in isolation

---

## Export and Integration

| Destination | Method | Use Case |
|---|---|---|
| Pub/Sub | Notification configs | Real-time alerting, SIEM ingestion, ticketing |
| Cloud Storage | Continuous export or snapshot | Long-term archival, compliance evidence |
| BigQuery | Continuous export | Advanced analytics, custom dashboards, SQL queries |
| Chronicle | Enterprise integration | SIEM, SOAR, threat hunting |
| Security Hub (AWS) | Cross-cloud (Enterprise) | Unified multi-cloud view |

---

## Custom Sources and Findings

Organizations can write custom findings to SCC via the SCC API, enabling third-party security tools (Prisma Cloud, Aqua Security, etc.) to appear alongside built-in findings. Custom source workflow:
1. Register a custom source via the SCC API.
2. Write findings to the source using the `projects/*/sources/*/findings` resource.
3. Findings appear in the SCC console and can trigger notification configs.

---

## Best Practices

1. **Activate SCC Premium at the organization level** to get full threat detection coverage across all projects.
2. **Enable notification configs** for CRITICAL and HIGH severity findings and route them to a real-time alerting channel (PagerDuty, Slack, etc.).
3. **Use mute rules** for findings that represent accepted risk, rather than ignoring them in the console — this maintains auditability.
4. **Enable Data Access audit logs** for the most sensitive services (BigQuery, Secret Manager, KMS) to maximize ETD detection coverage.
5. **Review Security Health Analytics findings weekly** and prioritize remediation by compliance framework impact.
6. **Integrate with BigQuery** for historical trend analysis and compliance reporting.
7. **Triage Attack Path Simulation results** regularly — a single finding may have low severity but high risk when combined with others.
8. **Use security marks** to tag assets with sensitivity classification; ETD can use these to increase alert priority for findings on sensitive assets.
9. **Run Web Security Scanner** in pre-production environments to catch vulnerabilities before deployment.
10. **Track finding SLAs**: set organizational SLAs for remediation (e.g., CRITICAL findings resolved within 24 hours, HIGH within 7 days) and monitor with Cloud Monitoring alerts on SCC finding counts.
