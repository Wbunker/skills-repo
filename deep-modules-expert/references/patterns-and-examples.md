# Deep vs Shallow Module Patterns and Examples

## Table of Contents
1. [The Depth Equation](#depth-equation)
2. [Classic Deep Module Examples](#deep-examples)
3. [Classic Shallow Module Anti-Patterns](#shallow-anti-patterns)
4. [Side-by-Side Comparisons](#comparisons)

---

## 1. The Depth Equation

**Module Depth = Benefit / Cost**
- **Benefit**: Total functionality and power provided
- **Cost**: Interface complexity (method count, parameter count, exception types, mental load to use)

A module is deep when benefit >> cost. The goal is not fewer classes but *more functionality per unit of interface*.

Ousterhout's key insight: "It's more important for a module to have a simple interface than a simple implementation."

---

## 2. Classic Deep Module Examples

### Unix I/O (canonical example)
Five system calls — `open`, `read`, `write`, `lseek`, `close` — hide:
- Disk device differences
- File format complexity
- Permission checks
- Concurrent access management
- Page cache, buffering, prefetch
- Symbolic links, hard links
- Block allocation

The same 5-call interface works for files, sockets, pipes, devices. Enormous benefit, minimal interface.

### Garbage Collection
The "world's deepest interface": calling `free()` is *removed* from the interface entirely. The implementation grows massively more complex; the interface shrinks. Perfect depth inversion.

### SQL
`SELECT * FROM orders WHERE customer_id = 42` hides:
- Query planning and optimization
- Index selection
- Transaction isolation
- I/O scheduling
- Lock management
- Distributed execution (in some systems)

One interface expression triggers enormous hidden machinery.

### TCP/IP Stack
Callers think: "send bytes reliably." Hidden: packet fragmentation, retransmission, congestion control, window sizing, checksum verification.

---

## 3. Classic Shallow Module Anti-Patterns

### Pass-Through Methods
```python
# Shallow: exists only to forward
class UserService:
    def get_user(self, user_id: str) -> User:
        return self._repository.get_user(user_id)  # identical signature, no value added
```
Test: if a method's body could be inlined at every call site with no loss, it's a pass-through.

### Java I/O Stacking (classitis)
```java
// Requires three classes just to read objects from a file
DataInputStream in = new DataInputStream(
    new BufferedInputStream(
        new FileInputStream("data.bin")));
```
The interface cost is enormous — caller must understand three abstractions, their interactions, and their ordering. A deep design would be `Files.readObjects("data.bin")` with buffering as a default.

### Temporal Decomposition (operation-based split)
```python
# Split by execution order, not by logical ownership
class OrderParser:          # reads file, parses format
class OrderValidator:       # reads same format knowledge
class OrderSerializer:      # writes same format knowledge
```
Format knowledge leaks into three modules. Change the format → three files change. A deep design: `OrderStore` encapsulates all format knowledge.

### Information Leakage
```python
# Client must know the module uses Redis internally
def get_session(user_id: str, redis_key_prefix: str) -> Session:
    ...
```
`redis_key_prefix` exposes an implementation decision. Deep: `get_session(user_id)` — the storage strategy is hidden.

### Conjoined Methods
```python
class Parser:
    def parse_header(self): ...     # sets self._state
    def parse_body(self):   ...     # reads self._state set by parse_header
```
You can't understand `parse_body` without reading `parse_header`. They're secretly one method with a forced call sequence.

### Exception Over-declaration
```java
// Shallow: client must handle 5 different exceptions for "read a config"
public Config load() throws FileNotFoundException, IOException,
    YAMLParseException, ValidationException, PermissionDeniedException { ... }
```
Deep alternative: one `ConfigException` wrapping the root cause, or a `Config.loadOrDefault()` that handles common cases internally.

---

## 4. Side-by-Side Comparisons

### File Reading

**Shallow**
```python
f = open("data.json")
raw = f.read()
f.close()
data = json.loads(raw)
```
Three concepts exposed: handle management, raw read, format parsing.

**Deeper**
```python
data = load_json("data.json")
```
One concept: get structured data from a file path. Handle lifecycle and buffering are hidden.

---

### HTTP Client

**Shallow (interface exposes internals)**
```python
client = HttpClient(connection_pool_size=10, retry_policy=ExponentialBackoff(3),
                    timeout=Timeout(connect=5, read=30), ssl_context=default_ssl())
response = client.request(method="GET", url=url, headers={}, stream=False)
```

**Deep (sensible defaults, minimal required surface)**
```python
response = http.get(url)
# Power users can still configure, but common case is one call
```

---

### User Authentication

**Shallow (temporal decomposition)**
```python
token = auth.generate_token(user_id)
auth.store_token(token, redis_client, ttl=3600)
auth.set_cookie(response, token)
```
Three calls, each exposing storage and transport details.

**Deep**
```python
auth.login(user_id, response)
# Hides: token generation, storage strategy, cookie/header transport
```
