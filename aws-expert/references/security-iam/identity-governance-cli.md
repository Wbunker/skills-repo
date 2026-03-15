# Identity, Governance & Threat Data — CLI Reference
For service concepts, see [identity-governance-capabilities.md](identity-governance-capabilities.md).

## AWS Directory Service

```bash
# --- Create directories ---
# Create AWS Managed Microsoft AD (Enterprise Edition)
aws ds create-microsoft-ad \
  --name corp.example.com \
  --short-name CORP \
  --password 'Str0ng!Password' \
  --edition Enterprise \
  --vpc-settings VpcId=vpc-xxxxxxxx,SubnetIds=subnet-aaaaaaaa,subnet-bbbbbbbb \
  --description "Production Managed AD"

# Create AWS Managed Microsoft AD (Standard Edition)
aws ds create-microsoft-ad \
  --name corp.example.com \
  --short-name CORP \
  --password 'Str0ng!Password' \
  --edition Standard \
  --vpc-settings VpcId=vpc-xxxxxxxx,SubnetIds=subnet-aaaaaaaa,subnet-bbbbbbbb

# Create AD Connector (proxy to on-premises AD)
aws ds create-ad-connector \
  --name corp.example.com \
  --short-name CORP \
  --password 'ServiceAccountPassword' \
  --size Large \
  --vpc-settings VpcId=vpc-xxxxxxxx,SubnetIds=subnet-aaaaaaaa,subnet-bbbbbbbb \
  --connect-settings CustomerDnsIps=10.0.1.10,10.0.1.11,CustomerUserName=svc-aws-connector

# Create Simple AD
aws ds create-directory \
  --name corp.example.com \
  --short-name CORP \
  --password 'AdminPassword' \
  --size Large \
  --vpc-settings VpcId=vpc-xxxxxxxx,SubnetIds=subnet-aaaaaaaa,subnet-bbbbbbbb

# --- Describe and manage ---
aws ds describe-directories
aws ds describe-directories \
  --directory-ids d-xxxxxxxxxx  # specific directory

# Check directory status (wait for Active state after creation)
aws ds describe-directories \
  --directory-ids d-xxxxxxxxxx \
  --query 'DirectoryDescriptions[0].Stage'

aws ds delete-directory --directory-id d-xxxxxxxxxx

# --- Trust relationships (Managed AD only) ---
# Create a trust with an on-premises domain
aws ds create-trust \
  --directory-id d-xxxxxxxxxx \
  --remote-domain-name onprem.example.com \
  --trust-password 'TrustPassword' \
  --trust-direction Two-Way \
  --trust-type Forest \
  --conditional-forwarder-ip-addrs 10.1.1.1 10.1.1.2

aws ds describe-trusts --directory-id d-xxxxxxxxxx

aws ds verify-trust --trust-id t-xxxxxxxxxxxxxxxxx

aws ds delete-trust \
  --trust-id t-xxxxxxxxxxxxxxxxx \
  --delete-associated-conditional-forwarder

# --- Snapshots ---
aws ds create-snapshot \
  --directory-id d-xxxxxxxxxx \
  --name "pre-migration-snapshot"

aws ds describe-snapshots --directory-id d-xxxxxxxxxx

aws ds restore-from-snapshot --snapshot-id s-xxxxxxxxxxxxxxxxx

aws ds delete-snapshot --snapshot-id s-xxxxxxxxxxxxxxxxx

# --- Domain join (EC2 seamless join) ---
aws ds create-computer \
  --directory-id d-xxxxxxxxxx \
  --computer-name MyServer \
  --password 'ComputerPassword' \
  --organizational-unit-distinguished-name 'OU=Computers,DC=corp,DC=example,DC=com'

# --- SSO and alias ---
aws ds enable-sso --directory-id d-xxxxxxxxxx
aws ds disable-sso --directory-id d-xxxxxxxxxx

aws ds create-alias \
  --directory-id d-xxxxxxxxxx \
  --alias my-corp-directory

# --- LDAPS ---
aws ds list-certificates --directory-id d-xxxxxxxxxx
aws ds register-certificate \
  --directory-id d-xxxxxxxxxx \
  --certificate-data file://ldaps-cert.pem \
  --type SubCA

aws ds enable-ldaps \
  --directory-id d-xxxxxxxxxx \
  --type Client  # Client = LDAPS for LDAP clients

aws ds describe-ldaps-settings --directory-id d-xxxxxxxxxx

# --- Multi-region (Enterprise AD only) ---
aws ds add-region \
  --directory-id d-xxxxxxxxxx \
  --region-name eu-west-1 \
  --vpc-settings VpcId=vpc-yyyyyyyy,SubnetIds=subnet-cccccccc,subnet-dddddddd

aws ds describe-regions --directory-id d-xxxxxxxxxx

aws ds remove-region \
  --directory-id d-xxxxxxxxxx \
  --region-name eu-west-1

# --- Tags ---
aws ds add-tags-to-resource \
  --resource-id d-xxxxxxxxxx \
  --tags Key=Environment,Value=Production

aws ds list-tags-for-resource --resource-id d-xxxxxxxxxx
```

---

## AWS Resource Access Manager (AWS RAM)

```bash
# --- Initial setup: enable organization-level sharing ---
# Run once from the management account (required before sharing with OUs)
aws ram enable-sharing-with-aws-organization

# --- Create a resource share ---
# Share a VPC subnet with an OU (no invitation needed within org)
aws ram create-resource-share \
  --name "shared-subnets-prod" \
  --principals arn:aws:organizations::123456789012:ou/o-aaaaaaaaaa/ou-bbbb-cccccccc \
  --resource-arns \
    arn:aws:ec2:us-east-1:123456789012:subnet/subnet-aaaaaaaa \
    arn:aws:ec2:us-east-1:123456789012:subnet/subnet-bbbbbbbb \
  --tags Key=Purpose,Value=NetworkSharing

# Share a Transit Gateway with the entire organization
aws ram create-resource-share \
  --name "shared-transit-gateway" \
  --principals arn:aws:organizations::123456789012:organization/o-aaaaaaaaaa \
  --resource-arns arn:aws:ec2:us-east-1:123456789012:transit-gateway/tgw-xxxxxxxxxxxxxxxxx \
  --allow-external-principals false

# Share with a specific external account (invitation required)
aws ram create-resource-share \
  --name "shared-private-ca" \
  --principals 987654321098 \
  --resource-arns arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/xxx \
  --allow-external-principals

# --- Manage existing shares ---
aws ram get-resource-shares \
  --resource-owner SELF  # shares you created
aws ram get-resource-shares \
  --resource-owner OTHER-ACCOUNTS  # shares you received

aws ram update-resource-share \
  --resource-share-arn arn:aws:ram:us-east-1:123456789012:resource-share/xxx \
  --name "shared-subnets-prod-updated" \
  --allow-external-principals false

aws ram delete-resource-share \
  --resource-share-arn arn:aws:ram:us-east-1:123456789012:resource-share/xxx

# --- Add / remove resources from a share ---
aws ram associate-resource-share \
  --resource-share-arn arn:aws:ram:us-east-1:123456789012:resource-share/xxx \
  --resource-arns arn:aws:ec2:us-east-1:123456789012:subnet/subnet-cccccccc

aws ram disassociate-resource-share \
  --resource-share-arn arn:aws:ram:us-east-1:123456789012:resource-share/xxx \
  --resource-arns arn:aws:ec2:us-east-1:123456789012:subnet/subnet-cccccccc

# --- Add / remove principals from a share ---
aws ram associate-resource-share \
  --resource-share-arn arn:aws:ram:us-east-1:123456789012:resource-share/xxx \
  --principals 111111111111

aws ram disassociate-resource-share \
  --resource-share-arn arn:aws:ram:us-east-1:123456789012:resource-share/xxx \
  --principals 111111111111

# --- Invitations (for external accounts outside org) ---
# Consumer account: list pending invitations
aws ram get-resource-share-invitations

# Consumer account: accept an invitation
aws ram accept-resource-share-invitation \
  --resource-share-invitation-arn arn:aws:ram:us-east-1:123456789012:resource-share-invitation/xxx

# Consumer account: reject an invitation
aws ram reject-resource-share-invitation \
  --resource-share-invitation-arn arn:aws:ram:us-east-1:123456789012:resource-share-invitation/xxx

# --- Discover shared resources (consumer view) ---
aws ram list-resources \
  --resource-owner OTHER-ACCOUNTS  # resources shared with me

aws ram list-principals \
  --resource-owner SELF  # principals who have access to my shared resources

aws ram list-resource-share-permissions \
  --resource-share-arn arn:aws:ram:us-east-1:123456789012:resource-share/xxx

# --- Permissions ---
# List available managed permissions for a resource type
aws ram list-permissions \
  --resource-type AWS::EC2::Subnet

aws ram get-permission \
  --permission-arn arn:aws:ram::aws:permission/AWSRAMDefaultPermissionSubnet

# Attach a custom permission to a resource share
aws ram associate-resource-share-permission \
  --resource-share-arn arn:aws:ram:us-east-1:123456789012:resource-share/xxx \
  --permission-arn arn:aws:ram::aws:permission/AWSRAMDefaultPermissionSubnet \
  --replace  # replaces existing permission for this resource type

# --- Tags ---
aws ram tag-resource \
  --resource-share-arn arn:aws:ram:us-east-1:123456789012:resource-share/xxx \
  --tags Key=Team,Value=Networking

aws ram untag-resource \
  --resource-share-arn arn:aws:ram:us-east-1:123456789012:resource-share/xxx \
  --tag-keys Team

aws ram list-resource-tags \
  --resource-share-arn arn:aws:ram:us-east-1:123456789012:resource-share/xxx
```

---

## Amazon Security Lake

```bash
# --- Enable Security Lake (delegated admin account or management account) ---
# Enable in specific regions (creates S3 bucket, Glue catalog, Lake Formation config)
aws securitylake create-data-lake \
  --configurations \
    '[{
      "region": "us-east-1",
      "encryptionConfiguration": {"kmsKeyId": "alias/security-lake-key"},
      "lifecycleConfiguration": {
        "transitions": [{"days": 60, "storageClass": "ONEZONE_IA"}],
        "expiration": {"days": 365}
      },
      "replicationConfiguration": {
        "regions": ["us-west-2"],
        "roleArn": "arn:aws:iam::123456789012:role/SecurityLakeReplication"
      }
    }]' \
  --meta-store-manager-role-arn arn:aws:iam::123456789012:role/SecurityLakeMetaStoreManager

aws securitylake list-data-lakes

aws securitylake get-data-lake-sources \
  --accounts 123456789012

# Update retention / replication settings
aws securitylake update-data-lake \
  --configurations \
    '[{
      "region": "us-east-1",
      "lifecycleConfiguration": {
        "transitions": [{"days": 90, "storageClass": "GLACIER"}],
        "expiration": {"days": 730}
      }
    }]'

aws securitylake delete-data-lake \
  --regions us-east-1

# --- Enable AWS native log sources ---
# Enable CloudTrail management events and VPC Flow Logs for specific accounts
aws securitylake create-aws-log-source \
  --sources \
    '[{
      "sourceName": "CLOUD_TRAIL_MGMT",
      "regions": ["us-east-1", "us-west-2"],
      "accounts": ["123456789012", "234567890123"]
    },
    {
      "sourceName": "VPC_FLOW",
      "regions": ["us-east-1"],
      "accounts": ["123456789012"]
    }]'

# Available source names: CLOUD_TRAIL_MGMT, VPC_FLOW, SH_FINDINGS, EKS_AUDIT,
#                          ROUTE53, WAF, LAMBDA_EXECUTION, S3_DATA

aws securitylake list-log-sources

aws securitylake delete-aws-log-source \
  --sources \
    '[{
      "sourceName": "VPC_FLOW",
      "regions": ["us-east-1"],
      "accounts": ["123456789012"]
    }]'

# --- Custom log sources (third-party / on-premises) ---
aws securitylake create-custom-log-source \
  --source-name MyFirewall \
  --event-classes '["NETWORK_ACTIVITY"]' \  # OCSF event class
  --configuration \
    'crawlerConfiguration={roleArn=arn:aws:iam::123456789012:role/SecurityLakeCrawler},
     providerIdentity={externalId=my-provider,principal=arn:aws:iam::555555555555:root}'

aws securitylake delete-custom-log-source --source-name MyFirewall

# --- Multi-account via Organizations ---
aws securitylake create-data-lake-organization-configuration \
  --auto-enable-new-account \
    '[{
      "region": "us-east-1",
      "sources": [
        {"sourceName": "CLOUD_TRAIL_MGMT"},
        {"sourceName": "VPC_FLOW"},
        {"sourceName": "SH_FINDINGS"}
      ]
    }]'

aws securitylake list-data-lake-organization-configurations

aws securitylake delete-data-lake-organization-configuration \
  --auto-enable-new-account \
    '[{"region": "us-east-1", "sources": [{"sourceName": "CLOUD_TRAIL_MGMT"}]}]'

# --- Subscribers (consumers of Security Lake data) ---
# Create a subscriber with S3 data access (e.g., for Athena or SIEM)
aws securitylake create-subscriber \
  --subscriber-name "security-team-athena" \
  --subscriber-identity \
    'principal=arn:aws:iam::999999999999:role/SecurityAnalystRole,externalId=unique-ext-id' \
  --sources \
    '[{"awsLogSource": {"sourceName": "CLOUD_TRAIL_MGMT", "sourceVersion": "2.0"}},
      {"awsLogSource": {"sourceName": "VPC_FLOW", "sourceVersion": "1.0"}}]' \
  --access-types S3

# Create a subscriber with notification (SQS) for event-driven ingestion
aws securitylake create-subscriber \
  --subscriber-name "siem-connector" \
  --subscriber-identity \
    'principal=arn:aws:iam::888888888888:role/SiemRole,externalId=siem-ext-id' \
  --sources \
    '[{"awsLogSource": {"sourceName": "SH_FINDINGS", "sourceVersion": "1.0"}}]' \
  --access-types LAKEFORMATION

# Create subscriber notification (webhook / SQS)
aws securitylake create-subscriber-notification \
  --subscriber-id <subscriber-id> \
  --configuration 'sqsNotificationConfiguration={}'  # SQS queue created automatically

aws securitylake list-subscribers

aws securitylake get-subscriber --subscriber-id <subscriber-id>

aws securitylake update-subscriber \
  --subscriber-id <subscriber-id> \
  --subscriber-name "siem-connector-updated" \
  --sources \
    '[{"awsLogSource": {"sourceName": "SH_FINDINGS", "sourceVersion": "1.0"}},
      {"awsLogSource": {"sourceName": "VPC_FLOW", "sourceVersion": "1.0"}}]'

aws securitylake delete-subscriber --subscriber-id <subscriber-id>

# --- Exception and status monitoring ---
aws securitylake list-data-lake-exceptions \
  --regions us-east-1
aws securitylake get-data-lake-exception-subscription
```
