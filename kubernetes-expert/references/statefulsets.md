# StatefulSets -- Deploying Stateful Applications

StatefulSets are the Kubernetes workload controller designed for applications that require stable, persistent identity and storage. Unlike Deployments, which treat pods as interchangeable cattle, StatefulSets treat each pod as a unique individual with a predictable name, dedicated storage, and deterministic lifecycle ordering.

## Why StatefulSets Exist

Deployments work well for stateless applications where any pod can handle any request and pods are fungible. Stateful applications break this model in three fundamental ways:

1. **Stable network identity** -- Clustered databases and distributed systems need peers to find each other by a predictable hostname. A MySQL replica must know exactly which pod is the primary. When a pod restarts, it must come back with the same identity.

2. **Stable persistent storage** -- Each instance in a database cluster owns its own data directory. If a pod is rescheduled to a different node, it must reattach to the same PersistentVolume containing its data, not receive a fresh empty volume.

3. **Ordered deployment and scaling** -- Many distributed systems require a specific initialization order. A primary database must be running before replicas attempt to connect and synchronize. Scaling down must remove the most recently added member first to avoid data loss.

StatefulSets provide all three guarantees, making them the correct abstraction for databases, message queues, consensus systems, and any application where pod identity matters.

## StatefulSet Specification

A complete StatefulSet manifest includes the controller spec, a pod template, and volume claim templates:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: database
spec:
  serviceName: postgres-headless    # required: must reference a headless Service
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  podManagementPolicy: OrderedReady  # default; alternative is Parallel
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 0                   # pods with ordinal >= partition are updated
  template:
    metadata:
      labels:
        app: postgres
    spec:
      terminationGracePeriodSeconds: 30
      containers:
        - name: postgres
          image: postgres:16
          ports:
            - containerPort: 5432
              name: postgres
          env:
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: password
            - name: PGDATA
              value: /var/lib/postgresql/data/pgdata
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
            limits:
              cpu: "1"
              memory: "1Gi"
          readinessProbe:
            exec:
              command: ["pg_isready", "-U", "postgres"]
            initialDelaySeconds: 5
            periodSeconds: 10
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: fast-ssd
        resources:
          requests:
            storage: 20Gi
```

### Key Spec Fields

| Field | Purpose |
|-------|---------|
| `serviceName` | Must match a headless Service name. Required for DNS record generation. |
| `replicas` | Number of desired pods. Scaling respects ordering guarantees. |
| `selector` | Label selector that must match the pod template labels. Immutable after creation. |
| `template` | Standard pod template spec. |
| `volumeClaimTemplates` | PVC templates. One PVC per pod per template is created automatically. |
| `podManagementPolicy` | `OrderedReady` (default) or `Parallel`. Controls pod creation/deletion ordering. |
| `updateStrategy` | `RollingUpdate` (default) or `OnDelete`. Controls how pods are updated on spec change. |

## Stable Network Identity

Every pod in a StatefulSet receives a predictable, stable identity derived from the StatefulSet name and an ordinal index starting at zero.

For a StatefulSet named `postgres` with 3 replicas:

| Ordinal | Pod Name | Hostname |
|---------|----------|----------|
| 0 | `postgres-0` | `postgres-0` |
| 1 | `postgres-1` | `postgres-1` |
| 2 | `postgres-2` | `postgres-2` |

These names are deterministic. If `postgres-1` is deleted, the replacement pod is also named `postgres-1` and receives the same hostname and the same PersistentVolumeClaim.

### DNS Records and Headless Service Pairing

StatefulSets require a headless Service (a Service with `clusterIP: None`) to generate DNS records for individual pods. The headless Service does not load-balance traffic; instead it creates DNS entries that resolve directly to pod IPs.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres-headless
  namespace: database
spec:
  clusterIP: None          # headless -- no virtual IP
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
      name: postgres
```

With this headless Service in place, each pod gets a fully qualified DNS record:

```
<pod-name>.<service-name>.<namespace>.svc.cluster.local
```

Concrete examples for the three postgres pods:

```
postgres-0.postgres-headless.database.svc.cluster.local
postgres-1.postgres-headless.database.svc.cluster.local
postgres-2.postgres-headless.database.svc.cluster.local
```

An SRV lookup on the headless Service returns all pod endpoints, enabling peer discovery. Applications can resolve a specific pod by name or enumerate all members by querying the Service domain.

This is the mechanism that allows database replicas to locate and connect to their primary, and distributed systems to form clusters with known membership.

## Stable Storage with volumeClaimTemplates

The `volumeClaimTemplates` field causes the StatefulSet controller to create a dedicated PersistentVolumeClaim for each pod. PVCs follow a deterministic naming convention:

```
<volumeClaimTemplate-name>-<statefulset-name>-<ordinal>
```

For the example above with volume claim template named `data` and StatefulSet named `postgres`:

| Pod | PVC Name |
|-----|----------|
| `postgres-0` | `data-postgres-0` |
| `postgres-1` | `data-postgres-1` |
| `postgres-2` | `data-postgres-2` |

### PVC Retention Behavior

PersistentVolumeClaims created by a StatefulSet are **not automatically deleted** when pods are deleted or when the StatefulSet is scaled down. This is a deliberate safety measure: data must survive pod rescheduling, node failures, and even accidental StatefulSet deletion.

When a pod is rescheduled (same ordinal, new node), it reattaches to the exact same PVC. The data is preserved across restarts.

Kubernetes 1.27+ introduced the `persistentVolumeClaimRetentionPolicy` field to control this behavior:

```yaml
spec:
  persistentVolumeClaimRetentionPolicy:
    whenDeleted: Retain    # what happens to PVCs when StatefulSet is deleted
    whenScaled: Retain     # what happens to PVCs when scaling down
```

Options for both fields are `Retain` (default, keep the PVC) or `Delete` (remove the PVC). For production databases, `Retain` is strongly recommended for both cases.

To manually clean up PVCs after removing a StatefulSet:

```bash
kubectl delete pvc -l app=postgres -n database
```

## Ordered Deployment and Scaling

With the default `podManagementPolicy: OrderedReady`, the StatefulSet controller enforces strict sequential ordering.

**Scaling up (0 to 3 replicas):**
1. Create `postgres-0`. Wait until it is Running and Ready.
2. Create `postgres-1`. Wait until it is Running and Ready.
3. Create `postgres-2`. Wait until it is Running and Ready.

**Scaling down (3 to 1 replica):**
1. Terminate `postgres-2`. Wait until fully terminated.
2. Terminate `postgres-1`. Wait until fully terminated.
3. `postgres-0` remains running.

Pods are always removed in reverse ordinal order. This guarantees that the primary (typically ordinal 0) is the last to be removed and the first to be created, which aligns with how most replicated databases expect initialization to proceed.

If any pod in the sequence fails to become Ready, the controller halts and does not proceed to the next pod. This prevents cascading failures in distributed systems that depend on quorum.

## Pod Management Policy

The `podManagementPolicy` field controls whether ordering guarantees are enforced:

### OrderedReady (default)

Pods are created sequentially (0, 1, 2...) and each must reach Ready before the next is started. Deletion proceeds in reverse order. This is the correct choice for systems with initialization dependencies.

### Parallel

All pods are created or terminated simultaneously, without waiting for predecessors. Use this when pods are independent and do not need sequencing, but you still need stable identity and storage.

```yaml
spec:
  podManagementPolicy: Parallel
```

Parallel mode is useful for workloads like distributed caches where each node is self-contained and peers discover each other asynchronously after startup. It significantly reduces startup time for large StatefulSets.

## Update Strategies

### RollingUpdate (default)

When the pod template spec changes, pods are terminated and recreated one at a time in **reverse ordinal order** (highest to lowest). Each new pod must become Ready before the controller proceeds to the next.

```yaml
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 0
```

#### Canary Updates with Partition

The `partition` parameter enables staged rollouts. Only pods with an ordinal **greater than or equal to** the partition value are updated. Pods with a lower ordinal retain the previous spec.

To canary a change on just the last pod of a 3-replica StatefulSet:

```yaml
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 2    # only postgres-2 gets the new spec
```

After validating the canary, lower the partition progressively (to 1, then 0) to roll out the update to all pods. This gives fine-grained control for stateful applications where a bad update could corrupt data.

### OnDelete

Pods are not automatically updated when the spec changes. The operator must manually delete each pod, and the controller recreates it with the new spec. This provides full manual control over the rollout sequence.

```yaml
spec:
  updateStrategy:
    type: OnDelete
```

OnDelete is appropriate for databases where you need to perform manual failover steps between updating each node (for example, promoting a new primary before updating the old one).

## Common Use Cases

### Databases (MySQL, PostgreSQL)

Replicated databases are the canonical StatefulSet use case. The primary takes ordinal 0, replicas take higher ordinals. Each instance needs its own data directory on a persistent volume, and replicas must know the primary's hostname to configure replication.

### Message Queues (Kafka, RabbitMQ)

Kafka brokers each have a unique broker ID and manage specific topic partitions stored on disk. Losing a broker's identity or storage would require expensive partition rebalancing. StatefulSets ensure brokers maintain their identity and data across restarts.

### Distributed Consensus Systems (ZooKeeper, etcd)

ZooKeeper and etcd require a fixed membership list with stable hostnames for leader election and quorum. StatefulSet DNS records provide exactly this. A three-node ZooKeeper ensemble can hardcode peer addresses as `zk-0.zk-headless:2888:3888`, `zk-1.zk-headless:2888:3888`, `zk-2.zk-headless:2888:3888`.

## Complete Example: Replicated MySQL

This example deploys a MySQL primary-replica cluster with a StatefulSet, headless Service, and a ConfigMap for initialization.

```yaml
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql-config
  namespace: database
data:
  primary.cnf: |
    [mysqld]
    server-id=1
    log-bin=mysql-bin
    binlog-format=ROW
  replica.cnf: |
    [mysqld]
    super-read-only
    log-bin=mysql-bin
    binlog-format=ROW
---
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
  namespace: database
type: Opaque
data:
  root-password: cGFzc3dvcmQxMjM=     # base64 of "password123"
  replication-password: cmVwbHBhc3M=   # base64 of "replpass"
---
apiVersion: v1
kind: Service
metadata:
  name: mysql-headless
  namespace: database
spec:
  clusterIP: None
  selector:
    app: mysql
  ports:
    - port: 3306
      targetPort: 3306
      name: mysql
---
apiVersion: v1
kind: Service
metadata:
  name: mysql-read
  namespace: database
spec:
  selector:
    app: mysql
  ports:
    - port: 3306
      targetPort: 3306
      name: mysql
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
  namespace: database
spec:
  serviceName: mysql-headless
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      initContainers:
        - name: init-mysql
          image: mysql:8.0
          command:
            - bash
            - "-c"
            - |
              set -ex
              # Determine server-id from pod ordinal
              [[ $(hostname) =~ -([0-9]+)$ ]] || exit 1
              ordinal=${BASH_REMATCH[1]}
              # Copy appropriate config based on ordinal
              if [[ $ordinal -eq 0 ]]; then
                cp /mnt/config/primary.cnf /mnt/conf.d/server.cnf
              else
                cp /mnt/config/replica.cnf /mnt/conf.d/server.cnf
              fi
              # Set server-id (ordinal + 1 to avoid server-id=0)
              echo "server-id=$((ordinal + 1))" >> /mnt/conf.d/server.cnf
          volumeMounts:
            - name: conf
              mountPath: /mnt/conf.d
            - name: config-map
              mountPath: /mnt/config
      containers:
        - name: mysql
          image: mysql:8.0
          ports:
            - containerPort: 3306
              name: mysql
          env:
            - name: MYSQL_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mysql-secret
                  key: root-password
          volumeMounts:
            - name: data
              mountPath: /var/lib/mysql
            - name: conf
              mountPath: /etc/mysql/conf.d
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
            limits:
              cpu: "1"
              memory: "1Gi"
          livenessProbe:
            exec:
              command: ["mysqladmin", "ping", "-u", "root", "-p${MYSQL_ROOT_PASSWORD}"]
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            exec:
              command: ["mysql", "-u", "root", "-p${MYSQL_ROOT_PASSWORD}", "-e", "SELECT 1"]
            initialDelaySeconds: 10
            periodSeconds: 5
      volumes:
        - name: conf
          emptyDir: {}
        - name: config-map
          configMap:
            name: mysql-config
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: standard
        resources:
          requests:
            storage: 10Gi
```

This setup provides:

- **`mysql-0`** as the primary (ordinal 0), configured with binary logging enabled for replication.
- **`mysql-1`** and **`mysql-2`** as read replicas, configured in `super-read-only` mode.
- A **headless Service** (`mysql-headless`) so replicas can locate the primary at `mysql-0.mysql-headless.database.svc.cluster.local`.
- A **regular Service** (`mysql-read`) that load-balances read traffic across all pods.
- An **init container** that inspects the pod's ordinal to apply the correct MySQL configuration before the main container starts.
- **Separate PVCs** (`data-mysql-0`, `data-mysql-1`, `data-mysql-2`) so each instance retains its data directory independently.

## StatefulSet vs Deployment

| Characteristic | Deployment | StatefulSet |
|---------------|------------|-------------|
| Pod names | Random suffix (`app-7d4f8b-x9k2z`) | Ordinal index (`app-0`, `app-1`) |
| Pod ordering | No ordering guarantee | Sequential creation and deletion |
| Storage | Shared PVC or no persistence | Dedicated PVC per pod via volumeClaimTemplates |
| Network identity | Interchangeable, accessed via Service | Stable DNS per pod via headless Service |
| Scaling | All pods equivalent | Ordinal-aware, reverse-order termination |
| Use case | Stateless web apps, APIs, workers | Databases, queues, distributed consensus |

**Use a Deployment** when pods are interchangeable, share the same configuration, and can be freely replaced. Examples: web servers, REST APIs, background workers.

**Use a StatefulSet** when each pod has a unique role or owns specific data, when pods need to discover each other by stable hostname, or when initialization order matters. Examples: database clusters, Kafka brokers, ZooKeeper ensembles, etcd clusters.

## Limitations and Considerations

**PVCs are not automatically deleted.** Scaling down or deleting a StatefulSet leaves PVCs (and their bound PVs) intact. This prevents data loss but requires manual cleanup. Always audit orphaned PVCs after removing StatefulSets.

**No automatic data rebalancing.** When scaling from 3 to 5 replicas, the new pods get empty volumes. The application is responsible for populating data on new members (through replication, snapshots, or backup restoration). Kubernetes provides the infrastructure but not the data migration logic.

**Deleting a StatefulSet does not delete pods.** You must scale to 0 first or delete the pods separately to ensure graceful, ordered termination. Deleting the StatefulSet object directly orphans the pods.

**Storage class must support dynamic provisioning.** The `volumeClaimTemplates` mechanism creates PVCs dynamically. If the specified StorageClass does not support dynamic provisioning, PVs must be pre-created manually.

**Pod disruption budget is important.** For quorum-based systems, always pair StatefulSets with a PodDisruptionBudget to prevent voluntary evictions (node drains, cluster upgrades) from breaking quorum:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: postgres-pdb
  namespace: database
spec:
  minAvailable: 2    # maintain quorum for a 3-node cluster
  selector:
    matchLabels:
      app: postgres
```

**Headless Service must exist before the StatefulSet.** The `serviceName` field references a headless Service. If that Service does not exist, DNS records for the pods will not be created, and peer discovery will fail.

**Updates can be slow.** With `OrderedReady` and `RollingUpdate`, updating a 10-replica StatefulSet means updating one pod at a time, waiting for each to become Ready. For large clusters, consider using `partition` to stage the rollout or `OnDelete` for manual control.
