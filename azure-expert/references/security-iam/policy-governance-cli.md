# Azure Policy & Governance — CLI Reference

---

## Azure Policy

### Policy Definitions

```bash
# List all built-in policy definitions
az policy definition list \
  --query "[?policyType=='BuiltIn'].{Name:name,DisplayName:displayName}" \
  --output table

# List built-in policies for a specific category
az policy definition list \
  --query "[?policyType=='BuiltIn' && metadata.category=='Monitoring'].{Name:name,DisplayName:displayName}" \
  --output table

# Search for policies by keyword in display name
az policy definition list \
  --query "[?contains(displayName, 'tag')].{Name:name,DisplayName:displayName,Category:metadata.category}" \
  --output table

# Show details of a specific built-in policy
az policy definition show \
  --name "0a914e76-4921-4c19-b460-a2d36003525a"

# Show details by display name pattern
az policy definition list \
  --query "[?displayName=='Require a tag on resource groups']" \
  --output json

# Create a custom policy definition from JSON file
az policy definition create \
  --name "require-costcenter-tag" \
  --display-name "Require CostCenter tag on resource groups" \
  --description "Requires CostCenter tag on all resource groups" \
  --mode All \
  --rules policy-rules.json \
  --params policy-parameters.json \
  --subscription <sub-id>

# Create a custom policy definition inline (simple example)
az policy definition create \
  --name "deny-public-storage" \
  --display-name "Deny public access on Storage Accounts" \
  --description "Storage accounts must disable public blob access" \
  --mode All \
  --rules '{
    "if": {
      "allOf": [
        { "field": "type", "equals": "Microsoft.Storage/storageAccounts" },
        { "field": "Microsoft.Storage/storageAccounts/allowBlobPublicAccess", "notEquals": "false" }
      ]
    },
    "then": { "effect": "deny" }
  }'

# Update a custom policy definition
az policy definition update \
  --name "deny-public-storage" \
  --display-name "Deny public blob access on Storage Accounts (Updated)"

# List custom policy definitions only
az policy definition list \
  --query "[?policyType=='Custom'].{Name:name,DisplayName:displayName}" \
  --output table

# Delete a custom policy definition
az policy definition delete \
  --name "deny-public-storage"

# Export a policy definition to JSON
az policy definition show \
  --name "deny-public-storage" \
  --output json > deny-public-storage.json
```

### Policy Initiatives (Sets)

```bash
# List all built-in initiatives (policy sets)
az policy set-definition list \
  --query "[?policyType=='BuiltIn'].{Name:name,DisplayName:displayName}" \
  --output table

# Show a specific built-in initiative
az policy set-definition show \
  --name "1f3afdf9-d0c9-4c3d-847f-89da613e70a8"  # Azure Security Benchmark

# Create a custom initiative from file
az policy initiative create \
  --name "my-baseline-initiative" \
  --display-name "Organization Baseline Compliance" \
  --description "Baseline policies for all subscriptions" \
  --definitions initiative-definitions.json \
  --params initiative-parameters.json

# Create a custom initiative inline with multiple policy definitions
az policy initiative create \
  --name "tagging-initiative" \
  --display-name "Required Tags Initiative" \
  --description "Enforce required tags on all resources" \
  --definitions '[
    {
      "policyDefinitionId": "/subscriptions/<sub>/providers/Microsoft.Authorization/policyDefinitions/require-costcenter-tag",
      "parameters": {}
    },
    {
      "policyDefinitionId": "/providers/Microsoft.Authorization/policyDefinitions/96670d01-0a4d-4649-9c89-2d3abc0a5025",
      "parameters": {
        "tagName": { "value": "Environment" }
      }
    }
  ]'

# List custom initiatives
az policy initiative list \
  --query "[?policyType=='Custom'].{Name:name,DisplayName:displayName}" \
  --output table

# Delete a custom initiative
az policy initiative delete \
  --name "tagging-initiative"
```

### Policy Assignments

```bash
# Assign a built-in policy to a resource group
az policy assignment create \
  --name "deny-public-storage-prod" \
  --display-name "Deny public storage in Prod RG" \
  --policy "/providers/Microsoft.Authorization/policyDefinitions/4fa4b6c0-31ca-4c0d-b10d-24b96f62a751" \
  --scope /subscriptions/<sub>/resourceGroups/myProdRG \
  --enforcement-mode Default

# Assign a policy with parameters
az policy assignment create \
  --name "require-tag-environment" \
  --display-name "Require Environment tag" \
  --policy "/providers/Microsoft.Authorization/policyDefinitions/96670d01-0a4d-4649-9c89-2d3abc0a5025" \
  --scope /subscriptions/<sub-id> \
  --params '{"tagName": {"value": "Environment"}}' \
  --non-compliance-message "All resources must have an Environment tag"

# Assign an initiative to a management group
az policy assignment create \
  --name "cis-baseline-corp" \
  --display-name "CIS Microsoft Azure Foundations Benchmark" \
  --policy-set-definition "/providers/Microsoft.Authorization/policySetDefinitions/612b5213-9160-4969-8578-1518bd2a000c" \
  --scope /providers/Microsoft.Management/managementGroups/Corp \
  --enforcement-mode Default

# Assign a policy in DoNotEnforce mode (audit only, no deny)
az policy assignment create \
  --name "audit-only-storage" \
  --display-name "Audit public storage (no enforce)" \
  --policy "/providers/Microsoft.Authorization/policyDefinitions/4fa4b6c0-31ca-4c0d-b10d-24b96f62a751" \
  --scope /subscriptions/<sub-id> \
  --enforcement-mode DoNotEnforce

# Assign DINE policy with managed identity for remediation
az policy assignment create \
  --name "deploy-diagnostic-settings" \
  --display-name "Deploy diagnostic settings for Storage Accounts" \
  --policy "/providers/Microsoft.Authorization/policyDefinitions/59759c62-9a22-4cdf-ae64-074495983fef" \
  --scope /subscriptions/<sub-id> \
  --mi-system-assigned \
  --location eastus \
  --params '{"logAnalytics": {"value": "/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.OperationalInsights/workspaces/myWorkspace"}}'

# Grant the policy assignment's managed identity the required role for remediation
ASSIGNMENT_ID=$(az policy assignment show --name "deploy-diagnostic-settings" --scope /subscriptions/<sub-id> --query identity.principalId --output tsv)
az role assignment create \
  --assignee $ASSIGNMENT_ID \
  --role "Monitoring Contributor" \
  --scope /subscriptions/<sub-id>

# List policy assignments at a scope
az policy assignment list \
  --scope /subscriptions/<sub-id> \
  --output table

# List all assignments including inherited
az policy assignment list \
  --scope /subscriptions/<sub>/resourceGroups/myRG \
  --disable-scope-strict-match \
  --output table

# Show a specific assignment
az policy assignment show \
  --name "deny-public-storage-prod" \
  --scope /subscriptions/<sub>/resourceGroups/myProdRG

# Delete a policy assignment
az policy assignment delete \
  --name "deny-public-storage-prod" \
  --scope /subscriptions/<sub>/resourceGroups/myProdRG
```

### Remediation

```bash
# Create a remediation task for a DINE/Modify policy
az policy remediation create \
  --name "remediate-diagnostic-settings" \
  --policy-assignment "deploy-diagnostic-settings" \
  --resource-group myRG

# Create a remediation task at subscription scope
az policy remediation create \
  --name "remediate-subscription-tags" \
  --policy-assignment "require-tag-environment" \
  --scope /subscriptions/<sub-id>

# Create a remediation task for an initiative policy
az policy remediation create \
  --name "remediate-initiative-policy" \
  --policy-assignment "cis-baseline-corp" \
  --definition-reference-id "<policy-definition-reference-id-in-initiative>" \
  --scope /providers/Microsoft.Management/managementGroups/Corp

# List remediation tasks
az policy remediation list \
  --resource-group myRG \
  --output table

# Show remediation task details and progress
az policy remediation show \
  --name "remediate-diagnostic-settings" \
  --resource-group myRG

# Cancel a running remediation task
az policy remediation cancel \
  --name "remediate-diagnostic-settings" \
  --resource-group myRG

# Delete a remediation task
az policy remediation delete \
  --name "remediate-diagnostic-settings" \
  --resource-group myRG
```

### Compliance State

```bash
# Trigger on-demand compliance scan for a subscription
az policy state trigger-scan \
  --subscription <sub-id> \
  --no-wait

# Trigger compliance scan for a resource group
az policy state trigger-scan \
  --resource-group myRG \
  --no-wait

# Summarize compliance state at subscription level
az policy state summarize \
  --subscription <sub-id> \
  --output json

# Summarize compliance at resource group level
az policy state summarize \
  --resource-group myRG \
  --output json

# List non-compliant resources for a specific assignment
az policy state list \
  --filter "complianceState eq 'NonCompliant' and policyAssignmentName eq 'deny-public-storage-prod'" \
  --output table

# List compliance state for all resources with a specific policy
az policy state list \
  --policy-definition "4fa4b6c0-31ca-4c0d-b10d-24b96f62a751" \
  --output table

# List compliance history for a resource
az policy state list \
  --resource /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/myStorage \
  --from "2024-01-01T00:00:00Z" \
  --output table
```

---

## Management Groups

```bash
# Create a management group
az account management-group create \
  --name CorpLandingZones \
  --display-name "Corp Landing Zones" \
  --parent LandingZones

# Create a management group at root level
az account management-group create \
  --name Sandboxes \
  --display-name "Sandboxes"

# List all management groups in the tenant
az account management-group list \
  --output table

# Show management group details and children
az account management-group show \
  --name CorpLandingZones \
  --expand \
  --recurse

# Move a subscription into a management group
az account management-group subscription add \
  --name CorpLandingZones \
  --subscription <sub-id>

# Remove a subscription from a management group
az account management-group subscription remove \
  --name CorpLandingZones \
  --subscription <sub-id>

# Move a child management group under a different parent
az account management-group update \
  --name CorpLandingZones \
  --parent PlatformLandingZones

# Delete a management group (must be empty — no subscriptions or child MGs)
az account management-group delete \
  --name CorpLandingZones

# Assign RBAC at management group scope
az role assignment create \
  --assignee <group-object-id> \
  --role Reader \
  --scope /providers/Microsoft.Management/managementGroups/CorpLandingZones

# List role assignments at management group
az role assignment list \
  --scope /providers/Microsoft.Management/managementGroups/CorpLandingZones \
  --output table
```

---

## Azure Deployment Stacks

```bash
# Create a deployment stack at resource group scope (denies delete on managed resources)
az stack group create \
  --name myPlatformStack \
  --resource-group myRG \
  --template-file platform-resources.bicep \
  --parameters Environment=Prod CostCenter=CC-1234 \
  --deny-settings-mode DenyDelete \
  --deny-settings-apply-to-child-scopes true \
  --action-on-unmanage detachAll

# Create a deployment stack at subscription scope
az stack sub create \
  --name myLandingZoneStack \
  --location eastus \
  --template-file landing-zone.bicep \
  --parameters @landing-zone.parameters.json \
  --deny-settings-mode DenyWriteAndDelete \
  --action-on-unmanage detachAll

# Create a deployment stack at management group scope
az stack mg create \
  --name myEnterpriseStack \
  --location eastus \
  --management-group-id CorpLandingZones \
  --template-file enterprise-policies.bicep \
  --deny-settings-mode DenyDelete

# List deployment stacks at resource group scope
az stack group list \
  --resource-group myRG \
  --output table

# List deployment stacks at subscription scope
az stack sub list \
  --output table

# Show stack details (managed resources, deny assignments)
az stack group show \
  --name myPlatformStack \
  --resource-group myRG

# Show managed resources in a stack
az stack group show \
  --name myPlatformStack \
  --resource-group myRG \
  --query resources \
  --output table

# Update a stack (update template or parameters)
az stack group create \
  --name myPlatformStack \
  --resource-group myRG \
  --template-file platform-resources-v2.bicep \
  --parameters Environment=Prod CostCenter=CC-5678 \
  --deny-settings-mode DenyDelete \
  --action-on-unmanage detachAll

# Delete a stack (detach resources — keep them, just remove stack management)
az stack group delete \
  --name myPlatformStack \
  --resource-group myRG \
  --action-on-unmanage detachAll \
  --yes

# Delete a stack and delete all managed resources
az stack group delete \
  --name myPlatformStack \
  --resource-group myRG \
  --action-on-unmanage deleteAll \
  --yes
```

---

## Microsoft Purview

```bash
# Create a Purview account
az purview account create \
  --account-name myPurviewAccount \
  --resource-group myRG \
  --location eastus \
  --sku-name Standard \
  --sku-capacity 4

# List Purview accounts
az purview account list \
  --resource-group myRG \
  --output table

# Show Purview account details (includes catalog endpoints)
az purview account show \
  --account-name myPurviewAccount \
  --resource-group myRG

# Get the Purview atlas endpoint (for API access)
az purview account show \
  --account-name myPurviewAccount \
  --resource-group myRG \
  --query properties.endpoints.catalog \
  --output tsv

# Add root collection admin to Purview
az purview account add-root-collection-admin \
  --account-name myPurviewAccount \
  --resource-group myRG \
  --object-id <user-object-id>

# Create a scan ruleset (define what to scan in data sources)
az purview scan-ruleset create \
  --account-name myPurviewAccount \
  --resource-group myRG \
  --scan-ruleset-name myAzureStorageScanRuleset \
  --data-source-type AzureStorage \
  --file-extensions .csv .json .parquet .txt

# Delete a Purview account
az purview account delete \
  --account-name myPurviewAccount \
  --resource-group myRG \
  --yes
```
