# AWS DynamoDB — CLI Reference
For service concepts, see [dynamodb-capabilities.md](dynamodb-capabilities.md).

## Amazon DynamoDB

```bash
# --- Table Management ---
aws dynamodb create-table \
  --table-name Users \
  --attribute-definitions \
      AttributeName=UserId,AttributeType=S \
      AttributeName=Email,AttributeType=S \
  --key-schema \
      AttributeName=UserId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes '[
    {
      "IndexName": "EmailIndex",
      "KeySchema": [{"AttributeName":"Email","KeyType":"HASH"}],
      "Projection": {"ProjectionType":"ALL"}
    }
  ]'

# Provisioned capacity table with LSI
aws dynamodb create-table \
  --table-name Orders \
  --attribute-definitions \
      AttributeName=CustomerId,AttributeType=S \
      AttributeName=OrderId,AttributeType=S \
      AttributeName=CreatedAt,AttributeType=S \
  --key-schema \
      AttributeName=CustomerId,KeyType=HASH \
      AttributeName=OrderId,KeyType=RANGE \
  --billing-mode PROVISIONED \
  --provisioned-throughput ReadCapacityUnits=10,WriteCapacityUnits=10 \
  --local-secondary-indexes '[
    {
      "IndexName": "CreatedAtIndex",
      "KeySchema": [
        {"AttributeName":"CustomerId","KeyType":"HASH"},
        {"AttributeName":"CreatedAt","KeyType":"RANGE"}
      ],
      "Projection": {"ProjectionType":"KEYS_ONLY"}
    }
  ]'

aws dynamodb list-tables
aws dynamodb describe-table --table-name Users

aws dynamodb update-table \
  --table-name Users \
  --billing-mode PAY_PER_REQUEST
  # or switch to provisioned:
  # --billing-mode PROVISIONED \
  # --provisioned-throughput ReadCapacityUnits=100,WriteCapacityUnits=50

# Enable TTL
aws dynamodb update-time-to-live \
  --table-name Sessions \
  --time-to-live-specification "Enabled=true,AttributeName=ExpiresAt"

aws dynamodb delete-table --table-name Users

# --- Item Operations ---
aws dynamodb put-item \
  --table-name Users \
  --item '{"UserId":{"S":"u001"},"Email":{"S":"alice@example.com"},"Age":{"N":"30"}}'

aws dynamodb get-item \
  --table-name Users \
  --key '{"UserId":{"S":"u001"}}' \
  --consistent-read

aws dynamodb update-item \
  --table-name Users \
  --key '{"UserId":{"S":"u001"}}' \
  --update-expression "SET #age = :newage, UpdatedAt = :ts" \
  --expression-attribute-names '{"#age":"Age"}' \
  --expression-attribute-values '{":newage":{"N":"31"},":ts":{"S":"2024-01-15T10:00:00Z"}}' \
  --return-values ALL_NEW

aws dynamodb delete-item \
  --table-name Users \
  --key '{"UserId":{"S":"u001"}}' \
  --condition-expression "attribute_exists(UserId)"

# --- Query and Scan ---
# Query by partition key
aws dynamodb query \
  --table-name Orders \
  --key-condition-expression "CustomerId = :cid" \
  --expression-attribute-values '{":cid":{"S":"c001"}}' \
  --limit 20

# Query GSI with filter
aws dynamodb query \
  --table-name Users \
  --index-name EmailIndex \
  --key-condition-expression "Email = :email" \
  --expression-attribute-values '{":email":{"S":"alice@example.com"}}'

# Scan with filter (use sparingly on large tables)
aws dynamodb scan \
  --table-name Users \
  --filter-expression "Age > :minage" \
  --expression-attribute-values '{":minage":{"N":"25"}}' \
  --projection-expression "UserId, Email, Age"

# Parallel scan (segment 0 of 4)
aws dynamodb scan \
  --table-name Users \
  --total-segments 4 \
  --segment 0

# --- Batch Operations ---
aws dynamodb batch-get-item \
  --request-items '{
    "Users": {
      "Keys": [
        {"UserId":{"S":"u001"}},
        {"UserId":{"S":"u002"}}
      ],
      "ConsistentRead": true
    }
  }'

aws dynamodb batch-write-item \
  --request-items '{
    "Users": [
      {"PutRequest": {"Item": {"UserId":{"S":"u003"},"Email":{"S":"bob@example.com"}}}},
      {"DeleteRequest": {"Key": {"UserId":{"S":"u001"}}}}
    ]
  }'

# --- Transactions ---
aws dynamodb transact-write-items \
  --transact-items '[
    {
      "Put": {
        "TableName": "Orders",
        "Item": {"CustomerId":{"S":"c001"},"OrderId":{"S":"o001"},"Status":{"S":"PLACED"}},
        "ConditionExpression": "attribute_not_exists(OrderId)"
      }
    },
    {
      "Update": {
        "TableName": "Inventory",
        "Key": {"ItemId":{"S":"item001"}},
        "UpdateExpression": "SET Quantity = Quantity - :qty",
        "ExpressionAttributeValues": {":qty":{"N":"1"},":zero":{"N":"0"}},
        "ConditionExpression": "Quantity > :zero"
      }
    }
  ]'

aws dynamodb transact-get-items \
  --transact-items '[
    {"Get": {"TableName":"Orders","Key":{"CustomerId":{"S":"c001"},"OrderId":{"S":"o001"}}}},
    {"Get": {"TableName":"Users","Key":{"UserId":{"S":"u001"}}}}
  ]'

# --- PartiQL ---
aws dynamodb execute-statement \
  --statement "SELECT * FROM Users WHERE UserId = 'u001'"

aws dynamodb batch-execute-statement \
  --statements '[
    {"Statement":"SELECT * FROM Users WHERE UserId = ?","Parameters":[{"S":"u001"}]},
    {"Statement":"SELECT * FROM Users WHERE UserId = ?","Parameters":[{"S":"u002"}]}
  ]'

# --- Backups ---
aws dynamodb create-backup \
  --table-name Users \
  --backup-name users-backup-$(date +%Y%m%d)

aws dynamodb list-backups --table-name Users
aws dynamodb describe-backup --backup-arn arn:aws:dynamodb:us-east-1:123456789012:table/Users/backup/01234567890

aws dynamodb restore-table-from-backup \
  --target-table-name Users-Restored \
  --backup-arn arn:aws:dynamodb:us-east-1:123456789012:table/Users/backup/01234567890

# Point-in-time recovery
aws dynamodb update-continuous-backups \
  --table-name Users \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true

aws dynamodb restore-table-to-point-in-time \
  --source-table-name Users \
  --target-table-name Users-PITR \
  --restore-date-time 2024-01-15T10:30:00Z

# Export to S3
aws dynamodb export-table-to-point-in-time \
  --table-arn arn:aws:dynamodb:us-east-1:123456789012:table/Users \
  --s3-bucket my-exports-bucket \
  --s3-prefix dynamodb/users/ \
  --export-time 2024-01-15T10:00:00Z \
  --export-format DYNAMODB_JSON

aws dynamodb list-exports --table-arn arn:aws:dynamodb:us-east-1:123456789012:table/Users

# --- Global Tables ---
aws dynamodb create-global-table \
  --global-table-name Users \
  --replication-group '[{"RegionName":"us-east-1"},{"RegionName":"eu-west-1"}]'

aws dynamodb describe-global-table --global-table-name Users
aws dynamodb list-global-tables

aws dynamodb update-global-table \
  --global-table-name Users \
  --replica-updates '[{"Create":{"RegionName":"ap-southeast-1"}}]'

# --- Streams ---
aws dynamodb update-table \
  --table-name Users \
  --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES

aws dynamodb describe-table --table-name Users  # check LatestStreamArn

# Enable Kinesis streaming destination
aws dynamodb enable-kinesis-streaming-destination \
  --table-name Users \
  --stream-arn arn:aws:kinesis:us-east-1:123456789012:stream/dynamodb-stream

aws dynamodb disable-kinesis-streaming-destination \
  --table-name Users \
  --stream-arn arn:aws:kinesis:us-east-1:123456789012:stream/dynamodb-stream

# --- Table Class ---
aws dynamodb update-table \
  --table-name OldData \
  --table-class STANDARD_INFREQUENT_ACCESS

# --- Auto Scaling ---
aws application-autoscaling register-scalable-target \
  --service-namespace dynamodb \
  --resource-id "table/Users" \
  --scalable-dimension dynamodb:table:ReadCapacityUnits \
  --min-capacity 5 \
  --max-capacity 1000

aws application-autoscaling put-scaling-policy \
  --service-namespace dynamodb \
  --resource-id "table/Users" \
  --scalable-dimension dynamodb:table:ReadCapacityUnits \
  --policy-name UsersReadScaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {"PredefinedMetricType":"DynamoDBReadCapacityUtilization"}
  }'
```
