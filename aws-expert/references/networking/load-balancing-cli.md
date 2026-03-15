# AWS Load Balancing — CLI Reference
For service concepts, see [load-balancing-capabilities.md](load-balancing-capabilities.md).

## Elastic Load Balancing (ELBv2)

```bash
# --- Create Load Balancers ---
# Application Load Balancer
aws elbv2 create-load-balancer \
  --name my-alb \
  --type application \
  --scheme internet-facing \
  --subnets subnet-12345678 subnet-87654321 \
  --security-groups sg-12345678 \
  --tags Key=Environment,Value=production

# Internal ALB
aws elbv2 create-load-balancer \
  --name my-internal-alb \
  --type application \
  --scheme internal \
  --subnets subnet-12345678 subnet-87654321 \
  --security-groups sg-12345678

# Network Load Balancer
aws elbv2 create-load-balancer \
  --name my-nlb \
  --type network \
  --scheme internet-facing \
  --subnets subnet-12345678 subnet-87654321

# NLB with Elastic IPs
aws elbv2 create-load-balancer \
  --name my-nlb-static \
  --type network \
  --scheme internet-facing \
  --subnet-mappings \
    SubnetId=subnet-12345678,AllocationId=eipalloc-12345678 \
    SubnetId=subnet-87654321,AllocationId=eipalloc-87654321

# Gateway Load Balancer
aws elbv2 create-load-balancer \
  --name my-gwlb \
  --type gateway \
  --subnets subnet-12345678

aws elbv2 describe-load-balancers
aws elbv2 describe-load-balancers --names my-alb
aws elbv2 describe-load-balancers --load-balancer-arns arn:aws:elasticloadbalancing:...

# Modify LB attributes (access logs, deletion protection, etc.)
aws elbv2 modify-load-balancer-attributes \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234 \
  --attributes \
    Key=access_logs.s3.enabled,Value=true \
    Key=access_logs.s3.bucket,Value=my-alb-logs \
    Key=access_logs.s3.prefix,Value=alb \
    Key=deletion_protection.enabled,Value=true

aws elbv2 delete-load-balancer \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234

# --- Target Groups ---
# HTTP target group (EC2 instances)
aws elbv2 create-target-group \
  --name my-targets \
  --protocol HTTP \
  --port 80 \
  --vpc-id vpc-12345678 \
  --health-check-protocol HTTP \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3 \
  --target-type instance

# IP target group (for ECS Fargate or cross-VPC targets)
aws elbv2 create-target-group \
  --name my-ip-targets \
  --protocol HTTP \
  --port 8080 \
  --vpc-id vpc-12345678 \
  --target-type ip

# Lambda target group
aws elbv2 create-target-group \
  --name my-lambda-targets \
  --target-type lambda

# TLS target group for NLB
aws elbv2 create-target-group \
  --name my-tls-targets \
  --protocol TLS \
  --port 443 \
  --vpc-id vpc-12345678 \
  --target-type instance

# gRPC target group
aws elbv2 create-target-group \
  --name my-grpc-targets \
  --protocol HTTP \
  --protocol-version GRPC \
  --port 50051 \
  --vpc-id vpc-12345678 \
  --target-type ip

aws elbv2 describe-target-groups
aws elbv2 describe-target-groups --load-balancer-arn arn:aws:elasticloadbalancing:...

# Modify target group attributes (deregistration delay, stickiness)
aws elbv2 modify-target-group-attributes \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234 \
  --attributes \
    Key=deregistration_delay.timeout_seconds,Value=60 \
    Key=stickiness.enabled,Value=true \
    Key=stickiness.type,Value=lb_cookie \
    Key=stickiness.lb_cookie.duration_seconds,Value=86400

aws elbv2 delete-target-group \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234

# --- Register/Deregister Targets ---
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234 \
  --targets Id=i-12345678 Id=i-87654321

# Register IP targets (Fargate / cross-VPC)
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-ip-targets/1234 \
  --targets Id=10.0.1.50,Port=8080 Id=10.0.2.60,Port=8080

# Register Lambda target
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-lambda-targets/1234 \
  --targets Id=arn:aws:lambda:us-east-1:123456789012:function:my-function

aws elbv2 deregister-targets \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234 \
  --targets Id=i-12345678

aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/1234

# --- Listeners ---
# HTTP listener with redirect to HTTPS
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234 \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=redirect,RedirectConfig='{Protocol=HTTPS,Port=443,StatusCode=HTTP_301}'

# HTTPS listener with ACM cert
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234 \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:us-east-1:123456789012:certificate/abc123 \
  --ssl-policy ELBSecurityPolicy-TLS13-1-2-2021-06 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...

# TCP listener for NLB
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/net/my-nlb/1234 \
  --protocol TCP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...

aws elbv2 describe-listeners \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/1234

# Modify listener (e.g., update default action)
aws elbv2 modify-listener \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234/abcd \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...

# Add SNI certificate to HTTPS listener
aws elbv2 add-listener-certificates \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234/abcd \
  --certificates CertificateArn=arn:aws:acm:us-east-1:123456789012:certificate/xyz789

# --- Listener Rules ---
# Path-based routing rule
aws elbv2 create-rule \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234/abcd \
  --priority 10 \
  --conditions Field=path-pattern,Values=/api/* \
  --actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/api-targets/1234

# Host header routing rule
aws elbv2 create-rule \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234/abcd \
  --priority 20 \
  --conditions Field=host-header,Values=api.example.com \
  --actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...

# Weighted forward action (blue/green)
aws elbv2 create-rule \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234/abcd \
  --priority 30 \
  --conditions Field=path-pattern,Values=/app/* \
  --actions \
    Type=forward,ForwardConfig='{
      "TargetGroups": [
        {"TargetGroupArn": "arn:aws:elasticloadbalancing:...blue...", "Weight": 90},
        {"TargetGroupArn": "arn:aws:elasticloadbalancing:...green...", "Weight": 10}
      ]
    }'

# Cognito authentication rule
aws elbv2 create-rule \
  --listener-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-alb/1234/abcd \
  --priority 5 \
  --conditions Field=path-pattern,Values=/protected/* \
  --actions \
    '[
      {
        "Type": "authenticate-cognito",
        "Order": 1,
        "AuthenticateCognitoConfig": {
          "UserPoolArn": "arn:aws:cognito-idp:us-east-1:123456789012:userpool/us-east-1_abc123",
          "UserPoolClientId": "clientid123",
          "UserPoolDomain": "my-domain"
        }
      },
      {
        "Type": "forward",
        "Order": 2,
        "TargetGroupArn": "arn:aws:elasticloadbalancing:..."
      }
    ]'

aws elbv2 describe-rules --listener-arn arn:aws:elasticloadbalancing:...

# Update rule priorities
aws elbv2 set-rule-priorities \
  --rule-priorities \
    RuleArn=arn:aws:elasticloadbalancing:...:rule/...,Priority=5 \
    RuleArn=arn:aws:elasticloadbalancing:...:rule/...,Priority=10

aws elbv2 modify-rule \
  --rule-arn arn:aws:elasticloadbalancing:...:rule/... \
  --conditions Field=path-pattern,Values=/api/v2/*

aws elbv2 delete-rule --rule-arn arn:aws:elasticloadbalancing:...:rule/...
```
