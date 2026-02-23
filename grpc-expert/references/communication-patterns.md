# gRPC Communication Patterns

gRPC defines four communication patterns built on top of HTTP/2. Each pattern maps to a distinct combination of unary and streaming message flows between client and server. Choosing the right pattern is a fundamental API design decision that affects performance, complexity, and user experience.

## Simple RPC (Unary RPC)

Unary RPC is the simplest pattern: one request, one response. It behaves like a traditional function call across the network.

### Proto Definition

```protobuf
syntax = "proto3";

package ecommerce;
option go_package = "ecommerce/";

import "google/protobuf/wrappers.proto";

service OrderService {
  rpc GetOrder(google.protobuf.StringValue) returns (Order);
}

message Order {
  string  id          = 1;
  string  description = 2;
  float   price       = 3;
  repeated string items = 4;
}
```

### Server Implementation (Go)

```go
func (s *server) GetOrder(ctx context.Context, req *wrapperspb.StringValue) (*pb.Order, error) {
    order, exists := s.orders[req.Value]
    if !exists {
        return nil, status.Errorf(codes.NotFound, "order %s not found", req.Value)
    }
    return order, nil
}
```

### Client Call (Go)

```go
conn, err := grpc.Dial("localhost:50051", grpc.WithTransportCredentials(insecure.NewCredentials()))
if err != nil {
    log.Fatalf("failed to dial: %v", err)
}
defer conn.Close()

client := pb.NewOrderServiceClient(conn)

ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

order, err := client.GetOrder(ctx, &wrapperspb.StringValue{Value: "order-1"})
if err != nil {
    st, ok := status.FromError(err)
    if ok {
        log.Printf("gRPC error: code=%s message=%s", st.Code(), st.Message())
    }
    return
}
log.Printf("Order: %v", order)
```

### Request-Response Lifecycle

1. Client calls the stub method, which serializes the request protobuf and initiates an HTTP/2 stream.
2. Client sends HTTP/2 HEADERS frame (method path `/ecommerce.OrderService/GetOrder`, content-type, metadata).
3. Client sends a single DATA frame containing the length-prefixed protobuf message.
4. Server receives the request, executes the handler, and returns the response.
5. Server sends response HEADERS, a single DATA frame with the response protobuf, then trailers containing the gRPC status code.
6. The HTTP/2 stream closes.

### When to Use

Unary RPC is appropriate for CRUD operations, simple lookups, authentication calls, configuration fetches, and any interaction where the entire request and response fit comfortably in a single message. Most gRPC services consist primarily of unary RPCs.

---

## Server-Streaming RPC

The server sends multiple response messages to a single client request. The client reads from the stream until it receives an end-of-stream signal.

### Proto Definition

The `stream` keyword on the return type declares a server-streaming method:

```protobuf
service OrderService {
  rpc SearchOrders(google.protobuf.StringValue) returns (stream Order);
}
```

### Server Implementation (Go)

The server calls `Send()` repeatedly to push messages to the client. When the handler returns `nil`, gRPC closes the stream with status OK.

```go
func (s *server) SearchOrders(query *wrapperspb.StringValue, stream pb.OrderService_SearchOrdersServer) error {
    for id, order := range s.orders {
        if strings.Contains(order.Description, query.Value) {
            if err := stream.Send(order); err != nil {
                return status.Errorf(codes.Internal, "failed to send order %s: %v", id, err)
            }
        }
    }
    // Returning nil closes the stream with status OK.
    return nil
}
```

### Client Implementation (Go)

The client calls `Recv()` in a loop until it receives `io.EOF`, which signals a successful end of the stream. Any other error indicates a failure.

```go
stream, err := client.SearchOrders(ctx, &wrapperspb.StringValue{Value: "electronics"})
if err != nil {
    log.Fatalf("search failed: %v", err)
}

for {
    order, err := stream.Recv()
    if err == io.EOF {
        // Server finished sending.
        break
    }
    if err != nil {
        log.Fatalf("error receiving order: %v", err)
    }
    log.Printf("Found order: %s - %s", order.Id, order.Description)
}
```

### Use Cases

- **Search results**: Return matching records incrementally rather than building a large single response.
- **Real-time feeds**: Push price updates, news events, or notifications as they occur.
- **Large data sets**: Stream rows from a database query to avoid materializing the full result in memory.
- **Event subscriptions**: Client subscribes to a topic and receives events as they happen.

---

## Client-Streaming RPC

The client sends multiple request messages while the server listens. When the client finishes, the server processes the accumulated data and returns a single response.

### Proto Definition

The `stream` keyword on the request type declares a client-streaming method:

```protobuf
service OrderService {
  rpc UpdateOrders(stream Order) returns (OrderSummary);
}

message OrderSummary {
  int32 updated_count = 1;
  float total_value   = 2;
}
```

### Server Implementation (Go)

The server calls `Recv()` in a loop until the client signals completion with `io.EOF`. It then sends the single response via `SendAndClose()`.

```go
func (s *server) UpdateOrders(stream pb.OrderService_UpdateOrdersServer) error {
    var count int32
    var total float32

    for {
        order, err := stream.Recv()
        if err == io.EOF {
            // Client finished sending. Return the aggregated result.
            return stream.SendAndClose(&pb.OrderSummary{
                UpdatedCount: count,
                TotalValue:   total,
            })
        }
        if err != nil {
            return status.Errorf(codes.Internal, "error reading stream: %v", err)
        }

        // Process each incoming order.
        s.orders[order.Id] = order
        count++
        total += order.Price
    }
}
```

### Client Implementation (Go)

The client calls `Send()` for each message, then calls `CloseAndRecv()` to signal completion and receive the server's response.

```go
stream, err := client.UpdateOrders(ctx)
if err != nil {
    log.Fatalf("failed to open stream: %v", err)
}

orders := []*pb.Order{
    {Id: "1", Description: "Laptop", Price: 1200.00},
    {Id: "2", Description: "Phone",  Price: 800.00},
    {Id: "3", Description: "Tablet", Price: 450.00},
}

for _, order := range orders {
    if err := stream.Send(order); err != nil {
        log.Fatalf("failed to send order: %v", err)
    }
}

summary, err := stream.CloseAndRecv()
if err != nil {
    log.Fatalf("error receiving summary: %v", err)
}
log.Printf("Updated %d orders, total value: %.2f", summary.UpdatedCount, summary.TotalValue)
```

### Use Cases

- **File upload**: Stream file chunks to the server, receive a confirmation with metadata.
- **Batch processing**: Submit a batch of records for bulk insertion or update.
- **Aggregation**: Send a series of data points; server returns computed statistics.
- **IoT telemetry**: Devices stream sensor readings; server acknowledges with a summary.

---

## Bidirectional-Streaming RPC

Both client and server send streams of messages independently. The two streams operate over a single HTTP/2 connection and can read and write in any order. The client initiates the call and both sides can send messages at any time.

### Proto Definition

The `stream` keyword appears on both the request and response:

```protobuf
service OrderService {
  rpc ProcessOrders(stream OrderRequest) returns (stream OrderStatus);
}

message OrderRequest {
  string id     = 1;
  string action = 2;  // "validate", "process", "ship"
}

message OrderStatus {
  string id     = 1;
  string status = 2;
  string detail = 3;
}
```

### Server Implementation (Go)

The server reads from the client stream and writes to the response stream. The read and write operations are independent; the server does not need to wait for all client messages before sending responses.

```go
func (s *server) ProcessOrders(stream pb.OrderService_ProcessOrdersServer) error {
    for {
        req, err := stream.Recv()
        if err == io.EOF {
            // Client has closed its send side.
            return nil
        }
        if err != nil {
            return status.Errorf(codes.Internal, "recv error: %v", err)
        }

        // Process the request and send a status back immediately.
        result := processOrder(req)
        if err := stream.Send(result); err != nil {
            return status.Errorf(codes.Internal, "send error: %v", err)
        }
    }
}
```

### Client Implementation (Go)

The client typically uses separate goroutines for sending and receiving, since both operations can proceed concurrently.

```go
stream, err := client.ProcessOrders(ctx)
if err != nil {
    log.Fatalf("failed to open bidi stream: %v", err)
}

// Send goroutine.
var wg sync.WaitGroup
wg.Add(1)
go func() {
    defer wg.Done()
    requests := []*pb.OrderRequest{
        {Id: "1", Action: "validate"},
        {Id: "2", Action: "process"},
        {Id: "3", Action: "ship"},
    }
    for _, req := range requests {
        if err := stream.Send(req); err != nil {
            log.Printf("send error: %v", err)
            return
        }
    }
    // Signal that the client is done sending.
    stream.CloseSend()
}()

// Receive loop runs on the main goroutine.
for {
    resp, err := stream.Recv()
    if err == io.EOF {
        break
    }
    if err != nil {
        log.Fatalf("recv error: %v", err)
    }
    log.Printf("Order %s: %s (%s)", resp.Id, resp.Status, resp.Detail)
}
wg.Wait()
```

### Use Cases

- **Chat applications**: Both participants send and receive messages freely.
- **Real-time collaboration**: Concurrent edits streamed in both directions.
- **Interactive processing**: Client sends work items, server replies with results as they complete, potentially out of order.
- **Gaming**: Player actions stream to the server; game state updates stream back.
- **Monitoring dashboards**: Client sends filter/subscription changes; server pushes matching events.

---

## Stream Lifecycle: Headers, Messages, Trailers, Status

Every gRPC call, regardless of pattern, follows the same HTTP/2 frame structure:

```
Client                                        Server
  |                                              |
  |──── HEADERS (method, metadata) ────────────>│
  |──── DATA (request message 1) ──────────────>│
  |──── DATA (request message N) ──────────────>│  (client streaming/bidi)
  |──── END_STREAM (half-close) ───────────────>│
  |                                              |
  |<──── HEADERS (initial metadata) ────────────│
  |<──── DATA (response message 1) ─────────────│
  |<──── DATA (response message N) ─────────────│  (server streaming/bidi)
  |<──── HEADERS (trailers: status, message) ───│
  |                                              |
```

**Headers** carry the RPC method path (`/package.Service/Method`), content-type (`application/grpc`), timeout, authentication tokens, and custom metadata key-value pairs.

**Messages** are length-prefixed protobuf payloads in DATA frames. The length prefix is a 1-byte compression flag followed by a 4-byte big-endian message length.

**Trailers** are sent as a final HEADERS frame with the END_STREAM flag. They carry `grpc-status` (the status code integer) and `grpc-message` (a human-readable error string). Custom trailer metadata can also be attached.

The client can read initial metadata (headers) with `stream.Header()` and trailing metadata with `stream.Trailer()` after the stream closes:

```go
// Reading metadata from a server-streaming call.
stream, _ := client.SearchOrders(ctx, query)
header, _ := stream.Header()
log.Printf("Server version: %s", header.Get("x-server-version"))

// After stream completes:
trailer := stream.Trailer()
log.Printf("Request ID: %s", trailer.Get("x-request-id"))
```

---

## Error Handling Across Patterns

### Unary RPC

Errors are returned directly. The client checks the error with `status.FromError()`:

```go
order, err := client.GetOrder(ctx, req)
if err != nil {
    st, ok := status.FromError(err)
    if ok {
        switch st.Code() {
        case codes.NotFound:
            log.Printf("Order not found: %s", st.Message())
        case codes.DeadlineExceeded:
            log.Printf("Request timed out")
        default:
            log.Printf("RPC error: %s", st.Message())
        }
    }
}
```

### Server-Streaming RPC

Errors surface during `Recv()`. The stream terminates immediately. Any error other than `io.EOF` indicates a failure:

```go
for {
    order, err := stream.Recv()
    if err == io.EOF {
        break // Clean completion.
    }
    if err != nil {
        // Stream terminated with an error. Extract status details.
        st, _ := status.FromError(err)
        log.Printf("Stream error after partial results: code=%s msg=%s", st.Code(), st.Message())
        break
    }
}
```

### Client-Streaming RPC

If the server encounters an error mid-stream, the client discovers it when calling `CloseAndRecv()` or when a subsequent `Send()` fails:

```go
for _, order := range orders {
    if err := stream.Send(order); err != nil {
        // Server may have closed the stream early.
        log.Printf("Send failed: %v", err)
        break
    }
}
summary, err := stream.CloseAndRecv()
if err != nil {
    st, _ := status.FromError(err)
    log.Printf("Server rejected batch: code=%s msg=%s", st.Code(), st.Message())
}
```

### Bidirectional-Streaming RPC

Either side can fail independently. The receive loop is typically the place where server errors surface. Context cancellation terminates both directions:

```go
ctx, cancel := context.WithCancel(context.Background())
defer cancel()

// If recv encounters an error, cancel the context to stop sends.
resp, err := stream.Recv()
if err != nil && err != io.EOF {
    cancel() // Propagate cancellation to the send goroutine.
}
```

### Rich Error Details

gRPC supports attaching structured error details using `google.rpc.Status` and the `errdetails` package:

```go
import "google.golang.org/genproto/googleapis/rpc/errdetails"

st := status.New(codes.InvalidArgument, "invalid order")
detailed, _ := st.WithDetails(&errdetails.BadRequest_FieldViolation{
    Field:       "price",
    Description: "price must be positive",
})
return nil, detailed.Err()
```

---

## Flow Control and Backpressure

gRPC inherits HTTP/2 flow control, which prevents a fast sender from overwhelming a slow receiver. This operates at two levels:

**Connection-level flow control** limits the total unacknowledged data across all streams on a single HTTP/2 connection. The default window is 65,535 bytes but gRPC typically increases it.

**Stream-level flow control** limits unacknowledged data on each individual RPC stream. When the receiver's window fills, the sender blocks until the receiver processes data and sends WINDOW_UPDATE frames.

In practice, this means:

- `Send()` blocks when the receiver's buffer is full. This is the primary backpressure mechanism.
- `Recv()` implicitly acknowledges data, releasing flow-control window capacity.
- The application does not need to manage flow control manually; gRPC and HTTP/2 handle it transparently.

You can tune the initial window sizes when creating a server or client:

```go
server := grpc.NewServer(
    grpc.InitialWindowSize(1 << 20),     // 1 MB per-stream window
    grpc.InitialConnWindowSize(1 << 20), // 1 MB per-connection window
)

conn, _ := grpc.Dial(addr,
    grpc.WithInitialWindowSize(1 << 20),
    grpc.WithInitialConnWindowSize(1 << 20),
)
```

For application-level flow control in bidirectional streams, use a semaphore or channel to limit in-flight work:

```go
sem := make(chan struct{}, 10) // Max 10 concurrent items in flight.

for {
    req, err := stream.Recv()
    if err == io.EOF { break }

    sem <- struct{}{}
    go func(r *pb.OrderRequest) {
        defer func() { <-sem }()
        result := processOrder(r)
        stream.Send(result) // Thread-safe in gRPC-Go.
    }(req)
}
```

---

## Microservices Communication Patterns

### Choosing the Right Pattern

| Scenario | Pattern | Rationale |
|----------|---------|-----------|
| Get user profile | Unary | Single request, single response, low latency |
| List all orders for a user | Server streaming | Result set may be large; stream avoids buffering |
| Upload a document | Client streaming | Document sent in chunks; server confirms on completion |
| Collaborative editing | Bidi streaming | Both sides send updates independently |
| Health check | Unary | Simple boolean liveness/readiness check |
| Event notification | Server streaming | Server pushes events as they occur |
| Batch data ingestion | Client streaming | Client sends many records; server responds with summary |
| Interactive search | Bidi streaming | Client refines queries as server returns partial results |

### Service-to-Service Design Guidelines

**Keep unary RPCs as the default.** Most service interactions are simple request-response. Unary RPCs are easiest to reason about, test, retry, and observe. Only introduce streaming when there is a clear benefit.

**Use server streaming for push-based delivery.** When a client would otherwise poll repeatedly, a server stream reduces latency and network overhead. The server pushes updates the moment they are available.

**Use client streaming for upload and aggregation.** When the client has a large or unbounded amount of data to send, client streaming avoids constructing a single enormous request message. The server processes data incrementally.

**Reserve bidirectional streaming for truly interactive flows.** Bidi streaming adds complexity to error handling, flow control, and observability. Use it when both sides genuinely need to send data independently and concurrently, such as chat or real-time collaborative tools.

**Design idempotent operations where possible.** Streaming RPCs are harder to retry than unary calls. If a stream fails partway through, the client needs to know which messages were processed. Including request IDs or sequence numbers in stream messages enables safe retries and deduplication on the server.

**Set deadlines on every call.** Even streaming RPCs should have deadlines. A long-running stream should use a generous but finite deadline, or implement application-level keepalive messages to detect stalled connections:

```go
ctx, cancel := context.WithTimeout(context.Background(), 30*time.Minute)
defer cancel()

stream, err := client.ProcessOrders(ctx)
```

**Use metadata for cross-cutting concerns.** Authentication tokens, trace IDs, and request IDs travel in gRPC metadata (HTTP/2 headers), keeping the protobuf messages focused on business data:

```go
md := metadata.Pairs("x-request-id", uuid.New().String())
ctx := metadata.NewOutgoingContext(ctx, md)
stream, err := client.ProcessOrders(ctx)
```
