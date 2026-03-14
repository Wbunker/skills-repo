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

Load these only when the topic requires it:

| Reference | Load when... |
|---|---|
| [services-catalog.md](references/services-catalog.md) | User asks "what AWS service does X", needs service comparison, or wants a full catalog overview |
| [compute.md](references/compute.md) | EC2, Lambda, ECS, EKS, Fargate, Batch, Elastic Beanstalk, Graviton |
| [storage.md](references/storage.md) | S3, EBS, EFS, FSx variants, Storage Gateway, Backup, DataSync, Snow Family |
| [database.md](references/database.md) | Aurora, RDS, DynamoDB, ElastiCache, MemoryDB, Neptune, Timestream, DocumentDB, Keyspaces |
| [networking.md](references/networking.md) | VPC, CloudFront, Route 53, Direct Connect, Transit Gateway, Load Balancers, PrivateLink, VPC Lattice |
| [security-iam-capabilities.md](references/security-iam-capabilities.md) | IAM concepts/policies/roles, Cognito, KMS, GuardDuty, Security Hub, WAF, Shield, Network Firewall — what each service does and its key features |
| [security-iam-cli.md](references/security-iam-cli.md) | CLI commands for all security/identity services: IAM, STS, Organizations, KMS, Secrets Manager, GuardDuty, Inspector, Macie, WAF, Shield, etc. |
| [ml-ai.md](references/ml-ai.md) | Bedrock, SageMaker, Amazon Q, Nova models, Rekognition, Comprehend, Transcribe, Translate, Lex |
| [analytics.md](references/analytics.md) | Redshift, Athena, EMR, Glue, Kinesis, MSK, OpenSearch, QuickSight, Lake Formation, DataZone |
| [management-devops.md](references/management-devops.md) | CloudFormation, CDK, CloudTrail, CloudWatch, Systems Manager, Control Tower, Config, OpsWorks |
| [serverless-integration.md](references/serverless-integration.md) | Lambda patterns, API Gateway, Step Functions, EventBridge, SQS, SNS, AppSync, MQ |
| [containers.md](references/containers.md) | ECS, EKS, ECR, Fargate, App Runner, EKS Anywhere, App Mesh |
| [cost-optimization.md](references/cost-optimization.md) | Savings Plans, Spot, Cost Explorer, Budgets, Trusted Advisor, right-sizing, tagging strategy |

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
