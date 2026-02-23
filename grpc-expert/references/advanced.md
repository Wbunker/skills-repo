# gRPC Beyond the Basics

Advanced gRPC patterns in Go: interceptors, deadlines, cancellation, error handling, multiplexing, metadata, name resolution, load balancing, and compression.

## Interceptors

Interceptors are gRPC middleware. They wrap every RPC on the client or server side for cross-cutting concerns like logging, auth, and metrics.

### Server-Side Unary Interceptor

```go
func loggingInterceptor(
    ctx context.Context, req interface{},
    info *grpc.UnaryServerInfo, handler grpc.UnaryHandler,
) (interface{}, error) {
    start := time.Now()
    resp, err := handler(ctx, req) // call the actual RPC
    log.Printf("%s %v err=%v", info.FullMethod, time.Since(start), err)
    return resp, err
}

server := grpc.NewServer(grpc.UnaryInterceptor(loggingInterceptor))
```

The `info.FullMethod` gives the method name (`/package.Service/Method`). Call `handler(ctx, req)` to proceed or return an error to short-circuit.

### Server-Side Stream Interceptor

Stream interceptors wrap the `grpc.ServerStream` to intercept individual messages:

```go
type wrappedStream struct{ grpc.ServerStream }

func (w *wrappedStream) RecvMsg(m interface{}) error {
    log.Printf("recv: %T", m)
    return w.ServerStream.RecvMsg(m)
}
func (w *wrappedStream) SendMsg(m interface{}) error {
    log.Printf("send: %T", m)
    return w.ServerStream.SendMsg(m)
}

func streamInterceptor(
    srv interface{}, ss grpc.ServerStream,
    info *grpc.StreamServerInfo, handler grpc.StreamHandler,
) error {
    return handler(srv, &wrappedStream{ss})
}

server := grpc.NewServer(grpc.StreamInterceptor(streamInterceptor))
```

### Client-Side Interceptors

```go
func clientUnaryInterceptor(
    ctx context.Context, method string, req, reply interface{},
    cc *grpc.ClientConn, invoker grpc.UnaryInvoker, opts ...grpc.CallOption,
) error {
    start := time.Now()
    err := invoker(ctx, method, req, reply, cc, opts...)
    log.Printf("client %s %v err=%v", method, time.Since(start), err)
    return err
}

conn, _ := grpc.Dial(target, grpc.WithUnaryInterceptor(clientUnaryInterceptor))
```

Client stream interceptors follow the same pattern: call `streamer()` to get the `grpc.ClientStream`, then return a wrapper that overrides `SendMsg`/`RecvMsg`.

### Chaining Multiple Interceptors

```go
server := grpc.NewServer(
    grpc.ChainUnaryInterceptor(
        recoveryInterceptor,  // outermost: catches panics
        loggingInterceptor,   // logs every call
        authInterceptor,      // validates credentials
        rateLimitInterceptor, // throttles requests
    ),
    grpc.ChainStreamInterceptor(streamRecovery, streamLogging, streamAuth),
)

conn, _ := grpc.Dial(target,
    grpc.WithChainUnaryInterceptor(clientLogging, clientRetry),
)
```

Interceptors execute in order: first wraps second wraps third. Place recovery first to catch panics from all downstream interceptors.

### Common Interceptor Patterns

```go
// Auth: extract token from metadata
func authInterceptor(ctx context.Context, req interface{},
    info *grpc.UnaryServerInfo, handler grpc.UnaryHandler,
) (interface{}, error) {
    md, ok := metadata.FromIncomingContext(ctx)
    if !ok {
        return nil, status.Errorf(codes.Unauthenticated, "no metadata")
    }
    if tokens := md.Get("authorization"); len(tokens) == 0 || !validateToken(tokens[0]) {
        return nil, status.Errorf(codes.Unauthenticated, "invalid token")
    }
    return handler(ctx, req)
}

// Recovery: convert panics to gRPC errors
func recoveryInterceptor(ctx context.Context, req interface{},
    info *grpc.UnaryServerInfo, handler grpc.UnaryHandler,
) (resp interface{}, err error) {
    defer func() {
        if r := recover(); r != nil {
            err = status.Errorf(codes.Internal, "internal error")
        }
    }()
    return handler(ctx, req)
}
```

## Deadlines

A deadline is an absolute point in time after which an RPC fails, regardless of progress.

### Setting and Checking Deadlines

```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

resp, err := client.GetOrder(ctx, &pb.OrderRequest{Id: "101"})
if err != nil {
    if status.Code(err) == codes.DeadlineExceeded {
        log.Println("server took too long")
    }
}
```

### Deadline Propagation

Deadlines propagate automatically through the context. If service A sets a 10s deadline and spends 3s processing before calling service B, B inherits ~7s remaining.

```go
func (s *server) ProcessOrder(ctx context.Context, req *pb.Order) (*pb.Result, error) {
    if deadline, ok := ctx.Deadline(); ok {
        if time.Until(deadline) < 500*time.Millisecond {
            return nil, status.Errorf(codes.DeadlineExceeded, "insufficient time")
        }
    }
    // Downstream call inherits the deadline via ctx
    return inventoryClient.CheckStock(ctx, &pb.StockRequest{ItemId: req.ItemId})
}
```

**Best practices**: Always set deadlines -- an RPC without one can hang indefinitely. Set a generous deadline at the edge (e.g., 30s) and let it propagate inward. Do not set them too tight; network jitter causes spurious failures.

## Cancellation

Cancellation lets a client abort an in-progress RPC. The signal propagates to the server and all downstream calls.

```go
ctx, cancel := context.WithCancel(context.Background())
go func() { <-userInterrupt; cancel() }()

stream, _ := client.SearchOrders(ctx, &pb.SearchRequest{Query: "item"})
for {
    order, err := stream.Recv()
    if status.Code(err) == codes.Canceled {
        break // client cancelled
    }
    processOrder(order)
}
```

Servers detect cancellation through the context:

```go
func (s *server) Export(req *pb.Req, stream pb.Svc_ExportServer) error {
    for _, batch := range batches {
        select {
        case <-stream.Context().Done():
            return status.Error(codes.Canceled, "client cancelled")
        default:
        }
        if err := stream.Send(processBatch(batch)); err != nil {
            return err
        }
    }
    return nil
}
```

## Error Handling

gRPC uses structured errors from `google.golang.org/grpc/status` and `google.golang.org/grpc/codes`.

### Status Codes

| Code | Name | When to Use |
|------|------|-------------|
| 0 | OK | Success |
| 1 | Canceled | Client cancelled the request |
| 2 | Unknown | Catch-all for unmapped errors |
| 3 | InvalidArgument | Bad client input (do not retry) |
| 4 | DeadlineExceeded | Operation took too long |
| 5 | NotFound | Entity does not exist |
| 6 | AlreadyExists | Duplicate create |
| 7 | PermissionDenied | Authenticated but not authorized |
| 8 | ResourceExhausted | Rate limit or quota exceeded |
| 9 | FailedPrecondition | System not in required state |
| 10 | Aborted | Concurrency conflict |
| 12 | Unimplemented | Method not implemented |
| 13 | Internal | Serious server-side bug |
| 14 | Unavailable | Transient; retry with backoff |
| 16 | Unauthenticated | No valid credentials |

### Rich Errors with Details

```go
import epb "google.golang.org/genproto/googleapis/rpc/errdetails"

// Server: attach structured details
st := status.New(codes.InvalidArgument, "invalid order")
st, _ = st.WithDetails(&epb.BadRequest{
    FieldViolations: []*epb.BadRequest_FieldViolation{
        {Field: "price", Description: "must be non-negative"},
    },
})
return nil, st.Err()
```

Other detail types: `RetryInfo` (when to retry), `DebugInfo` (stack traces), `PreconditionFailure`.

### Extracting Error Details on the Client

```go
if err != nil {
    st := status.Convert(err)
    for _, detail := range st.Details() {
        switch t := detail.(type) {
        case *epb.BadRequest:
            for _, v := range t.GetFieldViolations() {
                log.Printf("field=%s: %s", v.GetField(), v.GetDescription())
            }
        case *epb.RetryInfo:
            log.Printf("retry after %v", t.GetRetryDelay().AsDuration())
        }
    }
}
```

## Multiplexing

### Server: Multiple Services on One Port

```go
server := grpc.NewServer()
pb.RegisterOrderServiceServer(server, &orderServer{})
pb.RegisterInventoryServiceServer(server, &inventoryServer{})
pb.RegisterShippingServiceServer(server, &shippingServer{})
server.Serve(lis) // all share one port and one set of interceptors
```

### Client: One Connection, Multiple Stubs

```go
conn, _ := grpc.Dial("localhost:50051", grpc.WithInsecure())
orderClient := pb.NewOrderServiceClient(conn)
inventoryClient := pb.NewInventoryServiceClient(conn)
```

A single `grpc.ClientConn` multiplexes all stubs over one HTTP/2 connection pool.

## Metadata

Metadata is gRPC's equivalent of HTTP headers: string key-value pairs carried alongside RPCs. Binary values require keys ending in `-bin`.

### Client Sends Metadata

```go
md := metadata.Pairs("authorization", "Bearer tok", "request-id", "req-123")
ctx := metadata.NewOutgoingContext(context.Background(), md)
// Or append to existing:
ctx = metadata.AppendToOutgoingContext(ctx, "extra-key", "extra-val")

resp, err := client.GetOrder(ctx, req)
```

### Server Reads Metadata

```go
func (s *server) GetOrder(ctx context.Context, req *pb.OrderRequest) (*pb.Order, error) {
    md, ok := metadata.FromIncomingContext(ctx)
    if !ok {
        return nil, status.Error(codes.Internal, "no metadata")
    }
    tokens := md.Get("authorization") // returns []string
    // ...
}
```

### Response Headers and Trailers

```go
// Server sends headers (before response) and trailers (after response)
grpc.SendHeader(ctx, metadata.Pairs("server-region", "us-east-1"))
grpc.SetTrailer(ctx, metadata.Pairs("processing-time", "42ms"))

// Client reads them
var header, trailer metadata.MD
resp, err := client.GetOrder(ctx, req, grpc.Header(&header), grpc.Trailer(&trailer))
region := header.Get("server-region")
```

For streaming RPCs, use `stream.Header()` and `stream.Trailer()` on the client side.

## Name Resolution

Name resolution translates a target string into backend addresses. gRPC uses a pluggable resolver framework.

### Built-In Resolvers

```go
conn, _ := grpc.Dial("localhost:50051", opts...)                  // passthrough (default)
conn, _ := grpc.Dial("dns:///myservice.example.com:50051", opts...) // DNS with periodic re-resolve
```

### Custom Name Resolver

Implement `resolver.Builder` and `resolver.Resolver` for service discovery integration:

```go
type consulBuilder struct{}

func (b *consulBuilder) Build(target resolver.Target, cc resolver.ClientConn,
    opts resolver.BuildOptions) (resolver.Resolver, error) {
    r := &consulResolver{target: target, cc: cc}
    go r.watch()
    return r, nil
}
func (b *consulBuilder) Scheme() string { return "consul" }

type consulResolver struct {
    target resolver.Target
    cc     resolver.ClientConn
}
func (r *consulResolver) watch() {
    // Query Consul, then update addresses on change:
    r.cc.UpdateState(resolver.State{Addresses: []resolver.Address{
        {Addr: "10.0.0.1:50051"}, {Addr: "10.0.0.2:50051"},
    }})
}
func (r *consulResolver) ResolveNow(resolver.ResolveNowOptions) {}
func (r *consulResolver) Close()                                {}

func init() { resolver.Register(&consulBuilder{}) }
```

```go
conn, _ := grpc.Dial("consul:///order-service",
    grpc.WithDefaultServiceConfig(`{"loadBalancingPolicy":"round_robin"}`),
)
```

The same pattern applies to etcd, Zookeeper, or any service registry.

## Load Balancing

### Client-Side Load Balancing

The client resolves a name to multiple addresses and distributes RPCs. Two built-in policies:

- **pick_first** (default): sends all RPCs to the first working address.
- **round_robin**: distributes RPCs evenly across all addresses.

```go
conn, _ := grpc.Dial("dns:///myservice.example.com:50051",
    grpc.WithDefaultServiceConfig(`{"loadBalancingPolicy":"round_robin"}`),
)
```

Client-side LB requires the resolver to return multiple addresses (e.g., DNS with multiple A records).

### Proxy-Based (External) Load Balancing

An L7 proxy sits between client and backends. The proxy must understand HTTP/2 to balance individual RPCs over a single connection:

- **Envoy**: native gRPC support, per-RPC balancing, retries, circuit breaking.
- **Nginx**: gRPC proxying via `grpc_pass` (since 1.13.10).
- **HAProxy**: HTTP/2 and gRPC support (since 2.0).

Simpler for clients (one address) but adds latency and requires HA for the proxy itself.

### Look-Aside Load Balancing

The client queries an external LB service for backends and weights, then does client-side balancing with direct connections. The `xDS` protocol (Envoy control plane) is the modern standard for this.

### Kubernetes

Standard `ClusterIP` services do L4 (connection-level) balancing, which is ineffective for long-lived gRPC connections. Solutions:

1. **Headless Service** (`clusterIP: None`) + DNS resolver + `round_robin` for direct pod connections.
2. **Service mesh** (Istio, Linkerd) for transparent per-RPC balancing via sidecar.
3. **xDS control plane** for native gRPC xDS support.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: order-service
spec:
  clusterIP: None  # headless
  selector: { app: order-service }
  ports: [{ port: 50051, targetPort: 50051 }]
```

```go
conn, _ := grpc.Dial("dns:///order-service.default.svc.cluster.local:50051",
    grpc.WithDefaultServiceConfig(`{"loadBalancingPolicy":"round_robin"}`),
)
```

## Compression

gRPC supports per-message compression. Import the gzip package to register it:

```go
import _ "google.golang.org/grpc/encoding/gzip"
```

The server automatically handles compression when requested. Enable on the client per-call or globally:

```go
// Per-call
resp, err := client.GetOrder(ctx, req, grpc.UseCompressor(gzip.Name))

// Global default
conn, _ := grpc.Dial(target,
    grpc.WithDefaultCallOptions(grpc.UseCompressor(gzip.Name)),
)
```

Compression helps most with large messages (several KB+) containing compressible data. For small messages, CPU overhead outweighs bandwidth savings. Custom compressors (zstd, snappy) can be implemented via the `encoding.Compressor` interface and registered with `encoding.RegisterCompressor`.
