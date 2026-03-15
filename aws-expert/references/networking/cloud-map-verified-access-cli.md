# AWS Cloud Map & Verified Access — CLI Reference
For service concepts, see [cloud-map-verified-access-capabilities.md](cloud-map-verified-access-capabilities.md).

## AWS Cloud Map (`aws servicediscovery`)

```bash
# --- Namespaces ---

# HTTP namespace (API discovery only, no DNS)
aws servicediscovery create-http-namespace \
  --name prod.internal \
  --tags Key=Environment,Value=production

# Private DNS namespace (API + DNS within a VPC)
aws servicediscovery create-private-dns-namespace \
  --name prod.internal \
  --vpc vpc-12345678 \
  --tags Key=Environment,Value=production

# Public DNS namespace (API + public DNS; name must be a registered domain)
aws servicediscovery create-public-dns-namespace \
  --name discovery.example.com \
  --tags Key=Environment,Value=production

# Note: namespace creation is async; poll for completion
aws servicediscovery get-operation --operation-id <operation-id>

aws servicediscovery list-namespaces
aws servicediscovery get-namespace --id ns-xxxxxxxxxx
aws servicediscovery delete-namespace --id ns-xxxxxxxxxx

# --- Services ---

# Create a service with A record + Route 53 health check
aws servicediscovery create-service \
  --name payment \
  --namespace-id ns-xxxxxxxxxx \
  --dns-config 'NamespaceId=ns-xxxxxxxxxx,RoutingPolicy=MULTIVALUE,DnsRecords=[{Type=A,TTL=30}]' \
  --health-check-custom-config FailureThreshold=1

# Create a service with Route 53 HTTP health check
aws servicediscovery create-service \
  --name orders \
  --namespace-id ns-xxxxxxxxxx \
  --dns-config 'NamespaceId=ns-xxxxxxxxxx,RoutingPolicy=WEIGHTED,DnsRecords=[{Type=A,TTL=60}]' \
  --health-check-config 'Type=HTTP,ResourcePath=/health,FailureThreshold=3'

# Service for HTTP namespace (no DNS config needed)
aws servicediscovery create-service \
  --name catalog \
  --namespace-id ns-xxxxxxxxxx

aws servicediscovery list-services
aws servicediscovery get-service --id srv-xxxxxxxxxx
aws servicediscovery delete-service --id srv-xxxxxxxxxx

# Update service TTL or health check config
aws servicediscovery update-service \
  --id srv-xxxxxxxxxx \
  --service 'DnsConfig={DnsRecords=[{Type=A,TTL=15}]}'

# --- Instances ---

# Register an IP-based instance (most common for containers/ECS tasks)
aws servicediscovery register-instance \
  --service-id srv-xxxxxxxxxx \
  --instance-id task-abc123 \
  --attributes \
    AWS_INSTANCE_IPV4=10.0.1.45,\
    AWS_INSTANCE_PORT=8080,\
    version=2,\
    stage=prod

# Register an EC2 instance
aws servicediscovery register-instance \
  --service-id srv-xxxxxxxxxx \
  --instance-id i-1234567890abcdef0 \
  --attributes \
    AWS_EC2_INSTANCE_ID=i-1234567890abcdef0,\
    AWS_INSTANCE_PORT=80

# Note: register-instance is async
aws servicediscovery get-operation --operation-id <operation-id>

aws servicediscovery list-instances --service-id srv-xxxxxxxxxx
aws servicediscovery get-instance --service-id srv-xxxxxxxxxx --instance-id task-abc123

# Deregister instance (also async)
aws servicediscovery deregister-instance \
  --service-id srv-xxxxxxxxxx \
  --instance-id task-abc123

# Update custom health status (for services using custom health checks)
aws servicediscovery update-instance-custom-health-status \
  --service-id srv-xxxxxxxxxx \
  --instance-id task-abc123 \
  --status HEALTHY   # or UNHEALTHY

# --- Discovery ---

# Discover healthy instances for a service (API-based, sub-5s propagation)
aws servicediscovery discover-instances \
  --namespace-name prod.internal \
  --service-name payment

# Discover with attribute filter (only prod instances running v2)
aws servicediscovery discover-instances \
  --namespace-name prod.internal \
  --service-name payment \
  --query-parameters stage=prod,version=2 \
  --health-status HEALTHY

# Discover unhealthy instances (for debugging)
aws servicediscovery discover-instances \
  --namespace-name prod.internal \
  --service-name payment \
  --health-status UNHEALTHY

# Check instance health statuses
aws servicediscovery get-instances-health-status \
  --service-id srv-xxxxxxxxxx

# --- Tagging ---
aws servicediscovery tag-resource \
  --resource-arn arn:aws:servicediscovery:us-east-1:123456789012:namespace/ns-xxxxxxxxxx \
  --tags Key=CostCenter,Value=platform

aws servicediscovery list-tags-for-resource \
  --resource-arn arn:aws:servicediscovery:us-east-1:123456789012:namespace/ns-xxxxxxxxxx

aws servicediscovery untag-resource \
  --resource-arn arn:aws:servicediscovery:us-east-1:123456789012:namespace/ns-xxxxxxxxxx \
  --tag-keys CostCenter
```

---

## AWS Verified Access (`aws ec2 *-verified-access-*`)

```bash
# --- Verified Access Instances ---

# Create an instance (the top-level evaluation engine)
aws ec2 create-verified-access-instance \
  --description "Production Verified Access" \
  --tag-specifications \
    'ResourceType=verified-access-instance,Tags=[{Key=Environment,Value=production}]'

aws ec2 describe-verified-access-instances
aws ec2 describe-verified-access-instances \
  --verified-access-instance-ids vai-0ce000c0b7643abea

aws ec2 modify-verified-access-instance \
  --verified-access-instance-id vai-0ce000c0b7643abea \
  --description "Updated description"

aws ec2 delete-verified-access-instance \
  --verified-access-instance-id vai-0ce000c0b7643abea

# --- Trust Providers ---

# Create identity trust provider — IAM Identity Center
aws ec2 create-verified-access-trust-provider \
  --trust-provider-type user \
  --user-trust-provider-type iam-identity-center \
  --policy-reference-name idc \
  --description "IAM Identity Center" \
  --tag-specifications \
    'ResourceType=verified-access-trust-provider,Tags=[{Key=Environment,Value=production}]'

# Create identity trust provider — OIDC (Okta, JumpCloud, Azure AD, etc.)
aws ec2 create-verified-access-trust-provider \
  --trust-provider-type user \
  --user-trust-provider-type oidc \
  --policy-reference-name okta \
  --oidc-options '{
    "Issuer": "https://your-org.okta.com",
    "AuthorizationEndpoint": "https://your-org.okta.com/oauth2/v1/authorize",
    "TokenEndpoint": "https://your-org.okta.com/oauth2/v1/token",
    "UserInfoEndpoint": "https://your-org.okta.com/oauth2/v1/userinfo",
    "ClientId": "0oa1b2c3d4e5f6g7h8i9",
    "ClientSecret": "secret",
    "Scope": "openid email groups"
  }' \
  --description "Okta OIDC"

# Create device trust provider — CrowdStrike
aws ec2 create-verified-access-trust-provider \
  --trust-provider-type device \
  --device-trust-provider-type crowdstrike \
  --policy-reference-name crowdstrike \
  --device-options '{"TenantId": "your-tenant-id"}' \
  --description "CrowdStrike Falcon"

# Create device trust provider — Jamf Pro
aws ec2 create-verified-access-trust-provider \
  --trust-provider-type device \
  --device-trust-provider-type jamf \
  --policy-reference-name jamf \
  --device-options '{"PublicSigningKeyUrl": "https://your-jamf.jamfcloud.com/api/v1/verified-access/signing-key"}' \
  --description "Jamf Pro"

# Create device trust provider — JumpCloud
aws ec2 create-verified-access-trust-provider \
  --trust-provider-type device \
  --device-trust-provider-type jumpcloud \
  --policy-reference-name jumpcloud \
  --device-options '{"PublicSigningKeyUrl": "https://console.jumpcloud.com/api/v2/verified-access/signing-key"}' \
  --description "JumpCloud"

# Attach trust provider to instance
aws ec2 attach-verified-access-trust-provider \
  --verified-access-instance-id vai-0ce000c0b7643abea \
  --verified-access-trust-provider-id vatp-0bb32de759a3e19e7

# Detach trust provider from instance
aws ec2 detach-verified-access-trust-provider \
  --verified-access-instance-id vai-0ce000c0b7643abea \
  --verified-access-trust-provider-id vatp-0bb32de759a3e19e7

aws ec2 describe-verified-access-trust-providers
aws ec2 delete-verified-access-trust-provider \
  --verified-access-trust-provider-id vatp-0bb32de759a3e19e7

# --- Groups ---

# Create a group with a Cedar access policy
aws ec2 create-verified-access-group \
  --verified-access-instance-id vai-0ce000c0b7643abea \
  --description "Engineering applications" \
  --policy-enabled \
  --policy-document 'permit(principal, action, resource) when { context.idc.groups.contains("engineering") };' \
  --tag-specifications \
    'ResourceType=verified-access-group,Tags=[{Key=Team,Value=engineering}]'

# Create a group requiring identity + device compliance
aws ec2 create-verified-access-group \
  --verified-access-instance-id vai-0ce000c0b7643abea \
  --description "High-security applications" \
  --policy-enabled \
  --policy-document 'permit(principal, action, resource) when {
    context.idc.email.endsWith("@corp.example.com") &&
    context.crowdstrike.assessment.overall == "pass"
  };'

aws ec2 describe-verified-access-groups
aws ec2 describe-verified-access-groups \
  --verified-access-group-ids vagr-0dbe967baf14b7235

# Update group policy
aws ec2 modify-verified-access-group-policy \
  --verified-access-group-id vagr-0dbe967baf14b7235 \
  --policy-enabled \
  --policy-document 'permit(principal, action, resource) when { context.idc.groups.contains("engineering") };'

aws ec2 delete-verified-access-group \
  --verified-access-group-id vagr-0dbe967baf14b7235

# --- Endpoints ---

# Create load-balancer endpoint (HTTPS via ALB)
aws ec2 create-verified-access-endpoint \
  --verified-access-group-id vagr-0dbe967baf14b7235 \
  --endpoint-type load-balancer \
  --attachment-type vpc \
  --domain-certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/eb065ea0-EXAMPLE \
  --application-domain internal.example.com \
  --endpoint-domain-prefix myapp \
  --security-group-ids sg-12345678 \
  --load-balancer-options \
    'Protocol=https,Port=443,LoadBalancerArn=arn:aws:elasticloadbalancing:...,SubnetIds=["subnet-aaa","subnet-bbb"]' \
  --tag-specifications \
    'ResourceType=verified-access-endpoint,Tags=[{Key=App,Value=my-app}]'

# Create network-interface endpoint (direct ENI — EC2 instance)
aws ec2 create-verified-access-endpoint \
  --verified-access-group-id vagr-0dbe967baf14b7235 \
  --endpoint-type network-interface \
  --attachment-type vpc \
  --domain-certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/eb065ea0-EXAMPLE \
  --application-domain internal.example.com \
  --endpoint-domain-prefix myservice \
  --security-group-ids sg-12345678 \
  --network-interface-options \
    'NetworkInterfaceId=eni-0aec70418c8d87a0f,Protocol=https,Port=443'

# Create RDS endpoint (direct database access)
aws ec2 create-verified-access-endpoint \
  --verified-access-group-id vagr-0dbe967baf14b7235 \
  --endpoint-type rds \
  --attachment-type vpc \
  --security-group-ids sg-12345678 \
  --rds-options \
    'Protocol=tcp,Port=5432,RdsDbInstanceArn=arn:aws:rds:...,SubnetIds=["subnet-aaa","subnet-bbb"]'

# Create CIDR endpoint (IP range access)
aws ec2 create-verified-access-endpoint \
  --verified-access-group-id vagr-0dbe967baf14b7235 \
  --endpoint-type cidr \
  --attachment-type vpc \
  --security-group-ids sg-12345678 \
  --cidr-options \
    'Protocol=tcp,Cidr=10.0.0.0/8,SubnetIds=["subnet-aaa","subnet-bbb"],PortRanges=[{"FromPort":22,"ToPort":22}]'

aws ec2 describe-verified-access-endpoints
aws ec2 describe-verified-access-endpoints \
  --verified-access-endpoint-ids vae-0dbe967baf14b7235

# Update endpoint-level policy (overrides group policy for this endpoint)
aws ec2 modify-verified-access-endpoint-policy \
  --verified-access-endpoint-id vae-0dbe967baf14b7235 \
  --policy-enabled \
  --policy-document 'permit(principal, action, resource) when { context.idc.email == "admin@example.com" };'

aws ec2 delete-verified-access-endpoint \
  --verified-access-endpoint-id vae-0dbe967baf14b7235

# --- Logging ---

# Enable access logging to CloudWatch Logs
aws ec2 modify-verified-access-instance-logging-configuration \
  --verified-access-instance-id vai-0ce000c0b7643abea \
  --access-logs '{
    "CloudWatchLogs": {
      "Enabled": true,
      "LogGroup": "/aws/verified-access/prod"
    }
  }'

# Enable access logging to S3
aws ec2 modify-verified-access-instance-logging-configuration \
  --verified-access-instance-id vai-0ce000c0b7643abea \
  --access-logs '{
    "S3": {
      "Enabled": true,
      "BucketName": "my-va-logs",
      "Prefix": "verified-access/"
    }
  }'

aws ec2 describe-verified-access-instance-logging-configurations \
  --verified-access-instance-ids vai-0ce000c0b7643abea
```
