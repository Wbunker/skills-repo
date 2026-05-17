# Offline Concurrency Patterns — PEAA

These patterns address concurrency conflicts across **business transactions** — multi-request user sessions that span many HTTP requests but cannot hold a DB lock open the entire time.

---

## The Offline Concurrency Problem

A system transaction (DB transaction) is too short to span an entire user interaction. A user might:
1. Read order data (request 1 — ends DB transaction)
2. Think, edit, navigate (seconds to minutes — NO DB transaction)
3. Submit changes (request 2 — new DB transaction begins)

Between steps 1 and 3, another user may have modified the same data. The DB transaction in step 3 has no knowledge of this conflict unless we explicitly manage it.

Two strategies: detect conflict at commit (optimistic) or prevent conflict by locking early (pessimistic).

---

## Optimistic Offline Lock

**Intent**: Prevents conflicts between concurrent business transactions by detecting a conflict at commit time and rolling back the transaction.

**How It Works**
- No lock is acquired when reading data
- A version stamp (integer version, timestamp, or hash) is stored with each record
- At save time: compare the version read originally with the current version in DB
- If they differ: another user changed the record since we loaded it → conflict detected → rollback or retry

**Version Stamp Column**
```sql
ALTER TABLE orders ADD COLUMN version INT NOT NULL DEFAULT 0;
```

**Loading**
```java
public Order findById(long id) {
    // SELECT id, status, customer_id, version FROM orders WHERE id = ?
    Order order = ... ;
    order.setVersion(rs.getInt("version"));
    return order;
}
```

**Saving with Conflict Detection**
```java
public void update(Order order) throws OptimisticLockException {
    int rowsUpdated = jdbcTemplate.update(
        "UPDATE orders SET status = ?, version = version + 1 " +
        "WHERE id = ? AND version = ?",
        order.status(), order.id(), order.version()  // check original version
    );
    if (rowsUpdated == 0) {
        // Either row was deleted OR version changed (another user modified it)
        throw new OptimisticLockException("Order " + order.id() + " was modified concurrently");
    }
}
```

**Client Response to Conflict**
- Inform user: "This record was modified by another user. Please reload and try again."
- Alternatively: merge strategies (if non-conflicting fields were changed)

**Pros**
- No locking overhead; high concurrency
- Scales well; most transactions succeed without conflict

**Cons**
- User may lose work (writes a long form, gets conflict at submit time)
- Not appropriate when conflicts are common or correcting conflicts is costly

**When to Use**: Low-conflict domains; "read many, write few" patterns; long-running user editing sessions. **Default choice** unless conflicts are frequent.

**Modern Equivalent**: JPA `@Version` annotation — the EntityManager handles version comparison automatically and throws `OptimisticLockException`.

```java
@Entity
public class Order {
    @Version
    private Integer version;
    // JPA will: UPDATE orders SET ..., version=version+1 WHERE id=? AND version=?
}
```

---

## Pessimistic Offline Lock

**Intent**: Prevents conflicts between concurrent business transactions by requiring a process to acquire a lock before it begins to edit a record.

**How It Works**
- Before reading data to edit, acquire a lock from a lock manager
- Lock is stored in a `locks` table (not a DB row lock — those don't survive request boundaries)
- While lock is held, other users attempting to acquire a lock for the same record are denied
- Lock is released when the business transaction commits or explicitly abandoned
- Locks have an expiry time to handle clients that crash without releasing

**Lock Table**
```sql
CREATE TABLE business_locks (
    lockable_type   VARCHAR(50),
    lockable_id     BIGINT,
    lock_owner      VARCHAR(100),
    acquired_at     TIMESTAMP,
    expires_at      TIMESTAMP,
    PRIMARY KEY (lockable_type, lockable_id)
);
```

**Lock Manager**
```java
public class LockManager {

    public void acquireLock(String type, long id, String owner)
            throws ConcurrentEditException {
        // Try to insert a lock record
        int inserted = jdbcTemplate.update(
            "INSERT INTO business_locks (lockable_type, lockable_id, lock_owner, " +
            "acquired_at, expires_at) VALUES (?, ?, ?, NOW(), NOW() + INTERVAL '30 minutes') " +
            "ON CONFLICT DO NOTHING",
            type, id, owner);

        if (inserted == 0) {
            // Check if existing lock is expired
            Optional<Lock> existingLock = findLock(type, id);
            if (existingLock.isPresent() && existingLock.get().isExpired()) {
                releaseLock(type, id, existingLock.get().owner());
                acquireLock(type, id, owner);  // retry
            } else {
                throw new ConcurrentEditException(
                    "Record is currently being edited by " +
                    existingLock.map(Lock::owner).orElse("another user"));
            }
        }
    }

    public void releaseLock(String type, long id, String owner) {
        jdbcTemplate.update(
            "DELETE FROM business_locks WHERE lockable_type=? AND lockable_id=? AND lock_owner=?",
            type, id, owner);
    }
}
```

**Usage in Service Layer**
```java
public OrderDTO beginEdit(long orderId, String userId) throws ConcurrentEditException {
    lockManager.acquireLock("Order", orderId, userId);
    return orderAssembler.toDTO(orderRepo.findById(orderId));
}

public void commitEdit(long orderId, String userId, OrderUpdateDTO changes) {
    verifyLockOwner("Order", orderId, userId);
    // apply changes...
    orderRepo.save(order);
    lockManager.releaseLock("Order", orderId, userId);
}
```

**Lock Types**
- **Exclusive Write Lock**: Only one writer at a time; readers are unrestricted (default)
- **Exclusive Read Lock**: Only one reader/writer at a time (prevents dirty reads of in-progress work)
- **Read/Write Lock**: Multiple concurrent readers OR one exclusive writer

**Pros**
- Conflicts never reach commit; no user frustration from conflict at save time
- Correct for high-conflict or costly-conflict domains

**Cons**
- Reduced concurrency; users wait for locks
- Dead lock risk (two users hold locks each other needs)
- Orphaned locks if client crashes (requires expiry mechanism)

**When to Use**: High-conflict domains; editing a record takes a long time; correction cost of conflicts is high (financial records, medical data).

---

## Coarse-Grained Lock

**Intent**: Locks a set of related objects with a single lock.

**Problem**: Domain objects form clusters (Customer + Addresses + Contacts). When editing a customer, all related objects need to be locked consistently. Acquiring separate locks per object is error-prone and risks partial locks.

**Solution**: Lock the entire aggregate with one lock. All objects in the group share a version stamp / lock via their root.

**Implementation Options**

1. **Shared version stamp**: All objects in the cluster share the root's version field
```sql
ALTER TABLE addresses ADD COLUMN customer_version INT;  -- mirrors customer.version
```

2. **Root lock covers children**: Lock is acquired on the root (Customer). All mappers for child objects (Address, Contact) also check this lock before writing.

```java
// Lock Customer (root) to lock entire customer aggregate
lockManager.acquireLock("Customer", customerId, userId);
// Now Address and Contact for this customer are implicitly locked
```

**When to Use**
- Editing a cluster/aggregate where changes to any part should block concurrent edits to any other part
- Implementing DDD aggregate locking (one lock per aggregate root)

---

## Implicit Lock

**Intent**: Allows framework or layer supertype code to acquire offline locks automatically, so application code cannot forget to lock.

**Problem**: Pessimistic Offline Lock requires every place that edits data to acquire and release a lock. Forgetting even once leaves data unprotected. Application code carries this burden.

**Solution**: Move lock acquisition into framework code (a layer supertype, aspect, or AOP interceptor). Application code never calls `lockManager.acquire()` explicitly — it happens automatically.

**Implementation (AOP / Framework Layer)**
```java
// Aspect wrapping all mapper update() calls
@Aspect
public class LockAcquisitionAspect {
    @Before("execution(* *Mapper.update(..)) && args(domainObject)")
    public void acquireLock(DomainObject domainObject) {
        String owner = SecurityContext.currentUser();
        lockManager.acquireLock(
            domainObject.getClass().getSimpleName(),
            domainObject.getId(),
            owner);
    }
}
```

**Or via Layer Supertype**
```java
public abstract class DomainObject {
    public void beforeSave() {
        LockManager.current().verifyLockHeld(
            this.getClass().getSimpleName(), this.getId());
    }
}
```

**Pros**: Cannot forget to lock. Consistently applied.

**Cons**: Less visible — developers must understand the implicit behavior. Harder to debug lock failures.

**When to Use**: When Pessimistic Offline Lock is required and there's risk of forgetting to acquire explicitly. Useful in frameworks where DDD aggregate operations are channeled through a known infrastructure path.

---

## Choosing Between Optimistic and Pessimistic

| Factor | Prefer Optimistic | Prefer Pessimistic |
|---|---|---|
| Conflict frequency | Low | High |
| Cost of conflict to user | Low (reload is OK) | High (long form lost) |
| Edit session duration | Short | Long |
| Data sensitivity | Low | High (financial, medical) |
| Concurrency needs | High | Lower |
| Implementation complexity | Low | Medium-High |

**Default**: Use Optimistic Offline Lock. Switch to Pessimistic only when conflict frequency or cost justifies the complexity.
