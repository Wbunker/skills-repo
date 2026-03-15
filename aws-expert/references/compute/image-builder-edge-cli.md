# Image Builder / Edge Compute / SAR — CLI Reference

For service concepts, see [image-builder-edge-capabilities.md](image-builder-edge-capabilities.md).

## Amazon EC2 Image Builder

```bash
# --- Components ---
# List available AWS-managed components
aws imagebuilder list-components --owner AMAZON --output table

# List your own components
aws imagebuilder list-components --owner Self

# Create a custom build component from a local YAML document
aws imagebuilder create-component \
  --name install-nginx \
  --semantic-version 1.0.0 \
  --platform Linux \
  --data file://component-nginx.yaml

# Get component details
aws imagebuilder get-component \
  --component-build-version-arn arn:aws:imagebuilder:us-east-1:123456789012:component/install-nginx/1.0.0/1

# --- Image Recipes ---
# Create an image recipe (AMI output)
aws imagebuilder create-image-recipe \
  --name my-hardened-al2023 \
  --semantic-version 1.0.0 \
  --parent-image arn:aws:imagebuilder:us-east-1:aws:image/amazon-linux-2023-x86/x.x.x \
  --components '[
    {"componentArn": "arn:aws:imagebuilder:us-east-1:aws:component/update-linux/x.x.x"},
    {"componentArn": "arn:aws:imagebuilder:us-east-1:123456789012:component/install-nginx/1.0.0/1"}
  ]' \
  --block-device-mappings '[{"deviceName":"/dev/xvda","ebs":{"volumeSize":30,"volumeType":"gp3","encrypted":true}}]'

aws imagebuilder list-image-recipes --owner Self
aws imagebuilder get-image-recipe \
  --image-recipe-arn arn:aws:imagebuilder:us-east-1:123456789012:image-recipe/my-hardened-al2023/1.0.0

# --- Container Recipes ---
aws imagebuilder create-container-recipe \
  --name my-app-container \
  --semantic-version 1.0.0 \
  --container-type DOCKER \
  --parent-image arn:aws:imagebuilder:us-east-1:aws:image/amazon-linux-2023-x86/x.x.x \
  --target-repository '{"repositoryName":"my-app","service":"ECR"}' \
  --components '[{"componentArn":"arn:aws:imagebuilder:us-east-1:aws:component/update-linux/x.x.x"}]'

aws imagebuilder list-container-recipes --owner Self

# --- Infrastructure Configuration ---
# Create infra config (defines what EC2 resources Image Builder uses during build)
aws imagebuilder create-infrastructure-configuration \
  --name my-build-infra \
  --instance-profile-name EC2InstanceProfileForImageBuilder \
  --instance-types '["m5.large","m5.xlarge"]' \
  --subnet-id subnet-0abc12345def67890 \
  --security-group-ids '["sg-0abc12345def67890"]' \
  --terminate-instance-on-failure true \
  --logging '{"s3Logs":{"s3BucketName":"my-imagebuilder-logs","s3KeyPrefix":"build-logs/"}}'

aws imagebuilder list-infrastructure-configurations

# --- Distribution Configuration ---
# Create distribution config (defines where and how to share the final image)
aws imagebuilder create-distribution-configuration \
  --name my-distribution \
  --distributions '[{
    "region": "us-east-1",
    "amiDistributionConfiguration": {
      "name": "my-hardened-al2023-{{ imagebuilder:buildDate }}",
      "description": "Hardened AL2023 image",
      "amiTags": {"Project": "platform", "Environment": "prod"},
      "launchPermission": {
        "organizationArns": ["arn:aws:organizations::123456789012:organization/o-exampleorgid"]
      }
    }
  },{
    "region": "eu-west-1",
    "amiDistributionConfiguration": {
      "name": "my-hardened-al2023-{{ imagebuilder:buildDate }}"
    }
  }]'

# --- Image Pipelines ---
# Create a pipeline
aws imagebuilder create-image-pipeline \
  --name my-hardened-al2023-pipeline \
  --image-recipe-arn arn:aws:imagebuilder:us-east-1:123456789012:image-recipe/my-hardened-al2023/1.0.0 \
  --infrastructure-configuration-arn arn:aws:imagebuilder:us-east-1:123456789012:infrastructure-configuration/my-build-infra \
  --distribution-configuration-arn arn:aws:imagebuilder:us-east-1:123456789012:distribution-configuration/my-distribution \
  --schedule '{"scheduleExpression":"cron(0 4 ? * MON *)","pipelineExecutionStartCondition":"EXPRESSION_MATCH_AND_DEPENDENCY_UPDATES_AVAILABLE"}' \
  --image-scanning-configuration '{"imageScanningEnabled":true}' \
  --status ENABLED

# List and manage pipelines
aws imagebuilder list-image-pipelines
aws imagebuilder get-image-pipeline \
  --image-pipeline-arn arn:aws:imagebuilder:us-east-1:123456789012:image-pipeline/my-hardened-al2023-pipeline

# Trigger a pipeline manually
aws imagebuilder start-image-pipeline-execution \
  --image-pipeline-arn arn:aws:imagebuilder:us-east-1:123456789012:image-pipeline/my-hardened-al2023-pipeline

# --- Images (View Results) ---
aws imagebuilder list-images --owner Self
aws imagebuilder get-image \
  --image-build-version-arn arn:aws:imagebuilder:us-east-1:123456789012:image/my-hardened-al2023/1.0.0/1

# List all build versions for an image
aws imagebuilder list-image-build-versions \
  --image-version-arn arn:aws:imagebuilder:us-east-1:123456789012:image/my-hardened-al2023/1.0.0

# --- Image Scanning Findings ---
aws imagebuilder list-image-scan-findings \
  --filters '{"name":"imageBuildVersionArn","values":["arn:aws:imagebuilder:us-east-1:123456789012:image/my-hardened-al2023/1.0.0/1"]}'

# Aggregate scan findings across images
aws imagebuilder list-image-scan-finding-aggregations \
  --filter '{"name":"imageBuildVersionArn","values":["arn:aws:imagebuilder:us-east-1:123456789012:image/my-hardened-al2023/1.0.0/1"]}'

# --- Lifecycle Policies ---
# Create a lifecycle policy to delete images older than 90 days (keep last 5)
aws imagebuilder create-lifecycle-policy \
  --name retire-old-images \
  --execution-role arn:aws:iam::123456789012:role/EC2ImageBuilderLifecycleExecutionRole \
  --resource-type AMI_IMAGE \
  --policy-details '[{
    "action": {"type": "DELETE"},
    "filter": {
      "type": "AGE",
      "value": 90,
      "unit": "DAYS",
      "retainAtLeast": 5
    }
  }]' \
  --resource-selection '{"recipes":[{"name":"my-hardened-al2023","semanticVersion":"1.0.0"}]}'

aws imagebuilder list-lifecycle-policies
```

---

## AWS Local Zones

```bash
# --- Opt-In to Local Zones ---
# List all available Local Zones (and their opt-in status)
aws ec2 describe-availability-zones \
  --all-availability-zones \
  --filters Name=zone-type,Values=local-zone \
  --query 'AvailabilityZones[*].{Name:ZoneName,State:State,OptIn:OptInStatus,ParentZone:ParentZoneName}' \
  --output table

# Opt in to a specific Local Zone
aws ec2 modify-availability-zone-group \
  --group-name us-west-2-lax-1 \
  --opt-in-status opted-in

# Verify opt-in
aws ec2 describe-availability-zones \
  --filters Name=zone-type,Values=local-zone Name=state,Values=available \
  --query 'AvailabilityZones[*].{Name:ZoneName,OptIn:OptInStatus}'

# --- Create VPC Resources in a Local Zone ---
# Create a subnet in the Local Zone (uses the parent Region's VPC)
aws ec2 create-subnet \
  --vpc-id vpc-0abc12345def67890 \
  --cidr-block 10.0.100.0/24 \
  --availability-zone us-west-2-lax-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=lax-subnet}]'

# Launch an EC2 instance in the Local Zone subnet
aws ec2 run-instances \
  --image-id ami-0abc12345def67890 \
  --instance-type m5.large \
  --subnet-id subnet-0abc12345def67890 \
  --key-name my-key \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=lax-app-server}]'

# --- List Supported Instance Types in a Local Zone ---
aws ec2 describe-instance-type-offerings \
  --location-type availability-zone \
  --filters Name=location,Values=us-west-2-lax-1a \
  --query 'InstanceTypeOfferings[*].InstanceType' \
  --output text
```

---

## AWS Wavelength

```bash
# --- Enable Wavelength Zones ---
# List all Wavelength Zones
aws ec2 describe-availability-zones \
  --all-availability-zones \
  --filters Name=zone-type,Values=wavelength-zone \
  --query 'AvailabilityZones[*].{Name:ZoneName,State:State,OptIn:OptInStatus,Provider:ParentZoneName}' \
  --output table

# Opt in to a Wavelength Zone
aws ec2 modify-availability-zone-group \
  --group-name us-east-1-wl1 \
  --opt-in-status opted-in

# --- Carrier Gateway ---
# Create a carrier gateway for the VPC
aws ec2 create-carrier-gateway \
  --vpc-id vpc-0abc12345def67890 \
  --tag-specifications 'ResourceType=carrier-gateway,Tags=[{Key=Name,Value=wl-cgw}]'

aws ec2 describe-carrier-gateways

# Create a route table for the Wavelength Zone subnet
aws ec2 create-route-table \
  --vpc-id vpc-0abc12345def67890

# Add a default route through the carrier gateway
aws ec2 create-route \
  --route-table-id rtb-0abc12345def67890 \
  --destination-cidr-block 0.0.0.0/0 \
  --carrier-gateway-id cagw-0abc12345def67890

# --- Subnet and Instances ---
# Create a subnet in the Wavelength Zone
aws ec2 create-subnet \
  --vpc-id vpc-0abc12345def67890 \
  --cidr-block 10.0.200.0/24 \
  --availability-zone us-east-1-wl1-bos-wlz-1 \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=wavelength-subnet-bos}]'

# Launch an instance in the Wavelength Zone
aws ec2 run-instances \
  --image-id ami-0abc12345def67890 \
  --instance-type t3.medium \
  --subnet-id subnet-0abc12345def67890 \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=wavelength-app}]'

# --- Carrier IP ---
# Allocate a carrier IP (from the carrier's address space)
aws ec2 allocate-address \
  --domain vpc \
  --network-border-group us-east-1-wl1-bos-wlz-1

# Associate carrier IP with an instance's network interface
aws ec2 associate-address \
  --allocation-id eipalloc-0abc12345def67890 \
  --network-interface-id eni-0abc12345def67890
```

---

## VMware Cloud on AWS

VMware Cloud on AWS is managed through the VMware Cloud console (`vmc.vmware.com`) and the VMware Cloud on AWS CLI/API — not through the AWS CLI. The AWS CLI handles the supporting infrastructure (VPC, Direct Connect, ENI connections).

```bash
# --- AWS-Side: VPC and Connectivity Setup ---
# The SDDC connects to a customer VPC via an ENI; this VPC must exist before SDDC provisioning

# Create a dedicated VPC for VMware Cloud on AWS connectivity
aws ec2 create-vpc \
  --cidr-block 10.100.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=vmware-cloud-vpc}]'

# Create a subnet in the desired AZ (must match the AZ where the SDDC will be deployed)
aws ec2 create-subnet \
  --vpc-id vpc-0abc12345def67890 \
  --cidr-block 10.100.1.0/24 \
  --availability-zone us-east-1a

# --- Direct Connect for On-Premises Connectivity ---
# List Direct Connect connections
aws directconnect describe-connections

# Create a Direct Connect gateway to connect on-premises to VMware SDDC and AWS VPCs
aws directconnect create-direct-connect-gateway \
  --direct-connect-gateway-name vmware-cloud-dcgw \
  --amazon-side-asn 64512

# Describe Direct Connect gateways
aws directconnect describe-direct-connect-gateways

# --- Route 53 (for DNS resolution between on-premises and SDDC) ---
# Create a private hosted zone for VMware SDDC domain
aws route53 create-hosted-zone \
  --name sddc.internal \
  --caller-reference $(date +%s) \
  --hosted-zone-config '{"PrivateZone":true}' \
  --vpc '{"VPCRegion":"us-east-1","VPCId":"vpc-0abc12345def67890"}'

# --- VMware Cloud CLI (vmc-cli) for SDDC Management ---
# Install the VMware Cloud CLI (Python package)
# pip install vmware-cloud-cli

# Authenticate
# vmc login --refresh-token <your-refresh-token>

# List SDDCs
# vmc sddc list --org-id <org-id>

# Get SDDC details
# vmc sddc describe --org-id <org-id> --sddc-id <sddc-id>
```

---

## AWS Serverless Application Repository (SAR)

```bash
# --- Search and Browse Applications ---
# List public applications (no auth required for public apps)
aws serverlessrepo list-applications

# Search for applications by keyword
aws serverlessrepo list-applications \
  --query 'Applications[?contains(Name, `s3`)]'

# Get details of a specific application (public or accessible)
aws serverlessrepo get-application \
  --application-id arn:aws:serverlessrepo:us-east-1:123456789012:applications/my-app

# Get a specific semantic version
aws serverlessrepo get-application \
  --application-id arn:aws:serverlessrepo:us-east-1:123456789012:applications/my-app \
  --semantic-version 1.2.0

# List versions of an application
aws serverlessrepo list-application-versions \
  --application-id arn:aws:serverlessrepo:us-east-1:123456789012:applications/my-app

# --- Deploy an Application ---
# Step 1: Get the CloudFormation template for the app version
aws serverlessrepo create-cloud-formation-template \
  --application-id arn:aws:serverlessrepo:us-east-1:123456789012:applications/my-app \
  --semantic-version 1.0.0

# Step 2: Create a CloudFormation change set
aws serverlessrepo create-cloud-formation-change-set \
  --application-id arn:aws:serverlessrepo:us-east-1:123456789012:applications/my-app \
  --semantic-version 1.0.0 \
  --stack-name my-app-stack \
  --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
  --parameter-overrides '[{"Name":"BucketName","Value":"my-trigger-bucket"}]'

# Step 3: Execute the change set (get change-set-id from step 2 output)
aws cloudformation execute-change-set \
  --change-set-name arn:aws:cloudformation:us-east-1:123456789012:changeSet/my-app-stack-changeset/abc123

# Monitor the stack deployment
aws cloudformation describe-stacks \
  --stack-name my-app-stack \
  --query 'Stacks[0].StackStatus'

# --- Publish an Application ---
# Package the SAM app (upload code to S3, replace local paths with S3 URIs)
sam package \
  --template-file template.yaml \
  --output-template-file packaged.yaml \
  --s3-bucket my-sar-artifacts-bucket

# Publish to SAR (uses the Metadata block in template.yaml)
sam publish \
  --template packaged.yaml \
  --region us-east-1

# Publish a new version of an existing app
# (update SemanticVersion in template.yaml Metadata block, then re-package and publish)

# --- Manage Application Sharing ---
# Make an application public (share with all AWS accounts)
aws serverlessrepo put-application-policy \
  --application-id arn:aws:serverlessrepo:us-east-1:123456789012:applications/my-app \
  --statements '[{
    "Actions": ["ServerlessRepo:Deploy","ServerlessRepo:Search"],
    "Principals": ["*"],
    "StatementId": "make-public"
  }]'

# Share with a specific AWS account
aws serverlessrepo put-application-policy \
  --application-id arn:aws:serverlessrepo:us-east-1:123456789012:applications/my-app \
  --statements '[{
    "Actions": ["ServerlessRepo:Deploy"],
    "Principals": ["987654321098"],
    "StatementId": "share-with-partner"
  }]'

# View current sharing policy
aws serverlessrepo get-application-policy \
  --application-id arn:aws:serverlessrepo:us-east-1:123456789012:applications/my-app

# --- Update or Delete ---
# Update application metadata (description, readme, home page URL)
aws serverlessrepo update-application \
  --application-id arn:aws:serverlessrepo:us-east-1:123456789012:applications/my-app \
  --description "Updated description for my-app" \
  --readme-url s3://my-sar-artifacts-bucket/README.md

# Delete an application (and all its versions)
aws serverlessrepo delete-application \
  --application-id arn:aws:serverlessrepo:us-east-1:123456789012:applications/my-app
```
