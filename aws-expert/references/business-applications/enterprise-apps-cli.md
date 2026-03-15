# AWS Enterprise Apps — CLI Reference

For service concepts, see [enterprise-apps-capabilities.md](enterprise-apps-capabilities.md).

## AWS AppFabric

```bash
# --- App bundles ---
# Create an app bundle (container for app authorizations and ingestions)
aws appfabric create-app-bundle \
  --client-mutation-token "$(uuidgen)" \
  --customer-managed-key-arn arn:aws:kms:us-east-1:123456789012:key/mrk-12345

aws appfabric get-app-bundle \
  --app-bundle-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345

aws appfabric list-app-bundles

aws appfabric update-app-bundle \
  --app-bundle-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345 \
  --customer-managed-key-arn arn:aws:kms:us-east-1:123456789012:key/mrk-67890

aws appfabric delete-app-bundle \
  --app-bundle-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345

# --- App authorizations ---
# Create an app authorization (connect a SaaS app using OAuth or API key)
# OAuth 2.0 authorization (e.g., Salesforce, Okta)
aws appfabric create-app-authorization \
  --app-bundle-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345 \
  --app SALESFORCE \
  --auth-type oauth2 \
  --credential '{
    "oauth2Credential": {
      "clientId": "my-salesforce-client-id",
      "clientSecret": "my-salesforce-client-secret"
    }
  }' \
  --tenant '{
    "tenantIdentifier": "mycompany.salesforce.com",
    "tenantDisplayName": "MyCompany Salesforce"
  }'

# API key authorization (e.g., Zendesk)
aws appfabric create-app-authorization \
  --app-bundle-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345 \
  --app ZENDESK \
  --auth-type apiKey \
  --credential '{
    "apiKeyCredential": {
      "apiKey": "my-zendesk-api-key"
    }
  }' \
  --tenant '{
    "tenantIdentifier": "mycompany.zendesk.com",
    "tenantDisplayName": "MyCompany Zendesk"
  }'

aws appfabric get-app-authorization \
  --app-bundle-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345 \
  --app-authorization-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345/appauthorization/auth-id-12345

aws appfabric list-app-authorizations \
  --app-bundle-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345

aws appfabric update-app-authorization \
  --app-bundle-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345 \
  --app-authorization-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345/appauthorization/auth-id-12345 \
  --credential '{
    "oauth2Credential": {
      "clientId": "new-client-id",
      "clientSecret": "new-client-secret"
    }
  }'

# Connect authorization (complete OAuth flow by providing auth code)
aws appfabric connect-app-authorization \
  --app-bundle-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345 \
  --app-authorization-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345/appauthorization/auth-id-12345 \
  --auth-request '{
    "redirectUri": "https://myapp.example.com/callback",
    "code": "oauth-authorization-code-from-saas-app"
  }'

aws appfabric delete-app-authorization \
  --app-bundle-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345 \
  --app-authorization-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345/appauthorization/auth-id-12345

# --- Ingestions ---
# Create an ingestion (data pipeline from an app authorization)
aws appfabric create-ingestion \
  --app-bundle-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345 \
  --app SALESFORCE \
  --tenant-id mycompany.salesforce.com \
  --ingestion-type auditLog \
  --client-token "$(uuidgen)" \
  --tags Key=Environment,Value=prod

aws appfabric get-ingestion \
  --app-bundle-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345 \
  --ingestion-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345/ingestion/ing-id-12345

aws appfabric list-ingestions \
  --app-bundle-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345

# Start an ingestion
aws appfabric start-ingestion \
  --app-bundle-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345 \
  --ingestion-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345/ingestion/ing-id-12345

# Stop an ingestion
aws appfabric stop-ingestion \
  --app-bundle-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345 \
  --ingestion-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345/ingestion/ing-id-12345

aws appfabric delete-ingestion \
  --app-bundle-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345 \
  --ingestion-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345/ingestion/ing-id-12345

# --- Ingestion destinations ---
# Create an S3 ingestion destination (OCSF-normalized logs to S3 in Parquet)
aws appfabric create-ingestion-destination \
  --app-bundle-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345 \
  --ingestion-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345/ingestion/ing-id-12345 \
  --processing-configuration '{
    "auditLog": {
      "schema": "ocsf",
      "format": "parquet"
    }
  }' \
  --destination-configuration '{
    "auditLog": {
      "destinationType": "s3",
      "s3Bucket": {
        "bucketName": "my-security-data-lake",
        "prefix": "appfabric/salesforce/"
      }
    }
  }' \
  --client-token "$(uuidgen)"

# Create a Firehose ingestion destination
aws appfabric create-ingestion-destination \
  --app-bundle-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345 \
  --ingestion-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345/ingestion/ing-id-12345 \
  --processing-configuration '{
    "auditLog": {
      "schema": "ocsf",
      "format": "json"
    }
  }' \
  --destination-configuration '{
    "auditLog": {
      "destinationType": "firehose",
      "firehoseStream": {
        "streamName": "appfabric-to-splunk"
      }
    }
  }' \
  --client-token "$(uuidgen)"

aws appfabric get-ingestion-destination \
  --app-bundle-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345 \
  --ingestion-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345/ingestion/ing-id-12345 \
  --ingestion-destination-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345/ingestion/ing-id-12345/ingestiondestination/dest-id-12345

aws appfabric list-ingestion-destinations \
  --app-bundle-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345 \
  --ingestion-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345/ingestion/ing-id-12345

aws appfabric update-ingestion-destination \
  --app-bundle-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345 \
  --ingestion-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345/ingestion/ing-id-12345 \
  --ingestion-destination-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345/ingestion/ing-id-12345/ingestiondestination/dest-id-12345 \
  --destination-configuration '{
    "auditLog": {
      "destinationType": "s3",
      "s3Bucket": {
        "bucketName": "my-updated-security-bucket",
        "prefix": "appfabric/"
      }
    }
  }'

aws appfabric delete-ingestion-destination \
  --app-bundle-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345 \
  --ingestion-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345/ingestion/ing-id-12345 \
  --ingestion-destination-identifier arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345/ingestion/ing-id-12345/ingestiondestination/dest-id-12345

# --- Tagging ---
aws appfabric tag-resource \
  --resource-arn arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345 \
  --tags Key=CostCenter,Value=Security Key=Environment,Value=prod

aws appfabric list-tags-for-resource \
  --resource-arn arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345

aws appfabric untag-resource \
  --resource-arn arn:aws:appfabric:us-east-1:123456789012:appbundle/bundle-id-12345 \
  --tag-keys CostCenter
```

---

## AWS Supply Chain

> **Note**: AWS Supply Chain is primarily managed through the Supply Chain web console and REST API. Direct AWS CLI support for Supply Chain operations is limited to instance management. Data ingestion, insights, and planning are accessed via the Supply Chain application interface or the Supply Chain Data API (REST).

```bash
# --- Instance management ---
aws supplychain create-instance \
  --instance-name my-supply-chain \
  --instance-description "Production supply chain instance" \
  --kms-key-id arn:aws:kms:us-east-1:123456789012:key/mrk-12345

aws supplychain get-instance \
  --instance-id sc-id-12345

aws supplychain list-instances

aws supplychain update-instance \
  --instance-id sc-id-12345 \
  --instance-name my-supply-chain-prod \
  --instance-description "Updated production instance"

aws supplychain delete-instance \
  --instance-id sc-id-12345

# --- Data lake namespace / dataset management (via Supply Chain Data API) ---
# Note: The following use the Supply Chain REST Data API via aws supplychain subcommands

aws supplychain send-data-integration-event \
  --instance-id sc-id-12345 \
  --event-type scn.data.purchaseorder \
  --data '{
    "id": "PO-12345",
    "companyid": "MYCOMPANY",
    "vendor_tpartner_id": "VENDOR-001",
    "product_id": "SKU-ABC",
    "order_quantity": 500,
    "order_date": "2024-03-01",
    "promised_delivery_date": "2024-03-15",
    "status": "OPEN"
  }' \
  --event-group-id "batch-2024-03-01"

# Supported event types for data integration:
# scn.data.purchaseorder
# scn.data.shipment
# scn.data.inventory
# scn.data.forecast
# scn.data.inboundorder
# scn.data.inboundorderline
# scn.data.supplier
# scn.data.product

# --- Tags ---
aws supplychain tag-resource \
  --resource-arn arn:aws:scn:us-east-1:123456789012:instance/sc-id-12345 \
  --tags Key=Environment,Value=prod Key=CostCenter,Value=SupplyChain

aws supplychain list-tags-for-resource \
  --resource-arn arn:aws:scn:us-east-1:123456789012:instance/sc-id-12345

aws supplychain untag-resource \
  --resource-arn arn:aws:scn:us-east-1:123456789012:instance/sc-id-12345 \
  --tag-keys CostCenter
```
