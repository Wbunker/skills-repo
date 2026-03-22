# Azure Communication Services — CLI Reference
For service concepts, see [communication-capabilities.md](communication-capabilities.md).

## Azure Communication Services

```bash
# Install ACS extension
az extension add --name communication

# --- ACS Resource ---
az communication create \
  --resource-group myRG \
  --name myACSResource \
  --location global \
  --data-location unitedstates              # Create ACS resource (data-location for data residency)

az communication list --resource-group myRG  # List ACS resources
az communication show \
  --resource-group myRG \
  --name myACSResource                       # Show ACS resource details

az communication delete \
  --resource-group myRG \
  --name myACSResource --yes                 # Delete ACS resource

# --- Connection Strings ---
az communication list-key \
  --resource-group myRG \
  --name myACSResource                       # Show primary and secondary connection strings

az communication regenerate-key \
  --resource-group myRG \
  --name myACSResource \
  --key-type Primary                         # Regenerate primary key

# --- Identity Management ---
az communication identity user create \
  --connection-string "endpoint=https://...;accessKey=..."  # Create ACS communication user

az communication identity token issue \
  --connection-string "endpoint=https://...;accessKey=..." \
  --user "8:acs:..." \
  --scope voip chat                          # Issue access token for voip and chat

az communication identity token revoke \
  --connection-string "endpoint=https://...;accessKey=..." \
  --user "8:acs:..."                         # Revoke all tokens for a user

az communication identity user delete \
  --connection-string "endpoint=https://...;accessKey=..." \
  --user "8:acs:..."                         # Delete ACS user

# --- Phone Numbers ---
az communication phonenumber list \
  --connection-string "endpoint=https://...;accessKey=..."  # List purchased phone numbers

az communication phonenumber show \
  --connection-string "endpoint=https://...;accessKey=..." \
  --phonenumber "+15551234567"               # Show details for a number

# --- Send SMS (via ACS SDK; no direct az CLI) ---
# Use REST API or SDK; az communication provides resource management only
```

## Azure Communication Email

```bash
# Install email extension
az extension add --name communication

# --- Email Communication Resource ---
az communication email-domain create \
  --resource-group myRG \
  --name myEmailDomain \
  --email-service-name myEmailService \
  --location global \
  --domain-management AzureManaged          # Create Azure-managed domain (*.azurecomm.net)

az communication email-domain create \
  --resource-group myRG \
  --name mycompany.com \
  --email-service-name myEmailService \
  --location global \
  --domain-management CustomerManaged       # Use custom domain (requires DNS verification)

az communication email-domain list \
  --resource-group myRG \
  --email-service-name myEmailService        # List email domains

az communication email-domain show \
  --resource-group myRG \
  --name myEmailDomain \
  --email-service-name myEmailService        # Show domain + DNS verification status

az communication email-domain initiate-verification \
  --resource-group myRG \
  --name mycompany.com \
  --email-service-name myEmailService \
  --verification-type DKIM                   # Initiate DKIM verification for custom domain

az communication email-domain cancel-verification \
  --resource-group myRG \
  --name mycompany.com \
  --email-service-name myEmailService \
  --verification-type DKIM                   # Cancel pending verification

# --- Send Email (CLI) ---
az communication email send \
  --connection-string "endpoint=https://...;accessKey=..." \
  --sender "no-reply@mycompany.azurecomm.net" \
  --to "user@example.com" \
  --subject "Test email from CLI" \
  --text "Hello from Azure CLI" \
  --html "<h1>Hello from Azure CLI</h1>"    # Send a test email

# --- Email Service Resource ---
az communication email list --resource-group myRG  # List email services
```

## Notification Hubs

```bash
# --- Namespace Management ---
az notification-hub namespace create \
  --resource-group myRG \
  --name myNotifNamespace \
  --location eastus \
  --sku Standard                             # Create Standard namespace (for production)

az notification-hub namespace create \
  --resource-group myRG \
  --name myNotifDevNamespace \
  --location eastus \
  --sku Free                                 # Create Free namespace (for dev/test)

az notification-hub namespace list \
  --resource-group myRG                      # List all namespaces

az notification-hub namespace show \
  --resource-group myRG \
  --namespace-name myNotifNamespace          # Show namespace details

az notification-hub namespace check-availability \
  --name proposedNamespaceName               # Check if namespace name is available

az notification-hub namespace delete \
  --resource-group myRG \
  --name myNotifNamespace --yes              # Delete namespace (also deletes all hubs)

# --- Hub Management ---
az notification-hub create \
  --resource-group myRG \
  --namespace-name myNotifNamespace \
  --name myIoSAndroidHub \
  --location eastus                          # Create notification hub

az notification-hub list \
  --resource-group myRG \
  --namespace-name myNotifNamespace          # List hubs

az notification-hub show \
  --resource-group myRG \
  --namespace-name myNotifNamespace \
  --name myIoSAndroidHub                     # Show hub details

az notification-hub delete \
  --resource-group myRG \
  --namespace-name myNotifNamespace \
  --name myIoSAndroidHub --yes               # Delete hub

# --- Platform Credentials (PNS configuration) ---
# FCM v1 credentials (new Firebase Cloud Messaging v1)
az notification-hub credential gcm update \
  --resource-group myRG \
  --namespace-name myNotifNamespace \
  --notification-hub-name myIoSAndroidHub \
  --google-api-key "AAAA...:APA91bH..."     # Legacy FCM server key (use FCM v1 for new projects)

# APNs credentials (iOS)
az notification-hub credential apns update \
  --resource-group myRG \
  --namespace-name myNotifNamespace \
  --notification-hub-name myIoSAndroidHub \
  --apns-certificate ./AuthKey_ABC123.p8 \
  --certificate-key "P8_KEY_ID" \
  --app-id "com.mycompany.myapp" \
  --app-name "My iOS App" \
  --endpoint "https://api.push.apple.com"    # Production APNs (use api.sandbox.push.apple.com for dev)

# WNS credentials (Windows)
az notification-hub credential wns update \
  --resource-group myRG \
  --namespace-name myNotifNamespace \
  --notification-hub-name myIoSAndroidHub \
  --package-sid "ms-app://..." \
  --secret-key "WNS_CLIENT_SECRET"           # Windows Notification Service credentials

# List all configured credentials
az notification-hub credential list \
  --resource-group myRG \
  --namespace-name myNotifNamespace \
  --notification-hub-name myIoSAndroidHub

# --- Authorization Rules ---
az notification-hub authorization-rule create \
  --resource-group myRG \
  --namespace-name myNotifNamespace \
  --notification-hub-name myIoSAndroidHub \
  --name app-backend-rule \
  --rights Listen Send                       # Backend has both Listen and Send rights

az notification-hub authorization-rule create \
  --resource-group myRG \
  --namespace-name myNotifNamespace \
  --notification-hub-name myIoSAndroidHub \
  --name device-register-rule \
  --rights Listen                            # Device registration: Listen only

az notification-hub authorization-rule list \
  --resource-group myRG \
  --namespace-name myNotifNamespace \
  --notification-hub-name myIoSAndroidHub    # List authorization rules

az notification-hub authorization-rule list-keys \
  --resource-group myRG \
  --namespace-name myNotifNamespace \
  --notification-hub-name myIoSAndroidHub \
  --name app-backend-rule                    # Get connection strings for rule

az notification-hub authorization-rule regenerate-keys \
  --resource-group myRG \
  --namespace-name myNotifNamespace \
  --notification-hub-name myIoSAndroidHub \
  --name app-backend-rule \
  --policy-key PrimaryKey                    # Regenerate primary key for rule

# --- Test Sends ---
az notification-hub test-send \
  --resource-group myRG \
  --namespace-name myNotifNamespace \
  --notification-hub-name myIoSAndroidHub \
  --notification-format gcm \
  --message '{"data": {"message": "Test notification"}}'  # Send test push (GCM/FCM format)

az notification-hub test-send \
  --resource-group myRG \
  --namespace-name myNotifNamespace \
  --notification-hub-name myIoSAndroidHub \
  --notification-format apple \
  --message '{"aps": {"alert": "Test push", "sound": "default"}}'  # Test APNs send
```
