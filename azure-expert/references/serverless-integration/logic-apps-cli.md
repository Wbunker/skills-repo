# Azure Logic Apps — CLI Reference
For service concepts, see [logic-apps-capabilities.md](logic-apps-capabilities.md).

## Logic Apps Consumption (Multi-tenant)

```bash
# --- Workflow CRUD ---
# Create a Logic App workflow from an ARM/definition JSON file
az logic workflow create \
  --resource-group myRG \
  --name myLogicApp \
  --location eastus \
  --definition @workflow-definition.json

# List all Logic Apps in a resource group
az logic workflow list \
  --resource-group myRG \
  --query "[].{Name:name, State:state, Location:location}" \
  --output table

# Show details of a specific Logic App
az logic workflow show \
  --resource-group myRG \
  --name myLogicApp

# Delete a Logic App workflow
az logic workflow delete \
  --resource-group myRG \
  --name myLogicApp \
  --yes

# Enable a disabled Logic App
az logic workflow update \
  --resource-group myRG \
  --name myLogicApp \
  --state Enabled

# Disable a Logic App (stop processing triggers)
az logic workflow update \
  --resource-group myRG \
  --name myLogicApp \
  --state Disabled

# --- Run History ---
# List recent runs for a workflow
az logic workflow run list \
  --resource-group myRG \
  --name myLogicApp \
  --query "[].{RunId:name, Status:status, StartTime:startTime, EndTime:endTime}" \
  --output table

# Show details of a specific run
az logic workflow run show \
  --resource-group myRG \
  --name myLogicApp \
  --run-name 08585490862082911444

# List actions within a specific run
az logic workflow run action list \
  --resource-group myRG \
  --name myLogicApp \
  --run-name 08585490862082911444

# Show input/output of a specific action in a run
az logic workflow run action show \
  --resource-group myRG \
  --name myLogicApp \
  --run-name 08585490862082911444 \
  --action-name Send_an_email

# Cancel an in-progress run
az logic workflow run cancel \
  --resource-group myRG \
  --name myLogicApp \
  --run-name 08585490862082911444

# --- Trigger Management ---
# List triggers defined in a Logic App
az logic workflow trigger list \
  --resource-group myRG \
  --name myLogicApp

# Manually fire the trigger (for recurrence or polling triggers)
az logic workflow trigger run \
  --resource-group myRG \
  --name myLogicApp \
  --trigger-name Recurrence

# Get the callback URL for an HTTP Request trigger
az logic workflow trigger list-callback-url \
  --resource-group myRG \
  --name myLogicApp \
  --trigger-name manual
```

## Logic Apps Standard (Single-tenant)

```bash
# --- Create Standard Logic App ---
# Create a Logic Apps Standard resource on App Service Plan
az logicapp create \
  --resource-group myRG \
  --name myStandardLogicApp \
  --storage-account myStorageAcct \
  --plan myAppServicePlan \
  --location eastus

# Create on Container Apps (newer option)
az logicapp create \
  --resource-group myRG \
  --name myStandardLogicApp \
  --storage-account myStorageAcct \
  --environment myContainerAppEnv \
  --location eastus

# List Logic Apps Standard resources
az logicapp list \
  --resource-group myRG \
  --output table

# Show a Logic Apps Standard resource
az logicapp show \
  --resource-group myRG \
  --name myStandardLogicApp

# Start a Logic Apps Standard resource
az logicapp start \
  --resource-group myRG \
  --name myStandardLogicApp

# Stop a Logic Apps Standard resource
az logicapp stop \
  --resource-group myRG \
  --name myStandardLogicApp

# Restart a Logic Apps Standard resource
az logicapp restart \
  --resource-group myRG \
  --name myStandardLogicApp

# --- App Settings for Standard ---
# Set application settings (connection strings, parameters)
az logicapp config appsettings set \
  --resource-group myRG \
  --name myStandardLogicApp \
  --settings ServiceBusConnection="Endpoint=sb://..."

# List application settings
az logicapp config appsettings list \
  --resource-group myRG \
  --name myStandardLogicApp

# --- Deploy Standard Logic App via ZIP ---
# Deploy a ZIP package (VS Code project output)
az logicapp deployment source config-zip \
  --resource-group myRG \
  --name myStandardLogicApp \
  --src ./myLogicAppProject.zip

# --- Managed Identity for Standard ---
# Assign system-assigned managed identity
az logicapp identity assign \
  --resource-group myRG \
  --name myStandardLogicApp

# Show identity
az logicapp identity show \
  --resource-group myRG \
  --name myStandardLogicApp
```

## Integration Accounts (Enterprise Integration Pack)

```bash
# --- Integration Account Management ---
# Create an integration account (Standard tier for production B2B)
az logic integration-account create \
  --resource-group myRG \
  --name myIntegrationAccount \
  --location eastus \
  --sku Standard

# List integration accounts
az logic integration-account list \
  --resource-group myRG \
  --output table

# Show integration account details
az logic integration-account show \
  --resource-group myRG \
  --name myIntegrationAccount

# Link integration account to a Logic App (Consumption)
az logic workflow update \
  --resource-group myRG \
  --name myLogicApp \
  --integration-account /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.Logic/integrationAccounts/myIntegrationAccount

# --- Partners ---
# Create a trading partner
az logic integration-account partner create \
  --resource-group myRG \
  --integration-account-name myIntegrationAccount \
  --name Contoso \
  --partner-type B2B \
  --content '{
    "b2b": {
      "businessIdentities": [
        {"qualifier": "ZZ", "value": "Contoso"}
      ]
    }
  }'

# List partners
az logic integration-account partner list \
  --resource-group myRG \
  --integration-account-name myIntegrationAccount

# --- Agreements ---
# Create an X12 agreement between two partners
az logic integration-account agreement create \
  --resource-group myRG \
  --integration-account-name myIntegrationAccount \
  --name ContosoFabrikamX12 \
  --agreement-type X12 \
  --host-partner Contoso \
  --guest-partner Fabrikam \
  --host-identity-qualifier ZZ \
  --host-identity-value Contoso \
  --guest-identity-qualifier ZZ \
  --guest-identity-value Fabrikam \
  --content @x12-agreement.json

# List agreements
az logic integration-account agreement list \
  --resource-group myRG \
  --integration-account-name myIntegrationAccount

# --- Schemas ---
# Create (upload) an XSD schema
az logic integration-account schema create \
  --resource-group myRG \
  --integration-account-name myIntegrationAccount \
  --name MyOrderSchema \
  --schema-type Xml \
  --content @order-schema.xsd

# List schemas
az logic integration-account schema list \
  --resource-group myRG \
  --integration-account-name myIntegrationAccount

# --- Maps ---
# Create (upload) an XSLT map
az logic integration-account map create \
  --resource-group myRG \
  --integration-account-name myIntegrationAccount \
  --name OrderToInvoice \
  --map-type Xslt \
  --content @order-to-invoice.xslt

# List maps
az logic integration-account map list \
  --resource-group myRG \
  --integration-account-name myIntegrationAccount
```
