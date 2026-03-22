# Containers — Reference Index

| Namespace | Capabilities | CLI | Load when... |
|---|---|---|---|
| AKS | [containers/aks-capabilities.md](containers/aks-capabilities.md) | [containers/aks-cli.md](containers/aks-cli.md) | Managed Kubernetes clusters, node pools, add-ons (KEDA, Dapr, Key Vault CSI, Workload Identity, monitoring), networking models, cluster upgrades, node auto-provisioner, Azure Container Storage |
| Azure Container Apps | [containers/container-apps-capabilities.md](containers/container-apps-capabilities.md) | [containers/container-apps-cli.md](containers/container-apps-cli.md) | Serverless containers, KEDA-based scaling (HTTP, CPU, event-driven), Dapr integration, environments, jobs, managed certificates, ingress, traffic splitting |
| Azure Container Registry | [containers/acr-capabilities.md](containers/acr-capabilities.md) | [containers/acr-cli.md](containers/acr-cli.md) | Image registry, geo-replication, ACR Tasks (automated build+test), content trust, vulnerability scanning (Defender), token-based repo-scoped access |
| Container Instances & Arc | [containers/aci-arc-capabilities.md](containers/aci-arc-capabilities.md) | [containers/aci-arc-cli.md](containers/aci-arc-cli.md) | Azure Container Instances (serverless containers, container groups), Azure Arc (K8s management, GitOps, extensions, Arc-enabled data services) |

> **Note:** Compute-oriented AKS capabilities (cluster creation, basic setup) are in `compute/aks-capabilities.md`. This domain index focuses on more advanced/operational container topics. Cross-reference as needed.
