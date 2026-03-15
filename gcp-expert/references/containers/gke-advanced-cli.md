# GKE Deep Dive — Advanced CLI

## Fleet and GKE Enterprise

### Fleet Setup

```bash
# Enable Fleet API
gcloud services enable gkehub.googleapis.com

# Register an existing GKE cluster to a Fleet
gcloud container fleet memberships register my-cluster-membership \
  --gke-cluster=us-central1/my-cluster \
  --enable-workload-identity \
  --project=FLEET_HOST_PROJECT

# Register an external (non-GKE) cluster to a Fleet
gcloud container fleet memberships register my-external-cluster \
  --context=my-external-k8s-context \
  --kubeconfig=/path/to/kubeconfig \
  --enable-workload-identity \
  --project=FLEET_HOST_PROJECT

# List all Fleet memberships
gcloud container fleet memberships list --project=FLEET_HOST_PROJECT

# Describe a Fleet membership
gcloud container fleet memberships describe my-cluster-membership \
  --project=FLEET_HOST_PROJECT

# Delete a Fleet membership (unregisters cluster)
gcloud container fleet memberships delete my-cluster-membership \
  --project=FLEET_HOST_PROJECT

# Create a Fleet (if not already created)
gcloud container fleet create --project=FLEET_HOST_PROJECT --display-name="Production Fleet"

# Create a cluster directly into a Fleet
gcloud container clusters create my-fleet-cluster \
  --location=us-central1 \
  --fleet-project=FLEET_HOST_PROJECT \
  --enable-autopilot
```

### Config Sync

```bash
# Enable Config Sync feature on the Fleet
gcloud container fleet config-management enable --project=FLEET_HOST_PROJECT

# Apply Config Sync configuration for a specific cluster
gcloud container fleet config-management apply \
  --membership=my-cluster-membership \
  --project=FLEET_HOST_PROJECT \
  --config=apply-spec.yaml

# apply-spec.yaml content:
# applySpecVersion: 1
# spec:
#   configSync:
#     enabled: true
#     sourceFormat: unstructured
#     syncRepo: https://github.com/my-org/gke-config
#     syncBranch: main
#     syncRev: HEAD
#     policyDir: clusters/prod
#     secretType: none     # or 'token', 'cookiefile', 'gcenode', 'gcpserviceaccount', 'ssh'
#     preventDrift: true

# Apply using OCI image source (Artifact Registry)
gcloud container fleet config-management apply \
  --membership=my-cluster-membership \
  --project=FLEET_HOST_PROJECT \
  --config=oci-spec.yaml

# oci-spec.yaml content:
# applySpecVersion: 1
# spec:
#   configSync:
#     enabled: true
#     sourceFormat: unstructured
#     ociUrl: us-central1-docker.pkg.dev/PROJECT/repo/config:latest
#     secretType: gcpserviceaccount
#     gcpServiceAccountEmail: config-sync-sa@PROJECT.iam.gserviceaccount.com

# Check Config Sync status across all memberships
gcloud container fleet config-management status --project=FLEET_HOST_PROJECT

# Describe Config Sync status for a specific membership
gcloud container fleet config-management describe \
  --membership=my-cluster-membership \
  --project=FLEET_HOST_PROJECT

# Disable Config Sync for a membership
gcloud container fleet config-management delete \
  --membership=my-cluster-membership \
  --project=FLEET_HOST_PROJECT

# Disable Config Sync feature entirely
gcloud container fleet config-management disable --project=FLEET_HOST_PROJECT
```

### Policy Controller

```bash
# Enable Policy Controller on the Fleet
gcloud container fleet policycontroller enable --project=FLEET_HOST_PROJECT

# Enable Policy Controller with audit-only mode for a membership
gcloud container fleet policycontroller apply \
  --membership=my-cluster-membership \
  --project=FLEET_HOST_PROJECT \
  --audit-interval-seconds=60 \
  --exemptable-namespaces=kube-system,kube-public

# Enable Policy Controller with referential constraints
gcloud container fleet policycontroller update \
  --membership=my-cluster-membership \
  --project=FLEET_HOST_PROJECT \
  --mutation=enabled

# Check Policy Controller status
gcloud container fleet policycontroller status --project=FLEET_HOST_PROJECT

# Describe Policy Controller for a membership
gcloud container fleet policycontroller describe \
  --membership=my-cluster-membership \
  --project=FLEET_HOST_PROJECT

# Disable Policy Controller for a membership
gcloud container fleet policycontroller delete \
  --membership=my-cluster-membership \
  --project=FLEET_HOST_PROJECT

# Disable feature entirely
gcloud container fleet policycontroller disable --project=FLEET_HOST_PROJECT
```

### Multi-Cluster Ingress

```bash
# Enable Multi-Cluster Ingress feature on the Fleet
gcloud container fleet ingress enable \
  --config-membership=my-config-cluster-membership \
  --project=FLEET_HOST_PROJECT

# Check Multi-Cluster Ingress feature status
gcloud container fleet ingress describe --project=FLEET_HOST_PROJECT

# Apply a MultiClusterIngress resource (via kubectl on the config cluster)
kubectl apply -f - <<EOF
apiVersion: networking.gke.io/v1
kind: MultiClusterIngress
metadata:
  name: my-global-ingress
  namespace: prod
  annotations:
    networking.gke.io/static-ip: my-global-static-ip
spec:
  template:
    spec:
      backend:
        serviceName: my-mcs-service
        servicePort: 80
      rules:
        - host: api.example.com
          http:
            paths:
              - path: /
                backend:
                  serviceName: my-mcs-service
                  servicePort: 80
EOF

# Apply a MultiClusterService resource
kubectl apply -f - <<EOF
apiVersion: networking.gke.io/v1
kind: MultiClusterService
metadata:
  name: my-mcs-service
  namespace: prod
spec:
  template:
    spec:
      selector:
        app: my-app
      ports:
        - name: http
          protocol: TCP
          port: 80
          targetPort: 8080
EOF

# List MultiClusterIngress resources
kubectl get multiclusteringress -n prod

# View backend services created by MCI
gcloud compute backend-services list --global
```

---

## Workload Identity

```bash
# Enable Workload Identity on an existing cluster
gcloud container clusters update my-cluster \
  --location=us-central1 \
  --workload-pool=PROJECT_ID.svc.id.goog

# Enable Workload Identity on a new cluster
gcloud container clusters create my-cluster \
  --location=us-central1 \
  --workload-pool=PROJECT_ID.svc.id.goog

# Enable Workload Identity on a node pool
gcloud container node-pools update default-pool \
  --cluster=my-cluster \
  --location=us-central1 \
  --workload-metadata=GKE_METADATA

# Create a GCP service account for a workload
gcloud iam service-accounts create my-workload-sa \
  --display-name="My Workload Service Account"

# Grant the GCP SA the required permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:my-workload-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

# Bind the Kubernetes SA to the GCP SA (Workload Identity binding)
gcloud iam service-accounts add-iam-policy-binding \
  my-workload-sa@PROJECT_ID.iam.gserviceaccount.com \
  --member="serviceAccount:PROJECT_ID.svc.id.goog[my-namespace/my-ksa]" \
  --role="roles/iam.workloadIdentityUser"

# Annotate the Kubernetes ServiceAccount
kubectl annotate serviceaccount my-ksa \
  --namespace=my-namespace \
  iam.gke.io/gcp-service-account=my-workload-sa@PROJECT_ID.iam.gserviceaccount.com

# Verify Workload Identity is working
kubectl run -it --rm wi-test \
  --image=google/cloud-sdk:slim \
  --serviceaccount=my-ksa \
  --namespace=my-namespace \
  -- gcloud auth list
```

---

## GKE Gateway API

```bash
# Enable GKE Gateway Controller on a cluster
gcloud container clusters update my-cluster \
  --location=us-central1 \
  --gateway-api=standard

# List available GatewayClasses
kubectl get gatewayclass

# Deploy a Gateway (External Application Load Balancer)
kubectl apply -f - <<EOF
kind: Gateway
apiVersion: gateway.networking.k8s.io/v1beta1
metadata:
  name: external-http
  namespace: prod
spec:
  gatewayClassName: gke-l7-global-external-managed
  listeners:
    - name: http
      protocol: HTTP
      port: 80
    - name: https
      protocol: HTTPS
      port: 443
      tls:
        mode: Terminate
        certificateRefs:
          - kind: Secret
            name: my-tls-secret
      allowedRoutes:
        namespaces:
          from: All
EOF

# Deploy an HTTPRoute
kubectl apply -f - <<EOF
kind: HTTPRoute
apiVersion: gateway.networking.k8s.io/v1beta1
metadata:
  name: my-app-route
  namespace: prod
spec:
  parentRefs:
    - kind: Gateway
      name: external-http
      namespace: prod
  hostnames:
    - api.example.com
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /v1/users
      backendRefs:
        - name: user-service
          port: 80
    - matches:
        - path:
            type: PathPrefix
            value: /v1/orders
      backendRefs:
        - name: order-service
          port: 80
EOF

# Traffic splitting with HTTPRoute (canary deployment)
kubectl apply -f - <<EOF
kind: HTTPRoute
apiVersion: gateway.networking.k8s.io/v1beta1
metadata:
  name: my-app-canary
  namespace: prod
spec:
  parentRefs:
    - kind: Gateway
      name: external-http
      namespace: prod
  rules:
    - backendRefs:
        - name: my-app-stable
          port: 80
          weight: 90
        - name: my-app-canary
          port: 80
          weight: 10
EOF

# List Gateways and HTTPRoutes
kubectl get gateway -n prod
kubectl get httproute -n prod

# Describe Gateway (see assigned IP address)
kubectl describe gateway external-http -n prod
```

---

## Release Channels and Upgrades

```bash
# Enroll cluster in a release channel
gcloud container clusters update my-cluster \
  --location=us-central1 \
  --release-channel=regular

# Change release channel
gcloud container clusters update my-cluster \
  --location=us-central1 \
  --release-channel=stable

# View available Kubernetes versions for a channel
gcloud container get-server-config \
  --location=us-central1 \
  --format="yaml(channels)"

# Manually upgrade control plane to a specific version (within channel)
gcloud container clusters upgrade my-cluster \
  --location=us-central1 \
  --master \
  --cluster-version=1.31.2-gke.100

# Upgrade a specific node pool
gcloud container clusters upgrade my-cluster \
  --location=us-central1 \
  --node-pool=default-pool \
  --cluster-version=1.31.2-gke.100

# Set maintenance window for upgrades
gcloud container clusters update my-cluster \
  --location=us-central1 \
  --maintenance-window-start="2024-11-01T02:00:00Z" \
  --maintenance-window-end="2024-11-01T06:00:00Z" \
  --maintenance-window-recurrence="FREQ=WEEKLY;BYDAY=SA,SU"

# Add maintenance exclusion (block upgrades during period)
gcloud container clusters update my-cluster \
  --location=us-central1 \
  --add-maintenance-exclusion-name="holiday-freeze" \
  --add-maintenance-exclusion-start="2024-12-20T00:00:00Z" \
  --add-maintenance-exclusion-end="2025-01-02T00:00:00Z" \
  --add-maintenance-exclusion-scope=NO_UPGRADES
```

---

## Node Pools

```bash
# Create a node pool with specific settings
gcloud container node-pools create gpu-pool \
  --cluster=my-cluster \
  --location=us-central1 \
  --machine-type=n1-standard-8 \
  --accelerator=type=nvidia-l4,count=1,gpu-driver-version=latest \
  --num-nodes=0 \
  --enable-autoscaling \
  --min-nodes=0 \
  --max-nodes=10 \
  --node-labels=workload-type=gpu \
  --node-taints=nvidia.com/gpu=present:NoSchedule \
  --workload-metadata=GKE_METADATA \
  --disk-type=pd-ssd \
  --disk-size=100

# Create a Spot (preemptible) node pool for batch workloads
gcloud container node-pools create spot-pool \
  --cluster=my-cluster \
  --location=us-central1 \
  --machine-type=n2-standard-4 \
  --spot \
  --num-nodes=0 \
  --enable-autoscaling \
  --min-nodes=0 \
  --max-nodes=50 \
  --node-taints=cloud.google.com/gke-spot=true:NoSchedule

# Create a gVisor sandbox node pool
gcloud container node-pools create sandbox-pool \
  --cluster=my-cluster \
  --location=us-central1 \
  --machine-type=n2-standard-4 \
  --sandbox=gvisor \
  --num-nodes=2

# Create a Confidential VM node pool
gcloud container node-pools create confidential-pool \
  --cluster=my-cluster \
  --location=us-central1 \
  --machine-type=n2d-standard-4 \
  --enable-confidential-nodes \
  --num-nodes=2

# Enable autoscaling on existing node pool
gcloud container node-pools update default-pool \
  --cluster=my-cluster \
  --location=us-central1 \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=20

# Resize a node pool manually
gcloud container clusters resize my-cluster \
  --location=us-central1 \
  --node-pool=default-pool \
  --num-nodes=5

# Cordon and drain a node pool before deletion
kubectl cordon $(kubectl get nodes -l cloud.google.com/gke-nodepool=old-pool -o name)
kubectl drain $(kubectl get nodes -l cloud.google.com/gke-nodepool=old-pool -o name) \
  --ignore-daemonsets --delete-emptydir-data

# Delete a node pool
gcloud container node-pools delete old-pool \
  --cluster=my-cluster \
  --location=us-central1
```

---

## Node Auto-Provisioning

```bash
# Enable Node Auto-Provisioning on a cluster
gcloud container clusters update my-cluster \
  --location=us-central1 \
  --enable-autoprovisioning \
  --max-cpu=1000 \
  --max-memory=10000 \
  --autoprovisioning-service-account=node-sa@PROJECT_ID.iam.gserviceaccount.com \
  --autoprovisioning-scopes=https://www.googleapis.com/auth/cloud-platform

# Configure NAP with upgrade/repair settings
gcloud container clusters update my-cluster \
  --location=us-central1 \
  --autoprovisioning-upgrade-settings-max-surge-upgrade=1 \
  --autoprovisioning-upgrade-settings-max-unavailable-upgrade=0

# Disable Node Auto-Provisioning
gcloud container clusters update my-cluster \
  --location=us-central1 \
  --no-enable-autoprovisioning
```

---

## Binary Authorization

```bash
# Enable Binary Authorization on a cluster
gcloud container clusters update my-cluster \
  --location=us-central1 \
  --binauthz-evaluation-mode=PROJECT_SINGLETON_POLICY_ENFORCE

# Create a Binary Authorization policy
gcloud container binauthz policy import policy.yaml

# Example policy.yaml:
# admissionWhitelistPatterns:
#   - namePattern: us-central1-docker.pkg.dev/PROJECT/trusted-repo/*
# defaultAdmissionRule:
#   enforcementMode: ENFORCED_BLOCK_AND_AUDIT_LOG
#   evaluationMode: REQUIRE_ATTESTATION
#   requireAttestationsBy:
#     - projects/PROJECT/attestors/my-attestor
# globalPolicyEvaluationMode: ENABLE

# Export current policy
gcloud container binauthz policy export

# Create an attestor
gcloud container binauthz attestors create my-attestor \
  --attestation-authority-note=projects/PROJECT/notes/my-attestor-note \
  --description="Build pipeline attestor"

# List attestors
gcloud container binauthz attestors list

# Add a public key to an attestor (from a Cloud KMS signing key)
gcloud container binauthz attestors public-keys add \
  --attestor=my-attestor \
  --keyversion-project=PROJECT_ID \
  --keyversion-location=us-central1 \
  --keyversion-keyring=binauthz-keyring \
  --keyversion-key=attestor-key \
  --keyversion=1
```
