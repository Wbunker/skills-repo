# Amazon GuardDuty & Detective — CLI Reference
For service concepts, see [guardduty-detective-capabilities.md](guardduty-detective-capabilities.md).

## Amazon GuardDuty

```bash
# --- Enable / manage ---
aws guardduty create-detector \
  --enable \
  --finding-publishing-frequency FIFTEEN_MINUTES \
  --features Name=S3_DATA_EVENTS,Status=ENABLED \
            Name=EKS_AUDIT_LOGS,Status=ENABLED \
            Name=MALWARE_PROTECTION,Status=ENABLED \
            Name=RDS_LOGIN_EVENTS,Status=ENABLED \
            Name=LAMBDA_NETWORK_LOGS,Status=ENABLED \
            Name=RUNTIME_MONITORING,Status=ENABLED
aws guardduty list-detectors
aws guardduty get-detector --detector-id abc123
aws guardduty update-detector \
  --detector-id abc123 \
  --finding-publishing-frequency ONE_HOUR
aws guardduty delete-detector --detector-id abc123

# --- Findings ---
aws guardduty list-findings --detector-id abc123
aws guardduty list-findings --detector-id abc123 \
  --finding-criteria '{"Criterion":{"severity":{"Gte":7},"service.archived":{"Eq":["false"]}}}'
aws guardduty get-findings --detector-id abc123 --finding-ids finding-id-1 finding-id-2
aws guardduty archive-findings --detector-id abc123 --finding-ids finding-id-1
aws guardduty unarchive-findings --detector-id abc123 --finding-ids finding-id-1
aws guardduty update-findings-feedback \
  --detector-id abc123 \
  --finding-ids finding-id-1 \
  --feedback USEFUL \
  --comments "True positive - confirmed malicious activity"

# Describe finding types
aws guardduty list-finding-statistics \
  --detector-id abc123 \
  --finding-statistic-types COUNT_BY_SEVERITY

# Create sample findings (for testing)
aws guardduty create-sample-findings \
  --detector-id abc123 \
  --finding-types UnauthorizedAccess:EC2/TorIPCaller Backdoor:EC2/C&CActivity.B

# --- Trusted IPs and threat intel ---
aws guardduty create-ip-set \
  --detector-id abc123 \
  --name TrustedCorporateIPs \
  --format TXT \
  --location s3://my-guardduty-lists/trusted-ips.txt \
  --activate
aws guardduty list-ip-sets --detector-id abc123
aws guardduty get-ip-set --detector-id abc123 --ip-set-id ip-set-id
aws guardduty update-ip-set \
  --detector-id abc123 \
  --ip-set-id ip-set-id \
  --activate

aws guardduty create-threat-intel-set \
  --detector-id abc123 \
  --name MaliciousIPs \
  --format TXT \
  --location s3://my-guardduty-lists/malicious-ips.txt \
  --activate
aws guardduty list-threat-intel-sets --detector-id abc123

# --- Suppression rules ---
aws guardduty create-filter \
  --detector-id abc123 \
  --name SuppressDevEC2 \
  --action ARCHIVE \
  --finding-criteria '{"Criterion":{"resource.instanceDetails.tags.value":{"Eq":["dev"]},"type":{"Eq":["UnauthorizedAccess:EC2/TorIPCaller"]}}}'
aws guardduty list-filters --detector-id abc123
aws guardduty get-filter --detector-id abc123 --filter-name SuppressDevEC2
aws guardduty delete-filter --detector-id abc123 --filter-name SuppressDevEC2

# --- Multi-account / Organizations ---
aws guardduty enable-organization-admin-account --admin-account-id 123456789012
aws guardduty list-organization-admin-accounts
aws guardduty describe-organization-configuration --detector-id abc123
aws guardduty update-organization-configuration \
  --detector-id abc123 \
  --auto-enable-organization-members NEW_ACCOUNTS \
  --features Name=S3_DATA_EVENTS,AutoEnable=NEW Status=ENABLED

# Member accounts
aws guardduty list-members --detector-id abc123
aws guardduty get-member --detector-id abc123 --account-ids 111111111111
aws guardduty create-members \
  --detector-id abc123 \
  --account-details AccountId=111111111111,Email=account@example.com
aws guardduty invite-members \
  --detector-id abc123 \
  --account-ids 111111111111
aws guardduty disassociate-members --detector-id abc123 --account-ids 111111111111
aws guardduty delete-members --detector-id abc123 --account-ids 111111111111

# --- Finding export ---
aws guardduty create-publishing-destination \
  --detector-id abc123 \
  --destination-type S3 \
  --destination-properties DestinationArn=arn:aws:s3:::my-guardduty-findings,KmsKeyArn=arn:aws:kms:...
aws guardduty list-publishing-destinations --detector-id abc123
aws guardduty delete-publishing-destination --detector-id abc123 --destination-id dest-id

# --- Malware Protection ---
aws guardduty create-malware-protection-plan \
  --role arn:aws:iam::123456789012:role/GuardDutyMalwareProtectionRole \
  --protected-resource S3Bucket="{BucketName=my-bucket,ObjectPrefixes=[uploads/]}"
aws guardduty list-malware-protection-plans
aws guardduty get-malware-protection-plan --malware-protection-plan-id plan-id
aws guardduty delete-malware-protection-plan --malware-protection-plan-id plan-id
```

---

## Amazon Detective

```bash
# --- Enable (create behavior graph) ---
aws detective create-graph --tags Environment=Production
aws detective list-graphs
aws detective get-members --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx

# --- Multi-account ---
aws detective create-members \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx \
  --accounts AccountId=111111111111,EmailAddress=account@example.com \
  --message "You are invited to join Detective for security investigation"
aws detective list-members --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx
aws detective delete-members \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx \
  --account-ids 111111111111
aws detective disassociate-membership \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx

# Member invitations
aws detective accept-invitation \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx
aws detective reject-invitation \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx
aws detective list-invitations

# --- Organization integration ---
aws detective enable-organization-admin-account --account-id 123456789012
aws detective list-organization-admin-accounts
aws detective describe-organization-configuration \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx
aws detective update-organization-configuration \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx \
  --auto-enable

# --- Investigations ---
aws detective start-investigation \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx \
  --entity-arn arn:aws:iam::123456789012:user/alice \
  --scope-start-time 2024-01-01T00:00:00Z \
  --scope-end-time 2024-01-07T23:59:59Z
aws detective list-investigations \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx
aws detective get-investigation \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx \
  --investigation-id investigation-id
aws detective update-investigation-state \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx \
  --investigation-id investigation-id \
  --state CLOSED
aws detective list-indicators \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx \
  --investigation-id investigation-id

# Delete graph (disables Detective)
aws detective delete-graph --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx
```
