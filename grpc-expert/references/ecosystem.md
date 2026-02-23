# The gRPC Ecosystem

## Table of Contents
- [gRPC Gateway](#grpc-gateway)
- [HTTP/JSON Transcoding](#httpjson-transcoding)
- [gRPC Server Reflection](#grpc-server-reflection)
- [gRPC Middleware](#grpc-middleware)
- [Health Checking Protocol](#health-checking-protocol)
- [Ecosystem Tools and Projects](#ecosystem-tools-and-projects)

## gRPC Gateway

A reverse proxy that translates RESTful HTTP/JSON requests into gRPC calls. Serves both gRPC clients (internal microservices) and REST clients (browsers, mobile, third parties) from a single service implementation.

### Proto Annotations for HTTP Mapping

```protobuf
syntax = "proto3";
package ecommerce;
import "google/api/annotations.proto";

service ProductService {
  rpc GetProduct(GetProductRequest) returns (Product) {
    option (google.api.http) = { get: "/v1/products/{id}" };
  }
  rpc AddProduct(Product) returns (Product) {
    option (google.api.http) = { post: "/v1/products" body: "*" };
  }
  rpc UpdateProduct(UpdateProductRequest) returns (Product) {
    option (google.api.http) = { put: "/v1/products/{product.id}" body: "product" };
  }
  rpc ListProducts(ListProductsRequest) returns (ListProductsResponse) {
    option (google.api.http) = { get: "/v1/products" };
  }
}

message GetProductRequest { string id = 1; }
message ListProductsRequest {
  int32 page_size = 1;    // mapped from query param ?page_size=10
  string page_token = 2;  // mapped from query param ?page_token=abc
}
message UpdateProductRequest { Product product = 1; }
```

**Mapping rules**: `{field}` in the URL path binds to a request field. `body: "*"` maps the entire JSON body to the request message. `body: "field"` maps a specific sub-field. Any fields not in the path or body are automatically mapped from query parameters. Use `additional_bindings` for multiple HTTP routes to one RPC.

### Generating and Running the Gateway

```bash
# Install plugins
go install github.com/grpc-ecosystem/grpc-gateway/v2/protoc-gen-grpc-gateway@latest
go install github.com/grpc-ecosystem/grpc-gateway/v2/protoc-gen-openapiv2@latest

# Generate gateway code and OpenAPI spec
protoc -I . -I ./google/api \
  --go_out=. --go_opt=paths=source_relative \
  --go-grpc_out=. --go-grpc_opt=paths=source_relative \
  --grpc-gateway_out=. --grpc-gateway_opt=paths=source_relative \
  --openapiv2_out=./docs \
  proto/product.proto
```

Run the gateway alongside the gRPC server:

```go
func main() {
    // gRPC server on :50051
    lis, _ := net.Listen("tcp", ":50051")
    grpcServer := grpc.NewServer()
    pb.RegisterProductServiceServer(grpcServer, &productServer{})
    go grpcServer.Serve(lis)

    // HTTP gateway on :8080, proxying to gRPC
    ctx := context.Background()
    mux := runtime.NewServeMux()
    opts := []grpc.DialOption{grpc.WithTransportCredentials(insecure.NewCredentials())}
    pb.RegisterProductServiceHandlerFromEndpoint(ctx, mux, "localhost:50051", opts)
    http.ListenAndServe(":8080", mux)
}
```

REST clients call `GET http://localhost:8080/v1/products/123` and the gateway translates to a gRPC `GetProduct` call. The `protoc-gen-openapiv2` plugin generates OpenAPI v2 (Swagger) specs from the same annotations.

## HTTP/JSON Transcoding

### Envoy gRPC-JSON Transcoder

Envoy can transcode HTTP/JSON to gRPC at the edge without generated code. Provide a compiled proto descriptor:

```bash
protoc --include_imports --include_source_info --descriptor_set_out=proto.pb proto/product.proto
```

```yaml
http_filters:
  - name: envoy.filters.http.grpc_json_transcoder
    typed_config:
      "@type": type.googleapis.com/envoy.extensions.filters.http.grpc_json_transcoder.v3.GrpcJsonTranscoder
      proto_descriptor: "/etc/envoy/proto.pb"
      services: ["ecommerce.ProductService"]
      print_options:
        always_print_primitive_fields: true
  - name: envoy.filters.http.router
```

The upstream cluster must use HTTP/2 (`http2_protocol_options`).

### Connect Protocol

**Connect** (from Buf) is a gRPC-compatible framework that works natively over HTTP/1.1 and HTTP/2. A single handler serves three wire protocols: Connect, gRPC, and gRPC-Web.

```go
mux := http.NewServeMux()
path, handler := ecommercev1connect.NewProductServiceHandler(&ProductServer{})
mux.Handle(path, handler)
http.ListenAndServe(":8080", h2c.NewHandler(mux, &http2.Server{}))
```

No gateway needed -- plain `curl` works:

```bash
curl -H "Content-Type: application/json" \
  -d '{"id":"123"}' http://localhost:8080/ecommerce.v1.ProductService/GetProduct
```

`connect-web` provides TypeScript browser clients that communicate directly without gRPC-Web proxies. Google Cloud Endpoints and Cloud Run also provide built-in gRPC transcoding using the same `google.api.http` annotations.

## gRPC Server Reflection

Runtime service discovery allowing clients to query which services, methods, and message types a server exposes -- without needing `.proto` files.

### Enabling and Using Reflection

```go
import "google.golang.org/grpc/reflection"

server := grpc.NewServer()
pb.RegisterProductServiceServer(server, &productServer{})
reflection.Register(server)  // enable reflection
```

Use with `grpcurl` (no proto files needed):

```bash
grpcurl -plaintext localhost:50051 list                              # list services
grpcurl -plaintext localhost:50051 describe ecommerce.ProductService # describe service
grpcurl -plaintext -d '{"id":"123"}' localhost:50051 \
  ecommerce.ProductService/GetProduct                                # invoke RPC
```

**Security**: reflection exposes your full API surface. Disable in production or restrict to internal ports:

```go
if os.Getenv("ENABLE_REFLECTION") == "true" {
    reflection.Register(server)
}
```

## gRPC Middleware

### Interceptor Chains

Go gRPC v1.66+ supports native chaining. For older versions, use `go-grpc-middleware`:

```go
server := grpc.NewServer(
    grpc.ChainUnaryInterceptor(
        grpc_ctxtags.UnaryServerInterceptor(),
        grpc_zap.UnaryServerInterceptor(zapLogger),
        grpc_recovery.UnaryServerInterceptor(),
        grpc_auth.UnaryServerInterceptor(authFunc),
    ),
    grpc.ChainStreamInterceptor(
        grpc_zap.StreamServerInterceptor(zapLogger),
        grpc_recovery.StreamServerInterceptor(),
    ),
)
```

### Common Middleware

| Middleware | Package | Purpose |
|---|---|---|
| Logging (zap) | `grpc_zap` | Structured logging with zap |
| Logging (logrus) | `grpc_logrus` | Structured logging with logrus |
| Recovery | `grpc_recovery` | Recover from panics, return `INTERNAL` |
| Auth | `grpc_auth` | Extract/validate tokens from metadata |
| Retry | `grpc_retry` | Client-side automatic retry with backoff |
| Rate limiting | `grpc_ratelimit` | Server-side rate limiting |
| Validation | `grpc_validator` | Message validation (with `protoc-gen-validate`) |
| Prometheus | `grpc_prometheus` | Metrics export |
| OpenTelemetry | `otelgrpc` | Distributed tracing |

### Custom Middleware

```go
func timingInterceptor(ctx context.Context, req interface{},
    info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
    start := time.Now()
    resp, err := handler(ctx, req)  // call the actual handler
    log.Printf("RPC %s: %s, err=%v", info.FullMethod, time.Since(start), err)
    return resp, err
}

// Custom auth function for grpc_auth
func authFunc(ctx context.Context) (context.Context, error) {
    token, err := grpc_auth.AuthFromMD(ctx, "bearer")
    if err != nil {
        return nil, err
    }
    claims, err := validateToken(token)
    if err != nil {
        return nil, status.Errorf(codes.Unauthenticated, "invalid token")
    }
    return context.WithValue(ctx, "claims", claims), nil
}
```

## Health Checking Protocol

The standard `grpc.health.v1.Health` service provides a uniform way for load balancers and orchestrators to verify service availability.

### States

| State | Meaning |
|---|---|
| `UNKNOWN` | Status not yet set |
| `SERVING` | Healthy, accepting requests |
| `NOT_SERVING` | Unhealthy or shutting down |
| `SERVICE_UNKNOWN` | Requested service name not registered |

### Implementation in Go

```go
import (
    "google.golang.org/grpc/health"
    "google.golang.org/grpc/health/grpc_health_v1"
)

healthServer := health.NewServer()
grpc_health_v1.RegisterHealthServer(server, healthServer)

// Set overall server health (empty string = whole server)
healthServer.SetServingStatus("", grpc_health_v1.HealthCheckResponse_SERVING)

// Per-service health
healthServer.SetServingStatus("ecommerce.ProductService",
    grpc_health_v1.HealthCheckResponse_SERVING)

// On shutdown: healthServer.Shutdown() sets all to NOT_SERVING
```

### grpc-health-probe

```bash
grpc-health-probe -addr=localhost:50051
grpc-health-probe -addr=localhost:50051 -service="ecommerce.ProductService"
grpc-health-probe -addr=localhost:50051 -tls -tls-ca-cert=ca.pem
```

Exit code `0` = `SERVING`, non-zero = unhealthy or unreachable.

### Kubernetes Integration

Native gRPC probes (Kubernetes 1.24+):

```yaml
containers:
  - name: product-service
    ports:
      - containerPort: 50051
    livenessProbe:
      grpc:
        port: 50051
      initialDelaySeconds: 10
      periodSeconds: 10
    readinessProbe:
      grpc:
        port: 50051
        service: "ecommerce.ProductService"
      initialDelaySeconds: 5
      periodSeconds: 5
```

For older clusters, use exec with `grpc-health-probe`:

```yaml
livenessProbe:
  exec:
    command: ["/bin/grpc-health-probe", "-addr=:50051"]
```

## Ecosystem Tools and Projects

### buf: Modern Protobuf Toolchain

Replaces `protoc` with linting, breaking change detection, code generation, and the Buf Schema Registry (BSR).

```yaml
# buf.yaml
version: v2
modules:
  - path: proto
lint:
  use: [STANDARD]
breaking:
  use: [FILE]
```

```yaml
# buf.gen.yaml
version: v2
plugins:
  - remote: buf.build/protocolbuffers/go
    out: gen/go
    opt: paths=source_relative
  - remote: buf.build/grpc/go
    out: gen/go
    opt: paths=source_relative
```

```bash
buf lint                                      # lint proto files
buf breaking --against '.git#branch=main'     # detect breaking changes
buf generate                                  # generate code
buf push                                      # push to BSR
```

### CLI and GUI Clients

- **Evans**: interactive gRPC REPL (`evans --reflection repl -p 50051`)
- **Kreya**: GUI gRPC client with all four patterns, TLS, metadata
- **Postman**: gRPC support via proto import or reflection

### gRPC-Web

Enables browser clients to call gRPC services. Requires a proxy (Envoy with `envoy.filters.http.grpc_web`, or the Go gRPC-Web proxy) because browsers cannot use HTTP/2 trailers. The Connect protocol (`connect-web`) is increasingly preferred as it works without a special proxy.

### Service Mesh Integration

Istio, Linkerd, and Envoy provide first-class gRPC support: per-request L7 load balancing (critical because HTTP/2 multiplexes all RPCs over one connection), transparent mTLS, automatic metrics/tracing, method-level routing, and retry policies with gRPC status code awareness.

### Well-Known Types

| Type | Import | Purpose |
|---|---|---|
| `Timestamp` | `google/protobuf/timestamp.proto` | Point in time |
| `Duration` | `google/protobuf/duration.proto` | Span of time |
| `Empty` | `google/protobuf/empty.proto` | No request/response |
| `Any` | `google/protobuf/any.proto` | Arbitrary message embedding |
| `Struct` | `google/protobuf/struct.proto` | Dynamic JSON-like structures |
| `FieldMask` | `google/protobuf/field_mask.proto` | Partial updates |
| `Wrappers` | `google/protobuf/wrappers.proto` | Nullable scalars (`StringValue`, etc.) |
