# Microsoft 365 Integration — CLI Reference
For service concepts, see [m365-integration-capabilities.md](m365-integration-capabilities.md).

## App Registration (for Graph API access)

```bash
# --- Register an Entra ID App for Graph API ---
az ad app create \
  --display-name "My Graph API App" \
  --sign-in-audience AzureADMyOrg            # Single-tenant app

az ad app create \
  --display-name "My Multi-tenant Graph App" \
  --sign-in-audience AzureADMultipleOrgs     # Multi-tenant app

# Get app details
az ad app list --display-name "My Graph API App" --output table
az ad app show --id <app-id>

# --- Add Graph API Permissions ---
# Add User.Read.All (application permission — no sign-in required)
az ad app permission add \
  --id <app-id> \
  --api 00000003-0000-0000-c000-000000000000 \
  --api-permissions df021288-bdef-4463-88db-98f22de89214=Role  # User.Read.All (Application)

# Add Mail.Read (delegated permission)
az ad app permission add \
  --id <app-id> \
  --api 00000003-0000-0000-c000-000000000000 \
  --api-permissions 570282fd-fa5c-430d-a7fd-fc8dc98a9dca=Scope  # Mail.Read (Delegated)

# Common Microsoft Graph API permissions GUIDs
# User.Read.All (App): df021288-bdef-4463-88db-98f22de89214
# Group.ReadWrite.All (App): 62a82d76-70ea-4c6b-aae4-49462d0e1a0e
# Mail.ReadWrite (App): e2a3a72e-5f79-4c64-b1b1-878b674786c9
# Calendars.ReadWrite (App): ef54d2bf-783f-4e0f-bca1-3210c0444d99
# Sites.ReadWrite.All (App): 9492366f-7969-46a4-8d15-ed1a20078fff
# ChannelMessage.Read.All (App): 7b2449af-6ccd-4f69-bdd5-35ab5b08b5af

# List assigned permissions
az ad app permission list --id <app-id>

# Grant admin consent for all permissions (admin required)
az ad app permission admin-consent --id <app-id>

# Check grant status
az ad app permission list-grants --id <app-id>

# --- Create Service Principal ---
az ad sp create --id <app-id>                # Create service principal for app
az ad sp show --id <app-id>                  # Show service principal

# --- Create Client Secret ---
az ad app credential reset \
  --id <app-id> \
  --append \
  --years 2 \
  --display-name "Production secret"         # Create new client secret (append to preserve existing)

# List credentials (does not show secret values)
az ad app credential list --id <app-id>

# Delete a credential
az ad app credential delete \
  --id <app-id> \
  --key-id <credential-id>                   # Remove specific credential

# --- Federated Credentials (for GitHub Actions / Workload Identity) ---
az ad app federated-credential create \
  --id <app-id> \
  --parameters '{
    "name": "github-actions-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:myorg/myrepo:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'                                          # Allow GitHub Actions to use app without secret

az ad app federated-credential list --id <app-id>  # List federated credentials
```

## Microsoft Graph CLI (mgc)

```bash
# --- Install Microsoft Graph CLI ---
# Windows (via winget)
winget install Microsoft.Graph.CLI

# macOS/Linux
brew install microsoftgraph/tap/msgraph-cli

# --- Authentication ---
mgc login                                    # Interactive login (browser)
mgc login --strategy DeviceCode             # Device code flow
mgc login \
  --tenant-id <tenantId> \
  --client-id <clientId> \
  --client-secret <secret>                   # Service principal auth
mgc logout

# --- User Management ---
mgc users list                               # List all users
mgc users list --select displayName,mail,department  # Select specific fields
mgc users list --filter "department eq 'Engineering'"  # Filter users
mgc users list --top 50 --skip 0            # Paginate results

mgc users get --user-id user@example.com    # Get specific user by UPN or ID
mgc users get --user-id me                  # Get current signed-in user

mgc users create \
  --body '{"displayName":"New User","mailNickname":"newuser","userPrincipalName":"newuser@company.com","accountEnabled":true,"passwordProfile":{"forceChangePasswordNextSignIn":true,"password":"TempPass123!"}}'

mgc users update \
  --user-id user@example.com \
  --body '{"department": "Engineering", "jobTitle": "Senior Developer"}'

mgc users delete --user-id user@example.com  # Delete user

# --- Group Management ---
mgc groups list                              # List all groups
mgc groups list --filter "displayName eq 'Engineering Team'"
mgc groups get --group-id <group-id>         # Get group details
mgc groups create --body '{"displayName":"My Group","mailEnabled":false,"mailNickname":"mygroup","securityEnabled":true}'
mgc groups members list --group-id <group-id>  # List group members
mgc groups members add --group-id <group-id> --body '{"@odata.id":"https://graph.microsoft.com/v1.0/users/<user-id>"}'

# --- Mail ---
mgc users messages list --user-id me        # List recent emails
mgc users messages list \
  --user-id me \
  --top 10 \
  --filter "isRead eq false"                 # Unread emails

mgc users send-mail --user-id me \
  --body '{"message":{"subject":"Hello","body":{"contentType":"Text","content":"Hello!"},"toRecipients":[{"emailAddress":{"address":"user@example.com"}}]}}'

# --- Calendar ---
mgc users calendar-view list \
  --user-id me \
  --start-date-time "2024-01-15T00:00:00Z" \
  --end-date-time "2024-01-16T00:00:00Z"    # Get today's calendar events

# --- Teams ---
mgc teams list                               # List all teams user belongs to
mgc teams get --team-id <team-id>            # Get team details
mgc teams channels list --team-id <team-id> # List channels in a team

# Send message to Teams channel
mgc teams channels messages create \
  --team-id <team-id> \
  --channel-id <channel-id> \
  --body '{"body":{"content":"Hello from mgc CLI!","contentType":"text"}}'

# --- SharePoint ---
mgc sites list --search "Marketing"         # Search for SharePoint sites
mgc sites get --site-id "company.sharepoint.com,{site-id},{web-id}"  # Get site
mgc sites lists list --site-id <site-id>    # List lists in SharePoint site
mgc sites lists items list \
  --site-id <site-id> \
  --list-id <list-id> \
  --expand fields                            # Get list items with all fields
```

## CLI for Microsoft 365 (m365 CLI)

```bash
# --- Install ---
npm install -g @pnp/cli-microsoft365

# --- Authentication ---
m365 login                                   # Interactive login
m365 login --authType password \
  --userName admin@company.com \
  --password "..."                           # Username/password (not recommended)
m365 status                                  # Check login status
m365 logout

# --- SharePoint Operations ---
m365 spo site list                           # List all SharePoint sites
m365 spo site get --url "https://company.sharepoint.com/sites/mysite"
m365 spo site add \
  --url "https://company.sharepoint.com/sites/newsite" \
  --title "New Team Site" \
  --type TeamSite                            # Create SharePoint site

m365 spo list get --webUrl "https://company.sharepoint.com/sites/mysite" --title "Tasks"  # Get list
m365 spo listitem add \
  --webUrl "https://company.sharepoint.com/sites/mysite" \
  --listTitle "Tasks" \
  --Title "New task" \
  --Status "In Progress"                     # Add list item

# --- SPFx Deployment ---
m365 spo app add \
  --filePath ./sharepoint/solution/my-webpart.sppkg \
  --appCatalogUrl "https://company.sharepoint.com/sites/appcatalog"

m365 spo app deploy \
  --name "my-webpart.sppkg" \
  --appCatalogUrl "https://company.sharepoint.com/sites/appcatalog"

# --- Teams Operations ---
m365 teams team list                         # List teams
m365 teams channel list --teamId <team-id>  # List channels
m365 teams message send \
  --teamId <team-id> \
  --channelId <channel-id> \
  --message "Hello from m365 CLI!"          # Send Teams channel message

# --- Entra ID (formerly Azure AD) ---
m365 aad user list                           # List users
m365 aad app add --name "My New App"         # Register app
m365 aad app permission add \
  --appId <app-id> \
  --resource "Microsoft Graph" \
  --scope "User.Read"                        # Add permission to app
```

## Graph API via az rest

```bash
# --- Call Microsoft Graph via az CLI (using az rest) ---
# Get current user
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/me" \
  --resource "https://graph.microsoft.com"

# List all users
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/users" \
  --resource "https://graph.microsoft.com"

# Filter users
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/users?\$filter=department eq 'Engineering'" \
  --resource "https://graph.microsoft.com"

# Send email via Graph (as delegated user)
az rest --method POST \
  --url "https://graph.microsoft.com/v1.0/me/sendMail" \
  --resource "https://graph.microsoft.com" \
  --body '{
    "message": {
      "subject": "Test from az rest",
      "body": {"contentType": "Text", "content": "Hello!"},
      "toRecipients": [{"emailAddress": {"address": "user@example.com"}}]
    }
  }'

# Get Teams channels for a team
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/teams/<team-id>/channels" \
  --resource "https://graph.microsoft.com"

# Create group
az rest --method POST \
  --url "https://graph.microsoft.com/v1.0/groups" \
  --resource "https://graph.microsoft.com" \
  --body '{
    "displayName": "Engineering Team",
    "mailEnabled": false,
    "mailNickname": "engineering-team",
    "securityEnabled": true
  }'
```
