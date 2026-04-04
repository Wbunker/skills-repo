# Tomcat Deployment (Ch. 3)

## Table of Contents
1. [Web Application Layout](#web-application-layout)
2. [Deployment Methods](#deployment-methods)
3. [Virtual Hosts](#virtual-hosts)
4. [Manager Web Application](#manager-web-application)
5. [Hot Deployment and Reloading](#hot-deployment-and-reloading)
6. [Working with WAR Files](#working-with-war-files)
7. [Deployment with Maven](#deployment-with-maven)
8. [Common Deployment Errors](#common-deployment-errors)

---

## Web Application Layout

```
myapp/
├── WEB-INF/
│   ├── web.xml                   (deployment descriptor — required)
│   ├── classes/                  (compiled .class files)
│   │   └── com/example/MyServlet.class
│   ├── lib/                      (JAR dependencies)
│   │   └── dependency.jar
│   └── tags/                     (tag library descriptors)
├── META-INF/
│   └── context.xml               (optional: per-app context config)
├── index.html
├── index.jsp
└── static/
    ├── css/
    └── js/
```

`WEB-INF/` is never served directly to clients.
`META-INF/context.xml` overrides Context settings for this app.

---

## Deployment Methods

### 1. Drop into webapps/ (Simplest)

```bash
# Deploy unpacked directory
cp -r myapp/ $CATALINA_HOME/webapps/

# Deploy WAR file
cp myapp.war $CATALINA_HOME/webapps/
```

With `autoDeploy="true"` on the Host, Tomcat detects and deploys automatically.
The context path is the directory/WAR name: `myapp.war` → `/myapp`.
Root context: name the WAR `ROOT.war` or directory `ROOT/`.

### 2. Context XML Fragment (Recommended for Production)

Create `$CATALINA_BASE/conf/Catalina/localhost/myapp.xml`:

```xml
<Context docBase="/opt/apps/myapp"
         path="/myapp"
         reloadable="false">
  <!-- JNDI resources, environment entries, etc. -->
</Context>
```

Benefits: app lives outside `webapps/`, deployment config is separate from app code, no accidental undeploy.

**Naming:** filename determines the path (`myapp.xml` → `/myapp`); `ROOT.xml` → `/`.

### 3. server.xml Context (Avoid in Production)

```xml
<Host name="localhost" ...>
  <Context path="/myapp" docBase="/opt/apps/myapp" reloadable="false" />
</Host>
```

Requires Tomcat restart to pick up changes. Use fragment files instead.

### Jakarta EE Migration (Tomcat 10+)

Drop a Java EE WAR (using `javax.*`) into `webapps-javaee/`:
```bash
cp legacy-app.war $CATALINA_HOME/webapps-javaee/
```
Tomcat auto-migrates and deploys the converted app to `webapps/`.

---

## Virtual Hosts

Multiple hostnames on one Tomcat instance, each with its own webapps directory:

```xml
<Engine name="Catalina" defaultHost="www.example.com">
  <Host name="www.example.com" appBase="/srv/www/example/webapps"
        unpackWARs="true" autoDeploy="true">
  </Host>
  <Host name="api.example.com" appBase="/srv/www/api/webapps"
        unpackWARs="true" autoDeploy="false">
    <Alias>api2.example.com</Alias>
  </Host>
</Engine>
```

Context XML fragments for each virtual host go in:
`$CATALINA_BASE/conf/Catalina/api.example.com/myapp.xml`

---

## Manager Web Application

Built-in management UI and HTTP API at `/manager`.

### Setup — Add user to `conf/tomcat-users.xml`:

```xml
<role rolename="manager-gui"/>
<role rolename="manager-script"/>
<user username="admin" password="s3cr3t"
      roles="manager-gui,manager-script"/>
```

**Roles:**
- `manager-gui` — web UI
- `manager-script` — HTTP API (Ant, curl)
- `manager-jmx` — JMX proxy
- `manager-status` — server status only

**Remote access restriction:** By default, Manager only allows `127.0.0.1`. To allow other IPs, edit `webapps/manager/META-INF/context.xml`:
```xml
<Context antiResourceLocking="false" privileged="true">
  <Valve className="org.apache.catalina.valves.RemoteAddrValve"
         allow="127\.0\.0\.1|192\.168\.1\.\d+" />
</Context>
```

### Manager HTTP API

```bash
# Deploy WAR
curl -u admin:s3cr3t "http://localhost:8080/manager/text/deploy?path=/myapp" \
     --upload-file myapp.war

# Undeploy
curl -u admin:s3cr3t "http://localhost:8080/manager/text/undeploy?path=/myapp"

# Start / Stop / Reload
curl -u admin:s3cr3t "http://localhost:8080/manager/text/start?path=/myapp"
curl -u admin:s3cr3t "http://localhost:8080/manager/text/stop?path=/myapp"
curl -u admin:s3cr3t "http://localhost:8080/manager/text/reload?path=/myapp"

# List deployed applications
curl -u admin:s3cr3t "http://localhost:8080/manager/text/list"

# Server status
curl -u admin:s3cr3t "http://localhost:8080/manager/text/serverinfo"
```

---

## Hot Deployment and Reloading

**`autoDeploy="true"`** (Host attribute) — Tomcat polls for new/changed WARs and context files. Suitable for development.

**`reloadable="true"`** (Context attribute) — Tomcat watches `WEB-INF/classes/` and `WEB-INF/lib/` for changes and reloads the context. Significant performance cost; use only in development.

**Production pattern:** Set both to `false`; deploy new WARs via Manager API or replace files and use Manager reload.

**`deployOnStartup="true"`** (Host attribute, default) — Deploy all apps found in `appBase` at startup.

---

## Working with WAR Files

```bash
# Build WAR from directory
jar -cvf myapp.war -C myapp/ .

# Inspect WAR contents
jar -tf myapp.war

# Extract WAR
jar -xvf myapp.war

# Using Maven
mvn package    # produces target/myapp.war
```

---

## Deployment with Maven

### Tomcat Maven Plugin

```xml
<!-- pom.xml -->
<plugin>
  <groupId>org.apache.tomcat.maven</groupId>
  <artifactId>tomcat10-maven-plugin</artifactId>
  <version>2.3</version>
  <configuration>
    <url>http://localhost:8080/manager/text</url>
    <server>TomcatServer</server>   <!-- credentials in ~/.m2/settings.xml -->
    <path>/myapp</path>
  </configuration>
</plugin>
```

`~/.m2/settings.xml`:
```xml
<servers>
  <server>
    <id>TomcatServer</id>
    <username>admin</username>
    <password>s3cr3t</password>
  </server>
</servers>
```

```bash
mvn tomcat10:deploy
mvn tomcat10:redeploy
mvn tomcat10:undeploy
```

---

## Common Deployment Errors

| Error | Cause | Fix |
|---|---|---|
| 404 after deploy | Wrong context path or app not started | Check Manager `/list`; verify path matches URL |
| `ClassNotFoundException` | Missing JAR in `WEB-INF/lib/` | Add dependency to WAR |
| `NoClassDefFoundError: javax/servlet/...` | Tomcat 10+ with Java EE app | Migrate `javax.*` → `jakarta.*` or use `webapps-javaee/` |
| Context fails to start | Error in `web.xml` or listener init | Check `catalina.out` for stack trace |
| `FileNotFoundException` on deploy | `docBase` path does not exist | Verify path and permissions |
| Old code still running | Browser or Tomcat cache | Hard refresh; use Manager reload; clear `work/Catalina/` |
| Manager returns 403 | IP not in RemoteAddrValve allow list | Update `manager/META-INF/context.xml` |

**Clear compiled JSP cache:**
```bash
rm -rf $CATALINA_HOME/work/Catalina/localhost/myapp/
# Then reload or restart the app
```
