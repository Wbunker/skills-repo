# XML Mapping, Packaging, Deployment, and Testing
*Chapters 13–15 — Pro JPA 2 in Java EE 8, Mike Keith*

## XML Mapping Files — orm.xml (Ch 13)

`orm.xml` provides an alternative (or supplement) to annotations. It lives in the persistence unit's classpath root (typically `META-INF/orm.xml`) and is automatically detected. Multiple mapping files are supported.

### Purpose
- Override annotations without touching source code
- Provide mappings for classes you cannot annotate (third-party jars)
- Separate mapping concerns from domain classes
- Define default listeners, access type, and catalog/schema globally

### orm.xml Structure
```xml
<?xml version="1.0" encoding="UTF-8"?>
<entity-mappings
    xmlns="http://xmlns.jcp.org/xml/ns/persistence/orm"
    version="2.2">

  <!-- Global defaults for all entities in this file -->
  <persistence-unit-metadata>
    <persistence-unit-defaults>
      <schema>hr</schema>
      <catalog>main</catalog>
      <access>FIELD</access>
      <cascade-persist/>    <!-- auto-cascade persist on all relationships -->
      <entity-listeners>
        <entity-listener class="com.example.AuditListener"/>
      </entity-listeners>
    </persistence-unit-defaults>
  </persistence-unit-metadata>

  <package>com.example</package>  <!-- default package; use short class names below -->

  <entity class="Employee" access="FIELD" metadata-complete="false">
    <table name="emp"/>
    <attributes>
      <id name="id">
        <generated-value strategy="SEQUENCE" generator="emp_seq"/>
        <sequence-generator name="emp_seq" sequence-name="emp_id_seq"
                            allocation-size="50"/>
      </id>
      <basic name="firstName">
        <column name="first_name" nullable="false" length="50"/>
      </basic>
      <many-to-one name="department" fetch="LAZY">
        <join-column name="dept_id"/>
      </many-to-one>
      <one-to-many name="projects" mapped-by="lead" fetch="LAZY">
        <cascade><cascade-all/></cascade>
      </one-to-many>
    </attributes>
  </entity>

</entity-mappings>
```

### metadata-complete="true"
When set on an entity, **all annotations on that class are ignored** — only the XML mapping applies. When set on `<persistence-unit-defaults>`, it applies globally.

```xml
<entity class="Employee" metadata-complete="true">
  <!-- all mapping comes from XML only; @Column etc. on class are ignored -->
</entity>
```

### Overriding Annotations with XML
XML always takes precedence over annotations for the same element. Use this to remap column names, change fetch types, or adjust cascade settings in a deployment-specific file.

```xml
<!-- Change fetch type for a specific deployment -->
<many-to-one name="department" fetch="EAGER">
  <join-column name="dept_id"/>
</many-to-one>
```

### Including Additional Mapping Files in persistence.xml
```xml
<persistence-unit name="myPU">
  <mapping-file>META-INF/orm.xml</mapping-file>
  <mapping-file>META-INF/audit-mappings.xml</mapping-file>
</persistence-unit>
```

---

## persistence.xml Deep Dive (Ch 14)

### Full persistence.xml for Java EE (JTA)
```xml
<persistence xmlns="http://xmlns.jcp.org/xml/ns/persistence" version="2.2">
  <persistence-unit name="myPU" transaction-type="JTA">

    <!-- JTA datasource (JNDI name) -->
    <jta-data-source>java:app/jdbc/MyDS</jta-data-source>

    <!-- Optional: non-JTA datasource for queries outside transaction -->
    <non-jta-data-source>java:app/jdbc/MyDS_NoTx</non-jta-data-source>

    <!-- Explicit class list — required when jar scanning is disabled -->
    <class>com.example.Employee</class>
    <class>com.example.Department</class>

    <!-- Include classes from other JARs in the same EAR -->
    <jar-file>../lib/domain-model.jar</jar-file>

    <!-- true = only listed classes; false = scan for @Entity in classpath -->
    <exclude-unlisted-classes>false</exclude-unlisted-classes>

    <!-- L2 cache mode -->
    <shared-cache-mode>ENABLE_SELECTIVE</shared-cache-mode>

    <!-- Validation mode: AUTO, CALLBACK, NONE -->
    <validation-mode>AUTO</validation-mode>

    <properties>
      <!-- Schema generation: none | create | drop-and-create | drop -->
      <property name="javax.persistence.schema-generation.database.action" value="none"/>

      <!-- Provider-specific: Hibernate -->
      <property name="hibernate.show_sql"                value="false"/>
      <property name="hibernate.format_sql"              value="false"/>
      <property name="hibernate.dialect"
                value="org.hibernate.dialect.PostgreSQL10Dialect"/>
      <property name="hibernate.jdbc.batch_size"         value="50"/>
      <property name="hibernate.order_inserts"           value="true"/>
      <property name="hibernate.order_updates"           value="true"/>
      <property name="hibernate.cache.use_second_level_cache"  value="true"/>
      <property name="hibernate.cache.region.factory_class"
                value="org.hibernate.cache.jcache.internal.JCacheRegionFactory"/>
    </properties>

  </persistence-unit>
</persistence>
```

### Java SE (RESOURCE_LOCAL) persistence.xml
```xml
<persistence-unit name="myPU" transaction-type="RESOURCE_LOCAL">
  <provider>org.hibernate.jpa.HibernatePersistenceProvider</provider>

  <class>com.example.Employee</class>
  <exclude-unlisted-classes>true</exclude-unlisted-classes>

  <properties>
    <property name="javax.persistence.jdbc.driver"   value="org.postgresql.Driver"/>
    <property name="javax.persistence.jdbc.url"      value="jdbc:postgresql://localhost/mydb"/>
    <property name="javax.persistence.jdbc.user"     value="appuser"/>
    <property name="javax.persistence.jdbc.password" value="secret"/>
    <property name="javax.persistence.schema-generation.database.action" value="none"/>
  </properties>
</persistence-unit>
```

---

## Packaging and Deployment (Ch 14)

### Persistence Unit Root
JPA looks for `META-INF/persistence.xml` relative to the **persistence unit root** — the archive or directory that contains `META-INF/`:

| Deployment | Persistence Unit Root | persistence.xml location |
|---|---|---|
| `.war` | `WEB-INF/classes/` | `WEB-INF/classes/META-INF/persistence.xml` |
| `.jar` (EJB JAR) | JAR root | `META-INF/persistence.xml` inside JAR |
| `.ear` with separate persistence JAR | persistence JAR root | `META-INF/persistence.xml` inside that JAR |
| Java SE | classpath root | `META-INF/persistence.xml` on classpath |

### EAR Packaging Pattern
```
myapp.ear
├── META-INF/application.xml
├── myapp-web.war
│   └── WEB-INF/classes/...
├── myapp-ejb.jar
│   └── META-INF/persistence.xml  ← persistence unit here
└── lib/
    └── domain-model.jar           ← entity classes (referenced by jar-file element)
```

### Maven Build — persistence.xml placement
```
src/
  main/
    java/               ← entity classes
    resources/
      META-INF/
        persistence.xml   ← copied to WEB-INF/classes/META-INF/ in WAR
```

### Schema Generation (Dev/Test Only)
```xml
<!-- Create schema on startup, drop on shutdown -->
<property name="javax.persistence.schema-generation.database.action" value="drop-and-create"/>

<!-- Create schema from entity annotations -->
<property name="javax.persistence.schema-generation.create-source" value="metadata"/>

<!-- Create schema from SQL script -->
<property name="javax.persistence.schema-generation.create-source" value="script"/>
<property name="javax.persistence.schema-generation.create-script-source"
          value="META-INF/create.sql"/>

<!-- Load initial data -->
<property name="javax.persistence.sql-load-script-source"
          value="META-INF/data.sql"/>
```

### Class Transformers and Weaving
JPA providers use **bytecode enhancement (weaving)** to implement lazy loading and dirty tracking.

**Static weaving** (build-time, Hibernate, EclipseLink):
```xml
<!-- Hibernate Maven plugin -->
<plugin>
  <groupId>org.hibernate.orm.tooling</groupId>
  <artifactId>hibernate-enhance-maven-plugin</artifactId>
  <configuration>
    <enableLazyInitialization>true</enableLazyInitialization>
    <enableDirtyTracking>true</enableDirtyTracking>
  </configuration>
</plugin>
```

**Dynamic weaving** (runtime, via `PersistenceUnitInfo.addTransformer()`):
- In EE containers: done automatically by the server
- In Java SE: requires loading the provider as a Java agent (`-javaagent:hibernate-agent.jar`)

---

## Testing JPA (Ch 15)

### Strategy 1: Java SE EntityManager in Unit Tests
Fastest; no container required. Uses `RESOURCE_LOCAL` persistence unit with an in-memory DB.

```xml
<!-- src/test/resources/META-INF/persistence.xml -->
<persistence-unit name="testPU" transaction-type="RESOURCE_LOCAL">
  <provider>org.hibernate.jpa.HibernatePersistenceProvider</provider>
  <class>com.example.Employee</class>
  <exclude-unlisted-classes>true</exclude-unlisted-classes>
  <properties>
    <property name="javax.persistence.jdbc.driver"   value="org.h2.Driver"/>
    <property name="javax.persistence.jdbc.url"      value="jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1"/>
    <property name="javax.persistence.jdbc.user"     value="sa"/>
    <property name="javax.persistence.jdbc.password" value=""/>
    <property name="javax.persistence.schema-generation.database.action" value="drop-and-create"/>
    <property name="javax.persistence.schema-generation.create-source" value="metadata"/>
    <property name="hibernate.show_sql" value="true"/>
  </properties>
</persistence-unit>
```

```java
class EmployeeRepositoryTest {
    static EntityManagerFactory emf;
    EntityManager em;

    @BeforeAll
    static void setupEMF() {
        emf = Persistence.createEntityManagerFactory("testPU");
    }

    @BeforeEach
    void openEM() {
        em = emf.createEntityManager();
    }

    @AfterEach
    void closeEM() {
        em.close();
    }

    @AfterAll
    static void closeEMF() {
        emf.close();
    }

    @Test
    void testPersistAndFind() {
        em.getTransaction().begin();
        Employee e = new Employee();
        e.setName("Alice");
        em.persist(e);
        em.getTransaction().commit();

        em.clear();   // evict from L1 cache

        Employee found = em.find(Employee.class, e.getId());
        assertNotNull(found);
        assertEquals("Alice", found.getName());
    }
}
```

### Strategy 2: Arquillian (Container Integration Tests)
Tests run inside a real Java EE container (WildFly, Payara, etc.).

```xml
<!-- pom.xml -->
<dependency>
  <groupId>org.jboss.arquillian.junit5</groupId>
  <artifactId>arquillian-junit5-container</artifactId>
  <scope>test</scope>
</dependency>
<dependency>
  <groupId>org.wildfly.arquillian</groupId>
  <artifactId>wildfly-arquillian-container-managed</artifactId>
  <scope>test</scope>
</dependency>
```

```java
@ExtendWith(ArquillianExtension.class)
class EmployeeServiceIT {

    @Deployment
    public static WebArchive createDeployment() {
        return ShrinkWrap.create(WebArchive.class, "test.war")
            .addClasses(Employee.class, EmployeeService.class)
            .addAsWebInfResource(EmptyAsset.INSTANCE, "beans.xml")
            .addAsResource("META-INF/persistence.xml");
    }

    @Inject
    EmployeeService service;

    @Test
    void testFindAll() {
        List<Employee> all = service.findAll();
        assertNotNull(all);
    }
}
```

### Strategy 3: Spring TestContext / CDI Weld SE (Lightweight)
Weld SE lets you run CDI beans (including `@PersistenceContext`-injected EMs) outside a container.

```xml
<dependency>
  <groupId>org.jboss.weld.se</groupId>
  <artifactId>weld-se-core</artifactId>
  <scope>test</scope>
</dependency>
```

### Testing Tips

| Concern | Recommendation |
|---------|---------------|
| Isolation between tests | Begin a transaction in @BeforeEach, rollback in @AfterEach |
| Avoiding false negatives from L1 cache | Call `em.clear()` / `em.flush()` before assertions |
| Testing lazy loading | Keep EM open during assertion, or test within a transaction |
| Schema creation | Use `drop-and-create` for tests; `none` for production |
| Query cache testing | Disable L2 cache in test PU to avoid cross-test pollution |

### Transaction-per-Test Pattern
```java
@BeforeEach
void begin() {
    em.getTransaction().begin();
}

@AfterEach
void rollback() {
    if (em.getTransaction().isActive()) {
        em.getTransaction().rollback();
    }
}
```
Every test runs in a rolled-back transaction — the DB is clean for each test without truncating tables.

### Testing Bulk Operations
Bulk operations bypass the persistence context. Always flush first, then clear after:
```java
@Test
void testBulkUpdate() {
    em.getTransaction().begin();
    // setup
    Employee e = new Employee(); e.setName("Bob"); e.setSalary(BigDecimal.valueOf(40000));
    em.persist(e);
    em.flush();   // ensure record is in DB before bulk op

    int updated = em.createQuery("UPDATE Employee e SET e.salary = e.salary * 1.1")
                    .executeUpdate();
    em.clear();   // re-read to verify

    Employee refreshed = em.find(Employee.class, e.getId());
    assertEquals(0, BigDecimal.valueOf(44000).compareTo(refreshed.getSalary()));
    em.getTransaction().rollback();
}
```
