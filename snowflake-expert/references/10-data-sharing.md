# Configuring and Managing Secure Data Sharing

Reference for data sharing, Snowflake Marketplace, data exchanges, clean rooms, and Snowgrid.

## Table of Contents
- [Data Sharing Overview](#data-sharing-overview)
- [Direct Secure Data Sharing](#direct-secure-data-sharing)
- [Snowflake Marketplace](#snowflake-marketplace)
- [Private Data Exchange](#private-data-exchange)
- [Data Clean Rooms](#data-clean-rooms)
- [Design and Security Considerations](#design-and-security-considerations)

## Data Sharing Overview

Snowflake's data sharing is **zero-copy** — no data movement, no ETL, no storage duplication.

### How It Works
```
Provider Account                    Consumer Account
┌──────────────┐                   ┌──────────────┐
│  Source DB    │ ──── Share ────→  │  Read-Only   │
│  (owns data) │   (metadata only) │  Database     │
└──────────────┘                   └──────────────┘
```

- Provider creates a **share** containing database objects
- Consumer creates a **database from the share**
- Consumer queries provider's data in real-time (always current)
- **No data copied** — consumer reads from provider's storage
- Consumer pays only for compute (their own warehouse)

### Sharing Approaches
| Method | Use Case |
|--------|----------|
| **Direct sharing** | Known consumer accounts (same region/cloud) |
| **Listing (Marketplace)** | Public or private distribution |
| **Private Data Exchange** | Curated group of organizations |
| **Reader Account** | Share with non-Snowflake users |
| **Replication + Sharing** | Cross-region/cross-cloud sharing |

## Direct Secure Data Sharing

### Provider: Creating an Outbound Share
```sql
-- 1. Create share
CREATE SHARE sales_share COMMENT = 'Monthly sales data for partners';

-- 2. Grant database usage to share
GRANT USAGE ON DATABASE analytics_db TO SHARE sales_share;
GRANT USAGE ON SCHEMA analytics_db.public TO SHARE sales_share;

-- 3. Grant table/view access
GRANT SELECT ON TABLE analytics_db.public.monthly_sales TO SHARE sales_share;
GRANT SELECT ON VIEW analytics_db.public.partner_summary TO SHARE sales_share;

-- 4. Add consumer accounts
ALTER SHARE sales_share ADD ACCOUNTS = consumer_org.consumer_acct;

-- Add multiple consumers
ALTER SHARE sales_share ADD ACCOUNTS = org1.acct1, org2.acct2;

-- Secure views are recommended for sharing (hide underlying logic)
GRANT SELECT ON VIEW analytics_db.public.secure_partner_view TO SHARE sales_share;
```

### Consumer: Using Inbound Shares
```sql
-- View available shares
SHOW SHARES;

-- Create database from share
CREATE DATABASE partner_data FROM SHARE provider_org.provider_acct.sales_share;

-- Grant access to roles in consumer account
GRANT IMPORTED PRIVILEGES ON DATABASE partner_data TO ROLE analyst;

-- Query shared data (always up-to-date)
SELECT * FROM partner_data.public.monthly_sales;
```

### Reader Accounts (for non-Snowflake consumers)
```sql
-- Provider creates a managed reader account
CREATE MANAGED ACCOUNT partner_reader
  ADMIN_NAME = 'partner_admin'
  ADMIN_PASSWORD = 'StrongP@ss!'
  TYPE = READER;

-- Add reader account to share
ALTER SHARE sales_share ADD ACCOUNTS = <reader_account_locator>;

-- Provider pays for reader account's compute
-- Create warehouse in reader account for queries
```

### Sharing Functions and Procedures
```sql
-- Share secure UDFs
GRANT USAGE ON FUNCTION analytics_db.public.calc_score(INT) TO SHARE sales_share;

-- Share secure views (recommended over raw tables)
CREATE SECURE VIEW analytics_db.public.partner_view AS
SELECT customer_id, region, total_sales
FROM orders
WHERE partner_id = CURRENT_ACCOUNT();  -- filter per consumer
```

## Snowflake Marketplace

### For Consumers (Shopping)
1. Navigate to **Marketplace** in Snowsight
2. Browse or search data listings
3. **Free listings:** Click "Get" → creates database instantly
4. **Paid listings:** Request access → approval workflow
5. **Personalized listings:** Provider customizes data for you

```sql
-- After getting a listing, query it like any database
SELECT * FROM WEATHER_DATA.PUBLIC.DAILY_TEMPERATURES
WHERE CITY = 'New York' AND DATE >= '2024-01-01';
```

### For Providers (Publishing)
1. Create share with data to publish
2. Create a listing in Provider Studio
3. Choose: **Standard** (same data for all) or **Personalized** (per-consumer)
4. Set terms, description, sample queries
5. Publish to Marketplace (public) or specific consumers (private)

### Standard vs Personalized Listings
| Feature | Standard | Personalized |
|---------|----------|-------------|
| Same data for all | Yes | No — customized per consumer |
| Auto-fulfillment | Yes | Requires provider approval |
| Use case | Public datasets | Filtered/segmented data |
| Implementation | Single share | Secure views with `CURRENT_ACCOUNT()` |

## Private Data Exchange

A curated, invite-only marketplace for a group of organizations.

```
Data Exchange
├── Organization A (provider & consumer)
├── Organization B (provider & consumer)
├── Organization C (consumer only)
└── Organization D (provider only)
```

- Created and managed by an organization
- Members can publish and consume listings
- Not publicly visible on the Marketplace
- Use case: industry consortiums, supply chains, partner ecosystems

## Data Clean Rooms

Enable two or more parties to combine data for analysis **without exposing raw data**.

### Concept
```
Party A (Provider)          Clean Room           Party B (Consumer)
┌─────────────────┐   ┌──────────────────┐   ┌─────────────────┐
│ Customer emails  │──→│  Overlap analysis │←──│ Customer emails  │
│ Purchase data    │   │  (no raw data     │   │ Campaign data    │
│                  │   │   exposed)         │   │                  │
└─────────────────┘   └──────────────────┘   └─────────────────┘
                            ↓
                      Aggregated results
                      (counts, rates, etc.)
```

### Implementation
```sql
-- Provider creates secure functions that limit what consumer can compute
CREATE SECURE FUNCTION overlap_count(consumer_table STRING)
  RETURNS TABLE (overlap_count INT)
  AS $$
    SELECT COUNT(DISTINCT a.email)
    FROM provider_data.customers a
    INNER JOIN IDENTIFIER(consumer_table) b
      ON a.hashed_email = b.hashed_email
  $$;

-- Row access policies and masking policies enforce data boundaries
-- Consumer can call functions but never see raw data
```

### Snowflake Clean Room Features
- **Template-based:** Pre-defined analysis templates
- **Privacy controls:** Minimum aggregation thresholds
- **Audit trail:** Full access history
- **No data movement:** Zero-copy architecture

## Design and Security Considerations

### Share Design
- Share **secure views** rather than base tables
- Use `CURRENT_ACCOUNT()` in views to filter data per consumer
- Include only necessary columns and rows
- Test with consumer role before publishing

### Security
```sql
-- Secure views prevent DDL inspection
CREATE SECURE VIEW shared_view AS
SELECT col1, col2 FROM base_table WHERE region = 'US';

-- Consumers cannot:
-- - See the view definition
-- - See the underlying tables
-- - Modify data
-- - Access data outside the share grant
```

### Performance
- Consumer queries use **consumer's** warehouse (provider pays nothing for queries)
- Shared data benefits from provider's clustering and optimization
- Cross-region sharing requires replication (adds latency and cost)

### Key Differences: Sharing vs Cloning
| Feature | Data Sharing | Zero-Copy Cloning |
|---------|-------------|-------------------|
| Audience | Different accounts | Same account |
| Data movement | None (live link) | None initially (diverges over time) |
| Consumer can write | No (read-only) | Yes |
| Time Travel on shared data | Provider's Time Travel settings apply; consumers cannot use Time Travel on shared objects | Full Time Travel on clone |
