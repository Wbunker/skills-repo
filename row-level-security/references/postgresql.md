# PostgreSQL Row-Level Security

## Table of Contents

- [Enabling RLS](#enabling-rls)
- [Policy Syntax](#policy-syntax)
- [Permissive vs Restrictive](#permissive-vs-restrictive)
- [Session Variables for Tenant Context](#session-variables-for-tenant-context)
- [Common Policy Patterns](#common-policy-patterns)
- [Helper Functions](#helper-functions)
- [Performance Optimization](#performance-optimization)
- [Auditing Policies](#auditing-policies)

---

## Enabling RLS

```sql
-- Enable RLS on a table
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- CRITICAL: Force RLS on table owner too (prevents owner bypass)
ALTER TABLE documents FORCE ROW LEVEL SECURITY;
```

Without `FORCE`, the table owner (typically the role that created it) bypasses all policies. Superusers always bypass RLS.

## Policy Syntax

```sql
CREATE POLICY policy_name ON table_name
  [AS { PERMISSIVE | RESTRICTIVE }]  -- default: PERMISSIVE
  [FOR { ALL | SELECT | INSERT | UPDATE | DELETE }]
  [TO role_name [, ...]]  -- default: PUBLIC
  [USING (select_filter_expression)]  -- which existing rows are visible
  [WITH CHECK (write_filter_expression)];  -- which new/updated rows are allowed
```

**USING** = read filter (SELECT, UPDATE's WHERE, DELETE's WHERE)
**WITH CHECK** = write filter (INSERT's new row, UPDATE's new row)

For `INSERT`: only `WITH CHECK` applies (no existing rows to filter).
For `SELECT`: only `USING` applies.
For `UPDATE`/`DELETE`: `USING` filters which rows can be targeted, `WITH CHECK` validates the new values.

Always specify both `USING` and `WITH CHECK` on `UPDATE` policies to prevent users from modifying a row to reassign it to another user.

## Permissive vs Restrictive

```sql
-- PERMISSIVE policies are ORed together — any matching policy grants access
CREATE POLICY user_sees_own ON documents
  AS PERMISSIVE FOR SELECT TO app_user
  USING (user_id = current_setting('app.current_user_id')::uuid);

CREATE POLICY user_sees_shared ON documents
  AS PERMISSIVE FOR SELECT TO app_user
  USING (id IN (SELECT document_id FROM shares WHERE user_id = current_setting('app.current_user_id')::uuid));

-- RESTRICTIVE policies are ANDed — ALL must pass (in addition to at least one PERMISSIVE)
CREATE POLICY tenant_isolation ON documents
  AS RESTRICTIVE FOR ALL TO app_user
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
  WITH CHECK (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

**Pattern**: Use one RESTRICTIVE policy for tenant isolation (always enforced), then PERMISSIVE policies for role-based access within the tenant.

Evaluation: `(any PERMISSIVE passes) AND (all RESTRICTIVE pass)` = row visible.

## Session Variables for Tenant Context

```sql
-- Set at the start of each request (transaction-scoped for pooled connections)
SELECT set_config('app.current_user_id', 'user-uuid', true);
SELECT set_config('app.current_tenant_id', 'tenant-uuid', true);
SELECT set_config('app.current_role', 'admin', true);

-- Use in policies
CREATE POLICY tenant_isolation ON orders
  AS RESTRICTIVE FOR ALL TO app_user
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
  WITH CHECK (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

`set_config(name, value, is_local)`: when `is_local = true`, the setting is scoped to the current transaction and auto-clears on `COMMIT`/`ROLLBACK`. Always use `true` with connection pooling.

## Common Policy Patterns

### User-owned data

```sql
CREATE POLICY users_own_data ON profiles
  FOR ALL TO app_user
  USING (id = current_setting('app.current_user_id')::uuid)
  WITH CHECK (id = current_setting('app.current_user_id')::uuid);
```

### Team/org membership

```sql
CREATE POLICY team_access ON projects
  FOR SELECT TO app_user
  USING (
    team_id IN (
      SELECT team_id FROM team_members
      WHERE user_id = current_setting('app.current_user_id')::uuid
    )
  );
```

### Role-based within tenant

```sql
CREATE POLICY admin_full_access ON orders
  AS PERMISSIVE FOR ALL TO app_user
  USING (
    tenant_id = current_setting('app.current_tenant_id')::uuid
    AND current_setting('app.current_role') = 'admin'
  )
  WITH CHECK (
    tenant_id = current_setting('app.current_tenant_id')::uuid
    AND current_setting('app.current_role') = 'admin'
  );

CREATE POLICY user_own_orders ON orders
  AS PERMISSIVE FOR SELECT TO app_user
  USING (
    tenant_id = current_setting('app.current_tenant_id')::uuid
    AND user_id = current_setting('app.current_user_id')::uuid
  );
```

### Public read, authenticated write

```sql
CREATE POLICY public_read ON posts
  FOR SELECT TO PUBLIC
  USING (published = true);

CREATE POLICY owner_write ON posts
  FOR ALL TO app_user
  USING (author_id = current_setting('app.current_user_id')::uuid)
  WITH CHECK (author_id = current_setting('app.current_user_id')::uuid);
```

### Soft-delete protection

```sql
CREATE POLICY hide_deleted ON records
  AS RESTRICTIVE FOR SELECT TO app_user
  USING (deleted_at IS NULL);
```

## Helper Functions

Mark helper functions as `STABLE` (not `VOLATILE`) so the planner can optimize them:

```sql
CREATE OR REPLACE FUNCTION current_user_id()
RETURNS uuid
LANGUAGE sql
STABLE
AS $$
  SELECT current_setting('app.current_user_id')::uuid;
$$;

CREATE OR REPLACE FUNCTION current_tenant_id()
RETURNS uuid
LANGUAGE sql
STABLE
AS $$
  SELECT current_setting('app.current_tenant_id')::uuid;
$$;

-- Use in policies for cleaner syntax
CREATE POLICY tenant_isolation ON orders
  AS RESTRICTIVE FOR ALL TO app_user
  USING (tenant_id = current_tenant_id())
  WITH CHECK (tenant_id = current_tenant_id());
```

**Do not** pass row data into helper functions — this prevents the planner from pushing predicates down and forces per-row evaluation.

## Performance Optimization

### Index every policy column

```sql
-- For tenant_id policies
CREATE INDEX idx_orders_tenant ON orders (tenant_id);

-- For composite lookups
CREATE INDEX idx_orders_tenant_user ON orders (tenant_id, user_id);

-- For membership subqueries
CREATE INDEX idx_team_members_user ON team_members (user_id, team_id);

-- For expression-based policies (case-insensitive email)
CREATE INDEX idx_users_email_lower ON users (LOWER(email));
```

### Measure overhead

```sql
-- With RLS
SET LOCAL role = 'app_user';
SET LOCAL app.current_tenant_id = 'test-tenant';
EXPLAIN ANALYZE SELECT * FROM orders WHERE status = 'active';

-- Without RLS (compare)
RESET role;
EXPLAIN ANALYZE SELECT * FROM orders WHERE status = 'active';
```

Look for sequential scans in the policy predicates — these indicate missing indexes.

### Materialized views for complex permissions

```sql
-- Instead of complex subquery in every policy
CREATE MATERIALIZED VIEW user_accessible_projects AS
SELECT DISTINCT p.id AS project_id, tm.user_id
FROM projects p
JOIN team_members tm ON tm.team_id = p.team_id;

CREATE UNIQUE INDEX ON user_accessible_projects (project_id, user_id);

-- Refresh periodically or via trigger
REFRESH MATERIALIZED VIEW CONCURRENTLY user_accessible_projects;
```

## Auditing Policies

```sql
-- List all policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- Find tables with RLS enabled but no policies (dangerous — blocks all access)
SELECT c.relname
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relrowsecurity = true
  AND n.nspname = 'public'
  AND NOT EXISTS (
    SELECT 1 FROM pg_policies p WHERE p.tablename = c.relname AND p.schemaname = 'public'
  );

-- Find tables WITHOUT RLS that probably should have it
SELECT tablename FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
  AND tablename NOT IN (SELECT tablename FROM pg_policies WHERE schemaname = 'public')
ORDER BY tablename;
```
