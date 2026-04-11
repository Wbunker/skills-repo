# Ch 1 — Introduction to the JBoss Ecosystem

## The JBoss Portfolio

JBoss is Red Hat's middleware brand. The community server is **WildFly**; the enterprise product is **JBoss EAP**. All other JBoss products are separate middleware components.

```
Community Project        →  Enterprise Product
─────────────────────────────────────────────────
WildFly                  →  JBoss EAP
Infinispan               →  Red Hat Data Grid
Apache Camel             →  Red Hat Fuse / Camel K
Drools                   →  Red Hat Decision Services
jBPM                     →  Red Hat Process Automation Manager (PAM)
ActiveMQ Artemis         →  Red Hat AMQ Broker
Strimzi (Kafka)          →  Red Hat AMQ Streams
Keycloak                 →  Red Hat SSO / Red Hat Build of Keycloak
```

## WildFly Architecture

WildFly is a modular, subsystem-based application server built on JBoss Modules (classloading) and the **Domain Management Model** (DMR).

### Core Subsystems

| Subsystem | Purpose |
|-----------|---------|
| `undertow` | HTTP/HTTPS server, servlet container |
| `ejb3` | EJB 3.2 container |
| `weld` | CDI 4.0 implementation |
| `jpa` | JPA/Hibernate integration |
| `datasources` | JDBC datasource management |
| `messaging-activemq` | AMQ Broker / JMS |
| `elytron` | Security (auth, SSL, credential stores) |
| `infinispan` | Distributed cache |
| `jaxrs` | RESTEasy / JAX-RS |
| `webservices` | CXF / JAX-WS |
| `batch-jberet` | Batch Processing (Jakarta Batch) |
| `microprofile-*` | MicroProfile subsystems |
| `transactions` | JTA transaction manager (Narayana) |

### Configuration Files

| Mode | Primary Config | Use Case |
|------|---------------|----------|
| Standalone | `standalone/configuration/standalone.xml` | Single-server dev/test |
| Standalone + HA | `standalone-ha.xml` | Single server with clustering |
| Standalone Full | `standalone-full.xml` | All subsystems including messaging |
| Domain | `domain/configuration/domain.xml` + `host.xml` | Multi-server managed fleet |

**Modern recommendation:** Use standalone mode with Bootable JAR for cloud; use domain mode for traditional on-premises managed fleets.

## WildFly 39 Key Features (Jan 2026)

- TLS configuration for TCP-based transport in JGroups (replacing ASYM_ENCRYPT with AUTH)
- Idle-time-based eviction for distributable `HttpSession`
- RESTEasy updates with new `jaxrs` subsystem attributes
- Enhanced Galleon provisioning with preview feature packs
- Direct deployment artifacts to Maven Central

## Galleon — Provisioning System

Galleon lets you provision a customized WildFly with only the layers your application needs:

```xml
<!-- pom.xml snippet for Bootable JAR with Galleon layers -->
<plugin>
  <groupId>org.wildfly.plugins</groupId>
  <artifactId>wildfly-maven-plugin</artifactId>
  <version>5.1.0.Final</version>
  <configuration>
    <feature-packs>
      <feature-pack>
        <location>wildfly@maven(org.jboss.universe:community-universe):current</location>
      </feature-pack>
    </feature-packs>
    <layers>
      <layer>jaxrs-server</layer>
      <layer>microprofile-platform</layer>
    </layers>
    <bootable-jar>true</bootable-jar>
  </configuration>
</plugin>
```

Common Galleon layers: `core-server`, `web-server`, `jaxrs-server`, `ejb`, `jpa`, `datasources-web-server`, `microprofile-platform`, `cloud-server`

## WildFly CLI

The CLI (`jboss-cli.sh` / `jboss-cli.bat`) is the primary management interface:

```bash
# Connect
$JBOSS_HOME/bin/jboss-cli.sh --connect

# Read subsystem attribute
/subsystem=undertow:read-resource

# Deploy application
deploy /path/to/app.war

# Add datasource
/subsystem=datasources/data-source=MyDS:add(
  jndi-name="java:jboss/datasources/MyDS",
  driver-name="postgresql",
  connection-url="jdbc:postgresql://localhost/mydb",
  user-name="user", password="pass"
)

# Reload server
:reload

# Batch operations
batch
  /subsystem=datasources/data-source=MyDS:add(...)
  /subsystem=datasources/data-source=MyDS:enable
run-batch
```

## HAL Management Console

Browser-based administration at `http://localhost:9990`. Provides:
- Server status and runtime metrics
- Deployment management (upload/undeploy)
- Subsystem configuration (datasources, messaging, security)
- Log viewer
- Patching

## WildFly Maven Plugin

```xml
<plugin>
  <groupId>org.wildfly.plugins</groupId>
  <artifactId>wildfly-maven-plugin</artifactId>
  <version>5.1.0.Final</version>
</plugin>
```

Key goals:
- `wildfly:deploy` / `wildfly:undeploy` / `wildfly:redeploy`
- `wildfly:run` — start server and deploy
- `wildfly:package` — build Bootable JAR
- `wildfly:execute-commands` — run CLI scripts during build
- `wildfly:add-resource` — add datasources, other resources

## JBoss Modules (Classloading)

WildFly uses a modular classloading system. Each deployment gets its own classloader. Module descriptors live in `$JBOSS_HOME/modules/`.

Add a custom module:
```
$JBOSS_HOME/modules/com/example/mylib/main/
  mylib.jar
  module.xml
```

```xml
<!-- module.xml -->
<module name="com.example.mylib" xmlns="urn:jboss:module:1.9">
  <resources>
    <resource-root path="mylib.jar"/>
  </resources>
  <dependencies>
    <module name="javax.api"/>
  </dependencies>
</module>
```

Reference from deployment: `MANIFEST.MF` `Dependencies: com.example.mylib`

## Standards Support Matrix

| Standard | WildFly 39 |
|----------|-----------|
| Jakarta EE 10 (Full Platform) | Yes |
| Jakarta EE 10 (Web Profile) | Yes |
| Jakarta EE 11 (preview) | WildFly Preview only |
| MicroProfile 7.1 | Yes |
| Java SE 17 | Yes |
| Java SE 21 | Yes (recommended) |
