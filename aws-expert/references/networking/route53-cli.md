# AWS Route 53 — CLI Reference
For service concepts, see [route53-capabilities.md](route53-capabilities.md).

## Route 53

```bash
# --- Hosted Zones ---
# Create public hosted zone
aws route53 create-hosted-zone \
  --name example.com \
  --caller-reference $(date +%s)

# Create private hosted zone (associated with a VPC)
aws route53 create-hosted-zone \
  --name internal.example.com \
  --caller-reference $(date +%s) \
  --vpc VPCRegion=us-east-1,VPCId=vpc-12345678 \
  --hosted-zone-config PrivateZone=true,Comment="Internal zone"

aws route53 list-hosted-zones
aws route53 list-hosted-zones-by-name --dns-name example.com
aws route53 get-hosted-zone --id /hostedzone/Z1234ABCDEF

# Associate additional VPC with private hosted zone
aws route53 associate-vpc-with-hosted-zone \
  --hosted-zone-id /hostedzone/Z1234ABCDEF \
  --vpc VPCRegion=us-west-2,VPCId=vpc-87654321

aws route53 disassociate-vpc-from-hosted-zone \
  --hosted-zone-id /hostedzone/Z1234ABCDEF \
  --vpc VPCRegion=us-west-2,VPCId=vpc-87654321

aws route53 delete-hosted-zone --id /hostedzone/Z1234ABCDEF

# --- DNS Records ---
# Create/update/delete records using change-resource-record-sets
aws route53 change-resource-record-sets \
  --hosted-zone-id /hostedzone/Z1234ABCDEF \
  --change-batch '{
    "Comment": "Create A record for www",
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "www.example.com",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [{"Value": "203.0.113.10"}]
      }
    }]
  }'

# Create ALIAS record pointing to ALB
aws route53 change-resource-record-sets \
  --hosted-zone-id /hostedzone/Z1234ABCDEF \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "api.example.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z35SXDOTRQ7X7K",
          "DNSName": "my-alb-123456.us-east-1.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'

# Weighted routing (two records with same name, different weights)
aws route53 change-resource-record-sets \
  --hosted-zone-id /hostedzone/Z1234ABCDEF \
  --change-batch '{
    "Changes": [
      {
        "Action": "CREATE",
        "ResourceRecordSet": {
          "Name": "api.example.com",
          "Type": "A",
          "SetIdentifier": "primary",
          "Weight": 90,
          "AliasTarget": {
            "HostedZoneId": "Z35SXDOTRQ7X7K",
            "DNSName": "primary-alb.us-east-1.elb.amazonaws.com",
            "EvaluateTargetHealth": true
          }
        }
      },
      {
        "Action": "CREATE",
        "ResourceRecordSet": {
          "Name": "api.example.com",
          "Type": "A",
          "SetIdentifier": "canary",
          "Weight": 10,
          "AliasTarget": {
            "HostedZoneId": "Z35SXDOTRQ7X7K",
            "DNSName": "canary-alb.us-east-1.elb.amazonaws.com",
            "EvaluateTargetHealth": true
          }
        }
      }
    ]
  }'

# Failover routing
aws route53 change-resource-record-sets \
  --hosted-zone-id /hostedzone/Z1234ABCDEF \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "app.example.com",
        "Type": "A",
        "SetIdentifier": "primary",
        "Failover": "PRIMARY",
        "HealthCheckId": "abc-health-check-id",
        "AliasTarget": {
          "HostedZoneId": "Z35SXDOTRQ7X7K",
          "DNSName": "primary-alb.us-east-1.elb.amazonaws.com",
          "EvaluateTargetHealth": false
        }
      }
    }]
  }'

aws route53 list-resource-record-sets --hosted-zone-id /hostedzone/Z1234ABCDEF
aws route53 list-resource-record-sets \
  --hosted-zone-id /hostedzone/Z1234ABCDEF \
  --start-record-name www.example.com \
  --start-record-type A

# --- Health Checks ---
# HTTP health check
aws route53 create-health-check \
  --caller-reference $(date +%s) \
  --health-check-config '{
    "Type": "HTTP",
    "ResourcePath": "/health",
    "FullyQualifiedDomainName": "api.example.com",
    "Port": 80,
    "RequestInterval": 30,
    "FailureThreshold": 3
  }'

# HTTPS health check with string matching
aws route53 create-health-check \
  --caller-reference $(date +%s) \
  --health-check-config '{
    "Type": "HTTPS_STR_MATCH",
    "ResourcePath": "/health",
    "FullyQualifiedDomainName": "api.example.com",
    "Port": 443,
    "SearchString": "OK",
    "RequestInterval": 10,
    "FailureThreshold": 3
  }'

# Calculated health check (combining multiple health checks)
aws route53 create-health-check \
  --caller-reference $(date +%s) \
  --health-check-config '{
    "Type": "CALCULATED",
    "HealthThreshold": 2,
    "ChildHealthChecks": ["hc-id-1", "hc-id-2", "hc-id-3"]
  }'

aws route53 list-health-checks
aws route53 get-health-check --health-check-id abc-health-check-id
aws route53 get-health-check-status --health-check-id abc-health-check-id
aws route53 delete-health-check --health-check-id abc-health-check-id

# --- Query Logging ---
aws route53 create-query-logging-config \
  --hosted-zone-id /hostedzone/Z1234ABCDEF \
  --cloud-watch-logs-log-group-arn arn:aws:logs:us-east-1:123456789012:log-group:/route53/queries

# --- Test DNS Answer ---
aws route53 test-dns-answer \
  --hosted-zone-id /hostedzone/Z1234ABCDEF \
  --record-name www.example.com \
  --record-type A

# --- DNSSEC ---
aws route53 enable-hosted-zone-dnssec \
  --hosted-zone-id /hostedzone/Z1234ABCDEF

aws route53 get-dnssec --hosted-zone-id /hostedzone/Z1234ABCDEF
```

---

## Route 53 Resolver

```bash
# --- Resolver Endpoints ---
# Create inbound resolver endpoint (accept queries from on-premises)
aws route53resolver create-resolver-endpoint \
  --name inbound-endpoint \
  --direction INBOUND \
  --ip-addresses SubnetId=subnet-12345678,Ip=10.0.1.10 SubnetId=subnet-87654321,Ip=10.0.2.10 \
  --security-group-ids sg-12345678

# Create outbound resolver endpoint (forward queries to on-premises)
aws route53resolver create-resolver-endpoint \
  --name outbound-endpoint \
  --direction OUTBOUND \
  --ip-addresses SubnetId=subnet-12345678 SubnetId=subnet-87654321 \
  --security-group-ids sg-12345678

aws route53resolver list-resolver-endpoints
aws route53resolver get-resolver-endpoint --resolver-endpoint-id rslvr-in-12345678

# List IPs associated with an endpoint
aws route53resolver list-resolver-endpoint-ip-addresses \
  --resolver-endpoint-id rslvr-out-12345678

aws route53resolver update-resolver-endpoint \
  --resolver-endpoint-id rslvr-out-12345678 \
  --name updated-name

aws route53resolver delete-resolver-endpoint \
  --resolver-endpoint-id rslvr-out-12345678

# --- Resolver Rules ---
# Create a FORWARD rule (forward corp.example.com to on-premises DNS)
aws route53resolver create-resolver-rule \
  --name forward-corp \
  --rule-type FORWARD \
  --domain-name corp.example.com \
  --resolver-endpoint-id rslvr-out-12345678 \
  --target-ips Address=192.168.1.10,Port=53 Address=192.168.1.11,Port=53

# Associate rule with a VPC
aws route53resolver associate-resolver-rule \
  --resolver-rule-id rslvr-rr-12345678 \
  --vpc-id vpc-12345678 \
  --name my-association

aws route53resolver list-resolver-rules
aws route53resolver get-resolver-rule --resolver-rule-id rslvr-rr-12345678
aws route53resolver list-resolver-rule-associations
aws route53resolver get-resolver-rule-association --resolver-rule-association-id rslvr-rrassoc-12345678

aws route53resolver disassociate-resolver-rule \
  --resolver-rule-id rslvr-rr-12345678 \
  --vpc-id vpc-12345678

aws route53resolver delete-resolver-rule --resolver-rule-id rslvr-rr-12345678

# --- DNS Firewall ---
# Create domain list
aws route53resolver create-firewall-domain-list --name block-malicious
aws route53resolver update-firewall-domains \
  --firewall-domain-list-id rslvr-fdl-12345678 \
  --operation ADD \
  --domains malicious.example.com *.badactor.net

# Create rule group
aws route53resolver create-firewall-rule-group --name my-dns-firewall-rg

# Add a rule to the group
aws route53resolver create-firewall-rule \
  --name block-malicious-rule \
  --firewall-rule-group-id rslvr-frg-12345678 \
  --firewall-domain-list-id rslvr-fdl-12345678 \
  --priority 100 \
  --action BLOCK \
  --block-response NXDOMAIN

# Associate rule group with a VPC
aws route53resolver associate-firewall-rule-group \
  --firewall-rule-group-id rslvr-frg-12345678 \
  --vpc-id vpc-12345678 \
  --priority 100 \
  --name my-firewall-association
```
