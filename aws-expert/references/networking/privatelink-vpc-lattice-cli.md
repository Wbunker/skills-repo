# AWS PrivateLink & VPC Lattice — CLI Reference
For service concepts, see [privatelink-vpc-lattice-capabilities.md](privatelink-vpc-lattice-capabilities.md).

## VPC Lattice

```bash
# --- Service Networks ---
aws vpc-lattice create-service-network \
  --name my-service-network \
  --auth-type AWS_IAM \
  --tags Environment=production

aws vpc-lattice list-service-networks
aws vpc-lattice get-service-network --service-network-identifier my-service-network

# Associate a VPC with the service network
aws vpc-lattice create-service-network-vpc-association \
  --service-network-identifier my-service-network \
  --vpc-identifier vpc-12345678 \
  --security-group-ids sg-12345678

aws vpc-lattice list-service-network-vpc-associations \
  --service-network-identifier my-service-network

aws vpc-lattice delete-service-network-vpc-association \
  --service-network-vpc-association-identifier snva-12345678

aws vpc-lattice delete-service-network \
  --service-network-identifier my-service-network

# --- Services ---
aws vpc-lattice create-service \
  --name my-service \
  --auth-type AWS_IAM \
  --tags Environment=production

aws vpc-lattice list-services
aws vpc-lattice get-service --service-identifier my-service

# Associate service with service network
aws vpc-lattice create-service-network-service-association \
  --service-identifier my-service \
  --service-network-identifier my-service-network

aws vpc-lattice list-service-network-service-associations \
  --service-network-identifier my-service-network

aws vpc-lattice delete-service --service-identifier my-service

# --- Listeners ---
aws vpc-lattice create-listener \
  --service-identifier my-service \
  --name https-listener \
  --protocol HTTPS \
  --port 443 \
  --default-action \
    '{"forward":{"targetGroups":[{"targetGroupIdentifier":"my-tg","weight":100}]}}'

# HTTP listener with fixed response default
aws vpc-lattice create-listener \
  --service-identifier my-service \
  --name http-listener \
  --protocol HTTP \
  --port 80 \
  --default-action \
    '{"fixedResponse":{"statusCode":404}}'

aws vpc-lattice list-listeners --service-identifier my-service
aws vpc-lattice delete-listener \
  --service-identifier my-service \
  --listener-identifier https-listener

# --- Rules ---
aws vpc-lattice create-rule \
  --service-identifier my-service \
  --listener-identifier https-listener \
  --name api-route \
  --priority 10 \
  --match \
    '{"httpMatch":{"pathMatch":{"match":{"prefix":"/api"},"caseSensitive":false}}}' \
  --action \
    '{"forward":{"targetGroups":[{"targetGroupIdentifier":"api-tg","weight":100}]}}'

# Weighted routing rule (canary)
aws vpc-lattice create-rule \
  --service-identifier my-service \
  --listener-identifier https-listener \
  --name canary-rule \
  --priority 20 \
  --match '{"httpMatch":{"pathMatch":{"match":{"prefix":"/v2"},"caseSensitive":true}}}' \
  --action \
    '{"forward":{"targetGroups":[
      {"targetGroupIdentifier":"stable-tg","weight":90},
      {"targetGroupIdentifier":"canary-tg","weight":10}
    ]}}'

aws vpc-lattice list-rules \
  --service-identifier my-service \
  --listener-identifier https-listener

aws vpc-lattice delete-rule \
  --service-identifier my-service \
  --listener-identifier https-listener \
  --rule-identifier api-route

# --- Target Groups ---
# Instance target group
aws vpc-lattice create-target-group \
  --name my-ec2-tg \
  --type INSTANCE \
  --config \
    '{"port":80,"protocol":"HTTP","vpcIdentifier":"vpc-12345678","healthCheck":{"enabled":true,"path":"/health","protocol":"HTTP"}}'

# IP target group
aws vpc-lattice create-target-group \
  --name my-ip-tg \
  --type IP \
  --config \
    '{"port":8080,"protocol":"HTTP","ipAddressType":"IPV4","vpcIdentifier":"vpc-12345678"}'

# Lambda target group
aws vpc-lattice create-target-group \
  --name my-lambda-tg \
  --type LAMBDA

# ALB target group
aws vpc-lattice create-target-group \
  --name my-alb-tg \
  --type ALB \
  --config \
    '{"port":443,"protocol":"HTTPS","vpcIdentifier":"vpc-12345678"}'

# Register targets
aws vpc-lattice register-targets \
  --target-group-identifier my-ec2-tg \
  --targets '[{"id":"i-12345678","port":80},{"id":"i-87654321","port":80}]'

aws vpc-lattice list-targets --target-group-identifier my-ec2-tg
aws vpc-lattice list-target-groups
aws vpc-lattice delete-target-group --target-group-identifier my-ec2-tg

# --- Auth Policies ---
# Set auth policy on a service (allow specific IAM role)
aws vpc-lattice put-auth-policy \
  --resource-identifier my-service \
  --policy '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:role/ServiceA"
      },
      "Action": "vpc-lattice-svcs:Invoke",
      "Resource": "*"
    }]
  }'

# Set auth policy on a service network (allow entire org)
aws vpc-lattice put-auth-policy \
  --resource-identifier my-service-network \
  --policy '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": "*",
      "Action": "vpc-lattice-svcs:Invoke",
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:PrincipalOrgID": "o-1234567890"
        }
      }
    }]
  }'

aws vpc-lattice get-auth-policy --resource-identifier my-service
aws vpc-lattice delete-auth-policy --resource-identifier my-service

# --- Access Log Subscriptions ---
aws vpc-lattice create-access-log-subscription \
  --resource-identifier my-service \
  --destination-arn arn:aws:logs:us-east-1:123456789012:log-group:/vpc-lattice/access-logs
```
