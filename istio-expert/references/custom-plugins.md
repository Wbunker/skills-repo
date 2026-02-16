# Extending Istio with Custom Plugins

## Extension Mechanisms Overview

| Mechanism | Use Case | Complexity | Performance |
|-----------|----------|------------|-------------|
| **WasmPlugin** | Custom L7 logic (auth, headers, metrics) | Medium | Good (compiled Wasm) |
| **EnvoyFilter** | Direct Envoy config patching | High | Native (no overhead) |
| **ext_authz** | External authorization decisions | Low-Medium | Network call per request |
| **Rate Limit Service** | Global rate limiting | Medium | Network call per request |
| **Lua Filter** | Quick scripting (via EnvoyFilter) | Medium | Moderate |

**Recommendation**: Prefer WasmPlugin for new extensions. Use ext_authz for authorization. Avoid EnvoyFilter unless no alternative exists (it's fragile across Envoy upgrades).

## WasmPlugin CRD

```yaml
apiVersion: extensions.istio.io/v1alpha1
kind: WasmPlugin
metadata:
  name: custom-auth
  namespace: default
spec:
  selector:
    matchLabels:
      app: frontend
  url: oci://registry.example.com/istio-plugins/custom-auth:v1.0
  imagePullPolicy: IfNotPresent
  sha256: "abc123..."              # optional integrity check
  phase: AUTHN                     # when in filter chain to insert
  pluginConfig:                    # plugin-specific configuration
    api_key_header: "x-api-key"
    allowed_keys:
    - "key-123"
    - "key-456"
  match:
  - mode: SERVER                   # apply to inbound traffic
    ports:
    - number: 8080
```

### Phases

| Phase | Description | Order |
|-------|-------------|-------|
| `AUTHN` | Before Istio authn filters | First |
| `AUTHZ` | Before Istio authz filters | Second |
| `STATS` | Before Istio stats filters | Third |
| `UNSPECIFIED_PHASE` | Default position | After all Istio filters |

### Plugin Lifecycle

1. Plugin binary (`.wasm`) packaged as OCI image
2. Envoy downloads the Wasm module from registry
3. Module loaded into Envoy's Wasm VM (V8 or wasmtime)
4. Plugin receives callbacks for each request/response phase
5. Config updates trigger module reload without proxy restart

## Building Wasm Plugins

### proxy-wasm SDK

The [proxy-wasm](https://github.com/proxy-wasm) ABI is the standard interface. SDKs available for:

| Language | SDK | Binary Size | Best For |
|----------|-----|-------------|----------|
| **Rust** | proxy-wasm-rust-sdk | Small (~100KB) | Production, performance-critical |
| **Go** | proxy-wasm-go-sdk | Medium (~1-5MB) | Rapid development, Go teams |
| **C++** | proxy-wasm-cpp-sdk | Small | Maximum control |
| **AssemblyScript** | — | Small | TypeScript developers |

### Go Plugin Example

```go
package main

import (
    "github.com/tetratelabs/proxy-wasm-go-sdk/proxywasm"
    "github.com/tetratelabs/proxy-wasm-go-sdk/proxywasm/types"
)

func main() {
    proxywasm.SetVMContext(&vmContext{})
}

type vmContext struct {
    types.DefaultVMContext
}

func (*vmContext) NewPluginContext(contextID uint32) types.PluginContext {
    return &pluginContext{}
}

type pluginContext struct {
    types.DefaultPluginContext
    apiKeyHeader string
}

func (ctx *pluginContext) OnPluginStart(pluginConfigurationSize int) types.OnPluginStartStatus {
    // Read plugin configuration
    data, err := proxywasm.GetPluginConfiguration()
    if err != nil {
        proxywasm.LogCriticalf("failed to get plugin config: %v", err)
        return types.OnPluginStartStatusFailed
    }
    // Parse config (JSON)
    ctx.apiKeyHeader = "x-api-key" // simplified
    proxywasm.LogInfof("plugin started with config: %s", string(data))
    return types.OnPluginStartStatusOK
}

func (ctx *pluginContext) NewHttpContext(contextID uint32) types.HttpContext {
    return &httpContext{apiKeyHeader: ctx.apiKeyHeader}
}

type httpContext struct {
    types.DefaultHttpContext
    apiKeyHeader string
}

func (ctx *httpContext) OnHttpRequestHeaders(numHeaders int, endOfStream bool) types.Action {
    // Check for API key
    apiKey, err := proxywasm.GetHttpRequestHeader(ctx.apiKeyHeader)
    if err != nil || apiKey == "" {
        proxywasm.LogWarn("missing API key")
        proxywasm.SendHttpResponse(401, [][2]string{
            {"content-type", "application/json"},
        }, []byte(`{"error":"unauthorized"}`), -1)
        return types.ActionPause
    }

    // Add custom header
    proxywasm.AddHttpRequestHeader("x-validated", "true")
    return types.ActionContinue
}

func (ctx *httpContext) OnHttpResponseHeaders(numHeaders int, endOfStream bool) types.Action {
    proxywasm.AddHttpResponseHeader("x-powered-by", "custom-plugin")
    return types.ActionContinue
}
```

### Building and Deploying

```bash
# Build (Go)
tinygo build -o plugin.wasm -scheduler=none -target=wasi ./main.go

# Build (Rust)
cargo build --target wasm32-wasi --release

# Package as OCI image
docker build -t registry.example.com/plugins/my-plugin:v1 .
docker push registry.example.com/plugins/my-plugin:v1
```

**Dockerfile for OCI packaging:**
```dockerfile
FROM scratch
COPY plugin.wasm ./plugin.wasm
```

## EnvoyFilter

Direct Envoy configuration patching. **Use sparingly** — breaks easily across Envoy/Istio upgrades.

### Structure

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: custom-filter
  namespace: istio-system    # mesh-wide if in istio-system
spec:
  workloadSelector:          # optional: target specific workloads
    labels:
      app: my-app
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: SIDECAR_INBOUND
      listener:
        filterChain:
          filter:
            name: "envoy.filters.network.http_connection_manager"
            subFilter:
              name: "envoy.filters.http.router"
    patch:
      operation: INSERT_BEFORE
      value:
        name: envoy.filters.http.lua
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.http.lua.v3.Lua
          inline_code: |
            function envoy_on_request(handle)
              handle:headers():add("x-custom-header", "injected")
            end
```

### applyTo Targets

| Target | Description |
|--------|-------------|
| `CLUSTER` | Envoy cluster configuration |
| `LISTENER` | Listener configuration |
| `FILTER_CHAIN` | Filter chain within listener |
| `NETWORK_FILTER` | L4 network filter |
| `HTTP_FILTER` | L7 HTTP filter |
| `ROUTE_CONFIGURATION` | Route configuration |
| `VIRTUAL_HOST` | Virtual host within route config |
| `HTTP_ROUTE` | Individual route entry |

### Patch Operations

| Operation | Description |
|-----------|-------------|
| `ADD` | Add new element |
| `REMOVE` | Remove matching element |
| `INSERT_BEFORE` | Insert before matched filter |
| `INSERT_AFTER` | Insert after matched filter |
| `INSERT_FIRST` | Insert at beginning |
| `MERGE` | Merge into existing config |
| `REPLACE` | Replace existing config |

### Common EnvoyFilter Patterns

**Add custom response header:**
```yaml
configPatches:
- applyTo: HTTP_ROUTE
  match:
    context: SIDECAR_INBOUND
  patch:
    operation: MERGE
    value:
      response_headers_to_add:
      - header:
          key: "x-envoy-decorator"
          value: "my-service"
        append: true
```

**Local rate limiting:**
```yaml
configPatches:
- applyTo: HTTP_FILTER
  match:
    context: SIDECAR_INBOUND
    listener:
      filterChain:
        filter:
          name: "envoy.filters.network.http_connection_manager"
          subFilter:
            name: "envoy.filters.http.router"
  patch:
    operation: INSERT_BEFORE
    value:
      name: envoy.filters.http.local_ratelimit
      typed_config:
        "@type": type.googleapis.com/envoy.extensions.filters.http.local_ratelimit.v3.LocalRateLimit
        stat_prefix: http_local_rate_limiter
        token_bucket:
          max_tokens: 100
          tokens_per_fill: 100
          fill_interval: 60s
        filter_enabled:
          runtime_key: local_rate_limit_enabled
          default_value:
            numerator: 100
            denominator: HUNDRED
        filter_enforced:
          runtime_key: local_rate_limit_enforced
          default_value:
            numerator: 100
            denominator: HUNDRED
```

## External Authorization (ext_authz)

### Architecture

```
Client → Envoy → ext_authz service → Allow/Deny → Envoy → Upstream
```

### Configure Provider in MeshConfig

```yaml
meshConfig:
  extensionProviders:
  - name: "my-ext-authz-grpc"
    envoyExtAuthzGrpc:
      service: "ext-authz.auth.svc.cluster.local"
      port: 9000
      timeout: 500ms
      failOpen: false        # deny on authz service failure
      statusOnError: "503"
  - name: "my-ext-authz-http"
    envoyExtAuthzHttp:
      service: "ext-authz-http.auth.svc.cluster.local"
      port: 8080
      includeRequestHeadersInCheck:
      - "authorization"
      - "x-forwarded-for"
      headersToUpstreamOnAllow:
      - "x-auth-user"
      headersToDownstreamOnDeny:
      - "x-auth-error"
```

### Apply via AuthorizationPolicy

```yaml
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: ext-authz-policy
spec:
  selector:
    matchLabels:
      app: protected-api
  action: CUSTOM
  provider:
    name: my-ext-authz-grpc
  rules:
  - to:
    - operation:
        paths: ["/api/*"]
        notPaths: ["/api/health"]   # skip health checks
```

### OPA (Open Policy Agent) Integration

Deploy OPA as the ext_authz gRPC server:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: opa-ext-authz
  namespace: auth
spec:
  template:
    spec:
      containers:
      - name: opa
        image: openpolicyagent/opa:latest-envoy
        args:
        - "run"
        - "--server"
        - "--addr=0.0.0.0:8181"
        - "--set=plugins.envoy_ext_authz_grpc.addr=:9000"
        - "--set=decision_logs.console=true"
        - "/policies"
        volumeMounts:
        - name: policy
          mountPath: /policies
      volumes:
      - name: policy
        configMap:
          name: opa-policy
```

## Rate Limit Service

### Architecture

```
Client → Envoy → Rate Limit Service (check) → Allow/Limit → Envoy → Upstream
         ↕                    ↕
       Descriptors        Redis/Memcached
```

### Deployment

Deploy the [Envoy rate limit service](https://github.com/envoyproxy/ratelimit):

```yaml
# Rate limit config
domain: my-ratelimit
descriptors:
  - key: header_match
    value: api-route
    rate_limit:
      unit: minute
      requests_per_unit: 100
  - key: remote_address
    rate_limit:
      unit: second
      requests_per_unit: 10
```

### Configure via MeshConfig + EnvoyFilter

```yaml
meshConfig:
  extensionProviders:
  - name: "my-ratelimit"
    envoyRatelimit:
      service: "ratelimit.ratelimit.svc.cluster.local"
      port: 8081
```

## Lua Filters

Quick scripting via EnvoyFilter (no compilation required):

```yaml
configPatches:
- applyTo: HTTP_FILTER
  match:
    context: SIDECAR_INBOUND
    listener:
      filterChain:
        filter:
          name: "envoy.filters.network.http_connection_manager"
          subFilter:
            name: "envoy.filters.http.router"
  patch:
    operation: INSERT_BEFORE
    value:
      name: envoy.filters.http.lua
      typed_config:
        "@type": type.googleapis.com/envoy.extensions.filters.http.lua.v3.Lua
        inline_code: |
          function envoy_on_request(request_handle)
            local path = request_handle:headers():get(":path")
            request_handle:logInfo("Request path: " .. path)

            -- Add timestamp header
            request_handle:headers():add(
              "x-request-timestamp",
              os.date("!%Y-%m-%dT%H:%M:%SZ")
            )
          end

          function envoy_on_response(response_handle)
            response_handle:headers():add("x-lua-processed", "true")
          end
```

**Lua vs Wasm trade-offs:**
- Lua: simpler, no build step, limited API, worse performance for complex logic
- Wasm: compiled, full proxy-wasm API, better performance, requires build toolchain

## Plugin Development Best Practices

### Performance

- Wasm plugins add ~1-2ms latency per plugin in the filter chain
- ext_authz adds network round-trip latency (configure timeout carefully)
- Use `failOpen: true` for non-critical checks to avoid cascading failures
- Cache authorization decisions where possible

### Testing

```bash
# Test WasmPlugin with local Envoy
func-e run -c envoy.yaml  # func-e manages Envoy binaries

# Verify plugin is loaded
istioctl proxy-config log <pod> --level wasm:debug
kubectl logs <pod> -c istio-proxy | grep "wasm"

# Check EnvoyFilter application
istioctl proxy-config dump <pod> | grep "custom-filter"
```

### Rollout Strategy

1. Deploy plugin to a single test workload first
2. Monitor error rates and latency
3. Gradually expand to more workloads
4. Use `match` selectors to limit scope during rollout

### Versioning

- Tag OCI images with semantic versions
- Use `sha256` field for integrity verification
- Test new plugin versions alongside old ones using workload selectors
