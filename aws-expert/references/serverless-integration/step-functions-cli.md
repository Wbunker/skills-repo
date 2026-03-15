# AWS Step Functions — CLI Reference
For service concepts, see [step-functions-capabilities.md](step-functions-capabilities.md).

## Step Functions — stepfunctions

```bash
# --- State machines ---
aws stepfunctions create-state-machine \
  --name MyStateMachine \
  --definition file://state-machine.json \
  --role-arn arn:aws:iam::123456789012:role/stepfunctions-role \
  --type STANDARD

# Express workflow
aws stepfunctions create-state-machine \
  --name MyExpressWorkflow \
  --definition file://state-machine.json \
  --role-arn arn:aws:iam::123456789012:role/stepfunctions-role \
  --type EXPRESS \
  --logging-configuration '{
    "level":"ALL",
    "includeExecutionData":true,
    "destinations":[{"cloudWatchLogsLogGroup":{"logGroupArn":"arn:aws:logs:us-east-1:123456789012:log-group:/aws/states/express"}}]
  }'

aws stepfunctions update-state-machine \
  --state-machine-arn arn:aws:states:us-east-1:123456789012:stateMachine:MyStateMachine \
  --definition file://updated-definition.json

aws stepfunctions delete-state-machine \
  --state-machine-arn arn:aws:states:us-east-1:123456789012:stateMachine:MyStateMachine

aws stepfunctions list-state-machines
aws stepfunctions describe-state-machine \
  --state-machine-arn arn:aws:states:us-east-1:123456789012:stateMachine:MyStateMachine

aws stepfunctions validate-state-machine-definition \
  --definition file://state-machine.json

# --- Versions and aliases ---
aws stepfunctions publish-state-machine-version \
  --state-machine-arn arn:aws:states:us-east-1:123456789012:stateMachine:MyStateMachine \
  --description "v2.0 release"

aws stepfunctions create-state-machine-alias \
  --name prod \
  --routing-configuration \
    stateMachineVersionArn=arn:aws:states:us-east-1:123456789012:stateMachine:MyStateMachine:3,weight=100

# --- Executions ---
aws stepfunctions start-execution \
  --state-machine-arn arn:aws:states:us-east-1:123456789012:stateMachine:MyStateMachine \
  --name my-execution-$(date +%s) \
  --input '{"orderId":"12345","action":"process"}'

# Synchronous execution (Express only)
aws stepfunctions start-sync-execution \
  --state-machine-arn arn:aws:states:us-east-1:123456789012:stateMachine:MyExpressWorkflow \
  --input '{"key":"value"}'

aws stepfunctions describe-execution \
  --execution-arn arn:aws:states:us-east-1:123456789012:execution:MyStateMachine:my-execution

aws stepfunctions list-executions \
  --state-machine-arn arn:aws:states:us-east-1:123456789012:stateMachine:MyStateMachine \
  --status-filter RUNNING

aws stepfunctions get-execution-history \
  --execution-arn arn:aws:states:us-east-1:123456789012:execution:MyStateMachine:my-execution \
  --reverse-order

aws stepfunctions stop-execution \
  --execution-arn arn:aws:states:us-east-1:123456789012:execution:MyStateMachine:my-execution \
  --cause "Manual stop for maintenance"

# Redrive a failed execution
aws stepfunctions redrive-execution \
  --execution-arn arn:aws:states:us-east-1:123456789012:execution:MyStateMachine:my-execution

# --- Activity tasks ---
aws stepfunctions create-activity --name MyActivity
aws stepfunctions list-activities

# Worker: poll for a task
aws stepfunctions get-activity-task \
  --activity-arn arn:aws:states:us-east-1:123456789012:activity:MyActivity \
  --worker-name worker-1

# Worker: send result
aws stepfunctions send-task-success \
  --task-token "TASK_TOKEN_FROM_GET_ACTIVITY_TASK" \
  --output '{"result":"success"}'

aws stepfunctions send-task-failure \
  --task-token "TASK_TOKEN" \
  --error "ProcessingFailed" \
  --cause "Validation error on line 42"

aws stepfunctions send-task-heartbeat --task-token "TASK_TOKEN"
```
