# Documenting Security-Critical Architectural Constraints

## The Core Problem

You have a security rule that is invisible in the code. A new engineer (or an AI assistant) sees a database connection and a User model, reaches for the most direct path, and bypasses your abstraction — not out of malice, but because the constraint lives only in your team's heads. The fix is to make the constraint impossible to miss and expensive to violate.

---

## Layer 1: Source-Level Guardrails (Highest Signal)

These are discovered at the moment a developer is writing the code, making them the most effective.

### 1a. Deprecation / Blocking Annotations on Direct Access

Mark every surface that should not be called directly so that IDEs and compilers flag it immediately.

```java
// Java example
@Deprecated(since = "security", forRemoval = false)
// or a custom annotation:
@DirectDatabaseAccessForbidden(
    reason = "Bypasses tenant_id row-level security. Use UserRepository instead.",
    alternative = "com.example.repository.UserRepository"
)
public class UserDaoRaw { ... }
```

```python
# Python example
import warnings

class _UserTableDirectAccess:
    """
    SECURITY: Do not use this class directly.
    It bypasses tenant_id row-level security.
    Use UserRepository instead.
    """
    def query(self, *args, **kwargs):
        warnings.warn(
            "Direct user table access bypasses tenant_id RLS. Use UserRepository.",
            SecurityWarning,
            stacklevel=2,
        )
        ...
```

The key is that the warning or deprecation message names the exact security consequence and the correct alternative.

### 1b. Make the Repository the Only Public API

Move direct table/DAO access to a private or internal module. If engineers cannot import it without going out of their way, they will not use it by accident.

- In Python: prefix with `_` (e.g., `_user_table.py`) or place in an `_internal/` package.
- In Java/Kotlin: use package-private visibility or a module boundary (`module-info.java` that does not export the DAO).
- In TypeScript: keep raw query functions in a file not re-exported from `index.ts`.

---

## Layer 2: Co-located Documentation (Where Developers Read)

### 2a. A `SECURITY.md` or `ARCHITECTURE.md` at the Repository Root

This is often the first file a new engineer reads. Keep it short and make the constraint prominent.

```markdown
## Security: User Data Access

**Rule:** Never query the `users` table directly. Always go through `UserRepository`.

**Why:** `UserRepository` enforces `tenant_id` filtering on every query. A direct query
returns rows across all tenants, which is a data-isolation vulnerability.

**Enforcement:** `UserRepository` is the only exported interface to user data.
The underlying DAO is package-private and must not be made public.

**Correct pattern:**
```java
// Good
List<User> users = userRepository.findByEmail(email); // tenant_id added automatically

// Forbidden — will be caught in code review
List<User> users = jdbcTemplate.query("SELECT * FROM users WHERE email = ?", email);
```
```

### 2b. Inline Comments at the Entry Points

Put a security comment at the top of the `UserRepository` interface/class and at the top of any direct-access class that still exists.

```java
/**
 * SECURITY-CRITICAL: This is the only permitted way to access user data.
 *
 * Every method in this repository automatically applies a tenant_id filter
 * derived from the current security context. Bypassing this class and querying
 * the users table directly will expose cross-tenant data.
 *
 * See: docs/architecture/row-level-security.md
 */
public interface UserRepository { ... }
```

### 2c. ADR (Architecture Decision Record)

Write a one-page ADR that records *why* the constraint exists. This is especially useful for AI assistants that ingest repository context, because it provides explicit reasoning rather than just a rule.

File: `docs/adr/0012-user-repository-mandatory.md`

```markdown
# ADR-0012: UserRepository is the Mandatory Access Layer for User Data

## Status: Accepted

## Context
The users table is shared across tenants. Without filtering on tenant_id, any
query returns data belonging to other customers.

## Decision
All code that reads or writes user data must go through UserRepository.
Direct SQL or ORM queries against the users table are forbidden.

## Consequences
- UserRepository must be kept up to date when new query patterns are needed.
- Code review must reject any direct user table access.
- The underlying DAO remains package-private.

## Enforcement
- Package visibility prevents accidental import.
- A lint rule (see .sqlfluff / custom linter) flags raw queries referencing `users`.
- CI runs a grep check: `grep -r "FROM users" --include="*.java" src/` must return no results
  outside of the repository package itself.
```

---

## Layer 3: Tooling Enforcement (Catches What Humans Miss)

### 3a. Linting / Static Analysis

Add a rule to your linter or write a custom check that fails CI if it detects a direct query against the users table outside the repository layer.

```bash
# Simple CI step (bash)
VIOLATIONS=$(grep -rn --include="*.java" "FROM users" src/ | grep -v "src/repository/")
if [ -n "$VIOLATIONS" ]; then
  echo "SECURITY VIOLATION: Direct query against users table detected:"
  echo "$VIOLATIONS"
  exit 1
fi
```

For more sophisticated enforcement, tools like ArchUnit (Java), import-linter (Python), or dependency-cruiser (TypeScript/JS) let you encode "module X may not import module Y" as a test that runs in CI.

### 3b. Database-Level Defense in Depth

Even if code-level controls fail, add a database-level safety net:

- Create a `users_view` that includes a `WHERE tenant_id = current_setting('app.tenant_id')` predicate, and grant application users access only to the view, not the base table.
- This means a direct query will either return empty results (if the session variable is set) or fail entirely (if it is not), rather than returning all tenant data.

This is defense in depth: the repository is the primary control; the database permission is the backstop.

---

## Layer 4: AI-Specific Signals

AI coding assistants (including Claude) build context from the files in your repository. To steer them correctly:

### 4a. `CLAUDE.md` or `.cursorrules` / `.github/copilot-instructions.md`

Many AI tools read a project-level instructions file. Add an explicit rule:

```markdown
## Data Access Rules

- NEVER write direct SQL queries against the `users` table.
- ALWAYS use `UserRepository` to access user data.
- Reason: `UserRepository` enforces mandatory `tenant_id` filtering.
  Direct queries are a multi-tenant data isolation vulnerability.
- The underlying DAO is intentionally package-private. Do not change its visibility.
```

### 4b. Example-Driven Documentation

AI assistants weight concrete examples heavily. In your `ARCHITECTURE.md` or ADR, include a before/after block:

```markdown
### User Data Access

BAD — never do this:
```sql
SELECT * FROM users WHERE email = 'alice@example.com'
```

BAD — never do this either:
```java
jdbcTemplate.query("SELECT * FROM users WHERE id = ?", userId)
```

GOOD — always use the repository:
```java
userRepository.findById(userId)  // automatically adds WHERE tenant_id = :currentTenant
```
```

Seeing the forbidden patterns alongside the correct pattern teaches both humans and AI what NOT to generate.

---

## Priority Order

If you can only do a few of these, do them in this order:

1. **Make the correct path the easy path.** `UserRepository` should be the obvious thing to reach for; the raw DAO should be hard to import.
2. **Add a CI check.** Humans and AI forget; automated enforcement does not.
3. **Put a security comment in `UserRepository` itself.** That is where the developer is when they are about to write code.
4. **Add a `CLAUDE.md` rule.** Cheap, immediate effect on AI-assisted development.
5. **Write the ADR.** Provides durable reasoning for future engineers and future AI context windows.

The goal is to make the wrong choice require deliberate effort and to make the right choice obvious, documented, and reinforced at every level: IDE, code review, CI, and database.
