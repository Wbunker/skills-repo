# AWS Auto Scaling — Capabilities Reference

For CLI commands, see [auto-scaling-cli.md](auto-scaling-cli.md).

## EC2 Auto Scaling

**Purpose**: Automatically maintain the right number of EC2 instances to handle application load, with support for mixed instance types, Spot, and advanced scaling controls.

### Core Concepts

| Concept | Description |
|---|---|
| **Auto Scaling group (ASG)** | Logical group of instances with min, desired, and max capacity bounds |
| **Launch Template** | Configuration source for new instances (AMI, type, network, IAM profile, etc.) |
| **Desired capacity** | Current target instance count; adjusted by scaling policies or manually |
| **Health check** | EC2 status checks (default) or ELB health checks; unhealthy instances replaced |
| **Cooldown period** | Pause after a scaling event before another can occur (simple/step scaling) |
| **Warm pool** | Pre-initialized instances in a stopped/running state ready to serve traffic quickly |

### Scaling Policy Types

| Type | Trigger | Use Case |
|---|---|---|
| **Target tracking** | Maintain a metric at a target value (e.g., CPU at 50%) | Preferred; simplest to configure |
| **Step scaling** | Scale by different amounts based on alarm breach magnitude | Fine-grained response to metric levels |
| **Simple scaling** | Add/remove fixed number on alarm breach; waits for cooldown | Legacy; prefer step or target tracking |
| **Scheduled scaling** | Scale to defined capacity at specific times (cron or one-time) | Predictable load patterns |
| **Predictive scaling** | ML-based forecast of future demand; proactively provisions | Recurring cyclical load patterns |

### Mixed Instances Policy

- Combine multiple instance types and sizes in a single ASG
- Specify On-Demand and Spot capacity percentages
- `lowest-price` or `capacity-optimized` (recommended) allocation strategy for Spot
- **Capacity Rebalancing**: Proactively replace Spot Instances receiving rebalance recommendations

### Lifecycle Hooks

- Pause instance during launch (`autoscaling:EC2_INSTANCE_LAUNCHING`) or termination (`autoscaling:EC2_INSTANCE_TERMINATING`)
- Use to run custom logic: install software, drain connections, snapshot EBS
- Instance remains in `Pending:Wait` or `Terminating:Wait` state until action is completed or timeout

### Instance Refresh

- Rolling replacement of instances to apply new AMI or configuration
- Configurable: minimum healthy percentage, warm-up time, checkpoint intervals
- Supports canary deployments (deploy to a small percentage first)

### Key Constraints

- One Launch Template (or Launch Configuration) per ASG, but multiple versions can be referenced
- ASG spans multiple AZs but resides in one region
- Spot interruptions trigger automatic replacement from the capacity pool
