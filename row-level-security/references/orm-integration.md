# RLS + ORM Integration

How to set tenant/user context for RLS when using popular ORMs and frameworks.

## Table of Contents

- [Prisma](#prisma)
- [SQLAlchemy](#sqlalchemy)
- [Django](#django)
- [Drizzle](#drizzle)
- [General Pattern](#general-pattern)

---

## General Pattern

All ORMs follow the same pattern:
1. At the start of each request, set the session/transaction context
2. Execute the application query (RLS applies automatically)
3. At the end of the request, clean up (or use transaction-scoped settings)

```
Request arrives → Extract user ID from JWT → BEGIN transaction →
SET context variables → Execute queries (RLS filters automatically) → COMMIT
```

---

## Prisma

Prisma doesn't natively support `SET` commands. Use Prisma Client Extensions or `$executeRaw`:

### With Client Extensions (recommended)

```typescript
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient().$extends({
  query: {
    $allOperations({ args, query }) {
      // Context is set per-query via a transaction
      return query(args);
    },
  },
});

// Per-request: wrap in transaction with context
async function withRLS<T>(userId: string, tenantId: string, fn: (tx: any) => Promise<T>): Promise<T> {
  return prisma.$transaction(async (tx) => {
    await tx.$executeRaw`SELECT set_config('app.current_user_id', ${userId}, true)`;
    await tx.$executeRaw`SELECT set_config('app.current_tenant_id', ${tenantId}, true)`;
    return fn(tx);
  });
}

// Usage in API handler
app.get('/documents', async (req, res) => {
  const docs = await withRLS(req.user.id, req.user.tenantId, async (tx) => {
    return tx.document.findMany();  // RLS filters automatically
  });
  res.json(docs);
});
```

### Connection-per-request (alternative)

If using PgBouncer in transaction mode, ensure each Prisma query runs inside an explicit transaction with context set.

```typescript
// Middleware that wraps every handler in an RLS transaction
function rlsMiddleware(prisma: PrismaClient) {
  return async (req, res, next) => {
    req.db = {
      async query(fn) {
        return prisma.$transaction(async (tx) => {
          await tx.$executeRaw`SELECT set_config('app.current_user_id', ${req.user.id}, true)`;
          return fn(tx);
        });
      }
    };
    next();
  };
}
```

---

## SQLAlchemy

### Event-based context setting

```python
from sqlalchemy import event, text
from sqlalchemy.orm import Session

def set_rls_context(session: Session, user_id: str, tenant_id: str):
    """Set RLS context at the start of each request."""
    @event.listens_for(session, "after_begin")
    def set_context(session, transaction, connection):
        connection.execute(
            text("SELECT set_config('app.current_user_id', :uid, true)"),
            {"uid": user_id}
        )
        connection.execute(
            text("SELECT set_config('app.current_tenant_id', :tid, true)"),
            {"tid": tenant_id}
        )

# Flask integration
@app.before_request
def setup_rls():
    if current_user.is_authenticated:
        set_rls_context(db.session, str(current_user.id), str(current_user.tenant_id))
```

### Middleware approach (FastAPI)

```python
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

async def get_rls_session(request: Request, session: AsyncSession = Depends(get_session)):
    user = request.state.user
    await session.execute(
        text("SELECT set_config('app.current_user_id', :uid, true)"),
        {"uid": str(user.id)}
    )
    await session.execute(
        text("SELECT set_config('app.current_tenant_id', :tid, true)"),
        {"tid": str(user.tenant_id)}
    )
    yield session

@app.get("/documents")
async def list_documents(session: AsyncSession = Depends(get_rls_session)):
    result = await session.execute(select(Document))
    return result.scalars().all()  # RLS filters automatically
```

---

## Django

### django-rls package

```python
# pip install django-rls
# settings.py
INSTALLED_APPS = [
    'django_rls',
    ...
]

MIDDLEWARE = [
    'django_rls.middleware.RLSMiddleware',
    ...
]

# Configure which session variables to set
DJANGO_RLS = {
    'TENANT_ID': lambda request: str(request.user.tenant_id),
    'USER_ID': lambda request: str(request.user.id),
}
```

### Manual middleware

```python
from django.db import connection

class RLSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT set_config('app.current_user_id', %s, true)",
                    [str(request.user.id)]
                )
                cursor.execute(
                    "SELECT set_config('app.current_tenant_id', %s, true)",
                    [str(request.user.tenant_id)]
                )
        return self.get_response(request)
```

### Django + connection pooling gotcha

Django's default connection handling opens a new connection per request (no pooling). If using `django-db-connection-pool` or PgBouncer, you MUST use transaction-scoped settings (`true` parameter to `set_config`) and wrap each request in a transaction.

---

## Drizzle

Drizzle has first-class RLS support:

```typescript
import { pgPolicy, pgTable, uuid, text } from 'drizzle-orm/pg-core';
import { sql } from 'drizzle-orm';
import { authenticatedRole, authUid } from 'drizzle-orm/supabase';

// Define table with inline policies
export const documents = pgTable('documents', {
  id: uuid('id').primaryKey().defaultRandom(),
  title: text('title').notNull(),
  userId: uuid('user_id').notNull(),
}, (table) => [
  pgPolicy('user_owns_documents', {
    as: 'permissive',
    for: 'all',
    to: authenticatedRole,
    using: sql`${table.userId} = (SELECT auth.uid())`,
    withCheck: sql`${table.userId} = (SELECT auth.uid())`,
  }),
]);
```

### With manual context setting

```typescript
import { drizzle } from 'drizzle-orm/node-postgres';
import { sql } from 'drizzle-orm';

const db = drizzle(pool);

// Per-request context
async function withTenant<T>(tenantId: string, fn: (db: any) => Promise<T>): Promise<T> {
  return db.transaction(async (tx) => {
    await tx.execute(sql`SELECT set_config('app.current_tenant_id', ${tenantId}, true)`);
    return fn(tx);
  });
}
```

---

## Key Principles for All ORMs

1. **Always use transaction-scoped context** (`set_config(..., true)`) when using connection pooling
2. **Set context as early as possible** in the request lifecycle (middleware/beforeRequest)
3. **Never set context in application code** — centralize in middleware so it can't be forgotten
4. **Test with the ORM**, not raw SQL — ORMs may generate queries differently than expected
5. **Audit ORM-generated SQL** — use query logging to verify RLS context is being set before data queries
6. **Handle the no-auth case** — middleware should skip context setting (or set empty values) for unauthenticated routes
