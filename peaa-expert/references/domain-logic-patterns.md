# Domain Logic Patterns — PEAA

## Transaction Script

**Intent**: Organizes business logic by procedures where each procedure handles a single request from the presentation.

**Structure**
- One method (script) per business transaction or use case
- Script coordinates: validates input → loads data → executes logic → stores results → returns response
- Scripts may share common subroutines (validation helpers, calculation utilities)

**When to Use**
- Simple domain logic with few validations or rules
- CRUD-heavy applications
- Small team or rapid prototyping
- Integrating with existing procedural code

**When to Avoid**
- Domain grows complex — duplication across scripts becomes painful
- Multiple scripts need the same business rules (logic should centralize in a Domain Model instead)

**Implementation**
```java
// Command pattern or simple class per use case
public class PlaceOrderScript {
    private OrderGateway orderGateway;
    private InventoryGateway inventoryGateway;

    public void execute(long customerId, List<LineItem> items) {
        // validate
        if (items.isEmpty()) throw new ValidationException("No items");
        // load + check inventory
        for (LineItem item : items) {
            if (!inventoryGateway.isAvailable(item.productId(), item.quantity())) {
                throw new InsufficientInventoryException(item.productId());
            }
        }
        // calculate total
        Money total = items.stream()
            .map(i -> i.unitPrice().times(i.quantity()))
            .reduce(Money.ZERO, Money::add);
        // persist
        orderGateway.insert(customerId, items, total);
    }
}
```

**Common Data Source Companions**: Table Data Gateway, Row Data Gateway

---

## Domain Model

**Intent**: An object model of the domain incorporating both data and behavior.

**Structure**
- Domain objects map to domain concepts (Order, Customer, Invoice)
- Objects have methods that embody business rules (not just getters/setters)
- Objects collaborate through associations
- Domain layer is ignorant of persistence (with Data Mapper) or encapsulates it (with Active Record)

**When to Use**
- Complex business logic with policies, rules, calculations
- Long-lived applications where domain knowledge grows
- Multiple use cases share common business behavior
- Team has OO design skills

**When to Avoid**
- Simple CRUD with no real business rules — overhead not justified
- Team unfamiliar with OO design or ORM frameworks
- Tight deadline with simple problem — Transaction Script faster to bootstrap

**Key Design Principles**
- **Rich behavior**: Methods on domain objects, not anemic getters + service logic
- **Ubiquitous language**: Class/method names match domain language
- **Encapsulation**: Domain objects protect their invariants

**Example**
```java
public class Order {
    private List<LineItem> lineItems = new ArrayList<>();
    private OrderStatus status = OrderStatus.DRAFT;

    public void addItem(Product product, int quantity) {
        if (status != OrderStatus.DRAFT)
            throw new OrderException("Cannot modify submitted order");
        lineItems.add(new LineItem(product, quantity));
    }

    public Money total() {
        return lineItems.stream()
            .map(LineItem::subtotal)
            .reduce(Money.ZERO, Money::add);
    }

    public void submit() {
        if (lineItems.isEmpty())
            throw new OrderException("Cannot submit empty order");
        this.status = OrderStatus.SUBMITTED;
    }
}
```

**Common Data Source Companions**: Data Mapper (preferred for independence), Active Record (simpler but couples domain to DB)

---

## Table Module

**Intent**: A single instance handles the business logic for all rows in a database table or view.

**Structure**
- One class per table (or significant query result)
- Methods operate on a Record Set — tabular data passed in or held as state
- No per-row objects; logic driven by row identifiers

**When to Use**
- Moderate domain complexity
- Platform supports Record Set infrastructure well (ADO.NET DataSet, COM+)
- Table-centric thinking matches the team's mental model
- Avoiding the overhead of full Domain Model while getting better organization than Transaction Script

**When to Avoid**
- Complex domain relationships that don't map cleanly to tables
- When polymorphism and inheritance are needed in domain logic

**Example**
```csharp
public class OrderModule {
    private DataTable _data;

    public OrderModule(DataTable data) {
        _data = data;
    }

    public decimal GetTotal(int orderId) {
        // filter rows for this order, sum line totals
        var rows = _data.Select($"OrderId = {orderId}");
        return rows.Sum(r => (decimal)r["Quantity"] * (decimal)r["UnitPrice"]);
    }

    public void Submit(int orderId) {
        var rows = _data.Select($"OrderId = {orderId}");
        if (!rows.Any())
            throw new ArgumentException("Order not found");
        foreach (var row in rows)
            row["Status"] = "SUBMITTED";
    }
}
```

**Contrasted with Domain Model**
- Table Module: one instance, works on sets of rows via identifiers
- Domain Model: one object per row/entity, encapsulates its own state

---

## Service Layer

**Intent**: Defines an application's boundary with a layer of services that establishes a set of available operations and coordinates the application's response in each operation.

**Structure**
- Service methods = application use cases (one method per operation exposed to clients)
- Service coordinates: begins transaction, delegates to domain objects or gateways, commits
- Services do NOT contain domain logic — they orchestrate it

**When to Use**
- Multiple client types (web, REST API, batch, message consumer) all need the same operations
- Transaction demarcation needs a clear, centralized location
- Application is complex enough to warrant separating "what operations exist" from "how they're implemented"

**When to Avoid**
- Simple application with one client type — adds unnecessary layer
- Risk: services become "god scripts" containing domain logic (anemic domain model anti-pattern)

**Two Styles**
1. **Domain Facade** (thin): Service methods are thin wrappers; all logic in domain objects
2. **Operation Script** (thick): Services contain significant logic; domain objects are anemic

Fowler recommends **Domain Facade** style. Thick service layers replicate the problems of Transaction Script at a higher level.

**Example**
```java
// Service Layer (thin / Domain Facade style)
@Transactional
public class OrderService {
    private OrderRepository orders;
    private InventoryService inventory;

    public OrderId placeOrder(CustomerId customerId, List<OrderLine> lines) {
        Customer customer = customers.findById(customerId);
        Order order = customer.createOrder(lines);  // domain logic here
        inventory.reserve(order);                    // domain service
        orders.save(order);
        return order.id();
    }
}
```

**Relationship to Other Patterns**
- Service Layer + Domain Model + Data Mapper: the canonical "full stack" for complex applications
- Service Layer + Transaction Script: service IS the script; acceptable for simple cases
- Service Layer acts as the boundary for Remote Facade if distribution is needed
