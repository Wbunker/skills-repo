# Advanced Networking — CLI Reference

This file covers Cloud NAT, Private Service Connect (PSC), Service Directory, Traffic Director, and Network Intelligence Center CLI commands.

---

## Cloud NAT

Cloud NAT is configured as part of a Cloud Router.

```bash
# Create a Cloud Router (if one doesn't exist for this region)
gcloud compute routers create my-nat-router \
  --region=us-central1 \
  --network=my-vpc \
  --description="Router for Cloud NAT"

# Create Cloud NAT — NAT all subnets in the region
gcloud compute routers nats create my-nat-config \
  --router=my-nat-router \
  --router-region=us-central1 \
  --nat-all-subnet-ip-ranges \
  --auto-allocate-nat-external-ips \
  --min-ports-per-vm=64 \
  --description="NAT for all private subnets in us-central1"

# Create Cloud NAT with static external IPs
gcloud compute addresses create my-nat-ip-1 --region=us-central1
gcloud compute addresses create my-nat-ip-2 --region=us-central1

gcloud compute routers nats create my-nat-static \
  --router=my-nat-router \
  --router-region=us-central1 \
  --nat-all-subnet-ip-ranges \
  --nat-external-ip-pool=my-nat-ip-1,my-nat-ip-2

# Create Cloud NAT for specific subnets only
gcloud compute routers nats create my-nat-selective \
  --router=my-nat-router \
  --router-region=us-central1 \
  --nat-custom-subnet-ip-ranges=my-private-subnet,my-gke-subnet \
  --auto-allocate-nat-external-ips

# Create Cloud NAT with dynamic port allocation (better for variable workloads)
gcloud compute routers nats create my-nat-dynamic \
  --router=my-nat-router \
  --router-region=us-central1 \
  --nat-all-subnet-ip-ranges \
  --auto-allocate-nat-external-ips \
  --enable-dynamic-port-allocation \
  --min-ports-per-vm=64 \
  --max-ports-per-vm=4096

# Update NAT config — increase min ports (to address port exhaustion)
gcloud compute routers nats update my-nat-config \
  --router=my-nat-router \
  --router-region=us-central1 \
  --min-ports-per-vm=256

# Enable NAT logging (ERRORS_ONLY is cost-efficient; ALL logs every translation)
gcloud compute routers nats update my-nat-config \
  --router=my-nat-router \
  --router-region=us-central1 \
  --enable-logging \
  --log-filter=ERRORS_ONLY

# Disable logging
gcloud compute routers nats update my-nat-config \
  --router=my-nat-router \
  --router-region=us-central1 \
  --no-enable-logging

# Describe a NAT config
gcloud compute routers describe my-nat-router \
  --region=us-central1 \
  --format="yaml(nats)"

# List all NAT configs (view via router)
gcloud compute routers list --region=us-central1

# Get NAT status (shows port usage, active connections)
gcloud compute routers get-nat-mapping-info my-nat-router \
  --region=us-central1

# Get NAT IP addresses allocated
gcloud compute routers get-nat-mapping-info my-nat-router \
  --region=us-central1 \
  --format="yaml"

# Delete NAT config
gcloud compute routers nats delete my-nat-config \
  --router=my-nat-router \
  --router-region=us-central1
```

---

## Private Service Connect (PSC)

### PSC Endpoints for Google APIs

```bash
# Create a PSC endpoint for Google APIs (all-apis bundle)
# Step 1: Reserve an internal IP address
gcloud compute addresses create my-psc-google-apis-ip \
  --region=us-central1 \
  --subnet=my-private-subnet \
  --purpose=PRIVATE_SERVICE_CONNECT \
  --address=10.10.0.100

# Step 2: Create forwarding rule pointing to Google APIs service
gcloud compute forwarding-rules create my-psc-google-apis \
  --region=us-central1 \
  --address=my-psc-google-apis-ip \
  --target-google-apis-bundle=all-apis \
  --load-balancing-scheme="" \
  --network=my-vpc

# Create PSC endpoint for VPC-SC restricted APIs
gcloud compute addresses create my-psc-vpc-sc-ip \
  --region=us-central1 \
  --subnet=my-private-subnet \
  --purpose=PRIVATE_SERVICE_CONNECT \
  --address=10.10.0.101

gcloud compute forwarding-rules create my-psc-vpc-sc \
  --region=us-central1 \
  --address=my-psc-vpc-sc-ip \
  --target-google-apis-bundle=vpc-sc \
  --load-balancing-scheme="" \
  --network=my-vpc

# Step 3: Create DNS entry to point googleapis.com to PSC endpoint IP
# (Create a private DNS zone and A record)
gcloud dns managed-zones create googleapis-private \
  --dns-name=googleapis.com. \
  --visibility=private \
  --networks=my-vpc \
  --description="Route googleapis.com to PSC endpoint"

gcloud dns record-sets transaction start --zone=googleapis-private
gcloud dns record-sets transaction add "10.10.0.100" \
  --zone=googleapis-private \
  --name="*.googleapis.com." \
  --ttl=300 \
  --type=A
gcloud dns record-sets transaction execute --zone=googleapis-private

# Verify PSC endpoint
gcloud compute forwarding-rules describe my-psc-google-apis \
  --region=us-central1
```

### PSC Service Attachment (Producer Side)

```bash
# Create a service attachment (producer: publishing an internal service via PSC)
# Prerequisites: internal load balancer already created with forwarding rule

# Create service attachment
gcloud compute service-attachments create my-service-attachment \
  --region=us-central1 \
  --producer-forwarding-rule=my-internal-lb-forwarding-rule \
  --connection-preference=ACCEPT_AUTOMATIC \
  --nat-subnets=my-psc-nat-subnet \
  --description="PSC service attachment for my-api"

# Create with explicit consumer accept list
gcloud compute service-attachments create my-service-attachment-restricted \
  --region=us-central1 \
  --producer-forwarding-rule=my-internal-lb-forwarding-rule \
  --connection-preference=ACCEPT_MANUAL \
  --nat-subnets=my-psc-nat-subnet \
  --consumer-accept-list=projects/consumer-project-id=10

# Describe a service attachment (shows the PSC endpoint URL to share with consumers)
gcloud compute service-attachments describe my-service-attachment \
  --region=us-central1

# List service attachments
gcloud compute service-attachments list --region=us-central1

# Accept or reject pending consumer connections (ACCEPT_MANUAL mode)
gcloud compute service-attachments update my-service-attachment-restricted \
  --region=us-central1 \
  --consumer-accept-list=projects/consumer-project-id=20

# Delete a service attachment
gcloud compute service-attachments delete my-service-attachment \
  --region=us-central1
```

### PSC Endpoint for Producer Service (Consumer Side)

```bash
# Create PSC endpoint to connect to a producer service attachment
# Step 1: Reserve an internal IP
gcloud compute addresses create my-psc-consumer-ip \
  --region=us-central1 \
  --subnet=my-consumer-subnet \
  --purpose=PRIVATE_SERVICE_CONNECT \
  --address=10.20.0.50

# Step 2: Create forwarding rule to the producer's service attachment
gcloud compute forwarding-rules create my-psc-consumer-endpoint \
  --region=us-central1 \
  --address=my-psc-consumer-ip \
  --target-service-attachment=projects/producer-project/regions/us-central1/serviceAttachments/my-service-attachment \
  --load-balancing-scheme="" \
  --network=my-consumer-vpc

# Describe the consumer endpoint
gcloud compute forwarding-rules describe my-psc-consumer-endpoint \
  --region=us-central1
```

---

## Service Directory

```bash
# Create a namespace
gcloud service-directory namespaces create production \
  --location=us-central1

gcloud service-directory namespaces create staging \
  --location=us-central1

# List namespaces
gcloud service-directory namespaces list \
  --location=us-central1

# Describe a namespace
gcloud service-directory namespaces describe production \
  --location=us-central1

# Create a service within a namespace
gcloud service-directory services create payments-api \
  --namespace=production \
  --location=us-central1 \
  --annotations="version=v2,team=payments"

# List services in a namespace
gcloud service-directory services list \
  --namespace=production \
  --location=us-central1

# Describe a service
gcloud service-directory services describe payments-api \
  --namespace=production \
  --location=us-central1

# Create an endpoint for a service (IP:port)
gcloud service-directory endpoints create payments-api-endpoint-1 \
  --service=payments-api \
  --namespace=production \
  --location=us-central1 \
  --address=10.10.0.20 \
  --port=8080 \
  --annotations="zone=us-central1-a,healthy=true"

# Create a second endpoint
gcloud service-directory endpoints create payments-api-endpoint-2 \
  --service=payments-api \
  --namespace=production \
  --location=us-central1 \
  --address=10.10.0.21 \
  --port=8080 \
  --annotations="zone=us-central1-b,healthy=true"

# List endpoints for a service
gcloud service-directory endpoints list \
  --service=payments-api \
  --namespace=production \
  --location=us-central1

# Describe an endpoint
gcloud service-directory endpoints describe payments-api-endpoint-1 \
  --service=payments-api \
  --namespace=production \
  --location=us-central1

# Update endpoint (mark unhealthy)
gcloud service-directory endpoints update payments-api-endpoint-1 \
  --service=payments-api \
  --namespace=production \
  --location=us-central1 \
  --annotations="healthy=false"

# Resolve a service (client-side: get current endpoints)
gcloud service-directory services resolve payments-api \
  --namespace=production \
  --location=us-central1

# Delete an endpoint
gcloud service-directory endpoints delete payments-api-endpoint-1 \
  --service=payments-api \
  --namespace=production \
  --location=us-central1

# Delete a service
gcloud service-directory services delete payments-api \
  --namespace=production \
  --location=us-central1

# Delete a namespace
gcloud service-directory namespaces delete production \
  --location=us-central1
```

---

## Network Intelligence Center

### Connectivity Tests

```bash
# Create a connectivity test (VM to VM)
gcloud network-management connectivity-tests create vm-to-vm-test \
  --source-instance=projects/MY_PROJECT/zones/us-central1-a/instances/source-vm \
  --destination-instance=projects/MY_PROJECT/zones/us-central1-b/instances/dest-vm \
  --protocol=TCP \
  --destination-port=8080 \
  --description="Test connectivity from source to destination VM"

# Create a connectivity test (VM to IP address)
gcloud network-management connectivity-tests create vm-to-ip-test \
  --source-instance=projects/MY_PROJECT/zones/us-central1-a/instances/my-vm \
  --destination-ip-address=10.20.0.50 \
  --destination-port=443 \
  --protocol=TCP

# Create a connectivity test (VM to Cloud SQL instance)
gcloud network-management connectivity-tests create vm-to-cloudsql-test \
  --source-instance=projects/MY_PROJECT/zones/us-central1-a/instances/my-vm \
  --destination-cloud-sql-instance=MY_PROJECT:us-central1:my-cloudsql-instance \
  --destination-port=5432 \
  --protocol=TCP

# Create a connectivity test (external IP to load balancer)
gcloud network-management connectivity-tests create external-to-lb-test \
  --source-ip-address=203.0.113.1 \
  --destination-ip-address=34.120.5.10 \
  --destination-port=443 \
  --protocol=TCP

# Create a connectivity test between two GKE pods
gcloud network-management connectivity-tests create gke-pod-test \
  --source-gke-master-cluster=projects/MY_PROJECT/locations/us-central1/clusters/my-cluster \
  --source-ip-address=10.20.0.100 \
  --destination-ip-address=10.20.0.200 \
  --destination-port=8080 \
  --protocol=TCP

# Run a connectivity test (re-run after changes)
gcloud network-management connectivity-tests rerun vm-to-vm-test

# List connectivity tests
gcloud network-management connectivity-tests list

# Describe a connectivity test (view results and trace)
gcloud network-management connectivity-tests describe vm-to-vm-test

# View results in detail (trace steps, blocking point)
gcloud network-management connectivity-tests describe vm-to-vm-test \
  --format="yaml(reachabilityDetails)"

# Delete a connectivity test
gcloud network-management connectivity-tests delete vm-to-vm-test
```

### Firewall Insights

```bash
# Enable firewall insights (requires setting observation period)
# Firewall Insights is configured in Cloud Console; use Cloud Monitoring for metrics

# Query firewall insights via Cloud Logging (shadowed rules, unused rules)
gcloud logging read \
  'resource.type="gce_firewall_rule" AND
   logName="projects/MY_PROJECT/logs/firewallinsights.googleapis.com%2Ffirewall_hit_count"' \
  --project=MY_PROJECT \
  --limit=20

# Get firewall insights data via recommender (for overly permissive rules)
gcloud recommender recommendations list \
  --recommender=google.compute.firewall.Recommender \
  --location=global \
  --project=MY_PROJECT \
  --format="table(name,description,primaryImpact.category,stateInfo.state)"

# Describe a specific firewall recommendation
gcloud recommender recommendations describe RECOMMENDATION_ID \
  --recommender=google.compute.firewall.Recommender \
  --location=global \
  --project=MY_PROJECT

# Mark a recommendation as accepted (apply the change yourself, then mark)
gcloud recommender recommendations mark-succeeded RECOMMENDATION_ID \
  --recommender=google.compute.firewall.Recommender \
  --location=global \
  --project=MY_PROJECT \
  --etag=ETAG

# Mark as dismissed (not applicable)
gcloud recommender recommendations mark-dismissed RECOMMENDATION_ID \
  --recommender=google.compute.firewall.Recommender \
  --location=global \
  --project=MY_PROJECT \
  --etag=ETAG
```

### Network Topology (View via Console or API)

```bash
# Network Topology is primarily a Cloud Console visual tool
# Access via: https://console.cloud.google.com/networking/networkintelligence/topology

# Query topology metrics via Cloud Monitoring
gcloud monitoring metrics list \
  --filter="metric.type=networking.googleapis.com/topology"
```

### VPC Flow Logs (Network Intelligence)

```bash
# Query VPC flow logs in Cloud Logging
gcloud logging read \
  'resource.type="gce_subnetwork" AND
   logName="projects/MY_PROJECT/logs/compute.googleapis.com%2Fvpc_flows"' \
  --project=MY_PROJECT \
  --limit=50 \
  --format=json

# Query for flows from a specific source IP
gcloud logging read \
  'resource.type="gce_subnetwork" AND
   jsonPayload.connection.src_ip="10.10.0.5"' \
  --project=MY_PROJECT \
  --limit=20

# Query for flows to a specific destination port
gcloud logging read \
  'resource.type="gce_subnetwork" AND
   jsonPayload.connection.dest_port=443' \
  --project=MY_PROJECT \
  --limit=20
```
