---
name: prod-db-readonly-query
description: >
  Run read-only verification SELECTs against any Curantis prod RDS Postgres (patient-charts,
  notes, billing-claims, activities, etc.) via SSM port-forward through one of the prod
  SSM-managed EC2s. Also documents the canonical chain for verifying lookup-table value sets
  (Liquibase seed → Java enum → Prisma schema → prod DB). Use when: verifying a lookup-table
  value set, sanity-checking how many rows reference an enum id, confirming an FK is intact in
  prod, comparing what the docs/code claim versus what production actually has, or any other
  read-only "what is in prod right now?" question. Do NOT use for writes or migrations — those
  go through the audited `sup-sql-executor-prod` Jira-driven Lambda workflow.
---

# Prod DB Read-Only Query (Curantis)

## When to use which path

| Path | Use for | Audit trail |
|---|---|---|
| **SSM port-forward + psql/psycopg2** (this skill) | Ad-hoc read-only verification, value-set checks, FK sanity, row counts | None — keep it `SELECT` only |
| **`sup-sql-executor-prod` Lambda** | Writes, schema changes, anything needing approval, anything destructive | Jira SUP ticket → DynamoDB queue → human approval → execution |

If a query mutates anything, stop and use `sup-sql-executor-prod`. This skill exists *only* for reads.

## Prereqs (one-time)

- AWS profile `curantis_prod` configured (`aws sts get-caller-identity --profile curantis_prod` returns account `966605421973`)
- IAM permissions: `ssm:StartSession`, `secretsmanager:GetSecretValue`, `rds:DescribeDBInstances`
- `session-manager-plugin` installed. If `which session-manager-plugin` is empty, install without sudo:
  ```bash
  cd /tmp && curl -sSL "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/mac/sessionmanager-bundle.zip" -o ssm-bundle.zip
  unzip -q -o ssm-bundle.zip
  mkdir -p ~/bin && cp sessionmanager-bundle/bin/session-manager-plugin ~/bin/ && chmod +x ~/bin/session-manager-plugin
  export PATH="$HOME/bin:$PATH"   # add to ~/.zshrc to make permanent
  ```
- `psql` or `python3 -c "import psycopg2"` — either works.

## Topology (prod, account 966605421973, us-west-2)

- **VPC:** `vpc-09db9fc21342b7caf`
- **RDS Postgres SG:** `sg-06ffa9be1ec86dc20`
- **RDS hostname pattern:** `<service>.cgbhqwjv3il6.us-west-2.rds.amazonaws.com:5432`
- **Available service DBs** (from `aws --profile curantis_prod --region us-west-2 rds describe-db-instances`):
  `activities`, `bereaved-management`, `billing-claims`, `codes`, `community-bereaved`,
  `facilities`, `his`, `importer`, `jasperserver`, `meds-admin-records`, `notes`,
  `patient-benefits`, `patient-certification`, `patient-charts`, `patient-chart-status`,
  `pbm`, `rbac` (MySQL, port 3306), `resource-management`, `rules`, `signatures`,
  `volunteer-management`, plus 2 mirthdb instances.
  (Re-run `describe-db-instances` to confirm — list changes over time.)
- **SSM-managed EC2s** in the prod VPC (any one works as the port-forward target):
  ```
  i-0335399fb3830e2b9   10.75.3.62
  i-0e5e9dc43e299e7a6   10.75.4.15
  i-06ed591fe1d81ce1d   10.75.3.57
  ```
  Confirm one is online: `aws --profile curantis_prod --region us-west-2 ssm describe-instance-information`
- **Credentials secret pattern:** `sup-sql-executor/prod/db/<service-name>` in Secrets Manager.
  Schema: `{username, password, port}` — typically `username=jira_sql_bot`. (Hostname is NOT in the secret; use the pattern above.)

## Standard procedure

Replace `<SERVICE>` (e.g., `patient-charts`) and `<DBNAME>` (e.g., `patient_charts` — note the underscore vs hyphen) below.

### 1. Start port-forward in the background

```bash
export PATH="$HOME/bin:$PATH"
AWS_PROFILE=curantis_prod aws --region us-west-2 ssm start-session \
  --target i-0335399fb3830e2b9 \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters '{"host":["<SERVICE>.cgbhqwjv3il6.us-west-2.rds.amazonaws.com"],"portNumber":["5432"],"localPortNumber":["15432"]}' &
SSM_PID=$!

# Wait until the local port is listening (don't sleep blindly)
until nc -z localhost 15432 2>/dev/null; do sleep 1; done
echo "tunnel up"
```

### 2. Run the SELECT (psycopg2, recommended for structured output)

```bash
PGPASSWORD=$(aws --profile curantis_prod --region us-west-2 secretsmanager get-secret-value \
  --secret-id "sup-sql-executor/prod/db/<SERVICE>" --query SecretString --output text \
  | python3 -c "import json,sys;print(json.load(sys.stdin)['password'])") \
python3 - <<'PY'
import os, psycopg2
conn = psycopg2.connect(
    host="127.0.0.1", port=15432, dbname="<DBNAME>",
    user="jira_sql_bot", password=os.environ["PGPASSWORD"],
    sslmode="require", connect_timeout=10,
)
conn.autocommit = True
with conn.cursor() as cur:
    cur.execute("SET statement_timeout = '30s'")     # always cap; avoids runaway scans
    cur.execute("SET default_transaction_read_only = on")  # belt + suspenders
    cur.execute("SELECT id, description FROM your_lookup_table ORDER BY id")
    for r in cur.fetchall():
        print(r)
PY
```

Or with psql (one-shot, simpler for ad-hoc):

```bash
PGPASSWORD=$(aws --profile curantis_prod --region us-west-2 secretsmanager get-secret-value \
  --secret-id "sup-sql-executor/prod/db/<SERVICE>" --query SecretString --output text \
  | python3 -c "import json,sys;print(json.load(sys.stdin)['password'])") \
psql "host=127.0.0.1 port=15432 dbname=<DBNAME> user=jira_sql_bot sslmode=require" \
  -v ON_ERROR_STOP=1 \
  -c "SET default_transaction_read_only = on; SET statement_timeout='30s';" \
  -c "SELECT id, description FROM your_lookup_table ORDER BY id;"
```

### 3. Tear down the tunnel

```bash
lsof -nPi :15432 2>/dev/null | awk 'NR>1 {print $2}' | sort -u | xargs -r kill 2>/dev/null
nc -z localhost 15432 2>&1 && echo "still up" || echo "tunnel closed"
```

(`pkill -f session-manager-plugin` also works but kills *all* sessions.)

## Safety rules

- **Read-only only.** Set `default_transaction_read_only = on` and only run `SELECT`. Anything else, switch to `sup-sql-executor-prod`.
- **Always set `statement_timeout`.** Production query slots are shared — a runaway scan can hurt the service.
- **No PHI in output.** When summarizing results, never dump patient names / SSNs / DOBs. Aggregate counts and lookup-table values are fine; row-level patient data is not.
- **One question per session.** Don't leave the tunnel up between unrelated investigations.
- **Note `rbac` is MySQL on port 3306**, not Postgres. The pattern still works (port-forward to the MySQL host) but use `mysql` client and `pymysql` instead of psql/psycopg2.

## Recipe — Verify a lookup-table value set (canonical chain)

For any "what are the valid values of enum X?" question owned by a clinical service, walk all four sources and confirm they agree. If they don't, the in-process Java enum wins for what's on the FHIR wire (because producers serialize from the enum's `getDescription()`).

| # | Source | Path / command | Why |
|---|---|---|---|
| 1 | Liquibase seed changelog | `domains/clinical/libraries/clinical-domain/services/<svc>/src/main/resources/db-change-logs/*.xml` — grep for `tableName="<table>"` `<insert>` then any later `<update>` / `<addColumn>` | Historical record. Initial seeds + every renumber + every column add. |
| 2 | Prisma model | `domains/clinical/libraries/clinical-domain/libraries/database/prisma/schema.prisma` — find `model <CamelCaseName>` mapped to `@@map("<table>")` | Current schema source of truth (Liquibase is frozen for new changes). |
| 3 | Java enum | `services/<svc>/src/main/java/.../models/enums/<Enum>.java` — the `fromId` switch is the canonical id→description map | What the service actually uses in-process; what producers serialize. |
| 4 | Prod DB | This skill — `SELECT * FROM <table> ORDER BY id` plus `SELECT <fk_id>, COUNT(*) FROM <usage_table> GROUP BY 1` | Empirical truth + which values are actually in use. |

If sources 1–3 say there are 10 values and the spec docs say 4, **the spec docs are wrong**. We have proven this at least once for `care_location_types` (REQ-MC-002A in the `enclara-integration` skill — was claimed 4, actually 10).

## Troubleshooting

- **`tunnel up` never prints** — confirm the SSM target is `Online` (`describe-instance-information`); confirm your IAM allows `ssm:StartSession` on that instance ARN.
- **`SSL connection has been closed unexpectedly`** — RDS requires `sslmode=require`. Both psql and psycopg2 connection strings above include it.
- **`password authentication failed for user "jira_sql_bot"`** — secret rotated; re-pull `sup-sql-executor/prod/db/<service>` and confirm `username` field still says `jira_sql_bot` (it could change to e.g. `jira_sql_bot_v2`).
- **`relation "<table>" does not exist`** — wrong schema; query `information_schema.columns` to find it: `SELECT table_schema, table_name FROM information_schema.columns WHERE column_name='<col>'`.
- **Hangs on `until nc -z`** — local port already in use; pick a different `localPortNumber` (e.g., 15433).
