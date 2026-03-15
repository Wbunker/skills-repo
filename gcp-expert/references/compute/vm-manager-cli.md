# VM Manager — CLI Reference

For service concepts, see [vm-manager-capabilities.md](vm-manager-capabilities.md).

## VM Manager — Setup

```bash
# Enable VM Manager API
gcloud services enable osconfig.googleapis.com --project=PROJECT_ID

# Enable OS inventory and patch management via project metadata
gcloud compute project-info add-metadata \
  --metadata enable-osconfig=true \
  --project=PROJECT_ID

# Verify OS Config agent status on a VM (SSH into VM first)
sudo systemctl status google-osconfig-agent

# Install OS Config agent on VM (if not present)
# Debian/Ubuntu:
sudo apt-get install google-osconfig-agent
# RHEL/CentOS:
sudo yum install google-osconfig-agent
```

## VM Manager — OS Inventory

```bash
# List OS inventory for all VMs in a project/location
gcloud compute instances os-inventory list-instances \
  --project=PROJECT_ID \
  --location=us-central1-a

# Get detailed inventory for a specific instance
gcloud compute instances os-inventory describe INSTANCE_NAME \
  --zone=us-central1-a \
  --project=PROJECT_ID

# List installed packages on an instance
gcloud compute instances os-inventory describe INSTANCE_NAME \
  --zone=us-central1-a \
  --format="yaml(installedPackages)"

# List available package updates on an instance
gcloud compute instances os-inventory describe INSTANCE_NAME \
  --zone=us-central1-a \
  --format="yaml(packageUpdates)"

# Export inventory to Cloud Storage for all VMs (BigQuery export)
gcloud compute instances os-inventory list-instances \
  --project=PROJECT_ID \
  --format=json > inventory.json
```

## VM Manager — Patch Jobs (Ad-Hoc)

```bash
# Execute a patch job on all instances in a project
gcloud compute os-config patch-jobs execute \
  --project=PROJECT_ID \
  --instance-filter=all \
  --description="Monthly security patching" \
  --reboot-config=DEFAULT

# Patch specific instances by label
gcloud compute os-config patch-jobs execute \
  --project=PROJECT_ID \
  --instance-filter-labels="env=prod,os=ubuntu" \
  --patch-config-apt-type=UPGRADE \
  --reboot-config=ALWAYS

# Patch with zone rollout (one zone at a time)
gcloud compute os-config patch-jobs execute \
  --project=PROJECT_ID \
  --instance-filter=all \
  --rollout-mode=ZONE_BY_ZONE \
  --rollout-disruption-budget=10 \
  --rollout-disruption-budget-type=PERCENT

# Windows-only patch job (security updates only)
gcloud compute os-config patch-jobs execute \
  --project=PROJECT_ID \
  --instance-filter=all \
  --patch-config-windows-update-classifications=SECURITY \
  --reboot-config=DEFAULT

# Patch with pre and post scripts
gcloud compute os-config patch-jobs execute \
  --project=PROJECT_ID \
  --instance-filter=all \
  --patch-config-pre-step-linux-exec-step-config-gcs-object-bucket=my-scripts-bucket \
  --patch-config-pre-step-linux-exec-step-config-gcs-object-object=pre-patch.sh \
  --patch-config-post-step-linux-exec-step-config-gcs-object-bucket=my-scripts-bucket \
  --patch-config-post-step-linux-exec-step-config-gcs-object-object=post-patch.sh

# List all patch jobs
gcloud compute os-config patch-jobs list \
  --project=PROJECT_ID

# Describe a specific patch job (check status, progress)
gcloud compute os-config patch-jobs describe PATCH_JOB_ID \
  --project=PROJECT_ID

# List instances in a patch job with their status
gcloud compute os-config patch-jobs list-instance-details PATCH_JOB_ID \
  --project=PROJECT_ID \
  --filter="state=FAILED"

# Cancel a running patch job
gcloud compute os-config patch-jobs cancel PATCH_JOB_ID \
  --project=PROJECT_ID
```

## VM Manager — Patch Deployments (Scheduled)

```bash
# Create a weekly patch deployment (every Tuesday at 2am UTC)
gcloud compute os-config patch-deployments create weekly-security-patches \
  --project=PROJECT_ID \
  --instance-filter-all \
  --patch-config-reboot-config=DEFAULT \
  --recurring-schedule-weekly-day-of-week=TUESDAY \
  --recurring-schedule-time-of-day-hours=2 \
  --recurring-schedule-time-of-day-minutes=0 \
  --recurring-schedule-time-zone=UTC

# Create a monthly patch deployment (1st of each month)
gcloud compute os-config patch-deployments create monthly-full-patch \
  --project=PROJECT_ID \
  --instance-filter-all \
  --patch-config-apt-type=DIST_UPGRADE \
  --patch-config-reboot-config=ALWAYS \
  --recurring-schedule-monthly-week-day-of-month-day-of-week=MONDAY \
  --recurring-schedule-monthly-week-day-of-month-week=FIRST \
  --recurring-schedule-time-of-day-hours=3 \
  --recurring-schedule-time-zone=America/New_York

# List patch deployments
gcloud compute os-config patch-deployments list \
  --project=PROJECT_ID

# Describe a patch deployment
gcloud compute os-config patch-deployments describe DEPLOYMENT_NAME \
  --project=PROJECT_ID

# Pause a patch deployment
gcloud compute os-config patch-deployments pause DEPLOYMENT_NAME \
  --project=PROJECT_ID

# Resume a patch deployment
gcloud compute os-config patch-deployments resume DEPLOYMENT_NAME \
  --project=PROJECT_ID

# Delete a patch deployment
gcloud compute os-config patch-deployments delete DEPLOYMENT_NAME \
  --project=PROJECT_ID
```

## VM Manager — OS Policy Assignments

```bash
# List OS policy assignments in a location
gcloud compute os-config os-policy-assignments list \
  --location=us-central1 \
  --project=PROJECT_ID

# Describe an OS policy assignment
gcloud compute os-config os-policy-assignments describe ASSIGNMENT_NAME \
  --location=us-central1 \
  --project=PROJECT_ID

# Create an OS policy assignment from a YAML file
# (OS policies are complex; use YAML file for creation)
gcloud compute os-config os-policy-assignments create ASSIGNMENT_NAME \
  --location=us-central1 \
  --project=PROJECT_ID \
  --file=os-policy-assignment.yaml

# Example os-policy-assignment.yaml:
# osPolicies:
#   - id: ensure-nginx-installed
#     mode: ENFORCEMENT
#     resourceGroups:
#       - resources:
#           - id: nginx-pkg
#             pkg:
#               desiredState: INSTALLED
#               apt:
#                 name: nginx
# instanceFilter:
#   inclusionLabels:
#     - labels:
#         app: webserver
# rollout:
#   disruptionBudget:
#     percent: 10
#   minWaitDuration: 60s

# Get OS policy assignment report (compliance)
gcloud compute os-config os-policy-assignment-reports list \
  --location=us-central1 \
  --project=PROJECT_ID \
  --os-policy-assignment=ASSIGNMENT_NAME

# Delete an OS policy assignment
gcloud compute os-config os-policy-assignments delete ASSIGNMENT_NAME \
  --location=us-central1 \
  --project=PROJECT_ID
```

## VM Manager — Monitoring Patch Compliance

```bash
# Query patch compliance across fleet via Cloud Logging
gcloud logging read \
  'resource.type="gce_instance" jsonPayload."@type"="type.googleapis.com/google.cloud.osconfig.v1.PatchJob"' \
  --project=PROJECT_ID \
  --limit=50

# Export OS inventory to BigQuery for fleet-wide analysis
# (Set up recurring export in Cloud Console or via API)
# Then query:
# SELECT instance_name, package_name, package_version, last_refresh_time
# FROM `PROJECT_ID.osconfig.gce_packages`
# WHERE package_updates_available = TRUE
# ORDER BY last_refresh_time DESC

# Check VM Manager agent version on instance
gcloud compute instances describe INSTANCE_NAME \
  --zone=ZONE \
  --format="yaml(guestAttributes)"
```
