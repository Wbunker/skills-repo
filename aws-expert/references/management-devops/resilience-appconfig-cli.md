# Resilience & AppConfig — CLI Reference

For service concepts, see [resilience-appconfig-capabilities.md](resilience-appconfig-capabilities.md).

## AWS Infrastructure Composer

Infrastructure Composer does not have a dedicated AWS CLI service. It is a console-based and VS Code-based visual tool that reads and writes CloudFormation/SAM template files. Use the CloudFormation and SAM CLI for deploying the templates it generates.

```bash
# Deploy a SAM template produced by Infrastructure Composer
sam build
sam deploy --guided

# Deploy a CloudFormation template produced by Infrastructure Composer
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name my-app-stack \
  --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND

# Validate a generated template before deploying
aws cloudformation validate-template \
  --template-body file://template.yaml

# Sync local template changes to a deployed stack (SAM Sync for rapid iteration)
sam sync --stack-name my-app-stack --watch
```

---

## AWS Resilience Hub

```bash
# --- Applications ---
# Create an application in Resilience Hub
aws resiliencehub create-app \
  --name ecommerce-platform \
  --description "Primary e-commerce application" \
  --assessment-schedule DAILY

# List all applications
aws resiliencehub list-apps

# Describe a specific application
aws resiliencehub describe-app \
  --app-arn arn:aws:resiliencehub:us-east-1:123456789012:app/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Update application (e.g., attach a resiliency policy)
aws resiliencehub update-app \
  --app-arn arn:aws:resiliencehub:us-east-1:123456789012:app/APP-UUID \
  --policy-arn arn:aws:resiliencehub:us-east-1:123456789012:resiliency-policy/POLICY-UUID

# Delete an application
aws resiliencehub delete-app \
  --app-arn arn:aws:resiliencehub:us-east-1:123456789012:app/APP-UUID \
  --force-delete

# --- Resource Import ---
# Import resources from CloudFormation stacks into a draft app version
aws resiliencehub import-resources-to-draft-app-version \
  --app-arn arn:aws:resiliencehub:us-east-1:123456789012:app/APP-UUID \
  --source-arns \
    arn:aws:cloudformation:us-east-1:123456789012:stack/api-stack/STACK-UUID \
    arn:aws:cloudformation:us-east-1:123456789012:stack/db-stack/STACK-UUID

# Resolve resources in the draft app version (discovers all resource ARNs)
aws resiliencehub resolve-app-version-resources \
  --app-arn arn:aws:resiliencehub:us-east-1:123456789012:app/APP-UUID \
  --app-version draft

# List resources in a specific app version
aws resiliencehub list-app-version-resources \
  --app-arn arn:aws:resiliencehub:us-east-1:123456789012:app/APP-UUID \
  --app-version draft

# List unsupported resources (not tracked by Resilience Hub)
aws resiliencehub list-unsupported-app-version-resources \
  --app-arn arn:aws:resiliencehub:us-east-1:123456789012:app/APP-UUID \
  --app-version draft

# Publish the draft version (makes it the new live version)
aws resiliencehub publish-app-version \
  --app-arn arn:aws:resiliencehub:us-east-1:123456789012:app/APP-UUID

# List all versions of an application
aws resiliencehub list-app-versions \
  --app-arn arn:aws:resiliencehub:us-east-1:123456789012:app/APP-UUID

# --- Resiliency Policies ---
# List suggested policies from AWS
aws resiliencehub list-suggested-resiliency-policies

# Create a resiliency policy with RTO/RPO targets per disruption type
aws resiliencehub create-resiliency-policy \
  --policy-name "Tier1-MissionCritical" \
  --tier MissionCritical \
  --policy '{
    "AZ": {"rtoInSecs": 3600, "rpoInSecs": 3600},
    "Hardware": {"rtoInSecs": 3600, "rpoInSecs": 3600},
    "Software": {"rtoInSecs": 3600, "rpoInSecs": 3600},
    "Region": {"rtoInSecs": 86400, "rpoInSecs": 86400}
  }'

# Create a less strict policy for non-critical workloads
aws resiliencehub create-resiliency-policy \
  --policy-name "Tier3-Standard" \
  --tier NonCritical \
  --policy '{
    "AZ": {"rtoInSecs": 14400, "rpoInSecs": 14400},
    "Hardware": {"rtoInSecs": 14400, "rpoInSecs": 14400},
    "Software": {"rtoInSecs": 14400, "rpoInSecs": 14400},
    "Region": {"rtoInSecs": 259200, "rpoInSecs": 259200}
  }'

# List all policies
aws resiliencehub list-resiliency-policies

# Describe a policy
aws resiliencehub describe-resiliency-policy \
  --policy-arn arn:aws:resiliencehub:us-east-1:123456789012:resiliency-policy/POLICY-UUID

# --- Assessments ---
# Start a resiliency assessment
aws resiliencehub start-app-assessment \
  --app-arn arn:aws:resiliencehub:us-east-1:123456789012:app/APP-UUID \
  --app-version release \
  --assessment-name "2026-03-14-weekly-assessment"

# Describe an assessment (check status and results)
aws resiliencehub describe-app-assessment \
  --assessment-arn arn:aws:resiliencehub:us-east-1:123456789012:app-assessment/APP-UUID/ASSESSMENT-UUID

# List all assessments for an application
aws resiliencehub list-app-assessments \
  --app-arn arn:aws:resiliencehub:us-east-1:123456789012:app/APP-UUID

# Check for resource drift since last assessment
aws resiliencehub list-app-assessment-resource-drifts \
  --assessment-arn arn:aws:resiliencehub:us-east-1:123456789012:app-assessment/APP-UUID/ASSESSMENT-UUID

# --- Recommendations ---
# List alarm recommendations (CloudWatch alarms to add)
aws resiliencehub list-alarm-recommendations \
  --assessment-arn arn:aws:resiliencehub:us-east-1:123456789012:app-assessment/APP-UUID/ASSESSMENT-UUID

# List SOP recommendations (SSM runbooks to prepare)
aws resiliencehub list-sop-recommendations \
  --assessment-arn arn:aws:resiliencehub:us-east-1:123456789012:app-assessment/APP-UUID/ASSESSMENT-UUID

# List FIS test recommendations (chaos experiments to run)
aws resiliencehub list-test-recommendations \
  --assessment-arn arn:aws:resiliencehub:us-east-1:123456789012:app-assessment/APP-UUID/ASSESSMENT-UUID

# Create a CloudFormation recommendation template (auto-generates alarms/SOPs as IaC)
aws resiliencehub create-recommendation-template \
  --assessment-arn arn:aws:resiliencehub:us-east-1:123456789012:app-assessment/APP-UUID/ASSESSMENT-UUID \
  --name "ecommerce-alarms-sops" \
  --bucket-name my-resiliencehub-bucket \
  --recommendation-types Alarm Sop TestRecommendation

# Update recommendation status (track implementation)
aws resiliencehub batch-update-recommendation-status \
  --assessment-arn arn:aws:resiliencehub:us-east-1:123456789012:app-assessment/APP-UUID/ASSESSMENT-UUID \
  --request-entries '[{
    "referenceId": "alarm-rec-001",
    "excluded": false
  }]'

# --- AppComponents ---
# List AppComponents for a version
aws resiliencehub list-app-version-app-components \
  --app-arn arn:aws:resiliencehub:us-east-1:123456789012:app/APP-UUID \
  --app-version draft

# Add a custom AppComponent to group resources logically
aws resiliencehub create-app-version-app-component \
  --app-arn arn:aws:resiliencehub:us-east-1:123456789012:app/APP-UUID \
  --name "payment-service" \
  --type "AWS::ResilienceHub::ComputeAppComponent"
```

---

## AWS AppConfig

```bash
# --- Applications ---
# Create an application
aws appconfig create-application \
  --name my-service \
  --description "My microservice configuration"

# List applications
aws appconfig list-applications

# Get application details
aws appconfig get-application \
  --application-id APPLICATION-ID

# --- Environments ---
# Create an environment with a CloudWatch alarm monitor
aws appconfig create-environment \
  --application-id APPLICATION-ID \
  --name production \
  --monitors '[{
    "AlarmArn": "arn:aws:cloudwatch:us-east-1:123456789012:alarm:ErrorRateHigh",
    "AlarmRoleArn": "arn:aws:iam::123456789012:role/AppConfigMonitorRole"
  }]'

# List environments for an application
aws appconfig list-environments \
  --application-id APPLICATION-ID

# --- Configuration Profiles ---
# Create a feature flag configuration profile (hosted in AppConfig)
aws appconfig create-configuration-profile \
  --application-id APPLICATION-ID \
  --name feature-flags \
  --location-uri hosted \
  --type AWS.AppConfig.FeatureFlags

# Create a freeform profile sourced from SSM Parameter Store
aws appconfig create-configuration-profile \
  --application-id APPLICATION-ID \
  --name app-settings \
  --location-uri "ssm-parameter:///myapp/production/settings" \
  --retrieval-role-arn arn:aws:iam::123456789012:role/AppConfigRetrievalRole

# Create a freeform profile with a JSON Schema validator
aws appconfig create-configuration-profile \
  --application-id APPLICATION-ID \
  --name throttle-config \
  --location-uri hosted \
  --type AWS.Freeform \
  --validators '[{
    "Type": "JSON_SCHEMA",
    "Content": "{\"$schema\":\"http://json-schema.org/draft-07/schema\",\"type\":\"object\",\"properties\":{\"maxRPS\":{\"type\":\"number\"}},\"required\":[\"maxRPS\"]}"
  }]'

# List configuration profiles
aws appconfig list-configuration-profiles \
  --application-id APPLICATION-ID

# --- Hosted Configuration Versions ---
# Create a hosted configuration version (the actual config data)
aws appconfig create-hosted-configuration-version \
  --application-id APPLICATION-ID \
  --configuration-profile-id CONFIG-PROFILE-ID \
  --content '{"enableNewCheckout":{"enabled":false,"_createdAt":"2026-03-14T00:00:00Z","_updatedAt":"2026-03-14T00:00:00Z"}}'  \
  --content-type application/json

# List hosted configuration versions
aws appconfig list-hosted-configuration-versions \
  --application-id APPLICATION-ID \
  --configuration-profile-id CONFIG-PROFILE-ID

# Get a specific version's content
aws appconfig get-hosted-configuration-version \
  --application-id APPLICATION-ID \
  --configuration-profile-id CONFIG-PROFILE-ID \
  --version-number 3 \
  /tmp/config-v3.json  # writes binary output to file; inspect with cat

# Validate a configuration version before deploying
aws appconfig validate-configuration \
  --application-id APPLICATION-ID \
  --configuration-profile-id CONFIG-PROFILE-ID \
  --configuration-version 3

# --- Deployment Strategies ---
# Create a custom deployment strategy
aws appconfig create-deployment-strategy \
  --name "Linear10PercentEvery5Minutes" \
  --deployment-duration-in-minutes 50 \
  --growth-factor 10 \
  --growth-type LINEAR \
  --final-bake-time-in-minutes 10 \
  --replicate-to NONE

# List all deployment strategies (including AWS-managed ones)
aws appconfig list-deployment-strategies

# List AWS-managed strategies only
aws appconfig list-deployment-strategies \
  --query 'Items[?Id==`AppConfig.AllAtOnce` || Id==`AppConfig.Canary10Percent20Minutes`]'

# --- Deployments ---
# Deploy a configuration version to an environment
aws appconfig start-deployment \
  --application-id APPLICATION-ID \
  --environment-id ENVIRONMENT-ID \
  --deployment-strategy-id STRATEGY-ID \
  --configuration-profile-id CONFIG-PROFILE-ID \
  --configuration-version 3 \
  --description "Enable new checkout for 10% canary"

# Get deployment status
aws appconfig get-deployment \
  --application-id APPLICATION-ID \
  --environment-id ENVIRONMENT-ID \
  --deployment-number 5

# List deployments for an environment
aws appconfig list-deployments \
  --application-id APPLICATION-ID \
  --environment-id ENVIRONMENT-ID

# Stop (roll back) an active deployment
aws appconfig stop-deployment \
  --application-id APPLICATION-ID \
  --environment-id ENVIRONMENT-ID \
  --deployment-number 5

# --- Extensions ---
# Create an extension that calls Lambda on deployment complete
aws appconfig create-extension \
  --name notify-slack-on-deploy \
  --actions '{
    "ON_DEPLOYMENT_COMPLETE": [{
      "Name": "SlackNotify",
      "RoleArn": "arn:aws:iam::123456789012:role/AppConfigExtensionRole",
      "Uri": "arn:aws:lambda:us-east-1:123456789012:function:slack-notify"
    }],
    "ON_DEPLOYMENT_ROLLED_BACK": [{
      "Name": "SlackRollbackAlert",
      "RoleArn": "arn:aws:iam::123456789012:role/AppConfigExtensionRole",
      "Uri": "arn:aws:lambda:us-east-1:123456789012:function:slack-notify"
    }]
  }'

# Associate an extension with an application
aws appconfig create-extension-association \
  --extension-identifier notify-slack-on-deploy \
  --resource-identifier arn:aws:appconfig:us-east-1:123456789012:application/APPLICATION-ID

# --- AppConfig Agent (Lambda Extension) ---
# The AppConfig Agent Lambda layer ARN format (per region):
# arn:aws:lambda:<region>:027255383542:layer:AWS-AppConfig-Extension:<version>
# Retrieve config from running application via the agent:
# curl http://localhost:2772/applications/my-service/environments/production/configurations/feature-flags

# --- Account Settings ---
# View account-level settings (e.g., deletion protection)
aws appconfig get-account-settings

# Enable deletion protection for deployments
aws appconfig update-account-settings \
  --deletion-protection-check APPLY
```
