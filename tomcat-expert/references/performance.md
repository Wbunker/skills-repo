# Tomcat Performance Tuning (Ch. 4)

## Table of Contents
1. [JVM Tuning](#jvm-tuning)
2. [Connector and Thread Pool Tuning](#connector-and-thread-pool-tuning)
3. [Connection Pooling](#connection-pooling)
4. [JSP Precompilation](#jsp-precompilation)
5. [Compression](#compression)
6. [Caching Static Resources](#caching-static-resources)
7. [Load Testing Tools](#load-testing-tools)
8. [Capacity Planning](#capacity-planning)
9. [Virtual Threads (Java 21+)](#virtual-threads-java-21)

---

## JVM Tuning

Set in `bin/setenv.sh` via `CATALINA_OPTS`:

```bash
export CATALINA_OPTS="
  -Xms1g                    # initial heap (set equal to Xmx to avoid resizing)
  -Xmx4g                    # max heap
  -XX:+UseG1GC              # G1GC (default Java 9+; good for most cases)
  -XX:MaxGCPauseMillis=200  # target GC pause
  -XX:+UseStringDeduplication
  -Djava.awt.headless=true
  -Dfile.encoding=UTF-8
  -Djava.net.preferIPv4Stack=true
"
```

**GC selection guidance:**
- **G1GC** (`-XX:+UseG1GC`) — default Java 9+; balanced throughput/latency; good for heap 4GB+
- **ZGC** (`-XX:+UseZGC`) — ultra-low pause; Java 15+; good for latency-sensitive apps with large heaps
- **Shenandoah** — similar to ZGC; OpenJDK only

**Heap sizing:**
- Start: `-Xms` = `-Xmx` (eliminates heap resizing pauses)
- Rule of thumb: heap = 2× working set size, leave 25% of RAM for OS + non-heap
- Monitor with: `jstat -gc <pid> 5000` or JConsole/VisualVM

**Metaspace:**
```bash
-XX:MetaspaceSize=256m -XX:MaxMetaspaceSize=512m
```
Metaspace grows by default. Set `MaxMetaspaceSize` to prevent OOM in environments with many ClassLoaders (hot reloads, many apps).

---

## Connector and Thread Pool Tuning

### Shared Executor (Recommended)

```xml
<Executor name="tomcatThreadPool"
          className="org.apache.catalina.core.StandardThreadExecutor"
          namePrefix="catalina-exec-"
          maxThreads="400"
          minSpareThreads="25"
          maxQueueSize="100"
          prestartminSpareThreads="true" />

<Connector port="8080" protocol="HTTP/1.1"
           executor="tomcatThreadPool"
           acceptCount="100"
           connectionTimeout="20000"
           keepAliveTimeout="30000"
           maxKeepAliveRequests="100" />
```

**Key parameters:**

| Parameter | Default | Meaning |
|---|---|---|
| `maxThreads` | 200 | Max concurrent request handlers |
| `minSpareThreads` | 10 | Always-ready threads |
| `acceptCount` | 100 | Queue depth when all threads busy |
| `connectionTimeout` | 20000 ms | Time to wait for request line |
| `keepAliveTimeout` | 5000 ms | Time to wait for next request on keep-alive |
| `maxKeepAliveRequests` | 100 | Max requests per keep-alive connection |

**Thread count formula (starting point):**
```
maxThreads = available_cores × (1 + wait_time / service_time)
```

For CPU-bound: `cores × 1–2`. For I/O-bound (typical web app): `cores × 10–50`.

### NIO vs NIO2 vs APR

- **NIO** (`Http11NioProtocol`) — default; non-blocking; excellent for most use cases
- **NIO2** (`Http11Nio2Protocol`) — async NIO; marginal improvement over NIO in most tests
- **APR** (`Http11AprProtocol`) — native library (Tomcat Native); best for SSL with OpenSSL; required for sendfile

---

## Connection Pooling

Tomcat JDBC Pool (included) is faster than DBCP:

```xml
<Resource name="jdbc/MyDB"
          type="javax.sql.DataSource"
          factory="org.apache.tomcat.jdbc.pool.DataSourceFactory"
          driverClassName="com.mysql.cj.jdbc.Driver"
          url="jdbc:mysql://localhost:3306/mydb?useSSL=false&amp;serverTimezone=UTC"
          username="user" password="pass"
          maxActive="100"
          maxIdle="20"
          minIdle="10"
          maxWait="30000"
          initialSize="10"
          testOnBorrow="true"
          validationQuery="SELECT 1"
          validationInterval="30000"
          timeBetweenEvictionRunsMillis="30000"
          minEvictableIdleTimeMillis="60000"
          removeAbandoned="true"
          removeAbandonedTimeout="60"
          logAbandoned="true" />
```

---

## JSP Precompilation

Compiling JSPs ahead of time eliminates first-request latency.

### Request all JSPs at startup (simplest)

Add a Servlet to `web.xml`:
```xml
<servlet>
  <servlet-name>jsp</servlet-name>
  <servlet-class>org.apache.jasper.servlet.JspServlet</servlet-class>
</servlet>
```
Then make HTTP requests to all JSP URLs during deployment (e.g., via a smoke test script).

### Precompile at webapp start using JspC

```xml
<!-- in web.xml, map pre-compiled servlet -->
<servlet>
  <servlet-name>org.apache.jsp.index_jsp</servlet-name>
  <servlet-class>org.apache.jsp.index_jsp</servlet-class>
</servlet>
<servlet-mapping>
  <servlet-name>org.apache.jsp.index_jsp</servlet-name>
  <url-pattern>/index.jsp</url-pattern>
</servlet-mapping>
```

### Build-time with Maven/JspC

```bash
# Manual JspC compilation
$CATALINA_HOME/bin/jspc.sh -webapp /path/to/myapp -d /path/to/output/classes
```

---

## Compression

Enable HTTP response compression in the Connector:

```xml
<Connector port="8080" protocol="HTTP/1.1"
           compression="on"
           compressionMinSize="2048"
           compressibleMimeType="text/html,text/xml,text/plain,text/css,text/javascript,application/javascript,application/json"
           noCompressionUserAgents="gozilla, traviata" />
```

`compressionMinSize` — skip compression for responses smaller than this (bytes). Small responses cost more to compress than they save.

**Better alternative for static assets:** Let Apache httpd or Nginx handle static file compression with `mod_deflate` or `gzip_static`.

---

## Caching Static Resources

The `DefaultServlet` handles static files. Enable caching:

In `conf/web.xml` (global) or app's `web.xml`:
```xml
<servlet>
  <servlet-name>default</servlet-name>
  <servlet-class>org.apache.catalina.servlets.DefaultServlet</servlet-class>
  <init-param>
    <param-name>cacheMaxSize</param-name>
    <param-value>100000</param-value>  <!-- KB -->
  </init-param>
  <init-param>
    <param-name>cacheTTL</param-name>
    <param-value>5000</param-value>    <!-- ms -->
  </init-param>
  <init-param>
    <param-name>cacheObjectMaxSize</param-name>
    <param-value>500</param-value>     <!-- KB per object -->
  </init-param>
  <load-on-startup>1</load-on-startup>
</servlet>
```

For high-traffic static assets, serving via Apache httpd/Nginx in front of Tomcat is significantly faster.

---

## Load Testing Tools

### Apache Bench (ab) — quick baseline

```bash
# 1000 requests, 10 concurrent
ab -n 1000 -c 10 http://localhost:8080/myapp/

# With keep-alive
ab -n 1000 -c 10 -k http://localhost:8080/myapp/
```

Key metrics: Requests per second, Time per request (mean), Transfer rate, Connection times.

### Apache JMeter — realistic load tests

- GUI: `bin/jmeter.sh`
- Record browser interactions or define test plans manually
- Supports think times, user ramp-up, assertions, CSV data sets
- Run headless: `jmeter -n -t test-plan.jmx -l results.jtl`

### Siege

```bash
siege -c 25 -t 60s http://localhost:8080/myapp/
```

### Gatling — code-based load tests (Scala/DSL)

Preferred for CI/CD integration and repeatable, version-controlled tests.

---

## Capacity Planning

**Key measurements:**
- Throughput (requests/sec) at target concurrency
- 95th/99th percentile response times
- CPU and memory utilization under load

**Rough sizing formula:**
```
max_concurrent_users = maxThreads × (average_response_time_ms / 1000)
```

**Memory estimate:**
```
heap_required = (avg_session_size_KB × active_sessions) + (avg_request_size_KB × maxThreads) + app_overhead
```

**Monitoring in production:**
- JMX via JConsole or VisualVM: `CATALINA_OPTS="-Dcom.sun.management.jmxremote ..."`
- `/manager/status` page (server status)
- Access log analysis (AWStats, GoAccess)
- APM: New Relic, Dynatrace, OpenTelemetry

---

## Virtual Threads (Java 21+)

Tomcat 10.1+ supports Java 21 virtual threads for dramatically improved throughput on I/O-bound workloads.

```xml
<!-- server.xml: use virtual thread executor -->
<Executor name="virtualThreadPool"
          className="org.apache.catalina.core.StandardVirtualThreadExecutor"
          namePrefix="catalina-virt-" />

<Connector port="8080" protocol="HTTP/1.1"
           executor="virtualThreadPool" />
```

Virtual threads eliminate the thread-per-request bottleneck. No need to tune `maxThreads` — the JVM manages thread scheduling. Requires Java 21+ and Tomcat 10.1.x or 11.x.
