# AWS Cloud IDE & Shell — CLI Reference

For service concepts, see [cloud-ide-shell-capabilities.md](cloud-ide-shell-capabilities.md).

---

## AWS Cloud9

```bash
# --- Environments ---
# Create an EC2 environment (SSM connection, no inbound SSH needed)
aws cloud9 create-environment-ec2 \
  --name my-dev-env \
  --description "My Cloud9 environment" \
  --instance-type t3.small \
  --image-id amazonlinux-2023-x86-64 \
  --connection-type CONNECT_SSM \
  --subnet-id subnet-1234567890abcdef0 \
  --automatic-stop-time-minutes 30

# Create an EC2 environment with SSH connection
aws cloud9 create-environment-ec2 \
  --name my-ssh-env \
  --instance-type t3.medium \
  --image-id amazonlinux-2-x86-64 \
  --connection-type CONNECT_SSH \
  --subnet-id subnet-1234567890abcdef0

# Create an SSH environment (connect to your own server)
aws cloud9 create-environment-ssh \
  --name my-ssh-server-env \
  --description "Connect to on-prem server" \
  --host 10.0.1.100 \
  --port 22 \
  --login cloudshell-user \
  --environment-path /home/cloudshell-user/projects \
  --node-path /usr/bin/node

# List your environments
aws cloud9 list-environments

# Describe environments (pass IDs from list-environments)
aws cloud9 describe-environments \
  --environment-ids env-1234567890abcdef0 env-abcdef1234567890

# Describe environment status (e.g., ready, stopped)
aws cloud9 describe-environment-status \
  --environment-id env-1234567890abcdef0

# Update an environment (rename, change description)
aws cloud9 update-environment \
  --environment-id env-1234567890abcdef0 \
  --name new-env-name \
  --description "Updated description" \
  --managed-credentials-action ENABLE   # or DISABLE

# Delete an environment
aws cloud9 delete-environment \
  --environment-id env-1234567890abcdef0

# --- Membership (Collaboration) ---
# Add a member (share the environment)
aws cloud9 create-environment-membership \
  --environment-id env-1234567890abcdef0 \
  --user-arn arn:aws:iam::123456789012:user/alice \
  --permissions read-write   # or read-only

# List members of an environment
aws cloud9 list-environment-memberships \
  --environment-id env-1234567890abcdef0

# Describe a specific membership
aws cloud9 describe-environment-memberships \
  --environment-id env-1234567890abcdef0 \
  --user-arn arn:aws:iam::123456789012:user/alice

# Update a membership (change permissions)
aws cloud9 update-environment-membership \
  --environment-id env-1234567890abcdef0 \
  --user-arn arn:aws:iam::123456789012:user/alice \
  --permissions read-only

# Remove a member (revoke access)
aws cloud9 delete-environment-membership \
  --environment-id env-1234567890abcdef0 \
  --user-arn arn:aws:iam::123456789012:user/alice
```

---

## AWS CloudShell

CloudShell is a browser-based service accessed through the AWS Management Console. There is **no `aws cloudshell` CLI namespace** — CloudShell itself is the shell environment, not a service you interact with via the CLI.

### Accessing CloudShell

- Open the AWS Management Console and click the CloudShell icon in the top navigation bar
- Or navigate to: **AWS Console → CloudShell** (search for "CloudShell")
- The session automatically inherits the IAM credentials of the signed-in user

### Working with Files in CloudShell

```bash
# Files in $HOME (/home/cloudshell-user) persist between sessions (1 GB limit)
# Check available space
df -h $HOME

# Upload files: Use Actions → Upload file in the CloudShell console UI
# Download files: Use Actions → Download file in the CloudShell console UI

# Install tools to the persistent home directory (persists across sessions)
pip install --user boto3 awscli-local
npm install -g serverless

# Confirm installed AWS CLI version
aws --version

# Show current IAM identity (confirms inherited credentials)
aws sts get-caller-identity
```

### Common CloudShell Workflows

```bash
# --- Quick AWS operations without local setup ---
# Describe EC2 instances in the current region
aws ec2 describe-instances --query 'Reservations[].Instances[].[InstanceId,State.Name,Tags[?Key==`Name`].Value|[0]]' --output table

# Tail CloudWatch logs
aws logs tail /aws/lambda/my-function --follow

# Invoke a Lambda function
aws lambda invoke \
  --function-name my-function \
  --payload '{"key":"value"}' \
  --cli-binary-format raw-in-base64-out \
  /tmp/response.json && cat /tmp/response.json

# S3 operations
aws s3 ls s3://my-bucket/
aws s3 cp s3://my-bucket/file.txt /tmp/file.txt

# --- Scripting with pre-installed tools ---
# Use jq to process JSON
aws ec2 describe-instances | jq '.Reservations[].Instances[].InstanceId'

# Use Python for quick scripts
python3 -c "import boto3; s3 = boto3.client('s3'); print(s3.list_buckets())"
```

### VPC CloudShell

VPC CloudShell environments are created from the AWS Console (EC2 → CloudShell or directly in the CloudShell console). There is no CLI to create VPC CloudShell environments directly; they are managed through the console.

```bash
# Once inside a VPC CloudShell session, access private resources:
# Connect to a private RDS instance
mysql -h my-db.cluster-xxxxxxxx.us-east-1.rds.amazonaws.com -u admin -p

# Curl an internal API endpoint
curl http://internal-alb.us-east-1.elb.amazonaws.com/health

# Access an ElastiCache Redis cluster
redis-cli -h my-cluster.xxxxxx.cache.amazonaws.com -p 6379 ping
```
