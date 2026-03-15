# AWS Secrets Manager, ACM & CloudHSM — Capabilities Reference
For CLI commands, see [secrets-acm-cloudhsm-cli.md](secrets-acm-cloudhsm-cli.md).

## AWS Secrets Manager

**Purpose**: Store, rotate, and retrieve secrets (database credentials, API keys, OAuth tokens).

### Key Features

| Feature | Description |
|---|---|
| **Secret rotation** | Automated rotation using Lambda functions; native support for RDS, Redshift, DocumentDB, other DBs |
| **Versioning** | Secrets have versions with staging labels (AWSCURRENT, AWSPENDING, AWSPREVIOUS) |
| **Encryption** | Encrypted at rest using KMS (AWS managed or CMK) |
| **Resource policy** | Control cross-account or service access to specific secrets |
| **Replication** | Replicate secrets to multiple regions for DR and multi-region apps |
| **VPC endpoint** | Access Secrets Manager without internet via PrivateLink |
| **CloudTrail logging** | All secret access events are logged |

### vs. SSM Parameter Store

| | Secrets Manager | SSM Parameter Store |
|---|---|---|
| Cost | $0.40/secret/month | Free (Standard); $0.05/advanced param/month |
| Rotation | Native, automatic | Manual Lambda only |
| Cross-account | Yes (resource policy) | Limited |
| Versioning | Yes (labeled) | Yes (numbered) |
| Use case | Secrets requiring rotation | Config values, secrets without rotation |

---

## AWS Certificate Manager

**Purpose**: Provision, manage, and auto-renew SSL/TLS certificates for AWS services.

### Certificate Types

| Type | Description |
|---|---|
| **ACM-issued (public)** | Free; for use with AWS services (ALB, CloudFront, API Gateway, etc.); auto-renews |
| **ACM-issued (private)** | From AWS Private CA; for internal services; charged per cert issued |
| **Imported** | Bring your own certificate; you manage renewal; appears in ACM for association |

### Validation Methods

| Method | How it works |
|---|---|
| **DNS validation** | Add a CNAME record to your DNS zone; ACM validates automatically; preferred for auto-renewal |
| **Email validation** | ACM sends email to domain owner contacts; requires manual approval |

### Key Constraints

- ACM public certs **cannot be exported** — they can only be used with integrated AWS services
- Certs for CloudFront must be in **us-east-1** regardless of distribution region
- ACM auto-renews certs 60 days before expiration (DNS validation only; email requires manual re-validation)

---

## AWS CloudHSM

**Purpose**: FIPS 140-2 Level 3 validated hardware security modules for managing your own cryptographic keys.

### Key Concepts

| Concept | Description |
|---|---|
| **HSM cluster** | Group of HSMs in a VPC; provide high availability and load balancing |
| **HSM** | Physical hardware device dedicated to you in an AWS datacenter |
| **Crypto user (CU)** | HSM user that can create/use keys (set up by you, not AWS) |
| **Crypto officer (CO)** | HSM admin user for managing CUs and HSM configuration |

### vs. KMS Custom Key Store

| | CloudHSM (standalone) | KMS Custom Key Store |
|---|---|---|
| Key control | Full; you manage HSM | Partial; KMS manages API |
| KMS integration | No native | Yes — use KMS API backed by your HSM |
| PKCS#11 / JCE / CNG | Yes | No |
| Complexity | High | Medium |
| Use when | PKCS#11 required, full key custody | Regulatory compliance + KMS API convenience |
