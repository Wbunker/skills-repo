# Configuring Pods with ConfigMaps and Secrets

This reference covers injecting configuration data into pods using ConfigMaps, Secrets, environment variables, and the Downward API.

## Environment Variables

### Static Values

The simplest form of configuration. Values are set directly in the pod spec and cannot change without redeploying.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  containers:
    - name: app
      image: myapp:1.0
      env:
        - name: LOG_LEVEL
          value: "info"
        - name: MAX_CONNECTIONS
          value: "100"        # all values must be strings
        - name: GREETING
          value: "Hello $(LOG_LEVEL)"  # variable reference using $(VAR_NAME)
```

Variable references with `$(VAR_NAME)` resolve against previously defined env vars in the same container. Use `$$(VAR_NAME)` to escape and produce a literal `$(VAR_NAME)`.

### ConfigMap References

```yaml
env:
  - name: DATABASE_HOST
    valueFrom:
      configMapKeyRef:
        name: db-config
        key: host
        optional: false       # pod fails to start if key or ConfigMap is missing (default)
```

### Secret References

```yaml
env:
  - name: DATABASE_PASSWORD
    valueFrom:
      secretKeyRef:
        name: db-credentials
        key: password
        optional: false
```

### Bulk Import with envFrom

Imports all keys from a ConfigMap or Secret as environment variables. Keys that are not valid environment variable names are skipped (an event is logged).

```yaml
spec:
  containers:
    - name: app
      image: myapp:1.0
      envFrom:
        - configMapRef:
            name: app-config
          prefix: CFG_          # optional: prepended to each key
        - secretRef:
            name: app-secrets
          prefix: SECRET_
```

### Downward API via fieldRef

Exposes pod and node metadata as environment variables.

```yaml
env:
  - name: POD_NAME
    valueFrom:
      fieldRef:
        fieldPath: metadata.name
  - name: POD_NAMESPACE
    valueFrom:
      fieldRef:
        fieldPath: metadata.namespace
  - name: POD_IP
    valueFrom:
      fieldRef:
        fieldPath: status.podIP
  - name: NODE_NAME
    valueFrom:
      fieldRef:
        fieldPath: spec.nodeName
  - name: SERVICE_ACCOUNT
    valueFrom:
      fieldRef:
        fieldPath: spec.serviceAccountName
  - name: POD_UID
    valueFrom:
      fieldRef:
        fieldPath: metadata.uid
  - name: HOST_IP
    valueFrom:
      fieldRef:
        fieldPath: status.hostIP
```

Labels and annotations are available through fieldRef but only via volume projection, not as environment variables.

### Resource Requests and Limits via resourceFieldRef

```yaml
env:
  - name: CPU_REQUEST
    valueFrom:
      resourceFieldRef:
        containerName: app     # optional if pod has one container
        resource: requests.cpu
        divisor: 1m            # express in millicores
  - name: MEMORY_LIMIT
    valueFrom:
      resourceFieldRef:
        resource: limits.memory
        divisor: 1Mi           # express in mebibytes
```

Available resources: `requests.cpu`, `requests.memory`, `limits.cpu`, `limits.memory`, `requests.ephemeral-storage`, `limits.ephemeral-storage`.

## ConfigMaps

A ConfigMap holds non-confidential key-value configuration data. Each ConfigMap is namespaced and limited to **1 MiB** in size (total of all keys and values).

### Creating ConfigMaps

**From literal values:**

```bash
kubectl create configmap app-config \
  --from-literal=log.level=info \
  --from-literal=cache.ttl=300
```

**From a file (key defaults to filename):**

```bash
kubectl create configmap nginx-config \
  --from-file=nginx.conf

# Override the key name:
kubectl create configmap nginx-config \
  --from-file=main-config=nginx.conf
```

**From a directory (each file becomes a key):**

```bash
kubectl create configmap app-config \
  --from-file=config-dir/
```

Hidden files (dotfiles) and subdirectories are ignored.

**From an env file:**

```bash
kubectl create configmap app-config \
  --from-env-file=app.env
```

Lines of the form `KEY=VALUE` are parsed. Blank lines and `#` comments are ignored.

**Declarative manifest:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: default
data:
  log.level: info
  cache.ttl: "300"
  app.properties: |
    database.host=db.example.com
    database.port=5432
    feature.flags=dark-mode,beta-ui
binaryData:
  logo.png: <base64-encoded-data>     # for binary content
```

`data` holds UTF-8 strings. `binaryData` holds base64-encoded binary content. A key cannot appear in both fields.

### Consuming ConfigMaps as Volumes

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  volumes:
    - name: config-volume
      configMap:
        name: app-config
        items:                        # optional: select specific keys
          - key: app.properties
            path: application.properties   # filename inside the mount
        defaultMode: 0644             # file permissions (octal)
  containers:
    - name: app
      image: myapp:1.0
      volumeMounts:
        - name: config-volume
          mountPath: /etc/app-config
          readOnly: true
```

When `items` is omitted, every key in the ConfigMap becomes a file in the mount directory. When `items` is specified, only the listed keys are projected.

**Mounting a single key as a file without hiding the directory:**

```yaml
volumeMounts:
  - name: config-volume
    mountPath: /etc/app-config/application.properties
    subPath: app.properties           # prevents hiding existing dir contents
```

Note: `subPath` mounts do not receive automatic updates when the ConfigMap changes.

### Automatic Updates

When a ConfigMap is mounted as a volume (without `subPath`), the kubelet periodically syncs the contents. The update delay is governed by the kubelet sync period and its ConfigMap cache TTL, typically converging within **30-60 seconds** but not guaranteed to be instantaneous.

Environment variables sourced from ConfigMaps are **never** updated after pod startup. A pod restart is required.

### Immutable ConfigMaps

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config-v2
immutable: true
data:
  log.level: warn
```

Setting `immutable: true` prevents any further changes and causes the kubelet to stop watching the ConfigMap, significantly reducing API server load in clusters with many ConfigMaps. This cannot be reversed -- the ConfigMap must be deleted and recreated, and pods referencing it must be restarted.

## Secrets

Secrets hold confidential data such as passwords, tokens, and keys. They are functionally similar to ConfigMaps but carry additional semantics: values are base64-encoded in the API, access can be restricted via RBAC, and they can be encrypted at rest.

Secrets are also limited to **1 MiB** in size.

### Secret Types

| Type | Description | Required Keys |
|------|-------------|---------------|
| `Opaque` | Arbitrary user-defined data (default) | none |
| `kubernetes.io/dockerconfigjson` | Docker registry credentials | `.dockerconfigjson` |
| `kubernetes.io/tls` | TLS certificate and key | `tls.crt`, `tls.key` |
| `kubernetes.io/basic-auth` | Basic authentication | `username`, `password` |
| `kubernetes.io/ssh-auth` | SSH private key | `ssh-privatekey` |
| `kubernetes.io/service-account-token` | ServiceAccount token (legacy, auto-generated) | auto-populated |

### Creating Secrets

**From literals:**

```bash
kubectl create secret generic db-credentials \
  --from-literal=username=admin \
  --from-literal=password='s3cret!'
```

**TLS secret from cert files:**

```bash
kubectl create secret tls app-tls \
  --cert=tls.crt \
  --key=tls.key
```

**Docker registry secret:**

```bash
kubectl create secret docker-registry regcred \
  --docker-server=registry.example.com \
  --docker-username=user \
  --docker-password=pass \
  --docker-email=user@example.com
```

### data vs stringData

In a Secret manifest, `data` values must be base64-encoded. `stringData` accepts plain text for convenience -- values are encoded automatically when the object is created. On read-back from the API, only `data` (base64) is returned.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
data:
  username: YWRtaW4=            # echo -n 'admin' | base64
  password: czNjcmV0IQ==        # echo -n 's3cret!' | base64
---
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
stringData:                      # plain text, encoded on creation
  username: admin
  password: "s3cret!"
```

If the same key appears in both `data` and `stringData`, the `stringData` value takes precedence.

### Consuming Secrets

**As environment variables** (see the env/envFrom examples above).

**As a volume:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  volumes:
    - name: secret-volume
      secret:
        secretName: db-credentials
        defaultMode: 0400             # restrictive permissions for secrets
        items:
          - key: password
            path: db-password
  containers:
    - name: app
      image: myapp:1.0
      volumeMounts:
        - name: secret-volume
          mountPath: /etc/secrets
          readOnly: true
```

**Pulling images from private registries:**

```yaml
spec:
  imagePullSecrets:
    - name: regcred
```

### Encryption at Rest

By default, Secrets are stored **unencrypted** in etcd. Anyone with etcd access or API access to the namespace can read them. To enable encryption at rest, create an `EncryptionConfiguration`:

```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: <base64-encoded-32-byte-key>
      - identity: {}            # fallback: allows reading unencrypted secrets
```

The API server is configured with `--encryption-provider-config` pointing to this file. After enabling, run `kubectl get secrets --all-namespaces -o json | kubectl replace -f -` to re-encrypt existing Secrets.

Managed Kubernetes services (EKS, GKE, AKS) typically offer envelope encryption with a KMS provider, which is the recommended approach.

## Downward API (Volume Projection)

The Downward API exposes pod metadata, labels, and annotations as files via a volume. This complements the `fieldRef` environment variable approach and is the only way to expose labels and annotations.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
  labels:
    app: myapp
    version: v2
  annotations:
    build.commit: "abc123"
spec:
  volumes:
    - name: podinfo
      downwardAPI:
        items:
          - path: labels
            fieldRef:
              fieldPath: metadata.labels
          - path: annotations
            fieldRef:
              fieldPath: metadata.annotations
          - path: cpu-request
            resourceFieldRef:
              containerName: app
              resource: requests.cpu
              divisor: 1m
          - path: memory-limit
            resourceFieldRef:
              containerName: app
              resource: limits.memory
              divisor: 1Mi
  containers:
    - name: app
      image: myapp:1.0
      resources:
        requests:
          cpu: 250m
          memory: 128Mi
        limits:
          cpu: 500m
          memory: 256Mi
      volumeMounts:
        - name: podinfo
          mountPath: /etc/podinfo
```

Label and annotation files use the format `key="value"\n` with one entry per line. Unlike `subPath` mounts, standard Downward API volume mounts receive live updates when labels or annotations change.

## Projected Volumes

A `projected` volume combines multiple sources into a single mount directory.

```yaml
volumes:
  - name: all-config
    projected:
      sources:
        - configMap:
            name: app-config
            items:
              - key: app.properties
                path: app.properties
        - secret:
            name: db-credentials
            items:
              - key: password
                path: db-password
        - downwardAPI:
            items:
              - path: namespace
                fieldRef:
                  fieldPath: metadata.namespace
        - serviceAccountToken:
            path: token
            expirationSeconds: 3600
            audience: api.example.com
```

## Best Practices

### Configuration Management

- Use ConfigMaps for non-sensitive, environment-specific configuration. Keep secrets out of ConfigMaps.
- Use `immutable: true` on ConfigMaps and Secrets that should not change, especially in large clusters.
- Version ConfigMaps by name (e.g., `app-config-v3`) and update Deployment references to trigger rollouts, rather than editing ConfigMaps in place and waiting for kubelet sync.
- Avoid large ConfigMaps. If your configuration exceeds a few hundred kilobytes, consider mounting it from a persistent volume or init container instead.
- Set `optional: false` (the default) on references so that pods fail fast on misconfiguration rather than starting with missing data.

### Secret Hygiene

- Never commit Secret manifests with real values to version control. Even base64 is trivially decoded.
- Enable encryption at rest. Use a KMS provider (AWS KMS, GCP KMS, Azure Key Vault) for envelope encryption.
- Restrict Secret access with RBAC. Grant `get` on specific Secrets rather than blanket access to all Secrets in a namespace.
- Prefer volume mounts over environment variables for Secrets. Environment variables appear in logs, error reports, and child process environments. Volume-mounted files are less likely to leak.
- Rotate Secrets regularly. Volume-mounted Secrets auto-update; environment variable Secrets require a pod restart.

### External Secret Management

Kubernetes Secrets alone are often insufficient for production. External secret managers provide audit logging, automatic rotation, dynamic credentials, and centralized policy.

**HashiCorp Vault** with the Vault Agent Injector or Vault CSI Provider:

```yaml
metadata:
  annotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/role: "myapp"
    vault.hashicorp.com/agent-inject-secret-db-password: "secret/data/myapp/db"
    vault.hashicorp.com/agent-inject-template-db-password: |
      {{- with secret "secret/data/myapp/db" -}}
      {{ .Data.data.password }}
      {{- end -}}
```

**External Secrets Operator (ESO)** syncs secrets from external stores (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault, HashiCorp Vault) into Kubernetes Secrets:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  target:
    name: db-credentials          # resulting Kubernetes Secret
    creationPolicy: Owner
  data:
    - secretKey: password
      remoteRef:
        key: production/myapp/db
        property: password
```

**Sealed Secrets** by Bitnami allow encrypting Secrets so they can be safely stored in Git. The `kubeseal` CLI encrypts against a cluster-side controller's public key. Only the controller can decrypt:

```bash
# Encrypt a Secret into a SealedSecret
kubeseal --format yaml < secret.yaml > sealed-secret.yaml
```

```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: db-credentials
spec:
  encryptedData:
    password: AgBghT8...          # encrypted, safe to commit
```

The Sealed Secrets controller decrypts the SealedSecret and creates a regular Secret in the cluster.

### Choosing an Approach

| Requirement | Approach |
|---|---|
| Simple app config, non-sensitive | ConfigMap |
| Passwords, API keys within cluster | Secret with encryption at rest |
| Audit trail, dynamic credentials | External manager (Vault, cloud KMS) |
| GitOps-friendly encrypted secrets | Sealed Secrets or SOPS |
| Cross-cluster secret sync | External Secrets Operator |
