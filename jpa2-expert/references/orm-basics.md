# ORM Basics — Entity and Collection Mapping
*Chapters 4–5 — Pro JPA 2 in Java EE 8, Mike Keith*

## Basic Entity Mapping (Ch 4)

### @Entity and @Table
```java
@Entity
@Table(name = "emp",
       schema = "hr",
       uniqueConstraints = @UniqueConstraint(columnNames = {"email"}))
public class Employee { ... }
```
- `@Entity(name = "Emp")` sets the JPQL entity name (defaults to class simple name).
- `@Table` controls the physical table; optional if class name matches table name.

### Access Types: Field vs Property
JPA reads annotations on either **fields** (instance variables) or **properties** (getter methods). Access type is determined by where `@Id` is placed.

```java
// Field access (recommended): annotate fields directly
@Entity
public class Employee {
    @Id private Long id;
    @Column(name = "salary") private BigDecimal salary;
}

// Property access: annotate getters
@Entity
public class Employee {
    private Long id;
    @Id public Long getId() { return id; }
    @Column(name = "salary") public BigDecimal getSalary() { return salary; }
}
```
Do not mix unless you use `@Access(AccessType.FIELD)` / `@Access(AccessType.PROPERTY)` explicitly.

---

## Identity — @Id and @GeneratedValue

### Single-Field Primary Key
```java
@Id
@GeneratedValue(strategy = GenerationType.SEQUENCE,
                generator = "emp_seq")
@SequenceGenerator(name = "emp_seq", sequenceName = "emp_id_seq",
                   allocationSize = 50)
private Long id;
```

### Generation Strategies
| Strategy | Mechanism | Best for |
|----------|-----------|----------|
| `IDENTITY` | DB auto-increment (MySQL, SQL Server) | Simple; no batching support |
| `SEQUENCE` | DB sequence object | PostgreSQL, Oracle; supports batching |
| `TABLE` | Emulated sequence via a table row | Portable; worst perf |
| `AUTO` | Provider picks based on DB | Development/prototyping only |

### @SequenceGenerator
```java
@SequenceGenerator(
    name        = "emp_seq",      // generator name referenced by @GeneratedValue
    sequenceName = "emp_id_seq",  // actual DB sequence name
    initialValue = 1,
    allocationSize = 50           // provider fetches 50 IDs at once (reduces DB round-trips)
)
```

### @TableGenerator
```java
@TableGenerator(
    name         = "emp_gen",
    table        = "id_generator",
    pkColumnName = "gen_name",
    valueColumnName = "gen_val",
    pkColumnValue = "emp_id",
    allocationSize = 100
)
```

---

## Column Mapping

### @Column
```java
@Column(name       = "first_name",
        nullable   = false,
        length     = 50,
        unique     = false,
        insertable = true,
        updatable  = true)
private String firstName;
```

### @Basic
Explicit form of the default mapping. Rarely needed unless setting `fetch = FetchType.LAZY` on a field (provider support varies).
```java
@Basic(fetch = FetchType.LAZY, optional = false)
private String description;
```

### @Lob
For BLOB/CLOB data. Type determines which:
```java
@Lob private byte[]  photo;      // → BLOB
@Lob private String  biography;  // → CLOB
```

### @Temporal (Java EE 8 / JPA 2.2 — pre-Java-8 dates)
```java
@Temporal(TemporalType.DATE)      // maps to SQL DATE
private java.util.Date birthDate;

@Temporal(TemporalType.TIMESTAMP) // maps to SQL TIMESTAMP
private java.util.Date lastLogin;
```
With Java 8+: `LocalDate`, `LocalDateTime`, `Instant` map automatically — no `@Temporal` needed.

### @Enumerated
```java
public enum EmployeeType { FULL_TIME, PART_TIME, CONTRACT }

@Enumerated(EnumType.STRING)   // stores "FULL_TIME" — preferred (rename-safe)
private EmployeeType type;

@Enumerated(EnumType.ORDINAL)  // stores 0, 1, 2 — fragile if enum order changes
private EmployeeType type;
```

### @Transient
```java
@Transient   // not persisted; also works on field annotated with java transient keyword
private String cachedDisplayName;
```

---

## Embedded Value Types

### @Embeddable and @Embedded
An `@Embeddable` class has no identity of its own — its fields map into the owning entity's table.

```java
@Embeddable
public class Address {
    private String street;
    private String city;
    @Column(name = "zip_code") private String zip;
}

@Entity
public class Employee {
    @Id private Long id;
    @Embedded private Address address;          // columns in EMPLOYEE table
    @Embedded
    @AttributeOverrides({
        @AttributeOverride(name = "street", column = @Column(name = "mail_street")),
        @AttributeOverride(name = "city",   column = @Column(name = "mail_city")),
        @AttributeOverride(name = "zip",    column = @Column(name = "mail_zip"))
    })
    private Address mailingAddress;
}
```

---

## Collection Mapping (Ch 5)

### @ElementCollection — Collection of Simple Values
Stores a collection of basic types or embeddables in a **separate table**. No separate entity class; no `@Id` in the collection table.

```java
@Entity
public class Employee {
    @Id private Long id;

    @ElementCollection
    @CollectionTable(name = "phone_numbers",
                     joinColumns = @JoinColumn(name = "emp_id"))
    @Column(name = "phone_num")
    private List<String> phoneNumbers;
}
```
Generated table: `PHONE_NUMBERS(emp_id FK, phone_num)`

### @ElementCollection of Embeddables
```java
@ElementCollection
@CollectionTable(name = "emp_addresses",
                 joinColumns = @JoinColumn(name = "emp_id"))
private List<Address> addresses;
```

### Ordering Collections

```java
// @OrderColumn — DB column stores insertion-order index
@ElementCollection
@OrderColumn(name = "phone_order")
private List<String> phoneNumbers;

// @OrderBy — DB ORDER BY clause; read-only ordering (no index column)
@OneToMany(mappedBy = "employee")
@OrderBy("lastName ASC, firstName ASC")
private List<Contact> contacts;
```

### Map Mappings

#### Map with simple key and simple value (both non-entity)
```java
@ElementCollection
@CollectionTable(name = "emp_attributes",
                 joinColumns = @JoinColumn(name = "emp_id"))
@MapKeyColumn(name = "attr_name")
@Column(name = "attr_value")
private Map<String, String> attributes;
```

#### Map keyed by enum
```java
@ElementCollection
@MapKeyEnumerated(EnumType.STRING)
@MapKeyColumn(name = "phone_type")
@Column(name = "phone_num")
private Map<PhoneType, String> phones;
```

#### Map from entity relationship — key is a field on the value entity
```java
// Phones keyed by their phone type field on the Phone entity
@OneToMany(mappedBy = "employee")
@MapKey(name = "type")          // "type" is a field on Phone entity
private Map<PhoneType, Phone> phoneMap;
```

#### Map with entity key (@ManyToMany or @OneToMany)
```java
@ManyToMany
@JoinTable(name = "project_roles",
           joinColumns = @JoinColumn(name = "emp_id"),
           inverseJoinColumns = @JoinColumn(name = "project_id"))
@MapKeyJoinColumn(name = "role_id")
private Map<Role, Project> projectRoles;
```

### Set vs. List vs. Map — Performance Notes
| Type | Duplicate check | Order | Extra column | Notes |
|------|----------------|-------|--------------|-------|
| `Set` | Equals/hashCode | None | No | Best for unordered, no dupes |
| `List` + `@OrderColumn` | Allowed | Preserved | Order index column | Supports positional access |
| `List` + `@OrderBy` | Allowed | DB order | No | Sorted on read, not stored |
| `Map` | Key uniqueness | By key | Key column(s) | Most complex join |

---

## @MappedSuperclass
Not an entity, not queryable — just shares mapping annotations with subclasses.

```java
@MappedSuperclass
public abstract class Auditable {
    @Column(name = "created_at")
    @Temporal(TemporalType.TIMESTAMP)
    private Date createdAt;

    @Column(name = "updated_at")
    @Temporal(TemporalType.TIMESTAMP)
    private Date updatedAt;
}

@Entity
public class Employee extends Auditable {
    @Id private Long id;
    // inherits createdAt / updatedAt columns
}
```

---

## Common ORM Mistakes

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| `@Enumerated(ORDINAL)` | Breaks if enum values reordered | Use `EnumType.STRING` |
| Missing `@CollectionTable` | Provider uses a default name (may conflict) | Always specify explicitly |
| `@ElementCollection` on `Map` without `@MapKeyColumn` | Provider may use "KEY" as default column name | Specify `@MapKeyColumn` |
| `@Lob` on `String` expecting VARCHAR | Gets CLOB/TEXT instead | Drop `@Lob` for short strings |
| `@OrderColumn` on bidirectional `@OneToMany` | Owner side must be the `List` side | Put `@OrderColumn` on non-`mappedBy` side |
