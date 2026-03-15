# GCP Services Catalog

Complete reference of Google Cloud Platform services organized by category (current as of early 2026, ~250+ distinct services).

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
10. [Developer Tools](#developer-tools)
11. [Application Integration / Serverless](#application-integration--serverless)
12. [Internet of Things](#internet-of-things)
13. [Media Services](#media-services)
14. [Migration & Transfer](#migration--transfer)
15. [Business Applications](#business-applications)
16. [End-User Computing](#end-user-computing)
17. [Front-End Web & Mobile](#front-end-web--mobile)
18. [Healthcare & Life Sciences](#healthcare--life-sciences)
19. [Game Technology](#game-technology)

---

## Compute

| Service | Description |
|---|---|
| **Compute Engine (GCE)** | Resizable virtual machines on Google infrastructure; full control over OS, networking, and machine type |
| **Compute Engine Managed Instance Groups (MIGs)** | Automatically manages groups of identical VMs with auto-scaling, auto-healing, and rolling updates |
| **Spot VMs** | Fault-tolerant workloads on surplus Compute Engine capacity at up to 91% discount; can be preempted with 30s notice |
| **Preemptible VMs** | Legacy predecessor to Spot VMs; fixed 24-hour max lifetime and lower discount than Spot |
| **VM Manager** | Suite of OS management tools: OS patch management, OS Config, OS inventory across GCE fleet |
| **Cloud Run** | Fully managed serverless platform for stateless containers; auto-scales to zero; pay-per-request |
| **Cloud Run Jobs** | Run containerized batch jobs to completion; no HTTP serving required; parallel job execution supported |
| **Cloud Functions (1st gen)** | Event-driven serverless functions with per-function scaling; supports Node.js, Python, Go, Java, Ruby, .NET |
| **Cloud Functions (2nd gen)** | Next-generation Cloud Functions built on Cloud Run; longer timeouts, larger instances, concurrency support |
| **App Engine Standard** | Platform-as-a-service for web apps in sandboxed runtimes; scales to zero; per-request billing |
| **App Engine Flexible** | PaaS on GCE VMs; custom runtimes via Docker; always-on minimum instances; suited for long-running requests |
| **Google Kubernetes Engine (GKE)** | Fully managed Kubernetes service with integrated CI/CD, security, and observability |
| **GKE Autopilot** | Fully managed GKE mode where Google manages node provisioning, scaling, and security; pay per Pod resource |
| **Cloud Batch** | Fully managed batch computing service; provisions infrastructure and schedules job queues automatically |
| **Bare Metal Solution** | Dedicated physical servers in Google data centers for specialized workloads (Oracle, SAP, HPC) |
| **Google Cloud VMware Engine (GCVE)** | Migrate and run VMware vSphere workloads natively on Google Cloud dedicated infrastructure |
| **Migrate to Virtual Machines** | Lift-and-shift migration of VMs from on-premises, AWS, or Azure to Compute Engine |
| **Sole-Tenant Nodes** | Dedicated physical servers for your GCE VMs; useful for compliance, licensing, and performance isolation |
| **Cloud GPUs** | NVIDIA GPU accelerators (T4, V100, A100, H100) attached to GCE or GKE for ML training and HPC |

---

## Containers

| Service | Description |
|---|---|
| **Google Kubernetes Engine (GKE)** | Fully managed Kubernetes with auto-upgrades, auto-repair, and deep GCP integrations |
| **GKE Autopilot** | Serverless GKE mode; Google manages nodes; pay per Pod CPU/memory; security hardened by default |
| **Cloud Run** | Serverless containers with HTTP/gRPC serving; scales from zero to thousands of instances automatically |
| **Cloud Run Jobs** | Container-based batch and scheduled job execution without HTTP serving overhead |
| **Artifact Registry** | Universal artifact repository for container images, Helm charts, Maven, npm, Python packages, and more |
| **Cloud Build** | Managed CI/CD build service; runs builds in containers; integrates with GitHub, Bitbucket, Cloud Source Repos |
| **Cloud Deploy** | Managed continuous delivery pipeline to GKE, Cloud Run, and Anthos targets with approval gates |
| **Knative (open source)** | Open-source Kubernetes-based platform for building serverless and event-driven applications; basis for Cloud Run |
| **GKE Enterprise (formerly Anthos)** | Multi-cloud and hybrid Kubernetes management platform for GKE, on-prem, AWS, and Azure clusters |
| **Config Sync** | GitOps-based configuration management for GKE clusters; keeps cluster state in sync with a Git repository |
| **Policy Controller** | Kubernetes admission controller enforcing custom policies across GKE clusters; based on Open Policy Agent |

---

## Storage

| Service | Description |
|---|---|
| **Cloud Storage (Standard)** | Frequently accessed object storage; highest availability; no retrieval fees |
| **Cloud Storage (Nearline)** | Low-cost object storage for data accessed less than once per month; 30-day minimum storage |
| **Cloud Storage (Coldline)** | Very low-cost object storage for data accessed less than once per quarter; 90-day minimum storage |
| **Cloud Storage (Archive)** | Lowest-cost object storage for data accessed less than once per year; 365-day minimum storage |
| **Cloud Storage FUSE** | Open-source FUSE adapter allowing Cloud Storage buckets to be mounted as local filesystems on Linux/macOS |
| **Persistent Disk (pd-standard)** | Standard HDD-backed block storage for GCE; good price/performance for sequential I/O |
| **Persistent Disk (pd-balanced)** | SSD-backed block storage balancing performance and cost; default for most GCE workloads |
| **Persistent Disk (pd-ssd)** | High-performance SSD block storage for latency-sensitive applications |
| **Persistent Disk (pd-extreme)** | Highest-performance SSD block storage; configurable IOPS; for most demanding databases |
| **Hyperdisk** | Next-generation block storage with independently scalable throughput and IOPS; Hyperdisk Balanced, Extreme, Throughput tiers |
| **Cloud Filestore** | Managed NFS file storage for GCE and GKE; Basic, Enterprise, and High Scale tiers |
| **NetApp Cloud Volumes** | Enterprise-grade managed NFS/SMB file storage (formerly NetApp Cloud Volumes Service); ONTAP feature set |
| **Storage Transfer Service** | Managed data transfer from AWS S3, Azure Blob, HTTP/HTTPS URLs, or on-premises sources to Cloud Storage |
| **Transfer Appliance** | Physical data transfer appliance for migrating large datasets (hundreds of terabytes to petabytes) to GCP |
| **Backup and DR Service** | Centralized, application-consistent backup and disaster recovery for GCE, databases, VMware, and SAP |

---

## Database

| Service | Description |
|---|---|
| **Cloud SQL (MySQL)** | Fully managed MySQL with automated backups, replication, patching, and high availability |
| **Cloud SQL (PostgreSQL)** | Fully managed PostgreSQL with automated backups, read replicas, and HA via regional failover |
| **Cloud SQL (SQL Server)** | Fully managed Microsoft SQL Server with Windows Authentication and Always On availability groups |
| **AlloyDB for PostgreSQL** | PostgreSQL-compatible managed database with 4x faster transactional performance and 100x faster analytical queries than standard PostgreSQL |
| **Cloud Spanner** | Globally distributed, horizontally scalable relational database with ACID transactions and SQL support; unique 99.999% SLA |
| **Firestore** | Serverless, NoSQL document database with real-time listeners, offline support, and Firebase integration |
| **Datastore** | Legacy managed NoSQL document database; Firestore in Datastore mode; recommended to migrate to Firestore native mode |
| **Bigtable** | Fully managed, petabyte-scale, low-latency NoSQL wide-column database; HBase-compatible; ideal for time-series and IoT |
| **Memorystore for Redis** | Fully managed Redis in-memory data store; Standard tier with replication and failover |
| **Memorystore for Memcached** | Fully managed Memcached for distributed caching of application data |
| **Database Migration Service** | Serverless migration service for PostgreSQL, MySQL, Oracle, and SQL Server to Cloud SQL or AlloyDB |
| **Vertex AI Feature Store** | Managed repository for storing, sharing, and serving ML features; low-latency online serving and batch retrieval |

---

## Networking & Content Delivery

| Service | Description |
|---|---|
| **Virtual Private Cloud (VPC)** | Global, software-defined network providing logically isolated environments for GCP resources |
| **Cloud Load Balancing — Global HTTP(S)** | Global, anycast Layer 7 load balancer with SSL termination, URL mapping, and CDN integration |
| **Cloud Load Balancing — Regional HTTP(S)** | Regional Layer 7 load balancer for workloads requiring regional isolation |
| **Cloud Load Balancing — Network (TCP/UDP)** | Regional Layer 4 pass-through load balancer preserving client IPs; no proxy overhead |
| **Cloud Load Balancing — Internal** | Internal Layer 4 and Layer 7 load balancers for private traffic within a VPC |
| **Cloud CDN** | Content delivery network integrated with Cloud Load Balancing; cache static content at Google's global edge |
| **Media CDN** | High-throughput CDN optimized for media streaming and large file delivery at global scale |
| **Cloud DNS** | Highly available, scalable, managed authoritative DNS service; 100% uptime SLA |
| **Cloud NAT** | Managed network address translation for outbound internet access from VMs without external IPs |
| **Cloud Armor** | DDoS protection and Web Application Firewall (WAF) integrated with Cloud Load Balancing; OWASP Top 10 rules |
| **Cloud Interconnect (Dedicated)** | Direct 10/100 Gbps physical connections between on-premises networks and Google's network |
| **Cloud Interconnect (Partner)** | Connectivity through a supported service provider when Dedicated Interconnect colocation isn't available |
| **Cloud VPN** | IPsec VPN tunnels connecting on-premises or other-cloud networks to GCP VPCs |
| **Network Intelligence Center** | Centralized network observability: Connectivity Tests, Network Topology, Firewall Insights, Performance Dashboard |
| **Traffic Director** | Google Cloud's service mesh control plane for managing traffic between microservices (xDS-based) |
| **Service Directory** | Managed service registry for publishing, discovering, and connecting services across environments |
| **Private Service Connect** | Privately expose services across VPC networks using Google's network without VPC peering |
| **Cloud Domains** | Domain registration service integrated with Cloud DNS for managing domain names |
| **Network Connectivity Center** | Hub-and-spoke model for connecting on-premises, multi-cloud, and Google Cloud networks centrally |

---

## Analytics

| Service | Description |
|---|---|
| **BigQuery** | Fully managed, serverless, petabyte-scale data warehouse; columnar storage; SQL queries billed per TB scanned |
| **BigQuery ML** | Run machine learning models using standard SQL directly in BigQuery; no data movement required |
| **BigQuery BI Engine** | In-memory analysis service accelerating BigQuery and Looker Studio dashboards to sub-second latency |
| **Dataflow** | Fully managed Apache Beam service for unified stream and batch data processing pipelines |
| **Dataproc** | Managed Spark, Hadoop, Hive, Flink, and Presto clusters; fast provisioning with per-second billing |
| **Pub/Sub** | Fully managed, real-time messaging service for event ingestion and delivery at any scale |
| **Pub/Sub Lite** | Low-cost, zonal Pub/Sub alternative for high-volume, latency-tolerant streaming workloads |
| **Looker** | Enterprise BI and data analytics platform with LookML semantic layer; acquired by Google in 2020 |
| **Looker Studio** | Free, self-service data visualization and dashboarding tool (formerly Google Data Studio) |
| **Cloud Composer** | Fully managed Apache Airflow service for authoring, scheduling, and monitoring data pipelines |
| **Cloud Data Fusion** | Managed, code-free ETL/ELT data integration platform built on open-source CDAP |
| **Dataplex** | Intelligent data fabric for managing, monitoring, and governing distributed data across data lakes and warehouses |
| **Analytics Hub** | Exchange and share analytics assets (BigQuery datasets, Looker blocks) across organizations |
| **Datastream** | Serverless change data capture (CDC) and replication service for MySQL, PostgreSQL, Oracle, and SQL Server |
| **Dataprep (by Trifacta)** | Intelligent cloud data preparation service for exploring, cleaning, and transforming raw data visually |
| **Recommender** | ML-based recommendations and insights for optimizing GCP resources, security, and costs |

---

## Machine Learning & AI

| Service | Description |
|---|---|
| **Vertex AI Platform** | Unified ML platform for building, deploying, and scaling ML models and AI applications |
| **Vertex AI Workbench** | Managed JupyterLab notebooks integrated with GCP services for data science and ML development |
| **Vertex AI Pipelines** | Managed ML pipeline orchestration based on Kubeflow Pipelines and TFX |
| **Vertex AI Model Registry** | Central repository for managing and versioning trained ML models across the lifecycle |
| **Vertex AI Endpoints** | Low-latency, scalable model serving infrastructure for online prediction |
| **Vertex AI Search** | Managed enterprise search and recommendations built on Google's search technology |
| **Vertex AI Vision** | Managed computer vision platform for building, deploying, and managing vision models |
| **AutoML Tables** | Automatically builds and deploys state-of-the-art ML models on structured tabular data |
| **AutoML Vision** | Trains custom image classification and object detection models with minimal ML expertise |
| **AutoML Natural Language** | Trains custom text classification, entity extraction, and sentiment analysis models |
| **AutoML Video** | Trains custom video classification and object tracking models |
| **Gemini API (via Vertex AI)** | Access to Google's Gemini family of multimodal foundation models for text, vision, code, and reasoning |
| **Document AI** | Managed document processing service for extracting structured data from unstructured documents |
| **Vision AI (Cloud Vision API)** | Pre-trained models for image labeling, face detection, OCR, explicit content detection, and landmark detection |
| **Natural Language AI** | Pre-trained NLP for entity recognition, sentiment analysis, content classification, and syntax analysis |
| **Translation AI** | Neural machine translation supporting 100+ languages with glossary support and AutoML customization |
| **Speech-to-Text** | Converts audio to text using Google's ML models; supports 125+ languages with speaker diarization |
| **Text-to-Speech** | Converts text to natural-sounding speech using WaveNet and neural voices across 30+ languages |
| **Dialogflow CX** | Advanced conversational AI platform for building enterprise-grade chatbots and virtual agents |
| **Dialogflow ES** | Lightweight conversational AI for simpler virtual agents and chatbot prototyping |
| **Contact Center AI (CCAI)** | AI-powered virtual agents, agent assist, and conversation analytics for contact centers |
| **Recommendations AI** | Delivers personalized product recommendations for e-commerce and media applications |
| **Video Intelligence API** | Annotates videos with labels, objects, text, faces, shot changes, and explicit content |
| **AI Infrastructure (TPUs)** | Tensor Processing Units (TPU v4, v5e, v5p) purpose-built for large-scale ML training and inference |
| **NotebookLM** | AI-powered research and note-taking tool using Gemini; source-grounded Q&A and summarization |

---

## Security, Identity & Compliance

| Service | Description |
|---|---|
| **Cloud IAM** | Fine-grained access control for all GCP resources; roles, policies, service accounts, and conditions |
| **Cloud Identity** | Identity-as-a-service for managing users, groups, and devices; SAML/OIDC federation |
| **Identity Platform** | Customer identity management (CIAM) with sign-in, MFA, and federation for apps; Firebase Auth upgrade path |
| **BeyondCorp Enterprise** | Zero-trust access solution providing context-aware access to applications without a VPN |
| **Cloud KMS** | Managed service for creating, using, and auditing cryptographic keys; supports CMEK for GCP services |
| **Cloud HSM** | FIPS 140-2 Level 3 validated hardware security modules via Cloud KMS for highest-assurance key management |
| **Secret Manager** | Manages and versions API keys, passwords, certificates, and other sensitive data with access auditing |
| **Security Command Center** | Centralized security posture management; asset inventory, vulnerability detection, threat detection |
| **Chronicle SIEM** | Cloud-native SIEM platform built on Google's infrastructure for security telemetry at petabyte scale |
| **VPC Service Controls** | Creates security perimeters around GCP API services to prevent data exfiltration |
| **Certificate Authority Service** | Managed private CA for issuing, managing, and rotating internal TLS certificates at scale |
| **Binary Authorization** | Deploy-time security control for containers; enforces trusted image policies in GKE and Cloud Run |
| **Artifact Analysis** | Container vulnerability scanning and software bill of materials (SBOM) for images in Artifact Registry |
| **Cloud DLP (Data Loss Prevention)** | Discovers, classifies, and protects sensitive data (PII, PCI, PHI) across GCP and beyond |
| **Access Transparency** | Near-real-time logs of actions taken by Google personnel on your content for accountability |
| **Assured Workloads** | Compliance controls for regulated workloads (FedRAMP, ITAR, HIPAA, PCI DSS) with data residency enforcement |
| **Confidential Computing** | Encrypts data in use with Confidential VMs, Confidential GKE Nodes, and Confidential Dataflow |
| **reCAPTCHA Enterprise** | Fraud and bot detection for websites and mobile apps using adaptive risk scoring |
| **Managed Service for Microsoft Active Directory** | Highly available, hardened Microsoft Active Directory managed by Google |

---

## Management & Governance

| Service | Description |
|---|---|
| **Cloud Monitoring** | Managed metrics collection, dashboards, alerting, and uptime checks for GCP and hybrid environments |
| **Cloud Logging** | Centralized log aggregation, search, and export; Log Router, Log-based Metrics, and Log Analytics |
| **Cloud Trace** | Distributed tracing system for measuring latency across services in production applications |
| **Cloud Profiler** | Continuous production profiling of CPU and memory for applications running on GCP |
| **Error Reporting** | Aggregates and surfaces application errors from Cloud Logging with deduplication and alerting |
| **Cloud Deployment Manager** | GCP-native declarative IaC using YAML/Jinja2/Python templates (largely superseded by Terraform) |
| **Cloud Build** | Managed CI build service triggered by source changes; runs in Docker containers; integrates with Artifact Registry |
| **Cloud Deploy** | Managed continuous delivery to GKE, GKE Enterprise, Cloud Run, and Cloud Functions with promotion gates |
| **Cloud Scheduler** | Fully managed, enterprise-grade cron job scheduler for calling HTTP/S endpoints or Pub/Sub topics |
| **Cloud Tasks** | Managed asynchronous task execution and queueing with rate limiting and retry controls |
| **Terraform (Google Provider)** | Industry-standard IaC tool with mature `google` and `google-beta` providers for all GCP resources |
| **Config Connector** | Kubernetes add-on that allows management of GCP resources using Kubernetes manifests via GCP APIs |
| **Anthos Config Management** | Policy and configuration management across GKE and GKE Enterprise clusters via GitOps |
| **Cloud Audit Logs** | Immutable audit trail of admin activity and data access across all GCP services |
| **Resource Manager** | Hierarchical organization of GCP resources into organizations, folders, and projects |
| **Organization Policy Service** | Centrally set constraints on how GCP resources can be configured across the entire organization |
| **Cloud Asset Inventory** | Real-time inventory of all GCP assets with change history and search capabilities |
| **Cloud Console** | Web-based management UI for all GCP services with integrated Cloud Shell |
| **Cloud Shell** | Browser-based shell with gcloud CLI, Terraform, kubectl, and other tools pre-installed; 5 GB persistent disk |

---

## Developer Tools

| Service | Description |
|---|---|
| **Cloud SDK (gcloud CLI)** | Command-line interface for interacting with GCP services; includes gcloud, gsutil, bq, and kubectl |
| **Cloud Shell** | Browser-based shell pre-authenticated with GCP credentials; ephemeral VM with persistent home directory |
| **Cloud Source Repositories** | Fully managed private Git repositories hosted on GCP with integration to Cloud Build |
| **Artifact Registry** | Universal managed repository for container images, language packages (Maven, npm, pip), and Helm charts |
| **Cloud Workstations** | Managed cloud development environments running in GCP; consistent, secure, and accessible from any browser |
| **Cloud Code** | IDE plugin for VS Code and IntelliJ; GCP-integrated development for Kubernetes, Cloud Run, and more |
| **Firebase Studio** | Web-based AI-powered development environment (formerly Project IDX); full-stack app development on GCP |
| **Gemini Code Assist** | AI-powered coding assistant (formerly Duet AI for Developers); code completion, generation, and chat in IDE |
| **Cloud Endpoints** | Manages, secures, and monitors APIs deployed on App Engine, GKE, or GCE using OpenAPI or gRPC |
| **API Gateway** | Fully managed API gateway for Cloud Functions, Cloud Run, and App Engine backends |
| **Apigee API Management** | Enterprise-grade full lifecycle API management platform for designing, securing, and analyzing APIs |
| **Crashlytics** | Firebase crash reporting SDK for mobile apps; real-time crash reporting and analytics |

---

## Application Integration / Serverless

| Service | Description |
|---|---|
| **Cloud Functions** | Event-driven serverless functions; triggers from Pub/Sub, Cloud Storage, Firestore, HTTP, and Eventarc |
| **Cloud Run** | Managed serverless containers serving HTTP requests; scales to zero; supports WebSockets and gRPC |
| **Cloud Run Jobs** | Container-based batch job execution to completion; supports parallelism with indexed tasks |
| **Eventarc** | Managed event routing service delivering events from GCP services, custom sources, and third-party apps using CloudEvents |
| **Workflows** | Serverless workflow orchestration for connecting GCP services and APIs into reliable, stateful pipelines |
| **Pub/Sub** | Managed real-time messaging for decoupling services; guaranteed at-least-once delivery; push and pull subscriptions |
| **Cloud Tasks** | Managed task queue for asynchronous, reliable execution of work with rate limiting and retry |
| **Cloud Scheduler** | Enterprise cron service for scheduling Pub/Sub messages, HTTP calls, and App Engine jobs |
| **Apigee API Management** | Full lifecycle API platform; developer portal, analytics, monetization, and policy enforcement |
| **Integration Connectors** | Pre-built connectors for SaaS and enterprise systems (Salesforce, SAP, ServiceNow) for Application Integration |
| **Application Integration** | Managed integration platform (iPaaS) for connecting applications and data across hybrid environments |

---

## Internet of Things

| Service | Description |
|---|---|
| **Cloud IoT Core (deprecated 2023)** | Former managed IoT device connection and management service; deprecated August 2023; migrate to Pub/Sub |
| **Pub/Sub (IoT ingestion)** | Recommended replacement for IoT Core; ingest telemetry from millions of devices at scale |
| **Edge TPU (Coral)** | Purpose-built ASIC for running TensorFlow Lite ML inference at the edge on Coral hardware |
| **IoT Pattern (Pub/Sub + Cloud Functions)** | Reference architecture: devices → MQTT bridge or HTTP → Pub/Sub → Cloud Functions → Firestore/BigQuery |

---

## Media Services

| Service | Description |
|---|---|
| **Transcoder API** | Managed video transcoding service for converting media files into formats optimized for web and mobile delivery |
| **Video Intelligence API** | Annotates video content with labels, shot changes, objects, text, faces, and explicit content detection |
| **Live Stream API** | Managed live video streaming pipeline for encoding and packaging live content for delivery |
| **Video Stitcher API** | Server-side ad insertion for live and video-on-demand streams; dynamic ad stitching at scale |
| **Streaming API** | Low-latency video streaming API for embedding live streams into web and mobile applications |

---

## Migration & Transfer

| Service | Description |
|---|---|
| **Migrate to Virtual Machines** | Lift-and-shift migration of physical servers, VMware VMs, and cloud VMs to Compute Engine (formerly Velostrata) |
| **Migrate to Containers** | Modernize existing VMs into GKE containers automatically by analyzing and transforming workloads |
| **Database Migration Service** | Serverless, minimal-downtime database migration for PostgreSQL, MySQL, Oracle, and SQL Server to Cloud SQL or AlloyDB |
| **Storage Transfer Service** | Managed online data transfer from AWS S3, Azure Blob, HTTP sources, or POSIX file systems to Cloud Storage |
| **Transfer Appliance** | Physical hardware appliance shipped to customer for offline bulk data transfer (petabyte scale) to GCP |
| **BigQuery Data Transfer Service** | Automated data movement from SaaS applications (Google Ads, YouTube, Salesforce) and other clouds to BigQuery |
| **Datastream** | Serverless change data capture and replication for streaming database changes to BigQuery and Cloud Storage |

---

## Business Applications

| Service | Description |
|---|---|
| **Google Workspace** | Integrated suite of collaboration and productivity tools (Gmail, Drive, Docs, Meet, Calendar, Sheets) |
| **AppSheet** | No-code/low-code application builder for creating apps directly from Google Sheets, Drive, and databases |
| **Google Workspace APIs** | Programmatic access to Gmail, Calendar, Drive, Sheets, Docs, and Admin SDK for automation and integration |
| **Contact Center AI (CCAI)** | Modernizes contact centers with virtual agents, agent assist real-time guidance, and conversation analytics |
| **Google Meet Real-Time AI** | AI-powered features in Google Meet: transcription, translation, noise cancellation, and summarization |
| **Looker (BI platform)** | Enterprise analytics and embedded analytics platform with governed metrics layer (LookML) |
| **AppSheet Automation** | Workflow automation layer within AppSheet for triggering actions based on data changes and conditions |

---

## End-User Computing

| Service | Description |
|---|---|
| **Chrome Enterprise Upgrade** | Managed Chrome OS devices with centralized fleet management, policy enforcement, and security controls |
| **Chrome Browser Cloud Management** | Cloud-based management for Chrome Browser on Windows, macOS, and Linux |
| **Cloud Workstations** | Fully managed cloud development environments accessible from any browser; built on GKE and Persistent Disk |
| **Virtual Desktops via third-party** | VDI solutions (Citrix Virtual Apps and Desktops on GCP, VMware Horizon on GCVE) for legacy desktop workloads |

---

## Front-End Web & Mobile

| Service | Description |
|---|---|
| **Firebase Authentication** | Managed authentication with email/password, OAuth providers, phone auth, and anonymous sign-in |
| **Firebase Realtime Database** | Cloud-hosted JSON NoSQL database that syncs data in real time across all connected clients |
| **Firebase Firestore** | Flexible, scalable NoSQL cloud database (same as Cloud Firestore; Firebase-branded access) |
| **Firebase Hosting** | Fast and secure web hosting for web apps; global CDN delivery with one-command deploys |
| **Firebase Storage** | Cloud Storage for Firebase; backed by Google Cloud Storage; direct client upload/download with security rules |
| **Firebase Cloud Functions** | Cloud Functions triggered by Firebase events (auth, Firestore changes, Storage uploads, Analytics) |
| **Firebase Remote Config** | Change app behavior and appearance without an update; A/B testing and feature flags |
| **Firebase Analytics** | Free app analytics for iOS and Android powered by Google Analytics |
| **Google Maps Platform** | Maps, Places, Routes, and Street View APIs for embedding maps and location intelligence in applications |
| **Identity Platform** | CIAM with support for SAML, OIDC, email/password, and social logins; upgrade path from Firebase Auth |
| **Firebase App Distribution** | Pre-release mobile app distribution to testers with feedback collection and version management |
| **Firebase Test Lab** | Cloud-based app testing infrastructure running tests on real and virtual Android and iOS devices |

---

## Healthcare & Life Sciences

| Service | Description |
|---|---|
| **Cloud Healthcare API** | Managed HL7v2, FHIR R4, and DICOM store with de-identification, consent management, and streaming to BigQuery |
| **FHIR Store** | FHIR R4-compliant managed data store for healthcare interoperability and patient data exchange |
| **DICOM Store** | Managed DICOM-compliant medical imaging store with web viewer and de-identification tools |
| **HL7v2 Store** | Managed HL7v2 message store for ADT, ORM, ORU, and other clinical messaging workflows |
| **Vertex AI for Healthcare** | Pre-trained and customizable AI models for medical imaging, clinical NLP, and clinical decision support |
| **Healthcare Natural Language API** | Extracts medical entities, relationships, and normalized codes (ICD-10, RxNorm, SNOMED CT) from clinical text |
| **Life Sciences API** | Managed genomics pipeline execution service (formerly Google Genomics API) for running bioinformatics workflows |
| **HCLS Data Harmonization** | Reference architecture and tooling for harmonizing disparate healthcare data into FHIR-compliant format |
| **Clinical NLP** | AutoML and Vertex AI-based NLP models trained on clinical text for custom medical entity recognition |

---

## Game Technology

| Service | Description |
|---|---|
| **Agones** | Open-source game server hosting framework on GKE; manages dedicated game server lifecycle and scaling |
| **Cloud Spanner (for games)** | Globally distributed relational database used by major game studios for player inventory, leaderboards, and matchmaking |
| **Pub/Sub (game events)** | Real-time event streaming for in-game telemetry, analytics pipelines, and player activity tracking |
| **Firebase (game backend)** | Authentication, Realtime Database, Firestore, and Cloud Functions providing a managed mobile/web game backend |
| **Open Match** | Open-source matchmaking framework designed to run on GKE; scalable, customizable game matchmaking |
| **Vertex AI (game AI)** | ML models for player churn prediction, personalized recommendations, fraud detection, and NPC behavior |

---

## Quick Service Disambiguation

Common decision points when multiple services could apply:

| Use Case | Recommended Service | Why |
|---|---|---|
| Simple async message queue | **Pub/Sub** | Managed, global, at-least-once; easiest for decoupling services |
| Scheduled task execution | **Cloud Scheduler** | Cron-as-a-service; calls HTTP or Pub/Sub |
| Async work queue with rate limiting | **Cloud Tasks** | Pull queues, deduplication, retry with backoff |
| Complex workflow orchestration | **Workflows** | Stateful, serverless; step retry and error handling |
| Event routing across services | **Eventarc** | CloudEvents standard; GCP source events and custom sources |
| Transactional relational DB | **Cloud SQL** (MySQL/PG) or **AlloyDB** | Cloud SQL for standard workloads; AlloyDB for high performance |
| Globally distributed relational DB | **Cloud Spanner** | Unique globally consistent ACID transactions at scale |
| Serverless document database | **Firestore** | Real-time sync, offline support, Firebase integration |
| Wide-column / time-series NoSQL | **Bigtable** | HBase-compatible; petabyte-scale; sub-10ms latency |
| Analytics at petabyte scale | **BigQuery** | Serverless SQL data warehouse; pay per query |
| Stream processing | **Dataflow** | Apache Beam managed; unified batch and streaming |
| Batch Spark/Hadoop jobs | **Dataproc** | Managed clusters; per-second billing; fast start |
| Stateless container workload | **Cloud Run** | Serverless containers; scales to zero; cheapest for variable load |
| Kubernetes workload | **GKE** or **GKE Autopilot** | Autopilot for simplicity; Standard for control |
| Generative AI / LLM inference | **Vertex AI + Gemini API** | Managed Gemini access; RAG, fine-tuning, agent tooling |
| Custom ML training | **Vertex AI Training** | Managed training jobs; GPU/TPU support; MLOps pipelines |
| Secrets storage | **Secret Manager** | Versioned secrets with IAM access and audit logging |
| Encryption key management | **Cloud KMS** | CMEK for GCP services; HSM tier available |
| Static website / SPA | **Firebase Hosting + Cloud Storage** | Global CDN; one-command deploy |
| External API management | **Apigee** | Enterprise API gateway; policies, analytics, developer portal |
| Internal API proxy | **Cloud Endpoints** or **API Gateway** | Lighter weight; Cloud Run or GCF backends |
