# Exposing Your Pods with Services

## The Service Abstraction

Pods are ephemeral. They receive dynamic IP addresses that change on restart, reschedule, or scaling events. A Service provides a stable network identity (virtual IP and DNS name) for a logical set of Pods, decoupling consumers from the lifecycle of individual Pod instances.

A Service performs two functions: it groups Pods via a label selector, and it load-balances traffic across those Pods. The stable ClusterIP assigned to a Service persists for the lifetime of the Service object itself, regardless of what happens to the backing Pods.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app
  namespace: production
spec:
  selector:
    app: my-app
    tier: frontend
  ports:
    - name: http
      protocol: TCP
      port: 80          # Port the Service listens on
      targetPort: 8080  # Port on the Pod to forward to
```

The `targetPort` can also reference a named port defined in the Pod spec, which is useful when different Pod versions expose different port numbers:

```yaml
# In the Pod spec
ports:
  - name: web
    containerPort: 8080

# In the Service spec
targetPort: web
```

## Label Selectors

The `spec.selector` field determines which Pods belong to the Service. The selector performs an AND match -- all specified labels must be present on a Pod for it to receive traffic. The controller continuously evaluates the selector; Pods that gain or lose matching labels are added to or removed from the Service in real time.

Services without a selector are valid. They create the Service and its ClusterIP but do not automatically populate Endpoints. This pattern is used when you want to manually control what backs a Service (for example, pointing at an external database) by creating an Endpoints object with the same name.

## Service Types

### ClusterIP (default)

Allocates a virtual IP from the cluster's service CIDR, reachable only from within the cluster.

```yaml
spec:
  type: ClusterIP
  selector:
    app: backend
  ports:
    - port: 443
      targetPort: 8443
```

### NodePort

Extends ClusterIP by additionally opening a static port (default range 30000-32767) on every node in the cluster. Traffic arriving at `<NodeIP>:<NodePort>` is forwarded to the Service.

```yaml
spec:
  type: NodePort
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 31080   # Optional; auto-assigned if omitted
```

### LoadBalancer

Extends NodePort by provisioning an external load balancer through the cloud provider. The external IP appears in `status.loadBalancer.ingress`. On bare-metal clusters, this type requires an add-on such as MetalLB.

```yaml
spec:
  type: LoadBalancer
  selector:
    app: web
  ports:
    - port: 443
      targetPort: 8443
  loadBalancerSourceRanges:
    - 203.0.113.0/24    # Restrict external access by source IP
```

### ExternalName

Maps a Service to a DNS CNAME. No proxying occurs. The cluster DNS returns a CNAME record pointing to the specified external hostname. No selector, ClusterIP, or Endpoints are involved.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-db
spec:
  type: ExternalName
  externalName: db.legacy.example.com
```

Caveats: ExternalName does not support ports (the CNAME is returned as-is), and it does not work with TLS verification when the client expects a different hostname.

### Headless Services

Setting `clusterIP: None` creates a headless Service. Instead of a single virtual IP, a DNS lookup returns the individual Pod IPs as A/AAAA records. This is essential for StatefulSets and any workload where clients need to connect to specific Pods.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: cassandra
spec:
  clusterIP: None
  selector:
    app: cassandra
  ports:
    - port: 9042
```

With a headless Service backed by a StatefulSet, each Pod gets a stable DNS entry: `<pod-name>.<service-name>.<namespace>.svc.cluster.local`.

## kube-proxy Modes

kube-proxy runs on every node and programs the data-plane rules that implement Services. It watches the API server for Service and EndpointSlice changes and translates them into forwarding rules.

### iptables Mode (default)

kube-proxy writes iptables rules in the `nat` table. For each Service, a chain is created that uses random probability-based matching to distribute connections across backend Pods. This is purely in-kernel and does not involve userspace proxying.

Characteristics:
- Lower overhead per connection than userspace mode.
- Rule evaluation is O(n) in the number of rules. At very large scale (thousands of Services), rule programming and packet traversal can become slow.
- Connection tracking (`conntrack`) handles return traffic and session affinity.
- No built-in health checking of backends -- traffic may be sent to Pods that are failing readiness probes until EndpointSlice updates propagate.

### IPVS Mode

kube-proxy uses Linux IPVS (IP Virtual Server), a kernel-level Layer 4 load balancer. It creates a virtual server for each Service IP and adds real servers for each backend Pod.

Characteristics:
- Uses hash tables internally, giving O(1) lookup regardless of the number of Services.
- Supports multiple scheduling algorithms: `rr` (round-robin), `lc` (least connections), `dh` (destination hashing), `sh` (source hashing), `sed` (shortest expected delay), `nq` (never queue).
- Still uses iptables for masquerading and SNAT, but the core forwarding is handled by IPVS.
- Requires IPVS kernel modules (`ip_vs`, `ip_vs_rr`, etc.) to be loaded on each node.

Enable with `--proxy-mode=ipvs` on kube-proxy or via KubeProxyConfiguration:

```yaml
apiVersion: kubeproxy.config.k8s.io/v1alpha1
kind: KubeProxyConfiguration
mode: ipvs
ipvs:
  scheduler: rr
```

## Service DNS (CoreDNS)

CoreDNS is the default cluster DNS provider. It watches the Kubernetes API and serves DNS records for Services and Pods.

### Service DNS Records

Every ClusterIP Service gets an A record:

```
<service-name>.<namespace>.svc.cluster.local -> ClusterIP
```

For example, the Service `my-app` in namespace `production`:

```
my-app.production.svc.cluster.local -> 10.96.45.12
```

Named ports on a Service also get SRV records:

```
_http._tcp.my-app.production.svc.cluster.local -> 0 100 80 my-app.production.svc.cluster.local
```

### Pod DNS and Search Domains

Pods are configured (via `/etc/resolv.conf`) with search domains:

```
search production.svc.cluster.local svc.cluster.local cluster.local
nameserver 10.96.0.10
options ndots:5
```

This means a Pod in the `production` namespace can reach `my-app` using any of:
- `my-app` (resolved via search domains)
- `my-app.production`
- `my-app.production.svc`
- `my-app.production.svc.cluster.local` (fully qualified)

### The ndots Setting

The `ndots:5` option means that any name with fewer than 5 dots is treated as a relative name and the search domains are appended before trying the name as-is. This causes external lookups like `api.example.com` (2 dots, fewer than 5) to first try `api.example.com.production.svc.cluster.local`, then `api.example.com.svc.cluster.local`, and so on, before finally trying `api.example.com.` as an absolute name.

For workloads making many external DNS queries, reducing `ndots` or appending a trailing dot to FQDNs improves performance:

```yaml
spec:
  dnsConfig:
    options:
      - name: ndots
        value: "2"
```

## Endpoints and EndpointSlices

### Endpoints

For each Service with a selector, the Endpoints controller creates an Endpoints object with the same name. This object contains a flat list of all ready Pod IP:port pairs. The Endpoints object has a hard size limit that becomes problematic at scale.

```yaml
apiVersion: v1
kind: Endpoints
metadata:
  name: my-app
subsets:
  - addresses:
      - ip: 10.244.1.5
      - ip: 10.244.2.8
    ports:
      - port: 8080
```

### EndpointSlices

EndpointSlices (default since Kubernetes 1.21) replace Endpoints for scalability. Instead of one monolithic object, the controller creates multiple EndpointSlice objects, each holding up to 100 endpoints by default. This reduces the size of API watch events and speeds up kube-proxy programming.

```yaml
apiVersion: discovery.k8s.io/v1
kind: EndpointSlice
metadata:
  name: my-app-abc12
  labels:
    kubernetes.io/service-name: my-app
addressType: IPv4
endpoints:
  - addresses:
      - 10.244.1.5
    conditions:
      ready: true
      serving: true
      terminating: false
    nodeName: node-1
    zone: us-east-1a
ports:
  - name: http
    port: 8080
    protocol: TCP
```

Key fields in EndpointSlice endpoints:
- `ready`: Pod has passed readiness checks and is not terminating.
- `serving`: Pod can serve traffic (may be true even while terminating, allowing graceful drain).
- `terminating`: Pod is in the process of shutting down.

## Session Affinity

By default, kube-proxy distributes each new connection randomly. To pin a client to the same backend Pod, use session affinity:

```yaml
spec:
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 3600   # Default is 10800 (3 hours)
```

Session affinity is based on the client source IP. It is incompatible with scenarios where source IPs are masked by intermediate proxies. Note that only `ClientIP` and `None` are supported values.

## Multi-Port Services

A single Service can expose multiple ports. Each port must have a unique name when more than one is defined:

```yaml
spec:
  selector:
    app: my-app
  ports:
    - name: http
      port: 80
      targetPort: 8080
    - name: https
      port: 443
      targetPort: 8443
    - name: metrics
      port: 9090
      targetPort: 9090
```

## External IPs

The `externalIPs` field allows a Service to accept traffic on specific node IPs, independent of Service type. Kubernetes does not manage these IPs -- the administrator must ensure they are routed to cluster nodes.

```yaml
spec:
  type: ClusterIP
  externalIPs:
    - 192.168.1.100
  ports:
    - port: 80
      targetPort: 8080
```

Traffic arriving at `192.168.1.100:80` on any node will be handled by this Service. Use with caution: this bypasses cloud load balancers and can create security exposure if not carefully managed.

## Traffic Policies

### externalTrafficPolicy

Controls how traffic entering the cluster from external sources (NodePort, LoadBalancer) is routed.

**Cluster (default):** Traffic may be forwarded to Pods on any node. kube-proxy performs SNAT, which means the source IP seen by the Pod is the node IP, not the original client IP.

**Local:** Traffic is only sent to Pods on the node that received the connection. If no local Pod exists, the connection is dropped. Preserves client source IP (no SNAT). Cloud load balancers use health checks to avoid sending traffic to nodes without local Pods.

```yaml
spec:
  type: LoadBalancer
  externalTrafficPolicy: Local
  selector:
    app: web
  ports:
    - port: 443
      targetPort: 8443
```

Trade-offs of `Local`:
- Preserves source IP (critical for IP-based access control and logging).
- Can cause uneven load distribution if Pods are not spread evenly across nodes.
- Requires health check integration with the load balancer.

### internalTrafficPolicy

Controls routing of traffic originating from within the cluster. Available since Kubernetes 1.26 (stable).

**Cluster (default):** Traffic may be routed to any backend Pod across the cluster.

**Local:** Traffic is restricted to backend Pods on the same node as the client. If no local Pod exists, traffic is dropped. Useful for node-local caches or reducing cross-node bandwidth.

```yaml
spec:
  internalTrafficPolicy: Local
  selector:
    app: node-cache
  ports:
    - port: 6379
      targetPort: 6379
```

## Troubleshooting Services

### Verify the Service and Endpoints

```bash
# Check the Service exists and has a ClusterIP
kubectl get svc my-app -o wide

# Verify Endpoints are populated (empty means selector matches no ready Pods)
kubectl get endpoints my-app
kubectl get endpointslices -l kubernetes.io/service-name=my-app

# Confirm Pods matching the selector exist and are Ready
kubectl get pods -l app=my-app -o wide
```

### Common Failure Modes

**No Endpoints populated:**
- Selector labels do not match any Pod labels (check for typos).
- Pods exist but none are passing readiness probes.
- Pods are in a different namespace than the Service.

**Connection refused:**
- `targetPort` does not match the port the container is actually listening on.
- Container is binding to `127.0.0.1` instead of `0.0.0.0`.

**Intermittent timeouts:**
- A subset of backend Pods are unhealthy but still in the Endpoints (readiness probe too lenient).
- DNS resolution delays from high `ndots` value causing search domain iteration.
- conntrack table exhaustion under heavy connection churn.

**NodePort not reachable:**
- Firewall or security group rules blocking the NodePort range (30000-32767).
- `externalTrafficPolicy: Local` with no Pods on the target node.

### DNS Debugging

```bash
# Run a debug Pod with DNS tools
kubectl run dns-debug --image=busybox:1.36 --restart=Never --rm -it -- nslookup my-app.production.svc.cluster.local

# Check CoreDNS Pods are running
kubectl get pods -n kube-system -l k8s-app=kube-dns

# Inspect CoreDNS logs for errors
kubectl logs -n kube-system -l k8s-app=kube-dns --tail=50

# Verify resolv.conf inside a Pod
kubectl exec <pod-name> -- cat /etc/resolv.conf
```

### kube-proxy Debugging

```bash
# Check kube-proxy logs for programming errors
kubectl logs -n kube-system -l k8s-app=kube-proxy --tail=100

# Inspect iptables rules for a specific Service (on a node)
iptables-save | grep my-app

# For IPVS mode, inspect virtual servers
ipvsadm -Ln
```
