# Object-Relational Structural Patterns — PEAA

These patterns address how to map the structural elements of an object model — fields, associations, embedded values, and inheritance — to relational tables.

---

## Identity Field

**Intent**: Saves a database identity field in an object to maintain identity between an in-memory object and a database row.

**Problem**: Relational DBs identify rows by primary key; objects are identified by memory address. When loading from DB into objects, we need a stable, persistent identity.

**Implementation**
- Add a `long id` (or `UUID id`) field to every persistent domain object
- Initialized on INSERT (use generated keys or pre-assign via sequence)
- Never changed after assignment (immutable identity)

**Key Types**
- **Meaningful key**: Natural business key (e.g., SSN, email) — risky; business keys change
- **Meaningless key**: Surrogate integer or UUID — preferred; stable, no business semantics
- **Compound key**: Multiple columns form the key — harder to use in code

**Example**
```java
public abstract class DomainObject {
    private long id = 0;  // 0 = not yet persisted

    public long getId() { return id; }
    public void setId(long id) {
        if (this.id != 0) throw new IllegalStateException("ID already set");
        this.id = id;
    }
    public boolean isNew() { return id == 0; }
}
```

**Guidance**
- Always use surrogate keys for domain objects
- UUIDs avoid coordination between distributed nodes; longs are more compact
- Primary key = identity in Identity Map; Identity Field provides that linkage

---

## Foreign Key Mapping

**Intent**: Maps an association between objects to a foreign key reference between tables.

**Problem**: Object associations are direct references; relational associations are foreign keys. The mapper must translate between them.

**One-to-Many Example**
```
Customer (1) -----< Order (many)
orders.customer_id → customers.id
```

**Loading (Customer → Orders)**
```java
public class OrderMapper {
    public List<Order> findByCustomer(long customerId) throws SQLException {
        PreparedStatement stmt = conn.prepareStatement(
            "SELECT * FROM orders WHERE customer_id = ?");
        stmt.setLong(1, customerId);
        ResultSet rs = stmt.executeQuery();
        List<Order> orders = new ArrayList<>();
        while (rs.next()) orders.add(load(rs));
        return orders;
    }
}
```

**Saving (Order → Customer FK)**
```java
public void insert(Order order) throws SQLException {
    PreparedStatement stmt = conn.prepareStatement(
        "INSERT INTO orders(customer_id, status) VALUES(?,?)");
    stmt.setLong(1, order.customer().getId());  // FK = parent's ID
    stmt.setString(2, order.status());
    stmt.executeUpdate();
}
```

**Bidirectional Associations**: One side "owns" the FK. Load from both directions but only write FK from the owning side.

**Delete Cascade**: When deleting a parent, either cascade delete children in SQL (`ON DELETE CASCADE`) or explicitly delete children in the mapper before deleting parent.

---

## Association Table Mapping

**Intent**: Saves an association as a table with foreign keys to the tables of the associated classes.

**Problem**: Many-to-many associations have no natural home in either table. A link/join table is required.

**Example**
```
students ←---student_courses---→ courses
student_courses(student_id, course_id)
```

**Loading**
```java
public List<Course> findCoursesForStudent(long studentId) throws SQLException {
    PreparedStatement stmt = conn.prepareStatement(
        "SELECT c.* FROM courses c " +
        "JOIN student_courses sc ON c.id = sc.course_id " +
        "WHERE sc.student_id = ?");
    stmt.setLong(1, studentId);
    // ... build list of Course objects
}
```

**Saving (full replacement strategy)**
```java
public void updateStudentCourses(long studentId, List<Course> courses)
        throws SQLException {
    // Delete all existing links
    PreparedStatement del = conn.prepareStatement(
        "DELETE FROM student_courses WHERE student_id = ?");
    del.setLong(1, studentId);
    del.executeUpdate();
    // Insert new links
    PreparedStatement ins = conn.prepareStatement(
        "INSERT INTO student_courses(student_id, course_id) VALUES(?,?)");
    for (Course c : courses) {
        ins.setLong(1, studentId);
        ins.setLong(2, c.getId());
        ins.addBatch();
    }
    ins.executeBatch();
}
```

---

## Dependent Mapping

**Intent**: Has one class perform the database mapping for a child class.

**When to Use**: Some objects are completely owned by a single parent (e.g., `LineItem` owned by `Order`). They have no independent identity and are never accessed outside their parent.

**Characteristics**
- Dependent has no Identity Field of its own (or its key is composite including the parent's key)
- Dependent is always loaded and saved through the parent's mapper
- No separate mapper class for the dependent

**Example**
```java
// OrderMapper handles LineItem persistence — no LineItemMapper class
public Order load(ResultSet rs) throws SQLException {
    Order order = new Order(rs.getLong("id"), rs.getString("status"));
    // Load dependents inline
    PreparedStatement lineStmt = conn.prepareStatement(
        "SELECT * FROM line_items WHERE order_id = ?");
    lineStmt.setLong(1, order.getId());
    ResultSet lineRs = lineStmt.executeQuery();
    while (lineRs.next()) {
        order.addLineItem(new LineItem(
            lineRs.getLong("product_id"),
            lineRs.getInt("quantity"),
            new Money(lineRs.getBigDecimal("unit_price"))
        ));
    }
    return order;
}
```

---

## Embedded Value

**Intent**: Maps an object into several fields of another object's table.

**When to Use**: Value Objects (Money, DateRange, Address) that don't need their own table. Storing them inline in the owning object's row is simpler and faster.

**Example**
```
Money embedded in Product:
products(id, name, price_amount, price_currency)
```

```java
// In ProductMapper.load():
BigDecimal amount = rs.getBigDecimal("price_amount");
String currency = rs.getString("price_currency");
Money price = new Money(amount, Currency.getInstance(currency));
return new Product(rs.getLong("id"), rs.getString("name"), price);

// In ProductMapper.insert():
stmt.setBigDecimal(n, product.price().amount());
stmt.setString(n+1, product.price().currency().getCurrencyCode());
```

**Trade-offs**
- Simple, no join needed
- Value Object cannot be queried independently
- If the Value Object type is shared across many tables, schema duplication occurs

**JPA Equivalent**: `@Embedded` and `@Embeddable`

---

## Serialized LOB

**Intent**: Saves a graph of objects by serializing them into a single large object (BLOB or CLOB) stored in a DB field.

**When to Use**: Complex graphs of domain objects that don't need to be queried by their internal structure. Store the whole graph as one opaque field.

**Two Formats**
- **BLOB**: Binary serialization (Java Serialization, Protobuf) — compact, not human-readable
- **CLOB**: Text serialization (XML, JSON) — readable, queryable via SQL if DB supports it

**Example (JSON CLOB)**
```java
// Save
ObjectMapper mapper = new ObjectMapper();
String json = mapper.writeValueAsString(order.history());  // List<HistoryEntry>
stmt.setString(1, json);

// Load
String json = rs.getString("history");
List<HistoryEntry> history = mapper.readValue(json,
    new TypeReference<List<HistoryEntry>>(){});
```

**Trade-offs**
- Very simple to implement for complex graphs
- Contents invisible to SQL WHERE clauses (cannot query inside the LOB)
- Versioning / migration when object structure changes
- Performance: entire LOB loaded even if only part needed

---

## Single Table Inheritance (STI)

**Intent**: Represents an inheritance hierarchy of classes as a single table that has columns for all the fields of the various classes.

**Table Structure**
```sql
CREATE TABLE employees (
    id          BIGINT PRIMARY KEY,
    type        VARCHAR(20) NOT NULL,  -- discriminator: 'FULL_TIME', 'PART_TIME', 'CONTRACT'
    name        VARCHAR(100),
    annual_salary DECIMAL(12,2),       -- only FULL_TIME
    hourly_rate   DECIMAL(8,2),        -- only PART_TIME
    contract_end  DATE                 -- only CONTRACT
);
```

**Loading (polymorphic)**
```java
public Employee load(ResultSet rs) throws SQLException {
    String type = rs.getString("type");
    return switch (type) {
        case "FULL_TIME" -> new FullTimeEmployee(
            rs.getLong("id"), rs.getString("name"), rs.getBigDecimal("annual_salary"));
        case "PART_TIME" -> new PartTimeEmployee(
            rs.getLong("id"), rs.getString("name"), rs.getBigDecimal("hourly_rate"));
        case "CONTRACT" -> new ContractEmployee(
            rs.getLong("id"), rs.getString("name"), rs.getDate("contract_end"));
        default -> throw new IllegalArgumentException("Unknown type: " + type);
    };
}
```

**Pros**
- Single table = simple queries; no joins
- Easy to add new subclasses (add columns)
- Polymorphic queries are trivial (`SELECT * FROM employees`)

**Cons**
- Many null columns when subclasses have different fields
- Table can become wide and sparse
- DB cannot enforce NOT NULL on subclass-specific columns

**Best for**: Small, simple hierarchies with few subclass-specific fields.

---

## Class Table Inheritance (CTI)

**Intent**: Represents an inheritance hierarchy of classes with one table per class in the hierarchy.

**Table Structure**
```sql
CREATE TABLE employees (id BIGINT PRIMARY KEY, name VARCHAR(100));
CREATE TABLE full_time_employees (
    id BIGINT PRIMARY KEY REFERENCES employees(id),
    annual_salary DECIMAL(12,2));
CREATE TABLE part_time_employees (
    id BIGINT PRIMARY KEY REFERENCES employees(id),
    hourly_rate DECIMAL(8,2));
```

**Loading**
```java
public Employee findById(long id) throws SQLException {
    // Must join to determine type, then load subtype
    ResultSet base = queryBase(id);  // SELECT from employees
    String type = determineType(id); // e.g., check which sub-table has this ID
    return switch (type) {
        case "FULL_TIME" -> {
            ResultSet sub = queryFullTime(id);
            yield new FullTimeEmployee(id, base.getString("name"),
                sub.getBigDecimal("annual_salary"));
        }
        // ...
    };
}
```

**Pros**
- Normalized; no wasted columns
- Subclass tables contain only subclass-specific data
- DB constraints enforceable on each table

**Cons**
- Queries require joins across multiple tables
- Polymorphic queries need UNION or multi-step lookup
- More complex mapper code

**Best for**: Hierarchies where normalization matters; large number of subclass-specific fields.

---

## Concrete Table Inheritance (CTT)

**Intent**: Represents an inheritance hierarchy with one table per concrete class.

**Table Structure**
```sql
-- No shared employees table
CREATE TABLE full_time_employees (
    id BIGINT PRIMARY KEY, name VARCHAR(100), annual_salary DECIMAL(12,2));
CREATE TABLE part_time_employees (
    id BIGINT PRIMARY KEY, name VARCHAR(100), hourly_rate DECIMAL(8,2));
```

**Pros**
- No joins needed to load a concrete type
- Simple tables; each fully self-contained
- Good for leaf-class queries

**Cons**
- Polymorphic queries require UNION across all tables
- Shared superclass fields duplicated in each table
- Adding a field to the superclass requires altering all concrete tables
- IDs must be unique across all tables (shared sequence or UUID)

**Best for**: Leaf-class access patterns dominate; polymorphic queries are rare; few shared fields.

---

## Inheritance Mappers

**Intent**: A structure for organizing database mappers that handle inheritance hierarchies.

**Problem**: Each inheritance strategy (STI, CTI, CTT) requires different SQL but shares common load/save structure. How do you avoid duplicating mapper logic?

**Pattern**
- Abstract mapper superclass holds shared behavior (load common fields, register with Identity Map)
- Concrete mappers override SQL and subclass-specific loading
- Factory method or switch dispatches to the right concrete mapper

**Structure**
```java
public abstract class EmployeeMapper {
    // Template method
    public Employee findById(long id) {
        Employee cached = identityMap.get(id);
        if (cached != null) return cached;
        ResultSet rs = executeFind(id);
        Employee emp = load(rs);
        identityMap.put(id, emp);
        return emp;
    }

    protected abstract ResultSet executeFind(long id);
    protected abstract Employee load(ResultSet rs);
    protected abstract void doInsert(Employee emp, PreparedStatement stmt);
}

public class FullTimeEmployeeMapper extends EmployeeMapper {
    protected ResultSet executeFind(long id) { /* STI or CTI SQL */ }
    protected Employee load(ResultSet rs) { /* create FullTimeEmployee */ }
    protected void doInsert(Employee emp, PreparedStatement stmt) { /* ... */ }
}
```

**Guidance**: This is largely an implementation concern when hand-rolling Data Mappers. ORM frameworks (JPA/Hibernate) handle all four inheritance strategies via annotations (`@Inheritance(strategy = InheritanceType.SINGLE_TABLE/JOINED/TABLE_PER_CLASS)`), making manual Inheritance Mappers unnecessary.
