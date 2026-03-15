# AWS EC2 — CLI Reference

For service concepts, see [ec2-capabilities.md](ec2-capabilities.md).

## EC2 — Instances

```bash
# --- Launch Instances ---
# Launch one Amazon Linux 2023 instance using a Launch Template
aws ec2 run-instances \
  --launch-template LaunchTemplateId=lt-0abcd1234efgh5678,Version=1 \
  --count 1

# Launch an instance with explicit parameters
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type m7g.large \
  --key-name my-key-pair \
  --security-group-ids sg-0abc123def456789 \
  --subnet-id subnet-0abc123def456789 \
  --iam-instance-profile Name=MyInstanceProfile \
  --user-data file://user-data.sh \
  --metadata-options "HttpTokens=required,HttpEndpoint=enabled" \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=my-instance},{Key=Env,Value=prod}]' \
  --count 1

# Launch with instance store (spot + specific AZ)
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type c7g.4xlarge \
  --instance-market-options '{"MarketType":"spot","SpotOptions":{"SpotInstanceType":"one-time","InstanceInterruptionBehavior":"terminate"}}' \
  --placement '{"AvailabilityZone":"us-east-1a"}' \
  --count 1

# --- Describe Instances ---
aws ec2 describe-instances
aws ec2 describe-instances --instance-ids i-0abc123def456789
aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" "Name=tag:Env,Values=prod"

# Describe with JMESPath query: get instance IDs and private IPs
aws ec2 describe-instances \
  --query 'Reservations[*].Instances[*].[InstanceId,PrivateIpAddress,State.Name]' \
  --output table

# --- Start, Stop, Reboot, Terminate ---
aws ec2 start-instances --instance-ids i-0abc123def456789
aws ec2 stop-instances --instance-ids i-0abc123def456789
aws ec2 stop-instances --instance-ids i-0abc123def456789 --hibernate
aws ec2 reboot-instances --instance-ids i-0abc123def456789
aws ec2 terminate-instances --instance-ids i-0abc123def456789

# --- Instance Status and Console ---
aws ec2 describe-instance-status --instance-ids i-0abc123def456789
aws ec2 get-console-output --instance-ids i-0abc123def456789
aws ec2 get-console-screenshot --instance-ids i-0abc123def456789

# --- Modify Instance ---
aws ec2 modify-instance-attribute --instance-id i-0abc123def456789 --instance-type '{"Value":"m7g.xlarge"}'
aws ec2 modify-instance-metadata-options \
  --instance-id i-0abc123def456789 \
  --http-tokens required \
  --http-put-response-hop-limit 1

# --- IAM Instance Profile ---
aws ec2 associate-iam-instance-profile \
  --instance-id i-0abc123def456789 \
  --iam-instance-profile Name=MyNewProfile

aws ec2 describe-iam-instance-profile-associations
aws ec2 disassociate-iam-instance-profile --association-id iip-assoc-0abc123def456789

# --- Elastic IPs ---
aws ec2 allocate-address --domain vpc
aws ec2 associate-address --instance-id i-0abc123def456789 --allocation-id eipalloc-0abc123def456789
aws ec2 disassociate-address --association-id eipassoc-0abc123def456789
aws ec2 release-address --allocation-id eipalloc-0abc123def456789
aws ec2 describe-addresses

# --- Tags ---
aws ec2 create-tags --resources i-0abc123def456789 --tags Key=Owner,Value=team-platform
aws ec2 delete-tags --resources i-0abc123def456789 --tags Key=OldTag

# --- Waiter: Wait until instance is running ---
aws ec2 wait instance-running --instance-ids i-0abc123def456789
aws ec2 wait instance-stopped --instance-ids i-0abc123def456789
aws ec2 wait instance-terminated --instance-ids i-0abc123def456789

# --- EBS Volumes ---
aws ec2 create-volume \
  --availability-zone us-east-1a \
  --volume-type gp3 \
  --size 100 \
  --iops 3000 \
  --throughput 125 \
  --encrypted \
  --kms-key-id alias/my-key

aws ec2 attach-volume \
  --volume-id vol-0abc123def456789 \
  --instance-id i-0abc123def456789 \
  --device /dev/xvdf

aws ec2 detach-volume --volume-id vol-0abc123def456789
aws ec2 describe-volumes --filters "Name=attachment.instance-id,Values=i-0abc123def456789"
aws ec2 modify-volume --volume-id vol-0abc123def456789 --size 200 --iops 6000

# --- Snapshots ---
aws ec2 create-snapshot \
  --volume-id vol-0abc123def456789 \
  --description "Pre-deployment snapshot" \
  --tag-specifications 'ResourceType=snapshot,Tags=[{Key=Name,Value=pre-deploy}]'

aws ec2 describe-snapshots --owner-ids self
aws ec2 copy-snapshot \
  --source-region us-east-1 \
  --source-snapshot-id snap-0abc123def456789 \
  --description "DR copy" \
  --region us-west-2

aws ec2 delete-snapshot --snapshot-id snap-0abc123def456789
```

---

## EC2 — AMIs

```bash
# --- Describe AMIs ---
# List your own AMIs
aws ec2 describe-images --owners self

# Find latest Amazon Linux 2023 AMI (x86_64)
aws ec2 describe-images \
  --owners amazon \
  --filters \
    "Name=name,Values=al2023-ami-2023*" \
    "Name=architecture,Values=x86_64" \
    "Name=state,Values=available" \
  --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
  --output text

# Find latest Amazon Linux 2023 AMI (arm64 / Graviton)
aws ec2 describe-images \
  --owners amazon \
  --filters \
    "Name=name,Values=al2023-ami-2023*" \
    "Name=architecture,Values=arm64" \
    "Name=state,Values=available" \
  --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
  --output text

# --- Create AMI from Running Instance ---
aws ec2 create-image \
  --instance-id i-0abc123def456789 \
  --name "my-app-v2.1.0-$(date +%Y%m%d)" \
  --description "Production AMI baked from running instance" \
  --no-reboot

# Copy AMI to another region
aws ec2 copy-image \
  --source-region us-east-1 \
  --source-image-id ami-0abcdef1234567890 \
  --name "my-app-v2.1.0-copy" \
  --region us-west-2

# --- Share AMI ---
aws ec2 modify-image-attribute \
  --image-id ami-0abcdef1234567890 \
  --launch-permission '{"Add":[{"UserId":"123456789012"}]}'

# Make AMI public
aws ec2 modify-image-attribute \
  --image-id ami-0abcdef1234567890 \
  --launch-permission '{"Add":[{"Group":"all"}]}'

# --- Deprecate / Deregister AMI ---
aws ec2 enable-image-deprecation \
  --image-id ami-0abcdef1234567890 \
  --deprecate-at "2026-12-31T00:00:00.000Z"

aws ec2 deregister-image --image-id ami-0abcdef1234567890
```

---

## EC2 — Key Pairs and Security Groups

```bash
# --- Key Pairs ---
# Create key pair and save private key
aws ec2 create-key-pair \
  --key-name my-key-pair \
  --key-type ed25519 \
  --query 'KeyMaterial' \
  --output text > my-key-pair.pem
chmod 400 my-key-pair.pem

aws ec2 describe-key-pairs
aws ec2 delete-key-pair --key-name my-key-pair

# Import existing public key
aws ec2 import-key-pair \
  --key-name my-imported-key \
  --public-key-material fileb://~/.ssh/id_ed25519.pub

# --- Security Groups ---
aws ec2 create-security-group \
  --group-name my-app-sg \
  --description "Security group for my application" \
  --vpc-id vpc-0abc123def456789

# Allow inbound HTTPS from anywhere
aws ec2 authorize-security-group-ingress \
  --group-id sg-0abc123def456789 \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Allow inbound SSH from a specific CIDR
aws ec2 authorize-security-group-ingress \
  --group-id sg-0abc123def456789 \
  --protocol tcp \
  --port 22 \
  --cidr 10.0.0.0/8

# Allow inbound from another security group (for internal traffic)
aws ec2 authorize-security-group-ingress \
  --group-id sg-0abc123def456789 \
  --protocol tcp \
  --port 8080 \
  --source-group sg-0source123def456

# Revoke a rule
aws ec2 revoke-security-group-ingress \
  --group-id sg-0abc123def456789 \
  --protocol tcp \
  --port 22 \
  --cidr 10.0.0.0/8

aws ec2 describe-security-groups --group-ids sg-0abc123def456789
aws ec2 describe-security-group-rules --filters "Name=group-id,Values=sg-0abc123def456789"
aws ec2 delete-security-group --group-id sg-0abc123def456789
```

---

## EC2 — Placement Groups

```bash
# --- Create Placement Groups ---
# Cluster: low-latency, single AZ
aws ec2 create-placement-group \
  --group-name hpc-cluster \
  --strategy cluster

# Partition: fault isolation for distributed systems
aws ec2 create-placement-group \
  --group-name kafka-partition-group \
  --strategy partition \
  --partition-count 3

# Spread: max isolation for small critical groups
aws ec2 create-placement-group \
  --group-name critical-spread-group \
  --strategy spread

aws ec2 describe-placement-groups
aws ec2 delete-placement-group --group-name hpc-cluster

# Launch instance into a placement group
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type hpc7g.16xlarge \
  --placement '{"GroupName":"hpc-cluster"}' \
  --count 4
```

---

## EC2 — Launch Templates

```bash
# --- Create Launch Template ---
aws ec2 create-launch-template \
  --launch-template-name my-app-lt \
  --version-description "v1 - initial" \
  --launch-template-data '{
    "ImageId": "ami-0abcdef1234567890",
    "InstanceType": "m7g.large",
    "KeyName": "my-key-pair",
    "SecurityGroupIds": ["sg-0abc123def456789"],
    "IamInstanceProfile": {"Name": "MyInstanceProfile"},
    "MetadataOptions": {"HttpTokens": "required", "HttpEndpoint": "enabled", "HttpPutResponseHopLimit": 1},
    "TagSpecifications": [{"ResourceType": "instance", "Tags": [{"Key": "Env", "Value": "prod"}]}],
    "UserData": "'$(base64 -w0 user-data.sh)'"
  }'

# Create a new version of an existing Launch Template
aws ec2 create-launch-template-version \
  --launch-template-id lt-0abcd1234efgh5678 \
  --source-version 1 \
  --version-description "v2 - new AMI" \
  --launch-template-data '{"ImageId":"ami-0newimage1234567890"}'

# Set a default version
aws ec2 modify-launch-template \
  --launch-template-id lt-0abcd1234efgh5678 \
  --default-version 2

aws ec2 describe-launch-templates
aws ec2 describe-launch-template-versions --launch-template-id lt-0abcd1234efgh5678
aws ec2 delete-launch-template --launch-template-id lt-0abcd1234efgh5678
aws ec2 delete-launch-template-versions \
  --launch-template-id lt-0abcd1234efgh5678 \
  --versions 1
```

---

## EC2 — Spot Instances and Fleets

```bash
# --- Spot Instance Requests ---
# One-time Spot request
aws ec2 request-spot-instances \
  --instance-count 2 \
  --type one-time \
  --launch-specification '{
    "ImageId": "ami-0abcdef1234567890",
    "InstanceType": "c7g.4xlarge",
    "KeyName": "my-key-pair",
    "SecurityGroupIds": ["sg-0abc123def456789"],
    "SubnetId": "subnet-0abc123def456789"
  }'

# Persistent Spot request (re-submits after interruption)
aws ec2 request-spot-instances \
  --instance-count 1 \
  --type persistent \
  --launch-specification '{"ImageId":"ami-0abcdef1234567890","InstanceType":"m7g.xlarge"}' \
  --instance-interruption-behavior stop

aws ec2 describe-spot-instance-requests
aws ec2 cancel-spot-instance-requests --spot-instance-request-ids sir-0abc123def456789

# Spot price history (last 24 hours, specific type)
aws ec2 describe-spot-price-history \
  --instance-types c7g.4xlarge m7g.4xlarge \
  --product-descriptions "Linux/UNIX" \
  --start-time "$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-24H +%Y-%m-%dT%H:%M:%SZ)" \
  --query 'SpotPriceHistory[*].[InstanceType,AvailabilityZone,SpotPrice]' \
  --output table

# --- Spot Fleet ---
aws ec2 request-spot-fleet \
  --spot-fleet-request-config '{
    "IamFleetRole": "arn:aws:iam::123456789012:role/AmazonEC2SpotFleetRole",
    "TargetCapacity": 10,
    "AllocationStrategy": "priceCapacityOptimized",
    "LaunchSpecifications": [
      {"ImageId": "ami-0abc", "InstanceType": "m7g.large", "SubnetId": "subnet-0abc"},
      {"ImageId": "ami-0abc", "InstanceType": "m6g.large", "SubnetId": "subnet-0abc"},
      {"ImageId": "ami-0abc", "InstanceType": "m7g.xlarge", "SubnetId": "subnet-0abc"}
    ]
  }'

aws ec2 describe-spot-fleet-requests
aws ec2 describe-spot-fleet-instances --spot-fleet-request-id sfr-0abc123def456789
aws ec2 modify-spot-fleet-request \
  --spot-fleet-request-id sfr-0abc123def456789 \
  --target-capacity 20
aws ec2 cancel-spot-fleet-requests \
  --spot-fleet-request-ids sfr-0abc123def456789 \
  --terminate-instances

# --- EC2 Fleet (Spot + On-Demand mix) ---
aws ec2 create-fleet \
  --launch-template-configs '[{
    "LaunchTemplateSpecification": {"LaunchTemplateId":"lt-0abc","Version":"$Latest"},
    "Overrides": [
      {"InstanceType": "m7g.large", "SubnetId": "subnet-0abc"},
      {"InstanceType": "m6g.large", "SubnetId": "subnet-0def"},
      {"InstanceType": "c7g.large", "SubnetId": "subnet-0ghi"}
    ]
  }]' \
  --target-capacity-specification '{
    "TotalTargetCapacity": 20,
    "OnDemandTargetCapacity": 5,
    "SpotTargetCapacity": 15,
    "DefaultTargetCapacityType": "spot"
  }' \
  --spot-options '{"AllocationStrategy":"price-capacity-optimized","CapacityRebalance":{"ReplacementStrategy":"launch-before-terminate"}}' \
  --on-demand-options '{"AllocationStrategy":"lowest-price"}' \
  --type instant

aws ec2 describe-fleets
aws ec2 delete-fleets --fleet-ids fleet-0abc123def456789 --terminate-instances
```

---

## EC2 — Reserved Instances and Capacity

```bash
# --- Reserved Instances ---
# Describe purchased RIs
aws ec2 describe-reserved-instances
aws ec2 describe-reserved-instances \
  --filters "Name=state,Values=active" "Name=product-description,Values=Linux/UNIX"

# Browse available RI offerings
aws ec2 describe-reserved-instances-offerings \
  --instance-type m7g.large \
  --product-description "Linux/UNIX" \
  --offering-class standard \
  --offering-type "All Upfront" \
  --filters "Name=duration,Values=31536000"  # 1 year in seconds

# Purchase an RI
aws ec2 purchase-reserved-instances-offering \
  --reserved-instances-offering-id abc123de-f456-789a-bcde-f01234567890 \
  --instance-count 2

# Modify an RI (change AZ or network platform)
aws ec2 modify-reserved-instances \
  --reserved-instances-ids aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee \
  --target-configurations '[{"AvailabilityZone":"us-east-1b","InstanceCount":2,"Platform":"EC2-VPC"}]'

# --- On-Demand Capacity Reservations ---
aws ec2 create-capacity-reservation \
  --instance-type m7g.large \
  --instance-platform "Linux/UNIX" \
  --availability-zone us-east-1a \
  --instance-count 5 \
  --instance-match-criteria open \
  --end-date-type unlimited

aws ec2 describe-capacity-reservations
aws ec2 cancel-capacity-reservation --capacity-reservation-id cr-0abc123def456789

# Check usage of a capacity reservation
aws ec2 get-capacity-reservation-usage --capacity-reservation-id cr-0abc123def456789
```

---

## EC2 — Instance Types and Optimizer

```bash
# --- Describe Instance Types ---
aws ec2 describe-instance-types \
  --instance-types m7g.large c7g.large r7g.large

# List all Graviton (arm64) instances
aws ec2 describe-instance-types \
  --filters "Name=processor-info.supported-architecture,Values=arm64" \
  --query 'InstanceTypes[*].[InstanceType,VCpuInfo.DefaultVCpus,MemoryInfo.SizeInMiB]' \
  --output table

# List instance types by attribute (e.g., metal instances)
aws ec2 describe-instance-types \
  --filters "Name=bare-metal,Values=true" \
  --query 'InstanceTypes[*].InstanceType'

# Check instance type availability in a region
aws ec2 describe-instance-type-offerings \
  --location-type region \
  --filters "Name=instance-type,Values=m7g.large"

# Check availability in specific AZs
aws ec2 describe-instance-type-offerings \
  --location-type availability-zone \
  --filters "Name=instance-type,Values=p4d.24xlarge"

# Find instance types matching requirements (vCPUs, memory)
aws ec2 get-instance-types-from-instance-requirements \
  --architecture-types x86_64 \
  --virtualization-types hvm \
  --instance-requirements '{
    "VCpuCount": {"Min": 4, "Max": 16},
    "MemoryMiB": {"Min": 16384},
    "ExcludedInstanceTypes": ["t2.*", "t3.*"]
  }'
```
