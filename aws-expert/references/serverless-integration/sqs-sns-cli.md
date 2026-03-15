# AWS SQS & SNS — CLI Reference
For service concepts, see [sqs-sns-capabilities.md](sqs-sns-capabilities.md).

## SQS

```bash
# --- Create queues ---
aws sqs create-queue --queue-name my-queue
aws sqs create-queue \
  --queue-name my-queue.fifo \
  --attributes '{
    "FifoQueue": "true",
    "ContentBasedDeduplication": "true",
    "VisibilityTimeout": "60",
    "MessageRetentionPeriod": "1209600"
  }'

# Create queue with DLQ
aws sqs create-queue \
  --queue-name my-queue-with-dlq \
  --attributes '{
    "RedrivePolicy": "{\"deadLetterTargetArn\":\"arn:aws:sqs:us-east-1:123456789012:dlq\",\"maxReceiveCount\":\"5\"}",
    "VisibilityTimeout": "30"
  }'

# --- Queue management ---
aws sqs list-queues
aws sqs list-queues --queue-name-prefix my-
aws sqs get-queue-url --queue-name my-queue
aws sqs get-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue \
  --attribute-names All
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue \
  --attributes VisibilityTimeout=120,MessageRetentionPeriod=86400

aws sqs tag-queue \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue \
  --tags Env=prod,Team=platform

aws sqs purge-queue --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue
aws sqs delete-queue --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue

# --- Sending messages ---
aws sqs send-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue \
  --message-body '{"orderId":"12345","action":"process"}' \
  --delay-seconds 5 \
  --message-attributes '{
    "contentType": {"DataType":"String","StringValue":"application/json"}
  }'

# FIFO queue
aws sqs send-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue.fifo \
  --message-body '{"orderId":"12345"}' \
  --message-group-id "customer-42" \
  --message-deduplication-id "order-12345"

# Batch send (up to 10 messages)
aws sqs send-message-batch \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue \
  --entries '[
    {"Id":"1","MessageBody":"message one"},
    {"Id":"2","MessageBody":"message two","DelaySeconds":10}
  ]'

# --- Receiving and deleting ---
aws sqs receive-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue \
  --max-number-of-messages 10 \
  --wait-time-seconds 20 \
  --visibility-timeout 30 \
  --message-attribute-names All

aws sqs delete-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue \
  --receipt-handle "RECEIPT_HANDLE"

aws sqs delete-message-batch \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue \
  --entries '[
    {"Id":"1","ReceiptHandle":"HANDLE_1"},
    {"Id":"2","ReceiptHandle":"HANDLE_2"}
  ]'

aws sqs change-message-visibility \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue \
  --receipt-handle "RECEIPT_HANDLE" \
  --visibility-timeout 120

# --- Permissions ---
aws sqs add-permission \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue \
  --label AllowSNS \
  --aws-account-ids 123456789012 \
  --actions SendMessage

aws sqs remove-permission \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue \
  --label AllowSNS

# --- DLQ redrive ---
aws sqs list-dead-letter-source-queues \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-dlq

aws sqs start-message-move-task \
  --source-arn arn:aws:sqs:us-east-1:123456789012:my-dlq \
  --destination-arn arn:aws:sqs:us-east-1:123456789012:my-queue \
  --max-number-of-messages-per-second 5

aws sqs list-message-move-tasks \
  --source-arn arn:aws:sqs:us-east-1:123456789012:my-dlq

aws sqs cancel-message-move-task --task-handle TASK_HANDLE
```

---

## SNS

```bash
# --- Topics ---
aws sns create-topic --name my-topic
aws sns create-topic \
  --name my-topic.fifo \
  --attributes FifoTopic=true,ContentBasedDeduplication=true

aws sns list-topics
aws sns get-topic-attributes \
  --topic-arn arn:aws:sns:us-east-1:123456789012:my-topic

aws sns set-topic-attributes \
  --topic-arn arn:aws:sns:us-east-1:123456789012:my-topic \
  --attribute-name DisplayName \
  --attribute-value "My Application Topic"

aws sns delete-topic --topic-arn arn:aws:sns:us-east-1:123456789012:my-topic

# --- Subscriptions ---
# SQS subscription
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:my-topic \
  --protocol sqs \
  --notification-endpoint arn:aws:sqs:us-east-1:123456789012:my-queue

# Lambda subscription
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:my-topic \
  --protocol lambda \
  --notification-endpoint arn:aws:lambda:us-east-1:123456789012:function:my-function

# HTTP/S subscription
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:my-topic \
  --protocol https \
  --notification-endpoint https://api.example.com/sns-webhook

# Email subscription
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:my-topic \
  --protocol email \
  --notification-endpoint user@example.com

aws sns confirm-subscription \
  --topic-arn arn:aws:sns:us-east-1:123456789012:my-topic \
  --token "TOKEN_FROM_CONFIRMATION_MESSAGE"

aws sns list-subscriptions-by-topic \
  --topic-arn arn:aws:sns:us-east-1:123456789012:my-topic

aws sns unsubscribe \
  --subscription-arn arn:aws:sns:us-east-1:123456789012:my-topic:SUBSCRIPTION_ID

# --- Message filtering ---
aws sns set-subscription-attributes \
  --subscription-arn arn:aws:sns:us-east-1:123456789012:my-topic:SUB_ID \
  --attribute-name FilterPolicy \
  --attribute-value '{"eventType":["order.created","order.updated"],"priority":["high"]}'

# Filter on message body (not just attributes)
aws sns set-subscription-attributes \
  --subscription-arn arn:aws:sns:us-east-1:123456789012:my-topic:SUB_ID \
  --attribute-name FilterPolicyScope \
  --attribute-value MessageBody

aws sns get-subscription-attributes \
  --subscription-arn arn:aws:sns:us-east-1:123456789012:my-topic:SUB_ID

# --- Publishing ---
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:123456789012:my-topic \
  --message '{"orderId":"12345","status":"created"}' \
  --subject "Order Created" \
  --message-attributes '{
    "eventType": {"DataType":"String","StringValue":"order.created"},
    "priority": {"DataType":"String","StringValue":"high"}
  }'

# FIFO topic
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:123456789012:my-topic.fifo \
  --message '{"orderId":"12345"}' \
  --message-group-id "orders" \
  --message-deduplication-id "order-12345"

# Batch publish (up to 10 messages)
aws sns publish-batch \
  --topic-arn arn:aws:sns:us-east-1:123456789012:my-topic \
  --publish-batch-request-entries '[
    {"Id":"1","Message":"first message"},
    {"Id":"2","Message":"second message","Subject":"Alert"}
  ]'

# --- Permissions ---
aws sns add-permission \
  --topic-arn arn:aws:sns:us-east-1:123456789012:my-topic \
  --label AllowPublish \
  --aws-account-id 987654321098 \
  --action-name Publish

aws sns remove-permission \
  --topic-arn arn:aws:sns:us-east-1:123456789012:my-topic \
  --label AllowPublish

# --- Mobile push ---
aws sns create-platform-application \
  --name MyAndroidApp \
  --platform GCM \
  --attributes PlatformCredential=SERVER_KEY

aws sns create-platform-endpoint \
  --platform-application-arn arn:aws:sns:us-east-1:123456789012:app/GCM/MyAndroidApp \
  --token DEVICE_TOKEN

aws sns publish \
  --target-arn arn:aws:sns:us-east-1:123456789012:endpoint/GCM/MyAndroidApp/ENDPOINT_ID \
  --message '{"GCM":"{\"notification\":{\"title\":\"Hello\",\"body\":\"World\"}}"}'  \
  --message-structure json

# --- Data protection policy ---
aws sns put-data-protection-policy \
  --resource-arn arn:aws:sns:us-east-1:123456789012:my-topic \
  --data-protection-policy '{
    "Name":"block-pii",
    "Description":"Block PII in messages",
    "Version":"2021-06-01",
    "Statement":[{
      "Sid":"block-pii-inbound",
      "DataDirection":"Inbound",
      "Principal":["*"],
      "DataIdentifier":["arn:aws:dataprotection::aws:data-identifier/CreditCardNumber"],
      "Operation":{"Deny":{}}
    }]
  }'

aws sns get-data-protection-policy \
  --resource-arn arn:aws:sns:us-east-1:123456789012:my-topic
```
