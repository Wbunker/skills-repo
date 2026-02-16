# Working with Helm Charts

Helm is the package manager for Kubernetes. It packages related Kubernetes manifests into a single unit called a **chart**, which can be versioned, shared, and deployed as a cohesive **release**. Where raw manifests require you to manage each resource individually, Helm treats an entire application stack as one installable, upgradeable, and rollback-capable artifact.

## Core Concepts

A **chart** is a collection of files that describe a set of Kubernetes resources. A **release** is a running instance of a chart deployed into a cluster. The same chart can be installed multiple times, each producing an independent release with its own name. A **repository** is an HTTP server (or OCI registry) that hosts packaged charts for distribution.

Helm stores release metadata as Secrets (default) or ConfigMaps in the namespace where the release is deployed. There is no server-side component; the Helm CLI communicates directly with the Kubernetes API server using your kubeconfig credentials.

## Helm Architecture

The Helm client is a single binary that handles chart development, repository management, release lifecycle operations, and interfacing with the Kubernetes API. When you run `helm install`, the client renders templates locally by merging the chart templates with the supplied values, then sends the resulting manifests to the API server. Release history is tracked through versioned Secrets in the target namespace, enabling upgrade and rollback operations without any cluster-side controller.

## Repository Management

Repositories are the primary distribution mechanism for charts.

```bash
# Add a repository and give it a local alias
helm repo add bitnami https://charts.bitnami.com/bitnami

# Add a repository that requires authentication
helm repo add private-repo https://charts.example.com --username admin --password secret

# Refresh local cache of all configured repositories
helm repo update

# List configured repositories
helm repo list

# Remove a repository
helm repo remove bitnami
```

## Searching for Charts

```bash
# Search across all configured repositories (local index)
helm search repo nginx

# Search with version constraints
helm search repo nginx --version ">=13.0.0"

# Show all available versions, not just the latest
helm search repo nginx --versions

# Search Artifact Hub (public aggregator of Helm repositories)
helm search hub wordpress
```

## Inspecting Charts Before Installation

The `helm show` commands let you examine a chart without installing it.

```bash
# Display the full values.yaml with all configurable defaults
helm show values bitnami/nginx

# Display Chart.yaml metadata
helm show chart bitnami/nginx

# Display the README
helm show readme bitnami/nginx

# Display everything at once
helm show all bitnami/nginx
```

## Installing and Managing Releases

### Install

```bash
# Install with a specified release name
helm install my-nginx bitnami/nginx

# Generate a release name automatically
helm install bitnami/nginx --generate-name

# Install into a specific namespace, creating it if needed
helm install my-nginx bitnami/nginx -n web --create-namespace

# Override values inline
helm install my-nginx bitnami/nginx --set replicaCount=3 --set service.type=ClusterIP

# Override values from a file
helm install my-nginx bitnami/nginx -f production-values.yaml

# Perform a dry run to see rendered manifests without applying
helm install my-nginx bitnami/nginx --dry-run

# Wait for all resources to become ready before marking the release as deployed
helm install my-nginx bitnami/nginx --wait --timeout 5m
```

### Upgrade

Upgrades apply a new version of the chart or new values to an existing release. Each upgrade increments the release revision number.

```bash
# Upgrade to a new chart version
helm upgrade my-nginx bitnami/nginx --version 15.1.0

# Upgrade with new values, reusing values from the previous release for anything not specified
helm upgrade my-nginx bitnami/nginx --reuse-values --set replicaCount=5

# Upgrade or install if the release does not exist
helm upgrade --install my-nginx bitnami/nginx -f production-values.yaml
```

### Rollback

```bash
# Roll back to the previous revision
helm rollback my-nginx

# Roll back to a specific revision number
helm rollback my-nginx 2
```

### Uninstall

```bash
# Remove a release and all its Kubernetes resources
helm uninstall my-nginx

# Uninstall but keep release history for auditing
helm uninstall my-nginx --keep-history
```

## Querying Release State

```bash
# List all releases in the current namespace
helm list

# List across all namespaces
helm list -A

# Include releases in failed or pending states
helm list --all

# Show detailed status of a specific release
helm status my-nginx

# Show revision history
helm history my-nginx

# Retrieve the computed values for the current release
helm get values my-nginx

# Retrieve all values including defaults
helm get values my-nginx --all

# Retrieve the rendered manifests that were sent to the cluster
helm get manifest my-nginx

# Retrieve the post-install notes
helm get notes my-nginx
```

## Local Template Rendering

`helm template` renders chart templates locally without any cluster interaction. This is invaluable for debugging, CI pipelines, and generating manifests for GitOps workflows.

```bash
# Render templates to stdout
helm template my-nginx bitnami/nginx -f production-values.yaml

# Render and write to a file
helm template my-nginx bitnami/nginx -f production-values.yaml > rendered.yaml

# Render only specific templates
helm template my-nginx bitnami/nginx -s templates/deployment.yaml

# Validate rendered output against the Kubernetes API schema
helm template my-nginx bitnami/nginx --validate
```

## Chart Structure

A chart is a directory with a prescribed layout.

```
mychart/
  Chart.yaml          # Chart metadata (required)
  Chart.lock          # Locked dependency versions
  values.yaml         # Default configuration values
  charts/             # Dependency charts (subcharts)
  crds/               # Custom Resource Definitions
  templates/          # Go template files
    deployment.yaml
    service.yaml
    ingress.yaml
    _helpers.tpl      # Partial templates (named templates)
    NOTES.txt         # Post-install usage instructions
  .helmignore         # Patterns to exclude from packaging
```

### Chart.yaml

```yaml
apiVersion: v2
name: myapp
description: A web application chart
type: application          # "application" (default) or "library"
version: 1.2.0             # Chart version, follows SemVer
appVersion: "3.4.1"        # Version of the application being deployed
kubeVersion: ">=1.25.0"    # Optional constraint on Kubernetes versions
dependencies:
  - name: postgresql
    version: "12.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
    tags:
      - database
  - name: redis
    version: "17.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
```

The `type` field distinguishes between **application** charts (which produce Kubernetes resources) and **library** charts (which provide reusable template helpers to other charts but produce no resources on their own).

### values.yaml

This file defines the complete set of configurable parameters and their defaults. Any key here is accessible in templates through the `.Values` object.

```yaml
replicaCount: 2
image:
  repository: nginx
  tag: "1.25"
  pullPolicy: IfNotPresent
service:
  type: ClusterIP
  port: 80
ingress:
  enabled: false
  className: nginx
  hosts:
    - host: app.example.com
      paths:
        - path: /
          pathType: Prefix
resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi
postgresql:
  enabled: true
redis:
  enabled: false
```

### CRDs Directory

Files placed in `crds/` are applied before any templates during installation. They are never re-applied on upgrades and are never deleted on uninstall. This is by design: CRDs are cluster-scoped and their lifecycle should be managed deliberately. If you need more control over CRD lifecycle, manage them outside the chart or use hooks.

## Templating

Helm templates use Go's `text/template` package augmented by the Sprig function library and several Helm-specific extensions.

### Built-in Objects

| Object | Description |
|---|---|
| `.Values` | Merged values from values.yaml, parent charts, -f files, and --set flags |
| `.Release.Name` | Name of the release |
| `.Release.Namespace` | Target namespace |
| `.Release.Revision` | Current revision number (starts at 1) |
| `.Release.IsUpgrade` | True if this is an upgrade operation |
| `.Release.IsInstall` | True if this is an install operation |
| `.Chart.Name` | Chart name from Chart.yaml |
| `.Chart.Version` | Chart version from Chart.yaml |
| `.Chart.AppVersion` | Application version from Chart.yaml |
| `.Capabilities.KubeVersion` | Kubernetes version of the target cluster |
| `.Capabilities.APIVersions` | Available API versions in the cluster |
| `.Template.Name` | Path of the current template file |
| `.Template.BasePath` | Path of the templates directory |

### Basic Syntax

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-{{ .Chart.Name }}
  labels:
    app.kubernetes.io/name: {{ .Chart.Name }}
    app.kubernetes.io/instance: {{ .Release.Name }}
    app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ .Chart.Name }}
      app.kubernetes.io/instance: {{ .Release.Name }}
  template:
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          ports:
            - containerPort: {{ .Values.service.port }}
```

### Control Structures

```yaml
# Conditional blocks
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ .Release.Name }}-ingress
spec:
  ingressClassName: {{ .Values.ingress.className }}
  rules:
    {{- range .Values.ingress.hosts }}
    - host: {{ .host }}
      http:
        paths:
          {{- range .paths }}
          - path: {{ .path }}
            pathType: {{ .pathType }}
            backend:
              service:
                name: {{ $.Release.Name }}-svc
                port:
                  number: {{ $.Values.service.port }}
          {{- end }}
    {{- end }}
{{- end }}

# with narrows scope
{{- with .Values.resources }}
resources:
  {{- toYaml . | nindent 2 }}
{{- end }}

# if/else
{{- if eq .Values.service.type "NodePort" }}
  nodePort: {{ .Values.service.nodePort }}
{{- else if eq .Values.service.type "LoadBalancer" }}
  loadBalancerIP: {{ .Values.service.loadBalancerIP | default "" }}
{{- end }}
```

Note that inside a `range` or `with` block, `.` refers to the current element. Use `$` to access the root scope (`$.Values`, `$.Release`, etc.).

### Key Template Functions

```yaml
# default provides a fallback when a value is empty or unset
image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"

# quote wraps the value in double quotes (essential for strings that look like numbers or booleans)
version: {{ .Chart.AppVersion | quote }}

# toYaml converts a data structure to YAML text
# nindent adds a newline then indents by N spaces; indent adds spaces without a leading newline
{{- with .Values.podAnnotations }}
annotations:
  {{- toYaml . | nindent 4 }}
{{- end }}

# tpl renders a string as a template, useful for values that contain template expressions
annotations:
  checksum/config: {{ tpl .Values.configTemplate . }}

# required fails rendering with a message if the value is empty
{{ required "A valid .Values.database.host is required" .Values.database.host }}

# ternary provides inline conditional values
readOnly: {{ ternary "true" "false" .Values.readOnlyRootFilesystem }}

# lookup queries live cluster resources during rendering (no-op during helm template)
{{- if (lookup "v1" "Secret" .Release.Namespace "my-secret") }}
# Secret already exists
{{- end }}
```

### Named Templates and _helpers.tpl

Named templates defined with `define` are conventionally placed in `_helpers.tpl`. Files starting with `_` are not rendered as manifests.

```yaml
# templates/_helpers.tpl
{{- define "myapp.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{- define "myapp.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "myapp.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

Use `include` (not `template`) to invoke named templates because `include` returns the output as a string that can be piped through functions.

```yaml
metadata:
  name: {{ include "myapp.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
spec:
  selector:
    matchLabels:
      {{- include "myapp.selectorLabels" . | nindent 6 }}
```

### NOTES.txt

The `templates/NOTES.txt` file is a template that Helm renders and displays after install or upgrade. It typically provides connection instructions.

```
Your application has been deployed.

To access it:
{{- if eq .Values.service.type "LoadBalancer" }}
  export SERVICE_IP=$(kubectl get svc {{ include "myapp.fullname" . }} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
  echo http://$SERVICE_IP:{{ .Values.service.port }}
{{- else if eq .Values.service.type "ClusterIP" }}
  kubectl port-forward svc/{{ include "myapp.fullname" . }} 8080:{{ .Values.service.port }}
  echo http://127.0.0.1:8080
{{- end }}
```

## Values Precedence

When multiple value sources exist, Helm merges them with the following precedence (highest wins):

1. `--set` and `--set-string` flags on the command line
2. `-f` / `--values` files (last file wins if multiple are specified)
3. Parent chart's values.yaml (when deploying a subchart)
4. The chart's own `values.yaml` defaults

```bash
# Layered value files with targeted overrides
helm install myapp ./mychart \
  -f values-common.yaml \
  -f values-production.yaml \
  --set image.tag=v2.1.0
```

Nested values are set with dot notation. List items and complex types use special syntax.

```bash
--set ingress.hosts[0].host=app.example.com
--set ingress.hosts[0].paths[0].path=/
--set nodeSelector."kubernetes\.io/os"=linux
```

## Dependencies

Dependencies are declared in `Chart.yaml` and downloaded into the `charts/` directory.

```bash
# Download dependencies defined in Chart.yaml into charts/
helm dependency update ./mychart

# List current dependency status
helm dependency list ./mychart

# Rebuild Chart.lock after modifying Chart.yaml
helm dependency build ./mychart
```

Dependencies can be conditionally enabled with `condition` or `tags`.

```yaml
# In Chart.yaml
dependencies:
  - name: postgresql
    version: "12.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled    # Single boolean value path
    tags:
      - database                     # Enable/disable groups of dependencies
```

```yaml
# In values.yaml
postgresql:
  enabled: true

tags:
  database: true
```

The `condition` field takes precedence over `tags`. Subchart values are passed under a key matching the dependency name (e.g., `postgresql.auth.postgresPassword`).

## Hooks

Hooks let you run Kubernetes resources (typically Jobs or Pods) at specific points in the release lifecycle.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ .Release.Name }}-db-migrate
  annotations:
    "helm.sh/hook": pre-upgrade,pre-install
    "helm.sh/hook-weight": "-5"           # Lower weights run first
    "helm.sh/hook-delete-policy": before-hook-creation
spec:
  template:
    spec:
      containers:
        - name: migrate
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          command: ["./migrate", "--apply"]
      restartPolicy: Never
```

### Available Hook Points

| Hook | When It Runs |
|---|---|
| `pre-install` | After templates are rendered, before any resources are created |
| `post-install` | After all resources are created |
| `pre-upgrade` | After templates are rendered, before any resources are updated |
| `post-upgrade` | After all resources are updated |
| `pre-delete` | Before any resources are deleted during uninstall |
| `post-delete` | After all resources are deleted during uninstall |
| `pre-rollback` | After templates are rendered, before rollback is applied |
| `post-rollback` | After rollback is complete |
| `test` | Invoked by `helm test` |

### Hook Delete Policies

| Policy | Behavior |
|---|---|
| `before-hook-creation` | Delete the previous hook resource before launching the new one (default) |
| `hook-succeeded` | Delete the hook resource after it succeeds |
| `hook-failed` | Delete the hook resource if it fails |

Multiple hooks can share the same hook point. The `hook-weight` annotation (a string representing a number) controls execution order. Hooks with lower weights run first. Helm waits for each hook to reach a ready state before proceeding.

## Creating a Chart

```bash
# Scaffold a new chart with sensible defaults
helm create myapp
```

This generates a complete chart directory with a Deployment, Service, ServiceAccount, Ingress, and HPA pre-configured with best-practice templating patterns. The generated `_helpers.tpl` provides standard label and name helpers.

### Best Practices

**Naming**: Use `include "mychart.fullname"` for resource names so they are unique per release. Truncate to 63 characters to satisfy Kubernetes naming limits.

**Labels**: Apply the standard Kubernetes recommended labels (`app.kubernetes.io/name`, `app.kubernetes.io/instance`, `app.kubernetes.io/version`, `app.kubernetes.io/managed-by`) to all resources.

**Documentation**: Document every value in `values.yaml` with comments. Users rely on this as the primary configuration reference.

**Immutability**: Make Deployments roll on config changes by including a checksum annotation:

```yaml
annotations:
  checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
```

**Testing**: Use `helm lint` to catch template errors, `helm template` to verify rendered output, and `helm test` with hook-based test pods to validate deployed releases.

```bash
helm lint ./mychart
helm lint ./mychart -f production-values.yaml
```

**Packaging and distribution**:

```bash
# Package a chart into a .tgz archive
helm package ./mychart

# Push to an OCI-compatible registry
helm push mychart-1.2.0.tgz oci://registry.example.com/charts
```

## Helm vs Kustomize

Helm and Kustomize solve overlapping but distinct problems. They can also be used together.

| Aspect | Helm | Kustomize |
|---|---|---|
| Approach | Templating with Go templates | Patching plain YAML via overlays |
| Packaging | Charts are versioned, distributable packages | No packaging; works with directories of manifests |
| Configuration | Parameterized through values.yaml | Strategic merge patches and JSON patches |
| Lifecycle | Full release management: install, upgrade, rollback, uninstall, history | No release concept; applies manifests directly |
| Complexity | More powerful but steeper learning curve; template debugging can be opaque | Simpler mental model; what you see is closer to what you get |
| Ecosystem | Large public chart ecosystem via Artifact Hub and OCI registries | Built into kubectl (`kubectl apply -k`); no external tooling required |
| Best fit | Distributing reusable applications with many configuration knobs | Customizing manifests for different environments with minimal abstraction |

In practice, many teams use Helm for third-party application deployment (databases, monitoring stacks, ingress controllers) and Kustomize for internal applications where the team controls all manifests directly. Some workflows render Helm charts with `helm template` and then apply Kustomize overlays on top, combining the distribution benefits of Helm with the patch-based customization of Kustomize.
