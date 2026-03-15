# Google Compute Engine — CLI Reference

Capabilities reference: [gce-capabilities.md](gce-capabilities.md)

All commands use `gcloud compute` unless otherwise noted. Set project and zone defaults to avoid repeating flags:

```bash
gcloud config set project my-project-id
gcloud config set compute/zone us-central1-a
gcloud config set compute/region us-central1
```

---

## Instances

### Create an Instance

```bash
# Basic instance
gcloud compute instances create my-vm \
  --machine-type=n2-standard-4 \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-ssd \
  --zone=us-central1-a

# With custom service account, network, and tags
gcloud compute instances create my-app-vm \
  --machine-type=n2-standard-8 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=100GB \
  --boot-disk-type=pd-balanced \
  --subnet=projects/my-project/regions/us-central1/subnetworks/my-subnet \
  --no-address \
  --service-account=my-sa@my-project.iam.gserviceaccount.com \
  --scopes=cloud-platform \
  --tags=web-server,allow-health-check \
  --metadata=startup-script='#!/bin/bash
apt-get update && apt-get install -y nginx' \
  --zone=us-central1-a

# Custom machine type
gcloud compute instances create my-custom-vm \
  --machine-type=n2-custom-6-20480 \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --zone=us-central1-a

# Spot VM
gcloud compute instances create my-spot-vm \
  --machine-type=n2-standard-4 \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --provisioning-model=SPOT \
  --instance-termination-action=STOP \
  --zone=us-central1-a

# Confidential VM (AMD SEV)
gcloud compute instances create my-confidential-vm \
  --machine-type=n2d-standard-4 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --confidential-compute \
  --maintenance-policy=TERMINATE \
  --zone=us-central1-a

# Shielded VM
gcloud compute instances create my-shielded-vm \
  --machine-type=n2-standard-4 \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --shielded-secure-boot \
  --shielded-vtpm \
  --shielded-integrity-monitoring \
  --zone=us-central1-a

# With additional data disk
gcloud compute instances create my-db-vm \
  --machine-type=n2-standard-8 \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --boot-disk-size=50GB \
  --create-disk=name=my-db-vm-data,size=500GB,type=pd-ssd,auto-delete=no \
  --zone=us-central1-a

# From instance template
gcloud compute instances create my-vm-from-template \
  --source-instance-template=my-instance-template \
  --zone=us-central1-a

# With startup script from GCS
gcloud compute instances create my-vm \
  --machine-type=e2-standard-4 \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --metadata=startup-script-url=gs://my-bucket/startup.sh \
  --zone=us-central1-a

# With GPU
gcloud compute instances create my-gpu-vm \
  --machine-type=a2-highgpu-1g \
  --image-family=common-cu121-debian-11-py310 \
  --image-project=deeplearning-platform-release \
  --accelerator=type=nvidia-tesla-a100,count=1 \
  --maintenance-policy=TERMINATE \
  --boot-disk-size=200GB \
  --zone=us-central1-a
```

### Describe and List Instances

```bash
# Describe a single instance
gcloud compute instances describe my-vm --zone=us-central1-a

# List all instances in the project
gcloud compute instances list

# List with filter and format
gcloud compute instances list \
  --filter="zone:(us-central1-a us-central1-b) AND status=RUNNING" \
  --format="table(name,machineType.basename(),status,networkInterfaces[0].networkIP)"

# List instances with a specific tag
gcloud compute instances list --filter="tags.items=web-server"

# List and output as JSON for scripting
gcloud compute instances list --format=json | jq '.[].name'

# Get instance external IP
gcloud compute instances describe my-vm \
  --zone=us-central1-a \
  --format="get(networkInterfaces[0].accessConfigs[0].natIP)"
```

### Start, Stop, Reset, Suspend

```bash
# Stop an instance
gcloud compute instances stop my-vm --zone=us-central1-a

# Start a stopped instance
gcloud compute instances start my-vm --zone=us-central1-a

# Reset (hard reboot)
gcloud compute instances reset my-vm --zone=us-central1-a

# Suspend (saves to disk, cheaper than stopped)
gcloud compute instances suspend my-vm --zone=us-central1-a

# Resume from suspend
gcloud compute instances resume my-vm --zone=us-central1-a
```

### Update Instances

```bash
# Add/update metadata
gcloud compute instances add-metadata my-vm \
  --metadata=key1=value1,key2=value2 \
  --zone=us-central1-a

# Remove metadata key
gcloud compute instances remove-metadata my-vm \
  --keys=key1 \
  --zone=us-central1-a

# Add tags
gcloud compute instances add-tags my-vm \
  --tags=allow-lb-health-check,web-server \
  --zone=us-central1-a

# Remove tags
gcloud compute instances remove-tags my-vm \
  --tags=old-tag \
  --zone=us-central1-a

# Update machine type (instance must be stopped)
gcloud compute instances stop my-vm --zone=us-central1-a
gcloud compute instances set-machine-type my-vm \
  --machine-type=n2-standard-8 \
  --zone=us-central1-a
gcloud compute instances start my-vm --zone=us-central1-a

# Set service account
gcloud compute instances set-service-account my-vm \
  --service-account=my-sa@my-project.iam.gserviceaccount.com \
  --scopes=cloud-platform \
  --zone=us-central1-a
```

### Delete Instances

```bash
# Delete an instance (retains boot disk by default if auto-delete=no)
gcloud compute instances delete my-vm --zone=us-central1-a

# Delete without prompt
gcloud compute instances delete my-vm --zone=us-central1-a --quiet

# Delete multiple instances
gcloud compute instances delete vm1 vm2 vm3 --zone=us-central1-a --quiet
```

---

## Instance Templates

```bash
# Create an instance template
gcloud compute instance-templates create my-template \
  --machine-type=n2-standard-4 \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-balanced \
  --tags=web-server \
  --service-account=my-sa@my-project.iam.gserviceaccount.com \
  --scopes=cloud-platform \
  --metadata=startup-script='#!/bin/bash
apt-get update -y && apt-get install -y nginx
systemctl enable nginx && systemctl start nginx'

# Create template with no external IP
gcloud compute instance-templates create my-private-template \
  --machine-type=n2-standard-4 \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --no-address \
  --subnet=my-subnet \
  --region=us-central1

# Create regional template (can reference regional resources like regional subnets)
gcloud compute instance-templates create my-regional-template \
  --machine-type=n2-standard-4 \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --instance-template-region=us-central1

# Create template from existing instance
gcloud compute instances export my-vm \
  --destination-file=vm-config.yaml \
  --zone=us-central1-a

# List templates
gcloud compute instance-templates list

# Describe a template
gcloud compute instance-templates describe my-template

# Delete a template
gcloud compute instance-templates delete my-template --quiet
```

---

## Managed Instance Groups (MIGs)

```bash
# Create a zonal MIG
gcloud compute instance-groups managed create my-mig \
  --template=my-template \
  --size=3 \
  --zone=us-central1-a

# Create a regional MIG (distributes across zones)
gcloud compute instance-groups managed create my-regional-mig \
  --template=my-template \
  --size=6 \
  --region=us-central1

# List MIGs
gcloud compute instance-groups managed list

# Describe a MIG
gcloud compute instance-groups managed describe my-mig --zone=us-central1-a

# List instances in a MIG
gcloud compute instance-groups managed list-instances my-mig --zone=us-central1-a

# Set autoscaling
gcloud compute instance-groups managed set-autoscaling my-mig \
  --max-num-replicas=20 \
  --min-num-replicas=2 \
  --target-cpu-utilization=0.6 \
  --cool-down-period=90 \
  --zone=us-central1-a

# Autoscaling based on Cloud Monitoring metric
gcloud compute instance-groups managed set-autoscaling my-mig \
  --max-num-replicas=30 \
  --min-num-replicas=2 \
  --custom-metric-utilization=metric=custom.googleapis.com/myapp/queue_depth,utilization-target=10,utilization-target-type=GAUGE \
  --zone=us-central1-a

# Stop autoscaling
gcloud compute instance-groups managed stop-autoscaling my-mig --zone=us-central1-a

# Set autohealing with health check
gcloud compute health-checks create http my-health-check \
  --port=80 \
  --request-path=/health \
  --check-interval=10s \
  --timeout=5s \
  --healthy-threshold=1 \
  --unhealthy-threshold=3

gcloud compute instance-groups managed update my-mig \
  --health-check=my-health-check \
  --initial-delay=120 \
  --zone=us-central1-a

# Rolling update to new template
gcloud compute instance-groups managed rolling-action start-update my-mig \
  --version=template=my-new-template \
  --max-surge=3 \
  --max-unavailable=0 \
  --zone=us-central1-a

# Canary update (10% on new template)
gcloud compute instance-groups managed rolling-action start-update my-mig \
  --version=template=my-old-template \
  --canary-version=template=my-new-template,target-size=10% \
  --zone=us-central1-a

# Check rolling update status
gcloud compute instance-groups managed describe my-mig \
  --zone=us-central1-a \
  --format="get(updatePolicy,status.versionTarget)"

# Resize a MIG
gcloud compute instance-groups managed resize my-mig --size=10 --zone=us-central1-a

# Recreate specific instances in a MIG
gcloud compute instance-groups managed recreate-instances my-mig \
  --instances=my-mig-abc1,my-mig-xyz2 \
  --zone=us-central1-a

# Delete a MIG
gcloud compute instance-groups managed delete my-mig --zone=us-central1-a --quiet
```

---

## Disks & Snapshots

```bash
# Create a standalone persistent disk
gcloud compute disks create my-data-disk \
  --size=500GB \
  --type=pd-ssd \
  --zone=us-central1-a

# Create a Hyperdisk Balanced with custom IOPS/throughput
gcloud compute disks create my-hyperdisk \
  --size=1TB \
  --type=hyperdisk-balanced \
  --provisioned-iops=10000 \
  --provisioned-throughput=500 \
  --zone=us-central1-a

# Create regional persistent disk (replicated across 2 zones)
gcloud compute disks create my-regional-disk \
  --size=200GB \
  --type=pd-ssd \
  --region=us-central1 \
  --replica-zones=us-central1-a,us-central1-b

# Attach an existing disk to an instance
gcloud compute instances attach-disk my-vm \
  --disk=my-data-disk \
  --mode=rw \
  --zone=us-central1-a

# Attach disk as read-only (can be attached to multiple instances)
gcloud compute instances attach-disk my-vm \
  --disk=my-shared-disk \
  --mode=ro \
  --zone=us-central1-a

# Detach a disk
gcloud compute instances detach-disk my-vm \
  --disk=my-data-disk \
  --zone=us-central1-a

# Resize a disk (can only grow, not shrink)
gcloud compute disks resize my-data-disk \
  --size=1TB \
  --zone=us-central1-a

# List disks
gcloud compute disks list
gcloud compute disks list --filter="zone:us-central1-a AND NOT users:*" # Unattached disks

# Describe a disk
gcloud compute disks describe my-data-disk --zone=us-central1-a

# Delete a disk
gcloud compute disks delete my-data-disk --zone=us-central1-a --quiet

# Create a snapshot from a disk
gcloud compute disks snapshot my-data-disk \
  --snapshot-names=my-data-disk-snapshot-$(date +%Y%m%d) \
  --zone=us-central1-a \
  --storage-location=us-central1

# Create a snapshot with a description
gcloud compute snapshots create my-snapshot \
  --source-disk=my-data-disk \
  --source-disk-zone=us-central1-a \
  --description="Pre-upgrade backup $(date +%Y-%m-%d)" \
  --storage-location=us

# List snapshots
gcloud compute snapshots list
gcloud compute snapshots list --filter="sourceDisk:my-data-disk" --format="table(name,creationTimestamp,diskSizeGb,storageBytes)"

# Create a disk from a snapshot
gcloud compute disks create my-restored-disk \
  --source-snapshot=my-snapshot \
  --type=pd-ssd \
  --zone=us-central1-a

# Delete a snapshot
gcloud compute snapshots delete my-snapshot --quiet

# Create a snapshot schedule
gcloud compute resource-policies create snapshot-schedule my-hourly-snapshots \
  --region=us-central1 \
  --max-retention-days=7 \
  --start-time=04:00 \
  --hourly-schedule=4 \
  --on-source-disk-delete=keep-auto-snapshots

# Attach snapshot schedule to a disk
gcloud compute disks add-resource-policies my-data-disk \
  --resource-policies=my-hourly-snapshots \
  --zone=us-central1-a
```

---

## Images & Image Families

```bash
# List public images for a project
gcloud compute images list --project=debian-cloud
gcloud compute images list --project=ubuntu-os-cloud --no-standard-images
gcloud compute images list --project=centos-cloud

# List all available public image projects (useful overview)
gcloud compute images list --format="table(name,family,project)" \
  --filter="family~'^(debian|ubuntu|centos|rhel)'"

# Describe an image
gcloud compute images describe debian-12-bookworm-v20240415 --project=debian-cloud

# Get the latest image in a family
gcloud compute images describe \
  $(gcloud compute images list --project=debian-cloud \
    --filter="family=debian-12" \
    --sort-by="~creationTimestamp" \
    --limit=1 \
    --format="get(name)") \
  --project=debian-cloud

# Create a custom image from a disk
gcloud compute images create my-golden-image \
  --source-disk=my-configured-disk \
  --source-disk-zone=us-central1-a \
  --family=my-app-image-family \
  --description="Golden image with app v2.3.1 installed"

# Create an image from a snapshot
gcloud compute images create my-image-from-snapshot \
  --source-snapshot=my-snapshot \
  --family=my-app-image-family

# Create an image from a GCS file (raw disk image)
gcloud compute images create my-imported-image \
  --source-uri=gs://my-bucket/disk-image.tar.gz \
  --guest-os-features=VIRTIO_SCSI_MULTIQUEUE

# Set image deprecation
gcloud compute images deprecate my-old-image \
  --state=DEPRECATED \
  --replacement=my-new-image

# List images in a custom family
gcloud compute images list --filter="family=my-app-image-family"

# Delete an image
gcloud compute images delete my-old-image --quiet
```

---

## Firewall Rules

```bash
# Create a firewall rule to allow HTTP/HTTPS
gcloud compute firewall-rules create allow-http-https \
  --direction=INGRESS \
  --action=ALLOW \
  --rules=tcp:80,tcp:443 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=web-server \
  --priority=1000

# Allow SSH from a specific CIDR
gcloud compute firewall-rules create allow-ssh-corp \
  --direction=INGRESS \
  --action=ALLOW \
  --rules=tcp:22 \
  --source-ranges=203.0.113.0/24 \
  --priority=900

# Allow all internal traffic within a VPC
gcloud compute firewall-rules create allow-internal \
  --direction=INGRESS \
  --action=ALLOW \
  --rules=all \
  --source-ranges=10.128.0.0/9 \
  --priority=65534

# Allow load balancer health checks
gcloud compute firewall-rules create allow-health-check \
  --direction=INGRESS \
  --action=ALLOW \
  --rules=tcp:80,tcp:8080 \
  --source-ranges=130.211.0.0/22,35.191.0.0/16 \
  --target-tags=allow-health-check

# List firewall rules
gcloud compute firewall-rules list \
  --format="table(name,direction,priority,sourceRanges.list(),allowed[].map().firewall_rule().list())"

# Describe a firewall rule
gcloud compute firewall-rules describe allow-http-https

# Update a firewall rule (disable it)
gcloud compute firewall-rules update allow-http-https --disabled

# Delete a firewall rule
gcloud compute firewall-rules delete allow-http-https --quiet
```

---

## SSH & Serial Console

```bash
# SSH into an instance (creates SSH keys if needed, uses OS Login if configured)
gcloud compute ssh my-vm --zone=us-central1-a

# SSH with a custom command
gcloud compute ssh my-vm --zone=us-central1-a --command="sudo journalctl -u nginx -n 100"

# SSH through IAP (Identity-Aware Proxy) — no public IP needed
gcloud compute ssh my-vm --zone=us-central1-a --tunnel-through-iap

# SSH with port forwarding
gcloud compute ssh my-vm --zone=us-central1-a \
  -- -L 8080:localhost:8080 -N

# Copy files from local to instance
gcloud compute scp ./config.yaml my-vm:/etc/myapp/config.yaml --zone=us-central1-a

# Copy files from instance to local
gcloud compute scp my-vm:/var/log/app.log ./app.log --zone=us-central1-a

# Copy directory recursively
gcloud compute scp --recurse ./app/ my-vm:/opt/app/ --zone=us-central1-a

# Access serial console (useful when SSH is not available)
gcloud compute connect-to-serial-port my-vm --zone=us-central1-a

# Get serial console output (boot logs)
gcloud compute instances get-serial-port-output my-vm --zone=us-central1-a

# Enable serial console access (project-level setting)
gcloud compute project-info add-metadata \
  --metadata=serial-port-enable=TRUE
```

---

## Monitoring & Troubleshooting

```bash
# View instance logs in Cloud Logging
gcloud logging read \
  'resource.type="gce_instance" AND resource.labels.instance_id="INSTANCE_ID"' \
  --limit=50 \
  --format=json

# Get instance system event logs
gcloud logging read \
  'resource.type="gce_instance" logName="projects/my-project/logs/syslog"' \
  --freshness=1h

# Check instance OS inventory (requires Cloud Ops Agent)
gcloud compute instances os-inventory describe my-vm --zone=us-central1-a

# View instance uptime
gcloud compute instances describe my-vm \
  --zone=us-central1-a \
  --format="get(lastStartTimestamp,status)"

# Check MIG operations (useful for debugging rolling updates)
gcloud compute operations list \
  --filter="operationType=insert AND targetLink~my-mig" \
  --format="table(name,status,progress,insertTime)"

# Describe a specific operation for error details
gcloud compute operations describe OPERATION_ID --zone=us-central1-a

# List sole-tenant node groups and nodes
gcloud compute sole-tenancy node-groups list
gcloud compute sole-tenancy node-groups describe my-node-group --zone=us-central1-a

# Create a compact placement policy
gcloud compute resource-policies create group-placement my-placement-policy \
  --region=us-central1 \
  --collocation=COLLOCATED \
  --vm-count=4

# Create an instance with a placement policy
gcloud compute instances create my-hpc-vm \
  --machine-type=c3-standard-8 \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --resource-policies=my-placement-policy \
  --zone=us-central1-a
```
