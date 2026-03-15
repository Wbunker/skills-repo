# AWS End User Computing — CLI Reference

For service concepts, see [workspaces-capabilities.md](workspaces-capabilities.md).

---

## WorkSpaces Personal — Directories

```bash
# --- Register a directory with WorkSpaces ---
aws workspaces register-workspace-directory \
  --directory-id d-1234567890 \
  --subnet-ids subnet-0abc123def456789 subnet-0def456abc123789 \
  --enable-work-docs false \
  --enable-self-service false

# --- Describe registered directories ---
aws workspaces describe-workspace-directories
aws workspaces describe-workspace-directories --directory-ids d-1234567890

# --- Deregister a directory ---
aws workspaces deregister-workspace-directory \
  --directory-id d-1234567890
```

## WorkSpaces Personal — Bundles

```bash
# --- List available bundles (AWS-provided and custom) ---
aws workspaces describe-workspace-bundles
aws workspaces describe-workspace-bundles --owner AMAZON

# --- List your custom bundles ---
aws workspaces describe-workspace-bundles --owner Self

# --- Create a custom bundle from an image ---
aws workspaces create-workspace-bundle \
  --bundle-name "MyCorpStandardBundle" \
  --bundle-description "Standard office bundle with Office 365 and Zoom" \
  --image-id wsi-abc123def456 \
  --compute-type Name=STANDARD \
  --user-storage UserVolumeSizeGib=100 \
  --root-storage RootVolumeSizeGib=80

# --- Update a custom bundle's image ---
aws workspaces update-workspace-bundle \
  --bundle-id wsb-abc123def456 \
  --image-id wsi-newimage123456

# --- Delete a custom bundle ---
aws workspaces delete-workspace-bundle \
  --bundle-id wsb-abc123def456
```

## WorkSpaces Personal — Workspace Images

```bash
# --- Describe workspace images ---
aws workspaces describe-workspace-images
aws workspaces describe-workspace-images --image-ids wsi-abc123def456
aws workspaces describe-workspace-images --image-type OWNED

# --- Create an image from a running WorkSpace ---
aws workspaces create-workspace-image \
  --name "Corp-Standard-2024-Q4" \
  --description "Q4 2024 standard image with patched OS and Office 365" \
  --workspace-id ws-abc123def456 \
  --tags Key=Team,Value=IT Key=Quarter,Value=Q4-2024

# --- Share an image with another account ---
aws workspaces update-workspace-image-permission \
  --image-id wsi-abc123def456 \
  --allow-copy-image true \
  --shared-account-id 123456789012

# --- Delete a workspace image ---
aws workspaces delete-workspace-image \
  --image-id wsi-abc123def456
```

## WorkSpaces Personal — Create and Manage WorkSpaces

```bash
# --- Create WorkSpaces ---
# Create a single WorkSpace (Windows, Standard bundle, AutoStop hourly)
aws workspaces create-workspaces \
  --workspaces '[
    {
      "DirectoryId": "d-1234567890",
      "UserName": "jsmith",
      "BundleId": "wsb-0lq7j2cp4",
      "WorkspaceProperties": {
        "RunningMode": "AUTO_STOP",
        "RunningModeAutoStopTimeoutInMinutes": 60
      },
      "Tags": [{"Key": "Department", "Value": "Engineering"}]
    }
  ]'

# Create a WorkSpace with encryption and DCV protocol
aws workspaces create-workspaces \
  --workspaces '[
    {
      "DirectoryId": "d-1234567890",
      "UserName": "jdoe",
      "BundleId": "wsb-0lq7j2cp4",
      "VolumeEncryptionKey": "arn:aws:kms:us-east-1:123456789012:key/mrk-abc123",
      "UserVolumeEncryptionEnabled": true,
      "RootVolumeEncryptionEnabled": true,
      "WorkspaceProperties": {
        "RunningMode": "ALWAYS_ON",
        "UserVolumeSizeGib": 100,
        "RootVolumeSizeGib": 80
      },
      "Tags": [{"Key": "Department", "Value": "Finance"}]
    }
  ]'

# Create multiple WorkSpaces from a JSON file
aws workspaces create-workspaces \
  --workspaces file://workspaces.json

# --- Describe WorkSpaces ---
aws workspaces describe-workspaces
aws workspaces describe-workspaces --workspace-ids ws-abc123def456
aws workspaces describe-workspaces --directory-id d-1234567890
aws workspaces describe-workspaces --user-name jsmith --directory-id d-1234567890

# --- Describe WorkSpace state/connection status ---
aws workspaces describe-workspaces-connection-status \
  --workspace-ids ws-abc123def456

# --- Reboot (soft restart) a WorkSpace ---
aws workspaces reboot-workspaces \
  --reboot-workspace-requests '[{"WorkspaceId":"ws-abc123def456"}]'

# --- Rebuild (full rebuild from bundle; user data preserved) ---
aws workspaces rebuild-workspaces \
  --rebuild-workspace-requests '[{"WorkspaceId":"ws-abc123def456"}]'

# --- Restore a WorkSpace to a snapshot (wipes user volume changes since snapshot) ---
aws workspaces restore-workspace \
  --workspace-id ws-abc123def456

# --- Terminate (permanently delete) WorkSpaces ---
aws workspaces terminate-workspaces \
  --terminate-workspace-requests '[{"WorkspaceId":"ws-abc123def456"}]'

# Terminate multiple
aws workspaces terminate-workspaces \
  --terminate-workspace-requests \
    '[{"WorkspaceId":"ws-abc123def456"},{"WorkspaceId":"ws-def456abc789"}]'
```

## WorkSpaces Personal — Modify Properties

```bash
# --- Modify running mode (switch to AlwaysOn) ---
aws workspaces modify-workspace-properties \
  --workspace-id ws-abc123def456 \
  --workspace-properties RunningMode=ALWAYS_ON

# --- Switch to AutoStop with 60-minute timeout ---
aws workspaces modify-workspace-properties \
  --workspace-id ws-abc123def456 \
  --workspace-properties RunningMode=AUTO_STOP,RunningModeAutoStopTimeoutInMinutes=60

# --- Resize user volume ---
aws workspaces modify-workspace-properties \
  --workspace-id ws-abc123def456 \
  --workspace-properties UserVolumeSizeGib=200

# --- Upgrade bundle compute type ---
aws workspaces modify-workspace-properties \
  --workspace-id ws-abc123def456 \
  --workspace-properties ComputeTypeName=PERFORMANCE

# --- Modify access properties for a directory (enable/disable web/client access) ---
aws workspaces modify-workspace-access-properties \
  --resource-id d-1234567890 \
  --workspace-access-properties DeviceTypeWindows=ALLOW,DeviceTypeWeb=ALLOW,DeviceTypeOsx=ALLOW,DeviceTypeAndroid=DENY,DeviceTypeIos=DENY

# --- Modify workspace creation properties (default OU, RunningMode, etc.) ---
aws workspaces modify-workspace-creation-properties \
  --resource-id d-1234567890 \
  --workspace-creation-properties EnableInternetAccess=true,DefaultOu="OU=Workspaces,DC=corp,DC=example,DC=com",UserEnabledAsLocalAdministrator=false
```

## WorkSpaces Personal — Migration

```bash
# --- Migrate a WorkSpace to a different bundle ---
aws workspaces migrate-workspace \
  --source-workspace-id ws-abc123def456 \
  --bundle-id wsb-newbundle123

# --- Describe account modifications (BYOL status, etc.) ---
aws workspaces describe-account-modifications

# --- Describe snapshots available for restore ---
aws workspaces describe-workspace-snapshots \
  --workspace-id ws-abc123def456
```

## WorkSpaces Personal — IP Access Control Groups

```bash
# --- Create an IP access control group ---
aws workspaces create-ip-group \
  --group-name "CorpOfficeIPs" \
  --group-desc "Allow access from corporate office IPs" \
  --user-rules '[
    {"ipRule":"203.0.113.0/24","ruleDesc":"NYC Office"},
    {"ipRule":"198.51.100.0/24","ruleDesc":"London Office"}
  ]'

# --- Associate IP group with a directory ---
aws workspaces associate-ip-groups \
  --directory-id d-1234567890 \
  --group-ids wsipg-abc123def456

# --- Update rules in an IP group ---
aws workspaces update-rules-of-ip-group \
  --group-id wsipg-abc123def456 \
  --user-rules '[
    {"ipRule":"203.0.113.0/24","ruleDesc":"NYC Office"},
    {"ipRule":"198.51.100.50/32","ruleDesc":"CEO Home Office"}
  ]'

# --- Describe IP access control groups ---
aws workspaces describe-ip-groups
aws workspaces describe-ip-groups --group-ids wsipg-abc123def456

# --- Disassociate and delete an IP group ---
aws workspaces disassociate-ip-groups \
  --directory-id d-1234567890 \
  --group-ids wsipg-abc123def456

aws workspaces delete-ip-group \
  --group-id wsipg-abc123def456
```

## WorkSpaces Personal — Tags

```bash
# --- Tag a WorkSpace ---
aws workspaces create-tags \
  --resource-id ws-abc123def456 \
  --tags Key=CostCenter,Value=CC-1234 Key=Owner,Value=jsmith

# --- Describe tags ---
aws workspaces describe-tags \
  --resource-id ws-abc123def456

# --- Delete tags ---
aws workspaces delete-tags \
  --resource-id ws-abc123def456 \
  --tag-keys CostCenter
```

---

## WorkSpaces Web — Portals

```bash
# --- Create a WorkSpaces Web portal ---
aws workspaces-web create-portal \
  --display-name "CorpWebPortal" \
  --tags Key=Environment,Value=Production

# --- List portals ---
aws workspaces-web list-portals

# --- Describe a portal ---
aws workspaces-web get-portal \
  --portal-arn "arn:aws:workspaces-web:us-east-1:123456789012:portal/abc123def456"

# --- Update portal display name ---
aws workspaces-web update-portal \
  --portal-arn "arn:aws:workspaces-web:us-east-1:123456789012:portal/abc123def456" \
  --display-name "Updated Corp Web Portal"

# --- Delete a portal ---
aws workspaces-web delete-portal \
  --portal-arn "arn:aws:workspaces-web:us-east-1:123456789012:portal/abc123def456"
```

## WorkSpaces Web — Network Settings

```bash
# --- Create network settings (VPC, subnets, security groups) ---
aws workspaces-web create-network-settings \
  --vpc-id vpc-0abc123def456789 \
  --subnet-ids subnet-0abc123def456789 subnet-0def456abc123789 \
  --security-group-ids sg-0abc123def456789 \
  --tags Key=Environment,Value=Production

# --- Associate network settings with a portal ---
aws workspaces-web associate-network-settings \
  --portal-arn "arn:aws:workspaces-web:us-east-1:123456789012:portal/abc123def456" \
  --network-settings-arn "arn:aws:workspaces-web:us-east-1:123456789012:networkSettings/abc123"

# --- List and get network settings ---
aws workspaces-web list-network-settings
aws workspaces-web get-network-settings \
  --network-settings-arn "arn:aws:workspaces-web:us-east-1:123456789012:networkSettings/abc123"

# --- Disassociate and delete network settings ---
aws workspaces-web disassociate-network-settings \
  --portal-arn "arn:aws:workspaces-web:us-east-1:123456789012:portal/abc123def456"

aws workspaces-web delete-network-settings \
  --network-settings-arn "arn:aws:workspaces-web:us-east-1:123456789012:networkSettings/abc123"
```

## WorkSpaces Web — User Access Logging

```bash
# --- Create a user access logging settings resource ---
aws workspaces-web create-user-access-logging-settings \
  --kinesis-stream-arn "arn:aws:kinesis:us-east-1:123456789012:stream/workspaces-web-logs"

# --- Associate logging settings with a portal ---
aws workspaces-web associate-user-access-logging-settings \
  --portal-arn "arn:aws:workspaces-web:us-east-1:123456789012:portal/abc123def456" \
  --user-access-logging-settings-arn "arn:aws:workspaces-web:us-east-1:123456789012:userAccessLoggingSettings/abc123"

# --- List and get logging settings ---
aws workspaces-web list-user-access-logging-settings
aws workspaces-web get-user-access-logging-settings \
  --user-access-logging-settings-arn "arn:aws:workspaces-web:us-east-1:123456789012:userAccessLoggingSettings/abc123"

# --- Disassociate and delete logging settings ---
aws workspaces-web disassociate-user-access-logging-settings \
  --portal-arn "arn:aws:workspaces-web:us-east-1:123456789012:portal/abc123def456"

aws workspaces-web delete-user-access-logging-settings \
  --user-access-logging-settings-arn "arn:aws:workspaces-web:us-east-1:123456789012:userAccessLoggingSettings/abc123"
```

## WorkSpaces Web — Browser Settings

```bash
# --- Create browser settings (clipboard, download, upload, print policies) ---
aws workspaces-web create-browser-settings \
  --browser-policy '{
    "chromePolicies": {
      "PolicyForChrome": {
        "AllowFileSelectionDialogs": false,
        "PrintingEnabled": false
      }
    }
  }'

# --- Associate browser settings with a portal ---
aws workspaces-web associate-browser-settings \
  --portal-arn "arn:aws:workspaces-web:us-east-1:123456789012:portal/abc123def456" \
  --browser-settings-arn "arn:aws:workspaces-web:us-east-1:123456789012:browserSettings/abc123"

# --- List and get browser settings ---
aws workspaces-web list-browser-settings
aws workspaces-web get-browser-settings \
  --browser-settings-arn "arn:aws:workspaces-web:us-east-1:123456789012:browserSettings/abc123"

# --- Disassociate and delete browser settings ---
aws workspaces-web disassociate-browser-settings \
  --portal-arn "arn:aws:workspaces-web:us-east-1:123456789012:portal/abc123def456"

aws workspaces-web delete-browser-settings \
  --browser-settings-arn "arn:aws:workspaces-web:us-east-1:123456789012:browserSettings/abc123"
```

## WorkSpaces Web — Trust Store and IP Access Settings

```bash
# --- Create a trust store with custom CA certificates ---
aws workspaces-web create-trust-store \
  --certificate-list fileb://corp-ca-cert.pem

# --- Associate trust store with portal ---
aws workspaces-web associate-trust-store \
  --portal-arn "arn:aws:workspaces-web:us-east-1:123456789012:portal/abc123def456" \
  --trust-store-arn "arn:aws:workspaces-web:us-east-1:123456789012:trustStore/abc123"

# --- Create IP access settings ---
aws workspaces-web create-ip-access-settings \
  --ip-rules '[
    {"ipRange":"203.0.113.0/24","description":"NYC Office"},
    {"ipRange":"198.51.100.0/24","description":"London Office"}
  ]' \
  --display-name "CorpOfficeIPs"

# --- Associate IP access settings with portal ---
aws workspaces-web associate-ip-access-settings \
  --portal-arn "arn:aws:workspaces-web:us-east-1:123456789012:portal/abc123def456" \
  --ip-access-settings-arn "arn:aws:workspaces-web:us-east-1:123456789012:ipAccessSettings/abc123"

# --- List and get IP access settings ---
aws workspaces-web list-ip-access-settings
aws workspaces-web get-ip-access-settings \
  --ip-access-settings-arn "arn:aws:workspaces-web:us-east-1:123456789012:ipAccessSettings/abc123"
```

---

## AppStream 2.0 — Images and Image Builders

```bash
# --- List available images (AWS-provided and custom) ---
aws appstream describe-images
aws appstream describe-images --type PRIVATE
aws appstream describe-images --names "MyCorpImage-v1"

# --- Create an image builder (to build a new image) ---
aws appstream create-image-builder \
  --name "ImageBuilder-CorpApps" \
  --instance-type stream.standard.medium \
  --image-name "AppStream-WinServer2019-07-19-2021" \
  --vpc-config SubnetIds=subnet-0abc123def456789,SecurityGroupIds=sg-0abc123def456789 \
  --iam-role-arn arn:aws:iam::123456789012:role/AppStreamImageBuilderRole \
  --enable-default-internet-access false \
  --tags Key=Environment,Value=Build

# --- List image builders ---
aws appstream describe-image-builders

# --- Start and stop an image builder ---
aws appstream start-image-builder --name "ImageBuilder-CorpApps"
aws appstream stop-image-builder --name "ImageBuilder-CorpApps"

# --- Delete image builder ---
aws appstream delete-image-builder --name "ImageBuilder-CorpApps"

# --- Delete a custom image ---
aws appstream delete-image --name "MyCorpImage-v1"

# --- Share an image with another account ---
aws appstream update-image-permissions \
  --name "MyCorpImage-v1" \
  --shared-account-id 123456789012 \
  --image-permissions AllowFleet=true,AllowImageBuilder=false

# --- Describe image permissions ---
aws appstream describe-image-permissions \
  --name "MyCorpImage-v1"
```

## AppStream 2.0 — Fleets

```bash
# --- Create an always-on fleet ---
aws appstream create-fleet \
  --name "CorpAppsFleet" \
  --image-name "MyCorpImage-v2" \
  --instance-type stream.standard.medium \
  --fleet-type ALWAYS_ON \
  --compute-capacity DesiredInstances=5 \
  --vpc-config SubnetIds=subnet-0abc123def456789 subnet-0def456abc123789,SecurityGroupIds=sg-0abc123def456789 \
  --max-user-duration-in-seconds 28800 \
  --disconnect-timeout-in-seconds 900 \
  --idle-disconnect-timeout-in-seconds 900 \
  --enable-default-internet-access false \
  --iam-role-arn arn:aws:iam::123456789012:role/AppStreamFleetRole \
  --stream-view DESKTOP \
  --tags Key=Environment,Value=Production Key=CostCenter,Value=CC-1234

# --- Create an on-demand fleet ---
aws appstream create-fleet \
  --name "CorpAppsFleet-OnDemand" \
  --image-name "MyCorpImage-v2" \
  --instance-type stream.standard.medium \
  --fleet-type ON_DEMAND \
  --compute-capacity DesiredInstances=0 \
  --vpc-config SubnetIds=subnet-0abc123def456789,SecurityGroupIds=sg-0abc123def456789 \
  --max-user-duration-in-seconds 14400 \
  --disconnect-timeout-in-seconds 300

# --- Create an elastic fleet ---
aws appstream create-fleet \
  --name "CorpAppsFleet-Elastic" \
  --instance-type stream.standard.medium \
  --fleet-type ELASTIC \
  --platform WINDOWS_SERVER_2019 \
  --max-concurrent-sessions 50 \
  --vpc-config SubnetIds=subnet-0abc123def456789,SecurityGroupIds=sg-0abc123def456789 \
  --max-user-duration-in-seconds 7200

# --- Start and stop fleets ---
aws appstream start-fleet --name "CorpAppsFleet"
aws appstream stop-fleet --name "CorpAppsFleet"

# --- Describe fleets ---
aws appstream describe-fleets
aws appstream describe-fleets --names "CorpAppsFleet"

# --- Update fleet properties ---
aws appstream update-fleet \
  --name "CorpAppsFleet" \
  --compute-capacity DesiredInstances=10 \
  --disconnect-timeout-in-seconds 600 \
  --max-user-duration-in-seconds 43200

# --- Update fleet image ---
aws appstream update-fleet \
  --name "CorpAppsFleet" \
  --image-name "MyCorpImage-v3"

# --- Delete a fleet ---
aws appstream delete-fleet --name "CorpAppsFleet"
```

## AppStream 2.0 — Stacks

```bash
# --- Create a stack ---
aws appstream create-stack \
  --name "CorpAppsStack" \
  --description "Corporate application stack for engineers" \
  --storage-connectors '[
    {"ConnectorType":"HOMEFOLDERS","ResourceIdentifier":"appstream2-36fb080bb8-us-east-1-123456789012"}
  ]' \
  --user-settings '[
    {"Action":"CLIPBOARD_COPY_FROM_LOCAL_DEVICE","Permission":"ENABLED"},
    {"Action":"CLIPBOARD_COPY_TO_LOCAL_DEVICE","Permission":"DISABLED"},
    {"Action":"FILE_UPLOAD","Permission":"ENABLED"},
    {"Action":"FILE_DOWNLOAD","Permission":"DISABLED"},
    {"Action":"PRINTING_TO_LOCAL_DEVICE","Permission":"ENABLED"}
  ]' \
  --application-settings Enabled=true,SettingsGroup="CorpAppsGroup" \
  --tags Key=Environment,Value=Production

# --- Associate a fleet with a stack ---
aws appstream associate-fleet \
  --fleet-name "CorpAppsFleet" \
  --stack-name "CorpAppsStack"

# --- Describe stacks ---
aws appstream describe-stacks
aws appstream describe-stacks --names "CorpAppsStack"

# --- List fleets associated with a stack ---
aws appstream list-associated-fleets \
  --stack-name "CorpAppsStack"

# --- List stacks associated with a fleet ---
aws appstream list-associated-stacks \
  --fleet-name "CorpAppsFleet"

# --- Update a stack ---
aws appstream update-stack \
  --name "CorpAppsStack" \
  --description "Updated corporate stack" \
  --user-settings '[
    {"Action":"FILE_DOWNLOAD","Permission":"ENABLED"}
  ]'

# --- Disassociate fleet from stack ---
aws appstream disassociate-fleet \
  --fleet-name "CorpAppsFleet" \
  --stack-name "CorpAppsStack"

# --- Delete a stack ---
aws appstream delete-stack --name "CorpAppsStack"
```

## AppStream 2.0 — Applications (Elastic Fleets)

```bash
# --- Create an application (for elastic fleets) ---
aws appstream create-application \
  --name "MicrosoftWord" \
  --display-name "Microsoft Word 2021" \
  --description "Word processor" \
  --icon-s3-location S3Bucket=my-appstream-bucket,S3Key=icons/word.png \
  --launch-path "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE" \
  --platforms WINDOWS_SERVER_2019 \
  --instance-families stream.standard

# --- List applications ---
aws appstream describe-applications

# --- Associate application with a fleet ---
aws appstream associate-application-fleet \
  --application-arn "arn:aws:appstream:us-east-1:123456789012:application/MicrosoftWord" \
  --fleet-name "CorpAppsFleet-Elastic"

# --- Describe fleet application associations ---
aws appstream describe-application-fleet-associations \
  --fleet-name "CorpAppsFleet-Elastic"

# --- Disassociate application from fleet ---
aws appstream disassociate-application-fleet \
  --application-arn "arn:aws:appstream:us-east-1:123456789012:application/MicrosoftWord" \
  --fleet-name "CorpAppsFleet-Elastic"

# --- Update an application ---
aws appstream update-application \
  --name "MicrosoftWord" \
  --display-name "Microsoft Word 2021 (Updated)"

# --- Delete an application ---
aws appstream delete-application \
  --name "MicrosoftWord"
```

## AppStream 2.0 — Users (User Pool)

```bash
# --- Create a user pool user ---
aws appstream create-user \
  --user-name jsmith@corp.example.com \
  --authentication-type USERPOOL \
  --first-name "John" \
  --last-name "Smith" \
  --message-action SUPPRESS

# --- List users ---
aws appstream describe-users \
  --authentication-type USERPOOL

# --- Enable / disable a user ---
aws appstream enable-user \
  --user-name jsmith@corp.example.com \
  --authentication-type USERPOOL

aws appstream disable-user \
  --user-name jsmith@corp.example.com \
  --authentication-type USERPOOL

# --- Delete a user ---
aws appstream delete-user \
  --user-name jsmith@corp.example.com \
  --authentication-type USERPOOL
```

## AppStream 2.0 — User-Stack Associations

```bash
# --- Associate users with a stack (User Pool auth) ---
aws appstream batch-associate-user-stack \
  --user-stack-associations '[
    {
      "StackName": "CorpAppsStack",
      "UserName": "jsmith@corp.example.com",
      "AuthenticationType": "USERPOOL",
      "SendEmailNotification": true
    },
    {
      "StackName": "CorpAppsStack",
      "UserName": "jdoe@corp.example.com",
      "AuthenticationType": "USERPOOL",
      "SendEmailNotification": false
    }
  ]'

# --- Describe user-stack associations ---
aws appstream describe-user-stack-associations \
  --stack-name "CorpAppsStack" \
  --authentication-type USERPOOL

aws appstream describe-user-stack-associations \
  --user-name jsmith@corp.example.com \
  --authentication-type USERPOOL

# --- Disassociate users from a stack ---
aws appstream batch-disassociate-user-stack \
  --user-stack-associations '[
    {
      "StackName": "CorpAppsStack",
      "UserName": "jsmith@corp.example.com",
      "AuthenticationType": "USERPOOL"
    }
  ]'
```

## AppStream 2.0 — Streaming URLs

```bash
# --- Create a streaming URL (for SAML/API-based embedding) ---
aws appstream create-streaming-url \
  --stack-name "CorpAppsStack" \
  --fleet-name "CorpAppsFleet" \
  --user-id "jsmith@corp.example.com" \
  --application-id "MicrosoftWord" \
  --validity 3600

# --- Create an image builder streaming URL (for remote Image Builder access) ---
aws appstream create-image-builder-streaming-url \
  --name "ImageBuilder-CorpApps" \
  --validity 3600
```

## AppStream 2.0 — Sessions

```bash
# --- List active sessions ---
aws appstream describe-sessions \
  --stack-name "CorpAppsStack" \
  --fleet-name "CorpAppsFleet"

aws appstream describe-sessions \
  --stack-name "CorpAppsStack" \
  --fleet-name "CorpAppsFleet" \
  --user-id "jsmith@corp.example.com" \
  --authentication-type SAML

# --- Expire (force-end) a session ---
aws appstream expire-session \
  --session-id "abc123def456-ghi789-jkl012"
```

## AppStream 2.0 — Usage Reports

```bash
# --- Enable usage reports (delivered to S3) ---
aws appstream create-usage-report-subscription

# --- Describe usage report subscription ---
aws appstream describe-usage-report-subscriptions

# --- Delete usage report subscription ---
aws appstream delete-usage-report-subscription
```

## AppStream 2.0 — Tags

```bash
# --- Tag an AppStream resource ---
aws appstream tag-resource \
  --resource-arn "arn:aws:appstream:us-east-1:123456789012:fleet/CorpAppsFleet" \
  --tags Environment=Production CostCenter=CC-1234

# --- List tags on a resource ---
aws appstream list-tags-for-resource \
  --resource-arn "arn:aws:appstream:us-east-1:123456789012:fleet/CorpAppsFleet"

# --- Untag a resource ---
aws appstream untag-resource \
  --resource-arn "arn:aws:appstream:us-east-1:123456789012:fleet/CorpAppsFleet" \
  --tag-keys CostCenter
```
