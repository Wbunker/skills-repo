# Querying — JPQL and Criteria API
*Chapters 9–10 — Pro JPA 2 in Java EE 8, Mike Keith*

## JPQL Overview (Ch 9)

JPQL operates on the **entity model**, not tables/columns:
- Class names and field names (Java names, not SQL names)
- `FROM Employee e` — `Employee` is the entity name (from `@Entity(name=…)` or class name)
- Queries are portable across databases

---

## SELECT Basics

### Simple select
```java
List<Employee> result =
    em.createQuery("SELECT e FROM Employee e", Employee.class)
      .getResultList();
```

### With WHERE clause
```java
TypedQuery<Employee> q = em.createQuery(
    "SELECT e FROM Employee e WHERE e.salary > :minSalary", Employee.class);
q.setParameter("minSalary", new BigDecimal("50000"));
List<Employee> employees = q.getResultList();
```

### Positional parameters (legacy style)
```java
em.createQuery("SELECT e FROM Employee e WHERE e.name = ?1 AND e.dept.name = ?2",
               Employee.class)
  .setParameter(1, "Alice")
  .setParameter(2, "Engineering")
  .getResultList();
```

---

## Projection and Scalar Queries

### Single attribute
```java
List<String> names =
    em.createQuery("SELECT e.name FROM Employee e", String.class)
      .getResultList();
```

### Constructor expression (DTO projection)
```java
List<EmployeeSummary> result = em.createQuery(
    "SELECT NEW com.example.EmployeeSummary(e.id, e.name, e.department.name) " +
    "FROM Employee e", EmployeeSummary.class)
  .getResultList();
```
`EmployeeSummary` must have a matching constructor.

### Multiple values (Object[])
```java
List<Object[]> rows =
    em.createQuery("SELECT e.name, e.salary FROM Employee e").getResultList();
for (Object[] row : rows) {
    String name   = (String)     row[0];
    BigDecimal sal = (BigDecimal) row[1];
}
```

---

## Path Expressions and Navigation

```jpql
-- Single-valued association path
SELECT e.department.name FROM Employee e

-- Collection-valued path — must use JOIN, not dot navigation
SELECT p.name FROM Employee e JOIN e.projects p   -- correct
SELECT e.projects.name FROM Employee e            -- ILLEGAL
```

---

## JOIN Types

```jpql
-- Inner join (implicit — entities without dept are excluded)
SELECT e FROM Employee e JOIN e.department d WHERE d.name = 'Engineering'

-- Left outer join (include employees with no department)
SELECT e FROM Employee e LEFT JOIN e.department d WHERE d.name = 'Engineering' OR d IS NULL

-- Fetch join — load association eagerly in this query (no alias allowed in WHERE)
SELECT e FROM Employee e JOIN FETCH e.department
SELECT e FROM Employee e LEFT JOIN FETCH e.projects

-- Multiple fetch joins (use carefully; can cause cartesian product)
SELECT DISTINCT e FROM Employee e
    JOIN FETCH e.department
    LEFT JOIN FETCH e.phoneNumbers
```

**JOIN FETCH rules:**
- Cannot use the fetched alias in WHERE/ORDER BY in JPA 2.1 (provider-specific extension in some impls)
- Use `DISTINCT` or `LinkedHashSet` return type to deduplicate when joining collections

---

## Aggregate Functions

```jpql
SELECT COUNT(e)          FROM Employee e
SELECT COUNT(DISTINCT e.department) FROM Employee e
SELECT AVG(e.salary)     FROM Employee e
SELECT MAX(e.salary)     FROM Employee e
SELECT MIN(e.salary)     FROM Employee e
SELECT SUM(e.salary)     FROM Employee e WHERE e.department.name = 'Sales'
```

### GROUP BY and HAVING
```jpql
SELECT d.name, AVG(e.salary)
FROM Employee e JOIN e.department d
GROUP BY d.name
HAVING AVG(e.salary) > 60000
ORDER BY AVG(e.salary) DESC
```

---

## Subqueries

```jpql
-- Employees earning more than company average
SELECT e FROM Employee e
WHERE e.salary > (SELECT AVG(e2.salary) FROM Employee e2)

-- Employees who are on at least one project (EXISTS)
SELECT e FROM Employee e
WHERE EXISTS (SELECT p FROM e.projects p)

-- Employees not assigned to any project (NOT EXISTS)
SELECT e FROM Employee e
WHERE NOT EXISTS (SELECT p FROM e.projects p)

-- IN subquery
SELECT e FROM Employee e
WHERE e.department IN (
    SELECT d FROM Department d WHERE d.budget > 100000
)

-- ALL / ANY / SOME
SELECT e FROM Employee e
WHERE e.salary > ALL (SELECT e2.salary FROM Employee e2 WHERE e2.department.name = 'Sales')
```

---

## Named Queries

Define at the entity class:
```java
@Entity
@NamedQuery(name = "Employee.findByDept",
            query = "SELECT e FROM Employee e WHERE e.department.name = :deptName ORDER BY e.name")
@NamedQuery(name = "Employee.findHighEarners",
            query = "SELECT e FROM Employee e WHERE e.salary > :minSal")
public class Employee { ... }

// Multiple named queries:
@NamedQueries({
    @NamedQuery(name = "Employee.findAll",
                query = "SELECT e FROM Employee e"),
    @NamedQuery(name = "Employee.findByName",
                query = "SELECT e FROM Employee e WHERE e.name = :name")
})
```

Execute:
```java
List<Employee> engineers =
    em.createNamedQuery("Employee.findByDept", Employee.class)
      .setParameter("deptName", "Engineering")
      .getResultList();
```

---

## Pagination

```java
List<Employee> page =
    em.createQuery("SELECT e FROM Employee e ORDER BY e.id", Employee.class)
      .setFirstResult(20)   // 0-based offset
      .setMaxResults(10)    // page size
      .getResultList();
```

---

## Bulk UPDATE and DELETE

Bypass persistence context — **execute within own transaction, then clear PC**.

```java
// Bulk update
int updated = em.createQuery(
    "UPDATE Employee e SET e.salary = e.salary * 1.1 WHERE e.department.name = :dept")
  .setParameter("dept", "Engineering")
  .executeUpdate();

// Bulk delete
int deleted = em.createQuery(
    "DELETE FROM PhoneNumber p WHERE p.employee.id = :empId")
  .setParameter("empId", 42L)
  .executeUpdate();

em.clear();   // required: managed entities are now stale
```

**Pitfalls:**
- Managed entities in the PC are not updated by bulk ops — always `clear()` after
- Cascade operations do NOT apply to bulk deletes
- Check FK constraints before bulk delete (delete children before parents)

---

## Advanced Queries — Criteria API (Ch 10)

The Criteria API is type-safe and refactor-safe. It mirrors JPQL structure programmatically.

### Basic Criteria Query
```java
CriteriaBuilder cb = em.getCriteriaBuilder();
CriteriaQuery<Employee> cq = cb.createQuery(Employee.class);
Root<Employee> emp = cq.from(Employee.class);

cq.select(emp)
  .where(cb.gt(emp.get("salary"), 50000));

List<Employee> result = em.createQuery(cq).getResultList();
```

### Type-Safe Metamodel
Generate with Hibernate's annotation processor or manually:
```java
// Generated class Employee_
@StaticMetamodel(Employee.class)
public class Employee_ {
    public static volatile SingularAttribute<Employee, Long>       id;
    public static volatile SingularAttribute<Employee, String>     name;
    public static volatile SingularAttribute<Employee, BigDecimal> salary;
    public static volatile SingularAttribute<Employee, Department> department;
    public static volatile CollectionAttribute<Employee, Project>  projects;
}

// Usage
cq.where(cb.gt(emp.get(Employee_.salary), 50000));
```

### Joins with Criteria API
```java
Root<Employee> emp = cq.from(Employee.class);
Join<Employee, Department> dept = emp.join("department");        // inner join
Join<Employee, Department> dept = emp.join("department", JoinType.LEFT);  // left join

// Fetch join
Fetch<Employee, Department> f = emp.fetch("department");
Fetch<Employee, Project>    p = emp.fetch("projects", JoinType.LEFT);
```

### Predicates / WHERE
```java
Predicate highSalary = cb.gt(emp.get(Employee_.salary), 60000);
Predicate inEngineering = cb.equal(dept.get("name"), "Engineering");

cq.where(cb.and(highSalary, inEngineering));

// OR
cq.where(cb.or(highSalary, inEngineering));

// NOT
cq.where(cb.not(highSalary));

// LIKE
cq.where(cb.like(emp.get(Employee_.name), "A%"));

// IN
cq.where(emp.get(Employee_.name).in("Alice", "Bob", "Carol"));

// BETWEEN
cq.where(cb.between(emp.get(Employee_.salary),
         new BigDecimal("40000"), new BigDecimal("80000")));

// IS NULL / IS NOT NULL
cq.where(cb.isNull(emp.get("manager")));
```

### ORDER BY, GROUP BY, HAVING
```java
cq.orderBy(cb.desc(emp.get(Employee_.salary)),
           cb.asc(emp.get(Employee_.name)));

// Aggregate
CriteriaQuery<Object[]> agq = cb.createQuery(Object[].class);
Root<Employee> e = agq.from(Employee.class);
Join<Employee, Department> d = e.join("department");
agq.multiselect(d.get("name"), cb.avg(e.get(Employee_.salary)));
agq.groupBy(d.get("name"));
agq.having(cb.gt(cb.avg(e.get(Employee_.salary)), 50000.0));
```

### Dynamic Criteria Queries (main advantage over JPQL)
```java
public List<Employee> search(String name, BigDecimal minSalary, String deptName) {
    CriteriaBuilder cb = em.getCriteriaBuilder();
    CriteriaQuery<Employee> cq = cb.createQuery(Employee.class);
    Root<Employee> emp = cq.from(Employee.class);

    List<Predicate> predicates = new ArrayList<>();
    if (name != null)       predicates.add(cb.like(emp.get("name"), "%" + name + "%"));
    if (minSalary != null)  predicates.add(cb.ge(emp.get("salary"), minSalary));
    if (deptName != null) {
        Join<Employee, Department> d = emp.join("department");
        predicates.add(cb.equal(d.get("name"), deptName));
    }

    cq.where(predicates.toArray(new Predicate[0]));
    return em.createQuery(cq).getResultList();
}
```

---

## Native SQL Queries

```java
// Plain result
List<Object[]> rows =
    em.createNativeQuery("SELECT id, name FROM emp WHERE dept_id = ?")
      .setParameter(1, 10)
      .getResultList();

// Map to entity
List<Employee> emps = em.createNativeQuery(
    "SELECT * FROM emp WHERE dept_id = :deptId", Employee.class)
  .setParameter("deptId", 10)
  .getResultList();

// Named native query
@NamedNativeQuery(
    name = "Employee.nativeByDept",
    query = "SELECT * FROM emp WHERE dept_id = :deptId",
    resultClass = Employee.class
)
```

---

## Query Hints

Hints are provider-specific. Common Hibernate hints:
```java
em.createQuery("SELECT e FROM Employee e", Employee.class)
  .setHint("org.hibernate.readOnly", true)                // no dirty checking
  .setHint("org.hibernate.cacheable", true)               // use L2 query cache
  .setHint("javax.persistence.fetchgraph", graph)         // entity graph
  .getResultList();
```

---

## JPQL Quick-Reference Cheatsheet

```
SELECT <select_expr> FROM <from_clause>
  [JOIN [FETCH] <path> [AS <alias>]]
  [WHERE <condition_expr>]
  [GROUP BY <group_by_expr>]
  [HAVING <condition_expr>]
  [ORDER BY <orderby_expr> [ASC|DESC]]

Comparison: =, <>, <, >, <=, >=, BETWEEN, LIKE, IN, IS NULL, IS EMPTY, MEMBER OF
Logic:       AND, OR, NOT
Functions:   CONCAT, SUBSTRING, TRIM, LOWER, UPPER, LENGTH, LOCATE,
             ABS, SQRT, MOD, SIZE, INDEX,
             CURRENT_DATE, CURRENT_TIME, CURRENT_TIMESTAMP,
             CASE WHEN … THEN … ELSE … END,
             COALESCE(…), NULLIF(a, b), TYPE(e)
```
