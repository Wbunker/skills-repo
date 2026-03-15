# Chrome Enterprise — CLI Reference

## Important Note

**Chrome Enterprise management is primarily configured through the Google Admin Console** (admin.google.com), not through `gcloud` CLI. The Admin Console provides a GUI for:
- Enrolling devices and browsers
- Setting organizational unit (OU) structure and policies
- Deploying apps and extensions
- Viewing device/browser inventory

For programmatic management, use the **Chrome Management API** and **Chrome Policy API** via REST. The `gcloud` CLI has limited coverage of Chrome Enterprise management.

---

## Enable Chrome Management APIs

```bash
# Enable Chrome Management API (for device/browser inventory queries)
gcloud services enable chromemanagement.googleapis.com --project=my-project

# Enable Chrome Policy API (for reading/setting policies programmatically)
gcloud services enable chromepolicy.googleapis.com --project=my-project

# Verify enabled
gcloud services list --enabled \
  --filter="name:(chromemanagement OR chromepolicy)" \
  --project=my-project
```

---

## Service Account for Chrome APIs

```bash
# Create service account for Chrome API access
gcloud iam service-accounts create chrome-api-sa \
  --display-name="Chrome Management API SA" \
  --project=my-project

# Create key for service account
gcloud iam service-accounts keys create chrome-api-key.json \
  --iam-account=chrome-api-sa@my-project.iam.gserviceaccount.com \
  --project=my-project

# Note: Chrome APIs require OAuth 2.0 scopes granted in the Google Admin Console
# Admin Console → Security → API Controls → Domain-Wide Delegation
# Add service account client ID with these scopes:
# https://www.googleapis.com/auth/chrome.management.reports.readonly
# https://www.googleapis.com/auth/chrome.management.telemetry.readonly
# https://www.googleapis.com/auth/chrome.management.policy
# https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly
```

---

## Chrome Management API — REST Examples

### List Managed Chrome Browsers (CBCM)

```bash
TOKEN=$(gcloud auth print-access-token)

# List enrolled browsers for the domain
curl -s -H "Authorization: Bearer ${TOKEN}" \
  "https://chromemanagement.googleapis.com/v1/customers/my_customer/browsers?pageSize=100" \
  | python3 -m json.tool

# List browsers with specific filter (Chrome version below threshold)
curl -s -H "Authorization: Bearer ${TOKEN}" \
  "https://chromemanagement.googleapis.com/v1/customers/my_customer/browsers?filter=lastActivityTime>=2025-01-01T00:00:00Z" \
  | python3 -m json.tool
```

### List ChromeOS Devices (Admin SDK Directory API)

```bash
# List all ChromeOS devices in the organization
curl -s -H "Authorization: Bearer ${TOKEN}" \
  "https://admin.googleapis.com/admin/directory/v1/customer/my_customer/devices/chromeos?maxResults=100&projection=FULL" \
  | python3 -m json.tool

# List devices in a specific Organizational Unit
curl -s -H "Authorization: Bearer ${TOKEN}" \
  "https://admin.googleapis.com/admin/directory/v1/customer/my_customer/devices/chromeos?maxResults=100&orgUnitPath=/Students/Grade9" \
  | python3 -m json.tool

# Get a specific ChromeOS device
DEVICE_ID="device-unique-id-here"
curl -s -H "Authorization: Bearer ${TOKEN}" \
  "https://admin.googleapis.com/admin/directory/v1/customer/my_customer/devices/chromeos/${DEVICE_ID}" \
  | python3 -m json.tool

# Deprovision a ChromeOS device
curl -s -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"deprovisionReason": "retiring_device"}' \
  "https://admin.googleapis.com/admin/directory/v1/customer/my_customer/devices/chromeos/${DEVICE_ID}/action"

# Move device to a different OU
curl -s -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"deviceIds": ["'${DEVICE_ID}'"], "orgUnitPath": "/IT/Kiosk"}' \
  "https://admin.googleapis.com/admin/directory/v1/customer/my_customer/devices/chromeos/moveDevicesToOu"
```

### Chrome Policy API — Read Policies

```bash
# Resolve (read) policies applied to a specific OU
curl -s -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "policyTargetKey": {
      "targetResource": "orgunits/03ph8a2z1234abc"
    },
    "policySchemaFilter": "chrome.users.*"
  }' \
  "https://chromepolicy.googleapis.com/v1/customers/my_customer/policies:resolve" \
  | python3 -m json.tool

# List available policy schemas
curl -s -H "Authorization: Bearer ${TOKEN}" \
  "https://chromepolicy.googleapis.com/v1/customers/my_customer/policySchemas?filter=chrome.users&pageSize=50" \
  | python3 -m json.tool | grep '"name"'
```

### Chrome Policy API — Modify Policies

```bash
# Set a policy: force-install an extension to an OU
# (Extension ID: cjpalhdlnbpafiamejdnhcphjbkeiagm = uBlock Origin)
curl -s -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "policyTargetKey": {
          "targetResource": "orgunits/03ph8a2z1234abc"
        },
        "policyValue": {
          "policySchema": "chrome.users.appsconfig.ChromeAppInstallType",
          "value": {
            "appInstallType": "FORCED",
            "appId": "cjpalhdlnbpafiamejdnhcphjbkeiagm"
          }
        },
        "updateMask": "appInstallType"
      }
    ]
  }' \
  "https://chromepolicy.googleapis.com/v1/customers/my_customer/policies/orgunits:batchModify"

# Disable developer tools for an OU
curl -s -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "policyTargetKey": {
          "targetResource": "orgunits/03ph8a2z1234abc"
        },
        "policyValue": {
          "policySchema": "chrome.users.DeveloperToolsAvailability",
          "value": {"developerToolsAvailability": "DEVELOPER_TOOLS_DISALLOWED"}
        },
        "updateMask": "developerToolsAvailability"
      }
    ]
  }' \
  "https://chromepolicy.googleapis.com/v1/customers/my_customer/policies/orgunits:batchModify"
```

---

## Automating Chrome Enterprise with Python

For production automation, use the Google API Python client library:

```bash
# Install required libraries
pip install google-auth google-auth-httplib2 google-api-python-client

# Example: list all ChromeOS devices with Python
python3 - << 'EOF'
from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly']
SERVICE_ACCOUNT_FILE = 'chrome-api-key.json'
ADMIN_USER = 'admin@example.com'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES).with_subject(ADMIN_USER)

service = build('admin', 'directory_v1', credentials=credentials)

results = service.chromeosdevices().list(
    customerId='my_customer',
    maxResults=100,
    projection='BASIC'
).execute()

devices = results.get('chromeosdevices', [])
for device in devices:
    print(f"{device.get('serialNumber', 'N/A')}: {device.get('status', 'N/A')} - {device.get('osVersion', 'N/A')}")

print(f"\nTotal devices: {len(devices)}")
EOF
```

---

## Google Cloud Identity / Workspace Admin — User and Group Management

While not exclusive to Chrome Enterprise, Admin SDK is commonly used alongside Chrome management for user lifecycle:

```bash
# Enable Admin SDK API
gcloud services enable admin.googleapis.com --project=my-project

# List users in domain (via Admin SDK REST, not gcloud)
# gcloud does not have direct admin directory commands
# Use:
TOKEN=$(gcloud auth application-default print-access-token)

# List all users (requires admin service account with DWD)
curl -s -H "Authorization: Bearer ${TOKEN}" \
  "https://admin.googleapis.com/admin/directory/v1/users?domain=example.com&maxResults=100&orderBy=email" \
  | python3 -m json.tool | grep '"primaryEmail"'

# Suspend a user (for offboarding)
curl -s -X PUT \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"suspended": true}' \
  "https://admin.googleapis.com/admin/directory/v1/users/leavinguser@example.com"
```

---

## Useful Chrome Enterprise Console Paths

These actions are only available in the Google Admin Console (admin.google.com):

| Task | Console Path |
|---|---|
| Enroll browsers (generate enrollment token) | Devices → Chrome → Managed Browsers → Add |
| Set OU policies | Devices → Chrome → Settings → [User/Device Settings] → Select OU |
| View device inventory | Devices → Chrome → Devices |
| View browser inventory | Devices → Chrome → Managed Browsers |
| Deploy apps/extensions | Devices → Chrome → Apps & Extensions → [OU] |
| Kiosk app configuration | Devices → Chrome → Apps & Extensions → Kiosks |
| Zero-touch enrollment | Devices → Chrome → Devices → Pre-provisioned devices |
| Chrome version dashboard | Devices → Chrome → Managed Browsers → Version details |
