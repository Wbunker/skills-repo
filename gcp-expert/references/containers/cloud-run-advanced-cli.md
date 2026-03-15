# Cloud Run Advanced — CLI

## Traffic Splitting and Revision Management

```bash
# Deploy a new revision (default: 100% traffic immediately)
gcloud run deploy my-service \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-app:v2 \
  --region=us-central1 \
  --no-traffic    # deploy without sending any traffic to this revision

# List revisions and their traffic allocations
gcloud run revisions list \
  --service=my-service \
  --region=us-central1

# Describe a specific revision
gcloud run revisions describe my-service-00003-abc \
  --region=us-central1

# Split traffic: 90% to stable, 10% canary
gcloud run services update-traffic my-service \
  --region=us-central1 \
  --to-revisions=my-service-00002-xyz=90,my-service-00003-abc=10

# Gradually increase canary to 50/50
gcloud run services update-traffic my-service \
  --region=us-central1 \
  --to-revisions=my-service-00002-xyz=50,my-service-00003-abc=50

# Promote canary to 100% (complete the rollout)
gcloud run services update-traffic my-service \
  --region=us-central1 \
  --to-latest   # send all traffic to the latest revision

# Or explicitly specify the revision
gcloud run services update-traffic my-service \
  --region=us-central1 \
  --to-revisions=my-service-00003-abc=100

# Rollback: send all traffic to a specific older revision
gcloud run services update-traffic my-service \
  --region=us-central1 \
  --to-revisions=my-service-00002-xyz=100

# Deploy with a tag for testing without affecting live traffic
gcloud run deploy my-service \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-app:v3 \
  --region=us-central1 \
  --no-traffic \
  --tag=canary-v3
# Access via: https://canary-v3---my-service-HASH-uc.a.run.app

# Deploy with a tag AND allocate some traffic
gcloud run deploy my-service \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-app:v3 \
  --region=us-central1 \
  --tag=v3 \
  --no-traffic
gcloud run services update-traffic my-service \
  --region=us-central1 \
  --to-tags=v3=10

# Delete old revisions (keep last N)
gcloud run revisions delete my-service-00001-abc \
  --region=us-central1 \
  --quiet

# Delete multiple old revisions
for rev in $(gcloud run revisions list --service=my-service --region=us-central1 \
    --format="value(metadata.name)" | tail -n +6); do
  gcloud run revisions delete $rev --region=us-central1 --quiet
done
```

---

## GPU Deployment

```bash
# Deploy a Cloud Run service with an NVIDIA L4 GPU
gcloud run deploy llm-inference \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/llm-server:latest \
  --region=us-central1 \
  --execution-environment=gen2 \
  --gpu=1 \
  --gpu-type=nvidia-l4 \
  --no-cpu-throttling \
  --cpu=8 \
  --memory=32Gi \
  --min-instances=1 \
  --max-instances=5 \
  --timeout=300s \
  --concurrency=1 \
  --no-allow-unauthenticated \
  --service-account=llm-sa@PROJECT_ID.iam.gserviceaccount.com

# Deploy with 4 GPUs (for larger models)
gcloud run deploy large-llm \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/llm-large:latest \
  --region=us-central1 \
  --execution-environment=gen2 \
  --gpu=4 \
  --gpu-type=nvidia-l4 \
  --no-cpu-throttling \
  --cpu=8 \
  --memory=32Gi \
  --min-instances=1 \
  --max-instances=2 \
  --timeout=600s \
  --concurrency=1
```

---

## Sidecar (Multi-Container) Deployment

Multi-container Cloud Run services require a YAML spec. Create the YAML and use `gcloud run services replace`.

```yaml
# service-with-sidecar.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: my-service
  annotations:
    run.googleapis.com/launch-stage: BETA
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/execution-environment: gen2
    spec:
      serviceAccountName: my-runtime-sa@PROJECT_ID.iam.gserviceaccount.com
      containers:
        # Main (ingress) container
        - name: app
          image: us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-app:latest
          ports:
            - name: http1
              containerPort: 8080
          env:
            - name: DB_HOST
              value: "127.0.0.1"
            - name: DB_PORT
              value: "5432"
          resources:
            limits:
              cpu: "2"
              memory: "2Gi"
          startupProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
            failureThreshold: 10
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            periodSeconds: 30

        # Sidecar: Cloud SQL Auth Proxy
        - name: cloud-sql-proxy
          image: gcr.io/cloud-sql-connectors/cloud-sql-proxy:2.13.0
          args:
            - "--port=5432"
            - "PROJECT_ID:us-central1:my-postgres-instance"
          resources:
            limits:
              cpu: "0.5"
              memory: "256Mi"
```

```bash
# Deploy multi-container service from YAML
gcloud run services replace service-with-sidecar.yaml --region=us-central1

# Update and redeploy
gcloud run services replace service-with-sidecar.yaml --region=us-central1

# Export current service spec as YAML
gcloud run services describe my-service \
  --region=us-central1 \
  --format=export > current-service.yaml
```

---

## Health Checks

```bash
# Deploy with startup and liveness probes (via YAML spec)
# Include probes in service YAML as shown in sidecar section above.

# Or set probes via gcloud flags (HTTP probe example):
gcloud run deploy my-service \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-app:latest \
  --region=us-central1 \
  --startup-probe-initial-delay=5 \
  --startup-probe-period=5 \
  --startup-probe-failure-threshold=10 \
  --startup-probe-timeout=1 \
  --startup-probe-http-path=/healthz \
  --liveness-probe-period=30 \
  --liveness-probe-failure-threshold=3 \
  --liveness-probe-http-path=/healthz
```

---

## Multi-Region with Global Load Balancer

```bash
# Deploy the same service to multiple regions
for region in us-central1 europe-west1 asia-east1; do
  gcloud run deploy my-global-service \
    --image=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-app:latest \
    --region=${region} \
    --no-allow-unauthenticated \
    --min-instances=1
done

# Create Serverless NEGs for each region
for region in us-central1 europe-west1 asia-east1; do
  gcloud compute network-endpoint-groups create my-service-neg-${region} \
    --region=${region} \
    --network-endpoint-type=serverless \
    --cloud-run-service=my-global-service
done

# Reserve a global static external IP
gcloud compute addresses create my-global-ip --global

# Create a backend service
gcloud compute backend-services create my-global-backend \
  --global \
  --load-balancing-scheme=EXTERNAL_MANAGED

# Add all NEGs as backends
for region in us-central1 europe-west1 asia-east1; do
  gcloud compute backend-services add-backend my-global-backend \
    --global \
    --network-endpoint-group=my-service-neg-${region} \
    --network-endpoint-group-region=${region}
done

# Create a URL map
gcloud compute url-maps create my-global-url-map \
  --default-service=my-global-backend

# Create an HTTPS target proxy with a managed certificate
gcloud compute ssl-certificates create my-ssl-cert \
  --global \
  --domains=api.example.com

gcloud compute target-https-proxies create my-https-proxy \
  --global \
  --url-map=my-global-url-map \
  --ssl-certificates=my-ssl-cert

# Create HTTPS forwarding rule (binds IP to target proxy)
gcloud compute forwarding-rules create my-https-forwarding-rule \
  --global \
  --load-balancing-scheme=EXTERNAL_MANAGED \
  --address=my-global-ip \
  --target-https-proxy=my-https-proxy \
  --ports=443

# Create HTTP to HTTPS redirect
gcloud compute url-maps import my-http-redirect-map --global <<EOF
kind: compute#urlMap
name: my-http-redirect-map
defaultUrlRedirect:
  httpsRedirect: true
  redirectResponseCode: MOVED_PERMANENTLY_DEFAULT
EOF

gcloud compute target-http-proxies create my-http-proxy \
  --global \
  --url-map=my-http-redirect-map

gcloud compute forwarding-rules create my-http-forwarding-rule \
  --global \
  --load-balancing-scheme=EXTERNAL_MANAGED \
  --address=my-global-ip \
  --target-http-proxy=my-http-proxy \
  --ports=80

# Get the global IP address
gcloud compute addresses describe my-global-ip --global \
  --format="value(address)"
```

---

## Custom Domain Mappings

```bash
# Create a domain mapping (simple, single-region)
gcloud run domain-mappings create \
  --service=my-service \
  --domain=api.example.com \
  --region=us-central1

# List domain mappings
gcloud run domain-mappings list --region=us-central1

# Describe a domain mapping (get DNS records to configure)
gcloud run domain-mappings describe \
  --domain=api.example.com \
  --region=us-central1

# Delete a domain mapping
gcloud run domain-mappings delete \
  --domain=api.example.com \
  --region=us-central1
```

---

## Instance Scaling and CPU Settings

```bash
# Set min and max instances
gcloud run deploy my-service \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-app:latest \
  --region=us-central1 \
  --min-instances=2 \
  --max-instances=100 \
  --concurrency=80 \
  --cpu=1 \
  --memory=512Mi

# Enable CPU always allocated (for background processing)
gcloud run deploy my-service \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-app:latest \
  --region=us-central1 \
  --no-cpu-throttling \
  --min-instances=1

# Enable CPU boost for faster cold starts
gcloud run deploy my-service \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-app:latest \
  --region=us-central1 \
  --cpu-boost \
  --min-instances=0

# Enable session affinity
gcloud run deploy my-service \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-app:latest \
  --region=us-central1 \
  --session-affinity
```

---

## Cloud Run Integrations

```bash
# List available integration types
gcloud run integrations types list --region=us-central1

# Create a Cloud SQL integration for a service
gcloud run integrations create \
  --service=my-service \
  --type=cloudsql \
  --region=us-central1 \
  --parameters=instance=PROJECT_ID:us-central1:my-instance

# Create a Redis (Memorystore) integration
gcloud run integrations create \
  --service=my-service \
  --type=redis \
  --region=us-central1 \
  --parameters=memory-size-gb=1

# Create a Cloud Storage integration
gcloud run integrations create \
  --service=my-service \
  --type=cloudstorage \
  --region=us-central1

# List integrations for a service
gcloud run integrations list --region=us-central1

# Describe an integration
gcloud run integrations describe INTEGRATION_NAME --region=us-central1

# Delete an integration
gcloud run integrations delete INTEGRATION_NAME \
  --region=us-central1 \
  --service=my-service
```

---

## Service Describe and IAM

```bash
# Describe a Cloud Run service (full details)
gcloud run services describe my-service --region=us-central1

# Get service URL
gcloud run services describe my-service \
  --region=us-central1 \
  --format="value(status.url)"

# Allow unauthenticated access (public)
gcloud run services add-iam-policy-binding my-service \
  --region=us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"

# Restrict to authenticated users only
gcloud run services remove-iam-policy-binding my-service \
  --region=us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"

# Grant invoker to a specific service account
gcloud run services add-iam-policy-binding my-service \
  --region=us-central1 \
  --member="serviceAccount:caller-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

# Get service IAM policy
gcloud run services get-iam-policy my-service --region=us-central1

# Delete a service
gcloud run services delete my-service --region=us-central1
```
