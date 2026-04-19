# JPA Foundations
*Chapters 1–3 — Pro JPA 2 in Java EE 8, Mike Keith*

## What JPA Is

JPA (Java Persistence API / Jakarta Persistence) is the standard ORM specification for Java. It defines:
- How Java objects (entities) map to relational database tables
- A query language (JPQL) independent of SQL dialects
- APIs for managing entity lifecycle within transactions
- A portable unit of work: the **persistence context**

JPA is a specification; you always run against a **provider** implementation: Hibernate, EclipseLink, OpenJPA, etc. Behavior beyond the spec is provider-specific.

**Package:** `javax.persistence.*` (JPA 2.x / Java EE) → `jakarta.persistence.*` (Jakarta EE 9+)

---

## Getting Started

### Minimum dependencies (Maven, Java EE 8)
```xml
<dependency>
  <groupId>javax</groupId>
  <artifactId>javaee-api</artifactId>
  <version>8.0.1</version>
  <scope>provided</scope>
</dependency>
<!-- Or standalone with Hibernate -->
<dependency>
  <groupId>org.hibernate</groupId>
  <artifactId>hibernate-core</artifactId>
  <version>5.6.x.Final</version>
</dependency>
```

### Minimal Entity
```java
import javax.persistence.*;

@Entity
@Table(name = "employee")          // optional; defaults to class name
public class Employee {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "first_name", nullable = false, length = 50)
    private String firstName;

    // getters / setters ...
}
```

### Minimal persistence.xml
```xml
<persistence xmlns="http://xmlns.jcp.org/xml/ns/persistence" version="2.2">
  <persistence-unit name="myPU" transaction-type="JTA">
    <jta-data-source>java:app/jdbc/MyDS</jta-data-source>
    <exclude-unlisted-classes>false</exclude-unlisted-classes>
    <properties>
      <property name="javax.persistence.schema-generation.database.action"
                value="none"/>
    </properties>
  </persistence-unit>
</persistence>
```

For **Java SE** (resource-local):
```xml
<persistence-unit name="myPU" transaction-type="RESOURCE_LOCAL">
  <provider>org.hibernate.jpa.HibernatePersistenceProvider</provider>
  <class>com.example.Employee</class>
  <properties>
    <property name="javax.persistence.jdbc.driver"   value="org.h2.Driver"/>
    <property name="javax.persistence.jdbc.url"      value="jdbc:h2:mem:test"/>
    <property name="javax.persistence.jdbc.user"     value="sa"/>
    <property name="javax.persistence.jdbc.password" value=""/>
  </properties>
</persistence-unit>
```

---

## EntityManagerFactory and EntityManager

### In a Java EE Container (JTA)
```java
@PersistenceContext(unitName = "myPU")
private EntityManager em;   // container-managed, transaction-scoped

@PersistenceUnit(unitName = "myPU")
private EntityManagerFactory emf;  // injected factory if you need app-managed EM
```

### In Java SE (resource-local)
```java
EntityManagerFactory emf =
    Persistence.createEntityManagerFactory("myPU");

EntityManager em = emf.createEntityManager();
EntityTransaction tx = em.getTransaction();
try {
    tx.begin();
    // ... work ...
    tx.commit();
} catch (Exception e) {
    tx.rollback();
} finally {
    em.close();
}
emf.close();   // on application shutdown
```

### Container-Managed vs. Application-Managed EM

| | Container-Managed | Application-Managed |
|--|--|--|
| Creation | `@PersistenceContext` injection | `emf.createEntityManager()` |
| Transaction | JTA (auto-propagated) | Resource-local or JTA manual |
| Lifecycle | Container creates/closes per tx | Application calls `em.close()` |
| PC scope | Transaction-scoped (default) or extended | Tied to EM lifetime |
| Typical use | EJB / CDI beans in EE container | Java SE, tests, fine-grained control |

### Extended Persistence Context
An extended PC lives beyond a single transaction (typically a stateful EJB):
```java
@PersistenceContext(type = PersistenceContextType.EXTENDED)
private EntityManager em;
```
Entities remain MANAGED across method calls. Useful for long-running conversations. Changes flush to DB on the next commit.

---

## Entity States and Lifecycle

```
NEW ──── em.persist() ────► MANAGED
  ◄──── (not committed)       │    │
                           flush/  em.remove()
                          commit      │
                               │   REMOVED ──── commit ────► deleted in DB
                               │
                           em.detach() / em.close() / em.clear()
                               │
                           DETACHED ──── em.merge() ────► MANAGED (copy)
```

| State | Identity | In PC | In DB |
|-------|----------|-------|-------|
| **NEW** | No PK or unmanaged | No | No |
| **MANAGED** | Has PK, tracked | Yes | Yes (after flush) |
| **DETACHED** | Has PK, not tracked | No | Yes |
| **REMOVED** | Has PK, marked deleted | Yes | Until commit |

---

## Enterprise Application Integration (Ch 3)

### Injecting EntityManager in CDI/EJB
```java
@Stateless
public class EmployeeService {

    @PersistenceContext
    private EntityManager em;

    public Employee findById(Long id) {
        return em.find(Employee.class, id);
    }

    public void save(Employee e) {
        em.persist(e);
    }

    public List<Employee> findAll() {
        return em.createQuery("SELECT e FROM Employee e", Employee.class)
                 .getResultList();
    }
}
```

### Transaction Propagation
With `@Stateless` EJBs, the transaction is required by default (`REQUIRED`). If a service calls another service, the same persistence context propagates. Changes made in one EJB are visible to another EJB called in the same transaction.

```java
// Both services share the same persistence context within one transaction
@Stateless
public class DepartmentService {
    @EJB EmployeeService empService;
    @PersistenceContext EntityManager em;

    public void reorganize() {
        Department d = em.find(Department.class, 1L);
        empService.transferAll(d);  // same tx, same PC
    }
}
```

### DAO Pattern with JPA
```java
@Stateless
public class EmployeeRepository {
    @PersistenceContext EntityManager em;

    public void create(Employee e) { em.persist(e); }
    public Employee read(Long id)  { return em.find(Employee.class, id); }
    public Employee update(Employee e) { return em.merge(e); }
    public void delete(Long id)    { em.remove(em.find(Employee.class, id)); }

    public List<Employee> findByDept(String dept) {
        return em.createNamedQuery("Employee.byDept", Employee.class)
                 .setParameter("dept", dept)
                 .getResultList();
    }
}
```

---

## Common Startup Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Wrong persistence-unit name | `IllegalArgumentException` on bootstrap | Match name in `@PersistenceContext` and persistence.xml |
| No `<jta-data-source>` in EE | `TransactionRequiredException` | Add JNDI datasource ref |
| Forgetting `@Table` or wrong schema | Queries fail or create wrong table | Add `@Table(name=…, schema=…)` |
| Using `em` outside transaction | `TransactionRequiredException` on persist/merge/remove | Ensure method is `@Transactional` or inside `tx.begin()` |
| Not closing Java SE EM | Connection leak | Always `em.close()` in finally block |
