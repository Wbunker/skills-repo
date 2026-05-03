# Chapter 9: IMAP Server Performance Tuning

## Performance Bottlenecks

IMAP performance is typically limited by:
1. **Disk I/O** — reading/writing message files (most common)
2. **File descriptor limits** — each IMAP IDLE connection holds an fd
3. **DNS lookups** — per-connection reverse DNS
4. **TLS handshake overhead** — mitigated by session resumption
5. **Index/search** — full-text search on large mailboxes

## Disk I/O Optimization

### Use Maildir, not mbox

Maildir's one-file-per-message design enables concurrent access and benefits from OS file caching. mbox requires exclusive locks.

### Filesystem Tuning

```bash
# Mount with noatime to avoid updating access times on every read
# /etc/fstab:
/dev/sda2  /var/mail  ext4  defaults,noatime  0 2

# Or relatime (update atime only if older than mtime/ctime):
/dev/sda2  /var/mail  ext4  defaults,relatime  0 2
```

### SSD vs HDD

- **Active mailboxes**: SSD dramatically improves LIST and FETCH latency
- **Archival mailboxes**: HDD adequate
- **Mixed**: hot-tier SSD + cold-tier HDD with tiering

### Dovecot Index Files

Dovecot maintains per-mailbox index files (`dovecot.index`, `dovecot.index.cache`) that cache message metadata and avoid re-parsing message headers. These are critical for performance.

```
# Keep indexes on fast storage, mail on slower storage
mail_location = maildir:/var/mail/%u:INDEX=/var/cache/mail-indexes/%u
```

Never delete index files unless intentionally rebuilding; use `doveadm index` instead.

## Dovecot Process Settings

```
# conf.d/10-master.conf

# IMAP process limits
service imap {
  process_limit = 1024       # max concurrent IMAP processes
  vsz_limit = 256M           # per-process memory limit
}

# Pre-fork idle processes for fast connection handling
service imap-login {
  process_min_avail = 4      # always keep 4 ready processes
  service_count = 0          # never kill login processes
}
```

## File Descriptor Limits

Each IMAP IDLE connection keeps a file descriptor open. Raise OS limits:

```bash
# /etc/security/limits.conf
dovecot soft nofile 65536
dovecot hard nofile 65536

# systemd override
mkdir -p /etc/systemd/system/dovecot.service.d/
cat > /etc/systemd/system/dovecot.service.d/limits.conf <<EOF
[Service]
LimitNOFILE=65536
EOF
systemctl daemon-reload
```

Check current usage:
```bash
doveadm who | wc -l
cat /proc/$(pidof dovecot | awk '{print $1}')/limits | grep 'open files'
```

## Connection Limits and Rate Limiting

```
# conf.d/10-master.conf
service imap-login {
  client_limit = 10000        # total connections across all processes
}

# conf.d/20-imap.conf
imap_max_line_length = 65536  # reject overly long commands
```

Rate limit login attempts (per IP):
```
# conf.d/10-auth.conf
auth_cache_size = 10M
auth_cache_ttl = 1 hour

# Login process
login_max_connections = 256    # per imap-login process
```

## DNS and Reverse Lookups

By default Dovecot does a rDNS lookup for every connection. Disable if DNS is slow:
```
# conf.d/10-logging.conf
login_log_format_elements = user=<%u> method=%m rip=%r lip=%l mpid=%e %c
# (Remove %r if you don't want reverse DNS in logs)

# Disable rDNS:
# No direct conf option; ensure your DNS resolves quickly
# Or use a local caching resolver (systemd-resolved, unbound, dnsmasq)
```

## TLS Session Resumption

TLS handshakes are expensive. Enable session caching:
```
# conf.d/10-ssl.conf
ssl_session_timeout = 300       # 5 minutes session cache
ssl_dh = </etc/dovecot/dh.pem  # Pre-generated DH params

# Generate DH params (run once):
# openssl dhparam -out /etc/dovecot/dh.pem 4096
```

## IMAP IDLE and Connection Persistence

IMAP IDLE allows clients to maintain persistent connections waiting for new mail. This is more efficient than polling but uses connections.

Configure IDLE timeout:
```
# conf.d/20-imap.conf
imap_idle_notify_interval = 2 mins    # Send OK still-alive every 2 min
```

Clients should reconnect after the server IDLE timeout (default 30 minutes per RFC 2177). Ensure your load balancer / firewall does not kill long-lived connections:

```
# For nginx load balancer:
proxy_read_timeout 1800s;
proxy_send_timeout 1800s;

# For HAProxy:
timeout client  30m
timeout server  30m
```

## IMAP Proxying with Nginx

For large deployments, proxy IMAP through nginx to multiple backends:

```nginx
# /etc/nginx/nginx.conf
mail {
    auth_http     http://localhost:8080/auth;
    proxy_pass_error_message on;

    server {
        listen     993 ssl;
        protocol   imap;
        ssl_certificate     /etc/letsencrypt/live/mail.example.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/mail.example.com/privkey.pem;
    }
}
```

## Dovecot Director (Load Balancing)

Dovecot Director routes users to backend servers, ensuring a user always lands on the same backend (sticky sessions for index coherence):

```
# dovecot.conf on director node
protocols = director

service director {
  unix_listener login/director {
    mode = 0666
  }
  fifo_listener login/proxy-notify {
    mode = 0600
    user = $default_login_user
  }
  unix_listener director-userdb {
    mode = 0600
  }
  inet_listener {
    port = 9090
  }
}

director_servers = 10.0.0.2 10.0.0.3
director_mail_servers = 10.0.0.2 10.0.0.3
director_user_expire = 15 min
```

## Monitoring

```bash
# Active connections
doveadm who

# Per-user stats
doveadm stats dump user

# Global stats
doveadm stats dump global

# Replication lag (if using dsync replication)
doveadm replicator status '*'

# Log slow commands (> 5 seconds)
# conf.d/10-logging.conf:
# log_core_filter = category=storage,min_usecs=5000000
```

Metrics also available via Dovecot's built-in stats HTTP endpoint or via `prometheus_exporter` plugin.

## Benchmarking

```bash
# imaptest — Dovecot's IMAP load testing tool
apt install imaptest

imaptest host=mail.example.com \
  user=testuser pass=password \
  port=993 ssl \
  users=100 clients=10 \
  secs=60
```
