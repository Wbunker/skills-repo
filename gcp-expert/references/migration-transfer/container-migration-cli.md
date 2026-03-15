# Migrate to Containers — CLI Reference

## Tool: migctl

`migctl` is the dedicated CLI for Migrate to Containers. It is separate from `gcloud` and must be installed independently.

```bash
# Install migctl (requires gcloud and kubectl configured)
gcloud components install migrate-to-containers

# Or download directly
curl -O "https://anthos-migrate.gcr.io/v2/google/anthos-migrate/migctl:latest/linux/amd64"
chmod +x migctl
mv migctl /usr/local/bin/
```

---

## Setup: Install Migration Processing Cluster

```bash
# Step 1: Create a GKE cluster for migration processing
gcloud container clusters create migration-cluster \
  --zone=us-central1-a \
  --machine-type=e2-standard-4 \
  --num-nodes=3 \
  --workload-pool=my-project.svc.id.goog \
  --project=my-project

# Get credentials
gcloud container clusters get-credentials migration-cluster \
  --zone=us-central1-a \
  --project=my-project

# Step 2: Install Migrate to Containers on the cluster
migctl setup install

# Check installation status
migctl setup check

# Step 3: Add a migration source
# For VMware vCenter:
migctl source create vcenter-src \
  --type vsphere \
  --host 192.168.1.100 \
  --user migration-user@vsphere.local \
  --pass 'SECRET_PASSWORD' \
  --datacenter "My Datacenter"

# For AWS EC2:
migctl source create aws-src \
  --type aws \
  --access-key-id AKIAIOSFODNN7EXAMPLE \
  --secret-access-key SECRET \
  --region us-east-1

# For Google Compute Engine (same project):
migctl source create gce-src --type gce
```

---

## Migration Lifecycle

```bash
# Create a migration for a specific VM
# (--source-vm specifies the VM's identifier in the source)
migctl migration create web-server-migration \
  --source vcenter-src \
  --vm "web-server-prod-01" \
  --intent Image

# Check migration status
migctl migration status web-server-migration

# Run fit assessment (analyze VM suitability for containerization)
migctl migration run-assessment web-server-migration

# View fit assessment results
migctl migration get web-server-migration --output yaml

# Generate migration artifacts (Dockerfile + K8s manifests)
migctl migration generate-artifacts web-server-migration

# Watch artifact generation progress
migctl migration status web-server-migration --watch

# Get the generated artifacts (downloads to local directory)
migctl migration get-artifacts web-server-migration
```

---

## Working with Generated Artifacts

```bash
# After generate-artifacts, artifacts are in GCS and downloaded locally
# Edit config.yaml to customize the migration
cat migration-artifacts/config.yaml

# Key fields to customize in config.yaml:
# - endpoint.port: the port your app listens on
# - data.volumes[]: persistent volume mounts
# - environment: environment variables
# - resources.requests/limits: CPU and memory

# Build the container image from generated Dockerfile
docker build -t us-central1-docker.pkg.dev/my-project/my-repo/web-server:v1 \
  -f migration-artifacts/Dockerfile \
  migration-artifacts/

# Or use Cloud Build (recommended for CI/CD)
gcloud builds submit migration-artifacts/ \
  --tag=us-central1-docker.pkg.dev/my-project/my-repo/web-server:v1 \
  --project=my-project

# Push to Artifact Registry
docker push us-central1-docker.pkg.dev/my-project/my-repo/web-server:v1

# Apply generated Kubernetes manifests to target cluster
# (switch to your production GKE cluster first)
gcloud container clusters get-credentials prod-cluster \
  --zone=us-central1-a \
  --project=my-project

kubectl apply -f migration-artifacts/deployment_spec.yaml

# Verify deployment
kubectl get pods -l app=web-server
kubectl get services -l app=web-server
kubectl describe deployment web-server
```

---

## GKE Cluster Registration (for Source Clusters)

If using Migrate to Containers with a GKE source cluster:

```bash
# Register source cluster to Fleet
gcloud container fleet memberships register source-cluster \
  --gke-cluster=us-central1-a/source-cluster \
  --enable-workload-identity \
  --project=my-project

# List registered memberships
gcloud container fleet memberships list --project=my-project

# Describe a membership
gcloud container fleet memberships describe source-cluster \
  --project=my-project
```

---

## Artifact Registry for Migrated Images

```bash
# Create a repository for migrated container images
gcloud artifacts repositories create migrated-apps \
  --repository-format=docker \
  --location=us-central1 \
  --description="Migrated container images" \
  --project=my-project

# Configure Docker authentication for Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

# List images in the repository
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/my-project/migrated-apps \
  --include-tags \
  --project=my-project
```

---

## Post-Migration Validation

```bash
# Check that pods are running
kubectl get pods -n default -l app=web-server --watch

# View pod logs
kubectl logs -l app=web-server -f --tail=100

# Execute into a running container to validate
kubectl exec -it $(kubectl get pod -l app=web-server -o jsonpath='{.items[0].metadata.name}') -- /bin/bash

# Run a quick curl test against the service
kubectl run curl-test --image=curlimages/curl --rm -it --restart=Never -- \
  curl http://web-server-service:8080/health

# Check resource consumption vs limits
kubectl top pods -l app=web-server
kubectl top nodes
```

---

## Cleanup Migration Processing Cluster

After migrations are complete, the processing cluster can be deleted to save costs:

```bash
# Uninstall Migrate to Containers components
migctl setup uninstall

# Delete the processing cluster
gcloud container clusters delete migration-cluster \
  --zone=us-central1-a \
  --project=my-project \
  --quiet
```
