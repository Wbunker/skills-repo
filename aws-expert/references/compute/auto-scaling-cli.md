# AWS Auto Scaling — CLI Reference

For service concepts, see [auto-scaling-capabilities.md](auto-scaling-capabilities.md).

## EC2 — Auto Scaling

```bash
# --- Auto Scaling Groups ---
# Create ASG using a Launch Template
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name my-app-asg \
  --launch-template LaunchTemplateId=lt-0abcd1234efgh5678,Version='$Latest' \
  --min-size 2 \
  --max-size 20 \
  --desired-capacity 4 \
  --vpc-zone-identifier "subnet-0abc123,subnet-0def456,subnet-0ghi789" \
  --target-group-arns arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-tg/abc123 \
  --health-check-type ELB \
  --health-check-grace-period 300 \
  --tags "Key=Name,Value=my-app-asg,PropagateAtLaunch=true"

# Create ASG with mixed instances (On-Demand + Spot)
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name my-mixed-asg \
  --mixed-instances-policy '{
    "LaunchTemplate": {
      "LaunchTemplateSpecification": {"LaunchTemplateId": "lt-0abc", "Version": "$Latest"},
      "Overrides": [
        {"InstanceType": "m7g.large"},
        {"InstanceType": "m6g.large"},
        {"InstanceType": "c7g.large"}
      ]
    },
    "InstancesDistribution": {
      "OnDemandBaseCapacity": 2,
      "OnDemandPercentageAboveBaseCapacity": 20,
      "SpotAllocationStrategy": "price-capacity-optimized"
    }
  }' \
  --min-size 2 --max-size 50 --desired-capacity 6 \
  --vpc-zone-identifier "subnet-0abc123,subnet-0def456"

aws autoscaling describe-auto-scaling-groups
aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names my-app-asg
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name my-app-asg \
  --min-size 4 \
  --max-size 40

aws autoscaling delete-auto-scaling-group \
  --auto-scaling-group-name my-app-asg \
  --force-delete

# Set desired capacity manually
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name my-app-asg \
  --desired-capacity 8 \
  --honor-cooldown

# --- Scaling Policies ---
# Target tracking: keep CPU at 60%
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name my-app-asg \
  --policy-name cpu-target-tracking \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{
    "PredefinedMetricSpecification": {"PredefinedMetricType": "ASGAverageCPUUtilization"},
    "TargetValue": 60.0,
    "DisableScaleIn": false
  }'

# Step scaling policy
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name my-app-asg \
  --policy-name scale-out-step \
  --policy-type StepScaling \
  --adjustment-type ChangeInCapacity \
  --step-adjustments '[
    {"MetricIntervalLowerBound": 0, "MetricIntervalUpperBound": 20, "ScalingAdjustment": 2},
    {"MetricIntervalLowerBound": 20, "ScalingAdjustment": 4}
  ]'

# Scheduled scaling (e.g., scale up before business hours)
aws autoscaling put-scheduled-update-group-action \
  --auto-scaling-group-name my-app-asg \
  --scheduled-action-name scale-up-morning \
  --recurrence "0 7 * * 1-5" \
  --min-size 6 \
  --desired-capacity 10

aws autoscaling describe-policies --auto-scaling-group-name my-app-asg
aws autoscaling delete-policy --auto-scaling-group-name my-app-asg --policy-name cpu-target-tracking

# --- Lifecycle Hooks ---
aws autoscaling put-lifecycle-hook \
  --auto-scaling-group-name my-app-asg \
  --lifecycle-hook-name drain-connections \
  --lifecycle-transition autoscaling:EC2_INSTANCE_TERMINATING \
  --heartbeat-timeout 300 \
  --default-result CONTINUE \
  --notification-target-arn arn:aws:sqs:us-east-1:123456789012:lifecycle-hook-queue \
  --role-arn arn:aws:iam::123456789012:role/AutoScalingNotificationRole

aws autoscaling complete-lifecycle-action \
  --auto-scaling-group-name my-app-asg \
  --lifecycle-hook-name drain-connections \
  --instance-id i-0abc123def456789 \
  --lifecycle-action-result CONTINUE

aws autoscaling describe-lifecycle-hooks --auto-scaling-group-name my-app-asg

# --- Instance Refresh (rolling AMI update) ---
aws autoscaling start-instance-refresh \
  --auto-scaling-group-name my-app-asg \
  --preferences '{
    "MinHealthyPercentage": 90,
    "InstanceWarmup": 300,
    "SkipMatching": false,
    "CheckpointPercentages": [20, 50],
    "CheckpointDelay": 600
  }' \
  --desired-configuration '{"LaunchTemplate":{"LaunchTemplateId":"lt-0abc","Version":"3"}}'

aws autoscaling describe-instance-refreshes --auto-scaling-group-name my-app-asg
aws autoscaling cancel-instance-refresh --auto-scaling-group-name my-app-asg

# --- Warm Pools ---
aws autoscaling put-warm-pool \
  --auto-scaling-group-name my-app-asg \
  --pool-state Stopped \
  --min-size 2

aws autoscaling describe-warm-pool --auto-scaling-group-name my-app-asg
aws autoscaling delete-warm-pool --auto-scaling-group-name my-app-asg --force-delete

# --- Instance Protection ---
aws autoscaling set-instance-protection \
  --instance-ids i-0abc123def456789 \
  --auto-scaling-group-name my-app-asg \
  --protected-from-scale-in

# --- Describe Scaling Activity ---
aws autoscaling describe-scaling-activities --auto-scaling-group-name my-app-asg
aws autoscaling describe-account-limits
```
