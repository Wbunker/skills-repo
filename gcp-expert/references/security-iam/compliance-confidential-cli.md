# Assured Workloads & Confidential Computing — CLI Reference

For concepts and capabilities, see [compliance-confidential-capabilities.md](compliance-confidential-capabilities.md).

---

## Assured Workloads CLI

```bash
# Enable Assured Workloads API
gcloud services enable assuredworkloads.googleapis.com

# Create an Assured Workloads workload (folder with compliance controls)
gcloud assured workloads create \
  --organization=ORG_ID \
  --location=us-central1 \
  --display-name="FedRAMP Production" \
  --compliance-regime=FEDRAMP_MODERATE \
  --billing-account=billingAccounts/BILLING_ACCOUNT_ID

# Create FedRAMP High workload with CMEK
gcloud assured workloads create \
  --organization=ORG_ID \
  --location=us-central1 \
  --display-name="FedRAMP High - CUI" \
  --compliance-regime=FEDRAMP_HIGH \
  --billing-account=billingAccounts/BILLING_ACCOUNT_ID \
  --kms-settings-next-rotation-time=2027-01-01T00:00:00Z \
  --kms-settings-rotation-period=31536000s

# Create ITAR workload
gcloud assured workloads create \
  --organization=ORG_ID \
  --location=us-central1 \
  --display-name="ITAR Controlled" \
  --compliance-regime=ITAR \
  --billing-account=billingAccounts/BILLING_ACCOUNT_ID

# Create CJIS workload
gcloud assured workloads create \
  --organization=ORG_ID \
  --location=us-central1 \
  --display-name="CJIS Law Enforcement" \
  --compliance-regime=CJIS \
  --billing-account=billingAccounts/BILLING_ACCOUNT_ID

# Create EU Sovereign Controls workload (EU data boundary)
gcloud assured workloads create \
  --organization=ORG_ID \
  --location=europe-west3 \
  --display-name="EU Sovereign Workload" \
  --compliance-regime=EU_REGIONS_AND_SUPPORT \
  --billing-account=billingAccounts/BILLING_ACCOUNT_ID

# List all Assured Workloads workloads in an organization
gcloud assured workloads list \
  --organization=ORG_ID \
  --location=us-central1

# List workloads across all locations
gcloud assured workloads list \
  --organization=ORG_ID \
  --location=-

# Describe a workload (view applied org policies, compliance state)
gcloud assured workloads describe WORKLOAD_ID \
  --organization=ORG_ID \
  --location=us-central1

# List violations (compliance drift)
gcloud assured workloads violations list \
  --organization=ORG_ID \
  --location=us-central1 \
  --workload=WORKLOAD_ID

# List violations with filter for unacknowledged only
gcloud assured workloads violations list \
  --organization=ORG_ID \
  --location=us-central1 \
  --workload=WORKLOAD_ID \
  --filter="state=UNRESOLVED"

# Describe a specific violation
gcloud assured workloads violations describe VIOLATION_ID \
  --organization=ORG_ID \
  --location=us-central1 \
  --workload=WORKLOAD_ID

# Acknowledge a violation (mark as reviewed)
gcloud assured workloads violations acknowledge VIOLATION_ID \
  --organization=ORG_ID \
  --location=us-central1 \
  --workload=WORKLOAD_ID \
  --comment="Reviewed and approved exception per security policy"

# Delete an Assured Workloads workload (does NOT delete the folder's projects)
gcloud assured workloads delete WORKLOAD_ID \
  --organization=ORG_ID \
  --location=us-central1

# Update workload display name
gcloud assured workloads update WORKLOAD_ID \
  --organization=ORG_ID \
  --location=us-central1 \
  --display-name="Updated Workload Name"
```

### Assured Workloads Compliance Regime Values

| `--compliance-regime` value | Regime |
|---|---|
| `FEDRAMP_MODERATE` | FedRAMP Moderate |
| `FEDRAMP_HIGH` | FedRAMP High |
| `IL2` | DoD Impact Level 2 |
| `IL4` | DoD Impact Level 4 |
| `IL5` | DoD Impact Level 5 |
| `ITAR` | ITAR |
| `CJIS` | CJIS |
| `HIPAA` | HIPAA |
| `HITRUST` | HITRUST |
| `EU_REGIONS_AND_SUPPORT` | EU Sovereign Controls |
| `CA_REGIONS_AND_SUPPORT` | Canada Regions |
| `AU_REGIONS` | Australia Regions |

---

## Confidential VM CLI

```bash
# Create a Confidential VM (AMD SEV)
gcloud compute instances create my-confidential-vm \
  --zone=us-central1-a \
  --machine-type=n2d-standard-4 \
  --confidential-compute \
  --maintenance-policy=TERMINATE \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB \
  --shielded-secure-boot \
  --shielded-vtpm \
  --shielded-integrity-monitoring

# Create a Confidential VM with AMD SEV-SNP (stronger attestation)
gcloud compute instances create my-sevsnp-vm \
  --zone=us-central1-a \
  --machine-type=c2d-standard-4 \
  --confidential-compute-type=SEV_SNP \
  --maintenance-policy=TERMINATE \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud

# Create a Confidential VM with Intel TDX
gcloud compute instances create my-tdx-vm \
  --zone=us-central1-a \
  --machine-type=c3-standard-4 \
  --confidential-compute-type=TDX \
  --maintenance-policy=TERMINATE \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud

# Create a Confidential VM with a CMEK boot disk
gcloud compute instances create my-confidential-vm-cmek \
  --zone=us-central1-a \
  --machine-type=n2d-standard-4 \
  --confidential-compute \
  --maintenance-policy=TERMINATE \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-kms-key=projects/PROJECT_ID/locations/us-central1/keyRings/my-ring/cryptoKeys/my-key \
  --shielded-secure-boot \
  --shielded-vtpm

# Create an instance template for Confidential VMs (for use with MIGs)
gcloud compute instance-templates create confidential-template \
  --machine-type=n2d-standard-4 \
  --confidential-compute \
  --maintenance-policy=TERMINATE \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --shielded-secure-boot \
  --shielded-vtpm

# Verify Confidential VM status
gcloud compute instances describe my-confidential-vm \
  --zone=us-central1-a \
  --format="yaml(confidentialInstanceConfig,shieldedInstanceConfig)"

# List all Confidential VMs in a project
gcloud compute instances list \
  --filter="confidentialInstanceConfig.enableConfidentialCompute=true" \
  --format="table(name,zone,status,machineType)"

# List available Confidential-compatible machine types in a zone
gcloud compute machine-types list \
  --zones=us-central1-a \
  --filter="name~'^n2d|^c2d|^c3'"

# View attestation report count metric (via Cloud Monitoring API)
# Metric: compute.googleapis.com/confidential_vm/attestation_report_count
gcloud monitoring time-series list \
  --filter='metric.type="compute.googleapis.com/confidential_vm/attestation_report_count"'
```

---

## Confidential GKE Nodes CLI

```bash
# Create a GKE cluster with Confidential Nodes enabled from the start
gcloud container clusters create confidential-cluster \
  --zone=us-central1-a \
  --machine-type=n2d-standard-4 \
  --enable-confidential-nodes \
  --num-nodes=3

# Create a GKE cluster with Confidential Nodes and Workload Identity
gcloud container clusters create confidential-cluster \
  --zone=us-central1-a \
  --machine-type=n2d-standard-4 \
  --enable-confidential-nodes \
  --workload-pool=PROJECT_ID.svc.id.goog \
  --num-nodes=3 \
  --release-channel=regular

# Add a Confidential node pool to an existing cluster
gcloud container node-pools create confidential-pool \
  --cluster=my-cluster \
  --zone=us-central1-a \
  --machine-type=n2d-standard-4 \
  --enable-confidential-nodes \
  --num-nodes=3

# Add a Confidential node pool with autoscaling
gcloud container node-pools create confidential-pool \
  --cluster=my-cluster \
  --zone=us-central1-a \
  --machine-type=n2d-standard-4 \
  --enable-confidential-nodes \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=10

# Verify node pool is confidential
gcloud container node-pools describe confidential-pool \
  --cluster=my-cluster \
  --zone=us-central1-a \
  --format="yaml(config.confidentialNodes)"

# List all node pools and their confidential status
gcloud container node-pools list \
  --cluster=my-cluster \
  --zone=us-central1-a \
  --format="table(name,config.machineType,config.confidentialNodes.enabled)"
```

---

## Confidential Dataflow CLI

```bash
# Submit a Dataflow job using Confidential VMs
gcloud dataflow jobs run my-confidential-job \
  --gcs-location=gs://dataflow-templates/latest/Word_Count \
  --region=us-central1 \
  --staging-location=gs://my-bucket/staging \
  --parameters inputFile=gs://my-bucket/input.txt,output=gs://my-bucket/output \
  --additional-experiments=enable_confidential_dataflow_worker
```

---

## Confidential Dataproc CLI

```bash
# Create a Dataproc cluster with Confidential VMs
gcloud dataproc clusters create confidential-cluster \
  --region=us-central1 \
  --master-machine-type=n2d-standard-4 \
  --worker-machine-type=n2d-standard-4 \
  --num-workers=2 \
  --confidential-compute \
  --properties=dataproc:dataproc.conscrypt.provider.enable=false
```

---

## Shielded VM CLI

```bash
# Create a Shielded VM (without full confidential compute)
gcloud compute instances create my-shielded-vm \
  --zone=us-central1-a \
  --machine-type=n2-standard-4 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --shielded-secure-boot \
  --shielded-vtpm \
  --shielded-integrity-monitoring

# Enable Shielded VM features on an existing instance
# NOTE: instance must be stopped first
gcloud compute instances stop my-vm --zone=us-central1-a
gcloud compute instances update my-vm \
  --zone=us-central1-a \
  --shielded-secure-boot \
  --shielded-vtpm \
  --shielded-integrity-monitoring
gcloud compute instances start my-vm --zone=us-central1-a

# Update integrity policy baseline (after approved change to boot config)
gcloud compute instances update-shielded-instance-config my-vm \
  --zone=us-central1-a \
  --start-shield-integrity-monitoring

# View Shielded VM identity (endorsement key, signing key)
gcloud compute instances get-shielded-identity my-vm \
  --zone=us-central1-a

# Describe Shielded VM config
gcloud compute instances describe my-vm \
  --zone=us-central1-a \
  --format="yaml(shieldedInstanceConfig,shieldedInstanceIntegrityPolicy)"

# Create a Shielded VM instance template
gcloud compute instance-templates create shielded-template \
  --machine-type=n2-standard-4 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --shielded-secure-boot \
  --shielded-vtpm \
  --shielded-integrity-monitoring

# Org policy to require Shielded VMs across all projects in an org
cat > /tmp/require-shielded-vm.yaml << 'EOF'
name: organizations/ORG_ID/policies/compute.requireShieldedVm
spec:
  rules:
    - enforce: true
EOF
gcloud org-policies set-policy /tmp/require-shielded-vm.yaml

# Verify org policy is applied
gcloud org-policies describe compute.requireShieldedVm \
  --organization=ORG_ID
```

---

## Org Policy for Data Residency CLI

```bash
# Restrict resource creation to US regions (FedRAMP data residency)
cat > /tmp/us-residency-policy.yaml << 'EOF'
name: folders/FOLDER_ID/policies/gcp.resourceLocations
spec:
  rules:
    - values:
        allowedValues:
          - in:us-locations
EOF
gcloud org-policies set-policy /tmp/us-residency-policy.yaml

# Restrict to specific US regions only (stricter than in:us-locations)
cat > /tmp/us-strict-policy.yaml << 'EOF'
name: folders/FOLDER_ID/policies/gcp.resourceLocations
spec:
  rules:
    - values:
        allowedValues:
          - us-central1
          - us-east1
          - us-east4
          - us-west1
EOF
gcloud org-policies set-policy /tmp/us-strict-policy.yaml

# Restrict to EU regions only
cat > /tmp/eu-residency-policy.yaml << 'EOF'
name: folders/FOLDER_ID/policies/gcp.resourceLocations
spec:
  rules:
    - values:
        allowedValues:
          - in:europe-locations
EOF
gcloud org-policies set-policy /tmp/eu-residency-policy.yaml

# View applied org policies on a folder
gcloud org-policies list --folder=FOLDER_ID

# Describe a specific org policy on a folder
gcloud org-policies describe gcp.resourceLocations \
  --folder=FOLDER_ID

# Describe org policy at organization level
gcloud org-policies describe gcp.resourceLocations \
  --organization=ORG_ID

# Reset org policy to inherited default (remove override)
gcloud org-policies reset gcp.resourceLocations \
  --folder=FOLDER_ID

# List all available org policy constraints (filter for compute/security)
gcloud org-policies list-available-constraints \
  --organization=ORG_ID \
  --filter="name~'compute|iam|storage'"
```

---

## Access Approval CLI (Required for IL4/IL5/ITAR)

```bash
# Enable Access Approval API
gcloud services enable accessapproval.googleapis.com

# Configure Access Approval for a project (specify approvers)
gcloud access-approval settings update \
  --project=PROJECT_ID \
  --notification-emails=security-team@example.com,ciso@example.com \
  --enrolled-services=all

# Configure Access Approval at organization level
gcloud access-approval settings update \
  --organization=ORG_ID \
  --notification-emails=security-team@example.com \
  --enrolled-services=all

# View current Access Approval settings
gcloud access-approval settings get --project=PROJECT_ID

# List pending approval requests
gcloud access-approval requests list \
  --project=PROJECT_ID \
  --filter="state=PENDING"

# Approve an access request
gcloud access-approval requests approve REQUEST_NAME

# Dismiss (deny) an access request
gcloud access-approval requests dismiss REQUEST_NAME
```
