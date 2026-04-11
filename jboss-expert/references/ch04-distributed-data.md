# Ch 4 — Storing and Accessing Distributed Data

> **Book context:** Covered JBoss Data Grid 7.x and JBoss Data Virtualization. Current equivalents: **Red Hat Data Grid 8.x** (Infinispan 14/15) and **Teiid** (or query federation via Quarkus extensions). JBoss Data Grid is now **Red Hat Data Grid**; the community project is **Infinispan**.

## Infinispan / Red Hat Data Grid Overview

Infinispan is an in-memory distributed data grid embedded in WildFly and available as a standalone server (Red Hat Data Grid 8.x).

```
┌───────────────────────────────────────────────────────┐
│                  DATA GRID TOPOLOGY                   │
│                                                       │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐            │
│  │ Node 1  │   │ Node 2  │   │ Node 3  │            │
│  │         │   │         │   │         │            │
│  │[Cache A]│◄──┤[Cache A]│◄──┤[Cache A]│            │
│  │[Cache B]│   │[Cache B]│   │[Cache B]│            │
│  └────┬────┘   └────┬────┘   └────┬────┘            │
│       │             │             │                  │
│       └─────────────┼─────────────┘                  │
│                     │ JGroups cluster                 │
└─────────────────────┼─────────────────────────────────┘
                      │
                 Client library
                 (Hot Rod / REST / Memcached)
```

## Cache Modes

| Mode | Replication | Performance | Data Safety |
|------|-------------|-------------|-------------|
| **Local** | None — single node | Fastest | Lose data if node fails |
| **Replicated** | Full copy on every node | Read-fast, write-slow | Highest — any node has all data |
| **Distributed** | `numOwners` copies (default 2) | Balanced | Good — configurable redundancy |
| **Scattered** | 2 copies (primary + backup) | High read performance | Similar to distributed |
| **Invalidation** | Invalidate stale entries | Very fast | DB is source of truth |

## Infinispan Embedded in WildFly

WildFly embeds Infinispan for internal caches (HTTP sessions, EJB caches, Hibernate 2nd-level cache).

### Configuration (standalone-ha.xml)

```xml
<subsystem xmlns="urn:jboss:domain:infinispan:14.0">
  <cache-container name="web" default-cache="dist" modules="...">
    <transport lock-timeout="60000"/>
    <distributed-cache name="dist" mode="ASYNC">
      <locking isolation="REPEATABLE_READ"/>
      <transaction mode="BATCH"/>
      <file-store/>
    </distributed-cache>
  </cache-container>

  <!-- Custom application cache container -->
  <cache-container name="myapp" default-cache="products">
    <local-cache name="products">
      <expiration lifespan="300000" max-idle="60000"/>
      <memory max-count="10000"/>
    </local-cache>
  </cache-container>
</subsystem>
```

### Programmatic Access (Embedded)

```java
@Resource(lookup = "java:jboss/infinispan/cache/myapp/products")
private Cache<String, Product> productCache;

// Or via CacheContainer
@Resource(lookup = "java:jboss/infinispan/container/myapp")
private CacheContainer cacheContainer;
Cache<String, Product> cache = cacheContainer.getCache("products");

// Basic operations
cache.put("prod-1", product);
Product p = cache.get("prod-1");
cache.remove("prod-1");

// Conditional operations
cache.putIfAbsent("prod-1", product);
cache.replace("prod-1", oldProduct, newProduct);
```

### JCache (JSR-107) API

```java
@Inject
@CacheResult(cacheName = "products")
public Product findProduct(String id) {
    return db.find(id); // only called on cache miss
}

@CacheInvalidate(cacheName = "products")
public void deleteProduct(String id) {
    db.delete(id);
}

@CachePut(cacheName = "products")
public void saveProduct(@CacheKey String id, @CacheValue Product product) {
    db.save(product);
}
```

## Red Hat Data Grid 8.x (Standalone Server)

Red Hat Data Grid 8.x is the enterprise distribution of Infinispan for standalone deployments.

### Client Configuration (Hot Rod)

```java
// Maven dependency:
// org.infinispan:infinispan-client-hotrod:14.0.x.Final

ConfigurationBuilder builder = new ConfigurationBuilder();
builder.addServer()
    .host("datagrid-server")
    .port(11222)
    .security()
        .authentication().enable()
        .username("user")
        .password("password")
        .realm("default")
        .saslMechanism("SCRAM-SHA-256");

RemoteCacheManager cacheManager = new RemoteCacheManager(builder.build());
RemoteCache<String, Product> cache = cacheManager.getCache("products");

cache.put("prod-1", product);
cache.putAsync("prod-2", product2); // non-blocking
```

### REST API (Data Grid 8.x)

```bash
# Create cache
curl -X POST http://dg-server:11222/rest/v2/caches/products \
  -H "Content-Type: application/json" \
  -d '{"distributed-cache":{"mode":"SYNC","owners":2}}'

# Put entry
curl -X PUT http://dg-server:11222/rest/v2/caches/products/prod-1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Widget","price":9.99}'

# Get entry
curl http://dg-server:11222/rest/v2/caches/products/prod-1
```

## JPA with Hibernate Second-Level Cache

Hibernate's L2 cache integrates with Infinispan:

```xml
<!-- persistence.xml -->
<properties>
  <property name="hibernate.cache.use_second_level_cache" value="true"/>
  <property name="hibernate.cache.use_query_cache" value="true"/>
  <property name="hibernate.cache.region.factory_class"
            value="org.infinispan.hibernate.cache.v62.InfinispanRegionFactory"/>
  <property name="hibernate.cache.infinispan.cfg"
            value="infinispan-config.xml"/>
</properties>
```

```java
@Entity
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
public class Product {
    @Id private Long id;
    // ...

    @OneToMany
    @Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
    private List<Category> categories;
}
```

Cache concurrency strategies:
- `READ_ONLY` — immutable data, best performance
- `READ_WRITE` — updated data with soft locks
- `NONSTRICT_READ_WRITE` — no strict consistency, no locks
- `TRANSACTIONAL` — full JTA transaction support

## JDBC and Connection Pooling

WildFly uses **IronJacamar** as its JCA/JDBC connection pool.

### Adding a JDBC Driver Module

```bash
# 1. Create module directory
mkdir -p $JBOSS_HOME/modules/org/postgresql/main

# 2. Copy driver JAR
cp postgresql-42.7.0.jar $JBOSS_HOME/modules/org/postgresql/main/

# 3. Create module.xml
cat > $JBOSS_HOME/modules/org/postgresql/main/module.xml << EOF
<module name="org.postgresql" xmlns="urn:jboss:module:1.9">
  <resources>
    <resource-root path="postgresql-42.7.0.jar"/>
  </resources>
  <dependencies>
    <module name="javax.api"/>
    <module name="javax.transaction.api"/>
  </dependencies>
</module>
EOF

# 4. Register driver via CLI
/subsystem=datasources/jdbc-driver=postgresql:add(
  driver-name="postgresql",
  driver-module-name="org.postgresql",
  driver-class-name="org.postgresql.Driver",
  driver-xa-datasource-class-name="org.postgresql.xa.PGXADataSource"
)
```

### XA Datasource (Distributed Transactions)

```bash
/subsystem=datasources/xa-data-source=MyXADS:add(
  jndi-name="java:jboss/datasources/MyXADS",
  driver-name="postgresql",
  user-name="user",
  password="pass"
)
/subsystem=datasources/xa-data-source=MyXADS/xa-datasource-properties=ServerName:add(value="localhost")
/subsystem=datasources/xa-data-source=MyXADS/xa-datasource-properties=PortNumber:add(value="5432")
/subsystem=datasources/xa-data-source=MyXADS/xa-datasource-properties=DatabaseName:add(value="mydb")
```

## Data Virtualization (Teiid)

> JBoss Data Virtualization has been largely replaced by **Teiid** (community) or query federation patterns in modern microservices. The concept: federate data from multiple sources (RDBMS, files, web services) into a virtual relational view.

Current approach for new projects: use Teiid standalone or Quarkus Teiid extension for data virtualization needs rather than the deprecated JBoss DV product.

### Teiid VDB (Virtual Database) — concept

```xml
<!-- vdb.xml -->
<vdb name="MyVDB" version="1">
  <model name="PostgresModel">
    <source name="postgres" translator-name="postgresql"
            connection-jndi-name="java:jboss/datasources/PostgresDS"/>
  </model>
  <model name="CSVModel" type="PHYSICAL">
    <source name="files" translator-name="file"
            connection-jndi-name="java:jboss/file"/>
    <metadata type="DDL">
      CREATE FOREIGN TABLE products (id integer, name string)
        OPTIONS(uri 'products.csv', "importer.useFullSchemaName" 'false');
    </metadata>
  </model>
  <model name="FederatedModel" type="VIRTUAL">
    <metadata type="DDL">
      CREATE VIEW unified_products AS
        SELECT p.id, p.name, c.name as category
        FROM PostgresModel.products p
        JOIN CSVModel.products c ON p.id = c.id;
    </metadata>
  </model>
</vdb>
```

## Cache Strategy Decision Tree

```
What type of data are you caching?
├── Read-mostly, rarely changes → READ_ONLY (best performance)
├── Updated infrequently → READ_WRITE with distributed cache
├── Session state / HTTP sessions → Built-in WildFly web cache container
├── Expensive DB queries → Hibernate L2 + query cache
├── Shared across microservices → Remote Data Grid (Hot Rod client)
└── External session store → Remote Data Grid with REST API

How long should data live?
├── Short-lived (seconds/minutes) → Set lifespan + max-idle
├── Until invalidated → No expiry, explicit eviction
└── Persistent across restarts → File store or JDBC store
```
