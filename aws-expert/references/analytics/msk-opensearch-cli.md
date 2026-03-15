# AWS MSK & OpenSearch — CLI Reference
For service concepts, see [msk-opensearch-capabilities.md](msk-opensearch-capabilities.md).

## Amazon MSK

```bash
# --- Provisioned cluster ---
aws kafka create-cluster \
  --cluster-name my-kafka-cluster \
  --kafka-version "3.6.0" \
  --number-of-broker-nodes 3 \
  --broker-node-group-info '{
    "InstanceType": "kafka.m5.large",
    "ClientSubnets": ["subnet-a", "subnet-b", "subnet-c"],
    "StorageInfo": {"EbsStorageInfo": {"VolumeSize": 100}}
  }' \
  --encryption-info '{
    "EncryptionInTransit": {"ClientBroker": "TLS", "InCluster": true}
  }' \
  --client-authentication '{
    "Sasl": {"Scram": {"Enabled": true}},
    "Tls": {"CertificateAuthorityArnList": []}
  }'

aws kafka describe-cluster --cluster-arn arn:aws:kafka:us-east-1:123456789012:cluster/...
aws kafka list-clusters
aws kafka list-clusters-v2

# --- Serverless cluster ---
aws kafka create-cluster-v2 \
  --cluster-name my-serverless-kafka \
  --serverless '{
    "VpcConfigs": [{"SubnetIds": ["subnet-a", "subnet-b"], "SecurityGroupIds": ["sg-abc"]}],
    "ClientAuthentication": {"Sasl": {"Iam": {"Enabled": true}}}
  }'

aws kafka describe-cluster-v2 --cluster-arn arn:aws:kafka:us-east-1:123456789012:cluster/...

# --- Broker connection info ---
aws kafka get-bootstrap-brokers \
  --cluster-arn arn:aws:kafka:us-east-1:123456789012:cluster/...

# --- Configuration ---
aws kafka create-configuration \
  --name my-kafka-config \
  --kafka-versions "3.6.0" \
  --server-properties 'auto.create.topics.enable=false
log.retention.hours=168
num.partitions=3'

aws kafka list-configurations
aws kafka describe-configuration --arn arn:aws:kafka:us-east-1:123456789012:configuration/...

# --- Cluster operations ---
aws kafka list-cluster-operations \
  --cluster-arn arn:aws:kafka:us-east-1:123456789012:cluster/...

aws kafka reboot-broker \
  --cluster-arn arn:aws:kafka:us-east-1:123456789012:cluster/... \
  --broker-ids 1 2

aws kafka update-broker-count \
  --cluster-arn arn:aws:kafka:us-east-1:123456789012:cluster/... \
  --current-version "K3AEGXETSR30VB" \
  --target-number-of-broker-nodes 6

aws kafka update-broker-storage \
  --cluster-arn arn:aws:kafka:us-east-1:123456789012:cluster/... \
  --current-version "K3AEGXETSR30VB" \
  --target-broker-ebs-volume-info '[{"KafkaBrokerNodeId": "ALL", "VolumeSizeGB": 200}]'

aws kafka delete-cluster \
  --cluster-arn arn:aws:kafka:us-east-1:123456789012:cluster/...
```

---

## Amazon OpenSearch Service

```bash
# --- Domain lifecycle ---
aws opensearch create-domain \
  --domain-name my-domain \
  --engine-version OpenSearch_2.13 \
  --cluster-config '{
    "InstanceType": "r6g.large.search",
    "InstanceCount": 3,
    "DedicatedMasterEnabled": true,
    "DedicatedMasterType": "r6g.large.search",
    "DedicatedMasterCount": 3,
    "ZoneAwarenessEnabled": true,
    "ZoneAwarenessConfig": {"AvailabilityZoneCount": 3}
  }' \
  --ebs-options 'EBSEnabled=true,VolumeType=gp3,VolumeSize=100' \
  --node-to-node-encryption-options 'Enabled=true' \
  --encryption-at-rest-options 'Enabled=true' \
  --domain-endpoint-options 'EnforceHTTPS=true,TLSSecurityPolicy=Policy-Min-TLS-1-2-2019-07' \
  --access-policies '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::123456789012:role/OpenSearchRole"},
      "Action": "es:*",
      "Resource": "arn:aws:es:us-east-1:123456789012:domain/my-domain/*"
    }]
  }'

aws opensearch describe-domain --domain-name my-domain
aws opensearch list-domain-names
aws opensearch describe-domains --domain-names my-domain my-other-domain

aws opensearch update-domain-config \
  --domain-name my-domain \
  --cluster-config 'InstanceCount=6' \
  --ebs-options 'VolumeSize=200'

aws opensearch delete-domain --domain-name my-domain

# --- UltraWarm (warm storage) ---
aws opensearch update-domain-config \
  --domain-name my-domain \
  --cluster-config '{
    "WarmEnabled": true,
    "WarmType": "ultrawarm1.medium.search",
    "WarmCount": 2
  }'

# --- Cold storage ---
aws opensearch update-domain-config \
  --domain-name my-domain \
  --cold-storage-options 'Enabled=true'

# --- Tags ---
aws opensearch add-tags \
  --arn arn:aws:es:us-east-1:123456789012:domain/my-domain \
  --tag-list Key=Environment,Value=prod Key=Team,Value=data

aws opensearch list-tags \
  --arn arn:aws:es:us-east-1:123456789012:domain/my-domain

aws opensearch remove-tags \
  --arn arn:aws:es:us-east-1:123456789012:domain/my-domain \
  --tag-keys Environment

# --- Packages (custom plugins/dictionaries) ---
aws opensearch create-package \
  --package-name my-custom-dict \
  --package-type TXT-DICTIONARY \
  --package-source 'S3BucketName=my-bucket,S3Key=dictionaries/custom.txt'

aws opensearch associate-package \
  --package-id F123456789 \
  --domain-name my-domain

aws opensearch list-packages-for-domain --domain-name my-domain
aws opensearch dissociate-package --package-id F123456789 --domain-name my-domain
aws opensearch delete-package --package-id F123456789

# --- VPC endpoint ---
aws opensearch create-vpc-endpoint \
  --domain-arn arn:aws:es:us-east-1:123456789012:domain/my-domain \
  --vpc-options '{
    "SubnetIds": ["subnet-abc"],
    "SecurityGroupIds": ["sg-abc"]
  }'

aws opensearch list-vpc-endpoints-for-domain --domain-name my-domain
```
