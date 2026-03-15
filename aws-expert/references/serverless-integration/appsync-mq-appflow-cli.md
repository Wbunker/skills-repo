# AWS AppSync, MQ & AppFlow — CLI Reference

For service concepts, see [appsync-mq-appflow-capabilities.md](appsync-mq-appflow-capabilities.md).

## AppSync — appsync

```bash
# --- Create GraphQL API ---
aws appsync create-graphql-api \
  --name MyGraphQLAPI \
  --authentication-type API_KEY

# Multiple auth modes
aws appsync create-graphql-api \
  --name MyGraphQLAPI \
  --authentication-type AMAZON_COGNITO_USER_POOLS \
  --user-pool-config '{
    "userPoolId":"us-east-1_abc123",
    "awsRegion":"us-east-1",
    "defaultAction":"ALLOW"
  }' \
  --additional-authentication-providers '[{
    "authenticationType":"API_KEY"
  },{
    "authenticationType":"AWS_IAM"
  }]'

aws appsync list-graphql-apis
aws appsync get-graphql-api --api-id API_ID
aws appsync update-graphql-api --api-id API_ID --name NewName
aws appsync delete-graphql-api --api-id API_ID

# --- Schema ---
aws appsync start-schema-creation \
  --api-id API_ID \
  --definition fileb://schema.graphql

aws appsync get-schema-creation-status --api-id API_ID
aws appsync get-introspection-schema --api-id API_ID --format JSON schema-output.json

# --- Data sources ---
# DynamoDB data source
aws appsync create-data-source \
  --api-id API_ID \
  --name OrdersTable \
  --type AMAZON_DYNAMODB \
  --service-role-arn arn:aws:iam::123456789012:role/appsync-role \
  --dynamodb-config tableName=Orders,awsRegion=us-east-1

# Lambda data source
aws appsync create-data-source \
  --api-id API_ID \
  --name OrderLambda \
  --type AWS_LAMBDA \
  --service-role-arn arn:aws:iam::123456789012:role/appsync-role \
  --lambda-config lambdaFunctionArn=arn:aws:lambda:us-east-1:123456789012:function:orders

# HTTP data source
aws appsync create-data-source \
  --api-id API_ID \
  --name ExternalAPI \
  --type HTTP \
  --http-config endpoint=https://api.example.com

aws appsync list-data-sources --api-id API_ID

# --- Resolvers ---
# Unit resolver (JavaScript)
aws appsync create-resolver \
  --api-id API_ID \
  --type-name Query \
  --field-name getOrder \
  --data-source-name OrdersTable \
  --runtime name=APPSYNC_JS,runtimeVersion=1.0.0 \
  --code fileb://resolvers/getOrder.js

# Pipeline resolver
aws appsync create-resolver \
  --api-id API_ID \
  --type-name Mutation \
  --field-name createOrder \
  --kind PIPELINE \
  --pipeline-config functions=FUNCTION_ID_1,FUNCTION_ID_2 \
  --runtime name=APPSYNC_JS,runtimeVersion=1.0.0 \
  --code fileb://resolvers/createOrder.js

aws appsync list-resolvers --api-id API_ID --type-name Query

# --- Pipeline functions ---
aws appsync create-function \
  --api-id API_ID \
  --name ValidateOrder \
  --data-source-name OrdersTable \
  --runtime name=APPSYNC_JS,runtimeVersion=1.0.0 \
  --code fileb://functions/validateOrder.js

aws appsync list-functions --api-id API_ID

# --- Types ---
aws appsync create-type \
  --api-id API_ID \
  --definition 'type Order { id: ID! status: String! }' \
  --format SDL

aws appsync list-types --api-id API_ID --format SDL

# --- API keys ---
aws appsync create-api-key \
  --api-id API_ID \
  --description "Development key" \
  --expires 1767139200  # Unix timestamp

aws appsync list-api-keys --api-id API_ID
aws appsync update-api-key --api-id API_ID --id KEY_ID --expires 1798675200

# --- Caching ---
aws appsync create-api-cache \
  --api-id API_ID \
  --ttl 300 \
  --api-caching-behavior FULL_REQUEST_CACHING \
  --type R4_LARGE

aws appsync flush-api-cache --api-id API_ID
aws appsync delete-api-cache --api-id API_ID

# --- Merged APIs ---
aws appsync associate-merged-graphql-api \
  --source-api-identifier SOURCE_API_ID \
  --merged-api-identifier MERGED_API_ID \
  --source-api-association-config mergeType=MANUAL_MERGE

aws appsync start-schema-merge \
  --association-id ASSOC_ID \
  --merged-api-identifier MERGED_API_ID

aws appsync evaluate-code \
  --runtime name=APPSYNC_JS,runtimeVersion=1.0.0 \
  --code fileb://resolver.js \
  --context '{"arguments":{"id":"123"},"source":null}'
```

---

## Amazon MQ — mq

```bash
# --- Brokers ---
# Create ActiveMQ broker
aws mq create-broker \
  --broker-name MyActiveMQBroker \
  --broker-instance-type mq.m5.large \
  --engine-type ACTIVEMQ \
  --engine-version "5.17.6" \
  --deployment-mode ACTIVE_STANDBY_MULTI_AZ \
  --publicly-accessible false \
  --subnet-ids subnet-abc123 subnet-def456 \
  --security-groups sg-abc123 \
  --users '[{
    "Username":"admin",
    "Password":"SecureP@ssw0rd!",
    "ConsoleAccess":true,
    "Groups":["admins"]
  }]'

# Create RabbitMQ broker
aws mq create-broker \
  --broker-name MyRabbitMQBroker \
  --broker-instance-type mq.m5.large \
  --engine-type RABBITMQ \
  --engine-version "3.13" \
  --deployment-mode CLUSTER_MULTI_AZ \
  --publicly-accessible false \
  --subnet-ids subnet-abc123 subnet-def456 subnet-ghi789 \
  --security-groups sg-abc123 \
  --users '[{"Username":"admin","Password":"SecureP@ssw0rd!"}]'

aws mq list-brokers
aws mq describe-broker --broker-id BROKER_ID
aws mq reboot-broker --broker-id BROKER_ID

aws mq update-broker \
  --broker-id BROKER_ID \
  --auto-minor-version-upgrade

aws mq delete-broker --broker-id BROKER_ID

# --- Configurations ---
aws mq create-configuration \
  --name MyActiveMQConfig \
  --engine-type ACTIVEMQ \
  --engine-version "5.17.6"

aws mq list-configurations
aws mq describe-configuration --configuration-id CONFIG_ID
aws mq describe-configuration-revision --configuration-id CONFIG_ID --configuration-revision 1
aws mq list-configuration-revisions --configuration-id CONFIG_ID

aws mq update-configuration \
  --configuration-id CONFIG_ID \
  --data "$(base64 < activemq.xml)" \
  --description "Updated queue config"

# Apply configuration to broker
aws mq update-broker \
  --broker-id BROKER_ID \
  --configuration id=CONFIG_ID,revision=2

# --- Users ---
aws mq create-user \
  --broker-id BROKER_ID \
  --username newuser \
  --password "SecureP@ssw0rd!" \
  --groups readers

aws mq list-users --broker-id BROKER_ID
aws mq describe-user --broker-id BROKER_ID --username newuser
aws mq update-user --broker-id BROKER_ID --username newuser --password "NewP@ssw0rd!"
aws mq delete-user --broker-id BROKER_ID --username newuser

# --- Instance options ---
aws mq describe-broker-instance-options --engine-type ACTIVEMQ --deployment-mode ACTIVE_STANDBY_MULTI_AZ
aws mq describe-broker-engine-types --engine-type RABBITMQ
```

---

## AppFlow — appflow

```bash
# --- Connector profiles ---
# Salesforce connector profile
aws appflow create-connector-profile \
  --connector-profile-name SalesforceProfile \
  --connector-type Salesforce \
  --connection-mode Public \
  --connector-profile-config '{
    "connectorProfileProperties": {
      "Salesforce": {
        "instanceUrl": "https://yourorg.my.salesforce.com",
        "isSandboxEnvironment": false
      }
    },
    "connectorProfileCredentials": {
      "Salesforce": {
        "accessToken": "ACCESS_TOKEN",
        "refreshToken": "REFRESH_TOKEN",
        "oAuthRequest": {"authCode": "AUTH_CODE", "redirectUri": "https://redirect.uri"}
      }
    }
  }'

aws appflow describe-connector-profiles
aws appflow delete-connector-profile --connector-profile-name SalesforceProfile

# --- Flows ---
# Scheduled flow: Salesforce → S3
aws appflow create-flow \
  --flow-name SalesforceToS3 \
  --description "Daily sync of Salesforce accounts to S3" \
  --source-flow-config '{
    "connectorType": "Salesforce",
    "connectorProfileName": "SalesforceProfile",
    "sourceConnectorProperties": {
      "Salesforce": {
        "object": "Account",
        "enableDynamicFieldUpdate": false
      }
    }
  }' \
  --destination-flow-config-list '[{
    "connectorType": "S3",
    "destinationConnectorProperties": {
      "S3": {
        "bucketName": "my-data-lake",
        "bucketPrefix": "salesforce/accounts",
        "s3OutputFormatConfig": {
          "fileType": "PARQUET",
          "aggregationConfig": {"aggregationType": "SingleFile"}
        }
      }
    }
  }]' \
  --trigger-config '{
    "triggerType": "Scheduled",
    "triggerProperties": {
      "Scheduled": {
        "scheduleExpression": "rate(1day)",
        "dataPullMode": "Incremental",
        "scheduleStartTime": 1735689600.0
      }
    }
  }' \
  --tasks '[{
    "sourceFields": ["Id","Name","Industry","AnnualRevenue"],
    "taskType": "Filter",
    "connectorOperator": {"Salesforce": "PROJECTION"}
  },{
    "sourceFields": ["Id"],
    "taskType": "Map",
    "destinationField": "account_id",
    "connectorOperator": {"Salesforce": "NO_OP"}
  }]'

aws appflow describe-flow --flow-name SalesforceToS3
aws appflow list-flows
aws appflow start-flow --flow-name SalesforceToS3
aws appflow stop-flow --flow-name SalesforceToS3
aws appflow describe-flow-execution-records --flow-name SalesforceToS3

aws appflow update-flow \
  --flow-name SalesforceToS3 \
  --trigger-config '{"triggerType":"OnDemand"}' \
  --source-flow-config '...' \
  --destination-flow-config-list '[...]' \
  --tasks '[...]'

aws appflow delete-flow --flow-name SalesforceToS3

# --- Connectors ---
aws appflow describe-connectors
aws appflow describe-connector --connector-type Salesforce
aws appflow list-connector-entities \
  --connector-profile-name SalesforceProfile \
  --connector-type Salesforce
aws appflow describe-connector-entity \
  --entity-name Account \
  --connector-type Salesforce \
  --connector-profile-name SalesforceProfile
```
