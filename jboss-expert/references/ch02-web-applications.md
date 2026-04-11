# Ch 2 — Developing and Hosting Scalable Web Applications

## Application Packaging

| Archive | Contents | Use Case |
|---------|----------|----------|
| WAR | Servlets, JSF, web resources | Web application |
| JAR | EJBs, CDI beans, utility classes | Business logic module |
| EAR | WAR + JAR + descriptor | Full enterprise app |
| Bootable JAR | WildFly + WAR embedded | Cloud-native single artifact |

### WAR Structure
```
myapp.war/
  WEB-INF/
    web.xml              ← Servlet descriptor (optional with annotations)
    jboss-web.xml        ← WildFly-specific (context root, security domain)
    beans.xml            ← CDI activation (empty file or with bean-discovery-mode)
    classes/             ← Compiled classes
    lib/                 ← Dependency JARs
  META-INF/
    MANIFEST.MF          ← Module dependencies
  index.html, *.xhtml    ← Web resources
```

### EAR Structure
```
myapp.ear/
  META-INF/
    application.xml      ← Module declarations
    jboss-app.xml        ← WildFly-specific (security domains, loader repo)
  myapp-web.war
  myapp-ejb.jar
  lib/                   ← Shared libraries (visible to all modules)
```

## Servlets (Jakarta Servlet 6.0)

```java
@WebServlet("/hello")
public class HelloServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        resp.setContentType("text/html");
        resp.getWriter().println("<h1>Hello from WildFly</h1>");
    }
}
```

Filters: `@WebFilter`, async: `@WebServlet(asyncSupported=true)`, listeners: `@WebListener`

## CDI (Jakarta Contexts and Dependency Injection 4.0)

### Bean Scopes

| Scope | Annotation | Lifetime |
|-------|-----------|---------|
| Request | `@RequestScoped` | Single HTTP request |
| Session | `@SessionScoped` | HTTP session |
| Application | `@ApplicationScoped` | App lifetime (singleton) |
| Conversation | `@ConversationScoped` | Programmatically managed |
| Dependent | `@Dependent` (default) | Lifecycle of injecting bean |

```java
@ApplicationScoped
public class UserService {
    @Inject
    private UserRepository repo;

    public List<User> findAll() { return repo.findAll(); }
}
```

### Producers and Qualifiers

```java
@Qualifier
@Retention(RUNTIME)
@Target({FIELD, TYPE, METHOD})
public @interface Premium {}

@Produces @Premium
public Discount premiumDiscount() { return new Discount(0.20); }

// Injection point
@Inject @Premium Discount discount;
```

### Events

```java
@Inject Event<UserCreated> event;
event.fire(new UserCreated(user));

// Observer
void onUserCreated(@Observes UserCreated e) { ... }
// Async observer
void onAsync(@ObservesAsync UserCreated e) { ... }
```

Enable CDI: place `beans.xml` in `WEB-INF/` (empty = annotated-only discovery, `bean-discovery-mode="all"` = all classes)

## EJB (Jakarta Enterprise Beans 4.0)

### EJB Types

| Type | Annotation | Use Case |
|------|-----------|---------|
| Stateless Session | `@Stateless` | Shared business logic, pooled |
| Stateful Session | `@Stateful` | Per-client conversational state |
| Singleton | `@Singleton` | App-wide state, startup tasks |
| Message-Driven | `@MessageDriven` | Async JMS message processing |

```java
@Stateless
@TransactionAttribute(TransactionAttributeType.REQUIRED)
public class OrderService {
    @PersistenceContext
    private EntityManager em;

    public Order createOrder(Order order) {
        em.persist(order);
        return order;
    }
}
```

### Transaction Attributes

| Attribute | Behaviour |
|-----------|----------|
| `REQUIRED` (default) | Join existing or create new |
| `REQUIRES_NEW` | Always create new (suspends existing) |
| `MANDATORY` | Must have existing — exception if not |
| `NOT_SUPPORTED` | Suspend existing, run without |
| `SUPPORTS` | Join if exists, run without if not |
| `NEVER` | Exception if transaction exists |

### Scheduling with EJBs

```java
@Singleton
@Startup
public class SchedulerBean {
    @Schedule(hour="*", minute="*/15", persistent=false)
    public void runEvery15Min() { ... }
}
```

### Async EJBs

```java
@Stateless
public class ReportService {
    @Asynchronous
    public Future<Report> generateReport(String id) {
        // long operation
        return new AsyncResult<>(report);
    }
}
```

## JSF (Jakarta Faces 4.0)

```java
@Named("userBean")
@ViewScoped
public class UserBean implements Serializable {
    @Inject private UserService userService;
    private List<User> users;

    @PostConstruct
    public void init() { users = userService.findAll(); }

    public List<User> getUsers() { return users; }
}
```

```xhtml
<!-- users.xhtml -->
<h:dataTable value="#{userBean.users}" var="u">
  <h:column><h:outputText value="#{u.name}"/></h:column>
</h:dataTable>
```

Modern alternative: use **Jakarta REST** (JAX-RS) + frontend framework (React/Angular) instead of JSF for new projects.

## Datasources and JPA

### Datasource Configuration (CLI)

```bash
# Add JDBC driver module first, then:
/subsystem=datasources/data-source=MyDS:add(
  jndi-name="java:jboss/datasources/MyDS",
  driver-name="postgresql",
  connection-url="jdbc:postgresql://db:5432/mydb",
  user-name="${env.DB_USER}",
  password="${env.DB_PASS}",
  min-pool-size=5,
  max-pool-size=20,
  pool-prefill=true,
  validate-on-match=true,
  check-valid-connection-sql="SELECT 1"
)
```

### JPA persistence.xml

```xml
<persistence xmlns="https://jakarta.ee/xml/ns/persistence" version="3.1">
  <persistence-unit name="myPU" transaction-type="JTA">
    <jta-data-source>java:jboss/datasources/MyDS</jta-data-source>
    <properties>
      <property name="hibernate.dialect" value="org.hibernate.dialect.PostgreSQLDialect"/>
      <property name="hibernate.hbm2ddl.auto" value="validate"/>
      <property name="hibernate.show_sql" value="false"/>
    </properties>
  </persistence-unit>
</persistence>
```

### JPA Entity

```java
@Entity
@Table(name = "orders")
@NamedQuery(name = "Order.findByStatus",
            query = "SELECT o FROM Order o WHERE o.status = :status")
public class Order {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String status;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "customer_id")
    private Customer customer;
}
```

## Clustering and Session Replication

WildFly HA clusters use **JGroups** for node discovery and **Infinispan** for distributed session state.

### Enabling HA

1. Start with `standalone-ha.xml` (or `domain.xml` with `ha` profile)
2. Use `jvmRoute` in Undertow for sticky sessions
3. Add `<distributable/>` to `web.xml` for session replication

```xml
<!-- web.xml -->
<web-app>
  <distributable/>
</web-app>
```

### Deployment Descriptors for HA

```xml
<!-- jboss-web.xml -->
<jboss-web>
  <context-root>/myapp</context-root>
  <replication-config>
    <replication-trigger>SET_AND_NON_PRIMITIVE_GET</replication-trigger>
    <replication-granularity>SESSION</replication-granularity>
  </replication-config>
</jboss-web>
```

### Load Balancer Integration

- **mod_cluster**: Native WildFly load balancer module (Apache httpd or Undertow)
- **Kubernetes**: Use WildFly Operator's StatefulSet with headless service for cluster discovery

## JNDI Lookups

```java
// Container-managed (preferred)
@Resource(lookup = "java:jboss/datasources/MyDS")
private DataSource ds;

// Programmatic
InitialContext ctx = new InitialContext();
DataSource ds = (DataSource) ctx.lookup("java:jboss/datasources/MyDS");
```

Standard JNDI namespaces:
- `java:comp/` — component-scoped
- `java:module/` — module-scoped
- `java:app/` — application-scoped
- `java:global/` — global (all deployments)
- `java:jboss/` — WildFly-specific (datasources, messaging, etc.)
