# AWS ECR — CLI Reference
For service concepts, see [ecr-capabilities.md](ecr-capabilities.md).

## ECR (Private Registry)

```bash
# --- Authentication ---
# Get a login password and pipe to docker login (valid for 12 hours)
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin \
    123456789012.dkr.ecr.us-east-1.amazonaws.com

# --- Repositories ---
aws ecr create-repository \
  --repository-name my-app \
  --image-tag-mutability IMMUTABLE \
  --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=KMS,kmsKey=arn:aws:kms:us-east-1:123456789012:key/mrk-abc

aws ecr describe-repositories
aws ecr describe-repositories --repository-names my-app

# Set repository policy (cross-account pull)
aws ecr set-repository-policy \
  --repository-name my-app \
  --policy-text file://repo-policy.json

aws ecr get-repository-policy --repository-name my-app
aws ecr delete-repository-policy --repository-name my-app

aws ecr delete-repository --repository-name my-app --force

# Tag mutability
aws ecr put-image-tag-mutability \
  --repository-name my-app \
  --image-tag-mutability IMMUTABLE

# --- Images ---
# Push image (after docker build + docker tag)
docker tag my-app:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:v1.2.3
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:v1.2.3

aws ecr list-images --repository-name my-app
aws ecr list-images --repository-name my-app --filter tagStatus=UNTAGGED

aws ecr describe-images --repository-name my-app
aws ecr describe-images --repository-name my-app \
  --image-ids imageTag=v1.2.3
aws ecr describe-images --repository-name my-app \
  --query 'sort_by(imageDetails, &imagePushedAt)[-5:].[imageDigest,imageTags,imagePushedAt]' \
  --output table

# Pull a specific image manifest
aws ecr batch-get-image \
  --repository-name my-app \
  --image-ids imageTag=v1.2.3 \
  --query 'images[].imageManifest' --output text

# Re-tag an image by putting a new image manifest
MANIFEST=$(aws ecr batch-get-image \
  --repository-name my-app \
  --image-ids imageTag=v1.2.3 \
  --query 'images[0].imageManifest' --output text)
aws ecr put-image \
  --repository-name my-app \
  --image-tag latest \
  --image-manifest "$MANIFEST"

# Delete images
aws ecr batch-delete-image \
  --repository-name my-app \
  --image-ids imageTag=v0.9.0 imageDigest=sha256:abc123

# --- Lifecycle Policies ---
# Apply a lifecycle policy (keep last 10 tagged images; expire untagged after 1 day)
aws ecr put-lifecycle-policy \
  --repository-name my-app \
  --lifecycle-policy-text '{
    "rules": [
      {
        "rulePriority": 1,
        "description": "Expire untagged images after 1 day",
        "selection": {"tagStatus": "untagged", "countType": "sinceImagePushed", "countUnit": "days", "countNumber": 1},
        "action": {"type": "expire"}
      },
      {
        "rulePriority": 2,
        "description": "Keep last 10 tagged images",
        "selection": {"tagStatus": "tagged", "tagPrefixList": ["v"], "countType": "imageCountMoreThan", "countNumber": 10},
        "action": {"type": "expire"}
      }
    ]
  }'

aws ecr get-lifecycle-policy --repository-name my-app

# Dry-run lifecycle policy before applying
aws ecr start-lifecycle-policy-preview \
  --repository-name my-app \
  --lifecycle-policy-text file://lifecycle-policy.json

aws ecr get-lifecycle-policy-preview --repository-name my-app

aws ecr delete-lifecycle-policy --repository-name my-app

# --- Image Scanning ---
# Enable enhanced scanning at registry level
aws ecr put-registry-scanning-configuration \
  --scan-type ENHANCED \
  --rules '[{"repositoryFilters": [{"filter": "*", "filterType": "WILDCARD"}], "scanFrequency": "CONTINUOUS_SCAN"}]'

aws ecr get-registry-scanning-configuration

# Configure basic scanning on a repository
aws ecr put-image-scanning-configuration \
  --repository-name my-app \
  --image-scanning-configuration scanOnPush=true

# Trigger an on-demand basic scan
aws ecr start-image-scan \
  --repository-name my-app \
  --image-id imageTag=v1.2.3

aws ecr describe-image-scan-findings \
  --repository-name my-app \
  --image-id imageTag=v1.2.3

# --- Replication ---
# Configure cross-region and cross-account replication
aws ecr put-replication-configuration \
  --replication-configuration '{
    "rules": [
      {
        "destinations": [
          {"region": "us-west-2", "registryId": "123456789012"},
          {"region": "eu-west-1", "registryId": "123456789012"}
        ],
        "repositoryFilters": [{"filter": "prod/*", "filterType": "PREFIX_MATCH"}]
      }
    ]
  }'

aws ecr describe-registry  # view current replication config

aws ecr describe-image-replication-status \
  --repository-name my-app \
  --image-id imageTag=v1.2.3

# --- Pull-Through Cache Rules ---
# Cache Docker Hub images in ECR
aws ecr create-pull-through-cache-rule \
  --ecr-repository-prefix dockerhub \
  --upstream-registry-url registry-1.docker.io \
  --credential-arn arn:aws:secretsmanager:us-east-1:123456789012:secret:ecr-pullthroughcache/docker-hub

# Cache Quay images
aws ecr create-pull-through-cache-rule \
  --ecr-repository-prefix quay \
  --upstream-registry-url quay.io

aws ecr describe-pull-through-cache-rules

aws ecr validate-pull-through-cache-rule \
  --ecr-repository-prefix dockerhub

aws ecr update-pull-through-cache-rule \
  --ecr-repository-prefix dockerhub \
  --credential-arn arn:aws:secretsmanager:us-east-1:123456789012:secret:ecr-pullthroughcache/docker-hub-new

aws ecr delete-pull-through-cache-rule \
  --ecr-repository-prefix dockerhub

# Pull via cache rule (triggers caching on first pull)
docker pull 123456789012.dkr.ecr.us-east-1.amazonaws.com/dockerhub/library/nginx:latest

# --- Repository Creation Templates ---
aws ecr create-repository-creation-template \
  --prefix prod/ \
  --description "Template for production repos" \
  --image-tag-mutability IMMUTABLE \
  --lifecycle-policy file://lifecycle-policy.json \
  --repository-policy file://repo-policy.json \
  --resource-tags Key=Environment,Value=production \
  --applied-for PULL_THROUGH_CACHE REPLICATION

aws ecr describe-repository-creation-templates
aws ecr update-repository-creation-template --prefix prod/ --description "Updated"
aws ecr delete-repository-creation-template --prefix prod/

# --- Registry Policy ---
# Grant another account permission to replicate into this registry
aws ecr put-registry-policy --policy-text file://registry-policy.json
aws ecr get-registry-policy
aws ecr delete-registry-policy

# --- Tagging ---
aws ecr tag-resource \
  --resource-arn arn:aws:ecr:us-east-1:123456789012:repository/my-app \
  --tags Key=Team,Value=platform

aws ecr list-tags-for-resource \
  --resource-arn arn:aws:ecr:us-east-1:123456789012:repository/my-app
```

## ECR Public

```bash
# Authenticate to ECR Public (us-east-1 only)
aws ecr-public get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin public.ecr.aws

# Create a public repository
aws ecr-public create-repository \
  --repository-name my-public-app \
  --catalog-data '{
    "description": "My open-source application",
    "architectures": ["x86-64", "ARM 64"],
    "operatingSystems": ["Linux"],
    "logoImageBlob": "<base64-encoded-png>"
  }' \
  --region us-east-1

aws ecr-public describe-repositories --region us-east-1
aws ecr-public describe-repositories --repository-names my-public-app --region us-east-1

# Push to public repository
docker tag my-app:latest public.ecr.aws/<alias>/my-public-app:v1.0.0
docker push public.ecr.aws/<alias>/my-public-app:v1.0.0

# Put/re-tag image in public repository
aws ecr-public put-image \
  --repository-name my-public-app \
  --image-tag latest \
  --image-manifest "$MANIFEST" \
  --region us-east-1

aws ecr-public describe-images --repository-name my-public-app --region us-east-1

aws ecr-public delete-repository --repository-name my-public-app --force --region us-east-1
```
