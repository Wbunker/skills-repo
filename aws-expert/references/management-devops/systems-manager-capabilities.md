# AWS Systems Manager — Capabilities Reference
For CLI commands, see [systems-manager-cli.md](systems-manager-cli.md).

**Purpose**: Unified operations hub for viewing, managing, and automating tasks on AWS and hybrid infrastructure at scale — without requiring open ports or SSH.

## Parameter Store

| Concept | Description |
|---|---|
| **Standard parameter** | Free; up to 4 KB value; 10,000 per account per region |
| **Advanced parameter** | $0.05/month per parameter; up to 8 KB; supports parameter policies (expiration, notification) |
| **SecureString** | Parameter encrypted using KMS (AWS managed or CMK); transparent decryption on retrieval with IAM |
| **Hierarchy** | Path-based naming (e.g., `/myapp/prod/db-password`); retrieve all params under a path at once |
| **Versioning** | Every put creates a new version; reference a specific version with `name:version` |
| **Parameter labels** | Aliases for specific versions (e.g., `live`, `previous`); safer than hardcoding version numbers |

## Session Manager

- Browser-based interactive shell or port forwarding to EC2/on-premises instances
- **No inbound ports required** — no SSH, no bastion hosts
- Sessions encrypted in transit via TLS; session data can be logged to S3 or CloudWatch Logs
- Port forwarding: tunnel remote ports to localhost (`aws ssm start-session --document-name AWS-StartPortForwardingSession`)
- IAM-controlled access; session commands logged in CloudTrail

## Run Command

| Concept | Description |
|---|---|
| **SSM Document** | YAML or JSON definition of steps to execute; AWS-managed documents or custom |
| **Rate control** | `--max-concurrency` limits simultaneous targets; `--max-errors` stops execution after N failures |
| **Target selection** | Instance IDs, resource group, or tag-based targeting |
| **Command output** | Captured to S3 or CloudWatch Logs; truncated in console |
| **Common documents** | `AWS-RunShellScript`, `AWS-RunPowerShellScript`, `AWS-UpdateSSMAgent`, `AWS-InstallWindowsUpdates` |

## Automation

| Concept | Description |
|---|---|
| **Runbook (Automation document)** | YAML/JSON multi-step document defining actions, inputs, and outputs |
| **Step actions** | `aws:runCommand`, `aws:invokeLambdaFunction`, `aws:executeAwsApi`, `aws:waitForAwsResourceProperty`, `aws:branch` |
| **Execution modes** | Simple (one target), rate control (concurrency/error limits), multi-account via Organizations |
| **Change Calendar integration** | Block automation during change freeze windows |

## Patch Manager

| Concept | Description |
|---|---|
| **Patch baseline** | Rules defining which patches are approved (auto-approve by severity/classification after N days) |
| **Patch group** | Tag-based grouping of instances associated with a specific baseline; tag key `Patch Group` |
| **Maintenance window** | Scheduled time window for running patching (and other) tasks safely |
| **Patch compliance** | Report showing which instances have missing, failed, or installed patches |

## Other SSM Capabilities

| Capability | Description |
|---|---|
| **State Manager** | Associations that enforce configuration state on instances on a schedule (e.g., keep CWAgent running) |
| **Inventory** | Collect software, network, file, registry, and custom metadata from managed nodes |
| **Explorer** | Aggregated operational data dashboard across accounts and regions |
| **OpsCenter** | Create and manage OpsItems (operational issues); integrates with EventBridge and alarms |
| **Change Manager** | Formal change request workflow with approvals; audit trail; blocks changes outside maintenance windows |
| **Fleet Manager** | GUI for managing Windows and Linux instances: file browser, Registry editor, user management |
| **Distributor** | Package and distribute software agents (custom or AWS-managed) to managed nodes |
| **AppConfig** | Safely deploy application configuration changes with validators and rollout strategies |
