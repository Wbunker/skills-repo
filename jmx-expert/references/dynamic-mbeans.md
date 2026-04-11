# Dynamic MBeans

From Chapter 3 of *Java Management Extensions* by J. Steven Perry.

## What Is a Dynamic MBean?

A Dynamic MBean exposes its management interface at runtime via `MBeanInfo` rather than through a compile-time interface. This enables:

- Management interface determined by configuration files, databases, or annotations
- Wrapping legacy code where you cannot define a `XMBean` interface
- Variable attribute sets (e.g., one MBean per configuration key)

## The DynamicMBean Interface

```java
public interface DynamicMBean {
    // Metadata
    MBeanInfo getMBeanInfo();

    // Attribute access
    Object getAttribute(String attribute)
        throws AttributeNotFoundException, MBeanException, ReflectionException;

    void setAttribute(Attribute attribute)
        throws AttributeNotFoundException, InvalidAttributeValueException,
               MBeanException, ReflectionException;

    AttributeList getAttributes(String[] attributes);
    AttributeList setAttributes(AttributeList attributes);

    // Operation invocation
    Object invoke(String actionName, Object[] params, String[] signature)
        throws MBeanException, ReflectionException;
}
```

## Building MBeanInfo

`MBeanInfo` is the runtime descriptor. Construct it once (in constructor or lazily) and return it from `getMBeanInfo()`.

```java
private MBeanInfo buildMBeanInfo() {
    // Attributes
    MBeanAttributeInfo[] attributes = {
        new MBeanAttributeInfo(
            "State",            // name
            "java.lang.String", // type
            "Current state",    // description
            true,               // readable
            true,               // writable
            false               // isIs (boolean getter prefix)
        ),
        new MBeanAttributeInfo(
            "Count", "int", "Event count", true, false, false)
    };

    // Operations
    MBeanParameterInfo[] resetParams = {};
    MBeanOperationInfo[] operations = {
        new MBeanOperationInfo(
            "reset",                        // name
            "Reset the counter",            // description
            resetParams,                    // parameters
            "void",                         // return type
            MBeanOperationInfo.ACTION       // impact
        ),
        new MBeanOperationInfo(
            "compute",
            "Compute with multiplier",
            new MBeanParameterInfo[]{
                new MBeanParameterInfo("multiplier", "int", "Scale factor")
            },
            "int",
            MBeanOperationInfo.ACTION_INFO
        )
    };

    // Constructors (optional — document how the MBean is created)
    MBeanConstructorInfo[] constructors = {
        new MBeanConstructorInfo("Default constructor",
            this.getClass().getConstructors()[0])
    };

    // Notifications (empty if none)
    MBeanNotificationInfo[] notifications = {};

    return new MBeanInfo(
        this.getClass().getName(),   // className
        "A dynamic MBean example",   // description
        attributes,
        constructors,
        operations,
        notifications
    );
}
```

## Full Dynamic MBean Implementation

```java
public class DynamicHello implements DynamicMBean {
    private String state = "IDLE";
    private int count = 0;
    private final MBeanInfo mbeanInfo;

    public DynamicHello() {
        this.mbeanInfo = buildMBeanInfo();
    }

    @Override
    public MBeanInfo getMBeanInfo() { return mbeanInfo; }

    @Override
    public Object getAttribute(String attribute)
            throws AttributeNotFoundException {
        switch (attribute) {
            case "State": return state;
            case "Count": return count;
            default:
                throw new AttributeNotFoundException("No attribute: " + attribute);
        }
    }

    @Override
    public void setAttribute(Attribute attribute)
            throws AttributeNotFoundException, InvalidAttributeValueException {
        String name = attribute.getName();
        Object value = attribute.getValue();
        if ("State".equals(name)) {
            if (!(value instanceof String))
                throw new InvalidAttributeValueException("State must be String");
            state = (String) value;
        } else {
            throw new AttributeNotFoundException("No writable attribute: " + name);
        }
    }

    @Override
    public AttributeList getAttributes(String[] attributes) {
        AttributeList list = new AttributeList();
        for (String attr : attributes) {
            try {
                list.add(new Attribute(attr, getAttribute(attr)));
            } catch (AttributeNotFoundException e) { /* skip */ }
        }
        return list;
    }

    @Override
    public AttributeList setAttributes(AttributeList attributes) {
        AttributeList result = new AttributeList();
        for (Object obj : attributes) {
            Attribute attr = (Attribute) obj;
            try {
                setAttribute(attr);
                result.add(attr);
            } catch (Exception e) { /* skip failed sets */ }
        }
        return result;
    }

    @Override
    public Object invoke(String actionName, Object[] params, String[] signature)
            throws MBeanException, ReflectionException {
        if ("reset".equals(actionName)) {
            count = 0;
            state = "IDLE";
            return null;
        }
        if ("compute".equals(actionName)) {
            int multiplier = (Integer) params[0];
            return count * multiplier;
        }
        throw new ReflectionException(
            new NoSuchMethodException(actionName), "Unknown operation");
    }
}
```

## Registration (same as Standard MBean)

```java
MBeanServer mbs = ManagementFactory.getPlatformMBeanServer();
ObjectName name = new ObjectName("com.example:type=DynamicHello");
mbs.registerMBean(new DynamicHello(), name);
```

## MBeanInfo Caching Strategy

`getMBeanInfo()` may be called frequently by consoles. Cache the instance:

```java
// Build once, reuse — MBeanInfo is immutable
private final MBeanInfo mbeanInfo = buildMBeanInfo();
```

If the management interface can change at runtime (rare), rebuild and re-cache on change, but note that many JMX clients cache `MBeanInfo` themselves and won't see the update without reconnecting.

## DynamicMBean vs Standard MBean — Decision Guide

| Criterion | Standard MBean | Dynamic MBean |
|-----------|---------------|---------------|
| Compile-time safety | Yes | No |
| Interface defined at runtime | No | Yes |
| Attribute set varies per instance | No | Yes |
| Wrapping existing class | Awkward | Natural |
| JMX console usability | Excellent | Excellent |
| Code volume | Low | High |

## Common Errors

**`ReflectionException` wrapping `NoSuchMethodException`** — thrown from `invoke()` when an operation name is not recognized. Always include an `else` branch that throws this.

**`MBeanException` wrapping application exceptions** — wrap any checked exception thrown by your business logic: `throw new MBeanException(e, "description")`.

**Returning `null` from `getAttribute`** — valid, but some JMX consoles display it poorly. Prefer empty strings or zero values for "not set" semantics.
