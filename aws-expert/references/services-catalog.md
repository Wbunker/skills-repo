# AWS Services Catalog

Complete reference of AWS services organized by category (current as of early 2026, ~220+ distinct services).

## Table of Contents
1. [Compute](#compute)
2. [Containers](#containers)
3. [Storage](#storage)
4. [Database](#database)
5. [Networking & Content Delivery](#networking--content-delivery)
6. [Analytics](#analytics)
7. [Machine Learning & AI](#machine-learning--ai)
8. [Security, Identity & Compliance](#security-identity--compliance)
9. [Management & Governance](#management--governance)
10. [Cloud Financial Management](#cloud-financial-management)
11. [Developer Tools](#developer-tools)
12. [Application Integration](#application-integration)
13. [Internet of Things](#internet-of-things)
14. [Media Services](#media-services)
15. [Migration & Transfer](#migration--transfer)
16. [Business Applications](#business-applications)
17. [End User Computing](#end-user-computing)
18. [Front-End Web & Mobile](#front-end-web--mobile)
19. [Game Technology](#game-technology)
20. [Blockchain](#blockchain)
21. [Quantum Technologies](#quantum-technologies)
22. [Satellite](#satellite)
23. [Robotics](#robotics)

---

## Compute

| Service | Description |
|---|---|
| **Amazon EC2** | Resizable virtual servers with full control over compute (instance types, OS, networking) |
| **Amazon EC2 Auto Scaling** | Automatically adds/removes EC2 capacity based on demand using dynamic and predictive scaling |
| **Amazon EC2 Spot Instances** | Run fault-tolerant workloads on spare EC2 capacity for up to 90% off on-demand pricing |
| **Amazon EC2 Image Builder** | Build, test, and maintain secure Linux/Windows AMIs and container images via pipeline |
| **Amazon Lightsail** | Simplified VMs bundled with SSD storage, data transfer, DNS, and static IPs at fixed pricing |
| **AWS Batch** | Fully managed batch computing that dynamically provisions optimal infrastructure for jobs |
| **AWS Elastic Beanstalk** | Deploy and scale web apps (Java, .NET, PHP, Node.js, Python, Ruby, Go, Docker) without managing infrastructure |
| **AWS Lambda** | Run code without servers; pay per 100ms of execution time |
| **AWS Outposts** | Fully managed AWS infrastructure deployed on-premises for consistent hybrid experience |
| **AWS Local Zones** | Deploy latency-sensitive apps in AWS infrastructure closer to large population centers |
| **AWS Wavelength** | Ultra-low latency apps for 5G devices via infrastructure embedded in telecom datacenters |
| **AWS Snow Family** | Physical edge compute and data transfer devices (Snowcone, Snowball, Snowmobile) |
| **AWS Compute Optimizer** | Recommends optimal compute resources based on utilization metrics |
| **VMware Cloud on AWS** | Migrate and extend on-premises VMware vSphere environments to AWS |
| **AWS Serverless Application Repository** | Discover, deploy, and publish serverless applications using SAM templates |
| **AWS Savings Plans** | Flexible pricing model offering up to 72% savings on EC2, Lambda, and Fargate |

---

## Containers

| Service | Description |
|---|---|
| **Amazon ECS** | Managed container orchestration service native to AWS |
| **Amazon ECS Anywhere** | Run ECS-managed containers on customer-managed on-premises infrastructure |
| **Amazon ECR** | Fully managed Docker container registry for storing, managing, and deploying images |
| **Amazon EKS** | Fully managed Kubernetes service |
| **Amazon EKS Anywhere** | Create and operate Kubernetes clusters on your own on-premises infrastructure |
| **AWS Fargate** | Serverless compute engine for containers; no servers or clusters to manage |
| **AWS App Runner** | Fully managed service for deploying containerized web apps and APIs with automatic scaling |

---

## Storage

| Service | Description |
|---|---|
| **Amazon S3** | Object storage with virtually unlimited scale, 11 nines durability, built-in security |
| **Amazon S3 Vectors** | Purpose-built vector storage in S3 for billions of vectors with low-latency queries (GA 2025) |
| **Amazon EBS** | High-performance block storage for EC2; persists independently from instance life |
| **Amazon EFS** | Serverless, fully elastic shared file storage (NFS); scales automatically |
| **Amazon FSx for Lustre** | High-performance parallel file system for HPC, ML, and AI workloads |
| **Amazon FSx for NetApp ONTAP** | Fully managed NetApp ONTAP with enterprise data management on AWS |
| **Amazon FSx for OpenZFS** | Fully managed OpenZFS file storage for data-intensive workloads and NAS migrations |
| **Amazon FSx for Windows File Server** | Fully managed Windows-native shared file storage with full SMB support |
| **Amazon File Cache** | High-speed cache for datasets stored on-premises or in other clouds |
| **AWS Backup** | Centrally manage and automate backup across AWS services and hybrid environments |
| **AWS DataSync** | Automates and accelerates online data movement between on-premises and AWS storage |
| **AWS Elastic Disaster Recovery** | Fast, affordable application recovery using continuous replication |
| **AWS Storage Gateway** | Hybrid cloud storage connecting on-premises applications to AWS cloud storage |
| **AWS Transfer Family** | Managed SFTP/FTPS/FTP/AS2 file transfer into S3 or EFS |

---

## Database

| Service | Description |
|---|---|
| **Amazon Aurora** | MySQL/PostgreSQL-compatible relational DB; up to 5x faster, up to 128 TB distributed storage |
| **Amazon Aurora Serverless v2** | On-demand auto-scaling Aurora with fine-grained capacity adjustments |
| **Amazon RDS** | Managed relational DB: MySQL, MariaDB, PostgreSQL, Oracle, SQL Server, Db2 |
| **Amazon DynamoDB** | Serverless key-value/document DB; single-digit millisecond performance at any scale |
| **Amazon ElastiCache** | In-memory caching compatible with Valkey, Redis OSS, and Memcached |
| **Amazon MemoryDB** | Fully managed, durable in-memory database (Valkey/Redis OSS compatible) with Multi-AZ |
| **Amazon DocumentDB** | Fully managed MongoDB-compatible document database |
| **Amazon Keyspaces** | Managed, serverless Apache Cassandra-compatible database |
| **Amazon Neptune** | Fully managed graph database (Property Graph + RDF; Gremlin + SPARQL) |
| **Amazon Timestream** | Serverless time-series database for IoT and operational applications |
| **Amazon Redshift** | Fast, managed cloud data warehouse for petabyte-scale analytics |
| **Amazon Redshift Serverless** | Serverless Redshift; auto-provisions and scales without cluster management |
| **Oracle Database@AWS** | Oracle databases, RAC, and applications deployed and managed within AWS datacenters |

---

## Networking & Content Delivery

| Service | Description |
|---|---|
| **Amazon VPC** | Logically isolated virtual network for launching and controlling AWS resources |
| **Amazon CloudFront** | Global CDN accelerating websites, APIs, video, and data with 400+ PoPs |
| **Amazon Route 53** | Highly available DNS service with health checking and traffic routing policies |
| **AWS Global Accelerator** | Routes user traffic through AWS's global network for improved availability and latency |
| **Amazon VPC Lattice** | Application networking for service-to-service connectivity, security, and monitoring |
| **AWS Transit Gateway** | Central hub connecting VPCs and on-premises networks at scale |
| **AWS PrivateLink** | Private connectivity between VPCs and services without internet exposure |
| **AWS Direct Connect** | Dedicated private network connection from on-premises to AWS |
| **AWS VPN** | Encrypted tunnels connecting on-premises networks or remote users to AWS |
| **Elastic Load Balancing (ELB)** | Distributes traffic across targets: ALB (HTTP/7), NLB (TCP/4), GWLB (appliances), CLB (legacy) |
| **AWS App Mesh** | Service mesh providing application-level networking for microservices |
| **AWS Cloud Map** | Cloud resource discovery service for dynamically locating running services |
| **Amazon API Gateway** | Create, publish, maintain, monitor, and secure REST, HTTP, and WebSocket APIs |
| **AWS Verified Access** | Secure, VPN-less zero-trust access to corporate applications based on identity/device posture |
| **Amazon Route 53 Resolver DNS Firewall** | Filters and blocks DNS queries for known malicious domains from within VPCs |

---

## Analytics

| Service | Description |
|---|---|
| **Amazon Athena** | Serverless SQL query service for data in S3; pay per query |
| **Amazon CloudSearch** | Managed search for 34 languages with highlighting, autocomplete, geospatial search |
| **Amazon DataZone** | Data management for publishing, discovering, and governing data assets across sources |
| **Amazon EMR** | Big data platform for Spark, Hive, Flink, Hudi, and Presto |
| **Amazon FinSpace** | Data management and analytics purpose-built for financial services |
| **Amazon Kinesis Data Streams** | Massively scalable real-time data streaming; captures gigabytes per second |
| **Amazon Data Firehose** | Fully managed streaming data delivery to S3, Redshift, OpenSearch, Splunk |
| **Amazon Kinesis Video Streams** | Securely streams video from connected devices for analytics, ML, and playback |
| **Amazon Managed Service for Apache Flink** | Build and run streaming applications using SQL or Java |
| **Amazon MSK** | Fully managed Apache Kafka service for streaming data pipelines |
| **Amazon OpenSearch Service** | Managed search, analytics, and visualization (OpenSearch/Elasticsearch) |
| **Amazon OpenSearch Serverless** | Serverless OpenSearch for petabyte-scale workloads without cluster management |
| **Amazon QuickSight** | Cloud-powered BI for creating and publishing interactive dashboards |
| **Amazon Redshift** | Cloud data warehouse (also listed under Database) |
| **AWS Clean Rooms** | Analyze and collaborate on combined datasets without sharing raw data |
| **AWS Data Exchange** | Subscribe to and use third-party datasets directly in AWS |
| **AWS Glue** | Serverless ETL with Data Catalog, integration engines, and data quality features |
| **AWS Lake Formation** | Build, secure, and manage data lakes on S3 with fine-grained access control |
| **AWS Entity Resolution** | Match and link related records across applications using ML and rules |
| **AWS Data Pipeline** | Managed ETL for processing and moving data on schedules (largely superseded by Glue) |

---

## Machine Learning & AI

| Service | Description |
|---|---|
| **Amazon Bedrock** | Managed access to foundation models (Anthropic Claude, Meta Llama, Mistral, Cohere, Amazon Nova) via API |
| **Amazon Bedrock AgentCore** | Platform for deploying production-grade AI agents with runtime, tools, and guardrails |
| **Amazon Nova** | Amazon's family of frontier foundation models (Nova Micro, Lite, Pro, Canvas, Reel) |
| **Amazon SageMaker AI** | Comprehensive platform for building, training, and deploying ML models |
| **Amazon SageMaker HyperPod** | Purpose-built infrastructure for training and fine-tuning large models at scale |
| **Amazon SageMaker JumpStart** | One-click deployment of 150+ pre-trained ML models |
| **Amazon SageMaker Canvas** | No-code ML model building for business analysts |
| **Amazon SageMaker Clarify** | Detects bias and explains model predictions |
| **Amazon SageMaker Data Wrangler** | Data preparation and feature engineering |
| **Amazon SageMaker Feature Store** | Repository for storing, sharing, and accessing ML features |
| **Amazon SageMaker Autopilot** | Automatically builds, trains, and tunes the best ML model for a dataset |
| **Amazon Q** | Generative AI assistant for work, development, and business intelligence |
| **Amazon Q Business** | Enterprise generative AI assistant grounded in company data |
| **Amazon Q Developer** | AI assistant for software development: coding, debugging, testing, security scanning |
| **Amazon Augmented AI (A2I)** | Human review workflows for low-confidence ML predictions |
| **Amazon CodeGuru** | Intelligent recommendations for code quality and security vulnerability detection |
| **Amazon Comprehend** | NLP to extract insights from unstructured text |
| **Amazon Comprehend Medical** | NLP for extracting medical information from clinical text |
| **Amazon DevOps Guru** | ML-powered detection of anomalous application behavior |
| **Amazon Forecast** | Highly accurate time-series forecasting |
| **Amazon Fraud Detector** | ML-based detection of potentially fraudulent online activity |
| **Amazon Kendra** | Intelligent enterprise search powered by ML |
| **Amazon Lex** | Conversational chatbots and voice interfaces using ASR and NLU |
| **Amazon Lookout for Equipment** | Detects early warning signs of machine failures from sensor data |
| **Amazon Lookout for Vision** | Computer vision for spotting defects and anomalies in images |
| **Amazon Monitron** | End-to-end system for detecting abnormal industrial machinery behavior |
| **Amazon Nova Act** | AI service for building agents to automate browser-based tasks (GA 2025) |
| **Amazon Personalize** | Real-time individualized product and content recommendations |
| **Amazon Polly** | Text-to-speech across dozens of languages and voices |
| **Amazon Rekognition** | Image and video analysis: objects, scenes, faces, text, unsafe content |
| **Amazon Textract** | Extracts text, handwriting, forms, and tables from scanned documents |
| **Amazon Transcribe** | Automatic speech recognition (ASR) for converting speech to text |
| **Amazon Transcribe Medical** | ASR optimized for medical speech and clinical documentation |
| **Amazon Translate** | Neural machine translation across many languages |
| **AWS HealthLake** | HIPAA-eligible FHIR-format health data store and analytics |
| **AWS HealthScribe** | HIPAA-eligible automatic clinical notes from patient-clinician conversations |
| **AWS Panorama** | ML appliance for computer vision on on-premises IP cameras |
| **AWS Trainium** | Purpose-built ML chip for cost-efficient deep learning training |
| **AWS Inferentia** | Purpose-built ML chip for low-cost, high-performance inference |
| **Amazon PartyRock** | Code-free generative AI app builder for prompt engineering experimentation |

---

## Security, Identity & Compliance

| Service | Description |
|---|---|
| **AWS IAM** | Fine-grained access control for AWS services and resources |
| **AWS IAM Identity Center** | Centralized SSO across multiple AWS accounts and business applications |
| **Amazon Cognito** | User sign-up, sign-in, and access control for web and mobile apps |
| **Amazon Verified Permissions** | Fine-grained authorization for custom applications using Cedar policies |
| **AWS Directory Service** | Managed Microsoft Active Directory in the cloud |
| **AWS Resource Access Manager (RAM)** | Share AWS resources securely across accounts and Organizations |
| **AWS Organizations** | Policy-based governance and centralized management across multiple accounts |
| **Amazon GuardDuty** | Intelligent threat detection monitoring accounts, workloads, and data |
| **Amazon Inspector** | Automated vulnerability management scanning EC2, Lambda, and containers |
| **Amazon Macie** | ML-based discovery and classification of sensitive data in S3 |
| **Amazon Detective** | Analyzes and visualizes security data to investigate security issues |
| **Amazon Security Lake** | Centralizes security data from AWS, SaaS, and on-premises into OCSF data lake |
| **AWS Security Hub** | Unified security posture management aggregating findings across accounts |
| **AWS Artifact** | On-demand access to AWS compliance reports and agreements |
| **AWS Audit Manager** | Continuously audits AWS usage for risk and compliance |
| **AWS Certificate Manager (ACM)** | Provisions and auto-renews SSL/TLS certificates |
| **AWS CloudHSM** | FIPS 140-2 Level 3 validated HSMs for cryptographic key management |
| **AWS Secrets Manager** | Manages and auto-rotates secrets (DB credentials, API keys, OAuth tokens) |
| **AWS KMS** | Managed service for creating and controlling encryption keys |
| **AWS Private Certificate Authority** | Managed private CA for issuing internal certificates |
| **AWS Payment Cryptography** | HSM-backed cryptography for payment processing |
| **AWS Firewall Manager** | Centrally manage WAF, Shield, and Network Firewall rules across accounts |
| **AWS Network Firewall** | Managed stateful network firewall and IPS for VPCs |
| **AWS WAF** | Protects web apps and APIs against common exploits, bots, and OWASP Top 10 |
| **AWS Shield** | Managed DDoS protection; Standard (free/automatic) and Advanced (enhanced + 24/7 support) |
| **AWS Verified Access** | Secure, VPN-less zero-trust application access |

---

## Management & Governance

| Service | Description |
|---|---|
| **AWS CloudFormation** | Infrastructure-as-code for modeling, provisioning, and managing AWS resources |
| **AWS CDK** | Define cloud infrastructure using TypeScript, Python, Java, or C# |
| **AWS CloudTrail** | Records API calls and user activity for governance, audit, and compliance |
| **Amazon CloudWatch** | Collects metrics, logs, and events; alarms, dashboards, and Insights |
| **AWS Config** | Records resource configurations and evaluates compliance rules |
| **AWS Systems Manager** | Unified operations hub for managing and patching AWS and on-premises resources |
| **AWS Control Tower** | Sets up and governs a secure, multi-account AWS Landing Zone |
| **AWS Service Catalog** | Create and govern catalogs of approved IT products for your organization |
| **AWS Trusted Advisor** | Real-time recommendations across cost, performance, security, and fault tolerance |
| **AWS Health Dashboard** | Personalized view of AWS service health events affecting your resources |
| **AWS License Manager** | Manage software licenses (Microsoft, SAP, Oracle) across AWS and on-premises |
| **AWS Resource Explorer** | Search and discover resources across accounts and Regions |
| **AWS Well-Architected Tool** | Reviews architecture against AWS best practices |
| **AWS Infrastructure Composer** | Visual drag-and-drop IaC composer for serverless applications |
| **AWS Resilience Hub** | Assesses, validates, and tracks application resilience |
| **AWS AppConfig** | Deploy and validate application configurations with automatic rollback |

---

## Cloud Financial Management

| Service | Description |
|---|---|
| **AWS Cost Explorer** | Visualize and manage AWS costs and usage with customizable reports |
| **AWS Budgets** | Set cost/usage budgets with alerts and automated actions |
| **AWS Cost Anomaly Detection** | ML-powered detection of unexpected spending patterns |
| **AWS Cost Optimization Hub** | Personalized, actionable recommendations for reducing spend |
| **AWS Cost & Usage Report** | Granular billing data exportable to S3 |
| **AWS Billing Conductor** | Custom pricing and billing for ISVs and managed service providers |
| **AWS Savings Plans** | Commitment-based pricing for EC2, Lambda, and Fargate (up to 72% savings) |
| **AWS Pricing Calculator** | Estimate costs for planned AWS architectures |

---

## Developer Tools

| Service | Description |
|---|---|
| **Amazon Q Developer** | Generative AI for coding, testing, debugging, and security scanning |
| **Amazon CodeCatalyst** | Integrated CI/CD dev environment for planning, building, testing, and deploying |
| **AWS CodeCommit** | Fully managed, private Git source control |
| **AWS CodeBuild** | Managed build service; compiles code, runs tests, produces artifacts |
| **AWS CodeDeploy** | Automates deployments to EC2, Lambda, and on-premises servers |
| **AWS CodePipeline** | Fully managed continuous delivery for build, test, and deploy phases |
| **AWS CodeArtifact** | Managed artifact repository (npm, Maven, pip, NuGet) |
| **AWS Cloud9** | Cloud-based IDE for writing, running, and debugging code in a browser |
| **AWS CloudShell** | Browser-based shell pre-authenticated with AWS tools |
| **AWS X-Ray** | Distributed tracing and performance analysis for microservices |
| **AWS Fault Injection Service** | Managed chaos engineering for controlled resilience experiments |
| **Amazon Corretto** | No-cost production-ready OpenJDK distribution with long-term support |

---

## Application Integration

| Service | Description |
|---|---|
| **Amazon EventBridge** | Serverless event bus for event-driven applications (AWS, SaaS, custom sources) |
| **Amazon SNS** | Fully managed pub/sub messaging plus SMS, email, and push notifications |
| **Amazon SQS** | Fully managed message queuing for decoupling microservices |
| **Amazon MQ** | Managed message broker for Apache ActiveMQ and RabbitMQ |
| **AWS Step Functions** | Visual state machine orchestration for distributed applications |
| **Amazon AppFlow** | No-code integration for transferring data between SaaS apps and AWS |
| **Amazon MWAA** | Managed Apache Airflow for complex data pipeline orchestration |
| **AWS B2B Data Interchange** | Automates EDI document transformation to JSON/XML |
| **Amazon SWF** | Manages task coordination across distributed application components (legacy; prefer Step Functions) |

---

## Internet of Things

| Service | Description |
|---|---|
| **AWS IoT Core** | Managed cloud service for securely connecting devices at scale |
| **AWS IoT Greengrass** | Open-source edge runtime and cloud service for device software management |
| **AWS IoT Device Management** | Onboard, organize, monitor, and remotely manage IoT device fleets |
| **AWS IoT Device Defender** | Audits IoT configurations and monitors fleet security |
| **AWS IoT SiteWise** | Collects, stores, and monitors industrial equipment data at scale |
| **AWS IoT TwinMaker** | Creates digital twins of physical systems from real sensor data |
| **AWS IoT FleetWise** | Collects and transfers vehicle data to the cloud |
| **AWS IoT Events** | Detects and responds to events from IoT sensors using configurable logic |
| **AWS IoT Analytics** | Managed analytics for large volumes of IoT data |
| **FreeRTOS** | Real-time OS for microcontrollers connecting to AWS IoT Core |

---

## Media Services

| Service | Description |
|---|---|
| **AWS Elemental MediaLive** | Broadcast-grade live video encoding for TV and multiscreen streaming |
| **AWS Elemental MediaConvert** | File-based video transcoding for video-on-demand content |
| **AWS Elemental MediaPackage** | Video packaging and origin service with DRM support |
| **AWS Elemental MediaConnect** | High-quality IP-based live video transport |
| **AWS Elemental MediaStore** | Low-latency origin storage optimized for live video |
| **AWS Elemental MediaTailor** | Personalized ad insertion and channel assembly for streaming |
| **AWS Elemental Inference** | Auto-converts live/on-demand video into vertical mobile formats using AI (2025) |
| **Amazon IVS** | Managed low-latency live streaming for interactive video experiences |
| **Amazon Kinesis Video Streams** | Ingests and stores live video for analytics and ML (also in Analytics) |
| **Amazon Elastic Transcoder** | Video transcoding for device-compatible formats (legacy; prefer MediaConvert) |
| **Amazon Nimble Studio** | Cloud-based VFX, animation, and interactive content production |

---

## Migration & Transfer

| Service | Description |
|---|---|
| **AWS Application Migration Service (MGN)** | Lift-and-shift rehosting to AWS with minimal downtime |
| **AWS Database Migration Service (DMS)** | Migrate databases to AWS with minimal downtime; homogeneous and heterogeneous |
| **AWS DataSync** | Online data movement between on-premises and AWS (also in Storage) |
| **AWS Snow Family** | Offline bulk data transfer devices (also in Compute) |
| **AWS Transfer Family** | Managed SFTP/FTPS/FTP/AS2 into S3 or EFS (also in Storage) |
| **AWS Mainframe Modernization** | Platform to modernize, migrate, and run mainframe applications on AWS |
| **AWS Transform** | Agentic AI for modernizing legacy systems and eliminating technical debt |
| **AWS Schema Conversion Tool (SCT)** | Converts database schemas for engine-to-engine migrations |

---

## Business Applications

| Service | Description |
|---|---|
| **Amazon Connect** | Omnichannel cloud contact center with AI-powered customer experiences |
| **Amazon SES** | High-scale email sending/receiving for transactional and marketing email |
| **Amazon Pinpoint** | Targeted messaging via email, SMS, push notifications, and voice |
| **Amazon Chime SDK** | Embed real-time voice, video, and messaging in custom applications |
| **Amazon WorkMail** | Managed business email and calendar |
| **Amazon WorkDocs** | Enterprise document storage and collaboration |
| **AWS AppFabric** | Aggregates and normalizes security data across SaaS applications |
| **AWS Supply Chain** | AI-powered supply chain visibility, planning, and risk mitigation |
| **AWS Wickr** | End-to-end encrypted messaging, voice, and video |

---

## End User Computing

| Service | Description |
|---|---|
| **Amazon WorkSpaces** | Managed cloud desktop (Windows or Linux virtual desktops) |
| **Amazon WorkSpaces Core** | Cloud-based managed VDI for third-party VDI management solutions |
| **Amazon WorkSpaces Applications** | Managed application streaming to any browser |
| **Amazon WorkSpaces Web** | Low-cost managed workspace for secure browser-based access |
| **Amazon WorkSpaces Thin Client** | Cost-effective thin client device for cloud desktops |

---

## Front-End Web & Mobile

| Service | Description |
|---|---|
| **AWS Amplify** | Full-stack platform for building, deploying, and hosting web and mobile apps |
| **AWS AppSync** | Managed GraphQL API connecting apps to events, data sources, and AI models |
| **Amazon Location Service** | Maps, geocoding, routing, geofencing, and tracking for applications |
| **AWS Device Farm** | Test web and mobile apps on real browsers and physical mobile devices |
| **AWS App Runner** | Managed containerized web app deployment with auto scaling (also in Containers) |

---

## Game Technology

| Service | Description |
|---|---|
| **Amazon GameLift Servers** | Managed game server hosting for multiplayer workloads |
| **Amazon GameLift Streams** | Low-latency cloud game streaming service |

---

## Blockchain

| Service | Description |
|---|---|
| **Amazon Managed Blockchain** | Managed blockchain networks using Hyperledger Fabric or Ethereum |

---

## Quantum Technologies

| Service | Description |
|---|---|
| **Amazon Braket** | Managed quantum computing service for exploring and building quantum algorithms |
| **AWS Center for Quantum Networking** | Research initiative for quantum networking hardware, software, and applications |
| **AWS Center for Quantum Computing** | Research facility advancing quantum computing hardware and error correction |

---

## Satellite

| Service | Description |
|---|---|
| **AWS Ground Station** | Managed satellite ground station service; control satellites and ingest downlinked data |

---

## Robotics

| Service | Description |
|---|---|
| **AWS RoboMaker** | Cloud robotics simulation, development, and deployment service |

---

## Quick Service Disambiguation

Common decision points when multiple services could apply:

| Use Case | Recommended Service | Why |
|---|---|---|
| Simple queue between services | **SQS** | Easiest; pull-based, auto-scaling |
| Fan-out to multiple consumers | **SNS** | Pub/sub; combine with SQS for durability |
| Event-driven, filter/route events | **EventBridge** | Schema registry, SaaS sources, rich routing rules |
| Complex workflow orchestration | **Step Functions** | Visual state machines, error handling, parallel execution |
| Real-time data streaming | **Kinesis Data Streams** | Order guarantees, replay, millisecond latency |
| Streaming to storage/analytics | **Data Firehose** | Managed delivery; no consumer code needed |
| Apache Kafka workloads | **MSK** | Fully managed Kafka; bring existing Kafka apps |
| Transactional relational DB | **Aurora** | Best price/performance for MySQL/Postgres |
| High-scale key-value at ms latency | **DynamoDB** | Serverless, unlimited scale |
| Read-heavy with microsecond latency | **ElastiCache** | In-memory cache layer in front of DynamoDB/RDS |
| Full-text search | **OpenSearch Service** | Elasticsearch-compatible, managed |
| Analytical queries on S3 | **Athena** | Serverless SQL; no infrastructure |
| Large-scale data warehouse | **Redshift** | Columnar, petabyte-scale |
| Generative AI / LLM inference | **Bedrock** | Managed FM access; Claude, Llama, Nova |
| Custom ML model training | **SageMaker** | Full MLOps platform |
| Container workloads | **ECS + Fargate** | Simpler; AWS-native |
| Kubernetes workloads | **EKS** | Standard K8s API; more control |
| Secrets storage | **Secrets Manager** | Auto-rotation, audit trail |
| Encryption keys | **KMS** | Managed key lifecycle, HSM-backed |
| Static website / SPA | **S3 + CloudFront** | Cheapest; global CDN |
| REST/HTTP API | **API Gateway** | Throttling, auth, caching built-in |
| GraphQL API | **AppSync** | Managed GraphQL with real-time subscriptions |
