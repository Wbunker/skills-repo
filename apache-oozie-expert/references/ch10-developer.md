# Ch 10 — Developer Topics

## Table of Contents
- [Custom EL Functions](#custom-el-functions)
- [Custom Action Executor](#custom-action-executor)
- [Error Types](#error-types)
- [Deployment](#deployment)

---

## Custom EL Functions

EL functions are static Java methods exposed under a namespace prefix.

### Implementation

```java
package org.example.oozie;

public class MyELFunctions {
    // Must be static, return String/boolean/int/long/float/double
    public static String toUpperCase(String s) {
        return s == null ? "" : s.toUpperCase();
    }

    public static boolean isWeekend(String isoDate) {
        // parse isoDate, check day of week
        ...
    }
}
```

### EL Function Definition File

`my-el-functions.properties` (place on Oozie classpath or in ext dir):
```properties
#EL constant function definitions
my:toUpperCase=org.example.oozie.MyELFunctions#toUpperCase
my:isWeekend=org.example.oozie.MyELFunctions#isWeekend
```

### Registration in oozie-site.xml

```xml
<property>
  <name>oozie.service.ELService.ext.functions.workflow</name>
  <value>my:toUpperCase=org.example.oozie.MyELFunctions#toUpperCase,
         my:isWeekend=org.example.oozie.MyELFunctions#isWeekend</value>
</property>
<!-- For coordinator EL: -->
<property>
  <name>oozie.service.ELService.ext.functions.coord-action-create</name>
  <value>my:toUpperCase=org.example.oozie.MyELFunctions#toUpperCase</value>
</property>
```

### Usage in workflow XML

```xml
<decision name="check-day">
  <switch>
    <case to="weekend-job">${my:isWeekend(coord:nominalTime())}</case>
    <default to="weekday-job"/>
  </switch>
</decision>
```

---

## Custom Action Executor

Implement `org.apache.oozie.action.ActionExecutor` for custom action types.

Two modes:
- **Synchronous**: `start()` completes the action and calls `context.setExecutionData()` immediately
- **Asynchronous**: `start()` submits external work and calls `context.setStartData()` with external ID; Oozie polls `check()` periodically

### Skeleton

```java
public class MyActionExecutor extends ActionExecutor {

    public MyActionExecutor() {
        super("my-action");  // must match XML element name
    }

    @Override
    public void initActionType() {
        super.initActionType();
        // Register error codes
        registerError(IOException.class.getName(),
            ActionExecutorException.ErrorType.TRANSIENT, "MY001");
        registerError(RuntimeException.class.getName(),
            ActionExecutorException.ErrorType.NON_TRANSIENT, "MY002");
    }

    @Override
    public void start(Context context, Action action) throws ActionExecutorException {
        // Parse action XML
        Element actionXml = XmlUtils.parseXml(action.getConf());

        // Option A — synchronous
        context.setExecutionData("COMPLETED", null);

        // Option B — asynchronous: submit external job
        String externalId = submitExternalJob(actionXml);
        context.setStartData(externalId, "http://tracker-uri", "http://console-url");
    }

    @Override
    public void check(Context context, Action action) throws ActionExecutorException {
        // Poll external system
        String status = checkExternalJob(action.getExternalId());
        if ("DONE".equals(status)) {
            context.setExecutionData("COMPLETED", null);
        }
        // If still running, just return — Oozie will call check() again
    }

    @Override
    public void kill(Context context, Action action) throws ActionExecutorException {
        killExternalJob(action.getExternalId());
        context.setEndData(Action.Status.KILLED, "KILLED");
    }

    @Override
    public void end(Context context, Action action) throws ActionExecutorException {
        String externalStatus = action.getExternalStatus();
        Action.Status status = "COMPLETED".equals(externalStatus)
            ? Action.Status.OK : Action.Status.ERROR;
        context.setEndData(status, externalStatus);
    }

    @Override
    public boolean isCompleted(String externalStatus) {
        return "COMPLETED".equals(externalStatus) || "FAILED".equals(externalStatus);
    }
}
```

### Context Methods

| Method | Meaning |
|--------|---------|
| `context.setStartData(id, trackerUri, consoleUrl)` | Mark action as launched (async) |
| `context.setExecutionData(externalStatus, data)` | Mark action execution complete |
| `context.setEndData(status, externalStatus)` | Finalize action (OK or ERROR) |
| `context.setVar(name, value)` | Store data for the workflow |
| `context.getProtoActionConf()` | Get Hadoop config for the action |

---

## Error Types

| Type | Meaning | Retry? |
|------|---------|--------|
| `TRANSIENT` | Temporary failure (network, resource unavailable) | Yes — retried per `retry-max` |
| `NON_TRANSIENT` | Permanent failure (bad input, wrong class) | No |
| `ERROR` | Action completed in error state | No |
| `FAILED` | Fatal internal failure | No |

---

## Deployment

1. Package custom code as a JAR
2. Place JAR in `${OOZIE_HOME}/libext/` (picked up at startup)
3. Register in `oozie-site.xml`:

```xml
<!-- Register action executor -->
<property>
  <name>oozie.service.ActionService.executor.ext.classes</name>
  <value>org.example.oozie.MyActionExecutor</value>
</property>

<!-- Register action XML schema (XSD) -->
<property>
  <name>oozie.service.WorkflowSchemaService.ext.schemas</name>
  <value>my-action-0.1.xsd</value>
</property>
```

4. Place XSD in `conf/` directory
5. Restart Oozie server

### Action XSD Example

```xml
<!-- my-action-0.1.xsd -->
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           xmlns="uri:my:my-action:0.1"
           elementFormDefault="qualified"
           targetNamespace="uri:my:my-action:0.1">
  <xs:element name="my-action">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="endpoint" type="xs:string"/>
        <xs:element name="param" type="xs:string" minOccurs="0" maxOccurs="unbounded"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>
```

### Usage in Workflow

```xml
<action name="custom">
  <my-action xmlns="uri:my:my-action:0.1">
    <endpoint>http://external-service/api</endpoint>
    <param>key=value</param>
  </my-action>
  <ok to="next"/>
  <error to="fail"/>
</action>
```
