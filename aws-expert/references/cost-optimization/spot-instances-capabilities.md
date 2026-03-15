# AWS Spot Instances — Capabilities Reference
For CLI commands, see [spot-instances-cli.md](spot-instances-cli.md).

## EC2 Spot Instances

**Purpose**: Use spare EC2 capacity at discounts of up to 90% versus On-Demand pricing. AWS can reclaim capacity with a 2-minute warning, making Spot best suited for fault-tolerant, flexible workloads.

### Interruption Model

| Concept | Details |
|---|---|
| **2-minute interruption notice** | EC2 emits an instance interruption notification before terminating/stopping/hibernating the instance |
| **Rebalance Recommendation signal** | EC2 emits a proactive signal when a Spot Instance is at elevated interruption risk, before the 2-minute notice |
| **Interruption behaviors** | Terminate (default), Stop, or Hibernate — configured at request time |
| **Who controls interruption** | AWS reclaims capacity when needed; user cannot prevent it |

### Spot Instance Request Types

| Type | Behavior |
|---|---|
| **One-time** | Fulfilled once; if interrupted, request is not resubmitted |
| **Persistent** | Automatically resubmits request after interruption until cancelled or expired |

### Spot Fleet Allocation Strategies

| Strategy | How it works | Interruption Risk | Best for |
|---|---|---|---|
| **`priceCapacityOptimized`** (recommended) | Launches from pools with highest capacity + lowest price | Lowest | Most Spot workloads: containers, web, batch |
| **`capacityOptimized`** | Launches from pools with highest capacity availability | Lowest | High interruption cost: HPC, DL training, long CI |
| **`capacityOptimizedPrioritized`** | Capacity-optimized but honors instance type priority | Lowest | Capacity focus + specific instance preference |
| **`diversified`** | Distributes instances evenly across all specified pools | Low | Large, long-running fleets |
| **`lowestPrice`** | Cheapest pool with available capacity (default CLI) | Highest | Not recommended — ignores capacity risk |

### Spot with Auto Scaling Groups

- Use **mixed instances policy** to combine On-Demand base capacity with Spot for scale-out
- Specify multiple instance types and sizes to reduce risk of capacity shortage in any single pool
- ASG automatically replaces interrupted Spot Instances; uses Capacity Rebalancing to launch replacements proactively before interruption

### Best Practices for Interruption Handling

- Design for interruption: checkpoint state, use distributed/parallel job frameworks
- Specify many instance types across multiple Availability Zones
- Use `priceCapacityOptimized` allocation strategy
- Leverage EC2 Rebalance Recommendation signal to gracefully drain workloads
- Use Spot with On-Demand base capacity in ASG or EC2 Fleet for critical workloads

### Spot Advisor

- AWS tool (console/web) showing historical interruption frequency and savings by instance type and region
- Helps select instance types with low interruption rates (e.g., <5%) for a given region/AZ
