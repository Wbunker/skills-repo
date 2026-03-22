# Authentication — CLI Reference
For service concepts, see [auth-capabilities.md](auth-capabilities.md).

## App Service Easy Auth

```bash
# --- View Current Auth Configuration ---
az webapp auth show \
  --resource-group myRG \
  --name myWebApp                              # Show current Easy Auth configuration

# --- Enable Easy Auth with Microsoft (Entra ID) ---
az webapp auth microsoft update \
  --resource-group myRG \
  --name myWebApp \
  --client-id <app-registration-client-id> \
  --client-secret <client-secret> \
  --issuer https://sts.windows.net/<tenant-id>/v2.0 \
  --allowed-audiences api://mywebapp

# Enable with full configuration
az webapp auth update \
  --resource-group myRG \
  --name myWebApp \
  --enabled true \
  --action LoginWithAzureActiveDirectory \
  --aad-client-id <client-id> \
  --aad-client-secret <client-secret>

# --- Enable Easy Auth with Google ---
az webapp auth google update \
  --resource-group myRG \
  --name myWebApp \
  --client-id <google-client-id> \
  --client-secret <google-client-secret> \
  --allowed-audiences mywebapp

# --- Enable Easy Auth with Facebook ---
az webapp auth facebook update \
  --resource-group myRG \
  --name myWebApp \
  --app-id <facebook-app-id> \
  --app-secret <facebook-app-secret>

# --- Enable Easy Auth with GitHub ---
az webapp auth github update \
  --resource-group myRG \
  --name myWebApp \
  --client-id <github-client-id> \
  --client-secret <github-client-secret>

# --- Configure Easy Auth (V2 authsettings) ---
az webapp auth update \
  --resource-group myRG \
  --name myWebApp \
  --enabled true \
  --action Return401 \
  --token-store true \
  --runtime-version "~2"                       # V2 auth; return 401 for unauthenticated (API mode)

# Require Entra ID; redirect browser to login
az webapp auth update \
  --resource-group myRG \
  --name myWebApp \
  --enabled true \
  --action RedirectToLoginPage \
  --aad-client-id <client-id> \
  --aad-client-secret <client-secret>

# Allow only specific Entra ID tenant(s)
az webapp auth microsoft update \
  --resource-group myRG \
  --name myWebApp \
  --client-id <client-id> \
  --client-secret <client-secret> \
  --issuer https://sts.windows.net/<tenant-id>/  # Single-tenant

# --- Disable Easy Auth ---
az webapp auth update \
  --resource-group myRG \
  --name myWebApp \
  --enabled false                              # Disable authentication

# --- View auth settings for a slot ---
az webapp auth show \
  --resource-group myRG \
  --name myWebApp \
  --slot staging                               # Check auth config on staging slot

# --- Functions Easy Auth ---
az functionapp auth update \
  --resource-group myRG \
  --name myFunctionApp \
  --enabled true \
  --action LoginWithAzureActiveDirectory \
  --aad-client-id <client-id> \
  --aad-client-secret <client-secret>          # Enable Easy Auth on Function App

az functionapp auth show \
  --resource-group myRG \
  --name myFunctionApp                         # Show Function App auth config
```

## Entra ID App Registration (for Auth Flows)

```bash
# --- Create App Registration ---
# Single-page application (SPA)
az ad app create \
  --display-name "My SPA App" \
  --sign-in-audience AzureADMyOrg \
  --spa-redirect-uris "https://myapp.com" "http://localhost:3000"  # Register SPA with PKCE

# Web app with server-side auth
az ad app create \
  --display-name "My Web App" \
  --sign-in-audience AzureADMyOrg \
  --web-redirect-uris "https://myapp.azurewebsites.net/.auth/login/aad/callback" "http://localhost:5000/.auth/login/aad/callback"

# Mobile/native app (public client)
az ad app create \
  --display-name "My Mobile App" \
  --sign-in-audience AzureADMyOrg \
  --public-client-redirect-uris "myapp://auth"  # Custom URI scheme for mobile

# --- Configure App Registration ---
# Add Microsoft Graph permissions (for Entra External ID user info)
az ad app permission add \
  --id <app-id> \
  --api 00000003-0000-0000-c000-000000000000 \
  --api-permissions 64a6cdd6-aab1-4aaf-94b8-3cc8405e90d0=Scope  # User.Read (delegated)

# Grant admin consent
az ad app permission admin-consent --id <app-id>

# --- Add Redirect URIs ---
az ad app update \
  --id <app-id> \
  --web-redirect-uris "https://myapp.com/.auth/login/aad/callback" "https://www.myapp.com/.auth/login/aad/callback"

# --- Create Client Secret ---
az ad app credential reset \
  --id <app-id> \
  --append \
  --years 1 \
  --display-name "Production 2025"             # Add client secret

# --- Create Client Certificate (more secure than secret) ---
az ad app credential reset \
  --id <app-id> \
  --cert "@certificate.pem" \
  --append                                     # Add certificate credential

# Show app manifest
az ad app show --id <app-id>

# List all app registrations
az ad app list --display-name "My" --output table

# Delete app registration
az ad app delete --id <app-id>
```

## Entra External ID

```bash
# --- Create External Tenant (requires admin, done in portal or via REST) ---
# External tenants are created via Entra admin center or Graph API
# CLI limited for B2C tenant type

# For existing B2C tenant management via CLI:
az login --tenant <b2c-tenant-name>.onmicrosoft.com  # Login to B2C tenant

# --- B2C Tenant App Registration ---
az ad app create \
  --display-name "B2C Web App" \
  --sign-in-audience AzureADandPersonalMicrosoftAccount \
  --web-redirect-uris "https://myapp.com/signin-oidc"

# --- User Management via Graph (Entra External ID) ---
# Create external user
az rest --method POST \
  --url "https://graph.microsoft.com/v1.0/users" \
  --resource "https://graph.microsoft.com" \
  --body '{
    "displayName": "Jane Smith",
    "identities": [{
      "signInType": "emailAddress",
      "issuer": "mytenant.onmicrosoft.com",
      "issuerAssignedId": "jane@example.com"
    }],
    "passwordProfile": {
      "forceChangePasswordNextSignIn": true,
      "password": "TempPassword123!"
    }
  }'

# List external users
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/users?\$filter=userType eq 'Guest'" \
  --resource "https://graph.microsoft.com"

# Get user's sign-in activity
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/users/{userId}?\$select=signInActivity" \
  --resource "https://graph.microsoft.com"

# --- B2C via PowerShell (Azure AD B2C module) ---
# Install module
Install-Module -Name Microsoft.Graph -Scope CurrentUser -Force

Connect-MgGraph -TenantId "<b2c-tenant-id>" -Scopes "User.ReadWrite.All", "Directory.ReadWrite.All"

# List B2C users
Get-MgUser -Filter "creationType eq 'LocalAccount'" | Select DisplayName, Id, Identities

# Create B2C local account user
$passwordProfile = @{
    Password = "TempPass123!"
    ForceChangePasswordNextSignIn = $true
}
$identities = @(@{
    SignInType = "emailAddress"
    Issuer = "yourtenant.onmicrosoft.com"
    IssuerAssignedId = "newuser@example.com"
})
New-MgUser -DisplayName "New User" -Identities $identities -PasswordProfile $passwordProfile -AccountEnabled

# Reset a B2C user's password
Update-MgUser -UserId <user-id> -PasswordProfile @{Password = "NewTemp123!"; ForceChangePasswordNextSignIn = $true}

# Delete a B2C user
Remove-MgUser -UserId <user-id>
```

## Static Web Apps Auth (Configuration-based)

```bash
# SWA auth is configured via staticwebapp.config.json — no CLI commands for auth
# Use app settings to store provider secrets

az staticwebapp appsettings set \
  --resource-group myRG \
  --name myStaticApp \
  --setting-names \
    GOOGLE_CLIENT_ID="google-client-id" \
    GOOGLE_CLIENT_SECRET="google-client-secret"  # Store OAuth credentials as app settings

# Reference in staticwebapp.config.json:
# "google": {
#   "registration": {
#     "clientIdSettingName": "GOOGLE_CLIENT_ID",
#     "clientSecretSettingName": "GOOGLE_CLIENT_SECRET"
#   }
# }

# List app settings (verify env vars are set)
az staticwebapp appsettings list \
  --resource-group myRG \
  --name myStaticApp

# Test auth locally with SWA CLI
swa start http://localhost:3000 \
  --api-location ./api
# Navigate to http://localhost:4280/.auth/login/github for local auth simulation
```
