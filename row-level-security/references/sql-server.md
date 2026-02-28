# SQL Server Row-Level Security

## Table of Contents

- [Architecture](#architecture)
- [Creating Security Policies](#creating-security-policies)
- [Filter vs Block Predicates](#filter-vs-block-predicates)
- [Common Patterns](#common-patterns)
- [Performance](#performance)
- [MySQL Workarounds](#mysql-workarounds)

---

## Architecture

SQL Server RLS uses two components:
1. **Inline table-valued function** — the predicate logic (returns 1 for allowed rows)
2. **Security policy** — binds the function to table(s) as a filter or block predicate

```sql
-- 1. Create the predicate function
CREATE FUNCTION dbo.fn_tenant_predicate(@TenantId INT)
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN SELECT 1 AS result
  WHERE @TenantId = CAST(SESSION_CONTEXT(N'TenantId') AS INT)
     OR IS_MEMBER('db_owner') = 1;  -- admins bypass

-- 2. Create the security policy
CREATE SECURITY POLICY dbo.TenantPolicy
  ADD FILTER PREDICATE dbo.fn_tenant_predicate(TenantId) ON dbo.Orders,
  ADD BLOCK PREDICATE dbo.fn_tenant_predicate(TenantId) ON dbo.Orders,
  ADD FILTER PREDICATE dbo.fn_tenant_predicate(TenantId) ON dbo.Invoices,
  ADD BLOCK PREDICATE dbo.fn_tenant_predicate(TenantId) ON dbo.Invoices
WITH (STATE = ON);
```

## Filter vs Block Predicates

| Type | Behavior | Applied to |
|------|----------|------------|
| **FILTER** | Silently excludes rows from results | SELECT, UPDATE (which rows), DELETE (which rows) |
| **BLOCK** | Throws error if operation violates predicate | INSERT (AFTER INSERT), UPDATE (AFTER UPDATE, BEFORE UPDATE) |

```sql
-- Filter: user only sees their rows (silent exclusion)
ADD FILTER PREDICATE dbo.fn_user_predicate(UserId) ON dbo.Documents

-- Block AFTER INSERT: prevents inserting rows you wouldn't be able to read
ADD BLOCK PREDICATE dbo.fn_user_predicate(UserId) ON dbo.Documents AFTER INSERT

-- Block BEFORE UPDATE: prevents modifying rows you shouldn't access
ADD BLOCK PREDICATE dbo.fn_user_predicate(UserId) ON dbo.Documents BEFORE UPDATE

-- Block AFTER UPDATE: prevents updating a row to values that would be invisible
ADD BLOCK PREDICATE dbo.fn_user_predicate(UserId) ON dbo.Documents AFTER UPDATE
```

## Common Patterns

### Tenant isolation via SESSION_CONTEXT

```sql
-- Application sets context per request:
EXEC sp_set_session_context @key = N'TenantId', @value = 42, @read_only = 1;
-- @read_only = 1 prevents changing it within the session

-- Predicate function
CREATE FUNCTION dbo.fn_tenant_filter(@TenantId INT)
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN SELECT 1 AS result
  WHERE @TenantId = CAST(SESSION_CONTEXT(N'TenantId') AS INT);
```

### Role-based access

```sql
CREATE FUNCTION dbo.fn_role_predicate(@OwnerId INT, @IsPublic BIT)
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN SELECT 1 AS result
  WHERE @IsPublic = 1                                              -- public data
     OR @OwnerId = CAST(SESSION_CONTEXT(N'UserId') AS INT)        -- owner
     OR IS_MEMBER('Managers') = 1;                                  -- managers see all
```

### Disabling for maintenance

```sql
-- Temporarily disable
ALTER SECURITY POLICY dbo.TenantPolicy WITH (STATE = OFF);

-- Re-enable
ALTER SECURITY POLICY dbo.TenantPolicy WITH (STATE = ON);
```

## Performance

- Predicate functions execute for every row accessed — keep them simple
- Use `WITH SCHEMABINDING` on predicate functions (required and helps optimizer)
- `SESSION_CONTEXT` lookups are fast — prefer over table joins in predicates
- Avoid calling other functions, especially UDFs, within predicate functions
- For complex permission logic, pre-compute into a mapping table and join against it
- SQL Server can inline simple TVFs — verify with execution plans

### Known attack vectors (Red Gate research)

- **Side-channel via error messages**: Carefully crafted queries can reveal filtered row data through error messages (division by zero, type conversion). Mitigate by minimizing verbose error output in production.
- **Timing attacks**: Aggregate functions like `COUNT(*)` on filtered tables can leak information about row existence. Consider restricting aggregate access on sensitive tables.

---

## MySQL Workarounds

MySQL has **no native RLS**. Implement access control through these alternatives:

### Views as RLS substitute

```sql
-- Create a view that filters by current user
CREATE VIEW v_documents AS
SELECT * FROM documents
WHERE tenant_id = @current_tenant_id;

-- Application sets variable before queries:
SET @current_tenant_id = 42;
SELECT * FROM v_documents;
```

**Limitation**: Views are not security boundaries. Users with direct table access bypass them.

### Application-enforced via middleware

```python
# Every query goes through a middleware that injects tenant filter
class TenantMiddleware:
    def filter_query(self, query, tenant_id):
        return f"{query} WHERE tenant_id = {tenant_id}"
```

### MySQL on AWS — Virtual RLS

AWS published a pattern for Aurora MySQL using a combination of:
1. Database roles per tenant
2. Views with `CURRENT_USER()` checks
3. Stored procedures for controlled access
4. Trigger-based write validation

This is complex and fragile. If you need real RLS, migrate to PostgreSQL.

### Summary: MySQL vs PostgreSQL for RLS

| Feature | PostgreSQL | MySQL |
|---------|-----------|-------|
| Native RLS | Yes | No |
| Policy granularity | Per-operation (SELECT/INSERT/UPDATE/DELETE) | N/A |
| Enforcement | Database-level (cannot bypass) | Application-level (can bypass) |
| Performance | Optimized by query planner | View-based, limited optimization |
| Recommendation | Use for any multi-tenant or access-controlled data | Use application-level filtering or migrate |
