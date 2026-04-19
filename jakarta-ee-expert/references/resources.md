# Data and Resources
*Chapters 27–30 — Hibernate as ORM, Connectors, Caching, NoSQL*

## Chapter 27: Hibernate as JPA Provider

Hibernate is the reference implementation of Jakarta Persistence (JPA) 3.1. WildFly bundles it; other servers may use EclipseLink.

### Dependencies (standalone, not EE server)
```xml
<dependency>
  <groupId>org.hibernate.orm</groupId>
  <artifactId>hibernate-core</artifactId>
  <version>6.4.4.Final</version>
</dependency>
<dependency>
  <groupId>jakarta.persistence</groupId>
  <artifactId>jakarta.persistence-api</artifactId>
  <version>3.1.0</version>
  <scope>provided</scope>
</dependency>
```

### JPA Entity
```java
import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name="users")
public class User {
    @Id @GeneratedValue(strategy=GenerationType.IDENTITY)
    private Long id;

    @Column(name="full_name", nullable=false, length=100)
    private String name;

    @Column(unique=true, nullable=false)
    private String email;

    @Enumerated(EnumType.STRING)
    private UserStatus status;

    @ManyToOne(fetch=FetchType.LAZY)
    @JoinColumn(name="department_id")
    private Department department;

    @OneToMany(mappedBy="user", cascade=CascadeType.ALL, orphanRemoval=true)
    private List<Order> orders = new ArrayList<>();

    @ElementCollection
    @CollectionTable(name="user_roles", joinColumns=@JoinColumn(name="user_id"))
    @Column(name="role")
    private Set<String> roles = new HashSet<>();

    @CreationTimestamp
    private LocalDateTime createdAt;

    @Version
    private int version;  // optimistic locking
}
```

### persistence.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<persistence xmlns="https://jakarta.ee/xml/ns/persistence" version="3.1">
  <persistence-unit name="myPU" transaction-type="JTA">
    <jta-data-source>java:comp/DefaultDataSource</jta-data-source>
    <properties>
      <!-- Hibernate -->
      <property name="hibernate.dialect"
                value="org.hibernate.dialect.PostgreSQLDialect"/>
      <property name="hibernate.hbm2ddl.auto" value="validate"/>
      <!-- validate | update | create | create-drop -->
      <property name="hibernate.show_sql" value="false"/>
      <property name="hibernate.format_sql" value="true"/>
      <!-- Second-level cache -->
      <property name="hibernate.cache.use_second_level_cache" value="true"/>
      <property name="hibernate.cache.region.factory_class"
                value="org.hibernate.cache.jcache.JCacheRegionFactory"/>
    </properties>
  </persistence-unit>
</persistence>
```

### Jakarta Data Repository (JPA 3.1 / Jakarta EE 11 preview)
```java
// Jakarta Data (new in EE 11, available via Hibernate 6.x)
@Repository
public interface UserRepository extends CrudRepository<User, Long> {
    List<User> findByStatus(UserStatus status);
    Optional<User> findByEmail(String email);
    @Query("SELECT u FROM User u WHERE u.department.name = :dept")
    List<User> findByDepartment(@Param("dept") String departmentName);
}
```

### EntityManager Usage (CDI-injected, JTA-managed)
```java
@Stateless  // or @ApplicationScoped with @Transactional
public class UserRepository {

    @PersistenceContext
    private EntityManager em;

    public User findById(Long id) {
        return em.find(User.class, id);
    }

    public List<User> findByStatus(UserStatus status) {
        return em.createQuery(
            "SELECT u FROM User u WHERE u.status = :status", User.class)
            .setParameter("status", status)
            .getResultList();
    }

    public User save(User user) {
        if (user.getId() == null) {
            em.persist(user);
            return user;
        }
        return em.merge(user);
    }

    public void delete(Long id) {
        User user = em.find(User.class, id);
        if (user != null) em.remove(user);
    }
}
```

### JPQL and Criteria API
```java
// JPQL
List<User> activeUsers = em.createQuery(
    "SELECT u FROM User u WHERE u.status = 'ACTIVE' " +
    "ORDER BY u.name", User.class)
    .setMaxResults(100)
    .getResultList();

// Named query
@NamedQuery(name="User.findByEmail",
            query="SELECT u FROM User u WHERE u.email = :email")
// Usage:
em.createNamedQuery("User.findByEmail", User.class)
  .setParameter("email", "alice@example.com")
  .getSingleResult();

// Criteria API (type-safe)
CriteriaBuilder cb = em.getCriteriaBuilder();
CriteriaQuery<User> cq = cb.createQuery(User.class);
Root<User> root = cq.from(User.class);
cq.select(root)
  .where(cb.equal(root.get("status"), UserStatus.ACTIVE))
  .orderBy(cb.asc(root.get("name")));
List<User> users = em.createQuery(cq).getResultList();
```

### Hibernate-Specific Extensions
```java
// Native SQL
List<Object[]> rows = em.createNativeQuery(
    "SELECT id, name FROM users WHERE dept_id = ?")
    .setParameter(1, deptId)
    .getResultList();

// Hibernate Session for advanced operations
Session session = em.unwrap(Session.class);
session.enableFetchProfile("with-department");

// Batch processing
session.setJdbcBatchSize(50);
for (User u : users) {
    session.persist(u);
    if (i % 50 == 0) { session.flush(); session.clear(); }
}
```

### DataSource Configuration (WildFly)
```bash
./bin/jboss-cli.sh --connect
module add --name=org.postgresql \
  --resources=/path/to/postgresql-42.7.0.jar \
  --dependencies=jakarta.transaction.api

/subsystem=datasources/jdbc-driver=postgresql:add(
  driver-name=postgresql,
  driver-module-name=org.postgresql,
  driver-class-name=org.postgresql.Driver)

data-source add --name=MyDS \
  --driver-name=postgresql \
  --jndi-name=java:jboss/datasources/MyDS \
  --connection-url=jdbc:postgresql://localhost/mydb \
  --user-name=app --password=secret \
  --min-pool-size=5 --max-pool-size=30
```

---

## Chapter 28: Connectors (Jakarta Connectors 2.1)

Jakarta Connectors (formerly JCA) provides a standard way to integrate enterprise information systems (EIS): legacy databases, ERP systems, messaging systems, etc.

### Resource Adapter Architecture
```
Jakarta EE App
     │  @Resource injection
     ▼
Connection Factory (JNDI lookup)
     │
Resource Adapter (.rar file)
     │
Enterprise Information System (SAP, mainframe, legacy DB, etc.)
```

### Using a Resource Adapter
```java
@Resource(lookup="java:jboss/eis/SapConnection")
private ConnectionFactory sapConnectionFactory;

public void callSap() throws ResourceException {
    try (Connection conn = sapConnectionFactory.getConnection()) {
        Interaction interaction = conn.createInteraction();
        InteractionSpec spec = new SapInteractionSpec();
        // Execute EIS operation
        Record output = interaction.execute(spec, inputRecord);
    }
}
```

### Deploying a Resource Adapter (.rar)
```bash
# Copy to deployments
cp myconnector.rar standalone/deployments/

# Or via CLI
deploy /path/to/myconnector.rar
```

Configure connection pool in `standalone.xml` or via CLI:
```bash
/subsystem=resource-adapters/resource-adapter=myconnector.rar:add(archive=myconnector.rar, transaction-support=XATransaction)
/subsystem=resource-adapters/resource-adapter=myconnector.rar/connection-definitions=myCF:add(
  class-name=com.example.ManagedConnectionFactory,
  jndi-name=java:jboss/eis/MyCF,
  max-pool-size=10)
```

---

## Chapter 29: Caching

### JCache (JSR-107) with Infinispan

**Dependency:**
```xml
<dependency>
  <groupId>javax.cache</groupId>
  <artifactId>cache-api</artifactId>
  <version>1.1.1</version>
</dependency>
<!-- Infinispan as JCache provider -->
<dependency>
  <groupId>org.infinispan</groupId>
  <artifactId>infinispan-jcache</artifactId>
  <version>15.0.0.Final</version>
</dependency>
```

**Programmatic caching:**
```java
@ApplicationScoped
public class UserCacheService {

    private Cache<Long, User> userCache;

    @PostConstruct
    public void init() {
        CachingProvider provider = Caching.getCachingProvider();
        CacheManager manager = provider.getCacheManager();
        MutableConfiguration<Long, User> config =
            new MutableConfiguration<Long, User>()
                .setTypes(Long.class, User.class)
                .setExpiryPolicyFactory(
                    CreatedExpiryPolicy.factoryOf(new Duration(TimeUnit.MINUTES, 30)))
                .setStatisticsEnabled(true);
        userCache = manager.createCache("users", config);
    }

    public User getUser(Long id) {
        User user = userCache.get(id);
        if (user == null) {
            user = userRepository.findById(id);
            if (user != null) userCache.put(id, user);
        }
        return user;
    }

    public void evict(Long id) {
        userCache.remove(id);
    }
}
```

### JPA Second-Level Cache (Hibernate + Infinispan)
```java
@Entity
@Cache(usage=CacheConcurrencyStrategy.READ_WRITE)  // Hibernate cache annotation
public class Product {
    @Id Long id;
    String name;
    // rarely changes — good cache candidate
}
```

```xml
<!-- persistence.xml -->
<property name="hibernate.cache.use_second_level_cache" value="true"/>
<property name="hibernate.cache.use_query_cache" value="true"/>
<property name="hibernate.cache.region.factory_class"
          value="org.hibernate.cache.jcache.JCacheRegionFactory"/>
```

### CDI Cache Interceptor (custom)
```java
@Retention(RetentionPolicy.RUNTIME) @Target(ElementType.METHOD)
@InterceptorBinding
public @interface Cached { String cacheName(); long ttlSeconds() default 300; }

@Cached @Interceptor @Priority(Interceptor.Priority.APPLICATION)
public class CacheInterceptor {
    @AroundInvoke
    public Object cache(InvocationContext ctx) throws Exception {
        String key = ctx.getMethod().getName() + Arrays.toString(ctx.getParameters());
        Object cached = cacheService.get(key);
        if (cached != null) return cached;
        Object result = ctx.proceed();
        cacheService.put(key, result, /* ttl from annotation */);
        return result;
    }
}
```

---

## Chapter 30: NoSQL

### Jakarta NoSQL (Eclipse JNoSQL)
Jakarta NoSQL provides a standard API for NoSQL databases: document, column, key-value, and graph stores.

**Dependency (JNoSQL):**
```xml
<dependency>
  <groupId>org.eclipse.jnosql.mapping</groupId>
  <artifactId>jnosql-mapping-document</artifactId>
  <version>1.0.2</version>
</dependency>
<!-- Database driver, e.g., MongoDB -->
<dependency>
  <groupId>org.eclipse.jnosql.databases</groupId>
  <artifactId>jnosql-database-mongodb</artifactId>
  <version>1.0.2</version>
</dependency>
```

**Document Entity:**
```java
import org.eclipse.jnosql.mapping.Document;

@Entity
@Document("products")    // collection name
public class Product {

    @Id
    private String id;

    @Column
    private String name;

    @Column
    private BigDecimal price;

    @Column
    private List<String> tags;
}
```

**DocumentTemplate (CRUD):**
```java
@Inject DocumentTemplate template;

// Insert
template.insert(product);

// Find by ID
Optional<Product> p = template.find(Product.class, productId);

// Query
List<Product> cheap = template.select(Product.class)
    .where("price").lt(new BigDecimal("50"))
    .result();

// Delete
template.delete(Product.class, productId);
```

### Direct MongoDB Driver
For more control, use the MongoDB Java driver:
```xml
<dependency>
  <groupId>org.mongodb</groupId>
  <artifactId>mongodb-driver-sync</artifactId>
  <version>4.11.1</version>
</dependency>
```

```java
@ApplicationScoped
public class MongoClientProducer {
    @Produces @ApplicationScoped
    public MongoClient produceClient() {
        return MongoClients.create(
            MongoClientSettings.builder()
                .applyConnectionString(
                    new ConnectionString("mongodb://localhost:27017"))
                .build());
    }
}

// Usage
@Inject MongoClient client;

MongoDatabase db = client.getDatabase("myapp");
MongoCollection<Document> col = db.getCollection("products");

col.insertOne(new Document("name", "Widget").append("price", 9.99));
FindIterable<Document> docs = col.find(Filters.lt("price", 20));
```

### Redis (key-value)
```xml
<dependency>
  <groupId>io.lettuce</groupId>
  <artifactId>lettuce-core</artifactId>
  <version>6.3.2.RELEASE</version>
</dependency>
```

```java
@ApplicationScoped
public class RedisService {
    @Produces @ApplicationScoped
    public RedisClient produceClient() {
        return RedisClient.create("redis://localhost:6379");
    }

    @Inject RedisClient client;

    public void set(String key, String value, long ttlSeconds) {
        try (StatefulRedisConnection<String,String> conn = client.connect()) {
            conn.sync().setex(key, ttlSeconds, value);
        }
    }

    public String get(String key) {
        try (StatefulRedisConnection<String,String> conn = client.connect()) {
            return conn.sync().get(key);
        }
    }
}
```

---

## Common Data/Resource Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| `LazyInitializationException` | Accessing lazy collection outside persistence context | Use `JOIN FETCH`, `@Transactional` service layer, or `FetchType.EAGER` |
| N+1 query problem | Loading collection per row | Use `JOIN FETCH` in JPQL or `@BatchSize` |
| Optimistic locking failure | Concurrent updates | Catch `OptimisticLockException`, retry |
| DataSource not found | Wrong JNDI name | Check `jndi-name` in WildFly config matches `@PersistenceUnit` or `@Resource` |
| JCA connector not deployed | `.rar` not in deployments | Check server log for deployment errors |
| JCache provider not found | No JCache implementation on classpath | Add Infinispan or Ehcache dependency |
| MongoDB `_id` field mismatch | `@Id` field not `String` or `ObjectId` | Use `String` for `_id`; MongoDB auto-generates |
