# Azure Function → Supabase Data Copy — Pattern Guide

End-to-end guide for the pattern: an **Azure Function reads from a database in Azure and copies the
data to Supabase** (Supabase = managed Postgres + PostgREST). Covers trigger selection, serverless
connection management, source-DB read patterns, connecting to Supabase, incremental/CDC sync,
upsert/idempotency, batching, secrets, networking, and error handling.

For Function hosting/deploy mechanics see [../compute/functions-capabilities.md](../compute/functions-capabilities.md)
and [../compute/functions-cli.md](../compute/functions-cli.md). For source DB tiers see
[postgresql-mysql-capabilities.md](postgresql-mysql-capabilities.md),
[azure-sql-capabilities.md](azure-sql-capabilities.md), [cosmos-db-capabilities.md](cosmos-db-capabilities.md).

## Contents

- [Architecture & decision flow](#architecture--decision-flow)
- [Trigger selection](#trigger-selection)
- [Connection management in serverless (the static-client rule)](#connection-management-in-serverless-the-static-client-rule)
- [Reading from the source Azure database](#reading-from-the-source-azure-database)
- [Connecting to Supabase from a Function](#connecting-to-supabase-from-a-function)
- [Upsert & idempotency](#upsert--idempotency)
- [Incremental / CDC sync & watermarks](#incremental--cdc-sync--watermarks)
- [Batching & large copies](#batching--large-copies)
- [Secrets & Key Vault](#secrets--key-vault)
- [Networking & static outbound IP](#networking--static-outbound-ip)
- [Error handling & retries](#error-handling--retries)
- [End-to-end skeleton (Python, Timer-triggered)](#end-to-end-skeleton-python-timer-triggered)

---

## Architecture & decision flow

```
Source Azure DB ──(read)──> Azure Function ──(write)──> Supabase Postgres
  Azure SQL                  Timer / CDC trigger          Supavisor pooler (6543, txn mode)
  PostgreSQL Flex            transform/map                 OR supabase-js / PostgREST upsert
  Cosmos DB                  upsert + watermark
```

Decisions, in order:

1. **How fresh must the copy be?** Near-real-time → use a change-driven trigger (SQL trigger, Cosmos
   change feed). Periodic (minutes/hours) → Timer trigger that polls a watermark.
2. **Full reload or incremental?** Incremental is the default for anything non-trivial — track a
   high-water mark (timestamp/rowversion) so each run copies only new/changed rows.
3. **Write path into Supabase?** Bulk volume → direct Postgres connection via Supavisor (COPY /
   `INSERT … ON CONFLICT`). Modest volume / no DB driver wanted → supabase-js / PostgREST `.upsert()`.
4. **Hosting plan?** Flex Consumption is the production default. Premium or Flex (not classic
   Consumption) is **required** if you need a static outbound IP (VNet + NAT Gateway) to satisfy a
   Supabase IP allowlist.

---

## Trigger selection

| Source | Near-real-time option | Periodic option |
|---|---|---|
| **Azure SQL** | **Azure SQL trigger** (change-tracking based; fires on insert/update/delete) | Timer + polling a watermark column |
| **MySQL Flexible Server** | **Azure MySQL trigger** (poll-based; captures inserts + updates as `Update`, **not deletes**; requires adding a tracking column) | Timer + polling a watermark column |
| **PostgreSQL Flexible Server** | *No native Functions trigger* — Timer + watermark, or logical replication / Debezium externally | Timer + `WHERE updated_at > @lastWatermark` |
| **Cosmos DB (NoSQL API)** | **Cosmos DB trigger** (change feed; captures inserts + updates, **not deletes**) | Timer + `_ts` filter |

- **Azure SQL trigger**: requires change tracking enabled on DB + table; binds to
  `IReadOnlyList<SqlChange<T>>` (each `SqlChange` has `.Item` + `.Operation` ∈ Insert/Update/Delete).
  Maintains internal leases in an `az_func` schema. Needs elevated grants beyond `db_datareader`
  (see [reading section](#reading-from-the-source-azure-database)). `host.json` knobs:
  `MaxBatchSize` (100), `PollingIntervalMs` (1000), `MaxChangesPerWorker` (1000).
- **Azure MySQL trigger**: GA binding (`MySqlTrigger`), but **poll-based**, not native CDC. Requires
  adding a tracking column to each monitored table:
  `ALTER TABLE Products ADD az_func_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;`
  Binds to `IReadOnlyList<MySqlChange<T>>`; only operation surfaced is `Update` (inserts + updates
  collapse to it) — **deletes are not captured**. Auto-creates a `Leases_{FunctionId}_{TableId}`
  table. `host.json` `extensions.MySql`: `MaxBatchSize` (100), `PollingIntervalMs` (1000),
  `MaxChangesPerWorker` (1000). **Managed identity is not supported on this binding** — see MySQL
  read section. Output binding fails on spatial types (`GEOMETRY`/`POINT`/`POLYGON`).
- **Cosmos DB trigger**: built on the change-feed processor; needs a **lease container** (default
  `leases`, set `CreateLeaseContainerIfNotExists`). Captures inserts/updates only — **deletes need
  soft-delete (tombstone) docs or a TTL+reconciliation scheme**.
- **Timer trigger**: NCronTab 6-field CRON `{sec} {min} {hour} {day} {month} {dow}`. Every 5 min =
  `0 */5 * * * *`. Values are absolute times, not intervals. UTC by default — override with app
  setting `WEBSITE_TIME_ZONE`.

---

## Connection management in serverless (the static-client rule)

The single biggest correctness/cost issue in this pattern. Functions scale out to many instances;
each instance reuses the same worker process across many invocations.

- **Reuse one client/pool per process — never open a connection per invocation.** Create the DB
  client/pool **at module scope (global/static)** so all invocations on that instance share it.
  Opening a fresh connection per invocation exhausts both source and destination DBs under load.
- **Per-instance connection cap (Consumption): 600 active / 1,200 total.** Exceeding it logs
  `Host thresholds exceeded: Connections`. The cap is **per instance** — scale-out multiplies total
  connections hitting your DBs, so a 50-instance burst with a 10-connection pool each = 500
  connections at the backend. Size pools small (often `1`–`5` per instance) and rely on the
  destination pooler.
- ADO.NET / `Microsoft.Data.SqlClient` pools by default; `HttpClient`, `CosmosClient`, and Postgres
  drivers must be **manually** hoisted to a singleton. Do not dispose a static client.
- Cosmos: use **one `CosmosClient` for the app lifetime** (e.g. `Lazy<CosmosClient>`).
- Node: tune `http.globalAgent.maxSockets`; for `pg`, create one `Pool` at module load.

---

## Reading from the source Azure database

Prefer **managed identity (passwordless)** auth everywhere — no secrets to rotate. Enable a
system-assigned identity on the Function (`az functionapp identity assign`) and grant it DB access.

### Azure SQL

- **Drivers**: `Microsoft.Data.SqlClient` (.NET), `pyodbc` + Microsoft ODBC Driver 18 (Python),
  `mssql`/`tedious` (Node). Port **1433**.
- **Managed identity connection string**:
  `Server=demo.database.windows.net; Authentication=Active Directory Managed Identity; Database=testdb`
  (add `User Id=<clientId>` for user-assigned). DB grant:
  ```sql
  CREATE USER [<func-app-name>] FROM EXTERNAL PROVIDER;
  ALTER ROLE db_datareader ADD MEMBER [<func-app-name>];
  ```
  A Microsoft Entra admin must be set on the SQL server first.
- **SQL trigger CDC** requires extra grants: `GRANT VIEW CHANGE TRACKING ON [<Table>]`,
  `CREATE TABLE`, `CREATE SCHEMA`, and ALTER/DML on `SCHEMA::az_func`. Enable tracking:
  ```sql
  ALTER DATABASE [db] SET CHANGE_TRACKING = ON (CHANGE_RETENTION = 2 DAYS, AUTO_CLEANUP = ON);
  ALTER TABLE [dbo].[ToDo] ENABLE CHANGE_TRACKING;
  ```
  If the Function is offline longer than `CHANGE_RETENTION`, intervening changes are lost.

### Azure Database for PostgreSQL Flexible Server

- **No native Functions trigger** — use a Timer + watermark.
- **Drivers**: `psycopg` (v3) / `psycopg2` (Python), `pg` (Node). Port **5432**, `sslmode=require`.
- **Entra/managed-identity auth**: Postgres accepts an Entra access token **in the password field**.
  Token scope: `https://ossrdbms-aad.database.windows.net/.default`. Tokens expire (~24 h) — reuse the
  `DefaultAzureCredential` object (it caches) and refresh tokens, but keep the *connection* per the
  static-client rule.
  ```python
  cred = DefaultAzureCredential()
  token = cred.get_token("https://ossrdbms-aad.database.windows.net/.default").token
  uri = f"postgresql://{user}:{token}@{host}/{db}?sslmode=require"
  ```

### Azure Database for MySQL Flexible Server

- **Drivers**: `mysql-connector-python` / `PyMySQL` (Python), **`mysql2`** (Node — *not* legacy
  `mysql`, which lacks Entra token support), `MySqlConnector` or Connector/NET (.NET). The Functions
  MySQL binding always uses Connector/NET (`MySql.Data.MySqlClient`) under the hood. Host
  `*.mysql.database.azure.com`, port **3306**.
- **TLS is enforced (TLS 1.2+)**. With `sslmode=verify-ca`/`verify-identity` you must trust the
  combined root chain — **DigiCert Global Root G2 + Microsoft RSA Root CA 2017** (concatenate both
  PEMs and pass as `SslCa`/`ssl.ca`).
- **Auth — two different stories**:
  - **Your own Function code (Timer-trigger reads)**: managed identity / Entra **is** supported.
    Acquire a token for resource `https://ossrdbms-aad.database.windows.net` and **pass it as the
    password**; username = the Entra principal. Requires the **cleartext auth plugin**
    (`--enable-cleartext-plugin` / `mysql_clear_password`) so the token is sent un-hashed. Create the
    DB user with `CREATE AADUSER 'name@tenant.onmicrosoft.com';` (run as Entra admin), then `GRANT`.
    Server identity must be a **user-assigned** managed identity. Tokens last ~5–60 min — fetch fresh
    per connection (reuse the credential object for caching).
  - **The Functions MySQL binding (trigger/input/output)**: **managed identity is NOT supported** —
    you must supply a username/password connection string (store the password in Key Vault). This is
    the key gotcha vs Azure SQL.
- **CDC/incremental**: no native change tables. Options: the poll-based MySQL trigger binding (above),
  **binlog CDC** (`binlog_format=ROW`, `binlog_row_image=FULL`) via Debezium/external tooling,
  **read replicas** (up to 10) to offload reads, or — most common for this copy pattern — a
  **Timer trigger polling a watermark column**.

### Cosmos DB (NoSQL API)

- **Change feed trigger** for CDC, or read with the SQL query API filtering on `_ts` for polling.
- Managed-identity connection (extension v4.x+): app settings `<NAME>__accountEndpoint`,
  `<NAME>__credential=managedidentity`. With MI the trigger can't auto-create the lease container —
  pre-create it.

---

## Connecting to Supabase from a Function

Supabase is Postgres behind the **Supavisor** pooler, plus a PostgREST HTTP API. Two write paths:

### Path A — Direct Postgres via Supavisor (preferred for bulk)

Use the **transaction-mode pooler on port 6543** for serverless. Connections are ephemeral
(grabbed per query, released immediately) — exactly the serverless model.

| Mode | Host | Port | Notes |
|---|---|---|---|
| Direct | `db.[REF].supabase.co` | 5432 | IPv6 by default; persistent — **avoid in serverless** |
| Supavisor **session** | `aws-[REGION].pooler.supabase.com` | 5432 | IPv4-ok; supports prepared statements |
| Supavisor **transaction** | `aws-[REGION].pooler.supabase.com` | **6543** | **Use this for Functions**; no prepared statements |

- Pooler **username embeds the project ref**: `postgres.[PROJECT-REF]`. Connection string:
  `postgres://postgres.[REF]:[DB-PASSWORD]@aws-[REGION].pooler.supabase.com:6543/postgres`
- **Transaction mode does not support prepared statements — you must disable them:**
  - `pg` (node-postgres): don't pass a `name` to queries; `postgres.js`: `postgres(url, { prepare: false })`
  - `asyncpg` (Python): `statement_cache_size=0` on `connect()`/`create_pool()`
  - Prisma: append `?pgbouncer=true` (and `&connection_limit=1`)
- Keep per-instance pool small (`connection_limit=1`–`5`); Supavisor's **pool size** caps backend
  connections per role+db, and **session (5432) + transaction (6543) share that budget**.
- Grab strings from dashboard **Connect** button or **Project Settings → Database**.

### Path B — supabase-js / PostgREST `.upsert()` (HTTP, no DB driver)

- Authenticate with the **`service_role` key** (server-side only — it carries `BYPASSRLS` and skips
  all RLS; never ship it to a client). Pass it in the `apikey` header (and `Authorization: Bearer`).
- The `anon` key is RLS-constrained and meant for public clients — not for a backend copy job.
- Good for modest volumes / when you don't want to manage a Postgres connection. Note: **Supabase
  network restrictions do NOT apply to the HTTP API**, only to Postgres+pooler (see networking).

---

## Upsert & idempotency

The copy must be **idempotent** — re-running after a retry or overlapping watermark must not
duplicate rows. Always upsert on a stable key, never blind-insert.

- **Raw SQL (Path A)**:
  ```sql
  INSERT INTO target (id, col_a, col_b, updated_at)
  VALUES (...)
  ON CONFLICT (id) DO UPDATE
    SET col_a = EXCLUDED.col_a, col_b = EXCLUDED.col_b, updated_at = EXCLUDED.updated_at;
  ```
  Pass multi-row VALUES for batch upserts in one round-trip.
- **PostgREST / supabase-js (Path B)**: POST with header `Prefer: resolution=merge-duplicates`
  (or `resolution=ignore-duplicates`). Default conflict target is the primary key; for a different
  UNIQUE column use `on_conflict` (REST) / `onConflict` (supabase-js). Pass an **array of rows** to
  `.upsert([...], { onConflict: 'id' })` for a single bulk request.
- Ensure the target has a PK or UNIQUE constraint matching your conflict target, or upsert silently
  inserts duplicates.

### Cross-engine type mapping (MySQL/SQL → Supabase Postgres)

Copying from MySQL or Azure SQL into Postgres is a **cross-engine** copy — map types in the
transform step, don't assume 1:1:

| Source (MySQL) | Postgres target | Note |
|---|---|---|
| `TINYINT(1)` | `boolean` | MySQL booleans are `0/1` tinyints |
| `DATETIME` / `TIMESTAMP` | `timestamptz` | Normalize to UTC; MySQL `TIMESTAMP` is UTC-stored, `DATETIME` is naive |
| `INT UNSIGNED` / `BIGINT UNSIGNED` | `bigint` / `numeric` | Postgres has no unsigned ints — widen to avoid overflow |
| `ENUM(...)` | `text` + CHECK, or a Postgres `enum` | Pre-create the target enum if you want enforcement |
| `JSON` | `jsonb` | `jsonb` preferred in Postgres |
| `TINYBLOB`/`BLOB` | `bytea` | |
| `0000-00-00` dates | `NULL` | Invalid in Postgres — coerce in transform |

- Define the Supabase target schema explicitly (don't auto-create from a MySQL dump). Make the
  watermark column and PK first-class so upsert conflict targets are stable.
- Build a small column-mapping dict in the Function rather than relying on driver coercion.

---

## Incremental / CDC sync & watermarks

- **Watermark column**: pick a monotonically increasing source column — `rowversion`/`ROWVERSION`
  (Azure SQL, best — gap-free and update-aware), `updated_at` timestamp, or Cosmos `_ts`. On each
  run: `SELECT … WHERE watermark > @last ORDER BY watermark`, upsert, then persist the new max.
- **Watermark storage**: keep the last-synced value durably outside the function process —
  Azure Table Storage / Blob, or a small control row in the Supabase target itself
  (`sync_state(table_name, last_watermark)`). Update it **after** a successful batch commit.
- **Overlap, don't gap**: use `>=` with dedup-by-upsert, or subtract a small safety lag, to avoid
  missing rows committed in the same tick. Idempotent upserts make overlap harmless.
- **Deletes**: change feed / change tracking handle deletes differently. Cosmos change feed does
  **not** emit deletes — use soft-delete tombstones. Azure SQL trigger emits `Operation=Delete`.
  For timestamp polling, deletes are invisible — reconcile periodically or soft-delete at source.

---

## Batching & large copies

- Read and write in **chunks** (e.g. 500–5,000 rows). Multi-row `INSERT … ON CONFLICT` or `COPY`
  beats row-by-row by orders of magnitude. Commit per batch so a failure only retries one batch.
- **Initial backfill of a large table**: use **Durable Functions fan-out/fan-in** — an orchestrator
  partitions the keyspace (e.g. by id range or date), dispatches parallel activity functions (don't
  await each; collect tasks), then fans in with `Task.WhenAll` / `context.task_all`. The SDK handles
  parallelism + checkpointing. For very large fan-outs, subdivide via sub-orchestrations.
- For one-time/bulk migrations of an entire database, consider **Azure Database Migration Service**
  or a `pg_dump`/`COPY` pipeline instead of a Function — Functions shine for *ongoing incremental* sync.
- Mind Function timeouts: Consumption caps at 5 min (10 max); Flex defaults to 30 min. Long backfills
  belong in Durable Functions or Premium/Flex with raised timeout.

---

## Secrets & Key Vault

- Store the **Supabase DB password / service_role key** in Key Vault; reference from app settings:
  `@Microsoft.KeyVault(SecretUri=https://myvault.vault.azure.net/secrets/supabase-db-password)`
  or `@Microsoft.KeyVault(VaultName=myvault;SecretName=supabase-db-password)`. App code reads the
  setting normally — no code change.
- The Function's **system-assigned managed identity** resolves the reference; grant it **Key Vault
  Secrets User** (RBAC) or **Get** secrets (access-policy). For a user-assigned identity set
  `keyVaultReferenceIdentity`.
- Versionless references auto-refresh on rotation within ~24 h (platform cache). For the source
  Azure DB, prefer **managed identity over any stored password** — nothing to put in Key Vault.

---

## Networking & static outbound IP

Needed when Supabase **network restrictions** lock the DB/pooler to an allowlist.

- **Consumption-plan outbound IPs are shared and NOT static**; autoscale can change them anytime
  (even on Premium the reported IPs aren't a reliable allowlist).
- **Static egress = VNet integration + NAT Gateway.** Supported on **Premium (EP1+)**, **Flex
  Consumption**, and **Dedicated** — *not* classic Consumption. Setup: regional VNet integration into
  an empty subnet → Standard regional Public IP → NAT Gateway with that IP, associated to the subnet.
  Ensure `vnetRouteAllEnabled = 1` (legacy `WEBSITE_VNET_ROUTE_ALL = 1`). All egress then uses the
  static IP.
- **Supabase side**: add the Function's static IP as a **CIDR** in Database Settings → Network
  Restrictions. A new list **replaces** the old one — include existing CIDRs. Add both IPv4 and IPv6
  if direct connections resolve to IPv6. **Caveat: network restrictions cover Postgres + pooler only,
  NOT the HTTPS/PostgREST API** — so an allowlist protects Path A, not Path B.

---

## Error handling & retries

- **Idempotent upserts** (above) make at-least-once delivery safe — retries can't duplicate.
- **Transient DB errors** (pooler connection reset, timeout): retry with exponential backoff +
  jitter; cap attempts. Re-acquire the connection from the pool on a broken-connection error.
- **Token expiry** (Entra auth to source): refresh on auth-failed errors; the credential object
  caches tokens, so just re-fetch.
- **SQL trigger retry semantics**: a failed batch retries after 60 s; a row failing 5× in a row is
  permanently skipped — monitor for poison rows.
- **Poison/oversized batches**: on batch failure, split and retry, or dead-letter the offending rows
  to Storage/Service Bus for out-of-band inspection. Never let one bad row stall the whole sync.
- **Observability**: log batch counts, watermark advance, and durations to Application Insights
  (`APPLICATIONINSIGHTS_CONNECTION_STRING`). Alert if watermark stops advancing.

---

## End-to-end skeleton (Python, Timer-triggered)

Timer-triggered incremental copy from Azure SQL → Supabase via the transaction-mode pooler. Clients
are module-scoped (static-client rule); secrets come from Key Vault-referenced app settings.

```python
import os, datetime, azure.functions as func
import pyodbc                      # source: Azure SQL
import psycopg                     # destination: Supabase Postgres

app = func.FunctionApp()

# --- module scope: created once per worker, reused across invocations ---
SRC_CONN = os.environ["AZURE_SQL_CONNECTION"]          # MI: "...Authentication=Active Directory Managed Identity;..."
# Supavisor transaction pooler (6543); statement_cache_size=0 disables prepared statements.
DST_DSN = os.environ["SUPABASE_POOLER_DSN"]            # postgres://postgres.<ref>:<pwd>@aws-<region>.pooler.supabase.com:6543/postgres
_dst_pool = psycopg.connect(DST_DSN, autocommit=False, prepare_threshold=None)

WATERMARK_BLOB = "sync_state/orders.txt"               # or a control row in Supabase
BATCH = 2000

@app.timer_trigger(schedule="0 */5 * * * *", arg_name="timer", run_on_startup=False)
def sync_orders(timer: func.TimerRequest) -> None:
    last = read_watermark()                            # e.g. from Table/Blob storage
    with pyodbc.connect(SRC_CONN) as src:
        rows = src.execute(
            "SELECT id, customer, total, updated_at FROM dbo.Orders "
            "WHERE updated_at > ? ORDER BY updated_at", last).fetchmany(BATCH)
    if not rows:
        return
    with _dst_pool.cursor() as cur:
        cur.executemany(
            "INSERT INTO orders (id, customer, total, updated_at) VALUES (%s,%s,%s,%s) "
            "ON CONFLICT (id) DO UPDATE SET customer=EXCLUDED.customer, "
            "total=EXCLUDED.total, updated_at=EXCLUDED.updated_at",
            [(r.id, r.customer, r.total, r.updated_at) for r in rows])
        _dst_pool.commit()
    write_watermark(max(r.updated_at for r in rows))   # advance only after successful commit
```

Node equivalents: source `mssql`/`tedious` or `pg`; destination `pg` with a module-scoped `Pool`
and **no named queries** (so no prepared statements) against port 6543.
