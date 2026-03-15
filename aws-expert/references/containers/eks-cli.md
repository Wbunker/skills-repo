# AWS EKS — CLI Reference
For service concepts, see [eks-capabilities.md](eks-capabilities.md).

```bash
# --- kubeconfig ---
# Configure kubectl to talk to an EKS cluster
aws eks update-kubeconfig --name my-cluster --region us-east-1

# Use a specific role for cluster access
aws eks update-kubeconfig --name my-cluster --region us-east-1 \
  --role-arn arn:aws:iam::123456789012:role/EKSAdminRole

# --- Clusters ---
aws eks create-cluster \
  --name my-cluster \
  --kubernetes-version 1.31 \
  --role-arn arn:aws:iam::123456789012:role/eks-cluster-role \
  --resources-vpc-config \
    subnetIds=subnet-aaa,subnet-bbb,subnet-ccc,\
securityGroupIds=sg-abc,\
endpointPublicAccess=true,\
endpointPrivateAccess=true,\
publicAccessCidrs=203.0.113.0/24

aws eks list-clusters

aws eks describe-cluster --name my-cluster
aws eks describe-cluster --name my-cluster \
  --query 'cluster.{status:status,version:version,endpoint:endpoint}'

# Upgrade cluster to new Kubernetes version
aws eks update-cluster-version --name my-cluster --kubernetes-version 1.32

# Update cluster config (endpoint access, logging, networking)
aws eks update-cluster-config --name my-cluster \
  --resources-vpc-config endpointPublicAccess=false,endpointPrivateAccess=true
aws eks update-cluster-config --name my-cluster \
  --logging '{"clusterLogging": [{"types": ["api","audit","authenticator","controllerManager","scheduler"], "enabled": true}]}'

aws eks describe-cluster-versions

aws eks delete-cluster --name my-cluster

# Track update status
aws eks list-updates --name my-cluster
aws eks describe-update --name my-cluster --update-id <update-id>

# --- Node Groups (Managed) ---
aws eks create-nodegroup \
  --cluster-name my-cluster \
  --nodegroup-name my-nodes \
  --node-role arn:aws:iam::123456789012:role/eks-node-role \
  --subnets subnet-aaa subnet-bbb \
  --instance-types t3.medium m5.large \
  --ami-type AL2_x86_64 \
  --capacity-type ON_DEMAND \
  --scaling-config minSize=1,maxSize=10,desiredSize=2 \
  --disk-size 50 \
  --labels environment=production team=platform \
  --taints key=dedicated,value=gpu,effect=NO_SCHEDULE

aws eks list-nodegroups --cluster-name my-cluster

aws eks describe-nodegroup --cluster-name my-cluster --nodegroup-name my-nodes

# Upgrade nodegroup AMI / Kubernetes version
aws eks update-nodegroup-version \
  --cluster-name my-cluster \
  --nodegroup-name my-nodes \
  --kubernetes-version 1.32 \
  --force  # proceed even if pod disruption budgets would block it

# Scale or update labels/taints
aws eks update-nodegroup-config \
  --cluster-name my-cluster \
  --nodegroup-name my-nodes \
  --scaling-config minSize=2,maxSize=20,desiredSize=4 \
  --labels addOrUpdateLabels={environment=staging}

aws eks delete-nodegroup --cluster-name my-cluster --nodegroup-name my-nodes

# --- Fargate Profiles ---
aws eks create-fargate-profile \
  --cluster-name my-cluster \
  --fargate-profile-name my-fargate-profile \
  --pod-execution-role-arn arn:aws:iam::123456789012:role/eks-fargate-pod-execution-role \
  --subnets subnet-private-aaa subnet-private-bbb \
  --selectors \
    namespace=fargate-namespace \
    'namespace=kube-system,labels={app=coredns}'

aws eks list-fargate-profiles --cluster-name my-cluster

aws eks describe-fargate-profile \
  --cluster-name my-cluster \
  --fargate-profile-name my-fargate-profile

aws eks delete-fargate-profile \
  --cluster-name my-cluster \
  --fargate-profile-name my-fargate-profile

# --- Add-ons ---
# List available add-on versions
aws eks describe-addon-versions --addon-name vpc-cni
aws eks describe-addon-versions \
  --kubernetes-version 1.31 \
  --query 'addons[].{name:addonName,defaultVersion:addonVersions[?defaultVersion==`true`].addonVersion|[0]}'

aws eks list-addons --cluster-name my-cluster

# Install/update an add-on
aws eks create-addon \
  --cluster-name my-cluster \
  --addon-name vpc-cni \
  --addon-version v1.19.0-eksbuild.1 \
  --service-account-role-arn arn:aws:iam::123456789012:role/vpc-cni-irsa-role \
  --resolve-conflicts OVERWRITE

aws eks describe-addon --cluster-name my-cluster --addon-name vpc-cni
aws eks describe-addon-configuration --addon-name vpc-cni --addon-version v1.19.0-eksbuild.1

aws eks update-addon \
  --cluster-name my-cluster \
  --addon-name vpc-cni \
  --addon-version v1.19.2-eksbuild.1 \
  --resolve-conflicts PRESERVE

aws eks delete-addon --cluster-name my-cluster --addon-name vpc-cni

# --- Access Entries (cluster authentication — newer approach) ---
# Create an access entry for an IAM role
aws eks create-access-entry \
  --cluster-name my-cluster \
  --principal-arn arn:aws:iam::123456789012:role/EKSDevRole \
  --type STANDARD \
  --kubernetes-groups developers

# Associate an EKS access policy to an access entry
aws eks associate-access-policy \
  --cluster-name my-cluster \
  --principal-arn arn:aws:iam::123456789012:role/EKSDevRole \
  --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSViewPolicy \
  --access-scope type=namespace,namespaces=default,staging

aws eks list-access-entries --cluster-name my-cluster

aws eks describe-access-entry \
  --cluster-name my-cluster \
  --principal-arn arn:aws:iam::123456789012:role/EKSDevRole

aws eks list-associated-access-policies \
  --cluster-name my-cluster \
  --principal-arn arn:aws:iam::123456789012:role/EKSDevRole

aws eks list-access-policies  # list all EKS-managed access policies

aws eks disassociate-access-policy \
  --cluster-name my-cluster \
  --principal-arn arn:aws:iam::123456789012:role/EKSDevRole \
  --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSViewPolicy

aws eks update-access-entry \
  --cluster-name my-cluster \
  --principal-arn arn:aws:iam::123456789012:role/EKSDevRole \
  --kubernetes-groups developers senior-developers

aws eks delete-access-entry \
  --cluster-name my-cluster \
  --principal-arn arn:aws:iam::123456789012:role/EKSDevRole

# --- Pod Identity Associations ---
# Associate an IAM role with a Kubernetes service account
aws eks create-pod-identity-association \
  --cluster-name my-cluster \
  --namespace my-namespace \
  --service-account my-service-account \
  --role-arn arn:aws:iam::123456789012:role/MyPodRole

aws eks list-pod-identity-associations --cluster-name my-cluster
aws eks list-pod-identity-associations \
  --cluster-name my-cluster \
  --namespace my-namespace

aws eks describe-pod-identity-association \
  --cluster-name my-cluster \
  --association-id a-xxxxxxxxxxxxxxxxx

aws eks update-pod-identity-association \
  --cluster-name my-cluster \
  --association-id a-xxxxxxxxxxxxxxxxx \
  --role-arn arn:aws:iam::123456789012:role/MyUpdatedPodRole

aws eks delete-pod-identity-association \
  --cluster-name my-cluster \
  --association-id a-xxxxxxxxxxxxxxxxx

# --- OIDC Identity Provider (for IRSA) ---
aws eks associate-identity-provider-config \
  --cluster-name my-cluster \
  --oidc '{
    "identityProviderConfigName": "my-oidc",
    "issuerUrl": "https://oidc.eks.us-east-1.amazonaws.com/id/EXAMPLED539D4633E53DE1B71EXAMPLE",
    "clientId": "sts.amazonaws.com",
    "usernameClaim": "sub",
    "groupsClaim": "groups"
  }'

aws eks describe-identity-provider-config \
  --cluster-name my-cluster \
  --identity-provider-config 'type=oidc,name=my-oidc'

aws eks list-identity-provider-configs --cluster-name my-cluster

aws eks disassociate-identity-provider-config \
  --cluster-name my-cluster \
  --identity-provider-config 'type=oidc,name=my-oidc'

# --- Encryption Config ---
aws eks associate-encryption-config \
  --cluster-name my-cluster \
  --encryption-config \
    '[{"provider": {"keyArn": "arn:aws:kms:us-east-1:123456789012:key/abc"}, "resources": ["secrets"]}]'

# --- EKS Anywhere subscriptions ---
aws eks create-eks-anywhere-subscription \
  --name my-anywhere-subscription \
  --term unit=MONTHS,duration=12 \
  --license-quantity 10 \
  --auto-renew

aws eks list-eks-anywhere-subscriptions
aws eks describe-eks-anywhere-subscription --name my-anywhere-subscription

# --- Tagging ---
aws eks tag-resource \
  --resource-arn arn:aws:eks:us-east-1:123456789012:cluster/my-cluster \
  --tags Environment=production Team=platform

aws eks list-tags-for-resource \
  --resource-arn arn:aws:eks:us-east-1:123456789012:cluster/my-cluster
```
