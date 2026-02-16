# Chapter 3: Installing Your First Kubernetes Cluster

This chapter covers the practical steps for getting a working Kubernetes cluster running, from lightweight local development environments to production-grade installations with kubeadm. It also covers kubectl installation, kubeconfig management, and verifying cluster health.

## Minikube

Minikube runs a single- or multi-node Kubernetes cluster inside a VM or container on your local machine. It is the most common choice for local development and learning.

### Installation

```bash
# macOS (Homebrew)
brew install minikube

# Linux (x86-64 binary)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Windows (Chocolatey)
choco install minikube
```

Verify the installation:

```bash
minikube version
```

### Drivers

Minikube abstracts the runtime environment through drivers. The driver determines how the cluster node is provisioned.

| Driver | Platform | Notes |
|--------|----------|-------|
| `docker` | All | Default on most systems. Runs nodes as containers. Fastest startup. |
| `hyperkit` | macOS | Lightweight hypervisor. Deprecated in favor of docker driver on Apple Silicon. |
| `kvm2` | Linux | Uses KVM. Good isolation but requires hardware virtualization support. |
| `virtualbox` | All | Cross-platform VM driver. Slower but widely compatible. |
| `qemu` | macOS/Linux | Required for Apple Silicon Macs when a VM-based driver is needed. |
| `none` | Linux | Runs Kubernetes directly on the host. Requires root. Used in CI. |
| `podman` | All | Rootless container alternative to Docker. |

Set a default driver so you do not have to specify it each time:

```bash
minikube config set driver docker
```

### Profiles

Profiles let you run multiple independent clusters simultaneously, each with its own configuration and Kubernetes version.

```bash
# Start a cluster with a named profile
minikube start --profile dev-cluster --kubernetes-version=v1.29.2

# Start another cluster with a different version
minikube start --profile staging --kubernetes-version=v1.28.5

# List all profiles
minikube profile list

# Switch the active profile (sets the kubectl context)
minikube profile dev-cluster

# Delete a specific profile
minikube delete --profile staging

# Delete all profiles
minikube delete --all
```

Each profile creates its own kubeconfig context named `minikube-<profile>` (or just `minikube` for the default profile).

### Addons

Minikube ships with a catalog of built-in addons that install common cluster components.

```bash
# List all available addons and their status
minikube addons list

# Enable an addon
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable dashboard

# Disable an addon
minikube addons disable dashboard

# Open the dashboard in a browser (requires the dashboard addon)
minikube dashboard
```

Commonly used addons: `ingress`, `ingress-dns`, `metrics-server`, `dashboard`, `storage-provisioner`, `registry`, `metallb`.

### Multi-Node Clusters

Minikube supports multi-node clusters for testing scheduling, affinity, and node failure scenarios.

```bash
# Start a 3-node cluster
minikube start --nodes 3

# Check node status
kubectl get nodes

# Add a node to a running cluster
minikube node add

# Delete a specific node
minikube node delete minikube-m03

# Stop and restart a node (simulating failure)
minikube node stop minikube-m02
minikube node start minikube-m02
```

The first node is always the control plane. Additional nodes join as workers.

### Useful Minikube Commands

```bash
# SSH into the minikube node
minikube ssh

# Get the IP address of the cluster
minikube ip

# Access a NodePort service via minikube tunnel or service URL
minikube service <service-name> --url

# Create a tunnel for LoadBalancer services
minikube tunnel

# Mount a host directory into the node
minikube mount /host/path:/vm/path
```

## kind (Kubernetes in Docker)

kind runs Kubernetes clusters using Docker containers as nodes. It was originally built for testing Kubernetes itself and is popular in CI/CD pipelines due to its speed and reproducibility.

### Installation

```bash
# macOS / Linux (Homebrew)
brew install kind

# From release binary
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Go install
go install sigs.k8s.io/kind@latest
```

### Cluster Configuration

kind uses a YAML configuration file to define cluster topology and settings.

```yaml
# kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
networking:
  apiServerAddress: "127.0.0.1"
  apiServerPort: 6443
  podSubnet: "10.244.0.0/16"
  serviceSubnet: "10.96.0.0/12"
nodes:
  - role: control-plane
    kubeadmConfigPatches:
      - |
        kind: InitConfiguration
        nodeRegistration:
          kubeletExtraArgs:
            node-labels: "ingress-ready=true"
    extraPortMappings:
      - containerPort: 80
        hostPort: 80
        protocol: TCP
      - containerPort: 443
        hostPort: 443
        protocol: TCP
  - role: worker
  - role: worker
```

```bash
# Create a cluster from a config file
kind create cluster --name my-cluster --config kind-config.yaml

# Create a cluster with a specific Kubernetes version
kind create cluster --image kindest/node:v1.29.2

# List clusters
kind get clusters

# Delete a cluster
kind delete cluster --name my-cluster
```

### Multi-Node with kind

Define multiple node entries in the configuration file (shown above). For high-availability testing, specify multiple control-plane nodes:

```yaml
nodes:
  - role: control-plane
  - role: control-plane
  - role: control-plane
  - role: worker
  - role: worker
```

kind automatically configures a load balancer in front of multiple control-plane nodes.

### Loading Images into kind

Since kind nodes are containers, they have their own image store. You must explicitly load locally built images:

```bash
# Load a local image into the cluster
kind load docker-image my-app:latest --name my-cluster

# Alternatively, load from an archive
kind load image-archive my-app.tar --name my-cluster
```

### Ingress with kind

To use an ingress controller with kind, the control-plane node needs `extraPortMappings` (as shown in the config above) and the `ingress-ready` label. Then deploy an ingress controller:

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
```

## k3s and k3d

### k3s

k3s is a lightweight, certified Kubernetes distribution from Rancher/SUSE. It ships as a single binary under 100 MB and is suitable for edge, IoT, and resource-constrained environments. It replaces etcd with SQLite by default and bundles components like containerd, Flannel, CoreDNS, and Traefik.

```bash
# Install k3s (runs as a service)
curl -sfL https://get.k3s.io | sh -

# Check status
sudo systemctl status k3s

# The kubeconfig is written to /etc/rancher/k3s/k3s.yaml
sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml get nodes

# Copy kubeconfig for non-root use
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config

# Join a worker node (run on the worker, using the server's node-token)
curl -sfL https://get.k3s.io | K3S_URL=https://<server-ip>:6443 \
  K3S_TOKEN=$(sudo cat /var/lib/rancher/k3s/server/node-token) sh -

# Uninstall
/usr/local/bin/k3s-uninstall.sh        # server
/usr/local/bin/k3s-agent-uninstall.sh   # agent
```

### k3d

k3d is a wrapper that runs k3s clusters inside Docker containers, combining the lightweight nature of k3s with the convenience of containerized nodes.

```bash
# Install k3d
brew install k3d
# or
curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash

# Create a cluster with 2 worker nodes
k3d cluster create dev --agents 2

# Create a cluster with port mappings for ingress
k3d cluster create dev -p "8080:80@loadbalancer" -p "8443:443@loadbalancer"

# Import a local image
k3d image import my-app:latest -c dev

# List clusters
k3d cluster list

# Stop / start a cluster without deleting it
k3d cluster stop dev
k3d cluster start dev

# Delete
k3d cluster delete dev
```

## Docker Desktop Kubernetes

Docker Desktop includes a built-in single-node Kubernetes cluster on macOS and Windows.

To enable it: open Docker Desktop Settings, navigate to the Kubernetes section, check "Enable Kubernetes", and click "Apply & Restart". Docker Desktop installs the cluster components and configures a `docker-desktop` context in your kubeconfig automatically.

```bash
# Verify the cluster is running
kubectl config use-context docker-desktop
kubectl get nodes

# Reset the Kubernetes cluster (from Docker Desktop Settings > Kubernetes > Reset)
```

Advantages: zero additional installation, shared Docker daemon (images built with `docker build` are immediately available to the cluster), integrated with Docker Desktop networking.

Limitations: single-node only, limited configuration options, Kubernetes version tied to the Docker Desktop release, resource usage shared with Docker engine.

## kubeadm

kubeadm is the official tool for bootstrapping production-grade Kubernetes clusters. It handles cluster initialization, node joining, certificate generation, and upgrades. It does not provision infrastructure or install a CNI plugin; those are your responsibility.

### Prerequisites

All nodes need: a container runtime (containerd is standard), `kubelet`, `kubeadm`, and `kubectl`. Swap must be disabled. Required ports must be open (6443 for the API server, 10250 for kubelet, 2379-2380 for etcd).

```bash
# Disable swap
sudo swapoff -a
# Remove swap entries from /etc/fstab to persist across reboots

# Install containerd, kubelet, kubeadm, kubectl
# (Follow the official docs for your distribution to add the Kubernetes apt/yum repository)

# Enable and start kubelet
sudo systemctl enable --now kubelet
```

### Cluster Initialization

Run on the designated control-plane node:

```bash
# Initialize the control plane
sudo kubeadm init \
  --pod-network-cidr=10.244.0.0/16 \
  --control-plane-endpoint=<load-balancer-ip-or-dns>:6443 \
  --upload-certs

# Set up kubeconfig for the current user
mkdir -p $HOME/.kube
sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Install a CNI plugin (example: Calico)
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.27.0/manifests/calico.yaml
```

The `--pod-network-cidr` must match what the CNI plugin expects (Flannel uses `10.244.0.0/16`, Calico defaults to `192.168.0.0/16` but can be configured).

### Joining Nodes

`kubeadm init` outputs a join command. Run it on each worker node:

```bash
# Join a worker node (command provided by kubeadm init output)
sudo kubeadm join <control-plane-ip>:6443 \
  --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash>

# If the token has expired, generate a new one on the control plane
sudo kubeadm token create --print-join-command
```

### High Availability (HA) Control Plane

An HA setup requires at minimum three control-plane nodes and an external load balancer in front of the API servers.

```bash
# Initialize the first control-plane node with --upload-certs
sudo kubeadm init \
  --control-plane-endpoint=<load-balancer>:6443 \
  --upload-certs \
  --pod-network-cidr=10.244.0.0/16

# Join additional control-plane nodes (add --control-plane and --certificate-key flags)
sudo kubeadm join <load-balancer>:6443 \
  --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash> \
  --control-plane \
  --certificate-key <key>
```

The load balancer (HAProxy, Nginx, or a cloud LB) distributes traffic across all API server instances. etcd runs in a stacked topology by default (co-located with each control-plane node). For external etcd, provide an `--config` file specifying the etcd endpoints.

## kubectl Installation

kubectl is the primary CLI for interacting with any Kubernetes cluster.

```bash
# macOS
brew install kubectl

# Linux (official binary)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl

# Windows (Chocolatey)
choco install kubernetes-cli

# Verify
kubectl version --client
```

Enable shell completions for productivity:

```bash
# Bash
echo 'source <(kubectl completion bash)' >> ~/.bashrc
echo 'alias k=kubectl' >> ~/.bashrc
echo 'complete -o default -F __start_kubectl k' >> ~/.bashrc

# Zsh
echo 'source <(kubectl completion zsh)' >> ~/.zshrc
echo 'alias k=kubectl' >> ~/.zshrc
```

## Kubeconfig Structure

The kubeconfig file (default location `~/.kube/config`) tells kubectl how to find and authenticate to clusters. It consists of three primary sections.

### Clusters

Each entry defines an API server endpoint and its certificate authority.

```yaml
clusters:
  - name: production
    cluster:
      server: https://api.prod.example.com:6443
      certificate-authority-data: <base64-encoded-ca-cert>
  - name: minikube
    cluster:
      server: https://192.168.49.2:8443
      certificate-authority: /home/user/.minikube/ca.crt
```

### Users

Each entry defines credentials for authenticating to a cluster. Credentials can be client certificates, bearer tokens, exec-based plugins (for OIDC, cloud IAM), or auth provider configurations.

```yaml
users:
  - name: prod-admin
    user:
      client-certificate-data: <base64>
      client-key-data: <base64>
  - name: dev-user
    user:
      exec:
        apiVersion: client.authentication.k8s.io/v1beta1
        command: aws
        args:
          - eks
          - get-token
          - --cluster-name
          - my-eks-cluster
```

### Contexts

A context binds a cluster, a user, and optionally a default namespace into a named reference. You switch between contexts to target different clusters or roles.

```yaml
contexts:
  - name: prod-context
    context:
      cluster: production
      user: prod-admin
      namespace: default
  - name: dev-context
    context:
      cluster: minikube
      user: minikube-user
      namespace: development
current-context: dev-context
```

### Merging Multiple Kubeconfig Files

The `KUBECONFIG` environment variable accepts a colon-separated list of files. kubectl merges them at runtime:

```bash
export KUBECONFIG=~/.kube/config:~/.kube/eks-config:~/.kube/gke-config
```

To flatten merged configs into a single file:

```bash
KUBECONFIG=~/.kube/config:~/.kube/other kubectl config view --flatten > ~/.kube/merged-config
```

## Context Management

```bash
# List all contexts
kubectl config get-contexts

# Show the current context
kubectl config current-context

# Switch to a different context
kubectl config use-context prod-context

# Set a default namespace for a context
kubectl config set-context --current --namespace=my-namespace

# Create a new context manually
kubectl config set-context staging \
  --cluster=staging-cluster \
  --user=staging-admin \
  --namespace=staging

# Rename a context
kubectl config rename-context old-name new-name

# Delete a context
kubectl config delete-context staging

# Override context for a single command without switching
kubectl --context=prod-context get pods
```

For managing many contexts, consider tools like `kubectx` and `kubens`:

```bash
# Install
brew install kubectx

# Switch context interactively
kubectx

# Switch namespace interactively
kubens
```

## Verifying Cluster Health

After setting up any cluster, run through these checks to confirm it is functioning correctly.

```bash
# Check that all nodes are Ready
kubectl get nodes -o wide

# Verify system pods are running
kubectl get pods -n kube-system

# Check component status (API server, scheduler, controller-manager)
kubectl cluster-info

# Run a quick smoke test: deploy, expose, and test
kubectl create deployment nginx-test --image=nginx:latest
kubectl expose deployment nginx-test --port=80 --type=NodePort
kubectl get svc nginx-test

# Verify DNS resolution inside the cluster
kubectl run dns-test --image=busybox:1.36 --rm -it --restart=Never -- \
  nslookup kubernetes.default.svc.cluster.local

# Check that the metrics API is available (requires metrics-server)
kubectl top nodes
kubectl top pods -A

# Clean up smoke test resources
kubectl delete deployment nginx-test
kubectl delete svc nginx-test
```

For deeper diagnostics:

```bash
# Check etcd health (kubeadm clusters)
sudo ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  endpoint health

# Inspect kubelet logs on a node
journalctl -u kubelet -f

# Check API server audit logs (if configured)
# Location depends on audit policy configuration
```

## Common Post-Setup Add-ons

Most clusters need additional components beyond the base installation. These are the most commonly deployed add-ons.

**CNI Plugin** (required for kubeadm clusters): Provides pod networking. Choose one: Calico (network policy support, BGP), Flannel (simple overlay), Cilium (eBPF-based, advanced observability), Weave Net.

**Ingress Controller**: Routes external HTTP/HTTPS traffic to services. Popular choices are ingress-nginx (community maintained), Traefik (bundled with k3s), and HAProxy Ingress.

**Metrics Server**: Collects resource metrics from kubelets and exposes them through the Metrics API. Required for `kubectl top` and Horizontal Pod Autoscaler.

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

**Dashboard**: Web-based UI for cluster management and troubleshooting.

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
```

**cert-manager**: Automates TLS certificate issuance and renewal from sources like Let's Encrypt.

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml
```

**Storage Provisioner**: Provides dynamic persistent volume provisioning. Local development tools (minikube, kind, k3s) include a default provisioner. Production clusters use CSI drivers specific to the storage backend (AWS EBS, GCP PD, NFS, Ceph).

**CoreDNS**: Cluster DNS server. Installed by default in all standard distributions. Rarely needs manual installation but may need tuning for large clusters (adjusting cache size, adding forward zones).

**Kube-state-metrics and Prometheus**: For production observability. kube-state-metrics exposes cluster state as Prometheus metrics. Often deployed together via the kube-prometheus-stack Helm chart.

## Choosing a Local Cluster Tool

| Tool | Best For | Multi-Node | Speed | Resource Use |
|------|----------|------------|-------|--------------|
| minikube | Learning, general development | Yes | Medium | Medium-High |
| kind | CI/CD, testing, multi-node experiments | Yes (including HA) | Fast | Low-Medium |
| k3d | Lightweight local clusters, fast iteration | Yes | Fast | Low |
| Docker Desktop | macOS/Windows developers wanting zero setup | No | Medium | Medium |

For production or staging environments, use kubeadm, a managed service (EKS, GKE, AKS), or an installer like Kubespray or Cluster API.
