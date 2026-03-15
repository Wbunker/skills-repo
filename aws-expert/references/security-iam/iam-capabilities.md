# AWS IAM — Capabilities Reference
For CLI commands, see [iam-cli.md](iam-cli.md).

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

## IAM Access Analyzer

**Purpose**: Identify resources shared with external entities or unintended access, validate IAM policies, and find unused access.

### Core Concepts

| Concept | Description |
|---|---|
| **Analyzer** | Regional resource that continuously monitors supported resource types for external or unused access |
| **Zone of Trust** | Boundary used to evaluate access: either the AWS account or the entire AWS Organization |
| **Finding** | A result representing external access or unused access that may require review |
| **Archive Rule** | Auto-archive findings that match specified criteria (e.g., known-trusted external account) |
| **Policy Validation** | Checks a policy document against IAM policy grammar and best practices |
| **Custom Policy Check** | API-driven checks to enforce specific access controls before deploying policies |
| **Unused Access Analyzer** | Analyzer type that identifies unused roles, credentials, and permissions across accounts |

### Finding Types

- **External access findings**: resources accessible outside the zone of trust — S3 buckets, IAM roles, KMS keys, Lambda functions, SQS queues, Secrets Manager secrets, and more
- **Unused access findings**: unused roles (not used within configurable lookback period), unused IAM credentials (access keys, passwords not used), unused permissions (actions granted but never called)

### Policy Validation

- 100+ policy checks covering: general warnings, security warnings, suggestions, and errors
- Validates identity-based policies, resource-based policies, SCPs, trust policies, and more
- Returns findings with issue location (JSON path) and recommended fix

### Custom Policy Checks (via AWS CLI/API)

| Check | Description |
|---|---|
| `check-no-new-access` | Verify a new policy version does not grant more access than a reference policy |
| `check-access-not-granted` | Verify a policy does not grant specific actions or resource access |

### Archive Rules

Automatically archive findings that match criteria (e.g., a trusted external account ID or principal ARN), keeping the finding list focused on actionable items.

## IAM Roles Anywhere

**Purpose**: Extend IAM roles to on-premises workloads, CI/CD systems, or any workload outside AWS without long-term credentials.

### Core Concepts

| Concept | Description |
|---|---|
| **Trust Anchor** | References a Certificate Authority used to validate workload certificates; supports ACM Private CA, self-signed CAs, or external CAs |
| **Profile** | Selects the IAM role(s) to assume, optional session policies, and maximum session duration |
| **Role** | Standard IAM role whose trust policy permits `rolesanywhere.amazonaws.com` |
| **Subject** | The entity represented by an X.509 certificate presented by the workload |
| **Credential Helper** | `aws_signing_helper` tool; generates temporary credentials using an X.509 cert and private key |

### How It Works

1. Workload presents an X.509 certificate signed by a trusted CA
2. Roles Anywhere validates the certificate against the configured trust anchor
3. Roles Anywhere calls STS to issue temporary credentials for the matched IAM role
4. Workload uses temporary credentials to call AWS APIs (no long-term access keys required)

### Use Cases

- On-premises servers needing AWS API access
- GitHub Actions or Jenkins CI/CD pipelines
- Hybrid and multi-cloud environments
- Any workload that can hold an X.509 certificate

### Condition Keys for Fine-Grained Access Control

| Key | Use |
|---|---|
| `rolesanywhere:TrustAnchorArn` | Restrict which trust anchor a subject may use |
| `rolesanywhere:ProfileArn` | Restrict which profiles a subject may use |
| `rolesanywhere:SubjectCommonName` | Match on the CN field of the presented certificate |
| `rolesanywhere:X509Subject/SerialNumber` | Match on certificate serial number |
| `rolesanywhere:X509Issuer` | Match on certificate issuer DN |
