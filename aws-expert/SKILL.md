---
name: aws-expert
description: >
  Deep AWS expertise for architecture, implementation, troubleshooting, and best practices
  across the full AWS service catalog (200+ services). Use when the user asks about:
  designing or reviewing AWS architectures, selecting AWS services for a use case, implementing
  AWS infrastructure (CDK, CloudFormation, Terraform), IAM and security policies, cost
  optimization, migration to AWS, serverless patterns, container orchestration (ECS/EKS),
  data pipelines and analytics, networking (VPC, Transit Gateway, Direct Connect), machine
  learning on AWS (Bedrock, SageMaker), compliance and governance, or any specific AWS service
  (EC2, S3, Lambda, RDS, DynamoDB, etc.). Also use for Well-Architected Framework reviews
  and AWS certification study guidance.
---

# AWS Expert

## Core Approach

1. Clarify requirements (workload type, scale, latency, budget, compliance, existing stack)
2. Select services using the **service selection principles** below
3. Design with the Well-Architected Framework pillars in mind
4. Provide concrete implementation guidance (CDK preferred; CloudFormation or Terraform if specified)
5. Call out trade-offs, costs, and operational complexity honestly

## Service Selection Principles

- **Managed over self-managed** unless control/cost trade-off clearly favors self-managed
- **Serverless first** for unpredictable or spiky workloads (Lambda, Fargate, Aurora Serverless, DynamoDB on-demand)
- **Right-size the database**: relational → Aurora/RDS, key-value → DynamoDB, graph → Neptune, time-series → Timestream, search → OpenSearch
- **Avoid over-engineering**: a simple SQS+Lambda pattern beats a full event mesh for most use cases
- **Region and AZ strategy**: always design for multi-AZ; multi-region only when RTO/RPO demands it

## Reference Files

Reference files use a **2-tier system**: load a domain index first to identify the specific namespace file needed, then load only that namespace file.

When a query touches multiple namespaces and context is limited, prioritize loading higher-ranked namespaces first — see [namespace-priority.md](references/namespace-priority.md) for the ranked list and criteria.

**Tier 1 — Domain indexes** (load to navigate to the right namespace):

| Domain Index | Load when... |
|---|---|
| [services-catalog.md](references/services-catalog.md) | User asks "what AWS service does X", needs service comparison, or wants a full catalog overview |
| [compute.md](references/compute.md) | EC2, Auto Scaling, Lambda, Batch, Elastic Beanstalk, Lightsail, Graviton, Outposts |
| [storage.md](references/storage.md) | S3, EBS, EFS, FSx, Backup, DataSync, Storage Gateway, Transfer Family, Snow Family |
| [database.md](references/database.md) | Aurora, RDS, DynamoDB, ElastiCache, MemoryDB, Neptune, Timestream, DocumentDB, Keyspaces, Redshift |
| [networking.md](references/networking.md) | VPC, CloudFront, Route 53, ELB, Direct Connect, Transit Gateway, PrivateLink, VPC Lattice, Global Accelerator, VPN, App Mesh |
| [security-iam.md](references/security-iam.md) | IAM, STS, Identity Center, Organizations, Cognito, KMS, GuardDuty, Security Hub, WAF, Shield, Network Firewall |
| [ml-ai.md](references/ml-ai.md) | Bedrock, SageMaker, Amazon Q, Rekognition, Comprehend, Transcribe, Translate, Lex, Personalize, Forecast, Kendra |
| [analytics.md](references/analytics.md) | Redshift, Athena, EMR, Glue, Kinesis, MSK, OpenSearch, QuickSight, Lake Formation, DataZone, Clean Rooms |
| [management-devops.md](references/management-devops.md) | CloudFormation, CDK, SAM, CloudTrail, CloudWatch, Systems Manager, Config, Control Tower, CodePipeline, X-Ray |
| [serverless-integration.md](references/serverless-integration.md) | Lambda, API Gateway, Step Functions, EventBridge, SQS, SNS, AppSync, MQ, AppFlow |
| [containers.md](references/containers.md) | ECS, ECR, EKS, Fargate, App Runner, App Mesh |
| [cost-optimization.md](references/cost-optimization.md) | Savings Plans, Reserved Instances, Spot, Compute Optimizer, Cost Explorer, Budgets, CUR, tagging |
| [iot.md](references/iot.md) | IoT Core, Greengrass, Device Management, Device Defender, SiteWise, TwinMaker, FleetWise, IoT Events, IoT Analytics, FreeRTOS |
| [media-services.md](references/media-services.md) | MediaLive, MediaConvert, MediaPackage, MediaConnect, MediaStore, MediaTailor, IVS, Kinesis Video Streams, Nimble Studio |
| [migration-transfer.md](references/migration-transfer.md) | Application Migration Service, DMS, DataSync, Snow Family, Transfer Family, Mainframe Modernization, AWS Transform |
| [business-applications.md](references/business-applications.md) | Amazon Connect, SES, Pinpoint, Chime SDK, WorkMail, WorkDocs, AppFabric, Supply Chain, Wickr |
| [end-user-computing.md](references/end-user-computing.md) | WorkSpaces, AppStream 2.0, WorkSpaces Web, WorkSpaces Thin Client |
| [front-end-web-mobile.md](references/front-end-web-mobile.md) | Amplify, AppSync, Location Service, Device Farm |
| [developer-tools.md](references/developer-tools.md) | CodeCatalyst, Cloud9, CloudShell, CodeCommit, CodeBuild, CodeDeploy, CodePipeline, CodeArtifact, Corretto |
| [game-technology.md](references/game-technology.md) | Amazon GameLift Servers (multiplayer hosting, FlexMatch), GameLift Streams (cloud game streaming) |
| [blockchain.md](references/blockchain.md) | Amazon Managed Blockchain — Hyperledger Fabric permissioned networks, Ethereum node access |
| [quantum.md](references/quantum.md) | Amazon Braket — QPU access (IonQ/Rigetti/D-Wave), quantum simulators, hybrid quantum-classical jobs |
| [satellite-robotics.md](references/satellite-robotics.md) | AWS Ground Station satellite contact scheduling, AWS RoboMaker robot simulation and WorldForge |
| [healthcare.md](references/healthcare.md) | HealthLake FHIR data store, HealthImaging DICOM, HealthOmics genomics, HealthScribe clinical notes, Comprehend Medical NLP, Transcribe Medical |

**Tier 2 — Namespace files**: Each domain index lists specific namespace files (e.g., `compute/ec2-capabilities.md`, `compute/ec2-cli.md`). Load only the namespace file(s) relevant to the user's question.

## Well-Architected Framework Quick Reference

| Pillar | Key Questions |
|---|---|
| Operational Excellence | Runbooks? Observability? CI/CD? IaC? |
| Security | Least privilege? Encryption at rest/transit? Compliance scope? |
| Reliability | Multi-AZ? Backup/DR? Auto Scaling? Circuit breakers? |
| Performance Efficiency | Right service? Caching? CDN? Graviton? |
| Cost Optimization | Reserved/Savings Plans? Right-sizing? Idle resources? |
| Sustainability | Graviton? Efficient instance types? Data lifecycle policies? |

## Common Architecture Patterns

**Web Application**: CloudFront → ALB → ECS/Fargate or Lambda → Aurora/DynamoDB → S3 (static assets)

**Event-Driven**: EventBridge → Lambda → SQS (with DLQ) → downstream services

**Data Lake**: S3 (raw/processed/curated) → Glue ETL → Athena/Redshift → QuickSight

**ML Platform**: S3 → SageMaker (training) → SageMaker Endpoints or Bedrock → API Gateway

**Microservices**: EKS or ECS → VPC Lattice → RDS/DynamoDB per service → EventBridge for async

**Batch Processing**: S3 event trigger → Lambda or AWS Batch → results to S3/DynamoDB

**Real-Time Streaming**: Kinesis Data Streams → Lambda/Flink → DynamoDB/S3/OpenSearch

## CDK Conventions

Prefer CDK (TypeScript) for IaC examples unless user specifies otherwise:

```typescript
// Prefer L2 constructs over L1 (Cfn*) unless L2 doesn't exist
// Use Stack props for environment-specific configuration
// Use Aspects for cross-cutting concerns (tagging, compliance)
// Use app stages (cdk.Stage) for multi-environment pipelines
// Use cdk-nag for security and best practice validation
```
