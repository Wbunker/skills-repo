# Advanced Mapping and Topics
*Chapters 11–12 — Pro JPA 2 in Java EE 8, Mike Keith*

## Advanced Relationship Mappings (Ch 11)

### Self-Referential Relationships
```java
@Entity
public class Employee {
    @Id private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "manager_id")
    private Employee manager;

    @OneToMany(mappedBy = "manager")
    private List<Employee> reports = new ArrayList<>();
}
```

### Compound Primary Key as Foreign Key
When an entity with an `@EmbeddedId` is referenced as a FK in another entity:

```java
@Entity
@IdClass(DepartmentId.class)
public class Department {
    @Id private String country;
    @Id private Long   deptNo;
    private String name;
}

@Entity
public class Employee {
    @Id private Long id;

    @ManyToOne
    @JoinColumns({
        @JoinColumn(name = "dept_country", referencedColumnName = "country"),
        @JoinColumn(name = "dept_no",      referencedColumnName = "deptNo")
    })
    private Department department;
}
```

### Overriding Relationship Join Column in Embeddable
```java
@Entity
public class Employee {
    @Embedded
    @AssociationOverride(name = "address.country",
                         joinColumns = @JoinColumn(name = "home_country_id"))
    private ContactInfo contactInfo;
}
```

### Orphaned Relationship Objects (Advanced Cascade Scenarios)
When using `orphanRemoval = true` on a `@OneToMany`, removing an entity from the collection **immediately schedules a DELETE**. Do not re-add the same instance to another parent's collection in the same transaction — it will cause a conflict.

---

## Entity Graphs (JPA 2.1+)

Entity graphs control what is fetched in a single query without changing the entity mapping.

### Named Entity Graph
```java
@Entity
@NamedEntityGraph(
    name = "Employee.withDeptAndProjects",
    attributeNodes = {
        @NamedAttributeNode("department"),
        @NamedAttributeNode(value = "projects", subgraph = "project-tasks")
    },
    subgraphs = @NamedSubgraph(name = "project-tasks",
                                attributeNodes = @NamedAttributeNode("tasks"))
)
public class Employee { ... }
```

Apply to a query:
```java
EntityGraph<?> graph = em.getEntityGraph("Employee.withDeptAndProjects");

// fetch graph: attributes in graph are EAGER; all others LAZY
List<Employee> emps = em.createQuery("SELECT e FROM Employee e", Employee.class)
    .setHint("javax.persistence.fetchgraph", graph)
    .getResultList();

// load graph: attributes in graph are EAGER; others keep their mapping default
em.createQuery("SELECT e FROM Employee e", Employee.class)
    .setHint("javax.persistence.loadgraph", graph)
    .getResultList();
```

### Dynamic Entity Graph
```java
EntityGraph<Employee> graph = em.createEntityGraph(Employee.class);
graph.addAttributeNodes("department");
Subgraph<Project> sub = graph.addSubgraph("projects");
sub.addAttributeNodes("tasks");

Map<String, Object> hints = Map.of("javax.persistence.fetchgraph", graph);
Employee e = em.find(Employee.class, 1L, hints);
```

---

## Optimistic Locking (Ch 12)

### @Version
```java
@Entity
public class Employee {
    @Id private Long id;

    @Version                         // maps to VERSION column (int, long, Timestamp, etc.)
    private int version;

    private String name;
    private BigDecimal salary;
}
```

When two transactions read the same entity and both try to commit:
- First commit succeeds, version is incremented.
- Second commit fails with `OptimisticLockException` (or `RollbackException` wrapping it).

### LockModeType for Optimistic Locking
```java
// Re-read with optimistic lock (default when @Version present)
Employee e = em.find(Employee.class, 1L, LockModeType.OPTIMISTIC);

// Force version increment even on read (useful to prevent phantom reads)
em.lock(e, LockModeType.OPTIMISTIC_FORCE_INCREMENT);

// In a query
em.createQuery("SELECT e FROM Employee e WHERE e.id = :id", Employee.class)
  .setParameter("id", 1L)
  .setLockMode(LockModeType.OPTIMISTIC)
  .getSingleResult();
```

### Handling OptimisticLockException
```java
try {
    tx.begin();
    Employee e = em.find(Employee.class, id);
    e.setSalary(newSalary);
    tx.commit();
} catch (OptimisticLockException | RollbackException ex) {
    tx.rollback();
    // Notify user, retry, or merge changes
}
```

---

## Pessimistic Locking (Ch 12)

Acquires DB-level lock during the transaction. Prevents concurrent reads (shared) or writes (exclusive).

```java
// Shared lock — prevents dirty/non-repeatable reads
Employee e = em.find(Employee.class, 1L, LockModeType.PESSIMISTIC_READ);

// Exclusive lock — prevents all concurrent access
Employee e = em.find(Employee.class, 1L, LockModeType.PESSIMISTIC_WRITE);

// Exclusive lock + version increment (for entities with @Version)
em.lock(e, LockModeType.PESSIMISTIC_FORCE_INCREMENT);
```

### Lock Timeout Hint
```java
Map<String, Object> hints = Map.of("javax.persistence.lock.timeout", 2000);  // ms; 0 = no wait
Employee e = em.find(Employee.class, 1L, LockModeType.PESSIMISTIC_WRITE, hints);
```

`LockTimeoutException` thrown if lock cannot be acquired within timeout.

---

## Second-Level (L2) Cache (Ch 12)

The L1 cache (persistence context) is per-EM and always on. The L2 cache is **shared across EntityManager instances** and must be explicitly configured.

### Enabling L2 Cache in persistence.xml
```xml
<shared-cache-mode>ENABLE_SELECTIVE</shared-cache-mode>
```
Options: `ALL`, `NONE`, `ENABLE_SELECTIVE` (only `@Cacheable(true)`), `DISABLE_SELECTIVE` (all except `@Cacheable(false)`), `UNSPECIFIED`.

### @Cacheable
```java
@Entity
@Cacheable(true)   // enable L2 cache for this entity
public class Country { ... }

@Entity
@Cacheable(false)  // disable L2 cache (e.g., highly volatile data)
public class Order { ... }
```

### Evicting the Cache
```java
Cache cache = emf.getCache();
cache.evict(Employee.class, 1L);   // evict single entity
cache.evict(Employee.class);        // evict all instances of type
cache.evictAll();                   // clear entire L2 cache
```

### Controlling Cache Retrieval/Store Per Query
```java
em.createQuery("SELECT e FROM Employee e", Employee.class)
  .setHint("javax.persistence.cache.retrieveMode", CacheRetrieveMode.BYPASS) // skip cache reads
  .setHint("javax.persistence.cache.storeMode",    CacheStoreMode.REFRESH)   // force store after read
  .getResultList();
```

| Mode | Meaning |
|------|---------|
| `CacheRetrieveMode.USE` (default) | Use L2 cache on reads |
| `CacheRetrieveMode.BYPASS` | Skip L2 cache; go to DB |
| `CacheStoreMode.USE` (default) | Store query results in L2 cache |
| `CacheStoreMode.BYPASS` | Do not update cache |
| `CacheStoreMode.REFRESH` | Overwrite existing cached data |

---

## Entity Listeners and Lifecycle Callbacks (Ch 12)

### Inline Lifecycle Callbacks
```java
@Entity
public class Employee {
    @PrePersist
    void onPrePersist() { this.createdAt = LocalDateTime.now(); }

    @PreUpdate
    void onPreUpdate() { this.updatedAt = LocalDateTime.now(); }

    @PostLoad
    void onPostLoad() { /* after find/query */ }

    @PostPersist
    void onPostPersist() { /* after INSERT committed */ }

    @PreRemove
    void onPreRemove() { /* before DELETE */ }

    @PostRemove
    void onPostRemove() { /* after DELETE committed */ }

    @PostUpdate
    void onPostUpdate() { /* after UPDATE committed */ }
}
```

### External Entity Listener Class
```java
public class AuditListener {
    @PrePersist @PreUpdate
    public void setTimestamps(Auditable entity) {
        if (entity.getCreatedAt() == null) entity.setCreatedAt(LocalDateTime.now());
        entity.setUpdatedAt(LocalDateTime.now());
    }
}

@Entity
@EntityListeners(AuditListener.class)
public class Employee implements Auditable { ... }
```

### Listener Inheritance
- Listeners defined on a superclass are inherited by subclasses.
- Use `@ExcludeSuperclassListeners` to suppress inherited listeners.
- Use `@ExcludeDefaultListeners` to suppress default listeners registered in orm.xml.

### Default Listeners (global, applied to all entities)
Registered in `orm.xml`:
```xml
<entity-listeners>
  <entity-listener class="com.example.AuditListener"/>
</entity-listeners>
```

---

## Stored Procedures (JPA 2.1+)

### @NamedStoredProcedureQuery
```java
@Entity
@NamedStoredProcedureQuery(
    name = "Employee.getByDept",
    procedureName = "GET_EMPLOYEES_BY_DEPT",
    resultClasses = Employee.class,
    parameters = {
        @StoredProcedureParameter(name = "p_dept_id",   mode = ParameterMode.IN,  type = Long.class),
        @StoredProcedureParameter(name = "p_emp_count", mode = ParameterMode.OUT, type = Integer.class)
    }
)
public class Employee { ... }
```

Execute:
```java
StoredProcedureQuery spq = em.createNamedStoredProcedureQuery("Employee.getByDept");
spq.setParameter("p_dept_id", 10L);
spq.execute();
List<Employee> employees = spq.getResultList();
Integer count = (Integer) spq.getOutputParameterValue("p_emp_count");
```

### Dynamic Stored Procedure Call
```java
StoredProcedureQuery spq = em.createStoredProcedureQuery("GET_EMP_COUNT");
spq.registerStoredProcedureParameter(1, Integer.class, ParameterMode.OUT);
spq.execute();
Integer count = (Integer) spq.getOutputParameterValue(1);
```

---

## @Convert — Attribute Converters (JPA 2.1+)

Map Java types to custom column representations.

```java
@Converter(autoApply = true)   // applies to all Boolean fields automatically
public class BooleanToYNConverter implements AttributeConverter<Boolean, String> {
    public String convertToDatabaseColumn(Boolean val) { return val ? "Y" : "N"; }
    public Boolean convertToEntityAttribute(String col) { return "Y".equals(col); }
}

// Manual application (when autoApply = false):
@Convert(converter = BooleanToYNConverter.class)
private Boolean active;
```

---

## Unsynchronized Persistence Context (JPA 2.1+)

An `UNSYNCHRONIZED` persistence context does not auto-join the active JTA transaction. Changes flush only when explicitly joined.

```java
@PersistenceContext(synchronization = SynchronizationType.UNSYNCHRONIZED)
private EntityManager em;

// Explicitly join transaction when ready to flush:
em.joinTransaction();
```
Useful for "draft" or "pending" workflows where you want to stage changes before committing.
