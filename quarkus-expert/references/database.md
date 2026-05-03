# Database Access
## Chapter 7: Panache Active Record, Repository, Hibernate ORM, MongoDB, Transactions

---

## Panache Overview

Panache simplifies JPA/Hibernate by eliminating boilerplate. Two patterns:

| Pattern | Style | When to Use |
|---|---|---|
| **Active Record** | Entity extends `PanacheEntity` | Simple CRUD, minimal layering |
| **Repository** | Separate `PanacheRepository<T>` | Separation of concerns, testability |

---

## Panache Active Record

### Setup

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-hibernate-orm-panache</artifactId>
</dependency>
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-jdbc-postgresql</artifactId>
</dependency>
```

```properties
quarkus.datasource.db-kind=postgresql
quarkus.datasource.username=myuser
quarkus.datasource.password=mypassword
quarkus.datasource.jdbc.url=jdbc:postgresql://localhost:5432/mydb
quarkus.hibernate-orm.database.generation=drop-and-create   # dev only
quarkus.hibernate-orm.log.sql=true                           # dev debug
```

### Entity

```java
@Entity
public class Fruit extends PanacheEntity {
    // id is inherited as Long id

    public String name;
    public String color;

    @Column(nullable = false)
    public BigDecimal price;

    // Built-in static methods:
    // Fruit.findAll()
    // Fruit.findById(id)
    // Fruit.list("color", "red")
    // Fruit.count()
    // Fruit.deleteAll()
    // fruit.persist()
    // fruit.delete()

    // Custom finder
    public static List<Fruit> findByColor(String color) {
        return list("color", color);
    }

    public static Optional<Fruit> findByName(String name) {
        return find("name", name).firstResultOptional();
    }
}
```

### Composite Primary Key

```java
@Entity
public class OrderLine extends PanacheEntityBase {

    @EmbeddedId
    public OrderLineId id;

    public int quantity;
}
```

### CRUD Examples

```java
// Create
@Transactional
public Fruit create(String name, String color) {
    Fruit fruit = new Fruit();
    fruit.name = name;
    fruit.color = color;
    fruit.persist();
    return fruit;
}

// Read
Fruit byId = Fruit.findById(1L);
List<Fruit> all = Fruit.listAll();
List<Fruit> red = Fruit.list("color", "red");
List<Fruit> sorted = Fruit.listAll(Sort.by("name"));
Optional<Fruit> opt = Fruit.findByIdOptional(99L);

// Update — just modify fields inside @Transactional
@Transactional
public void updateName(Long id, String newName) {
    Fruit fruit = Fruit.findByIdOrElseThrow(id);
    fruit.name = newName;     // no explicit save needed
}

// Delete
@Transactional
public void delete(Long id) {
    Fruit.deleteById(id);
}

// Bulk delete
@Transactional
public long deleteByColor(String color) {
    return Fruit.delete("color", color);
}
```

### Queries

```java
// JPQL-style HQL (short form — table alias is implicit)
Fruit.list("name like ?1", "%apple%");
Fruit.list("name = ?1 and color = ?2", "Apple", "red");
Fruit.list("name = :name", Parameters.with("name", "Apple"));

// Count
long count = Fruit.count("color", "red");

// Exists
boolean exists = Fruit.count("name", "Apple") > 0;

// Pagination
PanacheQuery<Fruit> query = Fruit.findAll();
List<Fruit> page1 = query.page(0, 10).list();    // offset 0, size 10
List<Fruit> page2 = query.page(1, 10).list();

// Stream
try (Stream<Fruit> stream = Fruit.streamAll()) {
    stream.forEach(f -> process(f));
}
```

---

## Panache Repository Pattern

```java
@ApplicationScoped
public class FruitRepository implements PanacheRepository<Fruit> {

    public List<Fruit> findByColor(String color) {
        return list("color", color);
    }

    public Optional<Fruit> findByName(String name) {
        return find("name", name).firstResultOptional();
    }
}
```

```java
// Entity is a plain JPA entity (no PanacheEntity extension)
@Entity
public class Fruit {
    @Id @GeneratedValue
    public Long id;
    public String name;
    public String color;
}
```

```java
@Inject
FruitRepository fruitRepo;

@Transactional
public Fruit save(Fruit fruit) {
    fruitRepo.persist(fruit);
    return fruit;
}
```

---

## Hibernate ORM (Standard JPA)

Full JPA control when Panache isn't enough:

```java
@Inject
EntityManager em;

@Transactional
public List<Fruit> findExpensive() {
    return em.createQuery(
        "SELECT f FROM Fruit f WHERE f.price > :threshold", Fruit.class)
        .setParameter("threshold", new BigDecimal("5.00"))
        .getResultList();
}

// Named queries
@NamedQuery(name = "Fruit.findByColor",
            query = "FROM Fruit WHERE color = :color")
@Entity
public class Fruit { ... }
```

---

## Transactions

### `@Transactional` Annotation

```java
@ApplicationScoped
public class OrderService {

    @Transactional                          // starts a transaction, commits on return
    public Order placeOrder(Cart cart) {
        Order order = new Order(cart.userId);
        order.persist();
        for (CartItem item : cart.items) {
            OrderLine line = new OrderLine(order, item);
            line.persist();
            item.product.stock -= item.quantity;    // dirty check auto-flushes
        }
        return order;
    }

    @Transactional(Transactional.TxType.REQUIRES_NEW)
    public void auditLog(String message) { ... }    // always new transaction

    @Transactional(rollbackOn = BusinessException.class)
    public void riskMethod() throws BusinessException { ... }
}
```

### Transaction Propagation Types

| Type | Behavior |
|---|---|
| `REQUIRED` (default) | Join existing or start new |
| `REQUIRES_NEW` | Always start new, suspend existing |
| `MANDATORY` | Must have existing; throw if none |
| `SUPPORTS` | Join if existing; otherwise no transaction |
| `NOT_SUPPORTED` | Suspend existing; run without transaction |
| `NEVER` | Throw if transaction exists |

### Programmatic Transactions

```java
@Inject
QuarkusTransaction qt;

public void programmatic() {
    QuarkusTransaction.requiringNew().run(() -> {
        fruit.persist();
    });
}
```

---

## Multiple Data Sources

```properties
# Default datasource
quarkus.datasource.db-kind=postgresql
quarkus.datasource.jdbc.url=jdbc:postgresql://localhost/main

# Named datasource
quarkus.datasource."users-db".db-kind=postgresql
quarkus.datasource."users-db".jdbc.url=jdbc:postgresql://localhost/users

# Named persistence unit
quarkus.hibernate-orm."users".datasource=users-db
quarkus.hibernate-orm."users".packages=com.example.users
```

```java
@Inject
@PersistenceUnit("users")
EntityManager userEm;
```

---

## MongoDB with Panache

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-mongodb-panache</artifactId>
</dependency>
```

```properties
quarkus.mongodb.connection-string=mongodb://localhost:27017
quarkus.mongodb.database=mydb
```

### MongoDB Entity (Active Record)

```java
@MongoEntity(collection = "fruits")
public class Fruit extends PanacheMongoEntity {
    // id is ObjectId id (inherited)
    public String name;
    public String color;

    public static List<Fruit> findByColor(String color) {
        return list("color", color);
    }
}
```

### MongoDB Repository

```java
@ApplicationScoped
public class FruitRepository implements PanacheMongoRepository<Fruit> {

    public List<Fruit> findByColor(String color) {
        return list("color", color);
    }

    // Native MongoDB filter
    public List<Fruit> findExpensive() {
        return list(Filters.gt("price", 5.0));
    }
}
```

---

## REST Data with Panache

Auto-generate full CRUD REST API from a Panache entity:

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-hibernate-orm-rest-data-panache</artifactId>
</dependency>
```

```java
public interface FruitResource extends PanacheEntityResource<Fruit, Long> {
    // Generates: GET /fruit, GET /fruit/{id}, POST /fruit,
    //            PUT /fruit/{id}, DELETE /fruit/{id}
}
```

Customize with annotations:
```java
@ResourceProperties(path = "fruits", paged = true, hal = true)
public interface FruitResource extends PanacheEntityResource<Fruit, Long> {

    @MethodProperties(exposed = false)
    Response delete(Long id);               // disable delete
}
```

---

## Reactive Data Access with Hibernate Reactive

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-hibernate-reactive-panache</artifactId>
</dependency>
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-reactive-pg-client</artifactId>
</dependency>
```

```java
@Entity
public class ReactiveFruit extends PanacheEntity {
    public String name;
}

@ApplicationScoped
public class FruitService {

    @WithTransaction
    public Uni<Fruit> create(String name) {
        Fruit fruit = new Fruit();
        fruit.name = name;
        return fruit.persist();
    }

    public Uni<List<Fruit>> list() {
        return Fruit.listAll();
    }
}
```

Use `@WithTransaction` instead of `@Transactional` for reactive (non-blocking) transactions.
