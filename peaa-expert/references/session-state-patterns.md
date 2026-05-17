# Session State Patterns — PEAA

These three patterns address where to store conversational state — data that must persist across multiple HTTP requests within a single user session.

---

## The Problem: Stateless HTTP

HTTP is inherently stateless. Each request is independent. Yet users expect continuity: a shopping cart that persists, a multi-step form that remembers earlier steps, a logged-in identity.

Three storage locations exist for this conversational state, each with different trade-offs.

---

## Client Session State

**Intent**: Stores session state on the client.

**Mechanisms**
- **Cookies**: Small key-value pairs sent with every request; browser stores them; server reads from `Cookie` header
- **Hidden form fields**: Data embedded in HTML forms; returned to server on POST
- **URL rewriting / query parameters**: State encoded in URLs; fragile (links can be copied/expired)
- **Browser local storage / session storage**: Client-side JS storage; not sent to server automatically; requires explicit Ajax communication

**Example: Cookie-Based Token (JWT)**
```
# Client stores:
Cookie: session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# JWT payload (signed, optionally encrypted):
{
  "userId": 42,
  "role": "admin",
  "cartId": "cart-uuid-123",
  "exp": 1725000000
}
```

The server reads and validates the token on each request — no server-side session lookup needed.

**Hidden Form Field Example**
```html
<form method="POST" action="/checkout/payment">
  <input type="hidden" name="shippingAddressId" value="789"/>
  <input type="hidden" name="shippingMethod" value="EXPRESS"/>
  <!-- user-visible payment fields -->
</form>
```

**Pros**
- Highly scalable: server is stateless; any node can handle any request
- No clustering complexity
- Survives server restarts

**Cons**
- Limited size (4KB per cookie)
- Data is on the client — must be encrypted or signed to prevent tampering
- Sensitive data should NEVER be in plaintext cookies
- Large state bloats every HTTP request

**When to Use**
- Stateless server architecture (cloud, auto-scaling groups)
- Small amounts of state (user ID, preferences, cart reference)
- JWT-based authentication (token IS the session state)

**Security Rule**: Always sign client session data (HMAC) and encrypt sensitive data. Never trust unsigned client state.

---

## Server Session State

**Intent**: Keeps session state on the server in a serialized form.

**How It Works**
- Server maintains a session store (in-memory Map, Redis, database)
- Client receives a session ID (cookie: `JSESSIONID`, `SESSION`, etc.)
- On each request, server looks up session ID → loads session object

**In-Memory Session (Single Server)**
```java
// HttpSession abstraction (Servlet)
HttpSession session = request.getSession(true);
session.setAttribute("cart", cart);
session.setAttribute("userId", userId);
session.setMaxInactiveInterval(30 * 60);  // 30 minutes
```

**Distributed Session Store (Redis)**
```yaml
# Spring Session + Redis
spring:
  session:
    store-type: redis
    timeout: 30m
```
```java
// Code unchanged — Spring Session intercepts HttpSession calls
// and serializes/deserializes to/from Redis transparently
session.setAttribute("cart", cart);
```

**Session Object Design**
- Keep sessions small — only store what's needed between requests
- Store references (IDs) not full objects where possible
- Mark session objects as `Serializable` for distributed stores

**Pros**
- Natural programming model — session object is familiar
- Can hold arbitrary amounts of data (unlike cookies)
- Easy to invalidate (delete session record)

**Cons**
- Sticky sessions required without distributed store (all requests from a client go to the same server)
- Distributed store adds infrastructure complexity (Redis, Memcached, DB)
- Memory pressure on server or cache

**When to Use**
- Traditional web apps where server session is already established (Java EE, Spring MVC)
- When state is too large for cookies
- When distributed session store (Redis) is available

---

## Database Session State

**Intent**: Stores session data as committed data in the database, pending data is stored in separate "pending" records until confirmed.

**Two Sub-Approaches**

### A. Pending Records (True Database Session State)
Each step of a multi-request workflow writes "pending" records to the DB. When the user completes the business transaction, pending records become final; on abandonment, pending records are deleted.

```sql
-- Pending order during checkout
CREATE TABLE pending_orders (
    session_id    VARCHAR(128) PRIMARY KEY,
    customer_id   BIGINT,
    created_at    TIMESTAMP,
    expires_at    TIMESTAMP
);
CREATE TABLE pending_order_items (
    session_id  VARCHAR(128) REFERENCES pending_orders(session_id),
    product_id  BIGINT,
    quantity    INT
);
```

```java
// Each checkout step saves to pending tables
public void addItemToCart(String sessionId, long productId, int qty) {
    jdbcTemplate.update(
        "INSERT INTO pending_order_items(session_id, product_id, quantity) VALUES(?,?,?) " +
        "ON CONFLICT(session_id, product_id) DO UPDATE SET quantity = ?",
        sessionId, productId, qty, qty);
}

// On checkout confirmation — promote pending to real order
@Transactional
public Order confirmOrder(String sessionId) {
    PendingOrder pending = loadPending(sessionId);
    Order order = createFromPending(pending);
    orders.save(order);
    deletePending(sessionId);
    return order;
}
```

### B. Serialized Session in DB (Hybrid)
Serialize the session object as a blob/JSON in a sessions table. Similar to Server Session State but backed by a database rather than in-memory store.

```sql
CREATE TABLE sessions (
    id          VARCHAR(128) PRIMARY KEY,
    data        TEXT,  -- JSON blob of session state
    last_active TIMESTAMP,
    expires_at  TIMESTAMP
);
```

**Pros**
- Session data survives server restarts
- No sticky session requirement — any server reads from DB
- Easy horizontal scaling
- Session data queryable (can find abandoned carts, expired sessions)
- Simpler infrastructure than Redis cluster

**Cons**
- DB becomes a bottleneck (every request potentially reads/writes session)
- Latency of DB access vs. in-memory session

**When to Use**
- High-availability / horizontally-scaled deployments without Redis
- Session data must survive deployments
- Need to query or report on session data (e.g., abandoned cart analysis)
- Auditing requirements (session changes are committed DB records)

---

## Comparison

| Factor | Client Session State | Server Session State | Database Session State |
|---|---|---|---|
| Scalability | Highest | Medium (needs distributed store) | High |
| Data size limit | ~4KB (cookies) | Unlimited | Unlimited |
| Server memory pressure | None | High (in-memory) | Low |
| Survives server restart | Yes | No (in-memory) / Yes (Redis) | Yes |
| Infrastructure needed | None | Redis / sticky sessions | DB table |
| Security risk | Highest (on client) | Low | Low |
| Implementation complexity | Low-Medium | Low | Medium |

**Fowler's Guidance**
- Prefer stateless servers when possible — push toward Client Session State
- Use Database Session State for clustering without caching infrastructure
- Server Session State with a distributed cache (Redis) is the pragmatic choice for most modern apps
- Avoid in-memory single-server session state in cloud/container deployments where instances are ephemeral
