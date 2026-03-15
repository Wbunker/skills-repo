# Hybrid Connectivity — CLI Reference

---

## Cloud Interconnect — Dedicated

```bash
# List available Interconnect locations (Google PoPs)
gcloud compute interconnects locations list

# Describe a specific location
gcloud compute interconnects locations describe sjc-zone1-1890

# Create a Dedicated Interconnect (request physical circuit at a PoP)
# NOTE: This creates a request; Google must fulfill the physical cross-connect
gcloud compute interconnects create my-interconnect \
  --location=sjc-zone1-1890 \
  --link-type=LINK_TYPE_ETHERNET_10G_LR \
  --requested-link-count=2 \
  --description="Primary Dedicated Interconnect" \
  --noc-contact-email=noc@example.com

# Available link types:
# LINK_TYPE_ETHERNET_10G_LR (10 Gbps)
# LINK_TYPE_ETHERNET_100G_LR (100 Gbps)

# Describe a Dedicated Interconnect (check provisioning status, get LOA)
gcloud compute interconnects describe my-interconnect

# List all Interconnect resources
gcloud compute interconnects list

# Delete an Interconnect
gcloud compute interconnects delete my-interconnect
```

### Dedicated Interconnect VLAN Attachments

```bash
# Create a Cloud Router (required for VLAN attachments with BGP)
gcloud compute routers create my-cloud-router \
  --region=us-central1 \
  --network=my-vpc \
  --asn=65001 \
  --description="Cloud Router for Interconnect"

# Create a Dedicated Interconnect VLAN attachment
gcloud compute interconnects attachments dedicated create my-vlan-attachment \
  --interconnect=my-interconnect \
  --region=us-central1 \
  --router=my-cloud-router \
  --description="Primary VLAN attachment" \
  --vlan=100 \
  --bandwidth=BPS_1G

# Available bandwidth options:
# BPS_50M, BPS_100M, BPS_200M, BPS_300M, BPS_400M, BPS_500M
# BPS_1G, BPS_2G, BPS_5G, BPS_10G, BPS_20G, BPS_50G

# Describe a VLAN attachment (check state, BGP peer info)
gcloud compute interconnects attachments describe my-vlan-attachment \
  --region=us-central1

# List all VLAN attachments
gcloud compute interconnects attachments list --region=us-central1

# Delete a VLAN attachment
gcloud compute interconnects attachments delete my-vlan-attachment \
  --region=us-central1
```

---

## Cloud Interconnect — Partner

```bash
# List available Partner Interconnect locations and providers
gcloud compute interconnects locations list
# Each location shows edge-availability-domain (EAD) for redundancy planning

# Create a Partner Interconnect VLAN attachment
# This generates a pairing key to share with your service provider
gcloud compute interconnects attachments partner create my-partner-attachment \
  --region=us-central1 \
  --router=my-cloud-router \
  --description="Partner Interconnect attachment" \
  --edge-availability-domain=availability-domain-1

# After creating, get the pairing key to give to your service provider
gcloud compute interconnects attachments describe my-partner-attachment \
  --region=us-central1 \
  --format="value(pairingKey)"

# After provider activates the circuit, describe to verify status
gcloud compute interconnects attachments describe my-partner-attachment \
  --region=us-central1

# Delete a Partner Interconnect attachment
gcloud compute interconnects attachments delete my-partner-attachment \
  --region=us-central1
```

---

## HA VPN

### VPN Gateways

```bash
# Create an HA VPN gateway (Google-managed; two interfaces with two external IPs)
gcloud compute vpn-gateways create my-ha-vpn-gateway \
  --network=my-vpc \
  --region=us-central1 \
  --description="HA VPN gateway for on-prem connectivity"

# Describe an HA VPN gateway (shows two external IP addresses)
gcloud compute vpn-gateways describe my-ha-vpn-gateway \
  --region=us-central1

# List HA VPN gateways
gcloud compute vpn-gateways list --region=us-central1

# Delete an HA VPN gateway
gcloud compute vpn-gateways delete my-ha-vpn-gateway \
  --region=us-central1
```

### External VPN Gateways (Peer Device)

```bash
# Create an external VPN gateway resource (represents the on-prem device)
# Single-interface peer (one external IP on peer device)
gcloud compute external-vpn-gateways create my-onprem-vpn-gw \
  --interfaces=0=203.0.113.10 \
  --description="On-premises Cisco ASA"

# Dual-interface peer (two external IPs for redundancy)
gcloud compute external-vpn-gateways create my-onprem-vpn-gw-ha \
  --interfaces=0=203.0.113.10,1=203.0.113.11 \
  --description="On-premises redundant firewalls"

# Describe an external VPN gateway
gcloud compute external-vpn-gateways describe my-onprem-vpn-gw

# List external VPN gateways
gcloud compute external-vpn-gateways list

# Delete an external VPN gateway
gcloud compute external-vpn-gateways delete my-onprem-vpn-gw
```

### VPN Tunnels

```bash
# Create VPN tunnels (two tunnels required for HA VPN 99.99% SLA)
# Tunnel 1: GCP interface 0 → peer interface 0
gcloud compute vpn-tunnels create my-vpn-tunnel-1 \
  --vpn-gateway=my-ha-vpn-gateway \
  --vpn-gateway-region=us-central1 \
  --interface=0 \
  --peer-external-gateway=my-onprem-vpn-gw \
  --peer-external-gateway-interface=0 \
  --shared-secret="STRONG_PRE_SHARED_KEY_1" \
  --ike-version=2 \
  --router=my-cloud-router \
  --region=us-central1 \
  --description="HA VPN tunnel 1"

# Tunnel 2: GCP interface 1 → peer interface 0 (or interface 1 if dual-homed peer)
gcloud compute vpn-tunnels create my-vpn-tunnel-2 \
  --vpn-gateway=my-ha-vpn-gateway \
  --vpn-gateway-region=us-central1 \
  --interface=1 \
  --peer-external-gateway=my-onprem-vpn-gw \
  --peer-external-gateway-interface=0 \
  --shared-secret="STRONG_PRE_SHARED_KEY_2" \
  --ike-version=2 \
  --router=my-cloud-router \
  --region=us-central1 \
  --description="HA VPN tunnel 2"

# Describe a VPN tunnel (check status, GCP external IP)
gcloud compute vpn-tunnels describe my-vpn-tunnel-1 \
  --region=us-central1

# List VPN tunnels
gcloud compute vpn-tunnels list --region=us-central1

# Get tunnel status (look for ESTABLISHED)
gcloud compute vpn-tunnels list \
  --region=us-central1 \
  --format="table(name,status,detailedStatus)"

# Delete a VPN tunnel
gcloud compute vpn-tunnels delete my-vpn-tunnel-1 \
  --region=us-central1
```

---

## Cloud Router

```bash
# Create a Cloud Router
gcloud compute routers create my-cloud-router \
  --region=us-central1 \
  --network=my-vpc \
  --asn=65001 \
  --description="Cloud Router for hybrid connectivity"

# Describe a Cloud Router (view BGP peers, advertised routes, NAT configs)
gcloud compute routers describe my-cloud-router \
  --region=us-central1

# List Cloud Routers
gcloud compute routers list --region=us-central1

# Add BGP peer for VPN tunnel (configure after tunnel creation)
gcloud compute routers add-bgp-peer my-cloud-router \
  --region=us-central1 \
  --peer-name=bgp-peer-tunnel-1 \
  --interface=my-vpn-tunnel-1 \
  --peer-ip-address=169.254.1.2 \
  --my-ip-address=169.254.1.1 \
  --peer-asn=65002

# Add BGP peer for second tunnel
gcloud compute routers add-bgp-peer my-cloud-router \
  --region=us-central1 \
  --peer-name=bgp-peer-tunnel-2 \
  --interface=my-vpn-tunnel-2 \
  --peer-ip-address=169.254.2.2 \
  --my-ip-address=169.254.2.1 \
  --peer-asn=65002

# Update BGP peer (e.g., change advertised route priority)
gcloud compute routers update-bgp-peer my-cloud-router \
  --region=us-central1 \
  --peer-name=bgp-peer-tunnel-1 \
  --advertised-route-priority=100

# Enable BFD (Bidirectional Forwarding Detection) for fast failover
gcloud compute routers update-bgp-peer my-cloud-router \
  --region=us-central1 \
  --peer-name=bgp-peer-tunnel-1 \
  --enable-bfd \
  --bfd-min-receive-interval=300 \
  --bfd-min-transmit-interval=300 \
  --bfd-multiplier=5

# Add custom route advertisement (advertise specific CIDR to on-prem)
gcloud compute routers update my-cloud-router \
  --region=us-central1 \
  --advertisement-mode=CUSTOM \
  --set-advertisement-groups=ALL_SUBNETS \
  --set-advertisement-ranges=199.36.153.8/30="Private Google Access"

# Remove a BGP peer
gcloud compute routers remove-bgp-peer my-cloud-router \
  --region=us-central1 \
  --peer-name=bgp-peer-tunnel-1

# Get BGP peer status (active routes)
gcloud compute routers get-status my-cloud-router \
  --region=us-central1

# View learned routes from BGP peer
gcloud compute routers get-status my-cloud-router \
  --region=us-central1 \
  --format="yaml(result.bgpPeerStatus)"

# Delete a Cloud Router
gcloud compute routers delete my-cloud-router \
  --region=us-central1
```

### Cloud Router NAT

```bash
# Add Cloud NAT to a Cloud Router
gcloud compute routers nats create my-nat-config \
  --router=my-cloud-router \
  --router-region=us-central1 \
  --nat-all-subnet-ip-ranges \
  --auto-allocate-nat-external-ips

# Add Cloud NAT with specific subnet
gcloud compute routers nats create my-nat-restricted \
  --router=my-cloud-router \
  --router-region=us-central1 \
  --nat-custom-subnet-ip-ranges=my-private-subnet \
  --auto-allocate-nat-external-ips

# Add Cloud NAT with static external IPs
gcloud compute addresses create my-nat-ip-1 --region=us-central1
gcloud compute routers nats create my-nat-static \
  --router=my-cloud-router \
  --router-region=us-central1 \
  --nat-all-subnet-ip-ranges \
  --nat-external-ip-pool=my-nat-ip-1

# Update NAT config (increase min ports per VM)
gcloud compute routers nats update my-nat-config \
  --router=my-cloud-router \
  --router-region=us-central1 \
  --min-ports-per-vm=128

# Enable NAT logging
gcloud compute routers nats update my-nat-config \
  --router=my-cloud-router \
  --router-region=us-central1 \
  --enable-logging \
  --log-filter=ERRORS_ONLY

# Describe NAT config
gcloud compute routers describe my-cloud-router \
  --region=us-central1 \
  --format="yaml(nats)"

# Delete NAT config
gcloud compute routers nats delete my-nat-config \
  --router=my-cloud-router \
  --router-region=us-central1
```

---

## Network Connectivity Center (NCC)

```bash
# Create an NCC Hub
gcloud network-connectivity hubs create my-ncc-hub \
  --description="Central hub for hybrid connectivity"

# Describe a hub
gcloud network-connectivity hubs describe my-ncc-hub

# List hubs
gcloud network-connectivity hubs list

# Create a VPN spoke (connect HA VPN tunnels to the hub)
gcloud network-connectivity spokes linked-vpn-tunnels create my-vpn-spoke \
  --hub=my-ncc-hub \
  --region=us-central1 \
  --vpn-tunnels=my-vpn-tunnel-1,my-vpn-tunnel-2 \
  --description="VPN spoke for on-prem connectivity"

# Create an Interconnect spoke
gcloud network-connectivity spokes linked-interconnect-attachments create my-interconnect-spoke \
  --hub=my-ncc-hub \
  --region=us-central1 \
  --interconnect-attachments=my-vlan-attachment \
  --description="Interconnect spoke"

# Create a VPC spoke (connect a VPC to the hub)
gcloud network-connectivity spokes linked-vpc-network create my-vpc-spoke \
  --hub=my-ncc-hub \
  --vpc-network=projects/MY_PROJECT/global/networks/my-vpc \
  --description="VPC spoke"

# Create a Router Appliance spoke (for SD-WAN appliance)
gcloud network-connectivity spokes linked-router-appliances create my-sdwan-spoke \
  --hub=my-ncc-hub \
  --region=us-central1 \
  --router-appliance=instance=projects/MY_PROJECT/zones/us-central1-a/instances/my-sdwan-vm,ip=10.10.0.5 \
  --description="SD-WAN appliance spoke"

# Describe a spoke
gcloud network-connectivity spokes describe my-vpn-spoke \
  --region=us-central1

# List spokes
gcloud network-connectivity spokes list --region=us-central1

# List all spokes globally
gcloud network-connectivity spokes list

# Delete a spoke
gcloud network-connectivity spokes delete my-vpn-spoke \
  --region=us-central1

# Delete a hub (all spokes must be deleted first)
gcloud network-connectivity hubs delete my-ncc-hub
```
