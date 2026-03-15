# AWS SAM — CLI Reference

For service concepts, see [sam-capabilities.md](sam-capabilities.md).

## Installation & Version

```bash
# Install SAM CLI (macOS)
brew install aws-sam-cli

# Verify installation
sam --version

# Upgrade SAM CLI (macOS)
brew upgrade aws-sam-cli
```

---

## sam init — Scaffold a new project

```bash
# Interactive project scaffold (prompts for runtime, template, etc.)
sam init

# Non-interactive: Hello World in Python 3.12 using the quick-start template
sam init \
  --runtime python3.12 \
  --name my-api \
  --app-template hello-world \
  --no-interactive

# Non-interactive: Node.js with TypeScript
sam init \
  --runtime nodejs20.x \
  --name my-api \
  --app-template hello-world \
  --package-type Zip \
  --no-interactive

# Initialize from a custom template location
sam init --location gh:aws-samples/aws-sam-java-rest
```

---

## sam build — Compile and package

```bash
# Build all functions (reads template.yaml in current directory)
sam build

# Build with caching (skip unchanged functions)
sam build --cached

# Build in parallel (faster for multi-function apps)
sam build --cached --parallel

# Build using a container (matches Lambda runtime environment; requires Docker)
sam build --use-container

# Build a specific function
sam build MyFunction

# Build from a specific template file
sam build --template-file infra/template.yaml

# Build and output to a specific directory
sam build --build-dir .build

# Pass build parameters to the underlying build tool
sam build --parameter-overrides Env=prod
```

---

## sam local — Local testing with Docker

```bash
# --- sam local invoke ---
# Invoke a function once with an inline event
sam local invoke MyFunction --event events/s3-put.json

# Invoke with an empty event
sam local invoke MyFunction --event '{}' --no-event

# Pass environment variable overrides
sam local invoke MyFunction \
  --event events/api-gw.json \
  --env-vars env.json

# Invoke using a specific profile and region
sam local invoke MyFunction \
  --event events/test.json \
  --profile staging \
  --region us-east-1

# Invoke a function inside a SAR nested application
sam local invoke "NestedApp/ChildFunction" --event events/test.json

# Debug: attach a debugger on port 5858 (Node.js)
sam local invoke MyFunction \
  --event events/test.json \
  --debug-port 5858

# --- sam local start-api ---
# Start local API Gateway emulator (REST API)
sam local start-api

# Start on a specific port
sam local start-api --port 3000

# Hot-reload on code changes (no rebuild needed for interpreted runtimes)
sam local start-api --warm-containers EAGER

# Pass static environment variables
sam local start-api --env-vars env.json

# Override specific parameter values
sam local start-api --parameter-overrides TableName=local-table

# --- sam local start-lambda ---
# Start local Lambda endpoint (compatible with AWS SDK endpoint-url)
sam local start-lambda

# Start on a specific port
sam local start-lambda --port 3001

# Then invoke via AWS SDK or CLI:
# aws lambda invoke --function-name MyFunction \
#   --endpoint-url http://127.0.0.1:3001 \
#   --payload '{}' response.json

# --- sam local generate-event ---
# List all supported event sources
sam local generate-event

# Generate an S3 PutObject event
sam local generate-event s3 put \
  --bucket my-bucket \
  --key uploads/photo.jpg

# Generate an API Gateway event
sam local generate-event apigateway aws-proxy \
  --method POST \
  --path /orders \
  --body '{"item":"widget"}'

# Generate an SQS event with a specific message body
sam local generate-event sqs receive-message \
  --body '{"orderId":"123"}'

# Generate and pipe directly into invoke
sam local generate-event s3 put | sam local invoke ProcessS3Function
```

---

## sam deploy — Deploy to AWS

```bash
# First-time interactive deploy (prompts for stack name, region, S3 bucket, capabilities)
# Writes answers to samconfig.toml for subsequent runs
sam deploy --guided

# Deploy using saved samconfig.toml (CI/CD non-interactive)
sam deploy

# Deploy a specific stack name
sam deploy --stack-name prod-my-api

# Deploy to a specific region with a specific profile
sam deploy \
  --stack-name prod-my-api \
  --region us-east-1 \
  --profile prod-account

# Override template parameters at deploy time
sam deploy \
  --parameter-overrides \
    Env=prod \
    LogRetentionDays=90 \
    TableName=orders-prod

# Auto-confirm changeset without review (CI/CD pipelines)
sam deploy --no-confirm-changeset

# Disable rollback on failure (keep partial resources for debugging)
sam deploy --disable-rollback

# Deploy with a named config environment from samconfig.toml
sam deploy --config-env prod

# Build and deploy in a single step
sam build && sam deploy

# Upload large artifacts to a specific S3 prefix
sam deploy \
  --s3-bucket my-artifacts-bucket \
  --s3-prefix my-app/v2

# Deploy an image-based (container) function
sam deploy \
  --image-repository 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app \
  --capabilities CAPABILITY_IAM
```

---

## sam sync — Accelerate iteration (hot sync)

```bash
# Sync code changes directly (bypasses CloudFormation for Lambda code/config)
sam sync --stack-name my-app-dev

# Watch mode: continuously sync on file-system changes
sam sync --stack-name my-app-dev --watch

# Sync only code changes (skip infrastructure/SAM template changes)
sam sync --stack-name my-app-dev --code

# Sync a specific resource
sam sync --stack-name my-app-dev --resource-id MyFunction

# Sync with a specific config environment
sam sync --stack-name my-app-dev --config-env dev

# Sync with AWS profile and region
sam sync \
  --stack-name my-app-dev \
  --region us-east-1 \
  --profile dev-account \
  --watch
```

---

## sam logs — Tail CloudWatch Logs

```bash
# Tail logs for a function (by logical resource ID in template)
sam logs --name MyFunction --stack-name my-app

# Tail in real time
sam logs --name MyFunction --stack-name my-app --tail

# Filter logs by a pattern
sam logs --name MyFunction --stack-name my-app --filter "ERROR"

# Retrieve logs for a specific time range
sam logs --name MyFunction \
  --stack-name my-app \
  --start-time "2026-03-14T10:00:00" \
  --end-time "2026-03-14T10:30:00"

# Show logs with X-Ray trace correlation
sam logs --name MyFunction --stack-name my-app --include-traces
```

---

## sam traces — View X-Ray traces

```bash
# Show recent X-Ray traces for the stack
sam traces --stack-name my-app

# Show traces in real time
sam traces --stack-name my-app --tail

# Filter traces by a condition (uses X-Ray filter expressions)
sam traces --stack-name my-app --filter-expression "responsetime > 1"
```

---

## sam package — Package artifacts to S3

```bash
# Package template (uploads local artifacts to S3, outputs deployable template)
sam package \
  --s3-bucket my-artifacts-bucket \
  --output-template-file packaged.yaml

# Package for a specific region
sam package \
  --s3-bucket my-artifacts-bucket \
  --s3-prefix my-app/v1 \
  --region us-east-1 \
  --output-template-file packaged.yaml

# Package image-based functions
sam package \
  --image-repository 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app \
  --output-template-file packaged.yaml
```

---

## sam publish — Publish to Serverless Application Repository

```bash
# Publish app to SAR (requires a packaged template with Metadata.SemanticVersion)
sam publish \
  --template packaged.yaml \
  --region us-east-1

# Publish to a specific SAR region
sam publish \
  --template packaged.yaml \
  --region us-east-1 \
  --semantic-version 1.2.0
```

---

## sam pipeline — Bootstrap CI/CD infrastructure

```bash
# Bootstrap pipeline IAM roles and artifacts bucket for a stage
sam pipeline bootstrap

# Non-interactive bootstrap for a dev stage using existing IAM role
sam pipeline bootstrap \
  --stage dev \
  --region us-east-1 \
  --pipeline-user arn:aws:iam::123456789012:user/pipeline-user

# Generate pipeline configuration files (GitHub Actions, CodePipeline, GitLab, etc.)
sam pipeline init

# Generate GitHub Actions pipeline config non-interactively
sam pipeline init \
  --bootstrap-stackout-name aws-sam-cli-managed-dev-pipeline-resources \
  --ci-cd-system github-actions \
  --stage dev
```

---

## sam validate — Validate a SAM template

```bash
# Validate template.yaml for syntax and schema errors
sam validate

# Validate a specific template file
sam validate --template-file infra/template.yaml

# Validate with lint rules (checks best practices beyond schema)
sam validate --lint
```

---

## sam delete — Delete a deployed stack

```bash
# Delete the stack and all its resources (interactive confirmation)
sam delete --stack-name my-app

# Delete without confirmation prompt
sam delete --stack-name my-app --no-prompts

# Delete and also remove the S3 artifacts bucket contents
sam delete \
  --stack-name my-app \
  --region us-east-1 \
  --no-prompts
```

---

## sam list — Inspect deployed resources

```bash
# List all resources in the deployed stack with their physical IDs
sam list resources --stack-name my-app

# List stack outputs (useful for finding API Gateway endpoint, etc.)
sam list stack-outputs --stack-name my-app

# List stack outputs as JSON
sam list stack-outputs --stack-name my-app --output json

# List endpoints (API Gateway + Lambda Function URLs)
sam list endpoints --stack-name my-app
```

---

## Common Workflows

```bash
# --- First-time setup ---
sam init
sam build
sam deploy --guided            # creates samconfig.toml

# --- Inner loop (interpreted runtimes: Python, Node.js) ---
sam local start-api            # start API emulator
# edit code → changes reflected immediately (no rebuild)

# --- Inner loop (compiled runtimes: Java, Go, .NET) ---
sam build --cached --parallel
sam local invoke MyFunction --event events/test.json

# --- Rapid cloud iteration ---
sam sync --stack-name my-app-dev --watch

# --- CI/CD pipeline step ---
sam build --cached --parallel
sam deploy --no-confirm-changeset --config-env prod

# --- Debugging production issues ---
sam logs --name MyFunction --stack-name my-app --tail --filter "ERROR"
sam traces --stack-name my-app --tail
```
