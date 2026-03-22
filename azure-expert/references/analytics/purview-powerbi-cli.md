# Microsoft Purview & Power BI — CLI Reference

## Prerequisites

```bash
az login
az account set --subscription "My Subscription"

# Install Purview extension if needed
az extension add -n purview
```

---

## Microsoft Purview Account

```bash
# Create a Purview account
az purview account create \
  --name myPurviewAccount \
  --resource-group myRG \
  --location eastus

# Show Purview account details
az purview account show \
  --name myPurviewAccount \
  --resource-group myRG

# Get the Atlas endpoint (for REST API access)
az purview account show \
  --name myPurviewAccount \
  --resource-group myRG \
  --query "properties.endpoints.atlas" -o tsv

# Get the catalog endpoint
az purview account show \
  --name myPurviewAccount \
  --resource-group myRG \
  --query "properties.endpoints.catalog" -o tsv

# List Purview accounts
az purview account list \
  --resource-group myRG \
  -o table

# List Purview accounts across subscription
az purview account list \
  -o table

# Update account (add tags)
az purview account update \
  --name myPurviewAccount \
  --resource-group myRG \
  --tags environment=production

# Add managed event hub for Kafka notification (event-driven lineage)
az purview account add-root-collection-admin \
  --account-name myPurviewAccount \
  --resource-group myRG \
  --object-id <user-or-sp-object-id>

# Delete Purview account
az purview account delete \
  --name myPurviewAccount \
  --resource-group myRG \
  --yes
```

---

## Purview Network Configuration

```bash
# Create private endpoint for Purview portal
az network private-endpoint create \
  --name purview-portal-pe \
  --resource-group myRG \
  --vnet-name myVNet \
  --subnet mySubnet \
  --private-connection-resource-id $(az purview account show --name myPurviewAccount --resource-group myRG --query id -o tsv) \
  --group-id portal \
  --connection-name purview-portal-connection

# Create private endpoint for Purview account (catalog/scan APIs)
az network private-endpoint create \
  --name purview-account-pe \
  --resource-group myRG \
  --vnet-name myVNet \
  --subnet mySubnet \
  --private-connection-resource-id $(az purview account show --name myPurviewAccount --resource-group myRG --query id -o tsv) \
  --group-id account \
  --connection-name purview-account-connection
```

---

## Purview RBAC

```bash
# Purview uses its own RBAC system (configured via portal or REST API)
# Standard Azure RBAC roles:
PURVIEW_ID=$(az purview account show --name myPurviewAccount --resource-group myRG --query id -o tsv)

# Purview Data Curator — can edit assets in catalog
az role assignment create \
  --assignee <object-id> \
  --role "Purview Data Curator" \
  --scope $PURVIEW_ID

# Purview Data Reader — read-only catalog access
az role assignment create \
  --assignee <object-id> \
  --role "Purview Data Reader" \
  --scope $PURVIEW_ID

# Purview Data Source Administrator — manage data sources, trigger scans
az role assignment create \
  --assignee <object-id> \
  --role "Purview Data Source Administrator" \
  --scope $PURVIEW_ID
```

---

## Purview REST API (Atlas API)

Most Purview operations are performed via REST API or SDKs, not Azure CLI. Key endpoints:

```bash
# Get OAuth token for Purview API (using Azure CLI)
TOKEN=$(az account get-access-token \
  --resource "https://purview.azure.net" \
  --query accessToken -o tsv)

ENDPOINT="https://myPurviewAccount.purview.azure.com"

# --- Catalog Operations ---

# Search assets
curl -X POST "${ENDPOINT}/catalog/api/search/query?api-version=2022-08-01-preview" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"keywords": "sales", "limit": 10}'

# Get asset by GUID
curl -X GET "${ENDPOINT}/catalog/api/atlas/v2/entity/guid/<asset-guid>" \
  -H "Authorization: Bearer $TOKEN"

# Create/update asset (entity)
curl -X POST "${ENDPOINT}/catalog/api/atlas/v2/entity" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity": {
      "typeName": "azure_blob_path",
      "attributes": {
        "name": "sales-data",
        "qualifiedName": "https://mystorageaccount.blob.core.windows.net/data/sales"
      }
    }
  }'

# Apply classification to an asset
curl -X POST "${ENDPOINT}/catalog/api/atlas/v2/entity/guid/<asset-guid>/classifications" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '[{"typeName": "MICROSOFT.FINANCIAL.CREDIT_CARD_NUMBER"}]'

# List glossary terms
curl -X GET "${ENDPOINT}/catalog/api/atlas/v2/glossary" \
  -H "Authorization: Bearer $TOKEN"

# --- Scanning Operations ---

# List data sources
curl -X GET "${ENDPOINT}/scan/datasources?api-version=2022-07-01-preview" \
  -H "Authorization: Bearer $TOKEN"

# Register a data source (Azure Data Lake Gen2)
curl -X PUT "${ENDPOINT}/scan/datasources/my-adls-source?api-version=2022-07-01-preview" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "kind": "AdlsGen2",
    "properties": {
      "endpoint": "https://mystorageaccount.dfs.core.windows.net",
      "resourceId": "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{account}",
      "collection": {"referenceName": "myrootcollection", "type": "CollectionReference"}
    }
  }'

# Trigger a scan
curl -X POST "${ENDPOINT}/scan/datasources/my-adls-source/scans/full-scan/runs/?api-version=2022-07-01-preview" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Purview Python SDK

```python
from azure.purview.catalog import PurviewCatalogClient
from azure.purview.scanning import PurviewScanningClient
from azure.identity import DefaultAzureCredential

# Initialize clients
credential = DefaultAzureCredential()
endpoint = "https://myPurviewAccount.purview.azure.com"

catalog_client = PurviewCatalogClient(endpoint=endpoint, credential=credential)
scanning_client = PurviewScanningClient(endpoint=endpoint, credential=credential)

# Search for assets
results = catalog_client.discovery.query(body={"keywords": "customer", "limit": 20})
for item in results.get("value", []):
    print(f"Name: {item.get('name')}, Type: {item.get('entityType')}")

# Get asset details by GUID
asset = catalog_client.entity.get_by_guid(guid="<asset-guid>")
print(f"Asset name: {asset['entity']['attributes']['name']}")

# List data sources
for source in scanning_client.data_sources.list_all():
    print(f"Source: {source['name']}, Kind: {source['kind']}")
```

---

## Power BI Embedded (Azure Analysis Services Equivalent)

```bash
# Create Power BI Embedded resource (A-SKU for app-owns-data embedding)
az powerbi embedded-capacity create \
  --name myPBIEmbedded \
  --resource-group myRG \
  --location eastus \
  --sku-name A1 \
  --administration-members "user@mycompany.com"

# Valid SKU sizes: A1 (1 vCore), A2 (2), A3 (4), A4 (8), A5 (16), A6 (32)

# Show capacity details
az powerbi embedded-capacity show \
  --name myPBIEmbedded \
  --resource-group myRG

# List Power BI Embedded capacities
az powerbi embedded-capacity list \
  --resource-group myRG \
  -o table

# Update capacity (scale up/down)
az powerbi embedded-capacity update \
  --name myPBIEmbedded \
  --resource-group myRG \
  --sku-name A2

# Delete capacity
az powerbi embedded-capacity delete \
  --name myPBIEmbedded \
  --resource-group myRG \
  --yes
```

---

## Power BI REST API Patterns

```bash
# Authenticate as service principal
TOKEN=$(curl -s -X POST \
  "https://login.microsoftonline.com/{tenant-id}/oauth2/token" \
  -d "grant_type=client_credentials&client_id={client-id}&client_secret={client-secret}&resource=https://analysis.windows.net/powerbi/api" \
  | jq -r '.access_token')

PBAPI="https://api.powerbi.com/v1.0/myorg"

# List workspaces (groups)
curl -X GET "$PBAPI/groups" \
  -H "Authorization: Bearer $TOKEN" | jq '.value[].name'

# List reports in workspace
curl -X GET "$PBAPI/groups/{workspace-id}/reports" \
  -H "Authorization: Bearer $TOKEN" | jq '.value[].name'

# Get embed token for a report (app-owns-data)
curl -X POST "$PBAPI/groups/{workspace-id}/reports/{report-id}/GenerateToken" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"accessLevel": "View"}' | jq '.token'

# Refresh a dataset
curl -X POST "$PBAPI/groups/{workspace-id}/datasets/{dataset-id}/refreshes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notifyOption": "MailOnFailure"}'

# Get refresh history
curl -X GET "$PBAPI/groups/{workspace-id}/datasets/{dataset-id}/refreshes" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Azure Analysis Services

```bash
# Create an Analysis Services server
az analysisservices server create \
  --name myASServer \
  --resource-group myRG \
  --location eastus \
  --sku S0 \
  --administrator-user "user@mycompany.com"

# Show server details (connection string)
az analysisservices server show \
  --name myASServer \
  --resource-group myRG

# List servers
az analysisservices server list \
  --resource-group myRG \
  -o table

# Update server SKU (scale up)
az analysisservices server update \
  --name myASServer \
  --resource-group myRG \
  --sku S2

# Suspend server (pause billing — retains data)
az analysisservices server suspend \
  --name myASServer \
  --resource-group myRG

# Resume server
az analysisservices server resume \
  --name myASServer \
  --resource-group myRG

# Add an administrator
az analysisservices server update \
  --name myASServer \
  --resource-group myRG \
  --administrator-user "admin1@mycompany.com" "admin2@mycompany.com"

# List firewall rules
az analysisservices server list-gateway-status \
  --name myASServer \
  --resource-group myRG

# Delete server
az analysisservices server delete \
  --name myASServer \
  --resource-group myRG \
  --yes
```

---

## Purview Scan Rule Sets

```bash
# Create scan rule set (via REST API — no dedicated CLI command)
curl -X PUT "${ENDPOINT}/scan/scanrulesets/my-parquet-ruleset?api-version=2022-07-01-preview" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "kind": "AdlsGen2",
    "properties": {
      "scanningRule": {
        "fileExtensions": ["PARQUET", "DELTA", "CSV"],
        "customFileExtensions": []
      },
      "classificationRules": [
        {"name": "MICROSOFT.PERSONAL.EMAIL", "bindingVersion": null, "modifiedAt": null, "status": "Enabled"},
        {"name": "MICROSOFT.PERSONAL.NAME", "bindingVersion": null, "modifiedAt": null, "status": "Enabled"}
      ]
    }
  }'
```
