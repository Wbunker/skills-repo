# Authentication and Authorization on Kubernetes

Kubernetes does not have a built-in user database. Instead, it delegates identity to external systems and then enforces access control through a layered pipeline: authentication determines *who* you are, authorization determines *what* you can do, and admission controllers apply policy *before* objects are persisted.

## Authentication

Every request to the API server must be authenticated. Kubernetes supports multiple authentication strategies simultaneously; the first module to accept the request determines the identity.

### X.509 Client Certificates

The API server is started with `--client-ca-file`, which specifies a CA bundle. Any client certificate signed by that CA is considered authenticated. The common name (`CN`) of the certificate becomes the username, and organization (`O`) fields become group memberships.

```bash
# Generate a private key and CSR for user "alice" in group "dev-team"
openssl genrsa -out alice.key 2048
openssl req -new -key alice.key -out alice.csr \
  -subj "/CN=alice/O=dev-team"

# Sign it with the cluster CA (requires access to ca.crt and ca.key)
openssl x509 -req -in alice.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out alice.crt -days 365
```

You can also submit a `CertificateSigningRequest` resource to let the cluster sign the certificate:

```yaml
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: alice-csr
spec:
  request: <base64-encoded-csr>
  signerName: kubernetes.io/kube-apiserver-client
  usages:
    - client auth
```

After approval (`kubectl certificate approve alice-csr`), retrieve the signed certificate from `.status.certificate`.

### Bearer Tokens

Static token files (passed via `--token-auth-file`) map tokens to users. Each line in the CSV file contains `token,user,uid,"group1,group2"`. This method is simple but difficult to rotate and is discouraged in production. The token is passed in the `Authorization: Bearer <token>` header.

### OpenID Connect (OIDC)

OIDC is the recommended approach for human user authentication. The API server validates JWT ID tokens issued by a trusted identity provider (Keycloak, Okta, Azure AD, Google). Relevant API server flags:

- `--oidc-issuer-url` -- the issuer URL (must use HTTPS).
- `--oidc-client-id` -- the OAuth2 client ID.
- `--oidc-username-claim` -- the JWT claim to use as the username (default `sub`).
- `--oidc-groups-claim` -- the JWT claim containing group memberships.

The API server does not initiate OAuth flows. A client-side tool (such as `kubelogin` or `kubectl oidc-login`) handles the browser-based login and injects the token into kubeconfig.

### Webhook Token Authentication

With `--authentication-token-webhook-config-file`, the API server sends a `TokenReview` to an external service, which responds with the authenticated identity. This allows integration with custom token systems.

### kubeconfig Authentication Methods

The kubeconfig file supports several user authentication entries under `users[].user`:

- `client-certificate` and `client-key` -- paths to X.509 cert and key files.
- `client-certificate-data` and `client-key-data` -- base64-encoded inline cert and key.
- `token` -- a static bearer token.
- `exec` -- runs an external command that returns a credential (used by OIDC helpers, AWS IAM authenticator, GKE gcloud).

```yaml
users:
  - name: alice
    user:
      exec:
        apiVersion: client.authentication.k8s.io/v1beta1
        command: kubectl
        args:
          - oidc-login
          - get-token
          - --oidc-issuer-url=https://idp.example.com
          - --oidc-client-id=kubernetes
```

## User Accounts vs Service Accounts

Kubernetes draws a sharp distinction between human users and service accounts. Human user identities are managed externally (certificates, OIDC, webhooks); no `User` resource exists in the API. Service accounts are namespaced Kubernetes objects that provide an identity for processes running inside pods.

Key differences:

| Aspect | User Accounts | Service Accounts |
|---|---|---|
| Managed by | External identity provider | Kubernetes API (`v1/ServiceAccount`) |
| Scope | Cluster-wide | Namespaced |
| Credential | Certificate, OIDC token, etc. | Projected JWT token |
| Typical consumer | Humans via kubectl | Pods and controllers |

### ServiceAccounts

Every namespace starts with a `default` service account. Pods that do not specify a service account use it automatically.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: build-agent
  namespace: ci
automountServiceAccountToken: false
```

Setting `automountServiceAccountToken: false` on the ServiceAccount (or on individual pod specs) prevents the token from being mounted at `/var/run/secrets/kubernetes.io/serviceaccount/token`. This is a best practice for pods that do not need to call the API server.

### Token Projection

Since Kubernetes 1.20+, the default token mount uses *bound service account token volumes* instead of long-lived secrets. These tokens are audience-bound, time-limited, and automatically rotated by the kubelet. You can explicitly configure projected volumes:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  serviceAccountName: build-agent
  containers:
    - name: app
      image: myapp:1.0
      volumeMounts:
        - name: token
          mountPath: /var/run/secrets/tokens
          readOnly: true
  volumes:
    - name: token
      projected:
        sources:
          - serviceAccountToken:
              audience: vault
              expirationSeconds: 3600
              path: vault-token
```

This gives the pod a short-lived token scoped to the `vault` audience, useful for integrating with external systems like HashiCorp Vault.

## Authorization (RBAC)

Role-Based Access Control is the standard authorization mode (`--authorization-mode=RBAC`). It uses four resource types to express permissions.

### The RBAC Model

- **Role** -- grants permissions within a single namespace.
- **ClusterRole** -- grants permissions cluster-wide or across all namespaces.
- **RoleBinding** -- binds a Role or ClusterRole to subjects within a namespace.
- **ClusterRoleBinding** -- binds a ClusterRole to subjects across the entire cluster.

### Role Specification

A Role lists rules. Each rule specifies API groups, resources, and the verbs allowed on those resources.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: development
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list"]
    resourceNames: ["frontend"]
```

Available verbs: `get`, `list`, `watch`, `create`, `update`, `patch`, `delete`, `deletecollection`. The `resourceNames` field optionally restricts the rule to specific named resources.

The `apiGroups` field identifies the API group: `""` for the core group (pods, services, configmaps), `"apps"` for deployments and statefulsets, `"batch"` for jobs and cronjobs, and so on.

### ClusterRole

ClusterRoles work like Roles but are not namespaced. They can also grant access to cluster-scoped resources (nodes, namespaces, persistent volumes) and non-resource URLs (`/healthz`, `/metrics`).

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: node-viewer
rules:
  - apiGroups: [""]
    resources: ["nodes"]
    verbs: ["get", "list", "watch"]
  - nonResourceURLs: ["/healthz", "/healthz/*"]
    verbs: ["get"]
```

#### Aggregation Rules

ClusterRoles can aggregate rules from other ClusterRoles using label selectors. The built-in `admin`, `edit`, and `view` ClusterRoles use this mechanism so that CRD authors can extend them.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring-view
  labels:
    rbac.authorization.k8s.io/aggregate-to-view: "true"
rules:
  - apiGroups: ["monitoring.coreos.com"]
    resources: ["prometheusrules", "servicemonitors"]
    verbs: ["get", "list", "watch"]
```

Because this ClusterRole carries the label `aggregate-to-view: "true"`, its rules are automatically merged into the built-in `view` ClusterRole.

### Built-in ClusterRoles

| ClusterRole | Description |
|---|---|
| `cluster-admin` | Superuser access to all resources in all namespaces. Equivalent to `*` on everything. |
| `admin` | Full access within a namespace (creates roles, rolebindings) but cannot modify the namespace itself or resource quotas. |
| `edit` | Read/write access to most resources in a namespace but cannot view or modify roles or rolebindings. |
| `view` | Read-only access to most resources in a namespace. Cannot view secrets (to prevent privilege escalation). |

### RoleBinding

A RoleBinding grants the permissions defined in a Role or ClusterRole to one or more subjects (users, groups, or service accounts) within a namespace.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: dev-pod-readers
  namespace: development
subjects:
  - kind: User
    name: alice
    apiGroup: rbac.authorization.k8s.io
  - kind: Group
    name: dev-team
    apiGroup: rbac.authorization.k8s.io
  - kind: ServiceAccount
    name: build-agent
    namespace: ci
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

A RoleBinding can reference a ClusterRole; doing so scopes that ClusterRole's permissions down to the binding's namespace. This is a common pattern for reusing a single ClusterRole across many namespaces.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: global-node-viewers
subjects:
  - kind: Group
    name: ops-team
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: node-viewer
  apiGroup: rbac.authorization.k8s.io
```

### RBAC Best Practices

- **Principle of least privilege.** Grant only the verbs and resources required. Avoid wildcards (`"*"`) except for cluster-admin scenarios.
- **Prefer namespace-scoped Roles.** Use ClusterRoles with RoleBindings per namespace rather than ClusterRoleBindings, which grant access everywhere.
- **Avoid binding cluster-admin broadly.** Audit all ClusterRoleBindings regularly.
- **Use groups, not individual users.** Map OIDC groups or certificate organizations to RoleBindings so that access changes do not require updating bindings.
- **Use `kubectl auth can-i` to verify.** `kubectl auth can-i create deployments --namespace production --as alice` tests permissions without making changes.

## Admission Controllers

After authentication and authorization succeed, admission controllers intercept the request before the object is persisted to etcd. They can mutate or validate (or reject) the object.

Admission controllers are compiled into the API server and enabled with `--enable-admission-plugins`. Common admission controllers include:

- **NamespaceLifecycle** -- prevents creation of objects in terminating or non-existent namespaces.
- **LimitRanger** -- enforces `LimitRange` constraints, injecting default CPU/memory requests and limits into pods that do not specify them.
- **ResourceQuota** -- enforces namespace-level resource quotas. Rejects requests that would exceed the quota.
- **ServiceAccount** -- injects the default service account and mounts the projected token volume.
- **PodSecurity** -- enforces Pod Security Standards (replaces the deprecated PodSecurityPolicy).
- **MutatingAdmissionWebhook** and **ValidatingAdmissionWebhook** -- call external webhook services for custom admission logic (used by tools like OPA/Gatekeeper, Kyverno, and Istio).

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: development
spec:
  limits:
    - default:
        cpu: "500m"
        memory: "256Mi"
      defaultRequest:
        cpu: "100m"
        memory: "128Mi"
      type: Container
```

## Pod Security

### Pod Security Standards

Kubernetes defines three security profiles, each progressively more restrictive:

- **Privileged** -- unrestricted. No policy is applied.
- **Baseline** -- prevents known privilege escalations (no host networking, no host PID, no privileged containers) while remaining broadly compatible.
- **Restricted** -- heavily locked down. Requires running as non-root, dropping all capabilities, read-only root filesystems encouraged, and seccomp profiles enforced.

### Pod Security Admission

Pod Security Admission (PSA) is a built-in admission controller (enabled by default since Kubernetes 1.25) that enforces Pod Security Standards at the namespace level. It operates in three modes:

| Mode | Behavior |
|---|---|
| `enforce` | Rejects pods that violate the policy. |
| `audit` | Allows the pod but writes a violation to the audit log. |
| `warn` | Allows the pod but returns a warning to the user. |

Configure PSA by labeling namespaces:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: v1.30
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

A common rollout strategy is to start with `warn` and `audit` on the `restricted` profile while keeping `enforce` at `baseline`, then tighten `enforce` to `restricted` once all workloads comply.

## Security Contexts

A security context configures privilege and access control settings for a pod or individual container. These fields are set under `spec.securityContext` (pod-level) and `spec.containers[].securityContext` (container-level).

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
  namespace: production
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
    runAsNonRoot: true
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: app
      image: myapp:1.0
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL
          add:
            - NET_BIND_SERVICE
      volumeMounts:
        - name: tmp
          mountPath: /tmp
  volumes:
    - name: tmp
      emptyDir: {}
```

Key fields explained:

- **runAsUser / runAsGroup** -- specifies the UID/GID the container process runs as.
- **runAsNonRoot** -- the kubelet validates at startup that the container is not running as UID 0 and rejects it if so.
- **readOnlyRootFilesystem** -- mounts the container's root filesystem as read-only. Writable paths must be explicitly provided via volume mounts (such as an `emptyDir` for `/tmp`).
- **capabilities** -- Linux capabilities to add or drop. The `restricted` Pod Security Standard requires dropping `ALL` and only allows adding `NET_BIND_SERVICE`.
- **allowPrivilegeEscalation** -- when `false`, the container cannot gain more privileges than its parent process (sets the `no_new_privs` flag).
- **seccompProfile** -- sets the seccomp (secure computing) profile. `RuntimeDefault` applies the container runtime's default filter. The `restricted` standard requires `RuntimeDefault` or `Localhost`.

## NetworkPolicies

By default, all pods can communicate with all other pods across all namespaces. NetworkPolicies are namespace-scoped resources that restrict traffic to and from pods. They require a CNI plugin that supports them (Calico, Cilium, Weave Net, Antrea). Note that Flannel does not support NetworkPolicies.

### Ingress and Egress Rules

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: monitoring
      ports:
        - protocol: TCP
          port: 8080
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: database
      ports:
        - protocol: TCP
          port: 5432
    - to:
        - ipBlock:
            cidr: 10.0.0.0/8
            except:
              - 10.0.1.0/24
      ports:
        - protocol: TCP
          port: 443
```

Important semantics: items within a single `from` or `to` array entry are ANDed together, while separate entries in the `from`/`to` list are ORed. In the ingress rule above, traffic is allowed from pods labeled `app: frontend` in the same namespace OR from any pod in the `monitoring` namespace.

### Default Deny Policies

A baseline security posture starts with denying all traffic, then explicitly allowing what is needed.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

An empty `podSelector` (`{}`) selects all pods in the namespace. Because no `ingress` or `egress` rules are specified, all traffic in both directions is denied. You then layer additional NetworkPolicies to open specific paths. Policies are additive: if any policy allows a connection, it is permitted.

### DNS Egress

When applying default-deny egress, pods lose DNS resolution. You must explicitly allow egress to the DNS service:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector: {}
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```

### CNI Requirements

NetworkPolicy enforcement depends entirely on the CNI plugin. The Kubernetes API server accepts NetworkPolicy resources regardless of whether a supporting CNI is installed, but without one, the policies have no effect. Widely used CNI plugins with NetworkPolicy support:

- **Calico** -- full NetworkPolicy support including global network policies (custom CRD) and DNS-based egress rules.
- **Cilium** -- eBPF-based, supports Kubernetes NetworkPolicy plus its own `CiliumNetworkPolicy` CRD with L7 (HTTP, gRPC) filtering.
- **Weave Net** -- supports standard Kubernetes NetworkPolicy.

## Secrets Management Best Practices

Kubernetes Secrets are base64-encoded (not encrypted) by default and stored in etcd. Treat them as a starting point, not a complete solution.

- **Enable encryption at rest.** Configure the API server with an `EncryptionConfiguration` resource that uses `aescbc`, `aesgcm`, or a KMS provider to encrypt Secret data in etcd.
- **Restrict Secret access via RBAC.** The built-in `view` ClusterRole intentionally excludes Secrets. Create explicit, narrowly scoped roles for any workload that needs Secret access.
- **Use external secret stores.** Tools like the Secrets Store CSI Driver, External Secrets Operator, or HashiCorp Vault inject secrets from external providers (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager) directly into pods as volumes, avoiding the need to store sensitive material in the Kubernetes API.
- **Avoid environment variable injection for secrets.** Prefer volume mounts over `env.valueFrom.secretKeyRef`, because environment variables can appear in crash dumps, logs, and process listings.
- **Rotate secrets regularly.** Use projected service account tokens with short `expirationSeconds`. For application secrets, adopt an operator or controller that handles rotation (e.g., External Secrets Operator with its refresh interval).
- **Audit Secret access.** Enable Kubernetes audit logging and monitor `get`, `list`, and `watch` operations on Secret resources to detect unexpected access patterns.
- **Do not commit secrets to version control.** Use sealed-secrets or SOPS to encrypt secrets before they enter Git. The decryption key stays in the cluster.
