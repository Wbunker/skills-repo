# AWS Lambda Foundations
## Chapters 1–2: Serverless Concepts, Lambda Overview, Development Setup

---

## What Is Serverless?

Serverless is a deployment and execution model, not an absence of servers. The defining characteristics:

| Property | Description |
|----------|-------------|
| No server management | You do not provision, patch, or operate VMs or containers |
| Usage-based pricing | Pay per invocation and duration, not for idle capacity |
| Auto-scaling | Platform scales from 0 to thousands of instances automatically |
| Managed availability | High availability is the platform's responsibility |

### BaaS vs. FaaS

**Backend as a Service (BaaS)**: Managed third-party services replacing custom server-side code. Examples: Firebase, Cognito, S3, DynamoDB. You configure, not code, the backend.

**Functions as a Service (FaaS)**: Your code runs in short-lived, stateless functions managed by the platform. AWS Lambda is the canonical FaaS implementation.

A modern serverless application typically combines both: FaaS for custom logic, BaaS for infrastructure concerns.

### Serverless Tradeoffs

**Benefits:**
- Reduced operational overhead (no fleet management)
- Zero-cost when idle
- Elastic scaling without pre-provisioning
- Pay-per-use aligns cost with value delivered

**Limitations:**
- Cold starts add latency (see `advanced-lambda.md`)
- 15-minute maximum execution duration
- Limited local state (ephemeral /tmp only)
- Vendor lock-in risk
- Debugging and local development are harder
- Not suited for long-running, CPU-intensive, or ultra-low-latency workloads

---

## AWS Overview

### Regions and Availability Zones

- **Region**: Independent geographic area (e.g., `us-east-1`, `eu-west-1`). Regions are isolated; data does not cross regions unless you configure replication.
- **Availability Zone (AZ)**: One or more data centers within a region with independent power/networking. Lambda automatically distributes across AZs.

**Choosing a region**: Collocate Lambda with dependent services (DynamoDB, S3, etc.) to minimize latency and data transfer costs.

### Identity and Access Management (IAM)

Lambda interacts with IAM in two distinct roles:

| Role | Purpose |
|------|---------|
| **Execution Role** | The role your Lambda *function* assumes at runtime. Grants permissions to call other AWS services (S3, DynamoDB, SNS, etc.). |
| **Resource Policy** | Attached to the Lambda function itself. Controls which AWS services or accounts may *invoke* the function. |

**Principle of least privilege**: grant only the permissions the function actually uses. Use IAM condition keys to restrict by resource ARN, not `"Resource": "*"`.

### How to Interact with AWS

| Method | Use Case |
|--------|----------|
| AWS Console | Manual exploration, one-off tasks |
| AWS CLI | Scripting, quick commands, CI/CD steps |
| AWS SDKs (Java, Python, etc.) | Application code calling AWS APIs |
| CloudFormation / SAM | Infrastructure as Code (recommended for Lambda) |
| CDK | Higher-level IaC using programming languages |

---

## What Is AWS Lambda?

Lambda is AWS's FaaS implementation. Key facts:

- **Handler**: A Java method you write; Lambda calls it per invocation.
- **Runtime**: Managed JVM provided by AWS (Corretto 11, Corretto 17, etc.).
- **Execution environment**: A containerized sandbox (Firecracker microVM). Lambda may reuse it across invocations (warm) or create a new one (cold start).
- **Trigger**: Any event source that invokes your function (HTTP via API Gateway, file upload to S3, record added to Kinesis, etc.).

### Lambda Function vs. Lambda Application

- **Function**: Single unit of deployment — one JAR/ZIP, one handler class/method.
- **Application**: Multiple Lambda functions plus supporting AWS resources (DynamoDB tables, S3 buckets, API Gateway APIs), coordinated via CloudFormation/SAM.

---

## Development Environment Setup

### Prerequisites

```
Java 11+ (Amazon Corretto recommended)
Apache Maven or Gradle
AWS CLI v2
AWS SAM CLI
An AWS account with appropriate IAM permissions
```

### AWS CLI Setup

```bash
# Configure credentials (stored in ~/.aws/credentials)
aws configure
# AWS Access Key ID: <your key>
# AWS Secret Access Key: <your secret>
# Default region name: us-east-1
# Default output format: json

# Verify
aws sts get-caller-identity
```

### AWS SAM CLI

SAM (Serverless Application Model) is an open-source framework that extends CloudFormation with Lambda-specific resource types and local testing tools.

```bash
# Install (Linux/macOS)
pip install aws-sam-cli

# Verify
sam --version
```

### Hello World: Fastest Path

1. In the AWS Console, navigate to Lambda → Create function → Author from scratch
2. Runtime: Java 11 (Corretto)
3. Paste handler code inline (limited but works for quick experiments)
4. Test with a sample event payload

### Hello World: Proper Way (SAM)

```bash
# Initialize a Java Lambda project
sam init --runtime java11 --dependency-manager maven \
         --app-template hello-world --name my-lambda-app

# Project structure created:
# my-lambda-app/
#   template.yaml          ← SAM/CloudFormation template
#   HelloWorldFunction/
#     pom.xml
#     src/main/java/.../App.java    ← your handler
#     src/test/java/.../AppTest.java
```

**Minimal `pom.xml` dependencies:**

```xml
<dependencies>
  <!-- Lambda Java runtime interface -->
  <dependency>
    <groupId>com.amazonaws</groupId>
    <artifactId>aws-lambda-java-core</artifactId>
    <version>1.2.2</version>
  </dependency>

  <!-- Optional: typed AWS event classes (S3Event, KinesisEvent, etc.) -->
  <dependency>
    <groupId>com.amazonaws</groupId>
    <artifactId>aws-lambda-java-events</artifactId>
    <version>3.11.0</version>
  </dependency>
</dependencies>
```

```bash
# Build
cd HelloWorldFunction && mvn package

# Deploy (guided, creates/updates CloudFormation stack)
sam deploy --guided

# Invoke locally
sam local invoke HelloWorldFunction --event events/event.json
```

---

## Lambda in the Java Ecosystem

Java has historically been less popular for Lambda than Node.js or Python due to cold start overhead from JVM startup. However, Java remains common in enterprises for:

- Teams with deep Java expertise
- Applications already written in Java
- Use cases where warm-path latency matters more than cold-start latency
- Provisioned Concurrency mitigating cold starts

**Java runtimes available on Lambda (as of book):**
- Java 8 (OpenJDK)
- Java 8 on Amazon Corretto
- Java 11 on Amazon Corretto

**Recommended**: Java 11 on Corretto. Corretto is AWS's production-ready OpenJDK distribution.
