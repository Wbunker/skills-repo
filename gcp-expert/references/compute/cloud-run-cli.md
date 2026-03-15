# Cloud Run — CLI Reference

Capabilities reference: [cloud-run-capabilities.md](cloud-run-capabilities.md)

All commands use `gcloud run` unless otherwise noted.

```bash
# Set defaults to avoid repeating flags
gcloud config set run/region us-central1
gcloud config set project my-project-id
```

---

## Services

### Deploy a Service

```bash
# Basic service deploy from Artifact Registry image
gcloud run deploy my-service \
  --image=us-central1-docker.pkg.dev/my-project/my-repo/my-app:v1.2.3 \
  --region=us-central1 \
  --allow-unauthenticated

# Deploy with resource limits and scaling configuration
gcloud run deploy my-api \
  --image=us-central1-docker.pkg.dev/my-project/my-repo/my-api:latest \
  --region=us-central1 \
  --memory=1Gi \
  --cpu=2 \
  --concurrency=100 \
  --min-instances=1 \
  --max-instances=50 \
  --timeout=30s \
  --port=8080 \
  --service-account=my-run-sa@my-project.iam.gserviceaccount.com \
  --no-allow-unauthenticated

# Deploy with environment variables
gcloud run deploy my-service \
  --image=us-central1-docker.pkg.dev/my-project/my-repo/my-app:v2 \
  --region=us-central1 \
  --set-env-vars=ENV=production,LOG_LEVEL=info,DB_HOST=10.0.0.5 \
  --allow-unauthenticated

# Deploy with secrets from Secret Manager (as env vars)
gcloud run deploy my-service \
  --image=us-central1-docker.pkg.dev/my-project/my-repo/my-app:v2 \
  --region=us-central1 \
  --set-secrets=DB_PASSWORD=db-password:latest,API_KEY=my-api-key:v3

# Deploy with secrets mounted as files
gcloud run deploy my-service \
  --image=us-central1-docker.pkg.dev/my-project/my-repo/my-app:v2 \
  --region=us-central1 \
  --set-secrets=/secrets/db-password=db-password:latest

# Deploy with VPC connector
gcloud run deploy my-service \
  --image=us-central1-docker.pkg.dev/my-project/my-repo/my-app:v2 \
  --region=us-central1 \
  --vpc-connector=my-vpc-connector \
  --vpc-egress=all-traffic

# Deploy with CPU always allocated (for background processing)
gcloud run deploy my-worker \
  --image=us-central1-docker.pkg.dev/my-project/my-repo/my-worker:latest \
  --region=us-central1 \
  --cpu-always-allocated \
  --min-instances=1 \
  --max-instances=10 \
  --no-allow-unauthenticated

# Deploy with 2nd generation execution environment
gcloud run deploy my-service \
  --image=us-central1-docker.pkg.dev/my-project/my-repo/my-app:latest \
  --region=us-central1 \
  --execution-environment=gen2

# Deploy with HTTP/2 enabled (for gRPC)
gcloud run deploy my-grpc-service \
  --image=us-central1-docker.pkg.dev/my-project/my-repo/my-grpc-app:latest \
  --region=us-central1 \
  --use-http2

# Deploy from source (builds via Cloud Build and pushes to Artifact Registry)
gcloud run deploy my-service \
  --source=. \
  --region=us-central1 \
  --allow-unauthenticated
```

### Describe and List Services

```bash
# List all services in a region
gcloud run services list --region=us-central1

# List all services across all regions
gcloud run services list --platform=managed

# Describe a service (full configuration)
gcloud run services describe my-service --region=us-central1

# Get the service URL
gcloud run services describe my-service \
  --region=us-central1 \
  --format="get(status.url)"

# List services with custom format
gcloud run services list \
  --region=us-central1 \
  --format="table(metadata.name,status.url,status.conditions[0].status)"
```

### Update a Service

```bash
# Update environment variables (add/update, preserving existing)
gcloud run services update my-service \
  --region=us-central1 \
  --update-env-vars=LOG_LEVEL=debug

# Replace all environment variables
gcloud run services update my-service \
  --region=us-central1 \
  --set-env-vars=ENV=staging,LOG_LEVEL=debug

# Remove an environment variable
gcloud run services update my-service \
  --region=us-central1 \
  --remove-env-vars=OLD_VAR

# Update scaling
gcloud run services update my-service \
  --region=us-central1 \
  --min-instances=2 \
  --max-instances=100

# Update container image only (creates new revision)
gcloud run services update my-service \
  --region=us-central1 \
  --image=us-central1-docker.pkg.dev/my-project/my-repo/my-app:v1.3.0

# Update memory and CPU
gcloud run services update my-service \
  --region=us-central1 \
  --memory=2Gi \
  --cpu=4

# Update concurrency
gcloud run services update my-service \
  --region=us-central1 \
  --concurrency=200
```

### Delete a Service

```bash
gcloud run services delete my-service --region=us-central1 --quiet
```

---

## Revisions

```bash
# List revisions for a service
gcloud run revisions list --service=my-service --region=us-central1

# List revisions with traffic allocation
gcloud run revisions list \
  --service=my-service \
  --region=us-central1 \
  --format="table(metadata.name,status.observedGeneration,metadata.annotations['serving.knative.dev/route'],spec.containerConcurrency)"

# Describe a specific revision
gcloud run revisions describe my-service-00023-xyz --region=us-central1

# Delete an old revision (cannot delete a revision serving traffic)
gcloud run revisions delete my-service-00001-abc --region=us-central1 --quiet
```

---

## Traffic Splitting

```bash
# Send 100% traffic to the latest revision
gcloud run services update-traffic my-service \
  --region=us-central1 \
  --to-latest

# Send 90% to current, 10% to specific revision (canary)
gcloud run services update-traffic my-service \
  --region=us-central1 \
  --to-revisions=my-service-00022-abc=90,my-service-00023-xyz=10

# Roll back to a previous revision (100%)
gcloud run services update-traffic my-service \
  --region=us-central1 \
  --to-revisions=my-service-00021-def=100

# Tag a revision for direct testing without traffic allocation
gcloud run services update-traffic my-service \
  --region=us-central1 \
  --set-tags=canary=my-service-00023-xyz

# Access the tagged revision directly (no production traffic)
# URL format: https://canary---my-service-HASH-uc.a.run.app

# Remove a tag
gcloud run services update-traffic my-service \
  --region=us-central1 \
  --remove-tags=canary
```

---

## Cloud Run Jobs

```bash
# Create a job
gcloud run jobs create my-batch-job \
  --image=us-central1-docker.pkg.dev/my-project/my-repo/my-batch:latest \
  --region=us-central1 \
  --tasks=10 \
  --max-retries=3 \
  --parallelism=5 \
  --task-timeout=1h \
  --memory=2Gi \
  --cpu=2 \
  --service-account=my-batch-sa@my-project.iam.gserviceaccount.com \
  --set-env-vars=INPUT_BUCKET=gs://my-data,OUTPUT_BUCKET=gs://my-results

# Execute a job immediately
gcloud run jobs execute my-batch-job \
  --region=us-central1 \
  --wait

# Execute a job with overridden environment variables for this run
gcloud run jobs execute my-batch-job \
  --region=us-central1 \
  --update-env-vars=BATCH_DATE=2024-01-15 \
  --wait

# List all executions of a job
gcloud run jobs executions list \
  --job=my-batch-job \
  --region=us-central1

# Describe a specific execution
gcloud run jobs executions describe my-batch-job-execution-abc \
  --region=us-central1

# Describe a job
gcloud run jobs describe my-batch-job --region=us-central1

# List all jobs
gcloud run jobs list --region=us-central1

# Update a job configuration
gcloud run jobs update my-batch-job \
  --region=us-central1 \
  --image=us-central1-docker.pkg.dev/my-project/my-repo/my-batch:v2 \
  --tasks=20 \
  --parallelism=10

# Cancel a running execution
gcloud run jobs executions cancel my-batch-job-execution-abc \
  --region=us-central1

# Delete a job
gcloud run jobs delete my-batch-job --region=us-central1 --quiet
```

---

## Domain Mappings

```bash
# Create a domain mapping (maps custom domain to Cloud Run service)
gcloud run domain-mappings create \
  --service=my-service \
  --domain=api.example.com \
  --region=us-central1

# List domain mappings
gcloud run domain-mappings list --region=us-central1

# Describe a domain mapping (shows DNS records to create)
gcloud run domain-mappings describe --domain=api.example.com --region=us-central1

# Delete a domain mapping
gcloud run domain-mappings delete --domain=api.example.com --region=us-central1 --quiet
```

---

## IAM and Invoker Permissions

```bash
# Allow unauthenticated (public) access to a service
gcloud run services add-iam-policy-binding my-service \
  --region=us-central1 \
  --member=allUsers \
  --role=roles/run.invoker

# Grant a service account invoker access (for service-to-service calls)
gcloud run services add-iam-policy-binding my-service \
  --region=us-central1 \
  --member=serviceAccount:caller-sa@my-project.iam.gserviceaccount.com \
  --role=roles/run.invoker

# Grant a specific user invoker access
gcloud run services add-iam-policy-binding my-service \
  --region=us-central1 \
  --member=user:developer@example.com \
  --role=roles/run.invoker

# Grant Cloud Scheduler service account invoker access for scheduled triggers
gcloud run services add-iam-policy-binding my-service \
  --region=us-central1 \
  --member=serviceAccount:my-scheduler-sa@my-project.iam.gserviceaccount.com \
  --role=roles/run.invoker

# Grant Pub/Sub service account invoker access (for push subscriptions)
PROJECT_NUMBER=$(gcloud projects describe my-project --format="get(projectNumber)")
gcloud run services add-iam-policy-binding my-service \
  --region=us-central1 \
  --member=serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-pubsub.iam.gserviceaccount.com \
  --role=roles/run.invoker

# Get IAM policy for a service
gcloud run services get-iam-policy my-service --region=us-central1

# Remove an IAM binding
gcloud run services remove-iam-policy-binding my-service \
  --region=us-central1 \
  --member=user:former-dev@example.com \
  --role=roles/run.invoker
```

---

## Serverless VPC Access Connector

```bash
# Create a Serverless VPC Access connector (prerequisite for Cloud Run VPC access)
gcloud compute networks vpc-access connectors create my-vpc-connector \
  --region=us-central1 \
  --subnet=my-serverless-subnet \
  --subnet-project=my-project \
  --min-instances=2 \
  --max-instances=10 \
  --machine-type=e2-micro

# Or create with IP range (simpler, no dedicated subnet needed)
gcloud compute networks vpc-access connectors create my-vpc-connector \
  --region=us-central1 \
  --network=my-vpc \
  --range=10.8.0.0/28 \
  --min-instances=2 \
  --max-instances=10

# List connectors
gcloud compute networks vpc-access connectors list --region=us-central1

# Deploy Cloud Run with the connector
gcloud run deploy my-service \
  --image=us-central1-docker.pkg.dev/my-project/my-repo/my-app:latest \
  --region=us-central1 \
  --vpc-connector=my-vpc-connector \
  --vpc-egress=private-ranges-only
```

---

## Invoking Cloud Run Services

```bash
# Get a token and invoke the service (for testing authenticated services)
TOKEN=$(gcloud auth print-identity-token)
curl -H "Authorization: Bearer ${TOKEN}" https://my-service-HASH-uc.a.run.app/api/health

# Invoke using gcloud (wraps token generation)
gcloud run services proxy my-service --region=us-central1 --port=8080
# Then curl http://localhost:8080/api/health in another terminal
```
