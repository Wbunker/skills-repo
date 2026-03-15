# Amazon GuardDuty & Detective — Capabilities Reference
For CLI commands, see [guardduty-detective-cli.md](guardduty-detective-cli.md).

## Amazon GuardDuty

**Purpose**: Intelligent threat detection continuously monitoring AWS accounts, workloads, and data.

### Data Sources

| Source | What it detects |
|---|---|
| **VPC Flow Logs** | Unusual network activity, port scanning, crypto-mining traffic |
| **CloudTrail events** | Suspicious API activity, credential exfiltration, account takeover |
| **DNS logs** | DNS-based C2 communication, data exfiltration via DNS |
| **S3 data events** | S3 bucket compromises, data exfiltration |
| **EKS audit logs** | Kubernetes API anomalies, container escapes |
| **EKS runtime monitoring** | Container-level runtime threat detection (requires agent) |
| **ECS runtime monitoring** | Container-level runtime on Fargate and EC2 |
| **EC2 runtime monitoring** | OS-level threat detection (requires agent) |
| **Lambda network activity** | Unusual Lambda outbound connections |
| **RDS login activity** | Brute force, anomalous logins to Aurora |
| **Malware Protection** | Scan EBS volumes on suspicious EC2/container for malware |

### Finding Categories

| Category | Example finding types |
|---|---|
| **Backdoor** | EC2 making outbound calls to known C2 IPs |
| **CryptoCurrency** | EC2/container mining cryptocurrency |
| **Recon** | Port scanning, credential enumeration |
| **Trojan** | DNS queries to known malicious domains |
| **UnauthorizedAccess** | Tor exit node access, credential stuffing |
| **Stealth** | CloudTrail logging disabled, config changes to hide activity |
| **Impact** | S3 data destruction, ransomware indicators |
| **CredentialAccess** | IAM credential theft or unusual use |
| **Exfiltration** | Large data transfers out of S3 |

### Key Features

- **Multi-account**: Designate a delegated administrator; aggregate findings from all org accounts
- **Suppression rules**: Filter out known-good findings automatically
- **Trusted IP lists**: Mark known IP ranges as trusted (suppress findings from them)
- **Threat intelligence lists**: Add custom IOC lists (malicious IPs, domains)
- **EventBridge integration**: Route findings to SIEM, ticketing, or automated remediation
- **Finding export**: Continuous export to S3 for long-term retention and SIEM ingestion

---

## Amazon Detective

**Purpose**: Analyzes and visualizes security data to investigate and understand the root cause of security findings.

### Key Concepts

- Ingests CloudTrail, VPC Flow Logs, GuardDuty findings, EKS audit logs automatically
- Builds a **behavior graph** — a linked dataset across time correlating entities (IPs, users, roles, instances)
- Does **not** detect threats itself; it helps you **investigate** findings from GuardDuty, Security Hub, etc.

### Investigation Capabilities

| Capability | Description |
|---|---|
| **Entity profiles** | Timeline of activity for an IP, user, role, EC2 instance, or S3 bucket |
| **Finding groups** | AI-clustered related findings into a single investigation |
| **Scope time** | Adjust the time window of an investigation |
| **Related findings** | Surfaces GuardDuty findings related to the entity |
| **Geolocation** | Map API call and network activity by location |
| **Role session analysis** | See which assumed-role sessions made which API calls |
