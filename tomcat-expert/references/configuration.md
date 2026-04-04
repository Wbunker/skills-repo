# Tomcat Configuration Reference (Ch. 2 + Ch. 7)

## Table of Contents
1. [server.xml Structure](#serverxml-structure)
2. [Connectors](#connectors)
3. [Virtual Hosts](#virtual-hosts)
4. [Context Configuration](#context-configuration)
5. [Realms and Authentication](#realms-and-authentication)
6. [Session Management](#session-management)
7. [JNDI and JDBC Resources](#jndi-and-jdbc-resources)
8. [Valves](#valves)
9. [web.xml (Web Application)](#webxml-web-application)
10. [Other Config Files](#other-config-files)
11. [Version Migration Notes](#version-migration-notes)

---

## server.xml Structure

`$CATALINA_BASE/conf/server.xml` — main Tomcat configuration.

```xml
<Server port="8005" shutdown="SHUTDOWN">
  <Listener className="org.apache.catalina.startup.VersionLoggerListener" />

  <GlobalNamingResources>
    <Resource name="UserDatabase" auth="Container"
              type="org.apache.catalina.UserDatabase"
              factory="org.apache.catalina.users.MemoryUserDatabaseFactory"
              pathname="conf/tomcat-users.xml" />
  </GlobalNamingResources>

  <Service name="Catalina">
    <Executor name="tomcatThreadPool" className="org.apache.catalina.core.StandardThreadExecutor"
              maxThreads="200" minSpareThreads="10" />

    <Connector port="8080" protocol="HTTP/1.1"
               connectionTimeout="20000" redirectPort="8443"
               executor="tomcatThreadPool" />

    <Engine name="Catalina" defaultHost="localhost">
      <Realm className="org.apache.catalina.realm.LockOutRealm">
        <Realm className="org.apache.catalina.realm.UserDatabaseRealm"
               resourceName="UserDatabase" />
      </Realm>

      <Host name="localhost" appBase="webapps"
            unpackWARs="true" autoDeploy="true">
        <Valve className="org.apache.catalina.valves.AccessLogValve"
               directory="logs" prefix="localhost_access_log"
               suffix=".txt" pattern="%h %l %u %t &quot;%r&quot; %s %b" />
      </Host>
    </Engine>
  </Service>
</Server>
```

**Element hierarchy:** Server → Service → Connector(s) + Engine → Host(s) → Context(s)

---

## Connectors

### HTTP/1.1 Connector (NIO — default)

```xml
<Connector port="8080"
           protocol="HTTP/1.1"
           connectionTimeout="20000"
           maxHttpHeaderSize="8192"
           redirectPort="8443"
           compression="on"
           compressionMinSize="2048"
           noCompressionUserAgents="gozilla, traviata"
           compressibleMimeType="text/html,text/xml,text/plain,text/css,application/json" />
```

### HTTPS Connector

```xml
<!-- Tomcat 9 style (JSSE) -->
<Connector port="8443" protocol="org.apache.coyote.http11.Http11NioProtocol"
           SSLEnabled="true" scheme="https" secure="true">
  <SSLHostConfig>
    <Certificate certificateKeystoreFile="conf/keystore.jks"
                 certificateKeystorePassword="changeit"
                 type="RSA" />
  </SSLHostConfig>
</Connector>
```

```xml
<!-- Tomcat 10/11 with PEM files -->
<Connector port="8443" protocol="org.apache.coyote.http11.Http11NioProtocol"
           SSLEnabled="true">
  <SSLHostConfig>
    <Certificate certificateFile="conf/cert.pem"
                 certificateKeyFile="conf/key.pem"
                 type="RSA" />
  </SSLHostConfig>
</Connector>
```

### Changing Port 8080 to 80

Option 1 — Run Tomcat on port 80 (requires root or `authbind`):
```xml
<Connector port="80" protocol="HTTP/1.1" ... />
```

Option 2 — iptables redirect (preferred, no root needed for Tomcat):
```bash
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
```

Option 3 — Reverse proxy via Apache httpd or Nginx (recommended for production).

### AJP Connector (Tomcat 10+)

AJP is disabled by default in Tomcat 9.0.31+ and 10+. Enable only when using Apache httpd with mod_jk or mod_proxy_ajp and add a `secret`:

```xml
<Connector protocol="AJP/1.3" address="127.0.0.1" port="8009"
           secretRequired="true" secret="your_secret_here"
           redirectPort="8443" />
```

---

## Virtual Hosts

```xml
<Engine name="Catalina" defaultHost="www.example.com">
  <Host name="www.example.com" appBase="/var/www/example"
        unpackWARs="true" autoDeploy="true">
    <!-- apps in /var/www/example/ -->
  </Host>

  <Host name="shop.example.com" appBase="/var/www/shop"
        unpackWARs="true" autoDeploy="false">
    <Alias>store.example.com</Alias>
  </Host>
</Engine>
```

Each `Host` maps to a directory of web applications. DNS must point all hostnames to the server.

---

## Context Configuration

A Context represents a single web application.

**Preferred: Context XML fragment** at `conf/Catalina/hostname/appname.xml`:

```xml
<!-- conf/Catalina/localhost/myapp.xml -->
<Context docBase="/opt/webapps/myapp"
         path="/myapp"
         reloadable="false"
         crossContext="false">
  <Resource name="jdbc/MyDB" auth="Container"
            type="javax.sql.DataSource"
            ... />
</Context>
```

**`reloadable="true"`** — Tomcat watches for class changes and reloads (development only; hurts performance).

**`crossContext="true"`** — allows `ServletContext.getContext()` to access other apps (security risk; avoid).

---

## Realms and Authentication

Realms provide user/role data for container-managed security.

### UserDatabaseRealm (default — file-based)

```xml
<Realm className="org.apache.catalina.realm.UserDatabaseRealm"
       resourceName="UserDatabase" />
```

Users defined in `conf/tomcat-users.xml`:

```xml
<tomcat-users>
  <role rolename="manager-gui"/>
  <role rolename="admin-gui"/>
  <user username="admin" password="s3cr3t"
        roles="manager-gui,admin-gui"/>
</tomcat-users>
```

**Production:** Use a digest password instead of plaintext. Generate with:
```bash
bin/digest.sh -a SHA-256 mypassword
```
Then set `CredentialHandler` in server.xml.

### JDBCRealm

```xml
<Realm className="org.apache.catalina.realm.JDBCRealm"
       driverName="com.mysql.cj.jdbc.Driver"
       connectionURL="jdbc:mysql://localhost:3306/tomcat_users"
       connectionName="dbuser" connectionPassword="dbpass"
       userTable="users" userNameCol="username" userCredCol="password"
       userRoleTable="user_roles" roleNameCol="rolename" />
```

### JNDIRealm (LDAP/Active Directory)

```xml
<Realm className="org.apache.catalina.realm.JNDIRealm"
       connectionURL="ldap://ldap.example.com:389"
       userPattern="uid={0},ou=people,dc=example,dc=com"
       roleBase="ou=groups,dc=example,dc=com"
       roleName="cn"
       roleSearch="(member={0})" />
```

### Authentication Methods (in web.xml)

```xml
<login-config>
  <auth-method>FORM</auth-method>       <!-- BASIC | DIGEST | FORM | CLIENT-CERT -->
  <realm-name>My App</realm-name>
  <form-login-config>
    <form-login-page>/login.jsp</form-login-page>
    <form-error-page>/login-error.jsp</form-error-page>
  </form-login-config>
</login-config>

<security-constraint>
  <web-resource-collection>
    <web-resource-name>Secure Area</web-resource-name>
    <url-pattern>/admin/*</url-pattern>
  </web-resource-collection>
  <auth-constraint>
    <role-name>admin</role-name>
  </auth-constraint>
</security-constraint>
```

### Single Sign-On

Add to `<Host>` in server.xml:
```xml
<Valve className="org.apache.catalina.authenticator.SingleSignOn" />
```

---

## Session Management

### StandardManager (default — in-memory)

```xml
<Manager className="org.apache.catalina.session.StandardManager"
         maxActiveSessions="10000"
         sessionIdLength="32" />
```

Sessions lost on restart. Serializes sessions to `SESSIONS.ser` on shutdown by default.

### PersistentManager (survives restarts)

```xml
<Manager className="org.apache.catalina.session.PersistentManager"
         saveOnRestart="true"
         maxIdleBackup="10"
         minIdleSwap="60"
         maxIdleSwap="120">
  <Store className="org.apache.catalina.session.FileStore"
         directory="/tmp/tomcat-sessions" />
</Manager>
```

### JDBC Session Store

```xml
<Manager className="org.apache.catalina.session.PersistentManager">
  <Store className="org.apache.catalina.session.JDBCStore"
         driverName="com.mysql.cj.jdbc.Driver"
         connectionURL="jdbc:mysql://localhost/sessions"
         connectionName="user" connectionPassword="pass"
         sessionTable="tomcat_sessions"
         sessionIdCol="session_id"
         sessionDataCol="session_data"
         sessionValidCol="valid_session"
         sessionMaxInactiveCol="max_inactive"
         sessionLastAccessedCol="last_access" />
</Manager>
```

Session timeout in `web.xml` (minutes):
```xml
<session-config>
  <session-timeout>30</session-timeout>
</session-config>
```

---

## JNDI and JDBC Resources

### Connection Pool (DBCP2)

Define in `conf/context.xml` (global) or per-app context fragment:

```xml
<Resource name="jdbc/MyDB"
          auth="Container"
          type="javax.sql.DataSource"
          factory="org.apache.tomcat.jdbc.pool.DataSourceFactory"
          driverClassName="com.mysql.cj.jdbc.Driver"
          url="jdbc:mysql://localhost:3306/mydb"
          username="dbuser"
          password="dbpass"
          maxTotal="100"
          maxIdle="20"
          minIdle="5"
          maxWaitMillis="30000"
          validationQuery="SELECT 1"
          testOnBorrow="true" />
```

Lookup in servlet (Tomcat 9 / `javax.*`):
```java
Context ctx = new InitialContext();
DataSource ds = (DataSource) ctx.lookup("java:comp/env/jdbc/MyDB");
```

For Tomcat 10+ (`jakarta.*`): same code but `import jakarta.naming.*`.

Reference in `web.xml`:
```xml
<resource-ref>
  <res-ref-name>jdbc/MyDB</res-ref-name>
  <res-type>javax.sql.DataSource</res-type>
  <res-auth>Container</res-auth>
</resource-ref>
```

---

## Valves

Valves process requests/responses in the pipeline. Add inside `<Host>` or `<Context>`.

### AccessLogValve

```xml
<Valve className="org.apache.catalina.valves.AccessLogValve"
       directory="logs"
       prefix="access_log"
       suffix=".txt"
       pattern="%h %l %u %t &quot;%r&quot; %s %b %D"
       rotatable="true" />
```

Pattern variables: `%h`=remote host, `%u`=user, `%t`=time, `%r`=request line,
`%s`=status, `%b`=bytes, `%D`=processing time (ms).

### RemoteAddrValve (IP allowlist/blocklist)

```xml
<!-- Allow only localhost and internal network -->
<Valve className="org.apache.catalina.valves.RemoteAddrValve"
       allow="127\.0\.0\.1|192\.168\.1\.\d+" />

<!-- Block specific IPs -->
<Valve className="org.apache.catalina.valves.RemoteAddrValve"
       deny="10\.0\.0\.1" />
```

### ErrorReportValve

Disable server version in error pages (security hardening):
```xml
<Valve className="org.apache.catalina.valves.ErrorReportValve"
       showReport="false"
       showServerInfo="false" />
```

---

## web.xml (Web Application)

`WEB-INF/web.xml` defines application behavior. Key elements:

```xml
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee"
         version="6.0">  <!-- Jakarta EE 10 = 5.0, Jakarta EE 11 = 6.0 -->

  <display-name>My App</display-name>

  <!-- Servlet definition -->
  <servlet>
    <servlet-name>MyServlet</servlet-name>
    <servlet-class>com.example.MyServlet</servlet-class>
    <load-on-startup>1</load-on-startup>
  </servlet>
  <servlet-mapping>
    <servlet-name>MyServlet</servlet-name>
    <url-pattern>/api/*</url-pattern>
  </servlet-mapping>

  <!-- Filters -->
  <filter>
    <filter-name>AuthFilter</filter-name>
    <filter-class>com.example.AuthFilter</filter-class>
  </filter>
  <filter-mapping>
    <filter-name>AuthFilter</filter-name>
    <url-pattern>/*</url-pattern>
  </filter-mapping>

  <!-- Welcome files -->
  <welcome-file-list>
    <welcome-file>index.html</welcome-file>
    <welcome-file>index.jsp</welcome-file>
  </welcome-file-list>

  <!-- Error pages -->
  <error-page>
    <error-code>404</error-code>
    <location>/error/404.html</location>
  </error-page>
  <error-page>
    <exception-type>java.lang.Exception</exception-type>
    <location>/error/500.jsp</location>
  </error-page>

  <!-- Session -->
  <session-config>
    <session-timeout>30</session-timeout>
  </session-config>
</web-app>
```

---

## Other Config Files

| File | Purpose |
|---|---|
| `conf/context.xml` | Default context settings applied to all webapps |
| `conf/tomcat-users.xml` | Users and roles for UserDatabaseRealm |
| `conf/catalina.policy` | SecurityManager policy (when `-security` flag used) |
| `conf/catalina.properties` | Class loader paths, system properties |
| `conf/logging.properties` | Log levels and handlers |
| `conf/jaspic-providers.xml` | JASPIC authentication providers |

---

## Version Migration Notes

### Tomcat 9 → Tomcat 10/11 (Critical)

The most significant change: **`javax.*` → `jakarta.*`** namespace migration.

- Servlet API: `javax.servlet.*` → `jakarta.servlet.*`
- JSP: `javax.servlet.jsp.*` → `jakarta.servlet.jsp.*`
- JNDI: `javax.naming.*` → `jakarta.naming.*` (in app code using JNDI lookup)

**Auto-migration:** Drop old WAR into `$CATALINA_HOME/webapps-javaee/` — Tomcat 10+ runs the Tomcat Migration Tool automatically and deploys the converted app from `webapps/`.

**Manual migration tool:**
```bash
java -jar $CATALINA_HOME/lib/migration.jar --src myapp.war --dest myapp-jakarta.war
```

**web.xml namespace:** Update schema declaration:
```xml
<!-- Old (Java EE / Tomcat 9) -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee" version="4.0">

<!-- New (Jakarta EE 10 / Tomcat 10) -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee" version="5.0">

<!-- New (Jakarta EE 11 / Tomcat 11) -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee" version="6.0">
```

### AJP Security (Tomcat 9.0.31+)

AJP connector disabled by default; requires `secretRequired="true"` and a `secret` attribute when re-enabled.

### BIO Connector Removed (Tomcat 8.5+)

The old blocking-IO `Http11Protocol` connector is gone. Use `Http11NioProtocol` (default) or `Http11Nio2Protocol`.
