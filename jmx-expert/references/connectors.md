# Remote Connectors (JSR 160)

From Chapters 9–10 of *Java Management Extensions* by J. Steven Perry.

## Overview

JSR 160 (JMX Remote API) defines a transport-independent protocol for remotely accessing a JMX agent. The two standard transports are:

- **RMI connector** — uses Java RMI; the default and most widely deployed
- **JMXMP connector** — uses a custom TCP protocol (optional in the spec; not in standard JDK after Java 9)

The architecture:
```
Client JVM                         Server JVM
  JMXConnector ─── transport ───► JMXConnectorServer
  MBeanServerConnection                MBeanServer
```

## JMXServiceURL

The service URL identifies the connector endpoint:

```
service:jmx:<protocol>://<host>:<port>/<path>
```

Common forms:

```
# RMI with JNDI registry
service:jmx:rmi:///jndi/rmi://localhost:1099/jmxrmi

# RMI without JNDI (direct stub)
service:jmx:rmi://localhost:9000/stub/<base64-encoded-stub>

# JMXMP
service:jmx:jmxmp://localhost:5555
```

## Server-Side Setup

### RMI Connector with JNDI Registry

```java
// Start an RMI registry on port 1099
LocateRegistry.createRegistry(1099);

MBeanServer mbs = ManagementFactory.getPlatformMBeanServer();
JMXServiceURL url = new JMXServiceURL(
    "service:jmx:rmi:///jndi/rmi://localhost:1099/jmxrmi");

JMXConnectorServer cs =
    JMXConnectorServerFactory.newJMXConnectorServer(url, null, mbs);
cs.start();

// cs.getAddress() returns the actual bound URL
System.out.println("Connector available at: " + cs.getAddress());

// Shutdown
// cs.stop();
```

### Via System Properties (JVM launch flags)

```bash
java \
  -Dcom.sun.management.jmxremote \
  -Dcom.sun.management.jmxremote.port=9000 \
  -Dcom.sun.management.jmxremote.authenticate=false \
  -Dcom.sun.management.jmxremote.ssl=false \
  -jar myapp.jar
```

The platform connector is then reachable at `service:jmx:rmi:///jndi/rmi://localhost:9000/jmxrmi`.

## Client-Side Connection

```java
JMXServiceURL url = new JMXServiceURL(
    "service:jmx:rmi:///jndi/rmi://remotehost:1099/jmxrmi");

// No auth
JMXConnector connector = JMXConnectorFactory.connect(url);

// With credentials
Map<String, Object> env = new HashMap<>();
env.put(JMXConnector.CREDENTIALS, new String[]{"user", "password"});
JMXConnector connector = JMXConnectorFactory.connect(url, env);

// Get MBeanServerConnection
MBeanServerConnection mbsc = connector.getMBeanServerConnection();

// Use it like a local MBeanServer
Object val = mbsc.getAttribute(name, "HeapMemoryUsage");
mbsc.invoke(name, "gc", new Object[]{}, new String[]{});

// Close when done
connector.close();
```

### Try-with-Resources Pattern

```java
try (JMXConnector connector = JMXConnectorFactory.connect(url, env)) {
    MBeanServerConnection mbsc = connector.getMBeanServerConnection();
    // ... use mbsc ...
}  // connector.close() called automatically
```

## Remote Typed Proxies

```java
MBeanServerConnection mbsc = connector.getMBeanServerConnection();
ObjectName memoryName = new ObjectName(ManagementFactory.MEMORY_MXBEAN_NAME);

MemoryMXBean memProxy = ManagementFactory.newPlatformMXBeanProxy(
    mbsc, ManagementFactory.MEMORY_MXBEAN_NAME, MemoryMXBean.class);

MemoryUsage heap = memProxy.getHeapMemoryUsage();

// Or for Standard MBeans
HelloMBean helloProxy = JMX.newMBeanProxy(mbsc, helloName, HelloMBean.class);
helloProxy.printHello("Remote");
```

## Remote Notifications

Notifications work transparently over remote connectors. The connector handles buffering, fetching, and dispatch.

```java
MBeanServerConnection mbsc = connector.getMBeanServerConnection();

mbsc.addNotificationListener(cacheName,
    (notif, handback) -> System.out.println("Remote notif: " + notif.getType()),
    null, null);
```

### Fetch Period Tuning

The RMI connector client polls the server for buffered notifications. Default period is 1000ms. Tune via:

```java
Map<String, Object> env = new HashMap<>();
env.put("jmx.remote.x.client.connection.check.period", "2000");
env.put("jmx.remote.x.notification.fetch.timeout", "5000");
JMXConnector connector = JMXConnectorFactory.connect(url, env);
```

## Connection Event Listeners

```java
connector.addConnectionNotificationListener(
    (notification, handback) -> {
        JMXConnectionNotification n = (JMXConnectionNotification) notification;
        if (JMXConnectionNotification.CLOSED.equals(n.getType())) {
            System.out.println("Connection closed: " + n.getConnectionId());
        } else if (JMXConnectionNotification.FAILED.equals(n.getType())) {
            System.out.println("Connection failed — attempt reconnect");
        }
    },
    null, null
);
```

`JMXConnectionNotification` types:
- `OPENED` — connection established
- `CLOSED` — connection closed gracefully
- `FAILED` — connection lost
- `NOTIFS_LOST` — notification buffer overflowed on server

## Environment Map Keys

| Key | Meaning |
|-----|---------|
| `JMXConnector.CREDENTIALS` | `String[]{"user", "pass"}` for password auth |
| `"jmx.remote.x.client.connection.check.period"` | Heartbeat interval ms (default 60000) |
| `"jmx.remote.x.notification.fetch.timeout"` | Fetch call timeout ms |
| `"jmx.remote.x.notification.buffer.size"` | Server-side buffer capacity (notifications) |
| `"jmx.remote.rmi.client.socket.factory"` | Custom `RMIClientSocketFactory` for SSL |
| `"jmx.remote.rmi.server.socket.factory"` | Custom `RMIServerSocketFactory` for SSL |

## Adaptor vs Connector Distinction

- **Connector** — protocol-level bridge; the remote end is still a JMX client using `MBeanServerConnection`
- **Adaptor** — protocol translation to a non-JMX protocol (e.g., HTTP/HTML, SNMP)

The JMX 1.x RI included an HTML adaptor (`HtmlAdaptorServer`) that rendered MBeans as web pages. It is not part of the JMX standard. JConsole and Java Mission Control use the RMI connector.

## Common Setup Issues

**`java.rmi.ConnectException`** — server-side RMI registry not reachable, wrong port, or firewall blocking. Verify `LocateRegistry.createRegistry(port)` was called.

**`java.rmi.NoSuchObjectException`** — JMX connector server not started, or stub expired (JVM restarted). Re-export the stub.

**Two RMI ports** — the RMI connector opens TWO ports: the registry port and a random data port. For firewalled environments, fix both:

```java
// Fix data port to 9001, registry port to 9000
RMIClientSocketFactory csf = RMISocketFactory.getDefaultSocketFactory();
RMIServerSocketFactory ssf = RMISocketFactory.getDefaultSocketFactory();
RMIJRMPServerImpl server = new RMIJRMPServerImpl(9001, csf, ssf, null);
// ... bind to JMXConnectorServer
```

Or use the simpler system-property approach with `-Dcom.sun.management.jmxremote.rmi.port=9001`.

**Class not found on deserialization** — attribute/operation return types must be on the client's classpath. Use Open Types (`CompositeData`, `TabularData`) for cross-classloader compatibility.
