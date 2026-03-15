# Data Protection — Capabilities

## Cloud DLP (Sensitive Data Protection)

### Purpose
Cloud Data Loss Prevention (DLP), now marketed as **Sensitive Data Protection**, is a managed service for discovering, classifying, and de-identifying sensitive data across GCP storage systems and application streams. It provides over 150 built-in detectors for common sensitive data types and supports custom detectors.

### Built-in InfoType Detectors (partial list)

| Category | Examples |
|---|---|
| PII | `PERSON_NAME`, `EMAIL_ADDRESS`, `PHONE_NUMBER`, `DATE_OF_BIRTH`, `AGE` |
| Government ID | `US_SOCIAL_SECURITY_NUMBER`, `US_PASSPORT`, `US_DRIVERS_LICENSE_NUMBER`, `UK_NATIONAL_INSURANCE_NUMBER` |
| Financial | `CREDIT_CARD_NUMBER`, `IBAN_CODE`, `SWIFT_CODE`, `US_BANK_ROUTING_MICR` |
| Healthcare (PHI) | `US_HEALTHCARE_NPI`, `US_DEA_NUMBER`, `MEDICAL_TERM` |
| Network | `IP_ADDRESS`, `MAC_ADDRESS`, `URL` |
| Auth credentials | `AUTH_TOKEN`, `AWS_CREDENTIALS`, `AZURE_AUTH_TOKEN`, `GCP_CREDENTIALS`, `ENCRYPTION_KEY` |
| Geo | `LOCATION`, `STREET_ADDRESS`, `COUNTRY` |

### Custom InfoTypes
Define your own detectors for domain-specific sensitive data:
- **Dictionary**: match exact strings from a provided list (e.g., internal employee IDs)
- **Regex**: pattern matching with optional context words and proximity rules
- **Surrogate**: detect data that was previously tokenized or pseudonymized by DLP
- **Stored InfoType**: large custom dictionaries stored in Cloud Storage or BigQuery (up to hundreds of millions of terms)

### Inspection
DLP can inspect content for sensitive data:
- **Inline (API)**: send content directly in the API request; synchronous; up to 500 KiB
- **Cloud Storage**: scan files in GCS buckets (CSV, text, images with OCR, Avro, Parquet, JSON, etc.)
- **BigQuery**: scan rows in a dataset/table
- **Datastore**: scan entities
- **Async jobs**: long-running DLP jobs with results saved to BigQuery or Cloud Storage

### De-identification Transformations

| Transformation | Description | Reversible |
|---|---|---|
| **Redact** | Replace with empty string or a placeholder `[REDACTED]` | No |
| **Replace** | Replace with a fixed string | No |
| **Mask** | Replace characters with a masking character (e.g., `XXXX-1234`) | No |
| **Crypto hash** | SHA-256 hash of the matched text | No (one-way) |
| **Tokenize (Format-Preserving Encryption)** | Replace with format-preserving encrypted value; reversible with the KMS key | Yes (with key) |
| **Date shifting** | Shift dates randomly within a range; consistent per person with a key | Partially |
| **Generalization / bucketing** | Replace a value with a range or category (e.g., age 34 → 30-40) | No |
| **Pseudonymization** | Replace with an encrypted, consistent surrogate value | Yes (with key) |

**Key-based transformations** (FPE, crypto hash with key, date shift) use a Cloud KMS key, so only authorized parties with the key can reverse the transformation.

### Inspect Templates and Deidentify Templates
- **Inspect templates**: saved configurations for which infoTypes to detect, minimum likelihood thresholds, and exclusion rules. Reuse across jobs and API calls.
- **Deidentify templates**: saved de-identification transformation rules to apply consistently.

### DLP for Streaming Data
Use the DLP API's `inspectContent` and `deidentifyContent` methods inline in application code or Cloud Functions to inspect/de-identify data in real-time (e.g., in a Pub/Sub processing pipeline, before writing user input to a database).

---

## VPC Service Controls (VPC SC)

### Purpose
VPC Service Controls creates **security perimeters** around GCP services and their data to prevent data exfiltration. A perimeter defines which GCP projects/VPCs can access which GCP services. Requests crossing the perimeter boundary are denied, even if IAM permissions would otherwise allow them.

### Core concepts

**Access Policy**: the organization-wide container for VPC SC perimeters and access levels. One per org (or folder).

**Perimeter**: a named boundary that restricts access to specified GCP services (e.g., `storage.googleapis.com`, `bigquery.googleapis.com`) for projects within the perimeter. API calls from outside the perimeter to those services are blocked.

**Perimeter types**:
- **Regular perimeter**: strict enforcement; requests outside the perimeter are blocked
- **Bridge perimeter**: allows two regular perimeters to communicate with each other

**Restricted services**: the list of GCP service APIs that the perimeter applies to. Only calls to these APIs are subject to the perimeter rules.

**Ingress and Egress rules**: fine-grained rules that allow specific principals (users, service accounts) or access levels to access specific services/resources across the perimeter boundary without fully breaching it:
- **Ingress rule**: allows external identities/VPCs to access services within the perimeter
- **Egress rule**: allows identities within the perimeter to access services outside the perimeter

**Access levels**: conditions (from Access Context Manager) that allow specific principals to cross the perimeter boundary (e.g., requests from a corporate IP range, from Endpoint Verified devices).

**VPC Accessible Services**: restrict which GCP APIs can be called from VMs within a VPC, in addition to the perimeter enforcement.

### Dry-run mode
Test perimeter policy changes without enforcing them:
- Enable dry-run mode on a perimeter
- VPC SC logs what would have been blocked without actually blocking
- Review logs before switching to enforced mode

This is critical before applying VPC SC in production — many services have service-to-service dependencies that must be allowed via ingress/egress rules.

### Common use cases
- Prevent BigQuery datasets from being exported to projects outside the perimeter
- Prevent Cloud Storage bucket data from being accessed by external identities (even with public bucket settings)
- Restrict which VPCs can call Secret Manager or KMS
- Compliance: PCI DSS, HIPAA — ensure cardholder/PHI data cannot leave a defined boundary

### Limitations
- Not all GCP services support VPC SC (check the [supported services list](https://cloud.google.com/vpc-service-controls/docs/supported-products)).
- VPC SC perimeters require the organization's Access Policy to be configured.
- Service agent-to-service communications (e.g., Dataflow service agent calling Cloud Storage) require explicit ingress/egress rules.

---

## Binary Authorization

### Purpose
Binary Authorization enforces a policy that **only trusted container images can be deployed** to GKE, Cloud Run, or Anthos. It integrates with Artifact Registry's vulnerability scanning and software supply chain workflows to ensure images are built from trusted code, scanned, and signed before deployment.

### How it works
1. A **Binary Authorization policy** defines which images are allowed:
   - `defaultAdmissionRule`: what happens to images not explicitly covered by a rule
   - `clusterAdmissionRules` (GKE): per-cluster rules that override the default
   - Rules: `ALWAYS_ALLOW`, `ALWAYS_DENY`, or `REQUIRE_ATTESTATION`
2. For `REQUIRE_ATTESTATION` rules: the image digest must have an **attestation** signed by a trusted **attestor**.
3. An **attestor** is a named authority that attests to a quality of an image (e.g., "passed vulnerability scan", "reviewed by security team", "built by CI/CD").
4. An **attestation** is a cryptographic signature (using a Cloud KMS asymmetric signing key) binding an image digest to an attestor.
5. At deploy time, Binary Authorization verifies that the required attestations exist and were signed by the expected key.

### Attestor workflow (CI/CD pipeline integration)
1. CI builds the container image and pushes to Artifact Registry.
2. Vulnerability scanner (Artifact Analysis / Trivy / Snyk) scans the image.
3. If scan passes, the pipeline calls Binary Authorization API to create an attestation for the image digest, signed with the attestor's KMS key.
4. Deployment to GKE/Cloud Run checks for valid attestations per the policy.

### Breakglass procedure
Deployments can override the policy using a breakglass annotation (`alpha.image-policy.k8s.io/break-glass: "true"`) for emergency deployments. These overrides are logged in Cloud Audit Logs and should trigger alerts.

### Policy types
- **Project-wide policy**: applies to all GKE clusters and Cloud Run services in the project
- **Cluster-specific policy** (GKE): override the default rule for a specific cluster

---

## Certificate Authority Service (CAS)

### Purpose
Certificate Authority Service is a managed private PKI service for issuing TLS certificates for internal services, mTLS, and code signing. It eliminates the operational burden of managing CA infrastructure (HSMs, CRL distribution, OCSP responders, certificate lifecycle).

### Core concepts

**CA Pool**: a group of CAs that share a common issuance policy and can issue certificates together. Clients trust the pool, not individual CAs. CAs can be rotated within a pool without changing client trust configuration.

**Certificate Authority**: a CA within a pool. Can be a Root CA or Subordinate CA.
- **Root CA**: self-signed; the trust anchor. Typically offline or low-volume.
- **Subordinate CA**: signed by a Root CA (or an external CA); used for issuing end-entity certificates at scale.

**Certificate Template**: a reusable issuance configuration that constrains what can be in an issued certificate (key usage, extended key usage, allowed SANs, maximum validity, etc.).

**Certificate**: the issued TLS certificate (X.509). CAS stores the certificate and its metadata.

### Key features
- Hardware-backed CA keys (Cloud HSM FIPS 140-2 Level 3)
- Automatic CRL publishing and OCSP responder
- Certificate templates for enforcing issuance policies
- ACME protocol support (automating certificate issuance from CAS for ACME clients like certbot)
- Integration with Kubernetes cert-manager (via cert-manager-csi-driver-spiffe or Google CAS issuer plugin)
- IAM-controlled issuance: grant service accounts `roles/privateca.certificateRequester` to request certificates programmatically

### Common use cases
- Internal mTLS between microservices (Istio/Anthos service mesh CA replacement)
- TLS certificates for internal load balancers and services
- Client certificates for VPN or BeyondCorp device authentication
- Code signing certificates for Binary Authorization workflows

---

## Artifact Analysis (Vulnerability Scanning)

### Purpose
Artifact Analysis provides on-push vulnerability scanning for container images stored in Artifact Registry (and legacy Container Registry). It identifies vulnerabilities in OS packages and language-level dependencies.

### Scanning capabilities

| Scan Type | Details |
|---|---|
| OS packages | Debian, Ubuntu, Alpine, CentOS, RHEL, Windows base images |
| Language packages | npm (Node.js), pip (Python), Maven/Gradle (Java), Go modules, NuGet (.NET), Ruby gems |
| CVE database | Matches against National Vulnerability Database (NVD) and OS-specific security trackers |
| SBOM generation | Generate Software Bill of Materials (SBOM) in SPDX or CycloneDX format |

### Vulnerability findings
Each finding includes: CVE ID, severity (CRITICAL, HIGH, MEDIUM, LOW, MINIMAL), CVSS score, affected package/version, fixed version (if available), and references.

### Integration with Binary Authorization
Artifact Analysis can produce **attestations** automatically when a scan passes a quality gate (no critical vulnerabilities), enabling automated Binary Authorization workflows.

### On-demand scanning
Beyond Artifact Registry, the `gcloud artifacts docker images scan` command can scan images from any registry (including Docker Hub images) using Google's vulnerability scanner on-demand.

### SBOM (Software Bill of Materials)
Generate an SBOM for any image in Artifact Registry:
```bash
gcloud artifacts sbom export \
  --uri=us-central1-docker.pkg.dev/my-project/my-repo/my-image@sha256:DIGEST
```

---

## Access Transparency and Access Approval

### Access Transparency
Logs when Google infrastructure and support personnel access your GCP data or configuration. Access Transparency logs (separate from Cloud Audit Logs) include:
- The resource accessed
- The Google employee's justification (e.g., support case number, internal reason code)
- The action taken (read, modify)

Available for GCP services that support it (Compute Engine, Cloud Storage, BigQuery, Cloud SQL, etc.). Access Transparency logs are visible in Cloud Logging.

### Access Approval
Requires **explicit approval** from your organization before Google support or engineering can access your data or configuration in response to a support case. Google staff's request is sent via Pub/Sub to your approval system, and your admin must approve within a time window. If not approved, Google cannot access the data.

- Works with Cloud KMS Key Access Justifications for EKM key-backed data
- Approval requests can be routed to a custom HTTP endpoint or Pub/Sub for automated or ITSM-integrated approval workflows
- Dismissed or expired requests mean Google personnel cannot access the resource

---

## reCAPTCHA Enterprise

**Purpose**: Enterprise-grade bot detection and fraud prevention for websites and mobile apps using adaptive risk scoring.

### Core Concepts

| Concept | Description |
|---|---|
| **Site Key** | API key scoped to a domain or app; two types: score-based (v3 style) and checkbox (v2 style) |
| **Assessment** | Server-side API call to evaluate a reCAPTCHA token; returns risk score (0.0–1.0) and reasons |
| **Risk Score** | 0.0 = very likely bot; 1.0 = very likely human; threshold typically 0.5 |
| **Action** | Label attached to assessment (e.g., "login", "checkout") for analytics and policy tuning |
| **Annotation** | Post-hoc feedback to reCAPTCHA about whether a transaction was legitimate or fraud |
| **Express** | Frictionless protection via HTTP header analysis; no JavaScript token required |
| **WAF Integration** | reCAPTCHA Enterprise tokens enforced at Cloud Armor WAF layer (not just application layer) |
| **Mobile SDK** | Native Android and iOS SDKs for mobile app bot protection |
| **Password Leak Detection** | Check if user credentials have been compromised in known data breaches |

### Key Features

| Feature | Description |
|---|---|
| **Adaptive scoring** | ML model trained on Google's global traffic; adapts to new attack patterns automatically |
| **Reason codes** | Returns AUTOMATION, UNEXPECTED_ENVIRONMENT, TOO_MUCH_FRICTION, LOW_CONFIDENCE_SCORE, etc. |
| **Challenge types** | Invisible (score-based, no user interaction), Checkbox (visual challenge when score low) |
| **Account Defender** | Track user behavior across sessions; detect account takeover attempts; user risk scores |
| **Fraud Prevention** | Transaction fraud signals; combine with order signals to detect fraudulent purchases |
| **Cloud Armor integration** | Enforce reCAPTCHA token validity at WAF level; redirect suspicious traffic to reCAPTCHA challenge |
| **Annotations API** | Send ground truth labels (LEGITIMATE / FRAUDULENT) back to improve model accuracy |
| **Multi-factor detection** | Combines network, browser, device, and behavioral signals |

### Assessment Flow
1. Frontend: load reCAPTCHA JS → execute action → receive token
2. Backend: call `projects.assessments.create` with token + site key
3. Evaluate: check `tokenProperties.valid`, `riskAnalysis.score`, `riskAnalysis.reasons`
4. Decision: allow, challenge, or block based on score + action
5. Annotate: send result back to reCAPTCHA for model improvement

### When to Use
- Login and registration pages (credential stuffing, fake account creation)
- Checkout and payment flows (card testing, fraud)
- Password reset (account takeover)
- High-value API endpoints (scraping, abuse)
- Mobile apps with bot-driven abuse

### Pricing
- Free tier: 10,000 assessments/month
- Standard: $1 per 1,000 assessments after free tier
- Account Defender / Fraud Prevention: additional cost

---

## Access Transparency & Access Approval

**Purpose**: Near-real-time logs showing when and why Google personnel access your GCP content; Access Approval requires your explicit approval before Google can access your data.

### Access Transparency

| Concept | Description |
|---|---|
| **Access Transparency logs** | Near-real-time (within minutes) log entries in Cloud Logging when Google personnel access your content |
| **Justification** | Each log entry includes the reason for access: customer support ticket, security investigation, etc. |
| **Log format** | Appears in `_Required` log bucket (cannot be disabled); resource type `google.cloud.audit.AuditLog` |
| **Coverage** | Logs access by Google support engineers, site reliability engineers, and engineering personnel |
| **Availability** | Requires Premium Support or higher; available for most GCP services |

**Sample log entry fields**:
- `callerSuppliedUserAgent`: internal Google system identifier
- `requestMetadata.requestAttributes.reason`: justification code (e.g., `MULTI_PARTY_APPROVAL`)
- `authenticationInfo.principalEmail`: Google internal identity (obfuscated in some cases)
- `resourceName`: the GCP resource accessed

### Access Approval

| Concept | Description |
|---|---|
| **Access Approval** | Requires customer's explicit approval before Google personnel can access covered resources |
| **Approval Request** | Google sends an access request with justification; customer must approve within 12 hours or request expires |
| **Approvers** | Configured list of approvers (email addresses) who receive and can act on requests |
| **Approval Policy** | Resource-level policy defining which resources require approval and who can approve |
| **Active Key** | Signing key for approvals; Access Approval uses it to verify approval responses |
| **Dismiss** | Customer can dismiss (deny) an approval request; Google personnel cannot access |
| **Auto-dismiss** | Unanswered requests expire after 12 hours; Google cannot proceed |

### Access Approval Scope
Can be configured at: organization, folder, or project level. Covers GCP services (not Google Workspace). Works in conjunction with Access Transparency logging.

### Key Integration
- Access Transparency logs → Cloud Logging → Pub/Sub → SIEM (Chronicle, Splunk) for real-time alerting
- Access Approval requests → email notifications → customer approval workflow
- Combine with Assured Workloads for regulated workloads requiring government-grade access controls

---

## Best Practices

1. **Scan all Cloud Storage buckets** containing PII or financial data with DLP inspection jobs; schedule regular re-scans as data grows.
2. **Use format-preserving encryption (FPE) tokenization** for test environment data de-identification; it preserves data format for application testing while protecting real values.
3. **Apply VPC Service Controls in dry-run mode first**: the most common mistake is blocking legitimate service agent traffic; use dry-run logs to identify needed ingress/egress rules before enforcing.
4. **Include all service APIs that touch sensitive data** in the VPC SC perimeter, not just storage services (include BigQuery, Cloud Storage, Secret Manager, KMS, Container Registry/Artifact Registry).
5. **Use Binary Authorization in all production GKE clusters**: even without full attestation workflows, enabling the policy with `ALWAYS_DENY` as the default forces use of cluster-specific allow rules and improves awareness.
6. **Automate attestation creation in CI/CD**: failing to automate attestation means developers will seek workarounds (breakglass); the friction should be on the pipeline, not on the deployer.
7. **Use CAS subordinate CAs for issuing end-entity certificates**: keep root CAs offline and issue through intermediate/subordinate CAs to limit blast radius of CA compromise.
8. **Enable Artifact Analysis on all Artifact Registry repositories**: scanning is free for the first 100,000 container images per month; the cost of not scanning far outweighs the scan cost.
9. **Export DLP inspection job results to BigQuery** for trend analysis and compliance reporting (percentage of files containing PII, distribution by data type).
10. **Enable Access Transparency** for any GCP services containing regulated data; the audit trail of Google staff access is often required for SOC 2 Type II and ISO 27001 compliance.
