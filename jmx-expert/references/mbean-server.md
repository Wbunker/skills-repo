# MBean Server and Agent Services

From Chapters 6–7 of *Java Management Extensions* by J. Steven Perry.

## The MBean Server

The MBean Server is the central registry. It is the agent layer's core component: every MBean must be registered with it, and all management operations pass through it.

### Creating and Locating an MBean Server

```java
// Option 1: Platform MBean Server (JDK 5+, preferred for applications)
MBeanServer mbs = ManagementFactory.getPlatformMBeanServer();

// Option 2: Create a new MBean Server instance
MBeanServer mbs = MBeanServerFactory.createMBeanServer("com.example");

// Option 3: Find existing servers
ArrayList<MBeanServer> servers = MBeanServerFactory.findMBeanServer(null);
// null = return all; pass an agentId to filter
```

Use `ManagementFactory.getPlatformMBeanServer()` for almost all application code. Multiple MBean Server instances in one JVM are unusual and complicate connector setup.

### ObjectName

`ObjectName` is the unique identity of a registered MBean.

```java
// Fully qualified
ObjectName name = new ObjectName("com.example:type=Cache,name=primary");

// Wildcard — for queries only (cannot register with a wildcard name)
ObjectName pattern = new ObjectName("com.example:type=Cache,*");
ObjectName allInDomain = new ObjectName("com.example:*");
ObjectName everything = new ObjectName("*:*");

// Key ordering is irrelevant for equality
new ObjectName("a:k1=v1,k2=v2").equals(new ObjectName("a:k2=v2,k1=v1")); // true
```

Canonical property key order: keys are sorted lexicographically in `getCanonicalName()`.

### Registration and Unregistration

```java
// Register
mbs.registerMBean(mbean, name);

// Unregister
mbs.unregisterMBean(name);

// Check existence
boolean exists = mbs.isRegistered(name);

// Get MBean count
int count = mbs.getMBeanCount();
```

`registerMBean` returns an `ObjectInstance` containing the `ObjectName` and class name. The MBean class must be visible to the MBean Server's class loader (or use `ClassLoaderRepository`).

### Attribute Operations

```java
// Read single attribute
Object val = mbs.getAttribute(name, "Size");

// Read multiple attributes
String[] attrNames = {"Size", "Capacity", "LoadFactor"};
AttributeList list = mbs.getAttributes(name, attrNames);

// Write single attribute
mbs.setAttribute(name, new Attribute("Capacity", 500));

// Write multiple attributes
AttributeList updates = new AttributeList();
updates.add(new Attribute("Capacity", 500));
updates.add(new Attribute("LoadFactor", 0.75f));
mbs.setAttributes(name, updates);
```

### Invoking Operations

```java
// No parameters
mbs.invoke(name, "reset", new Object[]{}, new String[]{});

// With parameters — signature array uses class names as Strings
mbs.invoke(name, "resize",
    new Object[]{ 1000, true },
    new String[]{ "int", "boolean" });

// Returning a value
Integer result = (Integer) mbs.invoke(name, "computeChecksum",
    new Object[]{ "data" },
    new String[]{ String.class.getName() });
```

### Querying the MBean Server

```java
// By ObjectName pattern
Set<ObjectName> names = mbs.queryNames(new ObjectName("com.example:*"), null);

// By ObjectName pattern + filter
QueryExp filter = Query.eq(Query.attr("State"), Query.value("ACTIVE"));
Set<ObjectName> active = mbs.queryNames(new ObjectName("com.example:*"), filter);

// queryMBeans returns ObjectInstance (includes class name)
Set<ObjectInstance> instances = mbs.queryMBeans(new ObjectName("*:*"), null);
```

`QueryExp` combinators:

```java
Query.eq(Query.attr("State"), Query.value("RUNNING"))
Query.and(expr1, expr2)
Query.or(expr1, expr2)
Query.not(expr)
Query.gt(Query.attr("Count"), Query.value(100))
Query.between(Query.attr("Temp"), Query.value(0), Query.value(100))
Query.match(Query.attr("Name"), Query.value("cache-*"))  // glob
Query.isInstanceOf(Query.value("com.example.Cache"))
```

---

## Agent Services

The JMX agent provides four built-in management services registered in the MBean Server.

### Timer Service

Fires periodic or one-time notifications on a schedule.

```java
// Get or create the Timer service
Timer timer = new Timer();
ObjectName timerName = new ObjectName("com.example:type=Timer,name=scheduler");
mbs.registerMBean(timer, timerName);

// Add a periodic notification — every 5 seconds
Date startDate = new Date(System.currentTimeMillis() + 1000);
Integer notifId = timer.addNotification(
    "com.example.heartbeat",   // type
    "Heartbeat",               // message
    null,                      // user data
    startDate,                 // first occurrence
    5000L,                     // period (ms)
    0L                         // occurrences (0 = infinite)
);

timer.start();

// Remove a notification
timer.removeNotification(notifId);
timer.stop();
```

### Monitor Service

Monitors attribute values and emits notifications when thresholds are crossed.

#### CounterMonitor — numeric threshold, counts up

```java
CounterMonitor counter = new CounterMonitor();
ObjectName monitorName = new ObjectName("com.example:type=Monitor,name=errorCount");
mbs.registerMBean(counter, monitorName);

counter.addObservedObject(name);           // MBean to watch
counter.setObservedAttribute("ErrorCount"); // attribute name
counter.setInitThreshold(Long.valueOf(100)); // alert when >= 100
counter.setGranularityPeriod(1000L);        // poll every 1s
counter.setNotify(true);
counter.start();
```

#### GaugeMonitor — range alerts (high/low watermarks)

```java
GaugeMonitor gauge = new GaugeMonitor();
// ...register...
gauge.addObservedObject(name);
gauge.setObservedAttribute("ActiveConnections");
gauge.setThresholds(Number.class.cast(80), Number.class.cast(20)); // high, low
gauge.setNotifyHigh(true);
gauge.setNotifyLow(true);
gauge.setGranularityPeriod(2000L);
gauge.start();
```

#### StringMonitor — string value equality alert

```java
StringMonitor strMonitor = new StringMonitor();
// ...register...
strMonitor.addObservedObject(name);
strMonitor.setObservedAttribute("State");
strMonitor.setStringToCompare("FAILED");
strMonitor.setNotifyMatch(true);     // alert when value == "FAILED"
strMonitor.setNotifyDiffer(false);   // no alert when value != "FAILED"
strMonitor.setGranularityPeriod(1000L);
strMonitor.start();
```

### Relation Service

Manages typed relationships between MBeans.

```java
RelationService relService = new RelationService(true); // purge on unregister
ObjectName relServiceName = new ObjectName("JMXInternal:type=RelationService");
mbs.registerMBean(relService, relServiceName);
RelationServiceMBean relServiceProxy =
    JMX.newMBeanProxy(mbs, relServiceName, RelationServiceMBean.class);

// Define a relation type: "uses" — Cache uses DataSource
RoleInfo cacheRole = new RoleInfo("cache", Cache.class.getName(), true, false, 1, 1, "Cache");
RoleInfo dsRole = new RoleInfo("dataSource", DataSource.class.getName(), true, false, 1, 5, "DataSources");
relServiceProxy.createRelationType("uses", new RoleInfo[]{cacheRole, dsRole});

// Create a relation instance
RoleList roles = new RoleList();
roles.add(new Role("cache", List.of(cacheObjectName)));
roles.add(new Role("dataSource", List.of(dsObjectName1, dsObjectName2)));
relServiceProxy.createRelation("cache-uses-ds", "uses", roles);

// Query relations
List<String> relIds = relServiceProxy.findRelationsOfType("uses");
```

### ClassLoader Repository

The MBean Server maintains a `ClassLoaderRepository` containing class loaders of all registered MBeans that implement `ClassLoader`. Use `mbs.getClassLoaderRepository()` to load classes dynamically.

---

## MBeanServerDelegate

The MBean Server registers itself as `JMImplementation:type=MBeanServerDelegate`. It emits `MBeanServerNotification` events for:

- `MBeanServerNotification.REGISTRATION_NOTIFICATION` — MBean registered
- `MBeanServerNotification.UNREGISTRATION_NOTIFICATION` — MBean unregistered

```java
mbs.addNotificationListener(
    MBeanServerDelegate.DELEGATE_NAME,
    (notification, handback) -> {
        MBeanServerNotification n = (MBeanServerNotification) notification;
        System.out.println("MBean " + n.getType() + ": " + n.getMBeanName());
    },
    null, null);
```

## JMX.newMBeanProxy — Typed Proxy

```java
// Create a typed proxy for a Standard MBean
HelloMBean proxy = JMX.newMBeanProxy(mbs, name, HelloMBean.class);
proxy.setName("World");
proxy.printHello();

// MXBean proxy (for platform MXBeans using Open Types)
MemoryMXBean memProxy = ManagementFactory.getMemoryMXBean();
MemoryUsage heap = memProxy.getHeapMemoryUsage();
```

Proxies forward calls to `getAttribute`, `setAttribute`, and `invoke` on the MBean Server. They are the cleanest way to interact with MBeans from application code.
