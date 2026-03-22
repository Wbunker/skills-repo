# Azure Batch — CLI Reference

For service concepts, see [batch-capabilities.md](batch-capabilities.md).

## Batch Account — Create and Configure

```bash
# --- Create a Batch account (Batch Service pool allocation) ---
az batch account create \
  --name mybatchaccount \
  --resource-group myRG \
  --location eastus \
  --storage-account mystorageaccount

# Create a Batch account (User Subscription pool allocation — VMs appear in your sub)
az batch account create \
  --name mybatchaccount \
  --resource-group myRG \
  --location eastus \
  --storage-account mystorageaccount \
  --pool-allocation-mode UserSubscription \
  --keyvault /subscriptions/.../vaults/myKeyVault

# Log in to Batch account for subsequent az batch commands
az batch account login \
  --name mybatchaccount \
  --resource-group myRG \
  --shared-key-auth

# Show Batch account details
az batch account show \
  --name mybatchaccount \
  --resource-group myRG

# List Batch accounts
az batch account list --output table

# Upload an application package
az batch application package create \
  --resource-group myRG \
  --account-name mybatchaccount \
  --application-name myrenderer \
  --version 2.1.0 \
  --package-file ./renderer-v2.1.0.zip

# Activate an application package after upload
az batch application package activate \
  --resource-group myRG \
  --account-name mybatchaccount \
  --application-name myrenderer \
  --version 2.1.0 \
  --format zip
```

---

## Batch Pools — Create and Manage

```bash
# --- Create a pool (JSON configuration recommended for production) ---
# Simple pool using VM configuration
az batch pool create \
  --id mypool \
  --vm-size Standard_D4s_v5 \
  --target-dedicated-nodes 4 \
  --image canonical:0001-com-ubuntu-server-focal:20_04-lts \
  --node-agent-sku-id "batch.node.ubuntu 20.04"

# Create a pool with auto-scale and application packages (JSON file)
az batch pool create \
  --json-file pool.json

# pool.json example
cat > pool.json << 'EOF'
{
  "id": "mypool",
  "displayName": "My HPC Pool",
  "vmSize": "Standard_D8s_v5",
  "virtualMachineConfiguration": {
    "imageReference": {
      "publisher": "Canonical",
      "offer": "0001-com-ubuntu-server-focal",
      "sku": "20_04-lts",
      "version": "latest"
    },
    "nodeAgentSKUId": "batch.node.ubuntu 20.04"
  },
  "enableAutoScale": true,
  "autoScaleFormula": "$TargetDedicatedNodes = min(10, max(0, $PendingTasks.GetSample(1)));",
  "autoScaleEvaluationInterval": "PT5M",
  "startTask": {
    "commandLine": "/bin/bash -c 'apt-get install -y jq'",
    "userIdentity": {
      "autoUser": {
        "scope": "Pool",
        "elevationLevel": "Admin"
      }
    },
    "waitForSuccess": true,
    "maxTaskRetryCount": 2
  },
  "applicationPackageReferences": [
    {
      "applicationId": "myrenderer",
      "version": "2.1.0"
    }
  ]
}
EOF

# List pools
az batch pool list --output table

# Show pool details
az batch pool show --pool-id mypool

# Resize a pool (change dedicated node count)
az batch pool resize \
  --pool-id mypool \
  --target-dedicated-nodes 10

# Resize with low-priority nodes
az batch pool resize \
  --pool-id mypool \
  --target-dedicated-nodes 2 \
  --target-low-priority-nodes 8

# Stop a resize operation
az batch pool resize \
  --pool-id mypool \
  --abort

# Delete a pool
az batch pool delete --pool-id mypool --yes
```

---

## Batch Nodes — Manage

```bash
# List nodes in a pool
az batch node list --pool-id mypool --output table

# Show node details
az batch node show \
  --pool-id mypool \
  --node-id tvm-12345678_1-20240101t000000z

# Put a node in offline state (no new tasks scheduled)
az batch node make-offline \
  --pool-id mypool \
  --node-id tvm-12345678_1-20240101t000000z \
  --on-task-completion TaskCompletion

# Reimage a node (clean and re-run start task)
az batch node reimage \
  --pool-id mypool \
  --node-id tvm-12345678_1-20240101t000000z

# Delete specific nodes from a pool
az batch node delete \
  --pool-id mypool \
  --json-file delete-nodes.json
  # delete-nodes.json: {"nodeList": ["tvm-..._1-...", "tvm-..._2-..."]}

# Remote desktop connection info (Windows nodes)
az batch node remote-desktop \
  --pool-id mypool \
  --node-id tvm-12345678_1-20240101t000000z \
  --out-file node.rdp

# SSH login info (Linux nodes)
az batch node remote-login-settings show \
  --pool-id mypool \
  --node-id tvm-12345678_1-20240101t000000z
```

---

## Batch Jobs — Create and Manage

```bash
# Create a job
az batch job create \
  --id myjob \
  --pool-id mypool

# Create a job with priority and metadata
az batch job create \
  --json-file job.json

# job.json example
cat > job.json << 'EOF'
{
  "id": "render-job-001",
  "displayName": "Blender Render Job",
  "priority": 100,
  "poolInfo": {
    "poolId": "mypool"
  },
  "onAllTasksComplete": "terminateJob",
  "metadata": [
    {"name": "project", "value": "film-2024"},
    {"name": "requestedBy", "value": "render-team"}
  ]
}
EOF

# List jobs
az batch job list --output table

# Show job details
az batch job show --job-id myjob

# Disable a job (pause task scheduling)
az batch job disable --job-id myjob --disable-tasks requeue

# Enable a paused job
az batch job enable --job-id myjob

# Terminate a job (stop all tasks)
az batch job stop --job-id myjob --reason "manual termination"

# Delete a job
az batch job delete --job-id myjob --yes
```

---

## Batch Tasks — Create and Manage

```bash
# Create a single task
az batch task create \
  --job-id myjob \
  --task-id task-001 \
  --command-line "/bin/bash -c 'echo hello world > /tmp/output.txt'"

# Create a task with input/output files (JSON)
az batch task create \
  --job-id myjob \
  --json-file task.json

# task.json example
cat > task.json << 'EOF'
{
  "id": "render-frame-001",
  "displayName": "Render frame 001",
  "commandLine": "/bin/bash -c 'blender -b /mnt/input/scene.blend -o /mnt/output/ -f 1'",
  "resourceFiles": [
    {
      "autoStorageContainerName": "inputs",
      "blobPrefix": "scene-v2/"
    }
  ],
  "outputFiles": [
    {
      "filePattern": "/mnt/output/**/*",
      "destination": {
        "container": {
          "containerUrl": "https://mystorageaccount.blob.core.windows.net/outputs?<SAS>"
        }
      },
      "uploadOptions": {
        "uploadCondition": "TaskCompletion"
      }
    }
  ],
  "environmentSettings": [
    {"name": "FRAME_NUMBER", "value": "1"}
  ],
  "constraints": {
    "maxTaskRetryCount": 3,
    "maxWallClockTime": "PT2H"
  }
}
EOF

# Create multiple tasks from a collection (JSON array)
az batch task create \
  --job-id myjob \
  --json-file tasks-collection.json

# List tasks in a job
az batch task list --job-id myjob --output table

# Show task details and state
az batch task show --job-id myjob --task-id task-001

# Show task execution information
az batch task show --job-id myjob --task-id task-001 \
  --query executionInfo

# Get task file (stdout, stderr)
az batch task file show \
  --job-id myjob \
  --task-id task-001 \
  --file-path stdout.txt

# Download task output file
az batch task file download \
  --job-id myjob \
  --task-id task-001 \
  --file-path stdout.txt \
  --destination ./stdout.txt

# List task files
az batch task file list \
  --job-id myjob \
  --task-id task-001 \
  --output table

# Delete a task
az batch task delete \
  --job-id myjob \
  --task-id task-001 \
  --yes

# Reactivate a failed task (reset retry count)
az batch task reactivate \
  --job-id myjob \
  --task-id task-001
```
