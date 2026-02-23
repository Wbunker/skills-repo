# Design, Build, and Specify APIs

This reference covers the foundational decisions in API architecture: selecting an API style, designing resource models, specifying contracts with OpenAPI, and managing versioning across the lifecycle of a service.

## Introduction to REST

REST (Representational State Transfer) is an architectural style defined by Roy Fielding in his 2000 doctoral dissertation. It is not a protocol or a specification but a set of constraints that, when followed, produce systems with desirable properties like scalability, simplicity, and independent evolvability.

### Core Constraints

**Stateless.** Each request from client to server must contain all the information necessary to understand and process the request. The server holds no session state between requests. This constraint enables horizontal scaling because any server instance can handle any request.

**Client-Server.** The client and server are independent components that communicate over a well-defined interface. The client does not concern itself with data storage; the server does not concern itself with user interface. This separation allows each to evolve independently.

**Cacheable.** Responses must implicitly or explicitly label themselves as cacheable or non-cacheable. When a response is cacheable, the client (or intermediary) may reuse that response for equivalent future requests. Proper cache headers (`Cache-Control`, `ETag`, `Last-Modified`) are essential to this constraint.

**Uniform Interface.** This is the distinguishing constraint of REST. It mandates four sub-constraints: identification of resources through URIs, manipulation of resources through representations, self-descriptive messages, and hypermedia as the engine of application state (HATEOAS). The uniform interface simplifies architecture but can reduce efficiency for certain interaction patterns.

**Layered System.** A client cannot tell whether it is connected directly to the end server or to an intermediary. Layers such as load balancers, caches, and API gateways can be inserted transparently, improving scalability and enforcing security policies.

**Code on Demand (optional).** Servers may extend client functionality by transferring executable code, such as JavaScript. This is the only optional constraint.

### Resource-Based Design

In REST, the fundamental abstraction is the resource. A resource is any concept that can be named and addressed: a customer, an order, a product catalog entry. Resources are identified by URIs and manipulated through representations, typically JSON or XML documents that capture the current or intended state of the resource.

Good resource modeling starts by identifying the nouns in your domain, not the verbs. Instead of `/createOrder`, you expose `/orders` and use HTTP methods to express the operation.

## REST and HTTP by Example

HTTP provides the protocol vocabulary that maps naturally onto REST constraints. Understanding the semantics of methods, status codes, and headers is essential to building correct APIs.

### HTTP Methods

```
GET /products/8742
```

**GET** retrieves a representation of a resource. It must be safe (no side effects) and idempotent (multiple identical requests produce the same result). Responses to GET requests are cacheable by default.

```
POST /orders
Content-Type: application/json

{
  "product_id": 8742,
  "quantity": 2,
  "shipping_address_id": 301
}
```

**POST** submits data to a resource, typically creating a new subordinate resource. It is neither safe nor idempotent. A successful creation returns `201 Created` with a `Location` header pointing to the new resource.

```
PUT /orders/1055
Content-Type: application/json

{
  "product_id": 8742,
  "quantity": 3,
  "shipping_address_id": 301
}
```

**PUT** replaces the entire resource at the given URI. It is idempotent: sending the same PUT request multiple times produces the same server state. If the resource does not exist, PUT may create it.

```
PATCH /orders/1055
Content-Type: application/merge-patch+json

{
  "quantity": 4
}
```

**PATCH** applies a partial modification. Unlike PUT, only the fields included in the request body are updated. RFC 7396 defines JSON Merge Patch; RFC 6902 defines JSON Patch with explicit operations (add, remove, replace).

```
DELETE /orders/1055
```

**DELETE** removes the resource. It is idempotent: deleting an already-deleted resource returns the same outcome (typically `204 No Content` or `404 Not Found` on subsequent calls, depending on your convention).

### Status Codes

Correct use of status codes communicates outcome semantics without requiring clients to parse response bodies:

| Range | Meaning | Common Codes |
|-------|---------|-------------|
| 2xx | Success | `200 OK`, `201 Created`, `204 No Content` |
| 3xx | Redirection | `301 Moved Permanently`, `304 Not Modified` |
| 4xx | Client error | `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `409 Conflict`, `422 Unprocessable Entity`, `429 Too Many Requests` |
| 5xx | Server error | `500 Internal Server Error`, `502 Bad Gateway`, `503 Service Unavailable` |

### Headers and Content Negotiation

The `Accept` header allows clients to indicate their preferred representation format. The server responds with the best match and declares it in `Content-Type`:

```
GET /products/8742 HTTP/1.1
Accept: application/json, application/xml;q=0.9

HTTP/1.1 200 OK
Content-Type: application/json
ETag: "a1b2c3"
Cache-Control: max-age=3600
```

Content negotiation enables a single resource URI to serve multiple representation formats, keeping the uniform interface clean.

## The Richardson Maturity Model

Leonard Richardson proposed a maturity model that classifies APIs by how fully they use HTTP. It provides a useful lens for evaluating API design, though reaching Level 3 is not always the right goal.

### Level 0: The Swamp of POX

A single URI serves as a tunnel for all operations. HTTP is used purely as a transport mechanism. The method is always POST, and the operation is encoded in the request body.

```
POST /api
Content-Type: application/xml

<getProduct id="8742"/>
```

SOAP and XML-RPC services typically operate at this level. There is no use of HTTP semantics beyond basic transport.

### Level 1: Resources

Individual resources get their own URIs, but all interactions still use a single HTTP method (typically POST).

```
POST /products/8742
POST /orders
```

The improvement over Level 0 is addressability: each resource has a distinct identity. However, the semantics of the operation remain opaque.

### Level 2: HTTP Verbs

Operations are expressed using the correct HTTP methods. GET is used for reads, POST for creation, PUT/PATCH for updates, DELETE for removal. Status codes are used correctly.

```
GET  /products/8742      -> 200 OK
POST /orders             -> 201 Created
PUT  /orders/1055        -> 200 OK
DELETE /orders/1055      -> 204 No Content
```

Most production REST APIs operate at this level. It provides clear semantics and enables caching, idempotency, and safety guarantees.

### Level 3: Hypermedia Controls (HATEOAS)

Responses include hypermedia links that tell clients what actions are available and how to invoke them. The API becomes self-describing and discoverable.

```json
{
  "id": 1055,
  "status": "pending",
  "total": 59.98,
  "_links": {
    "self": { "href": "/orders/1055" },
    "cancel": { "href": "/orders/1055", "method": "DELETE" },
    "payment": { "href": "/orders/1055/payment", "method": "POST" }
  }
}
```

HATEOAS decouples clients from hard-coded URI structures and enables servers to evolve their URI schemes without breaking clients. In practice, adoption is limited because most API consumers prefer documented, stable URL patterns over runtime discovery.

## Introduction to RPC APIs

Remote Procedure Call (RPC) APIs model interactions as function invocations rather than resource manipulations. The client calls a named procedure on the server, passing arguments and receiving a result.

### When RPC Is More Appropriate

RPC fits naturally when the interaction is action-oriented rather than resource-oriented. Examples include triggering a build pipeline, sending a notification, or performing a complex calculation. If you find yourself inventing artificial resources to wrap procedural operations, RPC may be the more honest design.

RPC also excels in service-to-service communication within a microservices architecture, where the overhead of REST conventions (content negotiation, hypermedia, broad status code usage) provides little benefit and the performance characteristics of binary protocols matter.

### gRPC Basics

gRPC is a high-performance RPC framework built on HTTP/2 and Protocol Buffers. It uses `.proto` files to define services and message types:

```protobuf
syntax = "proto3";

service OrderService {
  rpc CreateOrder (CreateOrderRequest) returns (OrderResponse);
  rpc GetOrder (GetOrderRequest) returns (OrderResponse);
  rpc StreamUpdates (GetOrderRequest) returns (stream OrderUpdate);
}

message CreateOrderRequest {
  int64 product_id = 1;
  int32 quantity = 2;
}
```

Key advantages of gRPC: strongly typed contracts, efficient binary serialization, bidirectional streaming, and automatic code generation for many languages. The primary tradeoff is reduced human readability and limited browser support without a proxy layer (such as gRPC-Web or Envoy).

## GraphQL

GraphQL is a query language for APIs developed by Facebook. Instead of the server defining fixed response shapes, the client specifies exactly which fields it needs.

```graphql
query {
  order(id: "1055") {
    id
    status
    items {
      product { name, price }
      quantity
    }
  }
}
```

### When to Use GraphQL

GraphQL shines when clients have diverse data requirements. A mobile client may need a minimal subset of fields, while a dashboard may need deeply nested related data. GraphQL eliminates both over-fetching and under-fetching without requiring multiple endpoints or query parameter gymnastics.

### Tradeoffs vs REST

GraphQL shifts complexity from the client to the server. Caching is more difficult because requests are POST bodies rather than cacheable URLs. Authorization must be applied at the field level, not the endpoint level. Query complexity can lead to performance problems if not bounded (depth limiting, query cost analysis). Tooling for monitoring, rate limiting, and API gateway integration is less mature than for REST.

## REST API Standards and Structure

### URL Design and Resource Naming

URLs should be noun-based, use plural nouns for collections, and use path segments for hierarchy:

```
/customers                       # collection
/customers/42                    # individual resource
/customers/42/orders             # sub-collection
/customers/42/orders/1055        # nested resource
```

Conventions that improve consistency: use lowercase with hyphens for multi-word resources (`/shipping-addresses`, not `/shippingAddresses`), avoid deep nesting beyond two levels (prefer `/orders/1055?customer=42` over `/customers/42/orders/1055`), and never embed actions in the path (`/orders/1055/cancel` is a pragmatic exception when no clean resource mapping exists).

### Resource Naming Patterns

| Pattern | Example | Notes |
|---------|---------|-------|
| Collection | `GET /products` | Returns a list |
| Singleton | `GET /products/8742` | Returns one item |
| Sub-resource | `GET /products/8742/reviews` | Scoped to parent |
| Controller (action) | `POST /orders/1055/cancel` | Pragmatic RPC-style escape hatch |

## Collections and Pagination

Any collection endpoint that could return an unbounded number of results must support pagination. Three dominant strategies exist.

### Offset/Limit (Positional)

```
GET /products?offset=40&limit=20
```

Simple to implement and allows random access to any page. However, it suffers from drift: if items are inserted or deleted between requests, clients may see duplicates or miss items. Performance degrades on large offsets because the database must scan and discard `offset` rows.

### Cursor-Based

```
GET /products?after=eyJpZCI6OTk5fQ&limit=20
```

The cursor is an opaque token (often a base64-encoded identifier or timestamp) representing the position in the dataset. The server returns a `next_cursor` in the response. Cursor-based pagination is stable under concurrent writes and efficient at the database level (a `WHERE id > ?` query). The tradeoff is that clients cannot jump to an arbitrary page.

### Page-Based

```
GET /products?page=3&per_page=20
```

A simpler interface that maps naturally to user-facing pagination controls. Internally, it is equivalent to offset/limit (`offset = (page - 1) * per_page`) and inherits the same drift and performance characteristics.

### Link Headers

RFC 8288 defines web linking. Pagination links can be communicated in the `Link` header, keeping the response body free of pagination metadata:

```
Link: </products?page=4&per_page=20>; rel="next",
      </products?page=1&per_page=20>; rel="first",
      </products?page=12&per_page=20>; rel="last"
```

## Filtering Collections

### Query Parameters

Filtering on fields uses query parameters. A common convention is to use the field name directly:

```
GET /products?category=electronics&in_stock=true&min_price=25
```

For more expressive filtering, some APIs adopt an operator syntax:

```
GET /products?price[gte]=25&price[lte]=100
```

### Field Selection

Allow clients to request only the fields they need, reducing payload size:

```
GET /products?fields=id,name,price
```

This is a lightweight alternative to GraphQL's field selection for REST APIs.

### Sorting

```
GET /products?sort=-price,name
```

A leading `-` indicates descending order. Multiple sort fields are comma-separated. Document the default sort order for each collection.

## Error Handling

### RFC 7807 Problem Details

RFC 7807 (updated by RFC 9457) defines a standard JSON format for communicating errors. Adopting it provides a consistent structure that clients can parse generically:

```json
{
  "type": "https://api.example.com/problems/insufficient-funds",
  "title": "Insufficient Funds",
  "status": 422,
  "detail": "Account balance of $12.50 is less than the order total of $59.98.",
  "instance": "/orders/1055/payment",
  "balance": 12.50,
  "required": 59.98
}
```

The `Content-Type` for this response is `application/problem+json`.

**type** is a URI reference that identifies the problem type. It should be dereferenceable (i.e., a URL that returns documentation). **title** is a short human-readable summary. **status** mirrors the HTTP status code. **detail** is a human-readable explanation specific to this occurrence. **instance** identifies the specific occurrence. Additional members (`balance`, `required` above) provide machine-readable context.

### Consistent Error Format

Regardless of whether you adopt RFC 7807, consistency is paramount. Every error response from your API should use the same structure. Inconsistent error formats force clients to implement multiple parsing strategies and make debugging harder. Define your error format in your OpenAPI specification and enforce it across all endpoints.

### Status Code Usage for Errors

Use `400` for malformed requests (bad JSON, missing required fields). Use `422` for well-formed requests that violate business rules. Use `401` when authentication is missing, `403` when the authenticated user lacks permission. Use `409` for conflicts (e.g., creating a resource that already exists). Reserve `500` for genuinely unexpected server errors; never return `500` for validation failures.

## ADR: Choosing an API Standard

An Architecture Decision Record (ADR) documents the context, decision, and consequences of a significant architectural choice. Choosing an API style is one such decision.

A minimal ADR for API standard selection:

```
# ADR-001: API Style for Customer-Facing Services

## Status
Accepted

## Context
We are building a set of customer-facing services that will be consumed
by web and mobile clients with varying data requirements. We need to
choose between REST, gRPC, and GraphQL.

## Decision
We will use REST with OpenAPI 3.1 specifications for all customer-facing
APIs. Internal service-to-service communication will use gRPC where
latency and payload size are critical.

## Consequences
- REST provides broad tooling support, caching, and familiarity.
- OpenAPI enables code generation and contract testing.
- gRPC requires HTTP/2 infrastructure for internal services.
- Mobile clients may over-fetch; we will address this with field
  selection query parameters rather than adopting GraphQL.
```

ADRs are lightweight, versioned documents that live alongside the code. They prevent revisiting settled decisions and provide onboarding context for new team members.

## OpenAPI Specification

The OpenAPI Specification (OAS) is the dominant standard for describing REST APIs. Version 3.1 aligns fully with JSON Schema, resolving earlier inconsistencies.

### Structure

An OpenAPI document has four major sections:

**info** contains metadata: title, version, description, contact, and license.

**paths** maps URL paths to operations. Each operation specifies method, parameters, request body, responses, and security requirements.

**components** holds reusable definitions: schemas (data models), parameters, responses, security schemes, and examples.

**servers** lists the base URLs where the API is hosted.

```yaml
openapi: 3.1.0
info:
  title: Orders API
  version: 2.3.0

servers:
  - url: https://api.example.com/v2

paths:
  /orders:
    get:
      summary: List orders
      parameters:
        - name: status
          in: query
          schema:
            type: string
            enum: [pending, shipped, delivered]
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
            maximum: 100
      responses:
        '200':
          description: A page of orders
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OrderList'
    post:
      summary: Create an order
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateOrderRequest'
      responses:
        '201':
          description: Order created
          headers:
            Location:
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Order'
        '422':
          description: Validation error
          content:
            application/problem+json:
              schema:
                $ref: '#/components/schemas/ProblemDetail'

components:
  schemas:
    Order:
      type: object
      required: [id, status, total]
      properties:
        id:
          type: integer
          format: int64
        status:
          type: string
          enum: [pending, shipped, delivered]
        total:
          type: number
          format: double
    OrderList:
      type: object
      properties:
        items:
          type: array
          items:
            $ref: '#/components/schemas/Order'
        next_cursor:
          type: string
          nullable: true
```

## Practical OpenAPI

### Code Generation

OpenAPI specifications enable generating both server stubs and client SDKs. Tools like `openapi-generator` support dozens of languages:

```bash
# Generate a Spring Boot server stub
openapi-generator generate -i orders-api.yaml -g spring -o server/

# Generate a TypeScript client SDK
openapi-generator generate -i orders-api.yaml -g typescript-fetch -o client/
```

Code generation ensures the implementation matches the specification. Server stubs provide interface definitions that developers implement; client SDKs provide type-safe API access with request/response serialization handled automatically.

### Validation

Request and response validation against the OpenAPI schema catches contract violations early. Middleware such as `express-openapi-validator` (Node.js) or `openapi-core` (Python) intercepts requests and validates them against the spec before they reach handler code.

### Mocking

Tools like Prism (`@stoplight/prism-cli`) generate a mock server from an OpenAPI spec, returning example responses for every endpoint. This enables frontend development to proceed before backend implementation is complete:

```bash
prism mock orders-api.yaml
```

### Detecting Breaking Changes

Automated diff tools compare two versions of a specification and flag breaking changes: removed endpoints, changed parameter types, removed response fields, or altered required fields.

```bash
oasdiff breaking orders-api-v2.3.yaml orders-api-v2.4.yaml
```

Breaking changes should block CI pipelines. Non-breaking changes (adding optional fields, new endpoints) can proceed safely.

## API Versioning

### Strategies

**URL Path Versioning.** The version is embedded in the URL: `/v2/orders`. It is explicit and easy to route at the gateway level. The downside is that URLs change between versions, breaking bookmarks and hardcoded references.

**Header Versioning.** A custom header carries the version: `Api-Version: 2`. URLs remain stable, but the version is invisible in logs and browser address bars. Testing requires setting headers explicitly.

**Query Parameter Versioning.** The version is a query parameter: `/orders?version=2`. Similar tradeoffs to header versioning, with slightly better visibility.

**Content Negotiation Versioning.** The version is embedded in the media type: `Accept: application/vnd.example.v2+json`. This is the most RESTful approach, as it leverages HTTP content negotiation. It is also the most complex to implement and the least familiar to API consumers.

### Semantic Versioning for APIs

Apply semantic versioning principles: increment the major version for breaking changes, the minor version for backward-compatible additions, and the patch version for backward-compatible fixes. Only the major version needs to be reflected in the URL path or header; minor and patch versions are internal to the specification.

In practice, most teams version at the URL path level (`/v1`, `/v2`) for its simplicity and explicitness. The key discipline is maintaining backward compatibility within a major version and treating any breaking change as a major version bump that requires a migration path.

## Modeling Exchanges and Choosing an API Format

The right API format depends on the characteristics of the exchange.

**High-traffic services** benefit from compact payloads. gRPC with Protocol Buffers produces significantly smaller messages than JSON-based REST and supports HTTP/2 multiplexing natively. For internal service-to-service calls handling thousands of requests per second, the efficiency gains compound.

**Large payloads** may require streaming. gRPC supports server streaming (one request, many response messages), client streaming (many request messages, one response), and bidirectional streaming. REST over HTTP/1.1 has no native streaming support; HTTP/2 server push and chunked transfer encoding provide partial alternatives.

**HTTP/2 benefits** extend beyond gRPC. REST APIs served over HTTP/2 gain multiplexing (multiple requests over a single TCP connection), header compression (HPACK), and binary framing. These improvements reduce latency for APIs that require many concurrent requests, such as a dashboard aggregating data from multiple endpoints.

**Client diversity** favors REST. When your API serves browsers, mobile apps, third-party integrators, and command-line tools, REST's ubiquity and simplicity reduce integration friction. gRPC requires generated stubs and HTTP/2 support; GraphQL requires a client library that understands query construction.

A practical heuristic: expose REST for external and public APIs, use gRPC for internal service-to-service communication where performance matters, and consider GraphQL when client data requirements are highly variable and you want to avoid maintaining multiple bespoke endpoints.

## Multiple Specifications: The Golden Standard Question

Organizations often wonder whether a single specification format can serve all needs. In practice, most mature API platforms use multiple specifications for different purposes.

OpenAPI describes the HTTP contract: endpoints, methods, parameters, schemas. AsyncAPI extends similar concepts to event-driven and message-based APIs (Kafka topics, WebSocket channels). Protocol Buffers define gRPC service contracts. JSON Schema provides data validation independent of any transport.

The challenge is keeping these specifications consistent when they describe overlapping concerns. An order schema defined in OpenAPI, repeated in a protobuf message, and again in an AsyncAPI event introduces drift risk. Strategies to manage this include generating one specification from another (e.g., deriving OpenAPI from protobuf definitions), maintaining a single source-of-truth schema registry, or using code-first approaches where the specification is generated from annotated code.

There is no single golden specification. The practical answer is to choose one authoritative source for each concern (data shape, HTTP contract, event contract, RPC contract) and automate synchronization between them. The ADR process described earlier is the appropriate mechanism for documenting these choices and their rationale.
