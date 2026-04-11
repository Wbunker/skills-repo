# Open MBeans and Model MBeans

From Chapters 4–5 of *Java Management Extensions* by J. Steven Perry.

---

## Open MBeans

### Purpose

Open MBeans extend Dynamic MBeans with a restricted set of *Open Types* for attribute and operation parameter/return types. The goal is class-loader-independent interoperability: a remote manager can reconstruct values without having the application's classes on its classpath.

### Open Types Hierarchy

```
OpenType (abstract)
  SimpleType        — primitives + String, Date, ObjectName, BigInteger, BigDecimal
  ArrayType         — array of any OpenType
  CompositeType     — named record (like a struct or row)
  TabularType       — table of CompositeData rows, keyed by index names
```

### SimpleType Constants

```java
SimpleType.BOOLEAN    SimpleType.BYTE       SimpleType.CHARACTER
SimpleType.SHORT      SimpleType.INTEGER    SimpleType.LONG
SimpleType.FLOAT      SimpleType.DOUBLE     SimpleType.STRING
SimpleType.DATE       SimpleType.BIGDECIMAL SimpleType.BIGINTEGER
SimpleType.OBJECTNAME SimpleType.VOID
```

### CompositeType and CompositeData

`CompositeType` describes a record schema; `CompositeDataSupport` holds the values.

```java
// Define the schema
CompositeType serverInfoType = new CompositeType(
    "ServerInfo",                                   // typeName
    "Server status information",                    // description
    new String[]{"host", "port", "uptime"},         // itemNames
    new String[]{"Hostname", "Port", "Uptime ms"},  // itemDescriptions
    new OpenType[]{SimpleType.STRING, SimpleType.INTEGER, SimpleType.LONG}
);

// Create a value
Map<String, Object> values = new HashMap<>();
values.put("host", "localhost");
values.put("port", 8080);
values.put("uptime", System.currentTimeMillis() - startTime);

CompositeData serverInfo = new CompositeDataSupport(serverInfoType, values);

// Access fields
String host = (String) serverInfo.get("host");
```

### TabularType and TabularData

```java
// Build row type
CompositeType rowType = new CompositeType(
    "ConnectionRow", "A connection entry",
    new String[]{"id", "remoteAddr", "bytes"},
    new String[]{"ID", "Remote address", "Bytes transferred"},
    new OpenType[]{SimpleType.INTEGER, SimpleType.STRING, SimpleType.LONG}
);

// Build table type — index is "id"
TabularType tableType = new TabularType(
    "ConnectionTable", "Active connections",
    rowType, new String[]{"id"}
);

// Populate
TabularData table = new TabularDataSupport(tableType);
Map<String, Object> row = new HashMap<>();
row.put("id", 1);
row.put("remoteAddr", "10.0.0.5");
row.put("bytes", 4096L);
table.put(new CompositeDataSupport(rowType, row));
```

### Open MBean Descriptors

```java
// OpenMBeanAttributeInfoSupport for Open MBean attribute
OpenMBeanAttributeInfoSupport attrInfo = new OpenMBeanAttributeInfoSupport(
    "ServerInfo",
    "Current server state",
    serverInfoType,   // OpenType
    true,             // readable
    false,            // writable
    false             // isIs
);

// OpenMBeanOperationInfoSupport
OpenMBeanParameterInfoSupport param = new OpenMBeanParameterInfoSupport(
    "threshold", "Alert threshold", SimpleType.INTEGER);

OpenMBeanOperationInfoSupport opInfo = new OpenMBeanOperationInfoSupport(
    "setThreshold", "Update alert threshold",
    new OpenMBeanParameterInfoSupport[]{param},
    SimpleType.VOID, MBeanOperationInfo.ACTION
);

// Build OpenMBeanInfoSupport (implements MBeanInfo)
OpenMBeanInfoSupport info = new OpenMBeanInfoSupport(
    this.getClass().getName(),
    "Open MBean example",
    new OpenMBeanAttributeInfoSupport[]{attrInfo},
    new OpenMBeanConstructorInfoSupport[]{},
    new OpenMBeanOperationInfoSupport[]{opInfo},
    new MBeanNotificationInfo[]{}
);
```

---

## Model MBeans

### Purpose

Model MBeans adapt *existing* classes to JMX without modifying them. The `RequiredModelMBean` implementation (provided by every JMX agent) uses a `ModelMBeanInfo` descriptor to map MBean attribute/operation names to fields and methods of a target object.

This is the pattern for instrumenting third-party or legacy code.

### Key Classes

```
ModelMBean (interface)          — extends DynamicMBean + PersistentMBean + ModelMBeanNotificationBroadcaster
RequiredModelMBean (class)      — provided by the JMX RI; use this
ModelMBeanInfo (interface)
ModelMBeanInfoSupport (class)   — build the descriptor

ModelMBeanAttributeInfo         — attribute + Descriptor
ModelMBeanOperationInfo         — operation + Descriptor
ModelMBeanConstructorInfo       — constructor + Descriptor
ModelMBeanNotificationInfo      — notification + Descriptor

Descriptor (interface)
DescriptorSupport (class)       — key/value metadata map
```

### Descriptor Fields

Descriptors drive `RequiredModelMBean`'s reflection behavior:

| Field | Applies to | Meaning |
|-------|-----------|---------|
| `name` | all | Name of attribute/operation |
| `descriptorType` | all | `"attribute"` or `"operation"` or `"mbean"` |
| `getMethod` | attribute | Method name to call for getter |
| `setMethod` | attribute | Method name to call for setter |
| `value` | attribute | Cached value (used when no `getMethod`) |
| `default` | attribute | Default value |
| `persistPolicy` | attribute | `"Never"`, `"OnUpdate"`, `"OnTimer"`, `"Always"` |
| `currencyTimeLimit` | attribute | Seconds before cached value is stale (-1=always fresh, 0=always stale) |
| `role` | operation | `"getter"`, `"setter"`, `"operation"` |
| `targetObject` | mbean | The managed resource object |
| `targetType` | mbean | `"objectReference"` |

### Wrapping an Existing Class

```java
// Existing class — no modification needed
public class ConnectionPool {
    private int maxSize = 10;
    private int activeCount = 0;

    public int getMaxSize() { return maxSize; }
    public void setMaxSize(int maxSize) { this.maxSize = maxSize; }
    public int getActiveCount() { return activeCount; }
    public void resetPool() { activeCount = 0; }
}
```

```java
// Build ModelMBeanInfo to wrap ConnectionPool
private ModelMBeanInfo buildModelMBeanInfo(ConnectionPool pool) throws Exception {

    // Attribute: MaxSize — backed by getter/setter
    Descriptor maxSizeDesc = new DescriptorSupport(new String[]{
        "name=MaxSize", "descriptorType=attribute",
        "getMethod=getMaxSize", "setMethod=setMaxSize",
        "currencyTimeLimit=0"  // always fresh
    });
    ModelMBeanAttributeInfo maxSizeAttr = new ModelMBeanAttributeInfo(
        "MaxSize", "int", "Maximum pool size", true, true, false, maxSizeDesc);

    // Attribute: ActiveCount — read-only via getter
    Descriptor activeDesc = new DescriptorSupport(new String[]{
        "name=ActiveCount", "descriptorType=attribute",
        "getMethod=getActiveCount", "currencyTimeLimit=5"  // cache 5s
    });
    ModelMBeanAttributeInfo activeAttr = new ModelMBeanAttributeInfo(
        "ActiveCount", "int", "Active connections", true, false, false, activeDesc);

    // Operation: resetPool
    Descriptor resetDesc = new DescriptorSupport(new String[]{
        "name=resetPool", "descriptorType=operation", "role=operation"
    });
    ModelMBeanOperationInfo resetOp = new ModelMBeanOperationInfo(
        "resetPool", "Reset the connection pool",
        new MBeanParameterInfo[]{}, "void",
        MBeanOperationInfo.ACTION, resetDesc);

    // Support operations needed for attribute getter/setter dispatch
    ModelMBeanOperationInfo getMaxOp = new ModelMBeanOperationInfo(
        "getMaxSize", "Getter for MaxSize", new MBeanParameterInfo[]{},
        "int", MBeanOperationInfo.INFO,
        new DescriptorSupport(new String[]{
            "name=getMaxSize", "descriptorType=operation", "role=getter"}));

    ModelMBeanOperationInfo setMaxOp = new ModelMBeanOperationInfo(
        "setMaxSize", "Setter for MaxSize",
        new MBeanParameterInfo[]{
            new MBeanParameterInfo("maxSize", "int", "New max")},
        "void", MBeanOperationInfo.ACTION,
        new DescriptorSupport(new String[]{
            "name=setMaxSize", "descriptorType=operation", "role=setter"}));

    ModelMBeanOperationInfo getActiveOp = new ModelMBeanOperationInfo(
        "getActiveCount", "Getter for ActiveCount", new MBeanParameterInfo[]{},
        "int", MBeanOperationInfo.INFO,
        new DescriptorSupport(new String[]{
            "name=getActiveCount", "descriptorType=operation", "role=getter"}));

    return new ModelMBeanInfoSupport(
        ConnectionPool.class.getName(),
        "Connection pool management",
        new ModelMBeanAttributeInfo[]{maxSizeAttr, activeAttr},
        new ModelMBeanConstructorInfo[]{},
        new ModelMBeanOperationInfo[]{resetOp, getMaxOp, setMaxOp, getActiveOp},
        new ModelMBeanNotificationInfo[]{}
    );
}
```

```java
// Register the Model MBean
ConnectionPool pool = new ConnectionPool();
RequiredModelMBean modelMBean = new RequiredModelMBean();
modelMBean.setModelMBeanInfo(buildModelMBeanInfo(pool));
modelMBean.setManagedResource(pool, "objectReference");

MBeanServer mbs = ManagementFactory.getPlatformMBeanServer();
ObjectName name = new ObjectName("com.example:type=ConnectionPool");
mbs.registerMBean(modelMBean, name);
```

### Persistence with Model MBeans

Model MBeans support attribute persistence via the `persistPolicy` descriptor field.

```java
// Save/restore attribute values
Descriptor mbeanDesc = new DescriptorSupport(new String[]{
    "name=ConnectionPool", "descriptorType=mbean",
    "persistPolicy=OnUpdate",
    "persistLocation=/var/jmx",
    "persistName=pool-state"
});
```

Persistence is agent-implementation-specific; `RequiredModelMBean` in the JMX RI writes serialized XML.

### Open vs Model MBean — Decision Guide

| Criterion | Open MBean | Model MBean |
|-----------|-----------|------------|
| Interoperability across class loaders | Primary goal | Not the goal |
| Adapting existing classes | Awkward | Primary use case |
| Attribute value caching | Manual | Built into `RequiredModelMBean` |
| Persistence | No | Yes |
| Complexity | Medium | High |
| Required setup | Open Type descriptors | Full `ModelMBeanInfo` with Descriptor fields |
