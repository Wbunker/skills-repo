# AWS CDK — CLI Reference
For service concepts, see [cdk-capabilities.md](cdk-capabilities.md).

```bash
# Synthesize CloudFormation template(s) from CDK code
cdk synth

# Synthesize a specific stack
cdk synth MyStack

# Show diff between deployed stack and local code
cdk diff

# Diff a specific stack
cdk diff MyStack

# Deploy all stacks
cdk deploy

# Deploy a specific stack
cdk deploy MyStack

# Deploy with hotswap (skip CloudFormation for Lambda, ECS, Step Functions changes)
cdk deploy --hotswap

# Deploy with hotswap fallback (falls back to full CloudFormation if hotswap not possible)
cdk deploy --hotswap-fallback

# Watch mode (monitor source files and auto-deploy on changes)
cdk watch

# Watch a specific stack
cdk watch MyStack

# Bootstrap a target account/region (one-time setup)
cdk bootstrap

# Bootstrap a specific account and region
cdk bootstrap aws://123456789012/us-east-1

# Bootstrap with a custom qualifier
cdk bootstrap --qualifier myapp

# Bootstrap with trust for a pipeline account
cdk bootstrap \
  --trust 111122223333 \
  --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess

# Destroy a stack
cdk destroy MyStack

# Destroy without confirmation prompt
cdk destroy MyStack --force

# List all stacks in the app
cdk list
cdk ls

# Show the synthesized CloudFormation template
cdk synth MyStack --no-staging

# Pass context values
cdk deploy --context env=prod --context region=us-east-1

# Deploy all stacks matching a pattern
cdk deploy "MyApp/*"

# Acknowledge security-sensitive IAM/VPC changes (non-interactive)
cdk deploy --require-approval never

# Output CloudFormation template to a file
cdk synth MyStack > template.yaml

# Show metadata about the app
cdk metadata

# Acknowledge notices
cdk acknowledge <notice-id>

# Show version
cdk --version
```
