# Refactoring Playbook: Shallow → Deep

Concrete transformations for making modules deeper.

## Table of Contents
1. [Absorb Pass-Through Layers](#absorb-pass-through)
2. [Merge Temporally Decomposed Classes](#merge-temporal)
3. [Push Decisions Inward](#push-decisions-inward)
4. [Simplify Exception Surface](#simplify-exceptions)
5. [Introduce Defaults and Convenience Methods](#defaults)
6. [Replace State Exposure with Richer Methods](#rich-methods)
7. [Eliminate Conjoined Methods](#eliminate-conjoined)
8. [Context Objects for Parameter Clusters](#context-objects)
9. [Choosing What NOT to Merge](#dont-over-merge)

---

## 1. Absorb Pass-Through Layers

**Signal**: A class whose methods just call identically-named methods on a wrapped object.

**Before**
```python
class UserController:
    def __init__(self, service: UserService): self._service = service
    def get_user(self, uid): return self._service.get_user(uid)
    def update_user(self, uid, data): return self._service.update_user(uid, data)
```

**Transformation options**:
- **Delete the layer**: Let callers use `UserService` directly.
- **Add value**: If the layer does logging, auth checks, or request mapping, that's real depth — keep it and make the value explicit.
- **Consolidate**: If the controller is only a routing thin layer, use a router abstraction that already handles delegation.

**Rule**: A pass-through is only justified if crossing the boundary adds transformation, validation, or policy enforcement.

---

## 2. Merge Temporally Decomposed Classes

**Signal**: Two or more classes share knowledge of the same format, schema, or protocol.

**Before**
```python
class ConfigReader:
    def read(self, path: str) -> dict:   # knows YAML format
        ...

class ConfigValidator:
    def validate(self, data: dict):      # knows expected YAML keys
        ...

class ConfigWriter:
    def write(self, data: dict, path: str):  # knows YAML format
        ...
```

**After**
```python
class ConfigStore:
    def load(self, path: str) -> Config:     # owns: format, validation, defaults
        ...
    def save(self, config: Config, path: str):
        ...
```

**Why it works**: Format knowledge is now owned in one place. Change YAML to TOML → one file changes.

---

## 3. Push Decisions Inward

**Signal**: The interface exposes a parameter that names an implementation choice.

**Before**
```python
def cache_result(key: str, value: Any, backend: str, ttl_seconds: int):
    if backend == "redis":
        redis_client.setex(key, ttl_seconds, value)
    elif backend == "memcache":
        memcache_client.set(key, value, time=ttl_seconds)
```

**After**
```python
def cache_result(key: str, value: Any):
    # backend and TTL are configuration, not per-call decisions
    _backend.set(key, value, ttl=_default_ttl)
```

**Pattern**: Move configuration to module initialization; move per-call variability only where it's genuinely variable at the call site.

---

## 4. Simplify Exception Surface

**Signal**: A method declares or throws 4+ distinct exception types that callers mostly handle the same way.

**Before**
```python
def load_config(path: str) -> Config:
    # raises: FileNotFoundError, PermissionError, YAMLParseError,
    #         ValidationError, NetworkTimeoutError (for remote configs)
```

**After**
```python
def load_config(path: str) -> Config:
    # raises: ConfigLoadError (wraps root cause, callers get one catch)

# For callers that need to distinguish:
class ConfigLoadError(Exception):
    @property
    def is_not_found(self) -> bool: ...
    @property
    def is_parse_error(self) -> bool: ...
```

**Even deeper**: Handle transient errors (network timeouts, file locks) internally with retry. Surface only unrecoverable failures.

---

## 5. Introduce Defaults and Convenience Methods

**Signal**: 90% of callers pass the same options. The interface requires configuration for the common case.

**Before**
```java
HttpClient client = new HttpClient(
    new ConnectionPool(10),
    new RetryPolicy(3, ExponentialBackoff.DEFAULT),
    new Timeout(Duration.ofSeconds(5), Duration.ofSeconds(30)),
    SSLContext.getDefault()
);
Response r = client.request("GET", url, Collections.emptyMap(), false);
```

**After**
```java
Response r = Http.get(url);  // default client, sensible config built-in
// Power users still get: new HttpClient.Builder().timeout(60).build()
```

**Pattern**: Builder pattern or static factory with opinionated defaults. Deep module = common case is effortless, power case is still possible.

---

## 6. Replace State Exposure with Richer Methods

**Signal**: Callers read internal state, compute a condition, then call back into the module.

**Before**
```python
# Caller
if user.plan == "trial" and (datetime.now() - user.trial_start).days >= 27:
    email_service.send_trial_warning(user.email)
```

**After**
```python
# Module owns the business rule
class User:
    def notify_if_trial_expiring_soon(self, email_service):
        if self._is_trial_expiring():
            email_service.send_trial_warning(self.email)
```

Or even deeper:
```python
user.check_and_notify_expiry()  # fully encapsulated, no caller logic
```

**Test**: If external code makes decisions based on module state, that logic probably belongs inside the module.

---

## 7. Eliminate Conjoined Methods

**Signal**: Two methods must be called in sequence; calling one out of order causes errors or undefined behavior.

**Before**
```python
parser.set_input(raw_bytes)   # must come first
header = parser.parse_header()
body = parser.parse_body()    # silently wrong if parse_header not called
```

**After — Option A: Single method**
```python
result = parser.parse(raw_bytes)   # returns ParseResult with .header and .body
```

**After — Option B: Builder/state machine (enforce sequence in types)**
```python
partial = parser.start(raw_bytes)   # returns PartialParse, not Parser
result = partial.finish()           # only method available on PartialParse
```

**Rule**: If a sequence must be followed, make the type system enforce it — or eliminate the sequence by merging into one operation.

---

## 8. Context Objects for Parameter Clusters

**Signal**: A group of parameters travel together across many method signatures.

**Before**
```python
def process(data, user_id, tenant_id, request_id, trace_id, locale):
    ...
def validate(data, user_id, tenant_id, request_id, trace_id, locale):
    ...
def log_event(event, user_id, tenant_id, request_id, trace_id, locale):
    ...
```

**After**
```python
@dataclass
class RequestContext:
    user_id: str
    tenant_id: str
    request_id: str
    trace_id: str
    locale: str

def process(data, ctx: RequestContext): ...
def validate(data, ctx: RequestContext): ...
def log_event(event, ctx: RequestContext): ...
```

**Caution**: The context object itself must stay deep. Don't make it a grab-bag of every field in the system — keep it to genuinely cross-cutting concerns.

---

## 9. Choosing What NOT to Merge

Not all small classes are shallow. Don't merge when:

- **Responsibilities are independently testable and change at different rates** — a `PasswordHasher` and a `SessionTokenGenerator` both do one thing and change for different reasons.
- **The boundary enforces security or policy** — a thin auth layer between controller and service is justified even if it appears pass-through.
- **The interface is used by many clients** — a stable, narrow interface used by 20 callers is a feature; merging it removes a stable abstraction point.
- **Merging creates a god class** — if combining two classes produces a 2000-line class, the decomposition exists for a reason.

**The test**: Does keeping them separate hide complexity from callers, or expose it? If separate = simpler for callers, keep them separate.
