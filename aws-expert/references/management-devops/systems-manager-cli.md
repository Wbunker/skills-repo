# AWS Systems Manager — CLI Reference
For service concepts, see [systems-manager-capabilities.md](systems-manager-capabilities.md).

```bash
# --- Parameter Store ---
# Put a parameter
aws ssm put-parameter \
  --name /myapp/prod/db-password \
  --value "supersecret" \
  --type SecureString \
  --key-id alias/my-key \
  --description "Production DB password" \
  --overwrite

# Put a plain string parameter
aws ssm put-parameter \
  --name /myapp/prod/db-host \
  --value "db.internal.example.com" \
  --type String

# Get a single parameter (--with-decryption for SecureString)
aws ssm get-parameter \
  --name /myapp/prod/db-password \
  --with-decryption

# Get multiple parameters
aws ssm get-parameters \
  --names /myapp/prod/db-host /myapp/prod/db-password \
  --with-decryption

# Get all parameters under a path hierarchy
aws ssm get-parameters-by-path \
  --path /myapp/prod \
  --recursive \
  --with-decryption

# Get parameter history (versions)
aws ssm get-parameter-history \
  --name /myapp/prod/db-password \
  --with-decryption

# Describe parameters (list with metadata, no values)
aws ssm describe-parameters
aws ssm describe-parameters \
  --parameter-filters "Key=Path,Option=Recursive,Values=/myapp/prod"

# Label a parameter version
aws ssm label-parameter-version \
  --name /myapp/prod/db-password \
  --parameter-version 3 \
  --labels live previous

# Get a labeled version
aws ssm get-parameter \
  --name /myapp/prod/db-password:live \
  --with-decryption

# Delete a parameter
aws ssm delete-parameter --name /myapp/prod/db-password

# Delete multiple parameters
aws ssm delete-parameters \
  --names /myapp/prod/db-host /myapp/prod/db-password

# --- Session Manager ---
# Start an interactive session (no SSH required)
aws ssm start-session --target i-1234567890abcdef0

# Start a session with a specific document (e.g., port forwarding)
aws ssm start-session \
  --target i-1234567890abcdef0 \
  --document-name AWS-StartPortForwardingSession \
  --parameters portNumber=5432,localPortNumber=5432

# Port forwarding to a remote host (not just the instance)
aws ssm start-session \
  --target i-1234567890abcdef0 \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters host=db.internal.example.com,portNumber=5432,localPortNumber=5432

# Describe sessions
aws ssm describe-sessions --state Active
aws ssm describe-sessions --state History

# Terminate a session
aws ssm terminate-session --session-id session-id-here

# --- Run Command ---
# Run a shell script on instances
aws ssm send-command \
  --document-name "AWS-RunShellScript" \
  --targets '[{"Key":"tag:Env","Values":["prod"]}]' \
  --parameters '{"commands":["systemctl restart nginx", "echo done"]}' \
  --timeout-seconds 60 \
  --max-concurrency "50%" \
  --max-errors "10%" \
  --output-s3-bucket-name my-ssm-output-bucket \
  --output-s3-key-prefix run-command-output/
# Returns CommandId

# Send command to specific instances
aws ssm send-command \
  --document-name "AWS-RunShellScript" \
  --instance-ids i-1234567890abcdef0 i-0987654321fedcba0 \
  --parameters '{"commands":["uptime"]}'

# List commands
aws ssm list-commands
aws ssm list-commands --command-id <command-id>

# List command invocations (per-instance results)
aws ssm list-command-invocations \
  --command-id <command-id> \
  --details

# Get output from a specific invocation
aws ssm get-command-invocation \
  --command-id <command-id> \
  --instance-id i-1234567890abcdef0

# Cancel a running command
aws ssm cancel-command --command-id <command-id>

# --- Automation ---
# Start an automation runbook
aws ssm start-automation-execution \
  --document-name "AWS-RestartEC2Instance" \
  --parameters '{"InstanceId":["i-1234567890abcdef0"]}'

# Start with rate control (multi-account or many instances)
aws ssm start-automation-execution \
  --document-name "AWS-PatchInstanceWithRollback" \
  --parameters InstanceId=i-1234567890abcdef0 \
  --target-parameter-name InstanceId \
  --targets '[{"Key":"tag:Env","Values":["prod"]}]' \
  --max-concurrency "10%" \
  --max-errors "5%"

# Get automation execution details
aws ssm get-automation-execution \
  --automation-execution-id <execution-id>

# List automation executions
aws ssm describe-automation-executions
aws ssm describe-automation-executions \
  --filters '[{"Key":"DocumentNamePrefix","Values":["AWS-"]}]'

# Stop an automation execution
aws ssm stop-automation-execution \
  --automation-execution-id <execution-id>

# --- State Manager (Associations) ---
# Create an association (ensure configuration state)
aws ssm create-association \
  --name "AWS-GatherSoftwareInventory" \
  --targets '[{"Key":"tag:Env","Values":["prod"]}]' \
  --schedule-expression "rate(1 day)" \
  --association-name my-inventory-association

# Create association to run a script on a schedule
aws ssm create-association \
  --name "AWS-RunShellScript" \
  --association-name ensure-nginx-running \
  --targets '[{"Key":"tag:App","Values":["web"]}]' \
  --parameters '{"commands":["systemctl start nginx || true"]}' \
  --schedule-expression "rate(30 minutes)"

# List associations
aws ssm list-associations

# Describe an association
aws ssm describe-association \
  --association-id <association-id>

# Run an association immediately (outside scheduled window)
aws ssm start-associations-once \
  --association-ids <association-id>

# Delete an association
aws ssm delete-association --association-id <association-id>

# --- Patch Manager ---
# Create a patch baseline
aws ssm create-patch-baseline \
  --name my-linux-baseline \
  --operating-system AMAZON_LINUX_2 \
  --approval-rules \
    PatchRules='[{"PatchFilterGroup":{"PatchFilters":[{"Key":"CLASSIFICATION","Values":["Security","Bugfix"]},{"Key":"SEVERITY","Values":["Critical","Important"]}]},"ApproveAfterDays":7,"EnableNonSecurity":false}]' \
  --description "Auto-approve security patches after 7 days"

# Describe patch baselines
aws ssm describe-patch-baselines
aws ssm describe-patch-baselines \
  --filters '[{"Key":"NAME_PREFIX","Values":["my-"]}]'

# Register a patch baseline for a patch group
aws ssm register-patch-baseline-for-patch-group \
  --baseline-id pb-1234567890abcdef0 \
  --patch-group "prod-servers"

# Get the baseline assigned to a patch group
aws ssm get-patch-baseline-for-patch-group --patch-group "prod-servers"

# Describe patch groups
aws ssm describe-patch-groups

# Get patch compliance for instances
aws ssm describe-instance-patch-states \
  --instance-ids i-1234567890abcdef0

aws ssm describe-instance-patch-states-for-patch-group \
  --patch-group "prod-servers"

# Start a maintenance window execution (manual trigger)
aws ssm start-maintenance-window-execution \
  --window-id mw-1234567890abcdef0 \
  --task-id mwtask-1234567890abcdef0

# Create a maintenance window
aws ssm create-maintenance-window \
  --name my-patching-window \
  --schedule "cron(0 2 ? * SUN *)" \
  --duration 4 \
  --cutoff 1 \
  --allow-unassociated-targets
```
