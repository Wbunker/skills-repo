# Azure CLI & Cloud Shell — CLI Reference
For service concepts, see [cli-shell-capabilities.md](cli-shell-capabilities.md).

## Authentication & Account Management

```bash
# --- Authentication ---
az login                                          # Interactive browser login
az login --use-device-code                        # Device code flow (headless/SSH)
az login --identity                               # Managed identity (from Azure resource)
az login --identity --username <client-id>        # Specific user-assigned managed identity
az login --service-principal \
  --username $AZURE_CLIENT_ID \
  --password $AZURE_CLIENT_SECRET \
  --tenant $AZURE_TENANT_ID                       # Service principal with secret
az logout                                         # Sign out current account

# --- Account/Subscription Management ---
az account list                                   # List all accessible subscriptions
az account list --output table                    # Human-readable subscription list
az account show                                   # Show current active subscription
az account set --subscription "My Subscription"  # Switch active subscription by name
az account set --subscription 00000000-0000-0000-0000-000000000000  # by ID
az account get-access-token                       # Get bearer token for current session
az account get-access-token --resource https://management.azure.com/  # Specific resource token
```

## Configuration

```bash
# --- CLI Configuration ---
az configure --defaults group=myRG location=eastus  # Set persistent defaults
az config set defaults.group=myRG                   # Alternative config syntax
az config get defaults.group                         # Read a config value
az config unset defaults.group                       # Remove a default
az configure --list-defaults                         # Show all configured defaults

# --- Interactive Mode ---
az interactive                                       # Launch auto-complete shell with embedded docs

# --- Extensions ---
az extension add --name azure-devops               # Install an extension
az extension add --name aks-preview                # Install AKS preview features
az extension list                                  # List installed extensions
az extension list --output table                   # Tabular view
az extension update --name azure-devops            # Update an extension
az extension remove --name azure-devops            # Remove an extension
az extension list-available --output table         # Browse installable extensions
```

## Resource Groups

```bash
# --- Resource Groups ---
az group create --name myRG --location eastus      # Create resource group
az group list                                       # List all resource groups
az group list --query "[?location=='eastus']" -o table  # Filter by location
az group show --name myRG                           # Get details for one group
az group exists --name myRG                         # Returns true/false
az group update --name myRG --tags env=prod owner=team  # Update tags
az group delete --name myRG --yes --no-wait        # Delete (skip confirmation, async)
az group export --name myRG                         # Export ARM template of all resources
az group deployment create --resource-group myRG \
  --template-file azuredeploy.json \
  --parameters @azuredeploy.parameters.json        # Deploy ARM template to group
```

## Resource Management

```bash
# --- Resource Listing & Inspection ---
az resource list                                    # List all resources in subscription
az resource list --resource-group myRG             # Filter by resource group
az resource list --resource-type Microsoft.Compute/virtualMachines  # Filter by type
az resource list --tag env=prod                    # Filter by tag
az resource list --query "[].{name:name, type:type, rg:resourceGroup}" -o table

az resource show \
  --resource-group myRG \
  --name myVM \
  --resource-type Microsoft.Compute/virtualMachines  # Get full resource JSON

az resource delete \
  --resource-group myRG \
  --name myVM \
  --resource-type Microsoft.Compute/virtualMachines

az resource tag \
  --resource-group myRG \
  --name myVM \
  --resource-type Microsoft.Compute/virtualMachines \
  --tags env=prod costcenter=engineering            # Apply tags

az resource move \
  --destination-group newRG \
  --ids /subscriptions/.../resourceGroups/myRG/providers/Microsoft.Compute/virtualMachines/myVM
```

## RBAC & Role Assignments

```bash
# --- Role Assignments ---
az role assignment create \
  --assignee user@example.com \
  --role "Contributor" \
  --resource-group myRG                            # Assign Contributor to user on RG

az role assignment create \
  --assignee <sp-object-id> \
  --role "Storage Blob Data Contributor" \
  --scope /subscriptions/<subId>/resourceGroups/myRG/providers/Microsoft.Storage/storageAccounts/myacct

az role assignment list --resource-group myRG      # List all role assignments on RG
az role assignment list --assignee user@example.com  # All roles for a user
az role assignment delete \
  --assignee user@example.com \
  --role "Contributor" \
  --resource-group myRG

az role definition list --output table             # List all built-in roles
az role definition list --name "Contributor"       # Details for a specific role
az role definition create --role-definition @custom-role.json  # Create custom role
```

## Bicep

```bash
# --- Bicep ---
az bicep install                                    # Install Bicep CLI
az bicep upgrade                                    # Upgrade to latest Bicep version
az bicep version                                    # Show installed Bicep version
az bicep build --file main.bicep                   # Compile Bicep → ARM JSON
az bicep decompile --file azuredeploy.json         # Decompile ARM JSON → Bicep
az bicep lint --file main.bicep                    # Lint Bicep file for issues

# Deploy Bicep directly (az CLI compiles automatically)
az deployment group create \
  --resource-group myRG \
  --template-file main.bicep \
  --parameters @main.parameters.json

az deployment group what-if \
  --resource-group myRG \
  --template-file main.bicep \
  --parameters env=prod                            # Preview changes before deploy

az deployment sub create \
  --location eastus \
  --template-file subscription-level.bicep         # Subscription-scope deployment
```

## Useful Scripting Patterns

```bash
# Wait for a resource to reach a state
az vm wait --name myVM --resource-group myRG --created

# Output only a single value (for scripting)
RG_ID=$(az group show --name myRG --query id -o tsv)

# Loop over resources
az vm list --resource-group myRG --query "[].name" -o tsv | while read name; do
  echo "Processing: $name"
  az vm start --name "$name" --resource-group myRG --no-wait
done

# Check if resource exists before creating
if ! az group exists --name myRG; then
  az group create --name myRG --location eastus
fi
```
