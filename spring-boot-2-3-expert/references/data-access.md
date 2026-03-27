# Spring Boot 2.3 — Data Access

## Datasource Configuration

### Standard (HikariCP, the default pool)

```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/myapp
spring.datasource.username=postgres
spring.datasource.password=secret
spring.datasource.driver-class-name=org.postgresql.Driver

# HikariCP tuning
spring.datasource.hikari.maximum-pool-size=10
spring.datasource.hikari.minimum-idle=5
spring.datasource.hikari.connection-timeout=30000
spring.datasource.hikari.idle-timeout=600000
spring.datasource.hikari.max-lifetime=1800000
```

### H2 in-memory (dev/test)

```properties
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driver-class-name=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=

# Enable H2 web console
spring.h2.console.enabled=true
spring.h2.console.path=/h2-console
```

### MySQL

```properties
spring.datasource.url=jdbc:mysql://localhost:3306/myapp?serverTimezone=UTC&useSSL=false
spring.datasource.username=root
spring.datasource.password=secret
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver
```

### Custom DataSource bean

```java
@Bean
@ConfigurationProperties("app.datasource")
public HikariDataSource dataSource() {
    return DataSourceBuilder.create().type(HikariDataSource.class).build();
}
```

### Two DataSources

```java
@Primary
@Bean("primaryDataSource")
@ConfigurationProperties("app.datasource.primary")
public DataSource primaryDataSource() {
    return DataSourceBuilder.create().build();
}

@Bean("secondaryDataSource")
@ConfigurationProperties("app.datasource.secondary")
public DataSource secondaryDataSource() {
    return DataSourceBuilder.create().build();
}
```

---

## Spring Data JPA

### Dependencies

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>
<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <scope>runtime</scope>
</dependency>
```

### JPA Properties

```properties
spring.jpa.hibernate.ddl-auto=validate       # validate|update|create|create-drop|none
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.PostgreSQL10Dialect
spring.jpa.open-in-view=false                # recommended: disable OSIV
spring.jpa.properties.hibernate.jdbc.batch_size=20
spring.jpa.properties.hibernate.order_inserts=true
spring.jpa.properties.hibernate.order_updates=true
```

---

## @Entity

```java
package com.example.domain;

import javax.persistence.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "first_name", nullable = false, length = 100)
    private String firstName;

    @Column(name = "last_name", nullable = false, length = 100)
    private String lastName;

    @Column(unique = true, nullable = false)
    private String email;

    @Enumerated(EnumType.STRING)
    private UserStatus status = UserStatus.ACTIVE;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Version
    private Long version;   // optimistic locking

    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Order> orders = new ArrayList<>();

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "department_id")
    private Department department;

    // required no-arg constructor for JPA
    protected User() {}

    public User(String firstName, String lastName, String email) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.email = email;
    }

    // getters and setters
}

public enum UserStatus { ACTIVE, INACTIVE, BANNED }
```

---

## @Repository / JpaRepository

```java
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    // Derived query methods (auto-implemented from method name)
    Optional<User> findByEmail(String email);
    List<User> findByFirstNameIgnoreCase(String firstName);
    List<User> findByStatusAndDepartmentId(UserStatus status, Long deptId);
    boolean existsByEmail(String email);
    long countByStatus(UserStatus status);
    void deleteByEmail(String email);

    // Sorted
    List<User> findByStatusOrderByLastNameAsc(UserStatus status);

    // Pagination
    Page<User> findByStatus(UserStatus status, Pageable pageable);

    // JPQL
    @Query("SELECT u FROM User u WHERE u.email = :email AND u.status = 'ACTIVE'")
    Optional<User> findActiveByEmail(@Param("email") String email);

    // JPQL with join fetch (avoids N+1)
    @Query("SELECT DISTINCT u FROM User u LEFT JOIN FETCH u.orders WHERE u.id = :id")
    Optional<User> findWithOrders(@Param("id") Long id);

    // Native SQL
    @Query(value = "SELECT * FROM users WHERE LOWER(email) = LOWER(:email)",
           nativeQuery = true)
    Optional<User> findByEmailCaseInsensitive(@Param("email") String email);

    // Modifying queries
    @Modifying
    @Query("UPDATE User u SET u.status = :status WHERE u.id = :id")
    int updateStatus(@Param("id") Long id, @Param("status") UserStatus status);

    // Projections (interface-based)
    List<UserSummary> findByStatus(UserStatus status);  // returns projection
}

// Projection interface
public interface UserSummary {
    Long getId();
    String getFirstName();
    String getLastName();
    String getEmail();
}
```

---

## Query Method Keywords

| Keyword | Example | SQL equivalent |
|---------|---------|----------------|
| `And` | `findByFirstNameAndLastName` | `WHERE first_name=? AND last_name=?` |
| `Or` | `findByFirstNameOrEmail` | `WHERE first_name=? OR email=?` |
| `Between` | `findByAgeBetween(10, 20)` | `WHERE age BETWEEN 10 AND 20` |
| `LessThan` | `findByAgeLessThan(18)` | `WHERE age < 18` |
| `GreaterThan` | `findByAgeGreaterThan(18)` | `WHERE age > 18` |
| `IsNull` | `findByEmailIsNull` | `WHERE email IS NULL` |
| `IsNotNull` | `findByEmailIsNotNull` | `WHERE email IS NOT NULL` |
| `Like` | `findByNameLike("%John%")` | `WHERE name LIKE '%John%'` |
| `StartingWith` | `findByNameStartingWith("Jo")` | `WHERE name LIKE 'Jo%'` |
| `EndingWith` | `findByNameEndingWith("son")` | `WHERE name LIKE '%son'` |
| `Containing` | `findByNameContaining("oh")` | `WHERE name LIKE '%oh%'` |
| `IgnoreCase` | `findByEmailIgnoreCase` | `WHERE UPPER(email)=UPPER(?)` |
| `OrderBy` | `findByStatusOrderByNameAsc` | `ORDER BY name ASC` |
| `Not` | `findByStatusNot(ACTIVE)` | `WHERE status <> 'ACTIVE'` |
| `In` | `findByStatusIn(statuses)` | `WHERE status IN (...)` |
| `True/False` | `findByActiveTrue` | `WHERE active = true` |

---

## Pagination and Sorting

```java
// Create Pageable
Pageable pageable = PageRequest.of(0, 20);  // page 0, size 20

// With sorting
Pageable pageable = PageRequest.of(0, 20,
    Sort.by("lastName").ascending().and(Sort.by("firstName").ascending()));

// Calling repository
Page<User> page = userRepository.findByStatus(UserStatus.ACTIVE, pageable);

// Accessing page metadata
List<User> content = page.getContent();
int totalPages = page.getTotalPages();
long totalElements = page.getTotalElements();
int pageNumber = page.getNumber();
int pageSize = page.getSize();
boolean isFirst = page.isFirst();
boolean isLast = page.isLast();
boolean hasNext = page.hasNext();
```

In controllers (Spring MVC auto-resolves `Pageable` from request params):
```java
@GetMapping
public Page<UserDto> list(Pageable pageable) {
    // client calls: GET /users?page=0&size=20&sort=lastName,asc
    return userRepository.findAll(pageable).map(this::toDto);
}
```

Enable Pageable parameter resolution:
```java
@Configuration
public class MvcConfig implements WebMvcConfigurer {
    @Override
    public void addArgumentResolvers(List<HandlerMethodArgumentResolver> resolvers) {
        resolvers.add(new PageableHandlerMethodArgumentResolver());
    }
}
```

---

## @Transactional

```java
@Service
public class UserService {

    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @Transactional
    public User createUser(String firstName, String lastName, String email) {
        if (userRepository.existsByEmail(email)) {
            throw new DuplicateEmailException(email);
        }
        return userRepository.save(new User(firstName, lastName, email));
    }

    @Transactional(readOnly = true)    // enables read-only optimization
    public Optional<User> findById(Long id) {
        return userRepository.findById(id);
    }

    @Transactional(rollbackFor = Exception.class)   // rollback on checked exceptions too
    public void riskyOperation() throws Exception { }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void auditLog(String event) {
        // runs in its own new transaction, always committed separately
    }

    @Transactional(propagation = Propagation.MANDATORY)
    public void mustBeInTransaction() {
        // throws if no active transaction
    }

    @Transactional(isolation = Isolation.SERIALIZABLE)
    public void highIsolation() { }

    @Transactional(timeout = 10)   // rollback if exceeds 10 seconds
    public void longOperation() { }
}
```

**Key rules:**
- `@Transactional` only works on **public** methods called **from outside the bean** (proxy limitation)
- Self-invocation (calling `this.method()`) does NOT go through the proxy — transaction won't apply
- Default propagation is `REQUIRED` (join existing or create new)
- Default rollback is for `RuntimeException` and `Error` only

---

## JdbcTemplate

```java
@Repository
public class UserJdbcRepository {

    private final JdbcTemplate jdbc;

    public UserJdbcRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public Optional<User> findById(Long id) {
        try {
            User user = jdbc.queryForObject(
                "SELECT * FROM users WHERE id = ?",
                (rs, rowNum) -> new User(
                    rs.getLong("id"),
                    rs.getString("first_name"),
                    rs.getString("last_name"),
                    rs.getString("email")
                ),
                id
            );
            return Optional.ofNullable(user);
        } catch (EmptyResultDataAccessException e) {
            return Optional.empty();
        }
    }

    public List<User> findAll() {
        return jdbc.query(
            "SELECT * FROM users ORDER BY last_name",
            (rs, rowNum) -> new User(
                rs.getLong("id"),
                rs.getString("first_name"),
                rs.getString("last_name"),
                rs.getString("email")
            )
        );
    }

    public int insert(User user) {
        return jdbc.update(
            "INSERT INTO users (first_name, last_name, email) VALUES (?, ?, ?)",
            user.getFirstName(), user.getLastName(), user.getEmail()
        );
    }

    // NamedParameterJdbcTemplate for named params
    @Autowired
    private NamedParameterJdbcTemplate namedJdbc;

    public int updateEmail(Long id, String email) {
        Map<String, Object> params = new HashMap<>();
        params.put("id", id);
        params.put("email", email);
        return namedJdbc.update(
            "UPDATE users SET email = :email WHERE id = :id", params);
    }
}
```

---

## Database Migrations

### Flyway

```xml
<dependency>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-core</artifactId>
</dependency>
```

```properties
spring.flyway.locations=classpath:db/migration
spring.flyway.baseline-on-migrate=true
spring.flyway.validate-on-migrate=true
```

Migration files in `src/main/resources/db/migration/`:
```
V1__create_users_table.sql
V2__add_status_column.sql
V3__create_orders_table.sql
```

```sql
-- V1__create_users_table.sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    version BIGINT NOT NULL DEFAULT 0
);
```

### Liquibase

```xml
<dependency>
    <groupId>org.liquibase</groupId>
    <artifactId>liquibase-core</artifactId>
</dependency>
```

```properties
spring.liquibase.change-log=classpath:db/changelog/db.changelog-master.yaml
```

```yaml
# db/changelog/db.changelog-master.yaml
databaseChangeLog:
  - changeSet:
      id: 1
      author: dev
      changes:
        - createTable:
            tableName: users
            columns:
              - column:
                  name: id
                  type: BIGINT
                  autoIncrement: true
                  constraints:
                    primaryKey: true
              - column:
                  name: email
                  type: VARCHAR(255)
                  constraints:
                    nullable: false
                    unique: true
```

---

## Spring Data REST

Expose JPA repositories as REST endpoints automatically:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-rest</artifactId>
</dependency>
```

```java
// Add @RepositoryRestResource to customize
@RepositoryRestResource(path = "users", collectionResourceRel = "users")
public interface UserRepository extends JpaRepository<User, Long> {

    // Custom search endpoint: /users/search/findByEmail?email=x
    @RestResource(path = "findByEmail")
    Optional<User> findByEmail(@Param("email") String email);
}
```

Configuration:
```properties
spring.data.rest.base-path=/api
spring.data.rest.default-page-size=20
spring.data.rest.max-page-size=100
spring.data.rest.return-body-on-create=true
```

---

## R2DBC (Reactive, new in Spring Boot 2.3 GA)

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-r2dbc</artifactId>
</dependency>
<dependency>
    <groupId>io.r2dbc</groupId>
    <artifactId>r2dbc-postgresql</artifactId>
    <scope>runtime</scope>
</dependency>
```

```properties
spring.r2dbc.url=r2dbc:postgresql://localhost:5432/myapp
spring.r2dbc.username=postgres
spring.r2dbc.password=secret
```

```java
// Entity (uses Spring Data annotations, NOT javax.persistence)
import org.springframework.data.annotation.Id;
import org.springframework.data.relational.core.mapping.Table;

@Table("users")
public class User {
    @Id
    private Long id;
    private String firstName;
    private String lastName;
    private String email;
    // constructors, getters, setters
}

// Reactive repository
public interface UserRepository extends ReactiveCrudRepository<User, Long> {
    Mono<User> findByEmail(String email);
    Flux<User> findByStatus(String status);
}

// Service using reactive types
@Service
public class UserService {
    private final UserRepository repo;

    public UserService(UserRepository repo) { this.repo = repo; }

    public Flux<User> findAll() { return repo.findAll(); }
    public Mono<User> findById(Long id) { return repo.findById(id); }

    public Mono<User> create(User user) {
        return repo.findByEmail(user.getEmail())
            .flatMap(existing -> Mono.<User>error(
                new DuplicateEmailException(user.getEmail())))
            .switchIfEmpty(repo.save(user));
    }
}

// R2DBC WebFlux controller
@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;

    @GetMapping
    public Flux<User> getAll() { return userService.findAll(); }

    @GetMapping("/{id}")
    public Mono<ResponseEntity<User>> getById(@PathVariable Long id) {
        return userService.findById(id)
            .map(ResponseEntity::ok)
            .defaultIfEmpty(ResponseEntity.notFound().build());
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Mono<User> create(@RequestBody User user) {
        return userService.create(user);
    }
}
```
