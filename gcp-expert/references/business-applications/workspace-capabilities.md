# Google Workspace & AppSheet — Capabilities

## Google Workspace APIs

Google Workspace APIs enable programmatic access to Gmail, Drive, Calendar, Docs, Sheets, and other Workspace services from server-side or client-side applications.

### Authentication

| Method | Use Case |
|---|---|
| OAuth 2.0 (user credentials) | Access data on behalf of a specific user; user grants consent |
| Service account (application credentials) | Server-to-server; no user consent flow |
| Domain-wide delegation | Service account impersonates any user in the domain; requires Workspace admin approval |
| API keys | Only for public data (Maps, YouTube public data); NOT for Workspace user data |

**Domain-wide delegation setup:**
1. Create a service account in GCP project
2. Enable domain-wide delegation on the service account
3. In Google Admin Console (admin.google.com) → Security → API Controls → Domain-wide Delegation
4. Add the service account client ID + required OAuth scopes
5. Service account can then impersonate any user in the domain

### Core APIs

**Gmail API:**
- `users.messages.list/get/send/modify/delete`
- `users.threads.list/get/modify`
- `users.labels.list/create/update/delete`
- `users.drafts.create/send`
- Batch operations supported
- Push notifications via Pub/Sub (`users.watch`)

**Drive API:**
- `files.list/get/create/update/delete/copy`
- `files.export` (convert Docs/Sheets to PDF, CSV, etc.)
- `permissions.create/delete` (file sharing)
- `drives.list/get` (Shared Drives)
- Real-time change notifications via webhook channels (`changes.watch`)
- `files.list` with `spaces=drive` or `spaces=appDataFolder`

**Calendar API:**
- `events.list/get/insert/update/delete/import`
- `calendars.list/get/insert`
- `calendarList` (user's subscribed calendars)
- `freebusy.query` (check availability across multiple calendars)
- Event notifications via push channels

**Docs API:**
- `documents.get/create/batchUpdate`
- `batchUpdate`: insert text, replace text, format paragraphs, insert images, create tables
- Read-only access or full document modification
- Suitable for templated document generation

**Sheets API:**
- `spreadsheets.get/create/batchUpdate`
- `spreadsheets.values.get/update/append/batchGet/batchUpdate`
- `spreadsheets.values.clear`
- Row/column insertion, deletion, cell formatting via batchUpdate
- Suitable for read/write to spreadsheet data stores

**Admin SDK:**
- **Directory API**: manage users, groups, OUs, devices
  - `users.list/get/insert/update/delete`
  - `groups.list/get/insert/members.list/insert/delete`
  - `orgUnits.list/get/insert`
- **Reports API**: audit and usage reports
  - `activities.list` (login, admin, Drive activity logs)
  - `usageReports.get` (per-user and domain-level usage)
- **Groups Settings API**: manage group settings (who can join, post, view)
- **Reseller API**: for resellers managing customer accounts

**Chat API:**
- Create and manage Chat spaces programmatically
- Send messages, create cards (rich message format)
- Bots/apps respond to messages via webhook or Cloud Functions
- `spaces.messages.create` for sending messages

---

## Google Workspace Events API

Subscribe to real-time events from Google Workspace via **Pub/Sub**:

**Supported event types:**
- New Gmail messages, thread updates
- Google Calendar event changes
- Drive file/folder changes
- Chat new messages, memberships

**How it works:**
1. Create a subscription via the Workspace Events API (not Pub/Sub directly)
2. Specify a Pub/Sub topic as the delivery endpoint
3. Events are published as Pub/Sub messages
4. Process with Cloud Functions or Dataflow

**Key use cases:**
- Trigger workflows on new email (e.g., support ticket creation from Gmail)
- Sync calendar events to external systems
- Audit Drive activity in real time

---

## AppSheet

**AppSheet** is Google's no-code application development platform, acquired by Google in 2020 and integrated into Google Workspace.

### Data Sources

Connect AppSheet apps to:
- Google Sheets (most common; no additional setup)
- Google Drive (files/folders)
- Cloud SQL (MySQL/PostgreSQL via AppSheet connector)
- AlloyDB
- Salesforce
- Box, Dropbox
- Smartsheet

### App Features

- **Views**: forms, tables, detail views, galleries, maps, charts, calendars
- **Actions**: row add/update/delete, navigation, external URL, email/SMS trigger
- **Workflows (legacy)**: send email, SMS, push notification, update a table row
- **AppSheet Automation**: visual workflow builder (replacement for legacy Workflows)
  - Event triggers: record add/update/delete, form submit, scheduled time
  - Process steps: create/update records, send email, call webhook, run bot
  - Integration with Google Chat, Gmail, Cloud Tasks, Pub/Sub via webhooks
- **Security filters**: row-level access control based on user email or role
- **Sync**: offline-first; works without connectivity; syncs when back online
- **Deploy**: mobile app (iOS/Android PWA or standalone app), web app

### AppSheet Automation

Automation is AppSheet's built-in process automation (replaces Google Apps Script for data-centric workflows):
- **Bots**: contain events (triggers) and processes (actions)
- **Processes**: sequences of steps that can branch based on conditions
- **Steps**: send notification, data change, call webhook, run a task, create event
- **Webhooks**: call external REST APIs (Pub/Sub push endpoint, Zapier, Make, etc.)
- **Rate limits**: automation runs are metered; Enterprise plan for high volume

### AppSheet vs Apps Script vs Workflows

| Feature | AppSheet | Apps Script | Google Cloud Workflows |
|---|---|---|---|
| Audience | Citizen developers | Developers with JS knowledge | Cloud developers |
| Purpose | Build full apps | Automate Workspace | Orchestrate GCP services |
| Workspace integration | Deep (native data sources) | Native (all Workspace APIs) | Via HTTP steps |
| Custom code | Limited (expressions only) | Full JavaScript | Limited YAML expressions |
| Mobile | Yes (built-in mobile app) | Web only | Not applicable |

---

## Google Apps Script

**Apps Script** is a JavaScript runtime for automating Google Workspace and building lightweight web apps.

### Key capabilities

- **Script editor**: web-based IDE at script.google.com
- **Services**: `SpreadsheetApp`, `GmailApp`, `DriveApp`, `CalendarApp`, `DocumentApp`, `SitesApp`, `UrlFetchApp`, `PropertiesService`, `ScriptApp`
- **Triggers**:
  - Simple triggers: `onOpen()`, `onEdit()`, `onFormSubmit()` — run in the context of the user
  - Installable triggers: time-based (every minute to monthly), event-based (calendar, form, spreadsheet change) — run as the script owner
- **Deployment**:
  - Web app: expose script as HTTP endpoint; handle `doGet()` / `doPost()`
  - Google Workspace Add-on: extend Gmail, Docs, Sheets, Calendar with a sidebar/card UI
  - Sheets/Docs/Forms add-on (published to Workspace Marketplace)
- **Quotas**: daily execution limits (6 min/execution, 1800 executions/day for consumer accounts; higher for Workspace)
- **clasp CLI**: push/pull Apps Script projects from local development environment
