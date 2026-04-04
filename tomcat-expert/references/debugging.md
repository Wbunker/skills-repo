# Tomcat Debugging and Troubleshooting (Ch. 8)

## Table of Contents
1. [Log Files](#log-files)
2. [Configuring Logging](#configuring-logging)
3. [Common Startup Failures](#common-startup-failures)
4. [Runtime Errors](#runtime-errors)
5. [HTTP Debugging](#http-debugging)
6. [RequestDumperValve](#requestdumpervalve)
7. [When Tomcat Won't Shut Down](#when-tomcat-wont-shut-down)
8. [Memory Issues](#memory-issues)
9. [Thread Dumps](#thread-dumps)
10. [JMX Monitoring](#jmx-monitoring)

---

## Log Files

Default log location: `$CATALINA_HOME/logs/`

| File | Contents |
|---|---|
| `catalina.out` | stdout/stderr; all console output; main log file to check first |
| `catalina.YYYY-MM-DD.log` | Tomcat internal log (from `java.util.logging`) |
| `localhost.YYYY-MM-DD.log` | Per-host application log |
| `localhost_access_log.YYYY-MM-DD.txt` | HTTP access log (if AccessLogValve configured) |
| `manager.YYYY-MM-DD.log` | Manager webapp log |
| `host-manager.YYYY-MM-DD.log` | Host Manager webapp log |

```bash
# Follow main log
tail -f $CATALINA_HOME/logs/catalina.out

# Search for errors
grep -i "exception\|error\|severe" $CATALINA_HOME/logs/catalina.out | tail -50

# Watch all logs
tail -f $CATALINA_HOME/logs/*.log $CATALINA_HOME/logs/*.txt
```

---

## Configuring Logging

`$CATALINA_BASE/conf/logging.properties` controls `java.util.logging`:

```properties
# Root logger — set to INFO normally; DEBUG for troubleshooting
.handlers = 1catalina.org.apache.juli.AsyncFileHandler, java.util.logging.ConsoleHandler
.level = INFO

# Enable DEBUG for specific component
org.apache.catalina.level = FINE
org.apache.coyote.level = FINE

# Per-application logging
com.example.myapp.level = FINE
```

**Log levels (JUL → Log4j/SLF4J equivalents):**
`SEVERE` = ERROR, `WARNING` = WARN, `INFO` = INFO, `FINE` = DEBUG, `FINER`/`FINEST` = TRACE

### Log4j 2 Integration

Replace JUL with Log4j 2 by adding the log4j-jul bridge JAR to `$CATALINA_HOME/lib/` and setting:
```bash
CATALINA_OPTS="-Djava.util.logging.manager=org.apache.logging.log4j.jul.LogManager"
```

---

## Common Startup Failures

### Port Already in Use

```
java.net.BindException: Address already in use: bind
```

```bash
# Find process using port 8080
ss -tlnp | grep 8080
lsof -i :8080

# Kill it
kill -9 <pid>
```

### JAVA_HOME Not Set

```
Neither the JAVA_HOME nor the JRE_HOME environment variable is defined
```

```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk' >> ~/.bashrc
```

### Wrong Java Version

```
UnsupportedClassVersionError: ... (class file version 61.0, this JVM supports 55.0)
```

Application was compiled for Java 17 (class version 61) but Tomcat is running on Java 11 (max 55). Upgrade JDK.

### ClassNotFoundException / NoClassDefFoundError

```
java.lang.ClassNotFoundException: com.example.MyServlet
```

Missing class — check:
1. Is the class in `WEB-INF/classes/` (compiled) or a JAR in `WEB-INF/lib/`?
2. Is the JAR present?
3. Rebuild and redeploy.

### `ClassNotFoundException: javax.servlet.Servlet` on Tomcat 10+

App was built against Java EE (`javax.servlet`). Tomcat 10+ requires Jakarta EE (`jakarta.servlet`).
- Quick fix: Drop WAR in `webapps-javaee/` for auto-migration
- Proper fix: Rebuild app with `jakarta.servlet-api` dependency

### Context Failed to Start

```
SEVERE: Error configuring application listener of class ...
```

Check `catalina.out` for the full stack trace above this message. Usually a missing dependency or a misconfigured `web.xml`.

---

## Runtime Errors

### 404 Not Found

1. Is Tomcat running? `curl http://localhost:8080/`
2. Is the app deployed? `curl -u admin:pass http://localhost:8080/manager/text/list`
3. Is the app started (not stopped)?
4. Is the URL correct? Check context path.
5. Is the servlet/JSP file present in the deployment?

### 500 Internal Server Error

Always check `catalina.out` for the stack trace. The HTTP response body often contains the exception too if `showReport` is not disabled.

### 403 Forbidden

- For Manager: your IP is not in the allow list in `manager/META-INF/context.xml`
- For app: a security constraint blocks the role; check `web.xml`

### OutOfMemoryError: Java heap space

```bash
# Add heap dump on OOM (then analyze with Eclipse MAT)
CATALINA_OPTS="-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp/heapdump.hprof"
```

### OutOfMemoryError: Metaspace

Usually caused by class loader leaks from repeated hot reloads. Restart Tomcat to recover. Long-term: increase metaspace limit and find the leak.

---

## HTTP Debugging

### curl

```bash
# Basic request with verbose headers
curl -v http://localhost:8080/myapp/

# POST with JSON
curl -v -X POST http://localhost:8080/myapp/api/data \
     -H "Content-Type: application/json" \
     -d '{"key":"value"}'

# Follow redirects, show response code
curl -L -o /dev/null -w "%{http_code}" http://localhost:8080/myapp/

# Check HTTPS certificate
curl -v --cacert /path/to/ca.crt https://localhost:8443/myapp/
```

### HTTPie (more readable than curl)

```bash
http GET localhost:8080/myapp/api/items
http POST localhost:8080/myapp/api/items name="Widget" price:=9.99
```

### Response Codes

| Code | Meaning | Common Cause |
|---|---|---|
| 200 | OK | — |
| 301/302 | Redirect | Security constraint (CONFIDENTIAL), `sendRedirect()` |
| 400 | Bad Request | Malformed request, invalid headers |
| 401 | Unauthorized | Missing credentials |
| 403 | Forbidden | IP blocked, missing role |
| 404 | Not Found | Wrong path, app not deployed |
| 500 | Server Error | Application exception |
| 503 | Service Unavailable | Thread pool exhausted |

---

## RequestDumperValve

Logs the complete request and response headers for debugging. **Development only — never use in production** (dumps all data including cookies/passwords).

```xml
<!-- server.xml, inside <Host> or <Context> -->
<Valve className="org.apache.catalina.valves.RequestDumperValve" />
```

Output goes to `localhost.YYYY-MM-DD.log`.

---

## When Tomcat Won't Shut Down

```bash
# Normal shutdown
$CATALINA_HOME/bin/shutdown.sh

# If that hangs, use the PID file
kill $(cat $CATALINA_HOME/temp/tomcat.pid)

# Nuclear option
kill -9 $(cat $CATALINA_HOME/temp/tomcat.pid)

# Find Tomcat process manually
ps aux | grep catalina
jps -l | grep Bootstrap
```

**Common causes of shutdown hang:**
- Non-daemon thread in a webapp that won't stop (daemon thread leak)
- Long-running request blocking graceful shutdown
- JDBC connection pool not releasing connections

**Graceful shutdown timeout** (Tomcat 9+):
```xml
<Server port="8005" shutdown="SHUTDOWN">
  <!-- Waits up to 30s for active requests to finish -->
</Server>
```

Set via JVM: `-Dorg.apache.catalina.startup.EXIT_ON_INIT_FAILURE=true`

---

## Memory Issues

### Heap Dump Analysis

```bash
# Generate heap dump of running Tomcat
jmap -dump:format=b,file=/tmp/heap.hprof <tomcat_pid>

# Or on OOM automatically
CATALINA_OPTS="-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp/"
```

Analyze with Eclipse Memory Analyzer (MAT) or VisualVM.

### Class Loader Leaks (PermGen/Metaspace)

Symptoms: `OutOfMemoryError: Metaspace` after repeated reloads.
Causes: Static fields referencing class instances, ThreadLocal not cleaned up, JDBC driver registration.

```java
// In ServletContextListener.contextDestroyed() — deregister JDBC drivers
Enumeration<Driver> drivers = DriverManager.getDrivers();
while (drivers.hasMoreElements()) {
  DriverManager.deregisterDriver(drivers.nextElement());
}
```

---

## Thread Dumps

Capture when Tomcat is slow or hanging:

```bash
# UNIX signal (non-destructive)
kill -3 <tomcat_pid>
# Output appears in catalina.out

# jstack (more portable)
jstack <tomcat_pid> > /tmp/threaddump.txt

# jcmd
jcmd <tomcat_pid> Thread.print > /tmp/threaddump.txt
```

**What to look for:**
- Many threads in `WAITING` on the same lock → deadlock or contention
- Many threads blocked on JDBC → database pool exhausted
- HTTP acceptor threads all busy → maxThreads exhausted; increase thread pool or acceptCount

---

## JMX Monitoring

Enable JMX remote access in `setenv.sh`:

```bash
CATALINA_OPTS="$CATALINA_OPTS
  -Dcom.sun.management.jmxremote
  -Dcom.sun.management.jmxremote.port=9090
  -Dcom.sun.management.jmxremote.rmi.port=9091
  -Dcom.sun.management.jmxremote.ssl=false
  -Dcom.sun.management.jmxremote.authenticate=false
  -Djava.rmi.server.hostname=127.0.0.1
"
```

Connect with **JConsole** or **VisualVM**:
- `jconsole localhost:9090`
- Key MBeans: `Catalina:type=ThreadPool`, `Catalina:type=GlobalRequestProcessor`, `Catalina:type=Manager`

**Tomcat Manager Status page** (no JMX needed):
`http://localhost:8080/manager/status` — shows active threads, memory, request rates
