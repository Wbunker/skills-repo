# Supabase Row-Level Security

Supabase exposes your Postgres database directly to the client via PostgREST. RLS is the **only** thing standing between your users and raw SQL access. Tables without RLS enabled are publicly accessible through the API.

## Table of Contents

- [Critical Supabase Rules](#critical-supabase-rules)
- [Enabling RLS](#enabling-rls)
- [Auth Helper Functions](#auth-helper-functions)
- [Common Policy Patterns](#common-policy-patterns)
- [Performance: The (SELECT) Trick](#performance-the-select-trick)
- [Multi-Tenant Patterns](#multi-tenant-patterns)
- [Service Role vs Client](#service-role-vs-client)
- [Testing Policies](#testing-policies)
- [Gotchas](#gotchas)

---

## Critical Supabase Rules

1. **Enable RLS on EVERY table** — tables without RLS are fully exposed via the API
2. **Never expose `service_role` key** in client-side code — it bypasses all RLS
3. **Never base policies on `raw_user_meta_data`** — users can modify their own metadata
4. **Use `app_metadata`** for roles/permissions — only settable via server/admin API
5. **Always use `TO authenticated`** in policies — avoids evaluating for anon requests
6. **Wrap `auth.uid()` in `(SELECT ...)`** for performance — evaluated once, not per-row

## Enabling RLS

```sql
-- Via SQL Editor
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents FORCE ROW LEVEL SECURITY;

-- Or via Supabase Dashboard: Table Editor → table → RLS toggle
```

## Auth Helper Functions

Supabase provides these functions in policies:

```sql
auth.uid()        -- UUID of the authenticated user (from JWT sub claim)
auth.jwt()        -- full JWT claims as JSON
auth.role()       -- 'authenticated', 'anon', or 'service_role'
auth.email()      -- user's email from JWT
```

**Always wrap in subselect for performance:**

```sql
-- SLOW: auth.uid() re-evaluates for every row
USING (user_id = auth.uid())

-- FAST: evaluates once, reused for all rows
USING (user_id = (SELECT auth.uid()))
```

## Common Policy Patterns

### User-owned data

```sql
CREATE POLICY "Users see own data" ON profiles
  FOR SELECT TO authenticated
  USING (id = (SELECT auth.uid()));

CREATE POLICY "Users update own data" ON profiles
  FOR UPDATE TO authenticated
  USING (id = (SELECT auth.uid()))
  WITH CHECK (id = (SELECT auth.uid()));
```

### Public read, authenticated write

```sql
CREATE POLICY "Anyone can read published" ON posts
  FOR SELECT USING (published = true);

CREATE POLICY "Authors manage own posts" ON posts
  FOR ALL TO authenticated
  USING (author_id = (SELECT auth.uid()))
  WITH CHECK (author_id = (SELECT auth.uid()));
```

### Team/org access

```sql
CREATE POLICY "Team members see projects" ON projects
  FOR SELECT TO authenticated
  USING (
    team_id IN (
      SELECT team_id FROM team_members
      WHERE user_id = (SELECT auth.uid())
    )
  );
```

### Role-based using JWT claims

```sql
-- Using app_metadata (safe — not user-modifiable)
CREATE POLICY "Admins see all" ON documents
  FOR SELECT TO authenticated
  USING (
    (SELECT auth.jwt() -> 'app_metadata' ->> 'role') = 'admin'
  );

-- DANGEROUS: Do NOT use raw_user_meta_data — users can change it
-- USING ((auth.jwt() -> 'user_metadata' ->> 'role') = 'admin')  -- WRONG!
```

### Insert with auto-set owner

```sql
CREATE POLICY "Users create with ownership" ON documents
  FOR INSERT TO authenticated
  WITH CHECK (user_id = (SELECT auth.uid()));

-- Client code:
-- const { data } = await supabase.from('documents')
--   .insert({ title: 'New doc', user_id: session.user.id });
```

## Performance: The (SELECT) Trick

The single most important Supabase RLS optimization:

```sql
-- Without subselect: auth.uid() called for EVERY row in the table
USING (user_id = auth.uid())
-- Postgres treats auth.uid() as volatile → cannot optimize

-- With subselect: auth.uid() called ONCE, result reused
USING (user_id = (SELECT auth.uid()))
-- Postgres evaluates the subselect once as an InitPlan
```

This can make a 10-100x difference on tables with thousands of rows.

Also add client-side filters that mirror the RLS condition to help the query planner:

```typescript
// RLS policy: USING (user_id = (SELECT auth.uid()))
// Client query mirrors the filter:
const { data } = await supabase
  .from('documents')
  .select('*')
  .eq('user_id', session.user.id);  // helps query planner use index
```

## Multi-Tenant Patterns

### Simple: tenant_id column

```sql
-- Add tenant_id to every table
ALTER TABLE documents ADD COLUMN tenant_id uuid REFERENCES tenants(id);

-- Restrictive policy for tenant isolation
CREATE POLICY "Tenant isolation" ON documents
  AS RESTRICTIVE FOR ALL TO authenticated
  USING (tenant_id = (
    SELECT tenant_id FROM user_profiles WHERE id = (SELECT auth.uid())
  ))
  WITH CHECK (tenant_id = (
    SELECT tenant_id FROM user_profiles WHERE id = (SELECT auth.uid())
  ));

-- Then add permissive policies for role-based access within the tenant
```

### With SECURITY DEFINER for complex lookups

```sql
-- Create a function that runs with elevated privileges
CREATE OR REPLACE FUNCTION get_current_tenant_id()
RETURNS uuid
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT tenant_id FROM user_profiles WHERE id = auth.uid();
$$;

-- Use in policies (avoids RLS on user_profiles blocking the lookup)
CREATE POLICY "Tenant isolation" ON documents
  AS RESTRICTIVE FOR ALL TO authenticated
  USING (tenant_id = (SELECT get_current_tenant_id()))
  WITH CHECK (tenant_id = (SELECT get_current_tenant_id()));
```

## Service Role vs Client

| Key | When to use | RLS behavior |
|-----|-------------|-------------|
| `anon` key | Client-side, unauthenticated | RLS enforced, `auth.uid()` = NULL |
| User JWT | Client-side, authenticated | RLS enforced, `auth.uid()` = user's UUID |
| `service_role` key | Server-side only (webhooks, admin scripts, cron) | **Bypasses all RLS** |

**Never expose `service_role` in:**
- Client-side JavaScript bundles
- Mobile apps
- Environment variables accessible to client code
- Public repositories

## Testing Policies

Test from the **client SDK**, not the SQL Editor (SQL Editor runs as postgres superuser and bypasses RLS).

```typescript
// Test as authenticated user
const { data, error } = await supabase
  .from('documents')
  .select('*');
console.log('Visible rows:', data?.length);

// Test as different user: create a second Supabase client with a different user's JWT
```

Or test in SQL with role impersonation:

```sql
-- Impersonate authenticated user
SET LOCAL role = 'authenticated';
SET LOCAL request.jwt.claims = '{
  "sub": "user-uuid-here",
  "role": "authenticated",
  "app_metadata": {"role": "user"}
}';

SELECT * FROM documents;
RESET role;
```

## Gotchas

### 1. RLS + Realtime subscriptions
Supabase Realtime respects RLS — users only receive events for rows they can see. But the initial subscription setup can race with auth. Always wait for `onAuthStateChange` before subscribing.

### 2. Storage and RLS
Supabase Storage has its own RLS policies on `storage.objects`. These are separate from your table policies. Configure them in the Dashboard under Storage → Policies.

### 3. Foreign key lookups through RLS
If Table A's policy does `EXISTS (SELECT 1 FROM table_b WHERE ...)`, and Table B also has RLS, the policy query runs as the current user and Table B's RLS applies. This can cause unexpected access denials. Use `SECURITY DEFINER` functions to bypass this when needed.

### 4. Edge Functions and RLS
Edge Functions using `createClient` with the `service_role` key bypass RLS. Use the user's JWT instead when you want RLS to apply:

```typescript
// RLS bypassed:
const supabase = createClient(url, SERVICE_ROLE_KEY);

// RLS enforced:
const supabase = createClient(url, ANON_KEY, {
  global: { headers: { Authorization: `Bearer ${userJwt}` } }
});
```
