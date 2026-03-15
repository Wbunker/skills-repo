# Google Workspace & AppSheet — CLI Reference

## Service Account Setup for Workspace APIs

```bash
# Create a service account for Workspace API access
gcloud iam service-accounts create workspace-api-sa \
  --display-name="Workspace API Service Account" \
  --project=my-project

# Create and download a key (for server-side use)
gcloud iam service-accounts keys create workspace-sa-key.json \
  --iam-account=workspace-api-sa@my-project.iam.gserviceaccount.com \
  --project=my-project

# Enable required Workspace APIs
gcloud services enable gmail.googleapis.com \
  drive.googleapis.com \
  calendar-json.googleapis.com \
  docs.googleapis.com \
  sheets.googleapis.com \
  admin.googleapis.com \
  chat.googleapis.com \
  --project=my-project

# Check which services are enabled
gcloud services list --enabled \
  --filter="name:(gmail OR drive OR calendar OR docs OR sheets OR admin OR chat)" \
  --project=my-project
```

---

## Google Workspace API — curl Examples

### Gmail API

```bash
# Set token variable (obtain via OAuth 2.0 or service account impersonation)
TOKEN=$(gcloud auth print-access-token)

# List recent Gmail messages for a user (with domain-wide delegation)
curl -s -H "Authorization: Bearer ${TOKEN}" \
  "https://gmail.googleapis.com/gmail/v1/users/user@example.com/messages?maxResults=10&labelIds=INBOX" \
  | python3 -m json.tool

# Get a specific message
curl -s -H "Authorization: Bearer ${TOKEN}" \
  "https://gmail.googleapis.com/gmail/v1/users/user@example.com/messages/MESSAGE_ID?format=full" \
  | python3 -m json.tool

# Send an email (base64url encoded raw RFC 2822 message)
RAW_MESSAGE=$(printf "To: recipient@example.com\r\nSubject: Test\r\nContent-Type: text/plain\r\n\r\nHello from API" | base64 -w 0 | tr '+/' '-_')

curl -s -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"raw\": \"${RAW_MESSAGE}\"}" \
  "https://gmail.googleapis.com/gmail/v1/users/user@example.com/messages/send"
```

### Drive API

```bash
# List files in Drive
curl -s -H "Authorization: Bearer ${TOKEN}" \
  "https://www.googleapis.com/drive/v3/files?pageSize=20&fields=files(id,name,mimeType,modifiedTime)" \
  | python3 -m json.tool

# List files in a specific folder
FOLDER_ID="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs"
curl -s -H "Authorization: Bearer ${TOKEN}" \
  "https://www.googleapis.com/drive/v3/files?q='${FOLDER_ID}'+in+parents&fields=files(id,name,mimeType)" \
  | python3 -m json.tool

# Export a Google Doc to PDF
DOC_ID="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs"
curl -s -H "Authorization: Bearer ${TOKEN}" \
  "https://www.googleapis.com/drive/v3/files/${DOC_ID}/export?mimeType=application/pdf" \
  -o output.pdf

# Create a folder
curl -s -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Folder", "mimeType": "application/vnd.google-apps.folder"}' \
  "https://www.googleapis.com/drive/v3/files"
```

### Sheets API

```bash
# Get spreadsheet values from a range
SPREADSHEET_ID="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs"
RANGE="Sheet1!A1:D10"

curl -s -H "Authorization: Bearer ${TOKEN}" \
  "https://sheets.googleapis.com/v4/spreadsheets/${SPREADSHEET_ID}/values/${RANGE}" \
  | python3 -m json.tool

# Update values in a spreadsheet
curl -s -X PUT \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "range": "Sheet1!A1:B2",
    "majorDimension": "ROWS",
    "values": [["Name", "Value"], ["Alice", "42"]]
  }' \
  "https://sheets.googleapis.com/v4/spreadsheets/${SPREADSHEET_ID}/values/Sheet1!A1:B2?valueInputOption=USER_ENTERED"

# Append rows to a spreadsheet
curl -s -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "values": [["2025-01-15", "New row data", "100"]]
  }' \
  "https://sheets.googleapis.com/v4/spreadsheets/${SPREADSHEET_ID}/values/Sheet1!A:C:append?valueInputOption=USER_ENTERED"
```

### Admin SDK — Directory API

```bash
# List users in domain
curl -s -H "Authorization: Bearer ${TOKEN}" \
  "https://admin.googleapis.com/admin/directory/v1/users?domain=example.com&maxResults=100&orderBy=email" \
  | python3 -m json.tool

# Get a specific user
curl -s -H "Authorization: Bearer ${TOKEN}" \
  "https://admin.googleapis.com/admin/directory/v1/users/user@example.com" \
  | python3 -m json.tool

# List groups
curl -s -H "Authorization: Bearer ${TOKEN}" \
  "https://admin.googleapis.com/admin/directory/v1/groups?domain=example.com&maxResults=100" \
  | python3 -m json.tool

# List members of a group
GROUP_EMAIL="engineering@example.com"
curl -s -H "Authorization: Bearer ${TOKEN}" \
  "https://admin.googleapis.com/admin/directory/v1/groups/${GROUP_EMAIL}/members" \
  | python3 -m json.tool

# List Admin Audit Log (login events)
curl -s -H "Authorization: Bearer ${TOKEN}" \
  "https://admin.googleapis.com/admin/reports/v1/activity/users/all/applications/login?maxResults=50" \
  | python3 -m json.tool
```

---

## Domain-Wide Delegation Setup

```bash
# Step 1: Create service account
gcloud iam service-accounts create workspace-dwd-sa \
  --display-name="Workspace DWD SA" \
  --project=my-project

# Step 2: Enable domain-wide delegation on service account
# (must be done in Cloud Console: IAM > Service Accounts > Edit > Enable DWD)
# Or via API:
PROJECT_NUMBER=$(gcloud projects describe my-project --format='value(projectNumber)')
SA_EMAIL="workspace-dwd-sa@my-project.iam.gserviceaccount.com"

# Step 3: Get the client ID (numeric) for Admin Console entry
gcloud iam service-accounts describe ${SA_EMAIL} \
  --format="value(oauth2ClientId)" \
  --project=my-project

# Step 4: Add to Admin Console manually:
# admin.google.com → Security → API Controls → Manage Domain-Wide Delegation
# Add: Client ID (from step 3) + OAuth Scopes:
# https://www.googleapis.com/auth/gmail.readonly
# https://www.googleapis.com/auth/drive
# https://www.googleapis.com/auth/admin.directory.user.readonly

# Step 5: Create key file
gcloud iam service-accounts keys create dwd-key.json \
  --iam-account=${SA_EMAIL} \
  --project=my-project

echo "Key created. Use with google-auth library for DWD impersonation."
echo "Python example:"
echo "from google.oauth2 import service_account"
echo "credentials = service_account.Credentials.from_service_account_file('dwd-key.json', scopes=SCOPES).with_subject('user@example.com')"
```

---

## Apps Script with clasp CLI

```bash
# Install clasp (Command Line Apps Script)
npm install -g @google/clasp

# Login to clasp
clasp login

# Clone an existing Apps Script project
clasp clone SCRIPT_ID

# Create a new Apps Script project (standalone)
clasp create --type standalone --title "My Automation"

# Create a new Apps Script project bound to a Sheets document
clasp create --type sheets --title "Sheet Automation" --parentId SPREADSHEET_ID

# Push local changes to Apps Script
clasp push

# Pull latest from Apps Script
clasp pull

# Deploy as web app
clasp deploy --description "v1.0 deploy"

# List deployments
clasp deployments

# Open project in browser
clasp open

# Run a function
clasp run myFunction

# View logs
clasp logs --watch
```

---

## App Engine Deploy (for Apps Script Web Apps as GAE)

For web apps built with Apps Script that need to be deployed as Google App Engine services:

```bash
# Apps Script web apps are hosted by Google directly (not GAE)
# For custom backend services that integrate with Workspace, deploy to App Engine:

# Initialize App Engine app
gcloud app create --region=us-central --project=my-project

# Deploy an App Engine service (e.g., a Workspace integration backend)
# Assumes app.yaml exists in current directory
gcloud app deploy app.yaml \
  --project=my-project \
  --quiet

# View App Engine service
gcloud app services list --project=my-project

# View logs
gcloud app logs tail -s default --project=my-project

# Browse deployed app
gcloud app browse --project=my-project
```
