# Monitoring and Management Patterns

From Chapter 12 and practical examples throughout *Java Management Extensions* by J. Steven Perry.

## Instrumentation Design Principles

1. **Expose what operations need to observe** — throughput, queue depths, error counts, latencies, state transitions
2. **Avoid exposing internal implementation details** that change across versions
3. **Use standard JDK MXBeans as inspiration** — `MemoryMXBean`, `ThreadMXBean`, `RuntimeMXBean` model good attribute design
4. **Composite attributes for related data** — use `CompositeData` rather than many scalar attributes for related values (e.g., high/low/current watermarks)
5. **Notifications for state transitions** — don't poll; emit `Notification` when state changes

---

## Platform MXBeans (JDK Built-in)

The JDK instruments itself via `ManagementFactory`:

```java
// Memory
MemoryMXBean mem = ManagementFactory.getMemoryMXBean();
MemoryUsage heap = mem.getHeapMemoryUsage();
long used = heap.getUsed();
long max  = heap.getMax();

// Threading
ThreadMXBean threads = ManagementFactory.getThreadMXBean();
long[] deadlocked = threads.findDeadlockedThreads(); // null if none
int threadCount = threads.getThreadCount();

// Runtime
RuntimeMXBean runtime = ManagementFactory.getRuntimeMXBean();
long uptimeMs = runtime.getUptime();
String jvmName = runtime.getVmName();

// Garbage collectors
for (GarbageCollectorMXBean gc : ManagementFactory.getGarbageCollectorMXBeans()) {
    System.out.println(gc.getName() + " collections: " + gc.getCollectionCount()
        + " time: " + gc.getCollectionTime() + "ms");
}

// Class loading
ClassLoadingMXBean cl = ManagementFactory.getClassLoadingMXBean();
int loaded = cl.getLoadedClassCount();
```

---

## Standard Application Monitoring Pattern

### Throughput and Error Counter MBean

```java
// Interface
public interface RequestStatsMBean {
    long getRequestCount();
    long getErrorCount();
    double getErrorRate();          // errors / requests
    long getAverageLatencyMs();
    void resetStats();
}

// Implementation
public class RequestStats extends NotificationBroadcasterSupport
        implements RequestStatsMBean {
    private final AtomicLong requestCount = new AtomicLong();
    private final AtomicLong errorCount   = new AtomicLong();
    private final AtomicLong totalLatency = new AtomicLong();
    private final AtomicLong seq          = new AtomicLong();

    public void recordRequest(long latencyMs, boolean error) {
        requestCount.incrementAndGet();
        totalLatency.addAndGet(latencyMs);
        if (error) {
            long errors = errorCount.incrementAndGet();
            long total  = requestCount.get();
            double rate = (double) errors / total;
            if (rate > 0.05) {  // >5% error rate alert
                sendNotification(new Notification(
                    "com.example.stats.high-error-rate",
                    this, seq.incrementAndGet(),
                    System.currentTimeMillis(),
                    String.format("Error rate %.1f%%", rate * 100)));
            }
        }
    }

    @Override public long getRequestCount() { return requestCount.get(); }
    @Override public long getErrorCount()   { return errorCount.get(); }

    @Override public double getErrorRate() {
        long total = requestCount.get();
        return total == 0 ? 0.0 : (double) errorCount.get() / total;
    }

    @Override public long getAverageLatencyMs() {
        long total = requestCount.get();
        return total == 0 ? 0L : totalLatency.get() / total;
    }

    @Override public void resetStats() {
        requestCount.set(0);
        errorCount.set(0);
        totalLatency.set(0);
    }
}
```

---

## Using GaugeMonitor for Resource Alerting

Trigger alerts when a gauge exceeds or drops below watermarks:

```java
// Alert when connection pool active connections exceed 80 (high) or drop below 5 (low)
GaugeMonitor poolMonitor = new GaugeMonitor();
ObjectName monitorName = new ObjectName("com.example:type=Monitor,name=poolGauge");
mbs.registerMBean(poolMonitor, monitorName);

poolMonitor.addObservedObject(new ObjectName("com.example:type=ConnectionPool"));
poolMonitor.setObservedAttribute("ActiveCount");
poolMonitor.setThresholds(Number.class.cast(80), Number.class.cast(5));
poolMonitor.setNotifyHigh(true);
poolMonitor.setNotifyLow(true);
poolMonitor.setDifferenceMode(false);   // observe absolute value
poolMonitor.setGranularityPeriod(5000L); // poll every 5s

// Subscribe to the monitor's alerts
mbs.addNotificationListener(monitorName,
    (notif, handback) -> {
        MonitorNotification mn = (MonitorNotification) notif;
        System.out.println("Pool alert: " + mn.getType()
            + " triggered value: " + mn.getTrigger());
    },
    null, null);

poolMonitor.start();
```

`MonitorNotification` types:
- `MonitorNotification.THRESHOLD_HIGH_VALUE_EXCEEDED`
- `MonitorNotification.THRESHOLD_LOW_VALUE_EXCEEDED`
- `MonitorNotification.THRESHOLD_VALUE_EXCEEDED` (CounterMonitor)
- `MonitorNotification.STRING_TO_COMPARE_VALUE_MATCHED`
- `MonitorNotification.STRING_TO_COMPARE_VALUE_DIFFERED`

---

## Periodic Health Check with Timer

```java
Timer timer = new Timer();
ObjectName timerName = new ObjectName("com.example:type=Timer,name=healthCheck");
mbs.registerMBean(timer, timerName);

// Subscribe to timer notifications and perform health check in listener
mbs.addNotificationListener(timerName,
    (notif, handback) -> {
        MBeanServer server = (MBeanServer) handback;
        try {
            // Check JVM heap usage
            MemoryMXBean mem = ManagementFactory.getMemoryMXBean();
            MemoryUsage heap = mem.getHeapMemoryUsage();
            double pct = (double) heap.getUsed() / heap.getMax() * 100;
            if (pct > 85.0) {
                System.err.println("WARN: Heap at " + String.format("%.1f%%", pct));
            }
        } catch (Exception e) {
            System.err.println("Health check failed: " + e.getMessage());
        }
    },
    null, mbs);  // pass mbs as handback

Date start = new Date(System.currentTimeMillis() + 5000);
timer.addNotification("com.example.healthcheck", "Health check", null,
    start, 30_000L, 0L);  // every 30s, indefinitely
timer.start();
```

---

## MXBean Pattern (Java 6+)

`@MXBean` (or naming a class `XMXBean`) is the modern evolution. It automatically marshals complex types to Open Types for remote accessibility.

```java
@MXBean
public interface CacheStatsMXBean {
    CompositeData getUsageStats();  // auto-marshalled to CompositeData
    TabularData getTopKeys();       // auto-marshalled to TabularData
    void evictAll();
}

public class CacheStats implements CacheStatsMXBean {
    // Return a POJO — JMX converts it to CompositeData via reflection
    public UsageStats getUsageStats() {
        return new UsageStats(hits, misses, evictions);
    }
    // ...
}

// Registration — same as Standard MBean
mbs.registerMBean(new CacheStats(), new ObjectName("com.example:type=Cache"));
```

The `UsageStats` POJO must have `getX()` methods for each field. JMX generates the `CompositeType` automatically.

---

## JConsole and Java Mission Control Integration

These tools connect via the RMI connector:

```
# JConsole (bundled with JDK)
jconsole service:jmx:rmi:///jndi/rmi://localhost:9000/jmxrmi

# Java Mission Control (JDK 11+)
jmc
```

For JConsole plugin development, implement `com.sun.tools.jconsole.JConsolePlugin`.

---

## Common Operational Patterns

### Exposing Configuration Reload

```java
public interface AppConfigMBean {
    String getConfigFile();
    void reloadConfig();          // operation: re-reads config file
    boolean isAutoReloadEnabled();
    void setAutoReloadEnabled(boolean enabled);
}
```

### Exposing Circuit Breaker State

```java
public interface CircuitBreakerMBean {
    String getState();           // CLOSED, OPEN, HALF_OPEN
    int getFailureCount();
    long getLastFailureTime();   // epoch ms
    void reset();                // force back to CLOSED
    void tripOpen();             // force to OPEN for testing
}
```

### Thread Pool Monitoring

```java
public interface ThreadPoolMBean {
    int getCorePoolSize();
    void setCorePoolSize(int size);
    int getMaximumPoolSize();
    void setMaximumPoolSize(int size);
    int getActiveCount();
    long getCompletedTaskCount();
    int getQueueSize();
    int getLargestPoolSize();
}

// Wrap a ThreadPoolExecutor
public class ThreadPoolAdapter implements ThreadPoolMBean {
    private final ThreadPoolExecutor pool;
    public ThreadPoolAdapter(ThreadPoolExecutor pool) { this.pool = pool; }

    @Override public int getCorePoolSize() { return pool.getCorePoolSize(); }
    @Override public void setCorePoolSize(int s) { pool.setCorePoolSize(s); }
    @Override public int getActiveCount() { return pool.getActiveCount(); }
    @Override public long getCompletedTaskCount() { return pool.getCompletedTaskCount(); }
    @Override public int getQueueSize() { return pool.getQueue().size(); }
    @Override public int getMaximumPoolSize() { return pool.getMaximumPoolSize(); }
    @Override public void setMaximumPoolSize(int s) { pool.setMaximumPoolSize(s); }
    @Override public int getLargestPoolSize() { return pool.getLargestPoolSize(); }
}
```

---

## Naming Convention Cheat Sheet

```
# Single instance per type
com.company.app:type=Cache
com.company.app:type=ConnectionPool

# Named instances
com.company.app:type=Cache,name=user-cache
com.company.app:type=Cache,name=session-cache

# Hierarchical
com.company.app:type=DataSource,module=orders,name=primary

# Monitors and timers (separate domain or type)
com.company.app:type=Monitor,observing=Cache
com.company.app:type=Timer,name=health-check
```
