# AWS Spot Instances — CLI Reference
For service concepts, see [spot-instances-capabilities.md](spot-instances-capabilities.md).

## EC2 Spot and Spot Fleet (aws ec2)

```bash
# --- Spot Instance Price History ---

# View Spot price history for m5.large Linux/UNIX in us-east-1
aws ec2 describe-spot-price-history \
  --instance-types m5.large \
  --product-descriptions "Linux/UNIX" \
  --start-time 2025-02-01T00:00:00Z \
  --end-time 2025-03-01T00:00:00Z \
  --region us-east-1

# Compare Spot prices across multiple instance types
aws ec2 describe-spot-price-history \
  --instance-types m5.large m5a.large m5n.large m4.large \
  --product-descriptions "Linux/UNIX (Amazon VPC)" \
  --start-time 2025-03-01T00:00:00Z

# Get Spot prices for a specific AZ
aws ec2 describe-spot-price-history \
  --instance-types c5.xlarge \
  --availability-zone us-east-1a \
  --product-descriptions "Linux/UNIX"

# --- Spot Instance Requests ---

# Request a persistent Spot Instance
aws ec2 request-spot-instances \
  --instance-count 1 \
  --type persistent \
  --launch-specification '{
    "ImageId": "ami-0abcdef1234567890",
    "InstanceType": "m5.large",
    "KeyName": "my-key-pair",
    "SecurityGroupIds": ["sg-12345678"],
    "SubnetId": "subnet-12345678"
  }'

# List all Spot Instance requests
aws ec2 describe-spot-instance-requests

# Cancel a Spot Instance request
aws ec2 cancel-spot-instance-requests \
  --spot-instance-request-ids sir-12345678

# Create a Spot data feed subscription (deliver Spot usage logs to S3)
aws ec2 create-spot-datafeed-subscription \
  --bucket my-spot-datafeed-bucket \
  --prefix spot-logs/

# --- Spot Fleet ---

# Create a Spot Fleet with priceCapacityOptimized strategy (recommended)
aws ec2 request-spot-fleet \
  --spot-fleet-request-config '{
    "AllocationStrategy": "priceCapacityOptimized",
    "TargetCapacity": 10,
    "IamFleetRole": "arn:aws:iam::123456789012:role/AmazonEC2SpotFleetRole",
    "LaunchSpecifications": [
      {
        "ImageId": "ami-0abcdef1234567890",
        "InstanceType": "m5.large",
        "SubnetId": "subnet-12345678"
      },
      {
        "ImageId": "ami-0abcdef1234567890",
        "InstanceType": "m5a.large",
        "SubnetId": "subnet-12345678"
      },
      {
        "ImageId": "ami-0abcdef1234567890",
        "InstanceType": "m4.large",
        "SubnetId": "subnet-87654321"
      }
    ]
  }'

# Describe Spot Fleet requests
aws ec2 describe-spot-fleet-requests

# Get Spot Fleet instances
aws ec2 describe-spot-fleet-instances \
  --spot-fleet-request-id sfr-abcd1234

# Cancel a Spot Fleet (terminate all instances)
aws ec2 cancel-spot-fleet-requests \
  --spot-fleet-request-ids sfr-abcd1234 \
  --terminate-instances
```
