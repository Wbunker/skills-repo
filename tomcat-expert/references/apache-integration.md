# Apache httpd Integration (Ch. 5)

## Table of Contents
1. [Why Integrate with Apache httpd?](#why-integrate-with-apache-httpd)
2. [mod_proxy_http (Recommended)](#mod_proxy_http-recommended)
3. [mod_proxy_ajp](#mod_proxy_ajp)
4. [Load Balancing with mod_proxy_balancer](#load-balancing-with-mod_proxy_balancer)
5. [Nginx as Reverse Proxy](#nginx-as-reverse-proxy)
6. [APR / Tomcat Native Connector](#apr--tomcat-native-connector)
7. [SSL Termination at the Proxy](#ssl-termination-at-the-proxy)

---

## Why Integrate with Apache httpd?

- **Performance:** Apache/Nginx serve static files much faster than Tomcat
- **Port 80/443:** Proxy avoids running Tomcat as root
- **SSL termination:** Handle TLS at the proxy; Tomcat receives plain HTTP
- **Load balancing:** Distribute across multiple Tomcat instances
- **Virtual hosting:** One front-end server, multiple backend apps
- **Security:** Expose only port 80/443; keep Tomcat on internal ports

---

## mod_proxy_http (Recommended)

The simplest and most modern approach. Uses HTTP to proxy requests to Tomcat.

### Apache httpd Configuration

```apache
# Enable required modules
LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so

<VirtualHost *:80>
  ServerName www.example.com

  # Don't proxy requests for static files
  ProxyPass /static/ !
  Alias /static/ /var/www/example/static/

  # Proxy everything else to Tomcat
  ProxyPass         /myapp  http://localhost:8080/myapp
  ProxyPassReverse  /myapp  http://localhost:8080/myapp

  # Pass real client IP to Tomcat
  ProxyPreserveHost On
  RequestHeader set X-Forwarded-For "%{REMOTE_ADDR}s"
  RequestHeader set X-Forwarded-Proto "http"
</VirtualHost>
```

### Proxy Root to Tomcat

```apache
ProxyPass         /  http://localhost:8080/
ProxyPassReverse  /  http://localhost:8080/
```

### Tomcat Configuration

Tomcat's Connector should listen only on localhost when behind a proxy:

```xml
<Connector port="8080" protocol="HTTP/1.1"
           address="127.0.0.1"
           connectionTimeout="20000"
           scheme="http"
           proxyName="www.example.com"
           proxyPort="80" />
```

`proxyName` and `proxyPort` ensure `request.getServerName()` and `request.getServerPort()` return the correct values (important for redirects and `HttpServletRequest` URL generation).

---

## mod_proxy_ajp

AJP (Apache JServ Protocol) is a binary protocol designed for Apache ↔ Tomcat communication. Slightly more efficient than HTTP proxy for high volumes, but requires AJP to be enabled in Tomcat (disabled by default since Tomcat 9.0.31+).

### Tomcat AJP Connector

```xml
<!-- conf/server.xml -->
<Connector protocol="AJP/1.3"
           address="127.0.0.1"
           port="8009"
           secretRequired="true"
           secret="changeme_strong_secret"
           redirectPort="8443" />
```

### Apache httpd Configuration

```apache
LoadModule proxy_ajp_module modules/mod_proxy_ajp.so

<VirtualHost *:80>
  ServerName www.example.com

  ProxyPass         /myapp  ajp://localhost:8009/myapp secret=changeme_strong_secret
  ProxyPassReverse  /myapp  ajp://localhost:8009/myapp
</VirtualHost>
```

**Security note:** Bind AJP to `127.0.0.1` only. Never expose AJP port to the internet (Ghost/Ghostcat vulnerability CVE-2020-1938 exploited exposed AJP connectors).

---

## Load Balancing with mod_proxy_balancer

```apache
LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so
LoadModule proxy_balancer_module modules/mod_proxy_balancer.so
LoadModule lbmethod_byrequests_module modules/mod_lbmethod_byrequests.so
LoadModule slotmem_shm_module modules/mod_slotmem_shm.so

<Proxy "balancer://tomcatcluster">
  BalancerMember http://tomcat1:8080 route=tc1
  BalancerMember http://tomcat2:8080 route=tc2
  BalancerMember http://tomcat3:8080 route=tc3 status=+H  # hot standby
  ProxySet lbmethod=byrequests    # byrequests | bytraffic | bybusyness | heartbeat
  ProxySet stickysession=JSESSIONID   # session affinity by cookie
  ProxySet nofailover=Off
</Proxy>

<VirtualHost *:80>
  ServerName www.example.com
  ProxyPass         /  balancer://tomcatcluster/
  ProxyPassReverse  /  balancer://tomcatcluster/
</VirtualHost>
```

**Session affinity (sticky sessions):**
- Requires Tomcat to append worker route to session ID
- In Tomcat `server.xml`, set `jvmRoute` on the Engine:
```xml
<Engine name="Catalina" defaultHost="localhost" jvmRoute="tc1">
```
Session IDs become: `ABC123.tc1` — Apache routes by the suffix.

**Balancer Manager UI:**
```apache
<Location /balancer-manager>
  SetHandler balancer-manager
  Require host localhost
</Location>
```

---

## Nginx as Reverse Proxy

Nginx is often preferred over Apache httpd for its performance as a reverse proxy.

```nginx
upstream tomcat_backend {
  server 127.0.0.1:8080;
  keepalive 32;
}

server {
  listen 80;
  server_name www.example.com;

  # Serve static files directly
  location /static/ {
    root /var/www/example;
    expires 1y;
    add_header Cache-Control "public, immutable";
  }

  # Proxy to Tomcat
  location / {
    proxy_pass http://tomcat_backend;
    proxy_http_version 1.1;
    proxy_set_header Connection "";           # enable keepalive
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_connect_timeout 5s;
    proxy_read_timeout 60s;
    proxy_send_timeout 60s;
  }
}
```

**Tomcat Connector** (when behind Nginx):
```xml
<Connector port="8080" protocol="HTTP/1.1"
           address="127.0.0.1"
           scheme="https"
           proxyName="www.example.com"
           proxyPort="443" />
```

---

## APR / Tomcat Native Connector

Apache Portable Runtime (APR) provides native I/O and OpenSSL-based SSL, which is significantly faster for SSL than JSSE.

### Installation

```bash
# Ubuntu/Debian
apt install libapr1 libtcnative-1

# RHEL/CentOS
yum install tomcat-native

# Or build from source
cd $CATALINA_HOME/bin
tar xzf tomcat-native.tar.gz
cd tomcat-native-*-src/native
./configure --with-apr=/usr/bin/apr-1-config \
            --with-java-home=$JAVA_HOME \
            --with-ssl=yes \
            --prefix=$CATALINA_HOME
make && make install
```

### Configuration

```bash
# setenv.sh — add native lib to path
export LD_LIBRARY_PATH=$CATALINA_HOME/lib:$LD_LIBRARY_PATH
```

```xml
<!-- server.xml — APR HTTP connector -->
<Listener className="org.apache.catalina.core.AprLifecycleListener"
          SSLEngine="on" />

<Connector port="8443" protocol="org.apache.coyote.http11.Http11AprProtocol"
           SSLEnabled="true">
  <SSLHostConfig>
    <Certificate certificateFile="conf/cert.pem"
                 certificateKeyFile="conf/key.pem"
                 type="RSA" />
  </SSLHostConfig>
</Connector>
```

**Note:** Tomcat Native / APR is optional and mainly beneficial for SSL workloads. For most deployments behind a TLS-terminating proxy, the NIO connector is sufficient.

---

## SSL Termination at the Proxy

When Apache httpd or Nginx terminates SSL, Tomcat receives plain HTTP. Configure Tomcat to trust the proxy's forwarded headers.

### RemoteIpValve (preserves client IP through proxy)

```xml
<!-- server.xml, inside <Host> -->
<Valve className="org.apache.catalina.valves.RemoteIpValve"
       remoteIpHeader="x-forwarded-for"
       proxiesHeader="x-forwarded-by"
       protocolHeader="x-forwarded-proto"
       internalProxies="127\.0\.0\.1|192\.168\.0\.\d+" />
```

With this valve, `request.getScheme()` returns `https` when `X-Forwarded-Proto: https` is set, and `request.getRemoteAddr()` returns the real client IP.

**Without this valve:** redirects and `HttpServletResponse.sendRedirect()` will generate `http://` URLs even when the user accessed via HTTPS.
