# Migrate to Virtual Machines — CLI Reference

## Prerequisites

```bash
# Enable required APIs
gcloud services enable vmmigration.googleapis.com \
  --project=my-migration-project

# Confirm enabled
gcloud services list --filter="name:vmmigration" --project=my-migration-project
```

---

## Sources

Sources represent the origin environment (vCenter, AWS, Azure).

```bash
# Create a VMware vCenter source
gcloud migration vms sources create vcenter-source \
  --location=us-central1 \
  --description="On-premises vCenter datacenter" \
  --vmware-vcenter-address=192.168.1.100 \
  --vmware-username=migration-user@vsphere.local \
  --vmware-password=SECRET_PASSWORD \
  --project=my-migration-project

# Create an AWS source
gcloud migration vms sources create aws-source \
  --location=us-central1 \
  --aws-access-key-id=AKIAIOSFODNN7EXAMPLE \
  --aws-secret-access-key=SECRET \
  --aws-region=us-east-1 \
  --project=my-migration-project

# List all sources
gcloud migration vms sources list \
  --location=us-central1 \
  --project=my-migration-project \
  --format="table(name,description,createTime,state)"

# Describe a source
gcloud migration vms sources describe vcenter-source \
  --location=us-central1 \
  --project=my-migration-project

# Delete a source
gcloud migration vms sources delete vcenter-source \
  --location=us-central1 \
  --project=my-migration-project
```

---

## Datacenter Connectors

Connectors are deployed in the source environment (VMware only) to proxy replication traffic.

```bash
# Create a datacenter connector registration token
gcloud migration vms sources datacenter-connectors create dc-connector-1 \
  --source=vcenter-source \
  --location=us-central1 \
  --project=my-migration-project

# List connectors for a source
gcloud migration vms sources datacenter-connectors list \
  --source=vcenter-source \
  --location=us-central1 \
  --project=my-migration-project \
  --format="table(name,state,version,registrationId)"

# Describe a connector (shows health, version, registration state)
gcloud migration vms sources datacenter-connectors describe dc-connector-1 \
  --source=vcenter-source \
  --location=us-central1 \
  --project=my-migration-project

# Delete a connector
gcloud migration vms sources datacenter-connectors delete dc-connector-1 \
  --source=vcenter-source \
  --location=us-central1 \
  --project=my-migration-project
```

---

## Migrating VMs

A MigratingVm object tracks a single VM through its migration lifecycle.

```bash
# Create a migrating VM (begin replication setup)
# --source-vm-id is the VM's identifier in the source (VMware MoRef ID or AWS instance ID)
gcloud migration vms migrating-vms create web-server-1 \
  --source=vcenter-source \
  --location=us-central1 \
  --source-vm-id=vm-12345 \
  --description="Web server tier 1" \
  --target-defaults-zone=us-central1-a \
  --target-defaults-machine-type=n2-standard-4 \
  --target-defaults-network=projects/my-project/global/networks/vpc-prod \
  --target-defaults-subnetwork=projects/my-project/regions/us-central1/subnetworks/subnet-web \
  --project=my-migration-project

# List all migrating VMs for a source
gcloud migration vms migrating-vms list \
  --source=vcenter-source \
  --location=us-central1 \
  --project=my-migration-project \
  --format="table(name,currentSyncInfo.lastSyncTime,state,description)"

# Describe a migrating VM (shows replication state, last sync time, errors)
gcloud migration vms migrating-vms describe web-server-1 \
  --source=vcenter-source \
  --location=us-central1 \
  --project=my-migration-project

# Delete a migrating VM (stops replication, removes replicated data)
gcloud migration vms migrating-vms delete web-server-1 \
  --source=vcenter-source \
  --location=us-central1 \
  --project=my-migration-project
```

---

## Replication Management

```bash
# Start replication for a migrating VM
gcloud migration vms migrating-vms start-replication web-server-1 \
  --source=vcenter-source \
  --location=us-central1 \
  --project=my-migration-project

# Pause replication (e.g., to reduce bandwidth during business hours)
gcloud migration vms migrating-vms pause-replication web-server-1 \
  --source=vcenter-source \
  --location=us-central1 \
  --project=my-migration-project

# Resume replication
gcloud migration vms migrating-vms resume-replication web-server-1 \
  --source=vcenter-source \
  --location=us-central1 \
  --project=my-migration-project
```

---

## Clone Jobs (Test Before Cutover)

Clone jobs create a non-disruptive test GCE instance from replicated data.

```bash
# Create a clone job (instantiates a GCE VM for testing)
gcloud migration vms migrating-vms clone-jobs create test-clone-1 \
  --migrating-vm=web-server-1 \
  --source=vcenter-source \
  --location=us-central1 \
  --project=my-migration-project

# List clone jobs for a migrating VM
gcloud migration vms migrating-vms clone-jobs list \
  --migrating-vm=web-server-1 \
  --source=vcenter-source \
  --location=us-central1 \
  --project=my-migration-project \
  --format="table(name,state,createTime,computeEngineTargetDetails.vmName)"

# Describe a clone job
gcloud migration vms migrating-vms clone-jobs describe test-clone-1 \
  --migrating-vm=web-server-1 \
  --source=vcenter-source \
  --location=us-central1 \
  --project=my-migration-project
```

---

## Cutover Jobs (Final Migration)

```bash
# Create a cutover job (stops source VM, creates production GCE instance)
gcloud migration vms migrating-vms cutover-jobs create cutover-1 \
  --migrating-vm=web-server-1 \
  --source=vcenter-source \
  --location=us-central1 \
  --project=my-migration-project

# List cutover jobs
gcloud migration vms migrating-vms cutover-jobs list \
  --migrating-vm=web-server-1 \
  --source=vcenter-source \
  --location=us-central1 \
  --project=my-migration-project \
  --format="table(name,state,createTime,computeEngineTargetDetails.vmName,computeEngineTargetDetails.zone)"

# Describe a cutover job (shows progress, GCE VM name when complete)
gcloud migration vms migrating-vms cutover-jobs describe cutover-1 \
  --migrating-vm=web-server-1 \
  --source=vcenter-source \
  --location=us-central1 \
  --project=my-migration-project

# Cancel a cutover job (if still in progress)
gcloud migration vms migrating-vms cutover-jobs cancel cutover-1 \
  --migrating-vm=web-server-1 \
  --source=vcenter-source \
  --location=us-central1 \
  --project=my-migration-project
```

---

## Utilization Reports

Analyze source VM utilization for right-sizing recommendations.

```bash
# Create a utilization report for a source (analyzes all VMs in vCenter)
gcloud migration vms sources utilization-reports create report-jan-2025 \
  --source=vcenter-source \
  --location=us-central1 \
  --display-name="January 2025 Baseline" \
  --time-frame=MONTH \
  --project=my-migration-project

# List utilization reports
gcloud migration vms sources utilization-reports list \
  --source=vcenter-source \
  --location=us-central1 \
  --project=my-migration-project

# Describe a utilization report (includes VM utilization data and GCE recommendations)
gcloud migration vms sources utilization-reports describe report-jan-2025 \
  --source=vcenter-source \
  --location=us-central1 \
  --project=my-migration-project
```

---

## Watching Long-Running Operations

Migration operations are async and return an operation name.

```bash
# List recent migration operations
gcloud migration vms operations list \
  --location=us-central1 \
  --project=my-migration-project \
  --format="table(name,done,metadata.target,error)"

# Wait for a specific operation to complete
gcloud migration vms operations wait OPERATION_ID \
  --location=us-central1 \
  --project=my-migration-project
```
