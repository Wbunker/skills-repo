# Oozie Operations
## Chapters 3, 9: Deployment, CLI, REST API, Monitoring, HA, Security, Tuning, Debugging

---

## Chapter 3: Oozie Deployment

### Prerequisites

```
Java 8+
Hadoop 2.x or 3.x (YARN)
Maven 3.x (to build from source)
Relational DB: MySQL 5.x+, PostgreSQL 9.x+, or Oracle 11g+
  (Apache Derby for development only)
```

### Build from Source

```bash
# Clone and build (skipping tests for speed)
git clone https://github.com/apache/oozie.git
cd oozie
mvn clean package -DskipTests -Phadoop-2

# The distro tarball appears in:
distro/target/oozie-<version>-distro.tar.gz
```

### Install Oozie Server

```bash
# Extract
tar -xzf oozie-<version>-distro.tar.gz
cd oozie-<version>

# Configure Hadoop libs
bin/oozie-setup.sh prepare-war

# Set up shared library on HDFS
hdfs dfs -mkdir -p /user/oozie
bin/oozie-setup.sh sharelib create -fs hdfs://namenode:8020

# Initialize the database
bin/ooziedb.sh create -sqlfile oozie.sql -run

# Start Oozie
bin/oozied.sh start

# Verify
bin/oozie admin -oozie http://localhost:11000/oozie -status
```

### oozie-site.xml: Key Configuration Properties

```xml
<!-- Database -->
<property>
  <name>oozie.service.JPAService.jdbc.driver</name>
  <value>com.mysql.jdbc.Driver</value>
</property>
<property>
  <name>oozie.service.JPAService.jdbc.url</name>
  <value>jdbc:mysql://dbhost:3306/oozie</value>
</property>
<property>
  <name>oozie.service.JPAService.jdbc.username</name>
  <value>oozie</value>
</property>
<property>
  <name>oozie.service.JPAService.jdbc.password</name>
  <value>oozie-password</value>
</property>

<!-- Shared library path -->
<property>
  <name>oozie.service.WorkflowAppService.system.libpath</name>
  <value>/user/oozie/share/lib</value>
</property>

<!-- Max concurrent actions per workflow -->
<property>
  <name>oozie.service.ActionService.executor.ext.classes</name>
  <value>org.apache.oozie.action.email.EmailActionExecutor</value>
</property>

<!-- Email (for email action) -->
<property>
  <name>oozie.email.smtp.host</name>
  <value>smtp.example.com</value>
</property>
<property>
  <name>oozie.email.from.address</name>
  <value>oozie@example.com</value>
</property>

<!-- Purge settings -->
<property>
  <name>oozie.service.PurgeService.workflow.retention</name>
  <value>30</value>  <!-- days -->
</property>
<property>
  <name>oozie.service.PurgeService.coordinator.retention</name>
  <value>60</value>
</property>
```

---

## Chapter 9: Advanced Topics

### Oozie CLI

#### Workflow Operations

```bash
OOZIE=http://oozie-server:11000/oozie

# Submit and run a job
oozie job -oozie $OOZIE -config job.properties -run

# Submit without running (PREP state)
oozie job -oozie $OOZIE -config job.properties -submit

# Start a submitted job
oozie job -oozie $OOZIE -start <job-id>

# Check job info
oozie job -oozie $OOZIE -info <job-id>

# List recent jobs
oozie jobs -oozie $OOZIE -jobtype wf -status RUNNING

# Suspend / resume
oozie job -oozie $OOZIE -suspend <job-id>
oozie job -oozie $OOZIE -resume <job-id>

# Kill
oozie job -oozie $OOZIE -kill <job-id>

# Rerun a workflow from a specific action
oozie job -oozie $OOZIE -rerun <job-id> -config job.properties -action action-name

# View job log
oozie job -oozie $OOZIE -log <job-id>
oozie job -oozie $OOZIE -log <job-id> -action action-name
```

#### Admin Operations

```bash
# Server status
oozie admin -oozie $OOZIE -status

# List system properties
oozie admin -oozie $OOZIE -configuration

# Instrumentation metrics
oozie admin -oozie $OOZIE -instrumentation

# Shared library list
oozie admin -oozie $OOZIE -shareliblist

# Update shared library (after uploading new JARs)
oozie admin -oozie $OOZIE -sharelibupdate
```

---

### Oozie REST API

All CLI operations have REST equivalents. The base URL is `http://oozie:11000/oozie/v2/`.

| Operation | Method | Endpoint |
|-----------|--------|---------|
| Submit job | POST | `/jobs?action=start` with XML body |
| Job info | GET | `/job/<job-id>` |
| Job log | GET | `/job/<job-id>?show=log` |
| Suspend | PUT | `/job/<job-id>?action=suspend` |
| Resume | PUT | `/job/<job-id>?action=resume` |
| Kill | PUT | `/job/<job-id>?action=kill` |
| List jobs | GET | `/jobs?jobtype=wf&status=RUNNING` |
| Server status | GET | `/admin/status` |

**Submit a workflow via REST:**

```bash
curl -X POST "http://oozie:11000/oozie/v2/jobs?action=start" \
     -H "Content-Type: application/xml;charset=UTF-8" \
     -d @job-config.xml
```

---

### Monitoring and Observability

#### Oozie Web UI

Access at `http://oozie-server:11000/oozie`. Shows:
- All running/recent workflow, coordinator, and bundle jobs
- Per-job action timelines and status
- Log access per action
- Console output per action

#### Instrumentation and Metrics

Oozie exposes metrics via the admin endpoint:

```bash
oozie admin -oozie http://oozie:11000/oozie -instrumentation
```

Key metrics to monitor:
- `jpa.GET_WORKFLOW` — database read latency
- `jpa.UPDATE_WORKFLOW` — database write latency
- `action.executors.*` — per-action-type execution counts and durations
- `callbackQueue.*` — queue depth for Hadoop callbacks

#### JMS-Based Monitoring

Configure JMS to receive real-time job status events:

```xml
<!-- oozie-site.xml -->
<property>
  <name>oozie.jms.producer.connection.factory</name>
  <value>ConnectionFactory</value>
</property>
<property>
  <name>oozie.service.JMSTopicService.topic.name</name>
  <value>default:oozie.wf.${username}</value>
</property>
```

JMS events are emitted for job state transitions (RUNNING → SUCCEEDED, etc.), enabling external monitoring tools to react without polling.

---

### High Availability (HA)

Oozie HA runs multiple Oozie server instances behind a load balancer. They share the same relational database and coordinate via ZooKeeper.

```
                    Load Balancer
                   /             \
          Oozie Server 1    Oozie Server 2
                   \             /
                   ZooKeeper Ensemble
                         |
                    Shared Database (MySQL)
                         |
                      HDFS
```

#### Enabling HA

```xml
<!-- oozie-site.xml on all Oozie nodes -->
<property>
  <name>oozie.services.ext</name>
  <value>
    org.apache.oozie.service.ZKLocksService,
    org.apache.oozie.service.ZKXLogStreamingService,
    org.apache.oozie.service.ZKJobsConcurrencyService,
    org.apache.oozie.service.ZKUUIDService
  </value>
</property>
<property>
  <name>oozie.zookeeper.connection.string</name>
  <value>zk1:2181,zk2:2181,zk3:2181</value>
</property>
```

In HA mode, if an Oozie server fails mid-job, another server picks up the running jobs from the database and continues.

---

### Security (Kerberos)

#### Enabling Kerberos Authentication

```xml
<!-- oozie-site.xml -->
<property>
  <name>oozie.service.HadoopAccessorService.kerberos.enabled</name>
  <value>true</value>
</property>
<property>
  <name>local.realm</name>
  <value>EXAMPLE.COM</value>
</property>
<property>
  <name>oozie.service.HadoopAccessorService.keytab.file</name>
  <value>/etc/security/keytabs/oozie.service.keytab</value>
</property>
<property>
  <name>oozie.service.HadoopAccessorService.kerberos.principal</name>
  <value>oozie/oozie-host@EXAMPLE.COM</value>
</property>
```

#### User Impersonation (Proxyuser)

Oozie submits Hadoop jobs as the submitting user, not as the Oozie service user. This requires proxyuser configuration in `core-site.xml`:

```xml
<property>
  <name>hadoop.proxyuser.oozie.hosts</name>
  <value>*</value>
</property>
<property>
  <name>hadoop.proxyuser.oozie.groups</name>
  <value>*</value>
</property>
```

---

### JVM and Server Tuning

```bash
# CATALINA_OPTS in oozie-env.sh
export CATALINA_OPTS="-Xms1g -Xmx4g -XX:+UseG1GC -XX:MaxGCPauseMillis=200"
```

Key `oozie-site.xml` tuning properties:

| Property | Default | Recommendation |
|----------|---------|----------------|
| `oozie.service.CallbackService.early.requeue.max.retries` | 3 | Increase for slow clusters |
| `oozie.service.coord.normal.default.timeout` | 120 | Minutes to wait for data (per coordinator) |
| `oozie.service.JPAService.pool.max.active.conn` | 10 | Increase for high concurrency |
| `oozie.service.ActionService.executor.extension.classes` | — | Register custom action executors |

---

### Debugging Common Errors

#### Job Stuck in RUNNING

1. Check Oozie logs: `oozie job -log <job-id>`
2. Check the YARN application logs for the launcher job: `yarn logs -applicationId <app-id>`
3. Verify the callback URL is reachable from YARN nodes to the Oozie server

#### Action Keeps Failing with "Launcher ERROR"

- Check launcher job logs in YARN
- Verify the application JARs are on HDFS under `lib/`
- Run `oozie admin -shareliblist` to confirm shared libs are present
- Check `oozie-site.xml` for correct `nameNode` and `jobTracker` values

#### Coordinator Action Stuck in WAITING

- The dataset's `_SUCCESS` file or HCatalog partition does not exist yet
- Check `<timeout>` — if exceeded, action goes to `TIMEDOUT`
- Use `oozie job -info <coord-job-id>@<action-num>` to see missing dependencies

#### Common Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| `E0501: App does not exist` | Application path not found on HDFS | Upload app to HDFS, check path |
| `E0900: Could not load action XML` | workflow.xml schema error | Validate XML against schema |
| `JA018: sub-workflow app path...` | Sub-workflow path wrong | Check app-path in sub-workflow action |
| `Action type [xxx] is not supported` | Missing action extension JAR | Add JAR to shared lib or `lib/` |
| `Permission denied` | Kerberos/proxyuser issue | Check proxyuser config, keytab |
