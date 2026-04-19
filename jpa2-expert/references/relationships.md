# Relationships, Inheritance, and Embedded Ids
*Chapters 6–8 — Pro JPA 2 in Java EE 8, Mike Keith*

## Entity Relationships (Ch 6)

### Key Concepts
- **Owning side**: the entity whose table holds the foreign key (or the join table is defined on). Controls how JPA persists the relationship.
- **Inverse side**: annotated with `mappedBy = "<field on owning side>"`. Read-only from a persistence standpoint.
- **Always synchronize both sides** of a bidirectional relationship in Java code; JPA reads the owning side for SQL.

---

### @ManyToOne — Most Common Relationship
```java
@Entity
public class Employee {
    @Id private Long id;

    @ManyToOne(fetch = FetchType.LAZY,
               optional = false)          // NOT NULL FK
    @JoinColumn(name = "dept_id",
                nullable = false)
    private Department department;
}
```

---

### @OneToMany — Bidirectional (Preferred)
```java
@Entity
public class Department {
    @Id private Long id;

    @OneToMany(mappedBy = "department",   // "department" is the field on Employee
               cascade = CascadeType.ALL,
               orphanRemoval = true,
               fetch = FetchType.LAZY)
    private List<Employee> employees = new ArrayList<>();

    // Helper to keep both sides in sync
    public void addEmployee(Employee e) {
        employees.add(e);
        e.setDepartment(this);
    }
    public void removeEmployee(Employee e) {
        employees.remove(e);
        e.setDepartment(null);
    }
}
```

### @OneToMany — Unidirectional (with FK in child table)
```java
@OneToMany
@JoinColumn(name = "dept_id")    // FK in EMPLOYEE table; no mappedBy
private List<Employee> employees;
```
Without `@JoinColumn`, JPA defaults to a join table — usually undesirable for unidirectional one-to-many.

---

### @OneToOne

#### FK in this table (owning)
```java
@Entity
public class Employee {
    @OneToOne(fetch = FetchType.LAZY,
              cascade = CascadeType.ALL,
              orphanRemoval = true)
    @JoinColumn(name = "address_id", unique = true)
    private Address address;
}
```

#### FK in other table (inverse)
```java
@Entity
public class Address {
    @OneToOne(mappedBy = "address")
    private Employee employee;
}
```

#### Shared primary key (PK = FK)
```java
@Entity
public class EmployeeDetails {
    @Id private Long id;   // same value as Employee.id

    @OneToOne
    @MapsId                // id field maps to the FK
    @JoinColumn(name = "id")
    private Employee employee;
}
```

---

### @ManyToMany

```java
@Entity
public class Employee {
    @ManyToMany
    @JoinTable(name = "emp_project",
               joinColumns        = @JoinColumn(name = "emp_id"),
               inverseJoinColumns = @JoinColumn(name = "proj_id"))
    private Set<Project> projects = new HashSet<>();
}

@Entity
public class Project {
    @ManyToMany(mappedBy = "projects")   // "projects" is the field on Employee
    private Set<Employee> employees = new HashSet<>();
}
```

**When the join table needs extra columns:** replace `@ManyToMany` with an intermediary entity:
```java
@Entity
public class Participation {
    @Id @GeneratedValue private Long id;
    @ManyToOne @JoinColumn(name = "emp_id")  private Employee employee;
    @ManyToOne @JoinColumn(name = "proj_id") private Project  project;
    private String role;
    private LocalDate joinedDate;
}
```

---

### Cascade Types
```java
cascade = CascadeType.PERSIST    // persist child when parent is persisted
cascade = CascadeType.MERGE      // merge child when parent is merged
cascade = CascadeType.REMOVE     // delete child when parent is removed
cascade = CascadeType.REFRESH    // refresh child when parent is refreshed
cascade = CascadeType.DETACH     // detach child when parent is detached
cascade = CascadeType.ALL        // all of the above
```
**Never cascade REMOVE on a @ManyToMany** — removing one side would delete all related entities on the other side.

### orphanRemoval vs. CascadeType.REMOVE
| | `orphanRemoval = true` | `CascadeType.REMOVE` |
|--|--|--|
| Triggered by | Removing entity from collection | `em.remove(parent)` |
| Typical use | Parent "owns" children (composition) | Parent deleted → children deleted |
| Works on | `@OneToMany`, `@OneToOne` | All relationship types |

---

### Fetch Types
| Default | Type | Behavior |
|---------|------|----------|
| `@ManyToOne`, `@OneToOne` | `EAGER` | Loaded immediately with parent |
| `@OneToMany`, `@ManyToMany` | `LAZY` | Loaded on first access (proxy/collection) |

**Best practice:** use `LAZY` everywhere; fetch eagerly via JPQL JOIN FETCH or entity graphs when needed. Changing default to EAGER causes N+1 and over-fetching.

```java
// EAGER by default — change to LAZY:
@ManyToOne(fetch = FetchType.LAZY)
private Department department;
```

---

## Inheritance Mapping (Ch 7)

### SINGLE_TABLE — Default
All classes in the hierarchy share one table. Discriminator column identifies the subtype.

```java
@Entity
@Inheritance(strategy = InheritanceType.SINGLE_TABLE)
@DiscriminatorColumn(name = "emp_type", discriminatorType = DiscriminatorType.STRING)
public abstract class Employee {
    @Id @GeneratedValue private Long id;
    private String name;
}

@Entity
@DiscriminatorValue("FT")
public class FullTimeEmployee extends Employee {
    private BigDecimal salary;       // NULL for part-time rows
}

@Entity
@DiscriminatorValue("PT")
public class PartTimeEmployee extends Employee {
    private Float hourlyRate;        // NULL for full-time rows
}
```
Table: `EMPLOYEE(id, name, emp_type, salary, hourly_rate)` — subtype columns nullable.

### JOINED — Normalized
Each class has its own table; subclass tables FK back to superclass table.

```java
@Entity
@Inheritance(strategy = InheritanceType.JOINED)
public abstract class Employee {
    @Id @GeneratedValue private Long id;
    private String name;
}

@Entity
@PrimaryKeyJoinColumn(name = "ft_emp_id")   // optional; defaults to superclass PK name
public class FullTimeEmployee extends Employee {
    private BigDecimal salary;
}
```
Tables: `EMPLOYEE(id, name)`, `FULLTIMEEMPLOYEE(ft_emp_id FK → employee.id, salary)`

### TABLE_PER_CLASS — Concrete Tables Only
Each concrete class has a complete table (no shared table, no FK joins). Polymorphic queries require UNION ALL.

```java
@Entity
@Inheritance(strategy = InheritanceType.TABLE_PER_CLASS)
public abstract class Employee {
    @Id @GeneratedValue(strategy = GenerationType.TABLE)  // IDENTITY/SEQUENCE won't work
    private Long id;
    private String name;
}
```
Tables: `FULLTIMEEMPLOYEE(id, name, salary)`, `PARTTIMEEMPLOYEE(id, name, hourly_rate)`.

**Note:** IDENTITY generation doesn't work with TABLE_PER_CLASS because the same id must be unique across all concrete tables. Use TABLE or SEQUENCE.

### @MappedSuperclass (not an inheritance strategy)
The superclass is not an entity and cannot be queried. Just shares annotations.
```java
@MappedSuperclass
public abstract class BaseEntity {
    @Id @GeneratedValue private Long id;
    @Version private int version;
}
```

---

## Embedded Objects (Ch 8)

### @Embeddable / @Embedded (recap + advanced)
Already covered in `orm-basics.md`. Key addition: embeddables can themselves contain relationships.

```java
@Embeddable
public class ContactInfo {
    private String email;
    @ManyToOne
    @JoinColumn(name = "country_id")
    private Country country;
}
```

### Compound Primary Keys with @Embeddable: @EmbeddedId

```java
@Embeddable
public class ProjectAssignmentId implements Serializable {
    @Column(name = "emp_id")  private Long employeeId;
    @Column(name = "proj_id") private Long projectId;
    // equals() and hashCode() required
}

@Entity
public class ProjectAssignment {
    @EmbeddedId
    private ProjectAssignmentId id;

    @MapsId("employeeId")          // links EmbeddedId field to FK
    @ManyToOne @JoinColumn(name = "emp_id")
    private Employee employee;

    @MapsId("projectId")
    @ManyToOne @JoinColumn(name = "proj_id")
    private Project project;

    private String role;
}
```

### @IdClass (alternative to @EmbeddedId)
Keeps PK fields in the entity class itself; separate id class for `em.find()`.

```java
public class ProjectAssignmentId implements Serializable {
    private Long employeeId;
    private Long projectId;
    // equals() and hashCode() required
}

@Entity
@IdClass(ProjectAssignmentId.class)
public class ProjectAssignment {
    @Id
    @ManyToOne @JoinColumn(name = "emp_id")
    private Employee employee;   // field name must match ProjectAssignmentId.employeeId

    @Id
    @ManyToOne @JoinColumn(name = "proj_id")
    private Project project;

    private String role;
}
```

Finding by id:
```java
ProjectAssignmentId pk = new ProjectAssignmentId();
pk.setEmployeeId(1L);
pk.setProjectId(2L);
ProjectAssignment pa = em.find(ProjectAssignment.class, pk);
```

### @EmbeddedId vs @IdClass

| | `@EmbeddedId` | `@IdClass` |
|--|--|--|
| PK fields location | Embedded class | Entity class (repeated in id class) |
| JPQL access | `WHERE a.id.employeeId = :eid` | `WHERE a.employeeId = :eid` |
| Readability | Cleaner for complex PKs | More natural field access in JPQL |
| `@MapsId` needed? | Yes when FK fields compose PK | No (fields are directly in entity) |

---

## Relationship Best Practices

1. **Default to LAZY fetch** on all relationships; only fetch eagerly when needed via JOIN FETCH.
2. **Synchronize both sides** of bidirectional relationships using helper methods (`addChild()` / `removeChild()`).
3. **Use `orphanRemoval = true`** only for "composition" relationships (child cannot exist without parent).
4. **Avoid cascade REMOVE on @ManyToMany** — it will delete the entities on the other side.
5. **Add `@JoinColumn` on unidirectional @OneToMany** to prevent an unwanted join table.
6. **`equals()`/`hashCode()`** on entities: use business key (natural id) or only the `id` after `persist()`. Do not rely on default identity-based `equals()` for entities stored in sets.
