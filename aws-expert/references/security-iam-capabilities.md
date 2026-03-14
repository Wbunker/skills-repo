# AWS Security, Identity & Compliance — Capabilities Reference

High-level features and concepts for each service. For CLI commands, see [security-iam-cli.md](security-iam-cli.md).

## Table of Contents
1. [AWS IAM](#aws-iam)
2. [AWS STS (Security Token Service)](#aws-sts)
3. [AWS IAM Identity Center](#aws-iam-identity-center)
4. [AWS Organizations](#aws-organizations)
5. [Amazon Cognito](#amazon-cognito)
6. [Amazon Verified Permissions](#amazon-verified-permissions)
7. [AWS KMS](#aws-kms)
8. [AWS Secrets Manager](#aws-secrets-manager)
9. [AWS Certificate Manager (ACM)](#aws-certificate-manager)
10. [AWS CloudHSM](#aws-cloudhsm)
11. [Amazon GuardDuty](#amazon-guardduty)
12. [AWS Security Hub](#aws-security-hub)
13. [Amazon Inspector](#amazon-inspector)
14. [Amazon Macie](#amazon-macie)
15. [Amazon Detective](#amazon-detective)
16. [AWS WAF](#aws-waf)
17. [AWS Shield](#aws-shield)
18. [AWS Network Firewall](#aws-network-firewall)
19. [AWS Firewall Manager](#aws-firewall-manager)

---

## AWS IAM

**Purpose**: Controls who (authentication) can do what (authorization) on which AWS resources.

### Core Concepts

| Concept | Description |
|---|---|
| **User** | Long-term identity for a person or application; has credentials (password + access keys) |
| **Group** | Collection of users; attach policies to grant permissions to all members |
| **Role** | Identity assumed temporarily by users, services, or external identities; no long-term credentials |
| **Policy** | JSON document defining permissions; attached to identities or resources |
| **Principal** | Entity that can make requests: users, roles, AWS services, federated identities |
| **Permission boundary** | Maximum permissions an identity-based policy can grant to an IAM entity |
| **Service Control Policy (SCP)** | Org-level guardrails; constrain what accounts in an OU can do (see Organizations) |

### Policy Types

| Type | Where attached | Use case |
|---|---|---|
| **Identity-based** | User, group, or role | Grant permissions to an IAM entity |
| **Resource-based** | Resource (S3 bucket, KMS key, Lambda function) | Cross-account access, resource-level control |
| **Permission boundary** | User or role | Cap maximum permissions for delegated admin |
| **Session policy** | Passed when assuming a role | Further restrict a role's permissions for a specific session |
| **SCP** | AWS Organizations OU or account | Prevent actions regardless of identity-based policies |
| **VPC endpoint policy** | VPC endpoint | Restrict which AWS APIs are accessible via the endpoint |

### Policy Evaluation Logic

1. Explicit **Deny** always wins
2. **SCP** must allow (if Organizations)
3. **Resource-based policy** can grant cross-account access
4. **Identity-based policy** must allow
5. **Permission boundary** must allow (if set)
6. **Session policy** must allow (if role assumption)

### IAM Roles — Common Use Cases

| Use Case | Trust principal |
|---|---|
| EC2 instance accessing S3 | `ec2.amazonaws.com` |
| Lambda reading DynamoDB | `lambda.amazonaws.com` |
| Cross-account access | `arn:aws:iam::ACCOUNT_ID:root` |
| Federated identity (OIDC) | OIDC provider ARN + conditions |
| GitHub Actions CI/CD | `token.actions.githubusercontent.com` (OIDC) |
| EKS Pod (IRSA) | OIDC provider for the EKS cluster |

### Key Features

- **Access Analyzer**: Identifies resources shared externally; validates policy syntax; generates least-privilege policies from CloudTrail
- **Credential report**: Lists all users and the status of their credentials
- **IAM Access Advisor**: Shows services last accessed per user/role; helps right-size permissions
- **MFA enforcement**: Require MFA on console sign-in or before sensitive API calls via Condition keys
- **Password policy**: Enforce complexity, rotation, and reuse prevention for IAM users
- **Organizations integration**: Use IAM roles + SCPs for cross-account access patterns

### Important Condition Keys

| Key | Use |
|---|---|
| `aws:MultiFactorAuthPresent` | Require MFA for sensitive actions |
| `aws:RequestedRegion` | Restrict actions to specific regions |
| `aws:SourceVpc` / `aws:SourceVpce` | Restrict API calls to originate from a VPC |
| `aws:PrincipalTag` | Attribute-based access control (ABAC) |
| `aws:ResourceTag` | Require tags on resources being acted upon |
| `iam:PassedToService` | Control which services a role can be passed to |
| `sts:ExternalId` | Prevent confused deputy in cross-account roles |

---

## AWS STS

**Purpose**: Issues temporary security credentials for roles, federated users, and cross-account access.

### Key Operations

| Operation | Use |
|---|---|
| `AssumeRole` | Assume a role in same or different account |
| `AssumeRoleWithWebIdentity` | OIDC federation (GitHub Actions, Google, Cognito) |
| `AssumeRoleWithSAML` | SAML 2.0 federation (Okta, ADFS, Azure AD) |
| `GetSessionToken` | Temporary creds for IAM user (useful for MFA enforcement) |
| `GetFederationToken` | Long-lived temp creds for custom identity broker |
| `DecodeAuthorizationMessage` | Decode encoded error messages from authorization failures |

### Temporary Credential Duration

- `AssumeRole`: 15 min – 12 hours (default 1 hour; max set on role)
- `GetSessionToken`: 15 min – 36 hours
- `GetFederationToken`: 15 min – 36 hours

---

## AWS IAM Identity Center

**Purpose**: Centralized SSO for the AWS console, CLI, and business applications (formerly AWS SSO).

### Key Concepts

| Concept | Description |
|---|---|
| **Instance** | The Identity Center deployment (one per org, or account-level for standalone) |
| **Permission set** | A collection of IAM policies; becomes an IAM role in each account when assigned |
| **Account assignment** | Maps a user/group + permission set → AWS account |
| **Application assignment** | Maps a user/group → SAML/OIDC application |
| **Identity source** | Where users/groups are managed: built-in directory, Active Directory, or external IdP |

### Identity Sources

| Source | Description |
|---|---|
| **Identity Center directory** | Built-in; manage users/groups directly in Identity Center |
| **Active Directory** | AWS Managed AD or self-managed AD via AD Connector |
| **External IdP** | Any SAML 2.0 provider (Okta, Azure AD, Ping) via automatic provisioning (SCIM) |

### Capabilities

- **Multi-account access**: One login → access to all assigned AWS accounts with the right permission set
- **CLI SSO integration**: `aws sso login` + `aws configure sso` for local credentials
- **Trusted identity propagation**: Pass the user's identity to data services (Redshift, S3 Access Grants, EMR) for fine-grained data access control
- **ABAC support**: Tag users and use `aws:PrincipalTag` in permission set policies
- **MFA**: Enforce at the Identity Center level (TOTP, FIDO2/WebAuthn, SMS)
- **Access portal**: Managed web portal for users to sign in and access assigned accounts/apps

---

## AWS Organizations

**Purpose**: Manage multiple AWS accounts as a unit; apply governance policies across the org.

### Key Concepts

| Concept | Description |
|---|---|
| **Management account** | The root account; creates the org; not subject to SCPs |
| **Member account** | Any account in the org; subject to SCPs |
| **OU (Organizational Unit)** | Hierarchical grouping of accounts; policies applied to OU affect all child accounts |
| **SCP (Service Control Policy)** | Guardrails; define maximum permissions for accounts in OU/org |
| **Tag policy** | Enforce tag key/value standards across accounts |
| **Backup policy** | Define backup plans and apply them across accounts |
| **AI opt-out policy** | Control whether AWS AI services can use your data |
| **Delegated administrator** | Assign a member account to manage a specific AWS service (e.g., Security Hub) |

### SCP Behavior

- SCPs **do not grant permissions** — they define the maximum allowed
- Management account is **never** affected by SCPs
- An allow in an SCP still requires an allow in the IAM policy
- SCPs affect all principals in member accounts, including root user
- Commonly used to: deny leaving the org, require encryption, restrict regions, deny disabling security services

### Key Patterns

```json
// Deny all actions outside approved regions
{
  "Effect": "Deny",
  "Action": "*",
  "Resource": "*",
  "Condition": {
    "StringNotEquals": {
      "aws:RequestedRegion": ["us-east-1", "us-west-2"]
    },
    "ArnNotLike": {
      "aws:PrincipalARN": ["arn:aws:iam::*:role/BreakGlassRole"]
    }
  }
}
```

---

## Amazon Cognito

**Purpose**: Add user authentication and authorization to web and mobile apps.

### Two Services in One

| Service | Description |
|---|---|
| **User Pools** | User directory with sign-up, sign-in, MFA, social federation; issues JWTs |
| **Identity Pools** | Exchange tokens (Cognito, Google, SAML, OIDC) for temporary AWS credentials via STS |

### User Pools — Key Features

| Feature | Description |
|---|---|
| **Hosted UI** | Pre-built sign-in/sign-up pages; supports OAuth 2.0 flows |
| **Social federation** | Sign in with Google, Facebook, Apple, Amazon |
| **SAML/OIDC federation** | Enterprise SSO integration |
| **Lambda triggers** | Customize auth flows (pre-sign-up, pre-authentication, post-confirmation, etc.) |
| **Advanced Security** | Risk-based adaptive authentication; compromised credential detection |
| **App clients** | Configure per-app OAuth scopes, token expiry, redirect URIs |
| **Groups** | Assign users to groups; include group claims in tokens; map to IAM roles |
| **MFA** | TOTP, SMS; required or optional per pool or user |
| **User migration trigger** | Lazily migrate users from legacy user store without password reset |

### Identity Pools — Key Features

- Exchange any supported token for temporary AWS credentials (via STS)
- **Authenticated role**: IAM role for verified users
- **Unauthenticated role**: IAM role for guest users (optional)
- **Role-based access control**: Map Cognito groups or token claims to different IAM roles
- **Attribute access control**: Pass user attributes as session tags for ABAC

### Token Types (User Pools)

| Token | Contents | Typical expiry |
|---|---|---|
| **ID token** | User identity claims (name, email, groups) | 1 hour |
| **Access token** | OAuth scopes; used for API authorization | 1 hour |
| **Refresh token** | Used to obtain new ID/access tokens | 30 days (configurable) |

---

## Amazon Verified Permissions

**Purpose**: Fine-grained authorization service for your own applications using the Cedar policy language.

### Key Concepts

| Concept | Description |
|---|---|
| **Policy store** | Container for policies and the schema |
| **Schema** | Defines entity types (User, Photo, Album), their attributes, and valid action types |
| **Policy** | Cedar statements granting or forbidding principals to perform actions on resources |
| **Policy template** | Parameterized policy for creating many similar policies (e.g., share with specific user) |
| **Entity** | A principal (User) or resource (Photo) with typed attributes |
| **IsAuthorized API** | Real-time authorization decision: ALLOW or DENY |

### Cedar Policy Example

```cedar
// Allow premium users to view any photo
permit (
  principal in Group::"premium-users",
  action == Action::"ViewPhoto",
  resource
);

// Deny viewing photos in albums marked private
forbid (
  principal,
  action == Action::"ViewPhoto",
  resource
) when {
  resource.album.isPrivate == true &&
  !(principal in resource.album.owners)
};
```

### When to Use Verified Permissions vs IAM

| Use IAM | Use Verified Permissions |
|---|---|
| Controlling access to AWS services | Controlling access within your own application |
| AWS console/API access | App-level resource authorization (e.g., "can user X view document Y?") |
| EC2, S3, Lambda permissions | SaaS authorization logic, multi-tenant apps |

---

## AWS KMS

**Purpose**: Managed service for creating, controlling, and auditing cryptographic keys.

### Key Types

| Type | Description |
|---|---|
| **AWS managed key** | Created automatically by AWS services; you cannot manage directly; free |
| **Customer managed key (CMK)** | You create and control; $1/month per key; supports rotation, policies, grants |
| **AWS owned key** | Owned and managed entirely by AWS; no cost, no visibility |
| **Asymmetric key** | RSA or ECC key pairs for encryption or signing (cannot be used by AWS services for envelope encryption) |
| **HMAC key** | For generating and verifying Hash-based Message Authentication Codes |
| **Multi-region key** | Same key material replicated to multiple regions; one primary, replicas in others |

### Key Features

| Feature | Description |
|---|---|
| **Envelope encryption** | KMS encrypts a data key; data key encrypts the data; standard pattern for large data |
| **Key policy** | Resource-based policy on the key; must explicitly allow account root or no one can use it |
| **Grants** | Delegate key usage to AWS services or principals without modifying key policy |
| **Key rotation** | Automatic annual rotation for symmetric CMKs (key ID stays the same; old backing keys retained) |
| **Key aliases** | Friendly names for keys (`alias/my-key`); use instead of ARN in app config |
| **CloudTrail integration** | Every KMS API call logged; use for compliance and forensics |
| **Cross-account usage** | Key policy allows other account; grantee adds KMS permissions to their IAM policy |
| **Custom key store** | Back CMKs with AWS CloudHSM cluster you own; for regulatory requirements |

### Common Encryption Pattern (Envelope)

```
Application → GenerateDataKey(CMK) → KMS returns [plaintext_key, encrypted_key]
Application → Encrypt data with plaintext_key (in memory)
Application → Store encrypted_data + encrypted_key together
Application → Discard plaintext_key

Decrypt: Send encrypted_key to KMS Decrypt → get plaintext_key → decrypt data
```

---

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

---

## Amazon GuardDuty

**Purpose**: Intelligent threat detection continuously monitoring AWS accounts, workloads, and data.

### Data Sources

| Source | What it detects |
|---|---|
| **VPC Flow Logs** | Unusual network activity, port scanning, crypto-mining traffic |
| **CloudTrail events** | Suspicious API activity, credential exfiltration, account takeover |
| **DNS logs** | DNS-based C2 communication, data exfiltration via DNS |
| **S3 data events** | S3 bucket compromises, data exfiltration |
| **EKS audit logs** | Kubernetes API anomalies, container escapes |
| **EKS runtime monitoring** | Container-level runtime threat detection (requires agent) |
| **ECS runtime monitoring** | Container-level runtime on Fargate and EC2 |
| **EC2 runtime monitoring** | OS-level threat detection (requires agent) |
| **Lambda network activity** | Unusual Lambda outbound connections |
| **RDS login activity** | Brute force, anomalous logins to Aurora |
| **Malware Protection** | Scan EBS volumes on suspicious EC2/container for malware |

### Finding Categories

| Category | Example finding types |
|---|---|
| **Backdoor** | EC2 making outbound calls to known C2 IPs |
| **CryptoCurrency** | EC2/container mining cryptocurrency |
| **Recon** | Port scanning, credential enumeration |
| **Trojan** | DNS queries to known malicious domains |
| **UnauthorizedAccess** | Tor exit node access, credential stuffing |
| **Stealth** | CloudTrail logging disabled, config changes to hide activity |
| **Impact** | S3 data destruction, ransomware indicators |
| **CredentialAccess** | IAM credential theft or unusual use |
| **Exfiltration** | Large data transfers out of S3 |

### Key Features

- **Multi-account**: Designate a delegated administrator; aggregate findings from all org accounts
- **Suppression rules**: Filter out known-good findings automatically
- **Trusted IP lists**: Mark known IP ranges as trusted (suppress findings from them)
- **Threat intelligence lists**: Add custom IOC lists (malicious IPs, domains)
- **EventBridge integration**: Route findings to SIEM, ticketing, or automated remediation
- **Finding export**: Continuous export to S3 for long-term retention and SIEM ingestion

---

## AWS Security Hub

**Purpose**: Aggregates security findings from GuardDuty, Inspector, Macie, IAM Access Analyzer, Firewall Manager, and third-party tools; runs automated compliance checks.

### Security Standards (Automated Checks)

| Standard | Description |
|---|---|
| **AWS Foundational Security Best Practices** | AWS-curated controls across services |
| **CIS AWS Foundations Benchmark** | Center for Internet Security benchmark controls |
| **PCI DSS** | Payment Card Industry controls |
| **NIST SP 800-53** | NIST controls for federal systems |
| **SOC 2** | Service Organization Control 2 criteria |

### Key Concepts

| Concept | Description |
|---|---|
| **Finding** | A security issue; normalized to ASFF (Amazon Security Finding Format) |
| **Control** | An automated check; PASSED/FAILED/NOT_AVAILABLE result per account/region |
| **Security score** | Percentage of passed controls; per account and aggregated |
| **Insight** | Saved grouping/filter of findings for recurring analysis |
| **Custom action** | Send findings to EventBridge for automated response |
| **Aggregation region** | Link multiple regions; view all findings in one region |

### Integration Sources

AWS native: GuardDuty, Inspector, Macie, IAM Access Analyzer, Firewall Manager, Config, Systems Manager Patch Manager, Detective

Third-party: Palo Alto, CrowdStrike, Splunk, Rapid7, Tenable, and 60+ others

---

## Amazon Inspector

**Purpose**: Automated vulnerability management scanning for EC2, ECR container images, Lambda functions, and code (CodeGuru integration).

### Scan Types

| Scan | Target | What it finds |
|---|---|---|
| **EC2 scanning** | Running instances | OS CVEs, network reachability issues |
| **ECR container scanning** | Container images in ECR | OS CVEs, programming language package CVEs |
| **Lambda scanning** | Lambda function packages | Language dependency CVEs |
| **Lambda code scanning** | Lambda code | Security code issues via CodeGuru |
| **CIS scanning** | EC2 instances | CIS Benchmark hardening failures |
| **Code security scanning** | CodePipeline integration | SAST findings |

### Finding Severity

Uses CVSS v3 scoring:
- **Critical**: 9.0–10.0
- **High**: 7.0–8.9
- **Medium**: 4.0–6.9
- **Low**: 0.1–3.9

### Key Features

- **Delegated administrator**: Centralize across org accounts
- **Suppression rules**: Suppress findings matching criteria (e.g., accepted risk)
- **SBOM export**: Export software bill of materials per resource
- **ECR enhanced scanning**: Replace basic scanning; automatically rescans when new CVEs published
- **Auto-remediation**: Integrate with SSM Patch Manager via EventBridge

---

## Amazon Macie

**Purpose**: Uses ML to automatically discover and protect sensitive data (PII, PHI, financial data, credentials) stored in S3.

### Key Features

| Feature | Description |
|---|---|
| **Automated discovery** | Continuously evaluates all S3 buckets for sensitive data exposure risk |
| **Sensitive data discovery jobs** | Target specific buckets/objects; run on schedule or one-time |
| **Managed data identifiers** | Pre-built detectors for 200+ data types: SSNs, credit cards, credentials, health data |
| **Custom data identifiers** | Regex + keywords for business-specific sensitive data |
| **Allow lists** | Exclude known-safe patterns from findings (e.g., test data) |
| **Bucket inventory** | Visibility into all S3 buckets: public access, encryption, sharing status |
| **Multi-account** | Delegated admin aggregates findings across org |

### Finding Types

| Category | Examples |
|---|---|
| **Policy findings** | Bucket made public, bucket encryption disabled, bucket shared cross-account |
| **Sensitive data findings** | PII, credentials, financial data, health information found in object |

---

## Amazon Detective

**Purpose**: Analyzes and visualizes security data to investigate and understand the root cause of security findings.

### Key Concepts

- Ingests CloudTrail, VPC Flow Logs, GuardDuty findings, EKS audit logs automatically
- Builds a **behavior graph** — a linked dataset across time correlating entities (IPs, users, roles, instances)
- Does **not** detect threats itself; it helps you **investigate** findings from GuardDuty, Security Hub, etc.

### Investigation Capabilities

| Capability | Description |
|---|---|
| **Entity profiles** | Timeline of activity for an IP, user, role, EC2 instance, or S3 bucket |
| **Finding groups** | AI-clustered related findings into a single investigation |
| **Scope time** | Adjust the time window of an investigation |
| **Related findings** | Surfaces GuardDuty findings related to the entity |
| **Geolocation** | Map API call and network activity by location |
| **Role session analysis** | See which assumed-role sessions made which API calls |

---

## AWS WAF

**Purpose**: Web Application Firewall protecting web apps and APIs against Layer 7 attacks.

### Key Concepts

| Concept | Description |
|---|---|
| **Web ACL** | The top-level WAF resource; attached to ALB, CloudFront, API Gateway, Cognito, AppSync, App Runner |
| **Rule** | Inspects requests using conditions; has an action (Allow, Block, Count, CAPTCHA, Challenge) |
| **Rule group** | Reusable collection of rules; can be AWS Managed, third-party, or custom |
| **IP set** | List of IP/CIDR ranges for use in rules |
| **Regex pattern set** | Regular expressions for matching request content |
| **Scope** | REGIONAL (ALB, API Gateway, etc.) or CLOUDFRONT (must be in us-east-1) |

### AWS Managed Rule Groups

| Group | Protects Against |
|---|---|
| `AWSManagedRulesCommonRuleSet` | OWASP Top 10, common exploits |
| `AWSManagedRulesKnownBadInputsRuleSet` | Log4j, Spring4Shell, known exploit payloads |
| `AWSManagedRulesSQLiRuleSet` | SQL injection |
| `AWSManagedRulesLinuxRuleSet` | Linux-specific attacks |
| `AWSManagedRulesAmazonIpReputationList` | Amazon-tracked malicious IPs |
| `AWSManagedRulesBotControlRuleSet` | Bot detection (common bots; intelligent threat mitigation) |
| `AWSManagedRulesATPRuleSet` | Account takeover protection (credential stuffing) |
| `AWSManagedRulesACFPRuleSet` | Account creation fraud prevention |

### Rule Actions

| Action | Description |
|---|---|
| **Allow** | Permit the request; skip remaining rules |
| **Block** | Return 403 to the client |
| **Count** | Log the match but do not block; useful for testing rules |
| **CAPTCHA** | Serve a CAPTCHA puzzle; block if failed |
| **Challenge** | Serve a silent browser challenge (JavaScript check); block if failed |

### Key Features

- **Rate-based rules**: Block IPs exceeding a request rate threshold
- **Geo-match**: Allow or block by country
- **Label matching**: Rules can add labels; subsequent rules can match labels (chained logic)
- **Managed rule group versions**: Pin to a specific version or opt into auto-update
- **Request sampling**: Inspect 100 recent matched requests per rule in console/API
- **Logging**: Full request/response logging to Kinesis Firehose, S3, or CloudWatch Logs

---

## AWS Shield

**Purpose**: DDoS protection for AWS resources.

### Tiers

| Tier | Cost | What it includes |
|---|---|---|
| **Standard** | Free, automatic | Always-on L3/L4 protection for all AWS customers |
| **Advanced** | $3,000/month + data transfer | Enhanced detection, attack diagnostics, DRT access, cost protection, L7 auto-mitigation |

### Shield Advanced Key Features

| Feature | Description |
|---|---|
| **DDoS Response Team (DRT)** | 24/7 AWS security experts; grant them access via IAM role + Flow Logs |
| **Attack diagnostics** | Real-time attack visibility and post-attack reports |
| **Proactive engagement** | DRT contacts you proactively when health checks fail during an attack |
| **Cost protection** | AWS credits for scaling costs incurred during DDoS events |
| **Health-check based detection** | Tie Route 53 health checks to protections for faster detection |
| **Automatic L7 mitigation** | Automatically creates WAF rules during CloudFront/ALB attacks (requires WAF) |
| **Protection groups** | Logically group resources (e.g., all ALBs) for aggregate protection view |

### Protected Resource Types (Advanced)

EC2 Elastic IPs, ELB (ALB/NLB/CLB), CloudFront, Route 53, AWS Global Accelerator

---

## AWS Network Firewall

**Purpose**: Managed, stateful network firewall and intrusion prevention system (IPS) for VPCs.

### Key Concepts

| Concept | Description |
|---|---|
| **Firewall** | Deployed into a VPC; requires dedicated subnet per AZ |
| **Firewall policy** | Associates stateless and stateful rule groups; sets default actions |
| **Stateless rule group** | Processes packets individually; actions: pass, drop, forward to stateful engine |
| **Stateful rule group** | Inspects traffic flows; supports Suricata-compatible rules, domain lists, standard rules |
| **Rule group** | Can be shared across firewalls via resource policy |

### Stateful Rule Types

| Type | Use case |
|---|---|
| **Suricata-compatible rules** | Full IDS/IPS signatures; supports `alert`, `drop`, `pass` |
| **Domain list rules** | Allow/deny list of FQDNs; inspect HTTP Host and TLS SNI headers |
| **Standard 5-tuple rules** | Source/dest IP, port, protocol with optional keyword matching |

### Traffic Flow Pattern

```
Internet → IGW → Firewall endpoint (in firewall subnet) → Application subnet
(Route tables must route traffic through the firewall endpoint)
```

### Key Features

- **TLS inspection**: Decrypt and inspect TLS traffic (requires Certificate Manager private CA)
- **Centralized deployment**: Single firewall for multiple VPCs via Transit Gateway
- **Logging**: Alert and flow logs to S3, CloudWatch Logs, or Kinesis Firehose
- **Traffic analysis reports**: Identify top traffic patterns for rule creation

---

## AWS Firewall Manager

**Purpose**: Centrally configure and enforce AWS WAF, Shield Advanced, Network Firewall, and security group policies across accounts in AWS Organizations.

### Policy Types

| Policy Type | What it manages |
|---|---|
| **AWS WAF** | Deploy Web ACLs to ALBs, CloudFront, API Gateway across accounts |
| **Shield Advanced** | Auto-protect resource types across accounts |
| **Security group** | Enforce security group usage or audit non-compliant groups |
| **Network Firewall** | Deploy Network Firewalls to VPCs across accounts |
| **Route 53 DNS Firewall** | Deploy DNS Firewall rule groups across VPCs/accounts |
| **Palo Alto / third-party** | Deploy third-party NGFW via Marketplace |

### Key Requirements

- Must have **AWS Organizations** enabled
- **AWS Config** must be enabled in all member accounts (Firewall Manager uses Config to discover resources)
- Designate a **Firewall Manager administrator** account (separate from Org management account recommended)

### Key Features

- **Automatic remediation**: Automatically bring non-compliant resources into compliance
- **Compliance dashboard**: View policy compliance status per account
- **Resource sets**: Define a specific set of resources for a policy to target
- **Discovered resources**: Identify unprotected resources matching policy scope
- **Notification channel**: SNS alerts for compliance violations
