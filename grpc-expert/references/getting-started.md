# Getting Started with gRPC

This reference covers creating gRPC service definitions, implementing servers and clients in Go and Java, and best practices for protocol buffer design. It corresponds to the foundational workflow every gRPC project follows: define a service contract in a `.proto` file, generate language-specific code, then implement the server and client against that generated code.

## Creating the Service Definition

Every gRPC service begins with a `.proto` file written in Protocol Buffers version 3 syntax. This file is the single source of truth for your service contract.

### Syntax, Package, and Options

```protobuf
syntax = "proto3";

package ecommerce;

option go_package = "github.com/example/ecommerce/proto;ecommercepb";
option java_package = "com.example.ecommerce";
option java_multiple_files = true;
```

- `syntax = "proto3"` must be the first non-comment line. If omitted, protoc defaults to proto2.
- `package` provides a namespace that prevents name collisions across proto files and maps to language-specific packages (Go packages, Java packages, Python modules).
- `go_package` specifies the full Go import path. The portion after the semicolon is the Go package name used in generated code.
- `java_multiple_files = true` generates each top-level message and enum as a separate `.java` file rather than nesting them inside a single outer class.

### Defining Messages

Messages are the fundamental data structures exchanged in RPC calls.

```protobuf
message Product {
  // Scalar types
  string id = 1;
  string name = 2;
  string description = 3;
  float price = 4;
  bool in_stock = 5;
  int32 quantity = 6;

  // Enum
  enum Category {
    CATEGORY_UNSPECIFIED = 0;
    ELECTRONICS = 1;
    CLOTHING = 2;
    BOOKS = 3;
  }
  Category category = 7;

  // Repeated field (list/array)
  repeated string tags = 8;

  // Map field
  map<string, string> attributes = 9;

  // Nested message
  message Dimension {
    float height = 1;
    float width = 2;
    float depth = 3;
  }
  Dimension dimensions = 10;

  // Oneof - only one of these fields can be set at a time
  oneof promotion {
    float discount_percentage = 11;
    float flat_discount = 12;
  }

  // Optional - distinguishes between "not set" and "set to default value"
  optional string sku = 13;
}
```

Key rules for proto3 message fields:

- **Scalar types**: `double`, `float`, `int32`, `int64`, `uint32`, `uint64`, `sint32`, `sint64`, `fixed32`, `fixed64`, `sfixed32`, `sfixed64`, `bool`, `string`, `bytes`. Each has a well-defined default value (zero, empty string, false).
- **Enums** must have a zero value as the first entry. By convention, name it `UNSPECIFIED` or `UNKNOWN`.
- **Repeated fields** represent ordered lists. They serialize as empty when no elements are present.
- **Map fields** cannot be `repeated`. Keys can be any integral or string type; values can be any type except another map.
- **Oneof** fields share memory; setting one clears the others. Oneof fields cannot be `repeated`.
- **Optional** fields (added in proto3 revision) generate a `has_` method so you can distinguish between "field was not set" and "field was set to its default value."

### Defining Services

Services declare the RPC methods a server exposes:

```protobuf
service ProductInfo {
  // Unary RPC
  rpc addProduct(Product) returns (ProductID);
  rpc getProduct(ProductID) returns (Product);
}

message ProductID {
  string value = 1;
}
```

Each `rpc` method takes exactly one request message and returns exactly one response message for unary calls. Streaming variants use the `stream` keyword (covered in later chapters).

### Well-Known Types

Google provides a set of standard message types that solve common problems. Import them from `google/protobuf/`:

```protobuf
import "google/protobuf/timestamp.proto";
import "google/protobuf/empty.proto";
import "google/protobuf/any.proto";
import "google/protobuf/wrappers.proto";
import "google/protobuf/struct.proto";

message Order {
  string id = 1;

  // Timestamp for precise time representation
  google.protobuf.Timestamp created_at = 2;

  // Wrappers distinguish null from default values
  google.protobuf.StringValue coupon_code = 3;
  google.protobuf.Int32Value priority = 4;

  // Any can hold an arbitrary serialized message
  google.protobuf.Any extension = 5;

  // Struct for dynamic JSON-like data
  google.protobuf.Struct metadata = 6;
}

service OrderManagement {
  // Empty is used when no request or response payload is needed
  rpc cancelAllOrders(google.protobuf.Empty) returns (google.protobuf.Empty);
}
```

- **Timestamp**: Represents a point in time independent of timezone. Maps to `time.Time` in Go and `com.google.protobuf.Timestamp` in Java.
- **Empty**: A message with no fields, used when an RPC requires no input or output.
- **Wrappers** (`StringValue`, `Int32Value`, `BoolValue`, etc.): Provide nullable semantics for scalar types. A nil wrapper means "not set," distinct from "set to default."
- **Any**: Holds a serialized message plus a type URL. The receiver must know how to unpack it.
- **Struct**: Represents arbitrary JSON-like structured data. Useful when the schema is not known at compile time.

### Import Statements and Package Organization

For larger projects, split proto definitions across files:

```protobuf
// common/money.proto
syntax = "proto3";
package common;
option go_package = "github.com/example/common/proto;commonpb";

message Money {
  string currency_code = 1;
  int64 units = 2;
  int32 nanos = 3;
}
```

```protobuf
// ecommerce/product.proto
syntax = "proto3";
package ecommerce;
option go_package = "github.com/example/ecommerce/proto;ecommercepb";

import "common/money.proto";

message Product {
  string id = 1;
  string name = 2;
  common.Money price = 3;
}
```

When running `protoc`, use the `-I` (or `--proto_path`) flag to specify include directories so that imports resolve correctly.

## Implementation in Go

### Installing the Toolchain

```bash
# Install the protocol buffer compiler
# macOS
brew install protobuf

# Install Go plugins for protoc
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# Ensure $GOPATH/bin is in your PATH
export PATH="$PATH:$(go env GOPATH)/bin"
```

### Generating Go Code

```bash
protoc -I proto/ \
  --go_out=. --go_opt=paths=source_relative \
  --go-grpc_out=. --go-grpc_opt=paths=source_relative \
  proto/ecommerce/product.proto
```

This produces two files alongside the `.proto` file:
- `product.pb.go` -- message types, serialization methods
- `product_grpc.pb.go` -- gRPC client and server interfaces

### Implementing the Server

```go
package main

import (
    "context"
    "log"
    "net"

    "github.com/google/uuid"
    pb "github.com/example/ecommerce/proto/ecommercepb"
    "google.golang.org/grpc"
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/status"
)

// server implements the ProductInfoServer interface from generated code.
type server struct {
    pb.UnimplementedProductInfoServer
    products map[string]*pb.Product
}

func (s *server) AddProduct(ctx context.Context, req *pb.Product) (*pb.ProductID, error) {
    id := uuid.New().String()
    req.Id = id
    s.products[id] = req
    return &pb.ProductID{Value: id}, nil
}

func (s *server) GetProduct(ctx context.Context, req *pb.ProductID) (*pb.Product, error) {
    product, exists := s.products[req.Value]
    if !exists {
        return nil, status.Errorf(codes.NotFound, "product %s not found", req.Value)
    }
    return product, nil
}

func main() {
    lis, err := net.Listen("tcp", ":50051")
    if err != nil {
        log.Fatalf("failed to listen: %v", err)
    }

    grpcServer := grpc.NewServer()
    pb.RegisterProductInfoServer(grpcServer, &server{
        products: make(map[string]*pb.Product),
    })

    log.Println("gRPC server listening on :50051")
    if err := grpcServer.Serve(lis); err != nil {
        log.Fatalf("failed to serve: %v", err)
    }
}
```

Embedding `UnimplementedProductInfoServer` ensures forward compatibility: if new RPC methods are added to the proto definition, the server compiles without implementing them (they return an `Unimplemented` status by default).

### Creating the Client

```go
package main

import (
    "context"
    "log"
    "time"

    pb "github.com/example/ecommerce/proto/ecommercepb"
    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials/insecure"
)

func main() {
    conn, err := grpc.Dial("localhost:50051",
        grpc.WithTransportCredentials(insecure.NewCredentials()),
    )
    if err != nil {
        log.Fatalf("failed to connect: %v", err)
    }
    defer conn.Close()

    client := pb.NewProductInfoClient(conn)

    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    // Add a product
    productID, err := client.AddProduct(ctx, &pb.Product{
        Name:        "Apple iPhone 15",
        Description: "Latest iPhone model",
        Price:       999.0,
    })
    if err != nil {
        log.Fatalf("AddProduct failed: %v", err)
    }
    log.Printf("Product added with ID: %s", productID.Value)

    // Retrieve the product
    product, err := client.GetProduct(ctx, &pb.ProductID{Value: productID.Value})
    if err != nil {
        log.Fatalf("GetProduct failed: %v", err)
    }
    log.Printf("Product: %+v", product)
}
```

`grpc.Dial` establishes a connection to the server. In production, replace `insecure.NewCredentials()` with TLS credentials. The returned `ClientConn` manages connection pooling and reconnection internally.

## Implementation in Java

### Gradle Setup

```groovy
plugins {
    id 'java'
    id 'com.google.protobuf' version '0.9.4'
}

dependencies {
    implementation 'io.grpc:grpc-netty-shaded:1.62.2'
    implementation 'io.grpc:grpc-protobuf:1.62.2'
    implementation 'io.grpc:grpc-stub:1.62.2'
    compileOnly 'org.apache.tomcat:annotations-api:6.0.53'
}

protobuf {
    protoc {
        artifact = 'com.google.protobuf:protoc:3.25.3'
    }
    plugins {
        grpc {
            artifact = 'io.grpc:protoc-gen-grpc-java:1.62.2'
        }
    }
    generateProtoTasks {
        all()*.plugins {
            grpc {}
        }
    }
}
```

Place `.proto` files in `src/main/proto/`. Running `./gradlew build` generates Java classes into `build/generated/source/proto/`.

The protobuf plugin generates:
- Message classes (e.g., `Product`, `ProductID`) with builders, serialization, and parsing.
- `ProductInfoGrpc` containing the service stub classes: `ProductInfoBlockingStub`, `ProductInfoStub` (async), and `ProductInfoImplBase` (server base class).

### Implementing the Server

```java
package com.example.ecommerce;

import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.Status;
import io.grpc.stub.StreamObserver;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

public class ProductInfoServer {

    public static void main(String[] args) throws Exception {
        Server server = ServerBuilder.forPort(50051)
            .addService(new ProductInfoImpl())
            .build()
            .start();

        System.out.println("Server started on port 50051");

        Runtime.getRuntime().addShutdownHook(new Thread(server::shutdown));
        server.awaitTermination();
    }
}

class ProductInfoImpl extends ProductInfoGrpc.ProductInfoImplBase {

    private final Map<String, Product> products = new ConcurrentHashMap<>();

    @Override
    public void addProduct(Product request, StreamObserver<ProductID> responseObserver) {
        String id = UUID.randomUUID().toString();
        Product product = request.toBuilder().setId(id).build();
        products.put(id, product);

        responseObserver.onNext(ProductID.newBuilder().setValue(id).build());
        responseObserver.onCompleted();
    }

    @Override
    public void getProduct(ProductID request, StreamObserver<Product> responseObserver) {
        Product product = products.get(request.getValue());
        if (product == null) {
            responseObserver.onError(
                Status.NOT_FOUND
                    .withDescription("Product not found: " + request.getValue())
                    .asRuntimeException()
            );
            return;
        }
        responseObserver.onNext(product);
        responseObserver.onCompleted();
    }
}
```

The Java server uses the `StreamObserver` pattern. For each RPC, call `onNext` with the response, then `onCompleted`. For errors, call `onError` with an appropriate gRPC `Status`.

### Creating the Client

```java
package com.example.ecommerce;

import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;

public class ProductInfoClient {

    public static void main(String[] args) {
        ManagedChannel channel = ManagedChannelBuilder
            .forAddress("localhost", 50051)
            .usePlaintext()
            .build();

        ProductInfoGrpc.ProductInfoBlockingStub stub =
            ProductInfoGrpc.newBlockingStub(channel);

        // Add a product
        ProductID productId = stub.addProduct(Product.newBuilder()
            .setName("Apple iPhone 15")
            .setDescription("Latest iPhone model")
            .setPrice(999.0f)
            .build());
        System.out.println("Product added: " + productId.getValue());

        // Retrieve the product
        Product product = stub.getProduct(productId);
        System.out.println("Product retrieved: " + product.getName());

        channel.shutdown();
    }
}
```

`ManagedChannel` is the Java equivalent of Go's `ClientConn`. The blocking stub provides synchronous calls; use `newStub` for asynchronous calls with `StreamObserver` callbacks, or `newFutureStub` for `ListenableFuture`-based calls.

## Building and Running

A typical project structure and build workflow:

```
project/
  proto/
    ecommerce/
      product.proto
  go/
    server/main.go
    client/main.go
    go.mod
  java/
    build.gradle
    src/main/proto/ecommerce/product.proto
    src/main/java/com/example/ecommerce/
```

### Go Build

```bash
# Generate code
protoc -I proto/ \
  --go_out=go/ --go_opt=paths=source_relative \
  --go-grpc_out=go/ --go-grpc_opt=paths=source_relative \
  proto/ecommerce/product.proto

# Build and run
go build -o bin/server ./go/server
go build -o bin/client ./go/client

./bin/server &
./bin/client
```

### Java Build

```bash
# Generate code and compile (protobuf plugin handles generation)
./gradlew build

# Run
./gradlew runServer &
./gradlew runClient
```

### Using buf Instead of protoc

The `buf` CLI is a modern alternative to raw `protoc` invocations. It handles dependency management, linting, and code generation through a `buf.yaml` and `buf.gen.yaml` configuration:

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
buf generate
```

## Proto File Best Practices

**Naming conventions:**
- File names: `lower_snake_case.proto`.
- Message names: `PascalCase`. Field names: `lower_snake_case`.
- Enum type names: `PascalCase`. Enum values: `UPPER_SNAKE_CASE`, prefixed with the enum type name (e.g., `CATEGORY_ELECTRONICS`).
- Service names: `PascalCase`. RPC method names: `PascalCase`.

**Field numbering:**
- Field numbers 1-15 take one byte to encode; use them for frequently populated fields.
- Field numbers 16-2047 take two bytes. Reserve the lower range for high-frequency fields.
- Never reuse a field number after deleting a field. Use `reserved` to prevent accidental reuse:

```protobuf
message Product {
  reserved 6, 9 to 11;
  reserved "old_field_name";
}
```

**Backward compatibility rules:**
- Never change the field number or type of an existing field.
- New fields added to a message are ignored by old consumers (they use default values).
- Removed fields should be reserved to prevent their numbers or names from being reused.
- Renaming a field is safe at the wire level (only the number matters), but breaks JSON serialization since JSON uses field names.
- Do not change a `repeated` field to a scalar or vice versa.
- Changing between `int32`, `uint32`, `int64`, `uint64`, and `bool` is wire-compatible but may truncate values.

**General guidelines:**
- Use wrapper types (`google.protobuf.StringValue`, etc.) when you need to distinguish "not set" from "set to default." Alternatively, use `optional` in proto3.
- Keep messages focused. Prefer composing smaller messages over monolithic types.
- Version your packages when making breaking changes: `package ecommerce.v1;`, `package ecommerce.v2;`.
- Define request and response messages per RPC rather than reusing domain objects directly, so that each RPC can evolve independently.
