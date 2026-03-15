# Compliance & PKI — Capabilities Reference
For CLI commands, see [compliance-pki-cli.md](compliance-pki-cli.md).

## AWS Artifact

**Purpose**: On-demand access to AWS security and compliance documentation — audit reports, certifications, and legal agreements.

### Available Document Types

| Type | Examples |
|---|---|
| **Compliance reports** | SOC 1/2/3, PCI DSS Attestation of Compliance, ISO 27001/27017/27018, FedRAMP |
| **Certifications** | ISO certifications, CSA STAR, IRAP, HITRUST |
| **Agreements** | Business Associate Addendum (BAA) for HIPAA, Non-Disclosure Agreement (NDA) |
| **Marketplace vendor docs** | ISV security and compliance reports via AWS Marketplace Vendor Insights |

### Key Features

| Feature | Description |
|---|---|
| **No cost** | All Artifact reports and agreements are free |
| **On-demand download** | Immediate access without waiting for AWS to respond to audit requests |
| **Agreement management** | Accept, track, and manage agreements for single accounts or entire Organizations |
| **Organizations scope** | BAA/NDA accepted at the management account level covers all member accounts |

### Important Constraints

- Artifact documents cover **AWS infrastructure** only; customers must produce their own application-level compliance evidence
- Artifact complements but does not replace AWS Audit Manager for evidence collection
- Some reports are versioned; always confirm you are referencing the current report version

### Integration with Other Services

- **AWS Audit Manager**: Artifact provides the AWS-side compliance docs; Audit Manager collects customer-side evidence
- **AWS Organizations**: Agreements accepted at the management account can cover all member accounts

---

## AWS Audit Manager

**Purpose**: Continuously audits AWS usage to automate evidence collection and simplify risk and compliance assessments against frameworks such as PCI DSS, HIPAA, SOC 2, GDPR, and CIS Benchmarks.

### Core Concepts

| Concept | Description |
|---|---|
| **Framework** | Structured set of controls mapped to a compliance standard (prebuilt or custom) |
| **Assessment** | An instantiation of a framework scoped to specific AWS accounts and services; runs continuously |
| **Control** | A policy, procedure, or activity being evaluated (e.g., "MFA enabled on root account") |
| **Control set** | A grouping of controls within a framework (e.g., "Access Control" domain) |
| **Evidence** | Automatically collected data (Config snapshots, CloudTrail events, Security Hub checks) attached to controls |
| **Evidence folder** | Groups evidence items by day for a given control |
| **Assessment report** | Audit-ready PDF/CSV summarizing evidence and findings for a given assessment period |

### Prebuilt Frameworks

| Framework | Standard |
|---|---|
| PCI DSS | Payment Card Industry Data Security Standard |
| HIPAA | Health Insurance Portability and Accountability Act |
| SOC 2 | System and Organization Controls 2 |
| GDPR | General Data Protection Regulation |
| CIS Foundations Benchmark | Center for Internet Security AWS Foundations |
| GxP | FDA 21 CFR Part 11 / EU Annex 11 |
| AWS Operational Best Practices | AWS Config conformance packs |
| NIST 800-53 | National Institute of Standards and Technology |

### Evidence Sources

| Source | What Audit Manager collects |
|---|---|
| **AWS Config** | Resource configuration snapshots and compliance rule evaluations |
| **AWS CloudTrail** | API activity logs converted to user-activity evidence |
| **AWS Security Hub** | CSPM findings and security check results |
| **AWS License Manager** | License usage data |
| **Manual uploads** | Screenshots, policy documents, spreadsheets uploaded by team members |

### Key Features

- **Delegated reviews**: Assign control sets to subject matter experts across teams
- **Evidence Finder**: Search and filter evidence across assessments; export results to CSV
- **Cross-account**: Designate a delegated administrator account via Organizations
- **Custom controls and frameworks**: Build controls from scratch or modify prebuilt ones; share frameworks across accounts
- **Evidence integrity**: Evidence is stored in a tamper-resistant manner with hash validation

### Important Constraints

- Audit Manager collects evidence but **does not make compliance determinations** — interpretation requires compliance expertise
- Assessments must be set to inactive to stop evidence collection (and billing)
- Evidence is retained for the life of the assessment; deleting an assessment deletes its evidence

### Integration Patterns

```
AWS Config / CloudTrail / Security Hub
        │
        ▼
  Audit Manager Assessment
  (continuous evidence collection)
        │
        ├─► Delegated reviewers add manual evidence
        │
        ▼
  Assessment Report (PDF/CSV)
        │
        ▼
  External auditor / GRC tool
```

---

## AWS Private Certificate Authority (AWS Private CA)

**Purpose**: Managed private certificate authority service for issuing internal TLS certificates — eliminating the operational overhead of running on-premises CA infrastructure.

### Core Concepts

| Concept | Description |
|---|---|
| **Root CA** | Top of the CA hierarchy; self-signed; used to sign subordinate CA certificates |
| **Subordinate CA** | Issues end-entity certificates; signed by root CA or an external CA |
| **CA hierarchy** | Chain of trust from root → subordinate → end-entity certificates |
| **End-entity certificate** | TLS/client/code-signing certificate issued to an application, server, or device |
| **CRL (Certificate Revocation List)** | Published to S3; allows clients to check if a cert has been revoked |
| **OCSP** | Online Certificate Status Protocol; real-time revocation status |
| **Path length constraint** | Limits how many subordinate CAs can be chained below a given CA |

### Certificate Key Algorithms

| Algorithm | Notes |
|---|---|
| RSA 2048 / 3072 / 4096 | Widely compatible; larger key = slower |
| EC P-256 / P-384 / P-521 | Smaller, faster; preferred for TLS |
| ML-DSA 44/65/87 | Post-quantum algorithms (preview) |

### Pricing Model

| Component | Cost |
|---|---|
| Monthly CA fee | Per private CA active per month |
| Per certificate issued | Charged per certificate |
| ACM-managed private certs | Free when used with integrated services (ALB, CloudFront, API Gateway) |

### Key Features

- **ACM integration**: Request private certs via ACM; ACM handles auto-renewal and binding to AWS services
- **Short-lived certificates**: Issue certs with very short validity periods for zero-trust patterns
- **Cross-account sharing**: Share a CA with other accounts via RAM or resource-based policies
- **Audit reports**: Generate audit reports listing all issued/revoked certs
- **IoT and EKS**: Issue certificates for IoT devices and Kubernetes workloads (cert-manager integration)

### CA Hierarchy Pattern

```
Root CA (AWS Private CA — rarely used directly)
    │
    └─► Subordinate Issuing CA (issues end-entity certs)
             │
             ├─► TLS cert (ALB, internal services)
             ├─► Client cert (mTLS, IoT devices)
             └─► Code signing cert
```

### vs. ACM Public Certificates

| | AWS Private CA | ACM Public Certs |
|---|---|---|
| Trust | Private (internal only) | Publicly trusted |
| Cost | Per CA + per cert | Free |
| Export | Yes (private key exportable) | No |
| Use case | Internal TLS, mTLS, IoT, code signing | Public-facing HTTPS |
| Validation | None required | DNS or email |

---

## AWS Payment Cryptography

**Purpose**: Fully managed HSM-backed service providing cryptographic operations for payment card processing — replacing dedicated payment HSMs with a cloud-native, elastically scalable API.

### Core Concepts

| Concept | Description |
|---|---|
| **Key** | Cryptographic key stored and managed in the service; never leaves the HSM unencrypted |
| **Key alias** | Human-readable name mapped to a key ARN |
| **TR-31 key block** | ANSI X9.143 standard format for wrapping symmetric keys during export/import; includes key type and usage metadata |
| **TR-34** | ASC X9.134 standard for asymmetric key exchange between key management systems (e.g., distributing keys to POS terminals) |
| **DUKPT** | Derived Unique Key Per Transaction; derives a unique key per transaction from a base derivation key (BDK), limiting exposure per transaction |
| **Control plane** | Key management API (`payment-cryptography`) — create, import, export, delete keys |
| **Data plane** | Cryptographic operations API (`payment-cryptography-data`) — encrypt, PIN translate, MAC generate, etc. |

### Supported Compliance Standards

| Standard | Description |
|---|---|
| **PCI DSS** | Payment Card Industry Data Security Standard |
| **PCI PIN** | PIN security requirements for HSMs used in PIN processing |
| **PCI P2PE** | Point-to-Point Encryption for protecting card data from swipe to processor |

### Data Plane Operations

| Operation | Use case |
|---|---|
| `encrypt-data` / `decrypt-data` | Encrypt/decrypt cardholder data at rest or in transit |
| `re-encrypt-data` | Translate ciphertext from one key to another without exposing plaintext |
| `generate-mac` / `verify-mac` | Integrity protection for payment messages |
| `generate-pin-data` / `verify-pin-data` | Generate/verify PINs (PIN offset, ANSI PIN block) |
| `translate-pin-data` | Translate PIN block between formats or encryption keys (acquiring ↔ issuing domains) |
| `generate-card-validation-data` / `verify-card-validation-data` | CVV/CVV2 generation and verification |
| `verify-auth-request-cryptogram` | Verify EMV ARQC/ARPC for chip card transactions |

### Key Lifecycle

```
Import (TR-31 / TR-34)    Create (generated in HSM)
         │                          │
         └──────────┬───────────────┘
                    ▼
            Key (stored in HSM)
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
    start-key-usage   replicate   export (TR-31)
       (enable)     (multi-region)  (to other HSM)
          │
    Data plane ops
    (encrypt, MAC, PIN...)
          │
    stop-key-usage / delete-key
```

### Integration Patterns

- **AWS Lambda + API Gateway**: Serverless payment processing — Lambda calls Payment Cryptography data plane
- **Amazon ECS / EKS**: Containerized payment applications replacing socket-based HSM connections
- **Key import via TR-34**: Import zone master keys from existing payment HSMs during cloud migration
- **Multi-region replication**: Replicate keys to additional regions for DR and latency optimization

---

## AWS Signer

**Purpose**: Managed code-signing service that ensures the integrity and authenticity of code — preventing execution of unsigned or tampered artifacts.

### Core Concepts

| Concept | Description |
|---|---|
| **Signing Profile** | Named configuration specifying the platform, signature validity period, and signature algorithm |
| **Signing Job** | A single signing operation; consumes a source artifact and produces a signed artifact with a signature |
| **Platform** | Defines the signing algorithm and artifact format; AWS-managed and not customer-configurable |
| **Signature** | Cryptographic proof of code authenticity attached to or alongside the signed artifact |
| **Revocation** | Invalidate a signing profile or individual signature; prevents execution of previously signed artifacts |

### Supported Platforms

| Platform ID | Use case |
|---|---|
| `AWSLambda-SHA384-ECDSA` | Lambda deployment packages |
| `AWSIoTDeviceManagement-SHA256-ECDSA` | IoT firmware for over-the-air updates |
| `Notation-OCI-SHA384-ECDSA` | Container images via Notation CLI (OCI-compliant) |

### Lambda Code Signing

| Concept | Description |
|---|---|
| **Signing configuration** | Associates a signing profile with a Lambda function; all deployed packages must be signed by an approved profile |
| **Untrusted artifact policy** | `Warn` — logs a warning but allows invocation; `Enforce` — blocks invocation of unsigned or revoked packages |
| **Code signing config** | AWS resource (`aws lambda create-code-signing-config`) that holds signing profile ARNs and the untrusted artifact policy; attached to a Lambda function |

### Container Image Signing

- Uses the **Notation CLI** with the **AWS Signer plugin for Notation** (`notation sign` / `notation verify`)
- Produces OCI-compliant signatures stored alongside images in ECR
- **Trust policies** define which signing profiles and identities are trusted for verification
- Integrate with Kubernetes admission controllers (e.g., Ratify) to enforce signature verification at deployment time

### IoT Device Signing

- Sign firmware images using the `AWSIoTDeviceManagement-SHA256-ECDSA` platform
- Signed firmware is distributed via **AWS IoT Jobs** for over-the-air (OTA) updates
- IoT devices verify the signature before applying a firmware update, preventing installation of tampered firmware
