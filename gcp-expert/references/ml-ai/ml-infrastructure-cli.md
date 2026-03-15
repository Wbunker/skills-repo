# ML Infrastructure — CLI Reference

---

## Cloud TPU VMs

### Create and Manage TPU VMs

```bash
# Create a TPU VM (v4-8 slice; 8 chips; 1 host VM)
gcloud compute tpus tpu-vm create my-tpu-vm \
  --zone=us-central1-b \
  --accelerator-type=v4-8 \
  --version=tpu-vm-tf-2.13.0 \
  --project=PROJECT_ID

# Create a TPU VM with JAX runtime
gcloud compute tpus tpu-vm create my-jax-tpu \
  --zone=us-central1-b \
  --accelerator-type=v4-8 \
  --version=tpu-vm-jax-stable \
  --project=PROJECT_ID

# Create a TPU v5e VM
gcloud compute tpus tpu-vm create my-v5e-tpu \
  --zone=us-east1-d \
  --accelerator-type=v5e-8 \
  --version=tpu-vm-tf-2.14.0 \
  --project=PROJECT_ID

# Create a TPU v5p VM (larger slice)
gcloud compute tpus tpu-vm create my-v5p-tpu \
  --zone=us-east5-b \
  --accelerator-type=v5p-8 \
  --version=tpu-vm-v5p-tf-2.14.0 \
  --project=PROJECT_ID

# Create a large TPU pod slice (v4-64; 64 chips; 8 host VMs)
gcloud compute tpus tpu-vm create my-pod-slice \
  --zone=us-central1-b \
  --accelerator-type=v4-64 \
  --version=tpu-vm-jax-stable \
  --project=PROJECT_ID

# Create a preemptible TPU VM (cheaper; can be reclaimed)
gcloud compute tpus tpu-vm create my-preemptible-tpu \
  --zone=us-central1-b \
  --accelerator-type=v4-8 \
  --version=tpu-vm-jax-stable \
  --preemptible \
  --project=PROJECT_ID

# Create a TPU VM with a service account
gcloud compute tpus tpu-vm create my-tpu-sa \
  --zone=us-central1-b \
  --accelerator-type=v4-8 \
  --version=tpu-vm-jax-stable \
  --service-account=training-sa@PROJECT_ID.iam.gserviceaccount.com \
  --project=PROJECT_ID

# List all TPU VMs
gcloud compute tpus tpu-vm list \
  --zone=us-central1-b \
  --project=PROJECT_ID

# List TPU VMs across all zones
gcloud compute tpus tpu-vm list \
  --global \
  --project=PROJECT_ID

# Describe a TPU VM
gcloud compute tpus tpu-vm describe my-tpu-vm \
  --zone=us-central1-b \
  --project=PROJECT_ID

# SSH into a TPU VM
gcloud compute tpus tpu-vm ssh my-tpu-vm \
  --zone=us-central1-b \
  --project=PROJECT_ID

# SSH into a specific worker in a pod slice (0-indexed)
gcloud compute tpus tpu-vm ssh my-pod-slice \
  --zone=us-central1-b \
  --worker=0 \
  --project=PROJECT_ID

# Run a command on all workers in a pod slice
gcloud compute tpus tpu-vm ssh my-pod-slice \
  --zone=us-central1-b \
  --worker=all \
  --command="pip install jax[tpu] -f https://storage.googleapis.com/jax-releases/libtpu_releases.html" \
  --project=PROJECT_ID

# Copy files to all workers in a pod slice
gcloud compute tpus tpu-vm scp train.py my-pod-slice: \
  --zone=us-central1-b \
  --worker=all \
  --project=PROJECT_ID

# Start a stopped TPU VM
gcloud compute tpus tpu-vm start my-tpu-vm \
  --zone=us-central1-b \
  --project=PROJECT_ID

# Stop a running TPU VM (releases accelerator; preserves disk)
gcloud compute tpus tpu-vm stop my-tpu-vm \
  --zone=us-central1-b \
  --project=PROJECT_ID

# Delete a TPU VM
gcloud compute tpus tpu-vm delete my-tpu-vm \
  --zone=us-central1-b \
  --project=PROJECT_ID
```

### Queued Resources (for Large TPU Allocations)

```bash
# Create a queued resource request (will be fulfilled when capacity available)
gcloud compute tpus queued-resources create my-queued-resource \
  --zone=us-central1-b \
  --accelerator-type=v4-64 \
  --runtime-version=tpu-vm-jax-stable \
  --node-id=my-tpu-pod \
  --project=PROJECT_ID

# Create with a validity interval (cancel if not fulfilled within 2 hours)
gcloud compute tpus queued-resources create my-queued-resource \
  --zone=us-central1-b \
  --accelerator-type=v4-64 \
  --runtime-version=tpu-vm-jax-stable \
  --node-id=my-tpu-pod \
  --valid-until-time="$(date -u -d '+2 hours' '+%Y-%m-%dT%H:%M:%SZ')" \
  --project=PROJECT_ID

# List queued resource requests
gcloud compute tpus queued-resources list \
  --zone=us-central1-b \
  --project=PROJECT_ID

# Describe a queued resource (check state: WAITING → ACCEPTED → ACTIVE)
gcloud compute tpus queued-resources describe my-queued-resource \
  --zone=us-central1-b \
  --project=PROJECT_ID

# Delete a queued resource (cancel the request or release after use)
gcloud compute tpus queued-resources delete my-queued-resource \
  --zone=us-central1-b \
  --force \
  --project=PROJECT_ID
```

### List Available TPU Versions and Types

```bash
# List available TPU runtime versions
gcloud compute tpus tpu-vm versions list \
  --zone=us-central1-b \
  --project=PROJECT_ID

# List available accelerator types in a zone
gcloud compute tpus tpu-vm accelerator-types list \
  --zone=us-central1-b \
  --project=PROJECT_ID

# List accelerator types formatted
gcloud compute tpus tpu-vm accelerator-types list \
  --zone=us-central1-b \
  --format="table(acceleratorType,description)" \
  --project=PROJECT_ID
```

---

## GPU Instances (Compute Engine)

```bash
# Create a single T4 GPU instance
gcloud compute instances create my-t4-vm \
  --zone=us-central1-a \
  --machine-type=n1-standard-8 \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --maintenance-policy=TERMINATE \
  --image-family=pytorch-latest-gpu \
  --image-project=deeplearning-platform-release \
  --boot-disk-size=200GB \
  --boot-disk-type=pd-ssd \
  --project=PROJECT_ID

# Create a quad-A100 instance (a2-highgpu-4g)
gcloud compute instances create my-a100-4gpu \
  --zone=us-central1-a \
  --machine-type=a2-highgpu-4g \
  --maintenance-policy=TERMINATE \
  --image-family=pytorch-latest-gpu \
  --image-project=deeplearning-platform-release \
  --boot-disk-size=500GB \
  --boot-disk-type=pd-ssd \
  --scopes=cloud-platform \
  --service-account=training-sa@PROJECT_ID.iam.gserviceaccount.com \
  --project=PROJECT_ID

# Create an 8x A100 instance for large-scale training
gcloud compute instances create my-a100-8gpu \
  --zone=us-central1-a \
  --machine-type=a2-highgpu-8g \
  --maintenance-policy=TERMINATE \
  --image-family=tf2-latest-gpu \
  --image-project=deeplearning-platform-release \
  --boot-disk-size=1TB \
  --boot-disk-type=pd-balanced \
  --metadata=install-nvidia-driver=True \
  --project=PROJECT_ID

# Create an H100 instance (a3-highgpu-8g)
gcloud compute instances create my-h100 \
  --zone=us-central2-b \
  --machine-type=a3-highgpu-8g \
  --maintenance-policy=TERMINATE \
  --image-family=pytorch-latest-gpu \
  --image-project=deeplearning-platform-release \
  --boot-disk-size=1TB \
  --boot-disk-type=hyperdisk-balanced \
  --metadata=install-nvidia-driver=True \
  --project=PROJECT_ID

# Create an L4 GPU instance (for inference)
gcloud compute instances create my-l4-vm \
  --zone=us-central1-a \
  --machine-type=g2-standard-8 \
  --maintenance-policy=TERMINATE \
  --image-family=pytorch-latest-gpu \
  --image-project=deeplearning-platform-release \
  --boot-disk-size=200GB \
  --project=PROJECT_ID

# Create a preemptible GPU instance (significantly cheaper)
gcloud compute instances create my-preemptible-t4 \
  --zone=us-central1-a \
  --machine-type=n1-standard-8 \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --maintenance-policy=TERMINATE \
  --preemptible \
  --image-family=pytorch-latest-gpu \
  --image-project=deeplearning-platform-release \
  --project=PROJECT_ID

# Create a Spot GPU instance (newer preemptible; better availability)
gcloud compute instances create my-spot-a100 \
  --zone=us-central1-a \
  --machine-type=a2-highgpu-1g \
  --maintenance-policy=TERMINATE \
  --provisioning-model=SPOT \
  --image-family=pytorch-latest-gpu \
  --image-project=deeplearning-platform-release \
  --project=PROJECT_ID

# List available GPU accelerator types in a zone
gcloud compute accelerator-types list \
  --filter="zone:us-central1-a"

# Check GPU utilization and availability in a region
gcloud compute machine-types list \
  --filter="zone:us-central1 AND name:a2"

# Verify NVIDIA driver installed on a running GPU VM
gcloud compute ssh my-t4-vm \
  --zone=us-central1-a \
  --command="nvidia-smi" \
  --project=PROJECT_ID
```

---

## Deep Learning VM Images

```bash
# List available deep learning image families
gcloud compute images list \
  --project=deeplearning-platform-release \
  --format="table(name,family,status)" | head -50

# List only GPU-enabled images
gcloud compute images list \
  --project=deeplearning-platform-release \
  --filter="family:*gpu*" \
  --format="table(name,family)"

# List PyTorch images
gcloud compute images list \
  --project=deeplearning-platform-release \
  --filter="family:pytorch*" \
  --sort-by=creationTimestamp \
  --format="table(name,family,creationTimestamp)"

# Get the latest image in a family
gcloud compute images describe-from-family pytorch-latest-gpu \
  --project=deeplearning-platform-release

# Create a VM using a specific versioned DL image
gcloud compute instances create my-dl-vm \
  --zone=us-central1-a \
  --machine-type=n1-standard-4 \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --maintenance-policy=TERMINATE \
  --image=pytorch-2-2-gpu-debian-11-py310-v20240209 \
  --image-project=deeplearning-platform-release \
  --project=PROJECT_ID
```

---

## Vertex AI Workbench Instances

```bash
# Create a CPU Workbench instance
gcloud workbench instances create my-cpu-notebook \
  --location=us-central1-a \
  --machine-type=n1-standard-4 \
  --vm-image-project=deeplearning-platform-release \
  --vm-image-family=common-cpu-notebooks \
  --boot-disk-size=200 \
  --data-disk-size=200 \
  --project=PROJECT_ID

# Create a GPU Workbench instance (T4)
gcloud workbench instances create my-t4-notebook \
  --location=us-central1-a \
  --machine-type=n1-standard-8 \
  --accelerator-type=NVIDIA_TESLA_T4 \
  --accelerator-core-count=1 \
  --install-gpu-driver \
  --vm-image-project=deeplearning-platform-release \
  --vm-image-family=pytorch-latest-gpu \
  --boot-disk-size=200 \
  --data-disk-size=500 \
  --project=PROJECT_ID

# Create an A100 Workbench instance
gcloud workbench instances create my-a100-notebook \
  --location=us-central1-a \
  --machine-type=a2-highgpu-1g \
  --install-gpu-driver \
  --vm-image-project=deeplearning-platform-release \
  --vm-image-family=pytorch-latest-gpu \
  --boot-disk-size=500 \
  --data-disk-size=1000 \
  --project=PROJECT_ID

# Create with a service account
gcloud workbench instances create my-sa-notebook \
  --location=us-central1-a \
  --machine-type=n1-standard-4 \
  --vm-image-project=deeplearning-platform-release \
  --vm-image-family=common-cpu-notebooks \
  --service-account=notebook-sa@PROJECT_ID.iam.gserviceaccount.com \
  --project=PROJECT_ID

# Create with a custom startup script
gcloud workbench instances create my-custom-notebook \
  --location=us-central1-a \
  --machine-type=n1-standard-4 \
  --vm-image-project=deeplearning-platform-release \
  --vm-image-family=common-cpu-notebooks \
  --post-startup-script=gs://my-bucket/startup.sh \
  --project=PROJECT_ID

# List Workbench instances in a zone
gcloud workbench instances list \
  --location=us-central1-a \
  --project=PROJECT_ID

# List Workbench instances across all zones in a region
gcloud workbench instances list \
  --location=us-central1 \
  --project=PROJECT_ID

# Describe a Workbench instance
gcloud workbench instances describe my-t4-notebook \
  --location=us-central1-a \
  --project=PROJECT_ID

# Get the JupyterLab proxy URL
gcloud workbench instances describe my-t4-notebook \
  --location=us-central1-a \
  --format="value(proxyUri)" \
  --project=PROJECT_ID

# Start a stopped instance
gcloud workbench instances start my-t4-notebook \
  --location=us-central1-a \
  --project=PROJECT_ID

# Stop a running instance (saves cost; data persists)
gcloud workbench instances stop my-t4-notebook \
  --location=us-central1-a \
  --project=PROJECT_ID

# Reset a Workbench instance (restart the VM)
gcloud workbench instances reset my-t4-notebook \
  --location=us-central1-a \
  --project=PROJECT_ID

# Upgrade a Workbench instance (update to newer DL image)
gcloud workbench instances upgrade my-t4-notebook \
  --location=us-central1-a \
  --project=PROJECT_ID

# Delete a Workbench instance
gcloud workbench instances delete my-t4-notebook \
  --location=us-central1-a \
  --project=PROJECT_ID
```

---

## Hyperdisk ML

```bash
# Create a Hyperdisk ML disk for writing training checkpoints
gcloud compute disks create my-model-checkpoint-disk \
  --zone=us-central1-a \
  --type=hyperdisk-ml \
  --size=1TB \
  --provisioned-throughput=1200 \
  --access-mode=READ_WRITE_SINGLE \
  --project=PROJECT_ID

# Create a Hyperdisk ML disk for read-scale model serving (many VMs attach it)
gcloud compute disks create my-model-serving-disk \
  --zone=us-central1-a \
  --type=hyperdisk-ml \
  --size=1TB \
  --provisioned-throughput=1200 \
  --access-mode=READ_ONLY_MANY \
  --project=PROJECT_ID

# Attach a Hyperdisk ML disk to a VM (as read-only for serving fleet)
gcloud compute instances attach-disk my-serving-vm \
  --zone=us-central1-a \
  --disk=my-model-serving-disk \
  --mode=ro \
  --project=PROJECT_ID

# Detach a disk from a VM
gcloud compute instances detach-disk my-serving-vm \
  --zone=us-central1-a \
  --disk=my-model-serving-disk \
  --project=PROJECT_ID

# List Hyperdisk ML disks
gcloud compute disks list \
  --filter="type:hyperdisk-ml" \
  --zones=us-central1-a \
  --project=PROJECT_ID

# Describe a disk
gcloud compute disks describe my-model-serving-disk \
  --zone=us-central1-a \
  --project=PROJECT_ID

# Update disk access mode (e.g., switch from WRITE to READ_ONLY_MANY after training)
gcloud compute disks update my-model-checkpoint-disk \
  --zone=us-central1-a \
  --access-mode=READ_ONLY_MANY \
  --project=PROJECT_ID

# Create a snapshot of a Hyperdisk ML disk
gcloud compute snapshots create my-model-snapshot \
  --source-disk=my-model-checkpoint-disk \
  --source-disk-zone=us-central1-a \
  --storage-location=us-central1 \
  --project=PROJECT_ID

# Delete a disk
gcloud compute disks delete my-model-checkpoint-disk \
  --zone=us-central1-a \
  --project=PROJECT_ID
```

---

## Managed Runtimes (Colab Enterprise)

```bash
# Colab Enterprise runtimes are primarily managed via the UI or Vertex AI SDK
# Enable the Colab Enterprise API
gcloud services enable colab.googleapis.com \
  --project=PROJECT_ID

# List Colab Enterprise runtimes (via Vertex AI Notebooks API)
gcloud colab runtimes list \
  --region=us-central1 \
  --project=PROJECT_ID

# Describe a runtime
gcloud colab runtimes describe RUNTIME_ID \
  --region=us-central1 \
  --project=PROJECT_ID

# Delete a runtime
gcloud colab runtimes delete RUNTIME_ID \
  --region=us-central1 \
  --project=PROJECT_ID
```
