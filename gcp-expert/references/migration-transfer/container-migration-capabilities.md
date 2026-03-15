# Migrate to Containers — Capabilities

## Purpose

**Migrate to Containers** (formerly Anthos Migrate) automatically extracts applications from existing VMs and converts them into containers suitable for deployment on GKE. Rather than manually Dockerizing an application, the tool analyzes the VM's filesystem and running processes, then generates Dockerfiles and Kubernetes manifests.

---

## Supported Sources

| Source Type | Requirements |
|---|---|
| VMware vSphere VMs | vSphere 6.5 or later; VM running and accessible |
| AWS EC2 instances | EC2 instance reachable from the migration cluster |
| Google Compute Engine VMs | Same-project GCE VMs |

**Guest OS requirements:**
- Linux: RHEL/CentOS 7-8, Ubuntu 16.04-20.04, Debian 9-10
- Windows: limited support for Windows Server workloads (containerized Windows is less common)

---

## Core Workflow

### Step 1: Setup Migration Processing Cluster
- Deploy a **migration processing cluster**: a GKE cluster where the migration tooling runs
- The cluster does not serve the migrated workloads; it is only used during migration
- Install Migrate to Containers components via Helm or `migctl setup install`

### Step 2: Connect Source Environment
- For VMware: add vCenter credentials to the migration cluster
- For AWS: add AWS credentials (access key or IAM role via IRSA)
- For GCE: the cluster has automatic access via service account

### Step 3: Create Migration
- Define a Migration object pointing to the source VM
- The migration tooling connects to the source VM, analyzes the filesystem and running processes
- **Fit Assessment**: automated analysis of whether the VM is suitable for containerization
  - **Blockers**: issues that prevent migration (e.g., unsupported kernel module, GUI application)
  - **Warnings**: issues that may need attention (e.g., persistent state that should be externalized)
  - **Notes**: informational items

### Step 4: Generate Artifacts
- Run `migctl migration generate-artifacts`
- Output artifacts written to a Cloud Storage bucket:
  - **Dockerfile**: builds the container image; extracts the OS and application layers
  - **deployment_spec.yaml**: Kubernetes Deployment, Service, and PersistentVolumeClaim definitions
  - **config.yaml**: migration configuration; customize machine type, storage, network

### Step 5: Review and Customize Artifacts
- Review generated Dockerfile; add any missing dependencies
- Customize Kubernetes manifests:
  - Resource requests/limits (Migrate to Containers makes estimates)
  - Liveness/readiness probes (must add manually)
  - ConfigMaps for environment-specific configuration
  - PersistentVolume configuration for stateful data
  - Service type (ClusterIP, LoadBalancer, NodePort)
- Externalize state: replace local file storage with Cloud Storage, Cloud SQL, Memorystore

### Step 6: Build and Deploy
- Build container image from generated Dockerfile: `docker build` or Cloud Build
- Push to Artifact Registry
- Deploy generated Kubernetes manifests to target GKE cluster: `kubectl apply -f deployment_spec.yaml`

---

## Fit Assessment Details

The fit assessment categorizes source VMs:

| Category | Meaning |
|---|---|
| Excellent fit | Stateless app, no kernel dependencies, Linux app tier; best candidate |
| Good fit | Minor issues; containerizable with minor artifact edits |
| Moderate fit | Requires some refactoring; persistent state needs externalization |
| Poor fit | Significant blocking issues; manual containerization may be faster |
| Not recommended | DB engines, OS daemons, VM-level appliances; use Migrate to VMs instead |

**Applications that containerize well:**
- Java/Tomcat web applications
- Python/Node.js/Ruby web applications (if not using virtual environments with path dependencies)
- Custom Linux daemons/services
- Static file servers

**Applications that containerize poorly or should stay on VMs:**
- Relational databases (MySQL, PostgreSQL, Oracle) — use Cloud SQL instead
- Message brokers (ActiveMQ, RabbitMQ) — use Pub/Sub or managed equivalents
- NFS/CIFS servers — use Filestore instead
- Applications with kernel-level drivers or custom kernel modules
- GUI applications (no display server in containers)
- License-server-dependent applications

---

## Artifact Structure

After `generate-artifacts`, the output GCS bucket contains:

```
migration-artifacts/
├── Dockerfile           # Multi-stage; extracts app layer from OS layer
├── deployment_spec.yaml # K8s Deployment + Service + PVC + ConfigMap
├── config.yaml          # Editable migration config (ports, volumes, env vars)
├── logs/                # Migration analysis logs
└── data_volumes/        # Persistent data extracted from VM (if any)
```

**Dockerfile pattern:**
```dockerfile
# Generated Dockerfile example (illustrative)
FROM gcr.io/migrate-containers/base-image:latest AS migrated

# Copy application layer (extracted from source VM)
COPY --from=source /opt/tomcat /opt/tomcat
COPY --from=source /etc/myapp /etc/myapp

# Configure entry point
EXPOSE 8080
CMD ["/opt/tomcat/bin/catalina.sh", "run"]
```

---

## Modernization After Migration

Migrate to Containers produces a running container, but further modernization improves reliability and operability:

| Area | Before (Migrated) | After (Modernized) |
|---|---|---|
| Configuration | Hardcoded in image | Kubernetes ConfigMaps and Secrets |
| Health checks | None | Liveness + readiness probes |
| Resource limits | Best-guess estimates | Profiled actual usage; VPA recommendations |
| State storage | Local filesystem in PVC | Cloud SQL, Memorystore, Cloud Storage |
| Logging | stdout mixed with app logs | Structured JSON logs to Cloud Logging |
| Scaling | Fixed replica count | HorizontalPodAutoscaler |
| Security | Root user | Non-root user; read-only root filesystem |

---

## Integration with Cloud Build (CI/CD)

After artifact generation, integrate into Cloud Build for ongoing image builds:

```yaml
# cloudbuild.yaml for migrated app
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'us-central1-docker.pkg.dev/my-project/my-repo/migrated-app:$SHORT_SHA', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'us-central1-docker.pkg.dev/my-project/my-repo/migrated-app:$SHORT_SHA']
  - name: 'gcr.io/cloud-builders/kubectl'
    args: ['set', 'image', 'deployment/migrated-app', 'app=us-central1-docker.pkg.dev/my-project/my-repo/migrated-app:$SHORT_SHA']
    env:
      - 'CLOUDSDK_COMPUTE_ZONE=us-central1-a'
      - 'CLOUDSDK_CONTAINER_CLUSTER=prod-cluster'
```
