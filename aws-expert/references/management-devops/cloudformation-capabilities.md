# AWS CloudFormation — Capabilities Reference
For CLI commands, see [cloudformation-cli.md](cloudformation-cli.md).

**Purpose**: Infrastructure as Code (IaC) service that provisions and manages AWS resources using declarative JSON or YAML templates.

## Core Concepts

| Concept | Description |
|---|---|
| **Stack** | A collection of AWS resources managed as a single unit; create/update/delete all resources together |
| **Template** | JSON or YAML document describing resources, parameters, mappings, conditions, outputs, and metadata |
| **Change set** | Preview of proposed changes before executing an update; shows what will be added, modified, or deleted |
| **Stack set** | Deploy a stack to multiple accounts and/or regions from a single operation |
| **Nested stack** | A stack created as a resource within another stack (`AWS::CloudFormation::Stack`); enables template reuse |
| **Stack policy** | JSON document that controls which stack resources can be updated or replaced during updates |
| **Drift detection** | Compare actual resource configurations to template-defined expected configurations; identifies manual changes |
| **Custom resource** | Lambda-backed or SNS-backed resource for logic not natively supported (`AWS::CloudFormation::CustomResource`) |
| **Macro** | Transform template snippets using Lambda; used for custom DSLs and shorthand syntax |
| **Module** | Encapsulate and reuse common resource patterns as a registered CloudFormation module type |
| **Resource import** | Import existing resources into a stack without recreating them |
| **CloudFormation Guard (cfn-guard)** | Policy-as-code tool using a domain-specific language to validate templates before deployment |
| **StackSets operation** | Batch create/update/delete stack instances across target accounts and regions |

## Deletion and Update Policies

| Policy | Purpose |
|---|---|
| **DeletionPolicy: Retain** | Keep the resource when the stack is deleted |
| **DeletionPolicy: Snapshot** | Take a snapshot before deleting (RDS, EBS, ElastiCache) |
| **DeletionPolicy: Delete** | Default; delete the resource with the stack |
| **UpdateReplacePolicy** | Same options as DeletionPolicy; controls what happens to the old resource when it must be replaced during update |
| **UpdatePolicy** | Controls how CloudFormation handles updates to Auto Scaling groups, ElastiCache, and Lambda aliases (rolling updates, blue/green, etc.) |

## Key Features

| Feature | Description |
|---|---|
| **cfn-init** | EC2 instance helper that reads `AWS::CloudFormation::Init` metadata to install packages, write files, run commands |
| **cfn-signal** | Helper script that signals CloudFormation when an EC2 instance or application is ready (used with `CreationPolicy`) |
| **Rollback triggers** | CloudWatch alarms monitored during stack operations; trigger rollback if alarm fires within the monitoring window |
| **Cross-stack references** | Export output values from one stack (`Outputs` + `Export`) and import them in another (`Fn::ImportValue`) |
| **Dynamic references** | Reference SSM Parameter Store or Secrets Manager values directly in templates (`{{resolve:ssm:/my/param}}`) |
| **Resource import** | Adopt existing AWS resources into a stack using `IMPORT` change set type; resource must have `DeletionPolicy: Retain` |
| **Stack termination protection** | Prevent accidental stack deletion via the console or API |
| **Condition functions** | `Fn::If`, `Fn::Equals`, `Fn::And`, `Fn::Or`, `Fn::Not` to conditionally create resources or set properties |
| **Transform (SAM)** | `AWS::Serverless-2016-10-31` macro simplifies Lambda, API Gateway, and DynamoDB definitions |

## Stack Sets — Deployment Models

| Model | Description |
|---|---|
| **Self-managed** | You manually grant CloudFormation permissions to deploy into target accounts via IAM roles |
| **Service-managed** | Uses AWS Organizations; automatic deployment to new accounts in target OUs; no manual IAM setup |

## CloudFormation Guard

cfn-guard uses a rule DSL to check template properties:
```
# Example Guard rule — deny public S3 buckets
rule s3_bucket_not_public {
  AWS::S3::Bucket {
    Properties.PublicAccessBlockConfiguration.BlockPublicAcls == true
    Properties.PublicAccessBlockConfiguration.BlockPublicPolicy == true
  }
}
```
