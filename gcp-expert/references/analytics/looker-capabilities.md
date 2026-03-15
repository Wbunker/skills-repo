# Looker — Capabilities

## Purpose

Enterprise BI platform with a governed data modeling layer (LookML) and embedded analytics. Looker enables organizations to define business metrics once in code, then consistently query and visualize those metrics across the organization through dashboards, explores, and APIs. Contrast with Looker Studio (free, simpler, no semantic layer).

---

## Core Architecture

```
Data Warehouse (BigQuery, etc.)
        ↓
   LookML Model (semantic layer in Git)
        ↓
Looker Platform (explores, dashboards, schedules, APIs)
        ↓
End Users / Embedded Applications
```

---

## Core Concepts

| Concept | Description |
|---|---|
| LookML | YAML-like data modeling language; defines metrics, dimensions, and relationships in version-controlled files |
| Model | LookML file defining which database connection to use and which Explores to expose |
| Explore | Entry point for ad-hoc querying; JOIN of one or more Views; what users see in the Explore UI |
| View | LookML representation of a database table or derived table; contains dimensions and measures |
| Dimension | Non-aggregate field; maps to a column or expression; used in GROUP BY |
| Measure | Aggregate field (COUNT, SUM, AVG, etc.); defines the business metric |
| Derived Table | SQL query or LookML-defined virtual table; used for complex logic not available in raw tables |
| Persistent Derived Table (PDT) | Derived table materialized as a physical table in the database; rebuilt on schedule or trigger |
| Dashboard | Collection of tiles (visualizations) arranged on a canvas; shareable |
| Look | Single saved visualization (query result + chart config) |
| Schedule | Automated delivery of a Dashboard or Look (email, Slack, GCS, webhook) |
| Embed | Looker content embedded in external applications via signed URL or SSO embed |
| API | Looker REST API for programmatic access to queries, dashboards, users, and content |
| Git Integration | LookML stored in Git repository; development → staging → production promotion workflow |
| Instance | Deployed Looker server; cloud-hosted (Google Cloud) or customer-hosted (legacy) |

---

## LookML Overview

LookML files define the semantic layer:

```lookml
# view file: orders.view.lkml
view: orders {
  sql_table_name: `my_project.my_dataset.orders` ;;

  dimension: order_id {
    type: number
    primary_key: yes
    sql: ${TABLE}.order_id ;;
  }

  dimension: customer_id {
    type: number
    sql: ${TABLE}.customer_id ;;
  }

  dimension_group: created {
    type: time
    timeframes: [raw, date, week, month, year]
    sql: ${TABLE}.created_at ;;
  }

  measure: order_count {
    type: count
    drill_fields: [order_id, customer_id]
  }

  measure: total_revenue {
    type: sum
    sql: ${TABLE}.revenue ;;
    value_format_name: usd
  }

  measure: average_order_value {
    type: average
    sql: ${TABLE}.revenue ;;
    value_format_name: usd
  }
}

# model file: ecommerce.model.lkml
connection: "bigquery_connection"

include: "/views/*.view.lkml"

explore: orders {
  join: customers {
    type: left_outer
    sql_on: ${orders.customer_id} = ${customers.customer_id} ;;
    relationship: many_to_one
  }
}
```

---

## LookML Key Features

- **SQL injection via `$$` and `${}`**: reference other fields, tables, and computed values
- **Refinements**: extend or override existing views/explores without modifying original files (useful for marketplace blocks)
- **Extends**: inherit from parent views to avoid duplication
- **Datagroups**: define cache invalidation and PDT rebuild triggers based on SQL conditions or cron schedules
- **Access filters**: restrict query results based on user attributes (row-level security at semantic layer)
- **Required access grants**: control which Explores and fields a user can access
- **Liquid templating**: dynamic SQL generation based on user attributes or runtime parameters

---

## Derived Tables and PDTs

```lookml
# Regular derived table (computed at query time)
view: user_lifetime_value {
  derived_table: {
    sql: SELECT
           customer_id,
           SUM(revenue) AS lifetime_value,
           COUNT(*) AS total_orders
         FROM orders
         GROUP BY customer_id ;;
  }
  # dimensions and measures here...
}

# Persistent Derived Table (materialized in database)
view: user_ltv_pdt {
  derived_table: {
    sql: SELECT customer_id, SUM(revenue) AS ltv FROM orders GROUP BY 1 ;;
    datagroup_trigger: daily_datagroup   # rebuild trigger
    partition_keys: ["created_date"]
    cluster_keys: ["customer_id"]
    create_process: {
      sql_step: CREATE TABLE IF NOT EXISTS ... ;;
    }
  }
}
```

---

## Deployment Models

| Model | Description |
|---|---|
| Looker (Google Cloud hosted) | Managed instance on Google Cloud; Looker Core license; GCP Marketplace |
| Looker (customer-hosted) | Legacy; customer manages infrastructure; being phased out for new customers |
| Looker Studio | Separate free product; no LookML; simpler drag-drop; not for enterprise governance |

### Looker Core (Google Cloud Managed)
- Provisioned via `gcloud looker instances create` or Cloud Console
- Single-node or cluster; HA configuration
- VPC peering or Private Service Connect for database access
- Customer-managed encryption keys (CMEK) supported

---

## Looker vs Looker Studio

| Feature | Looker | Looker Studio |
|---|---|---|
| Cost | Paid (license per user or organization) | Free |
| Semantic layer | Yes (LookML) | No |
| Metric governance | Yes (single source of truth) | No |
| Git version control | Yes | No |
| Embedded analytics | Yes (signed embed, SSO embed) | Yes (iFrame embed) |
| API | Full REST API | Limited |
| Data sources | JDBC/native warehouse connectors | 1000+ connectors |
| Complexity | High (requires LookML developer) | Low (drag-drop) |
| Best for | Enterprise, governed BI | Ad-hoc, self-service, free |

---

## Looker APIs

Looker provides a comprehensive REST API:

| Category | Key Endpoints |
|---|---|
| Authentication | `POST /login` (returns access_token) |
| Queries | `POST /queries`, `POST /queries/run/{result_format}` |
| Looks | `GET /looks`, `POST /looks/{look_id}/run/{result_format}` |
| Dashboards | `GET /dashboards`, `POST /dashboards/{dashboard_id}/run_look` |
| Users | `GET /users`, `POST /users` |
| Folders | `GET /folders`, folder content management |
| Schedules | `GET /scheduled_plans`, `POST /scheduled_plans/run_once` |
| Embed | `POST /embed/sso_url` (signed SSO embed URL) |
| LookML | `GET /lookml_models`, `GET /lookml_models/{model_name}/explores/{explore_name}` |

**Authentication**: API client_id + client_secret; obtain access token valid for 1 hour; pass as `Authorization: token {access_token}` header.

---

## Looker Embedding

**Signed embed (iframe embed with SSO)**:
- Generate signed URL server-side using Looker embed secret
- Embed in `<iframe src="{signed_url}">` in your web application
- User identity and permissions carried in the signed URL
- No separate login required; transparent to end user

**Public embed**: embed without authentication; for public dashboards

**Looker Components (React)**: open-source component library for deeper integration

---

## Integration with GCP

- **BigQuery**: primary and deepest integration; supports BigQuery-specific SQL syntax in LookML; leverages BigQuery ML for in-database model prediction
- **Cloud SQL (MySQL, PostgreSQL)**: supported via Cloud SQL Auth Proxy or direct connection
- **Cloud Spanner**: supported via JDBC driver
- **Vertex AI**: Looker extensions can call Vertex AI APIs; LLM-powered natural language querying
- **Cloud Monitoring**: Looker metrics exported to Cloud Monitoring for operational visibility
- **Secret Manager**: store Looker database credentials in Secret Manager
- **IAP (Identity-Aware Proxy)**: for customer-hosted Looker instances behind a load balancer

---

## Monitoring and Administration

- **System Activity Explores**: built-in LookML model for Looker usage analytics (user activity, query history, API usage, content views, PDT status)
- **Looker Admin panel**: user management, group/role assignment, database connections, schedules, API keys
- **Git workflow**: use Looker's built-in Git integration or CI/CD pipelines for LookML deployments
- **lookml-linter**: community CLI tool for LookML style and correctness validation
- **Henry**: open-source Looker cleanup tool (find unused content, fields, explores)
