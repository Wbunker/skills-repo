# Image Builder / Edge Compute / SAR — Capabilities Reference

For CLI commands, see [image-builder-edge-cli.md](image-builder-edge-cli.md).

## Amazon EC2 Image Builder

**Purpose**: Fully managed service that automates the creation, testing, and distribution of hardened, up-to-date AMIs and container images; eliminates manual patching and image maintenance by defining reusable pipelines.

### Core Concepts

| Concept | Description |
|---|---|
| **Image Pipeline** | Top-level automation resource that ties together a recipe, infrastructure config, distribution config, and optional schedule |
| **Image Recipe** | Versioned document specifying a base AMI + ordered list of build and test components; produces an AMI output |
| **Container Recipe** | Versioned document specifying a base container image + components; produces an OCI image pushed to ECR |
| **Component** | Declarative YAML document (executed by AWSTOE) that defines steps in the build, validate, or test phase |
| **Infrastructure Configuration** | Defines the EC2 instance type, IAM instance profile, VPC/subnet/security groups, and logging settings used during the build |
| **Distribution Configuration** | Defines target AWS Regions, KMS encryption keys, AMI sharing (accounts/Organizations), and Launch Template associations |
| **AWSTOE** | AWS Task Orchestrator and Executor; agent installed automatically on build/test instances; interprets component YAML |
| **Managed Image** | The output artifact (AMI or container image) plus associated metadata (version, platform, scan results) |

### Build Pipeline Stages

| Stage | Phase | What Happens |
|---|---|---|
| **Build** | Build | Base image launched; build components execute; instance stopped; snapshot taken |
| **Build** | Validate | Instance launched from new image; validate-phase components run; instance stopped |
| **Test** | Test | Instance launched from validated image; test components run; results recorded |
| **Distribute** | Distribution | Image copied to configured regions; encryption applied; sharing permissions set |

Image distribution only proceeds if all test phases pass.

### Component Document Structure (AWSTOE YAML)

```yaml
name: InstallNginx
description: Install and start nginx
schemaVersion: 1.0
phases:
  - name: build
    steps:
      - name: Install
        action: ExecuteBash
        inputs:
          commands:
            - yum install -y nginx
  - name: test
    steps:
      - name: CheckNginx
        action: ExecuteBash
        inputs:
          commands:
            - systemctl is-active nginx
```

### Key Features

- **Automated patching**: Schedule pipelines weekly/monthly; Image Builder pulls the latest OS patches into each new image version
- **Amazon Inspector integration**: Enable `imageScanningConfiguration` to run Inspector vulnerability scans against each built image; findings stored in ECR
- **AWS Organizations support**: Distribute and share images across all member accounts via a single distribution configuration
- **AWS RAM sharing**: Share components, image recipes, and container recipes across accounts without copying
- **Lifecycle policies**: Automatically deprecate or delete old image versions based on age or count thresholds
- **STIG hardening**: AWS-managed STIG components available for Windows and Linux to meet DoD/regulated-industry requirements
- **No additional charge**: Pay only for underlying EC2 instances, EBS snapshots, S3, Inspector, and ECR — not for Image Builder itself

### Use Case Patterns

- **Golden AMI pipeline**: Base Amazon Linux → OS patch component → hardening component → Inspector scan → distribute to all regions; Auto Scaling Groups reference the latest AMI version
- **Container image factory**: Base ECR image → install app dependencies → security scan → push to ECR; ECS/EKS deployments pull verified images
- **Compliance baseline**: STIG component + CIS benchmark test component → only distribute if 100% of tests pass

---

## AWS Local Zones

**Purpose**: Extensions of AWS Regions placed closer to large population and industry centers, enabling single-digit millisecond latency to end users for latency-sensitive applications.

### Core Concepts

| Concept | Description |
|---|---|
| **Local Zone** | An AWS infrastructure deployment in a metro area, operating as an extension of a parent AWS Region (e.g., Los Angeles as an extension of `us-west-2`) |
| **Opt-in** | Local Zones are not enabled by default; must opt in per Local Zone per account in the AWS console or via CLI |
| **Local Zone subnet** | A VPC subnet with an AZ ID pointing to a Local Zone; resources placed in this subnet run on Local Zone hardware |
| **Parent Region** | The full AWS Region that owns the Local Zone; control plane, S3, RDS (full), and most global services remain in the parent Region |

### Supported Services (subset)

EC2 instances, EBS volumes, ECS, EKS nodes, ALB, VPC subnets, ElastiCache, RDS (limited instance types), FSx for Windows File Server

### Use Cases

- Media and entertainment: live video production, on-set rendering, real-time collaboration
- Real-time gaming with low-latency player connections
- Financial trading requiring proximity to exchange co-location facilities
- AR/VR content delivery to metro areas
- Healthcare and government workloads with data residency requirements for specific states/cities

### vs. Outposts / Wavelength

| | Local Zones | Outposts | Wavelength |
|---|---|---|---|
| Location | AWS-operated metro edge facility | Customer on-premises data center | 5G telecom provider edge |
| Hardware ownership | AWS | AWS (on your site) | AWS |
| Latency target | Single-digit ms to metro end users | Sub-ms to on-premises systems | Ultra-low latency to 5G mobile devices |
| Primary use case | Latency to end users in a city | Hybrid on-premises workloads | 5G mobile edge computing |
| Connectivity | Standard internet / Direct Connect | Service Link to parent Region | Carrier network (no public internet hop) |

---

## AWS Wavelength

**Purpose**: Embeds AWS compute and storage directly inside 5G carrier networks at telecom provider data centers, enabling sub-10ms latency for mobile and connected devices without traffic leaving the carrier network.

### Core Concepts

| Concept | Description |
|---|---|
| **Wavelength Zone** | An AWS infrastructure deployment embedded at a telecom provider's 5G edge data center |
| **Carrier gateway** | VPC resource that provides inbound connectivity from the carrier network and outbound to the internet via the carrier |
| **Carrier IP** | Public IP address allocated from the carrier's address space; assigned to instances for 5G traffic routing |
| **Parent Region connection** | Wavelength Zone connects back to the parent AWS Region over a dedicated, high-bandwidth carrier backbone for access to regional services |

### How It Works

1. Create a VPC with a standard subnet in the parent Region and a Wavelength Zone subnet
2. Attach a carrier gateway to the VPC
3. Deploy EC2 instances in the Wavelength Zone subnet
4. Mobile devices on the 5G network reach instances through the carrier gateway without leaving the carrier network
5. Instances access regional AWS services (DynamoDB, RDS, S3) over the carrier backbone

### Supported Telecom Providers

Verizon (US), Vodafone (UK, Germany), KDDI (Japan), SK Telecom (South Korea), and select other regional carriers.

### Supported Services in Wavelength Zones

EC2 instances (t3.medium, t3.xlarge, r5.2xlarge, g4dn.2xlarge), EBS volumes, VPC subnets, carrier gateways, EC2 Auto Scaling, EKS, ECS, Systems Manager, CloudWatch, CloudTrail, CloudFormation

### Use Cases

- Real-time game streaming to 5G mobile devices
- Live video and event streaming to mobile audiences
- AR/VR applications requiring sub-10ms round-trip latency
- Connected vehicle data processing at the network edge
- ML video inference for real-time object detection on mobile
- IoT and industrial automation requiring ultra-low latency

---

## VMware Cloud on AWS

**Purpose**: Jointly engineered service (VMware + AWS) that lets you run VMware vSphere workloads on dedicated bare-metal EC2 infrastructure in AWS, enabling lift-and-shift migration of on-premises VMware environments without refactoring.

### Core Concepts

| Concept | Description |
|---|---|
| **SDDC (Software-Defined Data Center)** | The top-level VMware resource; a logical data center containing clusters, compute, networking, and storage; deployed in a chosen AWS Region/AZ |
| **Cluster** | One or more bare-metal EC2 hosts running the VMware stack; minimum 2 hosts for production (stretched cluster available for HA) |
| **vSphere** | VMware's hypervisor and management platform (vCenter + ESXi); same APIs and tools as on-premises |
| **vSAN** | VMware's hyper-converged storage layer; uses local NVMe on the bare-metal hosts; no separate EBS volumes |
| **NSX-T** | VMware's network virtualization; provides logical switching, routing, micro-segmentation, and distributed firewall |
| **HCX (Hybrid Cloud Extension)** | VMware migration tool included with VMware Cloud on AWS; enables live vMotion migration from on-premises vSphere to the SDDC |
| **ENI (Elastic Network Interface)** | Provides the AWS-side network connection between the SDDC and the customer's VPC for accessing AWS native services |

### Bare-Metal Host Types

| Host Type | vCPUs | RAM | NVMe Storage | Primary Use |
|---|---|---|---|---|
| **i3en.metal** | 96 | 768 GB | 60 TB NVMe | General VMware workloads (original offering) |
| **i4i.metal** | 128 | 1024 GB | 30 TB NVMe | Latest generation; better price-performance |

### Architecture

```
On-Premises vSphere  ──HCX──▶  VMware Cloud on AWS (SDDC)
                                  │  vCenter / vSphere / vSAN / NSX-T
                                  │  (bare-metal EC2 i3en/i4i)
                                  │
                               AWS ENI
                                  │
                              Customer VPC
                                  │
                    ┌─────────────┼─────────────┐
                   S3           RDS           Others
```

### Integration with AWS Native Services

- **Amazon S3**: Direct access from VMs as an object store (via ENI in connected VPC)
- **Amazon RDS / Aurora**: VMs connect to managed databases in the VPC
- **Amazon FSx**: Windows file shares accessible from VMs
- **AWS Direct Connect / VPN**: Connects the SDDC's management network back to on-premises
- **AWS IAM / KMS**: Role-based access and encryption key management for the ENI connection
- **Amazon CloudWatch**: SDDC-level metrics forwarded via the AWS management plane

### Key Features

- VMware manages the SDDC software stack; AWS manages the underlying bare-metal hardware
- On-demand (hourly) and 1- or 3-year subscription pricing
- **Stretched cluster**: Hosts split across two AZs for zero-RPO/RTO storage HA
- Same VMware APIs, CLI tools (PowerCLI, govc), and operational runbooks as on-premises
- vCenter is accessible over the internet or Direct Connect; no VPN into the SDDC required for management

### Use Cases

- Lift-and-shift VMware workloads to AWS without VM refactoring
- Data center evacuation (contract expiry, consolidation)
- Disaster recovery target for on-premises VMware (using Site Recovery Manager or Zerto)
- Dev/test environments sharing the same VMware toolchain as production
- Burst capacity: extend on-premises capacity to AWS elastically

---

## AWS Serverless Application Repository (SAR)

**Purpose**: Managed catalog for discovering, deploying, and publishing serverless applications defined as AWS SAM templates; enables teams to share and reuse pre-built Lambda-based architectures without writing CloudFormation from scratch.

### Core Concepts

| Concept | Description |
|---|---|
| **Application** | A packaged serverless app defined by a SAM template + code artifacts stored in S3; has a unique ARN |
| **SAM template** | The `template.yaml` defining Lambda functions, APIs, DynamoDB tables, and other resources; extended CloudFormation |
| **SemanticVersion** | Each published version of an app follows semver (e.g., `1.2.3`); consumers can pin to a specific version |
| **Metadata block** | `AWS::ServerlessRepo::Application` section in the SAM template that provides name, author, description, license, and README |
| **Nested application** | A SAR application embedded inside another SAM template via `AWS::Serverless::Application` resource type |
| **Capabilities** | IAM acknowledgments required at deploy time: `CAPABILITY_IAM`, `CAPABILITY_NAMED_IAM`, `CAPABILITY_AUTO_EXPAND` |

### SAM Template Metadata Block

```yaml
Metadata:
  AWS::ServerlessRepo::Application:
    Name: my-app
    Description: Example serverless app
    Author: platform-team
    SpdxLicenseId: Apache-2.0
    LicenseUrl: LICENSE.txt
    ReadmeUrl: README.md
    Labels: ['s3', 'trigger', 'processing']
    HomePageUrl: https://github.com/org/my-app
    SemanticVersion: 1.0.0
    SourceCodeUrl: https://github.com/org/my-app
```

### Publishing Workflow

1. Write Lambda function code and SAM `template.yaml`
2. Add `AWS::ServerlessRepo::Application` metadata block
3. Run `sam package` to zip code and upload to S3; produces `packaged.yaml` with S3 URIs
4. Run `sam publish --template packaged.yaml` to publish to SAR
5. By default, the app is private; explicitly share with specific accounts or make public via resource policy

### Deployment Workflow (Consumer)

1. Browse SAR in the console or search via CLI
2. Review README, source code URL, and required capabilities
3. Create a CloudFormation change set via `aws serverlessrepo create-cloud-formation-change-set`
4. Review and execute the change set; SAR app deploys as a CloudFormation stack
5. Manage/delete via standard CloudFormation stack operations

### Visibility Options

| Visibility | Who Can See | How to Set |
|---|---|---|
| **Private** | Only the publishing account | Default |
| **Shared** | Specific AWS account IDs | Resource-based policy granting specific principals |
| **Public** | All AWS accounts | Resource-based policy granting `*` principal |

### Key Features

- **No additional charge**: Pay only for underlying Lambda, API Gateway, and other deployed resources
- **Nested applications**: Compose complex architectures by nesting SAR apps inside SAM templates; requires `CAPABILITY_AUTO_EXPAND`
- **CloudFormation integration**: Each deployment creates a standard CloudFormation stack; full lifecycle management, drift detection, and rollback
- **AWS-published apps**: AWS provides reference apps for common patterns (S3 trigger, DynamoDB stream processor, Lex chatbot, etc.)
- **Private app sharing**: Share across accounts in an AWS Organization without making apps public

### Use Case Patterns

- **Platform team golden patterns**: Publish approved Lambda deployment patterns (logging, tracing, error handling) to an internal SAR catalog; dev teams deploy without copying boilerplate
- **ISV distribution**: Publish a SaaS integration as a SAR app; customers deploy in one click without seeing source code
- **Nested composition**: Build a data pipeline by composing three SAR apps (ingest → transform → load) as nested applications in a parent SAM template
