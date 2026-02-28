# RLS Anti-Patterns and Debugging

Common failures, their root causes, and fixes. Read this when debugging broken policies or reviewing existing RLS implementations.

## Table of Contents

- [The 5 Classic Disasters](#the-5-classic-disasters)
- [The Over-Security Syndrome](#the-over-security-syndrome)
- [Debugging Workflow](#debugging-workflow)
- [Security Gaps to Audit](#security-gaps-to-audit)
- [Migration Pitfalls](#migration-pitfalls)

---

## The 5 Classic Disasters

### 1. The "Forgot About NULL" Pattern

**Symptom**: Everyone is blocked during auth loading. Users see blank pages for the first 1-2 seconds.

**Root cause**: Policy checks `auth.uid() = user_id`, but during the auth handshake `auth.uid()` returns NULL. `NULL = anything` evaluates to `NULL` (not `true`), so the policy blocks everyone.

**Fix**: Decide what unauthenticated users should see.

```sql
-- Public data visible to everyone (including during auth loading)
CREATE POLICY public_read ON posts
  FOR SELECT USING (
    published = true  -- no auth check for public data
  );

-- Private data requires auth
CREATE POLICY owner_read ON posts
  FOR SELECT TO authenticated
  USING (author_id = (SELECT auth.uid()));
```

**Key insight**: Separate public-read policies from authenticated-read policies. Never put both in one policy with OR.

### 2. The "Circular Dependency" Nightmare

**Symptom**: Queries hang or timeout. Performance degrades exponentially with more data.

**Root cause**: Table A's policy queries Table B. Table B's policy queries Table C. Table C's policy queries Table A. The database tries to resolve this recursively.

**Detection**:

```sql
-- Map all inter-table references in policies
SELECT
  p.tablename AS policy_table,
  p.policyname,
  regexp_matches(p.qual, 'FROM\s+(\w+)', 'gi') AS references_table
FROM pg_policies p
WHERE p.schemaname = 'public';
```

**Fix**: Break circles using session variables or `SECURITY DEFINER` functions.

```sql
-- BEFORE (circular): documents policy checks memberships, memberships policy checks documents
-- AFTER: both use session variable set once at request start
CREATE POLICY doc_access ON documents
  FOR SELECT TO authenticated
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

### 3. The "Case Sensitivity Killer"

**Symptom**: Users can't find their own data. Email-based lookups return nothing. Some users work, others don't.

**Root cause**: Policy compares `email = auth.email()` but one side is `User@Example.com` and the other is `user@example.com`. PostgreSQL string comparison is case-sensitive.

**Fix**:

```sql
-- Use LOWER() on both sides
CREATE POLICY email_access ON user_data
  FOR SELECT TO authenticated
  USING (LOWER(email) = LOWER((SELECT auth.email())));

-- Also normalize on insert
CREATE OR REPLACE FUNCTION normalize_email()
RETURNS TRIGGER AS $$
BEGIN
  NEW.email := LOWER(TRIM(NEW.email));
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER normalize_email_trigger
  BEFORE INSERT OR UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION normalize_email();

-- Add functional index for performance
CREATE INDEX idx_users_email_lower ON users (LOWER(email));
```

### 4. The "JWT Not Ready" Race Condition

**Symptom**: First query after login always fails. Page loads blank, then works on refresh. Realtime subscriptions miss initial data.

**Root cause**: Frontend app queries the database before the Supabase Auth JWT is available. `auth.uid()` returns NULL on the first request.

**Fix** (React/Next.js example):

```typescript
// Wait for auth state before any queries
function AuthGate({ children }) {
  const { session, isLoading } = useSession();

  if (isLoading) return <LoadingSkeleton />;
  if (!session) return <LoginPage />;
  return children;  // Only render data-fetching components after auth is ready
}

// For Supabase Realtime:
supabase.auth.onAuthStateChange((event, session) => {
  if (event === 'SIGNED_IN' && session) {
    // NOW safe to subscribe
    supabase.channel('my-channel').on('postgres_changes', ...).subscribe();
  }
});
```

### 5. The "Wrong Column Name" Classic

**Symptom**: Policy silently returns zero rows. No error. Users see empty tables.

**Root cause**: Policy references `user_id` but the column is actually `userId`, `owner_id`, or `created_by`. PostgreSQL doesn't validate column references in policy expressions at creation time.

**Detection**:

```sql
-- Extract column references from policies and compare to actual schema
SELECT
  p.tablename,
  p.policyname,
  p.qual AS policy_expression,
  c.column_name AS actual_columns
FROM pg_policies p
CROSS JOIN information_schema.columns c
WHERE p.schemaname = 'public'
  AND c.table_schema = 'public'
  AND c.table_name = p.tablename
ORDER BY p.tablename, p.policyname;
```

**Prevention**: Always verify policies with a test query immediately after creation.

---

## The Over-Security Syndrome

Common patterns where security blocks legitimate functionality:

### Admin can't see user data

**Problem**: Admin dashboard shows nothing because `auth.uid() = user_id` doesn't match admin's UUID.

**Fix**: Add an admin-specific permissive policy:

```sql
CREATE POLICY admin_access ON user_data
  FOR SELECT TO authenticated
  USING (
    (SELECT auth.jwt() -> 'app_metadata' ->> 'role') = 'admin'
    AND tenant_id = (SELECT get_current_tenant_id())  -- still scoped to tenant!
  );
```

### Team features completely broken

**Problem**: RLS only checks individual ownership. Shared documents, team projects, collaborative features all return empty.

**Fix**: Add team-based permissive policies alongside ownership policies:

```sql
-- Ownership (already exists)
CREATE POLICY owner_access ON documents FOR SELECT TO authenticated
  USING (owner_id = (SELECT auth.uid()));

-- Team access (ADD THIS)
CREATE POLICY team_access ON documents FOR SELECT TO authenticated
  USING (
    team_id IN (
      SELECT team_id FROM team_members WHERE user_id = (SELECT auth.uid())
    )
  );

-- Explicit sharing (ADD THIS)
CREATE POLICY shared_access ON documents FOR SELECT TO authenticated
  USING (
    id IN (
      SELECT document_id FROM document_shares WHERE user_id = (SELECT auth.uid())
    )
  );
```

### Service-to-service calls blocked

**Problem**: Background jobs, cron tasks, webhooks can't access data.

**Fix**: Use service role or a dedicated database role that bypasses RLS:

```sql
-- Create a service role
CREATE ROLE service_worker;
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_worker;
-- Don't add service_worker to any RLS policy's TO clause
-- Service worker inherits no policies → full access (when RLS uses TO app_user, not TO PUBLIC)
```

---

## Debugging Workflow

When users can't see their data:

```sql
-- 1. List all policies on the affected table
SELECT policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies WHERE tablename = 'affected_table';

-- 2. Check what the user's auth context looks like
SELECT auth.uid(), auth.role(), auth.jwt();

-- 3. Test the policy expression manually
SELECT *, (user_id = 'the-users-uuid'::uuid) AS would_match
FROM affected_table
LIMIT 20;  -- run as superuser to see all rows

-- 4. Check for data issues
SELECT DISTINCT user_id FROM affected_table
WHERE user_id::text LIKE '%the-users-uuid%';  -- partial match to catch formatting issues

-- 5. Test as the user
SET LOCAL role = 'authenticated';
SET LOCAL request.jwt.claims = '{"sub": "the-users-uuid"}';
SELECT * FROM affected_table;
RESET role;
```

---

## Security Gaps to Audit

### Policies that are too permissive

```sql
-- Find policies with USING (true) — wide open!
SELECT tablename, policyname FROM pg_policies
WHERE qual = 'true' OR qual IS NULL;

-- Find tables with RLS enabled but only SELECT policies (writes unprotected)
SELECT DISTINCT p1.tablename
FROM pg_policies p1
WHERE p1.schemaname = 'public'
  AND NOT EXISTS (
    SELECT 1 FROM pg_policies p2
    WHERE p2.tablename = p1.tablename
      AND p2.cmd IN ('INSERT', 'UPDATE', 'DELETE', 'ALL')
  );
```

### Missing WITH CHECK on write policies

If a policy uses `FOR ALL` or `FOR UPDATE` but only has `USING` without `WITH CHECK`, the `USING` expression is used for both. This can be acceptable but review explicitly — can a user UPDATE a row to change its `user_id` to someone else's?

### Foreign key leaks

RLS doesn't prevent foreign key constraint checks from revealing row existence. If Table A references Table B, inserting a row into A with a nonexistent B reference produces a different error than an existing-but-hidden B reference. This can leak information.

---

## Migration Pitfalls

### Enabling RLS on existing tables

Enabling RLS without policies blocks ALL access (except for table owner and superusers). Always:

1. Write and test policies FIRST
2. Enable RLS second
3. Test immediately

```sql
-- Safe migration order:
BEGIN;
  -- 1. Create policies (table still has no RLS, so these are dormant)
  CREATE POLICY ... ON my_table ...;

  -- 2. Enable RLS (policies now activate)
  ALTER TABLE my_table ENABLE ROW LEVEL SECURITY;
  ALTER TABLE my_table FORCE ROW LEVEL SECURITY;

  -- 3. Quick smoke test
  SET LOCAL role = 'app_user';
  SET LOCAL app.current_user_id = 'test-user-uuid';
  SELECT count(*) FROM my_table;  -- should return > 0
COMMIT;  -- or ROLLBACK if test fails
```

### Forgetting FORCE ROW LEVEL SECURITY

Without `FORCE`, the table owner bypasses RLS. If your app connects as the table owner, RLS is effectively disabled.

### Adding RLS to tables with existing application queries

Existing queries may rely on seeing all rows. After enabling RLS, any query path not using the correct role/session-context will silently return no rows. Audit all query paths: application code, admin dashboards, background jobs, migration scripts, reporting queries.
