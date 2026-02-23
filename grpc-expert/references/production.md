# Running gRPC in Production

This reference covers the operational concerns of deploying and maintaining gRPC services in production: testing strategies, continuous integration, containerized deployment, Kubernetes orchestration, observability, and debugging.

## Testing gRPC Applications

### Unit Testing with bufconn

The `bufconn` package provides an in-memory listener that avoids the need for real network ports during tests. This is the idiomatic approach for unit testing gRPC services in Go.

```go
package order_test

import (
    "context"
    "net"
    "testing"

    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials/insecure"
    "google.golang.org/grpc/test/bufconn"

    pb "example.com/order/proto"
)

const bufSize = 1024 * 1024

var lis *bufconn.Listener

func init() {
    lis = bufconn.Listen(bufSize)
    s := grpc.NewServer()
    pb.RegisterOrderServiceServer(s, &OrderServiceImpl{})
    go func() {
        if err := s.Serve(lis); err != nil {
            panic(err)
        }
    }()
}

func bufDialer(context.Context, string) (net.Conn, error) {
    return lis.Dial()
}

func TestAddOrder(t *testing.T) {
    ctx := context.Background()
    conn, err := grpc.NewClient(
        "passthrough:///bufnet",
        grpc.WithContextDialer(bufDialer),
        grpc.WithTransportCredentials(insecure.NewCredentials()),
    )
    if err != nil {
        t.Fatalf("failed to dial bufnet: %v", err)
    }
    defer conn.Close()

    client := pb.NewOrderServiceClient(conn)

    resp, err := client.AddOrder(ctx, &pb.Order{
        Items:       []string{"Widget A", "Widget B"},
        Description: "Test order",
        Price:       29.99,
        Destination: "San Francisco, CA",
    })
    if err != nil {
        t.Fatalf("AddOrder failed: %v", err)
    }
    if resp.GetId() == "" {
        t.Error("expected non-empty order ID")
    }
}
```

Key advantages of `bufconn`: tests run without allocating OS-level ports, avoiding port conflicts in CI; connections are in-memory so tests are fast; the full gRPC stack (interceptors, serialization, metadata) is exercised.

### Integration Testing

Integration tests start a real server on a local port and exercise the full network path:

```go
func TestIntegration_OrderService(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping integration test in short mode")
    }

    // Start the real server
    lis, err := net.Listen("tcp", "localhost:0") // random available port
    if err != nil {
        t.Fatal(err)
    }
    srv := grpc.NewServer()
    pb.RegisterOrderServiceServer(srv, NewOrderService(realDB))
    go srv.Serve(lis)
    defer srv.GracefulStop()

    // Connect a test client
    conn, err := grpc.NewClient(
        lis.Addr().String(),
        grpc.WithTransportCredentials(insecure.NewCredentials()),
    )
    if err != nil {
        t.Fatal(err)
    }
    defer conn.Close()

    client := pb.NewOrderServiceClient(conn)

    // Test the full flow
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    order, err := client.AddOrder(ctx, &pb.Order{
        Items: []string{"Item 1"},
        Price: 10.00,
    })
    if err != nil {
        t.Fatalf("AddOrder: %v", err)
    }

    got, err := client.GetOrder(ctx, &pb.OrderID{Id: order.GetId()})
    if err != nil {
        t.Fatalf("GetOrder: %v", err)
    }
    if got.Price != 10.00 {
        t.Errorf("price = %v, want 10.00", got.Price)
    }
}
```

Use `localhost:0` to let the OS assign a free port. This prevents collisions when running tests in parallel.

### Testing Streaming RPCs

Server-streaming RPCs require reading from the stream until `io.EOF`:

```go
func TestSearchOrders(t *testing.T) {
    ctx := context.Background()
    conn, err := grpc.NewClient("passthrough:///bufnet",
        grpc.WithContextDialer(bufDialer),
        grpc.WithTransportCredentials(insecure.NewCredentials()),
    )
    if err != nil {
        t.Fatal(err)
    }
    defer conn.Close()

    client := pb.NewOrderServiceClient(conn)
    stream, err := client.SearchOrders(ctx, &pb.SearchQuery{Query: "Widget"})
    if err != nil {
        t.Fatalf("SearchOrders: %v", err)
    }

    var results []*pb.Order
    for {
        order, err := stream.Recv()
        if err == io.EOF {
            break
        }
        if err != nil {
            t.Fatalf("Recv: %v", err)
        }
        results = append(results, order)
    }

    if len(results) == 0 {
        t.Error("expected at least one result")
    }
}
```

For bidirectional streaming, launch a goroutine for sending while the main test goroutine receives, coordinating with `stream.CloseSend()` to signal completion.

## Load Testing

### ghz: gRPC Benchmarking Tool

`ghz` is the standard command-line tool for gRPC load testing. It requires a proto file or server reflection.

```bash
# Basic load test: 200 requests, 50 concurrent
ghz --insecure \
    --proto ./order.proto \
    --call order.OrderService/AddOrder \
    -d '{"items":["Widget"],"price":10.0,"destination":"NYC"}' \
    -n 200 -c 50 \
    localhost:50051

# Duration-based test: run for 30 seconds
ghz --insecure \
    --proto ./order.proto \
    --call order.OrderService/GetOrder \
    -d '{"id":"order-123"}' \
    --duration 30s -c 20 \
    localhost:50051

# Using server reflection (no proto file needed)
ghz --insecure --call order.OrderService/AddOrder \
    -d '{"items":["Widget"],"price":10.0}' \
    -n 1000 -c 100 \
    localhost:50051
```

Interpreting ghz output -- the key metrics to evaluate:

| Metric | Healthy Target | Concern Threshold |
|--------|---------------|-------------------|
| Throughput (RPS) | Varies by service | Drops under load indicate bottlenecks |
| p50 latency | < 10ms (internal) | Baseline for typical requests |
| p95 latency | < 50ms | User-facing SLO boundary |
| p99 latency | < 200ms | Tail latency affecting reliability |
| Error rate | < 0.1% | > 1% requires investigation |

### Locust with gRPC

For more complex load patterns, Locust supports gRPC through custom clients:

```python
from locust import User, task, between
from locust.exception import LocustError
import grpc
import order_pb2
import order_pb2_grpc
import time

class GrpcUser(User):
    wait_time = between(0.5, 2.0)

    def on_start(self):
        self.channel = grpc.insecure_channel("localhost:50051")
        self.stub = order_pb2_grpc.OrderServiceStub(self.channel)

    def on_stop(self):
        self.channel.close()

    @task(3)
    def get_order(self):
        start = time.time()
        try:
            resp = self.stub.GetOrder(
                order_pb2.OrderID(id="order-123"),
                timeout=5,
            )
            elapsed = (time.time() - start) * 1000
            self.environment.events.request.fire(
                request_type="grpc",
                name="GetOrder",
                response_time=elapsed,
                response_length=resp.ByteSize(),
                exception=None,
            )
        except grpc.RpcError as e:
            elapsed = (time.time() - start) * 1000
            self.environment.events.request.fire(
                request_type="grpc",
                name="GetOrder",
                response_time=elapsed,
                response_length=0,
                exception=e,
            )
```

## Continuous Integration

### Proto Linting and Breaking Change Detection

The `buf` CLI enforces proto style and detects breaking changes:

```yaml
# buf.yaml
version: v2
lint:
  use:
    - STANDARD
  except:
    - PACKAGE_VERSION_SUFFIX
breaking:
  use:
    - FILE
```

```bash
# Lint proto files
buf lint proto/

# Check for breaking changes against the main branch
buf breaking proto/ --against '.git#branch=main'

# Check against a published BSR module
buf breaking proto/ --against 'buf.build/myorg/myapi'
```

Common breaking changes `buf breaking` catches: removing a field or RPC, changing a field type or number, renaming a service or method, changing a field from optional to repeated.

### CI Pipeline Configuration

```yaml
# .github/workflows/grpc-ci.yml
name: gRPC CI
on: [push, pull_request]

jobs:
  proto:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: bufbuild/buf-setup-action@v1
      - run: buf lint proto/
      - run: buf breaking proto/ --against '.git#branch=main'

  generate:
    runs-on: ubuntu-latest
    needs: proto
    steps:
      - uses: actions/checkout@v4
      - uses: bufbuild/buf-setup-action@v1
      - run: buf generate proto/
      - name: Check generated code is up to date
        run: |
          git diff --exit-code -- '*.pb.go' '*.pb.gw.go' || \
            (echo "Generated code is stale. Run buf generate." && exit 1)

  test:
    runs-on: ubuntu-latest
    needs: generate
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
      - run: go test -race -coverprofile=coverage.out ./...
      - run: go test -run Integration -count=1 ./...
```

The pipeline enforces three gates: proto files must be well-formed, generated code must be checked in and current, and all tests (unit and integration) must pass.

## Deployment with Docker

### Multi-Stage Dockerfile

```dockerfile
# Build stage
FROM golang:1.22-alpine AS builder
RUN apk add --no-cache git ca-certificates
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /grpc-server ./cmd/server

# Runtime stage using distroless
FROM gcr.io/distroless/static:nonroot
COPY --from=builder /grpc-server /grpc-server
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
EXPOSE 50051
USER nonroot:nonroot
ENTRYPOINT ["/grpc-server"]
```

Container image options compared:

| Base Image | Size | Shell | Debugging | Security |
|-----------|------|-------|-----------|----------|
| `scratch` | ~0 MB | No | Minimal | Smallest attack surface |
| `distroless/static` | ~2 MB | No | Minimal | No package manager |
| `alpine` | ~7 MB | Yes | Easy | Small but has shell |

Use `distroless` as the default. Use `alpine` when you need to shell into containers for debugging. Use `scratch` only when image size is critical and you bundle CA certs yourself.

### Docker Health Check

```dockerfile
# Install grpc_health_probe in a builder stage
FROM golang:1.22-alpine AS health
RUN go install github.com/grpc-ecosystem/grpc-health-probe@latest

FROM gcr.io/distroless/static:nonroot
COPY --from=builder /grpc-server /grpc-server
COPY --from=health /go/bin/grpc_health_probe /grpc_health_probe
EXPOSE 50051
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
    CMD ["/grpc_health_probe", "-addr=:50051"]
ENTRYPOINT ["/grpc-server"]
```

The gRPC server must implement the `grpc.health.v1.Health` service for the probe to work. In Go:

```go
import "google.golang.org/grpc/health"
import healthpb "google.golang.org/grpc/health/grpc_health_v1"

healthServer := health.NewServer()
healthpb.RegisterHealthServer(grpcServer, healthServer)
healthServer.SetServingStatus("order.OrderService", healthpb.HealthCheckResponse_SERVING)
```

## Deployment with Kubernetes

### Deployment and Service Manifests

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
  labels:
    app: order-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: order-service
  template:
    metadata:
      labels:
        app: order-service
    spec:
      containers:
        - name: order-service
          image: registry.example.com/order-service:v1.2.0
          ports:
            - containerPort: 50051
              protocol: TCP
              name: grpc
          env:
            - name: GRPC_PORT
              value: "50051"
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 256Mi
          livenessProbe:
            grpc:
              port: 50051
            initialDelaySeconds: 5
            periodSeconds: 10
          readinessProbe:
            grpc:
              port: 50051
            initialDelaySeconds: 3
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: order-service
spec:
  selector:
    app: order-service
  ports:
    - port: 50051
      targetPort: grpc
      protocol: TCP
```

Kubernetes 1.24+ supports native gRPC health probes via the `grpc` field. For older clusters, use `grpc_health_probe` as an exec probe:

```yaml
livenessProbe:
  exec:
    command: ["/grpc_health_probe", "-addr=:50051"]
  initialDelaySeconds: 5
  periodSeconds: 10
```

### The HTTP/2 Load Balancing Problem

Standard Kubernetes Services operate at L4 (TCP). Since gRPC uses HTTP/2, a single TCP connection is multiplexed for all RPCs. The kube-proxy round-robins at connection establishment, not per-request, so a single client connection pins to one backend pod. This means L4 Services do not distribute gRPC traffic evenly.

Solutions, in order of increasing complexity:

**Headless Service with client-side load balancing:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: order-service-headless
spec:
  clusterIP: None       # headless: DNS returns all pod IPs
  selector:
    app: order-service
  ports:
    - port: 50051
```

```go
import "google.golang.org/grpc/resolver"

// Use dns:/// scheme with round-robin to resolve headless service
conn, err := grpc.NewClient(
    "dns:///order-service-headless.default.svc.cluster.local:50051",
    grpc.WithDefaultServiceConfig(`{"loadBalancingConfig":[{"round_robin":{}}]}`),
    grpc.WithTransportCredentials(insecure.NewCredentials()),
)
```

**L7 proxy with Envoy or Istio:** A service mesh like Istio transparently intercepts gRPC traffic and performs per-RPC load balancing across pods. This is the most common production approach as it requires no client-side code changes.

```yaml
# Istio DestinationRule for gRPC load balancing
apiVersion: networking.istio.io/v1
kind: DestinationRule
metadata:
  name: order-service
spec:
  host: order-service
  trafficPolicy:
    loadBalancer:
      simple: ROUND_ROBIN
    connectionPool:
      http:
        h2UpgradePolicy: UPGRADE  # ensure HTTP/2
```

## Observability

### Metrics with Prometheus

The `go-grpc-prometheus` package provides interceptors that expose standard Prometheus metrics:

```go
import (
    grpcprom "github.com/grpc-ecosystem/go-grpc-middleware/providers/prometheus"
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

func main() {
    srvMetrics := grpcprom.NewServerMetrics(
        grpcprom.WithServerHandlingTimeHistogram(
            grpcprom.WithHistogramBuckets([]float64{
                0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0,
            }),
        ),
    )
    prometheus.MustRegister(srvMetrics)

    srv := grpc.NewServer(
        grpc.ChainUnaryInterceptor(srvMetrics.UnaryServerInterceptor()),
        grpc.ChainStreamInterceptor(srvMetrics.StreamServerInterceptor()),
    )

    // Expose /metrics endpoint on a separate HTTP port
    go func() {
        http.Handle("/metrics", promhttp.Handler())
        http.ListenAndServe(":9090", nil)
    }()
}
```

Key metrics to monitor:

- `grpc_server_handled_total` -- total RPCs completed, labeled by method and status code. Use for error rate and throughput.
- `grpc_server_handling_seconds` -- latency histogram. Derive p50/p95/p99 with `histogram_quantile()`.
- `grpc_server_started_total` minus `grpc_server_handled_total` -- in-flight RPCs, indicating concurrency pressure.
- `grpc_server_msg_received_total` / `grpc_server_msg_sent_total` -- message counts for streaming RPCs.

### Structured Logging

A logging interceptor captures request metadata for every RPC:

```go
import (
    "log/slog"
    "google.golang.org/grpc"
    "google.golang.org/grpc/status"
)

func loggingUnaryInterceptor(
    ctx context.Context,
    req interface{},
    info *grpc.UnaryServerInfo,
    handler grpc.UnaryHandler,
) (interface{}, error) {
    start := time.Now()
    resp, err := handler(ctx, req)
    duration := time.Since(start)

    st, _ := status.FromError(err)
    level := slog.LevelInfo
    if err != nil {
        level = slog.LevelError
    }

    slog.LogAttrs(ctx, level, "gRPC request",
        slog.String("method", info.FullMethod),
        slog.String("status", st.Code().String()),
        slog.Duration("duration", duration),
        slog.String("peer", peerFromContext(ctx)),
    )
    return resp, err
}
```

Use `slog.LevelDebug` for request/response body logging (expensive, disable in production). Use `slog.LevelInfo` for per-request logging. Use `slog.LevelWarn` for deadline-exceeded or cancelled RPCs. Use `slog.LevelError` for Internal, Unavailable, and Unknown status codes.

### Distributed Tracing with OpenTelemetry

```go
import (
    "go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
)

func initTracer() (*sdktrace.TracerProvider, error) {
    exporter, err := otlptracegrpc.New(context.Background(),
        otlptracegrpc.WithEndpoint("jaeger-collector:4317"),
        otlptracegrpc.WithInsecure(),
    )
    if err != nil {
        return nil, err
    }
    tp := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exporter),
        sdktrace.WithSampler(sdktrace.TraceIDRatioBased(0.1)), // sample 10%
    )
    otel.SetTracerProvider(tp)
    return tp, nil
}

func main() {
    tp, _ := initTracer()
    defer tp.Shutdown(context.Background())

    srv := grpc.NewServer(
        grpc.StatsHandler(otelgrpc.NewServerHandler()),
    )
    // ... register services and serve
}
```

Trace context propagates automatically through gRPC metadata. When service A calls service B, the `otelgrpc` handler injects the trace ID into outgoing metadata on the client side and extracts it on the server side. This produces connected spans across services without manual propagation code.

### Correlating Signals

Connect traces, metrics, and logs by embedding the trace ID in log entries and metric exemplars:

```go
func loggingInterceptorWithTrace(
    ctx context.Context, req interface{},
    info *grpc.UnaryServerInfo, handler grpc.UnaryHandler,
) (interface{}, error) {
    spanCtx := trace.SpanContextFromContext(ctx)
    resp, err := handler(ctx, req)

    slog.InfoContext(ctx, "gRPC request",
        slog.String("method", info.FullMethod),
        slog.String("trace_id", spanCtx.TraceID().String()),
        slog.String("span_id", spanCtx.SpanID().String()),
    )
    return resp, err
}
```

In Grafana, this enables jumping from a metric spike to example traces (via exemplars) to detailed logs for specific requests.

## Debugging and Troubleshooting

### grpcurl for Manual Testing

`grpcurl` is curl for gRPC. It works with server reflection or proto files.

```bash
# List available services (requires reflection)
grpcurl -plaintext localhost:50051 list

# Describe a service
grpcurl -plaintext localhost:50051 describe order.OrderService

# Call a unary RPC
grpcurl -plaintext -d '{"id":"order-123"}' \
    localhost:50051 order.OrderService/GetOrder

# Call with metadata (authentication headers)
grpcurl -plaintext \
    -H 'authorization: Bearer <token>' \
    -d '{"items":["Widget"],"price":10.0}' \
    localhost:50051 order.OrderService/AddOrder

# Using a proto file instead of reflection
grpcurl -plaintext -import-path ./proto -proto order.proto \
    -d '{"id":"order-123"}' \
    localhost:50051 order.OrderService/GetOrder
```

Enable server reflection in your Go server for `grpcurl` and other tools to work without proto files:

```go
import "google.golang.org/grpc/reflection"

srv := grpc.NewServer()
reflection.Register(srv)
```

### Environment Variable Debugging

Go gRPC has built-in debug logging controlled by environment variables:

```bash
# Enable verbose gRPC internal logging
GRPC_GO_LOG_SEVERITY_LEVEL=info \
GRPC_GO_LOG_VERBOSITY_LEVEL=2 \
    ./grpc-server

# Severity levels: info, warning, error
# Verbosity: 0 (least) to 99 (most detailed)
# Level 2 shows connection state changes, resolver updates, balancer picks
```

These are invaluable for diagnosing connection establishment, name resolution, and load balancer behavior without code changes.

### Channelz

Channelz exposes internal gRPC channel state via a gRPC service, useful for debugging connection pools and subchannel health:

```go
import "google.golang.org/grpc/channelz/service"

srv := grpc.NewServer()
service.RegisterChannelzServiceToServer(srv)
```

Query channelz via `grpcurl` to inspect active channels, subchannels, and socket states. It reveals per-connection statistics including messages sent/received, last message time, and stream counts.

### Common Issues and Remediation

**DNS resolution failures:** gRPC caches DNS results. In Kubernetes, pod IPs change on restarts. Use `dns:///` scheme with a short TTL or a headless service. Symptom: RPCs succeed initially then fail with `Unavailable` after a pod restart.

**TLS handshake errors:** Mismatched certificate names cause `transport: authentication handshake failed`. Verify the server certificate SAN matches the address the client connects to. For internal services, use `insecure.NewCredentials()` only within a trusted network or service mesh that provides mTLS.

**Deadline exceeded:** The client-set deadline expired before the server responded. Check both server processing time and network latency. Set deadlines appropriate to the operation -- 500ms for simple lookups, 5-30s for complex operations. Always propagate deadlines through context in downstream calls.

**Connection refused:** The server is not listening or the port is blocked. Verify the server is bound to `0.0.0.0` (not `127.0.0.1`) when running in containers. Check Kubernetes service selectors match pod labels. Confirm no NetworkPolicy is blocking the port.

**Resource exhaustion:** gRPC defaults to unlimited concurrent streams per connection. Set `grpc.MaxConcurrentStreams()` server option to bound resource usage. Monitor `grpc_server_started_total - grpc_server_handled_total` for in-flight request buildup.

```go
srv := grpc.NewServer(
    grpc.MaxConcurrentStreams(100),
    grpc.MaxRecvMsgSize(4 * 1024 * 1024),  // 4MB max message
    grpc.KeepaliveParams(keepalive.ServerParameters{
        MaxConnectionIdle: 5 * time.Minute,
        Time:              1 * time.Minute,   // ping if idle this long
        Timeout:           20 * time.Second,  // wait this long for ping ack
    }),
)
```
