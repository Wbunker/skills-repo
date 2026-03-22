# Azure Services Catalog

Complete reference of Azure services organized by category (current as of Q1 2026, 240+ distinct services).

## Table of Contents
1. [Compute](#compute)
2. [Containers](#containers)
3. [Storage](#storage)
4. [Databases](#databases)
5. [Networking & Content Delivery](#networking--content-delivery)
6. [Analytics](#analytics)
7. [AI & Machine Learning](#ai--machine-learning)
8. [Security & Identity](#security--identity)
9. [Management & Governance](#management--governance)
10. [Developer Tools & DevOps](#developer-tools--devops)
11. [Integration & Messaging](#integration--messaging)
12. [Internet of Things](#internet-of-things)
13. [Media Services](#media-services)
14. [Migration & Transfer](#migration--transfer)
15. [Business Applications](#business-applications)
16. [End User Computing](#end-user-computing)
17. [Front-End Web & Mobile](#front-end-web--mobile)
18. [Healthcare & Life Sciences](#healthcare--life-sciences)
19. [Game Technology](#game-technology)
20. [Industry-Specific & Specialized](#industry-specific--specialized)

---

## Compute

| Service | Azure Category | Primary Use Case | AWS Equivalent | Pricing Model |
|---|---|---|---|---|
| **Azure Virtual Machines** | Compute | IaaS virtual servers (Windows and Linux) | EC2 | Pay-as-you-go / Reserved / Spot |
| **Azure VM Scale Sets (VMSS)** | Compute | Auto-scaling groups of identical VMs (Uniform or Flexible orchestration) | EC2 Auto Scaling | Pay-as-you-go / Reserved |
| **Azure App Service** | Compute | PaaS for web apps, APIs, and mobile backends (.NET, Node, Python, Java, PHP) | Elastic Beanstalk / App Runner | App Service Plan (fixed tier) |
| **Azure Functions** | Compute | Event-driven serverless compute (Consumption / Flex / Premium / App Service) | Lambda | Consumption / Premium / App Service |
| **Azure Batch** | Compute | Large-scale parallel and HPC job scheduling | AWS Batch | Per VM usage |
| **Azure Service Fabric** | Compute | Microservices orchestration platform (stateful/stateless services, actors) | ECS (Service Fabric equivalent) | Per VM node |
| **Azure Service Fabric Managed Clusters** | Compute | Simplified managed Service Fabric (single resource for cluster + node types) | — | Per node |
| **Azure Spring Apps** | Compute | Managed Spring Boot / Spring Cloud hosting (Basic/Standard/Enterprise) | — | Per vCore/hour |
| **Azure CycleCloud** | Compute | HPC cluster orchestration (Slurm, PBS, Grid Engine, LSF) | AWS ParallelCluster | Per VM usage |
| **Azure VMware Solution (AVS)** | Compute | Run VMware vSphere workloads natively on Azure | VMware Cloud on AWS | Dedicated bare metal |
| **Azure Dedicated Host** | Compute | Single-tenant physical servers for BYOL compliance | EC2 Dedicated Hosts | Per host/hour |
| **Azure Spot Virtual Machines** | Compute | Interruptible VMs at up to 90% discount | EC2 Spot Instances | Spot pricing |
| **Azure Compute Gallery** | Compute | Store, replicate, and share VM images and application packages | EC2 AMI + Image Builder | Free (storage costs) |
| **Azure Lab Services** | Compute | Managed lab environments for training and education (retiring 2025 → use Dev Box) | — | Per lab hour |
| **Azure HPC Cache** | Compute | NFS caching for HPC workloads reading from on-prem NAS | — | Per cache size/hour |

---

## Containers

| Service | Azure Category | Primary Use Case | AWS Equivalent | Pricing Model |
|---|---|---|---|---|
| **Azure Kubernetes Service (AKS)** | Containers | Managed Kubernetes cluster (free control plane) | EKS | Free control plane; pay for nodes |
| **Azure Container Apps** | Containers | Serverless containers with KEDA autoscaling and Dapr; scale to zero | ECS Fargate / App Runner | Consumption / Dedicated |
| **Azure Container Instances (ACI)** | Containers | Serverless single containers or container groups; no cluster management | ECS Fargate (single task) | Per vCPU-second / GB-second |
| **Azure Container Registry (ACR)** | Containers | Private Docker/OCI image registry with geo-replication and ACR Tasks | ECR | Basic / Standard / Premium |
| **Azure Kubernetes Fleet Manager** | Containers | Manage and orchestrate multiple AKS clusters at scale (updates, workload placement) | — | Per cluster managed |
| **Azure Arc** | Hybrid | Extend Azure management (policy, RBAC, monitoring, GitOps) to any K8s, server, or data service | EKS Anywhere / ECS Anywhere | Per vCore/server managed |
| **Azure Red Hat OpenShift (ARO)** | Containers | Fully managed OpenShift Kubernetes platform | ROSA | Per cluster node |

---

## Storage

| Service | Azure Category | Primary Use Case | AWS Equivalent | Pricing Model |
|---|---|---|---|---|
| **Azure Blob Storage** | Storage | Object storage for unstructured data (block, append, page blobs) | S3 | Per GB stored + transactions |
| **Azure Data Lake Storage Gen2 (ADLS Gen2)** | Storage | Object storage with hierarchical namespace (HNS) for analytics workloads | S3 + Lake Formation | Per GB stored + transactions |
| **Azure Files** | Storage | Fully managed cloud file shares (SMB 3.x and NFS 4.1) | EFS / FSx for Windows File Server | Per GB provisioned |
| **Azure NetApp Files** | Storage | Enterprise-grade NFS/SMB for SAP HANA, Oracle, VDI, HPC (NetApp ONTAP) | FSx for NetApp ONTAP | Per capacity pool |
| **Azure Disk Storage (Managed Disks)** | Storage | Persistent block storage for VMs (Standard HDD/SSD, Premium SSD v1/v2, Ultra Disk) | EBS | Per GB provisioned (type-dependent) |
| **Azure Container Storage** | Storage | Kubernetes-native storage management for AKS (pools of disks, NVMe, ephemeral) | — | Per volume/hour |
| **Azure Managed Lustre** | Storage | High-performance parallel file system for HPC and AI training | FSx for Lustre | Per TB provisioned |
| **Azure Elastic SAN** | Storage | Cloud-native iSCSI SAN for block storage (database, VMs) | — | Per TiB provisioned |
| **Azure Backup** | Storage | Centralized backup for VMs, SQL, SAP HANA, AKS, Blob, Files, Disks | AWS Backup | Per instance + storage |
| **Azure Site Recovery (ASR)** | Storage / DR | Disaster recovery replication and failover (VM → Azure or region-to-region) | CloudEndure / DRS | Per protected instance |
| **Azure Archive Storage** | Storage | Long-term data archival (lowest cost, hours retrieval) | S3 Glacier Deep Archive | Per GB stored |
| **Azure Queue Storage** | Storage | Simple HTTP/S message queuing (up to 64 KB messages, 7-day TTL) | SQS | Per million transactions |
| **Azure Table Storage** | Storage | NoSQL key-value store (PartitionKey + RowKey); prefer Cosmos DB for new workloads | DynamoDB (basic) | Per GB + transactions |
| **Azure Data Box** | Storage | Physical offline data transfer devices (Disk 35TB / Box 80TB / Heavy 770TB) | Snowball / Snowcone | Per device order |
| **Azure StorSimple** | Storage | Hybrid cloud storage appliance (legacy) | Storage Gateway | Per appliance |
| **Azure Confidential Ledger** | Storage | Tamper-proof ledger backed by blockchain and TEE for audit trails | QLDB | Per transaction |

---

## Databases

| Service | Azure Category | Primary Use Case | AWS Equivalent | Pricing Model |
|---|---|---|---|---|
| **Azure SQL Database** | Databases | Fully managed relational SQL Server PaaS (General Purpose / Business Critical / Hyperscale / Serverless) | Aurora / RDS SQL Server | DTU or vCore; Serverless option |
| **Azure SQL Managed Instance** | Databases | Near 100% SQL Server compat (cross-DB queries, SQL Agent, CLR, linked servers) | RDS Custom for SQL Server | vCore-based |
| **SQL Server on Azure VMs** | Databases | Full SQL Server IaaS (BYOL or PAYG) with SQL IaaS Agent extension | RDS Custom / EC2 | Per VM + license |
| **Azure Database for PostgreSQL Flexible Server** | Databases | Managed PostgreSQL with full extension support (pgvector, PostGIS, Citus, pg_cron) | Aurora PostgreSQL / RDS PostgreSQL | vCore + storage |
| **Azure Database for MySQL Flexible Server** | Databases | Managed MySQL with HA, read replicas, PgBouncer | Aurora MySQL / RDS MySQL | vCore + storage |
| **Azure Database for MariaDB** | Databases | Managed MariaDB (retiring 2025 — migrate to PostgreSQL Flexible Server) | RDS MariaDB | vCore + storage |
| **Azure Cosmos DB (Core/NoSQL API)** | Databases | Globally distributed multi-model NoSQL; primary API with SQL-like query | DynamoDB | RU/s (provisioned/autoscale) or serverless |
| **Azure Cosmos DB for MongoDB** | Databases | Wire-compatible MongoDB API on Cosmos DB | DocumentDB | RU/s or serverless |
| **Azure Cosmos DB for MongoDB vCore** | Databases | MongoDB-compatible PaaS with vCore provisioning model (dedicated, native MongoDB) | DocumentDB Elastic Clusters | Per vCore + storage |
| **Azure Cosmos DB for Apache Cassandra** | Databases | Cassandra CQL-compatible API on Cosmos DB | Keyspaces | RU/s or serverless |
| **Azure Cosmos DB for Apache Gremlin** | Databases | Graph database (property graph, Gremlin query language) | Neptune | RU/s or serverless |
| **Azure Cosmos DB for Table** | Databases | Cosmos DB with Azure Table Storage-compatible API (global distribution, SLAs) | DynamoDB (basic) | RU/s or serverless |
| **Azure Managed Instance for Apache Cassandra** | Databases | Fully managed native Apache Cassandra (open-source, not Cosmos DB layer) | Keyspaces / EC2 Cassandra | Per node/hour |
| **Azure Cache for Redis** | Databases | In-memory cache and session store (Basic/Standard/Premium/Enterprise/Enterprise Flash) | ElastiCache for Redis | Per node size / Enterprise |
| **Azure Synapse Analytics (dedicated SQL pool)** | Databases / Analytics | Cloud data warehouse (formerly SQL DW), MPP, DWU-based | Redshift | Per DWU (Data Warehouse Unit) |
| **Azure Database Migration Service (DMS)** | Databases | Migrate on-prem databases to Azure (online/offline, SQL/Oracle/MySQL/PG/Mongo) | AWS DMS | Per compute tier |

---

## Networking & Content Delivery

| Service | Azure Category | Primary Use Case | AWS Equivalent | Pricing Model |
|---|---|---|---|---|
| **Azure Virtual Network (VNet)** | Networking | Private network isolation (subnets, NSGs, route tables, peering, service endpoints) | VPC | Free (outbound bandwidth charged) |
| **Azure Virtual Network Manager (AVNM)** | Networking | Centrally manage VNets at scale (security admin rules, connectivity configs) | — | Per policy/month |
| **Azure Load Balancer** | Networking | L4 TCP/UDP load balancing (regional; internal or external; Standard SKU) | NLB | Per rule + data processed |
| **Azure Application Gateway** | Networking | L7 HTTP/HTTPS regional load balancer with WAF v2 | ALB + WAF | Per gateway hour + capacity units |
| **Azure Front Door** | Networking | Global L7 HTTP load balancing, CDN, WAF, URL rewrite (Standard/Premium) | CloudFront + Global Accelerator | Per GB + request |
| **Azure Traffic Manager** | Networking | DNS-based global traffic routing (Priority/Weighted/Performance/Geographic/Subnet) | Route 53 routing policies | Per DNS query |
| **Azure CDN** | Networking | Content delivery network (Microsoft / Verizon / Akamai profiles; consolidating into Front Door) | CloudFront | Per GB transferred |
| **Azure ExpressRoute** | Networking | Dedicated private connectivity to Azure datacenters (50 Mbps–100 Gbps) | Direct Connect | Per circuit speed + gateway |
| **Azure VPN Gateway** | Networking | IPsec/IKE VPN tunnels to on-premises (S2S, P2S, VNet-to-VNet) | Site-to-Site VPN | Per gateway SKU + tunnel |
| **Azure Virtual WAN** | Networking | Managed hub-and-spoke networking at scale (branch, VPN, ExpressRoute termination) | Transit Gateway | Per connection + data |
| **Azure Route Server** | Networking | BGP route exchange between NVAs and Azure VNets (dynamic routing without UDRs) | — | Per hour |
| **Azure Firewall** | Networking | Managed stateful L3–L7 cloud-native firewall (Standard/Premium/Basic) | AWS Network Firewall | Per deployment hour + data |
| **Azure Web Application Firewall (WAF)** | Networking | OWASP-based WAF on App Gateway or Front Door | AWS WAF | Per rule + request |
| **Azure DDoS Protection** | Networking | Volumetric, protocol, and application-layer DDoS mitigation (Network/IP SKUs) | AWS Shield Advanced | Per protected network/IP |
| **Azure Bastion** | Networking | Browser-based or native-client RDP/SSH without public IPs on VMs | EC2 Instance Connect Endpoint | Per host hour + data |
| **Azure Private Link / Private Endpoints** | Networking | Private IP access to Azure PaaS over VNet (no internet traversal) | AWS PrivateLink | Per endpoint hour + data |
| **Azure NAT Gateway** | Networking | Managed outbound SNAT for private subnets (up to 16 public IPs, 64K ports/IP) | VPC NAT Gateway | Per hour + data |
| **Azure DNS (Public Zones)** | Networking | Authoritative public DNS hosting with Anycast | Route 53 | Per zone + query |
| **Azure Private DNS Zones** | Networking | DNS resolution within VNets; required for Private Endpoint name resolution | Route 53 Private Hosted Zones | Per zone + query |
| **Azure DNS Private Resolver** | Networking | Conditional DNS forwarding between on-premises and Azure (replaces DNS forwarder VMs) | Route 53 Resolver | Per endpoint/hour |
| **Azure Network Watcher** | Networking | Network monitoring, diagnostics, packet capture, topology, flow logs, Traffic Analytics | VPC Reachability Analyzer + Flow Logs | Per check + flow log |
| **Azure Peering Service** | Networking | Optimized internet routing to Microsoft network via partner ISPs | AWS Global Accelerator (peering tier) | Per prefix/month |
| **Azure Network Function Manager** | Networking | Deploy partner network functions (firewall, SD-WAN) on Azure Stack Edge | AWS Marketplace NF | Per NF deployment |
| **Azure Programmable Connectivity (APC)** | Networking | Telco API access (SIM swap, location, number verify) via operator APIs | — | Per API call |

---

## Analytics

| Service | Azure Category | Primary Use Case | AWS Equivalent | Pricing Model |
|---|---|---|---|---|
| **Azure Synapse Analytics** | Analytics | Unified analytics workspace (dedicated SQL pool + serverless SQL + Spark + pipelines) | Redshift + Glue + Athena | Serverless SQL (per TB) + dedicated DWUs |
| **Microsoft Fabric** | Analytics | Unified SaaS analytics platform (OneLake, Lakehouse, Warehouse, Real-Time Intelligence, Power BI, Data Factory) | — | Per Fabric capacity (F-SKU) |
| **Azure Data Factory (ADF)** | Analytics | Cloud ETL/ELT pipeline orchestration (100+ connectors, mapping data flows) | AWS Glue | Per activity run + DIU hours |
| **Azure Databricks** | Analytics | Apache Spark-based unified data and AI platform (Delta Lake, Unity Catalog, Photon) | EMR + SageMaker | Per DBU (Databricks Unit) |
| **Azure Event Hubs** | Analytics | Real-time streaming ingestion (Kafka-compatible; Standard/Premium/Dedicated) | Kinesis Data Streams + MSK | Per throughput unit + events |
| **Azure Stream Analytics** | Analytics | Real-time stream processing with SQL-like SAQL (inputs: Event Hubs, IoT Hub; outputs: Cosmos DB, SQL, Power BI) | Kinesis Data Analytics (Flink) | Per streaming unit |
| **Azure Data Explorer (ADX / Kusto)** | Analytics | Sub-second log and time-series analytics at scale; KQL query language | — | Per cluster (compute + storage) |
| **Microsoft Purview (Data Governance)** | Analytics | Data catalog, data map, lineage, classification, data policy across multi-cloud | AWS Glue Data Catalog + Lake Formation | Per capacity unit |
| **Power BI Embedded** | Analytics | Embed Power BI reports and dashboards in custom applications (A-SKU) | QuickSight Embedded | Per A-SKU capacity/hour |
| **Azure Analysis Services** | Analytics | Enterprise-grade tabular semantic model (SSAS in cloud); note: Power BI Premium for new | — | Per QU (Query Unit) |
| **Azure HDInsight** | Analytics | Managed open-source clusters (Hadoop, Spark, Kafka, HBase, Hive LLAP) | EMR | Per cluster hour |
| **Azure Data Share** | Analytics | Securely share data with external organizations (snapshot or in-place sharing) | AWS Data Exchange | Per snapshot + storage |
| **Azure Open Datasets** | Analytics | Curated public datasets (weather, demographics, census) for ML and analytics | AWS Open Data | Free |

---

## AI & Machine Learning

| Service | Azure Category | Primary Use Case | AWS Equivalent | Pricing Model |
|---|---|---|---|---|
| **Azure OpenAI Service** | AI | GPT-4o, o1/o3 reasoning, DALL-E 3, Whisper, embeddings via Azure-hosted OpenAI | Amazon Bedrock (OpenAI models) | Per 1K tokens (model-dependent) |
| **Azure Machine Learning** | AI | End-to-end ML platform: training, pipelines, AutoML, MLflow, managed endpoints, Responsible AI | SageMaker | Per compute + storage |
| **Azure AI Foundry** | AI | GenAI app development hub (hub/project model, model catalog, prompt flow, agents, evaluation) | Amazon Bedrock Studio / SageMaker Studio | Per model token usage |
| **Azure AI Search (Cognitive Search)** | AI | AI-enriched full-text and vector search with semantic ranking and hybrid retrieval | OpenSearch Service / Kendra | Per search unit |
| **Azure AI Vision** | AI Services | Image analysis, dense captioning, OCR (Read API), spatial analysis, background removal | Rekognition | Per image/call |
| **Azure AI Speech** | AI Services | Speech-to-text (real-time + batch), text-to-speech (neural voices), speaker recognition, pronunciation assessment | Transcribe / Polly | Per audio hour / character |
| **Azure AI Language** | AI Services | NLP: NER, key phrase extraction, sentiment, opinion mining, summarization, CLU, QA | Comprehend | Per text unit |
| **Azure AI Document Intelligence** | AI Services | Form/document extraction, layout analysis, prebuilt models (invoice, receipt, ID, tax) | Textract | Per page |
| **Azure AI Translator** | AI Services | Real-time text and document translation (100+ languages), custom translator | Translate | Per character |
| **Azure AI Content Safety** | AI Services | Detect harmful content in text/images; prompt shields; groundedness detection | Rekognition (moderation) | Per API call |
| **Azure AI Face** | AI Services | Face detection, analysis, verification, identification (restricted access) | Rekognition Faces | Per call |
| **Azure AI Video Indexer** | AI | AI-powered video analysis (transcript, OCR, face tagging, scene, entities) | Rekognition Video + Transcribe | Per minute analyzed |
| **Azure AI Immersive Reader** | AI Services | Reading and comprehension assistance (dyslexia, language learners) embedded in apps | — | Per read session |
| **Azure AI Anomaly Detector** | AI Services | Time-series anomaly detection (univariate and multivariate); being consolidated into AI Services | — | Per API call |
| **Azure AI Metrics Advisor** | AI Services | Monitor business metrics with AI-powered anomaly detection and root-cause analysis | Lookout for Metrics | Per time series |
| **Azure AI Personalizer** | AI Services | Reinforcement learning-based content personalization (actions, context, reward loop) | Amazon Personalize | Per API call |
| **Azure Bot Service** | AI | Build, host, and connect conversational AI bots across channels (Teams, Slack, Web Chat) | Amazon Lex | Per message |
| **Azure Cognitive Services (multi-service)** | AI Services | Single endpoint/key for Vision, Speech, Language, Decision services | Amazon AI services | Bundled per call |
| **Azure AI Health Insights** | AI Services | Clinical AI: Radiology Insights, Clinical Matching, Patient Timeline, Oncology Insights | Comprehend Medical (partial) | Per API call |
| **Azure Health Bot** | Healthcare AI | HIPAA-compliant conversational healthcare bot with medical content | — | Per message |

---

## Security & Identity

| Service | Azure Category | Primary Use Case | AWS Equivalent | Pricing Model |
|---|---|---|---|---|
| **Microsoft Entra ID** | Identity | Cloud identity and access management (IAM, SSO, MFA, Conditional Access) | IAM + Identity Center + Cognito | Free / P1 / P2 per user/month |
| **Microsoft Entra ID Governance** | Identity | Access reviews, entitlement management, lifecycle workflows, access packages | IAM Access Analyzer | P2 / Governance license per user |
| **Microsoft Entra Privileged Identity Management (PIM)** | Identity | Just-in-time privileged access, time-bound assignments, approval workflows | IAM with time-based conditions | Entra ID P2 (included) |
| **Microsoft Entra External ID** | Identity | Customer and partner identity (B2C + B2B, replacing Azure AD B2C) | Cognito | Per MAU (Monthly Active User) |
| **Microsoft Entra Verified ID** | Identity | Decentralized identity credentials (verifiable credentials / DID) | — | Per verification |
| **Microsoft Entra Internet Access** | Identity / Security | Secure access to internet and SaaS (SSE — Security Service Edge, SWG) | — | Per user/month |
| **Microsoft Entra Private Access** | Identity / Security | Zero Trust Network Access (ZTNA) to replace VPN for private app access | — | Per user/month |
| **Azure Key Vault** | Security | Secrets, keys (RSA/EC), certificates management (Standard/Premium HSM) | Secrets Manager + KMS + ACM | Per operation + HSM |
| **Azure Key Vault Managed HSM** | Security | Single-tenant FIPS 140-2 Level 3 HSM for customer-managed keys | AWS CloudHSM | Per HSM hour |
| **Microsoft Defender for Cloud** | Security | Cloud security posture management (CSPM) and workload protection (CWPP) | Security Hub + GuardDuty | Per resource/month |
| **Microsoft Defender EASM** | Security | External Attack Surface Management — discover and monitor internet-exposed assets | — | Per asset/month |
| **Microsoft Sentinel** | Security | Cloud-native SIEM and SOAR (KQL analytics, playbooks, UEBA, threat intelligence) | Amazon Security Lake + OpenSearch | Per GB ingested |
| **Azure DDoS Protection** | Security | Network-layer volumetric/protocol DDoS mitigation (Network/IP protection tiers) | AWS Shield Advanced | Per protected network/IP |
| **Azure Web Application Firewall (WAF)** | Security | OWASP rule-set and bot protection (on App Gateway, Front Door, CDN) | AWS WAF | Per rule + request |
| **Azure Policy** | Governance | Organizational compliance rules enforced at scale (Deny/Audit/Modify/DeployIfNotExists) | AWS Config Rules + SCPs | Free |
| **Azure Blueprints** | Governance | Package policy, RBAC, and ARM for landing zones (deprecated → use Deployment Stacks) | AWS Control Tower customizations | Free |
| **Azure Deployment Stacks** | Governance | Manage related resources as a group with deny-assignments (replaces Blueprints) | AWS CloudFormation StackSets | Free |
| **Azure Management Groups** | Governance | Hierarchical subscription organization for policy and RBAC inheritance | AWS Organizations | Free |
| **Microsoft Purview (Compliance)** | Compliance | Data classification, compliance score, sensitivity labels, eDiscovery, DLP | Macie + Security Lake | Per capacity / M365 license |
| **Azure Attestation** | Security | Remote attestation for TEE environments (Intel SGX, SEV-SNP, TDX) | AWS Nitro Enclaves | Per call |
| **Azure Confidential Computing** | Security | Trusted Execution Environments (DCsv3 VMs with SEV-SNP / TDX) | EC2 Nitro Enclaves | Premium VM surcharge |

---

## Management & Governance

| Service | Azure Category | Primary Use Case | AWS Equivalent | Pricing Model |
|---|---|---|---|---|
| **Azure Monitor** | Management | Metrics, Logs (Log Analytics), alerts, dashboards, workbooks, autoscale | CloudWatch | Per GB ingested + alert rules |
| **Azure Monitor Managed Service for Prometheus** | Management | Managed Prometheus-compatible metrics store for AKS and VMs | Amazon Managed Service for Prometheus | Per metric sample ingested |
| **Azure Managed Grafana** | Management | Managed Grafana dashboards with Entra ID SSO; integrates with Azure Monitor | Amazon Managed Grafana | Per active user/month |
| **Log Analytics Workspace** | Management | Centralized log aggregation and KQL querying (backend for Azure Monitor Logs) | CloudWatch Logs + OpenSearch | Per GB ingested + retention |
| **Application Insights** | Management | APM for web apps and microservices (distributed tracing, live metrics, availability tests) | X-Ray + CloudWatch Application Insights | Per GB ingested |
| **Azure Resource Manager (ARM)** | Management | IaC deployment engine; Bicep and Terraform compile/target ARM | CloudFormation | Free |
| **Bicep** | Management | DSL for ARM deployments (preferred Azure-native IaC) | CDK (TypeScript equivalent) | Free |
| **Azure Advisor** | Management | Personalized recommendations for cost, security, reliability, performance, excellence | Trusted Advisor + Compute Optimizer | Free |
| **Azure Service Health** | Management | Personalized alerts for Azure service issues, planned maintenance, health advisories | AWS Personal Health Dashboard | Free |
| **Azure Resource Graph** | Management | Fast at-scale resource inventory queries (KQL) across all subscriptions | AWS Resource Explorer | Per query |
| **Azure Automation** | Management | Runbooks (PowerShell/Python), DSC configuration, change tracking, update management | Systems Manager Automation | Per job minute |
| **Azure Update Manager** | Management | Unified OS patch management for Azure VMs and Arc-enabled servers | Systems Manager Patch Manager | Per VM/month |
| **Azure Cost Management + Billing** | Management | Cost analysis, budgets, anomaly alerts, cost allocation, exports | Cost Explorer + Budgets + CUR | Free |
| **Azure Migrate** | Management | Discovery, assessment, and migration of on-prem servers, databases, and apps | Application Migration Service | Free assessment |
| **Azure Chaos Studio** | Management | Chaos engineering experiments for resilience testing (fault injection, blast radius) | AWS Fault Injection Simulator | Per fault-hour |
| **Azure Load Testing** | Management | Fully managed high-scale load testing service (Apache JMeter-compatible) | — | Per virtual user-hour |
| **Azure Lighthouse** | Management | Cross-tenant management for MSPs and partners (delegated resource management) | — | Free |
| **Azure Center for SAP Solutions** | Management | Centralized visibility, management, and quality checks for SAP on Azure | — | Free (pay for underlying resources) |
| **Azure Deployment Environments** | Management | Templated dev environments for developers from catalog (Bicep/ARM/Terraform) | AWS Service Catalog | Per environment-hour |

---

## Developer Tools & DevOps

| Service | Azure Category | Primary Use Case | AWS Equivalent | Pricing Model |
|---|---|---|---|---|
| **Azure DevOps** | DevOps | End-to-end DevOps (Boards, Repos, Pipelines, Artifacts, Test Plans) | CodeCatalyst / individual Code* | Per user / free tier |
| **GitHub Actions with Azure** | DevOps | CI/CD workflows with native Azure OIDC integration (no secrets) | CodePipeline + CodeBuild | Per workflow minute |
| **Azure Pipelines** | DevOps | CI/CD pipelines with multi-platform agent support (YAML + Classic) | CodePipeline + CodeBuild | Per parallel job |
| **Azure Artifacts** | DevOps | Universal package feed (NuGet, npm, Maven, PyPI, Universal Packages) | CodeArtifact | Per GB stored + network |
| **Azure Test Plans** | DevOps | Manual and exploratory testing management | — | Per user |
| **Azure DevTest Labs** | DevOps | Managed developer and test environments with cost controls, quotas, auto-shutdown | — | Per VM usage |
| **Microsoft Dev Box** | DevOps | Project-specific cloud developer workstations (Windows 11, SSO, Intune-managed) | — | Per dev box/hour |
| **Azure Developer CLI (azd)** | DevOps | End-to-end developer workflow (`azd up/down/deploy`) for cloud-native apps | SAM CLI | Free |
| **Microsoft Playwright Testing** | DevOps | Cloud-scale Playwright browser testing with parallel execution | — | Per browser minute |
| **Azure Cloud Shell** | DevOps | Browser-based shell (Bash/PowerShell) with az CLI, kubectl, Helm, Terraform pre-installed | CloudShell | Free (storage costs) |
| **Azure CLI (az)** | DevOps | Cross-platform command-line tool for all Azure services | AWS CLI | Free |
| **Azure PowerShell (Az module)** | DevOps | PowerShell module for Azure resource management | AWS Tools for PowerShell | Free |
| **Visual Studio Code (Azure extensions)** | DevOps | IDE with Bicep intellisense, Azure Functions, AKS, ARM, Terraform tools | AWS Toolkit for VS Code | Free |

---

## Integration & Messaging

| Service | Azure Category | Primary Use Case | AWS Equivalent | Pricing Model |
|---|---|---|---|---|
| **Azure Service Bus** | Integration | Enterprise async messaging: queues (FIFO, sessions, DLQ) and topics/subscriptions (pub-sub) | SQS + SNS | Per operation + namespace |
| **Azure Event Grid** | Integration | Managed event routing for Azure and custom events; supports MQTT broker (namespaces) | EventBridge | Per operation |
| **Azure Event Hubs** | Integration | High-throughput streaming ingestion (Kafka-compatible; Capture to ADLS/Blob) | Kinesis Data Streams | Per TU + events |
| **Azure Logic Apps** | Integration | Low-code workflow automation: Consumption (multi-tenant) and Standard (single-tenant VNet) | Step Functions + AppFlow | Per action / fixed (Standard) |
| **Azure API Management (APIM)** | Integration | Full-lifecycle API gateway, developer portal, policies, multi-region, self-hosted gateway | API Gateway | Per unit/hour |
| **Azure API Center** | Integration | Catalog and govern all APIs across the organization (complements APIM) | — | Per API/month |
| **Azure Functions** | Integration | Serverless event-driven compute triggered by 20+ Azure and custom triggers | Lambda | Consumption / Premium |
| **Azure Relay** | Integration | Hybrid connectivity for on-premises services without firewall changes | — | Per listener hour + messages |
| **Azure Web PubSub** | Integration | Real-time bidirectional WebSocket messaging at scale (100K+ connections) | API Gateway WebSocket | Per connection + message |
| **Azure SignalR Service** | Integration | Managed SignalR for real-time ASP.NET Core apps (hub pattern) | — | Per connection + message |
| **Azure Fluid Relay** | Integration | Real-time collaborative data synchronization for apps (Fluid Framework) | — | Per session |
| **Azure Data Factory (ADF)** | Integration | ETL/ELT and data pipeline orchestration (also under Analytics) | Glue + Step Functions | Per run + DIU |

---

## Internet of Things

| Service | Azure Category | Primary Use Case | AWS Equivalent | Pricing Model |
|---|---|---|---|---|
| **Azure IoT Hub** | IoT | Bidirectional device-to-cloud messaging, device twins, direct methods, device management | IoT Core | Per message unit |
| **Azure IoT Central** | IoT | SaaS IoT application platform (no-code/low-code device management + analytics) | IoT SiteWise Monitor | Per device/month |
| **Azure IoT Edge** | IoT | Run cloud workloads (containers) on edge devices; offline operation | Greengrass | Free (device compute costs) |
| **Azure IoT Operations** | IoT | Industrial IoT orchestration at the edge (MQTT broker, data processor pipeline, Akri) | — | Per device/month |
| **Azure Digital Twins** | IoT | Spatial intelligence graph modeling of physical environments (DTDL models) | AWS TwinMaker | Per operation + query |
| **Azure Device Provisioning Service (DPS)** | IoT | Zero-touch, at-scale device provisioning (X.509, TPM, symmetric key attestation) | IoT Fleet Provisioning | Per operation |
| **Azure Sphere** | IoT | Secured MCU OS and cloud security service for IoT hardware | FreeRTOS + IoT Device Defender | Per device license |
| **Azure RTOS (ThreadX)** | IoT | Real-time OS for microcontrollers (open-source, used in 12B+ devices) | FreeRTOS | Free / open source |
| **Azure Maps** | IoT / Spatial | Geospatial APIs (mapping, routing, geofencing, weather, indoor maps) | Amazon Location Service | Per transaction |
| **Azure Notification Hubs** | IoT / Mobile | Cross-platform push notifications at scale (FCM, APNs, WNS, HMS, ADM, Baidu) | SNS Mobile Push | Per push notification |

---

## Media Services

| Service | Azure Category | Primary Use Case | AWS Equivalent | Pricing Model |
|---|---|---|---|---|
| **Azure Media Services** | Media | Video encoding (H.264/H.265/AV1), packaging, live streaming, DRM content protection | MediaConvert + MediaPackage | Per output minute + streaming |
| **Azure AI Video Indexer** | Media | AI-powered video analysis (transcript, face tagging, scene, entities, topics) | Rekognition Video + Transcribe | Per minute analyzed |
| **Azure CDN** | Media | Content delivery for video and large media files (low-latency global distribution) | CloudFront | Per GB transferred |
| **Azure Communication Services (ACS)** | Media | CPaaS: programmable voice, video calling, SMS, email, chat APIs for apps | Chime SDK + Pinpoint + SES | Per message/minute/email |

---

## Migration & Transfer

| Service | Azure Category | Primary Use Case | AWS Equivalent | Pricing Model |
|---|---|---|---|---|
| **Azure Migrate** | Migration | Discovery, assessment, and agentless migration of VMs and apps to Azure | Application Migration Service | Free assessment; per migration |
| **Azure Database Migration Service (DMS)** | Migration | Migrate on-prem databases to Azure SQL / PostgreSQL / MySQL / Cosmos DB | AWS DMS | Per compute tier |
| **Azure Data Box** | Migration | Physical offline data transfer (Disk 35TB / Box 80TB / Heavy 770TB — ship to Azure DC) | Snowball / Snowcone | Per device order |
| **Azure Import/Export Service** | Migration | Ship your own drives to Azure datacenters for large data import/export | — | Per drive processed |
| **Azure Storage Migration Service** | Migration | File server-to-server or server-to-Azure Files migration | DataSync | Per GB transferred |
| **Azure File Sync** | Migration | Sync on-premises file servers to Azure Files (also used for cloud-tiering migration) | DataSync | Per server endpoint |
| **Azure Site Recovery (ASR)** | Migration / DR | Replication and failover for VMs (lift-and-shift to Azure or cross-region DR) | CloudEndure / DRS | Per protected instance |
| **Azure Arc** | Migration | Extend Azure management to on-prem after migration; Arc Data Services | ECS/EKS Anywhere | Per vCore managed |
| **App Service Migration Assistant** | Migration | Assess IIS web apps and migrate to Azure App Service | — | Free |
| **Azure Migrate Containerization Tool** | Migration | Containerize Java/ASP.NET apps for AKS or App Service | — | Free |

---

## Business Applications

| Service | Azure Category | Primary Use Case | AWS Equivalent | Pricing Model |
|---|---|---|---|---|
| **Power Apps** | Business Apps | Low-code business app development (canvas apps, model-driven apps on Dataverse) | — | Per user/app/month |
| **Power Automate** | Business Apps | Low-code workflow automation (cloud flows, desktop flows / RPA, AI Builder) | AppFlow | Per user / flow run |
| **Power BI** | Business Apps | Business intelligence and self-service analytics (Pro / Premium Per User / Premium Capacity) | QuickSight | Per user / Premium capacity |
| **Copilot Studio (Power Virtual Agents)** | Business Apps | Low-code chatbot builder with GPT integration, Teams/web channel | Amazon Lex | Per session |
| **Power Pages** | Business Apps | Low-code external-facing websites/portals backed by Dataverse | — | Per authenticated/anonymous user |
| **Microsoft Dataverse** | Business Apps | Enterprise relational data platform for Power Platform and Dynamics 365 | — | Per GB storage + capacity |
| **Dynamics 365** | Business Apps | ERP (Finance, Supply Chain, Operations) and CRM (Sales, Service, Marketing, Field) SaaS | — | Per user/month |
| **Azure Communication Services (ACS)** | Business Apps | Programmable voice, video, SMS, email, chat APIs for embedding in apps | Chime SDK + Pinpoint + SES | Per usage |
| **Microsoft Graph API** | Business Apps | Unified REST API for Microsoft 365 data (users, mail, Teams, SharePoint, OneDrive) | — | Included with M365 |

---

## End User Computing

| Service | Azure Category | Primary Use Case | AWS Equivalent | Pricing Model |
|---|---|---|---|---|
| **Azure Virtual Desktop (AVD)** | EUC | Managed multi-session Windows 10/11 desktops and RemoteApp streaming | WorkSpaces / AppStream 2.0 | Per VM hour + user license |
| **Windows 365** | EUC | Cloud PC — fixed-cost always-on persistent Windows desktop (Business / Enterprise / Frontline) | WorkSpaces Personal | Per Cloud PC/month |
| **Microsoft Dev Box** | EUC | Project-specific cloud developer workstations (also under Developer Tools) | — | Per dev box/hour |
| **Azure Lab Services** | EUC | Managed lab VMs for training and education (retiring 2025 — migrate to Dev Box / DevTest Labs) | — | Per lab hour |

---

## Front-End Web & Mobile

| Service | Azure Category | Primary Use Case | AWS Equivalent | Pricing Model |
|---|---|---|---|---|
| **Azure Static Web Apps** | Web & Mobile | Host static sites (React, Angular, Vue, Next.js, Blazor) + managed Functions API with global CDN | Amplify Hosting | Free / Standard tier |
| **Azure App Service (Web Apps)** | Web & Mobile | PaaS web hosting for .NET, Node.js, Python, Java, PHP with deployment slots | Elastic Beanstalk | Per App Service Plan |
| **Azure Notification Hubs** | Web & Mobile | Cross-platform push notifications at scale (also under IoT) | SNS Mobile Push | Per push notification |
| **Azure Spatial Anchors** | Web & Mobile | Multi-user shared AR spatial experiences (HoloLens, iOS, Android) | — | Per anchor query |
| **App Center (retiring March 2025)** | Web & Mobile | Build, test, distribute, and monitor mobile apps (→ migrate to Firebase / alternatives) | Device Farm | Per build / device-hour |

---

## Healthcare & Life Sciences

| Service | Azure Category | Primary Use Case | AWS Equivalent | Pricing Model |
|---|---|---|---|---|
| **Azure Health Data Services — FHIR Service** | Healthcare | HL7 FHIR R4 REST API for healthcare interoperability; SMART on FHIR; Bulk export | AWS HealthLake | Per GB stored + request |
| **Azure Health Data Services — DICOM Service** | Healthcare | Medical imaging (DICOMweb: WADO-RS, STOW-RS, QIDO-RS) storage and retrieval | AWS HealthImaging | Per GB stored |
| **Azure Health Data Services — MedTech Service** | Healthcare | IoMT device data ingestion (Event Hubs) → FHIR Observations mapping | — | Per message |
| **Azure Health Bot** | Healthcare | HIPAA-compliant conversational healthcare bot (triage, symptoms, medication info) | — | Per message |
| **Text Analytics for Health** | Healthcare | NLP extraction of clinical entities (diagnoses, medications, anatomy) from medical text | Comprehend Medical | Per text unit |
| **Azure AI Health Insights** | Healthcare | Clinical AI models: Radiology Insights, Clinical Matching, Patient Timeline, Oncology Insights | — | Per API call |
| **Azure Genomics** | Healthcare | Cloud-scale genomics analysis pipeline (BWA, GATK) | AWS HealthOmics | Per gigabase |

---

## Game Technology

| Service | Azure Category | Primary Use Case | AWS Equivalent | Pricing Model |
|---|---|---|---|---|
| **Azure PlayFab** | Gaming | Managed LiveOps backend (player auth, Economy v2, multiplayer, leaderboards, analytics) | GameLift Servers / GameSparks | Per MAU + premium features |
| **PlayFab Multiplayer Servers** | Gaming | Containerized game server fleet (auto-scale, geo-distributed, allocation API) | GameLift Servers | Per active server/hour |
| **AKS with Agones** | Gaming | Open-source game server lifecycle management on Kubernetes | GameLift Servers | Per node (AKS costs) |
| **Azure CDN / Front Door** | Gaming | Game asset delivery (patches, DLC, binaries) and low-latency API routing | CloudFront + Global Accelerator | Per GB + request |
| **Cosmos DB for Games** | Gaming | Global player state, leaderboards, real-time events (change feed) | DynamoDB Global Tables | Per RU/s |

---

## Industry-Specific & Specialized

| Service | Azure Category | Primary Use Case | Notes |
|---|---|---|---|
| **Azure Quantum** | Quantum Computing | Access to quantum hardware (IonQ, Quantinuum, Rigetti) and quantum simulators | Amazon Braket | Per quantum shot + simulation |
| **Azure Orbital** | Space | Ground station as a service for satellite contact scheduling and data downlink | AWS Ground Station | Per contact-minute |
| **Azure Orbital Analytics** | Space | Geospatial analytics pipeline for satellite imagery | — | Per imagery processed |
| **Azure Operator Nexus** | Telecom | On-premises Azure-managed platform for telco network functions (5G core, RAN) | AWS Outposts (telco) | Per rack/node |
| **Azure Operator 5G Core** | Telecom | Cloud-native 5G packet core (AMF, SMF, UPF) on Azure / Nexus | — | Per subscription |
| **Azure Private 5G Core** | Telecom | Deploy private 5G networks on enterprise premises with Azure management | — | Per SIM/month |
| **Azure Modeling and Simulation Workbench** | Simulation | Secure cloud enclave for semiconductor EDA workloads | — | Per compute hour |
| **Azure Data Manager for Agriculture** | Agriculture | Standardized data management for farm data (weather, soil, satellite, telemetry) | — | Per API call |
| **Microsoft Cloud for Financial Services** | Industry | Compliance, data solutions, and apps for FSI (regulatory, risk, customer 360) | — | Bundled solutions |
| **Microsoft Cloud for Retail** | Industry | Retail analytics, omnichannel, supply chain, and shopper personalization | — | Bundled solutions |
| **Microsoft Cloud for Manufacturing** | Industry | Connected factory, asset monitoring, supply chain, and sustainability | — | Bundled solutions |
| **Microsoft Cloud for Healthcare** | Industry | Care management, clinical data, patient engagement (built on Azure + M365 + D365) | AWS HealthLake (partial) | Bundled solutions |
| **Microsoft Cloud for Sustainability** | Industry | Carbon accounting, ESG data, and emissions reporting | — | Per capability |
| **Microsoft Cloud for Nonprofit** | Industry | Fundraising, volunteer management, program delivery (D365 + Power Platform) | — | Nonprofit pricing |
