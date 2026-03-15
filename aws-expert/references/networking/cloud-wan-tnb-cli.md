# Cloud WAN & Telecom Network Builder — CLI Reference
For service concepts, see [cloud-wan-tnb-capabilities.md](cloud-wan-tnb-capabilities.md).

## AWS Cloud WAN (networkmanager service)

```bash
# --- Global Networks ---
aws networkmanager create-global-network \
  --description "Corporate global network" \
  --tags Key=Name,Value=corp-global-network

aws networkmanager describe-global-networks
aws networkmanager describe-global-networks \
  --global-network-ids network-12345678abcdef012

aws networkmanager delete-global-network \
  --global-network-id network-12345678abcdef012

# --- Core Networks ---
aws networkmanager create-core-network \
  --global-network-id network-12345678abcdef012 \
  --description "Production core network" \
  --tags Key=Name,Value=prod-core-network

aws networkmanager list-core-networks

aws networkmanager get-core-network \
  --core-network-id core-network-12345678abcdef012

aws networkmanager delete-core-network \
  --core-network-id core-network-12345678abcdef012

# --- Core Network Policy ---
# Get the current policy (LIVE or PENDING version)
aws networkmanager get-core-network-policy \
  --core-network-id core-network-12345678abcdef012 \
  --alias LIVE

aws networkmanager get-core-network-policy \
  --core-network-id core-network-12345678abcdef012 \
  --alias PENDING

# Put (create) a new policy version — produces a pending Change Set
aws networkmanager put-core-network-policy \
  --core-network-id core-network-12345678abcdef012 \
  --policy-document file://core-network-policy.json

# Delete a specific policy version
aws networkmanager delete-core-network-policy-version \
  --core-network-id core-network-12345678abcdef012 \
  --policy-version-id 3

# --- Change Sets ---
# List change set items before executing
aws networkmanager get-core-network-change-set \
  --core-network-id core-network-12345678abcdef012 \
  --policy-version-id 3

# Execute (apply) the pending Change Set
aws networkmanager execute-core-network-change-set \
  --core-network-id core-network-12345678abcdef012 \
  --policy-version-id 3

# --- VPC Attachments ---
aws networkmanager create-vpc-attachment \
  --core-network-id core-network-12345678abcdef012 \
  --vpc-arn arn:aws:ec2:us-east-1:123456789012:vpc/vpc-12345678 \
  --subnet-arns \
    arn:aws:ec2:us-east-1:123456789012:subnet/subnet-aaaaaaaa \
    arn:aws:ec2:us-east-1:123456789012:subnet/subnet-bbbbbbbb \
  --options Ipv6Support=false,ApplianceModeSupport=false \
  --tags Key=Name,Value=prod-vpc-attach

aws networkmanager list-attachments \
  --core-network-id core-network-12345678abcdef012

aws networkmanager list-attachments \
  --core-network-id core-network-12345678abcdef012 \
  --attachment-type VPC \
  --state AVAILABLE

aws networkmanager get-vpc-attachment \
  --attachment-id attachment-12345678abcdef012

aws networkmanager update-vpc-attachment \
  --attachment-id attachment-12345678abcdef012 \
  --add-subnet-arns arn:aws:ec2:us-east-1:123456789012:subnet/subnet-cccccccc

aws networkmanager delete-attachment \
  --attachment-id attachment-12345678abcdef012

# Accept a pending attachment (when require-attachment-acceptance is set in policy)
aws networkmanager accept-attachment \
  --attachment-id attachment-12345678abcdef012

aws networkmanager reject-attachment \
  --attachment-id attachment-12345678abcdef012

# --- Site-to-Site VPN Attachments ---
aws networkmanager create-site-to-site-vpn-attachment \
  --core-network-id core-network-12345678abcdef012 \
  --vpn-connection-arn arn:aws:ec2:us-east-1:123456789012:vpn-connection/vpn-12345678 \
  --tags Key=Name,Value=branch-vpn-attach

aws networkmanager get-site-to-site-vpn-attachment \
  --attachment-id attachment-12345678abcdef012

# --- Connect (SD-WAN / GRE) Attachments ---
aws networkmanager create-connect-attachment \
  --core-network-id core-network-12345678abcdef012 \
  --edge-location us-east-1 \
  --transport-attachment-id attachment-12345678abcdef012 \
  --options Protocol=GRE \
  --tags Key=Name,Value=sdwan-connect-attach

aws networkmanager create-connect-peer \
  --connect-attachment-id attachment-12345678abcdef012 \
  --peer-address 192.0.2.1 \
  --bgp-options PeerAsn=65000 \
  --inside-cidr-blocks 169.254.6.0/29 \
  --tags Key=Name,Value=sdwan-peer-1

aws networkmanager list-connect-peers

aws networkmanager get-connect-peer \
  --connect-peer-id connect-peer-12345678abcdef012

aws networkmanager delete-connect-peer \
  --connect-peer-id connect-peer-12345678abcdef012

# --- Transit Gateway Peering ---
aws networkmanager create-transit-gateway-peering \
  --core-network-id core-network-12345678abcdef012 \
  --transit-gateway-arn arn:aws:ec2:us-east-1:123456789012:transit-gateway/tgw-12345678 \
  --tags Key=Name,Value=tgw-peering

aws networkmanager list-peerings \
  --core-network-id core-network-12345678abcdef012

aws networkmanager get-transit-gateway-peering \
  --peering-id peering-12345678abcdef012

# Create a TGW route table attachment after peering is established
aws networkmanager create-transit-gateway-route-table-attachment \
  --peering-id peering-12345678abcdef012 \
  --transit-gateway-route-table-arn arn:aws:ec2:us-east-1:123456789012:transit-gateway-route-table/tgw-rtb-12345678 \
  --tags Key=Name,Value=tgw-rt-attach

aws networkmanager delete-peering \
  --peering-id peering-12345678abcdef012

# --- Network Manager: Sites, Links, Devices ---
aws networkmanager create-site \
  --global-network-id network-12345678abcdef012 \
  --description "New York Data Center" \
  --location Latitude=40.7128,Longitude=-74.0060,Address="New York, NY" \
  --tags Key=Name,Value=nyc-dc

aws networkmanager list-sites \
  --global-network-id network-12345678abcdef012

aws networkmanager create-link \
  --global-network-id network-12345678abcdef012 \
  --site-id site-12345678abcdef012 \
  --description "Primary MPLS link" \
  --bandwidth UploadSpeed=100,DownloadSpeed=100 \
  --provider "AT&T" \
  --type MPLS

aws networkmanager create-device \
  --global-network-id network-12345678abcdef012 \
  --site-id site-12345678abcdef012 \
  --description "Edge router NYC" \
  --model "ASR1001-X" \
  --vendor "Cisco"

aws networkmanager create-connection \
  --global-network-id network-12345678abcdef012 \
  --device-id device-aaaa \
  --connected-device-id device-bbbb \
  --link-id link-12345678abcdef012 \
  --connected-link-id link-87654321abcdef012

# --- Route Analyzer ---
aws networkmanager start-route-analysis \
  --global-network-id network-12345678abcdef012 \
  --source TransitGatewayAttachmentArn=arn:aws:ec2:us-east-1:123456789012:transit-gateway-attachment/tgw-attach-12345678,IpAddress=10.0.1.10 \
  --destination TransitGatewayAttachmentArn=arn:aws:ec2:us-east-1:123456789012:transit-gateway-attachment/tgw-attach-87654321,IpAddress=10.1.1.10

aws networkmanager get-route-analysis \
  --global-network-id network-12345678abcdef012 \
  --route-analysis-id ra-12345678abcdef012

# --- Tags ---
aws networkmanager tag-resource \
  --resource-arn arn:aws:networkmanager::123456789012:core-network/core-network-12345678abcdef012 \
  --tags Key=Environment,Value=Production

aws networkmanager untag-resource \
  --resource-arn arn:aws:networkmanager::123456789012:core-network/core-network-12345678abcdef012 \
  --tag-keys Environment
```

---

## AWS Telecom Network Builder (tnb service)

```bash
# --- Function Packages ---
aws tnb create-sol-function-package \
  --tags Key=Name,Value=upf-function-package

aws tnb list-sol-function-packages

aws tnb get-sol-function-package \
  --vnf-pkg-id fp-12345678abcdef012

# Upload the VNFD and artifacts (content-type must match)
aws tnb upload-sol-function-package-content \
  --vnf-pkg-id fp-12345678abcdef012 \
  --content-type application/zip \
  --file fileb://upf-vnfd-package.zip

aws tnb get-sol-function-package-content \
  --vnf-pkg-id fp-12345678abcdef012 \
  --accept application/zip \
  outfile://downloaded-upf-package.zip

aws tnb get-sol-function-package-descriptor \
  --vnf-pkg-id fp-12345678abcdef012 \
  --accept text/plain

aws tnb update-sol-function-package \
  --vnf-pkg-id fp-12345678abcdef012 \
  --operational-state ENABLED

aws tnb delete-sol-function-package \
  --vnf-pkg-id fp-12345678abcdef012

# --- Network Packages ---
aws tnb create-sol-network-package \
  --tags Key=Name,Value=5g-core-network-package

aws tnb list-sol-network-packages

aws tnb get-sol-network-package \
  --nsd-info-id np-12345678abcdef012

# Upload the NSD and artifacts
aws tnb upload-sol-network-package-content \
  --nsd-info-id np-12345678abcdef012 \
  --content-type application/zip \
  --file fileb://5g-core-nsd-package.zip

aws tnb get-sol-network-package-content \
  --nsd-info-id np-12345678abcdef012 \
  --accept application/zip \
  outfile://downloaded-nsd-package.zip

aws tnb get-sol-network-package-descriptor \
  --nsd-info-id np-12345678abcdef012 \
  --accept text/plain

aws tnb update-sol-network-package \
  --nsd-info-id np-12345678abcdef012 \
  --nsd-operational-state ENABLED

aws tnb delete-sol-network-package \
  --nsd-info-id np-12345678abcdef012

# --- Network Instances ---
aws tnb create-sol-network-instance \
  --nsd-info-id np-12345678abcdef012 \
  --ns-name "5g-core-prod" \
  --ns-description "Production 5G Core network instance" \
  --tags Key=Name,Value=5g-core-prod

aws tnb list-sol-network-instances

aws tnb get-sol-network-instance \
  --ns-instance-id ni-12345678abcdef012

# --- Network Instance Lifecycle Operations ---
# Instantiate (deploy resources defined in the NSD)
aws tnb instantiate-sol-network-instance \
  --ns-instance-id ni-12345678abcdef012 \
  --additional-params-for-ns '{"vpcId":"vpc-12345678","subnetId":"subnet-12345678"}'

# Terminate (tear down resources, keep instance record)
aws tnb terminate-sol-network-instance \
  --ns-instance-id ni-12345678abcdef012

# Update a running instance
aws tnb update-sol-network-instance \
  --ns-instance-id ni-12345678abcdef012 \
  --update-type MODIFY_VNF_INFORMATION \
  --modify-vnf-info-data '{"vnfInstanceId":"vnf-aaaa","vnfConfigurableProperties":{"key":"value"}}'

# Delete the instance record (must be in NOT_INSTANTIATED or TERMINATED state)
aws tnb delete-sol-network-instance \
  --ns-instance-id ni-12345678abcdef012

# --- Lifecycle Operation Occurrences ---
# List all lifecycle operation occurrences (instantiate, terminate, update records)
aws tnb list-sol-network-operations

aws tnb get-sol-network-operation \
  --ns-lcm-op-occ-id lo-12345678abcdef012

# --- Tags ---
aws tnb list-tags-for-resource \
  --resource-arn arn:aws:tnb:us-east-1:123456789012:network-instance/ni-12345678abcdef012

aws tnb tag-resource \
  --resource-arn arn:aws:tnb:us-east-1:123456789012:network-instance/ni-12345678abcdef012 \
  --tags Key=Environment,Value=Production

aws tnb untag-resource \
  --resource-arn arn:aws:tnb:us-east-1:123456789012:network-instance/ni-12345678abcdef012 \
  --tag-keys Environment
```
