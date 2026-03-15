# AWS IoT Core & Device Management — CLI Reference

For service concepts, see [iot-core-capabilities.md](iot-core-capabilities.md).

---

## Things and Thing Types

```bash
# --- Thing CRUD ---
aws iot create-thing \
  --thing-name MyDevice001 \
  --attribute-payload '{"attributes": {"location": "us-east", "model": "v2"}}'

aws iot describe-thing --thing-name MyDevice001

aws iot update-thing \
  --thing-name MyDevice001 \
  --attribute-payload '{"attributes": {"firmware": "2.1.0"}, "merge": true}'

aws iot list-things
aws iot list-things --attribute-name location --attribute-value us-east
aws iot list-things --thing-type-name Thermostat

aws iot delete-thing --thing-name MyDevice001

# --- Thing Types ---
aws iot create-thing-type \
  --thing-type-name Thermostat \
  --thing-type-properties '{
    "thingTypeDescription": "Smart thermostat device",
    "searchableAttributes": ["manufacturer", "model", "firmwareVersion"]
  }'

aws iot describe-thing-type --thing-type-name Thermostat
aws iot list-thing-types

# Deprecate a thing type (required before deletion, must wait 5 minutes)
aws iot deprecate-thing-type --thing-type-name OldThingType
aws iot delete-thing-type --thing-type-name OldThingType
```

---

## Thing Groups

```bash
# --- Static groups ---
aws iot create-thing-group \
  --thing-group-name FactoryFloor \
  --thing-group-properties '{
    "thingGroupDescription": "All devices on the factory floor",
    "attributePayload": {"attributes": {"plant": "Atlanta"}}
  }'

# Nested group (child of parent)
aws iot create-thing-group \
  --thing-group-name Line1 \
  --parent-group-name FactoryFloor

aws iot describe-thing-group --thing-group-name FactoryFloor
aws iot list-thing-groups
aws iot list-thing-groups --parent-group FactoryFloor

aws iot add-thing-to-thing-group \
  --thing-group-name FactoryFloor \
  --thing-name MyDevice001

aws iot remove-thing-from-thing-group \
  --thing-group-name FactoryFloor \
  --thing-name MyDevice001

aws iot list-things-in-thing-group --thing-group-name FactoryFloor
aws iot list-thing-groups-for-thing --thing-name MyDevice001

aws iot delete-thing-group --thing-group-name Line1

# --- Dynamic groups ---
aws iot create-dynamic-thing-group \
  --thing-group-name HighTempDevices \
  --query-string 'shadow.reported.temperature > 85'

aws iot update-dynamic-thing-group \
  --thing-group-name HighTempDevices \
  --thing-group-properties '{"thingGroupDescription": "Devices reporting high temperature"}' \
  --query-version '2017-09-30' \
  --query-string 'shadow.reported.temperature > 90'

aws iot delete-dynamic-thing-group --thing-group-name HighTempDevices
```

---

## Certificates

```bash
# --- Create and activate a certificate ---
# Generate a new key pair and certificate
aws iot create-keys-and-certificate \
  --set-as-active \
  --certificate-pem-outfile certificate.pem \
  --public-key-outfile public.key \
  --private-key-outfile private.key

# Register a CSR-based certificate
aws iot create-certificate-from-csr \
  --certificate-signing-request file://device.csr \
  --set-as-active

# Register an externally generated certificate (without CA registration)
aws iot register-certificate-without-ca \
  --certificate-pem file://device-cert.pem \
  --status ACTIVE

# --- Manage certificate lifecycle ---
aws iot describe-certificate --certificate-id <cert-id>
aws iot list-certificates
aws iot list-certificates-by-ca --ca-certificate-id <ca-cert-id>

aws iot update-certificate \
  --certificate-id <cert-id> \
  --new-status INACTIVE   # ACTIVE | INACTIVE | REVOKED | PENDING_TRANSFER | PENDING_ACTIVATION

aws iot delete-certificate --certificate-id <cert-id>

# --- Attach/detach certificate to thing ---
aws iot attach-thing-principal \
  --thing-name MyDevice001 \
  --principal arn:aws:iot:us-east-1:123456789012:cert/<cert-id>

aws iot detach-thing-principal \
  --thing-name MyDevice001 \
  --principal arn:aws:iot:us-east-1:123456789012:cert/<cert-id>

aws iot list-thing-principals --thing-name MyDevice001
aws iot list-principal-things --principal arn:aws:iot:us-east-1:123456789012:cert/<cert-id>

# --- CA Certificates ---
# Get registration code for CA cert verification
aws iot get-registration-code

# Register CA certificate
aws iot register-ca-certificate \
  --ca-certificate file://root-ca.pem \
  --verification-certificate file://verification.pem \
  --set-as-active \
  --allow-auto-registration

aws iot describe-ca-certificate --certificate-id <ca-cert-id>
aws iot list-ca-certificates

aws iot update-ca-certificate \
  --certificate-id <ca-cert-id> \
  --new-status INACTIVE

aws iot delete-ca-certificate --certificate-id <ca-cert-id>
```

---

## Policies

```bash
# --- Create and manage policies ---
aws iot create-policy \
  --policy-name DevicePolicy \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": "iot:Connect",
        "Resource": "arn:aws:iot:us-east-1:123456789012:client/${iot:ClientId}"
      },
      {
        "Effect": "Allow",
        "Action": ["iot:Publish", "iot:Subscribe", "iot:Receive"],
        "Resource": "arn:aws:iot:us-east-1:123456789012:topic/devices/${iot:ClientId}/*"
      },
      {
        "Effect": "Allow",
        "Action": ["iot:GetThingShadow", "iot:UpdateThingShadow", "iot:DeleteThingShadow"],
        "Resource": "arn:aws:iot:us-east-1:123456789012:thing/${iot:ClientId}"
      }
    ]
  }'

aws iot get-policy --policy-name DevicePolicy
aws iot list-policies
aws iot list-policy-versions --policy-name DevicePolicy

aws iot create-policy-version \
  --policy-name DevicePolicy \
  --policy-document file://updated-policy.json \
  --set-as-default

aws iot set-default-policy-version \
  --policy-name DevicePolicy \
  --policy-version-id 3

aws iot delete-policy-version \
  --policy-name DevicePolicy \
  --policy-version-id 2

aws iot delete-policy --policy-name DevicePolicy

# --- Attach/detach policy ---
aws iot attach-policy \
  --policy-name DevicePolicy \
  --target arn:aws:iot:us-east-1:123456789012:cert/<cert-id>

# Attach policy to a thing group
aws iot attach-policy \
  --policy-name DevicePolicy \
  --target arn:aws:iot:us-east-1:123456789012:thinggroup/FactoryFloor

aws iot detach-policy \
  --policy-name DevicePolicy \
  --target arn:aws:iot:us-east-1:123456789012:cert/<cert-id>

aws iot list-attached-policies --target arn:aws:iot:us-east-1:123456789012:cert/<cert-id>
aws iot list-principal-policies --principal arn:aws:iot:us-east-1:123456789012:cert/<cert-id>
```

---

## Topic Rules (Rules Engine)

```bash
# --- Create a topic rule ---
aws iot create-topic-rule \
  --rule-name HighTempAlert \
  --topic-rule-payload '{
    "sql": "SELECT *, clientid() AS deviceId, timestamp() AS eventTime FROM '\''sensors/+/temperature'\'' WHERE temperature > 85",
    "description": "Route high temperature readings to SNS",
    "actions": [
      {
        "sns": {
          "targetArn": "arn:aws:sns:us-east-1:123456789012:HighTempAlerts",
          "roleArn": "arn:aws:iam::123456789012:role/IoTRulesRole",
          "messageFormat": "JSON"
        }
      },
      {
        "dynamoDBv2": {
          "roleArn": "arn:aws:iam::123456789012:role/IoTRulesRole",
          "putItem": {
            "tableName": "TelemetryAlerts"
          }
        }
      }
    ],
    "errorAction": {
      "cloudwatchLogs": {
        "logGroupName": "/aws/iot/rule-errors",
        "roleArn": "arn:aws:iam::123456789012:role/IoTRulesRole"
      }
    },
    "ruleDisabled": false,
    "awsIotSqlVersion": "2016-03-23"
  }'

# --- Rule with S3 destination ---
aws iot create-topic-rule \
  --rule-name ArchiveTelemetry \
  --topic-rule-payload '{
    "sql": "SELECT * FROM '\''sensors/#'\''",
    "actions": [{
      "s3": {
        "roleArn": "arn:aws:iam::123456789012:role/IoTRulesRole",
        "bucketName": "my-iot-archive",
        "key": "${topic()}/${timestamp()}.json"
      }
    }],
    "ruleDisabled": false,
    "awsIotSqlVersion": "2016-03-23"
  }'

aws iot get-topic-rule --rule-name HighTempAlert
aws iot list-topic-rules
aws iot list-topic-rules --topic 'sensors/+/temperature'  # filter by topic pattern

aws iot replace-topic-rule \
  --rule-name HighTempAlert \
  --topic-rule-payload file://updated-rule.json

aws iot disable-topic-rule --rule-name HighTempAlert
aws iot enable-topic-rule --rule-name HighTempAlert
aws iot delete-topic-rule --rule-name HighTempAlert

# --- Topic rule destinations (for HTTP/VPC endpoints) ---
aws iot create-topic-rule-destination \
  --destination-configuration '{
    "httpUrlConfiguration": {
      "confirmationUrl": "https://myapi.example.com/iot-confirm"
    }
  }'

aws iot get-topic-rule-destination --arn arn:aws:iot:us-east-1:123456789012:ruledestination/http/...
aws iot list-topic-rule-destinations
aws iot update-topic-rule-destination --arn arn:... --status ENABLED
aws iot delete-topic-rule-destination --arn arn:...
```

---

## Device Shadow

```bash
# --- Classic (unnamed) shadow ---
# Get shadow
aws iot-data get-thing-shadow \
  --thing-name MyDevice001 \
  output.json

# Update shadow (desired state)
aws iot-data update-thing-shadow \
  --thing-name MyDevice001 \
  --payload '{"state": {"desired": {"color": "blue", "brightness": 90}}}' \
  output.json

# Delete shadow
aws iot-data delete-thing-shadow --thing-name MyDevice001

# --- Named shadows ---
aws iot-data get-thing-shadow \
  --thing-name MyDevice001 \
  --shadow-name thermostat \
  output.json

aws iot-data update-thing-shadow \
  --thing-name MyDevice001 \
  --shadow-name thermostat \
  --payload '{"state": {"desired": {"setpoint": 72}}}' \
  output.json

aws iot-data delete-thing-shadow \
  --thing-name MyDevice001 \
  --shadow-name thermostat

aws iot-data list-named-shadows-for-thing --thing-name MyDevice001

# --- Publish directly to MQTT topic ---
aws iot-data publish \
  --topic 'factory/line1/command' \
  --payload '{"action": "restart"}' \
  --qos 1
```

---

## Jobs (Remote Operations)

```bash
# --- Create a job ---
aws iot create-job \
  --job-id firmware-update-2024-001 \
  --targets arn:aws:iot:us-east-1:123456789012:thinggroup/FactoryFloor \
  --document-source s3://my-iot-jobs/firmware-update-doc.json \
  --description "Update firmware to v2.1.0" \
  --target-selection SNAPSHOT \
  --job-executions-rollout-config '{
    "maximumPerMinute": 100,
    "exponentialRate": {
      "baseRatePerMinute": 20,
      "incrementFactor": 1.5,
      "rateIncreaseCriteria": {"numberOfSucceededThings": 50}
    }
  }' \
  --abort-config '{
    "criteriaList": [{
      "action": "CANCEL",
      "failureType": "ALL",
      "minNumberOfExecutedThings": 10,
      "thresholdPercentage": 20.0
    }]
  }' \
  --timeout-config '{"inProgressTimeoutInMinutes": 60}'

# Continuous job targeting a dynamic group
aws iot create-job \
  --job-id continuous-config-push \
  --targets arn:aws:iot:us-east-1:123456789012:thinggroup/AllDevices \
  --document '{"operation": "updateConfig", "configUrl": "https://example.com/config.json"}' \
  --target-selection CONTINUOUS

# --- Manage jobs ---
aws iot describe-job --job-id firmware-update-2024-001
aws iot list-jobs
aws iot list-jobs --status IN_PROGRESS
aws iot list-jobs --target-selection CONTINUOUS

aws iot cancel-job \
  --job-id firmware-update-2024-001 \
  --force    # force-cancel even IN_PROGRESS executions

aws iot delete-job --job-id firmware-update-2024-001 --force

# --- Job executions ---
aws iot list-job-executions-for-job \
  --job-id firmware-update-2024-001 \
  --status FAILED

aws iot list-job-executions-for-thing \
  --thing-name MyDevice001

aws iot describe-job-execution \
  --job-id firmware-update-2024-001 \
  --thing-name MyDevice001

aws iot cancel-job-execution \
  --job-id firmware-update-2024-001 \
  --thing-name MyDevice001

# --- Job templates ---
aws iot create-job-template \
  --job-template-id standard-firmware-update \
  --document-source s3://my-iot-jobs/standard-update-doc.json \
  --description "Standard firmware update template" \
  --timeout-config '{"inProgressTimeoutInMinutes": 60}'

aws iot list-job-templates
aws iot describe-job-template --job-template-id standard-firmware-update
aws iot delete-job-template --job-template-id standard-firmware-update
```

---

## Fleet Indexing

```bash
# --- Enable fleet indexing ---
aws iot update-indexing-configuration \
  --thing-indexing-configuration '{
    "thingIndexingMode": "REGISTRY_AND_SHADOW",
    "thingConnectivityIndexingMode": "STATUS",
    "deviceDefenderIndexingMode": "VIOLATIONS",
    "namedShadowIndexingMode": "ON",
    "managedFields": [],
    "customFields": [
      {"name": "shadow.reported.temperature", "type": "Number"},
      {"name": "attributes.location", "type": "String"}
    ]
  }' \
  --thing-group-indexing-configuration '{"thingGroupIndexingMode": "ON"}'

aws iot get-indexing-configuration

# --- Search things ---
aws iot search-index \
  --query-string 'connectivity.connected:true'

aws iot search-index \
  --query-string 'attributes.location:"us-east" AND shadow.reported.temperature:[70 TO *]' \
  --max-results 50

aws iot search-index \
  --query-string 'thingGroupNames:FactoryFloor AND connectivity.connected:false'

# Aggregation queries
aws iot get-statistics \
  --query-string 'attributes.model:"v2"' \
  --aggregation-field 'shadow.reported.temperature'

aws iot get-percentiles \
  --query-string 'connectivity.connected:true' \
  --aggregation-field 'shadow.reported.batteryLevel' \
  --percents 50 90 99

aws iot get-cardinality \
  --query-string 'connectivity.connected:true' \
  --aggregation-field 'attributes.location'
```

---

## Provisioning

```bash
# --- Fleet Provisioning templates ---
aws iot create-provisioning-template \
  --template-name DeviceFleetTemplate \
  --provisioning-role-arn arn:aws:iam::123456789012:role/IoTProvisioningRole \
  --template-body file://provisioning-template.json \
  --enabled

aws iot describe-provisioning-template --template-name DeviceFleetTemplate
aws iot list-provisioning-templates

aws iot update-provisioning-template \
  --template-name DeviceFleetTemplate \
  --enabled \
  --pre-provisioning-hook '{
    "targetArn": "arn:aws:lambda:us-east-1:123456789012:function:PreProvisioningHook",
    "payloadVersion": "2020-04-01"
  }'

aws iot create-provisioning-claim \
  --template-name DeviceFleetTemplate
  # Returns temporary claim certificate for the device to use

aws iot delete-provisioning-template --template-name DeviceFleetTemplate

# --- Bulk registration ---
aws iot start-thing-registration-task \
  --template-body file://bulk-reg-template.json \
  --input-file-bucket my-bulk-registration-bucket \
  --input-file-key devices.csv \
  --role-arn arn:aws:iam::123456789012:role/IoTBulkRegRole

aws iot describe-thing-registration-task --task-id <task-id>
aws iot list-thing-registration-tasks --status InProgress
aws iot list-thing-registration-task-reports --task-id <task-id> --report-type RESULTS

aws iot stop-thing-registration-task --task-id <task-id>
```

---

## Secure Tunneling

```bash
# --- Open a tunnel ---
aws iotsecuretunneling open-tunnel \
  --description "SSH access to factory device" \
  --destination-config '{
    "thingName": "MyDevice001",
    "services": ["SSH"]
  }' \
  --timeout-config '{"maxLifetimeTimeoutMinutes": 120}'

aws iotsecuretunneling describe-tunnel --tunnel-id <tunnel-id>
aws iotsecuretunneling list-tunnels
aws iotsecuretunneling list-tunnels --thing-name MyDevice001

# Rotate access tokens (invalidate existing tokens and issue new ones)
aws iotsecuretunneling rotate-tunnel-access-token \
  --tunnel-id <tunnel-id> \
  --client-mode SOURCE   # SOURCE | DESTINATION | ALL

aws iotsecuretunneling close-tunnel --tunnel-id <tunnel-id>
```

---

## Endpoint and Custom Domain

```bash
# --- Get account endpoint ---
aws iot describe-endpoint --endpoint-type iot:Data-ATS
# Returns: <prefix>.iot.<region>.amazonaws.com

aws iot describe-endpoint --endpoint-type iot:CredentialProvider
aws iot describe-endpoint --endpoint-type iot:Jobs

# --- Custom domains ---
aws iot create-domain-configuration \
  --domain-configuration-name MyCustomDomain \
  --domain-name iot.example.com \
  --server-certificate-arns arn:aws:acm:us-east-1:123456789012:certificate/<cert-id> \
  --service-type DATA

aws iot describe-domain-configuration --domain-configuration-name MyCustomDomain
aws iot list-domain-configurations

aws iot update-domain-configuration \
  --domain-configuration-name MyCustomDomain \
  --domain-configuration-status ENABLED \
  --authorizer-config '{
    "defaultAuthorizerName": "MyCustomAuthorizer",
    "allowAuthorizerOverride": true
  }'

aws iot delete-domain-configuration --domain-configuration-name MyCustomDomain

# --- Custom authorizers ---
aws iot create-authorizer \
  --authorizer-name MyJWTAuthorizer \
  --authorizer-function-arn arn:aws:lambda:us-east-1:123456789012:function:JWTAuthorizer \
  --signing-disabled \
  --token-key-name authorization \
  --status ACTIVE

aws iot describe-authorizer --authorizer-name MyJWTAuthorizer
aws iot list-authorizers
aws iot delete-authorizer --authorizer-name MyJWTAuthorizer
```
