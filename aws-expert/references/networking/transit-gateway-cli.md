# AWS Transit Gateway — CLI Reference
For service concepts, see [transit-gateway-capabilities.md](transit-gateway-capabilities.md).

## Transit Gateway

```bash
# --- Transit Gateways ---
aws ec2 create-transit-gateway \
  --description "Central hub TGW" \
  --options \
    AmazonSideAsn=64512,\
    AutoAcceptSharedAttachments=disable,\
    DefaultRouteTableAssociation=enable,\
    DefaultRouteTablePropagation=enable,\
    VpnEcmpSupport=enable,\
    DnsSupport=enable,\
    MulticastSupport=disable \
  --tag-specifications 'ResourceType=transit-gateway,Tags=[{Key=Name,Value=central-tgw}]'

aws ec2 describe-transit-gateways
aws ec2 describe-transit-gateways --transit-gateway-ids tgw-12345678
aws ec2 modify-transit-gateway \
  --transit-gateway-id tgw-12345678 \
  --options AutoAcceptSharedAttachments=enable
aws ec2 delete-transit-gateway --transit-gateway-id tgw-12345678

# --- VPC Attachments ---
aws ec2 create-transit-gateway-vpc-attachment \
  --transit-gateway-id tgw-12345678 \
  --vpc-id vpc-12345678 \
  --subnet-ids subnet-12345678 subnet-87654321 \
  --tag-specifications 'ResourceType=transit-gateway-attachment,Tags=[{Key=Name,Value=prod-vpc-attach}]'

aws ec2 describe-transit-gateway-attachments
aws ec2 describe-transit-gateway-vpc-attachments \
  --filters Name=transit-gateway-id,Values=tgw-12345678

aws ec2 modify-transit-gateway-vpc-attachment \
  --transit-gateway-attachment-id tgw-attach-12345678 \
  --add-subnet-ids subnet-99999999

aws ec2 delete-transit-gateway-vpc-attachment \
  --transit-gateway-attachment-id tgw-attach-12345678

# Accept a pending VPC attachment (for cross-account)
aws ec2 accept-transit-gateway-vpc-attachment \
  --transit-gateway-attachment-id tgw-attach-12345678

# --- Route Tables ---
aws ec2 create-transit-gateway-route-table \
  --transit-gateway-id tgw-12345678 \
  --tag-specifications 'ResourceType=transit-gateway-route-table,Tags=[{Key=Name,Value=isolated-rt}]'

aws ec2 describe-transit-gateway-route-tables \
  --filters Name=transit-gateway-id,Values=tgw-12345678

# Associate attachment with a non-default route table
aws ec2 associate-transit-gateway-route-table \
  --transit-gateway-route-table-id tgw-rtb-12345678 \
  --transit-gateway-attachment-id tgw-attach-12345678

aws ec2 disassociate-transit-gateway-route-table \
  --transit-gateway-route-table-id tgw-rtb-12345678 \
  --transit-gateway-attachment-id tgw-attach-12345678

# Enable route propagation from an attachment to a route table
aws ec2 enable-transit-gateway-route-table-propagation \
  --transit-gateway-route-table-id tgw-rtb-12345678 \
  --transit-gateway-attachment-id tgw-attach-12345678

aws ec2 disable-transit-gateway-route-table-propagation \
  --transit-gateway-route-table-id tgw-rtb-12345678 \
  --transit-gateway-attachment-id tgw-attach-12345678

# Add static route to TGW route table
aws ec2 create-transit-gateway-route \
  --transit-gateway-route-table-id tgw-rtb-12345678 \
  --destination-cidr-block 10.2.0.0/16 \
  --transit-gateway-attachment-id tgw-attach-87654321

# Search routes in a TGW route table
aws ec2 search-transit-gateway-routes \
  --transit-gateway-route-table-id tgw-rtb-12345678 \
  --filters Name=type,Values=static

aws ec2 delete-transit-gateway-route \
  --transit-gateway-route-table-id tgw-rtb-12345678 \
  --destination-cidr-block 10.2.0.0/16

aws ec2 delete-transit-gateway-route-table \
  --transit-gateway-route-table-id tgw-rtb-12345678

# --- Peering Attachments ---
aws ec2 create-transit-gateway-peering-attachment \
  --transit-gateway-id tgw-12345678 \
  --peer-transit-gateway-id tgw-87654321 \
  --peer-account-id 123456789012 \
  --peer-region us-west-2

# Accept peering in the peer account/region
aws ec2 accept-transit-gateway-peering-attachment \
  --transit-gateway-attachment-id tgw-attach-peering-12345678 \
  --region us-west-2
```
