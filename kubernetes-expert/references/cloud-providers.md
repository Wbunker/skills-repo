# Managed Kubernetes on Cloud Providers: GKE, EKS, and AKS

This reference covers the three major managed Kubernetes offerings corresponding to Chapters 14-16 of "The Kubernetes Bible" by Russ McKendrick. Each section provides CLI-driven workflows, architecture details, and provider-specific features.

## Google Kubernetes Engine (GKE)

GKE is Google Cloud's managed Kubernetes service. Google originated Kubernetes internally (as Borg), and GKE reflects that lineage with tight integration into Google Cloud infrastructure and an opinionated operational model.

### Cluster Creation

```bash
# Authenticate and set project
gcloud auth login
gcloud config set project my-project-id
gcloud config set compute/region us-central1

# Create a Standard mode cluster with a default node pool
gcloud container clusters create my-cluster \
  --region us-central1 \
  --num-nodes 2 \
  --machine-type e2-standard-4 \
  --disk-size 100 \
  --enable-ip-alias \
  --release-channel regular

# Create an Autopilot cluster (Google manages node infrastructure)
gcloud container clusters create-auto my-autopilot-cluster \
  --region us-central1 \
  --release-channel regular
```

### Autopilot vs Standard Mode

**Standard mode** gives you full control over node configuration, machine types, node pools, and scaling policies. You pay per node (VM) regardless of utilization.

**Autopilot mode** removes node-level management entirely. Google provisions and scales nodes automatically based on Pod resource requests. You pay per Pod resource (CPU, memory, ephemeral storage) rather than per VM. Autopilot enforces security best practices: Pods run as non-root by default, host access is restricted, and privileged containers are disallowed unless explicitly exempted.

Use Standard when you need GPU node pools, specific kernel modules, DaemonSets with host access, or fine-grained node tuning. Use Autopilot for most production workloads where operational simplicity is preferred.

### Node Pool Management

```bash
# Add a node pool with autoscaling
gcloud container node-pools create high-memory-pool \
  --cluster my-cluster \
  --region us-central1 \
  --machine-type n2-highmem-8 \
  --num-nodes 1 \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 10 \
  --enable-autorepair \
  --enable-autoupgrade

# Add a preemptible (spot) node pool for batch workloads
gcloud container node-pools create spot-pool \
  --cluster my-cluster \
  --region us-central1 \
  --machine-type e2-standard-4 \
  --spot \
  --num-nodes 0 \
  --enable-autoscaling \
  --min-nodes 0 \
  --max-nodes 20

# Resize a node pool manually
gcloud container clusters resize my-cluster \
  --node-pool high-memory-pool \
  --num-nodes 3 \
  --region us-central1

# List node pools
gcloud container node-pools list --cluster my-cluster --region us-central1
```

Auto-upgrade keeps nodes on a supported Kubernetes version according to the chosen release channel (rapid, regular, or stable). Auto-repair detects unhealthy nodes and recreates them automatically.

### GKE-Specific Features

**Workload Identity** is the recommended way to grant Pods access to Google Cloud APIs. It binds a Kubernetes ServiceAccount to a Google Cloud IAM service account, eliminating the need for exported JSON keys.

```bash
# Enable Workload Identity on the cluster
gcloud container clusters update my-cluster \
  --region us-central1 \
  --workload-pool=my-project-id.svc.id.goog

# Create a Google Cloud service account and bind it
gcloud iam service-accounts create my-app-sa \
  --display-name "My App Service Account"

gcloud iam service-accounts add-iam-policy-binding \
  my-app-sa@my-project-id.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:my-project-id.svc.id.goog[my-namespace/my-ksa]"

# Annotate the Kubernetes ServiceAccount
kubectl annotate serviceaccount my-ksa \
  --namespace my-namespace \
  iam.gke.io/gcp-service-account=my-app-sa@my-project-id.iam.gserviceaccount.com
```

**Binary Authorization** enforces deploy-time policy by requiring container images to be signed by trusted authorities before they can run on the cluster.

**GKE Ingress** uses Google Cloud Load Balancers. Annotating an Ingress resource with `kubernetes.io/ingress.class: gce` provisions an external HTTP(S) load balancer. The `gce-internal` class provisions an internal load balancer. GKE also supports the Gateway API natively.

### Networking

**VPC-native clusters** (enabled with `--enable-ip-alias`) assign Pod and Service IP ranges from the VPC's secondary CIDR ranges. This makes Pods directly routable within the VPC and is required for features like Private Google Access, VPC peering, and shared VPC.

```bash
# Create a private cluster (nodes have no public IPs)
gcloud container clusters create private-cluster \
  --region us-central1 \
  --enable-ip-alias \
  --enable-private-nodes \
  --enable-private-endpoint \
  --master-ipv4-cidr 172.16.0.0/28 \
  --network my-vpc \
  --subnetwork my-subnet
```

Private clusters restrict the control plane endpoint to internal IPs. Use `--enable-private-endpoint` for full isolation or omit it to keep a public endpoint with authorized networks controlling access.

## Amazon Elastic Kubernetes Service (EKS)

EKS is AWS's managed Kubernetes service. AWS manages the control plane (API server, etcd) across multiple availability zones. Worker node management is your responsibility unless you use managed node groups or Fargate.

### Cluster Creation

The `eksctl` tool provides a higher-level CLI than raw `aws` commands.

```bash
# Create a cluster with eksctl (creates VPC, subnets, node group)
eksctl create cluster \
  --name my-cluster \
  --region us-east-1 \
  --version 1.29 \
  --nodegroup-name standard-workers \
  --node-type m5.xlarge \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 10 \
  --managed

# Or with the AWS CLI (control plane only, no nodes)
aws eks create-cluster \
  --name my-cluster \
  --region us-east-1 \
  --kubernetes-version 1.29 \
  --role-arn arn:aws:iam::111122223333:role/eks-cluster-role \
  --resources-vpc-config subnetIds=subnet-aaa,subnet-bbb,securityGroupIds=sg-xxx

# Wait for cluster to become active
aws eks wait cluster-active --name my-cluster --region us-east-1

# Update kubeconfig
aws eks update-kubeconfig --name my-cluster --region us-east-1
```

### Compute Options: Managed Node Groups vs Self-Managed vs Fargate

**Managed node groups** are the standard approach. AWS provisions EC2 instances, handles AMI updates, and integrates with the cluster autoscaler. Nodes appear as regular EC2 instances in your account.

**Self-managed node groups** give you complete control over the EC2 launch template, AMI, and bootstrap process. Use these for specialized needs like custom AMIs or specific instance store configurations.

**Fargate** runs each Pod on its own isolated micro-VM with no shared compute. You define Fargate profiles that match Pods by namespace and labels. Fargate eliminates node management entirely but has restrictions: no DaemonSets, no privileged containers, no GPUs, and no persistent volumes backed by EBS.

```bash
# Add a managed node group
eksctl create nodegroup \
  --cluster my-cluster \
  --name gpu-workers \
  --node-type p3.2xlarge \
  --nodes 1 \
  --nodes-min 0 \
  --nodes-max 4 \
  --managed

# Create a Fargate profile
eksctl create fargateprofile \
  --cluster my-cluster \
  --name my-fargate-profile \
  --namespace my-fargate-ns \
  --labels app=batch-processor

# Or with AWS CLI
aws eks create-fargate-profile \
  --cluster-name my-cluster \
  --fargate-profile-name my-fargate-profile \
  --pod-execution-role-arn arn:aws:iam::111122223333:role/fargate-role \
  --selectors namespace=my-fargate-ns,labels={app=batch-processor} \
  --subnets subnet-aaa subnet-bbb
```

### IAM Roles for Service Accounts (IRSA)

IRSA lets Kubernetes Pods assume IAM roles without embedding credentials. It works through an OIDC identity provider associated with the cluster.

```bash
# Associate an OIDC provider with the cluster
eksctl utils associate-iam-oidc-provider \
  --cluster my-cluster \
  --approve

# Create an IAM role and Kubernetes ServiceAccount together
eksctl create iamserviceaccount \
  --cluster my-cluster \
  --name my-app-sa \
  --namespace default \
  --attach-policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess \
  --approve
```

The resulting ServiceAccount is annotated with the IAM role ARN. Pods using this ServiceAccount receive temporary credentials via a projected token volume, which the AWS SDK picks up automatically.

### EKS Add-ons

EKS add-ons are AWS-managed components installed on the cluster. Core add-ons include:

```bash
# List available add-ons
aws eks describe-addon-versions --kubernetes-version 1.29 \
  --query 'addons[].addonName' --output text

# Install the EBS CSI driver add-on
aws eks create-addon \
  --cluster-name my-cluster \
  --addon-name aws-ebs-csi-driver \
  --service-account-role-arn arn:aws:iam::111122223333:role/ebs-csi-role

# Update an add-on
aws eks update-addon \
  --cluster-name my-cluster \
  --addon-name vpc-cni \
  --resolve-conflicts OVERWRITE
```

- **VPC CNI** (`vpc-cni`): Assigns real VPC IP addresses to Pods, making them first-class citizens in the VPC network. Each Pod gets an ENI-attached IP from the subnet CIDR.
- **CoreDNS** (`coredns`): Cluster DNS resolution.
- **kube-proxy** (`kube-proxy`): Maintains network rules on nodes for Service routing.
- **EBS CSI Driver** (`aws-ebs-csi-driver`): Provisions EBS volumes as PersistentVolumes. Required for dynamic provisioning with the `gp3` or `io2` StorageClasses.

### AWS Load Balancer Controller

The AWS Load Balancer Controller (replacing the older ALB Ingress Controller) provisions ALBs for Ingress resources and NLBs for LoadBalancer-type Services.

```bash
# Install via Helm
helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=my-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller
```

Ingress resources annotated with `alb.ingress.kubernetes.io/scheme: internet-facing` get an internet-facing ALB. The controller also supports target group binding, WAF integration, and the Gateway API.

### Networking

EKS clusters require a VPC with subnets across at least two availability zones. Public subnets host load balancers; private subnets host worker nodes.

```bash
# eksctl generates a dedicated VPC by default, or use an existing one:
eksctl create cluster \
  --name my-cluster \
  --vpc-private-subnets subnet-aaa,subnet-bbb \
  --vpc-public-subnets subnet-ccc,subnet-ddd

# Restrict public API access
aws eks update-cluster-config \
  --name my-cluster \
  --resources-vpc-config endpointPublicAccess=true,publicAccessCidrs="203.0.113.0/24",endpointPrivateAccess=true
```

Subnet tagging is critical. Public subnets must have `kubernetes.io/role/elb=1` and private subnets must have `kubernetes.io/role/internal-elb=1` for the load balancer controller to discover them.

## Azure Kubernetes Service (AKS)

AKS is Azure's managed Kubernetes offering. The control plane is fully managed and free of charge; you pay only for worker node VMs. AKS integrates deeply with Azure Active Directory (Entra ID), Azure Monitor, and Azure networking.

### Cluster Creation

```bash
# Create a resource group
az group create --name my-rg --location eastus

# Create an AKS cluster
az aks create \
  --resource-group my-rg \
  --name my-cluster \
  --node-count 3 \
  --node-vm-size Standard_D4s_v5 \
  --enable-managed-identity \
  --network-plugin azure \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group my-rg --name my-cluster

# Create a cluster with autoscaling
az aks create \
  --resource-group my-rg \
  --name autoscale-cluster \
  --node-count 2 \
  --min-count 1 \
  --max-count 10 \
  --enable-cluster-autoscaler \
  --node-vm-size Standard_D4s_v5 \
  --enable-managed-identity \
  --generate-ssh-keys
```

### Node Pools

AKS supports multiple node pools with different VM sizes, OS types (Linux and Windows), and scaling configurations.

```bash
# Add a node pool
az aks nodepool add \
  --resource-group my-rg \
  --cluster-name my-cluster \
  --name gpupool \
  --node-count 1 \
  --node-vm-size Standard_NC6s_v3 \
  --min-count 0 \
  --max-count 4 \
  --enable-cluster-autoscaler

# Add a spot instance node pool
az aks nodepool add \
  --resource-group my-rg \
  --cluster-name my-cluster \
  --name spotpool \
  --priority Spot \
  --eviction-policy Delete \
  --spot-max-price -1 \
  --node-count 1 \
  --min-count 0 \
  --max-count 20 \
  --enable-cluster-autoscaler

# Virtual nodes (Azure Container Instances backend, serverless)
az aks enable-addons \
  --resource-group my-rg \
  --name my-cluster \
  --addons virtual-node \
  --subnet-name virtual-node-subnet
```

**Virtual nodes** use Azure Container Instances (ACI) to run Pods without dedicated VMs, similar to Fargate on EKS. They are suitable for burst workloads but have limitations around persistent storage and DaemonSets.

### Azure AD Integration and Managed Identity

AKS supports Azure AD (Entra ID) for cluster authentication, enabling RBAC tied to Azure AD users and groups.

```bash
# Enable Azure AD integration with Azure RBAC
az aks create \
  --resource-group my-rg \
  --name aad-cluster \
  --enable-aad \
  --enable-azure-rbac \
  --aad-admin-group-object-ids <group-object-id> \
  --enable-managed-identity \
  --generate-ssh-keys

# Assign Azure Kubernetes Service RBAC roles
az role assignment create \
  --assignee <user-or-group-id> \
  --role "Azure Kubernetes Service RBAC Writer" \
  --scope /subscriptions/<sub>/resourceGroups/my-rg/providers/Microsoft.ContainerService/managedClusters/aad-cluster
```

**Managed identity** replaces service principal credentials. The cluster's managed identity is used to manage Azure resources (load balancers, disks, public IPs) on behalf of the cluster. Workload Identity (Azure AD federated credentials) extends this to Pods, similar in concept to GKE Workload Identity and EKS IRSA.

### AKS-Specific Features

**Azure CNI** assigns VNet IP addresses directly to Pods (similar to AWS VPC CNI). Every Pod gets an IP from the subnet, making them routable within the VNet. The alternative, `kubenet`, uses a bridge with NAT and is simpler but less integrated.

```bash
# Azure CNI Overlay (more IP-efficient than traditional Azure CNI)
az aks create \
  --resource-group my-rg \
  --name overlay-cluster \
  --network-plugin azure \
  --network-plugin-mode overlay \
  --pod-cidr 192.168.0.0/16 \
  --enable-managed-identity \
  --generate-ssh-keys
```

**Azure Disk and Azure Files CSI drivers** are installed by default on AKS. Azure Disk provides block storage (ReadWriteOnce) backed by managed disks. Azure Files provides SMB/NFS shares (ReadWriteMany) for workloads needing shared file access.

```bash
# Verify CSI drivers are running
kubectl get pods -n kube-system -l app=csi-azuredisk-node
kubectl get pods -n kube-system -l app=csi-azurefile-node
```

### Application Gateway Ingress Controller (AGIC)

AGIC uses Azure Application Gateway (a Layer 7 load balancer with WAF capabilities) as the Ingress controller for AKS.

```bash
# Enable AGIC as an AKS add-on
az aks enable-addons \
  --resource-group my-rg \
  --name my-cluster \
  --addons ingress-appgw \
  --appgw-subnet-cidr "10.225.0.0/16" \
  --appgw-name my-appgw

# Alternatively, use an existing Application Gateway
az aks enable-addons \
  --resource-group my-rg \
  --name my-cluster \
  --addons ingress-appgw \
  --appgw-id /subscriptions/<sub>/resourceGroups/my-rg/providers/Microsoft.Network/applicationGateways/my-existing-appgw
```

Ingress resources annotated with `kubernetes.io/ingress.class: azure/application-gateway` are served by the Application Gateway. AGIC supports SSL termination, URL path-based routing, multi-site hosting, and Web Application Firewall (WAF) policies.

## Comparison: GKE vs EKS vs AKS

| Feature | GKE | EKS | AKS |
|---|---|---|---|
| **Control plane cost** | $0.10/hr (Standard); per-Pod (Autopilot) | $0.10/hr per cluster | Free |
| **Default CNI** | GKE VPC-native (Dataplane V2/Cilium) | AWS VPC CNI | Azure CNI or kubenet |
| **Serverless Pods** | Autopilot | Fargate | Virtual Nodes (ACI) |
| **Managed node updates** | Auto-upgrade with release channels | Managed node group AMI updates | Auto-upgrade with planned maintenance |
| **Max nodes per cluster** | 15,000 | 450 managed node groups (up to thousands of nodes) | 5,000 |
| **Identity to workloads** | Workload Identity | IRSA / Pod Identity | Workload Identity (Azure AD federated) |
| **SLA** | 99.95% (regional) / 99.5% (zonal) | 99.95% | 99.95% (with SLA tier) / 99.5% (free tier) |
| **Built-in Ingress** | GKE Ingress (GCLB) | AWS LB Controller (ALB/NLB) | AGIC (App Gateway) |
| **Service mesh** | Anthos Service Mesh (Istio-based) | AWS App Mesh / EKS add-on for Istio | Open Service Mesh / Istio add-on |
| **Logging and monitoring** | Cloud Logging, Cloud Monitoring | CloudWatch Container Insights | Azure Monitor Container Insights |
| **GPU support** | NVIDIA T4, V100, A100, H100 | P3, P4, G5, Inf1 (Inferentia) | NC, ND, NV series |

## Multi-Cloud Considerations

Running Kubernetes across multiple cloud providers introduces architectural challenges that extend well beyond cluster creation.

**Cluster federation and GitOps.** No provider's managed Kubernetes integrates natively with another. Use a GitOps tool like Flux or Argo CD to maintain consistent workload definitions across clusters. Store manifests in a single repository with per-cluster overlays (Kustomize) or value files (Helm).

**Networking.** Pod CIDR ranges must not overlap if you intend to connect clusters. Each provider uses a different CNI model: GKE and EKS assign VPC-routable IPs to Pods by default, while AKS does so with Azure CNI but not with kubenet. Cross-cloud connectivity typically requires a service mesh (Istio with multi-cluster configuration) or a dedicated connectivity layer like Submariner. Alternatively, expose services at the edge with provider-neutral Ingress (e.g., NGINX Ingress Controller) and use DNS-based failover via external-dns and weighted records.

**Identity and secrets.** Each provider has its own IAM model. Avoid embedding cloud-specific annotations in application manifests. Instead, use external-secrets-operator or a Vault instance to centralize secret management and abstract provider-specific identity bindings behind a consistent interface.

**Storage.** PersistentVolume implementations are provider-specific and not portable. For stateful workloads that must run across clouds, consider application-level replication (database clustering, object storage) rather than trying to replicate block volumes. CSI drivers differ in capability: snapshot support, volume expansion, and access modes vary.

**Cost management.** Pricing models differ significantly. GKE Autopilot charges per Pod resource, EKS charges a flat cluster fee plus EC2 or Fargate costs, and AKS has no control plane fee. Normalize cost comparisons by total cost of ownership, including egress, load balancer hours, persistent disk, and operational overhead.

**Portability strategy.** True multi-cloud portability requires discipline: use namespace-scoped resources, avoid provider-specific annotations in core manifests (push them to overlays), rely on the Kubernetes API rather than provider extensions where possible, and run the same Ingress controller (e.g., NGINX, Envoy Gateway) across all clusters. Accept that some integration points (IAM, storage, load balancing) will always have provider-specific configuration, and isolate that configuration into clearly bounded layers.
