# Namespace Priority Ranking

Ranked by importance and usage frequency to guide which namespaces to load first when a query is ambiguous, and to inform skill maintenance prioritization.

## Ranking Criteria

Each namespace is scored on a weighted blend of five factors:

| Factor | Description |
|---|---|
| **Adoption breadth** | Estimated % of AWS accounts using this service |
| **Architectural centrality** | How many other services depend on or integrate with it |
| **Decision frequency** | How often architects/developers make non-trivial choices about it |
| **Market momentum** | Growth trajectory and active customer investment (2025–26) |
| **Cross-cutting leverage** | Knowing it deeply improves overall AWS proficiency |

---

## Top 30 Namespaces

| Rank | Namespace | Primary Reasoning |
|---|---|---|
| 1 | `security-iam/iam` | Every API call, every resource, every deployment touches IAM. Highest cross-cutting leverage of any namespace. |
| 2 | `storage/s3` | Used by ~99% of AWS accounts. Foundation for data lakes, static hosting, backups, artifacts, ML training — everything lands in S3. |
| 3 | `networking/vpc` | Every production workload lives in a VPC. Subnets, security groups, routing, and NAT are daily architectural decisions. |
| 4 | `compute/ec2` | Dominant compute primitive. Largest installed base; basis for ECS/EKS node groups and countless lift-and-shift workloads. |
| 5 | `compute/lambda` | Core serverless runtime. Drives the entire event-driven ecosystem; used directly and as glue behind dozens of other services. |
| 6 | `management-devops/cloudwatch` | Monitoring and logging are mandatory. Default observability plane — metrics, alarms, Logs, and dashboards required in every architecture. |
| 7 | `database/aurora-rds` | Most common relational database choice. Aurora spans MySQL/PostgreSQL/Serverless and is the default for OLTP workloads. |
| 8 | `database/dynamodb` | Most popular NoSQL database on AWS. Serverless, infinitely scalable, default for key-value and document workloads. |
| 9 | `serverless-integration/sqs-sns` | Fundamental async messaging in virtually every distributed architecture. SNS fan-out + SQS buffering is the most common integration pattern. |
| 10 | `management-devops/cloudformation` | IaC backbone of AWS. CDK and SAM both synthesize to CloudFormation. Stacks, changesets, and drift detection are essential knowledge. |
| 11 | `management-devops/cdk` | Rapidly becoming the preferred IaC layer for developer teams. TypeScript/Python construct model is replacing raw CloudFormation for new projects. |
| 12 | `serverless-integration/api-gateway` | Entry point for every HTTP/WebSocket API. REST, HTTP, and WebSocket tiers each have distinct trade-offs requiring active decisions. |
| 13 | `containers/ecs` | Most widely adopted AWS-native container orchestration. Simpler than EKS; enormous installed base. |
| 14 | `containers/eks` | Standard for Kubernetes workloads. Growing rapidly as Kubernetes adoption accelerates. |
| 15 | `ml-ai/bedrock` | Fastest growing by demand. GenAI is the #1 architectural initiative for most enterprises; Bedrock is the primary AWS entry point. |
| 16 | `networking/load-balancing` | ALB/NLB in front of nearly every production app — containers, EC2, Lambda. Target groups and listener rules are constant decision points. |
| 17 | `networking/cloudfront` | CDN for web apps, APIs, and S3-hosted content. Near-universal for user-facing workloads; also the WAF attachment point. |
| 18 | `security-iam/secrets-acm-cloudhsm` | Secrets Manager and ACM are near-universal — every production app rotates DB credentials and needs TLS certificates. |
| 19 | `serverless-integration/eventbridge` | Standard event bus for event-driven architectures; now also covers Pipes (polling sources) and Scheduler (replacing cron). |
| 20 | `security-iam/organizations-cognito` | Multi-account Organizations is table stakes beyond startup scale. Cognito is the default user auth layer for web/mobile apps. |
| 21 | `management-devops/systems-manager` | Parameter Store alone makes this essential — de facto config/secrets for many teams. Session Manager replaces bastion SSH. |
| 22 | `analytics/glue` | Standard ETL/data integration service. Data Catalog is the metadata layer for Athena, Redshift, and Lake Formation. |
| 23 | `storage/ebs` | Persistent block storage for EC2 and databases. Volume types, snapshots, and encryption are routine choices for every EC2 architecture. |
| 24 | `ml-ai/sagemaker` | Complete ML platform. Any team building custom models uses SageMaker for training, deployment, and MLOps. |
| 25 | `analytics/kinesis` | Real-time streaming core pattern. Data Streams, Firehose, and Flink cover the full streaming stack. |
| 26 | `developer-tools/cicd-pipeline` | CodePipeline/CodeBuild/CodeDeploy/CodeArtifact are the AWS-native DevOps stack. |
| 27 | `security-iam/verified-permissions-kms` | KMS underpins encryption for nearly every service — S3, RDS, Secrets Manager, EBS. Cedar authz via Verified Permissions growing. |
| 28 | `analytics/redshift` | Default AWS data warehouse. Serverless tier lowers barrier; Spectrum bridges S3 data lakes. |
| 29 | `serverless-integration/step-functions` | Workflow orchestration increasingly standard. Express/Standard workflows replace custom state management in Lambda chains. |
| 30 | `management-devops/sam` | Primary IaC framework for Lambda-centric serverless. `sam build/deploy/sync` is the daily workflow for serverless developers. |

---

## Ranks 31–40 (Honorable Mentions)

| Rank | Namespace |
|---|---|
| 31 | `networking/route53` — DNS essential but low decision surface area |
| 32 | `management-devops/cloudtrail` — mandatory for audit/compliance but architecturally simple |
| 33 | `containers/ecr` — used alongside ECS/EKS; decisions are straightforward |
| 34 | `security-iam/security-hub-inspector-macie` — growing rapidly with compliance requirements |
| 35 | `analytics/athena-emr` — Athena is the default serverless query layer over S3 |
| 36 | `networking/transit-gateway` — essential for multi-VPC / hybrid architectures |
| 37 | `storage/backup-datasync` — growing as governance and compliance requirements increase |
| 38 | `security-iam/waf-shield` — required for any internet-facing production application |
| 39 | `serverless-integration/lambda` — serverless-integration/lambda vs compute/lambda: covers event source mappings and integration patterns |
| 40 | `ml-ai/amazon-q` — Q Developer and Q Business adoption accelerating rapidly |

---

## Notes on Volatility

- **ml-ai/bedrock** (#15) is likely to move into the top 10 within 12 months as GenAI workloads mature.
- **containers/eks** (#14) continues rising as organizations standardize on Kubernetes.
- **management-devops/cdk** (#11) is displacing CloudFormation (#10) for new projects — ranks may swap.
- **security-iam** namespaces are collectively the highest-leverage domain; IAM (#1), organizations-cognito (#20), and KMS (#27) form a security triad that appears in every architecture review.
