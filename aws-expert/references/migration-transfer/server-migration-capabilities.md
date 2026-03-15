# AWS Server Migration — Capabilities Reference

For CLI commands, see [server-migration-cli.md](server-migration-cli.md).

## AWS Application Migration Service (MGN)

**Purpose**: Agent-based lift-and-shift service that continuously replicates source servers to AWS for rehosting. Evolved from CloudEndure Migration (which AWS acquired in 2019); MGN is now the primary AWS service for this use case.

### Core Concepts

| Concept | Description |
|---|---|
| **Source server** | Any physical, virtual, or cloud server you want to migrate; identified by the installed AWS Replication Agent |
| **AWS Replication Agent** | Lightweight software installed on the source; captures all block-level changes and streams them to a replication server in the target AWS account |
| **Replication server** | Temporary EC2 instance (t3.small by default) launched by MGN in your VPC to receive replicated data; terminated after cutover |
| **Staging area subnet** | Private subnet in your VPC where replication servers and staging volumes live during replication |
| **Launch template** | EC2 launch configuration applied when MGN launches test or production instances; includes instance type, subnet, security groups, IAM profile |
| **Test instance** | Non-disruptive copy launched to validate the migrated server before cutover |
| **Cutover instance** | Final production instance launched to replace the source server |
| **Replication lag** | Time between a change on the source and its arrival on the staging volume; typically seconds |
| **Data replication state** | Lifecycle state: Not started → Initial sync → Backlog → Replicated (continuous) → Disconnected |

### Agent Installation & Source Support

**Supported source operating systems:**

| Platform | Versions |
|---|---|
| **Windows Server** | 2003, 2008, 2008 R2, 2012, 2012 R2, 2016, 2019, 2022 |
| **Windows desktop** | 7, 8, 10, 11 |
| **RHEL / CentOS** | 5.0–5.11, 6.x, 7.x, 8.x, 9.x |
| **Ubuntu** | 12.04–22.04 LTS |
| **SLES** | 11, 12, 15 |
| **Debian** | 7–11 |
| **Oracle Linux** | 6.x, 7.x, 8.x |
| **Amazon Linux** | 1, 2, 2023 |

Agent requires outbound TCP 443 and TCP 1500 from source to AWS endpoints.

### Test / Cutover Workflow

1. **Initialize replication**: Install agent → replication begins → staging area populated
2. **Wait for "Ready for testing"**: Replication lag near zero, no backlog
3. **Launch test instance**: MGN converts staging volumes to EBS, launches EC2 with launch template settings
4. **Validate**: Verify application functionality, connectivity, performance
5. **Mark test as passed** (or revert and adjust launch settings)
6. **Launch cutover instance**: Same conversion flow; this is the production instance
7. **Finalize cutover**: Source server marked as cutover; cleanup removes staging resources

### Launch Settings (per source server)

| Setting | Description |
|---|---|
| **Instance type right-sizing** | MGN can recommend an instance type based on source CPU/RAM; or specify manually |
| **OS licensing** | License-included (pay-as-you-go) or BYOL (bring your own Windows/SQL license via Dedicated Hosts) |
| **Boot mode** | Legacy BIOS or UEFI |
| **Tenancy** | Shared, Dedicated Instance, Dedicated Host |
| **Public IP** | Assign automatically or use Elastic IP |
| **Security groups** | One or more SGs applied at launch |
| **IAM instance profile** | Role attached to the migrated EC2 |
| **Termination protection** | Prevent accidental termination |
| **Post-migration actions** | SSM documents or custom scripts run after cutover |

### Post-Migration Actions

Post-migration actions are AWS Systems Manager (SSM) documents or custom scripts defined per source server or at the wave/application level. They run automatically after a successful test or cutover launch. Common uses: domain join, install agents, configure software, update DNS.

### Waves and Applications

- **Application**: A logical grouping of source servers that are migrated together (e.g., all servers for a three-tier web app).
- **Wave**: A grouping of applications that are migrated in the same cutover window. Enables coordinated, large-scale migration scheduling.

### Replication Server Configuration

- Default instance type: `t3.small` (suitable for most workloads; increase for high-throughput sources)
- Staging volumes: EBS `gp3` by default; can be changed to `io1`/`io2` for high-IOPS sources
- Bandwidth throttling: Set per-agent in MGN console or via API
- Data-in-transit encryption: TLS 1.2+ always enabled; data-at-rest on staging volumes optionally encrypted with KMS

### CloudEndure Heritage

AWS Application Migration Service is the managed evolution of CloudEndure Migration. CloudEndure Migration is no longer available for new projects as of January 2024. Existing CloudEndure accounts were migrated to MGN. The underlying replication technology is the same; MGN adds native AWS console/API integration, IAM, and deeper service integrations.

---

## AWS Mainframe Modernization (AWS M2)

**Purpose**: Managed runtime environment for migrating and modernizing IBM z/OS and other mainframe workloads to AWS. Supports two paths: **rehosting** (run as-is) and **refactoring** (transform to modern architecture).

### Core Concepts

| Concept | Description |
|---|---|
| **Environment** | Managed runtime cluster (ECS-backed) in your VPC; runs mainframe applications |
| **Application** | Deployed mainframe workload; references S3-stored artifacts |
| **Runtime engine** | Either Micro Focus Enterprise Server (rehosting) or AWS Blu Age (refactoring) |
| **Deployment** | Versioned application artifact deployed to an environment |
| **Batch job** | JCL-based batch processing job managed and scheduled within M2 |
| **Data store** | Managed VSAM, EBCDIC, GDG, or relational data accessed by M2 applications |

### Runtime Engines

**Micro Focus Enterprise Server (Rehosting)**
- Runs COBOL, PL/I, JCL, and CICS/IMS workloads with minimal code changes
- Compatible execution of mainframe programs without source code transformation
- Supports VSAM file access, batch JCL scheduling, CICS online transaction processing
- License included in M2 pricing

**AWS Blu Age (Refactoring)**
- Automated refactoring of COBOL/RPG/PL/I to Java microservices
- Generates Spring Boot applications deployed as containers
- Blu Age Developer tooling for code review and customization
- Resulting applications are cloud-native and no longer mainframe-dependent

### Automated Refactoring Pipeline

1. Upload source code (COBOL, copybooks, JCL, maps) to S3
2. M2 Automated Refactoring analyzes and converts to Java
3. Generated Java/Spring Boot artifacts are stored in S3
4. Deploy to M2 environment or any container runtime (ECS, EKS)

### Data Migration

- **AWS Mainframe Modernization Data Replication**: Uses AWS DMS-compatible approach to replicate mainframe data files (VSAM, sequential) to Amazon RDS, Aurora, or DynamoDB
- **AWS Blu Age Data Layer**: Blu Age refactored apps use a compatibility layer to access data in relational form

### Environments & Deployment

| Feature | Detail |
|---|---|
| **High availability** | Multi-AZ deployment option |
| **Scaling** | Manual capacity adjustment (vCPUs); auto-scaling not currently supported |
| **VPC integration** | Runs in customer VPC; private endpoints supported |
| **Storage** | EFS-backed application file systems for persistent VSAM/GDG data |
| **Monitoring** | CloudWatch metrics, logs; M2 console provides job execution history |

### When to Use M2

- You have IBM z/OS COBOL or PL/I applications to migrate
- Rehosting path: minimal risk, fast migration, same business logic
- Refactoring path: reduce long-term mainframe licensing, modernize codebase
- Avoid if source is Unisys, Bull, or non-IBM mainframe (limited support)

---

## AWS Transform

**Purpose**: AI-powered agentic service for automated legacy code modernization. Uses generative AI to assess, plan, and execute code transformations across multiple legacy platforms.

### Transformation Targets

| Source Platform | Target | Notes |
|---|---|---|
| **.NET Framework** | .NET (modern cross-platform) | Upgrades .NET Framework apps to .NET 8+ |
| **Mainframe COBOL** | Java / cloud-native | Agentic conversion with human review steps |
| **VMware workloads** | AWS native (EC2, containers) | Assessment and migration planning |

### Key Concepts

| Concept | Description |
|---|---|
| **Transformation hub** | Central console for managing all transformation projects across account |
| **Assessment report** | AI-generated analysis of source code; identifies incompatibilities, effort, risk areas |
| **Conversion job** | A transformation run on a source code repository; produces converted code artifacts |
| **Human-in-the-loop** | For complex transformations, AI flags items for human review and approval before proceeding |
| **Code review** | Developer reviews AI-generated code changes in IDE or console before accepting |

### .NET Transformation Workflow

1. Connect source code repository (CodeCatalyst, CodeCommit, or upload ZIP)
2. AWS Transform runs assessment → generates compatibility report
3. Approve transformation → agent converts project files, dependencies, APIs
4. Review diff of changes in console
5. Accept changes → updated code committed to repository
6. Build and test with standard CI/CD pipeline

### Mainframe Transformation Workflow

1. Upload COBOL source, copybooks, JCL to S3
2. Run assessment to identify complexity, dependencies, data structures
3. Agent generates Java equivalents with compatibility shims
4. Human review of flagged items (complex transforms, ambiguous logic)
5. Accept → Java artifacts stored in S3, deployable to M2 or ECS

### CLI & Console Notes

AWS Transform is primarily console-driven. There is no dedicated `aws transform` CLI service at GA. Orchestration via console; artifacts are managed via S3. Integration with CodeCatalyst for repository connectivity.

### When to Use AWS Transform vs M2

| Scenario | Recommendation |
|---|---|
| Run COBOL as-is with minimal change | M2 (Micro Focus rehosting) |
| Convert COBOL to Java permanently | M2 (Blu Age) or AWS Transform (mainframe path) |
| Modernize .NET Framework apps | AWS Transform |
| VMware migration assessment | AWS Transform |
