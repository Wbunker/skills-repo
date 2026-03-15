# AWS Runtime & Testing — CLI Reference

For service concepts, see [runtime-testing-capabilities.md](runtime-testing-capabilities.md).

---

## Amazon Corretto

Amazon Corretto is a JDK distribution, not an AWS service with a CLI namespace. There is no `aws corretto` CLI command. Corretto is installed and managed as a system package or Docker image.

```bash
# --- Installation (Amazon Linux 2) ---
# Install Corretto 17 JDK (compiler + runtime)
sudo yum install -y java-17-amazon-corretto-devel

# Install Corretto 21 JDK
sudo yum install -y java-21-amazon-corretto-devel

# Install Corretto 11 JDK
sudo yum install -y java-11-amazon-corretto-devel

# --- Installation (Amazon Linux 2023) ---
sudo dnf install -y java-21-amazon-corretto-devel
sudo dnf install -y java-17-amazon-corretto-devel

# --- Installation (Ubuntu/Debian) ---
wget -O - https://apt.corretto.aws/corretto.key | sudo gpg --dearmor -o /usr/share/keyrings/corretto-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/corretto-keyring.gpg] https://apt.corretto.aws stable main" | sudo tee /etc/apt/sources.list.d/corretto.list
sudo apt-get update
sudo apt-get install -y java-21-amazon-corretto-jdk

# --- Installation (macOS) ---
brew tap homebrew/cask-versions
brew install --cask corretto21   # or corretto17, corretto11

# --- Version Management ---
# List installed Java versions
java -version
javac -version

# Switch Java version (Amazon Linux / RHEL)
sudo alternatives --config java
sudo alternatives --config javac

# Set JAVA_HOME
export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))
echo "export JAVA_HOME=$JAVA_HOME" >> ~/.bashrc

# --- Docker ---
# Run a container with Corretto 21
docker run --rm public.ecr.aws/amazoncorretto/amazoncorretto:21 java -version

# Use in a Dockerfile
# FROM public.ecr.aws/amazoncorretto/amazoncorretto:21
# COPY target/app.jar /app/app.jar
# CMD ["java", "-jar", "/app/app.jar"]

# --- Lambda Runtime Reference (no CLI needed, specified in function config) ---
# java8.al2   → Corretto 8 on Amazon Linux 2
# java11      → Corretto 11 on Amazon Linux 2
# java17      → Corretto 17 on Amazon Linux 2023
# java21      → Corretto 21 on Amazon Linux 2023
aws lambda create-function \
  --function-name my-java-function \
  --runtime java21 \
  --handler com.example.Handler::handleRequest \
  --role arn:aws:iam::123456789012:role/LambdaRole \
  --zip-file fileb://function.zip
```

---

## AWS X-Ray

For full CLI reference, see [management-devops/xray-fis-cli.md](../management-devops/xray-fis-cli.md).

Key commands for common X-Ray tasks:

```bash
# --- Search Traces ---
# Find traces with errors in the last hour
aws xray get-trace-summaries \
  --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --filter-expression 'error = true'

# Find slow traces (response time > 5 seconds)
aws xray get-trace-summaries \
  --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --filter-expression 'responsetime > 5'

# Get full trace detail (segments and subsegments)
aws xray batch-get-traces \
  --trace-ids 1-58406520-a006649127e371903a2de979

# --- Service Map ---
# Get service map for the last 30 minutes
aws xray get-service-graph \
  --start-time $(date -u -v-30M +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ)

# --- Sampling Rules ---
# List current sampling rules
aws xray get-sampling-rules

# Create a custom sampling rule (100% sampling for /checkout endpoint)
aws xray create-sampling-rule \
  --sampling-rule '{
    "RuleName": "CheckoutAlways",
    "Priority": 1,
    "FixedRate": 1.0,
    "ReservoirSize": 100,
    "ServiceName": "checkout-service",
    "ServiceType": "*",
    "Host": "*",
    "HTTPMethod": "POST",
    "URLPath": "/checkout",
    "ResourceARN": "*",
    "Version": 1
  }'

# Delete a sampling rule
aws xray delete-sampling-rule --rule-name CheckoutAlways

# --- Groups ---
# Create a trace group for production errors
aws xray create-group \
  --group-name prod-errors \
  --filter-expression 'error = true AND service("api-service")' \
  --insights-configuration InsightsEnabled=true,NotificationsEnabled=true

# List groups
aws xray get-groups

# Delete a group
aws xray delete-group --group-name prod-errors
```

---

## AWS Fault Injection Service (FIS)

For full CLI reference, see [management-devops/xray-fis-cli.md](../management-devops/xray-fis-cli.md).

Key commands for common FIS tasks:

```bash
# --- Discover Available Actions ---
# List all available FIS fault actions
aws fis list-actions

# Get details of a specific action (parameters, targets)
aws fis get-action --id aws:ec2:terminate-instances
aws fis get-action --id aws:lambda:inject-api-internal-error
aws fis get-action --id aws:ecs:stop-task

# --- Create an Experiment Template ---
# Inject Lambda errors for 5 minutes with a CloudWatch stop condition
aws fis create-experiment-template \
  --description "Inject Lambda errors in staging" \
  --stop-conditions '[{
    "source": "aws:cloudwatch:alarm",
    "value": "arn:aws:cloudwatch:us-east-1:123456789012:alarm:staging-error-rate-high"
  }]' \
  --targets '{
    "lambdaFunctions": {
      "resourceType": "aws:lambda:function",
      "resourceTags": {"Env": "staging"},
      "selectionMode": "ALL"
    }
  }' \
  --actions '{
    "injectErrors": {
      "actionId": "aws:lambda:inject-api-internal-error",
      "parameters": {"duration": "PT5M", "percentage": "25"},
      "targets": {"Functions": "lambdaFunctions"}
    }
  }' \
  --role-arn arn:aws:iam::123456789012:role/FISRole

# --- Run an Experiment ---
# Start an experiment
aws fis start-experiment \
  --experiment-template-id EXT123456789ABCDEF \
  --tags Name=lambda-error-injection-test

# Monitor experiment status
aws fis get-experiment --id EXP123456789ABCDEF

# Stop an experiment early
aws fis stop-experiment --id EXP123456789ABCDEF

# List recent experiments
aws fis list-experiments

# --- Manage Templates ---
# List experiment templates
aws fis list-experiment-templates

# Delete an experiment template
aws fis delete-experiment-template --id EXT123456789ABCDEF
```
