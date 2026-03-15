# AWS Storage Gateway & Transfer Family — Capabilities Reference

For CLI commands, see [storage-gateway-transfer-cli.md](storage-gateway-transfer-cli.md).

## AWS Storage Gateway

**Purpose**: Hybrid cloud storage service providing on-premises access to AWS storage; bridges on-premises applications to S3, FSx for Windows, S3 Glacier, and EBS snapshots via standard file, tape, and block protocols.

### Gateway Types

| Type | Protocol | Backend | Use Case |
|---|---|---|---|
| **S3 File Gateway** | NFS (v3, v4.1), SMB (v2, v3) | Amazon S3 | On-premises apps storing files as S3 objects; local cache for low-latency access |
| **FSx File Gateway** | SMB | FSx for Windows File Server | Low-latency on-premises access to Windows file shares hosted in FSx |
| **Tape Gateway** | iSCSI VTL | S3 / S3 Glacier | Replace physical tape libraries; integrate with existing backup software (Veeam, Backup Exec) |
| **Volume Gateway** | iSCSI | S3 (via EBS snapshots) | Block storage for on-premises apps; Cached mode (primary in S3) or Stored mode (primary on-premises) |

### Deployment Options

| Option | Platform |
|---|---|
| **On-premises VM** | VMware vSphere, Microsoft Hyper-V, or KVM |
| **Hardware appliance** | AWS Storage Gateway Hardware Appliance (physical device) |
| **EC2** | Deploy as EC2 instance for DR or cloud-native scenarios |

### Key Features

| Feature | Description |
|---|---|
| **Local cache** | Frequently accessed data served from local cache for low latency; LRU eviction when full |
| **Bandwidth management** | Schedule upload bandwidth windows to avoid business-hour congestion |
| **Volume Gateway — Cached mode** | Primary data in S3; frequently accessed data cached locally |
| **Volume Gateway — Stored mode** | Primary data on-premises; asynchronous snapshots to S3 as EBS snapshots |
| **Tape Gateway** | Virtual tape library (VTL); virtual tapes archived to S3 Glacier or S3 Glacier Deep Archive |
| **Encryption** | All data encrypted in transit (TLS) and at rest (S3-SSE or SSE-KMS) |

### Important Constraints

- Maximum individual file size for S3 File Gateway: 5 TB (S3 object limit)
- AWS recommends <50 ms network latency for optimal performance
- Gateway activation requires internet connectivity to AWS

---

## AWS Transfer Family

**Purpose**: Fully managed file transfer service supporting SFTP, FTPS, FTP, and AS2 protocols for transferring files into and out of Amazon S3 and Amazon EFS without managing server infrastructure.

### Key Concepts

| Concept | Description |
|---|---|
| **Server** | A Transfer Family endpoint hosting one or more protocols; deployed in up to 3 AZs; auto-scaling |
| **User** | An account on the server; authenticated via SSH key, password, or external IdP |
| **Connector** | Outbound transfer endpoint for AS2 and SFTP to external servers |
| **Workflow** | Serverless post-upload processing pipeline (copy, tag, scan, compress, encrypt, decrypt) |
| **Web app** | Managed browser-based file transfer UI for S3 access |

### Supported Protocols

| Protocol | Use Case |
|---|---|
| **SFTP** (SSH File Transfer Protocol v3) | Secure file transfers; most common for partner integrations |
| **FTPS** (FTP Secure) | FTP with TLS encryption; legacy partner compatibility |
| **FTP** | Unencrypted; use only in trusted internal network environments |
| **AS2** (Applicability Statement 2) | Compliance-heavy B2B transfers (supply chain, payments, EDI/ERP/CRM) |

### Storage Backends

| Backend | Notes |
|---|---|
| **Amazon S3** | Files transferred directly to/from S3 buckets; supports all S3 storage classes |
| **Amazon EFS** | NFS-backed; ideal for shared file access; supply chain, content management, web serving |

### Identity Providers

Service-managed (SSH keys + Secrets Manager for passwords), custom identity provider (Lambda or API Gateway), Azure Active Directory, Amazon Cognito, Okta

### Key Features

| Feature | Description |
|---|---|
| **Managed workflows** | Automated post-transfer processing: copy, tag, scan, filter, compress/decompress, encrypt/decrypt |
| **Connectors** | Outbound SFTP and AS2 connections to external partners; monitor transfer status |
| **Logical directories** | Map user home directories to S3 prefixes or EFS paths; hide bucket structure from users |
| **Endpoint types** | Public (internet-facing) or VPC (private; route via VPC and optionally Direct Connect) |
| **Data ports** | FTP/FTPS data connections use ports 8192–8200 |

## AWS Storage Gateway

**Purpose**: Hybrid cloud storage service providing on-premises access to AWS storage; bridges on-premises applications to S3, FSx for Windows, S3 Glacier, and EBS snapshots via standard file, tape, and block protocols.

### Gateway Types

| Type | Protocol | Backend | Use Case |
|---|---|---|---|
| **S3 File Gateway** | NFS (v3, v4.1), SMB (v2, v3) | Amazon S3 | On-premises apps storing files as S3 objects; local cache for low-latency access |
| **FSx File Gateway** | SMB | FSx for Windows File Server | Low-latency on-premises access to Windows file shares hosted in FSx |
| **Tape Gateway** | iSCSI VTL | S3 / S3 Glacier | Replace physical tape libraries; integrate with existing backup software (Veeam, Backup Exec) |
| **Volume Gateway** | iSCSI | S3 (via EBS snapshots) | Block storage for on-premises apps; Cached mode (primary in S3) or Stored mode (primary on-premises) |

### Deployment Options

| Option | Platform |
|---|---|
| **On-premises VM** | VMware vSphere, Microsoft Hyper-V, or KVM |
| **Hardware appliance** | AWS Storage Gateway Hardware Appliance (physical device) |
| **EC2** | Deploy as EC2 instance for DR or cloud-native scenarios |

### Key Features

| Feature | Description |
|---|---|
| **Local cache** | Frequently accessed data served from local cache for low latency; LRU eviction when full |
| **Bandwidth management** | Schedule upload bandwidth windows to avoid business-hour congestion |
| **Volume Gateway — Cached mode** | Primary data in S3; frequently accessed data cached locally |
| **Volume Gateway — Stored mode** | Primary data on-premises; asynchronous snapshots to S3 as EBS snapshots |
| **Tape Gateway** | Virtual tape library (VTL); virtual tapes archived to S3 Glacier or S3 Glacier Deep Archive |
| **Encryption** | All data encrypted in transit (TLS) and at rest (S3-SSE or SSE-KMS) |

### Important Constraints

- Maximum individual file size for S3 File Gateway: 5 TB (S3 object limit)
- AWS recommends <50 ms network latency for optimal performance
- Gateway activation requires internet connectivity to AWS

---

## AWS Transfer Family

**Purpose**: Fully managed file transfer service supporting SFTP, FTPS, FTP, and AS2 protocols for transferring files into and out of Amazon S3 and Amazon EFS without managing server infrastructure.

### Key Concepts

| Concept | Description |
|---|---|
| **Server** | A Transfer Family endpoint hosting one or more protocols; deployed in up to 3 AZs; auto-scaling |
| **User** | An account on the server; authenticated via SSH key, password, or external IdP |
| **Connector** | Outbound transfer endpoint for AS2 and SFTP to external servers |
| **Workflow** | Serverless post-upload processing pipeline (copy, tag, scan, compress, encrypt, decrypt) |
| **Web app** | Managed browser-based file transfer UI for S3 access |

### Supported Protocols

| Protocol | Use Case |
|---|---|
| **SFTP** (SSH File Transfer Protocol v3) | Secure file transfers; most common for partner integrations |
| **FTPS** (FTP Secure) | FTP with TLS encryption; legacy partner compatibility |
| **FTP** | Unencrypted; use only in trusted internal network environments |
| **AS2** (Applicability Statement 2) | Compliance-heavy B2B transfers (supply chain, payments, EDI/ERP/CRM) |

### Storage Backends

| Backend | Notes |
|---|---|
| **Amazon S3** | Files transferred directly to/from S3 buckets; supports all S3 storage classes |
| **Amazon EFS** | NFS-backed; ideal for shared file access; supply chain, content management, web serving |

### Identity Providers

Service-managed (SSH keys + Secrets Manager for passwords), custom identity provider (Lambda or API Gateway), Azure Active Directory, Amazon Cognito, Okta

### Key Features

| Feature | Description |
|---|---|
| **Managed workflows** | Automated post-transfer processing: copy, tag, scan, filter, compress/decompress, encrypt/decrypt |
| **Connectors** | Outbound SFTP and AS2 connections to external partners; monitor transfer status |
| **Logical directories** | Map user home directories to S3 prefixes or EFS paths; hide bucket structure from users |
| **Endpoint types** | Public (internet-facing) or VPC (private; route via VPC and optionally Direct Connect) |
| **Data ports** | FTP/FTPS data connections use ports 8192–8200 |
