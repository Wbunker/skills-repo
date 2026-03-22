# Azure App Registration

All Microsoft Graph API access requires an application registered in Microsoft Entra ID
(formerly Azure Active Directory). This document covers the complete setup process.

## Prerequisites

- A Microsoft 365 / Azure account
- **Cloud Application Administrator** role or higher in the Entra tenant
- Free Azure account works: https://azure.microsoft.com/pricing/purchase-options/azure-account

## Step-by-Step Registration

### 1. Navigate to App Registrations

1. Sign in to [Microsoft Entra admin center](https://entra.microsoft.com)
2. Go to **Identity** > **Applications** > **App registrations**
3. Click **New registration**

### 2. Configure the App

| Field | Value |
|-------|-------|
| **Name** | Your app name (e.g., `my-m365-automation`) |
| **Supported account types** | "Accounts in this organizational directory only" (single-tenant) for most scripts |
| **Redirect URI** | Leave blank for now (add after for delegated flows) |

Click **Register**.

### 3. Save These Values (from the Overview pane)

```
Application (client) ID:  xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Directory (tenant) ID:    xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Object ID:                xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

These are **not secret** — safe to store in config files (not client secrets).

### 4. Create a Client Secret (for App-Only / Daemon Access)

1. In the app registration, go to **Certificates & secrets**
2. Click **Client secrets** > **New client secret**
3. Add a description, choose expiry (max 24 months; 12 months recommended)
4. Click **Add**
5. **Copy the secret VALUE immediately** — it is never shown again

```
Client Secret Value:  abc~xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Client Secret ID:     xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  (less important)
```

**Alternatively, use a certificate** (more secure for production):
- Go to **Certificates & secrets** > **Certificates** > **Upload certificate**
- Upload a `.cer`, `.pem`, or `.crt` file

### 5. Configure API Permissions

This is where you define what data the app can access.

1. Go to **API permissions** > **Add a permission**
2. Select **Microsoft Graph**
3. Choose permission type:
   - **Delegated permissions**: App acts on behalf of a signed-in user
   - **Application permissions**: App acts with its own identity (no user)
4. Search for and add the permissions you need (see table below)
5. Click **Add permissions**

For **application permissions**, an admin must **Grant admin consent**:
- Click "Grant admin consent for [Your Tenant]" after adding permissions
- This is a one-time step per permission set

### 6. Configure Redirect URI (for Delegated Flows Only)

For device code flow (CLI/script use): No redirect URI needed.

For authorization code flow (web app):
1. Go to **Authentication** > **Add a platform** > **Web**
2. Enter redirect URI (e.g., `http://localhost:8080/callback`)
3. Under **Advanced settings**, enable **Allow public client flows** if using device code flow from a desktop/script

## Permission Reference

### Mail Permissions

| Permission | Type | What it allows |
|------------|------|----------------|
| `Mail.Read` | Delegated | Read user's mail |
| `Mail.ReadWrite` | Delegated | Read and write user's mail |
| `Mail.Send` | Delegated | Send mail as user |
| `Mail.Read.Shared` | Delegated | Read shared mailboxes |
| `Mail.Read` (same name) | Application | Read all users' mail (tenant-wide) |
| `Mail.ReadWrite.All` | Application | Read/write all users' mail |
| `Mail.Send.All` | Application | Send as any user |

### Calendar Permissions

| Permission | Type | What it allows |
|------------|------|----------------|
| `Calendars.Read` | Delegated/Application | Read calendars |
| `Calendars.ReadWrite` | Delegated/Application | Read and write calendars |
| `Calendars.ReadBasic` | Delegated | Read free/busy only |
| `Calendars.ReadBasic.All` | Application | Read free/busy for all users |

### Files / OneDrive Permissions

| Permission | Type | What it allows |
|------------|------|----------------|
| `Files.Read` | Delegated | Read user's files |
| `Files.ReadWrite` | Delegated | Read/write user's own files |
| `Files.Read.All` | Delegated | Read all files user can access |
| `Files.ReadWrite.All` | Delegated/Application | Read/write all files |

### Teams / Chat Permissions

| Permission | Type | What it allows |
|------------|------|----------------|
| `Chat.Read` | Delegated | Read user's chats |
| `Chat.ReadWrite` | Delegated | Read/write user's chats |
| `Chat.Read.All` | Application | Read all chats in tenant |
| `Chat.ReadWrite.All` | Application | Read/write all chats |
| `ChannelMessage.Read.All` | Delegated/Application | Read channel messages |
| `ChannelMessage.Send` | Delegated | Send to channels |

### Contacts Permissions

| Permission | Type | What it allows |
|------------|------|----------------|
| `Contacts.Read` | Delegated/Application | Read contacts |
| `Contacts.ReadWrite` | Delegated/Application | Read/write contacts |

### User / Profile Permissions

| Permission | Type | What it allows |
|------------|------|----------------|
| `User.Read` | Delegated | Read signed-in user's profile |
| `User.Read.All` | Application | Read all users' profiles |
| `User.ReadWrite` | Delegated | Read/write signed-in user's profile |

## Environment Variables Pattern

Store credentials in environment variables, never in code:

```bash
# .env file (add to .gitignore)
AZURE_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_CLIENT_SECRET=abc~xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

```python
import os
from dotenv import load_dotenv

load_dotenv()

TENANT_ID     = os.environ["AZURE_TENANT_ID"]
CLIENT_ID     = os.environ["AZURE_CLIENT_ID"]
CLIENT_SECRET = os.environ["AZURE_CLIENT_SECRET"]
```

## Key Concepts

- **Single-tenant vs Multi-tenant**: Use "this organizational directory only" for scripts
  used within a single company. Multi-tenant allows any M365 org to use your app.
- **Client secret lifetime**: Max 24 months. Set a calendar reminder to rotate before expiry.
- **Certificate vs Secret**: Certificates are more secure and preferred for production.
  Scripts can use client secrets for ease of development.
- **Admin consent**: Application permissions (app-only) ALWAYS require admin consent.
  Delegated permissions may or may not require admin consent depending on the permission.
- **Principle of least privilege**: Request only the permissions your app actually needs.
