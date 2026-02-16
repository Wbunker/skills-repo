# Kubernetes Architecture: From Container Images to Running Pods

This reference covers the architecture of a Kubernetes cluster -- the control plane
components that make scheduling decisions, the node-level agents that run workloads,
the networking model that connects everything, and the end-to-end lifecycle of a Pod
from API request to running containers.


## Cluster Topology

A Kubernetes cluster consists of one or more control plane nodes and one or more
worker nodes. The control plane is the brain; worker nodes supply compute capacity.

```
+------------------------------------------------------------------+
|                        Kubernetes Cluster                        |
|                                                                  |
|  +---------------------------+   +----------------------------+  |
|  |     Control Plane Node    |   |       Worker Node (N)      |  |
|  |                           |   |                            |  |
|  |  +---------------------+  |   |  +----------------------+  |  |
|  |  |   kube-apiserver    |  |   |  |       kubelet        |  |  |
|  |  +---------------------+  |   |  +----------------------+  |  |
|  |  +---------------------+  |   |  +----------------------+  |  |
|  |  |       etcd          |  |   |  |     kube-proxy       |  |  |
|  |  +---------------------+  |   |  +----------------------+  |  |
|  |  +---------------------+  |   |  +----------------------+  |  |
|  |  |   kube-scheduler    |  |   |  |  container runtime   |  |  |
|  |  +---------------------+  |   |  |  (containerd/CRI-O)  |  |  |
|  |  +---------------------+  |   |  +----------------------+  |  |
|  |  | kube-controller-mgr |  |   |                            |  |
|  |  +---------------------+  |   |  +------+ +------+ +----+  |  |
|  |  +---------------------+  |   |  | Pod  | | Pod  | | .. |  |  |
|  |  | cloud-controller-mgr|  |   |  +------+ +------+ +----+  |  |
|  |  +---------------------+  |   |                            |  |
|  +---------------------------+   +----------------------------+  |
+------------------------------------------------------------------+
```

In production the control plane is typically run across three or five nodes for
high availability. etcd requires an odd-numbered quorum for leader election.


## Control Plane Components

### kube-apiserver

The API server is the single entry point for all cluster operations. Every
component -- kubectl, kubelet, controllers, schedulers -- communicates through
the API server. It never talks directly to etcd's peers or to kubelets; everything
is mediated here.

Responsibilities:

- Authenticates and authorizes every request (client certs, bearer tokens, OIDC).
- Runs the admission control chain (mutating then validating webhooks).
- Validates object schemas against the OpenAPI spec for the relevant API group.
- Persists the resulting object to etcd.
- Serves the watch API: long-lived HTTP streams that notify clients of changes.

The API server is stateless. You can run multiple replicas behind a load balancer.
All persistent state lives in etcd.

### etcd

etcd is a distributed key-value store that holds the entire cluster state --
every Pod spec, every Service, every ConfigMap. It uses the Raft consensus
protocol to replicate data across members.

Key properties:

- Strongly consistent reads and writes via leader-based replication.
- Watch support: clients can subscribe to key-prefix changes, which is how
  the API server implements its own watch mechanism.
- Typical key layout: `/registry/<resource-type>/<namespace>/<name>`.
- Performance-sensitive: latency on etcd disk I/O directly impacts cluster
  responsiveness. SSDs are strongly recommended.

Only the API server should communicate with etcd. No other component reads
from or writes to etcd directly.

### kube-scheduler

The scheduler watches for newly created Pods that have no node assignment
(`.spec.nodeName` is empty) and selects an appropriate node for each one.

The scheduling pipeline has two phases:

1. **Filtering** -- eliminates nodes that cannot run the Pod. Checks include
   resource requests (CPU, memory), taints/tolerations, node selectors, affinity
   rules, and volume topology constraints.

2. **Scoring** -- ranks the remaining feasible nodes. Scoring plugins consider
   factors like spreading Pods across failure domains, bin-packing efficiency,
   and image locality (preferring nodes that already have the container image
   cached).

The scheduler writes its decision by setting `.spec.nodeName` on the Pod object
via the API server. It does not contact the node directly.

You can run multiple schedulers and reference a specific one in a Pod spec with
`.spec.schedulerName`.

### kube-controller-manager

The controller manager runs a set of control loops (controllers) that watch the
current state of cluster objects and work to bring actual state in line with
desired state. Each controller is logically separate but they are compiled into
a single binary for operational simplicity.

Important built-in controllers:

| Controller              | Purpose                                                  |
|-------------------------|----------------------------------------------------------|
| ReplicaSet controller   | Ensures the correct number of Pod replicas are running   |
| Deployment controller   | Manages rollouts, rollbacks, and ReplicaSet transitions  |
| Job controller          | Runs Pods to completion, tracks success/failure counts   |
| Node controller         | Monitors node health, evicts Pods from unreachable nodes |
| Service account controller | Creates default ServiceAccounts in new namespaces     |
| Endpoint slice controller  | Populates EndpointSlice objects for Services          |

Every controller follows the same pattern: watch the API server for relevant
events, compare desired state to actual state, take corrective action by
creating, updating, or deleting objects through the API server.

### cloud-controller-manager

The cloud controller manager contains controller loops that depend on the
underlying cloud provider (AWS, GCP, Azure, etc.). It was split out of
kube-controller-manager to allow cloud vendors to iterate independently.

Typical responsibilities:

- **Node controller**: checks the cloud provider API to determine whether a node
  that has stopped responding has been deleted from the cloud.
- **Route controller**: sets up routes in the cloud infrastructure so that
  containers on different nodes can communicate.
- **Service controller**: creates, updates, and deletes cloud load balancers
  when a Service of type LoadBalancer is created.

On bare-metal clusters this component is not present.


## Node Components

### kubelet

The kubelet is an agent running on every node. It is responsible for making sure
that containers described in PodSpecs are running and healthy.

Workflow:

1. Watches the API server for Pods assigned to its node (`.spec.nodeName` matches).
2. Translates the PodSpec into a set of container runtime calls via the Container
   Runtime Interface (CRI).
3. Runs liveness, readiness, and startup probes.
4. Reports Pod status and node conditions back to the API server.
5. Manages volume mounts by calling the appropriate CSI driver.

The kubelet does not manage containers that were not created by Kubernetes. It
only acts on Pods from the API server (or from static Pod manifests placed in a
local directory, used for bootstrapping control plane components).

### kube-proxy

kube-proxy runs on every node and maintains network rules that implement the
Service abstraction. When a client connects to a ClusterIP, kube-proxy ensures
the traffic reaches a healthy backend Pod.

Operating modes:

- **iptables mode** (long-time default): programs iptables rules that DNAT
  traffic destined for a Service VIP to a randomly selected backend Pod IP.
  Scales to thousands of services but rule updates are O(n) for n rules.

- **IPVS mode**: uses Linux IPVS (IP Virtual Server) in the kernel. Supports
  multiple load balancing algorithms (round-robin, least connections, etc.)
  and handles large numbers of services more efficiently.

- **nftables mode** (Kubernetes 1.29+): uses nftables as the backend,
  providing better performance characteristics than iptables.

kube-proxy watches Service and EndpointSlice objects from the API server and
reconfigures rules whenever the backend set changes.

### Container Runtime

The container runtime is the software that actually pulls images, creates
containers, and manages their lifecycle. Kubernetes communicates with the
runtime through the Container Runtime Interface (CRI), a gRPC API.

```
  kubelet
    |
    | CRI gRPC calls
    v
+-----------------+       +-----------------+
|   containerd    |  or   |     CRI-O       |
+-----------------+       +-----------------+
    |                         |
    | OCI runtime calls       | OCI runtime calls
    v                         v
+-----------------+       +-----------------+
|      runc       |       |      runc       |
+-----------------+       +-----------------+
```

**containerd** is the most widely deployed CRI-compatible runtime. It manages
the full container lifecycle: image pull, snapshot creation, container execution
(delegated to an OCI runtime like runc), and container deletion.

**CRI-O** is a lightweight alternative built specifically for Kubernetes. It
implements only the CRI interface with no extras beyond what Kubernetes requires.

Both containerd and CRI-O delegate actual container creation to an OCI-compliant
low-level runtime, typically **runc**, which sets up Linux namespaces, cgroups,
and seccomp profiles for the container process.

Docker (dockershim) was removed as a supported runtime in Kubernetes 1.24. Images
built with `docker build` remain fully compatible since they conform to the OCI
image specification.


## End-to-End: How a Pod Gets Created

The following sequence traces what happens when a user runs
`kubectl create deployment nginx --image=nginx --replicas=3`.

```
kubectl                API Server              etcd
  |                        |                     |
  |--- POST Deployment --->|                     |
  |                        |--- write Dep ------>|
  |                        |                     |
  |                        |                     |
  |    Deployment Controller (watching)          |
  |         |                                    |
  |         |--- create ReplicaSet ------------->|
  |         |                                    |
  |    ReplicaSet Controller (watching)          |
  |         |                                    |
  |         |--- create Pod x3 ----------------->|
  |         |                                    |
  |    Scheduler (watching for unbound Pods)     |
  |         |                                    |
  |         |--- bind Pod to Node (x3) --------->|
  |         |                                    |
  |    kubelet on each Node (watching)           |
  |         |                                    |
  |         |--- CRI: pull image, start container|
  |         |--- report Pod status -------------->|
  |                                              |
```

Step by step:

1. **kubectl** sends a POST request to `/apis/apps/v1/namespaces/default/deployments`.
2. **API server** authenticates the request, runs admission controllers, validates
   the Deployment spec, and persists it to etcd.
3. **Deployment controller** detects the new Deployment, creates a ReplicaSet
   object with the desired replica count and Pod template.
4. **ReplicaSet controller** detects the new ReplicaSet, sees zero existing Pods
   matching its selector, and creates three Pod objects.
5. **Scheduler** detects three new Pods with empty `.spec.nodeName`. For each Pod
   it runs the filtering and scoring pipeline, then patches the Pod with the
   chosen node name.
6. **kubelet** on each assigned node detects a Pod bound to its node. It calls
   containerd (or CRI-O) via CRI to pull the `nginx` image and start the
   container. It configures networking by invoking the CNI plugin. It sets up
   any volumes via CSI.
7. **kubelet** updates the Pod status (phase, conditions, container statuses)
   back to the API server, which persists it to etcd.


## Networking Model

Kubernetes imposes three fundamental networking requirements:

1. Every Pod gets its own unique IP address.
2. All Pods can communicate with all other Pods without NAT.
3. Agents on a node (kubelet, kube-proxy) can communicate with all Pods on
   that node.

### Pod-to-Pod Communication

Pods on the same node communicate through a virtual bridge (typically `cbr0`
or `cni0`). Each Pod's network namespace has a veth pair -- one end in the Pod,
the other attached to the bridge.

Pods on different nodes communicate through the overlay or underlay network
provided by the CNI plugin:

```
  Node A                              Node B
+------------------+             +------------------+
| Pod A (10.244.1.5)             | Pod B (10.244.2.9)
|   |  veth        |             |   |  veth        |
|   v              |             |   v              |
| [cni0 bridge]    |             | [cni0 bridge]    |
|   |              |             |   |              |
+---|------eth0----+             +---|------eth0----+
    |                                |
    +---- overlay / underlay --------+
          (VXLAN, WireGuard,
           BGP, etc.)
```

### Pod-to-Service Communication

A Service provides a stable virtual IP (ClusterIP) and DNS name in front of a
dynamic set of Pod backends. When a Pod connects to a Service ClusterIP,
kube-proxy rules (iptables, IPVS, or nftables) on the local node DNAT the
packet to one of the backend Pod IPs chosen from the EndpointSlice.

DNS resolution is handled by CoreDNS:
`my-service.my-namespace.svc.cluster.local` resolves to the Service ClusterIP.

### External-to-Service Communication

Traffic from outside the cluster can reach Services through several mechanisms:

- **NodePort**: opens a static port (30000-32767) on every node. External
  clients send traffic to `<NodeIP>:<NodePort>`.
- **LoadBalancer**: provisions a cloud load balancer that forwards to NodePorts.
  The cloud-controller-manager handles the lifecycle.
- **Ingress / Gateway API**: L7 routing. An Ingress controller (NGINX, Envoy,
  Traefik, etc.) runs inside the cluster and routes HTTP/HTTPS traffic based on
  host and path rules.
- **ExternalIPs**: assigns routable IPs directly to a Service. Requires
  external routing configuration.


## Add-ons

### CoreDNS

CoreDNS is the cluster DNS server. It watches the API server for Service and
Pod objects and serves DNS records:

| Record                                        | Type | Value              |
|-----------------------------------------------|------|--------------------|
| `my-svc.my-ns.svc.cluster.local`             | A    | ClusterIP          |
| `my-svc.my-ns.svc.cluster.local`             | SRV  | port + target      |
| `10-244-1-5.my-ns.pod.cluster.local`         | A    | Pod IP             |
| `my-headless.my-ns.svc.cluster.local`        | A    | Pod IPs (all)      |

CoreDNS runs as a Deployment in the `kube-system` namespace with a
corresponding Service at a well-known ClusterIP (commonly `10.96.0.10`).
Kubelet injects this IP into every Pod's `/etc/resolv.conf`.

### metrics-server

metrics-server collects resource utilization data (CPU, memory) from kubelets
via the Summary API and exposes it through the Kubernetes Metrics API
(`metrics.k8s.io`). It powers:

- `kubectl top nodes` and `kubectl top pods`.
- Horizontal Pod Autoscaler (HPA) decision-making.

metrics-server stores data only in memory and does not provide historical data.
For long-term metrics, deploy Prometheus or a similar monitoring stack.

### CNI Plugins

The Container Network Interface (CNI) defines how network interfaces are
configured for containers. The kubelet invokes the configured CNI plugin when
setting up or tearing down a Pod's network namespace.

Common CNI plugins:

| Plugin   | Approach            | Encryption         | Network Policy |
|----------|---------------------|--------------------|----------------|
| Calico   | BGP or VXLAN        | WireGuard optional | Yes            |
| Cilium   | eBPF-based dataplane| WireGuard/IPsec    | Yes (L3-L7)    |
| Flannel  | VXLAN overlay       | No (by default)    | No             |
| Weave    | VXLAN + sleeve      | IPsec optional     | Yes            |

The choice of CNI plugin determines the cluster's Pod CIDR allocation strategy,
maximum performance characteristics, and whether NetworkPolicy objects are
enforced.


## API Groups and Versioning

The Kubernetes API is organized into API groups. Each group can be versioned
independently, allowing new features to graduate from alpha to beta to stable
without disrupting existing stable APIs.

Common API groups:

| Group                | Path prefix                   | Key resources                    |
|----------------------|-------------------------------|----------------------------------|
| core (legacy)        | `/api/v1`                     | Pod, Service, ConfigMap, Secret  |
| `apps`               | `/apis/apps/v1`               | Deployment, StatefulSet, DaemonSet|
| `batch`              | `/apis/batch/v1`              | Job, CronJob                     |
| `networking.k8s.io`  | `/apis/networking.k8s.io/v1`  | Ingress, NetworkPolicy           |
| `rbac.authorization.k8s.io` | `/apis/rbac.authorization.k8s.io/v1` | Role, ClusterRole, Bindings |
| `storage.k8s.io`     | `/apis/storage.k8s.io/v1`    | StorageClass, CSIDriver          |

Version maturity levels:

- **v1alpha1**: experimental, may change or be removed without notice. Disabled
  by default; must be enabled via feature gates.
- **v1beta1**: feature is considered mostly stable. Enabled by default. May have
  minor schema changes.
- **v1**: stable, production-ready. Backward-compatible changes only.

When multiple versions exist for the same resource, the API server stores objects
at a single internal version and converts on the fly when serving older or newer
API versions.

You can discover available API groups with `kubectl api-resources` and
`kubectl api-versions`.


## Admission Controllers

Admission controllers intercept requests to the API server after authentication
and authorization but before the object is persisted to etcd. They can modify
(mutate) or reject (validate) requests.

```
  Request --> Authentication --> Authorization --> Admission --> etcd
                                                     |
                                          +----------+----------+
                                          |                     |
                                   Mutating Webhooks    Validating Webhooks
                                   (can modify object)  (can only accept/reject)
```

Admission runs in two phases:

1. **Mutating admission** -- plugins can modify the incoming object. Examples:
   injecting sidecar containers, setting default resource limits, adding labels.
   Runs first so that validating admission sees the final form of the object.

2. **Validating admission** -- plugins can accept or reject but not modify.
   Examples: enforcing that all Pods have resource limits, blocking images from
   untrusted registries, enforcing naming conventions.

Important built-in admission controllers:

| Controller                | Effect                                              |
|---------------------------|-----------------------------------------------------|
| `NamespaceLifecycle`      | Prevents creating objects in terminating namespaces  |
| `LimitRanger`             | Applies default resource requests/limits from LimitRange objects |
| `ServiceAccount`          | Injects ServiceAccount token volumes into Pods       |
| `DefaultStorageClass`     | Assigns the default StorageClass to PVCs lacking one |
| `ResourceQuota`           | Enforces namespace-level resource quotas             |
| `PodSecurity`             | Enforces Pod Security Standards (replaced PodSecurityPolicy) |
| `MutatingAdmissionWebhook`  | Calls external mutating webhooks                  |
| `ValidatingAdmissionWebhook`| Calls external validating webhooks                |

Starting in Kubernetes 1.28, **ValidatingAdmissionPolicy** allows you to write
CEL (Common Expression Language) expressions directly in Kubernetes objects
instead of deploying an external webhook server. This reduces latency and
operational complexity for common validation rules.

Example use case: reject any Deployment whose image tag is `latest`:

```
rule: "object.spec.template.spec.containers.all(c, !c.image.endsWith(':latest'))"
```

The admission chain is one of the most powerful extensibility points in
Kubernetes. Policy engines like OPA/Gatekeeper, Kyverno, and cloud-provider
admission plugins all operate as webhook-based admission controllers.


## Summary of Component Interactions

```
+------------------------------- Control Plane ------+
|                                                    |
|   kubectl/API clients                              |
|        |                                           |
|        v                                           |
|   kube-apiserver  <------>  etcd                   |
|        ^                                           |
|        |    (watch + write)                        |
|        |                                           |
|   +----+--------+-----------+----------+           |
|   |             |           |          |           |
|  scheduler  deployment  replicaset   node          |
|             controller  controller  controller     |
|                                                    |
+----------------------------------------------------+
         |  (Pod binding, status updates)
         v
+------------------ Worker Node --------------------+
|                                                    |
|   kubelet  ---- CRI ---->  containerd/CRI-O       |
|      |                         |                   |
|      |                      OCI runtime (runc)     |
|      |                                             |
|      +---- CNI ---->  network plugin               |
|      +---- CSI ---->  storage plugin               |
|                                                    |
|   kube-proxy  ---->  iptables/IPVS/nftables rules  |
|                                                    |
+----------------------------------------------------+
```

Every arrow passes through the API server. Components never communicate
peer-to-peer (with the exception of kubelet calling the local container runtime
and CNI/CSI plugins). This centralized communication pattern makes the API
server the single source of truth and the sole audit point for all cluster
operations.
