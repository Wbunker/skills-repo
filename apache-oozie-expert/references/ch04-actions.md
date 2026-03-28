# Ch 4 — Workflow Actions

## Table of Contents
- [Action Execution Model](#action-execution-model)
- [MapReduce Action](#mapreduce-action)
- [Java Action](#java-action)
- [Hive Action](#hive-action)
- [Pig Action](#pig-action)
- [Spark Action](#spark-action)
- [Shell Action](#shell-action)
- [FS Action](#fs-action)
- [Sub-Workflow Action](#sub-workflow-action)
- [DistCp Action](#distcp-action)
- [Sqoop Action](#sqoop-action)
- [Email Action](#email-action)
- [SSH Action](#ssh-action)
- [Error Handling & Retry](#error-handling--retry)
- [XML Namespace URIs](#xml-namespace-uris)

---

## Action Execution Model

- Actions run as YARN jobs (async) or launcher-only tasks (sync)
- Every action has `<ok to="..."/>` and `<error to="..."/>` transitions
- Oozie polls action status via the callback URL or periodic check
- `retry-max` and `retry-interval` on `<action>` override global defaults

---

## MapReduce Action

```xml
<action name="mr-action" retry-max="3" retry-interval="10">
  <map-reduce>
    <job-tracker>${jobTracker}</job-tracker>
    <name-node>${nameNode}</name-node>
    <prepare>
      <delete path="${outputDir}"/>
      <mkdir path="${outputDir}"/>
    </prepare>
    <configuration>
      <property><name>mapred.mapper.class</name><value>org.example.MyMapper</value></property>
      <property><name>mapred.reducer.class</name><value>org.example.MyReducer</value></property>
      <property><name>mapred.input.dir</name><value>${inputDir}</value></property>
      <property><name>mapred.output.dir</name><value>${outputDir}</value></property>
    </configuration>
  </map-reduce>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

**Streaming:**
```xml
<map-reduce>
  <job-tracker>${jobTracker}</job-tracker>
  <name-node>${nameNode}</name-node>
  <streaming>
    <mapper>/bin/cat</mapper>
    <reducer>/usr/bin/wc</reducer>
  </streaming>
  <configuration>
    <property><name>mapred.input.dir</name><value>${inputDir}</value></property>
    <property><name>mapred.output.dir</name><value>${outputDir}</value></property>
  </configuration>
</map-reduce>
```
Cannot mix `<streaming>` and `<pipes>` in one action.

---

## Java Action

Runs a Java main class as a single map task. Use for lightweight processing that doesn't need full MR.

```xml
<action name="java-action">
  <java>
    <job-tracker>${jobTracker}</job-tracker>
    <name-node>${nameNode}</name-node>
    <prepare>
      <delete path="${outputDir}"/>
    </prepare>
    <main-class>org.example.Main</main-class>
    <java-opts>-Xmx512m</java-opts>
    <arg>${inputPath}</arg>
    <arg>${outputPath}</arg>
    <file>${nameNode}/jars/helper.jar#helper.jar</file>
    <capture-output/>
  </java>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

- `<capture-output/>`: stdout written as Java Properties (`key=value` per line)
- Access captured output: `${wf:actionData('java-action')['key']}`
- Exit code 0 → ok; non-zero → error
- **Gotcha:** Hadoop may retry the map task even when Oozie doesn't. Make operations idempotent.

---

## Hive Action

```xml
<action name="hive-action">
  <hive xmlns="uri:oozie:hive-action:0.2">
    <job-tracker>${jobTracker}</job-tracker>
    <name-node>${nameNode}</name-node>
    <prepare>
      <delete path="${outputDir}"/>
    </prepare>
    <job-xml>${nameNode}/hive/hive-site.xml</job-xml>
    <script>queries/transform.hql</script>
    <param>INPUT=${inputDir}</param>
    <param>OUTPUT=${outputDir}</param>
  </hive>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

- Script path is relative to workflow app directory on HDFS
- `oozie.use.system.libpath=true` required in `job.properties`
- Use `<job-xml>` to specify hive-site.xml if metastore connection is needed

---

## Pig Action

```xml
<action name="pig-action">
  <pig>
    <job-tracker>${jobTracker}</job-tracker>
    <name-node>${nameNode}</name-node>
    <script>scripts/process.pig</script>
    <param>INPUT=${inputDir}</param>
    <param>OUTPUT=${outputDir}</param>
    <argument>-v</argument>
  </pig>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

---

## Spark Action

```xml
<action name="spark-action">
  <spark xmlns="uri:oozie:spark-action:0.1">
    <job-tracker>${jobTracker}</job-tracker>
    <name-node>${nameNode}</name-node>
    <master>yarn</master>
    <mode>cluster</mode>
    <name>MySparkJob</name>
    <class>org.example.SparkMain</class>
    <jar>${nameNode}/jars/myapp.jar</jar>
    <spark-opts>--executor-memory 4G --num-executors 10 --conf spark.eventLog.enabled=true --conf spark.eventLog.dir=hdfs:///spark-logs --conf spark.yarn.historyServer.address=history:18080</spark-opts>
    <arg>--input=${inputPath}</arg>
    <arg>--output=${outputPath}</arg>
  </spark>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

For Spark History Server: set `spark.eventLog.enabled=true`, `spark.eventLog.dir`, and `spark.yarn.historyServer.address`.

---

## Shell Action

```xml
<action name="shell-action">
  <shell xmlns="uri:oozie:shell-action:0.2">
    <job-tracker>${jobTracker}</job-tracker>
    <name-node>${nameNode}</name-node>
    <exec>run.sh</exec>
    <argument>--mode=production</argument>
    <argument>${inputPath}</argument>
    <env-var>MY_VAR=hello</env-var>
    <file>run.sh#run.sh</file>
    <capture-output/>
  </shell>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

- `<file>hdfs_path#local_name</file>` symlinks the file into the working directory
- `<capture-output/>` captures stdout as Java Properties
- Script must be executable or called via `bash run.sh`

---

## FS Action

HDFS file system operations. **Not atomic** — failure mid-sequence leaves partial state.

```xml
<action name="fs-action">
  <fs>
    <delete path="${workDir}/temp"/>
    <mkdir path="${workDir}/output"/>
    <move source="${workDir}/staging" target="${workDir}/final"/>
    <chmod path="${workDir}/output" permissions="-rwxr-xr-x" dir-files="true"/>
    <touchz path="${workDir}/done.flag"/>
    <chgrp path="${workDir}/output" group="hadoop" dir-files="true"/>
  </fs>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

Operations execute in document order. No YARN job is launched.

---

## Sub-Workflow Action

```xml
<action name="sub-wf">
  <sub-workflow>
    <app-path>${nameNode}/workflows/child-wf</app-path>
    <propagate-configuration/>
    <configuration>
      <property><name>childInput</name><value>${someVar}</value></property>
    </configuration>
  </sub-workflow>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

- `<propagate-configuration/>` passes parent config to child; without it child starts with empty config
- Child workflow runs with the same user as the parent

---

## DistCp Action

```xml
<action name="distcp-action">
  <distcp xmlns="uri:oozie:distcp-action:0.2">
    <job-tracker>${jobTracker}</job-tracker>
    <name-node>${nameNode}</name-node>
    <arg>-update</arg>
    <arg>-skipcrccheck</arg>
    <arg>hdfs://source-cluster/data/input</arg>
    <arg>hdfs://dest-cluster/data/output</arg>
  </distcp>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

---

## Sqoop Action

```xml
<action name="sqoop-action">
  <sqoop xmlns="uri:oozie:sqoop-action:0.4">
    <job-tracker>${jobTracker}</job-tracker>
    <name-node>${nameNode}</name-node>
    <command>import --connect jdbc:mysql://dbhost/mydb --table users --target-dir ${outputDir} --num-mappers 4</command>
  </sqoop>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

---

## Email Action

```xml
<action name="notify">
  <email xmlns="uri:oozie:email-action:0.2">
    <to>ops@example.com</to>
    <cc>team@example.com</cc>
    <subject>Job ${wf:name()} completed</subject>
    <body>Workflow ${wf:id()} finished at ${timestamp()}</body>
  </email>
  <ok to="end"/>
  <error to="fail"/>
</action>
```

Requires SMTP config in `oozie-site.xml`:
```xml
<property><name>oozie.email.smtp.host</name><value>smtp.example.com</value></property>
<property><name>oozie.email.smtp.port</name><value>25</value></property>
<property><name>oozie.email.from.address</name><value>oozie@example.com</value></property>
```

---

## SSH Action

```xml
<action name="ssh-action">
  <ssh xmlns="uri:oozie:ssh-action:0.1">
    <host>user@remotehost.example.com</host>
    <command>/bin/bash</command>
    <args>-c</args>
    <args>echo key=value</args>
    <capture-output/>
  </ssh>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

Oozie server must have passwordless SSH access to the target host.

---

## Error Handling & Retry

Per-action retry (overrides global oozie-site.xml defaults):
```xml
<action name="flaky-action" retry-max="5" retry-interval="30">
  <!-- retry-interval in minutes -->
  ...
</action>
```

Global defaults in `oozie-site.xml`:
```xml
<property><name>oozie.action.retries.max</name><value>3</value></property>
<property><name>oozie.action.retry.interval</name><value>10</value></property>
<property><name>oozie.action.retry.policy</name><value>periodic</value></property>
```

Error policy: `periodic` (fixed interval) or `exponential` (doubles each retry).

---

## XML Namespace URIs

| Action | Namespace |
|--------|-----------|
| Workflow | `uri:oozie:workflow:0.5` |
| Hive | `uri:oozie:hive-action:0.2` |
| Hive2 | `uri:oozie:hive2-action:0.1` |
| Spark | `uri:oozie:spark-action:0.1` |
| Shell | `uri:oozie:shell-action:0.2` |
| SSH | `uri:oozie:ssh-action:0.1` |
| Sqoop | `uri:oozie:sqoop-action:0.4` |
| DistCp | `uri:oozie:distcp-action:0.2` |
| Email | `uri:oozie:email-action:0.2` |
