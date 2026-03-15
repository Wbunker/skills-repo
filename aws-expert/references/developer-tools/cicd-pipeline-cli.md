# AWS CI/CD Pipeline Tools — CLI Reference

For service concepts, see [cicd-pipeline-capabilities.md](cicd-pipeline-capabilities.md).

---

## CodeCommit

```bash
# --- Repositories ---
# Create a repository
aws codecommit create-repository \
  --repository-name my-repo \
  --repository-description "My application source" \
  --tags Team=backend,Env=prod

# List repositories
aws codecommit list-repositories \
  --sort-by repositoryName \
  --order ascending

# Get repository metadata (clone URLs, ARN, default branch)
aws codecommit get-repository --repository-name my-repo

# Update a repository description
aws codecommit update-repository-description \
  --repository-name my-repo \
  --repository-description "Updated description"

# Update default branch
aws codecommit update-default-branch \
  --repository-name my-repo \
  --default-branch-name main

# Delete a repository
aws codecommit delete-repository --repository-name my-repo

# --- Branches ---
# List branches
aws codecommit list-branches --repository-name my-repo

# Get branch (latest commit)
aws codecommit get-branch \
  --repository-name my-repo \
  --branch-name main

# Create a branch from a commit
aws codecommit create-branch \
  --repository-name my-repo \
  --branch-name feature/my-feature \
  --commit-id abc1234567890abcdef1234567890abcdef12345

# Delete a branch
aws codecommit delete-branch \
  --repository-name my-repo \
  --branch-name feature/old-feature

# --- Commits ---
# Get a commit
aws codecommit get-commit \
  --repository-name my-repo \
  --commit-id abc1234567890abcdef1234567890abcdef12345

# Get differences between two commits
aws codecommit get-differences \
  --repository-name my-repo \
  --before-commit-specifier main \
  --after-commit-specifier feature/my-feature

# Get file contents from a repository
aws codecommit get-file \
  --repository-name my-repo \
  --file-path src/index.js \
  --commit-specifier main \
  --query fileContent \
  --output text | base64 --decode

# Get folder contents listing
aws codecommit get-folder \
  --repository-name my-repo \
  --folder-path src

# Put a file (create or update a file directly via API)
aws codecommit put-file \
  --repository-name my-repo \
  --branch-name main \
  --file-path README.md \
  --file-content fileb://README.md \
  --commit-message "Update README" \
  --name "CI Bot" \
  --email "ci@example.com"

# Delete a file via API
aws codecommit delete-file \
  --repository-name my-repo \
  --branch-name main \
  --file-path old-file.txt \
  --parent-commit-id abc1234567890abcdef1234567890abcdef12345 \
  --commit-message "Remove old file"

# --- Pull Requests ---
# Create a pull request
aws codecommit create-pull-request \
  --title "Add payment feature" \
  --description "Implements Stripe integration" \
  --targets repositoryName=my-repo,sourceReference=feature/payment,destinationReference=main

# List pull requests
aws codecommit list-pull-requests \
  --repository-name my-repo \
  --pull-request-status OPEN

# Get pull request details
aws codecommit get-pull-request --pull-request-id 42

# List pull request commits
aws codecommit get-pull-request-approval-states --pull-request-id 42

# Update a pull request (title or description)
aws codecommit update-pull-request-title \
  --pull-request-id 42 \
  --title "Updated title"

# Merge a pull request (three-way merge)
aws codecommit merge-pull-request-by-three-way \
  --pull-request-id 42 \
  --repository-name my-repo \
  --source-commit-id abc123 \
  --commit-message "Merge feature/payment into main" \
  --name "CI Bot" \
  --email "ci@example.com"

# Merge a pull request (squash merge)
aws codecommit merge-pull-request-by-squash \
  --pull-request-id 42 \
  --repository-name my-repo \
  --source-commit-id abc123 \
  --commit-message "Add payment feature (squashed)" \
  --name "CI Bot" \
  --email "ci@example.com"

# Merge a pull request (fast-forward)
aws codecommit merge-pull-request-by-fast-forward \
  --pull-request-id 42 \
  --repository-name my-repo \
  --source-commit-id abc123

# Close a pull request without merging
aws codecommit update-pull-request-status \
  --pull-request-id 42 \
  --pull-request-status CLOSED

# Post a comment on a pull request
aws codecommit post-comment-for-pull-request \
  --pull-request-id 42 \
  --repository-name my-repo \
  --before-commit-id abc123 \
  --after-commit-id def456 \
  --content "This looks good, but consider error handling" \
  --location filePath=src/payment.js,filePosition=42,relativeFileVersion=AFTER

# --- Approval Rules ---
# Create an approval rule on a pull request
aws codecommit create-pull-request-approval-rule \
  --pull-request-id 42 \
  --approval-rule-name "Require two approvals" \
  --approval-rule-content '{"Version":"2018-11-08","Statements":[{"Type":"Approvers","NumberOfApprovalsNeeded":2,"ApprovalPoolMembers":["arn:aws:sts::123456789012:assumed-role/Developers/*"]}]}'

# Approve a pull request
aws codecommit update-pull-request-approval-state \
  --pull-request-id 42 \
  --revision-id <revision-id> \
  --approval-state APPROVE

# Revoke approval
aws codecommit update-pull-request-approval-state \
  --pull-request-id 42 \
  --revision-id <revision-id> \
  --approval-state REVOKE

# Create an approval rule template (applies to future PRs across repos)
aws codecommit create-approval-rule-template \
  --approval-rule-template-name RequireTwoApprovals \
  --approval-rule-template-description "Requires two approvals from developers" \
  --approval-rule-template-content '{"Version":"2018-11-08","Statements":[{"Type":"Approvers","NumberOfApprovalsNeeded":2}]}'

# Associate an approval rule template with a repository
aws codecommit associate-approval-rule-template-with-repository \
  --approval-rule-template-name RequireTwoApprovals \
  --repository-name my-repo

# List approval rule templates
aws codecommit list-approval-rule-templates

# --- Triggers ---
# Put repository triggers (create or replace all triggers)
aws codecommit put-repository-triggers \
  --repository-name my-repo \
  --triggers '[
    {
      "name": "NotifyOnPush",
      "destinationArn": "arn:aws:sns:us-east-1:123456789012:repo-events",
      "customData": "my-repo",
      "branches": ["main", "develop"],
      "events": ["push"]
    }
  ]'

# Get repository triggers
aws codecommit get-repository-triggers --repository-name my-repo

# Test repository triggers (sends a test event)
aws codecommit test-repository-triggers \
  --repository-name my-repo \
  --triggers '[{"name":"NotifyOnPush","destinationArn":"arn:aws:sns:us-east-1:123456789012:repo-events","events":["push"]}]'

# Delete all triggers
aws codecommit put-repository-triggers \
  --repository-name my-repo \
  --triggers '[]'
```

---

## CodeBuild

```bash
# --- Build Projects ---
# Create a build project
aws codebuild create-project \
  --name my-build-project \
  --source type=GITHUB,location=https://github.com/myorg/myrepo.git \
  --artifacts type=S3,location=my-artifacts-bucket,packaging=ZIP \
  --environment type=LINUX_CONTAINER,image=aws/codebuild/standard:7.0,computeType=BUILD_GENERAL1_MEDIUM \
  --service-role arn:aws:iam::123456789012:role/CodeBuildRole

# Create with VPC configuration
aws codebuild create-project \
  --name my-vpc-build \
  --source type=CODECOMMIT,location=https://git-codecommit.us-east-1.amazonaws.com/v1/repos/myrepo \
  --artifacts type=NO_ARTIFACTS \
  --environment type=LINUX_CONTAINER,image=aws/codebuild/standard:7.0,computeType=BUILD_GENERAL1_SMALL,privilegedMode=true \
  --vpc-config vpcId=vpc-1234,subnets=subnet-1234 subnet-5678,securityGroupIds=sg-1234 \
  --service-role arn:aws:iam::123456789012:role/CodeBuildRole \
  --cache type=S3,location=my-cache-bucket/prefix

# Update a build project
aws codebuild update-project \
  --name my-build-project \
  --environment computeType=BUILD_GENERAL1_LARGE

# List build projects
aws codebuild list-projects

# Get project details (can batch)
aws codebuild batch-get-projects --names my-build-project my-other-project

# Delete a build project
aws codebuild delete-project --name my-build-project

# --- Builds ---
# Start a build
aws codebuild start-build \
  --project-name my-build-project

# Start a build with overrides
aws codebuild start-build \
  --project-name my-build-project \
  --source-version main \
  --buildspec-override file://buildspec-override.yaml \
  --environment-variables-override name=DEPLOY_ENV,value=staging,type=PLAINTEXT \
  --compute-type-override BUILD_GENERAL1_LARGE

# Stop a build
aws codebuild stop-build --id my-build-project:build-id

# Get build details (can batch)
aws codebuild batch-get-builds --ids my-build-project:build-id-1 my-build-project:build-id-2

# List builds for a project
aws codebuild list-builds-for-project \
  --project-name my-build-project \
  --sort-order DESCENDING

# List all builds
aws codebuild list-builds --sort-order DESCENDING

# --- Reports ---
# Create a report group
aws codebuild create-report-group \
  --name my-test-reports \
  --type TEST \
  --export-config exportConfigType=S3,s3Destination='{bucketName=my-reports-bucket,path=test-reports,packaging=ZIP}'

# List report groups
aws codebuild list-report-groups

# Get report group details (can batch)
aws codebuild batch-get-report-groups --report-group-arns <arn1> <arn2>

# List reports for a report group
aws codebuild list-reports-for-report-group \
  --report-group-arn arn:aws:codebuild:us-east-1:123456789012:report-group/my-test-reports

# Get report details (pass/fail counts, test cases)
aws codebuild batch-get-reports \
  --report-arns <report-arn>

# List test cases in a report
aws codebuild describe-test-cases \
  --report-arn <report-arn> \
  --filter status=FAILED

# --- Batch Builds ---
aws codebuild start-build-batch \
  --project-name my-batch-project

aws codebuild stop-build-batch --id my-batch-project:batch-id

aws codebuild batch-get-build-batches --ids my-batch-project:batch-id
```

---

## CodeDeploy

```bash
# --- Applications ---
# Create an application
aws deploy create-application \
  --application-name my-app \
  --compute-platform Server   # Server | Lambda | ECS

# List applications
aws deploy list-applications

# Get application details
aws deploy get-application --application-name my-app

# Delete an application
aws deploy delete-application --application-name my-app

# --- Deployment Groups ---
# Create a deployment group (EC2 blue/green with load balancer)
aws deploy create-deployment-group \
  --application-name my-app \
  --deployment-group-name my-dg \
  --service-role-arn arn:aws:iam::123456789012:role/CodeDeployRole \
  --deployment-style deploymentType=BLUE_GREEN,deploymentOption=WITH_TRAFFIC_CONTROL \
  --blue-green-deployment-configuration \
    terminateBlueInstancesOnDeploymentSuccess='{action=TERMINATE,terminationWaitTimeInMinutes=5}',
    deploymentReadyOption='{actionOnTimeout=CONTINUE_DEPLOYMENT,waitTimeInMinutes=0}',
    greenFleetProvisioningOption='{action=COPY_AUTO_SCALING_GROUP}' \
  --load-balancer-info elbInfoList='[{name=my-alb-tg}]' \
  --auto-scaling-groups my-asg

# Create a deployment group (EC2 in-place with tags)
aws deploy create-deployment-group \
  --application-name my-app \
  --deployment-group-name in-place-dg \
  --service-role-arn arn:aws:iam::123456789012:role/CodeDeployRole \
  --deployment-style deploymentType=IN_PLACE,deploymentOption=WITH_TRAFFIC_CONTROL \
  --ec2-tag-filters Key=Env,Value=prod,Type=KEY_AND_VALUE \
  --deployment-config-name CodeDeployDefault.AllAtOnce

# Create a deployment group (Lambda)
aws deploy create-deployment-group \
  --application-name my-lambda-app \
  --deployment-group-name lambda-dg \
  --service-role-arn arn:aws:iam::123456789012:role/CodeDeployRole \
  --deployment-style deploymentType=BLUE_GREEN,deploymentOption=WITHOUT_TRAFFIC_CONTROL \
  --deployment-config-name CodeDeployDefault.LambdaCanary10Percent5Minutes

# List deployment groups
aws deploy list-deployment-groups --application-name my-app

# Get deployment group
aws deploy get-deployment-group \
  --application-name my-app \
  --deployment-group-name my-dg

# --- Deployments ---
# Register an application revision (S3)
aws deploy register-application-revision \
  --application-name my-app \
  --s3-location bucket=my-deploy-bucket,key=my-app/revision.zip,bundleType=zip

# Create a deployment
aws deploy create-deployment \
  --application-name my-app \
  --deployment-group-name my-dg \
  --s3-location bucket=my-deploy-bucket,bundleType=zip,key=my-app/revision.zip \
  --description "Release 1.2.3" \
  --auto-rollback-configuration enabled=true,events=DEPLOYMENT_FAILURE

# Create a deployment from GitHub
aws deploy create-deployment \
  --application-name my-app \
  --deployment-group-name my-dg \
  --github-location repository=myorg/myrepo,commitId=abc123def456

# Get deployment status
aws deploy get-deployment --deployment-id d-EXAMPLE

# List deployments
aws deploy list-deployments \
  --application-name my-app \
  --deployment-group-name my-dg \
  --include-only-statuses InProgress Queued

# Stop a deployment
aws deploy stop-deployment \
  --deployment-id d-EXAMPLE \
  --auto-rollback-enabled   # also roll back if stopped

# Continue a blue/green deployment (complete the traffic shift)
aws deploy continue-deployment \
  --deployment-id d-EXAMPLE \
  --deployment-wait-type READY_WAIT   # advance past the ready state

# List deployment instances
aws deploy list-deployment-instances \
  --deployment-id d-EXAMPLE \
  --instance-status_filter Failed

# Get deployment instance details (lifecycle events)
aws deploy get-deployment-instance \
  --deployment-id d-EXAMPLE \
  --instance-id i-1234567890abcdef0

# --- Deployment Configurations ---
# List deployment configurations
aws deploy list-deployment-configs

# Create a custom deployment configuration
aws deploy create-deployment-config \
  --deployment-config-name my-custom-config \
  --minimum-healthy-hosts type=FLEET_PERCENT,value=75
```

---

## CodePipeline

```bash
# --- Pipelines ---
# Create a pipeline from a JSON definition
aws codepipeline create-pipeline \
  --pipeline file://pipeline-definition.json

# Get pipeline definition
aws codepipeline get-pipeline --name my-pipeline

# Update a pipeline definition
aws codepipeline update-pipeline \
  --pipeline file://updated-pipeline.json

# Delete a pipeline
aws codepipeline delete-pipeline --name my-pipeline

# List pipelines
aws codepipeline list-pipelines

# Get pipeline state (current stage and action status)
aws codepipeline get-pipeline-state --name my-pipeline

# --- Executions ---
# Start a pipeline execution (manual trigger)
aws codepipeline start-pipeline-execution \
  --name my-pipeline \
  --source-revisions actionName=Source,revisionType=COMMIT_ID,revisionValue=abc123

# Start with pipeline-level variables (V2 pipelines)
aws codepipeline start-pipeline-execution \
  --name my-pipeline \
  --variables name=Environment,value=staging

# Stop a pipeline execution
aws codepipeline stop-pipeline-execution \
  --pipeline-name my-pipeline \
  --pipeline-execution-id <execution-id> \
  --reason "Stopping for investigation" \
  --abandon   # abandon in-progress actions immediately (omit to wait for current actions to finish)

# Get pipeline execution details
aws codepipeline get-pipeline-execution \
  --pipeline-name my-pipeline \
  --pipeline-execution-id <execution-id>

# List pipeline executions
aws codepipeline list-pipeline-executions \
  --pipeline-name my-pipeline

# List action executions with details
aws codepipeline list-action-executions \
  --pipeline-name my-pipeline \
  --filter pipelineExecutionId=<execution-id>

# --- Stage Transitions ---
# Disable a stage transition (gate a stage from running)
aws codepipeline disable-stage-transition \
  --pipeline-name my-pipeline \
  --stage-name Deploy \
  --transition-type Inbound \
  --reason "Freeze for maintenance window"

# Enable a stage transition (re-open the gate)
aws codepipeline enable-stage-transition \
  --pipeline-name my-pipeline \
  --stage-name Deploy \
  --transition-type Inbound

# Retry a failed stage
aws codepipeline retry-stage-execution \
  --pipeline-name my-pipeline \
  --stage-name Build \
  --pipeline-execution-id <execution-id> \
  --retry-mode FAILED_ACTIONS

# --- Manual Approvals ---
# Approve or reject a manual approval action
aws codepipeline put-approval-result \
  --pipeline-name my-pipeline \
  --stage-name Approval \
  --action-name ManualApproval \
  --result summary="Approved after review",status=Approved \
  --token <approval-token>  # token from GetPipelineState

# Reject:
aws codepipeline put-approval-result \
  --pipeline-name my-pipeline \
  --stage-name Approval \
  --action-name ManualApproval \
  --result summary="Issues found in staging",status=Rejected \
  --token <approval-token>

# --- Webhooks (for custom source triggers) ---
aws codepipeline put-webhook \
  --webhook file://webhook-definition.json

aws codepipeline list-webhooks
aws codepipeline delete-webhook --name my-webhook
```

---

## CodeArtifact

```bash
# --- Domains ---
# Create a domain
aws codeartifact create-domain \
  --domain my-domain \
  --encryption-key alias/my-key

# List domains
aws codeartifact list-domains

# Get domain details
aws codeartifact describe-domain --domain my-domain

# Delete a domain
aws codeartifact delete-domain --domain my-domain

# --- Repositories ---
# Create a repository
aws codeartifact create-repository \
  --domain my-domain \
  --repository my-npm-repo \
  --description "Internal npm packages"

# Create a repository with an upstream (proxy to npm public registry)
aws codeartifact create-repository \
  --domain my-domain \
  --repository npm-proxy \
  --description "Proxy for npmjs.com" \
  --upstreams repositoryName=npmjs-upstream

# Associate an external connection (proxy to public registry)
aws codeartifact associate-external-connection \
  --domain my-domain \
  --repository npm-proxy \
  --external-connection public:npmjs   # or public:pypi, public:maven-central, public:nuget-org

# List repositories
aws codeartifact list-repositories
aws codeartifact list-repositories-in-domain --domain my-domain

# Get repository details
aws codeartifact describe-repository \
  --domain my-domain \
  --repository my-npm-repo

# Delete a repository
aws codeartifact delete-repository \
  --domain my-domain \
  --repository my-npm-repo

# --- Authorization Token ---
# Get a token (valid 12 hours by default) for package manager authentication
aws codeartifact get-authorization-token \
  --domain my-domain \
  --domain-owner 123456789012 \
  --query authorizationToken \
  --output text

# Login shorthand (configures npm/pip/mvn automatically)
aws codeartifact login \
  --tool npm \
  --domain my-domain \
  --domain-owner 123456789012 \
  --repository my-npm-repo

# For pip:
aws codeartifact login \
  --tool pip \
  --domain my-domain \
  --domain-owner 123456789012 \
  --repository my-python-repo

# --- Packages ---
# List packages in a repository
aws codeartifact list-packages \
  --domain my-domain \
  --repository my-npm-repo \
  --format npm

# List package versions
aws codeartifact list-package-versions \
  --domain my-domain \
  --repository my-npm-repo \
  --format npm \
  --package my-internal-lib

# Get package version details
aws codeartifact describe-package-version \
  --domain my-domain \
  --repository my-npm-repo \
  --format npm \
  --package my-internal-lib \
  --package-version 1.2.3

# Get a package version asset (download)
aws codeartifact get-package-version-asset \
  --domain my-domain \
  --repository my-npm-repo \
  --format npm \
  --package my-internal-lib \
  --package-version 1.2.3 \
  --asset my-internal-lib-1.2.3.tgz \
  /tmp/my-internal-lib-1.2.3.tgz

# Delete a package version
aws codeartifact delete-package-versions \
  --domain my-domain \
  --repository my-npm-repo \
  --format npm \
  --package my-internal-lib \
  --versions 0.0.1 0.0.2

# Publish a generic package version
aws codeartifact publish-package-version \
  --domain my-domain \
  --repository my-generic-repo \
  --format generic \
  --namespace my-namespace \
  --package my-tool \
  --package-version 1.0.0 \
  --asset-name my-tool-1.0.0.tar.gz \
  --asset-content /path/to/my-tool-1.0.0.tar.gz \
  --asset-sha256 <sha256>
```
