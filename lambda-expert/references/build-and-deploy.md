# Build and Deploy AWS Lambda Functions
## Chapter 4: Packaging, SAM Templates, CloudFormation, IAM, Deployment

---

## Build and Package

Lambda requires a self-contained deployment artifact. The JVM runtime does not fetch dependencies at runtime — everything must be bundled.

### Option 1: Uber JAR (Fat JAR) with Maven Shade Plugin

All classes and dependencies are merged into a single JAR. This is the simplest and most common approach.

```xml
<!-- pom.xml -->
<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-shade-plugin</artifactId>
      <version>3.3.0</version>
      <configuration>
        <createDependencyReducedPom>false</createDependencyReducedPom>
      </configuration>
      <executions>
        <execution>
          <phase>package</phase>
          <goals><goal>shade</goal></goals>
        </execution>
      </executions>
    </plugin>
  </plugins>
</build>
```

```bash
mvn package
# Produces: target/my-function-1.0.jar (uber JAR)
```

**Limitations of uber JARs:**
- Merge conflicts: two dependencies with same class path → one wins silently.
- Signed JARs break when merged (signatures become invalid). Use `<filters>` to exclude `META-INF/*.SF`, `META-INF/*.DSA`, `META-INF/*.RSA`.

```xml
<configuration>
  <filters>
    <filter>
      <artifact>*:*</artifact>
      <excludes>
        <exclude>META-INF/*.SF</exclude>
        <exclude>META-INF/*.DSA</exclude>
        <exclude>META-INF/*.RSA</exclude>
      </excludes>
    </filter>
  </filters>
</configuration>
```

### Option 2: ZIP File (Classes + lib/)

Separate your compiled classes from dependency JARs. Lambda supports this structure:

```
my-function.zip
├── com/example/MyHandler.class
├── com/example/model/...
└── lib/
    ├── aws-lambda-java-core-1.2.2.jar
    ├── jackson-databind-2.13.0.jar
    └── ...
```

**Maven Assembly Plugin** can produce this layout:

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-assembly-plugin</artifactId>
  <configuration>
    <descriptors>
      <descriptor>src/assembly/zip.xml</descriptor>
    </descriptors>
  </configuration>
  <executions>
    <execution>
      <phase>package</phase>
      <goals><goal>single</goal></goals>
    </execution>
  </executions>
</plugin>
```

### Reproducible Builds

Lambda deployment packages are compared by hash for change detection (CloudFormation/SAM skip re-deploy if hash unchanged). Ensure reproducible builds:

```xml
<!-- Maven 3.2+ reproducible builds -->
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-jar-plugin</artifactId>
  <configuration>
    <archive>
      <manifestEntries>
        <Build-Jdk-Spec>${java.specification.version}</Build-Jdk-Spec>
      </manifestEntries>
    </archive>
  </configuration>
</plugin>
```

Set `project.build.outputTimestamp` in `pom.xml` to a fixed date for fully reproducible JARs.

### Multiple Modules

For a multi-Lambda application, each function should have its own Maven module with its own deployment artifact. A parent POM aggregates them:

```
my-app/
  pom.xml              ← parent POM (packaging=pom, lists modules)
  order-function/
    pom.xml
    src/...
  payment-function/
    pom.xml
    src/...
  template.yaml        ← SAM template referencing both
```

Build all at once: `mvn package` from parent directory.

---

## Infrastructure as Code: SAM and CloudFormation

### Why IaC?

Manual console configuration is error-prone, undocumented, and non-reproducible. IaC:
- Version-controls your infrastructure alongside your code
- Enables environment parity (dev/staging/prod from same template)
- Provides rollback on deployment failure
- Makes peer review of infrastructure changes possible

### AWS CloudFormation

CloudFormation is the AWS native IaC service. You describe resources in JSON or YAML; CloudFormation provisions and manages them.

```yaml
# Raw CloudFormation Lambda resource
Resources:
  MyFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: my-function
      Runtime: java11
      Handler: com.example.MyHandler::handleRequest
      Code:
        S3Bucket: my-deployment-bucket
        S3Key: my-function-1.0.jar
      Role: !GetAtt MyExecutionRole.Arn
      MemorySize: 512
      Timeout: 30
```

### AWS Serverless Application Model (SAM)

SAM is a superset of CloudFormation with shorthand for Lambda-specific resources. SAM templates are valid CloudFormation (SAM CLI transforms them before deployment).

```yaml
# template.yaml (SAM format)
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Runtime: java11
    MemorySize: 512
    Timeout: 30
    Environment:
      Variables:
        LOG_LEVEL: INFO

Resources:
  OrderFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: com.example.OrderHandler::handleRequest
      CodeUri: order-function/target/order-function-1.0.jar
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /orders
            Method: post
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref OrdersTable

  OrdersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: orders
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: orderId
          AttributeType: S
      KeySchema:
        - AttributeName: orderId
          KeyType: HASH

Outputs:
  ApiUrl:
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/orders"
```

### SAM Deployment Workflow

```bash
# 1. Build (runs mvn package / gradle build per CodeUri)
sam build

# 2. First-time guided deploy (saves config to samconfig.toml)
sam deploy --guided

# 3. Subsequent deploys (uses samconfig.toml)
sam deploy

# 4. Delete stack
sam delete
```

`sam deploy` stages artifacts to S3, runs CloudFormation change set, and applies the diff.

### SAM Policy Templates

SAM provides canned IAM policy templates for common patterns:

| SAM Policy | What It Grants |
|------------|----------------|
| `DynamoDBCrudPolicy` | Read/write to a specific DynamoDB table |
| `DynamoDBReadPolicy` | Read-only on a specific DynamoDB table |
| `S3ReadPolicy` | GetObject on a specific S3 bucket |
| `S3CrudPolicy` | CRUD on a specific S3 bucket |
| `SQSSendMessagePolicy` | SendMessage to a specific SQS queue |
| `SNSPublishMessagePolicy` | Publish to a specific SNS topic |
| `SSMParameterReadPolicy` | GetParameter for a specific parameter path |

---

## IAM and Security

### Execution Role

Every Lambda function must have an IAM execution role. Lambda assumes this role when invoking your function.

**Minimum required permissions** (CloudWatch Logs):
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ],
    "Resource": "arn:aws:logs:*:*:*"
  }]
}
```

Add resource-specific permissions for each AWS service the function calls.

### Principle of Least Privilege

- Grant access to specific resources by ARN, not `"Resource": "*"`
- Use separate execution roles for each function
- Audit permissions with IAM Access Analyzer
- Rotate credentials; Lambda uses temporary STS credentials — never hardcode keys

```yaml
# SAM: inline policy instead of SAM policy template
Policies:
  - Statement:
    - Effect: Allow
      Action:
        - dynamodb:GetItem
        - dynamodb:PutItem
      Resource: !GetAtt OrdersTable.Arn
```

### Resource Policy (Who Can Invoke)

A Lambda resource policy controls what external principals (other accounts, services) may invoke the function.

```bash
# Allow API Gateway to invoke your function
aws lambda add-permission \
  --function-name my-function \
  --statement-id allow-api-gateway \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:123456789:abc123/*/POST/orders"
```

SAM's `Events` property generates resource policies automatically.

### Secrets Management

Never put secrets (DB passwords, API keys) in environment variables as plaintext. Use:

1. **AWS Secrets Manager**: Store secret; retrieve via SDK in Lambda init phase:

```java
private static final String DB_PASSWORD = getSecret("prod/db/password");

private static String getSecret(String secretId) {
    AWSSecretsManager client = AWSSecretsManagerClientBuilder.defaultClient();
    GetSecretValueRequest req = new GetSecretValueRequest().withSecretId(secretId);
    return client.getSecretValue(req).getSecretString();
}
```

2. **SSM Parameter Store** (simpler, lower cost for non-secrets): Use `SecureString` type for encrypted values.

Cache secrets in static fields. They are fetched once per cold start, not per invocation.

---

## Deployment Best Practices

| Practice | Reason |
|----------|--------|
| Deploy via SAM/CloudFormation, not manually | Reproducibility, rollback, code review |
| Use `sam build` before `sam deploy` | Ensures fresh artifacts |
| Store `samconfig.toml` in version control | Team consistency |
| Use separate stacks per environment | Isolation between dev/staging/prod |
| Enable CloudFormation stack termination protection (prod) | Prevent accidental deletion |
| Tag all resources | Cost allocation, ownership tracking |
| Pin dependency versions in `pom.xml` | Reproducible builds |
