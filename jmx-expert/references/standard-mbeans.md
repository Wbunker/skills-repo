# Standard MBeans

From Chapter 2 of *Java Management Extensions* by J. Steven Perry.

## What Is a Standard MBean?

A Standard MBean is the simplest MBean type. The JMX agent discovers its manageable interface by reflection at registration time. It requires:

1. A Java interface named `<ClassName>MBean`
2. A class that implements that interface

The naming convention is the contract — no XML, no descriptor files.

## Defining the MBean Interface

```java
// HelloMBean.java — the management interface
public interface HelloMBean {
    // Attribute: read-write
    String getName();
    void setName(String name);

    // Attribute: read-only
    int getCacheSize();

    // Operation
    void printHello();
    void printHello(String whoName);
}
```

Rules for the interface:
- Getter `getX()` / setter `setX(T)` pairs expose read-write attributes
- Getter only → read-only attribute
- Setter only → write-only attribute
- `isX()` is valid for `boolean` attributes
- Any other method → operation

## Implementing the MBean Class

```java
public class Hello implements HelloMBean {
    private String name = "World";
    private int cacheSize = 200;

    @Override public String getName() { return name; }
    @Override public void setName(String name) { this.name = name; }
    @Override public int getCacheSize() { return cacheSize; }

    @Override
    public void printHello() {
        System.out.println("Hello, " + name + "!");
    }

    @Override
    public void printHello(String whoName) {
        System.out.println("Hello, " + whoName + "!");
    }
}
```

## Registering with the MBean Server

```java
MBeanServer mbs = ManagementFactory.getPlatformMBeanServer();

// ObjectName format: domain:key=value[,key=value,...]
ObjectName name = new ObjectName("com.example:type=Hello");

Hello mbean = new Hello();
mbs.registerMBean(mbean, name);
```

## ObjectName Conventions

```
domain:type=ClassName
domain:type=ClassName,name=instance1
domain:type=ClassName,module=core,name=primary
```

- Domain is arbitrary but should be your package name or application name
- Keys `type` and `name` are conventional; you can add any key=value pairs
- ObjectName supports wildcards for queries: `com.example:type=Hello,*`

## Querying MBeans

```java
// Find all MBeans in domain
Set<ObjectName> names = mbs.queryNames(
    new ObjectName("com.example:*"), null);

// Read an attribute
Object value = mbs.getAttribute(name, "CacheSize");

// Write an attribute
mbs.setAttribute(name, new Attribute("Name", "JMX"));

// Invoke an operation
mbs.invoke(name, "printHello",
    new Object[]{"Perry"},
    new String[]{String.class.getName()});
```

## MBeanInfo Introspection

At registration, the MBean Server builds an `MBeanInfo` descriptor:

```java
MBeanInfo info = mbs.getMBeanInfo(name);

// Attributes
for (MBeanAttributeInfo attr : info.getAttributes()) {
    System.out.println(attr.getName() + " readable=" + attr.isReadable()
        + " writable=" + attr.isWritable());
}

// Operations
for (MBeanOperationInfo op : info.getOperations()) {
    System.out.println(op.getName() + " impact=" + op.getImpact());
}
```

`MBeanOperationInfo.getImpact()` values:
- `ACTION` (1) — changes state, no return value
- `INFO` (0) — read-only, returns data
- `ACTION_INFO` (2) — changes state and returns data
- `UNKNOWN` (3) — unspecified

## Compliance Checklist

- [ ] Interface named exactly `<ClassName>MBean`
- [ ] Class is `public` and has a no-arg constructor (or constructor used at registration)
- [ ] Attribute types are JMX-compatible (primitives, String, Number, arrays, `CompositeData`, `TabularData`)
- [ ] Getters and setters have matching types
- [ ] Operations do not overload by parameter count with differing types (causes ambiguity in some clients)

## Common Pitfalls

**Wrong interface name** — `HelloManager` implementing `HelloMBean` fails; the name must match the concrete class, not a parent.

**Non-serializable attribute types** — When used over remote connectors, attribute and operation parameter types must be serializable by both sides. Prefer standard Java types.

**Thread safety** — The MBean Server can call your MBean from multiple threads. Use `synchronized`, `volatile`, or `java.util.concurrent` types on shared state.
