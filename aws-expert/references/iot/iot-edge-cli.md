# AWS IoT Edge — CLI Reference

For service concepts, see [iot-edge-capabilities.md](iot-edge-capabilities.md).

---

## AWS IoT Greengrass v2 — `aws greengrassv2`

### Components

```bash
# --- Create a component version from a recipe ---
aws greengrassv2 create-component-version \
  --inline-recipe '{
    "RecipeFormatVersion": "2020-01-25",
    "ComponentName": "com.example.TempSensor",
    "ComponentVersion": "1.0.0",
    "ComponentDescription": "Reads temperature from sensor and publishes to IoT Core",
    "ComponentPublisher": "MyCompany",
    "ComponentDependencies": {
      "aws.greengrass.Nucleus": {"VersionRequirement": ">=2.0.0", "DependencyType": "SOFT"}
    },
    "Manifests": [{
      "Platform": {"os": "linux"},
      "Lifecycle": {
        "Run": "python3 {artifacts:path}/sensor.py"
      },
      "Artifacts": [
        {"URI": "s3://my-greengrass-components/temp-sensor/1.0.0/sensor.py", "Unarchive": "NONE"}
      ]
    }],
    "ComponentConfiguration": {
      "DefaultConfiguration": {
        "publishInterval": 5,
        "mqttTopic": "factory/sensors/temperature"
      }
    }
  }'

# Create from S3-hosted recipe
aws greengrassv2 create-component-version \
  --lambda-function '{
    "lambdaArn": "arn:aws:lambda:us-east-1:123456789012:function:ProcessSensorData:PROD",
    "componentName": "com.example.ProcessSensorData",
    "componentVersion": "1.0.0",
    "componentPlatforms": [{"name": "Linux x86_64", "attributes": {"os": "linux", "architecture": "x86_64"}}],
    "componentLambdaParameters": {
      "eventSources": [
        {"topic": "factory/sensors/#", "type": "IOT_CORE"}
      ],
      "maxQueueSize": 1000,
      "maxInstancesCount": 1,
      "maxIdleTimeInSeconds": 60,
      "timeoutInSeconds": 30,
      "statusTimeoutInSeconds": 60,
      "pinned": true,
      "inputPayloadEncodingType": "json",
      "execArgs": [],
      "environmentVariables": {"REGION": "us-east-1"}
    }
  }'

aws greengrassv2 describe-component \
  --arn arn:aws:greengrass:us-east-1:123456789012:components:com.example.TempSensor:versions:1.0.0

aws greengrassv2 list-components

# List public AWS-provided components
aws greengrassv2 list-components --scope PUBLIC

# List private (account-owned) components
aws greengrassv2 list-components --scope PRIVATE

aws greengrassv2 list-component-versions \
  --arn arn:aws:greengrass:us-east-1:123456789012:components:com.example.TempSensor

# Get component recipe (returned as base64 blob)
aws greengrassv2 get-component \
  --arn arn:aws:greengrass:us-east-1:123456789012:components:com.example.TempSensor:versions:1.0.0 \
  --recipe-output-format YAML

# Download component artifacts
aws greengrassv2 get-component-version-artifact \
  --arn arn:aws:greengrass:us-east-1:123456789012:components:com.example.TempSensor:versions:1.0.0 \
  --artifact-name sensor.py

aws greengrassv2 delete-component \
  --arn arn:aws:greengrass:us-east-1:123456789012:components:com.example.TempSensor:versions:1.0.0
```

---

### Deployments

```bash
# --- Create a deployment to a thing group ---
aws greengrassv2 create-deployment \
  --target-arn arn:aws:iot:us-east-1:123456789012:thinggroup/FactoryDevices \
  --deployment-name "Production Deployment v2.1" \
  --components '{
    "aws.greengrass.Nucleus": {
      "componentVersion": "2.12.0"
    },
    "aws.greengrass.StreamManager": {
      "componentVersion": "2.1.0"
    },
    "com.example.TempSensor": {
      "componentVersion": "1.0.0",
      "configurationUpdate": {
        "merge": "{\"publishInterval\": 10, \"mqttTopic\": \"factory/line1/temperature\"}"
      }
    },
    "com.example.AlertProcessor": {
      "componentVersion": "2.3.1",
      "configurationUpdate": {
        "reset": ["/thresholds"],
        "merge": "{\"thresholds\": {\"high\": 90, \"critical\": 100}}"
      },
      "runWith": {
        "posixUser": "ggc_user:ggc_group",
        "systemResourceLimits": {
          "memory": 67108864,
          "cpus": 0.25
        }
      }
    }
  }' \
  --deployment-policies '{
    "failureHandlingPolicy": "ROLLBACK",
    "componentUpdatePolicy": {
      "timeoutInSeconds": 60,
      "action": "NOTIFY_COMPONENTS"
    },
    "configurationValidationPolicy": {
      "timeoutInSeconds": 30
    }
  }' \
  --iot-job-configuration '{
    "jobExecutionsRolloutConfig": {
      "maximumPerMinute": 50,
      "exponentialRate": {
        "baseRatePerMinute": 10,
        "incrementFactor": 2.0,
        "rateIncreaseCriteria": {"numberOfSucceededThings": 25}
      }
    },
    "abortConfig": {
      "criteriaList": [{
        "action": "CANCEL",
        "failureType": "ALL",
        "minNumberOfExecutedThings": 5,
        "thresholdPercentage": 20.0
      }]
    },
    "timeoutConfig": {"inProgressTimeoutInMinutes": 30}
  }'

# --- Deploy to a single core device ---
aws greengrassv2 create-deployment \
  --target-arn arn:aws:iot:us-east-1:123456789012:thing/FactoryDevice001 \
  --deployment-name "Single device test v1.0" \
  --components '{
    "com.example.TempSensor": {"componentVersion": "1.0.0"}
  }'

# --- List and describe deployments ---
aws greengrassv2 list-deployments

aws greengrassv2 list-deployments \
  --target-arn arn:aws:iot:us-east-1:123456789012:thinggroup/FactoryDevices \
  --history-filter LATEST_ONLY

aws greengrassv2 get-deployment \
  --deployment-id <deployment-id>

# --- Cancel a deployment ---
aws greengrassv2 cancel-deployment \
  --deployment-id <deployment-id>

# --- Delete a deployment (removes from history; stops future rollouts) ---
aws greengrassv2 delete-deployment \
  --deployment-id <deployment-id>
```

---

### Core Device Management

```bash
# --- List and describe core devices ---
aws greengrassv2 list-core-devices

aws greengrassv2 list-core-devices \
  --thing-group-arn arn:aws:iot:us-east-1:123456789012:thinggroup/FactoryDevices

aws greengrassv2 list-core-devices --status HEALTHY  # HEALTHY | UNHEALTHY

aws greengrassv2 get-core-device \
  --core-device-thing-name FactoryDevice001

# --- List components installed on a core device ---
aws greengrassv2 list-installed-components \
  --core-device-thing-name FactoryDevice001

# --- List deployments for a core device ---
aws greengrassv2 list-effective-deployments \
  --core-device-thing-name FactoryDevice001

# --- Deregister a core device (disassociate from Greengrass) ---
aws greengrassv2 disassociate-service-role-from-account

aws greengrassv2 delete-core-device \
  --core-device-thing-name FactoryDevice001

# --- Service role (Greengrass service role for accessing other AWS services) ---
aws greengrassv2 associate-service-role-to-account \
  --role-arn arn:aws:iam::123456789012:role/GreengrassServiceRole

aws greengrassv2 get-service-role-for-account
aws greengrassv2 disassociate-service-role-from-account
```

---

### Artifact Upload to S3 (prerequisite for component creation)

```bash
# Upload component artifacts before creating the component version
aws s3 cp sensor.py \
  s3://my-greengrass-components/com.example.TempSensor/1.0.0/sensor.py

aws s3 cp model.tar.gz \
  s3://my-greengrass-components/com.example.MLInference/1.0.0/model.tar.gz

# Grant Greengrass access to the bucket (bucket policy example - not a CLI command)
# Principal: iot.greengrass.amazonaws.com
# Action: s3:GetObject on bucket/components/*
```

---

### Tagging Greengrass Resources

```bash
aws greengrassv2 tag-resource \
  --resource-arn arn:aws:greengrass:us-east-1:123456789012:deployments/<deployment-id> \
  --tags '{"Environment": "prod", "Team": "iot-platform"}'

aws greengrassv2 untag-resource \
  --resource-arn arn:aws:greengrass:us-east-1:123456789012:deployments/<deployment-id> \
  --tag-keys Environment

aws greengrassv2 list-tags-for-resource \
  --resource-arn arn:aws:greengrass:us-east-1:123456789012:deployments/<deployment-id>
```

---

## FreeRTOS — Cloud-Side Management via `aws iot`

FreeRTOS devices do not have a separate AWS CLI namespace. All cloud-side resources (things, certificates, policies, jobs) are managed with `aws iot`. See [iot-core-cli.md](iot-core-cli.md) for those commands.

FreeRTOS-specific considerations:

```bash
# --- Register a FreeRTOS device as a thing ---
aws iot create-thing \
  --thing-name FreeRTOSDevice001 \
  --attribute-payload '{"attributes": {"board": "ESP32", "os": "freertos", "version": "202210.01"}}'

# --- Create certificate for FreeRTOS device ---
# The private key and certificate are embedded in the device firmware
aws iot create-keys-and-certificate \
  --set-as-active \
  --certificate-pem-outfile freertos-cert.pem \
  --public-key-outfile freertos-public.key \
  --private-key-outfile freertos-private.key

# Attach minimal policy for FreeRTOS core libraries
aws iot create-policy \
  --policy-name FreeRTOSDevicePolicy \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {"Effect": "Allow", "Action": "iot:Connect", "Resource": "arn:aws:iot:*:*:client/${iot:ClientId}"},
      {"Effect": "Allow", "Action": ["iot:Publish", "iot:Subscribe", "iot:Receive"],
       "Resource": ["arn:aws:iot:*:*:topic/$aws/things/${iot:ClientId}/*",
                    "arn:aws:iot:*:*:topicfilter/$aws/things/${iot:ClientId}/*"]},
      {"Effect": "Allow", "Action": ["iot:GetThingShadow", "iot:UpdateThingShadow", "iot:DeleteThingShadow"],
       "Resource": "arn:aws:iot:*:*:thing/${iot:ClientId}"}
    ]
  }'

# --- OTA update for FreeRTOS (using IoT Jobs + AWS Signer) ---

# 1. Create a code-signing profile
aws signer put-signing-profile \
  --profile-name FreeRTOSSigningProfile \
  --signing-material '{"certificateArn": "arn:aws:acm:us-east-1:123456789012:certificate/<cert-id>"}' \
  --platform-id AmazonFreeRTOS-Default

# 2. Sign the firmware image
aws signer start-signing-job \
  --source '{"s3": {"bucketName": "my-firmware-bucket", "key": "firmware-v2.1.0.bin", "version": "latest"}}' \
  --destination '{"s3": {"bucketName": "my-signed-firmware-bucket", "prefix": "signed/"}}' \
  --profile-name FreeRTOSSigningProfile

# 3. Create the OTA update job
aws iot create-ota-update \
  --ota-update-id firmware-ota-2024-001 \
  --targets arn:aws:iot:us-east-1:123456789012:thinggroup/FreeRTOSDevices \
  --files '[{
    "fileName": "firmware.bin",
    "fileVersion": "1",
    "fileLocation": {
      "s3Location": {
        "bucket": "my-signed-firmware-bucket",
        "key": "signed/firmware-v2.1.0.bin"
      }
    },
    "codeSigning": {
      "awsSignerJobId": "<signer-job-id>"
    }
  }]' \
  --role-arn arn:aws:iam::123456789012:role/OTAUpdateRole \
  --target-selection SNAPSHOT

aws iot get-ota-update --ota-update-id firmware-ota-2024-001
aws iot list-ota-updates
aws iot delete-ota-update --ota-update-id firmware-ota-2024-001
```
