# AWS EventBridge — CLI Reference
For service concepts, see [eventbridge-capabilities.md](eventbridge-capabilities.md).

## EventBridge — events

```bash
# --- Event buses ---
aws events create-event-bus --name my-custom-bus
aws events list-event-buses
aws events describe-event-bus --name my-custom-bus
aws events update-event-bus --name my-custom-bus --description "Custom bus for order events"
aws events delete-event-bus --name my-custom-bus

# Cross-account policy: allow another account to put events
aws events put-permission \
  --event-bus-name my-custom-bus \
  --action events:PutEvents \
  --principal 987654321098 \
  --statement-id allow-account-987

aws events remove-permission --statement-id allow-account-987 --event-bus-name my-custom-bus

# --- Rules ---
# Event pattern rule
aws events put-rule \
  --name OrderCreatedRule \
  --event-bus-name my-custom-bus \
  --event-pattern '{
    "source": ["myapp.orders"],
    "detail-type": ["OrderCreated"],
    "detail": {
      "status": ["PENDING"]
    }
  }' \
  --state ENABLED

# Schedule rule (use EventBridge Scheduler for new schedules)
aws events put-rule \
  --name DailyCleanup \
  --schedule-expression "cron(0 2 * * ? *)" \
  --state ENABLED

aws events describe-rule --name OrderCreatedRule
aws events list-rules --event-bus-name my-custom-bus
aws events disable-rule --name OrderCreatedRule --event-bus-name my-custom-bus
aws events enable-rule --name OrderCreatedRule --event-bus-name my-custom-bus
aws events delete-rule --name OrderCreatedRule --event-bus-name my-custom-bus

# --- Targets ---
# Lambda target
aws events put-targets \
  --rule OrderCreatedRule \
  --event-bus-name my-custom-bus \
  --targets '[{
    "Id": "LambdaTarget",
    "Arn": "arn:aws:lambda:us-east-1:123456789012:function:process-order"
  }]'

# SQS target with input transformation
aws events put-targets \
  --rule OrderCreatedRule \
  --event-bus-name my-custom-bus \
  --targets '[{
    "Id": "SQSTarget",
    "Arn": "arn:aws:sqs:us-east-1:123456789012:order-queue",
    "InputTransformer": {
      "InputPathsMap": {"orderId": "$.detail.orderId"},
      "InputTemplate": "{\"order_id\": \"<orderId>\", \"source\": \"eventbridge\"}"
    }
  }]'

# Step Functions target
aws events put-targets \
  --rule OrderCreatedRule \
  --event-bus-name my-custom-bus \
  --targets '[{
    "Id": "SFNTarget",
    "Arn": "arn:aws:states:us-east-1:123456789012:stateMachine:OrderWorkflow",
    "RoleArn": "arn:aws:iam::123456789012:role/eventbridge-sfn-role"
  }]'

aws events remove-targets \
  --rule OrderCreatedRule \
  --event-bus-name my-custom-bus \
  --ids LambdaTarget

aws events list-targets-by-rule --rule OrderCreatedRule --event-bus-name my-custom-bus

# --- Sending events ---
aws events put-events \
  --entries '[{
    "Source": "myapp.orders",
    "DetailType": "OrderCreated",
    "Detail": "{\"orderId\": \"12345\", \"status\": \"PENDING\"}",
    "EventBusName": "my-custom-bus"
  }]'

# Test event pattern
aws events test-event-pattern \
  --event-pattern '{"source":["myapp.orders"]}' \
  --event '{"source":"myapp.orders","detail-type":"OrderCreated","detail":{}}'

# --- Archives and replay ---
aws events create-archive \
  --archive-name OrdersArchive \
  --event-source-arn arn:aws:events:us-east-1:123456789012:event-bus/my-custom-bus \
  --event-pattern '{"source":["myapp.orders"]}' \
  --retention-days 30

aws events describe-archive --archive-name OrdersArchive

aws events start-replay \
  --replay-name OrderReplay \
  --source-arn arn:aws:events:us-east-1:123456789012:archive/OrdersArchive \
  --event-start-time 2025-01-01T00:00:00 \
  --event-end-time 2025-01-02T00:00:00 \
  --destination '{"Arn":"arn:aws:events:us-east-1:123456789012:event-bus/my-custom-bus"}'
```

---

## EventBridge Scheduler — scheduler

```bash
# --- Schedules ---
# One-time schedule
aws scheduler create-schedule \
  --name SendWelcomeEmail \
  --schedule-expression "at(2025-06-01T09:00:00)" \
  --schedule-expression-timezone "America/New_York" \
  --target '{
    "Arn": "arn:aws:lambda:us-east-1:123456789012:function:send-welcome-email",
    "RoleArn": "arn:aws:iam::123456789012:role/scheduler-role",
    "Input": "{\"userId\":\"abc123\"}"
  }' \
  --flexible-time-window Mode=OFF

# Recurring rate schedule
aws scheduler create-schedule \
  --name ProcessQueue \
  --schedule-expression "rate(5 minutes)" \
  --target '{
    "Arn": "arn:aws:lambda:us-east-1:123456789012:function:process-queue",
    "RoleArn": "arn:aws:iam::123456789012:role/scheduler-role"
  }' \
  --flexible-time-window Mode=OFF

# Cron schedule with flexible window (reduces thundering herd)
aws scheduler create-schedule \
  --name DailyReport \
  --schedule-expression "cron(0 8 * * ? *)" \
  --schedule-expression-timezone "Europe/London" \
  --target '{
    "Arn": "arn:aws:sqs:us-east-1:123456789012:reports-queue",
    "RoleArn": "arn:aws:iam::123456789012:role/scheduler-role",
    "SqsParameters": {"MessageGroupId": "daily-report"}
  }' \
  --flexible-time-window Mode=FLEXIBLE,MaximumWindowInMinutes=15

# Universal target (270+ services via SDK API)
aws scheduler create-schedule \
  --name TriggerECSTask \
  --schedule-expression "rate(1 hour)" \
  --target '{
    "Arn": "arn:aws:scheduler:::aws-sdk:ecs:runTask",
    "RoleArn": "arn:aws:iam::123456789012:role/scheduler-role",
    "Input": "{\"Cluster\":\"my-cluster\",\"TaskDefinition\":\"my-task\",\"LaunchType\":\"FARGATE\"}"
  }' \
  --flexible-time-window Mode=OFF

aws scheduler get-schedule --name DailyReport
aws scheduler list-schedules
aws scheduler update-schedule --name DailyReport --schedule-expression "cron(0 9 * * ? *)" \
  --schedule-expression-timezone "Europe/London" \
  --target '...' --flexible-time-window Mode=OFF
aws scheduler delete-schedule --name DailyReport

# --- Schedule groups ---
aws scheduler create-schedule-group --name production-schedules
aws scheduler list-schedule-groups
aws scheduler get-schedule-group --name production-schedules
aws scheduler delete-schedule-group --name production-schedules
# Note: deleting a group deletes all schedules within it

# Create schedule in a group
aws scheduler create-schedule \
  --name MySchedule \
  --group-name production-schedules \
  --schedule-expression "rate(1 hour)" \
  --target '{"Arn":"...","RoleArn":"..."}' \
  --flexible-time-window Mode=OFF
```

---

## EventBridge Pipes — pipes

```bash
# --- Create a pipe ---
# SQS → Lambda (simple)
aws pipes create-pipe \
  --name OrderProcessingPipe \
  --role-arn arn:aws:iam::123456789012:role/pipes-role \
  --source arn:aws:sqs:us-east-1:123456789012:order-queue \
  --source-parameters '{
    "SqsQueueParameters": {
      "BatchSize": 10,
      "MaximumBatchingWindowInSeconds": 5
    }
  }' \
  --target arn:aws:lambda:us-east-1:123456789012:function:process-order

# SQS → filter → Lambda enrichment → Step Functions
aws pipes create-pipe \
  --name EnrichedOrderPipe \
  --role-arn arn:aws:iam::123456789012:role/pipes-role \
  --source arn:aws:sqs:us-east-1:123456789012:order-queue \
  --source-parameters '{
    "SqsQueueParameters": {"BatchSize": 1}
  }' \
  --filter-pattern '{"body": {"status": ["PENDING"]}}' \
  --enrichment arn:aws:lambda:us-east-1:123456789012:function:enrich-order \
  --enrichment-parameters '{
    "InputTemplate": "{\"orderId\": \"<$.body.orderId>\"}"
  }' \
  --target arn:aws:states:us-east-1:123456789012:stateMachine:OrderWorkflow \
  --target-parameters '{
    "StepFunctionStateMachineParameters": {"InvocationType": "FIRE_AND_FORGET"}
  }'

# DynamoDB Streams → EventBridge bus
aws pipes create-pipe \
  --name DDBChangesPipe \
  --role-arn arn:aws:iam::123456789012:role/pipes-role \
  --source arn:aws:dynamodb:us-east-1:123456789012:table/Orders/stream/2024-01-01T00:00:00.000 \
  --source-parameters '{
    "DynamoDBStreamParameters": {
      "StartingPosition": "LATEST",
      "BatchSize": 10
    }
  }' \
  --target arn:aws:events:us-east-1:123456789012:event-bus/my-custom-bus \
  --target-parameters '{
    "EventBridgeEventBusParameters": {
      "DetailType": "DynamoDBChange",
      "Source": "myapp.dynamodb"
    }
  }'

aws pipes describe-pipe --name OrderProcessingPipe
aws pipes list-pipes
aws pipes start-pipe --name OrderProcessingPipe
aws pipes stop-pipe --name OrderProcessingPipe
aws pipes update-pipe --name OrderProcessingPipe --desired-state RUNNING
aws pipes delete-pipe --name OrderProcessingPipe
```
