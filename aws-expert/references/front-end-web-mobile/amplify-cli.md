# AWS Amplify — CLI Reference

For service concepts, see [amplify-capabilities.md](amplify-capabilities.md).

## `aws amplify` — Amplify Hosting & Backend Environments (AWS CLI)

```bash
# --- Apps ---
# Create a new Amplify app connected to a Git repository
aws amplify create-app \
  --name my-app \
  --repository https://github.com/myorg/my-app \
  --access-token GITHUB_PAT \
  --platform WEB

# Create app for manual deploys (no Git)
aws amplify create-app \
  --name my-static-app \
  --platform WEB

aws amplify list-apps
aws amplify get-app --app-id APP_ID
aws amplify update-app --app-id APP_ID --name new-name
aws amplify delete-app --app-id APP_ID

# --- Branches ---
aws amplify create-branch \
  --app-id APP_ID \
  --branch-name main \
  --stage PRODUCTION \
  --enable-auto-build \
  --environment-variables KEY1=VALUE1,KEY2=VALUE2

aws amplify create-branch \
  --app-id APP_ID \
  --branch-name staging \
  --stage BETA \
  --enable-basic-auth \
  --basic-auth-credentials "$(echo -n 'user:password' | base64)"

aws amplify list-branches --app-id APP_ID
aws amplify get-branch --app-id APP_ID --branch-name main

aws amplify update-branch \
  --app-id APP_ID \
  --branch-name main \
  --enable-performance-mode \
  --framework "Next.js - SSR"

aws amplify delete-branch --app-id APP_ID --branch-name feature/old

# --- Deployments ---
# Start a manual deploy (for non-Git apps or manual ZIP deploys)
aws amplify start-deployment \
  --app-id APP_ID \
  --branch-name main

# Create deployment (get S3 upload URL for ZIP)
aws amplify create-deployment \
  --app-id APP_ID \
  --branch-name main
# Returns: jobId, zipUploadUrl — upload ZIP to zipUploadUrl then start deployment

aws amplify start-deployment \
  --app-id APP_ID \
  --branch-name main \
  --job-id JOB_ID

# List and inspect jobs
aws amplify list-jobs --app-id APP_ID --branch-name main
aws amplify get-job --app-id APP_ID --branch-name main --job-id JOB_ID

# Stop a running build
aws amplify stop-job --app-id APP_ID --branch-name main --job-id JOB_ID

# Retry last job
aws amplify start-job \
  --app-id APP_ID \
  --branch-name main \
  --job-type RETRY \
  --job-id JOB_ID

# --- Domain Associations ---
aws amplify create-domain-association \
  --app-id APP_ID \
  --domain-name example.com \
  --sub-domain-settings '[
    {"prefix":"","branchName":"main"},
    {"prefix":"www","branchName":"main"},
    {"prefix":"staging","branchName":"staging"}
  ]'

aws amplify get-domain-association --app-id APP_ID --domain-name example.com
aws amplify list-domain-associations --app-id APP_ID

aws amplify update-domain-association \
  --app-id APP_ID \
  --domain-name example.com \
  --sub-domain-settings '[{"prefix":"","branchName":"main"},{"prefix":"www","branchName":"main"}]'

aws amplify delete-domain-association --app-id APP_ID --domain-name example.com

# --- Webhooks (trigger builds from external systems) ---
aws amplify create-webhook \
  --app-id APP_ID \
  --branch-name main \
  --description "Trigger from external CI"

aws amplify list-webhooks --app-id APP_ID
aws amplify get-webhook --webhook-id WEBHOOK_ID
aws amplify delete-webhook --webhook-id WEBHOOK_ID

# --- Backend Environments (Gen 1) ---
aws amplify create-backend-environment \
  --app-id APP_ID \
  --environment-name prod \
  --stack-name amplify-myapp-prod \
  --deployment-artifacts "amplify-prod-deployment"

aws amplify list-backend-environments --app-id APP_ID
aws amplify get-backend-environment --app-id APP_ID --environment-name prod
aws amplify delete-backend-environment --app-id APP_ID --environment-name dev

# --- Build cache ---
# Delete build cache to force fresh install
aws amplify delete-job \
  --app-id APP_ID \
  --branch-name main \
  --job-id JOB_ID

# --- Artifacts ---
aws amplify list-artifacts \
  --app-id APP_ID \
  --branch-name main \
  --job-id JOB_ID \
  --artifact-type TEST

aws amplify get-artifact-url \
  --artifact-id ARTIFACT_ID

# --- Tags ---
aws amplify tag-resource \
  --resource-arn arn:aws:amplify:us-east-1:123456789012:apps/APP_ID \
  --tags Environment=production,Team=frontend

aws amplify list-tags-for-resource \
  --resource-arn arn:aws:amplify:us-east-1:123456789012:apps/APP_ID
```

---

## Amplify Gen 1 CLI (`amplify` command)

The `amplify` CLI is installed globally via npm and manages Gen 1 backend resources (CloudFormation-based).

```bash
# Install
npm install -g @aws-amplify/cli

# Initialize a new Amplify project in a repo
amplify init

# Add backend categories
amplify add auth          # Cognito User Pool + Identity Pool
amplify add api           # AppSync GraphQL or API Gateway REST
amplify add storage       # S3 bucket or DynamoDB table
amplify add function      # Lambda function
amplify add hosting       # Amplify Hosting or S3+CloudFront
amplify add analytics     # Pinpoint

# Deploy changes to cloud
amplify push              # Deploy all pending backend changes
amplify push --yes        # Skip confirmation prompts
amplify publish           # Build frontend + deploy backend + publish to hosting

# Environment management
amplify env add           # Create a new backend environment (e.g., staging)
amplify env list          # List all environments
amplify env checkout prod # Switch to a different environment
amplify env pull          # Pull the latest backend config for current env

# Pull existing project (for a new developer joining the team)
amplify pull --appId APP_ID --envName prod

# Code generation (GraphQL types, statements)
amplify codegen add       # Configure codegen for the project
amplify codegen           # Re-generate models/types from schema

# Status and config
amplify status            # Show pending changes by category
amplify console           # Open Amplify console in browser
amplify info              # Print system and project diagnostic info

# Remove resources
amplify remove auth       # Remove auth category
amplify delete            # Delete entire Amplify project (with CloudFormation stacks)
```

---

## Amplify Gen 2 CLI (`npx ampx` command)

`npx ampx` is the Gen 2 CLI, distributed as `@aws-amplify/backend-cli`. No global install required.

```bash
# --- Sandbox (personal dev environment) ---
# Deploy personal sandbox (watches for changes)
npx ampx sandbox

# Deploy sandbox once without watching
npx ampx sandbox --once

# Deploy sandbox for a specific named profile
npx ampx sandbox --profile my-aws-profile

# Delete your personal sandbox
npx ampx sandbox delete

# --- Code generation ---
# Generate amplify_outputs.json (client config) from deployed backend
npx ampx generate outputs \
  --app-id APP_ID \
  --branch main

# Generate TypeScript client types from schema
npx ampx generate graphql-client-code \
  --app-id APP_ID \
  --branch main \
  --format graphql-codegen

# Generate TypeScript types for Amplify Data models
npx ampx generate forms \
  --app-id APP_ID \
  --branch main

# --- Pipeline deployments (CI/CD) ---
# Used in CI pipelines before building the frontend
npx ampx pipeline-deploy \
  --app-id APP_ID \
  --branch main

# --- Info and diagnostics ---
npx ampx --version
npx ampx info
```
