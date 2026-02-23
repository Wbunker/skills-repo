# gRPC Under the Hood

## RPC Flow: Lifecycle of a gRPC Call

**1. Channel creation.** The client establishes a `Channel` -- a long-lived connection (or pool) managing DNS resolution, load balancing, TLS, and HTTP/2 setup. Channels are reused across RPCs.

**2. Stub invocation.** The client calls a method on a generated stub, which packages the method as `/{package}.{ServiceName}/{MethodName}` with call metadata (headers, deadline, compression).

**3. Serialization.** The request is serialized via Protocol Buffers, then wrapped in gRPC's length-prefixed frame: 1-byte compressed flag + 4-byte big-endian message length + message bytes.

**4. HTTP/2 framing.** The client opens an HTTP/2 stream, sends a HEADERS frame with request metadata, then DATA frame(s) with the length-prefixed message. For unary and server-streaming calls, END_STREAM is set on the last DATA frame.

**5. Server processing.** The server extracts, deserializes, and dispatches to the service method handler.

**6. Response.** The server serializes and length-prefixes the response, sends DATA frames on the same stream, then trailers (HEADERS with END_STREAM) containing `grpc-status` and optionally `grpc-message`.

**7. Client completion.** The client deserializes the response, reads trailers for status, and returns the result or error.

## Message Encoding with Protocol Buffers

### Field Tags and Wire Types

Each field is prefixed by a varint tag encoding `(field_number << 3) | wire_type`. The wire type tells the parser how to read the value:

| Wire Type | ID | Used For |
|---|---|---|
| Varint | 0 | int32, int64, uint32, uint64, sint32, sint64, bool, enum |
| 64-bit | 1 | fixed64, sfixed64, double |
| Length-delimited | 2 | string, bytes, embedded messages, packed repeated fields |
| 32-bit | 5 | fixed32, sfixed32, float |

### Varint Encoding

Each byte uses 7 bits for data and the MSB as a continuation flag (1 = more bytes, 0 = last byte), in little-endian order. Example: 300 encodes as `0xAC 0x02` -- binary `10101100 00000010`, drop MSBs to get `0101100 0000010`, reverse groups: `0000010_0101100` = 300.

**ZigZag encoding** for `sint32`/`sint64` maps signed integers so small absolute values have small encodings: `ZigZag(n) = (n << 1) ^ (n >> 31)`. This maps 0->0, -1->1, 1->2, -2->3. Without ZigZag, negative int32 values always consume 10 bytes.

### String, Bytes, and Nested Messages

All use wire type 2 (length-delimited): tag varint, byte-length varint, raw bytes. Strings must be valid UTF-8. Nested messages are serialized independently and embedded as length-delimited bytes, allowing arbitrary nesting.

Example -- `"gRPC"` in field 1: `0A 04 67525043` (tag `0x0A` = field 1 wire type 2, length 4, UTF-8 bytes).

### Repeated Fields and Maps

**Packed** (default for scalar numerics in proto3): one tag, total byte length, then all values concatenated. Example -- repeated int32 `[1,2,3]` in field 4: `22 03 01 02 03`.

**Unpacked**: each element gets its own tag-value pair (used for strings, bytes, messages).

**Maps** are syntactic sugar for repeated entries of a synthetic message with `key` (field 1) and `value` (field 2). No guaranteed wire ordering.

### Default Values and Field Presence

Proto3 omits fields set to default values (zero, empty string, false), so receivers cannot distinguish "explicitly set to default" from "not set." A message with all defaults serializes to zero bytes. The `optional` keyword (proto3.15+) restores presence tracking with `has_*` methods.

### Why Protobuf Beats JSON

**Size.** JSON repeats field names as strings and encodes numbers as decimal text. Protobuf uses integer tags (1-2 bytes) and binary varints. A message like `{"userId":12345,"name":"Alice","active":true}` is ~45 bytes in JSON vs ~13 bytes in protobuf -- a 60-70% reduction.

**Speed.** Protobuf parsing is a linear scan: read varint tag, dispatch on field number, read known-length value. No tokenization, no string matching, no escape processing. JSON requires character-by-character scanning, key comparison, and decimal number parsing.

## gRPC over HTTP/2

### HTTP/2 Fundamentals

**Binary framing.** All communication is split into typed frames (DATA, HEADERS, SETTINGS, WINDOW_UPDATE, etc.) with a stream identifier and flags.

**Multiplexing.** Multiple streams share one TCP connection, eliminating application-layer head-of-line blocking. Each gRPC call maps to one stream.

**HPACK header compression.** A dynamic table on both sides indexes recently seen header pairs. Repeated headers like `:method POST` or `content-type: application/grpc` compress to 1-2 byte indices.

### gRPC-to-HTTP/2 Mapping

| gRPC Concept | HTTP/2 Concept |
|---|---|
| Channel | TCP connection(s) |
| RPC call | Stream |
| Request/response metadata | HEADERS frame |
| Request/response message | DATA frame(s) |
| Status and trailers | HEADERS frame (trailers) |

### Request Headers

The initial HEADERS frame contains: `:method POST`, `:path /{package}.{Service}/{Method}`, `:authority`, `:scheme`, `content-type: application/grpc`, `te: trailers`, `grpc-timeout` (e.g., `1S`, `100m`, `200u`), `grpc-encoding` (e.g., `gzip`), `user-agent`, and any custom metadata (binary values use `-bin` suffix with base64).

### Length-Prefixed Message Framing

```
+------------------+----------------------------+------------------------+
| Compressed Flag  |     Message Length          |     Message Bytes      |
|    (1 byte)      |   (4 bytes, big-endian)    |    (variable length)   |
+------------------+----------------------------+------------------------+
```

This framing is necessary because HTTP/2 DATA frames can be split or coalesced arbitrarily. The length prefix lets gRPC reconstruct message boundaries independent of frame boundaries.

### Response Trailers

After all response messages, the server sends trailers with END_STREAM: `grpc-status` (integer code, 0 = OK), `grpc-message` (percent-encoded error text), and optional custom trailing metadata. Trailers are essential because the final RPC status is unknown until all messages are sent.

### Connection Management

**Keepalive.** HTTP/2 PING frames detect dead connections. Configurable via `GRPC_KEEPALIVE_TIME_MS` and `GRPC_KEEPALIVE_TIMEOUT_MS`.

**Idle timeout.** Connections with no active RPCs are closed after `GRPC_MAX_CONNECTION_IDLE_MS` via GOAWAY.

**Max concurrent streams.** `SETTINGS_MAX_CONCURRENT_STREAMS` limits multiplexed RPCs. When reached, new RPCs queue or trigger additional connections.

**GOAWAY.** The server sends GOAWAY with the last stream ID it will process. In-flight RPCs complete; new RPCs use a fresh connection.

## Message Flow in Communication Patterns

### Unary RPC

```
Client                              Server
  |-- HEADERS (:path, metadata) -->   |
  |-- DATA (request msg) ---------->  |    END_STREAM
  |                                   |
  |  <-- HEADERS (response metadata)--|
  |  <-- DATA (response msg) --------|
  |  <-- HEADERS (trailers) ---------|    END_STREAM
```

### Server Streaming RPC

```
Client                              Server
  |-- HEADERS (:path, metadata) -->   |
  |-- DATA (request msg) ---------->  |    END_STREAM
  |                                   |
  |  <-- HEADERS (response metadata)--|
  |  <-- DATA (response msg 1) ------|
  |  <-- DATA (response msg 2) ------|
  |  <-- DATA (response msg N) ------|
  |  <-- HEADERS (trailers) ---------|    END_STREAM
```

### Client Streaming RPC

```
Client                              Server
  |-- HEADERS (:path, metadata) -->   |
  |-- DATA (request msg 1) -------->  |
  |-- DATA (request msg 2) -------->  |
  |-- DATA (request msg N) -------->  |    END_STREAM
  |                                   |
  |  <-- HEADERS (response metadata)--|
  |  <-- DATA (response msg) --------|
  |  <-- HEADERS (trailers) ---------|    END_STREAM
```

### Bidirectional Streaming RPC

```
Client                              Server
  |-- HEADERS (:path, metadata) -->   |
  |-- DATA (request msg 1) -------->  |
  |  <-- HEADERS (response metadata)--|
  |  <-- DATA (response msg 1) ------|
  |-- DATA (request msg 2) -------->  |
  |  <-- DATA (response msg 2) ------|
  |-- DATA (request msg 3) -------->  |    END_STREAM
  |  <-- DATA (response msg 3) ------|
  |  <-- HEADERS (trailers) ---------|    END_STREAM
```

Both sides send DATA frames independently. The server need not wait for all client messages. The stream closes when both sides set END_STREAM.

## HTTP/2 Flow Control and gRPC Streaming

HTTP/2 flow control uses WINDOW_UPDATE frames at two levels:

**Per-stream windows** prevent a slow consumer on one stream from stalling others. If a streaming RPC's receiver falls behind, only that stream's window fills; other RPCs are unaffected.

**Per-connection windows** cap total unacknowledged data across all streams, preventing memory exhaustion.

**Backpressure.** When a streaming producer outpaces its consumer, the window fills and `Send` blocks. In bidirectional streaming, deadlocks can occur if both sides block waiting for the other to consume. Applications must be aware that sends are not instantaneous.

**Window sizing.** The HTTP/2 default is 65,535 bytes. gRPC implementations typically increase this via SETTINGS. High-throughput streaming benefits from 1-16 MB windows to reduce WINDOW_UPDATE round-trips. Some implementations (notably gRPC-Go) dynamically estimate bandwidth-delay product (BDP) and auto-tune the window.

## Connection Pooling and Multiplexing

A single HTTP/2 connection supports hundreds of concurrent streams, eliminating large connection pools.

**Default behavior.** Most gRPC implementations use one HTTP/2 connection per channel. All RPCs multiplex over it.

**Scaling beyond one connection.** A single TCP connection is bounded by `MAX_CONCURRENT_STREAMS` and the TCP congestion window. TCP-level head-of-line blocking (resolved by HTTP/3/QUIC) can bottleneck throughput. Solutions: multiple connections per channel, multiple channels, or an L7 load balancer.

**Subchannels.** A channel manages subchannels, each a connection to a backend address. The load balancer (pick-first, round-robin, or custom) selects a subchannel per RPC. Each handles reconnection with exponential backoff and jitter.

**Resource cost.** Each connection consumes a TCP socket, TLS state, HPACK tables (~4 KB per direction), and flow control buffers.
