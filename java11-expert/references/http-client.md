# Java 11 HTTP Client API
## HttpClient, HttpRequest, HttpResponse, Async, WebSocket, HTTP/2 (JEP 321)

---

## Overview

Java 11 standardizes the HTTP Client API (JEP 321), previously incubating in `jdk.incubator.http` since Java 9. It lives in the `java.net.http` package (module `java.net.http`).

Key features:
- Fluent builder APIs for client, request, and response
- HTTP/1.1 and HTTP/2 support (automatic upgrade)
- Synchronous and asynchronous (non-blocking) sending
- WebSocket support
- Full redirect, proxy, authentication, and cookie support

---

## `HttpClient`

The client is immutable and thread-safe. Create once, reuse.

```java
import java.net.http.HttpClient;
import java.time.Duration;

// Minimal client (defaults: HTTP/2, no redirect follow, system proxy)
HttpClient client = HttpClient.newHttpClient();

// Configured client
HttpClient client = HttpClient.newBuilder()
    .version(HttpClient.Version.HTTP_2)              // HTTP_1_1 or HTTP_2
    .followRedirects(HttpClient.Redirect.NORMAL)     // NEVER, ALWAYS, NORMAL
    .connectTimeout(Duration.ofSeconds(10))
    .executor(Executors.newFixedThreadPool(4))        // custom thread pool for async
    .proxy(ProxySelector.of(new InetSocketAddress("proxy.example.com", 8080)))
    .authenticator(Authenticator.getDefault())
    .cookieHandler(new CookieManager())
    .sslContext(sslContext)                          // custom TLS
    .build();
```

### `HttpClient.Redirect` Values

| Value | Behavior |
|-------|---------|
| `NEVER` | Never follow redirects |
| `ALWAYS` | Follow all redirects (including HTTP → HTTPS) |
| `NORMAL` | Follow HTTPS → HTTPS and HTTP → HTTP; not HTTP → HTTPS |

---

## `HttpRequest`

Requests are immutable.

```java
import java.net.http.HttpRequest;
import java.net.URI;

// GET
HttpRequest getRequest = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/users"))
    .GET()
    .timeout(Duration.ofSeconds(30))
    .header("Accept", "application/json")
    .header("Authorization", "Bearer " + token)
    .build();

// POST with body
HttpRequest postRequest = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/users"))
    .POST(HttpRequest.BodyPublishers.ofString("{\"name\":\"Alice\"}"))
    .header("Content-Type", "application/json")
    .build();

// PUT
HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/users/1"))
    .PUT(HttpRequest.BodyPublishers.ofString(json))
    .build();

// DELETE
HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/users/1"))
    .DELETE()
    .build();

// Custom method
HttpRequest.newBuilder()
    .uri(uri)
    .method("PATCH", HttpRequest.BodyPublishers.ofString(json))
    .build();
```

### `BodyPublishers` — Request Body Sources

```java
HttpRequest.BodyPublishers.noBody()               // no request body (GET, DELETE)
HttpRequest.BodyPublishers.ofString("text")       // UTF-8 string
HttpRequest.BodyPublishers.ofString(s, charset)   // specific charset
HttpRequest.BodyPublishers.ofByteArray(bytes)
HttpRequest.BodyPublishers.ofByteArrays(iterableOfBytes)
HttpRequest.BodyPublishers.ofFile(Path.of("data.json"))
HttpRequest.BodyPublishers.ofInputStream(() -> inputStream)
HttpRequest.BodyPublishers.fromPublisher(publisher)  // reactive streams
```

---

## `HttpResponse` and `BodyHandlers`

### Synchronous Sending

```java
import java.net.http.HttpResponse;

HttpResponse<String> response =
    client.send(request, HttpResponse.BodyHandlers.ofString());

response.statusCode()           // 200, 404, etc.
response.body()                 // String body
response.headers()              // HttpHeaders
response.headers().map()        // Map<String, List<String>>
response.headers().firstValue("Content-Type")  // Optional<String>
response.uri()                  // final URI (after redirects)
response.version()              // HttpClient.Version.HTTP_2
response.previousResponse()     // Optional<HttpResponse<T>> (redirect chain)
```

### `BodyHandlers` — Response Body Types

```java
HttpResponse.BodyHandlers.ofString()              // String (UTF-8)
HttpResponse.BodyHandlers.ofString(charset)
HttpResponse.BodyHandlers.ofByteArray()           // byte[]
HttpResponse.BodyHandlers.ofFile(path)            // saves to file, returns Path
HttpResponse.BodyHandlers.ofInputStream()         // InputStream (streaming)
HttpResponse.BodyHandlers.ofLines()               // Stream<String>
HttpResponse.BodyHandlers.discarding()            // void (discard body)
HttpResponse.BodyHandlers.replacing(value)        // always returns given value
HttpResponse.BodyHandlers.buffering(handler, size) // buffered wrapper
```

---

## Asynchronous Sending

`sendAsync` returns a `CompletableFuture` — non-blocking.

```java
CompletableFuture<HttpResponse<String>> futureResponse =
    client.sendAsync(request, HttpResponse.BodyHandlers.ofString());

// Chain operations
futureResponse
    .thenApply(HttpResponse::body)
    .thenApply(body -> parseJson(body))
    .thenAccept(data -> updateUI(data))
    .exceptionally(ex -> {
        log.error("Request failed", ex);
        return null;
    });

// Or get the value (blocks)
String body = client.sendAsync(request, HttpResponse.BodyHandlers.ofString())
    .thenApply(HttpResponse::body)
    .join();  // join() preferred in async chains (unchecked exceptions)
```

### Multiple Concurrent Requests

```java
List<URI> uris = List.of(
    URI.create("https://api.example.com/a"),
    URI.create("https://api.example.com/b"),
    URI.create("https://api.example.com/c")
);

List<CompletableFuture<String>> futures = uris.stream()
    .map(uri -> HttpRequest.newBuilder(uri).build())
    .map(req -> client.sendAsync(req, HttpResponse.BodyHandlers.ofString())
        .thenApply(HttpResponse::body))
    .collect(Collectors.toList());

// Wait for all
CompletableFuture.allOf(futures.toArray(CompletableFuture[]::new)).join();
List<String> bodies = futures.stream().map(CompletableFuture::join).collect(Collectors.toList());
```

---

## HTTP/2

The client automatically negotiates HTTP/2 when the server supports it (via ALPN extension in TLS). No code change required.

```java
HttpClient client = HttpClient.newBuilder()
    .version(HttpClient.Version.HTTP_2)  // negotiate HTTP/2; fall back to HTTP/1.1
    .build();

// Check which version was used
HttpResponse<String> response = client.send(request, BodyHandlers.ofString());
System.out.println(response.version());  // HTTP_1_1 or HTTP_2
```

HTTP/2 server push is not directly exposed in the Java 11 API via `sendAsync`. It requires the `PushPromiseHandler` parameter:

```java
Map<HttpRequest, CompletableFuture<HttpResponse<String>>> pushes = new ConcurrentHashMap<>();

HttpResponse<String> response = client.send(
    request,
    HttpResponse.BodyHandlers.ofString(),
    (initiatingRequest, pushPromiseRequest, acceptor) -> {
        CompletableFuture<HttpResponse<String>> pushed =
            acceptor.apply(HttpResponse.BodyHandlers.ofString());
        pushes.put(pushPromiseRequest, pushed);
    }
);
```

---

## WebSocket

```java
import java.net.http.WebSocket;

WebSocket ws = client.newWebSocketBuilder()
    .buildAsync(URI.create("wss://echo.websocket.org"), new WebSocket.Listener() {
        @Override
        public CompletionStage<?> onText(WebSocket ws, CharSequence data, boolean last) {
            System.out.println("Received: " + data);
            ws.request(1);   // request next message
            return null;
        }

        @Override
        public void onOpen(WebSocket ws) {
            System.out.println("Connected");
            ws.request(1);   // must call request() to start receiving
        }

        @Override
        public CompletionStage<?> onClose(WebSocket ws, int statusCode, String reason) {
            System.out.println("Closed: " + statusCode);
            return null;
        }

        @Override
        public void onError(WebSocket ws, Throwable error) {
            System.err.println("Error: " + error);
        }
    }).join();

// Send text
ws.sendText("Hello, WebSocket!", true);  // true = last part (complete message)

// Send binary
ws.sendBinary(ByteBuffer.wrap(data), true);

// Send ping
ws.sendPing(ByteBuffer.wrap("ping".getBytes()));

// Close
ws.sendClose(WebSocket.NORMAL_CLOSURE, "goodbye");
```

### WebSocket Flow Control

`ws.request(n)` is mandatory to receive messages — prevents buffer overflow. Call once per `onText`/`onBinary` invocation.

---

## Authentication

### Basic / Digest Auth

```java
HttpClient client = HttpClient.newBuilder()
    .authenticator(new Authenticator() {
        @Override
        protected PasswordAuthentication getPasswordAuthentication() {
            return new PasswordAuthentication("user", "pass".toCharArray());
        }
    })
    .build();
```

### Bearer Token (Manual Header)

```java
HttpRequest.newBuilder()
    .uri(uri)
    .header("Authorization", "Bearer " + accessToken)
    .build();
```

---

## Error Handling

```java
try {
    HttpResponse<String> response = client.send(request, BodyHandlers.ofString());
    if (response.statusCode() >= 400) {
        throw new RuntimeException("HTTP error: " + response.statusCode());
    }
} catch (IOException e) {
    // Network error, connection refused, DNS failure
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
    throw new RuntimeException("Interrupted", e);
} catch (HttpTimeoutException e) {
    // Request or connect timeout
}
```

---

## Module Declaration

If using modules, declare the dependency:

```java
module com.example.myapp {
    requires java.net.http;
}
```
