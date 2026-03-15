# AWS Cloud Map & Verified Access — Capabilities Reference
For CLI commands, see [cloud-map-verified-access-cli.md](cloud-map-verified-access-cli.md).

## AWS Cloud Map

**Purpose**: Fully managed service discovery — register cloud resources with custom names and let applications find them dynamically via API queries or DNS, with automatic filtering of unhealthy endpoints. Eliminates manual service registries in microservices and containerized workloads.

### Namespace Types

| Namespace Type | Discovery Methods | Route 53 Integration | Typical Use Case |
|---|---|---|---|
| **HTTP namespace** | `DiscoverInstances` API only | None | API-only discovery; no DNS overhead |
| **Private DNS namespace** | `DiscoverInstances` API + DNS queries within a VPC | Creates private hosted zone automatically | ECS/EKS microservices inside a VPC |
| **Public DNS namespace** | `DiscoverInstances` API + public internet DNS | Creates public hosted zone automatically | Internet-accessible services; namespace name must be a registered domain |

### Core Concepts

| Concept | Description |
|---|---|
| **Namespace** | Logical grouping for an application's services; defines the discovery method and the DNS suffix (e.g., `prod.internal`) |
| **Service** | Template within a namespace for a specific resource type; carries DNS record config and health check settings |
| **Instance** | A registered resource endpoint (IP/port, EC2 ID, CNAME, or custom attributes); created via `RegisterInstance` |
| **Custom attributes** | Arbitrary key-value metadata attached to an instance (e.g., `version=2`, `az=us-east-1a`); filterable during discovery |
| **Health check (Route 53)** | Route 53-managed health check; unhealthy instances are automatically excluded from `DiscoverInstances` and DNS responses |
| **Custom health check** | Application-controlled; app calls `UpdateInstanceCustomHealthStatus` to mark instances healthy/unhealthy |

### Instance Attributes

| Attribute | Description |
|---|---|
| `AWS_INSTANCE_IPV4` | IPv4 address; required for A records and health checks |
| `AWS_INSTANCE_IPV6` | IPv6 address; used for AAAA records |
| `AWS_INSTANCE_PORT` | Port; required when service uses SRV record or Route 53 health check |
| `AWS_EC2_INSTANCE_ID` | EC2 instance ID; Cloud Map uses the instance's primary IP automatically |
| `AWS_ALIAS_DNS_NAME` | DNS name for CNAME-based resources |
| `AWS_INIT_HEALTH_STATUS` | Set initial health to `HEALTHY` or `UNHEALTHY` at registration (API only) |

### Key Features

- **Sub-5-second propagation**: API-based discovery updates (`DiscoverInstances`) propagate within 5 seconds — faster than DNS TTL-based propagation
- **Attribute filtering**: `DiscoverInstances` accepts `QueryParameters` to filter instances by custom attributes (e.g., only `stage=prod`)
- **ECS native integration**: ECS automatically calls `RegisterInstance` when tasks start and `DeregisterInstance` when tasks stop; no application code changes needed
- **Health-aware responses**: Only healthy instances are returned; prevents routing to degraded pods/tasks
- **IAM access control**: Fine-grained IAM policies can restrict which services can call `DiscoverInstances` on a given namespace
- **IPv6 support**: Dualstack endpoints available (`servicediscovery.<region>.api.aws`)

### Integration Patterns

```
ECS Service  →  task start  →  Cloud Map RegisterInstance (auto)
             →  task stop   →  Cloud Map DeregisterInstance (auto)
             →  Route 53 health check (optional)

Application  →  DiscoverInstances API  →  returns healthy IP:port list
             →  (or) DNS query: service.namespace  →  Route 53 resolves via private hosted zone
```

**ECS Service Discovery setup**: When creating an ECS service, set `serviceRegistries` with a Cloud Map service ARN. ECS manages the full registration lifecycle.

### CDK Example

```typescript
import * as servicediscovery from 'aws-cdk-lib/aws-servicediscovery';

const namespace = new servicediscovery.PrivateDnsNamespace(this, 'Namespace', {
  name: 'prod.internal',
  vpc,
});

const service = namespace.createService('PaymentService', {
  dnsRecordType: servicediscovery.DnsRecordType.A,
  dnsTtl: Duration.seconds(30),
  healthCheck: {
    type: servicediscovery.HealthCheckType.HTTP,
    resourcePath: '/health',
  },
});

// ECS service auto-registration
const ecsService = new ecs.FargateService(this, 'FargateService', {
  cluster,
  taskDefinition,
  cloudMapOptions: {
    cloudMapNamespace: namespace,
    name: 'payment',
  },
});
```

---

## AWS Verified Access

**Purpose**: Zero-trust, VPN-less access to corporate applications. Every request is evaluated in real time against identity and device posture policies using the Cedar policy language — no VPN client, no network-level trust grants. Users access applications via HTTPS or TCP directly through their browser or CLI tools.

### How It Works

```
User browser/tool  →  Verified Access endpoint (DNS name)
                   →  Verified Access instance evaluates Cedar policy
                       using trust context from:
                         - Identity provider (who the user is)
                         - Device trust provider (device posture)
                   →  Policy ALLOW: proxies request to application
                   →  Policy DENY: returns 403
```

### Core Concepts

| Concept | Description |
|---|---|
| **Verified Access instance** | The evaluation engine; attach trust providers here; one instance per deployment/environment |
| **Trust provider** | Source of trust context data; one identity provider + one or more device providers per instance |
| **Policy reference name** | Short name (e.g., `idc`, `okta`) used in Cedar policies to reference a trust provider's context data |
| **Verified Access group** | Logical grouping of endpoints sharing a common access policy; simplifies administration |
| **Verified Access endpoint** | Maps to a single application (load balancer, network interface, RDS instance, or CIDR range); has a generated DNS name |
| **Access policy (Cedar)** | Cedar language policy evaluated per request; can reference identity and device trust context |
| **Trust context** | Runtime data from trust providers injected into Cedar evaluation (e.g., user email, device compliance state) |
| **Signed context header** | Verified Access injects a signed `x-amzn-ava-user-context` JWT into forwarded requests; applications can use this for personalization without re-authentication |

### Trust Providers

| Type | Provider | `--trust-provider-type` | `--user/device-trust-provider-type` |
|---|---|---|---|
| **Identity** | AWS IAM Identity Center | `user` | `iam-identity-center` |
| **Identity** | Any OIDC-compatible IdP (Okta, JumpCloud, Azure AD) | `user` | `oidc` |
| **Device** | Jamf Pro | `device` | `jamf` |
| **Device** | CrowdStrike Falcon | `device` | `crowdstrike` |
| **Device** | JumpCloud | `device` | `jumpcloud` |

### Cedar Policy Basics

Cedar policies use `permit`/`forbid` statements. The `context` object contains trust data keyed by each provider's `PolicyReferenceName`.

```cedar
// Allow access if user is in the "engineering" group (IAM Identity Center)
permit(principal, action, resource)
when {
  context.idc.groups.contains("engineering")
};

// Require both: valid identity AND compliant device (CrowdStrike)
permit(principal, action, resource)
when {
  context.idc.email.endsWith("@example.com") &&
  context.crowdstrike.assessment.overall == "pass"
};

// Restrict by email domain only (OIDC provider with reference name "okta")
permit(principal, action, resource)
when {
  context.okta.email.endsWith("@corp.example.com")
};
```

### Endpoint Types

| Endpoint Type | `--endpoint-type` | Use Case |
|---|---|---|
| **Load balancer** | `load-balancer` | ALB or NLB-fronted web applications |
| **Network interface** | `network-interface` | EC2 instances, containers via ENI |
| **RDS** | `rds` | Direct database access (no SSH tunnel needed) |
| **CIDR** | `cidr` | Network-level access to IP ranges |

### Key Features

- **No VPN client required**: Users access via browser (HTTPS) or direct TCP — no VPN software to install or manage
- **Per-request evaluation**: Every request is re-evaluated; a user whose device falls out of compliance is denied immediately
- **Signed identity context**: Applications receive a signed JWT header with user claims — enables personalization without a separate auth layer
- **Centralized logging**: Access logs in OCSF (Open Cybersecurity Schema Framework) format to S3, CloudWatch Logs, or Kinesis Data Firehose; ready for SIEM ingestion
- **FIPS 140-2**: Optional FIPS mode on the Verified Access instance for regulated workloads
- **TCP support**: Non-HTTP workloads (SSH, RDP, Git over SSH, database clients) supported via TCP endpoint type

### Integration Patterns

```
IAM Identity Center SSO  →  trust provider (user)
CrowdStrike Falcon sensor →  trust provider (device)
Both attached to Verified Access instance
  →  group policy: require identity + device compliance
  →  endpoints: internal ALB (web app), RDS instance (database)

Result: users reach internal apps via browser/psql without VPN
        every request re-checks identity + device posture
```

### CDK Example

```typescript
import * as ec2 from 'aws-cdk-lib/aws-ec2';

// Verified Access resources are in the ec2 L1 constructs (CfnVerifiedAccess*)
const vaiInstance = new ec2.CfnVerifiedAccessInstance(this, 'VAInstance', {
  description: 'Production Verified Access',
  tags: [{ key: 'Environment', value: 'production' }],
});

const trustProvider = new ec2.CfnVerifiedAccessTrustProvider(this, 'TrustProvider', {
  trustProviderType: 'user',
  userTrustProviderType: 'iam-identity-center',
  policyReferenceName: 'idc',
  description: 'IAM Identity Center',
  tags: [{ key: 'Environment', value: 'production' }],
});

const group = new ec2.CfnVerifiedAccessGroup(this, 'VAGroup', {
  verifiedAccessInstanceId: vaiInstance.attrVerifiedAccessInstanceId,
  policyEnabled: true,
  policyDocument: `
    permit(principal, action, resource)
    when { context.idc.groups.contains("engineering") };
  `,
  description: 'Engineering applications',
});

const endpoint = new ec2.CfnVerifiedAccessEndpoint(this, 'VAEndpoint', {
  verifiedAccessGroupId: group.attrVerifiedAccessGroupId,
  endpointType: 'load-balancer',
  attachmentType: 'vpc',
  domainCertificateArn: cert.certificateArn,
  applicationDomain: 'internal.example.com',
  endpointDomainPrefix: 'myapp',
  securityGroupIds: [sg.securityGroupId],
  loadBalancerOptions: {
    protocol: 'https',
    port: 443,
    loadBalancerArn: alb.loadBalancerArn,
    subnetIds: vpc.privateSubnets.map(s => s.subnetId),
  },
});
```
