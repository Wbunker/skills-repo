# Ch 9 — Developing Workflows (jBPM / Process Automation)

> **Book context:** Covered JBoss BPM Suite. Current state:
> - Community project: **jBPM 7/8** (KIE platform, same as Drools)
> - Enterprise product: **Red Hat Process Automation Manager (PAM)** → migrating to **Red Hat Openshift Process Services (RHPAM)**
> - Cloud-native: **Kogito** (Quarkus/Spring Boot based process engine)
> - Standard: **BPMN 2.0** for process modeling, **CMMN** for adaptive case management, **DMN** for embedded decisions

## jBPM Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      jBPM ARCHITECTURE                          │
│                                                                  │
│  Process Sources (BPMN 2.0 XML):                                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                 │
│  │  Process   │  │   Human    │  │  Decision  │                 │
│  │ Definition │  │   Tasks    │  │  (DMN)     │                 │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘                 │
│        └───────────────┴────────────────┘                        │
│                         │                                        │
│                         ▼                                        │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                    KIE Container                           │  │
│  │  ProcessRuntime → RuntimeManager → RuntimeEngine           │  │
│  └────────────────────────────────────────────────────────────┘  │
│                         │                                        │
│  ┌──────────┐  ┌────────┴────────┐  ┌────────────┐              │
│  │ Process  │  │  Human Task     │  │  Persistence│              │
│  │ Instance │  │  Service        │  │  (JPA/DB)  │              │
│  └──────────┘  └─────────────────┘  └────────────┘              │
└──────────────────────────────────────────────────────────────────┘
```

## BPMN 2.0 Elements

### Flow Objects

| Element | Symbol | Purpose |
|---------|--------|---------|
| Start Event | ○ | Triggers process start |
| End Event | ⬤ | Terminates process |
| User Task | ☐ (person) | Manual task assigned to human |
| Service Task | ☐ (gear) | Automated, calls Java/REST |
| Script Task | ☐ (paper) | Runs inline code |
| Exclusive Gateway | ◇ (X) | Conditional branching (one path) |
| Parallel Gateway | ◇ (+) | Split/join parallel flows |
| Inclusive Gateway | ◇ (O) | Multiple conditional paths |
| Intermediate Event | ◎ | Wait, timer, signal, error |
| Subprocess | ☐ + | Embedded or reusable subprocess |
| Call Activity | ☐ thick | Call another process |

## BPMN 2.0 XML Process Definition

```xml
<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"
             xmlns:tns="http://www.example.com/processes"
             targetNamespace="http://www.example.com/processes">

  <process id="order-approval" name="Order Approval" isExecutable="true">

    <!-- Process variables -->
    <property id="orderId" itemSubjectRef="tns:orderId"/>
    <property id="approvalStatus" itemSubjectRef="tns:approvalStatus"/>

    <!-- Start Event -->
    <startEvent id="start" name="Order Submitted">
      <outgoing>flow1</outgoing>
    </startEvent>

    <!-- Automatic validation service task -->
    <serviceTask id="validateOrder" name="Validate Order"
                 implementation="Java"
                 operationRef="tns:validateOrderOp">
      <incoming>flow1</incoming>
      <outgoing>flow2</outgoing>
    </serviceTask>

    <!-- Exclusive Gateway: check validation result -->
    <exclusiveGateway id="validationCheck" name="Valid?">
      <incoming>flow2</incoming>
      <outgoing>flow3</outgoing>  <!-- valid -->
      <outgoing>flow4</outgoing>  <!-- invalid -->
    </exclusiveGateway>

    <!-- Human Task: manager approval -->
    <userTask id="managerApproval" name="Manager Approval">
      <incoming>flow3</incoming>
      <outgoing>flow5</outgoing>
      <potentialOwner>
        <resourceAssignmentExpression>
          <formalExpression>group(Managers)</formalExpression>
        </resourceAssignmentExpression>
      </potentialOwner>
    </userTask>

    <!-- End events -->
    <endEvent id="approved" name="Order Approved">
      <incoming>flow5</incoming>
    </endEvent>
    <endEvent id="rejected" name="Order Rejected">
      <incoming>flow4</incoming>
    </endEvent>

    <!-- Sequence Flows -->
    <sequenceFlow id="flow1" sourceRef="start" targetRef="validateOrder"/>
    <sequenceFlow id="flow2" sourceRef="validateOrder" targetRef="validationCheck"/>
    <sequenceFlow id="flow3" sourceRef="validationCheck" targetRef="managerApproval">
      <conditionExpression>#{valid == true}</conditionExpression>
    </sequenceFlow>
    <sequenceFlow id="flow4" sourceRef="validationCheck" targetRef="rejected">
      <conditionExpression>#{valid == false}</conditionExpression>
    </sequenceFlow>
    <sequenceFlow id="flow5" sourceRef="managerApproval" targetRef="approved"/>
  </process>
</definitions>
```

## jBPM Java API

### RuntimeManager Setup (with persistence)

```java
@ApplicationScoped
public class ProcessEngineConfig {

    @Inject private EntityManagerFactory emf;

    @Produces @ApplicationScoped
    public RuntimeManager runtimeManager() {
        RuntimeEnvironment env = RuntimeEnvironmentBuilder.Factory.get()
            .newDefaultBuilder()
            .entityManagerFactory(emf)
            .addAsset(
                ResourceFactory.newClassPathResource("processes/order-approval.bpmn2"),
                ResourceType.BPMN2
            )
            .addAsset(
                ResourceFactory.newClassPathResource("rules/approval-rules.drl"),
                ResourceType.DRL
            )
            .get();

        // Strategies: SINGLETON, PER_REQUEST, PER_PROCESS_INSTANCE
        return RuntimeManagerFactory.Factory.get()
            .newSingletonRuntimeManager(env, "order-approval");
    }
}
```

### Starting a Process Instance

```java
@Stateless
public class OrderWorkflowService {

    @Inject private RuntimeManager runtimeManager;

    public Long startOrderApproval(Order order) {
        RuntimeEngine engine = runtimeManager.getRuntimeEngine(
            ProcessInstanceIdContext.get()
        );
        KieSession session = engine.getKieSession();

        try {
            // Process variables
            Map<String, Object> variables = new HashMap<>();
            variables.put("orderId", order.getId());
            variables.put("orderTotal", order.getTotal());
            variables.put("customerType", order.getCustomer().getType());

            // Start process
            ProcessInstance instance = session.startProcess(
                "order-approval", variables
            );

            return instance.getId();

        } finally {
            runtimeManager.disposeRuntimeEngine(engine);
        }
    }

    public ProcessInstance getStatus(Long instanceId) {
        RuntimeEngine engine = runtimeManager.getRuntimeEngine(
            ProcessInstanceIdContext.get(instanceId)
        );
        try {
            return engine.getKieSession()
                .getProcessInstance(instanceId);
        } finally {
            runtimeManager.disposeRuntimeEngine(engine);
        }
    }
}
```

### Human Task Service

```java
@Stateless
public class TaskService {

    @Inject private RuntimeManager runtimeManager;

    public List<TaskSummary> getTasksForUser(String userId) {
        RuntimeEngine engine = runtimeManager.getRuntimeEngine(
            EmptyContext.get()
        );
        try {
            org.kie.api.task.TaskService taskService = engine.getTaskService();
            return taskService.getTasksAssignedAsPotentialOwner(
                userId, "en-UK"
            );
        } finally {
            runtimeManager.disposeRuntimeEngine(engine);
        }
    }

    public void claimAndCompleteTask(Long taskId, String userId,
                                     Map<String, Object> results) {
        RuntimeEngine engine = runtimeManager.getRuntimeEngine(
            EmptyContext.get()
        );
        try {
            org.kie.api.task.TaskService taskService = engine.getTaskService();

            // Claim from group
            taskService.claim(taskId, userId);

            // Start working on it
            taskService.start(taskId, userId);

            // Complete with output variables
            taskService.complete(taskId, userId, results);

        } finally {
            runtimeManager.disposeRuntimeEngine(engine);
        }
    }

    public void delegateTask(Long taskId, String fromUser, String toUser) {
        // ...
        taskService.delegate(taskId, fromUser, toUser);
    }
}
```

## Service Task (Work Item Handler)

Service tasks are implemented as `WorkItemHandler`:

```java
public class SendEmailHandler implements WorkItemHandler {

    @Inject private MailService mailService;

    @Override
    public void executeWorkItem(WorkItem workItem, WorkItemManager manager) {
        String to = (String) workItem.getParameter("To");
        String subject = (String) workItem.getParameter("Subject");
        String body = (String) workItem.getParameter("Body");

        try {
            mailService.send(to, subject, body);

            // Signal completion (with output params if needed)
            Map<String, Object> results = new HashMap<>();
            results.put("status", "sent");
            manager.completeWorkItem(workItem.getId(), results);

        } catch (Exception e) {
            manager.abortWorkItem(workItem.getId());
        }
    }

    @Override
    public void abortWorkItem(WorkItem workItem, WorkItemManager manager) {
        manager.abortWorkItem(workItem.getId());
    }
}

// Registration in process engine setup:
session.getWorkItemManager().registerWorkItemHandler(
    "Send Email", new SendEmailHandler()
);
```

## Timer Events

```xml
<!-- Boundary timer on user task (escalation after 24h) -->
<boundaryEvent id="approvalTimer" attachedToRef="managerApproval" cancelActivity="false">
  <timerEventDefinition>
    <timeDuration>PT24H</timeDuration>  <!-- ISO 8601 -->
  </timerEventDefinition>
  <outgoing>escalationFlow</outgoing>
</boundaryEvent>

<!-- Cycle timer: every hour -->
<timerEventDefinition>
  <timeCycle>R/PT1H</timeCycle>
</timerEventDefinition>

<!-- Specific date -->
<timerEventDefinition>
  <timeDate>2026-12-31T23:59:00</timeDate>
</timerEventDefinition>
```

## Signal and Message Events

```java
// Send signal to all process instances
session.signalEvent("OrderCancelled", orderId);

// Send signal to specific instance
session.signalEvent("OrderCancelled", orderId, processInstanceId);

// In BPMN: receive with IntermediateCatchEvent using SignalEventDefinition
```

## Process Variables and Data Mapping

```xml
<!-- Data object in process -->
<dataObject id="order" name="order" itemSubjectRef="tns:orderType"/>

<!-- I/O for user task -->
<userTask id="reviewTask">
  <ioSpecification>
    <dataInput id="orderIn" name="order" itemSubjectRef="tns:orderType"/>
    <dataOutput id="commentOut" name="comment" itemSubjectRef="tns:stringType"/>
  </ioSpecification>
  <dataInputAssociation>
    <sourceRef>order</sourceRef>
    <targetRef>orderIn</targetRef>
  </dataInputAssociation>
  <dataOutputAssociation>
    <sourceRef>commentOut</sourceRef>
    <targetRef>reviewComment</targetRef>
  </dataOutputAssociation>
</userTask>
```

## KIE Server — Process REST API

```bash
# Start process instance
curl -X POST \
  "http://kie-server:8080/kie-server/services/rest/server/containers/order-processes/processes/order-approval/instances" \
  -H "Content-Type: application/json" \
  -u user:password \
  -d '{"variables": {"orderId": {"value": "123", "type": "Long"}}}'

# Get process instance
curl "http://kie-server:8080/kie-server/services/rest/server/containers/order-processes/processes/instances/1" \
  -u user:password

# Get tasks for user
curl "http://kie-server:8080/kie-server/services/rest/server/queries/tasks/instances/pot-owners?user=john" \
  -u user:password

# Complete task
curl -X PUT \
  "http://kie-server:8080/kie-server/services/rest/server/containers/order-processes/tasks/5/states/completed" \
  -H "Content-Type: application/json" \
  -u user:password \
  -d '{"approvalStatus": {"value": "APPROVED", "type": "String"}}'
```

## Kogito (Cloud-Native Processes)

For new Kubernetes-native projects:

```xml
<!-- pom.xml -->
<dependency>
  <groupId>org.kie.kogito</groupId>
  <artifactId>kogito-quarkus</artifactId>
</dependency>
```

BPMN2 files in `src/main/resources/` are auto-compiled and exposed as REST endpoints:
- `POST /order-approval` — start process
- `GET /order-approval` — list all instances
- `GET /order-approval/{id}` — get instance
- `GET /order-approval/{id}/tasks` — get human tasks

## Workflow Pattern Decision Tree

```
What type of workflow do you need?
├── Sequential steps with human approval → BPMN user tasks + service tasks
├── Parallel work streams → Parallel gateways (fork/join)
├── Rules-driven routing → Exclusive/inclusive gateways + DMN
├── Long-running, waiting for events → Intermediate catch events (signal/message/timer)
├── Case management (flexible, ad-hoc) → CMMN (Case Management Model and Notation)
└── Short-lived, stateless orchestration → Microservices choreography (Kafka + Camel)

What deployment model?
├── Embedded in WildFly/EJB app → RuntimeManager + KIE API
├── Standalone service → KIE Server (REST/JMS)
├── Kubernetes native → Kogito on Quarkus
└── Business user self-service → Business Central (KIE Workbench)
```

## Persistence Configuration for jBPM

jBPM persists process state to a database via JPA:

```xml
<!-- persistence.xml for jBPM -->
<persistence-unit name="org.jbpm.persistence.jpa" transaction-type="JTA">
  <provider>org.hibernate.jpa.HibernatePersistenceProvider</provider>
  <jta-data-source>java:jboss/datasources/jbpmDS</jta-data-source>

  <!-- jBPM managed entities -->
  <class>org.drools.persistence.info.SessionInfo</class>
  <class>org.jbpm.persistence.processinstance.ProcessInstanceInfo</class>
  <class>org.drools.persistence.info.WorkItemInfo</class>
  <class>org.jbpm.persistence.correlation.CorrelationKeyInfo</class>
  <class>org.jbpm.persistence.correlation.CorrelationPropertyInfo</class>
  <!-- Human task entities -->
  <class>org.jbpm.services.task.impl.model.TaskImpl</class>
  <class>org.jbpm.services.task.impl.model.ContentImpl</class>
  <!-- ... other jBPM entities ... -->

  <properties>
    <property name="hibernate.dialect" value="org.hibernate.dialect.PostgreSQLDialect"/>
    <property name="hibernate.hbm2ddl.auto" value="update"/>
    <property name="hibernate.show_sql" value="false"/>
  </properties>
</persistence-unit>
```
