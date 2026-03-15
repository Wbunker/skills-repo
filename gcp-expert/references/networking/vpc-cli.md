# VPC — CLI Reference

---

## Networks

```bash
# Create a custom mode VPC network
gcloud compute networks create my-vpc \
  --subnet-mode=custom \
  --bgp-routing-mode=regional \
  --description="Production VPC"

# Create with global BGP routing (allows dynamic routes to propagate across all regions)
gcloud compute networks create my-global-vpc \
  --subnet-mode=custom \
  --bgp-routing-mode=global

# Describe a network
gcloud compute networks describe my-vpc

# List all networks in the project
gcloud compute networks list

# List with specific fields
gcloud compute networks list \
  --format="table(name,subnetMode,bgpRoutingMode,autoCreateSubnetworks)"

# Convert auto-mode network to custom (irreversible)
gcloud compute networks update my-auto-vpc \
  --switch-to-custom-subnet-mode

# Update BGP routing mode
gcloud compute networks update my-vpc \
  --bgp-routing-mode=global

# Delete a network
gcloud compute networks delete my-vpc
```

---

## Subnets

```bash
# Create a subnet
gcloud compute networks subnets create my-subnet-us \
  --network=my-vpc \
  --region=us-central1 \
  --range=10.10.0.0/24 \
  --description="US Central subnet"

# Create subnet with Private Google Access enabled
gcloud compute networks subnets create my-subnet-us-pga \
  --network=my-vpc \
  --region=us-central1 \
  --range=10.10.1.0/24 \
  --enable-private-ip-google-access

# Create subnet with VPC flow logs enabled
gcloud compute networks subnets create my-subnet-with-logs \
  --network=my-vpc \
  --region=us-central1 \
  --range=10.10.2.0/24 \
  --enable-flow-logs \
  --logging-aggregation-interval=interval-5-sec \
  --logging-flow-sampling=0.5 \
  --logging-metadata=include-all

# Create subnet with secondary ranges (for GKE pods and services)
gcloud compute networks subnets create my-gke-subnet \
  --network=my-vpc \
  --region=us-central1 \
  --range=10.10.3.0/24 \
  --secondary-range=pods=10.20.0.0/16,services=10.30.0.0/20

# Create dual-stack IPv4+IPv6 subnet (internal IPv6)
gcloud compute networks subnets create my-dual-stack-subnet \
  --network=my-vpc \
  --region=us-central1 \
  --range=10.10.4.0/24 \
  --stack-type=IPV4_IPV6 \
  --ipv6-access-type=INTERNAL

# Create subnet with external IPv6
gcloud compute networks subnets create my-ext-ipv6-subnet \
  --network=my-vpc \
  --region=us-central1 \
  --range=10.10.5.0/24 \
  --stack-type=IPV4_IPV6 \
  --ipv6-access-type=EXTERNAL

# Describe a subnet
gcloud compute networks subnets describe my-subnet-us \
  --region=us-central1

# List subnets in a region
gcloud compute networks subnets list \
  --regions=us-central1

# List all subnets for a network
gcloud compute networks subnets list \
  --filter="network:my-vpc"

# Expand subnet CIDR range (can only expand, not shrink)
gcloud compute networks subnets expand-ip-range my-subnet-us \
  --region=us-central1 \
  --prefix-length=22

# Add secondary range to existing subnet
gcloud compute networks subnets update my-gke-subnet \
  --region=us-central1 \
  --add-secondary-ranges=pods2=10.40.0.0/16

# Enable/disable Private Google Access
gcloud compute networks subnets update my-subnet-us \
  --region=us-central1 \
  --enable-private-ip-google-access

gcloud compute networks subnets update my-subnet-us \
  --region=us-central1 \
  --no-enable-private-ip-google-access

# Enable flow logs on existing subnet
gcloud compute networks subnets update my-subnet-us \
  --region=us-central1 \
  --enable-flow-logs \
  --logging-aggregation-interval=interval-30-sec \
  --logging-flow-sampling=0.5

# Disable flow logs
gcloud compute networks subnets update my-subnet-us \
  --region=us-central1 \
  --no-enable-flow-logs

# Delete a subnet
gcloud compute networks subnets delete my-subnet-us \
  --region=us-central1
```

---

## Firewall Rules

```bash
# Allow SSH from a specific IP range (tag-based target)
gcloud compute firewall-rules create allow-ssh-from-office \
  --network=my-vpc \
  --direction=INGRESS \
  --priority=1000 \
  --action=ALLOW \
  --rules=tcp:22 \
  --source-ranges=203.0.113.0/24 \
  --target-tags=ssh-access \
  --description="Allow SSH from office IP range"

# Allow HTTPS from the internet to web servers (tag-based)
gcloud compute firewall-rules create allow-https-external \
  --network=my-vpc \
  --direction=INGRESS \
  --priority=1000 \
  --action=ALLOW \
  --rules=tcp:443 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=web-server

# Allow HTTP and HTTPS
gcloud compute firewall-rules create allow-http-https \
  --network=my-vpc \
  --direction=INGRESS \
  --priority=1000 \
  --action=ALLOW \
  --rules=tcp:80,tcp:443 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=web-server

# Allow internal traffic within VPC
gcloud compute firewall-rules create allow-internal \
  --network=my-vpc \
  --direction=INGRESS \
  --priority=65534 \
  --action=ALLOW \
  --rules=all \
  --source-ranges=10.0.0.0/8

# Allow health check traffic from Google LB probers
gcloud compute firewall-rules create allow-health-checks \
  --network=my-vpc \
  --direction=INGRESS \
  --priority=1000 \
  --action=ALLOW \
  --rules=tcp \
  --source-ranges=130.211.0.0/22,35.191.0.0/16 \
  --target-tags=web-server

# Service account-based firewall rule (app server → database)
gcloud compute firewall-rules create allow-app-to-db \
  --network=my-vpc \
  --direction=INGRESS \
  --priority=1000 \
  --action=ALLOW \
  --rules=tcp:5432 \
  --source-service-accounts=myapp@my-project.iam.gserviceaccount.com \
  --target-service-accounts=mydb@my-project.iam.gserviceaccount.com

# Deny a specific IP range (higher priority than allow rules)
gcloud compute firewall-rules create deny-known-bad-ips \
  --network=my-vpc \
  --direction=INGRESS \
  --priority=500 \
  --action=DENY \
  --rules=all \
  --source-ranges=192.0.2.0/24

# Allow egress to specific destinations only (deny-all egress + specific allows)
gcloud compute firewall-rules create deny-all-egress \
  --network=my-vpc \
  --direction=EGRESS \
  --priority=65534 \
  --action=DENY \
  --rules=all \
  --destination-ranges=0.0.0.0/0 \
  --target-tags=restricted-vm

gcloud compute firewall-rules create allow-egress-to-db \
  --network=my-vpc \
  --direction=EGRESS \
  --priority=1000 \
  --action=ALLOW \
  --rules=tcp:5432 \
  --destination-ranges=10.10.0.0/24 \
  --target-tags=restricted-vm

# Enable firewall rule logging on an existing rule
gcloud compute firewall-rules update allow-ssh-from-office \
  --enable-logging

# Describe a firewall rule
gcloud compute firewall-rules describe allow-https-external

# List all firewall rules for a network
gcloud compute firewall-rules list \
  --filter="network:my-vpc" \
  --format="table(name,direction,priority,sourceRanges,targetTags,allowed)"

# Delete a firewall rule
gcloud compute firewall-rules delete allow-ssh-from-office
```

---

## Routes

```bash
# List all routes
gcloud compute routes list

# List routes for a specific network
gcloud compute routes list \
  --filter="network:my-vpc"

# Create a static route to on-premises via VPN gateway
gcloud compute routes create route-to-onprem \
  --network=my-vpc \
  --destination-range=192.168.0.0/16 \
  --next-hop-vpn-tunnel=my-vpn-tunnel \
  --next-hop-vpn-tunnel-region=us-central1 \
  --priority=100

# Create a static route to an instance (e.g., NAT appliance)
gcloud compute routes create route-via-nat-appliance \
  --network=my-vpc \
  --destination-range=0.0.0.0/0 \
  --next-hop-instance=my-nat-vm \
  --next-hop-instance-zone=us-central1-a \
  --priority=900 \
  --tags=needs-nat

# Create a blackhole route (drop traffic to a range)
gcloud compute routes create blackhole-bad-range \
  --network=my-vpc \
  --destination-range=198.51.100.0/24

# Describe a route
gcloud compute routes describe route-to-onprem

# Delete a route
gcloud compute routes delete route-to-onprem
```

---

## VPC Peering

```bash
# Create peering from VPC-A to VPC-B (must also run from VPC-B side)
gcloud compute networks peerings create peer-a-to-b \
  --network=vpc-a \
  --peer-project=project-b \
  --peer-network=vpc-b \
  --export-custom-routes \
  --import-custom-routes

# Create peering from VPC-B to VPC-A (project-b runs this)
gcloud compute networks peerings create peer-b-to-a \
  --network=vpc-b \
  --peer-project=project-a \
  --peer-network=vpc-a \
  --export-custom-routes \
  --import-custom-routes

# List peerings for a network
gcloud compute networks peerings list \
  --network=vpc-a

# Describe a peering
gcloud compute networks peerings describe peer-a-to-b \
  --network=vpc-a

# Update peering (enable/disable route exchange)
gcloud compute networks peerings update peer-a-to-b \
  --network=vpc-a \
  --export-custom-routes \
  --import-custom-routes

# Delete a peering
gcloud compute networks peerings delete peer-a-to-b \
  --network=vpc-a
```

---

## Shared VPC

```bash
# Enable Shared VPC on a host project (run as Organization Admin)
gcloud compute shared-vpc enable my-host-project

# Associate a service project with the host project
gcloud compute shared-vpc associated-projects add my-service-project \
  --host-project=my-host-project

# List service projects associated with a host
gcloud compute shared-vpc associated-projects list \
  --host-project=my-host-project

# Get Shared VPC status for a project
gcloud compute shared-vpc get-host-project my-service-project

# Remove a service project from Shared VPC
gcloud compute shared-vpc associated-projects remove my-service-project \
  --host-project=my-host-project

# Disable Shared VPC on the host project
gcloud compute shared-vpc disable my-host-project

# Grant subnet-level IAM to a service project's service account (for specific subnet access)
gcloud compute networks subnets add-iam-policy-binding my-shared-subnet \
  --region=us-central1 \
  --project=my-host-project \
  --member="serviceAccount:SERVICE_ACCOUNT@my-service-project.iam.gserviceaccount.com" \
  --role="roles/compute.networkUser"
```

---

## Network Tags (on Instances)

```bash
# Add network tags when creating a VM
gcloud compute instances create my-web-vm \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --tags=web-server,ssh-access \
  --network=my-vpc \
  --subnet=my-subnet-us

# Add tags to an existing VM
gcloud compute instances add-tags my-web-vm \
  --zone=us-central1-a \
  --tags=monitoring,backup-agent

# Remove tags from a VM
gcloud compute instances remove-tags my-web-vm \
  --zone=us-central1-a \
  --tags=backup-agent

# List instances with a specific tag
gcloud compute instances list \
  --filter="tags.items=web-server"
```
