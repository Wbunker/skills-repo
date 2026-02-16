# Persistent Storage in Kubernetes

Kubernetes decouples storage from pod lifecycles through a layered abstraction: volumes attach storage to pods, PersistentVolumes represent cluster-wide storage resources, PersistentVolumeClaims let pods request storage without knowing backend details, and StorageClasses enable fully dynamic provisioning.

## Volume Types

Volumes are declared in `pod.spec.volumes` and mounted into containers via `container.volumeMounts`. A volume's lifetime is tied to the pod that encloses it.

### emptyDir

A temporary directory created when a pod is assigned to a node and destroyed when the pod is removed. All containers in the pod share the same emptyDir contents. Primary use cases include scratch space, caches, and sharing files between containers in a multi-container pod.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: scratch-pod
spec:
  containers:
    - name: writer
      image: busybox
      command: ["sh", "-c", "echo hello > /data/greeting && sleep 3600"]
      volumeMounts:
        - name: scratch
          mountPath: /data
    - name: reader
      image: busybox
      command: ["sh", "-c", "cat /data/greeting && sleep 3600"]
      volumeMounts:
        - name: scratch
          mountPath: /data
  volumes:
    - name: scratch
      emptyDir: {}
```

Set `emptyDir.medium: Memory` to back the volume with a tmpfs (RAM-backed filesystem). Use `emptyDir.sizeLimit` to cap consumption.

### hostPath

Mounts a file or directory from the host node's filesystem into the pod. Data persists beyond the pod's lifetime but is node-local, meaning a rescheduled pod on a different node sees different (or no) data.

```yaml
volumes:
  - name: host-data
    hostPath:
      path: /var/log/app
      type: DirectoryOrCreate
```

Valid `type` values: `""` (no check), `DirectoryOrCreate`, `Directory`, `FileOrCreate`, `File`, `Socket`, `CharDevice`, `BlockDevice`. Avoid hostPath in production workloads; it introduces node-specific coupling and security risks.

### configMap and secret

Mount ConfigMap keys or Secret keys as files inside a container. Secrets are base64-encoded at rest and mounted as tmpfs by default.

```yaml
volumes:
  - name: app-config
    configMap:
      name: my-config
      items:
        - key: app.properties
          path: application.properties
  - name: app-secrets
    secret:
      secretName: my-secret
      defaultMode: 0400
```

When a ConfigMap or Secret is updated, mounted files are eventually refreshed (kubelet sync period, typically 60 seconds). Subpath mounts do not receive updates.

### projected

Combines multiple volume sources into a single directory. Supports `configMap`, `secret`, `downwardAPI`, and `serviceAccountToken` sources.

```yaml
volumes:
  - name: combined
    projected:
      sources:
        - configMap:
            name: app-config
        - secret:
            name: app-secret
        - downwardAPI:
            items:
              - path: labels
                fieldRef:
                  fieldPath: metadata.labels
        - serviceAccountToken:
            path: token
            expirationSeconds: 3600
            audience: api
```

Projected volumes are the standard mechanism for mounting bound service account tokens with configurable expiration.

### downwardAPI

Exposes pod and container metadata as files. Available fields include `metadata.name`, `metadata.namespace`, `metadata.labels`, `metadata.annotations`, `spec.nodeName`, `spec.serviceAccountName`, `status.podIP`, and container-level resource requests and limits.

```yaml
volumes:
  - name: podinfo
    downwardAPI:
      items:
        - path: "cpu-request"
          resourceFieldRef:
            containerName: app
            resource: requests.cpu
            divisor: "1m"
```

## PersistentVolumes

A PersistentVolume (PV) is a cluster-scoped resource representing a piece of provisioned storage. PVs exist independently of any pod and have their own lifecycle.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-data
spec:
  capacity:
    storage: 50Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: fast-ssd
  csi:
    driver: ebs.csi.aws.com
    volumeHandle: vol-0abc123def456
    fsType: ext4
  nodeAffinity:
    required:
      nodeSelectorTerms:
        - matchExpressions:
            - key: topology.kubernetes.io/zone
              operator: In
              values:
                - us-east-1a
```

### Capacity

Set via `spec.capacity.storage`. This is the total size of the volume. Kubernetes does not enforce the capacity limit at the filesystem level; it is used for matching PVCs to PVs.

### Access Modes

Each PV declares one or more access modes. A PV can only be mounted using one access mode at a time, even if it supports several.

| Mode | Abbreviation | Description |
|------|--------------|-------------|
| ReadWriteOnce | RWO | Mounted read-write by a single node |
| ReadOnlyMany | ROX | Mounted read-only by many nodes |
| ReadWriteMany | RWX | Mounted read-write by many nodes |
| ReadWriteOncePod | RWOP | Mounted read-write by a single pod (v1.29+) |

RWO is the most widely supported mode across storage backends. RWX requires a shared filesystem (NFS, CephFS, EFS). RWOP provides the strongest isolation guarantee, ensuring that exactly one pod across the entire cluster can write to the volume.

### Reclaim Policy

Controls what happens to a PV after its bound PVC is deleted.

- **Retain**: The PV and its data are preserved. An administrator must manually clean up and delete or re-provision the PV. The PV enters the `Released` state and cannot be bound to a new PVC until it is manually cleared of its `claimRef`.
- **Delete**: The PV and its backing storage asset (e.g., the cloud disk) are both deleted automatically. This is the default for dynamically provisioned volumes.

The legacy `Recycle` policy (basic `rm -rf`) is deprecated. Use Delete with dynamic provisioning instead.

### PV Lifecycle

A PersistentVolume moves through these phases:

1. **Available**: The PV is free and not yet bound to a claim.
2. **Bound**: The PV is bound to a PVC.
3. **Released**: The PVC has been deleted, but the resource has not yet been reclaimed. The PV still holds a reference to the deleted claim in `spec.claimRef`.
4. **Failed**: Automatic reclamation failed.

To rebind a Retained PV, delete the PV (data on the backend is preserved), then recreate it, or manually remove the `spec.claimRef` field.

## PersistentVolumeClaims

A PersistentVolumeClaim (PVC) is a namespaced request for storage. Pods reference PVCs, and the control plane binds PVCs to appropriate PVs.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-claim
  namespace: app
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: fast-ssd
  selector:
    matchLabels:
      environment: production
```

### Binding Process

1. A user creates a PVC specifying access modes, size, and optionally a StorageClass and label selector.
2. The PV controller searches for an existing Available PV that satisfies all criteria: matching StorageClass name, sufficient capacity, compatible access modes, and matching labels if a selector is specified.
3. If a matching PV exists, the controller binds the PVC to it by setting `spec.claimRef` on the PV and `spec.volumeName` on the PVC. Binding is a one-to-one mapping.
4. If no matching PV exists and a StorageClass with a provisioner is specified, dynamic provisioning creates a new PV automatically.
5. If no PV can be found or provisioned, the PVC remains in the `Pending` state until a suitable PV becomes available.

A PVC can request less storage than the PV provides. The PVC binds to the smallest PV that satisfies the request. The excess capacity is not available to other claims.

### Using PVCs in Pods

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
    - name: app
      image: myapp:latest
      volumeMounts:
        - name: data
          mountPath: /var/lib/data
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: data-claim
```

A pod referencing a PVC will not start until the PVC is bound. StatefulSets use `volumeClaimTemplates` to create per-replica PVCs automatically:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: database
spec:
  serviceName: database
  replicas: 3
  selector:
    matchLabels:
      app: database
  template:
    metadata:
      labels:
        app: database
    spec:
      containers:
        - name: db
          image: postgres:16
          volumeMounts:
            - name: pgdata
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: pgdata
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: fast-ssd
        resources:
          requests:
            storage: 100Gi
```

This creates PVCs named `pgdata-database-0`, `pgdata-database-1`, `pgdata-database-2`. Deleting the StatefulSet does not delete these PVCs; they must be removed manually.

## StorageClasses

A StorageClass provides a way to describe different "classes" of storage and enables dynamic provisioning of PersistentVolumes.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "5000"
  throughput: "250"
  encrypted: "true"
  kmsKeyId: arn:aws:kms:us-east-1:111122223333:key/abcd-1234
reclaimPolicy: Delete
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
mountOptions:
  - noatime
```

### Dynamic Provisioning

When a PVC references a StorageClass, the provisioner plugin listed in that StorageClass automatically creates a PV matching the claim's requirements. The `parameters` field is passed directly to the provisioner and is backend-specific (e.g., disk type, IOPS, encryption settings for cloud providers).

### volumeBindingMode

- **Immediate**: The PV is provisioned and bound as soon as the PVC is created, before any pod references it. This can result in a volume provisioned in a zone where no pod can schedule.
- **WaitForFirstConsumer**: Provisioning and binding are delayed until a pod using the PVC is scheduled. The scheduler's node assignment determines the topology (zone, region) of the provisioned volume. This is the recommended mode for topology-constrained storage.

### allowVolumeExpansion

When set to `true`, PVCs using this StorageClass can be expanded by editing `spec.resources.requests.storage` to a larger value. The underlying CSI driver must support expansion. Some filesystems (ext4, xfs) support online expansion; others may require the pod to be restarted. Shrinking a volume is not supported.

### Default StorageClass

A cluster can have one default StorageClass, marked with the annotation `storageclass.kubernetes.io/is-default-class: "true"`. PVCs that omit `storageClassName` are assigned the default class. If no default exists, PVCs without a class remain unbound unless a matching pre-provisioned PV is available. To request no StorageClass explicitly (bind only to manually created PVs), set `storageClassName: ""`.

## CSI Drivers

The Container Storage Interface (CSI) is the standard plugin mechanism for exposing storage systems to Kubernetes. CSI drivers run as pods in the cluster, typically deployed as a DaemonSet (node plugin) and a Deployment (controller plugin).

Common CSI drivers:

| Provider | Driver Name | RWX Support |
|----------|-------------|-------------|
| AWS EBS | ebs.csi.aws.com | No |
| AWS EFS | efs.csi.aws.com | Yes |
| GCP PD | pd.csi.storage.gke.io | No |
| GCP Filestore | filestore.csi.storage.gke.io | Yes |
| Azure Disk | disk.csi.azure.com | No |
| Azure File | file.csi.azure.com | Yes |

CSI drivers register themselves via a `CSIDriver` object:

```yaml
apiVersion: storage.k8s.io/v1
kind: CSIDriver
metadata:
  name: ebs.csi.aws.com
spec:
  attachRequired: true
  podInfoOnMount: false
  volumeLifecycleModes:
    - Persistent
  fsGroupPolicy: File
```

The `fsGroupPolicy` field controls whether the driver supports volume ownership changes: `None`, `File` (Kubernetes recursively chowns), or `ReadWriteOnceWithFSType` (chown only if fsType is defined and access mode is RWO).

## Volume Snapshots

Volume snapshots provide point-in-time copies of volumes. They require a CSI driver that implements snapshot operations and the external-snapshotter controller.

Three resources are involved:

```yaml
# 1. Define a snapshot class
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-snapclass
driver: ebs.csi.aws.com
deletionPolicy: Delete
parameters:
  tagSpecification_1: "Department=Engineering"

---
# 2. Take a snapshot of an existing PVC
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: data-snapshot
spec:
  volumeSnapshotClassName: csi-snapclass
  source:
    persistentVolumeClaimName: data-claim

---
# 3. Restore a PVC from the snapshot
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-restored
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 20Gi
  dataSource:
    name: data-snapshot
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
```

The `deletionPolicy` on VolumeSnapshotClass controls whether the underlying storage snapshot is deleted (`Delete`) or preserved (`Retain`) when the VolumeSnapshot object is removed.

## Best Practices

**Use WaitForFirstConsumer binding mode.** This prevents volumes from being provisioned in zones where no pod can run, avoiding scheduling deadlocks with topology-constrained storage.

**Set a default StorageClass.** Every cluster should have exactly one default StorageClass so that PVCs without an explicit class are handled predictably.

**Enable volume expansion.** Set `allowVolumeExpansion: true` on StorageClasses to allow resizing without reprovisioning. Monitor disk usage with alerts and expand proactively.

**Prefer dynamic provisioning over static PVs.** Manual PV management does not scale. Use StorageClasses and let provisioners handle the lifecycle.

**Use RWOP when single-writer semantics matter.** For databases and other stateful workloads that must not have concurrent writers, RWOP provides stronger guarantees than RWO (which only restricts to a single node, not a single pod).

**Set appropriate reclaim policies.** Use `Retain` for production data where accidental deletion must be recoverable. Use `Delete` for ephemeral or easily reproducible data.

**Separate storage concerns in StatefulSets.** Use distinct `volumeClaimTemplates` entries for data and write-ahead logs so they can use different StorageClasses with different performance characteristics.

**Back up with snapshots.** Integrate VolumeSnapshots into backup workflows. Schedule periodic snapshots and test restore procedures regularly.

**Do not use hostPath in production.** It ties pods to specific nodes, breaks portability, and introduces security risks. Use it only for single-node development clusters or DaemonSets that must access specific host paths (like log collectors).

**Mind the fsGroup performance impact.** For volumes with many files, recursive ownership changes on mount can be slow. Use `fsGroupPolicy: None` on the CSI driver or `pod.spec.securityContext.fsGroupChangePolicy: OnRootMismatch` to avoid unnecessary recursive chown operations.
