# Distribution Patterns — PEAA

These two patterns address how to communicate between processes separated by a network boundary. They exist to counteract the high cost of remote method calls.

---

## The Distribution Principle (Context)

**Fowler's central rule**: Do not distribute objects.

Remote calls are orders of magnitude slower than local calls. The natural design for in-process OO (many small objects with fine-grained methods) becomes disastrous when applied to distributed systems: hundreds of remote calls per user action destroy performance.

The two distribution patterns solve this by:
1. Presenting a coarse-grained interface over fine-grained internal objects (Remote Facade)
2. Carrying data across the boundary in bulk objects instead of many small calls (Data Transfer Object)

---

## Remote Facade

**Intent**: Provides a coarse-grained facade on fine-grained objects to improve efficiency over a network.

**Problem**
Your domain model has fine-grained objects with fine-grained methods:
```java
order.getCustomer().getAddress().getStreet()  // 3 object navigations
order.addLineItem(product, qty)                // fine-grained mutation
order.recalculateTotals()
order.validate()
```

If these are remote calls, performance collapses. A single user action requires dozens of round trips.

**Solution**
Add a coarse-grained facade that batches what a client typically needs into a single remote call:

```java
// Remote interface — coarse-grained
public interface OrderRemoteFacade {
    // One call returns everything needed to render an order form
    OrderDTO getOrderForEditing(long orderId);

    // One call submits all changes made in the UI
    void updateOrder(long orderId, OrderUpdateDTO changes);

    // One call returns order summary list
    List<OrderSummaryDTO> getOrdersForCustomer(long customerId);
}
```

**Implementation**
```java
public class OrderRemoteFacadeImpl implements OrderRemoteFacade {

    private OrderRepository orders;
    private OrderService orderService;

    @Override
    public OrderDTO getOrderForEditing(long orderId) {
        Order order = orders.findById(orderId);
        // Assemble DTO from multiple fine-grained domain objects
        return OrderAssembler.toDTO(order);
    }

    @Override
    public void updateOrder(long orderId, OrderUpdateDTO changes) {
        // One remote call triggers multiple fine-grained domain operations
        Order order = orders.findById(orderId);
        order.updateShippingAddress(changes.shippingAddress());
        changes.lineItemUpdates().forEach(u ->
            order.updateLineItemQuantity(u.lineItemId(), u.quantity()));
        orders.save(order);
    }
}
```

**Key Design Principles**
- Remote Facade is purely a distribution concern — put NO domain logic in it
- Facade delegates to the real domain model; domain model remains unaware of distribution
- Facade methods are coarse enough that clients can complete a full use case in 1-2 remote calls

**When to Use**
- True network boundary exists (different process, different server)
- Fine-grained domain model exists that is excellent for local use
- Must expose functionality to external clients (external apps, legacy systems, third parties)

**When NOT to Use**
- In-process calls — no distribution needed, no facade needed
- Most modern microservices are best served by designing coarse REST APIs directly, not by adding a facade over fine-grained objects

---

## Data Transfer Object (DTO)

**Intent**: An object that carries data between processes, reducing the number of method calls.

**Problem**
When sending data across a network boundary, each method call has significant overhead. Fine-grained accessors become unacceptable:
```java
// Fine-grained — terrible over network (each call = round trip)
String street = remoteOrder.getCustomer().getAddress().getStreet();
String city   = remoteOrder.getCustomer().getAddress().getCity();
String zip    = remoteOrder.getCustomer().getAddress().getZip();
```

**Solution**
Pack all needed data into one serializable object and send it in one call:
```java
// One call retrieves everything
OrderDTO dto = orderService.getOrder(orderId);
// All data available locally
String street = dto.getCustomerStreet();
String city   = dto.getCustomerCity();
String zip    = dto.getCustomerZip();
```

**DTO Structure**
- Plain data container — no business logic, no domain behavior
- Serializable (must survive process boundary: Java serialization, JSON, XML, Protobuf)
- Flat or nested, but designed for what the client actually needs — not mirroring the domain model 1:1

**Example**
```java
// DTO (plain data, serializable)
public class OrderDTO {
    private long id;
    private String status;
    private BigDecimal total;
    private String customerName;
    private String customerEmail;
    private String shippingStreet;
    private String shippingCity;
    private String shippingZip;
    private List<LineItemDTO> lineItems;

    // getters and setters only — no business logic
}

public class LineItemDTO {
    private long productId;
    private String productName;
    private int quantity;
    private BigDecimal unitPrice;
    private BigDecimal subtotal;
}
```

**Assembler**
DTO assembly from domain objects belongs in an Assembler (not in the DTO or domain objects):
```java
public class OrderAssembler {
    public static OrderDTO toDTO(Order order) {
        OrderDTO dto = new OrderDTO();
        dto.setId(order.id());
        dto.setStatus(order.status().name());
        dto.setTotal(order.total().amount());
        dto.setCustomerName(order.customer().fullName());
        dto.setShippingStreet(order.shippingAddress().street());
        // ...
        dto.setLineItems(order.lineItems().stream()
            .map(LineItemAssembler::toDTO)
            .collect(toList()));
        return dto;
    }
}
```

**DTO vs. Domain Object**
| Aspect | Domain Object | DTO |
|---|---|---|
| Logic | Rich business methods | None — data only |
| Boundary | Internal to process | Crosses process boundary |
| Shape | Optimized for domain | Optimized for client needs |
| Serializable | Not required | Required |

**DTO in Modern APIs**
The pattern is universal in REST APIs — your JSON request/response bodies ARE Data Transfer Objects (often called "request/response bodies", "API models", or "view models"). Libraries like MapStruct, ModelMapper, and hand-written assemblers handle DTO ↔ domain mapping.

**Anti-patterns**
- Exposing domain objects directly over REST (couples API contract to internal model)
- DTOs with business logic (defeats the purpose — put logic in domain objects)
- One DTO class shared across all use cases (different operations need different projections)

**When to Use**
- Any network boundary (REST API, gRPC, RMI, message queue payloads)
- As response bodies in REST controllers
- As command objects (request DTOs) for incoming data before validation and domain mapping
