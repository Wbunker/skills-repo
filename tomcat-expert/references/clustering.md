# Tomcat Clustering (Ch. 10)

## Table of Contents
1. [Clustering Concepts](#clustering-concepts)
2. [Request Distribution Strategies](#request-distribution-strategies)
3. [Session Management in a Cluster](#session-management-in-a-cluster)
4. [Tomcat In-Memory Session Replication](#tomcat-in-memory-session-replication)
5. [Persistent Session Store (Database)](#persistent-session-store-database)
6. [Load Balancing with Apache httpd](#load-balancing-with-apache-httpd)
7. [Load Balancing with Nginx](#load-balancing-with-nginx)
8. [Health Checks and Failover](#health-checks-and-failover)
9. [Stateless Architecture (Preferred)](#stateless-architecture-preferred)

---

## Clustering Concepts

| Term | Definition |
|---|---|
| Cluster | Group of Tomcat instances serving the same application |
| Load balancer | Front-end that distributes requests across cluster members |
| Session affinity (sticky sessions) | Routing a user's requests to the same server throughout their session |
| Session replication | Copying session data to all (or some) cluster members |
| Failover | Redirecting requests to another member when one fails |
| `jvmRoute` | Unique ID appended to session IDs to identify the originating server |

**Session affinity vs. replication:**
- Affinity alone: simpler, lower overhead, but session is lost if that server fails
- Replication: sessions survive server failure, but higher overhead
- Stateless design (JWT, server-side cache like Redis): no session to replicate — best for scalability

---

## Request Distribution Strategies

### DNS Round Robin

- Multiple A records for the same hostname
- Simplest setup; no single point of failure at DNS
- No health checking; requests route to dead servers until DNS TTL expires
- No session affinity
- **Suitable for:** truly stateless applications

### TCP Load Balancer (HAProxy, AWS NLB)

```
Client → HAProxy (TCP L4) → Tomcat instances
```

HAProxy example (`/etc/haproxy/haproxy.cfg`):
```
frontend http_front
  bind *:80
  default_backend tomcat_servers

backend tomcat_servers
  balance roundrobin
  option httpchk GET /health
  cookie SERVERID insert indirect nocache
  server tc1 10.0.0.1:8080 check cookie tc1
  server tc2 10.0.0.2:8080 check cookie tc2
  server tc3 10.0.0.3:8080 check cookie tc3 backup
```

### HTTP Reverse Proxy (Apache httpd, Nginx)

See [apache-integration.md](apache-integration.md) for full configuration.

---

## Session Management in a Cluster

### Option 1: Sticky Sessions (Session Affinity)

Route requests from a given session to the same Tomcat instance. Simple, no replication overhead.

**Tomcat setup** — set `jvmRoute` on the Engine:
```xml
<!-- server.xml on each node — unique per node -->
<Engine name="Catalina" defaultHost="localhost" jvmRoute="tc1">
```

Session IDs become: `ABC123XYZ.tc1`

**Load balancer** routes by the suffix (`.tc1`, `.tc2`, etc.) — see apache-integration.md for mod_proxy_balancer configuration.

**Limitation:** Sessions lost when that node fails.

### Option 2: All-to-All Session Replication

Every node has a copy of every session. Provides full failover.

See [Tomcat In-Memory Session Replication](#tomcat-in-memory-session-replication) below.

**Limitation:** Memory and network overhead scales with O(n × session_count). Not practical for large clusters (> ~6 nodes) or large sessions.

### Option 3: External Session Store (Redis/Memcached)

Sessions stored in a shared external cache. Any node can serve any request. Best scalability.

Use a library like **Spring Session** with Redis:
```xml
<!-- pom.xml -->
<dependency>
  <groupId>org.springframework.session</groupId>
  <artifactId>spring-session-data-redis</artifactId>
</dependency>
```

No Tomcat clustering configuration needed — the app handles it.

---

## Tomcat In-Memory Session Replication

Tomcat's built-in clustering uses IP multicast (or static membership) to discover nodes and replicate sessions.

### Configuration (identical on all nodes — only `jvmRoute` differs)

```xml
<!-- server.xml, inside <Engine> -->
<Cluster className="org.apache.catalina.ha.tcp.SimpleTcpCluster"
         channelSendOptions="8">

  <Manager className="org.apache.catalina.ha.session.DeltaManager"
           expireSessionsOnShutdown="false"
           notifyListenersOnReplication="true" />

  <Channel className="org.apache.catalina.tribes.group.GroupChannel">
    <Membership className="org.apache.catalina.tribes.membership.McastService"
                address="228.0.0.4"
                port="45564"
                frequency="500"
                dropTime="3000" />

    <Receiver className="org.apache.catalina.tribes.transport.nio.NioReceiver"
              address="auto"
              port="4000"
              autoBind="100"
              selectorTimeout="5000"
              maxThreads="6" />

    <Sender className="org.apache.catalina.tribes.transport.ReplicationTransmitter">
      <Transport className="org.apache.catalina.tribes.transport.nio.PooledParallelSender" />
    </Sender>

    <Interceptor className="org.apache.catalina.tribes.group.interceptors.TcpFailureDetector" />
    <Interceptor className="org.apache.catalina.tribes.group.interceptors.MessageDispatchInterceptor" />
  </Channel>

  <Valve className="org.apache.catalina.ha.tcp.ReplicationValve" filter="" />
  <Valve className="org.apache.catalina.ha.session.JvmRouteBinderValve" />

  <ClusterListener className="org.apache.catalina.ha.session.ClusterSessionListener" />
</Cluster>
```

**Enable distributable in `web.xml`** — required for session replication:
```xml
<web-app ...>
  <distributable/>
  ...
</web-app>
```

All objects stored in the session must be `Serializable`.

### Static Membership (no multicast)

For cloud environments where multicast is unavailable:
```xml
<Channel ...>
  <!-- Replace McastService with StaticMembershipService -->
  <Interceptor className="org.apache.catalina.tribes.group.interceptors.StaticMembershipInterceptor">
    <Member className="org.apache.catalina.tribes.membership.StaticMember"
            host="10.0.0.1" port="4000" uniqueId="{0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,1}" />
    <Member className="org.apache.catalina.tribes.membership.StaticMember"
            host="10.0.0.2" port="4000" uniqueId="{0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,2}" />
  </Interceptor>
  ...
</Channel>
```

### Test IP Multicast

```bash
# On each node — check multicast support
route -n | grep "224\."

# Test with multicast ping (install mtools)
ping 228.0.0.4
```

---

## Persistent Session Store (Database)

Simpler than in-memory replication; sessions survive restarts; suitable for moderate scale.

```xml
<!-- In Context (per-app) or conf/context.xml (global) -->
<Manager className="org.apache.catalina.session.PersistentManager"
         saveOnRestart="true"
         maxIdleBackup="30"
         minIdleSwap="60"
         maxIdleSwap="600">
  <Store className="org.apache.catalina.session.JDBCStore"
         driverName="com.mysql.cj.jdbc.Driver"
         connectionURL="jdbc:mysql://db-host:3306/tomcat_sessions"
         connectionName="tomcat" connectionPassword="password"
         sessionTable="tomcat_sessions"
         sessionIdCol="session_id"
         sessionDataCol="session_data"
         sessionValidCol="valid_session"
         sessionMaxInactiveCol="max_inactive"
         sessionLastAccessedCol="last_access" />
</Manager>
```

**Create the sessions table:**
```sql
CREATE TABLE tomcat_sessions (
  session_id     VARCHAR(100) NOT NULL PRIMARY KEY,
  valid_session  CHAR(1)      NOT NULL,
  max_inactive   INT          NOT NULL,
  last_access    BIGINT       NOT NULL,
  app_name       VARCHAR(255),
  session_data   MEDIUMBLOB,
  KEY kapp_last_access (app_name, last_access)
);
```

---

## Load Balancing with Apache httpd

Full configuration in [apache-integration.md](apache-integration.md). Key points for clustering:

```apache
<Proxy "balancer://mycluster">
  BalancerMember http://10.0.0.1:8080 route=tc1 loadfactor=1
  BalancerMember http://10.0.0.2:8080 route=tc2 loadfactor=1
  ProxySet lbmethod=byrequests
  ProxySet stickysession=JSESSIONID
</Proxy>
```

Requires `jvmRoute` set on each Tomcat's Engine element matching the `route=` value.

---

## Load Balancing with Nginx

```nginx
upstream tomcat_cluster {
  ip_hash;  # sticky sessions by client IP (simple alternative to cookie-based)
  server 10.0.0.1:8080 weight=1;
  server 10.0.0.2:8080 weight=1;
  server 10.0.0.3:8080 weight=1 backup;
  keepalive 32;
}
```

For cookie-based sticky sessions with Nginx, use the `sticky` directive (Nginx Plus) or a Lua-based solution.

---

## Health Checks and Failover

### Simple Health Check Endpoint

Add a lightweight servlet or static file that returns 200:

```java
@WebServlet("/health")
public class HealthServlet extends HttpServlet {
  protected void doGet(HttpServletRequest req, HttpServletResponse resp)
      throws IOException {
    resp.setStatus(200);
    resp.getWriter().write("OK");
  }
}
```

### Apache httpd Health Check

```apache
<Proxy "balancer://mycluster">
  BalancerMember http://10.0.0.1:8080 route=tc1
  ProxySet lbmethod=bybusyness
  ProxySet nofailover=Off
</Proxy>

# Built-in health check (mod_proxy_hcheck)
<Proxy "balancer://mycluster">
  BalancerMember http://10.0.0.1:8080 hcmethod=GET hcuri=/health hcinterval=10
</Proxy>
```

### HAProxy Health Check

```
backend tomcat_servers
  option httpchk GET /health HTTP/1.1\r\nHost:\ localhost
  http-check expect status 200
  server tc1 10.0.0.1:8080 check inter 10s fall 3 rise 2
```

---

## Stateless Architecture (Preferred)

For new applications, avoid server-side HTTP session state entirely:

- **JWTs** in cookies or Authorization header — client holds state
- **Spring Session + Redis** — centralized session store, any node serves any request
- **Database-backed state** — each request reads from DB

Benefits: trivially scalable, no clustering configuration, deploys independently.

```
Client → Any Tomcat node (no affinity needed) → Shared DB/Redis
```

When this is feasible, skip all clustering configuration above and simply run multiple Tomcat instances behind a round-robin load balancer.
