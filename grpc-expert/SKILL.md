---
name: grpc-expert
description: >
  Expert-level gRPC assistance covering protocol buffers, service definitions,
  communication patterns, HTTP/2 internals, security, and production deployment.
  Use when the user is working with gRPC, protocol buffers (protobuf), .proto
  files, protoc compiler, gRPC services, unary RPCs, server streaming, client
  streaming, bidirectional streaming, gRPC interceptors, gRPC metadata, gRPC
  deadlines, gRPC cancellation, gRPC error handling, gRPC status codes,
  gRPC load balancing, gRPC name resolution, gRPC-Go, gRPC-Java, gRPC-Python,
  gRPC-Web, tonic (Rust gRPC), grpcurl, gRPC reflection, gRPC health checking,
  gRPC gateway, HTTP/JSON transcoding, channel credentials, call credentials,
  TLS for gRPC, mTLS for gRPC, or any gRPC-related API design and implementation.
  Also triggers on discussions of protobuf message design, protobuf encoding,
  varints, proto3 syntax, service mesh gRPC support, Envoy gRPC, gRPC
  middleware, connect-go, buf CLI, or inter-service communication using gRPC.
---

# gRPC Expert

## Core Concept

gRPC is a high-performance, open-source **remote procedure call (RPC) framework** that uses **Protocol Buffers** as its interface definition language and serialization format, and **HTTP/2** as its transport protocol. It enables efficient, type-safe communication between services across languages and platforms.

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                      gRPC Architecture                        │
│                                                               │
│  ┌─────────────┐          HTTP/2           ┌─────────────┐   │
│  │  gRPC Client │◄────────────────────────►│  gRPC Server │   │
│  │             │   Protocol Buffers        │             │   │
│  │  Generated  │   (binary encoding)       │  Generated  │   │
│  │  Stub       │                           │  Service     │   │
│  │             │   Frames:                 │  Skeleton    │   │
│  │  Channel ───┼──► HEADERS (metadata)     │             │   │
│  │             │   DATA (protobuf msg)     │  Service     │   │
│  │  Interceptors│   HEADERS (trailers)     │  Impl        │   │
│  └─────────────┘                           └─────────────┘   │
│                                                               │
│  .proto file ──► protoc ──► Generated code (any language)     │
└──────────────────────────────────────────────────────────────┘
```

## Communication Patterns

| Pattern | Client | Server | Use Case |
|---------|--------|--------|----------|
| **Unary** | 1 request | 1 response | Simple request-response (most common) |
| **Server streaming** | 1 request | N responses | Real-time feeds, large result sets |
| **Client streaming** | N requests | 1 response | File upload, aggregation |
| **Bidirectional streaming** | N requests | N responses | Chat, real-time collaboration |

```protobuf
service OrderService {
  rpc GetOrder(OrderRequest) returns (Order);                        // Unary
  rpc SearchOrders(SearchQuery) returns (stream Order);              // Server streaming
  rpc UpdateOrders(stream OrderUpdate) returns (OrderSummary);       // Client streaming
  rpc ProcessOrders(stream OrderRequest) returns (stream OrderStatus); // Bidi streaming
}
```

## Protocol Buffers Quick Reference

```protobuf
syntax = "proto3";

package ecommerce;
option go_package = "ecommerce/";
option java_package = "com.example.ecommerce";

message Product {
  string   id          = 1;
  string   name        = 2;
  float    price       = 3;
  repeated string tags = 4;    // list
  optional string desc = 5;    // explicit presence tracking
  ProductType type     = 6;

  oneof promotion {             // only one can be set
    string  coupon_code = 7;
    float   discount    = 8;
  }
}

enum ProductType {
  PRODUCT_TYPE_UNSPECIFIED = 0;
  ELECTRONICS             = 1;
  CLOTHING                = 2;
}
```

**Scalar types:** `double`, `float`, `int32`, `int64`, `uint32`, `uint64`, `sint32`, `sint64`, `fixed32`, `fixed64`, `sfixed32`, `sfixed64`, `bool`, `string`, `bytes`

## gRPC Status Codes

| Code | Name | When to Use |
|------|------|-------------|
| 0 | `OK` | Success |
| 1 | `CANCELLED` | Client cancelled the request |
| 2 | `UNKNOWN` | Unknown error (default for exceptions) |
| 3 | `INVALID_ARGUMENT` | Bad request parameters |
| 4 | `DEADLINE_EXCEEDED` | Timeout before completion |
| 5 | `NOT_FOUND` | Resource does not exist |
| 6 | `ALREADY_EXISTS` | Resource already exists |
| 7 | `PERMISSION_DENIED` | Caller lacks permission |
| 8 | `RESOURCE_EXHAUSTED` | Rate limited or quota exceeded |
| 9 | `FAILED_PRECONDITION` | System not in required state |
| 10 | `ABORTED` | Concurrency conflict |
| 11 | `OUT_OF_RANGE` | Value outside valid range |
| 12 | `UNIMPLEMENTED` | Method not implemented |
| 13 | `INTERNAL` | Internal server error |
| 14 | `UNAVAILABLE` | Service temporarily unavailable (retry) |
| 16 | `UNAUTHENTICATED` | Missing or invalid authentication |

## Essential Tools

| Tool | Purpose |
|------|---------|
| `protoc` | Protocol Buffer compiler — generates code from .proto files |
| `buf` | Modern protobuf toolchain — linting, breaking change detection, BSR |
| `grpcurl` | curl for gRPC — CLI tool to invoke gRPC services |
| `grpc_health_probe` | Health check probe for Kubernetes gRPC services |
| `evans` | Interactive gRPC client with REPL |
| `ghz` | gRPC benchmarking and load testing tool |
| `grpc-gateway` | Generates reverse proxy for REST JSON to gRPC |
| `connect-go` | Connect protocol — gRPC-compatible with browser support |

## gRPC vs REST Comparison

| Dimension | gRPC | REST (JSON/HTTP) |
|-----------|------|------------------|
| **Protocol** | HTTP/2 | HTTP/1.1 or HTTP/2 |
| **Serialization** | Protocol Buffers (binary) | JSON (text) |
| **Contract** | .proto file (strict) | OpenAPI/Swagger (optional) |
| **Streaming** | Native (4 patterns) | Limited (SSE, WebSocket) |
| **Code generation** | Built-in, multi-language | Third-party tools |
| **Browser support** | Via gRPC-Web or Connect | Native |
| **Performance** | Higher throughput, lower latency | More overhead |
| **Human readable** | No (binary on wire) | Yes |

## Reference Documents

Load these as needed based on the specific topic:

| Topic | File | When to read |
|-------|------|-------------|
| **Introduction** | [references/introduction.md](references/introduction.md) | What gRPC is, why it exists, service definitions, client-server flow, gRPC vs other protocols, real-world use cases (Ch 1) |
| **Getting Started** | [references/getting-started.md](references/getting-started.md) | Writing .proto files, protobuf messages and services, building gRPC server and client in Go and Java, compiling and running (Ch 2) |
| **Communication Patterns** | [references/communication-patterns.md](references/communication-patterns.md) | Unary RPC, server streaming, client streaming, bidirectional streaming, microservices communication patterns (Ch 3) |
| **Under the Hood** | [references/under-the-hood.md](references/under-the-hood.md) | RPC flow internals, protocol buffer encoding (varints, wire types), HTTP/2 framing, message flow for all patterns (Ch 4) |
| **Advanced Features** | [references/advanced.md](references/advanced.md) | Interceptors, deadlines, cancellation, error handling, multiplexing, metadata, name resolution, load balancing, compression (Ch 5) |
| **Security** | [references/security.md](references/security.md) | TLS, one-way TLS, mTLS, channel credentials, call credentials, basic auth, OAuth 2.0, JWT, Google token-based auth (Ch 6) |
| **Production** | [references/production.md](references/production.md) | Testing, load testing, CI/CD, Docker deployment, Kubernetes deployment, observability (metrics, logs, tracing), debugging (Ch 7) |
| **Ecosystem** | [references/ecosystem.md](references/ecosystem.md) | gRPC Gateway, HTTP/JSON transcoding, server reflection, gRPC middleware, health checking protocol, health probe, ecosystem projects (Ch 8) |
