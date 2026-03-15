# Niche Analytics — CLI Reference
For service concepts, see [niche-analytics-capabilities.md](niche-analytics-capabilities.md).

## Amazon CloudSearch

> **Note**: Amazon CloudSearch is no longer available to new customers. Migrate new workloads to Amazon OpenSearch Service.

```bash
# --- Domain management ---
aws cloudsearch create-domain --domain-name my-search-domain

aws cloudsearch list-domain-names
aws cloudsearch describe-domains
aws cloudsearch describe-domains --domain-names my-search-domain

aws cloudsearch delete-domain --domain-name my-search-domain

# --- Index fields ---
# Define a text field with highlighting enabled
aws cloudsearch define-index-field \
  --domain-name my-search-domain \
  --name title \
  --type text \
  --text-options '{"ReturnEnabled": true, "HighlightEnabled": true, "SortEnabled": false}'

# Define a literal field with faceting enabled
aws cloudsearch define-index-field \
  --domain-name my-search-domain \
  --name category \
  --type literal \
  --literal-options '{"ReturnEnabled": true, "FacetEnabled": true, "SearchEnabled": true}'

# Define an int field (sortable)
aws cloudsearch define-index-field \
  --domain-name my-search-domain \
  --name price \
  --type int \
  --int-options '{"ReturnEnabled": true, "SearchEnabled": true, "FacetEnabled": true, "SortEnabled": true}'

# Define a latlon field for geospatial search
aws cloudsearch define-index-field \
  --domain-name my-search-domain \
  --name location \
  --type latlon \
  --lat-lon-options '{"ReturnEnabled": true, "SearchEnabled": true}'

aws cloudsearch describe-index-fields --domain-name my-search-domain
aws cloudsearch delete-index-field --domain-name my-search-domain --index-field-name title

# --- Analysis schemes (language processing) ---
aws cloudsearch define-analysis-scheme \
  --domain-name my-search-domain \
  --analysis-scheme '{
    "AnalysisSchemeName": "english_scheme",
    "AnalysisSchemeLanguage": "en",
    "AnalysisOptions": {
      "Synonyms": "{\"running\": [\"jogging\", \"sprinting\"]}",
      "Stopwords": "[\"the\", \"a\", \"and\"]",
      "StemmingDictionary": "{}",
      "AlgorithmicStemming": "full"
    }
  }'

aws cloudsearch describe-analysis-schemes --domain-name my-search-domain
aws cloudsearch delete-analysis-scheme \
  --domain-name my-search-domain \
  --analysis-scheme-name english_scheme

# --- Suggesters (autocomplete) ---
aws cloudsearch define-suggester \
  --domain-name my-search-domain \
  --suggester '{
    "SuggesterName": "title_suggest",
    "DocumentSuggesterOptions": {
      "SourceField": "title",
      "FuzzyMatching": "low",
      "SortExpression": "_score"
    }
  }'

aws cloudsearch describe-suggesters --domain-name my-search-domain
aws cloudsearch delete-suggester \
  --domain-name my-search-domain \
  --suggester-name title_suggest

# --- Expressions (custom ranking) ---
aws cloudsearch define-expression \
  --domain-name my-search-domain \
  --name boost_recent \
  --expression-value '_score * (1 + (1 / (1 + (_time - timestamp))))'

aws cloudsearch describe-expressions --domain-name my-search-domain

# --- Index and scaling ---
# Rebuild the index after field changes
aws cloudsearch index-documents --domain-name my-search-domain

aws cloudsearch describe-scaling-parameters --domain-name my-search-domain
aws cloudsearch update-scaling-parameters \
  --domain-name my-search-domain \
  --scaling-parameters '{
    "DesiredInstanceType": "search.m5.large",
    "DesiredReplicationCount": 2,
    "DesiredPartitionCount": 1
  }'

# --- Access policies ---
aws cloudsearch describe-service-access-policies --domain-name my-search-domain
aws cloudsearch update-service-access-policies \
  --domain-name my-search-domain \
  --access-policies '{
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::123456789012:root"},
      "Action": ["cloudsearch:search", "cloudsearch:suggest"],
      "Condition": {"IpAddress": {"aws:SourceIp": "203.0.113.0/24"}}
    }]
  }'

# --- Availability options ---
aws cloudsearch describe-availability-options --domain-name my-search-domain
aws cloudsearch update-availability-options \
  --domain-name my-search-domain \
  --multi-az    # enable Multi-AZ

# --- Search and suggest (via HTTP; not CLI commands) ---
# Search: GET https://<search-endpoint>/2013-01-01/search?q=coffee&q.parser=simple&return=title,price
# Structured query: ?q=(and 'coffee' (range field=price [5,25]))&q.parser=structured
# Facets: &facet.category={sort:"count"}
# Highlights: &highlight.title={}
# Sorting: &sort=price asc
# Suggestions: GET https://<search-endpoint>/2013-01-01/suggest?q=cof&suggester=title_suggest&size=5
```

---

## Amazon FinSpace

```bash
# --- Environments ---
aws finspace create-environment \
  --name my-finspace-env \
  --description "Capital markets analytics environment" \
  --kms-key-id arn:aws:kms:us-east-1:123456789012:key/mrk-abc123

aws finspace list-environments
aws finspace get-environment --environment-id env-abc123
aws finspace delete-environment --environment-id env-abc123

# --- kdb Environments ---
aws finspace create-kx-environment \
  --name my-kx-env \
  --kms-key-id arn:aws:kms:us-east-1:123456789012:key/mrk-abc123

aws finspace list-kx-environments
aws finspace get-kx-environment --environment-id env-kx-abc123
aws finspace delete-kx-environment --environment-id env-kx-abc123

# --- kdb Databases ---
aws finspace create-kx-database \
  --environment-id env-kx-abc123 \
  --database-name tickdb \
  --description "Tick data historical database"

aws finspace list-kx-databases --environment-id env-kx-abc123
aws finspace get-kx-database \
  --environment-id env-kx-abc123 \
  --database-name tickdb

# Create a changeset (append data to a database)
aws finspace create-kx-changeset \
  --environment-id env-kx-abc123 \
  --database-name tickdb \
  --change-requests '[
    {
      "changeType": "PUT",
      "s3Path": "s3://my-bucket/tickdata/2024/01/01/",
      "dbPath": "/2024.01.01/"
    }
  ]'

aws finspace list-kx-changesets \
  --environment-id env-kx-abc123 \
  --database-name tickdb

# --- kdb Clusters ---
aws finspace create-kx-cluster \
  --environment-id env-kx-abc123 \
  --cluster-name hdb-cluster-1 \
  --cluster-type HDB \
  --release-label 1.0 \
  --capacity-configuration '{"nodeType": "kx.s.xlarge", "nodeCount": 2}' \
  --databases '[{
    "databaseName": "tickdb",
    "cacheConfigurations": [{"cacheType": "CACHE_1000", "dbPaths": ["/"]}]
  }]' \
  --vpc-configuration '{
    "vpcId": "vpc-abc123",
    "securityGroupIds": ["sg-abc123"],
    "subnetIds": ["subnet-abc123"],
    "ipAddressType": "IP_V4"
  }' \
  --az-mode SINGLE \
  --availability-zone-id use1-az1

aws finspace list-kx-clusters --environment-id env-kx-abc123
aws finspace get-kx-cluster \
  --environment-id env-kx-abc123 \
  --cluster-name hdb-cluster-1

aws finspace delete-kx-cluster \
  --environment-id env-kx-abc123 \
  --cluster-name hdb-cluster-1

# --- kdb Users ---
aws finspace create-kx-user \
  --environment-id env-kx-abc123 \
  --user-name quant-analyst \
  --iam-role arn:aws:iam::123456789012:role/FinSpaceKxUserRole

aws finspace list-kx-users --environment-id env-kx-abc123

# Get connection string for a cluster
aws finspace get-kx-connection-string \
  --environment-id env-kx-abc123 \
  --cluster-name hdb-cluster-1 \
  --user-arn arn:aws:iam::123456789012:user/quant-analyst

# --- Scaling groups ---
aws finspace create-kx-scaling-group \
  --environment-id env-kx-abc123 \
  --scaling-group-name auto-scale-group \
  --host-type kx.sg.xlarge \
  --availability-zone-id use1-az1

aws finspace list-kx-scaling-groups --environment-id env-kx-abc123
```

---

## AWS Data Exchange

```bash
# --- Discover data sets on Marketplace ---
# (Browse the Marketplace console; subscribing is done via Marketplace not CLI directly)

# --- Data sets (provider side) ---
aws dataexchange create-data-set \
  --asset-type S3_SNAPSHOT \
  --description "Daily equity prices" \
  --name "Equity Prices Dataset"

aws dataexchange list-data-sets
aws dataexchange get-data-set --data-set-id ds-abc123
aws dataexchange delete-data-set --data-set-id ds-abc123

# --- Revisions ---
aws dataexchange create-revision \
  --data-set-id ds-abc123 \
  --comment "2024-01-01 daily update"

aws dataexchange list-revisions --data-set-id ds-abc123
aws dataexchange get-revision \
  --data-set-id ds-abc123 \
  --revision-id rev-abc123

# Finalize a revision (makes it available to subscribers)
aws dataexchange update-revision \
  --data-set-id ds-abc123 \
  --revision-id rev-abc123 \
  --finalized

aws dataexchange delete-revision \
  --data-set-id ds-abc123 \
  --revision-id rev-abc123

# --- Assets: import from S3 (provider) ---
aws dataexchange create-job \
  --type IMPORT_ASSETS_FROM_S3 \
  --details '{
    "ImportAssetsFromS3": {
      "DataSetId": "ds-abc123",
      "RevisionId": "rev-abc123",
      "AssetSources": [
        {"Bucket": "my-provider-bucket", "Key": "data/equity-prices-2024-01-01.csv"}
      ]
    }
  }'

# --- Assets: export to S3 (subscriber) ---
aws dataexchange create-job \
  --type EXPORT_ASSETS_TO_S3 \
  --details '{
    "ExportAssetsToS3": {
      "DataSetId": "ds-abc123",
      "RevisionId": "rev-abc123",
      "AssetDestinations": [
        {
          "AssetId": "asset-abc123",
          "Bucket": "my-subscriber-bucket",
          "Key": "received/equity-prices-2024-01-01.csv"
        }
      ]
    }
  }'

# --- Jobs (async operations) ---
aws dataexchange start-job --job-id job-abc123
aws dataexchange get-job --job-id job-abc123
aws dataexchange list-jobs \
  --data-set-id ds-abc123 \
  --revision-id rev-abc123

# --- Auto-export event actions (subscriber: auto-deliver new revisions to S3) ---
aws dataexchange create-event-action \
  --action '{
    "ExportRevisionToS3": {
      "RevisionDestination": {
        "Bucket": "my-subscriber-bucket",
        "KeyPattern": "${Revision.CreatedAt}/${Asset.Name}"
      }
    }
  }' \
  --event '{
    "RevisionPublished": {
      "DataSetId": "ds-abc123"
    }
  }'

aws dataexchange list-event-actions
aws dataexchange get-event-action --event-action-id ea-abc123
aws dataexchange delete-event-action --event-action-id ea-abc123

# --- Data grants (direct peer-to-peer sharing, no Marketplace) ---
aws dataexchange create-data-grant \
  --name "Partner equity data share" \
  --source-data-set-id ds-abc123 \
  --grant-distribution-scope AWS_ORGANIZATION \
  --receiver-principal 123456789012    # target AWS account ID

aws dataexchange list-data-grants
aws dataexchange get-data-grant --data-grant-id dg-abc123
aws dataexchange accept-data-grant --data-grant-arn arn:aws:dataexchange:us-east-1:123456789012:data-grants/dg-abc123
aws dataexchange revoke-data-grant --data-grant-id dg-abc123

# --- Received data grants (subscriber view) ---
aws dataexchange list-received-data-grants
aws dataexchange get-received-data-grant \
  --data-grant-arn arn:aws:dataexchange:us-east-1:123456789012:data-grants/dg-abc123

# --- Tagging ---
aws dataexchange tag-resource \
  --resource-arn arn:aws:dataexchange:us-east-1:123456789012:data-sets/ds-abc123 \
  --tags Environment=prod Team=data

aws dataexchange list-tags-for-resource \
  --resource-arn arn:aws:dataexchange:us-east-1:123456789012:data-sets/ds-abc123
```
