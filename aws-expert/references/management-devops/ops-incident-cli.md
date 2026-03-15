# Ops & Incident Tools — CLI Reference

For service concepts, see [ops-incident-capabilities.md](ops-incident-capabilities.md).

## AWS Chatbot

```bash
# --- Slack Channel Configurations ---
# Create a Slack channel configuration
aws chatbot create-slack-channel-configuration \
  --configuration-name ops-alerts \
  --slack-workspace-id T01ABCDEFGH \
  --slack-channel-id C01ABCDEFGH \
  --iam-role-arn arn:aws:iam::123456789012:role/ChatbotChannelRole \
  --sns-topic-arns arn:aws:sns:us-east-1:123456789012:ops-alerts \
  --guardrail-policy-arns arn:aws:iam::aws:policy/ReadOnlyAccess \
  --logging-level INFO

# List Slack channel configurations
aws chatbot get-slack-channel-configurations

# List Slack channel configurations for a specific workspace
aws chatbot get-slack-channel-configurations \
  --chat-configuration-arn arn:aws:chatbot::123456789012:chat-configuration/slack-channel/ops-alerts

# Update a Slack channel configuration (e.g., add SNS topic)
aws chatbot update-slack-channel-configuration \
  --chat-configuration-arn arn:aws:chatbot::123456789012:chat-configuration/slack-channel/ops-alerts \
  --sns-topic-arns \
    arn:aws:sns:us-east-1:123456789012:ops-alerts \
    arn:aws:sns:us-east-1:123456789012:security-alerts

# Delete a Slack channel configuration
aws chatbot delete-slack-channel-configuration \
  --chat-configuration-arn arn:aws:chatbot::123456789012:chat-configuration/slack-channel/ops-alerts

# List available Slack workspaces (workspaces that have authorized Chatbot)
aws chatbot get-slack-workspaces

# --- Microsoft Teams Channel Configurations ---
# Create a Teams channel configuration
aws chatbot create-teams-channel-configuration \
  --configuration-name teams-ops-alerts \
  --team-id XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX \
  --team-name "Engineering" \
  --channel-id XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX \
  --channel-name "ops-alerts" \
  --tenant-id XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX \
  --iam-role-arn arn:aws:iam::123456789012:role/ChatbotChannelRole \
  --sns-topic-arns arn:aws:sns:us-east-1:123456789012:ops-alerts \
  --guardrail-policy-arns arn:aws:iam::aws:policy/ReadOnlyAccess

# List Teams channel configurations
aws chatbot get-teams-channel-configurations

# Update a Teams channel configuration
aws chatbot update-teams-channel-configuration \
  --chat-configuration-arn arn:aws:chatbot::123456789012:chat-configuration/teams-channel/teams-ops-alerts \
  --iam-role-arn arn:aws:iam::123456789012:role/ChatbotChannelRoleUpdated

# Delete a Teams channel configuration
aws chatbot delete-teams-channel-configuration \
  --chat-configuration-arn arn:aws:chatbot::123456789012:chat-configuration/teams-channel/teams-ops-alerts

# List Microsoft Teams configured tenants
aws chatbot list-microsoft-teams-configured-tenants

# List Teams user identities (users who have linked their AWS identity)
aws chatbot list-microsoft-teams-user-identities \
  --chat-configuration-arn arn:aws:chatbot::123456789012:chat-configuration/teams-channel/teams-ops-alerts

# --- Account Preferences ---
# Get account-level Chatbot preferences
aws chatbot get-account-preferences

# Update account preferences (enable/disable training data)
aws chatbot update-account-preferences \
  --training-data-collection-disabled
```

---

## AWS Incident Manager

```bash
# --- Replication Sets (must be created before anything else) ---
# Create a replication set (defines regions where Incident Manager operates)
aws ssm-incidents create-replication-set \
  --regions '{
    "us-east-1": {"sseKmsKeyId": "DefaultKey"},
    "us-west-2": {"sseKmsKeyId": "DefaultKey"}
  }'

# Get replication set status and configuration
aws ssm-incidents list-replication-sets

# Update replication set (add a region)
aws ssm-incidents update-replication-set \
  --arn arn:aws:ssm-incidents:us-east-1:123456789012:replication-set/REPLICATION-SET-UUID \
  --actions '[{
    "addRegionAction": {
      "regionName": "eu-west-1",
      "sseKmsKeyId": "DefaultKey"
    }
  }]'

# --- Response Plans ---
# Create a response plan
aws ssm-incidents create-response-plan \
  --name web-service-outage \
  --display-name "Web Service Outage" \
  --incident-template '{
    "title": "Web Service Outage",
    "impact": 2,
    "summary": "The primary web service is experiencing an outage",
    "notificationTargets": [
      {"snsTopicArn": "arn:aws:sns:us-east-1:123456789012:incident-notifications"}
    ]
  }' \
  --chat-channel '{
    "chatbotSns": ["arn:aws:sns:us-east-1:123456789012:incident-notifications"]
  }' \
  --engagements \
    arn:aws:ssm-contacts:us-east-1:123456789012:escalation-plan/on-call-escalation \
  --actions '[{
    "ssmAutomation": {
      "documentName": "AWSIncidents-CriticalIncidentRunbookTemplate",
      "documentVersion": "$DEFAULT",
      "roleArn": "arn:aws:iam::123456789012:role/IncidentManagerAutomationRole",
      "targetAccount": "RESPONSE_PLAN_OWNER_ACCOUNT"
    }
  }]'

# List all response plans
aws ssm-incidents list-response-plans

# Get response plan details
aws ssm-incidents get-response-plan \
  --arn arn:aws:ssm-incidents:us-east-1:123456789012:response-plan/web-service-outage

# Update a response plan
aws ssm-incidents update-response-plan \
  --arn arn:aws:ssm-incidents:us-east-1:123456789012:response-plan/web-service-outage \
  --incident-template-impact 1

# Delete a response plan
aws ssm-incidents delete-response-plan \
  --arn arn:aws:ssm-incidents:us-east-1:123456789012:response-plan/web-service-outage

# --- Incidents ---
# Create an incident manually (trigger from a response plan)
aws ssm-incidents start-incident \
  --response-plan-arn arn:aws:ssm-incidents:us-east-1:123456789012:response-plan/web-service-outage \
  --title "P1: Checkout service is down" \
  --impact 1 \
  --trigger-details '{
    "source": "manual",
    "timestamp": "2026-03-14T10:00:00Z"
  }'

# Get an incident record
aws ssm-incidents get-incident-record \
  --arn arn:aws:ssm-incidents:us-east-1:123456789012:incident-record/web-service-outage/INCIDENT-UUID

# List incidents (filter by status)
aws ssm-incidents list-incidents \
  --filters '[{
    "key": "status",
    "condition": {"equals": {"stringValues": ["OPEN"]}}
  }]'

# Update an incident (change status, impact, or summary)
aws ssm-incidents update-incident-record \
  --arn arn:aws:ssm-incidents:us-east-1:123456789012:incident-record/web-service-outage/INCIDENT-UUID \
  --status RESOLVED \
  --summary "Issue resolved by restarting the checkout service fleet"

# --- Timeline Events ---
# Create a manual timeline event on an incident
aws ssm-incidents create-timeline-event \
  --incident-record-arn arn:aws:ssm-incidents:us-east-1:123456789012:incident-record/web-service-outage/INCIDENT-UUID \
  --event-data '"Identified root cause: memory leak in checkout-service v2.3.1"' \
  --event-type Custom Event \
  --event-time "2026-03-14T10:15:00Z"

# List timeline events for an incident
aws ssm-incidents list-timeline-events \
  --incident-record-arn arn:aws:ssm-incidents:us-east-1:123456789012:incident-record/web-service-outage/INCIDENT-UUID

# Get a specific timeline event
aws ssm-incidents get-timeline-event \
  --incident-record-arn arn:aws:ssm-incidents:us-east-1:123456789012:incident-record/web-service-outage/INCIDENT-UUID \
  --event-id EVENT-UUID

# Update a timeline event
aws ssm-incidents update-timeline-event \
  --incident-record-arn arn:aws:ssm-incidents:us-east-1:123456789012:incident-record/web-service-outage/INCIDENT-UUID \
  --event-id EVENT-UUID \
  --event-data '"Root cause confirmed: memory leak fixed in hotfix v2.3.2"'

# --- Related Items ---
# Add related items to an incident (metrics, runbooks, dashboards)
aws ssm-incidents update-related-items \
  --incident-record-arn arn:aws:ssm-incidents:us-east-1:123456789012:incident-record/web-service-outage/INCIDENT-UUID \
  --related-items-update '{
    "itemsToAdd": [{
      "identifier": {
        "type": "METRIC",
        "value": {"url": "https://console.aws.amazon.com/cloudwatch/..."}
      },
      "title": "Checkout service error rate"
    }]
  }'

# List related items for an incident
aws ssm-incidents list-related-items \
  --incident-record-arn arn:aws:ssm-incidents:us-east-1:123456789012:incident-record/web-service-outage/INCIDENT-UUID

# --- Post-Incident Analysis ---
# Create a post-incident analysis
aws ssm-incidents create-post-incident-analysis \
  --incident-record-arn arn:aws:ssm-incidents:us-east-1:123456789012:incident-record/web-service-outage/INCIDENT-UUID

# List post-incident analyses
aws ssm-incidents list-incident-analyses \
  --incident-record-arn arn:aws:ssm-incidents:us-east-1:123456789012:incident-record/web-service-outage/INCIDENT-UUID
```

---

## AWS User Notifications

```bash
# --- Notification Hubs ---
# Create a notification hub in a region
aws notifications create-notification-hub \
  --region us-east-1

# List all notification hubs
aws notifications list-notification-hubs

# Delete a notification hub
aws notifications deregister-notification-hub \
  --notification-hub-region us-east-1

# --- Notification Configurations ---
# Create a notification configuration (top-level container for event rules)
aws notifications create-notification-configuration \
  --name security-alerts \
  --description "Security Hub and GuardDuty alerts" \
  --aggregation-duration PT5M

# List notification configurations
aws notifications list-notification-configurations

# Get a notification configuration
aws notifications get-notification-configuration \
  --arn arn:aws:notifications::123456789012:configuration/security-alerts

# Update a notification configuration
aws notifications update-notification-configuration \
  --arn arn:aws:notifications::123456789012:configuration/security-alerts \
  --aggregation-duration PT15M

# Delete a notification configuration
aws notifications delete-notification-configuration \
  --arn arn:aws:notifications::123456789012:configuration/security-alerts

# --- Event Rules ---
# Create an event rule for Security Hub HIGH/CRITICAL findings
aws notifications create-event-rule \
  --notification-configuration-arn arn:aws:notifications::123456789012:configuration/security-alerts \
  --source aws.securityhub \
  --event-type "Security Hub Findings - Imported" \
  --regions us-east-1 us-west-2 \
  --event-pattern '{
    "detail": {
      "findings": {
        "Severity": {
          "Label": ["HIGH", "CRITICAL"]
        }
      }
    }
  }'

# Create an event rule for CloudWatch alarm state changes
aws notifications create-event-rule \
  --notification-configuration-arn arn:aws:notifications::123456789012:configuration/ops-alerts \
  --source aws.cloudwatch \
  --event-type "CloudWatch Alarm State Change" \
  --regions us-east-1

# List event rules for a notification configuration
aws notifications list-event-rules \
  --notification-configuration-arn arn:aws:notifications::123456789012:configuration/security-alerts

# Get an event rule
aws notifications get-event-rule \
  --arn arn:aws:notifications::123456789012:rule/RULE-UUID

# Update an event rule
aws notifications update-event-rule \
  --arn arn:aws:notifications::123456789012:rule/RULE-UUID \
  --regions us-east-1 us-west-2 eu-west-1

# Delete an event rule
aws notifications delete-event-rule \
  --arn arn:aws:notifications::123456789012:rule/RULE-UUID

# --- Notification Channels (Email) ---
# Create an email contact
aws notifications create-email-contact \
  --name ops-team-email \
  --email-address ops-team@example.com

# List managed notification account contacts
aws notifications list-managed-notification-account-contacts

# Associate a channel with a notification configuration
aws notifications associate-channel \
  --notification-configuration-arn arn:aws:notifications::123456789012:configuration/security-alerts \
  --arn arn:aws:notifications::123456789012:contact/ops-team-email

# Disassociate a channel
aws notifications disassociate-channel \
  --notification-configuration-arn arn:aws:notifications::123456789012:configuration/security-alerts \
  --arn arn:aws:notifications::123456789012:contact/ops-team-email

# List channels associated with a notification configuration
aws notifications list-channels \
  --notification-configuration-arn arn:aws:notifications::123456789012:configuration/security-alerts

# --- Notification Events ---
# List notification events (delivered events)
aws notifications list-notification-events \
  --notification-configuration-arn arn:aws:notifications::123456789012:configuration/security-alerts

# Get a specific notification event
aws notifications get-notification-event \
  --arn arn:aws:notifications::123456789012:notification-event/EVENT-UUID \
  --locale en-US
```

---

## AWS Quick Setup

```bash
# --- Configuration Managers ---
# Create a host management configuration manager
aws ssm-quicksetup create-configuration-manager \
  --name fleet-host-management \
  --description "Enable SSM Agent, inventory, patching, and CloudWatch agent fleet-wide" \
  --configuration-definitions '[{
    "type": "AWSQuickSetupType-SSMHostMgmt",
    "typeVersion": "1.0",
    "parameters": {
      "UpdateSsmAgent": "true",
      "CollectInventory": "true",
      "ScanForPatches": "true",
      "InstallCloudWatchAgent": "true",
      "UpdateCloudWatchAgent": "true"
    },
    "localDeploymentAdministrationRoleArn": "arn:aws:iam::123456789012:role/QuickSetupAdminRole",
    "localDeploymentExecutionRoleName": "AmazonSSMRoleForInstancesQuickSetup"
  }]' \
  --tags '{"Environment": "production"}'

# List all configuration managers
aws ssm-quicksetup list-configuration-managers

# Get configuration manager details and deployment status
aws ssm-quicksetup get-configuration-manager \
  --manager-arn arn:aws:ssm-quicksetup:us-east-1:123456789012:configuration-manager/MANAGER-UUID

# Update a configuration manager (e.g., change parameters)
aws ssm-quicksetup update-configuration-manager \
  --manager-arn arn:aws:ssm-quicksetup:us-east-1:123456789012:configuration-manager/MANAGER-UUID \
  --configuration-definitions '[{
    "id": "DEFINITION-UUID",
    "parameters": {
      "UpdateSsmAgent": "true",
      "CollectInventory": "true",
      "ScanForPatches": "true",
      "InstallCloudWatchAgent": "true",
      "UpdateCloudWatchAgent": "true",
      "InstallAndManageCloudWatchAgent": "true"
    }
  }]'

# Delete a configuration manager
aws ssm-quicksetup delete-configuration-manager \
  --manager-arn arn:aws:ssm-quicksetup:us-east-1:123456789012:configuration-manager/MANAGER-UUID

# --- Configuration Definitions ---
# List all configuration definitions within a manager
aws ssm-quicksetup list-configuration-definitions \
  --manager-arn arn:aws:ssm-quicksetup:us-east-1:123456789012:configuration-manager/MANAGER-UUID

# --- Quick Setup Service Settings ---
# Get Quick Setup service settings for the account/region
aws ssm-quicksetup get-service-settings

# Update service settings (e.g., enable Explorer integration)
aws ssm-quicksetup update-service-settings \
  --explorer-enabling-role-arn arn:aws:iam::123456789012:role/AWSServiceRoleForSSM
```

---

## AWS Systems Manager for SAP

```bash
# --- Applications ---
# Register an SAP HANA application
aws ssm-sap register-application \
  --application-id HDB \
  --application-type HANA \
  --instances i-0abcdef1234567890 \
  --credentials '[{
    "databaseName": "HDB",
    "credentialType": "ADMIN",
    "secretId": "arn:aws:secretsmanager:us-east-1:123456789012:secret:sap-hana-system-user"
  }]' \
  --sap-instance-number "00" \
  --sid HDB

# List all registered SAP applications
aws ssm-sap list-applications

# Get details of a specific SAP application
aws ssm-sap get-application \
  --application-id HDB \
  --application-arn arn:aws:ssm-sap:us-east-1:123456789012:instance/HDB

# Update application credentials (e.g., after Secrets Manager rotation)
aws ssm-sap update-application-settings \
  --application-id HDB \
  --application-arn arn:aws:ssm-sap:us-east-1:123456789012:instance/HDB \
  --credentials '[{
    "databaseName": "HDB",
    "credentialType": "ADMIN",
    "secretId": "arn:aws:secretsmanager:us-east-1:123456789012:secret:sap-hana-system-user-rotated"
  }]'

# Deregister an SAP application
aws ssm-sap deregister-application \
  --application-id HDB \
  --application-arn arn:aws:ssm-sap:us-east-1:123456789012:instance/HDB

# --- Components ---
# List components of an SAP application
aws ssm-sap list-components \
  --application-id HDB \
  --application-arn arn:aws:ssm-sap:us-east-1:123456789012:instance/HDB

# Get a specific component
aws ssm-sap get-component \
  --application-id HDB \
  --application-arn arn:aws:ssm-sap:us-east-1:123456789012:instance/HDB \
  --component-id HANADB

# --- Databases ---
# List databases registered with SSM for SAP
aws ssm-sap list-databases

# List databases for a specific application and component
aws ssm-sap list-databases \
  --application-id HDB \
  --application-arn arn:aws:ssm-sap:us-east-1:123456789012:instance/HDB \
  --component-id HANADB

# Get database details
aws ssm-sap get-database \
  --application-id HDB \
  --application-arn arn:aws:ssm-sap:us-east-1:123456789012:instance/HDB \
  --component-id HANADB \
  --database-id SYSTEMDB

# --- Start / Stop ---
# Start an SAP application
aws ssm-sap start-application \
  --application-id HDB \
  --application-arn arn:aws:ssm-sap:us-east-1:123456789012:instance/HDB

# Start an SAP application and refresh discovery afterward
aws ssm-sap start-application \
  --application-id HDB \
  --application-arn arn:aws:ssm-sap:us-east-1:123456789012:instance/HDB \
  --start-and-discover

# Stop an SAP application
aws ssm-sap stop-application \
  --application-id HDB \
  --application-arn arn:aws:ssm-sap:us-east-1:123456789012:instance/HDB \
  --stop-connected-entity DBMS

# --- Backup and Restore ---
# Backup a HANA database to S3
aws ssm-sap backup-database \
  --application-id HDB \
  --application-arn arn:aws:ssm-sap:us-east-1:123456789012:instance/HDB \
  --component-id HANADB \
  --database-id SYSTEMDB

# Restore a HANA database from backup
aws ssm-sap restore-database \
  --application-id HDB \
  --application-arn arn:aws:ssm-sap:us-east-1:123456789012:instance/HDB \
  --component-id HANADB \
  --database-id SYSTEMDB \
  --source-system '{
    "applicationId": "HDB",
    "applicationArn": "arn:aws:ssm-sap:us-east-1:123456789012:instance/HDB",
    "componentId": "HANADB",
    "databaseId": "SYSTEMDB"
  }'

# --- Operations ---
# Get the status of an async operation (backup, restore, start, stop)
aws ssm-sap get-operation \
  --operation-id OPERATION-UUID

# List operations for an application
aws ssm-sap list-operations \
  --application-id HDB \
  --application-arn arn:aws:ssm-sap:us-east-1:123456789012:instance/HDB

# Filter operations by type and status
aws ssm-sap list-operations \
  --application-id HDB \
  --application-arn arn:aws:ssm-sap:us-east-1:123456789012:instance/HDB \
  --filters '[
    {"name": "operationType", "value": "BACKUP", "operator": "EQUALS"},
    {"name": "status", "value": "SUCCESS", "operator": "EQUALS"}
  ]'

# --- Resource Permissions ---
# Put resource permission (share resource with another account)
aws ssm-sap put-resource-permission \
  --resource-arn arn:aws:ssm-sap:us-east-1:123456789012:instance/HDB \
  --action-type RESTORE \
  --source-resource-arn arn:aws:ssm-sap:us-east-1:111111111111:instance/QA-HDB

# Get resource permissions for a database
aws ssm-sap get-resource-permission \
  --resource-arn arn:aws:ssm-sap:us-east-1:123456789012:instance/HDB \
  --action-type RESTORE

# Delete resource permission
aws ssm-sap delete-resource-permission \
  --resource-arn arn:aws:ssm-sap:us-east-1:123456789012:instance/HDB \
  --action-type RESTORE \
  --source-resource-arn arn:aws:ssm-sap:us-east-1:111111111111:instance/QA-HDB
```
