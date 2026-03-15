# AWS Clean Rooms & Entity Resolution — CLI Reference

For service concepts, see [clean-rooms-entity-resolution-capabilities.md](clean-rooms-entity-resolution-capabilities.md).

## AWS Clean Rooms

```bash
# --- Collaboration ---
aws cleanrooms create-collaboration \
  --name ad-measurement-collab \
  --description "Advertising measurement collaboration" \
  --members '[
    {
      "accountId": "210987654321",
      "displayName": "PartnerCompany",
      "memberAbilities": ["CAN_QUERY"],
      "paymentConfiguration": {"queryCompute": {"isResponsible": false}}
    }
  ]' \
  --creator-member-abilities CAN_QUERY CAN_RECEIVE_RESULTS \
  --creator-display-name "MyCompany" \
  --query-log-status ENABLED

aws cleanrooms list-collaborations
aws cleanrooms get-collaboration --collaboration-identifier col-abc123

aws cleanrooms delete-collaboration --collaboration-identifier col-abc123

# --- Membership (joining a collaboration) ---
aws cleanrooms create-membership \
  --collaboration-identifier col-abc123 \
  --query-log-status ENABLED \
  --default-result-configuration '{
    "outputConfiguration": {
      "s3": {
        "resultFormat": "CSV",
        "bucket": "my-results-bucket",
        "keyPrefix": "clean-rooms-results/"
      }
    },
    "roleArn": "arn:aws:iam::123456789012:role/CleanRoomsRole"
  }'

aws cleanrooms list-memberships
aws cleanrooms get-membership --membership-identifier mem-abc123
aws cleanrooms delete-membership --membership-identifier mem-abc123

# --- Configured tables ---
aws cleanrooms create-configured-table \
  --name my-impressions-table \
  --table-reference '{
    "glue": {"databaseName": "ad_data", "tableName": "impressions"}
  }' \
  --allowed-columns '["user_id", "campaign_id", "impression_date", "click"]' \
  --analysis-method DIRECT_QUERY

aws cleanrooms list-configured-tables
aws cleanrooms get-configured-table --configured-table-identifier ct-abc123

# --- Analysis rules ---
# Aggregation rule (only aggregate queries allowed)
aws cleanrooms create-configured-table-analysis-rule \
  --configured-table-identifier ct-abc123 \
  --analysis-rule-type AGGREGATION \
  --analysis-rule-policy '{
    "v1": {
      "aggregation": {
        "aggregateColumns": [
          {"columnNames": ["click"], "function": "SUM"},
          {"columnNames": ["user_id"], "function": "COUNT_DISTINCT"}
        ],
        "joinColumns": ["user_id"],
        "dimensionColumns": ["campaign_id", "impression_date"],
        "scalarFunctions": ["YEAR", "MONTH"],
        "outputConstraints": [{"columnName": "user_id", "minimum": 100, "type": "COUNT_DISTINCT"}]
      }
    }
  }'

# Custom rule (pre-approved templates only)
aws cleanrooms create-configured-table-analysis-rule \
  --configured-table-identifier ct-abc123 \
  --analysis-rule-type CUSTOM \
  --analysis-rule-policy '{
    "v1": {
      "custom": {
        "allowedAnalyses": ["arn:aws:cleanrooms:us-east-1:123456789012:membership/mem-abc123/analysistemplate/at-abc123"],
        "allowedAnalysisProviders": []
      }
    }
  }'

# --- Configured table associations ---
aws cleanrooms create-configured-table-association \
  --name impressions-association \
  --membership-identifier mem-abc123 \
  --configured-table-identifier ct-abc123 \
  --role-arn arn:aws:iam::123456789012:role/CleanRoomsRole

aws cleanrooms list-configured-table-associations \
  --membership-identifier mem-abc123

# --- Analysis templates ---
aws cleanrooms create-analysis-template \
  --membership-identifier mem-abc123 \
  --name campaign-reach-analysis \
  --format SQL \
  --source '{
    "text": "SELECT campaign_id, COUNT(DISTINCT user_id) AS reach FROM impressions_association GROUP BY campaign_id"
  }' \
  --description "Measures unique reach per campaign"

aws cleanrooms list-analysis-templates --membership-identifier mem-abc123

# --- Protected queries ---
aws cleanrooms start-protected-query \
  --membership-identifier mem-abc123 \
  --type SQL \
  --sql-parameters '{"queryString": "SELECT campaign_id, COUNT(DISTINCT user_id) as reach FROM impressions GROUP BY campaign_id"}' \
  --result-configuration '{
    "outputConfiguration": {
      "s3": {
        "resultFormat": "CSV",
        "bucket": "my-results-bucket",
        "keyPrefix": "results/"
      }
    }
  }'

aws cleanrooms get-protected-query \
  --membership-identifier mem-abc123 \
  --protected-query-identifier pq-abc123

aws cleanrooms list-protected-queries --membership-identifier mem-abc123
```

---

## AWS Entity Resolution

```bash
# --- Schema mappings ---
aws entityresolution create-schema-mapping \
  --schema-name customer-schema \
  --mapped-input-fields '[
    {"fieldName": "first_name", "type": "NAME", "subType": "FIRST"},
    {"fieldName": "last_name", "type": "NAME", "subType": "LAST"},
    {"fieldName": "email", "type": "EMAIL_ADDRESS"},
    {"fieldName": "phone", "type": "PHONE_NUMBER"},
    {"fieldName": "address", "type": "ADDRESS"}
  ]'

aws entityresolution get-schema-mapping --schema-name customer-schema
aws entityresolution list-schema-mappings
aws entityresolution delete-schema-mapping --schema-name customer-schema

# --- Matching workflows (rule-based) ---
aws entityresolution create-matching-workflow \
  --workflow-name customer-dedup \
  --input-source-config '[
    {
      "inputSourceARN": "arn:aws:glue:us-east-1:123456789012:table/my_db/customers",
      "schemaName": "customer-schema",
      "applyNormalization": true
    }
  ]' \
  --output-source-config '[
    {
      "outputS3Path": "s3://my-bucket/entity-resolution-output/",
      "output": [
        {"name": "customer_id"},
        {"name": "email"},
        {"name": "match_id"}
      ]
    }
  ]' \
  --resolution-techniques '{
    "resolutionType": "RULE_MATCHING",
    "ruleBasedProperties": {
      "rules": [
        {"ruleName": "email-match", "matchingKeys": ["email"]},
        {"ruleName": "name-phone-match", "matchingKeys": ["first_name", "last_name", "phone"]}
      ],
      "attributeMatchingModel": "MANY_TO_MANY"
    }
  }' \
  --role-arn arn:aws:iam::123456789012:role/EntityResolutionRole

# Matching workflow (ML-based)
aws entityresolution create-matching-workflow \
  --workflow-name customer-ml-dedup \
  --input-source-config '[
    {
      "inputSourceARN": "arn:aws:glue:us-east-1:123456789012:table/my_db/customers",
      "schemaName": "customer-schema",
      "applyNormalization": true
    }
  ]' \
  --output-source-config '[
    {
      "outputS3Path": "s3://my-bucket/entity-resolution-output/",
      "output": [{"name": "customer_id"}, {"name": "match_id"}]
    }
  ]' \
  --resolution-techniques '{"resolutionType": "ML_MATCHING"}' \
  --role-arn arn:aws:iam::123456789012:role/EntityResolutionRole

aws entityresolution get-matching-workflow --workflow-name customer-dedup
aws entityresolution list-matching-workflows
aws entityresolution delete-matching-workflow --workflow-name customer-dedup

# --- Run a matching job ---
aws entityresolution start-matching-job --workflow-name customer-dedup

aws entityresolution get-matching-job \
  --workflow-name customer-dedup \
  --job-id job-abc123

aws entityresolution list-matching-jobs --workflow-name customer-dedup

# --- ID namespaces (for ID resolution) ---
aws entityresolution create-id-namespace \
  --id-namespace-name internal-ids \
  --type SOURCE \
  --input-source-config '[
    {"inputSourceARN": "arn:aws:glue:us-east-1:123456789012:table/my_db/ids", "schemaName": "id-schema"}
  ]'

aws entityresolution get-id-namespace --id-namespace-name internal-ids
aws entityresolution list-id-namespaces
aws entityresolution delete-id-namespace --id-namespace-name internal-ids

# --- ID mapping workflows ---
aws entityresolution create-id-mapping-workflow \
  --workflow-name internal-to-partner \
  --input-source-config '[
    {"inputSourceARN": "arn:aws:entityresolution:us-east-1:123456789012:idnamespace/internal-ids", "type": "SOURCE"},
    {"inputSourceARN": "arn:aws:entityresolution:us-east-1:123456789012:idnamespace/partner-ids", "type": "TARGET"}
  ]' \
  --output-source-config '[
    {"outputS3Path": "s3://my-bucket/id-mapping-output/"}
  ]' \
  --id-mapping-techniques '{
    "idMappingType": "PROVIDER",
    "providerProperties": {
      "providerServiceArn": "arn:aws:entityresolution:us-east-1::providerservice/LiveRamp/IdentityLink"
    }
  }' \
  --role-arn arn:aws:iam::123456789012:role/EntityResolutionRole

aws entityresolution start-id-mapping-job --workflow-name internal-to-partner

aws entityresolution get-id-mapping-job \
  --workflow-name internal-to-partner \
  --job-id job-xyz789

aws entityresolution list-id-mapping-workflows
aws entityresolution delete-id-mapping-workflow --workflow-name internal-to-partner
```
