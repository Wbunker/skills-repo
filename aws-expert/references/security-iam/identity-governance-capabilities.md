# Identity, Governance & Threat Data — Capabilities Reference
For CLI commands, see [identity-governance-cli.md](identity-governance-cli.md).

## AWS Directory Service

**Purpose**: Managed Microsoft Active Directory and AD-compatible directory services, enabling AWS workloads and applications to use existing Active Directory credentials and group policies without managing AD infrastructure.

### Directory Type Comparison

| | AWS Managed Microsoft AD | AD Connector | Simple AD |
|---|---|---|---|
| **What it is** | Real Microsoft AD, managed by AWS | Proxy to on-premises AD | Samba 4-based, AD-compatible |
| **Hosted where** | AWS (standalone or hybrid) | Bridges on-prem AD to AWS | AWS (standalone) |
| **Schema extensions** | Yes | No | No |
| **Trust relationships** | Yes (forest/external trusts) | No | No |
| **MFA** | Yes (RADIUS) | Yes (RADIUS) | No |
| **RDS SQL Server** | Yes | No | No |
| **Objects supported** | 30K (Standard) / 500K (Enterprise) | Depends on on-prem AD | 500 / 5,000 (Small/Large) |
| **Use case** | Cloud-native AD or hybrid lift-and-shift | Extend on-prem AD to AWS with no sync | Low-cost basic directory |

### AWS Managed Microsoft AD — Key Features

| Feature | Description |
|---|---|
| **Multi-AZ deployment** | Domain controllers deployed across two AZs automatically |
| **Automated patching** | AWS patches and monitors domain controllers |
| **Daily snapshots** | Automatic snapshots with point-in-time restore |
| **Trust relationships** | One-way or two-way trusts with on-premises AD domains |
| **Fine-grained password policies** | Per-group password and account lockout policies |
| **Secure LDAP (LDAPS)** | TLS-encrypted LDAP connections |
| **MFA via RADIUS** | Integrate with on-premises RADIUS server for MFA |
| **Seamless domain join** | EC2 Windows/Linux instances automatically join the domain |

### AD Connector

- Acts as a **proxy**; all authentication requests are forwarded to on-premises AD
- No directory data is cached or stored in AWS
- Requires connectivity to on-premises AD (Direct Connect or VPN)
- Supports domain join for EC2, WorkSpaces, and other AWS services

### AWS Services That Integrate with Directory Service

| Service | Notes |
|---|---|
| **Amazon WorkSpaces** | Virtual desktops authenticated via AD |
| **Amazon RDS for SQL Server** | Windows Authentication using Managed AD |
| **AWS IAM Identity Center** | Use AD as the identity source for SSO |
| **Amazon EC2** | Seamless domain join for Windows and Linux instances |
| **Amazon FSx for Windows** | AD-integrated file shares (requires Managed AD or trust) |
| **Amazon QuickSight / Connect / Chime** | User authentication via AD |
| **AWS Management Console** | Console access via IAM Identity Center + AD identity source |

### Multi-Region Replication (Managed AD Enterprise)

- Replicate a Managed AD directory to additional AWS regions
- Each region gets its own domain controllers for low-latency authentication
- Required when applications span multiple regions

---

## AWS Resource Access Manager (AWS RAM)

**Purpose**: Share AWS resources securely across accounts within an AWS Organization (or with specific external accounts) without duplicating resources, reducing cost and operational overhead.

### Core Concepts

| Concept | Description |
|---|---|
| **Resource share** | Container defining what resources are shared, with whom, and what permissions apply |
| **Owner account** | The AWS account that owns the resource and creates the share |
| **Principal** | Who the resource is shared with — another account ID, an OU, the entire Organization, or an IAM role/user |
| **Managed permission** | RAM permission set defining what the principal can do with the shared resource |
| **Invitation** | Required when sharing with accounts outside your Organization; not required within the Organization after enabling org-level sharing |

### How Resource Sharing Works

```
Owner Account                        Consumer Account
─────────────                        ────────────────
Creates resource (e.g., VPC subnet)
Creates resource share in RAM
Specifies principal (account/OU)  ──► Consumer sees resource natively
                                       in their console and API
Owner retains ownership              Consumer uses resource as if their own
Owner can revoke at any time         (within RAM permission boundaries)
```

### Commonly Shared Resource Types

| Resource | Typical pattern |
|---|---|
| **VPC subnets** | Central networking account shares subnets into spoke accounts (hub-and-spoke VPC model) |
| **Transit Gateway** | Share TGW from a network account with all application accounts |
| **Route 53 Resolver rules** | Share DNS forwarding rules across accounts |
| **AWS License Manager configs** | Enforce software license limits across all accounts |
| **AWS Glue Data Catalog** | Share databases/tables across analytics accounts |
| **AWS Network Firewall policies** | Share firewall policies via Firewall Manager |
| **Aurora DB clusters** | Share clusters for cross-account read access |
| **Private CA (AWS Private CA)** | Share a CA with accounts that need to issue certificates |

### Key Features

| Feature | Description |
|---|---|
| **No additional cost** | RAM itself is free; only the underlying resources are billed to the owner |
| **Organization-level sharing** | Enable once at org level; share with OUs without enumerating account IDs |
| **Native console experience** | Shared resources appear in the consumer's service console as if locally owned |
| **Audit via CloudTrail** | All sharing actions are logged |
| **Custom permissions** | Create custom managed permissions limiting what consumers can do |

### Important Constraints

- Resource shares are **regional** (except global resources, which must be shared from `us-east-1`)
- The owner retains full control; consumers can use but cannot modify ownership
- Not all AWS resource types are shareable — check the RAM shareable resources list
- Consumers cannot re-share resources they received via RAM
- Sharing with external accounts (outside Organization) requires the recipient to accept an invitation

### Integration with AWS Organizations

```bash
# Enable organization-wide sharing (run once from management account)
aws ram enable-sharing-with-aws-organization

# Then share with an entire OU — no invitations needed
aws ram create-resource-share \
  --name "network-subnets" \
  --principals arn:aws:organizations::123456789012:ou/o-xxx/ou-yyy \
  --resource-arns arn:aws:ec2:us-east-1:123456789012:subnet/subnet-xxx
```

---

## Amazon Security Lake

**Purpose**: Fully managed security data lake that centralizes security logs and findings from AWS services, SaaS providers, on-premises systems, and custom sources into a normalized, OCSF-format data lake stored in your own S3 buckets.

### Core Concepts

| Concept | Description |
|---|---|
| **OCSF** | Open Cybersecurity Schema Framework — vendor-neutral, open standard for normalizing security event data across sources |
| **Data lake** | Purpose-built repository in your S3 buckets; you own and control the data |
| **Log source** | An AWS service, third-party tool, or custom source sending data to Security Lake |
| **Rollup Region** | A designated region that aggregates data from multiple regions for centralized querying |
| **Subscriber** | A service or tool that reads Security Lake data — either via S3 direct access or SQS notifications |
| **Subscriber notification** | SQS/EventBridge notification to a subscriber when new data objects are available |

### Supported Native AWS Log Sources

| Source | Data type |
|---|---|
| **AWS CloudTrail** | Management events and S3/Lambda data events |
| **VPC Flow Logs** | Network traffic metadata |
| **Amazon Route 53 Resolver query logs** | DNS query activity |
| **Amazon EKS audit logs** | Kubernetes API server audit events |
| **AWS WAFv2 logs** | Web application firewall request logs |
| **AWS Security Hub findings** | CSPM findings aggregated from all enabled security tools |
| **AWS Lambda execution logs** | Function invocation telemetry |
| **Amazon S3 data access logs** | Object-level access to S3 buckets |

### Data Normalization Pipeline

```
Raw log source (CloudTrail JSON, VPC Flow Logs, etc.)
        │
        ▼
  Security Lake ingestion
        │
        ▼
  Normalize to OCSF schema  ──► Convert to Apache Parquet
        │
        ▼
  Partition in S3 by source/region/date
        │
        ├─► AWS Glue Data Catalog (schema metadata)
        │
        ├─► Query via Amazon Athena / Amazon Redshift
        │
        └─► Subscriber notification (SQS/EventBridge) → SIEM, SOAR, analytics tool
```

### Key Features

| Feature | Description |
|---|---|
| **You own the data** | Data stored in S3 in your account; no vendor lock-in |
| **OCSF normalization** | All sources normalized to a common schema — eliminates per-source parsing in your SIEM |
| **Multi-account & multi-region** | Enable via Organizations; designate rollup regions |
| **Lifecycle management** | Configure retention and S3 storage class transitions per source |
| **Subscriber access control** | Grant read access to specific sources, accounts, and regions |
| **Custom log sources** | Onboard any third-party or on-premises source by sending OCSF-formatted data |

### Subscriber Types

| Subscriber Type | How it works | Use case |
|---|---|---|
| **Data access** | Direct S3 access via Lake Formation permissions | Athena queries, Spark jobs, Redshift Spectrum |
| **Query access** | Glue Data Catalog integration | Analytics tools that use standard SQL |
| **Notification** | SQS or EventBridge events when new objects arrive | SIEM/SOAR tools polling for new data |

### Integration Patterns

- **Amazon Security Hub → Security Lake**: Security Hub findings flow into Security Lake as a native source — gives historical retention and cross-account aggregation
- **Athena**: Query Security Lake data directly; AWS provides prebuilt Athena query templates for common investigations
- **Third-party SIEMs (Splunk, Sumo Logic, etc.)**: Integrate as subscribers; receive SQS notifications and pull Parquet data from S3
- **Amazon OpenSearch / QuickSight**: Build security dashboards from Security Lake data
- **GuardDuty + Detective**: GuardDuty findings flow into Security Lake; Detective correlates them using the behavior graph

### Multi-Account Architecture

```
Management / Delegated Admin Account
  └─ Security Lake enabled organization-wide
       │
       ├─ Account A: CloudTrail, VPC Flow Logs → sent to rollup region
       ├─ Account B: EKS audit logs, WAF logs → sent to rollup region
       └─ Rollup Region S3 bucket ← all data centralized here
                │
                ├─ Athena queries
                ├─ Subscriber: SIEM tool
                └─ Subscriber: Security Operations team
```
