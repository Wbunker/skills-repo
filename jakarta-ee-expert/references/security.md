# Security
*Chapters 12–14, 31–33 — Form Auth, Client Certs, REST Security, JMX Security, JWT, Enterprise Security API*

## Jakarta Security 3.0 Overview

Jakarta Security 3.0 provides a portable, CDI-based security API that abstracts authentication mechanisms and identity stores.

**Core components:**
- `HttpAuthenticationMechanism` — how authentication is performed (form, basic, custom)
- `IdentityStore` — where credentials are verified (LDAP, DB, custom)
- `SecurityContext` — programmatic access to authentication info
- Annotations for declarative auth mechanism configuration

---

## Chapter 12: Form-Based Authentication

### Declarative Form Auth (`@FormAuthenticationMechanismDefinition`)
```java
@ApplicationScoped
@FormAuthenticationMechanismDefinition(
    loginToContinue = @LoginToContinue(
        loginPage        = "/login.xhtml",
        errorPage        = "/login-error.xhtml",
        useForwardToLogin = false   // redirect vs forward
    )
)
public class ApplicationConfig {}
```

### Database Identity Store
```java
@ApplicationScoped
@DatabaseIdentityStoreDefinition(
    dataSourceLookup = "java:comp/DefaultDataSource",
    callerQuery      = "SELECT password FROM users WHERE email = ?",
    groupsQuery      = "SELECT role FROM user_roles WHERE email = ?",
    hashAlgorithm    = Pbkdf2PasswordHash.class,
    hashAlgorithmParameters = {
        "Pbkdf2PasswordHash.Iterations=3072",
        "Pbkdf2PasswordHash.Algorithm=PBKDF2WithHmacSHA256",
        "Pbkdf2PasswordHash.SaltSizeBytes=32"
    }
)
public class ApplicationConfig {}
```

### LDAP Identity Store
```java
@LdapIdentityStoreDefinition(
    url            = "ldap://ldap.example.com:389",
    callerBaseDn   = "ou=users,dc=example,dc=com",
    groupSearchBase= "ou=groups,dc=example,dc=com"
)
```

### Login Page (Facelets)
```xhtml
<!-- login.xhtml -->
<h:form id="loginForm" prependId="false">
  <h:inputText     id="j_username" name="j_username" value=""/>
  <h:inputSecret   id="j_password" name="j_password" value=""/>
  <h:commandButton value="Login" />
  <!-- Action URL must be j_security_check -->
</h:form>
```

The form action must POST to `j_security_check`. With Jakarta Faces use a plain HTML form or ensure the action resolves to `j_security_check`.

### Role-Based Access in web.xml
```xml
<security-constraint>
  <web-resource-collection>
    <web-resource-name>Admin Area</web-resource-name>
    <url-pattern>/admin/*</url-pattern>
  </web-resource-collection>
  <auth-constraint>
    <role-name>admin</role-name>
  </auth-constraint>
</security-constraint>

<security-role><role-name>admin</role-name></security-role>
<security-role><role-name>user</role-name></security-role>
```

### Programmatic Security Check
```java
@Inject private SecurityContext securityContext;

public String adminAction() {
    if (!securityContext.isCallerInRole("admin")) {
        throw new NotAuthorizedException("Admin role required");
    }
    // ...
    return "success";
}

public String currentUser() {
    return securityContext.getCallerPrincipal().getName();
}
```

---

## Chapter 13: Client Certificates (Mutual TLS)

### Concept
Both client and server authenticate with X.509 certificates. Used in enterprise/IoT where password auth is insufficient.

### Server-Side Configuration (WildFly `standalone.xml`)
```xml
<security-realms>
  <security-realm name="ApplicationRealm">
    <server-identities>
      <ssl>
        <keystore path="server.keystore" relative-to="jboss.server.config.dir"
                  keystore-password="keystorePass" alias="server"
                  key-password="keyPass"/>
      </ssl>
    </server-identities>
    <authentication>
      <truststore path="server.truststore"
                  relative-to="jboss.server.config.dir"
                  keystore-password="truststorePass"/>
    </authentication>
  </security-realm>
</security-realms>

<!-- HTTPS listener with CLIENT-CERT -->
<https-listener name="https" socket-binding="https"
                security-realm="ApplicationRealm"
                verify-client="REQUIRED"/>
```

### Generating Certificates (OpenSSL / keytool)
```bash
# Generate CA key and self-signed cert
openssl req -newkey rsa:2048 -nodes -keyout ca.key -x509 -days 365 -out ca.crt

# Generate server cert signed by CA
keytool -genkeypair -alias server -keyalg RSA -keystore server.keystore -storepass pass
keytool -certreq -alias server -keystore server.keystore -storepass pass -file server.csr
openssl x509 -req -CA ca.crt -CAkey ca.key -in server.csr -out server.crt

# Generate client cert
keytool -genkeypair -alias client -keyalg RSA -keystore client.keystore -storepass pass
```

### Configure `web.xml` for CLIENT-CERT auth
```xml
<login-config>
  <auth-method>CLIENT-CERT</auth-method>
</login-config>
```

### Reading Client Cert in Servlet/Bean
```java
X509Certificate[] certs = (X509Certificate[])
    request.getAttribute("jakarta.servlet.request.X509Certificate");
if (certs != null && certs.length > 0) {
    String dn = certs[0].getSubjectX500Principal().getName();
    // extract CN, OU, etc.
}
```

---

## Chapter 14: REST Security (JWT Bearer Tokens)

### Jakarta REST Security Filter
```java
@Provider
@Priority(Priorities.AUTHENTICATION)
public class JwtAuthFilter implements ContainerRequestFilter {

    @Override
    public void filter(ContainerRequestContext ctx) {
        String authHeader = ctx.getHeaderString(HttpHeaders.AUTHORIZATION);
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            ctx.abortWith(Response.status(Response.Status.UNAUTHORIZED).build());
            return;
        }
        String token = authHeader.substring("Bearer ".length());
        try {
            validateToken(token);  // throws on invalid
        } catch (Exception e) {
            ctx.abortWith(Response.status(Response.Status.UNAUTHORIZED).build());
        }
    }
}
```

### Securing Specific Endpoints with `@NameBinding`
```java
// Define binding annotation
@NameBinding
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.TYPE, ElementType.METHOD})
public @interface Secured {}

// Apply to filter
@Secured
@Provider
@Priority(Priorities.AUTHENTICATION)
public class JwtAuthFilter implements ContainerRequestFilter { ... }

// Apply to resource
@Path("/orders")
public class OrderResource {
    @GET @Secured
    public List<Order> getOrders() { ... }

    @GET @Path("public")   // No @Secured — open
    public List<Order> getPublicOrders() { ... }
}
```

### MicroProfile JWT (Chapter 32 — see also)
For full JWT support including claim injection:
```xml
<dependency>
  <groupId>org.eclipse.microprofile.jwt</groupId>
  <artifactId>microprofile-jwt-auth-api</artifactId>
  <version>2.1</version>
</dependency>
```

```java
@Path("/profile")
@RequestScoped
@RolesAllowed("user")
public class ProfileResource {
    @Inject JsonWebToken jwt;

    @GET
    public String getEmail() {
        return jwt.getClaim("email");
    }
}
```

Enable in `microprofile-config.properties`:
```properties
mp.jwt.verify.publickey.location=/META-INF/public-key.pem
mp.jwt.verify.issuer=https://auth.example.com
```

---

## Chapter 31: Secured JMX

JMX (Java Management Extensions) for monitoring should be secured to prevent unauthorized access to MBeans.

### WildFly JMX over Remoting (secured)
WildFly exposes JMX via its management interface, which is already authenticated via the management realm.

**Connect from Java client:**
```java
Map<String, Object> env = new HashMap<>();
env.put(CallbackHandler.class.getName(),
    new AuthCallbackHandler("admin", "adminPass"));

JMXServiceURL url = new JMXServiceURL(
    "service:jmx:remote+http://localhost:9990");
JMXConnector conn = JMXConnectorFactory.connect(url, env);
MBeanServerConnection mbsc = conn.getMBeanServerConnection();
```

**JConsole with WildFly:**
```bash
./bin/jconsole.sh -J-Djava.class.path=bin/client/jboss-client.jar \
  service:jmx:remote+http://localhost:9990
```

### Registering a Secured Custom MBean
```java
@MXBean
public interface AppMetricsMXBean {
    long getActiveUsers();
    int getQueueDepth();
    void resetCounters();
}

@ApplicationScoped
public class AppMetrics implements AppMetricsMXBean {
    private long activeUsers;
    // ...

    @PostConstruct
    public void registerMBean() throws Exception {
        MBeanServer server = ManagementFactory.getPlatformMBeanServer();
        ObjectName name = new ObjectName("com.example:type=AppMetrics");
        server.registerMBean(this, name);
    }
}
```

---

## Chapter 32: Java Web Tokens with Encryption

### JWT Structure
```
Header.Payload.Signature
eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ1c2VyMSIsImlzcyI6Imh0dHBzOi8v...
```

### Generating JWT with JJWT Library
```xml
<dependency>
  <groupId>io.jsonwebtoken</groupId>
  <artifactId>jjwt-api</artifactId><version>0.12.5</version>
</dependency>
<dependency>
  <groupId>io.jsonwebtoken</groupId>
  <artifactId>jjwt-impl</artifactId><version>0.12.5</version><scope>runtime</scope>
</dependency>
```

```java
@ApplicationScoped
public class JwtService {
    private final PrivateKey privateKey;
    private final PublicKey  publicKey;

    public JwtService() throws Exception {
        KeyPair kp = KeyPairGenerator.getInstance("RSA").generateKeyPair();
        privateKey = kp.getPrivate();
        publicKey  = kp.getPublic();
    }

    public String generateToken(String subject, List<String> roles) {
        return Jwts.builder()
            .subject(subject)
            .issuer("https://auth.example.com")
            .issuedAt(new Date())
            .expiration(Date.from(Instant.now().plusSeconds(3600)))
            .claim("roles", roles)
            .signWith(privateKey)
            .compact();
    }

    public Claims validateToken(String token) {
        return Jwts.parser()
            .verifyWith(publicKey)
            .build()
            .parseSignedClaims(token)
            .getPayload();
    }
}
```

### Encrypted JWT (JWE)
Use the `jose4j` library for JWE (encrypted payloads):
```java
// Encrypt
JsonWebEncryption jwe = new JsonWebEncryption();
jwe.setAlgorithmHeaderValue(KeyManagementAlgorithmIdentifiers.RSA_OAEP_256);
jwe.setEncryptionMethodHeaderParameter(ContentEncryptionAlgorithmIdentifiers.AES_256_GCM);
jwe.setKey(recipientPublicKey);
jwe.setPayload(claims);
String encryptedToken = jwe.getCompactSerialization();
```

---

## Chapter 33: Java Enterprise Security API

Jakarta Security 3.0 full programmatic API.

### Custom HttpAuthenticationMechanism
```java
@ApplicationScoped
public class ApiKeyAuthMechanism implements HttpAuthenticationMechanism {

    @Inject private IdentityStoreHandler identityStoreHandler;

    @Override
    public AuthenticationStatus validateRequest(
            HttpServletRequest request,
            HttpServletResponse response,
            HttpMessageContext ctx) throws AuthException {

        String apiKey = request.getHeader("X-API-Key");
        if (apiKey == null) {
            return ctx.responseUnauthorized();
        }

        CredentialValidationResult result =
            identityStoreHandler.validate(new ApiKeyCredential(apiKey));

        if (result.getStatus() == VALID) {
            return ctx.notifyContainerAboutLogin(result);
        }
        return ctx.responseUnauthorized();
    }
}
```

### Custom IdentityStore
```java
@ApplicationScoped
public class ApiKeyIdentityStore implements IdentityStore {

    @Inject private ApiKeyRepository repo;

    @Override
    public CredentialValidationResult validate(Credential credential) {
        if (!(credential instanceof ApiKeyCredential)) {
            return NOT_VALIDATED_RESULT;
        }
        ApiKey key = repo.findByKey(((ApiKeyCredential) credential).getKey());
        if (key == null || key.isExpired()) return INVALID_RESULT;
        return new CredentialValidationResult(key.getOwner(), key.getRoles());
    }

    @Override
    public Set<ValidationType> validationTypes() {
        return EnumSet.of(ValidationType.VALIDATE);
    }
}
```

### CDI Events for Security
```java
// Observe login events
public void onLogin(@Observes @Authenticated AuthenticatedEvent event) {
    auditLog.record("Login: " + event.getPrincipal().getName());
}

public void onLogout(@Observes LoggedOutEvent event) {
    auditLog.record("Logout: " + event.getPrincipal().getName());
}
```

---

## Security Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| 401 on all requests | No `IdentityStore` found | Ensure `@ApplicationScoped` identity store is a CDI bean |
| Form redirect loops | Login page also secured | Exclude login page from security constraint |
| JWT expired but accepted | Clock skew | Add `allowedClockSkewSeconds` to parser |
| CLIENT-CERT auth fails | Truststore missing client CA | Import client CA into server truststore |
| JMX connection refused | Management port not open | Check WildFly management listener binding |
| CORS error on REST API | Missing CORS filter | Add `@Provider` CorsFilter with `Access-Control-Allow-Origin` |
