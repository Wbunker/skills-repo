# AWS QuickSight — CLI Reference
For service concepts, see [quicksight-capabilities.md](quicksight-capabilities.md).

## Amazon QuickSight

```bash
# --- Data sources ---
aws quicksight create-data-source \
  --aws-account-id 123456789012 \
  --data-source-id my-redshift-source \
  --name "My Redshift" \
  --type REDSHIFT \
  --data-source-parameters '{
    "RedshiftParameters": {
      "Host": "my-cluster.abc.us-east-1.redshift.amazonaws.com",
      "Port": 5439,
      "Database": "dev"
    }
  }' \
  --credentials '{
    "CredentialPair": {"Username": "analyst", "Password": "P@ssw0rd!"}
  }' \
  --permissions '[{"Principal": "arn:aws:quicksight:us-east-1:123456789012:user/default/admin", "Actions": ["quicksight:DescribeDataSource","quicksight:DescribeDataSourcePermissions","quicksight:PassDataSource"]}]'

aws quicksight list-data-sources --aws-account-id 123456789012

# --- Datasets ---
aws quicksight create-data-set \
  --aws-account-id 123456789012 \
  --data-set-id orders-dataset \
  --name "Orders Dataset" \
  --import-mode SPICE \
  --physical-table-map '{
    "orders-table": {
      "RelationalTable": {
        "DataSourceArn": "arn:aws:quicksight:us-east-1:123456789012:datasource/my-redshift-source",
        "Schema": "public",
        "Name": "orders",
        "InputColumns": [
          {"Name": "order_id", "Type": "STRING"},
          {"Name": "amount", "Type": "DECIMAL"}
        ]
      }
    }
  }'

aws quicksight list-data-sets --aws-account-id 123456789012

# Refresh SPICE dataset
aws quicksight create-ingestion \
  --aws-account-id 123456789012 \
  --data-set-id orders-dataset \
  --ingestion-id manual-refresh-$(date +%Y%m%d%H%M%S) \
  --ingestion-type FULL_REFRESH

# --- Analyses ---
aws quicksight create-analysis \
  --aws-account-id 123456789012 \
  --analysis-id my-analysis \
  --name "Sales Analysis" \
  --source-entity '{
    "SourceTemplate": {
      "Arn": "arn:aws:quicksight:us-east-1:123456789012:template/my-template",
      "DataSetReferences": [{"DataSetPlaceholder": "orders", "DataSetArn": "arn:aws:quicksight:us-east-1:123456789012:dataset/orders-dataset"}]
    }
  }'

# --- Dashboards ---
aws quicksight create-dashboard \
  --aws-account-id 123456789012 \
  --dashboard-id sales-dashboard \
  --name "Sales Dashboard" \
  --source-entity '{
    "SourceAnalysis": {
      "Arn": "arn:aws:quicksight:us-east-1:123456789012:analysis/my-analysis",
      "DataSetReferences": [{"DataSetPlaceholder": "orders", "DataSetArn": "arn:aws:quicksight:us-east-1:123456789012:dataset/orders-dataset"}]
    }
  }' \
  --version-description "v1"

aws quicksight describe-dashboard \
  --aws-account-id 123456789012 \
  --dashboard-id sales-dashboard

aws quicksight list-dashboards --aws-account-id 123456789012

# --- User management ---
aws quicksight register-user \
  --aws-account-id 123456789012 \
  --namespace default \
  --identity-type IAM \
  --iam-arn arn:aws:iam::123456789012:user/analyst \
  --email analyst@example.com \
  --user-role AUTHOR

aws quicksight describe-user \
  --aws-account-id 123456789012 \
  --namespace default \
  --user-name analyst

# --- Groups ---
aws quicksight create-group \
  --aws-account-id 123456789012 \
  --namespace default \
  --group-name analysts \
  --description "Data analyst group"

aws quicksight create-group-membership \
  --aws-account-id 123456789012 \
  --namespace default \
  --group-name analysts \
  --member-name analyst

aws quicksight list-group-memberships \
  --aws-account-id 123456789012 \
  --namespace default \
  --group-name analysts
```
