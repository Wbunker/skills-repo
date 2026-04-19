# Architecture
*Chapters 16–21 — MicroProfile, Custom CDI, Interceptors, Bean Validation, Concurrency, Batch*

## Chapter 16: MicroProfile

MicroProfile extends Jakarta EE for cloud-native microservices. Jakarta EE servers (WildFly, Open Liberty, Payara, Quarkus) implement it alongside core EE specs.

### MicroProfile Dependency
```xml
<dependency>
  <groupId>org.eclipse.microprofile</groupId>
  <artifactId>microprofile</artifactId>
  <version>6.1</version>
  <scope>provided</scope>
  <type>pom</type>
</dependency>
```

### MP Config — Externalized Configuration
```java
@ApplicationScoped
public class AppConfig {
    @Inject @ConfigProperty(name="db.url")
    private String dbUrl;

    @Inject @ConfigProperty(name="max.retries", defaultValue="3")
    private int maxRetries;

    @Inject @ConfigProperty(name="feature.enabled", defaultValue="false")
    private Provider<Boolean> featureFlag;  // dynamic re-read
}
```

Config sources (highest priority first):
1. System properties (`-Ddb.url=...`)
2. Environment variables (`DB_URL`)
3. `microprofile-config.properties` in `META-INF/`
4. Custom `ConfigSource` implementations

### MP Health
```java
@ApplicationScoped
@Liveness
public class AppLivenessCheck implements HealthCheck {
    @Override
    public HealthCheckResponse call() {
        return HealthCheckResponse.named("app-live")
            .status(true).build();
    }
}

@ApplicationScoped
@Readiness
public class DatabaseReadinessCheck implements HealthCheck {
    @Inject DataSource ds;
    @Override
    public HealthCheckResponse call() {
        try (Connection c = ds.getConnection()) {
            c.isValid(1);
            return HealthCheckResponse.named("db-ready").up().build();
        } catch (Exception e) {
            return HealthCheckResponse.named("db-ready").down()
                .withData("error", e.getMessage()).build();
        }
    }
}
```

Endpoints: `GET /health`, `GET /health/live`, `GET /health/ready`, `GET /health/started`

### MP Metrics
```java
@ApplicationScoped
public class OrderService {
    @Inject MetricRegistry registry;

    @Counted(name="order.created", description="Orders placed")
    @Timed(name="order.time", description="Order processing time")
    public Order createOrder(OrderRequest req) { ... }
}
```

Scrape endpoint for Prometheus: `GET /metrics` (OpenMetrics format)

### MP Fault Tolerance
```java
@ApplicationScoped
public class ExternalService {

    @Retry(maxRetries=3, delay=500, delayUnit=ChronoUnit.MILLIS)
    @Timeout(2000)
    @CircuitBreaker(requestVolumeThreshold=10, failureRatio=0.5,
                    delay=5000, successThreshold=2)
    @Fallback(fallbackMethod="fallback")
    public String callExternal() {
        return httpClient.get("https://external.example.com/data");
    }

    public String fallback() {
        return "cached-default-value";
    }
}
```

### MP REST Client (type-safe)
```java
@RegisterRestClient(baseUri="https://api.example.com")
@Path("/users")
public interface UserApiClient {
    @GET @Path("{id}")
    @Produces(MediaType.APPLICATION_JSON)
    User getUser(@PathParam("id") Long id);
}

// Inject and use
@Inject @RestClient UserApiClient userClient;
User u = userClient.getUser(42L);
```

### MP OpenAPI
```java
@OpenAPIDefinition(
    info = @Info(title="My API", version="1.0"),
    servers = @Server(url="http://localhost:8080/api"))
@ApplicationPath("/api")
public class RestApplication extends Application {}
```
Endpoint: `GET /openapi` (YAML) or `GET /openapi?format=JSON`

---

## Chapter 17: Custom CDI

### CDI Producers
Create managed objects that CDI can inject but doesn't instantiate directly:

```java
@ApplicationScoped
public class ConfigProducer {

    @Produces @ApplicationScoped
    public DataSource produceDataSource() throws NamingException {
        InitialContext ctx = new InitialContext();
        return (DataSource) ctx.lookup("java:comp/DefaultDataSource");
    }

    @Produces @Dependent
    public EntityManager produceEntityManager(
            @SuppressWarnings("unused") InjectionPoint ip) {
        return emf.createEntityManager();
    }

    @Produces @RequestScoped @Named("currentUser")
    public User produceCurrentUser(HttpServletRequest request) {
        return (User) request.getSession().getAttribute("user");
    }
}
```

### CDI Events
```java
// Define event payload
public class UserCreatedEvent {
    private final User user;
    public UserCreatedEvent(User user) { this.user = user; }
    public User getUser() { return user; }
}

// Fire event
@Inject private Event<UserCreatedEvent> userCreatedEvent;
userCreatedEvent.fire(new UserCreatedEvent(newUser));

// Observe event (synchronous)
public void onUserCreated(@Observes UserCreatedEvent event) {
    emailService.sendWelcome(event.getUser());
}

// Observe after transaction (Jakarta EE)
public void onUserCreated(@Observes(during=TransactionPhase.AFTER_SUCCESS)
                           UserCreatedEvent event) { ... }

// Async event (CDI 2.0+)
userCreatedEvent.fireAsync(new UserCreatedEvent(newUser));
public void onUserCreatedAsync(@ObservesAsync UserCreatedEvent event) { ... }
```

### CDI Qualifiers
Distinguish multiple beans of the same type:
```java
// Define qualifier
@Qualifier
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.FIELD, ElementType.METHOD, ElementType.TYPE})
public @interface Premium {}

// Two implementations
@Premium @ApplicationScoped
public class PremiumEmailService implements EmailService { ... }

@ApplicationScoped
public class BasicEmailService implements EmailService { ... }

// Inject specific implementation
@Inject @Premium private EmailService emailService;
```

### CDI Decorators
Add behavior around an existing bean:
```java
@Decorator
@Priority(Interceptor.Priority.APPLICATION)
public class AuditingUserService implements UserService {
    @Inject @Delegate private UserService delegate;

    @Override
    public User create(String email) {
        auditLog.record("Creating user: " + email);
        User user = delegate.create(email);
        auditLog.record("Created user: " + user.getId());
        return user;
    }
}
```

Enable in `beans.xml`:
```xml
<beans xmlns="https://jakarta.ee/xml/ns/jakartaee">
  <decorators>
    <class>com.example.AuditingUserService</class>
  </decorators>
</beans>
```

---

## Chapter 18: Interceptors

Jakarta Interceptors 2.1 — AOP-style cross-cutting concerns.

### Defining an Interceptor Binding
```java
@InterceptorBinding
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.METHOD, ElementType.TYPE})
public @interface Audited {}
```

### Implementing the Interceptor
```java
@Audited
@Interceptor
@Priority(Interceptor.Priority.APPLICATION)
public class AuditInterceptor {

    @Inject private AuditService auditService;

    @AroundInvoke
    public Object audit(InvocationContext ctx) throws Exception {
        String method = ctx.getMethod().getName();
        Object[] params = ctx.getParameters();
        try {
            Object result = ctx.proceed();
            auditService.logSuccess(method, params);
            return result;
        } catch (Exception e) {
            auditService.logFailure(method, params, e);
            throw e;
        }
    }
}
```

### Applying the Interceptor
```java
@ApplicationScoped
@Audited   // Entire bean audited
public class UserService {

    @Audited   // Or just specific methods
    public User create(String email) { ... }

    public User findById(Long id) { ... }   // Not audited
}
```

### Lifecycle Interceptors
```java
@AroundConstruct
public void onConstruct(InvocationContext ctx) throws Exception {
    System.out.println("Bean being constructed");
    ctx.proceed();
}

@PostConstruct
public void afterConstruct(InvocationContext ctx) throws Exception {
    ctx.proceed();
    System.out.println("Bean constructed");
}
```

---

## Chapter 19: Bean Validation 3.0

### Built-in Constraints
```java
public class UserRegistration {
    @NotBlank(message="Name is required")
    @Size(min=2, max=100)
    private String name;

    @NotNull @Email
    private String email;

    @Min(18) @Max(120)
    private int age;

    @Past
    private LocalDate birthDate;

    @Pattern(regexp="[A-Z]{2}\\d{4}", message="Format: AB1234")
    private String memberCode;

    @Positive
    private BigDecimal balance;

    @NotEmpty
    private List<@Valid Address> addresses;  // cascaded validation
}
```

### Custom Constraint
```java
// Define annotation
@Constraint(validatedBy = NoHtmlValidator.class)
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
public @interface NoHtml {
    String message() default "HTML tags not allowed";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}

// Implement validator
public class NoHtmlValidator implements ConstraintValidator<NoHtml, String> {
    @Override
    public boolean isValid(String value, ConstraintValidatorContext ctx) {
        return value == null || !value.contains("<");
    }
}
```

### Validation Groups
```java
public interface OnCreate {}
public interface OnUpdate {}

public class UserDto {
    @NotNull(groups = OnUpdate.class)
    private Long id;

    @NotBlank(groups = {OnCreate.class, OnUpdate.class})
    private String name;

    @NotBlank(groups = OnCreate.class)
    private String password;
}

// Validate with group
validator.validate(dto, OnCreate.class);
```

### Programmatic Validation
```java
@Inject Validator validator;

Set<ConstraintViolation<UserDto>> violations = validator.validate(dto);
if (!violations.isEmpty()) {
    for (ConstraintViolation<UserDto> v : violations) {
        System.out.println(v.getPropertyPath() + ": " + v.getMessage());
    }
}
```

### Jakarta REST Integration
`@Valid` triggers validation on method params:
```java
@POST @Path("/users")
public Response createUser(@Valid UserRegistration reg) {
    // Only called if validation passes
    userService.create(reg);
    return Response.status(201).build();
}
// If invalid: 400 Bad Request with constraint violation details
```

---

## Chapter 20: Jakarta Concurrency 3.0

Provides managed threads safe for Jakarta EE (CDI injection, transactions, naming context propagated).

### ManagedExecutorService
```java
@Resource ManagedExecutorService executor;

// Submit async task
Future<String> future = executor.submit(() -> {
    // CDI injection works here!
    return externalService.call();
});

// Non-blocking CompletableFuture
CompletableFuture<User> cf =
    executor.supplyAsync(() -> userService.findById(42L))
            .thenApply(u -> enrich(u));
```

### ManagedScheduledExecutorService
```java
@Resource ManagedScheduledExecutorService scheduler;

ScheduledFuture<?> task = scheduler.scheduleAtFixedRate(
    () -> cleanupExpiredSessions(),
    0, 30, TimeUnit.MINUTES);
```

### ContextService — Propagate Context to External Threads
```java
@Resource ContextService contextService;

Runnable task = contextService.createContextualProxy(
    () -> {
        // This runnable now has JEE context (CDI, naming, etc.)
        userService.doWork();
    },
    Runnable.class);

// Can now run on a non-managed thread
new Thread(task).start();
```

### Jakarta Concurrency 3.0 Annotations
```java
@ManagedExecutorDefinition(
    name = "java:app/concurrent/MyExecutor",
    hungTaskThreshold = 120000,
    maxAsync = 5)
@ApplicationScoped
public class AppConfig {}

// Inject by name
@Resource(lookup="java:app/concurrent/MyExecutor")
ManagedExecutorService customExecutor;
```

---

## Chapter 21: Batch Processing 2.1

Jakarta Batch handles chunk-oriented and batchlet (task) jobs. Good for large data imports, report generation, ETL.

### Job XML (`META-INF/batch-jobs/import-users.xml`)
```xml
<job id="import-users" xmlns="https://jakarta.ee/xml/ns/jakartaee">
  <step id="read-and-import">
    <chunk item-count="100">
      <reader ref="userCsvReader"/>
      <processor ref="userProcessor"/>
      <writer ref="userDbWriter"/>
    </chunk>
  </step>
</job>
```

### ItemReader
```java
@Named("userCsvReader")
@Dependent
public class UserCsvReader implements ItemReader {
    @Inject @BatchProperty(name="file.path") private String filePath;

    private BufferedReader reader;
    private long lineNumber = 0;

    @Override
    public void open(Serializable checkpoint) throws Exception {
        reader = new BufferedReader(new FileReader(filePath));
        if (checkpoint != null) {
            long skip = (Long) checkpoint;
            for (long i = 0; i < skip; i++) reader.readLine();
            lineNumber = skip;
        }
    }

    @Override
    public Object readItem() throws Exception {
        String line = reader.readLine();
        if (line == null) return null;  // signals end
        lineNumber++;
        return parseCsvLine(line);
    }

    @Override
    public Serializable checkpointInfo() { return lineNumber; }

    @Override
    public void close() throws Exception { reader.close(); }
}
```

### ItemProcessor
```java
@Named("userProcessor")
@Dependent
public class UserProcessor implements ItemProcessor {
    @Inject Validator validator;

    @Override
    public Object processItem(Object item) throws Exception {
        UserDto dto = (UserDto) item;
        Set<ConstraintViolation<UserDto>> violations = validator.validate(dto);
        if (!violations.isEmpty()) return null;  // null = skip
        return mapToEntity(dto);
    }
}
```

### ItemWriter
```java
@Named("userDbWriter")
@Dependent
public class UserDbWriter implements ItemWriter {
    @Inject UserRepository repo;

    @Override
    public void writeItems(List<Object> items) {
        items.forEach(i -> repo.save((User) i));
    }
}
```

### Starting and Monitoring a Job
```java
@Inject JobOperator jobOperator;

// Start
Properties props = new Properties();
props.setProperty("file.path", "/data/users.csv");
long executionId = jobOperator.start("import-users", props);

// Check status
JobExecution exec = jobOperator.getJobExecution(executionId);
System.out.println(exec.getBatchStatus()); // STARTED, COMPLETED, FAILED...

// Restart failed job from checkpoint
jobOperator.restart(executionId, props);
```

### Batchlet (Non-chunk Task)
```java
@Named("cleanupBatchlet")
@Dependent
public class CleanupBatchlet extends AbstractBatchlet {
    @Override
    public String process() throws Exception {
        int deleted = archiveService.deleteExpired();
        return deleted > 0 ? "SUCCESS" : "NOTHING_TO_DO";
    }
}
```

---

## Common Architecture Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| CDI bean not injected | `beans.xml` missing or wrong discovery mode | Add `WEB-INF/beans.xml`; use `bean-discovery-mode="all"` if needed |
| Interceptor not firing | Not enabled in `beans.xml` | Not needed with `@Priority`; check annotation is on both binding and interceptor |
| `@Transactional` rollback not happening | Exception caught before propagating | Rethrow or mark with `rollbackOn` |
| ManagedExecutorService not found | Using `new Thread()` instead | Use `@Resource ManagedExecutorService` |
| Batch job not found | Job XML not in `META-INF/batch-jobs/` | Move XML to correct location |
| Bean Validation not running | `@Valid` missing | Add `@Valid` to JAX-RS param or inject `Validator` manually |
| MP Config property not found | Property name wrong or source missing | Check env var name (`DB_URL` for `db.url`) |
