# Object-Relational Metadata Mapping Patterns — PEAA

These three patterns address how to describe, query, and abstract access to persistent objects — moving beyond hand-coded SQL toward more configurable and expressive approaches.

---

## Metadata Mapping

**Intent**: Holds details of object-relational mapping in metadata, often driving a generic mapping framework.

**Problem**: Hand-coded Data Mappers repeat similar patterns for every class: read column X → set field Y. This is tedious and diverges as the schema evolves.

**Solution**: Describe the mapping in configuration (XML, annotations, attributes) and write generic mapper code that reads the configuration at runtime.

**Metadata Describes**
- Which table maps to which class
- Which column maps to which field
- Data type conversions
- Association handling (FK column, join table)
- Inheritance strategy and discriminator

**Implementation Approaches**

1. **Reflection + Annotations** (modern standard)
```java
@Entity
@Table(name = "orders")
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "status")
    private String status;

    @ManyToOne
    @JoinColumn(name = "customer_id")
    private Customer customer;

    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL)
    private List<LineItem> lineItems;
}
```

2. **XML Descriptor** (Hibernate's original approach)
```xml
<class name="Order" table="orders">
    <id name="id" column="id">
        <generator class="identity"/>
    </id>
    <property name="status" column="status"/>
    <many-to-one name="customer" column="customer_id"/>
    <bag name="lineItems" table="line_items" cascade="all">
        <key column="order_id"/>
        <one-to-many class="LineItem"/>
    </bag>
</class>
```

**Benefits**
- Mapping logic centralized and declarative
- Mapper code is generic — doesn't change as domain classes change
- Framework can generate SQL at startup

**Modern Reality**: Metadata Mapping IS what ORM frameworks implement. JPA annotations are the industry-standard metadata format. Understanding this pattern explains WHY annotations like `@Column`, `@JoinColumn`, and `@Table` exist and what the ORM does with them.

---

## Query Object

**Intent**: An object that represents a database query.

**Problem**: Embedding SQL strings throughout application code is brittle — typos, schema changes break strings silently, and queries are hard to compose programmatically.

**Solution**: Represent a query as an object. Build the query by calling methods; the Query Object translates to SQL at execution time.

**Structure**
```java
QueryObject query = new QueryObject(Order.class);
query.addCriteria(Criteria.greaterThan("total", new Money(100, USD)));
query.addCriteria(Criteria.equals("status", "submitted"));
query.addOrdering("createdAt", Direction.DESC);

List<Order> results = query.execute(session);
// Generates: SELECT * FROM orders WHERE total > 100 AND status = 'submitted'
//            ORDER BY created_at DESC
```

**Benefits**
- Type-safe query construction (no string concatenation)
- Composable: criteria can be built incrementally from user input
- Database-independent: same query object generates different SQL dialects
- Testable: can inspect the query object without executing it

**Criteria Pattern**
```java
public interface Criteria {
    String toSql(ClassDescriptor descriptor);

    static Criteria equals(String field, Object value) {
        return desc -> desc.columnFor(field) + " = " + formatValue(value);
    }

    static Criteria greaterThan(String field, Object value) {
        return desc -> desc.columnFor(field) + " > " + formatValue(value);
    }

    static Criteria and(Criteria left, Criteria right) {
        return desc -> "(" + left.toSql(desc) + " AND " + right.toSql(desc) + ")";
    }
}
```

**Modern Equivalents**
- **JPA Criteria API**: Type-safe programmatic query construction
- **QueryDSL**: Code-generated type-safe query DSL (more ergonomic than JPA Criteria API)
- **Spring Data Specifications**: Composable query predicates for Spring Data repositories
- **jOOQ**: SQL-first query builder with type safety

**When to Use**
- Queries constructed dynamically from user-supplied filters
- Need database independence
- Complex conditional query logic (instead of concatenating SQL strings)

---

## Repository

**Intent**: Mediates between the domain and data mapping layers using a collection-like interface for accessing domain objects.

**Problem**: When using Data Mapper, client code still needs to invoke mappers — which means knowing about persistence infrastructure. Query logic (how to find objects) leaks into service or domain code.

**Solution**: A Repository presents a collection-like interface. Clients add objects to, remove from, and query the repository as if it were an in-memory collection. All SQL / query logic lives inside.

**Interface (appears collection-like)**
```java
public interface OrderRepository {
    Order findById(OrderId id);
    List<Order> findByCustomer(CustomerId customerId);
    List<Order> findSubmittedAfter(LocalDate date);
    List<Order> findAll(Specification<Order> spec);   // with Query Object / Specification
    void save(Order order);
    void remove(Order order);
}
```

**Implementation (hides persistence details)**
```java
public class JpaOrderRepository implements OrderRepository {
    @PersistenceContext
    private EntityManager em;

    @Override
    public Order findById(OrderId id) {
        return em.find(Order.class, id.value());
    }

    @Override
    public List<Order> findByCustomer(CustomerId customerId) {
        return em.createQuery(
            "SELECT o FROM Order o WHERE o.customerId = :cid", Order.class)
            .setParameter("cid", customerId.value())
            .getResultList();
    }

    @Override
    public void save(Order order) {
        em.persist(order);
    }
}
```

**Specification Pattern Integration**
For complex, composable query conditions:
```java
public interface Specification<T> {
    boolean isSatisfiedBy(T candidate);           // in-memory evaluation
    Predicate toPredicate(CriteriaBuilder cb, Root<T> root);  // to JPA predicate
}

Specification<Order> highValue = order -> order.total().isGreaterThan(THRESHOLD);
Specification<Order> submitted = order -> order.status() == SUBMITTED;
Specification<Order> highValueSubmitted = highValue.and(submitted);

List<Order> orders = orderRepository.findAll(highValueSubmitted);
```

**Repository vs. DAO**
| Aspect | Repository | DAO |
|---|---|---|
| Abstraction | Domain collection | DB table |
| Language | Domain concepts | DB operations |
| Used with | Domain Model | Any approach |
| Returns | Domain objects | Often DTOs or Result Sets |

**Repository belongs to the domain layer** — it's an interface defined in terms of domain concepts. The implementation belongs to the infrastructure layer. This allows domain code to depend on the repository interface without depending on any persistence technology.

**Modern Equivalents**
- **Spring Data JPA**: `JpaRepository<Order, Long>` — provides standard CRUD + derived query methods
- **Spring Data's `@Query`**: Custom JPQL/SQL when derived methods aren't enough
- **Axon's `EventSourcingRepository`**: Repository backed by event store
- The Repository pattern is the dominant pattern for data access in modern Spring/DDD applications

**When to Use**
- Domain Model + Data Mapper combination
- Multiple query strategies needed for one domain class
- Want to hide persistence technology from domain and service layers
- Test: can substitute in-memory repository for fast unit tests

**Anti-patterns to Avoid**
- Repository that exposes `EntityManager` or `Session` to callers (breaks abstraction)
- One repository per table (instead of one per aggregate root — DDD principle)
- Thin repository that's just a pass-through to JPA without adding domain-language query methods
