# JPA and JDBC Basics
*Chapters 11–13 (Zambon) — Jakarta Persistence, JDBC Direct Access, RESTful Web Services*

## Chapter 11: Jakarta Persistence API (JPA) — Beginner Introduction

JPA maps Java objects (entities) to database tables. The server-provided JPA implementation (EclipseLink on GlassFish, Hibernate on WildFly) handles SQL generation.

### persistence.xml

`src/main/resources/META-INF/persistence.xml` — required to define a persistence unit:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<persistence xmlns="https://jakarta.ee/xml/ns/persistence" version="3.1">

  <persistence-unit name="myPU" transaction-type="JTA">
    <!-- Uses server-managed data source (JNDI name) -->
    <jta-data-source>java:app/jdbc/MyDS</jta-data-source>

    <!-- List entity classes OR let the server scan automatically -->
    <class>com.example.User</class>
    <class>com.example.Order</class>

    <properties>
      <!-- Create/update schema automatically (dev only) -->
      <property name="jakarta.persistence.schema-generation.database.action"
                value="create"/>
      <!-- EclipseLink SQL logging -->
      <property name="eclipselink.logging.level" value="FINE"/>
      <!-- Hibernate SQL logging -->
      <property name="hibernate.show_sql" value="true"/>
    </properties>
  </persistence-unit>

</persistence>
```

**transaction-type="JTA"** — use container-managed transactions (standard for Jakarta EE apps). Use `RESOURCE_LOCAL` only for standalone Java SE.

### Defining a Data Source (GlassFish `glassfish-resources.xml`)

Place in `src/main/webapp/WEB-INF/glassfish-resources.xml`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE resources PUBLIC "-//GlassFish.org//DTD GlassFish Application Server 3.1 Resource Definitions//EN"
  "http://glassfish.org/dtd/glassfish-resources_1_5.dtd">
<resources>
  <jdbc-connection-pool name="MyPool"
      datasource-classname="org.h2.jdbcx.JdbcDataSource"
      res-type="javax.sql.DataSource">
    <property name="URL" value="jdbc:h2:mem:mydb;DB_CLOSE_DELAY=-1"/>
    <property name="User" value="sa"/>
    <property name="Password" value=""/>
  </jdbc-connection-pool>
  <jdbc-resource pool-name="MyPool" jndi-name="java:app/jdbc/MyDS"/>
</resources>
```

For H2 in-memory (development), add the dependency:
```xml
<dependency>
  <groupId>com.h2database</groupId>
  <artifactId>h2</artifactId>
  <version>2.2.224</version>
  <scope>runtime</scope>
</dependency>
```

### Entity Class

```java
package com.example;

import jakarta.persistence.*;
import java.time.LocalDate;

@Entity
@Table(name = "users")
@NamedQuery(name = "User.findAll",   query = "SELECT u FROM User u ORDER BY u.name")
@NamedQuery(name = "User.findByEmail", query = "SELECT u FROM User u WHERE u.email = :email")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    private String name;

    @Column(nullable = false, unique = true, length = 200)
    private String email;

    @Column(name = "birth_date")
    private LocalDate birthDate;

    @Enumerated(EnumType.STRING)
    private UserStatus status = UserStatus.ACTIVE;

    // Getters and setters (JPA requires no-arg constructor and getters/setters)
    public User() {}

    public User(String name, String email) {
        this.name  = name;
        this.email = email;
    }

    public Long getId()               { return id; }
    public String getName()           { return name; }
    public void setName(String n)     { this.name = n; }
    public String getEmail()          { return email; }
    public void setEmail(String e)    { this.email = e; }
    public LocalDate getBirthDate()   { return birthDate; }
    public void setBirthDate(LocalDate d) { this.birthDate = d; }
    public UserStatus getStatus()     { return status; }
    public void setStatus(UserStatus s) { this.status = s; }
}
```

### Repository (DAO) Pattern

```java
package com.example;

import jakarta.ejb.Stateless;
import jakarta.inject.Inject;
import jakarta.persistence.*;
import java.util.List;
import java.util.Optional;

@Stateless    // gives automatic @Transactional behaviour; or use @ApplicationScoped + @Transactional
public class UserRepository {

    @PersistenceContext(unitName = "myPU")
    private EntityManager em;

    public User save(User user) {
        if (user.getId() == null) {
            em.persist(user);
            return user;
        } else {
            return em.merge(user);
        }
    }

    public Optional<User> findById(Long id) {
        return Optional.ofNullable(em.find(User.class, id));
    }

    public List<User> findAll() {
        return em.createNamedQuery("User.findAll", User.class)
                 .getResultList();
    }

    public Optional<User> findByEmail(String email) {
        try {
            return Optional.of(
                em.createNamedQuery("User.findByEmail", User.class)
                  .setParameter("email", email)
                  .getSingleResult());
        } catch (NoResultException e) {
            return Optional.empty();
        }
    }

    public void delete(Long id) {
        User user = em.find(User.class, id);
        if (user != null) em.remove(user);
    }
}
```

### JPQL Quick Reference

```java
// Simple select
em.createQuery("SELECT u FROM User u", User.class).getResultList();

// WHERE clause with named parameter
em.createQuery("SELECT u FROM User u WHERE u.status = :status", User.class)
  .setParameter("status", UserStatus.ACTIVE)
  .getResultList();

// ORDER BY, LIMIT
em.createQuery("SELECT u FROM User u ORDER BY u.name ASC", User.class)
  .setMaxResults(10)
  .setFirstResult(0)   // offset for pagination
  .getResultList();

// COUNT
Long count = em.createQuery("SELECT COUNT(u) FROM User u", Long.class)
               .getSingleResult();

// JOIN (fetch related entity)
em.createQuery(
    "SELECT o FROM Order o JOIN FETCH o.user WHERE o.user.id = :userId",
    Order.class)
  .setParameter("userId", userId)
  .getResultList();

// UPDATE (bulk)
em.createQuery("UPDATE User u SET u.status = :s WHERE u.lastLogin < :date")
  .setParameter("s", UserStatus.INACTIVE)
  .setParameter("date", LocalDate.now().minusYears(1))
  .executeUpdate();

// DELETE (bulk)
em.createQuery("DELETE FROM User u WHERE u.status = :s")
  .setParameter("s", UserStatus.DELETED)
  .executeUpdate();
```

### Relationships

```java
// One-to-Many (User has many Orders)
@OneToMany(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true)
private List<Order> orders = new ArrayList<>();

// Many-to-One (Order belongs to User)
@ManyToOne(fetch = FetchType.LAZY)
@JoinColumn(name = "user_id", nullable = false)
private User user;

// Many-to-Many
@ManyToMany
@JoinTable(name = "user_roles",
    joinColumns        = @JoinColumn(name = "user_id"),
    inverseJoinColumns = @JoinColumn(name = "role_id"))
private Set<Role> roles = new HashSet<>();
```

**FetchType:**
- `LAZY` (default for collections) — load on access; prevents N+1 by deferring
- `EAGER` (default for `@ManyToOne`/`@OneToOne`) — load immediately with parent

---

## Chapter 12: JDBC Direct Access

JDBC is the lower-level alternative to JPA — useful when you need exact SQL control, stored procedures, or bulk operations that JPA handles poorly.

### DataSource Injection (Jakarta EE)

```java
import jakarta.annotation.Resource;
import javax.sql.DataSource;

@Stateless
public class ReportRepository {

    @Resource(lookup = "java:app/jdbc/MyDS")
    private DataSource dataSource;

    public List<SalesReport> getMonthlySales(int year) {
        String sql = """
            SELECT month, SUM(amount) as total
            FROM orders
            WHERE YEAR(order_date) = ?
            GROUP BY month
            ORDER BY month
            """;

        List<SalesReport> results = new ArrayList<>();
        try (Connection conn = dataSource.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {

            ps.setInt(1, year);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    results.add(new SalesReport(
                        rs.getInt("month"),
                        rs.getBigDecimal("total")
                    ));
                }
            }
        } catch (SQLException e) {
            throw new RuntimeException("Failed to fetch sales report", e);
        }
        return results;
    }
}
```

### JDBC CRUD Pattern

```java
// INSERT
public long insertUser(String name, String email) throws SQLException {
    String sql = "INSERT INTO users (name, email) VALUES (?, ?)";
    try (Connection conn = dataSource.getConnection();
         PreparedStatement ps = conn.prepareStatement(sql,
             Statement.RETURN_GENERATED_KEYS)) {

        ps.setString(1, name);
        ps.setString(2, email);
        ps.executeUpdate();

        try (ResultSet keys = ps.getGeneratedKeys()) {
            if (keys.next()) return keys.getLong(1);
        }
    }
    throw new RuntimeException("Insert failed — no generated key");
}

// UPDATE
public int updateEmail(long id, String newEmail) throws SQLException {
    String sql = "UPDATE users SET email = ? WHERE id = ?";
    try (Connection conn = dataSource.getConnection();
         PreparedStatement ps = conn.prepareStatement(sql)) {
        ps.setString(1, newEmail);
        ps.setLong(2, id);
        return ps.executeUpdate();   // rows affected
    }
}

// DELETE
public int deleteUser(long id) throws SQLException {
    try (Connection conn = dataSource.getConnection();
         PreparedStatement ps = conn.prepareStatement(
             "DELETE FROM users WHERE id = ?")) {
        ps.setLong(1, id);
        return ps.executeUpdate();
    }
}
```

### When to Use JPA vs. JDBC

| Scenario | Use |
|----------|-----|
| Standard CRUD on mapped entities | JPA |
| Complex reporting / aggregations | JDBC (or JPA native query) |
| Bulk insert/update of thousands of rows | JDBC (JPA has overhead) |
| Stored procedure calls | JDBC |
| Full control over SQL | JDBC |
| Graph of related objects | JPA (with JOIN FETCH) |
| Schema-first development | Either; JDBC if schema is not ORM-friendly |

### JDBC + JPA Together

Use `@PersistenceContext EntityManager` for entity operations and `@Resource DataSource` for raw queries — they can coexist in the same EJB/CDI bean as long as both use the same JTA transaction.

```java
@Stateless
public class HybridRepository {
    @PersistenceContext(unitName = "myPU") private EntityManager em;
    @Resource(lookup = "java:app/jdbc/MyDS")  private DataSource ds;

    public void importBatch(List<UserDto> batch) throws SQLException {
        // Raw JDBC for speed
        String sql = "INSERT INTO users (name,email) VALUES (?,?) ON CONFLICT DO NOTHING";
        try (Connection c = ds.getConnection();
             PreparedStatement ps = c.prepareStatement(sql)) {
            for (UserDto u : batch) {
                ps.setString(1, u.name());
                ps.setString(2, u.email());
                ps.addBatch();
            }
            ps.executeBatch();
        }
    }

    public List<User> findActive() {
        // JPA for mapped entities
        return em.createQuery("SELECT u FROM User u WHERE u.status = 'ACTIVE'", User.class)
                 .getResultList();
    }
}
```

---

## Chapter 13: RESTful Web Services (JAX-RS Basics)

Jakarta REST (formerly JAX-RS) builds HTTP APIs with annotations. It complements Faces for mobile/SPA clients.

### Application Class

```java
import jakarta.ws.rs.ApplicationPath;
import jakarta.ws.rs.core.Application;

@ApplicationPath("/api")   // all REST resources at /myapp/api/*
public class RestApplication extends Application {}
```

### Simple REST Resource

```java
package com.example.rest;

import jakarta.inject.Inject;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.*;
import java.net.URI;
import java.util.List;

@Path("/users")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class UserResource {

    @Inject private UserRepository userRepo;

    @GET
    public List<User> getAll() {
        return userRepo.findAll();
    }

    @GET
    @Path("{id}")
    public Response getById(@PathParam("id") Long id) {
        return userRepo.findById(id)
            .map(u -> Response.ok(u).build())
            .orElse(Response.status(Response.Status.NOT_FOUND).build());
    }

    @POST
    public Response create(User user, @Context UriInfo uriInfo) {
        User saved = userRepo.save(user);
        URI location = uriInfo.getAbsolutePathBuilder()
            .path(String.valueOf(saved.getId())).build();
        return Response.created(location).entity(saved).build();
    }

    @PUT
    @Path("{id}")
    public Response update(@PathParam("id") Long id, User user) {
        return userRepo.findById(id)
            .map(existing -> {
                existing.setName(user.getName());
                existing.setEmail(user.getEmail());
                return Response.ok(userRepo.save(existing)).build();
            })
            .orElse(Response.status(Response.Status.NOT_FOUND).build());
    }

    @DELETE
    @Path("{id}")
    public Response delete(@PathParam("id") Long id) {
        userRepo.delete(id);
        return Response.noContent().build();
    }

    // Query parameter example: GET /api/users?status=ACTIVE
    @GET
    @Path("search")
    public List<User> search(@QueryParam("status") String status,
                              @QueryParam("limit") @DefaultValue("20") int limit) {
        return userRepo.findByStatus(status, limit);
    }
}
```

### JSON Binding (JSON-B)

JSON-B automatically serializes/deserializes Java objects to/from JSON:

```java
import jakarta.json.bind.annotation.*;

public class UserDto {
    @JsonbProperty("user_name")      // custom JSON key
    public String name;

    @JsonbTransient                  // exclude from JSON
    public String passwordHash;

    @JsonbDateFormat("yyyy-MM-dd")
    public LocalDate birthDate;

    @JsonbNillable                   // include null as JSON null
    public String nickname;
}
```

### Exception Mapping

```java
@Provider
public class NotFoundExceptionMapper
        implements ExceptionMapper<EntityNotFoundException> {

    @Override
    public Response toResponse(EntityNotFoundException ex) {
        return Response.status(Response.Status.NOT_FOUND)
            .entity(Map.of("error", ex.getMessage()))
            .type(MediaType.APPLICATION_JSON)
            .build();
    }
}
```

### Annotation Quick Reference

| Annotation | Purpose |
|-----------|---------|
| `@Path("/path")` | Maps class or method to a URL path |
| `@GET`, `@POST`, `@PUT`, `@DELETE`, `@PATCH` | HTTP method binding |
| `@Produces(MediaType.APPLICATION_JSON)` | Response content type |
| `@Consumes(MediaType.APPLICATION_JSON)` | Request body content type |
| `@PathParam("id")` | Extracts `{id}` from the URL |
| `@QueryParam("q")` | Extracts `?q=` from URL |
| `@DefaultValue("10")` | Default if param absent |
| `@FormParam("name")` | Extracts form field |
| `@HeaderParam("X-Token")` | Extracts request header |
| `@BeanParam` | Groups multiple params into a POJO |
| `@Context UriInfo` | Injects URI/request context |
| `@Provider` | Registers a JAX-RS extension (filter, mapper) |

---

## Common JPA/JDBC/REST Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| `TransactionRequiredException` | No transaction on `em.persist()` | Use `@Stateless` or `@Transactional` |
| `LazyInitializationException` | Accessing lazy collection outside transaction | Use `JOIN FETCH` in query or open session in view (avoid) |
| Entity not updated | `em.merge()` not called | Merge detached entity, or keep entity in managed state |
| Duplicate key on persist | `em.persist()` on already-managed entity | Use `em.merge()` for updates |
| `NoResultException` | `getSingleResult()` with no row | Use `getResultList()` and check `isEmpty()` |
| JDBC connection leak | Not using try-with-resources | Always `try (Connection c = ds.getConnection()) {}` |
| REST returns 415 | Missing `@Consumes` or wrong Content-Type | Ensure client sends `Content-Type: application/json` |
| REST returns 500 | JSON-B cannot serialize | Check for cycles, missing no-arg constructor |
| REST 404 on everything | `@ApplicationPath` conflict | Ensure only one `Application` subclass; check app context path |
