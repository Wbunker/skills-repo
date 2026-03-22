# Microsoft Entra ID & RBAC — CLI Reference

Entra ID (Azure AD) operations use `az ad` commands. Azure RBAC uses `az role`. Some operations require Microsoft Graph permissions and may require `az rest` calls for advanced scenarios.

---

## Users

```bash
# Create a new user
az ad user create \
  --display-name "Jane Smith" \
  --user-principal-name jane.smith@contoso.onmicrosoft.com \
  --password "TemporaryPassword123!" \
  --force-change-password-next-sign-in true \
  --mail-nickname janesmith

# Show user details
az ad user show \
  --id jane.smith@contoso.onmicrosoft.com

# Show user by Object ID
az ad user show \
  --id 00000000-0000-0000-0000-000000000001

# List all users (paginated)
az ad user list \
  --output table

# Filter users by display name
az ad user list \
  --filter "startswith(displayName,'Jane')" \
  --output table

# List guest users only
az ad user list \
  --filter "userType eq 'Guest'" \
  --output table

# Update user properties (e.g., disable account)
az ad user update \
  --id jane.smith@contoso.onmicrosoft.com \
  --account-enabled false

# Update user job title and department
az ad user update \
  --id jane.smith@contoso.onmicrosoft.com \
  --job-title "Senior Engineer" \
  --department "Platform Engineering"

# Reset user password
az ad user update \
  --id jane.smith@contoso.onmicrosoft.com \
  --password "NewPassword123!" \
  --force-change-password-next-sign-in true

# Delete a user
az ad user delete \
  --id jane.smith@contoso.onmicrosoft.com

# Get user's Object ID (useful for role assignments)
az ad user show \
  --id jane.smith@contoso.onmicrosoft.com \
  --query id \
  --output tsv

# List groups the user belongs to
az ad user get-member-groups \
  --id jane.smith@contoso.onmicrosoft.com \
  --security-enabled-only false \
  --output table
```

---

## Groups

```bash
# Create a security group
az ad group create \
  --display-name "Platform Engineers" \
  --mail-nickname platform-engineers

# Create a mail-enabled security group (requires Exchange Online)
# Use Azure portal or Graph API for mail-enabled groups

# Show group details
az ad group show \
  --group "Platform Engineers"

# Show group by Object ID
az ad group show \
  --group 00000000-0000-0000-0000-000000000002

# List all groups
az ad group list \
  --output table

# Filter groups by display name prefix
az ad group list \
  --filter "startswith(displayName,'Platform')" \
  --output table

# Add a user to a group
az ad group member add \
  --group "Platform Engineers" \
  --member-id 00000000-0000-0000-0000-000000000001

# Add a service principal to a group
az ad group member add \
  --group "Platform Engineers" \
  --member-id <service-principal-object-id>

# List group members
az ad group member list \
  --group "Platform Engineers" \
  --output table

# Check if a user is a member of a group
az ad group member check \
  --group "Platform Engineers" \
  --member-id 00000000-0000-0000-0000-000000000001

# Remove a user from a group
az ad group member remove \
  --group "Platform Engineers" \
  --member-id 00000000-0000-0000-0000-000000000001

# Delete a group
az ad group delete \
  --group "Platform Engineers"

# Get Object ID of a group
az ad group show \
  --group "Platform Engineers" \
  --query id \
  --output tsv
```

---

## Service Principals

```bash
# Create a service principal with Contributor role on a subscription (creates app + SP)
az ad sp create-for-rbac \
  --name mySP \
  --role Contributor \
  --scopes /subscriptions/<sub-id>

# Create a service principal with Reader role on a resource group
az ad sp create-for-rbac \
  --name myReadOnlySP \
  --role Reader \
  --scopes /subscriptions/<sub>/resourceGroups/myRG

# Create a service principal with Federated Credential (no secret — for GitHub Actions)
az ad sp create-for-rbac \
  --name myGitHubSP \
  --role Contributor \
  --scopes /subscriptions/<sub-id> \
  --sdk-auth false

# Show service principal details
az ad sp show \
  --id myapp  # by display name, app ID, or object ID

# Show SP by app ID (client ID)
az ad sp show \
  --id 00000000-0000-0000-0000-000000000003

# List service principals
az ad sp list \
  --filter "startswith(displayName,'my')" \
  --output table

# List all service principals for a specific app
az ad sp list \
  --filter "appId eq '00000000-0000-0000-0000-000000000003'" \
  --output table

# Reset (rotate) service principal credentials
az ad sp credential reset \
  --id myapp \
  --years 1

# Delete a service principal's credentials
az ad sp credential delete \
  --id myapp \
  --key-id <credential-key-id>

# List credentials for a service principal
az ad sp credential list \
  --id myapp \
  --output table

# Delete a service principal
az ad sp delete \
  --id myapp
```

---

## App Registrations

```bash
# Create an app registration
az ad app create \
  --display-name myWebApp \
  --sign-in-audience AzureADMyOrg \
  --web-redirect-uris "https://myapp.example.com/auth/callback"

# List app registrations
az ad app list \
  --display-name myWebApp \
  --output table

# Show app registration details
az ad app show \
  --id <app-id-or-object-id>

# Update app registration (add redirect URI)
az ad app update \
  --id <app-id> \
  --web-redirect-uris "https://myapp.example.com/auth/callback" "https://localhost:5001/auth/callback"

# Add API permission to app (require Graph User.Read)
az ad app permission add \
  --id <app-id> \
  --api 00000003-0000-0000-c000-000000000000 \
  --api-permissions e1fe6dd8-ba31-4d61-89e7-88639da4683d=Scope  # User.Read delegated

# Grant admin consent for API permissions
az ad app permission grant \
  --id <app-id> \
  --api 00000003-0000-0000-c000-000000000000 \
  --scope User.Read

# Grant admin consent for all permissions
az ad app permission admin-consent \
  --id <app-id>

# Add a federated credential (GitHub Actions OIDC)
az ad app federated-credential create \
  --id <app-id> \
  --parameters '{
    "name": "GitHubActions-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:myorg/myrepo:ref:refs/heads/main",
    "description": "GitHub Actions main branch",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# Delete an app registration
az ad app delete \
  --id <app-id>
```

---

## Managed Identity

```bash
# Create a user-assigned managed identity
az identity create \
  --name myManagedIdentity \
  --resource-group myRG \
  --location eastus

# Show managed identity details (note principalId for RBAC)
az identity show \
  --name myManagedIdentity \
  --resource-group myRG

# Get managed identity principal ID (for role assignments)
az identity show \
  --name myManagedIdentity \
  --resource-group myRG \
  --query principalId \
  --output tsv

# Assign managed identity to a VM
az vm identity assign \
  --name myVM \
  --resource-group myRG \
  --identities myManagedIdentity

# Enable system-assigned identity on a VM
az vm identity assign \
  --name myVM \
  --resource-group myRG

# Get system-assigned identity principal ID from a VM
az vm show \
  --name myVM \
  --resource-group myRG \
  --query identity.principalId \
  --output tsv

# Grant managed identity Storage Blob Data Reader role on a storage account
MI_PRINCIPAL_ID=$(az identity show --name myManagedIdentity --resource-group myRG --query principalId --output tsv)
az role assignment create \
  --assignee $MI_PRINCIPAL_ID \
  --role "Storage Blob Data Reader" \
  --scope /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/myStorage

# Assign managed identity to App Service
az webapp identity assign \
  --name myWebApp \
  --resource-group myRG \
  --identities /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myManagedIdentity

# List user-assigned managed identities
az identity list \
  --resource-group myRG \
  --output table

# Delete a user-assigned managed identity
az identity delete \
  --name myManagedIdentity \
  --resource-group myRG
```

---

## RBAC Role Assignments

```bash
# Assign a built-in role to a user on a resource group
az role assignment create \
  --assignee jane.smith@contoso.com \
  --role "Contributor" \
  --scope /subscriptions/<sub>/resourceGroups/myRG

# Assign a role to a group (recommended over individual users)
GROUP_ID=$(az ad group show --group "Platform Engineers" --query id --output tsv)
az role assignment create \
  --assignee $GROUP_ID \
  --role "Reader" \
  --scope /subscriptions/<sub-id>

# Assign a role at Management Group scope
az role assignment create \
  --assignee jane.smith@contoso.com \
  --role "Reader" \
  --scope /providers/Microsoft.Management/managementGroups/myMG

# Assign a service-specific role on a specific resource
az role assignment create \
  --assignee <sp-or-mi-principal-id> \
  --role "Key Vault Secrets User" \
  --scope /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.KeyVault/vaults/myKeyVault

# List role assignments at a scope
az role assignment list \
  --scope /subscriptions/<sub>/resourceGroups/myRG \
  --output table

# List all role assignments for a specific user
az role assignment list \
  --assignee jane.smith@contoso.com \
  --all \
  --output table

# List role assignments including inherited (from parent scopes)
az role assignment list \
  --scope /subscriptions/<sub>/resourceGroups/myRG \
  --include-inherited \
  --output table

# Delete a role assignment
az role assignment delete \
  --assignee jane.smith@contoso.com \
  --role "Contributor" \
  --scope /subscriptions/<sub>/resourceGroups/myRG

# List all built-in roles
az role definition list \
  --output table \
  --query "[].{Name:roleName,Description:description}"

# Show details of a specific role
az role definition list \
  --name "Contributor" \
  --output json

# Create a custom role from JSON file
az role definition create \
  --role-definition custom-vm-operator.json

# Update a custom role
az role definition update \
  --role-definition custom-vm-operator-updated.json

# Delete a custom role
az role definition delete \
  --name "Custom VM Operator"
```

---

## PIM (Privileged Identity Management)

PIM operations require the `az pim` command group (may be in preview). Some operations require REST API calls via `az rest`.

```bash
# Create an eligible role assignment via PIM (preview commands)
az pim role eligibility create \
  --role-definition-id <role-definition-id> \
  --principal-id <user-or-group-object-id> \
  --scope /subscriptions/<sub-id> \
  --start-date-time "2024-01-01T00:00:00Z" \
  --expiration-type NoExpiration

# Create an active role assignment via PIM (permanent active — use sparingly)
az pim role assignment create \
  --role-definition-id <role-definition-id> \
  --principal-id <user-object-id> \
  --scope /subscriptions/<sub-id> \
  --justification "Break-glass account activation"

# List eligible role assignments
az pim role eligibility list \
  --scope /subscriptions/<sub-id> \
  --output table

# Activate an eligible role (user self-service)
az pim role activation create \
  --role-definition-id <role-definition-id> \
  --scope /subscriptions/<sub-id> \
  --justification "Deploying production release" \
  --duration PT4H  # 4 hours

# List active role assignments (including PIM-activated)
az pim role assignment list \
  --scope /subscriptions/<sub-id> \
  --output table
```
