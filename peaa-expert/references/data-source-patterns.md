# Data Source Architectural Patterns — PEAA

These four patterns represent the main approaches to connecting domain logic with a relational database. They sit on a spectrum from simple/coupled to complex/decoupled.

## Comparison at a Glance

| Pattern | Per table or per row? | Domain logic mixed in? | Complexity | Best paired with |
|---|---|---|---|---|
| Table Data Gateway | Per table | No | Low | Transaction Script, Table Module |
| Row Data Gateway | Per row | No | Low-Medium | Transaction Script |
| Active Record | Per row | Yes | Medium | Simple Domain Model |
| Data Mapper | Separate mapper | No | High | Rich Domain Model |

---

## Table Data Gateway

**Intent**: An object that acts as a Gateway to a database table. One instance handles all the rows in the table.

**Structure**
- One class per table (or significant view)
- Methods: `find(id)`, `findAll()`, `insert(...)`, `update(...)`, `delete(id)`
- Returns raw data structures (Record Set, Map, or simple data objects) — not domain objects
- No domain logic in the gateway

**Example**
```java
public class OrderGateway {
    private DataSource ds;

    public ResultSet findById(long id) throws SQLException {
        PreparedStatement stmt = ds.getConnection()
            .prepareStatement("SELECT * FROM orders WHERE id = ?");
        stmt.setLong(1, id);
        return stmt.executeQuery();
    }

    public long insert(long customerId, Timestamp createdAt, String status) throws SQLException {
        PreparedStatement stmt = ds.getConnection()
            .prepareStatement("INSERT INTO orders(customer_id, created_at, status) VALUES(?,?,?)",
                Statement.RETURN_GENERATED_KEYS);
        stmt.setLong(1, customerId);
        stmt.setTimestamp(2, createdAt);
        stmt.setString(3, status);
        stmt.executeUpdate();
        ResultSet keys = stmt.getGeneratedKeys();
        keys.next();
        return keys.getLong(1);
    }

    public void update(long id, String status) throws SQLException {
        PreparedStatement stmt = ds.getConnection()
            .prepareStatement("UPDATE orders SET status = ? WHERE id = ?");
        stmt.setString(1, status);
        stmt.setLong(2, id);
        stmt.executeUpdate();
    }
}
```

**When to Use**
- Transaction Script or Table Module as domain logic approach
- Need clean separation of SQL from scripting logic
- Testing: easy to mock gateway in scripts

---

## Row Data Gateway

**Intent**: An object that acts as a Gateway to a single record in a data source. There is one instance per row.

**Structure**
- Each instance holds data for one row
- Methods: field accessors + `insert()`, `update()`, `delete()`, static `find*(...)` factory methods
- Does not contain domain logic — pure data + persistence

**Compared to Active Record**
- Row Data Gateway: same structure, but NO domain logic. Domain logic lives in Transaction Scripts.
- Active Record: same structure, but WITH domain logic.

**Example**
```java
public class OrderGateway {
    private long id;
    private long customerId;
    private String status;
    private DataSource ds;

    // Factory / finder
    public static OrderGateway findById(long id, DataSource ds) throws SQLException {
        PreparedStatement stmt = ds.getConnection()
            .prepareStatement("SELECT * FROM orders WHERE id = ?");
        stmt.setLong(1, id);
        ResultSet rs = stmt.executeQuery();
        rs.next();
        return new OrderGateway(rs, ds);
    }

    public void update() throws SQLException {
        PreparedStatement stmt = ds.getConnection()
            .prepareStatement("UPDATE orders SET status=?, customer_id=? WHERE id=?");
        stmt.setString(1, status);
        stmt.setLong(2, customerId);
        stmt.setLong(3, id);
        stmt.executeUpdate();
    }

    // Getters and setters for customerId, status, etc.
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}
```

**When to Use**
- Transaction Script domain logic
- Prefer finer-grained object access over Table Data Gateway's set-level access
- Small number of tables

---

## Active Record

**Intent**: An object that wraps a row in a database table or view, encapsulates the database access, and adds domain logic on that data.

**Structure**
- One class per table; one instance per row
- Contains: data fields, DB access methods (`save()`, `delete()`, `find*()`) AND domain logic methods
- The class IS both a domain object and its own persistence mechanism

**Trade-offs**
- Simple: no separate mapper layer
- Couples domain model to DB schema — hard to refactor either independently
- Works best when domain model and DB schema are close in structure

**Example (Ruby on Rails style — the canonical Active Record implementation)**
```ruby
class Order < ApplicationRecord
  has_many :line_items
  belongs_to :customer

  validates :status, inclusion: { in: %w[draft submitted shipped] }

  def submit!
    raise "Cannot submit empty order" if line_items.empty?
    update!(status: 'submitted')
  end

  def total
    line_items.sum { |li| li.unit_price * li.quantity }
  end
end

# Usage
order = Order.find(42)
order.submit!
```

**Java / manual Active Record**
```java
public class Order {
    private long id;
    private String status;
    private static DataSource ds;

    public static Order findById(long id) throws SQLException { /* SQL here */ }

    public void save() throws SQLException {
        if (id == 0) insert();
        else update();
    }

    public void submit() {
        if ("draft".equals(status)) this.status = "submitted";
        else throw new IllegalStateException("Cannot submit");
    }
}
```

**When to Use**
- Simple Domain Model where domain objects closely mirror tables
- Team wants the simplicity of one-class-per-table without a separate mapper
- Framework (Rails, Django) provides Active Record as default — follow the framework

**When to Avoid**
- Complex domain model with many associations, inheritance, or divergent schema
- Domain objects need to be persistence-ignorant (testable without DB)

---

## Data Mapper

**Intent**: A layer of Mappers that moves data between objects and a database while keeping them independent of each other and the mapper itself.

**Structure**
- **Domain objects**: pure business logic, no DB knowledge
- **Mapper objects**: one mapper per domain class; handle SQL + object construction
- Domain objects never reference mappers; mappers know about both domain and DB

**Responsibilities of a Mapper**
1. Load: execute SQL, create domain objects from ResultSet
2. Save: read domain object state, execute INSERT/UPDATE SQL
3. Identity management: integrate with Identity Map to prevent duplicate loads
4. Association handling: handle foreign keys, lazy loading, collections

**Example**
```java
public class OrderMapper {
    private IdentityMap<Long, Order> identityMap = new IdentityMap<>();
    private DataSource ds;

    public Order findById(long id) throws SQLException {
        if (identityMap.contains(id)) return identityMap.get(id);

        PreparedStatement stmt = ds.getConnection()
            .prepareStatement("SELECT * FROM orders WHERE id = ?");
        stmt.setLong(1, id);
        ResultSet rs = stmt.executeQuery();
        rs.next();
        Order order = load(rs);
        identityMap.put(id, order);
        return order;
    }

    private Order load(ResultSet rs) throws SQLException {
        long id = rs.getLong("id");
        String status = rs.getString("status");
        // construct domain object WITHOUT knowing about DB
        return new Order(id, status);
    }

    public void insert(Order order) throws SQLException {
        PreparedStatement stmt = ds.getConnection()
            .prepareStatement("INSERT INTO orders(status) VALUES(?)",
                Statement.RETURN_GENERATED_KEYS);
        stmt.setString(1, order.status());
        stmt.executeUpdate();
        ResultSet keys = stmt.getGeneratedKeys();
        keys.next();
        order.setId(keys.getLong(1));
        identityMap.put(order.id(), order);
    }

    public void update(Order order) throws SQLException {
        PreparedStatement stmt = ds.getConnection()
            .prepareStatement("UPDATE orders SET status=? WHERE id=?");
        stmt.setString(1, order.status());
        stmt.setLong(2, order.id());
        stmt.executeUpdate();
    }
}
```

**When to Use**
- Rich Domain Model that must be persistence-ignorant
- DB schema and domain model are significantly different
- Need to test domain logic without DB
- Using an ORM (Hibernate, JPA, SQLAlchemy) — they implement Data Mapper for you

**When to Avoid**
- Simple schemas where Active Record suffices — Data Mapper adds substantial complexity
- Small applications — overhead rarely worth it

**Modern Reality**
Most modern Data Mappers are provided by ORM frameworks. When using JPA/Hibernate, Spring Data, or SQLAlchemy, you are using the Data Mapper pattern. The mapper = the ORM's persistence machinery; your entity = the domain object.
