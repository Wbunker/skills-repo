# AWS EKS — Capabilities Reference
For CLI commands, see [eks-cli.md](eks-cli.md).

## Amazon EKS

**Purpose**: Fully managed Kubernetes service; run Kubernetes on AWS without managing the control plane.

### Key Concepts

| Concept | Description |
|---|---|
| **Control plane** | AWS managed; etcd + API server + scheduler + controller manager; runs in AWS-managed accounts; HA by default across multiple AZs |
| **Data plane** | Your EC2 nodes or Fargate where pods actually run |
| **EKS Standard** | You manage node groups; AWS manages control plane |
| **EKS Auto Mode** | AWS manages both control plane and data plane (node provisioning, scaling, patching, cost optimization) |
| **kubeconfig** | Update with `aws eks update-kubeconfig` to authenticate kubectl to the cluster |

### Node Types

| Type | Description |
|---|---|
| **Managed node groups** | EC2 Auto Scaling groups managed by EKS; automated drain, update, and health checks; support On-Demand and Spot capacity types; multiple AMI types (Amazon Linux 2, Bottlerocket, Windows) |
| **Self-managed nodes** | EC2 instances you register manually; full control; you manage updates and draining |
| **Fargate profiles** | Serverless pods; no nodes to manage; each pod runs in an isolated VM; selector matches namespace + labels |

### Networking

| Component | Description |
|---|---|
| **Amazon VPC CNI** | Default CNI plugin; each pod gets a real VPC IP address from the node's ENI; enables native VPC routing and security groups for pods |
| **Security groups for pods** | Assign EC2 security groups directly to specific pods (via `SecurityGroupPolicy` CRD); requires VPC CNI with `ENABLE_POD_ENI=true` |
| **Cluster endpoint** | API server endpoint; can be public (default), private (within VPC only), or both |
| **CoreDNS** | Cluster DNS; add-on managed by EKS |

### EKS Add-ons

| Add-on | Description |
|---|---|
| **Amazon VPC CNI** | Pod networking; installed by default |
| **kube-proxy** | Service networking; installed by default |
| **CoreDNS** | Cluster DNS; installed by default |
| **Amazon EBS CSI Driver** | Persistent volumes backed by EBS |
| **Amazon EFS CSI Driver** | Shared persistent volumes backed by EFS |
| **EKS Pod Identity Agent** | DaemonSet that provides credentials to pods; required for Pod Identity feature |
| **AWS Load Balancer Controller** | Manages ALB/NLB for Ingress and Service resources |
| **Amazon GuardDuty Agent** | Runtime threat detection for EKS workloads |
| **ADOT (AWS Distro for OpenTelemetry)** | Metrics and traces to CloudWatch and X-Ray |
| **Metrics Server** | Horizontal Pod Autoscaler data source |
| **Karpenter** | High-performance node autoscaler; provisions right-sized nodes on demand |

EKS manages add-on versioning, security patches, and compatibility. You can override configuration fields not managed by EKS without those fields being reverted.

### IAM for Pods: IRSA vs EKS Pod Identity

| Feature | IRSA (IAM Roles for Service Accounts) | EKS Pod Identity |
|---|---|---|
| **Mechanism** | OIDC federation; each cluster has its own OIDC provider | Agent-based; EKS Pod Identity Agent DaemonSet runs on nodes |
| **IAM trust policy principal** | OIDC provider ARN with namespace/service-account conditions | `pods.eks.amazonaws.com` service principal (same for all clusters) |
| **Role reuse across clusters** | No — separate trust policy entry per cluster | Yes — one role, associate to multiple clusters |
| **OIDC provider setup** | Required per cluster | Not required |
| **Fargate support** | Yes | No |
| **Windows nodes** | Yes | No |
| **Complexity** | Higher | Lower |
| **Recommendation** | Legacy / Fargate | Preferred for new EC2-based workloads |

### Cluster Authentication and Access

| Mechanism | Description |
|---|---|
| **aws-auth ConfigMap** | Legacy; maps IAM users/roles to Kubernetes RBAC users/groups; high blast radius if misconfigured |
| **EKS Access Entries** | Newer API-managed approach; create access entries for IAM principals; associate access policies (EKS managed or custom Kubernetes RBAC) without editing aws-auth |
| **OIDC / SAML federation** | Integrate external IdPs for human user authentication |

Cluster endpoint access modes: `PUBLIC` (default), `PRIVATE` (in-VPC only), or `PUBLIC_AND_PRIVATE`.

### Cluster Upgrades

- AWS releases new Kubernetes minor versions; standard support 14 months, extended support available
- Upgrade control plane first via `update-cluster-version`, then upgrade add-ons, then upgrade node groups
- EKS validates compatibility before allowing the upgrade
- Managed node groups support in-place rolling updates with pod draining

### Autoscaling

| Scaler | Description |
|---|---|
| **Cluster Autoscaler** | Scales managed node groups based on pending pods; reads ASG tags |
| **Karpenter** | Provisions individual EC2 instances (not ASG-based); bin-packs pods; supports Spot interruption handling and consolidation |
| **Horizontal Pod Autoscaler (HPA)** | Scales pod replicas based on CPU/memory or custom metrics |
| **Vertical Pod Autoscaler (VPA)** | Adjusts pod resource requests/limits; recommends or auto-applies sizing |

### EKS Anywhere

Deploy EKS clusters on-premises on VMware vSphere, bare metal, AWS Snow, Nutanix, or Docker (dev only). Uses the same EKS Distro (etcd, Kubernetes components) as EKS in the cloud. Managed via `eksctl anywhere` or Cluster API. EKS Connector registers clusters with AWS console for visibility.

---

## Comparison Tables

### IRSA vs EKS Pod Identity

| Feature | IRSA | EKS Pod Identity |
|---|---|---|
| **Mechanism** | OIDC federation via IAM | Agent-based via `pods.eks.amazonaws.com` service |
| **Trust policy** | Unique per cluster (OIDC provider ARN) | Single principal, reusable across clusters |
| **OIDC provider** | Required — create one per cluster | Not required |
| **Fargate support** | Yes | No |
| **Windows nodes** | Yes | No |
| **Scalability** | Each pod assumes role independently | Agent caches credentials per node |
| **Setup complexity** | Higher (OIDC + trust policy per cluster) | Lower (association in EKS API) |
| **Prefer when** | Fargate, Windows nodes, EKS Anywhere | New EC2-based EKS workloads |
