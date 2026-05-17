# Base Patterns — PEAA

These are fundamental building blocks used across many of the other patterns in the book. They are not specific to any one layer.

---

## Gateway

**Intent**: An object that encapsulates access to an external system or resource.

**Problem**: Code that uses an external system (database, messaging system, web service, file system) becomes tightly coupled to its API. This makes testing, replacement, and evolution difficult.

**Solution**: Wrap all access behind a Gateway with an interface defined in terms of your application's needs.

```java
// Application-defined interface
public interface PaymentGateway {
    PaymentResult charge(Money amount, CreditCard card);
    void refund(String transactionId, Money amount);
}

// Infrastructure implementation
public class StripePaymentGateway implements PaymentGateway {
    private StripeClient stripe;

    @Override
    public PaymentResult charge(Money amount, CreditCard card) {
        // translate to Stripe's API
        ChargeParams params = ChargeParams.builder()
            .amount(amount.inCents())
            .currency(amount.currency().getCurrencyCode())
            .source(card.stripeToken())
            .build();
        Charge charge = stripe.charges().create(params);
        return new PaymentResult(charge.getId(), charge.getStatus());
    }
}
```

**Compared to Facade**: Gateway wraps an external system you don't control. Facade simplifies your own complex subsystem.

**Testing**: Replace Gateway with a Service Stub in tests — domain logic can be tested without real external systems.

---

## Mapper

**Intent**: An object that sets up a communication between two independent objects.

**Problem**: Two objects need to communicate but should not be aware of each other — introducing a direct dependency would violate their independence.

**Solution**: A Mapper stands between them, translating in both directions without either object knowing the Mapper exists.

**Examples in PEAA**
- Data Mapper: translates between domain objects and database tables
- DTO Assembler: translates between domain objects and Data Transfer Objects

**Compared to Facade / Gateway**
- Gateway: wraps external system, your code calls through it
- Facade: simplifies your own code behind a simpler interface
- Mapper: creates communication between two independent objects that shouldn't know each other

---

## Layer Supertype

**Intent**: A type that acts as the supertype for all types in its layer.

**Problem**: All domain objects need common behavior (identity field management, dirty tracking, common validation hooks). Duplicating this in every class is wasteful.

**Solution**: An abstract base class for all objects in a layer provides shared implementation.

```java
// Domain Layer Supertype
public abstract class DomainObject {
    private Long id;

    public Long getId() { return id; }
    public void setId(Long id) {
        if (this.id != null) throw new IllegalStateException("ID already set");
        this.id = id;
    }
    public boolean isNew() { return id == null; }

    // Hook for validation before save
    public void validate() { /* override in subclasses */ }
}

// All domain objects extend it
public class Order extends DomainObject {
    private String status;

    @Override
    public void validate() {
        if (status == null) throw new ValidationException("Status is required");
    }
}
```

**Other Layer Supertypes**
- Mapper Layer Supertype: shared mapper behavior (Identity Map access, session integration)
- Presentation Layer Supertype: shared controller behavior (auth checking, error handling)

---

## Separated Interface

**Intent**: Defines an interface in a separate package from its implementation.

**Problem**: A high-level module (domain layer) needs to use a low-level service (e.g., sending email, logging). If the domain directly references the implementation, the dependency is inverted — domain depends on infrastructure.

**Solution**: Define the interface in the domain (or application) package. The implementation lives in the infrastructure package. The domain depends only on the interface.

```
com.example.domain
  ├── OrderRepository (interface — domain defines this)
  └── EmailNotifier (interface — domain defines this)

com.example.infrastructure
  ├── JpaOrderRepository implements OrderRepository
  └── SmtpEmailNotifier implements EmailNotifier
```

```java
// In domain package — interface
public interface OrderRepository {
    Order findById(OrderId id);
    void save(Order order);
}

// In infrastructure package — implementation
public class JpaOrderRepository implements OrderRepository {
    @PersistenceContext
    private EntityManager em;

    @Override
    public Order findById(OrderId id) {
        return em.find(Order.class, id.value());
    }
}
```

**This IS the Dependency Inversion Principle (DIP)**: high-level modules define interfaces; low-level modules implement them. Domain doesn't know about JPA, SMTP, or any infrastructure technology.

---

## Registry

**Intent**: A well-known object that other objects can use to find common objects and services.

**Problem**: Objects need to find services or configurations but passing them everywhere as parameters is unwieldy.

**Solution**: A global Registry (often a singleton or thread-local) provides lookup by key.

```java
// Thread-local Registry (request-scoped services)
public class ServiceRegistry {
    private static final ThreadLocal<ServiceRegistry> current = new ThreadLocal<>();

    private UnitOfWork unitOfWork;
    private IdentityMap identityMap;

    public static ServiceRegistry current() {
        return current.get();
    }

    public static void setCurrent(ServiceRegistry registry) {
        current.set(registry);
    }

    public UnitOfWork unitOfWork() { return unitOfWork; }
    public IdentityMap identityMap() { return identityMap; }
}
```

**Caution**: Registry is effectively a service locator, which is considered an anti-pattern in modern DI-oriented design (hides dependencies, hard to test). Prefer dependency injection (Spring, CDI) over Registry when possible. Use Registry only when DI is unavailable or impractical (e.g., static initialization, domain objects that need services but can't receive them via constructor).

---

## Value Object

**Intent**: A small simple object, like money or date range, whose equality is not based on identity but on the values of its fields.

**Key Properties**
1. **No identity**: Two Value Objects with the same values are equal
2. **Immutable**: Never change after creation (avoids aliasing bugs)
3. **Self-validating**: Constructor enforces invariants

```java
public final class Money {
    private final BigDecimal amount;
    private final Currency currency;

    public Money(BigDecimal amount, Currency currency) {
        Objects.requireNonNull(amount, "amount");
        Objects.requireNonNull(currency, "currency");
        if (amount.compareTo(BigDecimal.ZERO) < 0)
            throw new IllegalArgumentException("Amount cannot be negative");
        this.amount = amount;
        this.currency = currency;
    }

    public Money add(Money other) {
        assertSameCurrency(other);
        return new Money(this.amount.add(other.amount), this.currency);
    }

    public Money times(int factor) {
        return new Money(this.amount.multiply(BigDecimal.valueOf(factor)), this.currency);
    }

    private void assertSameCurrency(Money other) {
        if (!this.currency.equals(other.currency))
            throw new IllegalArgumentException("Currency mismatch");
    }

    @Override
    public boolean equals(Object o) {
        if (!(o instanceof Money m)) return false;
        return amount.compareTo(m.amount) == 0 && currency.equals(m.currency);
    }

    @Override
    public int hashCode() { return Objects.hash(amount.stripTrailingZeros(), currency); }
}
```

**Compared to Entity**: Entity has identity (same object even if fields change). Value Object has no identity (a $10 USD bill is equal to any other $10 USD bill).

**JPA**: Use `@Embedded` to store Value Objects in their owner's table without giving them an independent identity.

---

## Money

**Intent**: Represents a monetary value combining an amount and a currency, providing arithmetic that is correct for money.

**Why Money Deserves Its Own Pattern**
- Floating-point arithmetic is **wrong** for money (0.1 + 0.2 ≠ 0.3 in IEEE 754)
- Currency mismatch must be caught (adding USD to EUR is an error)
- Rounding rules are domain-specific (half-up, banker's rounding, etc.)

**Core Implementation** (see Value Object for full example)
```java
// Key arithmetic rules:
Money price = new Money(new BigDecimal("9.99"), USD);
Money tax   = price.times(new BigDecimal("0.08")).round(RoundingMode.HALF_UP);
Money total = price.add(tax);

// Allocation (split without losing cents)
Money[] shares = total.allocate(new int[]{1, 1, 1});  // split in thirds exactly
```

**Allocation**: When splitting money, simple division loses cents due to rounding. Allocation distributes the remainder:
```java
public Money[] allocate(int[] ratios) {
    // ... distribute amount proportionally, add remainders to first shares
}
```

**Use `BigDecimal`, not `double` or `float`**. Always store amounts as integers (cents) or use `BigDecimal` with explicit scale.

---

## Special Case

**Intent**: A subclass that provides special behavior for particular cases, replacing conditional null checks with polymorphism.

**Also known as**: Null Object Pattern (for the null case)

**Problem**: Code is littered with null checks and edge-case conditionals:
```java
Customer customer = findCustomer(id);
String name = (customer != null) ? customer.name() : "Guest";
Money discount = (customer != null) ? customer.discount() : Money.ZERO;
```

**Solution**: Create a subclass (Special Case) that implements the expected behavior for the edge case — returning sensible defaults, no-ops, or special behavior.

```java
// Special Case for missing customer
public class GuestCustomer extends Customer {
    @Override
    public String name() { return "Guest"; }

    @Override
    public Money discount() { return Money.ZERO; }

    @Override
    public boolean isGuest() { return true; }
}

// Repository returns Special Case instead of null
public Customer findById(long id) {
    Customer c = queryById(id);
    return c != null ? c : new GuestCustomer();
}

// Client code — no null checks needed
Customer customer = repo.findById(id);
String name = customer.name();        // "Guest" for unknown customers
Money discount = customer.discount(); // ZERO for unknown customers
```

**When to Use**
- Null checks for the same condition appear in many places
- The "missing" case has meaningful default behavior
- Error handling for external systems (return a "failed payment" Special Case instead of throwing)

---

## Plugin

**Intent**: Links classes during configuration rather than at compile time.

**How It Works**: Choose the implementation class via configuration (property file, environment variable, IoC container) at startup — not by hard-coding the class reference in the dependent code.

```java
// Domain code depends only on interface
public interface TaxCalculator {
    Money calculate(Order order);
}

// Configuration selects implementation
# application.properties
tax.calculator.class=com.example.tax.CanadianTaxCalculator

// Factory reads config and instantiates
public class TaxCalculatorPlugin {
    public static TaxCalculator create() {
        String className = config.get("tax.calculator.class");
        return (TaxCalculator) Class.forName(className).getDeclaredConstructor().newInstance();
    }
}
```

**Modern Equivalent**: Spring's `@Conditional`, `@Profile`, `@Bean` configuration classes. The Plugin pattern IS what Spring's IoC container does: configuration selects implementations; code depends on interfaces.

---

## Service Stub

**Intent**: Removes dependence on problematic services during testing.

Also known as: **Test Double**, **Mock**, **Stub**

**Problem**: Tests that hit real external services (payment processors, email services, external APIs) are slow, fragile, and have side effects.

**Solution**: Replace the real service with a stub that returns predictable test values without hitting the external system.

```java
// Real implementation (production)
public class StripePaymentGateway implements PaymentGateway {
    public PaymentResult charge(Money amount, CreditCard card) {
        // hits real Stripe API
    }
}

// Service Stub (test)
public class StubPaymentGateway implements PaymentGateway {
    private boolean shouldSucceed = true;

    public void willFail() { shouldSucceed = false; }

    @Override
    public PaymentResult charge(Money amount, CreditCard card) {
        if (shouldSucceed)
            return new PaymentResult("test-txn-id", "succeeded");
        else
            return new PaymentResult(null, "failed");
    }
}

// Test
@Test
void order_fails_when_payment_rejected() {
    StubPaymentGateway stub = new StubPaymentGateway();
    stub.willFail();
    OrderService service = new OrderService(stub);
    assertThrows(PaymentFailedException.class, () -> service.checkout(cart));
}
```

**Works with Separated Interface / Gateway**: The test injects a stub that implements the same interface as the real service. Domain code is unaware of the substitution.

**Modern tools**: Mockito, MockMVC, WireMock — all implement the Service Stub concept. Mockito's `mock()` and `when().thenReturn()` create stubs automatically without writing stub classes.

---

## Record Set

**Intent**: An in-memory representation of tabular data.

**What It Is**: An object that mimics a database result set: rows and columns of data, navigable in memory, often disconnected from the DB after loading.

**Classic Examples**
- ADO.NET `DataSet` / `DataTable`
- Java `ResultSet` (connected) or `CachedRowSet` (disconnected)
- JDBC result data copied into `List<Map<String, Object>>`

**In PEAA Context**
- Table Module works with Record Sets — the module operates on a DataTable, not on individual domain objects
- Table Data Gateway returns a Record Set to the calling Transaction Script

```java
// Table Data Gateway returns a ResultSet (or List of Maps)
public List<Map<String, Object>> findOrdersByCustomer(long customerId) {
    List<Map<String, Object>> results = new ArrayList<>();
    ResultSet rs = executeQuery(customerId);
    while (rs.next()) {
        Map<String, Object> row = new LinkedHashMap<>();
        row.put("id", rs.getLong("id"));
        row.put("status", rs.getString("status"));
        row.put("total", rs.getBigDecimal("total"));
        results.add(row);
    }
    return results;
}
```

**Modern Relevance**
- Less relevant in Java/OO contexts where you map to domain objects or DTOs
- Still used in reporting, ETL, and data-grid scenarios where tabular structure is the natural output
- Spring JDBC's `RowMapper` / `JdbcTemplate.queryForList()` produces Record Set-equivalent structures
