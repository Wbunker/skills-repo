---
name: row-level-security
description: >
  Implement, debug, and optimize Row-Level Security (RLS) across PostgreSQL, Supabase, and
  SQL Server. Covers policy design for multi-tenant SaaS, role-based access, team/org sharing,
  and attribute-based access control. Use when: (1) setting up RLS policies from scratch,
  (2) debugging "users can't see their own data" issues, (3) fixing RLS performance problems,
  (4) reviewing existing policies for security gaps, (5) migrating from application-level to
  database-level access control, (6) implementing tenant isolation, or when the user says
  /row-level-security, "add RLS", "row level security", "tenant isolation", or "policy".
---

# Row-Level Security

Implement database-enforced access control that filters rows based on the executing user's identity and role. RLS moves authorization from application code into the database itself — every query path is protected, including direct SQL, ORMs, admin tools, and migration scripts.

## Decision: Which Platform?

| Platform | Read | When |
|----------|------|------|
| **PostgreSQL** | `references/postgresql.md` | Native Postgres, any Postgres-compatible DB |
| **Supabase** | `references/supabase.md` | Supabase projects (wraps Postgres RLS + auth.uid()) |
| **SQL Server** | `references/sql-server.md` | Microsoft SQL Server environments |
| **MySQL** | `references/sql-server.md` (MySQL section at bottom) | MySQL — no native RLS, uses workarounds |

Read the reference for the user's platform. If unclear, ask.

## Core Workflow

### Step 1: Classify tables

Categorize every table that holds user data:

| Category | RLS approach | Example |
|----------|-------------|---------|
| **User-owned** | `WHERE user_id = current_user_id()` | profiles, settings, drafts |
| **Tenant-scoped** | `WHERE tenant_id = current_tenant_id()` | all SaaS business data |
| **Team-shared** | `WHERE id IN (SELECT ... FROM memberships)` | projects, documents |
| **Public read** | `SELECT` open, writes restricted | blog posts, product listings |
| **Admin-only** | Role-based policy | audit logs, system config |
| **Cross-tenant** | No RLS or service-role only | analytics aggregates, system tables |

### Step 2: Design policies

For each table, define policies for each operation:

```
Table: documents
  SELECT — owner OR team member OR public=true
  INSERT — authenticated, set owner=current_user
  UPDATE — owner OR team admin
  DELETE — owner only
```

**Critical rules**:
- Always specify both `USING` (read filter) and `WITH CHECK` (write validation) on write policies
- Use `RESTRICTIVE` policies for tenant isolation (ANDed), `PERMISSIVE` for role access (ORed)
- Handle NULL auth context explicitly — `auth.uid() IS NULL` blocks unauthenticated, not everyone
- Use `LOWER()` for case-insensitive string comparisons (email, username)

### Step 3: Implement

Read the platform-specific reference, then:

1. Enable RLS on each table
2. Force RLS on table owners (prevents bypass)
3. Create policies per the design from Step 2
4. Index every column referenced in policy expressions
5. Test as a non-superuser / non-service-role connection

### Step 4: Test thoroughly

Test every policy with at least these personas:

| Persona | Expected behavior |
|---------|-------------------|
| Unauthenticated | See only public data, cannot write |
| Authenticated user A | See own data + shared data, cannot see user B's data |
| Team member | See team resources, not other teams |
| Admin | See all data within their tenant |
| Superadmin / service role | Bypasses RLS (expected and dangerous) |

```sql
-- Test as a specific user (PostgreSQL)
SET LOCAL role = 'app_user';
SET LOCAL app.current_user_id = 'user-uuid-here';
SELECT * FROM documents;  -- should only return user's docs
RESET role;
```

### Step 5: Optimize

RLS policies execute on every row access. Common performance issues:

| Problem | Fix |
|---------|-----|
| Policy does `EXISTS (SELECT 1 FROM permissions ...)` | Add composite index on permissions lookup columns |
| Policy joins large tables | Use session variables instead: `current_setting('app.tenant_id')` |
| Subselect re-evaluates per row | Wrap in `(SELECT auth.uid())` to evaluate once (Supabase) |
| Missing index on `tenant_id` | Add index; consider partial indexes for common filters |

Run `EXPLAIN ANALYZE` on critical queries with RLS enabled vs disabled to measure overhead.

## The 5 Patterns That Always Break

For detailed debugging workflows, read `references/anti-patterns.md`.

| # | Pattern | Symptom | Quick fix |
|---|---------|---------|-----------|
| 1 | **Forgot NULL** | Everyone blocked during auth loading | Add `OR auth.uid() IS NULL` for public data |
| 2 | **Circular deps** | Infinite hang — Table A policy checks Table B, B checks A | Use session variables instead of cross-table joins |
| 3 | **Case mismatch** | `email = auth.email()` fails — one is uppercase | Use `LOWER()` on both sides |
| 4 | **JWT race condition** | First query after login always fails | Wait for auth state before querying |
| 5 | **Wrong column name** | Policy silently returns no rows | Audit policy columns against actual schema |

## Connection Pooling Safety

When using PgBouncer, Supabase pooler, or any connection pool, tenant context MUST be transaction-scoped:

```sql
BEGIN;
SELECT set_config('app.current_tenant_id', $1, true);  -- true = transaction-local
-- ... application queries (RLS uses current_setting('app.current_tenant_id')) ...
COMMIT;
-- Setting auto-clears — no tenant leakage to next request
```

Never use session-level `SET` with connection pooling — the connection may be reused by a different tenant.

## ORM Integration

For patterns integrating RLS with Prisma, SQLAlchemy, Django, and Drizzle, read `references/orm-integration.md`.

## Emergency: Production Is Broken

If RLS is blocking legitimate users in production right now:

```sql
-- 1. Audit current policies
SELECT tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies WHERE schemaname = 'public';

-- 2. Identify the blocking policy (test as affected user)
SET LOCAL role = 'authenticated';
SET LOCAL request.jwt.claims = '{"sub": "affected-user-uuid"}';
EXPLAIN ANALYZE SELECT * FROM affected_table;

-- 3. Emergency: temporarily allow access while you fix (add logging!)
CREATE POLICY emergency_access ON affected_table
  FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- 4. Fix the real policy, then drop the emergency one
DROP POLICY emergency_access ON affected_table;
```
