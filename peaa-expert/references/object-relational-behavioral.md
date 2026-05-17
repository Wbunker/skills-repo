# Object-Relational Behavioral Patterns — PEAA

These three patterns address the behavioral challenges of mapping domain objects to a relational database: tracking changes, preventing duplicate loads, and deferring data loading.

---

## Unit of Work

**Intent**: Maintains a list of objects affected by a business transaction and coordinates the writing out of changes and the resolution of concurrency problems.

**Problem It Solves**
Without Unit of Work, code must manually track what changed and call the right save method at the right time. This leads to:
- Missing saves (forgot to call `update()`)
- Duplicate saves (called `update()` too many times)
- Incorrect ordering (save before dependencies are saved)

**How It Works**
1. Objects register themselves with the Unit of Work when they are:
   - **New** (created, not yet in DB)
   - **Dirty** (loaded and modified)
   - **Removed** (marked for deletion)
   - **Clean** (loaded, not modified — tracked but not saved)
2. At transaction commit, Unit of Work:
   - INSERTs all new objects
   - UPDATEs all dirty objects (in correct order)
   - DELETEs all removed objects
   - Wraps everything in a single DB transaction

**Registration Approaches**
- **Caller Registration**: Application code explicitly calls `unitOfWork.registerDirty(obj)` — simple but error-prone
- **Object Registration**: Domain objects call `unitOfWork.registerDirty(this)` in their setters — safer but couples domain to UoW
- **Unit of Work Controller**: UoW takes a snapshot at load time, compares at commit (change detection) — most transparent; used by Hibernate

**Example (simplified)**
```java
public class UnitOfWork {
    private List<DomainObject> newObjects = new ArrayList<>();
    private List<DomainObject> dirtyObjects = new ArrayList<>();
    private List<DomainObject> removedObjects = new ArrayList<>();

    public void registerNew(DomainObject obj) { newObjects.add(obj); }
    public void registerDirty(DomainObject obj) {
        if (!dirtyObjects.contains(obj)) dirtyObjects.add(obj);
    }
    public void registerRemoved(DomainObject obj) { removedObjects.add(obj); }

    public void commit() {
        insertNew();
        updateDirty();
        deleteRemoved();
    }

    private void insertNew() {
        for (DomainObject obj : newObjects)
            MapperRegistry.getMapper(obj.getClass()).insert(obj);
    }
    private void updateDirty() {
        for (DomainObject obj : dirtyObjects)
            MapperRegistry.getMapper(obj.getClass()).update(obj);
    }
    private void deleteRemoved() {
        for (DomainObject obj : removedObjects)
            MapperRegistry.getMapper(obj.getClass()).delete(obj);
    }
}
```

**Thread Safety**: One Unit of Work per request/thread (request-scoped). Use a thread-local or request context to hold the current UoW.

**Modern Equivalent**: JPA's `EntityManager` / Hibernate's `Session` implement Unit of Work pattern. The "flush" operation is Unit of Work commit.

---

## Identity Map

**Intent**: Ensures that each object gets loaded only once by keeping every loaded object in a map. Looks up objects using the map when referring to them.

**Problem It Solves**
Without Identity Map, loading the same DB row twice in one transaction creates two distinct Java objects. This breaks:
- Object identity (two objects representing the same entity are `!=`)
- Modifications on one object not reflected in the other
- Duplicate writes at save time

**How It Works**
- One map per class per Unit of Work/session
- Key: database primary key; Value: loaded domain object
- `find(id)` checks the map first; only queries DB on cache miss
- Newly inserted objects are added to the map

**Example**
```java
public class IdentityMap<K, V> {
    private Map<K, V> store = new HashMap<>();

    public V get(K key) { return store.get(key); }
    public void put(K key, V value) { store.put(key, value); }
    public boolean contains(K key) { return store.containsKey(key); }
}

// In OrderMapper:
public Order findById(long id) throws SQLException {
    Order cached = identityMap.get(id);
    if (cached != null) return cached;          // cache hit

    // cache miss — go to DB
    ResultSet rs = executeQuery(id);
    Order order = load(rs);
    identityMap.put(id, order);                 // register in map
    return order;
}
```

**Scope**
- Identity Map is per-session / per-Unit of Work — NOT a cross-session cache (that would be a second-level cache, which is a different concern)
- Each request gets a fresh Identity Map; objects don't survive across transactions

**Interaction with Unit of Work**: The Identity Map tracks all loaded objects. The Unit of Work tracks which of those are dirty/new/removed. They work together — often the same object plays both roles in a session object (Hibernate Session / JPA EntityManager).

**Modern Equivalent**: JPA first-level cache / Hibernate session-level cache IS the Identity Map.

---

## Lazy Load

**Intent**: An object that doesn't contain all of the data you need but knows how to get it.

**Problem It Solves**
Loading an object's full graph (Customer → Orders → LineItems → Products) eagerly fetches far more data than any single use case needs, causing:
- Excessive DB queries / data transfer
- Slow response times
- Risk of loading entire database graph

**Four Implementation Patterns**

### 1. Lazy Initialization
Check a field for null on first access; load it then.
```java
public class Customer {
    private List<Order> orders;  // null until accessed

    public List<Order> getOrders() {
        if (orders == null) {
            orders = OrderMapper.findByCustomer(this.id);
        }
        return orders;
    }
}
```
- Simplest implementation
- Requires domain object to know about mapper — breaks persistence ignorance
- Works fine in Active Record; awkward in Data Mapper

### 2. Virtual Proxy
A proxy object looks identical to the real object but loads data on first method call.
```java
// Proxy returned by mapper; loads real collection on first access
public class OrderCollectionProxy implements List<Order> {
    private Long customerId;
    private List<Order> delegate;

    @Override
    public Order get(int index) {
        if (delegate == null) delegate = OrderMapper.findByCustomer(customerId);
        return delegate.get(index);
    }
    // ... other List methods delegating similarly
}
```
- Transparent to client code
- More complex to implement; often generated by frameworks

### 3. Value Holder
Wrap the value in a holder object; client must call `getValue()` explicitly.
```java
public class Customer {
    private ValueHolder<List<Order>> orders;

    public Customer(long id) {
        this.orders = new ValueHolder<>(() -> OrderMapper.findByCustomer(id));
    }

    public List<Order> getOrders() { return orders.getValue(); }
}

public class ValueHolder<T> {
    private Supplier<T> loader;
    private T value;

    public T getValue() {
        if (value == null) value = loader.get();
        return value;
    }
}
```
- Explicit; client code knows it's lazy
- Less transparent than Virtual Proxy

### 4. Ghost
Object loaded with only its ID. First access to any field triggers full load.
```java
public class Order {
    private LoadState state = LoadState.GHOST;
    private long id;
    private String status;

    public String getStatus() {
        if (state == LoadState.GHOST) load();
        return status;
    }

    private void load() {
        Order loaded = OrderMapper.findById(id);
        this.status = loaded.status;
        this.state = LoadState.LOADED;
    }
}
```
- Transparent to client code like Virtual Proxy
- Requires all field accessors to check load state — verbose

**When to Use Lazy Load**
- Associations that are often NOT needed when the owning object is loaded
- Collections with many members
- Associated objects that are large or expensive to load

**When NOT to Use**
- Associations that are almost always needed — eager loading is more efficient
- Simple schemas where the full graph is small

**N+1 Problem**: Naive lazy loading of a collection of N objects, each lazily loading an association, causes N+1 queries. Solution: batch loading or JOIN FETCH when you know you need the association.

**Modern Equivalent**: JPA/Hibernate `FetchType.LAZY` on associations. Virtual Proxy implemented by Hibernate's proxy mechanism (Javassist/ByteBuddy). The `@LazyCollection` and `@BatchSize` annotations address the N+1 problem.
