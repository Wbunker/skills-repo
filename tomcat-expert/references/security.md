# Tomcat Security (Ch. 6)

## Table of Contents
1. [OS-Level Hardening](#os-level-hardening)
2. [Network Security](#network-security)
3. [Tomcat Hardening](#tomcat-hardening)
4. [SSL/TLS Configuration](#ssltls-configuration)
5. [SecurityManager](#securitymanager)
6. [Input Validation and Filtering](#input-validation-and-filtering)
7. [Access Control with Valves](#access-control-with-valves)
8. [Common Security Checklist](#common-security-checklist)

---

## OS-Level Hardening

**Never run Tomcat as root.** Create a dedicated low-privilege user:

```bash
useradd -r -m -U -d /opt/tomcat -s /bin/false tomcat
chown -R tomcat:tomcat /opt/tomcat
chmod -R 750 /opt/tomcat
chmod 640 /opt/tomcat/conf/*     # config files readable only by tomcat user
```

**Directory permissions:**
```bash
chmod 750 /opt/tomcat/bin/*.sh
chmod 640 /opt/tomcat/conf/server.xml
chmod 640 /opt/tomcat/conf/tomcat-users.xml
```

**File system isolation:** Consider running Tomcat in a container (Docker/Podman) or under systemd with sandboxing directives.

---

## Network Security

**Bind connectors to specific addresses:**

```xml
<!-- Only accept connections from localhost (when behind a proxy) -->
<Connector port="8080" address="127.0.0.1" ... />

<!-- Bind HTTP to all interfaces but AJP only to localhost -->
<Connector protocol="AJP/1.3" address="127.0.0.1" port="8009" ... />
```

**Disable unused connectors:** Comment out AJP if not using Apache httpd.

**Firewall rules:**
```bash
# Allow only 80/443 from internet; block 8080, 8009, 8005
iptables -A INPUT -p tcp --dport 8080 -s 127.0.0.1 -j ACCEPT
iptables -A INPUT -p tcp --dport 8080 -j DROP
```

**Change shutdown port and command** (default is trivially guessable):
```xml
<Server port="8005" shutdown="CHANGE_THIS_TO_SOMETHING_LONG_AND_RANDOM">
```
Or disable: `port="-1"` (requires `kill` to stop; prevents `shutdown.sh`).

---

## Tomcat Hardening

### Hide Server Version

In `conf/server.xml`, add to the existing `<Host>`:
```xml
<Valve className="org.apache.catalina.valves.ErrorReportValve"
       showReport="false"
       showServerInfo="false" />
```

Remove the default apps that expose server version:
```bash
rm -rf $CATALINA_HOME/webapps/ROOT
rm -rf $CATALINA_HOME/webapps/docs
rm -rf $CATALINA_HOME/webapps/examples
```

Restrict Manager/Host-Manager access to known IPs (see deployment.md).

### Secure tomcat-users.xml

Use digest passwords — never store plaintext:
```bash
# Generate SHA-256 digest
$CATALINA_HOME/bin/digest.sh -a SHA-256 -h org.apache.catalina.realm.MessageDigestCredentialHandler mypassword
```

Configure the realm to use digests:
```xml
<Realm className="org.apache.catalina.realm.UserDatabaseRealm" resourceName="UserDatabase">
  <CredentialHandler className="org.apache.catalina.realm.MessageDigestCredentialHandler"
                     algorithm="SHA-256" />
</Realm>
```

### HTTP Headers Hardening

Add security headers via a Filter in your app's `web.xml`, or via Apache httpd/Nginx:

```xml
<!-- In app web.xml or global conf/web.xml -->
<filter>
  <filter-name>httpHeaderSecurity</filter-name>
  <filter-class>org.apache.catalina.filters.HttpHeaderSecurityFilter</filter-class>
  <init-param>
    <param-name>hstsEnabled</param-name>
    <param-value>true</param-value>
  </init-param>
  <init-param>
    <param-name>hstsMaxAgeSeconds</param-name>
    <param-value>31536000</param-value>
  </init-param>
  <init-param>
    <param-name>antiClickJackingEnabled</param-name>
    <param-value>true</param-value>
  </init-param>
  <init-param>
    <param-name>antiClickJackingOption</param-name>
    <param-value>DENY</param-value>
  </init-param>
  <init-param>
    <param-name>xContentTypeOptionsEnabled</param-name>
    <param-value>true</param-value>
  </init-param>
</filter>
<filter-mapping>
  <filter-name>httpHeaderSecurity</filter-name>
  <url-pattern>/*</url-pattern>
</filter-mapping>
```

---

## SSL/TLS Configuration

### Generate Self-Signed Certificate (Development)

```bash
keytool -genkeypair -alias tomcat -keyalg RSA -keysize 2048 \
        -validity 365 \
        -keystore $CATALINA_HOME/conf/keystore.jks \
        -dname "CN=localhost, OU=Dev, O=MyOrg, L=City, S=State, C=US"
```

### Generate CSR for Commercial Certificate

```bash
keytool -genkeypair -alias tomcat -keyalg RSA -keysize 2048 \
        -keystore $CATALINA_HOME/conf/keystore.jks

keytool -certreq -alias tomcat \
        -keystore $CATALINA_HOME/conf/keystore.jks \
        -file tomcat.csr
# Submit tomcat.csr to your CA
```

After receiving cert:
```bash
keytool -importcert -alias tomcat -file signed_cert.crt \
        -keystore $CATALINA_HOME/conf/keystore.jks
```

### HTTPS Connector (JSSE/NIO — Tomcat 9+)

```xml
<Connector port="8443"
           protocol="org.apache.coyote.http11.Http11NioProtocol"
           SSLEnabled="true"
           maxThreads="150" scheme="https" secure="true">
  <SSLHostConfig protocols="TLSv1.2+TLSv1.3"
                 ciphers="HIGH:!aNULL:!MD5:!3DES">
    <Certificate certificateKeystoreFile="conf/keystore.jks"
                 certificateKeystorePassword="changeit"
                 type="RSA" />
  </SSLHostConfig>
</Connector>
```

### HTTPS with PEM Files (Tomcat 10+)

```xml
<Connector port="8443" protocol="org.apache.coyote.http11.Http11NioProtocol"
           SSLEnabled="true">
  <SSLHostConfig protocols="TLSv1.2+TLSv1.3">
    <Certificate certificateFile="conf/cert.pem"
                 certificateKeyFile="conf/key.pem"
                 certificateChainFile="conf/chain.pem"
                 type="RSA" />
  </SSLHostConfig>
</Connector>
```

### Force HTTPS Redirect

```xml
<!-- In web.xml security-constraint -->
<security-constraint>
  <web-resource-collection>
    <web-resource-name>All</web-resource-name>
    <url-pattern>/*</url-pattern>
  </web-resource-collection>
  <user-data-constraint>
    <transport-guarantee>CONFIDENTIAL</transport-guarantee>
  </user-data-constraint>
</security-constraint>
```

### Let's Encrypt / ACME

Use Certbot to obtain free certificates. Recommended approach: terminate TLS at Apache/Nginx (which handles ACME renewal natively), proxy to Tomcat over plain HTTP on localhost.

### TLS Best Practices

```xml
<SSLHostConfig protocols="TLSv1.2+TLSv1.3"
               disableSessionTickets="true"
               honorCipherOrder="false">
```

- Disable TLS 1.0 and TLS 1.1 (use `TLSv1.2+TLSv1.3`)
- Enable HSTS (see `HttpHeaderSecurityFilter` above)
- Use OCSP stapling: `<SSLHostConfig ... certificateVerificationDepth="10">`

---

## SecurityManager

Java's SecurityManager (deprecated in Java 17, removed in Java 21) allows fine-grained permissions. Use only on Tomcat 9 if needed.

Start Tomcat with SecurityManager:
```bash
$CATALINA_HOME/bin/catalina.sh start -security
```

Policy file: `conf/catalina.policy`

```
// Grant all to Tomcat itself
grant codeBase "file:${catalina.home}/bin/-" {
  permission java.security.AllPermission;
};

// Grant limited permissions to a web app
grant codeBase "file:${catalina.home}/webapps/myapp/-" {
  permission java.io.FilePermission "/tmp/-", "read,write";
  permission java.net.SocketPermission "api.example.com:443", "connect";
};
```

**Note:** SecurityManager is unavailable in Java 21+. Use OS-level sandboxing (containers, seccomp) instead.

---

## Input Validation and Filtering

### Built-in Filters

**CSRF Prevention:**
```xml
<filter>
  <filter-name>csrfPrevention</filter-name>
  <filter-class>org.apache.catalina.filters.CsrfPreventionFilter</filter-class>
</filter>
<filter-mapping>
  <filter-name>csrfPrevention</filter-name>
  <url-pattern>/*</url-pattern>
</filter-mapping>
```

**Request parameters filter (restrict special chars):**
```xml
<filter>
  <filter-name>parameterFilter</filter-name>
  <filter-class>org.apache.catalina.filters.RestCsrfPreventionFilter</filter-class>
</filter>
```

### Common Injection Vectors

| Attack | Prevention |
|---|---|
| SQL Injection | Use PreparedStatement/parameterized queries; never concatenate user input into SQL |
| XSS | HTML-encode all output: `ESAPI.encoder().encodeForHTML(input)` |
| Path Traversal | Validate and canonicalize file paths; use `File.getCanonicalPath()` |
| Command Injection | Never pass user input to `Runtime.exec()`; use parameterized alternatives |
| Log Injection | Sanitize newlines from user input before logging |

### HTTP Request Filtering (Connector level)

Reject requests with suspicious characters in the URL at the Connector level:
```xml
<Connector port="8080"
           relaxedQueryChars='[]|{}^&#x60;"&lt;&gt;'
           relaxedPathChars='[]|{}^&#x60;"&lt;&gt;' />
```

The default `allowedHttpMethods` in the HTTP Connector blocks non-standard methods.

---

## Access Control with Valves

### Restrict by IP

```xml
<!-- Allow only specific subnets -->
<Valve className="org.apache.catalina.valves.RemoteAddrValve"
       allow="127\.0\.0\.1|10\.0\.0\.\d+|192\.168\.1\.\d+" />
```

### Rate Limiting (Tomcat 11)

```xml
<Valve className="org.apache.catalina.valves.RateLimitFilter"
       bucketDuration="60"
       bucketRequests="300"
       statusCode="429"
       statusMessage="Too Many Requests" />
```

---

## Common Security Checklist

- [ ] Tomcat runs as dedicated non-root user
- [ ] Default apps removed (`ROOT`, `docs`, `examples`)
- [ ] Manager/Host-Manager restricted to localhost or internal IPs
- [ ] `tomcat-users.xml` uses digest passwords
- [ ] Server version hidden (`ErrorReportValve showServerInfo="false"`)
- [ ] Shutdown port changed or disabled
- [ ] AJP disabled or bound to `127.0.0.1` with `secret`
- [ ] HTTPS enabled; TLS 1.0/1.1 disabled
- [ ] HSTS header set
- [ ] `X-Content-Type-Options`, `X-Frame-Options` headers set
- [ ] `RemoteIpValve` configured if behind a reverse proxy
- [ ] Config files (`conf/`) not world-readable
- [ ] Application uses prepared statements (no SQL injection)
- [ ] All user output HTML-encoded (no XSS)
