# AWS Global Accelerator & VPN — CLI Reference
For service concepts, see [global-accelerator-vpn-capabilities.md](global-accelerator-vpn-capabilities.md).

## Global Accelerator

> **Important**: All Global Accelerator commands must be run against the `us-west-2` region (`--region us-west-2`).

```bash
# --- Accelerators ---
# Standard accelerator (IPv4)
aws globalaccelerator create-accelerator \
  --name my-accelerator \
  --ip-address-type IPV4 \
  --enabled \
  --region us-west-2

# Dual-stack accelerator (IPv4 + IPv6)
aws globalaccelerator create-accelerator \
  --name my-dualstack-accelerator \
  --ip-address-type DUAL_STACK \
  --enabled \
  --region us-west-2

aws globalaccelerator list-accelerators --region us-west-2
aws globalaccelerator describe-accelerator \
  --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abc123 \
  --region us-west-2

# Disable accelerator (required before deletion)
aws globalaccelerator update-accelerator \
  --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abc123 \
  --no-enabled \
  --region us-west-2

aws globalaccelerator delete-accelerator \
  --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abc123 \
  --region us-west-2

# --- Listeners ---
aws globalaccelerator create-listener \
  --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abc123 \
  --port-ranges FromPort=80,ToPort=80 FromPort=443,ToPort=443 \
  --protocol TCP \
  --client-affinity NONE \
  --region us-west-2

# Listener with SOURCE_IP client affinity
aws globalaccelerator create-listener \
  --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abc123 \
  --port-ranges FromPort=53,ToPort=53 \
  --protocol UDP \
  --client-affinity SOURCE_IP \
  --region us-west-2

aws globalaccelerator list-listeners \
  --accelerator-arn arn:aws:globalaccelerator::123456789012:accelerator/abc123 \
  --region us-west-2

aws globalaccelerator update-listener \
  --listener-arn arn:aws:globalaccelerator::123456789012:listener/abc123 \
  --client-affinity SOURCE_IP \
  --region us-west-2

aws globalaccelerator delete-listener \
  --listener-arn arn:aws:globalaccelerator::123456789012:listener/abc123 \
  --region us-west-2

# --- Endpoint Groups ---
aws globalaccelerator create-endpoint-group \
  --listener-arn arn:aws:globalaccelerator::123456789012:listener/abc123 \
  --endpoint-group-region us-east-1 \
  --endpoint-configurations \
    EndpointId=arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234,Weight=100,ClientIPPreservationEnabled=true \
  --traffic-dial-percentage 100 \
  --health-check-protocol HTTP \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --threshold-count 3 \
  --region us-west-2

# Endpoint group with NLB
aws globalaccelerator create-endpoint-group \
  --listener-arn arn:aws:globalaccelerator::123456789012:listener/abc123 \
  --endpoint-group-region us-west-2 \
  --endpoint-configurations \
    EndpointId=arn:aws:elasticloadbalancing:us-west-2:123456789012:loadbalancer/net/my-nlb/1234,Weight=100 \
  --traffic-dial-percentage 100 \
  --region us-west-2

aws globalaccelerator list-endpoint-groups \
  --listener-arn arn:aws:globalaccelerator::123456789012:listener/abc123 \
  --region us-west-2

# Shift traffic to 0% for maintenance
aws globalaccelerator update-endpoint-group \
  --endpoint-group-arn arn:aws:globalaccelerator::123456789012:endpointgroup/abc123 \
  --traffic-dial-percentage 0 \
  --region us-west-2

aws globalaccelerator delete-endpoint-group \
  --endpoint-group-arn arn:aws:globalaccelerator::123456789012:endpointgroup/abc123 \
  --region us-west-2

# --- Endpoints ---
aws globalaccelerator add-endpoints \
  --endpoint-group-arn arn:aws:globalaccelerator::123456789012:endpointgroup/abc123 \
  --endpoint-configurations \
    EndpointId=i-12345678,Weight=50 \
    EndpointId=i-87654321,Weight=50 \
  --region us-west-2

aws globalaccelerator remove-endpoints \
  --endpoint-group-arn arn:aws:globalaccelerator::123456789012:endpointgroup/abc123 \
  --endpoint-identifiers EndpointId=i-12345678 \
  --region us-west-2

aws globalaccelerator list-endpoint-groups \
  --listener-arn arn:aws:globalaccelerator::123456789012:listener/abc123 \
  --region us-west-2

# --- BYOIP ---
aws globalaccelerator provision-byoip-cidr \
  --cidr 203.0.113.0/24 \
  --cidr-authorization-context Message="...",Signature="..." \
  --region us-west-2

aws globalaccelerator list-byoip-cidrs --region us-west-2

aws globalaccelerator advertise-byoip-cidr \
  --cidr 203.0.113.0/24 \
  --region us-west-2
```

---

## VPN

```bash
# --- Site-to-Site VPN ---
# Create Virtual Private Gateway (VGW)
aws ec2 create-vpn-gateway \
  --type ipsec.1 \
  --amazon-side-asn 64512 \
  --tag-specifications 'ResourceType=vpn-gateway,Tags=[{Key=Name,Value=my-vgw}]'

aws ec2 attach-vpn-gateway --vpn-gateway-id vgw-12345678 --vpc-id vpc-12345678
aws ec2 describe-vpn-gateways
aws ec2 detach-vpn-gateway --vpn-gateway-id vgw-12345678 --vpc-id vpc-12345678
aws ec2 delete-vpn-gateway --vpn-gateway-id vgw-12345678

# Create Customer Gateway (represents on-premises device)
aws ec2 create-customer-gateway \
  --type ipsec.1 \
  --public-ip 203.0.113.100 \
  --bgp-asn 65000 \
  --tag-specifications 'ResourceType=customer-gateway,Tags=[{Key=Name,Value=on-prem-cgw}]'

aws ec2 describe-customer-gateways
aws ec2 delete-customer-gateway --customer-gateway-id cgw-12345678

# Create VPN Connection (VGW + static routing)
aws ec2 create-vpn-connection \
  --type ipsec.1 \
  --customer-gateway-id cgw-12345678 \
  --vpn-gateway-id vgw-12345678 \
  --options StaticRoutesOnly=true \
  --tag-specifications 'ResourceType=vpn-connection,Tags=[{Key=Name,Value=my-vpn}]'

# Create VPN Connection (VGW + BGP dynamic routing)
aws ec2 create-vpn-connection \
  --type ipsec.1 \
  --customer-gateway-id cgw-12345678 \
  --vpn-gateway-id vgw-12345678 \
  --options StaticRoutesOnly=false \
  --tag-specifications 'ResourceType=vpn-connection,Tags=[{Key=Name,Value=my-bgp-vpn}]'

# Create VPN Connection attached to Transit Gateway
aws ec2 create-vpn-connection \
  --type ipsec.1 \
  --customer-gateway-id cgw-12345678 \
  --transit-gateway-id tgw-12345678 \
  --options StaticRoutesOnly=false

aws ec2 describe-vpn-connections
aws ec2 describe-vpn-connections --filters Name=state,Values=available

# Add static route to VPN
aws ec2 create-vpn-connection-route \
  --vpn-connection-id vpn-12345678 \
  --destination-cidr-block 192.168.0.0/16

aws ec2 delete-vpn-connection-route \
  --vpn-connection-id vpn-12345678 \
  --destination-cidr-block 192.168.0.0/16

aws ec2 delete-vpn-connection --vpn-connection-id vpn-12345678

# Enable route propagation from VGW to a route table
aws ec2 enable-vgw-route-propagation \
  --route-table-id rtb-12345678 \
  --gateway-id vgw-12345678

# --- Client VPN ---
aws ec2 create-client-vpn-endpoint \
  --client-cidr-block 10.100.0.0/16 \
  --server-certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/server-cert \
  --authentication-options \
    Type=certificate-authentication,MutualAuthentication='{ClientRootCertificateChainArn=arn:aws:acm:us-east-1:123456789012:certificate/client-cert}' \
  --connection-log-options Enabled=false \
  --tag-specifications 'ResourceType=client-vpn-endpoint,Tags=[{Key=Name,Value=my-client-vpn}]'

aws ec2 associate-client-vpn-target-network \
  --client-vpn-endpoint-id cvpn-endpoint-12345678 \
  --subnet-id subnet-12345678

aws ec2 create-client-vpn-route \
  --client-vpn-endpoint-id cvpn-endpoint-12345678 \
  --destination-cidr-block 0.0.0.0/0 \
  --target-vpc-subnet-id subnet-12345678

aws ec2 authorize-client-vpn-ingress \
  --client-vpn-endpoint-id cvpn-endpoint-12345678 \
  --target-network-cidr 10.0.0.0/8 \
  --authorize-all-groups

aws ec2 describe-client-vpn-endpoints
aws ec2 delete-client-vpn-endpoint --client-vpn-endpoint-id cvpn-endpoint-12345678
```
