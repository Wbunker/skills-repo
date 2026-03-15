# AWS Direct Connect — CLI Reference
For service concepts, see [direct-connect-capabilities.md](direct-connect-capabilities.md).

## Direct Connect

```bash
# --- Connections ---
# Create a dedicated connection
aws directconnect create-connection \
  --location EqDC2 \
  --bandwidth 1Gbps \
  --connection-name my-dx-connection

aws directconnect describe-connections
aws directconnect describe-connections --connection-id dxcon-12345678

# Update connection name
aws directconnect update-connection \
  --connection-id dxcon-12345678 \
  --connection-name new-connection-name

aws directconnect delete-connection --connection-id dxcon-12345678

# --- Virtual Interfaces ---
# Create private VIF (connect to a VPC via VGW)
aws directconnect create-private-virtual-interface \
  --connection-id dxcon-12345678 \
  --new-private-virtual-interface '{
    "virtualInterfaceName": "private-vif",
    "vlan": 100,
    "asn": 65000,
    "authKey": "bgp-md5-auth-key",
    "amazonAddress": "169.254.100.1/30",
    "customerAddress": "169.254.100.2/30",
    "addressFamily": "ipv4",
    "virtualGatewayId": "vgw-12345678"
  }'

# Create private VIF via Direct Connect Gateway
aws directconnect create-private-virtual-interface \
  --connection-id dxcon-12345678 \
  --new-private-virtual-interface '{
    "virtualInterfaceName": "private-vif-dcgw",
    "vlan": 101,
    "asn": 65000,
    "directConnectGatewayId": "dcgw-12345678",
    "addressFamily": "ipv4"
  }'

# Create public VIF (access all AWS public endpoints)
aws directconnect create-public-virtual-interface \
  --connection-id dxcon-12345678 \
  --new-public-virtual-interface '{
    "virtualInterfaceName": "public-vif",
    "vlan": 200,
    "asn": 65000,
    "authKey": "bgp-md5-auth-key",
    "amazonAddress": "169.254.200.1/30",
    "customerAddress": "169.254.200.2/30",
    "addressFamily": "ipv4",
    "routeFilterPrefixes": [{"cidr": "203.0.113.0/24"}]
  }'

# Create transit VIF (connect to Transit Gateway via DXGW)
aws directconnect create-transit-virtual-interface \
  --connection-id dxcon-12345678 \
  --new-transit-virtual-interface '{
    "virtualInterfaceName": "transit-vif",
    "vlan": 300,
    "asn": 65000,
    "mtu": 8500,
    "directConnectGatewayId": "dcgw-12345678",
    "addressFamily": "ipv4"
  }'

aws directconnect describe-virtual-interfaces
aws directconnect describe-virtual-interfaces --connection-id dxcon-12345678
aws directconnect delete-virtual-interface --virtual-interface-id dxvif-12345678

# --- Direct Connect Gateway ---
aws directconnect create-direct-connect-gateway \
  --direct-connect-gateway-name my-dcgw \
  --amazon-side-asn 64512

aws directconnect describe-direct-connect-gateways
aws directconnect delete-direct-connect-gateway --direct-connect-gateway-id dcgw-12345678

# Associate DXGW with a VGW (for private VIF)
aws directconnect create-direct-connect-gateway-association \
  --direct-connect-gateway-id dcgw-12345678 \
  --gateway-id vgw-12345678

# Associate DXGW with a Transit Gateway
aws directconnect create-direct-connect-gateway-association \
  --direct-connect-gateway-id dcgw-12345678 \
  --gateway-id tgw-12345678 \
  --add-allowed-prefixes-to-direct-connect-gateway \
    cidr=10.0.0.0/8 cidr=172.16.0.0/12

aws directconnect describe-direct-connect-gateway-associations \
  --direct-connect-gateway-id dcgw-12345678

aws directconnect delete-direct-connect-gateway-association \
  --association-id assoc-12345678

# --- Link Aggregation Groups (LAG) ---
aws directconnect create-lag \
  --number-of-connections 2 \
  --location EqDC2 \
  --connections-bandwidth 1Gbps \
  --lag-name my-lag

aws directconnect describe-lags
aws directconnect associate-connection-with-lag \
  --connection-id dxcon-12345678 \
  --lag-id dxlag-12345678

aws directconnect delete-lag --lag-id dxlag-12345678

# --- Describe Locations ---
aws directconnect describe-locations
```
