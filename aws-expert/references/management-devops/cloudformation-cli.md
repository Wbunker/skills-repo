# AWS CloudFormation — CLI Reference
For service concepts, see [cloudformation-capabilities.md](cloudformation-capabilities.md).

```bash
# --- Stacks ---
# Create a stack
aws cloudformation create-stack \
  --stack-name my-stack \
  --template-body file://template.yaml \
  --parameters ParameterKey=Env,ParameterValue=prod \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --tags Key=Project,Value=MyApp

# Update a stack
aws cloudformation update-stack \
  --stack-name my-stack \
  --template-body file://template.yaml \
  --parameters ParameterKey=Env,UsePreviousValue=true \
  --capabilities CAPABILITY_IAM

# Delete a stack
aws cloudformation delete-stack --stack-name my-stack

# Describe stacks
aws cloudformation describe-stacks --stack-name my-stack
aws cloudformation describe-stacks  # all stacks

# List stacks by status
aws cloudformation list-stacks \
  --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE

# Wait for stack operation to complete
aws cloudformation wait stack-create-complete --stack-name my-stack
aws cloudformation wait stack-update-complete --stack-name my-stack
aws cloudformation wait stack-delete-complete --stack-name my-stack

# Cancel an in-progress update
aws cloudformation cancel-update-stack --stack-name my-stack

# Continue rollback after a failed update
aws cloudformation continue-update-rollback --stack-name my-stack

# Get the stack policy
aws cloudformation get-stack-policy --stack-name my-stack

# Set a stack policy (prevent replacements/deletions)
aws cloudformation set-stack-policy \
  --stack-name my-stack \
  --stack-policy-body file://stack-policy.json

# Enable termination protection
aws cloudformation update-termination-protection \
  --stack-name my-stack \
  --enable-termination-protection

# --- Change Sets ---
# Create a change set (preview changes before updating)
aws cloudformation create-change-set \
  --stack-name my-stack \
  --change-set-name my-changes \
  --template-body file://template.yaml \
  --parameters ParameterKey=Env,ParameterValue=prod \
  --capabilities CAPABILITY_IAM \
  --change-set-type UPDATE   # or CREATE for a new stack

# Describe a change set (see what will change)
aws cloudformation describe-change-set \
  --stack-name my-stack \
  --change-set-name my-changes

# Execute a change set (apply the changes)
aws cloudformation execute-change-set \
  --stack-name my-stack \
  --change-set-name my-changes

# Delete a change set
aws cloudformation delete-change-set \
  --stack-name my-stack \
  --change-set-name my-changes

# List change sets for a stack
aws cloudformation list-change-sets --stack-name my-stack

# --- Deploy shorthand (create-or-update with change set) ---
aws cloudformation deploy \
  --stack-name my-stack \
  --template-file template.yaml \
  --parameter-overrides Env=prod InstanceType=t3.micro \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --no-fail-on-empty-changeset \
  --tags Project=MyApp Team=Platform

# --- Templates ---
# Validate a template for syntax errors
aws cloudformation validate-template --template-body file://template.yaml

# Get the template of a deployed stack
aws cloudformation get-template --stack-name my-stack

# Get template summary (parameters, capabilities required)
aws cloudformation get-template-summary --template-body file://template.yaml

# Package a template (upload local artifacts to S3, update references)
aws cloudformation package \
  --template-file template.yaml \
  --s3-bucket my-artifacts-bucket \
  --output-template-file packaged.yaml

# --- Drift Detection ---
# Start drift detection on a stack
aws cloudformation detect-stack-drift --stack-name my-stack
# Returns StackDriftDetectionId

# Check drift detection status
aws cloudformation describe-stack-drift-detection-status \
  --stack-drift-detection-id <id>

# List drifted resources
aws cloudformation describe-stack-resource-drifts \
  --stack-name my-stack \
  --stack-resource-drift-status-filters MODIFIED DELETED

# Detect drift on a specific resource
aws cloudformation detect-stack-resource-drift \
  --stack-name my-stack \
  --logical-resource-id MyBucket

# --- Stack Resources ---
# List resources in a stack
aws cloudformation list-stack-resources --stack-name my-stack

# Describe a specific resource
aws cloudformation describe-stack-resource \
  --stack-name my-stack \
  --logical-resource-id MyBucket

# List stack events (useful for debugging failures)
aws cloudformation describe-stack-events --stack-name my-stack

# --- Exports and Imports ---
# List all exports from stacks in the region
aws cloudformation list-exports

# List stacks that import a specific export
aws cloudformation list-imports --export-name MyVpcId

# --- Resource Import ---
# Import existing resources into a stack (stack must have DeletionPolicy: Retain on those resources)
aws cloudformation create-change-set \
  --stack-name my-stack \
  --change-set-name import-resources \
  --change-set-type IMPORT \
  --resources-to-import '[{"ResourceType":"AWS::S3::Bucket","LogicalResourceId":"MyBucket","ResourceIdentifier":{"BucketName":"my-existing-bucket"}}]' \
  --template-body file://template.yaml

# --- Stack Sets ---
# Create a stack set
aws cloudformation create-stack-set \
  --stack-set-name my-stack-set \
  --template-body file://template.yaml \
  --capabilities CAPABILITY_IAM \
  --permission-model SERVICE_MANAGED   # or SELF_MANAGED
  # For SERVICE_MANAGED, add: --auto-deployment Enabled=true,RetainStacksOnAccountRemoval=false

# Create stack instances (deploy to accounts/regions)
aws cloudformation create-stack-instances \
  --stack-set-name my-stack-set \
  --accounts 111122223333 444455556666 \
  --regions us-east-1 us-west-2 \
  --operation-preferences MaxConcurrentCount=2,FailureToleranceCount=1

# For SERVICE_MANAGED, deploy to an OU:
aws cloudformation create-stack-instances \
  --stack-set-name my-stack-set \
  --deployment-targets OrganizationalUnitIds=ou-xxxx-xxxxxxxx \
  --regions us-east-1

# Update stack set and all instances
aws cloudformation update-stack-set \
  --stack-set-name my-stack-set \
  --template-body file://updated-template.yaml \
  --regions us-east-1 us-west-2

# List stack instances
aws cloudformation list-stack-instances --stack-set-name my-stack-set

# Signal a resource (for cfn-init / cfn-signal patterns)
aws cloudformation signal-resource \
  --stack-name my-stack \
  --logical-resource-id MyEC2Instance \
  --unique-id i-1234567890abcdef0 \
  --status SUCCESS
```
