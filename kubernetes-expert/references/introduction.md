# Kubernetes Fundamentals

Kubernetes exists because of a convergence of three industry shifts: the move from monolithic to microservice architectures, the move from virtual machines to containers, and the operational need to manage containers at scale. Understanding these shifts explains why Kubernetes was built and what problems it solves.

## Monoliths vs. Microservices

A monolithic application is a single deployable unit where all components -- user interface, business logic, data access -- are compiled and packaged together. A monolith runs as one process (or a small number of tightly coupled processes) and is typically deployed as a single artifact to a server or VM.

Monoliths have real advantages. Development is straightforward early on: one codebase, one build pipeline, one deployment. Debugging is simpler because all code shares the same process and memory space. Transactions that span multiple business domains are easy to implement because everything lives in the same database.

The problems surface as the application grows. A change to a single module requires redeploying the entire application. Teams working on different features contend with the same codebase, creating merge conflicts and coordination overhead. Scaling is coarse-grained: if the payment module needs more resources but the catalog module does not, you still scale the entire application. A memory leak or crash in one component brings down every component.

Microservices decompose the application into small, independently deployable services. Each service owns a single business capability, maintains its own data store, and communicates with other services over well-defined APIs (typically HTTP/REST or gRPC). Teams can develop, test, deploy, and scale each service independently.

The tradeoffs are significant. Microservices introduce distributed systems complexity: network latency, partial failures, eventual consistency, and the need for service discovery. Debugging a request that traverses ten services is harder than debugging one that stays in a single process. Operational overhead multiplies because each service needs its own build pipeline, monitoring, and deployment strategy. This operational overhead is precisely the problem Kubernetes was designed to address.

A typical microservices decomposition might look like:

```
[API Gateway] --> [User Service] --> [User DB]
              --> [Order Service] --> [Order DB]
              --> [Payment Service] --> [Payment DB]
              --> [Notification Service] --> [Message Queue]
              --> [Inventory Service] --> [Inventory DB]
```

Each service is a separate deployment unit with its own lifecycle. The question becomes: how do you deploy, connect, scale, and manage dozens or hundreds of these services? Containers provide the packaging mechanism; Kubernetes provides the orchestration.

## Virtual Machines vs. Containers

Virtual machines and containers both provide isolation, but they achieve it in fundamentally different ways.

A virtual machine runs a full guest operating system on top of a hypervisor. The hypervisor (Type 1 like ESXi or Hyper-V, or Type 2 like VirtualBox) emulates hardware and mediates access to the physical host. Each VM includes its own kernel, system libraries, and user-space binaries. A typical VM image is measured in gigabytes and takes seconds to minutes to boot.

```
+-------+ +-------+ +-------+
| App A | | App B | | App C |
| Bins  | | Bins  | | Bins  |
| Guest | | Guest | | Guest |
|  OS   | |  OS   | |  OS   |
+-------+ +-------+ +-------+
+-------------------------------+
|          Hypervisor           |
+-------------------------------+
|        Host OS / Hardware     |
+-------------------------------+
```

Containers share the host operating system's kernel. Isolation is provided by Linux kernel features: namespaces (for process, network, mount, user, and IPC isolation) and cgroups (for resource limits on CPU, memory, and I/O). A container packages only the application and its dependencies -- not an entire OS. Container images are measured in megabytes and start in milliseconds to seconds.

```
+-------+ +-------+ +-------+
| App A | | App B | | App C |
| Bins  | | Bins  | | Bins  |
+-------+ +-------+ +-------+
+-------------------------------+
|      Container Runtime        |
+-------------------------------+
|        Host OS / Kernel       |
+-------------------------------+
```

The practical consequences are substantial:

- **Density**: A host that runs 10-20 VMs can run hundreds of containers because containers do not carry the overhead of a full OS.
- **Startup time**: Containers start in under a second; VMs take tens of seconds to minutes.
- **Image size**: A minimal container image (Alpine-based) can be 5-10 MB; a VM image is typically 1-10 GB.
- **Portability**: A container image encapsulates everything above the kernel. If it runs on one Linux host, it runs on any Linux host with a compatible kernel.
- **Isolation**: VMs provide stronger isolation (separate kernels). Containers share a kernel, so a kernel vulnerability can affect all containers on the host. This distinction matters for multi-tenant environments.

VMs and containers are not mutually exclusive. A common production pattern runs containers inside VMs: the VM provides the strong isolation boundary, and containers provide lightweight application packaging within it. Kata Containers and Firecracker microVMs further blur the line by running each container in a lightweight VM.

## Docker and Container Basics

Docker popularized containers starting in 2013 by providing a simple developer experience around Linux container primitives. While Docker is not the only container runtime (containerd, CRI-O, and Podman are alternatives), it established the standards and workflows that Kubernetes builds upon.

The core Docker workflow involves three steps:

1. **Build**: Write a Dockerfile that specifies how to construct the image, then run `docker build` to produce an image.
2. **Ship**: Push the image to a container registry with `docker push`.
3. **Run**: Pull and run the image on any host with `docker run`.

A Dockerfile is a series of instructions that produce a filesystem layer at each step:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Key Docker commands in practice:

```bash
docker build -t myapp:1.0 .              # Build image from Dockerfile
docker run -d -p 8080:8000 myapp:1.0     # Run container, map port
docker ps                                 # List running containers
docker logs <container-id>                # View container stdout/stderr
docker exec -it <container-id> /bin/sh   # Shell into running container
docker stop <container-id>                # Graceful stop (SIGTERM then SIGKILL)
```

## Container Images, Layers, and Registries

A container image is an ordered collection of filesystem layers plus metadata (environment variables, entrypoint command, exposed ports, labels). Each instruction in a Dockerfile that modifies the filesystem (RUN, COPY, ADD) creates a new layer. Layers are content-addressable -- identified by the SHA256 hash of their contents -- and are immutable once created.

Layering enables two important optimizations:

- **Caching**: If a layer has not changed, Docker reuses it from cache during builds. This is why Dockerfiles typically copy dependency manifests (requirements.txt, package.json) before copying application source code -- dependency layers change less frequently and can be cached.
- **Sharing**: Multiple images that share the same base image (e.g., python:3.12-slim) store that base layer only once on disk. When pulling images, only layers not already present on the host are downloaded.

```
Image: myapp:1.0
  Layer 5: COPY . .                    (application code, ~2 MB)
  Layer 4: RUN pip install ...         (Python packages, ~50 MB)
  Layer 3: COPY requirements.txt .     (dependency manifest, ~1 KB)
  Layer 2: WORKDIR /app                (metadata only, 0 bytes)
  Layer 1: FROM python:3.12-slim       (base OS + Python, ~120 MB)
```

When a container runs, a thin writable layer is added on top of the read-only image layers using a union filesystem (overlay2 is the default storage driver). Writes go to this writable layer; the underlying image layers remain unchanged. This is why containers are ephemeral by default -- stopping and removing a container discards the writable layer.

A container registry is a server that stores and distributes container images. The registry protocol is standardized by the OCI Distribution Specification. Registries include:

- **Docker Hub**: The default public registry. Official images (nginx, postgres, python) live here.
- **Cloud provider registries**: Amazon ECR, Google Artifact Registry, Azure Container Registry. These offer integration with IAM, vulnerability scanning, and geographic replication.
- **Self-hosted registries**: Harbor, GitLab Container Registry, JFrog Artifactory. Used when images must stay within an organization's network.

Images are identified by a registry, repository, and tag: `registry.example.com/team/myapp:1.0`. Tags are mutable pointers -- pushing a new image with the same tag overwrites the previous one. For reproducibility, reference images by their immutable digest: `myapp@sha256:abc123...`.

## Problems Kubernetes Solves

Running a handful of containers with `docker run` works for development. Running hundreds of containers across dozens of hosts in production requires solving a set of hard problems. Kubernetes provides built-in solutions for each of these.

### Service Discovery and Load Balancing

In a microservices architecture, services need to find and communicate with each other. IP addresses are ephemeral -- containers start and stop, and their IPs change. Kubernetes assigns each Service a stable virtual IP (ClusterIP) and a DNS name (e.g., `order-service.production.svc.cluster.local`). Requests to that IP or DNS name are load-balanced across the healthy Pods backing the Service. No application-level service discovery library is needed.

### Load Balancing

Kubernetes distributes traffic across multiple instances of a service. Internal traffic is handled by kube-proxy (using iptables or IPVS rules). External traffic can be managed through Services of type LoadBalancer (which provision a cloud load balancer) or through Ingress resources (which provide HTTP-level routing, TLS termination, and path-based routing).

### Storage Orchestration

Containers are ephemeral, but many workloads need persistent data. Kubernetes abstracts storage through PersistentVolumes (PV) and PersistentVolumeClaims (PVC). A PVC declares what storage a workload needs (size, access mode, storage class); the cluster dynamically provisions or binds appropriate storage. The same Pod spec works whether the underlying storage is a local disk, an NFS share, an AWS EBS volume, or a GCP Persistent Disk.

### Automated Rollouts and Rollbacks

Updating a service from version 1.0 to 2.0 across 50 instances without downtime is complex. Kubernetes Deployments handle this natively. A rolling update incrementally replaces old Pods with new ones, respecting configurable parameters like `maxSurge` and `maxUnavailable`. If the new version fails health checks, the rollout automatically pauses. Rolling back to a previous version is a single command (`kubectl rollout undo`) because Kubernetes retains the history of previous ReplicaSets.

### Self-Healing

Kubernetes continuously monitors the actual state of the cluster against the desired state and takes corrective action:

- If a container process crashes, the kubelet restarts it (subject to the restart policy and backoff).
- If a node becomes unreachable, the control plane reschedules the Pods that were running on it to healthy nodes.
- Liveness probes detect containers that are running but not functioning correctly (e.g., deadlocked) and restart them.
- Readiness probes detect containers that are not yet ready to serve traffic and remove them from Service endpoints until they recover.

This self-healing behavior means operators do not need to write custom monitoring scripts to restart failed processes or migrate workloads off failed hosts.

### Secret and Configuration Management

Applications need configuration (database URLs, feature flags) and secrets (API keys, TLS certificates). Hardcoding these in container images is insecure and inflexible. Kubernetes provides ConfigMaps for non-sensitive configuration and Secrets for sensitive data. Both can be injected into Pods as environment variables or mounted as files. Secrets are base64-encoded by default (not encrypted), but integration with external secret stores (HashiCorp Vault, AWS Secrets Manager) through CSI drivers or operators provides encryption at rest and dynamic rotation.

### Horizontal Scaling

Kubernetes scales workloads horizontally by adjusting the number of Pod replicas. Manual scaling is a single command (`kubectl scale`). The Horizontal Pod Autoscaler (HPA) automates scaling based on CPU utilization, memory usage, or custom metrics. The Vertical Pod Autoscaler (VPA) adjusts resource requests and limits for individual containers. Cluster-level scaling is handled by the Cluster Autoscaler, which adds or removes nodes based on pending Pod resource requests.

## History: From Borg to Kubernetes

Kubernetes did not emerge from a vacuum. It is the open-source descendant of two internal Google systems.

**Borg** is Google's internal cluster management system, in operation since the mid-2000s. Borg manages the deployment and scheduling of thousands of applications across millions of machines in Google's data centers. It introduced many concepts that Kubernetes inherits: declarative job specifications, a centralized controller that reconciles actual state with desired state, and a shared-pool model where different workloads share the same physical machines for efficiency.

**Omega** was a research evolution of Borg that experimented with a shared-state scheduling architecture using optimistic concurrency control. While Omega itself was not directly open-sourced, its design lessons influenced Kubernetes.

In 2014, Google announced Kubernetes as an open-source project. Unlike a direct port of Borg (which was deeply entangled with Google's internal infrastructure), Kubernetes was designed from scratch for the broader ecosystem. It was written in Go, used etcd for its state store, and adopted a modular architecture with pluggable networking, storage, and runtime interfaces.

In 2015, Google donated Kubernetes to the newly formed **Cloud Native Computing Foundation (CNCF)**, a vendor-neutral organization under the Linux Foundation. This was a deliberate move to foster community governance and prevent any single company from controlling the project. The CNCF now hosts a broad ecosystem of cloud-native projects:

- **Graduated projects** (stable, widely adopted): Kubernetes, Prometheus, Envoy, containerd, CoreDNS, etcd, Helm, Fluentd, Argo, and others.
- **Incubating and sandbox projects**: Projects at earlier stages of maturity covering areas like service mesh (Linkerd), policy (Open Policy Agent), observability (OpenTelemetry), and security (Falco).

Kubernetes reached version 1.0 in July 2015. It follows a roughly quarterly release cycle, with each minor release supported for approximately 14 months. The project has a contributor base of thousands of developers across hundreds of organizations.

## When to Use Kubernetes

Kubernetes is powerful but not universally appropriate. It introduces significant complexity in infrastructure, networking, security, and operations. The decision to adopt it should be driven by actual requirements rather than industry trends.

**Kubernetes is a strong fit when:**

- You run multiple services that need independent scaling and deployment. The overhead of Kubernetes is amortized across many services; running a single application on Kubernetes provides little benefit over simpler alternatives.
- You need automated recovery from failures. Self-healing, automatic rescheduling, and health checking reduce operational toil for workloads that must be highly available.
- You deploy frequently and need zero-downtime updates. Rolling updates, canary deployments (with service mesh integration), and instant rollbacks support continuous delivery workflows.
- You want to avoid cloud vendor lock-in. Kubernetes provides a consistent API across AWS (EKS), Google Cloud (GKE), Azure (AKS), and on-premises environments. The same manifests work across providers.
- Your team has (or is willing to invest in) the operational expertise. Kubernetes has a steep learning curve covering networking, RBAC, resource management, observability, and security.

**Kubernetes may be overkill when:**

- You have a small number of services (1-3) with modest traffic. A managed container service like AWS ECS or Fargate, Google Cloud Run, or Azure Container Apps provides simpler operation with less overhead.
- Your team is small and lacks dedicated platform or infrastructure engineers. The operational burden of Kubernetes can overwhelm a team that is also responsible for application development.
- Your workload is a single monolithic application that does not need independent scaling of components. A VM-based deployment with a load balancer may be simpler and equally effective.
- You are running serverless or event-driven workloads that fit naturally into Functions-as-a-Service platforms (AWS Lambda, Google Cloud Functions). Kubernetes can host event-driven workloads via KEDA or Knative, but the native serverless platforms require less operational overhead.

The managed Kubernetes offerings (EKS, GKE, AKS) reduce operational burden significantly by managing the control plane, but the cluster operator is still responsible for node management, networking configuration, security policies, upgrades, and workload tuning.

## Ecosystem Overview

Kubernetes is the foundation of a broad ecosystem. Understanding the major categories helps when navigating the landscape.

**Container Runtimes**: containerd (default in most distributions), CRI-O (used by OpenShift). Docker Engine is no longer used as a Kubernetes runtime directly since v1.24, though Docker-built images remain fully compatible because they conform to the OCI image specification.

**Networking**: Kubernetes defines a networking model (every Pod gets an IP, Pods can communicate without NAT) but delegates implementation to CNI plugins. Common choices include Calico (network policy, BGP), Cilium (eBPF-based networking and observability), Flannel (simple overlay networking), and Weave Net.

**Service Mesh**: Istio, Linkerd, and Consul Connect add mutual TLS, traffic management, observability, and fine-grained policy between services without modifying application code.

**Package Management**: Helm is the de facto package manager. Helm Charts package Kubernetes manifests with templating and values for customization. Kustomize provides a template-free approach using overlays and patches.

**GitOps and Continuous Delivery**: Argo CD and Flux watch Git repositories for manifest changes and automatically reconcile the cluster state to match. This "desired state in Git" model provides audit trails, rollback via git revert, and declarative infrastructure management.

**Observability**: Prometheus (metrics collection and alerting), Grafana (dashboards and visualization), Loki (log aggregation), and OpenTelemetry (distributed tracing and metrics) form the standard cloud-native observability stack.

**Security**: Open Policy Agent / Gatekeeper (policy enforcement), Falco (runtime threat detection), Trivy and Grype (image vulnerability scanning), cert-manager (automated TLS certificate management), and the built-in RBAC system.

**Storage**: Rook (Ceph orchestration on Kubernetes), Longhorn (lightweight distributed block storage), and CSI drivers from every major cloud and storage vendor.

**Serverless on Kubernetes**: Knative (scale-to-zero HTTP workloads), KEDA (event-driven autoscaling based on external event sources like message queues).

This ecosystem means Kubernetes is not just a container orchestrator -- it is a platform for building platforms. Organizations use Kubernetes as the foundation and layer on the components they need, creating internal developer platforms tailored to their requirements.
