# Database Access with Spring Boot

Chapter 4 of *Spring Boot Up & Running* — JPA entities, Spring Data repositories, datasource configuration, H2, transactions.

---

## Auto-configuration Behavior

When `spring-boot-starter-data-jpa` is on the classpath, Spring Boot auto-configures:
- A `DataSource` from `spring.datasource.*` properties
- A `JpaTransactionManager`
- Hibernate as the JPA provider
- `EntityManagerFactory` with sensible defaults
- Spring Data JPA repository scanning from the main package downward

Add an in-memory database for development/testing:
```xml
<dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <scope>runtime</scope>
</dependency>
```

Spring Boot detects H2 and auto-configures it. Access the H2 console at `http://localhost:8080/h2-console` after enabling:
```properties
spring.h2.console.enabled=true
spring.datasource.url=jdbc:h2:mem:testdb
```

---

## Datasource Configuration

```properties
# PostgreSQL example
spring.datasource.url=jdbc:postgresql://localhost:5432/mydb
spring.datasource.username=myuser
spring.datasource.password=secret
spring.datasource.driver-class-name=org.postgresql.Driver

# Connection pool (HikariCP is the default)
spring.datasource.hikari.maximum-pool-size=10
spring.datasource.hikari.minimum-idle=2
spring.datasource.hikari.connection-timeout=30000
```

---

## JPA Entity

```java
@Entity
@Table(name = "coffees")
public class Coffee {

    @Id
    private String id;

    @NotBlank
    private String name;

    // No-arg constructor required by JPA
    public Coffee() {}

    public Coffee(String id, String name) {
        this.id = id;
        this.name = name;
    }
    // getters/setters...
}
```

### Common JPA Annotations

| Annotation | Purpose |
|-----------|---------|
| `@Entity` | Marks the class as a JPA managed entity |
| `@Table(name="...")` | Maps to a specific table name |
| `@Id` | Declares the primary key field |
| `@GeneratedValue` | Auto-generates the primary key |
| `@Column(name="...", nullable=false)` | Column customization |
| `@Transient` | Field is not persisted |
| `@OneToMany` / `@ManyToOne` | Relationship mappings |
| `@JoinColumn` | Specifies the foreign key column |
| `@Enumerated(EnumType.STRING)` | Persists enum as string |

### Primary Key Generation Strategies

```java
// Auto-increment (database generated)
@Id
@GeneratedValue(strategy = GenerationType.IDENTITY)
private Long id;

// UUID (application generated)
@Id
@GeneratedValue(strategy = GenerationType.UUID)  // JPA 3.1 / Hibernate 6
private UUID id;

// Manually assigned (no generation)
@Id
private String id;
```

---

## Spring Data JPA Repositories

Spring Data JPA eliminates boilerplate DAO code. Extend one of these interfaces:

| Interface | What it provides |
|-----------|----------------|
| `Repository<T, ID>` | Marker only; no methods |
| `CrudRepository<T, ID>` | `save`, `findById`, `findAll`, `delete`, `count` |
| `PagingAndSortingRepository<T, ID>` | Adds `findAll(Pageable)` and `findAll(Sort)` |
| `JpaRepository<T, ID>` | Adds `flush`, `saveAndFlush`, `deleteInBatch`, `findAll(Example)` |

```java
public interface CoffeeRepository extends CrudRepository<Coffee, String> {
    // Spring Data derives queries from method names automatically:
    List<Coffee> findByName(String name);
    Optional<Coffee> findByNameIgnoreCase(String name);
    List<Coffee> findByNameContainingOrderByNameAsc(String substring);
    boolean existsByName(String name);
    long countByName(String name);
    void deleteByName(String name);
}
```

---

## Query Methods — Derived Query Syntax

Spring Data parses method names to generate JPQL:

| Keyword | Example | Generated clause |
|---------|---------|-----------------|
| `findBy` | `findByName` | `WHERE name = ?` |
| `findByNameAnd` | `findByNameAndOrigin` | `WHERE name = ? AND origin = ?` |
| `findByNameOr` | `findByNameOrOrigin` | `WHERE name = ? OR origin = ?` |
| `Containing` | `findByNameContaining` | `WHERE name LIKE %?%` |
| `StartingWith` | `findByNameStartingWith` | `WHERE name LIKE ?%` |
| `Between` | `findByPriceBetween` | `WHERE price BETWEEN ? AND ?` |
| `LessThan` | `findByPriceLessThan` | `WHERE price < ?` |
| `IsNull` | `findByOriginIsNull` | `WHERE origin IS NULL` |
| `OrderBy` | `findByNameOrderByPriceAsc` | `ORDER BY price ASC` |

---

## Custom JPQL Queries

```java
public interface CoffeeRepository extends JpaRepository<Coffee, String> {

    // JPQL — uses entity/field names, not table/column names
    @Query("SELECT c FROM Coffee c WHERE c.price < :maxPrice ORDER BY c.price ASC")
    List<Coffee> findCheaperThan(@Param("maxPrice") double maxPrice);

    // Native SQL — use cautiously, bypasses JPA abstraction
    @Query(value = "SELECT * FROM coffees WHERE origin = :origin", nativeQuery = true)
    List<Coffee> findByOriginNative(@Param("origin") String origin);

    // Modifying query (INSERT/UPDATE/DELETE)
    @Modifying
    @Transactional
    @Query("UPDATE Coffee c SET c.price = :price WHERE c.id = :id")
    int updatePrice(@Param("id") String id, @Param("price") double price);
}
```

---

## Pagination and Sorting

```java
// Controller
@GetMapping
public Page<Coffee> getCoffees(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size,
        @RequestParam(defaultValue = "name") String sortBy) {
    Pageable pageable = PageRequest.of(page, size, Sort.by(sortBy));
    return coffeeRepository.findAll(pageable);
}

// Repository (extend JpaRepository or PagingAndSortingRepository)
Page<Coffee> findByOrigin(String origin, Pageable pageable);
```

`Page<T>` includes: content, totalElements, totalPages, number (current page), size.

---

## Transactions

Spring Boot auto-configures `@EnableTransactionManagement`. Use `@Transactional` to demarcate transactions:

```java
@Service
@Transactional(readOnly = true)   // default read-only for all methods
public class CoffeeService {

    @Transactional          // overrides class-level: read-write for this method
    public Coffee create(Coffee coffee) {
        return coffeeRepository.save(coffee);
    }

    public List<Coffee> findAll() {
        return coffeeRepository.findAll();   // uses read-only tx
    }
}
```

Key `@Transactional` attributes:
- `readOnly = true` — hint to JPA/DB for optimization; no dirty checking
- `propagation` — `REQUIRED` (default), `REQUIRES_NEW`, `SUPPORTS`, etc.
- `isolation` — `DEFAULT`, `READ_COMMITTED`, `SERIALIZABLE`, etc.
- `rollbackFor` — exception types that trigger rollback (default: `RuntimeException`)
- `timeout` — seconds before transaction is rolled back

---

## Schema Management

```properties
# Hibernate DDL auto (dev only)
spring.jpa.hibernate.ddl-auto=create-drop   # dev: recreate schema each start
spring.jpa.hibernate.ddl-auto=update        # dev: add columns if missing
spring.jpa.hibernate.ddl-auto=validate      # prod: verify schema but don't change
spring.jpa.hibernate.ddl-auto=none          # prod: let Flyway/Liquibase manage

# Print SQL (useful for debugging)
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
```

For production schema migrations, use **Flyway** or **Liquibase**:
```xml
<dependency>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-core</artifactId>
</dependency>
```
Place migrations in `src/main/resources/db/migration/V1__init.sql`, `V2__add_column.sql`, etc.

---

## Relationships

```java
// One-to-Many (Order has many Items)
@Entity
public class Order {
    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<OrderItem> items = new ArrayList<>();
}

@Entity
public class OrderItem {
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id")
    private Order order;
}
```

**N+1 problem**: lazy loading triggers a query per entity when iterating a collection.

Fix with `@EntityGraph` or a JOIN FETCH query:
```java
@Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.id = :id")
Optional<Order> findWithItems(@Param("id") Long id);
```

---

## Common Pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| `LazyInitializationException` | Accessing lazy collection outside transaction | Use `@Transactional` on service method or use eager loading |
| `NonUniqueResultException` | Query returning multiple rows when one expected | Use `findAll` variant or add `DISTINCT` |
| Schema not created | Missing `@Entity` scan | Ensure entities are in sub-packages of `@SpringBootApplication` |
| `detached entity passed to persist` | Saving an entity that was loaded in another session | Re-load or use `merge()` |
| Circular JSON on relationship | Bidirectional mapping serialized by Jackson | Use `@JsonIgnore`, `@JsonManagedReference`/`@JsonBackReference`, or DTOs |
