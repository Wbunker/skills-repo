# AWS Lake Formation & DataZone — CLI Reference
For service concepts, see [lake-formation-datazone-capabilities.md](lake-formation-datazone-capabilities.md).

## AWS Lake Formation

```bash
# --- Register S3 location ---
aws lakeformation register-resource \
  --resource-arn arn:aws:s3:::my-data-lake \
  --role-arn arn:aws:iam::123456789012:role/LakeFormationRole \
  --use-service-linked-role

aws lakeformation list-resources
aws lakeformation deregister-resource --resource-arn arn:aws:s3:::my-data-lake

# --- Grant permissions ---
# Database-level
aws lakeformation grant-permissions \
  --principal DataLakePrincipalIdentifier=arn:aws:iam::123456789012:role/AnalystRole \
  --resource '{"Database": {"Name": "my_db"}}' \
  --permissions DESCRIBE

# Table-level
aws lakeformation grant-permissions \
  --principal DataLakePrincipalIdentifier=arn:aws:iam::123456789012:role/AnalystRole \
  --resource '{"Table": {"DatabaseName": "my_db", "Name": "orders"}}' \
  --permissions SELECT

# Column-level (specific columns only)
aws lakeformation grant-permissions \
  --principal DataLakePrincipalIdentifier=arn:aws:iam::123456789012:role/AnalystRole \
  --resource '{
    "TableWithColumns": {
      "DatabaseName": "my_db",
      "Name": "customers",
      "ColumnNames": ["customer_id", "region", "signup_date"]
    }
  }' \
  --permissions SELECT

# Batch grant
aws lakeformation batch-grant-permissions \
  --entries '[
    {
      "Id": "grant-1",
      "Principal": {"DataLakePrincipalIdentifier": "arn:aws:iam::123456789012:role/AnalystRole"},
      "Resource": {"Table": {"DatabaseName": "my_db", "Name": "orders"}},
      "Permissions": ["SELECT"]
    },
    {
      "Id": "grant-2",
      "Principal": {"DataLakePrincipalIdentifier": "arn:aws:iam::123456789012:role/AnalystRole"},
      "Resource": {"Table": {"DatabaseName": "my_db", "Name": "products"}},
      "Permissions": ["SELECT"]
    }
  ]'

# --- Revoke permissions ---
aws lakeformation revoke-permissions \
  --principal DataLakePrincipalIdentifier=arn:aws:iam::123456789012:role/AnalystRole \
  --resource '{"Table": {"DatabaseName": "my_db", "Name": "orders"}}' \
  --permissions SELECT

# --- Inspect effective permissions ---
aws lakeformation get-effective-permissions-for-path \
  --resource-arn arn:aws:glue:us-east-1:123456789012:table/my_db/orders

aws lakeformation list-permissions \
  --resource '{"Table": {"DatabaseName": "my_db", "Name": "orders"}}'

# --- LF-Tags (ABAC) ---
aws lakeformation create-lf-tag \
  --tag-key Sensitivity \
  --tag-values PII Confidential Internal Public

aws lakeformation list-lf-tags

aws lakeformation add-lf-tags-to-resource \
  --resource '{
    "TableWithColumns": {
      "DatabaseName": "my_db",
      "Name": "customers",
      "ColumnNames": ["ssn", "email", "phone"]
    }
  }' \
  --lf-tags '[{"TagKey": "Sensitivity", "TagValues": ["PII"]}]'

# Grant via LF-Tag expression
aws lakeformation grant-permissions \
  --principal DataLakePrincipalIdentifier=arn:aws:iam::123456789012:role/AnalystRole \
  --resource '{
    "LFTagPolicy": {
      "ResourceType": "TABLE",
      "Expression": [{"TagKey": "Sensitivity", "TagValues": ["Internal", "Public"]}]
    }
  }' \
  --permissions SELECT \
  --permissions-with-grant-option SELECT

# --- Data cell filters (row + column) ---
aws lakeformation create-data-cells-filter \
  --table-data '{
    "TableCatalogId": "123456789012",
    "DatabaseName": "my_db",
    "TableName": "orders",
    "Name": "us_orders_no_pii",
    "RowFilter": {
      "FilterExpression": "region = '\''us-east-1'\''"
    },
    "ColumnNames": ["order_id", "amount", "region", "order_date"]
  }'

aws lakeformation list-data-cells-filter \
  --table '{"DatabaseName": "my_db", "Name": "orders"}'
```

---

## AWS DataZone

```bash
# --- Domain management ---
aws datazone create-domain \
  --name my-data-domain \
  --description "Central data domain for analytics" \
  --domain-execution-role arn:aws:iam::123456789012:role/DataZoneDomainRole \
  --single-sign-on '{"type": "IAM_IDC"}'

aws datazone get-domain --identifier d-abc123def456

# --- Projects ---
aws datazone create-project \
  --domain-identifier d-abc123def456 \
  --name analytics-team \
  --description "Analytics team project"

aws datazone list-projects --domain-identifier d-abc123def456

# --- Data sources (import from Glue/Redshift) ---
aws datazone create-data-source \
  --domain-identifier d-abc123def456 \
  --project-identifier p-abc123 \
  --name glue-data-source \
  --type GLUE \
  --configuration '{
    "glueRunConfiguration": {
      "relationalFilterConfigurations": [
        {"databaseName": "my_db", "filterExpressions": [{"type": "INCLUDE", "expression": "*"}]}
      ]
    }
  }'

aws datazone start-data-source-run \
  --domain-identifier d-abc123def456 \
  --data-source-identifier ds-abc123

# --- Assets ---
aws datazone create-asset \
  --domain-identifier d-abc123def456 \
  --owning-project-identifier p-abc123 \
  --name orders-table \
  --type-identifier amazon.datazone.RelationalTableAssetType \
  --forms-input '[{"formName": "AssetCommonDetailsForm", "content": "{\"description\": \"Daily orders data\"}"}]'

aws datazone search \
  --domain-identifier d-abc123def456 \
  --search-scope ASSET \
  --search-text "orders"

# --- Subscriptions ---
aws datazone create-subscription-request \
  --domain-identifier d-abc123def456 \
  --subscribed-listings '[{"identifier": "l-abc123def456"}]' \
  --subscribed-principals '[{"project": {"identifier": "p-consumer123"}}]' \
  --request-reason "Need orders data for revenue analysis"

aws datazone list-subscription-requests --domain-identifier d-abc123def456

aws datazone accept-subscription-request \
  --domain-identifier d-abc123def456 \
  --identifier sr-abc123
```
