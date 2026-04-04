---
name: tomcat-expert
description: >
  Expert guide for Apache Tomcat administration, configuration, and deployment based on
  "Tomcat: The Definitive Guide" (Jason Brittain & Ian Darwin, O'Reilly). Use when the user
  needs to install, configure, deploy, tune, secure, or troubleshoot Apache Tomcat; integrate
  Tomcat with Apache httpd; set up clustering or session replication; manage server.xml,
  web.xml, or context configuration; handle SSL/TLS; configure realms and authentication;
  tune JVM or thread pool performance; or debug Tomcat startup/runtime issues.
  Covers Tomcat 11 (Jakarta EE 11, current), 10.1 (Jakarta EE 10), and 9.0 (Java EE 8, EOL 2027).
---

# Tomcat Expert

Based on *Tomcat: The Definitive Guide* by Jason Brittain & Ian Darwin, updated for current
versions. Tomcat 11.x is the latest (Jakarta EE 11); Tomcat 10.1.x is stable (Jakarta EE 10);
Tomcat 9.0.x is legacy (Java EE 8, EOL March 2027).

**Critical namespace change:** Tomcat 10+ uses `jakarta.*` packages. Apps built for Tomcat 9
and earlier use `javax.*` and must be migrated. Place old WARs in `webapps-javaee/` for
automatic migration via the bundled migration tool.

## Reference Files — Load by Topic

| Topic | File | Covers (book chapter) |
|---|---|---|
| Install, startup, shutdown | [references/installation.md](references/installation.md) | Ch. 1 |
| Configuration, server.xml, realms, sessions, JNDI | [references/configuration.md](references/configuration.md) | Ch. 2 + Ch. 7 |
| Deploying webapps, WAR files, Manager | [references/deployment.md](references/deployment.md) | Ch. 3 |
| Performance tuning, JVM, threads, benchmarking | [references/performance.md](references/performance.md) | Ch. 4 |
| Apache httpd integration, mod_proxy, APR | [references/apache-integration.md](references/apache-integration.md) | Ch. 5 |
| Security, SSL/TLS, SecurityManager, input filtering | [references/security.md](references/security.md) | Ch. 6 |
| Debugging, logs, troubleshooting | [references/debugging.md](references/debugging.md) | Ch. 8 |
| Clustering, load balancing, session replication | [references/clustering.md](references/clustering.md) | Ch. 10 |

## Quick Version Reference

| Version | Spec | Java Required | Status |
|---|---|---|---|
| 11.0.x | Jakarta EE 11 | Java 17+ | Current/latest |
| 10.1.x | Jakarta EE 10 | Java 11+ | Stable |
| 9.0.x | Java EE 8 | Java 8+ | Legacy (EOL Mar 2027) |

## Directory Layout

```
$CATALINA_HOME/
├── bin/          startup.sh, shutdown.sh, catalina.sh
├── conf/         server.xml, web.xml, context.xml, catalina.policy, tomcat-users.xml
├── lib/          shared JARs
├── logs/         catalina.out, access logs
├── webapps/      deployed applications
├── webapps-javaee/  auto-migrate javax.* → jakarta.* (Tomcat 10+)
├── work/         JSP compiled output
└── temp/         temporary files
```

`$CATALINA_BASE` separates instance config from installation when running multiple instances.
