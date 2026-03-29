# Workflow Actions
## Chapter 4: Oozie Workflow Actions

---

## Action Execution Model

All actions follow the same pattern in workflow XML:

```xml
<action name="step-name" [retry-max="3"] [retry-interval="2"]>
  <action-type xmlns="uri:oozie:<type>-action:X.Y">
    <!-- action-specific config -->
  </action-type>
  <ok to="next-node"/>
  <error to="error-handler"/>
</action>
```

Most actions are **asynchronous** — Oozie submits a launcher job to YARN, which runs the actual work. The launcher calls back to Oozie on completion.

---

## MapReduce Action

Runs a MapReduce job on the cluster.

```xml
<action name="mr-job">
  <map-reduce>
    <job-tracker>${jobTracker}</job-tracker>
    <name-node>${nameNode}</name-node>
    <configuration>
      <property>
        <name>mapred.mapper.class</name>
        <value>com.example.MyMapper</value>
      </property>
      <property>
        <name>mapred.reducer.class</name>
        <value>com.example.MyReducer</value>
      </property>
      <property>
        <name>mapred.input.dir</name>
        <value>${inputPath}</value>
      </property>
      <property>
        <name>mapred.output.dir</name>
        <value>${outputPath}</value>
      </property>
    </configuration>
  </map-reduce>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

For YARN (MR2), use:
```xml
<property><name>mapreduce.framework.name</name><value>yarn</value></property>
```

---

## Java Action

Runs an arbitrary Java `main()` method in a YARN container. Useful for custom logic that does not fit other action types.

```xml
<action name="java-job">
  <java>
    <job-tracker>${jobTracker}</job-tracker>
    <name-node>${nameNode}</name-node>
    <main-class>com.example.MyMain</main-class>
    <java-opts>-Xmx512m</java-opts>
    <arg>--input</arg>
    <arg>${inputPath}</arg>
    <arg>--output</arg>
    <arg>${outputPath}</arg>
    <file>/user/me/app/lib/my-app.jar#my-app.jar</file>
    <capture-output/>   <!-- capture System.setProperty output as action data -->
  </java>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

`<capture-output/>` allows the Java program to write key=value pairs to `${OOZIE_ACTION_OUTPUT_PROPS}`, which are then accessible via `${wf:actionData("java-job")["key"]}`.

---

## Hive Action

Runs a HiveQL script or inline query.

```xml
<action name="hive-job">
  <hive xmlns="uri:oozie:hive-action:0.5">
    <job-tracker>${jobTracker}</job-tracker>
    <name-node>${nameNode}</name-node>
    <job-xml>hive-site.xml</job-xml>
    <script>scripts/transform.hql</script>
    <param>INPUT=${inputPath}</param>
    <param>OUTPUT=${outputPath}</param>
  </hive>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

For HiveServer2 (Hive 2.x), use the `hive2` action type:

```xml
<action name="hive2-job">
  <hive2 xmlns="uri:oozie:hive2-action:0.1">
    <jdbc-url>jdbc:hive2://hiveserver:10000/default</jdbc-url>
    <script>scripts/query.hql</script>
    <param>DATE=${coord:nominalTime()}</param>
  </hive2>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

---

## Pig Action

Runs a Pig Latin script.

```xml
<action name="pig-job">
  <pig>
    <job-tracker>${jobTracker}</job-tracker>
    <name-node>${nameNode}</name-node>
    <script>scripts/process.pig</script>
    <param>INPUT=${inputPath}</param>
    <param>OUTPUT=${outputPath}</param>
    <argument>-useHCatalog</argument>
  </pig>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

---

## Spark Action

Runs a Spark application.

```xml
<action name="spark-job">
  <spark xmlns="uri:oozie:spark-action:0.2">
    <job-tracker>${jobTracker}</job-tracker>
    <name-node>${nameNode}</name-node>
    <master>yarn</master>
    <mode>cluster</mode>
    <name>MySparkApp</name>
    <class>com.example.SparkMain</class>
    <jar>${nameNode}/user/me/app/lib/spark-app.jar</jar>
    <spark-opts>--executor-memory 2g --num-executors 5</spark-opts>
    <arg>${inputPath}</arg>
    <arg>${outputPath}</arg>
  </spark>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

---

## Sqoop Action

Runs a Sqoop import or export.

```xml
<action name="sqoop-import">
  <sqoop xmlns="uri:oozie:sqoop-action:0.2">
    <job-tracker>${jobTracker}</job-tracker>
    <name-node>${nameNode}</name-node>
    <command>import --connect jdbc:mysql://db:3306/mydb \
      --username ${dbUser} --password ${dbPassword} \
      --table orders --target-dir ${outputPath} \
      --num-mappers 4</command>
  </sqoop>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

Alternatively, use `<arg>` elements instead of `<command>`:

```xml
<sqoop xmlns="uri:oozie:sqoop-action:0.2">
  <arg>import</arg>
  <arg>--connect</arg><arg>jdbc:mysql://db/mydb</arg>
  <arg>--table</arg><arg>orders</arg>
  <arg>--target-dir</arg><arg>${outputPath}</arg>
</sqoop>
```

---

## Shell Action

Runs a shell script or command on the Oozie server node (not on YARN). Use with caution — not suitable for heavy computation.

```xml
<action name="shell-step">
  <shell xmlns="uri:oozie:shell-action:0.3">
    <job-tracker>${jobTracker}</job-tracker>
    <name-node>${nameNode}</name-node>
    <exec>scripts/run.sh</exec>
    <argument>${inputPath}</argument>
    <env-var>MY_ENV=value</env-var>
    <file>scripts/run.sh#run.sh</file>
    <capture-output/>
  </shell>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

The `#run.sh` suffix in `<file>` is a symlink name — makes the file available as `run.sh` in the working directory.

---

## FS Action

Performs HDFS filesystem operations. Runs synchronously on the Oozie server (no YARN job).

```xml
<action name="prep-hdfs">
  <fs>
    <delete path="${outputPath}"/>
    <mkdir path="${outputPath}"/>
    <move source="${stagingPath}/data" target="${outputPath}/data"/>
    <chmod path="${outputPath}" permissions="-rwxr-xr-x" dir-files="true"/>
    <touchz path="${outputPath}/_SUCCESS"/>
  </fs>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

Available FS operations: `<delete>`, `<mkdir>`, `<move>`, `<chmod>`, `<chgrp>`, `<touchz>`, `<setrep>`.

---

## Email Action

Sends an email notification. Commonly used for success/failure alerts.

```xml
<action name="send-alert">
  <email xmlns="uri:oozie:email-action:0.1">
    <to>${alertEmail}</to>
    <cc>${teamEmail}</cc>
    <subject>Pipeline ${wf:name()} ${wf:id()} - FAILED</subject>
    <body>
      Workflow: ${wf:name()}
      Failed at: ${wf:lastErrorNode()}
      Error: ${wf:errorMessage(wf:lastErrorNode())}
    </body>
  </email>
  <ok to="fail"/>
  <error to="fail"/>
</action>
```

Requires SMTP configuration in `oozie-site.xml`:
```xml
<property><name>oozie.email.smtp.host</name><value>smtp.example.com</value></property>
<property><name>oozie.email.from.address</name><value>oozie@example.com</value></property>
```

---

## Sub-Workflow Action

Runs another Oozie workflow as a child. The parent waits for the child to complete.

```xml
<action name="run-subworkflow">
  <sub-workflow>
    <app-path>${nameNode}/user/me/child-workflow</app-path>
    <propagate-configuration/>   <!-- pass parent config to child -->
    <configuration>
      <property>
        <name>childInputPath</name>
        <value>${outputPath}</value>
      </property>
    </configuration>
  </sub-workflow>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

`<propagate-configuration/>` forwards the parent's job configuration to the child workflow.

---

## DistCp Action

Copies data between HDFS clusters (or within a cluster).

```xml
<action name="distcp-step">
  <distcp xmlns="uri:oozie:distcp-action:0.2">
    <job-tracker>${jobTracker}</job-tracker>
    <name-node>${nameNode}</name-node>
    <arg>${sourceCluster}/data/input</arg>
    <arg>${nameNode}/data/input</arg>
  </distcp>
  <ok to="next"/>
  <error to="fail"/>
</action>
```

---

## Library Management

JARs in the `lib/` subdirectory of the application path are **automatically added** to the classpath of all actions in that workflow.

For shared libraries used across workflows, configure `oozie.libpath` in `oozie-site.xml` or in `job.properties`:

```properties
oozie.libpath=${nameNode}/user/oozie/share/lib
oozie.use.system.libpath=true
```

The Oozie shared library (`/user/oozie/share/lib/`) contains standard libraries for Hive, Pig, Spark, Sqoop, etc. populated by `oozie-setup.sh sharelib create`.
