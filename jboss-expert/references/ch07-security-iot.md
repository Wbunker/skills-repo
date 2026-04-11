# Ch 7 — Security (WildFly Elytron) and IoT Messaging

> **Book context:** Covered "Delivers Information Safely" (security via PicketBox/KeyCloak) and "Connects IoT" (AMQ/MQTT). Major change: **PicketBox is fully replaced by WildFly Elytron** in WildFly 26+. The security vault is replaced by Elytron credential stores.

## WildFly Elytron

Elytron is WildFly's security framework, replacing the legacy PicketBox/JAAS subsystem.

```
┌──────────────────────────────────────────────────────────────┐
│                    ELYTRON SECURITY MODEL                    │
│                                                              │
│  Authentication Mechanisms (HTTP/SASL):                      │
│  BASIC · FORM · DIGEST · CLIENT_CERT · BEARER_TOKEN · OIDC   │
│                      │                                       │
│                      ▼                                       │
│  ┌──────────────────────────────────────┐                   │
│  │         Security Domain              │                   │
│  │  realms → identity → role mapping    │                   │
│  └──────────────────────────────────────┘                   │
│                      │                                       │
│  Security Realms:                                            │
│  properties-realm · jdbc-realm · ldap-realm · filesystem-realm│
│  token-realm (JWT) · aggregate-realm · caching-realm        │
│                                                              │
│  Credential Store (replaces Security Vault):                 │
│  Encrypted key-value store for passwords/secrets            │
└──────────────────────────────────────────────────────────────┘
```

## Elytron Configuration

### Security Domain with Properties Realm

```xml
<subsystem xmlns="urn:wildfly:elytron:18.0">
  <!-- Properties file realm (dev/test only) -->
  <security-realms>
    <properties-realm name="AppRealm">
      <users-properties path="users.properties"
                        relative-to="jboss.server.config.dir"
                        plain-text="false"
                        digest-realm-name="AppRealm"/>
      <groups-properties path="roles.properties"
                         relative-to="jboss.server.config.dir"/>
    </properties-realm>
  </security-realms>

  <!-- Role decoder: groups → roles -->
  <mappers>
    <simple-role-decoder name="groups-to-roles" attribute="groups"/>
  </mappers>

  <!-- Security domain -->
  <security-domains>
    <security-domain name="AppDomain"
                     default-realm="AppRealm"
                     permission-mapper="default-permission-mapper">
      <realm name="AppRealm" role-decoder="groups-to-roles"/>
    </security-domain>
  </security-domains>

  <!-- HTTP authentication factory -->
  <http>
    <http-authentication-factory name="application-http-authentication"
                                  security-domain="AppDomain"
                                  http-server-mechanism-factory="global">
      <mechanism-configuration>
        <mechanism mechanism-name="BASIC">
          <mechanism-realm realm-name="AppRealm"/>
        </mechanism>
        <mechanism mechanism-name="FORM"/>
      </mechanism-configuration>
    </http-authentication-factory>
  </http>
</subsystem>
```

### JDBC Realm

```xml
<jdbc-realm name="JdbcRealm">
  <principal-query sql="SELECT password FROM users WHERE username=?"
                   data-source="MyDS">
    <bcrypt-mapper password-index="1" salt-index="2" iteration-count-index="3"/>
  </principal-query>
  <principal-query sql="SELECT role FROM user_roles WHERE username=?"
                   data-source="MyDS">
    <attribute-mapping>
      <attribute to="groups" index="1"/>
    </attribute-mapping>
  </principal-query>
</jdbc-realm>
```

### LDAP Realm

```xml
<ldap-realm name="LdapRealm" dir-context="LdapDirContext"
            direct-verification="true">
  <identity-mapping rdn-identifier="uid"
                    search-base-dn="ou=users,dc=example,dc=com">
    <attribute-mapping>
      <attribute from="cn" to="cn"/>
      <filter-base-dn="ou=groups,dc=example,dc=com"
                from="cn" to="groups"
                filter="(member=uid={0},ou=users,dc=example,dc=com)"/>
    </attribute-mapping>
  </identity-mapping>
</ldap-realm>
```

## Credential Store (Replaces Security Vault)

The credential store is an encrypted keystore for secrets (passwords, tokens).

```bash
# Create credential store
$JBOSS_HOME/bin/elytron-tool.sh credential-store \
  --create \
  --location /opt/wildfly/credential-store.cs \
  --password "masterPassword" \
  --add "ds.password" \
  --secret "dbPassword123"

# Add entry via CLI
/subsystem=elytron/credential-store=MyStore:add(
  location="credential-store.cs",
  relative-to="jboss.server.config.dir",
  credential-reference={clear-text="masterPassword"},
  create=true
)

/subsystem=elytron/credential-store=MyStore:add-alias(
  alias="ds.password",
  secret-value="dbPassword123"
)
```

Reference in datasource:
```xml
<data-source name="MyDS" jndi-name="...">
  ...
  <credential-reference store="MyStore" alias="ds.password"/>
</data-source>
```

## SSL/TLS Configuration

```xml
<subsystem xmlns="urn:wildfly:elytron:18.0">
  <!-- Key store from PKCS12 file -->
  <key-stores>
    <key-store name="applicationKS">
      <credential-reference clear-text="${env.KEYSTORE_PASS}"/>
      <implementation type="PKCS12"/>
      <file path="application.keystore"
            relative-to="jboss.server.config.dir"/>
    </key-store>
  </key-stores>

  <!-- Key manager -->
  <key-managers>
    <key-manager name="applicationKM" algorithm="SunX509"
                 key-store="applicationKS">
      <credential-reference clear-text="${env.KEY_PASS}"/>
    </key-manager>
  </key-managers>

  <!-- SSL context -->
  <server-ssl-contexts>
    <server-ssl-context name="applicationSSC"
                        key-manager="applicationKM"
                        protocols="TLSv1.3 TLSv1.2"
                        cipher-suite-filter="RECOMMENDED"/>
  </server-ssl-contexts>
</subsystem>
```

Generate self-signed cert:
```bash
keytool -genkeypair \
  -alias application \
  -keyalg RSA -keysize 2048 \
  -validity 365 \
  -keystore application.keystore \
  -storepass password \
  -dname "CN=localhost,O=MyOrg,C=US"
```

## Application Security Annotations

```java
@Stateless
public class OrderService {

    // Method-level security
    @RolesAllowed({"ADMIN", "MANAGER"})
    public void cancelOrder(Long id) { ... }

    @PermitAll
    public List<Order> findPublicOrders() { ... }

    @DenyAll
    public void internalMethod() { ... }

    // Programmatic security check
    @Resource
    private SessionContext ctx;

    public void sensitiveOp() {
        if (!ctx.isCallerInRole("ADMIN")) {
            throw new SecurityException("ADMIN role required");
        }
        // ...
    }
}
```

Activate on deployment:
```xml
<!-- jboss-web.xml -->
<security-domain>AppDomain</security-domain>
```

## Keycloak / OIDC Integration

WildFly supports OIDC natively via the `elytron-oidc-client` subsystem:

```xml
<subsystem xmlns="urn:wildfly:elytron-oidc-client:2.0">
  <provider name="keycloak">
    <provider-url>https://keycloak.example.com/realms/myrealm</provider-url>
  </provider>
  <secure-deployment name="myapp.war">
    <provider>keycloak</provider>
    <client-id>myapp</client-id>
    <public-client>false</public-client>
    <credential name="secret" value="${env.KEYCLOAK_CLIENT_SECRET}"/>
  </secure-deployment>
</subsystem>
```

Or configure per-deployment in `oidc.json` placed in `WEB-INF/`:
```json
{
  "client-id": "myapp",
  "provider-url": "https://keycloak.example.com/realms/myrealm",
  "public-client": false,
  "credentials": { "secret": "${env.KEYCLOAK_SECRET}" },
  "ssl-required": "external"
}
```

## Migration: PicketBox → Elytron

| PicketBox (legacy) | Elytron (current) |
|-------------------|------------------|
| `security` subsystem | `elytron` subsystem |
| Security domain (in `security`) | Security domain (in `elytron`) |
| Security vault | Credential store |
| `LoginModule` | `SecurityRealm` |
| `<security-domain>` in jboss-web.xml | Same, but points to Elytron domain |
| `@SecurityDomain` annotation | `@RunAsPrincipal`, Elytron virtual security domain |

Migration tool:
```bash
$JBOSS_HOME/bin/elytron-tool.sh vault \
  --keystore old-vault.keystore \
  --keystore-password vaultPassword \
  --enc-dir vault \
  --iteration 50 \
  --salt 12345678 \
  --alias vault \
  --target-credential-store new-credential-store.cs \
  --target-password newStorePassword
```

## IoT — MQTT Messaging

### WildFly + ActiveMQ Artemis MQTT

ActiveMQ Artemis supports MQTT natively (enable the MQTT acceptor):

```xml
<!-- In messaging-activemq subsystem -->
<remote-acceptor name="mqtt-acceptor" socket-binding="mqtt">
  <param name="protocols" value="MQTT"/>
</remote-acceptor>

<!-- In socket-binding-group -->
<socket-binding name="mqtt" port="1883"/>
```

### Eclipse Paho MQTT Client

```java
// Maven: org.eclipse.paho:org.eclipse.paho.client.mqttv3:1.2.5

MqttClient client = new MqttClient(
    "tcp://broker:1883",
    MqttClient.generateClientId(),
    new MemoryPersistence()
);

MqttConnectOptions options = new MqttConnectOptions();
options.setCleanSession(true);
options.setAutomaticReconnect(true);
options.setUserName("user");
options.setPassword("password".toCharArray());
options.setConnectionTimeout(30);
options.setKeepAliveInterval(60);

client.connect(options);

// Subscribe
client.subscribe("sensors/temperature/#", 1, (topic, msg) -> {
    String payload = new String(msg.getPayload());
    System.out.println("Received from " + topic + ": " + payload);
});

// Publish
MqttMessage message = new MqttMessage("25.4".getBytes());
message.setQos(1);        // At least once
message.setRetained(true);
client.publish("sensors/temperature/device-1", message);
```

### MQTT QoS Levels

| QoS | Name | Guarantee | Use Case |
|-----|------|-----------|---------|
| 0 | At most once | Fire and forget — may lose | Non-critical telemetry |
| 1 | At least once | Guaranteed, may duplicate | Most IoT sensor data |
| 2 | Exactly once | Guaranteed, no duplicates | Billing, commands |

### IoT Pattern — Device Shadow / Last Known Value

```java
// Retain last known sensor reading (retained=true)
// → new subscribers immediately receive current state
message.setRetained(true);
client.publish("devices/sensor-1/state", message);

// Last will: published if client disconnects unexpectedly
options.setWill(
    "devices/sensor-1/status",
    "offline".getBytes(),
    1,    // QoS
    true  // retained
);
```

## Security Decision Tree

```
What are you securing?
├── Web application (HTTP) → Undertow HTTP authentication factory
│   ├── Username/password → BASIC or FORM mechanism
│   ├── Single Sign-On → OIDC (Keycloak) via elytron-oidc-client
│   └── Client certificate → CLIENT_CERT mechanism
├── EJBs → @RolesAllowed + security domain reference
├── REST API → BEARER_TOKEN mechanism (JWT) or OIDC
├── Management console / CLI → Management security realm (separate from app)
└── Datasource passwords → Credential store (never plain-text in XML)

Migration from PicketBox?
├── Security domains → Re-create as Elytron security domains
├── Security vault → Migrate to Elytron credential store (use elytron-tool.sh)
└── LoginModules → Replace with Elytron security realms (jdbc-realm, ldap-realm)
```
