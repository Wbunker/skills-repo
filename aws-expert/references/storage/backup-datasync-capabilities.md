# AWS Backup & DataSync — Capabilities Reference
For CLI commands, see [backup-datasync-cli.md](backup-datasync-cli.md).

## AWS Backup

**Purpose**: Centralized, policy-based data protection service that automates backups across AWS services and on-premises resources from a single console.

### Key Concepts

| Concept | Description |
|---|---|
| **Backup plan** | Policy defining backup frequency, retention, lifecycle, and vault destination; applied via tags or resource assignment |
| **Backup vault** | Secure container storing recovery points; encrypted with KMS key independent of source; access-controlled via resource policy |
| **Recovery point** | A snapshot or backup of a resource; stored in a vault with its own ARN |
| **Backup rule** | Component of a backup plan defining schedule (cron), retention period, and lifecycle transitions |
| **Backup Vault Lock** | WORM protection on a vault; prevents deletion of recovery points or changes to retention (even by root); Compliance or Governance mode |
| **Legal hold** | Place an indefinite lock on specific recovery points during legal or compliance investigations |

### Supported Services

EC2/EBS, S3, RDS (all engines), Aurora, DynamoDB, DocumentDB, Neptune, Redshift, EFS, FSx (all variants), Storage Gateway volumes, VMware Cloud on AWS, EKS clusters, CloudFormation stacks, Timestream, SAP HANA

### Key Features

| Feature | Description |
|---|---|
| **Backup plans** | Define schedules, retention, and storage tiers; apply to resources by tag or explicit assignment |
| **Lifecycle management** | Automatically transition recovery points from warm to cold storage to reduce costs |
| **Cross-region backup** | Copy recovery points to another region on demand or via plan rules |
| **Cross-account backup** | Copy or restore across AWS accounts; fan-in to a central backup account; requires AWS Organizations |
| **Tag-based policies** | Apply backup plans to all resources matching a specific tag key/value |
| **Audit Manager** | Pre-built and custom compliance controls; generate audit reports |
| **Restore testing** | Automate periodic restore tests to validate recoverability |
| **Centralized billing** | Backup charges appear under "Backup" service line (not individual services) when using full AWS Backup management |

### Important Constraints

- AWS Backup does not manage backups created outside of AWS Backup (e.g., manual RDS snapshots)
- Not all resource types support lifecycle transition to cold storage
- Not all resource types support incremental backups
- Cross-account backup requires AWS Organizations

---

## AWS DataSync

**Purpose**: Secure, high-speed data transfer service for moving file and object data to, from, and between AWS storage services; automates infrastructure management, scheduling, monitoring, and integrity validation.

### Key Concepts

| Concept | Description |
|---|---|
| **Agent** | Software appliance (VM or EC2) deployed in your on-premises environment or cloud; connects DataSync to source/destination |
| **Location** | Source or destination endpoint for a task (NFS, SMB, HDFS, S3, EFS, FSx, object storage, other clouds) |
| **Task** | Defines a source location, destination location, and transfer settings (filters, scheduling, options) |
| **Task execution** | A single run of a task; provides real-time and post-execution metrics |

### Supported Locations

| Type | Sources / Destinations |
|---|---|
| **On-premises** | NFS, SMB, HDFS, object storage (S3-compatible) |
| **AWS** | S3, EFS, FSx for Windows, FSx for Lustre, FSx for OpenZFS, FSx for ONTAP |
| **Other clouds** | Google Cloud Storage, Azure Blob Storage, Azure Files, Wasabi, DigitalOcean Spaces, Oracle Cloud, Cloudflare R2, Backblaze B2, IBM Cloud, Alibaba Cloud, and more |

### Key Features

| Feature | Description |
|---|---|
| **High speed** | Purpose-built protocol; parallel multi-threaded transfers; 10x faster than open-source tools |
| **Integrity validation** | Checksums verified during transfer and after completion |
| **Encryption** | End-to-end encryption in transit; IAM and VPC endpoint support |
| **Scheduling** | Hourly, daily, or custom cron-based schedules |
| **Filtering** | Include/exclude patterns to select specific files |
| **Bandwidth throttling** | Limit bandwidth usage to avoid impacting production workloads |

### Use Cases

Data migration to AWS, archive cold data to S3 Glacier, replication for DR, hybrid cloud data processing (ML, analytics)

---

## AWS Elastic Disaster Recovery (DRS)

**Purpose**: Minimizes downtime and data loss by continuously replicating source servers (physical, VMware, other clouds, or other AWS Regions) to a low-cost staging area in AWS; enables fast recovery with RPO of seconds and RTO of minutes.

### Key Concepts

| Concept | Description |
|---|---|
| **AWS Replication Agent** | Lightweight agent installed on each source server; performs continuous block-level replication over TCP port 1500 to the staging area |
| **Staging area subnet** | A designated subnet in the target AWS account and Region where lightweight replication servers and EBS staging volumes receive replicated data at low cost |
| **Replication server** | Automatically launched and terminated EC2 instance in the staging area that receives data from the agent; no permanent infrastructure required |
| **Source server** | The server being protected; can be physical, VMware VM, cloud VM (Azure, GCP, etc.), or an EC2 instance in another Region |
| **Recovery instance** | Full-size EC2 instance launched from replicated data into the target VPC during a drill or actual recovery |
| **Point-in-time (PIT) recovery** | EBS snapshots captured automatically during replication; configurable retention; allows launching instances from a previous consistent state |
| **Launch template** | EC2 launch configuration (subnet, security groups, instance type, EBS settings) applied when launching recovery instances |

### Recovery Objectives

| Metric | Value |
|---|---|
| **RPO (Recovery Point Objective)** | Seconds (continuous block-level replication) |
| **RTO (Recovery Time Objective)** | Minutes (automated server conversion and instance launch) |

### Supported Source Environments

Physical servers, VMware vSphere VMs, Microsoft Azure VMs, Google Cloud VMs, other cloud providers, EC2 instances in other AWS Regions; both Linux and Windows operating systems supported.

### Key Features

| Feature | Description |
|---|---|
| **Continuous block-level replication** | Agent replicates every disk write to the staging area in near real-time; no snapshot-based gaps |
| **Automatic server conversion** | On recovery, AWS converts the source server image to boot natively as an EC2 instance |
| **Drill testing** | Launch up to 100 recovery instances simultaneously for non-disruptive testing; production replication continues unaffected; drill instances are isolated |
| **Failback** | After recovery, use `reverse-replication` to replicate data back from AWS to the original or an alternate primary site |
| **Point-in-time recovery** | Choose the most recent state or restore from a previous snapshot for application-consistent recovery |
| **Instance right-sizing** | Automatically matches recovery instance type to source server hardware profile |
| **No idle infrastructure costs** | Staging area uses minimal compute and low-cost EBS storage; full EC2 capacity only consumed during drills or actual recovery |

### Recovery Workflow

1. Initialize DRS service in target Region
2. Install AWS Replication Agent on each source server
3. Configure replication settings (subnet, EBS type, encryption, snapshot retention)
4. Configure launch settings (instance type, VPC, security groups, tags)
5. Monitor replication state; perform periodic drill tests
6. On disaster: initiate recovery → AWS launches recovery instances in target VPC
7. On resolution: use `reverse-replication` → replicate back to primary → failback

### Important Constraints

- Agent must be installed per server; agentless replication is not supported
- Replication traffic uses TCP port 1500 inbound to the staging area subnet security group
- Drills consume AWS resources (EC2 + EBS) for the duration; charges apply
- Failback requires generating DRS-specific credentials and installing the Failback Client on the recovery instance
- DRS must be initialized separately in each target AWS Region where it will be used
