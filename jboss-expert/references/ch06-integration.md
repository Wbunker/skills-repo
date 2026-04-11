# Ch 6 — Integrating Applications with JBoss Fuse / Apache Camel

> **Book context:** Covered JBoss Fuse 6.x which was OSGi-based (Apache ServiceMix/Karaf). Current state:
> - **Red Hat Fuse 7.x** is Spring Boot based (no more OSGi/Karaf requirement)
> - **Camel K** is the Kubernetes-native operator-based approach
> - **Apache Camel 4.x** is the community project (used standalone or embedded in Spring Boot / Quarkus)
> - JBoss AMQ messaging is now **AMQ Broker** (ActiveMQ Artemis) and **AMQ Streams** (Kafka/Strimzi)

## Apache Camel Architecture

Camel implements **Enterprise Integration Patterns (EIP)** with a DSL for building message routes.

```
┌──────────────────────────────────────────────────────────────┐
│                    APACHE CAMEL ROUTE                        │
│                                                              │
│  from(source)                                                │
│       │                                                      │
│       ▼                                                      │
│  ┌─────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐  │
│  │Consumer │──▶│ Processor│──▶│ Processor│──▶│ Producer │  │
│  │(Endpoint│   │(Transform│   │(Filter,  │   │(Endpoint)│  │
│  │ URI)    │   │ Enrich)  │   │ Route)   │   │  URI)    │  │
│  └─────────┘   └──────────┘   └──────────┘   └──────────┘  │
│                                                              │
│  Exchange flows through: InMessage → [processing] → OutMessage│
└──────────────────────────────────────────────────────────────┘
```

## Camel 4.x — Route DSL

### Java DSL

```java
@ApplicationScoped
public class OrderRoutes extends RouteBuilder {

    @Override
    public void configure() throws Exception {

        // Error handling
        errorHandler(deadLetterChannel("jms:queue:DLQ")
            .maximumRedeliveries(3)
            .redeliveryDelay(1000)
            .useExponentialBackOff());

        // Simple file → JMS route
        from("file:orders/incoming?noop=true&consumer.delay=5000")
            .routeId("file-to-jms")
            .log("Processing order file: ${header.CamelFileName}")
            .unmarshal().json(Order.class)
            .validate(body().isNotNull())
            .to("jms:queue:orders");

        // JMS → transform → REST
        from("jms:queue:orders")
            .routeId("order-processor")
            .unmarshal().json(Order.class)
            .process(exchange -> {
                Order order = exchange.getIn().getBody(Order.class);
                order.setStatus("PROCESSED");
                exchange.getIn().setBody(order);
            })
            .marshal().json()
            .to("rest:post:http://inventory-service/api/orders");

        // Content-Based Router (EIP)
        from("jms:queue:incoming-orders")
            .choice()
                .when(simple("${body.type} == 'STANDARD'"))
                    .to("direct:standardOrder")
                .when(simple("${body.type} == 'EXPRESS'"))
                    .to("direct:expressOrder")
                .otherwise()
                    .to("direct:unknownOrder")
            .end();
    }
}
```

### YAML DSL (Camel K / modern)

```yaml
# order-route.yaml
- route:
    id: file-processor
    from:
      uri: "file:orders/incoming"
      parameters:
        noop: true
    steps:
      - log:
          message: "Processing: ${header.CamelFileName}"
      - unmarshal:
          json: {}
      - to:
          uri: "jms:queue:orders"
```

## Common Camel Components

| Component | URI Scheme | Use Case |
|-----------|-----------|---------|
| File | `file:path` | Read/write files |
| JMS | `jms:queue:name` | JMS messaging |
| Kafka | `kafka:topic` | Kafka producer/consumer |
| HTTP | `http:host/path` | HTTP calls |
| REST | `rest:method:path` | REST with OpenAPI |
| JDBC | `jdbc:datasource` | SQL queries |
| JPA | `jpa:Entity` | JPA operations |
| Timer | `timer:name?period=1000` | Scheduled polling |
| Direct | `direct:name` | In-VM synchronous |
| SEDA | `seda:name` | In-VM async (queued) |
| AMQP | `amqp:queue:name` | AMQP protocol |
| FTP/SFTP | `ftp://host/path` | FTP file transfer |
| Mail | `imap://host` | Email |
| XSLT | `xslt:transform.xsl` | XML transformation |
| Bean | `bean:beanName` | Invoke CDI/Spring bean |

## Enterprise Integration Patterns (EIP)

### Message Router

```java
// Content-Based Router
.choice()
    .when(header("type").isEqualTo("A")).to("direct:processA")
    .when(header("type").isEqualTo("B")).to("direct:processB")
    .otherwise().to("direct:processDefault");

// Dynamic Router
.dynamicRouter(method(DynamicRouterBean.class, "route"));

// Recipient List
.recipientList(header("destinations").tokenize(","));
```

### Message Transformer

```java
// Simple transform
.transform(simple("Hello ${body}"))

// Bean transform
.bean(TransformerBean.class, "transform")

// Marshal/Unmarshal
.marshal().json()        // Object → JSON string
.unmarshal().json(Foo.class)  // JSON string → Object
.marshal().csv()
.marshal().jaxb()        // Object → XML
```

### Aggregator

```java
from("jms:queue:parts")
    .aggregate(header("orderId"), new GroupedBodyAggregationStrategy())
    .completionSize(3)              // aggregate 3 messages
    .completionTimeout(5000)        // or after 5 seconds
    .to("direct:assembleOrder");
```

### Splitter

```java
from("direct:bulkOrder")
    .split(body().tokenize(","))   // split CSV
        .parallelProcessing()
        .to("jms:queue:single-orders")
    .end();
```

### Enricher

```java
from("direct:getOrder")
    .enrich("direct:getCustomerDetails",
            (original, resource) -> {
                original.getIn().setHeader("customer",
                    resource.getIn().getBody());
                return original;
            });
```

## AMQ Broker (ActiveMQ Artemis)

AMQ Broker replaces the old HornetQ in WildFly.

### WildFly Messaging Configuration

```xml
<subsystem xmlns="urn:jboss:domain:messaging-activemq:14.0">
  <server name="default">
    <security-setting name="#">
      <role name="guest" send="true" consume="true" create-non-durable-queue="true"/>
    </security-setting>

    <address-setting name="#" dead-letter-address="jms.queue.DLQ"
                     expiry-address="jms.queue.ExpiryQueue"
                     max-delivery-attempts="3"
                     redelivery-delay="1000"
                     max-size-bytes="10485760"
                     message-counter-history-day-limit="10"/>

    <http-connector name="http-connector" socket-binding="http"
                    endpoint="http-acceptor"/>
    <http-acceptor name="http-acceptor" http-listener="default"/>

    <jms-queue name="OrderQueue" entries="java:jboss/exported/jms/queue/OrderQueue"/>
    <jms-queue name="DLQ" entries="java:jboss/exported/jms/queue/DLQ"/>
    <jms-topic name="OrderEvents" entries="java:jboss/exported/jms/topic/OrderEvents"/>

    <connection-factory name="RemoteConnectionFactory"
                        connectors="http-connector"
                        entries="java:jboss/exported/jms/RemoteConnectionFactory"/>
    <pooled-connection-factory name="activemq-ra"
                               transaction="xa"
                               connectors="in-vm"
                               entries="java:/JmsXA java:jboss/DefaultJMSConnectionFactory"/>
  </server>
</subsystem>
```

### JMS Producer

```java
@Stateless
public class OrderPublisher {

    @Inject
    @JMSConnectionFactory("java:/JmsXA")
    private JMSContext context;

    @Resource(lookup = "java:jboss/exported/jms/queue/OrderQueue")
    private Destination orderQueue;

    public void publishOrder(Order order) {
        context.createProducer()
            .setProperty("orderType", order.getType())
            .setDeliveryMode(DeliveryMode.PERSISTENT)
            .setTimeToLive(TimeUnit.HOURS.toMillis(24))
            .send(orderQueue, order);
    }
}
```

### Message-Driven Bean (Consumer)

```java
@MessageDriven(activationConfig = {
    @ActivationConfigProperty(
        propertyName = "destinationLookup",
        propertyValue = "java:jboss/exported/jms/queue/OrderQueue"),
    @ActivationConfigProperty(
        propertyName = "destinationType",
        propertyValue = "jakarta.jms.Queue"),
    @ActivationConfigProperty(
        propertyName = "messageSelector",
        propertyValue = "orderType = 'STANDARD'")
})
public class OrderProcessor implements MessageListener {

    @Inject private OrderService orderService;

    @Override
    public void onMessage(Message message) {
        try {
            Order order = message.getBody(Order.class);
            orderService.process(order);
        } catch (JMSException e) {
            throw new RuntimeException(e);
        }
    }
}
```

## AMQ Streams (Apache Kafka / Strimzi)

AMQ Streams is Red Hat's distribution of Strimzi for Kafka on Kubernetes.

### Kafka Producer (MicroProfile Reactive Messaging)

```java
@ApplicationScoped
public class OrderProducer {

    @Channel("orders-out")
    Emitter<Order> emitter;

    public void sendOrder(Order order) {
        emitter.send(
            Message.of(order)
                .addMetadata(OutgoingKafkaRecordMetadata.<String>builder()
                    .withKey(order.getId().toString())
                    .withTopic("orders")
                    .withHeaders(new RecordHeaders()
                        .add("type", order.getType().getBytes()))
                    .build())
        );
    }
}
```

### Kafka Consumer

```java
@ApplicationScoped
public class OrderConsumer {

    @Incoming("orders-in")
    @Acknowledgment(Acknowledgment.Strategy.MANUAL)
    public CompletionStage<Void> processOrder(Message<Order> message) {
        Order order = message.getPayload();
        // process...
        return message.ack();
    }
}
```

`microprofile-config.properties`:
```properties
mp.messaging.outgoing.orders-out.connector=smallrye-kafka
mp.messaging.outgoing.orders-out.topic=orders
mp.messaging.outgoing.orders-out.bootstrap.servers=kafka:9092
mp.messaging.outgoing.orders-out.value.serializer=io.quarkus.kafka.client.serialization.ObjectMapperSerializer

mp.messaging.incoming.orders-in.connector=smallrye-kafka
mp.messaging.incoming.orders-in.topic=orders
mp.messaging.incoming.orders-in.group.id=order-consumer-group
mp.messaging.incoming.orders-in.bootstrap.servers=kafka:9092
```

## Camel K (Kubernetes-Native)

Camel K runs Camel routes as Kubernetes resources without a full application server.

```bash
# Install Camel K operator
kubectl apply -f https://github.com/apache/camel-k/releases/latest/download/camel-k.yaml

# Run a route directly from file
kamel run order-route.yaml

# Run with dependencies
kamel run route.java --dependency camel:jackson --dependency camel:kafka
```

## Integration Pattern Selection

```
What are you integrating?
├── Files (FTP, local, S3) → Camel file/ftp/aws-s3 components
├── Databases → Camel JDBC/JPA, or direct JPA in EJB
├── REST services → Camel HTTP/REST, or MicroProfile REST Client
├── SOAP services → Camel CXF component
├── JMS messaging → AMQ Broker + Camel JMS, or MDB
├── Kafka streaming → AMQ Streams + Camel Kafka, or MicroProfile Reactive
└── Complex orchestration (multiple systems) → Apache Camel routes

How is it deployed?
├── Part of WildFly app → Camel embedded (camel-core dependency)
├── Kubernetes → Camel K operator
├── Spring Boot microservice → Red Hat Fuse 7.x Spring Boot
└── On-premises standalone → Red Hat Fuse 7.x (Karaf for legacy)
```
