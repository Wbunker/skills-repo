# AWS VPC — CLI Reference
For service concepts, see [vpc-capabilities.md](vpc-capabilities.md).

## VPC — Core Resources

```bash
# --- VPC ---
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=my-vpc}]'
aws ec2 describe-vpcs
aws ec2 describe-vpcs --filters Name=isDefault,Values=false
aws ec2 modify-vpc-attribute --vpc-id vpc-12345678 --enable-dns-hostnames
aws ec2 modify-vpc-attribute --vpc-id vpc-12345678 --enable-dns-support
aws ec2 delete-vpc --vpc-id vpc-12345678

# Add secondary CIDR block
aws ec2 associate-vpc-cidr-block --vpc-id vpc-12345678 --cidr-block 10.1.0.0/16

# --- Subnets ---
aws ec2 create-subnet \
  --vpc-id vpc-12345678 \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-1a}]'

aws ec2 describe-subnets --filters Name=vpc-id,Values=vpc-12345678
aws ec2 delete-subnet --subnet-id subnet-12345678

# Enable auto-assign public IP on subnet
aws ec2 modify-subnet-attribute --subnet-id subnet-12345678 --map-public-ip-on-launch

# --- Route Tables ---
aws ec2 create-route-table \
  --vpc-id vpc-12345678 \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=public-rt}]'

aws ec2 describe-route-tables --filters Name=vpc-id,Values=vpc-12345678

# Add a route
aws ec2 create-route \
  --route-table-id rtb-12345678 \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id igw-12345678

# Associate route table with a subnet
aws ec2 associate-route-table \
  --route-table-id rtb-12345678 \
  --subnet-id subnet-12345678

# Replace an existing route table association
aws ec2 replace-route-table-association \
  --association-id rtbassoc-12345678 \
  --route-table-id rtb-87654321

aws ec2 delete-route --route-table-id rtb-12345678 --destination-cidr-block 10.1.0.0/16
aws ec2 delete-route-table --route-table-id rtb-12345678

# --- Internet Gateway ---
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=my-igw}]'

aws ec2 attach-internet-gateway --internet-gateway-id igw-12345678 --vpc-id vpc-12345678
aws ec2 detach-internet-gateway --internet-gateway-id igw-12345678 --vpc-id vpc-12345678
aws ec2 describe-internet-gateways --filters Name=attachment.vpc-id,Values=vpc-12345678
aws ec2 delete-internet-gateway --internet-gateway-id igw-12345678

# --- Elastic IP ---
aws ec2 allocate-address --domain vpc
aws ec2 associate-address --allocation-id eipalloc-12345678 --instance-id i-12345678
aws ec2 describe-addresses
aws ec2 release-address --allocation-id eipalloc-12345678

# --- NAT Gateway ---
# Public NAT Gateway (requires an EIP)
aws ec2 create-nat-gateway \
  --subnet-id subnet-12345678 \
  --allocation-id eipalloc-12345678 \
  --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=my-nat-gw}]'

# Private NAT Gateway (no EIP required)
aws ec2 create-nat-gateway \
  --subnet-id subnet-12345678 \
  --connectivity-type private

aws ec2 describe-nat-gateways
aws ec2 describe-nat-gateways --filter Name=state,Values=available
aws ec2 delete-nat-gateway --nat-gateway-id nat-12345678

# --- Egress-Only Internet Gateway (IPv6) ---
aws ec2 create-egress-only-internet-gateway --vpc-id vpc-12345678
aws ec2 describe-egress-only-internet-gateways

# --- DHCP Options ---
aws ec2 create-dhcp-options \
  --dhcp-configuration \
    "Key=domain-name,Values=example.com" \
    "Key=domain-name-servers,Values=10.0.0.2,AmazonProvidedDNS"
aws ec2 associate-dhcp-options --dhcp-options-id dopt-12345678 --vpc-id vpc-12345678
aws ec2 describe-dhcp-options
```

---

## VPC — Security Groups & NACLs

```bash
# --- Security Groups ---
aws ec2 create-security-group \
  --group-name web-sg \
  --description "Web tier security group" \
  --vpc-id vpc-12345678 \
  --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=web-sg}]'

aws ec2 describe-security-groups --filters Name=vpc-id,Values=vpc-12345678
aws ec2 describe-security-groups --group-ids sg-12345678

# Add inbound rules
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Add inbound rule referencing another security group
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --ip-permissions \
    IpProtocol=tcp,FromPort=8080,ToPort=8080,UserIdGroupPairs=[{GroupId=sg-87654321}]

# Add outbound rules
aws ec2 authorize-security-group-egress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 5432 \
  --cidr 10.0.2.0/24

# Remove rules
aws ec2 revoke-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

aws ec2 revoke-security-group-egress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 5432 \
  --cidr 10.0.2.0/24

# Update rule descriptions
aws ec2 update-security-group-rule-descriptions-ingress \
  --group-id sg-12345678 \
  --ip-permissions 'IpProtocol=tcp,FromPort=443,ToPort=443,IpRanges=[{CidrIp=0.0.0.0/0,Description="Public HTTPS"}]'

aws ec2 delete-security-group --group-id sg-12345678

# --- Network ACLs ---
aws ec2 create-network-acl \
  --vpc-id vpc-12345678 \
  --tag-specifications 'ResourceType=network-acl,Tags=[{Key=Name,Value=private-nacl}]'

aws ec2 describe-network-acls --filters Name=vpc-id,Values=vpc-12345678

# Add inbound rule (rule 100, allow HTTPS from anywhere)
aws ec2 create-network-acl-entry \
  --network-acl-id acl-12345678 \
  --rule-number 100 \
  --protocol tcp \
  --rule-action allow \
  --ingress \
  --cidr-block 0.0.0.0/0 \
  --port-range From=443,To=443

# Add outbound rule (rule 100, allow ephemeral ports)
aws ec2 create-network-acl-entry \
  --network-acl-id acl-12345678 \
  --rule-number 100 \
  --protocol tcp \
  --rule-action allow \
  --egress \
  --cidr-block 0.0.0.0/0 \
  --port-range From=1024,To=65535

# Replace (update) an existing entry
aws ec2 replace-network-acl-entry \
  --network-acl-id acl-12345678 \
  --rule-number 100 \
  --protocol tcp \
  --rule-action allow \
  --ingress \
  --cidr-block 10.0.0.0/8 \
  --port-range From=443,To=443

aws ec2 delete-network-acl-entry --network-acl-id acl-12345678 --rule-number 100 --ingress

# Associate NACL with subnet
aws ec2 replace-network-acl-association \
  --association-id aclassoc-12345678 \
  --network-acl-id acl-12345678

aws ec2 delete-network-acl --network-acl-id acl-12345678
```

---

## VPC — Peering & Endpoints

```bash
# --- VPC Peering ---
# Request peering connection (same account)
aws ec2 create-vpc-peering-connection \
  --vpc-id vpc-12345678 \
  --peer-vpc-id vpc-87654321 \
  --tag-specifications 'ResourceType=vpc-peering-connection,Tags=[{Key=Name,Value=vpc-a-to-b}]'

# Cross-account peering (specify peer-owner-id)
aws ec2 create-vpc-peering-connection \
  --vpc-id vpc-12345678 \
  --peer-vpc-id vpc-87654321 \
  --peer-owner-id 123456789012

# Cross-region peering
aws ec2 create-vpc-peering-connection \
  --vpc-id vpc-12345678 \
  --peer-vpc-id vpc-87654321 \
  --peer-region us-west-2

# Accept peering (must be run in accepter account/region)
aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id pcx-12345678

aws ec2 describe-vpc-peering-connections
aws ec2 describe-vpc-peering-connections \
  --filters Name=status-code,Values=active

aws ec2 reject-vpc-peering-connection --vpc-peering-connection-id pcx-12345678
aws ec2 delete-vpc-peering-connection --vpc-peering-connection-id pcx-12345678

# Add routes for peering (must add on both sides)
aws ec2 create-route \
  --route-table-id rtb-12345678 \
  --destination-cidr-block 10.1.0.0/16 \
  --vpc-peering-connection-id pcx-12345678

# --- VPC Endpoints ---
# Gateway endpoint (S3)
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-12345678 \
  --service-name com.amazonaws.us-east-1.s3 \
  --vpc-endpoint-type Gateway \
  --route-table-ids rtb-12345678 rtb-87654321

# Interface endpoint (Secrets Manager)
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-12345678 \
  --service-name com.amazonaws.us-east-1.secretsmanager \
  --vpc-endpoint-type Interface \
  --subnet-ids subnet-12345678 subnet-87654321 \
  --security-group-ids sg-12345678 \
  --private-dns-enabled

# Interface endpoint for a custom endpoint service
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-12345678 \
  --service-name com.amazonaws.vpce.us-east-1.vpce-svc-12345678 \
  --vpc-endpoint-type Interface \
  --subnet-ids subnet-12345678

aws ec2 describe-vpc-endpoints
aws ec2 describe-vpc-endpoints --filters Name=vpc-id,Values=vpc-12345678
aws ec2 describe-vpc-endpoint-services

# Modify endpoint (e.g., add subnet, update policy)
aws ec2 modify-vpc-endpoint \
  --vpc-endpoint-id vpce-12345678 \
  --add-subnet-ids subnet-87654321 \
  --policy-document file://endpoint-policy.json

aws ec2 delete-vpc-endpoints --vpc-endpoint-ids vpce-12345678

# --- Endpoint Services (PrivateLink) ---
aws ec2 create-vpc-endpoint-service-configuration \
  --network-load-balancer-arns arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/net/my-nlb/1234 \
  --acceptance-required

aws ec2 describe-vpc-endpoint-service-configurations
aws ec2 accept-vpc-endpoint-connections \
  --service-id vpce-svc-12345678 \
  --vpc-endpoint-ids vpce-87654321

aws ec2 modify-vpc-endpoint-service-configuration \
  --service-id vpce-svc-12345678 \
  --no-acceptance-required
```

---

## VPC — Flow Logs

```bash
# Create flow logs to CloudWatch Logs
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-12345678 \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name /vpc/flowlogs \
  --deliver-logs-permission-arn arn:aws:iam::123456789012:role/FlowLogRole

# Create flow logs to S3
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-12345678 \
  --traffic-type ALL \
  --log-destination-type s3 \
  --log-destination arn:aws:s3:::my-flow-logs-bucket/vpc-logs/

# Flow logs for a subnet
aws ec2 create-flow-logs \
  --resource-type Subnet \
  --resource-ids subnet-12345678 \
  --traffic-type REJECT \
  --log-destination-type s3 \
  --log-destination arn:aws:s3:::my-flow-logs-bucket/

# Flow logs for a network interface
aws ec2 create-flow-logs \
  --resource-type NetworkInterface \
  --resource-ids eni-12345678 \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name /vpc/eni-flowlogs \
  --deliver-logs-permission-arn arn:aws:iam::123456789012:role/FlowLogRole

aws ec2 describe-flow-logs
aws ec2 describe-flow-logs --filter Name=resource-id,Values=vpc-12345678
aws ec2 delete-flow-logs --flow-log-ids fl-12345678
```
