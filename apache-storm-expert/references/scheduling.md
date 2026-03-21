# Storm Scheduler
## Chapter 6: Cluster Scheduling, Resource Allocation, and Multi-Tenancy

---

## Why Scheduling Matters

By default, Storm's scheduler distributes tasks across available Supervisor slots without regard to topology priority, resource isolation, or co-location preferences. For shared clusters running multiple topologies, the default scheduler can cause resource contention and unpredictable performance.

---

## Default Scheduler (EvenScheduler)

Storm's built-in `EvenScheduler` distributes tasks across available slots using a simple round-robin strategy:

- **Goal**: spread topology executors across as many worker processes/nodes as possible
- **Algorithm**: assign workers to topologies in round-robin order, then assign executors evenly across the assigned workers
- **No isolation**: topologies share Supervisor nodes; one topology cannot reserve dedicated nodes
- **No resource awareness**: does not account for CPU, memory, or network capacity per slot

**Configuration** (default — no action needed):
```yaml
storm.scheduler: "org.apache.storm.scheduler.EvenScheduler"
```

---

## Isolation Scheduler

The `IsolationScheduler` provides **node-level isolation** for specific topologies — their workers run on dedicated Supervisor nodes, not shared with other topologies.

```yaml
storm.scheduler: "org.apache.storm.scheduler.IsolationScheduler"

isolation.scheduler.machines:
  "critical-topology": 3    # 3 dedicated Supervisor nodes
  "reporting-topology": 2   # 2 dedicated nodes
  # All other topologies share the remaining nodes
```

**Use when**: SLA-critical topologies must not be affected by noisy neighbors.

**Limitations**:
- Node-level granularity only (cannot isolate by CPU/memory within a node)
- Non-isolated topologies share remaining nodes
- Static configuration — requires cluster restart to change allocations

---

## Resource-Aware Scheduler (RAS)

Introduced in Storm 1.x, the Resource-Aware Scheduler allows topologies to **declare CPU and memory requirements** per component, and the scheduler honors those constraints when placing tasks.

### Declaring Resources

```java
// Per-component CPU and memory requirements
builder.setBolt("heavy-bolt", new HeavyBolt(), 4)
       .shuffleGrouping("spout")
       .setCPULoad(150.0)       // 150% of a CPU core (1.5 cores)
       .setMemoryLoad(512.0);   // 512 MB on-heap

builder.setSpout("kafka-spout", new KafkaSpout(), 2)
       .setCPULoad(50.0)
       .setMemoryLoad(256.0, 64.0);  // 256 MB on-heap, 64 MB off-heap
```

### Supervisor Resource Configuration

```yaml
supervisor.cpu.capacity: 400.0    # 4 CPU cores (100 per core)
supervisor.memory.capacity.mb: 8192  # 8 GB RAM
```

### Topology Resource Budget

```java
Config conf = new Config();
conf.setTopologyCPUBudget(600.0);       // total CPU budget
conf.setTopologyMemoryBudgetMb(4096);   // total memory budget
conf.setTopologyWorkerMaxHeapSize(768); // per-worker JVM heap
```

### Scheduling Strategies within RAS

- **DefaultResourceAwareStrategy**: bin-packs tasks onto nodes to maximize cluster utilization
- **ConstraintSolverStrategy**: honors user-specified co-location and anti-affinity constraints

---

## Multi-Tenant Storm: Topology Priority

RAS supports topology scheduling priority for multi-tenant clusters:

```java
conf.setTopologyPriority(1);  // lower number = higher priority
```

When resources are scarce, higher-priority topologies are scheduled first. Lower-priority topologies may be evicted (killed) to make room.

**Priority tiers** (configurable per-user or per-topology):
```yaml
topology.priority: 0    # highest priority (reserved)
topology.priority: 5    # normal
topology.priority: 29   # lowest (best-effort)
```

---

## Custom Scheduler

Implement `IScheduler` to build a scheduler with custom logic:

```java
public class MyScheduler implements IScheduler {
    public void prepare(Map conf) { ... }

    public void schedule(Topologies topologies, Cluster cluster) {
        // Get available slots
        List<WorkerSlot> availableSlots = cluster.getAvailableSlots();

        // Get unassigned topologies
        Collection<TopologyDetails> unassigned = cluster.needsSchedulingTopologies(topologies);

        for (TopologyDetails topology : unassigned) {
            // Your custom assignment logic
            List<ExecutorDetails> executors = cluster.getUnassignedExecutors(topology);
            // assign(topology, Map<WorkerSlot, List<ExecutorDetails>>)
            cluster.assign(slot, topology.getId(), executors);
        }
    }
}
```

Register via `storm.yaml`:
```yaml
storm.scheduler: "com.example.MyScheduler"
```

---

## Scheduler Comparison

| Scheduler | Isolation | Resource-Aware | Priority | When to Use |
|-----------|-----------|---------------|----------|-------------|
| EvenScheduler | None | No | No | Dev/test; single-tenant production |
| IsolationScheduler | Node-level | No | No | Critical topologies needing dedicated nodes |
| ResourceAwareScheduler | Component-level | Yes | Yes | Multi-tenant clusters with mixed workloads |
| Custom | Arbitrary | Custom | Custom | Special placement constraints |

---

## Practical Scheduling Patterns

### Reserve Nodes for Critical Topologies

Use IsolationScheduler to pin SLA-critical topologies to dedicated nodes:
```yaml
isolation.scheduler.machines:
  "fraud-detection": 5
  "payment-processing": 3
```

### Right-Sizing with RAS

1. Profile each bolt's CPU and memory usage in staging
2. Set `setCPULoad` and `setMemoryLoad` with 20% headroom
3. Set `supervisor.cpu.capacity` and `supervisor.memory.capacity.mb` based on actual hardware
4. Monitor placement via Storm UI → Topology → Worker Resources

### Controlling Worker Heap

Per-topology worker heap size — prevent OOM without wasting cluster memory:

```java
conf.setTopologyWorkerMaxHeapSize(1024); // 1 GB per worker JVM
```

Also configure GC settings via `topology.worker.gc.childopts`:
```java
conf.put(Config.TOPOLOGY_WORKER_GC_CHILDOPTS,
         "-XX:+UseG1GC -XX:MaxGCPauseMillis=100");
```
