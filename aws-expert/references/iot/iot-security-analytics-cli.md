# AWS IoT Security & Analytics — CLI Reference

For service concepts, see [iot-security-analytics-capabilities.md](iot-security-analytics-capabilities.md).

---

## AWS IoT Device Defender — `aws iot` (Audit & Detect)

### Audit Configuration

```bash
# --- Enable and configure audit ---
aws iot update-account-audit-configuration \
  --role-arn arn:aws:iam::123456789012:role/IoTAuditRole \
  --audit-notification-target-configurations '{
    "SNS": {
      "targetArn": "arn:aws:sns:us-east-1:123456789012:IoTAuditAlerts",
      "roleArn": "arn:aws:iam::123456789012:role/IoTAuditRole",
      "enabled": true
    }
  }' \
  --audit-check-configurations '{
    "CA_CERTIFICATE_EXPIRING": {"enabled": true},
    "DEVICE_CERTIFICATE_EXPIRING": {"enabled": true},
    "DEVICE_CERTIFICATE_KEY_QUALITY": {"enabled": true},
    "DEVICE_CERTIFICATE_SHARED_USE": {"enabled": true},
    "IOT_POLICY_OVERLY_PERMISSIVE": {"enabled": true},
    "LOGGING_DISABLED": {"enabled": true},
    "REVOKED_CA_CERTIFICATE_STILL_ACTIVE": {"enabled": true},
    "REVOKED_DEVICE_CERTIFICATE_STILL_ACTIVE": {"enabled": true},
    "IOT_ROLE_ALIAS_OVERLY_PERMISSIVE": {"enabled": true}
  }'

aws iot describe-account-audit-configuration

# --- Schedule recurring audits ---
aws iot create-scheduled-audit \
  --scheduled-audit-name DailySecurityAudit \
  --frequency DAILY \
  --day-of-week SUN \
  --target-check-names \
    CA_CERTIFICATE_EXPIRING \
    DEVICE_CERTIFICATE_EXPIRING \
    IOT_POLICY_OVERLY_PERMISSIVE \
    LOGGING_DISABLED

aws iot create-scheduled-audit \
  --scheduled-audit-name WeeklyFullAudit \
  --frequency WEEKLY \
  --day-of-week MON \
  --target-check-names ALL

aws iot list-scheduled-audits
aws iot describe-scheduled-audit --scheduled-audit-name DailySecurityAudit

aws iot update-scheduled-audit \
  --scheduled-audit-name DailySecurityAudit \
  --frequency WEEKLY \
  --day-of-week MON

aws iot delete-scheduled-audit --scheduled-audit-name DailySecurityAudit

# --- Run an on-demand audit ---
aws iot start-on-demand-audit-task \
  --target-check-names \
    CA_CERTIFICATE_EXPIRING \
    DEVICE_CERTIFICATE_EXPIRING \
    IOT_POLICY_OVERLY_PERMISSIVE

aws iot describe-audit-task --task-id <task-id>
aws iot list-audit-tasks
aws iot list-audit-tasks --task-type ON_DEMAND_AUDIT_TASK
aws iot list-audit-tasks --task-type SCHEDULED_AUDIT_TASK --task-status COMPLETED

# --- Audit findings ---
aws iot list-audit-findings \
  --task-id <task-id>

aws iot list-audit-findings \
  --check-name DEVICE_CERTIFICATE_EXPIRING \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-12-31T23:59:59Z

aws iot describe-audit-finding --finding-id <finding-id>

# --- Suppress findings (for known/accepted non-compliance) ---
aws iot create-audit-suppression \
  --check-name DEVICE_CERTIFICATE_EXPIRING \
  --resource-identifier '{"deviceCertificateId": "<cert-id>"}' \
  --expiration-date 2025-06-01T00:00:00Z \
  --suppress-indefinitely false \
  --description "Test certificate, expiry expected"

aws iot list-audit-suppressions
aws iot delete-audit-suppression \
  --check-name DEVICE_CERTIFICATE_EXPIRING \
  --resource-identifier '{"deviceCertificateId": "<cert-id>"}'
```

---

### Mitigation Actions

```bash
# --- Create mitigation actions ---

# Quarantine device by adding to restricted group
aws iot create-mitigation-action \
  --action-name QuarantineDevice \
  --role-arn arn:aws:iam::123456789012:role/IoTMitigationRole \
  --action-params '{
    "addThingsToThingGroupParams": {
      "thingGroupNames": ["QuarantineGroup"],
      "overrideDynamicGroups": true
    }
  }'

# Replace device policy with restricted blank policy
aws iot create-mitigation-action \
  --action-name RestrictDevicePolicy \
  --role-arn arn:aws:iam::123456789012:role/IoTMitigationRole \
  --action-params '{
    "replaceDefaultPolicyVersionParams": {
      "templateName": "BLANK_POLICY"
    }
  }'

# Deactivate a device certificate
aws iot create-mitigation-action \
  --action-name DeactivateCertificate \
  --role-arn arn:aws:iam::123456789012:role/IoTMitigationRole \
  --action-params '{
    "updateDeviceCertificateParams": {
      "action": "DEACTIVATE"
    }
  }'

# Publish finding to SNS for external processing
aws iot create-mitigation-action \
  --action-name NotifySecurityTeam \
  --role-arn arn:aws:iam::123456789012:role/IoTMitigationRole \
  --action-params '{
    "publishFindingToSnsParams": {
      "topicArn": "arn:aws:sns:us-east-1:123456789012:SecurityAlerts"
    }
  }'

aws iot list-mitigation-actions
aws iot describe-mitigation-action --action-name QuarantineDevice
aws iot delete-mitigation-action --action-name QuarantineDevice

# --- Apply mitigation actions to audit findings ---
aws iot start-audit-mitigation-actions-task \
  --task-id remediation-task-001 \
  --target '{"auditTaskId": "<audit-task-id>"}' \
  --audit-check-to-actions-mapping '{
    "DEVICE_CERTIFICATE_EXPIRING": ["DeactivateCertificate"],
    "IOT_POLICY_OVERLY_PERMISSIVE": ["NotifySecurityTeam"]
  }' \
  --client-request-token <token>

aws iot list-audit-mitigation-actions-tasks
aws iot describe-audit-mitigation-actions-task --task-id remediation-task-001

aws iot list-audit-mitigation-actions-executions \
  --task-id remediation-task-001 \
  --action-status COMPLETED

aws iot cancel-audit-mitigation-actions-task --task-id remediation-task-001
```

---

### Detect — Security Profiles and Behaviors

```bash
# --- Create a security profile ---
aws iot create-security-profile \
  --security-profile-name DeviceBehaviorProfile \
  --security-profile-description "Monitor device connection and messaging behavior" \
  --behaviors '[
    {
      "name": "AuthorizationFailureLimit",
      "metric": "aws:num-authorization-failures",
      "criteria": {
        "comparisonOperator": "greater-than",
        "value": {"count": 5},
        "durationSeconds": 300,
        "consecutiveDatapointsToAlarm": 1,
        "consecutiveDatapointsToClear": 1
      },
      "suppressAlerts": false
    },
    {
      "name": "MessageRateNormal",
      "metric": "aws:num-messages-sent",
      "criteria": {
        "comparisonOperator": "less-than",
        "value": {"count": 1000},
        "durationSeconds": 300
      }
    },
    {
      "name": "NoUnexpectedPorts",
      "metric": "aws:listening-tcp-ports",
      "criteria": {
        "comparisonOperator": "in-port-set",
        "value": {"ports": [8883, 443]}
      }
    }
  ]' \
  --alert-targets '{
    "SNS": {
      "alertTargetArn": "arn:aws:sns:us-east-1:123456789012:SecurityViolations",
      "roleArn": "arn:aws:iam::123456789012:role/IoTDefenderRole"
    }
  }' \
  --additional-metrics-to-retain-v2 '[
    {"metric": "aws:num-messages-sent"},
    {"metric": "aws:source-ip-address"}
  ]'

aws iot describe-security-profile --security-profile-name DeviceBehaviorProfile
aws iot list-security-profiles

aws iot update-security-profile \
  --security-profile-name DeviceBehaviorProfile \
  --behaviors file://updated-behaviors.json

aws iot delete-security-profile --security-profile-name DeviceBehaviorProfile

# --- Attach/detach security profile ---
aws iot attach-security-profile \
  --security-profile-name DeviceBehaviorProfile \
  --security-profile-target-arn arn:aws:iot:us-east-1:123456789012:thinggroup/FactoryDevices

# Attach to all registered things
aws iot attach-security-profile \
  --security-profile-name DeviceBehaviorProfile \
  --security-profile-target-arn arn:aws:iot:us-east-1:$AWS_ACCOUNT_ID:all/registered-things

aws iot detach-security-profile \
  --security-profile-name DeviceBehaviorProfile \
  --security-profile-target-arn arn:aws:iot:us-east-1:123456789012:thinggroup/FactoryDevices

aws iot list-targets-for-security-profile --security-profile-name DeviceBehaviorProfile
aws iot list-security-profiles-for-target \
  --security-profile-target-arn arn:aws:iot:us-east-1:123456789012:thinggroup/FactoryDevices

# --- Violations ---
aws iot list-active-violations
aws iot list-active-violations \
  --security-profile-name DeviceBehaviorProfile

aws iot list-active-violations \
  --thing-name MyDevice001

aws iot list-violation-events \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --security-profile-name DeviceBehaviorProfile

# Update violation verification state
aws iot put-verification-state-on-violation \
  --violation-id <violation-id> \
  --verification-state FALSE_POSITIVE \
  --verification-state-description "Normal scheduled maintenance activity"

# --- Custom metrics ---
aws iot create-custom-metric \
  --metric-name battery_level \
  --metric-type number \
  --display-name "Battery Level (%)" \
  --client-request-token <token>

aws iot list-custom-metrics
aws iot describe-custom-metric --metric-name battery_level
aws iot delete-custom-metric --metric-name battery_level

# --- ML Detect ---
# Enable ML behaviors in a security profile
aws iot create-security-profile \
  --security-profile-name MLDetectProfile \
  --behaviors '[
    {
      "name": "MLMessagingAnomaly",
      "metric": "aws:num-messages-sent",
      "criteria": {
        "mlDetectionConfig": {"confidenceLevel": "MEDIUM"}
      }
    }
  ]'

# Get ML model training status
aws iot get-behavior-model-training-summaries \
  --security-profile-name MLDetectProfile
```

---

## AWS IoT Events — `aws iotevents` and `aws iotevents-data`

### Inputs

```bash
# --- Create an input ---
aws iotevents create-input \
  --input-name TemperatureSensorInput \
  --input-description "Temperature sensor readings" \
  --input-definition '{
    "attributes": [
      {"jsonPath": "deviceId"},
      {"jsonPath": "temperature"},
      {"jsonPath": "humidity"},
      {"jsonPath": "timestamp"}
    ]
  }'

aws iotevents describe-input --input-name TemperatureSensorInput
aws iotevents list-inputs

aws iotevents update-input \
  --input-name TemperatureSensorInput \
  --input-definition '{
    "attributes": [
      {"jsonPath": "deviceId"},
      {"jsonPath": "temperature"},
      {"jsonPath": "humidity"},
      {"jsonPath": "batteryLevel"},
      {"jsonPath": "timestamp"}
    ]
  }'

aws iotevents delete-input --input-name TemperatureSensorInput
```

---

### Detector Models

```bash
# --- Create a detector model ---
aws iotevents create-detector-model \
  --detector-model-name TemperatureAlertDetector \
  --detector-model-description "Detect sustained high temperature conditions" \
  --key deviceId \
  --role-arn arn:aws:iam::123456789012:role/IoTEventsRole \
  --evaluation-method SERIAL \
  --detector-model-definition '{
    "states": [
      {
        "stateName": "Normal",
        "onInput": {
          "events": [
            {
              "eventName": "CheckHighTemp",
              "condition": "$input.TemperatureSensorInput.temperature > 85",
              "actions": [
                {
                  "setVariable": {
                    "variableName": "highTempCount",
                    "value": "$variable.highTempCount + 1"
                  }
                }
              ]
            }
          ],
          "transitionEvents": [
            {
              "eventName": "GoToAlert",
              "condition": "$variable.highTempCount >= 3",
              "actions": [],
              "nextState": "Alert"
            }
          ]
        },
        "onEnter": {
          "events": [
            {
              "eventName": "Reset",
              "condition": "true",
              "actions": [
                {
                  "setVariable": {
                    "variableName": "highTempCount",
                    "value": "0"
                  }
                }
              ]
            }
          ]
        },
        "onExit": {"events": []}
      },
      {
        "stateName": "Alert",
        "onEnter": {
          "events": [
            {
              "eventName": "SendAlert",
              "condition": "true",
              "actions": [
                {
                  "sns": {
                    "targetArn": "arn:aws:sns:us-east-1:123456789012:TemperatureAlerts"
                  }
                },
                {
                  "iotTopicPublish": {
                    "mqttTopic": "alerts/temperature/$input.TemperatureSensorInput.deviceId"
                  }
                },
                {
                  "setTimer": {
                    "timerName": "alertTimer",
                    "seconds": 300
                  }
                }
              ]
            }
          ]
        },
        "onInput": {
          "events": [],
          "transitionEvents": [
            {
              "eventName": "TempNormal",
              "condition": "$input.TemperatureSensorInput.temperature <= 75",
              "actions": [],
              "nextState": "Normal"
            }
          ]
        },
        "onExit": {"events": []}
      }
    ],
    "initialStateName": "Normal"
  }'

aws iotevents describe-detector-model --detector-model-name TemperatureAlertDetector
aws iotevents list-detector-models

# List versions of a detector model
aws iotevents list-detector-model-versions --detector-model-name TemperatureAlertDetector

aws iotevents update-detector-model \
  --detector-model-name TemperatureAlertDetector \
  --role-arn arn:aws:iam::123456789012:role/IoTEventsRole \
  --detector-model-definition file://updated-detector-model.json

aws iotevents delete-detector-model --detector-model-name TemperatureAlertDetector
```

---

### Alarm Models

```bash
# --- Create an alarm model ---
aws iotevents create-alarm-model \
  --alarm-model-name MotorTemperatureAlarm \
  --alarm-model-description "Alarm when motor temperature exceeds threshold" \
  --role-arn arn:aws:iam::123456789012:role/IoTEventsRole \
  --key deviceId \
  --severity 50 \
  --alarm-rule '{
    "simpleRule": {
      "inputProperty": "$input.TemperatureSensorInput.temperature",
      "comparisonOperator": "GREATER",
      "threshold": "90"
    }
  }' \
  --alarm-notification '{
    "notificationActions": [
      {
        "action": {
          "sns": {
            "targetArn": "arn:aws:sns:us-east-1:123456789012:MotorAlarms",
            "payload": {
              "contentExpression": "'\''Alarm: motor temp ${}'\''",
              "type": "STRING"
            }
          }
        }
      }
    ]
  }' \
  --alarm-event-actions '{
    "alarmActions": [
      {"sns": {"targetArn": "arn:aws:sns:us-east-1:123456789012:MotorAlarms"}}
    ]
  }'

aws iotevents describe-alarm-model --alarm-model-name MotorTemperatureAlarm
aws iotevents list-alarm-models
aws iotevents delete-alarm-model --alarm-model-name MotorTemperatureAlarm
```

---

### IoT Events Data Plane — `aws iotevents-data`

```bash
# --- Send messages to inputs ---
aws iotevents-data batch-put-message \
  --messages '[
    {
      "messageId": "msg-001",
      "inputName": "TemperatureSensorInput",
      "payload": "{\"deviceId\": \"device-001\", \"temperature\": 92.5, \"humidity\": 45}"
    },
    {
      "messageId": "msg-002",
      "inputName": "TemperatureSensorInput",
      "payload": "{\"deviceId\": \"device-002\", \"temperature\": 75.0, \"humidity\": 50}"
    }
  ]'

# --- List and describe detectors ---
aws iotevents-data list-detectors \
  --detector-model-name TemperatureAlertDetector

aws iotevents-data describe-detector \
  --detector-model-name TemperatureAlertDetector \
  --key-value "device-001"

# --- Update detector state (manual override) ---
aws iotevents-data batch-update-detector \
  --detectors '[
    {
      "messageId": "update-001",
      "detectorModelName": "TemperatureAlertDetector",
      "keyValue": "device-001",
      "state": {
        "stateName": "Normal",
        "variables": [{"name": "highTempCount", "value": "0"}],
        "timers": []
      }
    }
  ]'

# --- Alarm data operations ---
aws iotevents-data list-alarms \
  --alarm-model-name MotorTemperatureAlarm

aws iotevents-data describe-alarm \
  --alarm-model-name MotorTemperatureAlarm \
  --key-value "device-001"

# Acknowledge alarm
aws iotevents-data batch-acknowledge-alarm \
  --acknowledge-action-requests '[
    {
      "requestId": "ack-001",
      "alarmModelName": "MotorTemperatureAlarm",
      "keyValue": "device-001",
      "note": "Investigated and within tolerance"
    }
  ]'

# Snooze alarm
aws iotevents-data batch-snooze-alarm \
  --snooze-action-requests '[
    {
      "requestId": "snooze-001",
      "alarmModelName": "MotorTemperatureAlarm",
      "keyValue": "device-001",
      "snoozeDuration": 300,
      "note": "Maintenance window"
    }
  ]'

# Reset alarm
aws iotevents-data batch-reset-alarm \
  --reset-action-requests '[
    {
      "requestId": "reset-001",
      "alarmModelName": "MotorTemperatureAlarm",
      "keyValue": "device-001"
    }
  ]'

# Enable/disable alarm
aws iotevents-data batch-enable-alarm \
  --enable-action-requests '[
    {"requestId": "enable-001", "alarmModelName": "MotorTemperatureAlarm", "keyValue": "device-001"}
  ]'

aws iotevents-data batch-disable-alarm \
  --disable-action-requests '[
    {"requestId": "disable-001", "alarmModelName": "MotorTemperatureAlarm", "keyValue": "device-001", "note": "Sensor offline"}
  ]'
```

---

## AWS IoT Analytics — `aws iotanalytics`

### Channels

```bash
# --- Create a channel ---
aws iotanalytics create-channel \
  --channel-name SensorDataChannel \
  --channel-storage '{
    "serviceManagedS3": {}
  }' \
  --retention-period '{"unlimited": false, "numberOfDays": 90}'

# Customer-managed S3 channel
aws iotanalytics create-channel \
  --channel-name SensorDataChannelCustom \
  --channel-storage '{
    "customerManagedS3": {
      "bucket": "my-iot-analytics-raw",
      "keyPrefix": "raw-messages/",
      "roleArn": "arn:aws:iam::123456789012:role/IoTAnalyticsRole"
    }
  }'

aws iotanalytics describe-channel --channel-name SensorDataChannel
aws iotanalytics list-channels

aws iotanalytics update-channel \
  --channel-name SensorDataChannel \
  --retention-period '{"unlimited": false, "numberOfDays": 30}'

# Direct message ingestion (bypass IoT Core rule)
aws iotanalytics batch-put-message \
  --channel-name SensorDataChannel \
  --messages '[
    {"messageId": "msg-001", "payload": "{\"deviceId\": \"d1\", \"temp\": 72.5}"},
    {"messageId": "msg-002", "payload": "{\"deviceId\": \"d2\", \"temp\": 68.0}"}
  ]'

aws iotanalytics sample-channel-data \
  --channel-name SensorDataChannel \
  --max-messages 10

aws iotanalytics delete-channel --channel-name SensorDataChannel
```

---

### Pipelines

```bash
# --- Create a pipeline ---
aws iotanalytics create-pipeline \
  --pipeline-name SensorDataPipeline \
  --pipeline-activities '[
    {
      "channel": {
        "name": "ChannelActivity",
        "channelName": "SensorDataChannel",
        "next": "LambdaEnrich"
      }
    },
    {
      "lambda": {
        "name": "LambdaEnrich",
        "lambdaName": "IoTAnalyticsEnricher",
        "batchSize": 10,
        "next": "AddTimestamp"
      }
    },
    {
      "addAttributes": {
        "name": "AddTimestamp",
        "attributes": {
          "processed_at": "${timestamp()}"
        },
        "next": "FilterBadQuality"
      }
    },
    {
      "filter": {
        "name": "FilterBadQuality",
        "filter": "quality = '\''GOOD'\''",
        "next": "ConvertTempToF"
      }
    },
    {
      "math": {
        "name": "ConvertTempToF",
        "attribute": "temperature_f",
        "math": "temperature_c * 9 / 5 + 32",
        "next": "EnrichFromRegistry"
      }
    },
    {
      "deviceRegistryEnrich": {
        "name": "EnrichFromRegistry",
        "attribute": "registry",
        "thingName": "deviceId",
        "roleArn": "arn:aws:iam::123456789012:role/IoTAnalyticsRole",
        "next": "DatastoreActivity"
      }
    },
    {
      "datastore": {
        "name": "DatastoreActivity",
        "datastoreName": "SensorDatastore"
      }
    }
  ]'

aws iotanalytics describe-pipeline --pipeline-name SensorDataPipeline
aws iotanalytics list-pipelines

aws iotanalytics update-pipeline \
  --pipeline-name SensorDataPipeline \
  --pipeline-activities file://updated-pipeline.json

# Run pipeline reprocessing (reprocess historical channel data)
aws iotanalytics start-pipeline-reprocessing \
  --pipeline-name SensorDataPipeline \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z

aws iotanalytics list-pipeline-reprocessings --pipeline-name SensorDataPipeline

aws iotanalytics cancel-pipeline-reprocessing \
  --pipeline-name SensorDataPipeline \
  --reprocessing-id <reprocessing-id>

aws iotanalytics delete-pipeline --pipeline-name SensorDataPipeline
```

---

### Datastores

```bash
# --- Create a datastore ---
aws iotanalytics create-datastore \
  --datastore-name SensorDatastore \
  --datastore-storage '{"serviceManagedS3": {}}' \
  --retention-period '{"unlimited": false, "numberOfDays": 365}' \
  --file-format-configuration '{
    "parquetConfiguration": {
      "schemaDefinition": {
        "columns": [
          {"name": "deviceId", "type": "string"},
          {"name": "temperature_c", "type": "double"},
          {"name": "temperature_f", "type": "double"},
          {"name": "humidity", "type": "double"},
          {"name": "timestamp", "type": "bigint"},
          {"name": "processed_at", "type": "string"}
        ]
      }
    }
  }'

aws iotanalytics describe-datastore --datastore-name SensorDatastore
aws iotanalytics list-datastores

aws iotanalytics update-datastore \
  --datastore-name SensorDatastore \
  --retention-period '{"unlimited": false, "numberOfDays": 180}'

aws iotanalytics delete-datastore --datastore-name SensorDatastore
```

---

### Datasets

```bash
# --- Create a SQL dataset ---
aws iotanalytics create-dataset \
  --dataset-name DailyTemperatureSummary \
  --actions '[
    {
      "actionName": "SqlQuery",
      "queryAction": {
        "sqlQuery": "SELECT deviceId, DATE_TRUNC('\''hour'\'', from_unixtime(timestamp)) AS hour, AVG(temperature_c) AS avg_temp_c, MAX(temperature_c) AS max_temp_c, MIN(temperature_c) AS min_temp_c, COUNT(*) AS readings FROM SensorDatastore WHERE __dt >= current_date - interval '\''1'\'' day GROUP BY 1, 2",
        "filters": [
          {
            "deltaTime": {
              "offsetSeconds": -86400,
              "timeExpression": "from_unixtime(timestamp)"
            }
          }
        ]
      }
    }
  ]' \
  --triggers '[
    {
      "schedule": {"expression": "cron(0 1 * * ? *)"}
    }
  ]' \
  --retention-period '{"unlimited": false, "numberOfDays": 30}' \
  --content-delivery-rules '[
    {
      "destination": {
        "s3DestinationConfiguration": {
          "bucket": "my-iot-reports",
          "key": "temperature-summary/!{iotanalytics:scheduleTime}/report.csv",
          "roleArn": "arn:aws:iam::123456789012:role/IoTAnalyticsRole"
        }
      }
    }
  ]'

# --- Create a container dataset (ML training) ---
aws iotanalytics create-dataset \
  --dataset-name MLTrainingDataset \
  --actions '[
    {
      "actionName": "ContainerAction",
      "containerAction": {
        "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/my-analytics:latest",
        "executionRoleArn": "arn:aws:iam::123456789012:role/IoTAnalyticsContainerRole",
        "resourceConfiguration": {
          "computeType": "ACU_1",
          "volumeSizeInGB": 10
        },
        "variables": [
          {
            "name": "LOOKBACK_DAYS",
            "stringValue": "30"
          },
          {
            "name": "INPUT_DATASET",
            "datasetContentVersionValue": {
              "datasetName": "DailyTemperatureSummary"
            }
          }
        ]
      }
    }
  ]'

aws iotanalytics describe-dataset --dataset-name DailyTemperatureSummary
aws iotanalytics list-datasets

# Manually trigger dataset content generation
aws iotanalytics create-dataset-content --dataset-name DailyTemperatureSummary

aws iotanalytics list-dataset-contents --dataset-name DailyTemperatureSummary

aws iotanalytics get-dataset-content \
  --dataset-name DailyTemperatureSummary \
  --version-id \$LATEST   # or specific version ID

aws iotanalytics delete-dataset-content \
  --dataset-name DailyTemperatureSummary \
  --version-id <version-id>

aws iotanalytics update-dataset \
  --dataset-name DailyTemperatureSummary \
  --actions file://updated-actions.json \
  --triggers file://updated-triggers.json

aws iotanalytics delete-dataset --dataset-name DailyTemperatureSummary
```
