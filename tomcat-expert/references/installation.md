# Tomcat Installation & Startup (Ch. 1)

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation by Platform](#installation-by-platform)
3. [Environment Variables](#environment-variables)
4. [Starting and Stopping](#starting-and-stopping)
5. [Running as a Service](#running-as-a-service)
6. [Testing the Installation](#testing-the-installation)
7. [Multiple Instances](#multiple-instances)

---

## Prerequisites

- **Java:** Tomcat 11 requires Java 17+; Tomcat 10.1 requires Java 11+; Tomcat 9 requires Java 8+
- Download from: https://tomcat.apache.org/download-11.cgi (or /download-10.cgi, /download-90.cgi)
- Verify Java: `java -version`

---

## Installation by Platform

### Linux (binary release)

```bash
# Download and extract
wget https://downloads.apache.org/tomcat/tomcat-11/v11.0.x/bin/apache-tomcat-11.0.x.tar.gz
tar xzf apache-tomcat-11.0.x.tar.gz -C /opt
ln -s /opt/apache-tomcat-11.0.x /opt/tomcat

# Make scripts executable
chmod +x /opt/tomcat/bin/*.sh

# Create dedicated user (never run Tomcat as root)
useradd -r -m -U -d /opt/tomcat -s /bin/false tomcat
chown -R tomcat:tomcat /opt/tomcat
```

### Linux (package manager)

```bash
# Ubuntu/Debian
sudo apt install tomcat10   # or tomcat9

# RHEL/CentOS/Fedora
sudo dnf install tomcat
```

Package installs place config in `/etc/tomcat/` and webapps in `/var/lib/tomcat/webapps/`.

### Windows

1. Download the Windows installer (.exe) or zip from tomcat.apache.org
2. Run installer — optionally installs as Windows Service
3. Or: extract zip, set `JAVA_HOME`, run `bin\startup.bat`

### macOS

```bash
# Homebrew
brew install tomcat@10   # or tomcat (latest)
brew services start tomcat
```

Manual: extract tarball, set `JAVA_HOME`, run `bin/startup.sh`.

---

## Environment Variables

Set in `bin/setenv.sh` (create if it doesn't exist — sourced automatically by `catalina.sh`):

```bash
# bin/setenv.sh
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
export CATALINA_HOME=/opt/tomcat
export CATALINA_BASE=/opt/tomcat          # separate from HOME for multi-instance
export CATALINA_PID=/opt/tomcat/temp/tomcat.pid

# JVM tuning
export CATALINA_OPTS="-Xms512m -Xmx2g -XX:+UseG1GC"
export JAVA_OPTS="-Djava.awt.headless=true"
```

| Variable | Purpose |
|---|---|
| `JAVA_HOME` | JDK location |
| `CATALINA_HOME` | Tomcat installation directory |
| `CATALINA_BASE` | Instance-specific config (defaults to CATALINA_HOME) |
| `CATALINA_OPTS` | JVM options for Tomcat server process only |
| `JAVA_OPTS` | JVM options for all Java processes (including startup/stop scripts) |
| `CATALINA_PID` | PID file location (enables `catalina.sh stop` to kill by PID) |

---

## Starting and Stopping

```bash
# Start
$CATALINA_HOME/bin/startup.sh          # background, logs to catalina.out
$CATALINA_HOME/bin/catalina.sh run     # foreground (useful for debugging)

# Stop (graceful, 5 second timeout by default)
$CATALINA_HOME/bin/shutdown.sh

# Force stop if graceful fails
kill $(cat $CATALINA_HOME/temp/tomcat.pid)

# Windows
bin\startup.bat
bin\shutdown.bat
```

**Port conflicts:** Default ports are 8080 (HTTP), 8443 (HTTPS), 8009 (AJP), 8005 (shutdown).
Check with `ss -tlnp | grep 808` or `netstat -an | grep 8080`.

---

## Running as a Service

### systemd (Linux)

Create `/etc/systemd/system/tomcat.service`:

```ini
[Unit]
Description=Apache Tomcat 11
After=network.target

[Service]
Type=forking
User=tomcat
Group=tomcat
Environment="JAVA_HOME=/usr/lib/jvm/java-17-openjdk"
Environment="CATALINA_HOME=/opt/tomcat"
Environment="CATALINA_BASE=/opt/tomcat"
Environment="CATALINA_PID=/opt/tomcat/temp/tomcat.pid"
ExecStart=/opt/tomcat/bin/startup.sh
ExecStop=/opt/tomcat/bin/shutdown.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now tomcat
systemctl status tomcat
```

### Windows Service

Use `bin\service.bat install` (via Tomcat's service installer) or the Windows installer which handles this automatically.

### macOS launchd

Homebrew installs a plist automatically; use `brew services start tomcat`.

---

## Testing the Installation

1. Start Tomcat
2. Open http://localhost:8080 — should see the Tomcat welcome page
3. Check logs: `tail -f $CATALINA_HOME/logs/catalina.out`
4. Test Manager app: http://localhost:8080/manager/html (requires user in `tomcat-users.xml` with `manager-gui` role)

---

## Multiple Instances

Run multiple Tomcat instances from one installation using `CATALINA_BASE`:

```bash
# Instance directory structure
/opt/tomcat-instance1/
├── conf/        (copy from $CATALINA_HOME/conf/)
├── logs/
├── webapps/
├── work/
└── temp/

# Start instance
CATALINA_BASE=/opt/tomcat-instance1 /opt/tomcat/bin/startup.sh
```

Each instance needs unique port numbers in its `conf/server.xml`.
