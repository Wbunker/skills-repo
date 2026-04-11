# JMX Security

From Chapter 11 of *Java Management Extensions* by J. Steven Perry.

## Security Model Overview

JMX remote security has two layers:

1. **Authentication** — verify identity (who is connecting)
2. **Authorization** — enforce access control (what they can do)

For in-process access (same JVM), no security configuration is needed. Security applies to remote connector connections only.

## Password-Based Authentication

### Server-side: password file

Create a Java properties file (`jmxremote.password`):

```properties
# username = password  (plain text — protect with chmod 600)
monitorRole  monitorpassword
controlRole  controlpassword
```

Set permissions on Unix:
```bash
chmod 600 /etc/jmx/jmxremote.password
```

JVM launch flags:
```bash
java \
  -Dcom.sun.management.jmxremote.port=9000 \
  -Dcom.sun.management.jmxremote.password.file=/etc/jmx/jmxremote.password \
  -Dcom.sun.management.jmxremote.ssl=false \
  -jar myapp.jar
```

### Access control file

```properties
# username = readonly | readwrite
monitorRole  readonly
controlRole  readwrite
```

```bash
-Dcom.sun.management.jmxremote.access.file=/etc/jmx/jmxremote.access
```

### Client-side: passing credentials

```java
Map<String, Object> env = new HashMap<>();
env.put(JMXConnector.CREDENTIALS, new String[]{"controlRole", "controlpassword"});
JMXConnector connector = JMXConnectorFactory.connect(url, env);
```

## Programmatic Authentication

For non-file-based auth (LDAP, database, custom), implement `JMXAuthenticator`:

```java
public class LdapAuthenticator implements JMXAuthenticator {
    @Override
    public Subject authenticate(Object credentials) {
        if (!(credentials instanceof String[]))
            throw new SecurityException("Expected String[] credentials");
        String[] creds = (String[]) credentials;
        String username = creds[0];
        String password = creds[1];

        // Verify against LDAP / database / etc.
        if (!verify(username, password))
            throw new SecurityException("Authentication failed");

        // Return a Subject with principals
        Set<Principal> principals = Set.of(new JMXPrincipal(username));
        return new Subject(true, principals, Set.of(), Set.of());
    }
}

// Register with connector server
Map<String, Object> env = new HashMap<>();
env.put(JMXConnectorServer.AUTHENTICATOR, new LdapAuthenticator());
JMXConnectorServer cs = JMXConnectorServerFactory.newJMXConnectorServer(url, env, mbs);
```

## SSL/TLS Transport Security

### Server-side SSL

```java
// Build SSLContext or use system defaults
// Set JSSE system properties
System.setProperty("javax.net.ssl.keyStore", "/etc/jmx/keystore.jks");
System.setProperty("javax.net.ssl.keyStorePassword", "keystorepass");

// Use JVM launch flags
-Dcom.sun.management.jmxremote.ssl=true
-Dcom.sun.management.jmxremote.ssl.need.client.auth=true   // mutual TLS
-Djavax.net.ssl.keyStore=/etc/jmx/keystore.jks
-Djavax.net.ssl.keyStorePassword=keystorepass
-Djavax.net.ssl.trustStore=/etc/jmx/truststore.jks
-Djavax.net.ssl.trustStorePassword=truststorepass
```

### Programmatic SSL connector

```java
// Server side
SslRMIClientSocketFactory csf = new SslRMIClientSocketFactory();
SslRMIServerSocketFactory ssf = new SslRMIServerSocketFactory(
    null,               // cipher suites (null = default)
    null,               // protocols (null = default)
    true                // need client auth
);

Map<String, Object> env = new HashMap<>();
env.put(RMIConnectorServer.RMI_CLIENT_SOCKET_FACTORY_ATTRIBUTE, csf);
env.put(RMIConnectorServer.RMI_SERVER_SOCKET_FACTORY_ATTRIBUTE, ssf);

JMXConnectorServer cs = JMXConnectorServerFactory.newJMXConnectorServer(url, env, mbs);
cs.start();
```

```java
// Client side
System.setProperty("javax.net.ssl.trustStore", "/etc/jmx/truststore.jks");
System.setProperty("javax.net.ssl.trustStorePassword", "pass");

Map<String, Object> env = new HashMap<>();
env.put(JMXConnector.CREDENTIALS, new String[]{"user", "pass"});
// SslRMIClientSocketFactory is bundled in the stub — no extra config needed for RMI
JMXConnector connector = JMXConnectorFactory.connect(url, env);
```

## Java Security Manager Authorization (Legacy)

When a `SecurityManager` is installed, JMX enforces `MBeanPermission` checks. This applies to all MBean Server operations.

```
MBeanPermission("<className>#<memberName>[<objectName>]", "<action>")
```

Actions:
- `getAttribute`, `setAttribute` — attribute access
- `invoke` — operation invocation
- `registerMBean`, `unregisterMBean` — lifecycle
- `queryMBeans`, `queryNames` — discovery
- `addNotificationListener`, `removeNotificationListener` — subscriptions

### policy file example

```
grant principal javax.management.remote.JMXPrincipal "controlRole" {
    permission javax.management.MBeanPermission "*", "getAttribute, setAttribute, invoke";
    permission javax.management.MBeanPermission "*", "registerMBean, unregisterMBean";
    permission javax.management.MBeanPermission "*", "queryMBeans, queryNames";
    permission javax.management.MBeanPermission "*", "addNotificationListener";
};

grant principal javax.management.remote.JMXPrincipal "monitorRole" {
    permission javax.management.MBeanPermission "*", "getAttribute";
    permission javax.management.MBeanPermission "*", "queryMBeans, queryNames";
    permission javax.management.MBeanPermission "*", "addNotificationListener";
};
```

Note: The Java Security Manager was deprecated in Java 17 and removed in Java 24. In modern JVMs, rely on `JMXAuthenticator` + SSL rather than `SecurityManager`.

## Subject Delegation

A JMX client can invoke operations on behalf of a different `Subject`:

```java
Subject delegatee = new Subject(true,
    Set.of(new JMXPrincipal("auditor")), Set.of(), Set.of());

MBeanServerConnection delegatedMbsc =
    connector.getMBeanServerConnection(delegatee);
// Operations on delegatedMbsc are performed as "auditor"
```

The server must have a `SecurityManager` installed and the connector server must support subject delegation for this to be enforced.

## Security Checklist

- [ ] `jmxremote.password` has permissions `600` (owner-read-only)
- [ ] `jmxremote.access` restricts monitoring roles to `readonly`
- [ ] SSL enabled for any network-facing connector (avoid plain-text credentials)
- [ ] Client truststores contain only trusted server certificates
- [ ] Mutual TLS enabled when client identity must be verified at transport layer
- [ ] No plaintext passwords in JVM launch scripts visible via `ps aux` — use config files
- [ ] `JMXAuthenticator` logs authentication failures with rate limiting
