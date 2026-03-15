# AWS Collaboration — CLI Reference

For service concepts, see [collaboration-capabilities.md](collaboration-capabilities.md).

## Amazon WorkMail

```bash
# --- Organizations ---
aws workmail list-organizations

aws workmail describe-organization \
  --organization-id m-abc12345def67890

# Create a WorkMail organization (requires an existing directory)
aws workmail create-organization \
  --alias mycompany \
  --directory-id d-1234567890 \
  --kms-key-arn arn:aws:kms:us-east-1:123456789012:key/mrk-12345

aws workmail delete-organization \
  --organization-id m-abc12345def67890 \
  --delete-directory

# --- Users ---
aws workmail create-user \
  --organization-id m-abc12345def67890 \
  --name jsmith \
  --display-name "John Smith" \
  --password 'TempP@ssw0rd!'

aws workmail describe-user \
  --organization-id m-abc12345def67890 \
  --user-id user-id-12345

aws workmail list-users \
  --organization-id m-abc12345def67890

# Enable mailbox for a user
aws workmail register-to-work-mail \
  --organization-id m-abc12345def67890 \
  --entity-id user-id-12345 \
  --email jsmith@example.com

# Update user password
aws workmail reset-password \
  --organization-id m-abc12345def67890 \
  --user-id user-id-12345 \
  --password 'NewP@ssw0rd!'

# Update user display name
aws workmail update-user \
  --organization-id m-abc12345def67890 \
  --user-id user-id-12345 \
  --display-name "John A. Smith"

# Deregister mailbox (disable email but keep user)
aws workmail deregister-from-work-mail \
  --organization-id m-abc12345def67890 \
  --entity-id user-id-12345

aws workmail delete-user \
  --organization-id m-abc12345def67890 \
  --user-id user-id-12345

# --- Groups ---
aws workmail create-group \
  --organization-id m-abc12345def67890 \
  --name support-team

aws workmail describe-group \
  --organization-id m-abc12345def67890 \
  --group-id group-id-12345

aws workmail list-groups \
  --organization-id m-abc12345def67890

# Register group with an email address
aws workmail register-to-work-mail \
  --organization-id m-abc12345def67890 \
  --entity-id group-id-12345 \
  --email support@example.com

# Add member to group
aws workmail associate-member-to-group \
  --organization-id m-abc12345def67890 \
  --group-id group-id-12345 \
  --member-id user-id-12345

# List group members
aws workmail list-group-members \
  --organization-id m-abc12345def67890 \
  --group-id group-id-12345

# Remove member from group
aws workmail disassociate-member-from-group \
  --organization-id m-abc12345def67890 \
  --group-id group-id-12345 \
  --member-id user-id-12345

aws workmail delete-group \
  --organization-id m-abc12345def67890 \
  --group-id group-id-12345

# --- Resources (rooms/equipment) ---
aws workmail create-resource \
  --organization-id m-abc12345def67890 \
  --name "Conference Room A" \
  --type ROOM

aws workmail describe-resource \
  --organization-id m-abc12345def67890 \
  --resource-id res-id-12345

aws workmail list-resources \
  --organization-id m-abc12345def67890

# Update resource booking policy
aws workmail update-resource \
  --organization-id m-abc12345def67890 \
  --resource-id res-id-12345 \
  --booking-options '{
    "AutoAcceptRequests": true,
    "AutoDeclineRecurringRequests": false,
    "AutoDeclineConflictingRequests": true
  }'

# Register resource with email
aws workmail register-to-work-mail \
  --organization-id m-abc12345def67890 \
  --entity-id res-id-12345 \
  --email conferenceroom-a@example.com

aws workmail delete-resource \
  --organization-id m-abc12345def67890 \
  --resource-id res-id-12345

# --- Aliases ---
aws workmail create-alias \
  --organization-id m-abc12345def67890 \
  --entity-id user-id-12345 \
  --alias john.smith@example.com

aws workmail list-aliases \
  --organization-id m-abc12345def67890 \
  --entity-id user-id-12345

aws workmail delete-alias \
  --organization-id m-abc12345def67890 \
  --entity-id user-id-12345 \
  --alias john.smith@example.com

# --- Access control rules ---
# Block access from specific IP ranges
aws workmail create-mobile-device-access-rule \
  --organization-id m-abc12345def67890 \
  --name "Block unknown devices" \
  --effect DENY \
  --not-device-types '["iPad", "iPhone", "WindowsPhone"]'

aws workmail list-mobile-device-access-rules \
  --organization-id m-abc12345def67890

# Organization-level access rules (IP, protocol, impersonation)
aws workmail put-access-control-rule \
  --organization-id m-abc12345def67890 \
  --name "Allow only corporate IPs" \
  --effect ALLOW \
  --description "Restrict access to corporate IP range" \
  --ip-ranges '["203.0.113.0/24"]' \
  --actions '["ActiveSync", "IMAP", "SMTP", "AutoDiscover", "WebMail", "EWS"]'

aws workmail list-access-control-rules \
  --organization-id m-abc12345def67890

aws workmail delete-access-control-rule \
  --organization-id m-abc12345def67890 \
  --name "Allow only corporate IPs"

# --- Email flow rules (inbound/outbound Lambda processing) ---
aws workmail create-inbound-mail-flow-rule \
  --organization-id m-abc12345def67890 \
  --rule-name "Virus Scan" \
  --effect BOUNCE \
  --conditions '[{"IncomingDomain": {"Operator": "NOT_CONTAINS", "Value": "@trusted.com"}}]'

aws workmail list-inbound-mail-flow-rules \
  --organization-id m-abc12345def67890

# Lambda action rule
aws workmail create-inbound-mail-flow-rule \
  --organization-id m-abc12345def67890 \
  --rule-name "Compliance Archive" \
  --effect ALLOW \
  --actions '[{"S3Action": {"RoleArn": "arn:aws:iam::123456789012:role/WorkMailRole", "BucketName": "email-archive", "ObjectKeyPrefix": "inbound/"}}]'

# --- Impersonation roles (for programmatic mailbox access) ---
aws workmail create-impersonation-role \
  --organization-id m-abc12345def67890 \
  --name "Compliance Reader" \
  --type READ_ONLY \
  --rules '[{"Effect": "ALLOW", "Impersonation-matched-targets": []}]'

aws workmail list-impersonation-roles \
  --organization-id m-abc12345def67890

# --- Tags ---
aws workmail tag-resource \
  --resource-arn arn:aws:workmail:us-east-1:123456789012:organization/m-abc12345def67890 \
  --tags '[{"Key": "Environment", "Value": "prod"}]'
```

---

## Amazon WorkDocs

```bash
# --- Sites (via WorkDocs console or Directory Service; CLI for resource management) ---
aws workdocs describe-instances \
  --authentication-token "USER_TOKEN"

aws workdocs describe-document-versions \
  --authentication-token "USER_TOKEN" \
  --document-id doc-id-12345

# --- Users ---
aws workdocs describe-users \
  --authentication-token "USER_TOKEN" \
  --organization-id d-1234567890

aws workdocs create-user \
  --organization-id d-1234567890 \
  --username jsmith \
  --given-name John \
  --surname Smith \
  --password 'TempP@ssw0rd!' \
  --email-address jsmith@example.com \
  --storage-rule '{"StorageAllocatedInBytes": 53687091200}'  # 50 GB

aws workdocs describe-users \
  --authentication-token "USER_TOKEN" \
  --query 'Users[?Username==`jsmith`]'

aws workdocs update-user \
  --authentication-token "USER_TOKEN" \
  --user-id user-id-12345 \
  --given-name "John" \
  --surname "Smith" \
  --type MINIMALUSER

aws workdocs delete-user \
  --authentication-token "USER_TOKEN" \
  --user-id user-id-12345

# --- Folders ---
aws workdocs create-folder \
  --authentication-token "USER_TOKEN" \
  --name "Q1 Reports" \
  --parent-folder-id parent-folder-id-12345

aws workdocs describe-folder-contents \
  --authentication-token "USER_TOKEN" \
  --folder-id folder-id-12345 \
  --type ALL \
  --sort DATE \
  --order DESCENDING

aws workdocs update-folder \
  --authentication-token "USER_TOKEN" \
  --folder-id folder-id-12345 \
  --name "Q1 2024 Reports"

aws workdocs delete-folder \
  --authentication-token "USER_TOKEN" \
  --folder-id folder-id-12345

# Recycle folder and its contents
aws workdocs delete-folder-contents \
  --authentication-token "USER_TOKEN" \
  --folder-id folder-id-12345

# --- Documents ---
# Step 1: Initiate document creation (get upload URL)
aws workdocs initiate-document-version-upload \
  --authentication-token "USER_TOKEN" \
  --parent-folder-id folder-id-12345 \
  --name "annual-report.pdf" \
  --content-type "application/pdf"

# Step 2: Upload the file using the presigned URL returned above (use curl or SDK)
# Step 3: Update document version status to ACTIVE
aws workdocs update-document-version \
  --authentication-token "USER_TOKEN" \
  --document-id doc-id-12345 \
  --version-id version-id-12345 \
  --version-status ACTIVE

aws workdocs get-document \
  --authentication-token "USER_TOKEN" \
  --document-id doc-id-12345

aws workdocs describe-document-versions \
  --authentication-token "USER_TOKEN" \
  --document-id doc-id-12345

# Get download URL for a specific version
aws workdocs get-document-version \
  --authentication-token "USER_TOKEN" \
  --document-id doc-id-12345 \
  --version-id version-id-12345 \
  --include-custom-metadata

aws workdocs update-document \
  --authentication-token "USER_TOKEN" \
  --document-id doc-id-12345 \
  --name "annual-report-final.pdf" \
  --resource-state ACTIVE

aws workdocs delete-document \
  --authentication-token "USER_TOKEN" \
  --document-id doc-id-12345

# --- Permissions (sharing) ---
aws workdocs add-resource-permissions \
  --authentication-token "USER_TOKEN" \
  --resource-id doc-id-12345 \
  --principals '[
    {"Id": "user-id-12345", "Type": "USER", "Role": "VIEWER"},
    {"Id": "group-id-12345", "Type": "GROUP", "Role": "CONTRIBUTOR"}
  ]'

aws workdocs describe-resource-permissions \
  --authentication-token "USER_TOKEN" \
  --resource-id doc-id-12345

aws workdocs remove-resource-permission \
  --authentication-token "USER_TOKEN" \
  --resource-id doc-id-12345 \
  --principal-id user-id-12345 \
  --principal-type USER

# Share link
aws workdocs create-notification-subscription \
  --organization-id d-1234567890 \
  --endpoint arn:aws:sns:us-east-1:123456789012:workdocs-notifications \
  --protocol SNS \
  --subscription-type ALL

# --- Custom metadata & labels ---
aws workdocs create-custom-metadata \
  --authentication-token "USER_TOKEN" \
  --resource-id doc-id-12345 \
  --custom-metadata '{"department": "finance", "fiscal-year": "2024", "status": "approved"}'

aws workdocs describe-custom-metadata \
  --authentication-token "USER_TOKEN" \
  --resource-id doc-id-12345

aws workdocs delete-custom-metadata \
  --authentication-token "USER_TOKEN" \
  --resource-id doc-id-12345 \
  --keys department fiscal-year

aws workdocs create-labels \
  --authentication-token "USER_TOKEN" \
  --resource-id doc-id-12345 \
  --labels Important Reviewed

aws workdocs delete-labels \
  --authentication-token "USER_TOKEN" \
  --resource-id doc-id-12345 \
  --labels Reviewed

# --- Activity feed ---
aws workdocs describe-activities \
  --authentication-token "USER_TOKEN" \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-31T23:59:59Z \
  --activity-types "DOCUMENT_VERSION_UPLOADED,DOCUMENT_SHARED"

# --- Comments ---
aws workdocs create-comment \
  --authentication-token "USER_TOKEN" \
  --document-id doc-id-12345 \
  --version-id version-id-12345 \
  --text "Please review section 3.2"

aws workdocs describe-comments \
  --authentication-token "USER_TOKEN" \
  --document-id doc-id-12345 \
  --version-id version-id-12345

aws workdocs delete-comment \
  --authentication-token "USER_TOKEN" \
  --document-id doc-id-12345 \
  --version-id version-id-12345 \
  --comment-id comment-id-12345
```

---

## AWS Wickr

> **Note**: AWS Wickr is primarily managed through the Wickr Admin console and the Wickr API (REST). Direct AWS CLI support is limited. The following covers available CLI operations.

```bash
# Wickr network management via AWS CLI (wickr service endpoint)
# Note: Most Wickr administration is performed via the Wickr Admin Console
# or the Wickr REST API (https://docs.wickr.aws/docs)

# List Wickr networks in your account (if using AWS CLI wickr integration)
aws wickr list-networks

aws wickr get-network --network-id network-id-12345

# For Wickr programmatic user management, use the Wickr REST API:
# POST /user  - create user
# GET  /user/{userId} - describe user
# DELETE /user/{userId} - deactivate user
# POST /room  - create room
# POST /message - send message (bot framework)
```
