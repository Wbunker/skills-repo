# Mobile & Notification — CLI Reference
For service concepts, see [mobile-capabilities.md](mobile-capabilities.md).

## Azure Notification Hubs

```bash
# --- Namespace Management ---
az notification-hub namespace create \
  --resource-group myRG \
  --name myMobileAppNS \
  --location eastus \
  --sku Standard                               # Create Standard namespace (production)

az notification-hub namespace create \
  --resource-group myRG \
  --name myDevNS \
  --location eastus \
  --sku Free                                   # Free namespace for dev/test

az notification-hub namespace list \
  --resource-group myRG --output table         # List all namespaces

az notification-hub namespace show \
  --resource-group myRG \
  --namespace-name myMobileAppNS              # Show namespace details

az notification-hub namespace check-availability \
  --name myProposedNamespace                   # Check if name is available

az notification-hub namespace delete \
  --resource-group myRG \
  --name myMobileAppNS --yes                  # Delete namespace and all hubs

# --- Hub Management ---
az notification-hub create \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --name myiOSAndroidHub \
  --location eastus                            # Create notification hub

az notification-hub list \
  --resource-group myRG \
  --namespace-name myMobileAppNS              # List hubs in namespace

az notification-hub show \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --name myiOSAndroidHub                       # Show hub configuration

az notification-hub delete \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --name myiOSAndroidHub --yes                 # Delete hub
```

## Platform Credentials Configuration

```bash
# --- FCM v1 Credentials (Google Firebase Cloud Messaging v1) ---
# FCM v1 uses OAuth 2.0 service account (not legacy server key)
az notification-hub credential gcm update \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --notification-hub-name myiOSAndroidHub \
  --google-api-key "your-legacy-fcm-server-key"  # Legacy FCM (not recommended for new)

# For FCM v1, use portal (REST API; CLI support limited)

# --- APNs Credentials (Apple Push Notification service) ---
# Token-based auth (preferred — no expiry)
az notification-hub credential apns update \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --notification-hub-name myiOSAndroidHub \
  --apns-certificate ./AuthKey_ABCDEF1234.p8 \
  --certificate-key "ABCDEF1234" \
  --app-id "com.mycompany.myapp" \
  --app-name "My Mobile App" \
  --endpoint "https://api.push.apple.com"      # Production APNs

az notification-hub credential apns update \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --notification-hub-name myiOSAndroidHub \
  --apns-certificate ./AuthKey_ABCDEF1234.p8 \
  --certificate-key "ABCDEF1234" \
  --app-id "com.mycompany.myapp" \
  --app-name "My Mobile App" \
  --endpoint "https://api.sandbox.push.apple.com"  # Sandbox (development)

# Certificate-based auth (legacy .p12)
az notification-hub credential apns update \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --notification-hub-name myiOSAndroidHub \
  --apns-certificate ./PushCert.p12 \
  --certificate-key "p12-password" \
  --endpoint "https://api.push.apple.com"

# --- WNS Credentials (Windows Notification Service) ---
az notification-hub credential wns update \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --notification-hub-name myiOSAndroidHub \
  --package-sid "ms-app://s-1-15-2-..." \
  --secret-key "WNS_CLIENT_SECRET_FROM_AZURE_PORTAL"  # WNS credentials

# --- ADM Credentials (Amazon Device Messaging / Kindle) ---
az notification-hub credential adm update \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --notification-hub-name myiOSAndroidHub \
  --client-id "adm-client-id" \
  --client-secret "adm-client-secret"          # Kindle/ADM credentials

# --- List All Credentials ---
az notification-hub credential list \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --notification-hub-name myiOSAndroidHub      # Show all configured PNS credentials
```

## Authorization Rules and Connection Strings

```bash
# --- Authorization Rules ---
# Backend service: Listen (receive feedback) + Send (push notifications)
az notification-hub authorization-rule create \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --notification-hub-name myiOSAndroidHub \
  --name backend-send-rule \
  --rights Listen Send

# Mobile app (device registration): Listen only
az notification-hub authorization-rule create \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --notification-hub-name myiOSAndroidHub \
  --name device-register-rule \
  --rights Listen

# Management (full access): Listen + Send + Manage
az notification-hub authorization-rule create \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --notification-hub-name myiOSAndroidHub \
  --name admin-rule \
  --rights Listen Send Manage

# List authorization rules
az notification-hub authorization-rule list \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --notification-hub-name myiOSAndroidHub

# Get connection strings for a rule
az notification-hub authorization-rule list-keys \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --notification-hub-name myiOSAndroidHub \
  --name backend-send-rule                     # Returns primary and secondary connection strings

# Rotate keys
az notification-hub authorization-rule regenerate-keys \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --notification-hub-name myiOSAndroidHub \
  --name backend-send-rule \
  --policy-key PrimaryKey                      # Rotate primary key (use SecondaryKey for secondary)

# Delete an authorization rule
az notification-hub authorization-rule delete \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --notification-hub-name myiOSAndroidHub \
  --name old-rule
```

## Test Sends

```bash
# --- Test Push Notifications ---
# Test FCM (Android)
az notification-hub test-send \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --notification-hub-name myiOSAndroidHub \
  --notification-format gcm \
  --message '{"data": {"title": "Test", "body": "Hello from CLI"}}' \
  --tag-expression "topic:test"                # Send to test tag

# Test APNs (iOS)
az notification-hub test-send \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --notification-hub-name myiOSAndroidHub \
  --notification-format apple \
  --message '{"aps": {"alert": {"title": "Test", "body": "Hello!"}, "sound": "default"}}'

# Test WNS (Windows)
az notification-hub test-send \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --notification-hub-name myiOSAndroidHub \
  --notification-format windows \
  --message '<toast><visual><binding template="ToastText01"><text id="1">Hello from CLI</text></binding></visual></toast>'

# Broadcast test (all platforms)
az notification-hub test-send \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --notification-hub-name myiOSAndroidHub \
  --notification-format template \
  --message '{"message": "Broadcast test notification"}' \
  --tag-expression ""                          # Empty tag expression = all devices
```

## Namespace-level Authorization

```bash
# --- Namespace Authorization Rules ---
az notification-hub namespace authorization-rule create \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --name RootManageSharedAccessKey \
  --rights Listen Send Manage                  # Manage namespace-level access

az notification-hub namespace authorization-rule list \
  --resource-group myRG \
  --namespace-name myMobileAppNS

az notification-hub namespace authorization-rule list-keys \
  --resource-group myRG \
  --namespace-name myMobileAppNS \
  --name RootManageSharedAccessKey             # Get namespace-level connection string
```
