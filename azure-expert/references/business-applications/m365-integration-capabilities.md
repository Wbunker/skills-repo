# Microsoft 365 Integration — Capabilities Reference
For CLI commands, see [m365-integration-cli.md](m365-integration-cli.md).

## Microsoft Graph API

**Purpose**: The unified REST API endpoint for all Microsoft 365 services and Microsoft identity platform. A single endpoint (`https://graph.microsoft.com`) provides access to data across Azure AD/Entra ID, Exchange, SharePoint, Teams, OneDrive, Planner, Intune, Defender, and more.

### Base URL and Versions

| Version | URL | Status |
|---|---|---|
| **v1.0** | `https://graph.microsoft.com/v1.0/` | Stable; production use |
| **beta** | `https://graph.microsoft.com/beta/` | Preview features; may change |

### Key Resource Areas

| Area | Resources | Common Operations |
|---|---|---|
| **Identity** | users, groups, servicePrincipals, applications, directoryRoles | CRUD users, group membership, app registration |
| **Mail** | messages, mailFolders, attachments | Read/send/move email; manage folders |
| **Calendar** | events, calendars, calendarGroups | Create/update meetings; find meeting times |
| **Files** | driveItems, drives, sites | Upload/download files; OneDrive and SharePoint |
| **Teams** | teams, channels, chats, chatMessages | Send messages; create teams; manage channels |
| **SharePoint** | sites, lists, listItems | CRUD items in SharePoint lists |
| **Planner** | plans, tasks, buckets | Manage Planner tasks and boards |
| **Security** | alerts, incidents, secureScores | Read security alerts; manage incidents |
| **Intune** | managedDevices, deviceCompliancePolicies | Device management queries |
| **Reports** | usage reports, audit logs | Microsoft 365 usage and activity reports |

### Authentication and Permissions

#### Permission Types

| Type | Description | When Used |
|---|---|---|
| **Delegated** | Permissions granted to app acting on behalf of a signed-in user; limited by user's rights | Interactive apps (user must sign in) |
| **Application** | Permissions granted to app running as its own identity (no user context) | Background services, daemons, automation |

#### Common Permission Scopes

| Permission | Type | Access |
|---|---|---|
| `User.Read` | Delegated | Read current user's profile |
| `User.ReadWrite.All` | Application | Read/write all users |
| `Mail.Read` | Delegated | Read user's mail |
| `Mail.Send` | Delegated | Send mail as user |
| `Calendars.ReadWrite` | Delegated | Read/write user's calendar |
| `Files.ReadWrite.All` | Delegated | Read/write all files user can access |
| `Sites.ReadWrite.All` | Application | Read/write SharePoint sites |
| `Chat.ReadWrite` | Delegated | Read/send Teams chat messages |
| `ChannelMessage.Send` | Delegated | Send messages to Teams channels |
| `Group.ReadWrite.All` | Application | Manage all groups and teams |

### Graph SDK Libraries

| Language | Package |
|---|---|
| **Python** | `pip install msgraph-sdk` (`msgraph.generated.*` classes) |
| **.NET** | `dotnet add package Microsoft.Graph` |
| **JavaScript/TypeScript** | `npm install @microsoft/microsoft-graph-client` |
| **Java** | `com.microsoft.graph:microsoft-graph` (Maven) |
| **Go** | `github.com/microsoftgraph/msgraph-sdk-go` |
| **PHP** | `composer require microsoft/microsoft-graph` |

### Python SDK Example

```python
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient

credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)
client = GraphServiceClient(credential, scopes=["https://graph.microsoft.com/.default"])

# List users
users = await client.users.get()
for user in users.value:
    print(f"{user.display_name}: {user.mail}")

# Send email
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import SendMailPostRequestBody
from msgraph.generated.models.message import Message
# ... (build Message object and call client.users.by_user_id(user_id).send_mail.post())
```

### REST API Examples

```bash
# Get current user
GET https://graph.microsoft.com/v1.0/me

# Get all users (application permission)
GET https://graph.microsoft.com/v1.0/users

# Filter users by department
GET https://graph.microsoft.com/v1.0/users?$filter=department eq 'Engineering'

# Get user's mail (last 10 messages)
GET https://graph.microsoft.com/v1.0/me/messages?$top=10&$orderby=receivedDateTime desc

# Send a Teams channel message
POST https://graph.microsoft.com/v1.0/teams/{teamId}/channels/{channelId}/messages
{
  "body": {"content": "Hello team!", "contentType": "text"}
}

# Get SharePoint site items
GET https://graph.microsoft.com/v1.0/sites/{siteId}/lists/{listId}/items?$expand=fields

# Create a calendar event
POST https://graph.microsoft.com/v1.0/me/events
```

### Graph Explorer

- Browser tool at `developer.microsoft.com/graph/graph-explorer`
- Sign in with Microsoft 365 account; browse and run Graph API calls interactively
- Auto-generates code samples in multiple languages
- Try API calls before implementing in application

---

## Microsoft Teams App Development

### App Types

| Type | Description | Implementation |
|---|---|---|
| **Tab** | Custom web page embedded in Teams (personal, channel, or meeting tab) | Any web app; use Teams JavaScript SDK |
| **Bot** | Conversational AI in 1:1 or channel chats | Azure Bot Framework + Teams Bot SDK |
| **Message Extension** | Search, create, or act on content from compose box | Azure Bot Framework |
| **Connector** | Incoming webhooks or card-based notifications | Incoming webhook URL or adaptive card connector |
| **Meeting Extension** | In-meeting apps, meeting stage, side panel | Teams Meeting API |
| **Copilot Plugin** | Extend Microsoft Copilot with app capabilities | Plugin manifest |

### Teams JavaScript SDK

```typescript
import * as microsoftTeams from "@microsoft/teams-js";

// Initialize
await microsoftTeams.app.initialize();

// Get current context (user, team, channel)
const context = await microsoftTeams.app.getContext();
console.log(context.user.displayName, context.channel.id);

// Authentication (SSO)
const token = await microsoftTeams.authentication.getAuthToken();
// Exchange token for Graph API token via On-Behalf-Of flow
```

### Teams Toolkit

- VS Code extension for Teams app development
- Scaffold tab, bot, message extension, and copilot plugin projects
- Local debugging with Teams Toolkit DevTunnel integration
- Deploy to Azure (App Service, Azure Functions) with one click
- Provisioning via Bicep templates

---

## SharePoint Framework (SPFx)

**Purpose**: Custom web parts, extensions, and list form customizations in SharePoint Online. Uses TypeScript/React and runs in the SharePoint page context.

### Component Types

| Type | Description |
|---|---|
| **Web Part** | Custom UI component embedded in SharePoint pages; can use any JavaScript framework |
| **Application Customizer** | Add custom HTML/JS to SharePoint page header or footer |
| **Field Customizer** | Custom rendering for list column values |
| **Command Set** | Custom buttons in list/library toolbar or item context menu |
| **Form Customizer** | Replace default new/edit/view forms for a list |

### Development Tools

```bash
# Create SPFx solution
npx @microsoft/generator-sharepoint  # Yeoman generator for SPFx

# Build
gulp build

# Bundle for production
gulp bundle --ship

# Package
gulp package-solution --ship   # Creates .sppkg file for deployment

# Deploy to SharePoint App Catalog via CLI for Microsoft 365
m365 spo app add --filePath ./sharepoint/solution/my-solution.sppkg
m365 spo app deploy --name my-solution.sppkg
```

---

## Outlook Add-ins

**Purpose**: Extend Outlook (web, desktop, mobile) with custom task panes, compose integrations, and contextual cards.

### Types

| Type | Trigger | Use Case |
|---|---|---|
| **Mail read add-in** | Reading a message | Show CRM data for sender; create task from email |
| **Mail compose add-in** | Composing/replying | Insert templates; lookup product info |
| **Appointment add-in** | Creating/viewing calendar events | Meeting room booking; video conferencing integration |
| **Module extension** | Navigation pane item | Standalone module within Outlook |

### Technology

- **Office.js**: Office Add-in JavaScript API; provides access to email properties, compose actions
- **Task pane**: Side panel web app (any framework)
- **Manifest**: XML or JSON (Unified Manifest) describing add-in metadata, permissions, extension points
- **Outlook REST API (via Graph)**: Access mailbox data with proper Graph permissions
- **Sideloading**: Developer test via Outlook → Get Add-ins → My Add-ins → Upload custom manifest
