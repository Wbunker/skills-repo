# Spring Boot 2.3 — Messaging

## RabbitMQ / Spring AMQP

### Dependency

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-amqp</artifactId>
</dependency>
```

### Configuration

```properties
spring.rabbitmq.host=localhost
spring.rabbitmq.port=5672
spring.rabbitmq.username=guest
spring.rabbitmq.password=guest
spring.rabbitmq.virtual-host=/

# Connection pool
spring.rabbitmq.listener.simple.concurrency=3
spring.rabbitmq.listener.simple.max-concurrency=10
spring.rabbitmq.listener.simple.prefetch=10
spring.rabbitmq.listener.simple.acknowledge-mode=auto
```

### Declare Exchange, Queue, Binding

```java
@Configuration
public class RabbitConfig {

    public static final String ORDER_EXCHANGE = "order.exchange";
    public static final String ORDER_QUEUE = "order.created.queue";
    public static final String ORDER_ROUTING_KEY = "order.created";

    @Bean
    public TopicExchange orderExchange() {
        return new TopicExchange(ORDER_EXCHANGE, true, false);
    }

    @Bean
    public Queue orderQueue() {
        return QueueBuilder.durable(ORDER_QUEUE)
            .withArgument("x-dead-letter-exchange", "order.dlx")
            .build();
    }

    @Bean
    public Binding orderBinding(Queue orderQueue, TopicExchange orderExchange) {
        return BindingBuilder.bind(orderQueue)
            .to(orderExchange)
            .with(ORDER_ROUTING_KEY);
    }

    // Dead letter queue
    @Bean
    public DirectExchange deadLetterExchange() {
        return new DirectExchange("order.dlx");
    }

    @Bean
    public Queue deadLetterQueue() {
        return QueueBuilder.durable("order.dlq").build();
    }

    // JSON message converter
    @Bean
    public MessageConverter jsonMessageConverter() {
        return new Jackson2JsonMessageConverter();
    }

    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory,
                                          MessageConverter messageConverter) {
        RabbitTemplate template = new RabbitTemplate(connectionFactory);
        template.setMessageConverter(messageConverter);
        return template;
    }
}
```

### Sending Messages

```java
@Service
public class OrderPublisher {

    private final RabbitTemplate rabbitTemplate;

    public OrderPublisher(RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }

    public void publishOrderCreated(OrderDto order) {
        rabbitTemplate.convertAndSend(
            RabbitConfig.ORDER_EXCHANGE,
            RabbitConfig.ORDER_ROUTING_KEY,
            order
        );
    }

    // With custom headers
    public void publishWithHeaders(OrderDto order) {
        rabbitTemplate.convertAndSend(
            RabbitConfig.ORDER_EXCHANGE,
            RabbitConfig.ORDER_ROUTING_KEY,
            order,
            message -> {
                message.getMessageProperties().setHeader("source", "api");
                message.getMessageProperties().setPriority(5);
                return message;
            }
        );
    }

    // Request/reply (RPC)
    public OrderConfirmation sendAndReceive(OrderDto order) {
        return (OrderConfirmation) rabbitTemplate.convertSendAndReceive(
            RabbitConfig.ORDER_EXCHANGE,
            RabbitConfig.ORDER_ROUTING_KEY,
            order
        );
    }
}
```

### Receiving Messages

```java
@Component
public class OrderListener {

    private static final Logger log = LoggerFactory.getLogger(OrderListener.class);

    @RabbitListener(queues = RabbitConfig.ORDER_QUEUE)
    public void handleOrderCreated(OrderDto order) {
        log.info("Received order: {}", order.getId());
        // process order
    }

    // With message metadata
    @RabbitListener(queues = RabbitConfig.ORDER_QUEUE)
    public void handleWithHeaders(OrderDto order,
                                  @Header("source") String source,
                                  @Headers Map<String, Object> headers,
                                  Message message) {
        log.info("From source: {}, correlationId: {}",
            source, message.getMessageProperties().getCorrelationId());
    }

    // Inline queue/exchange/binding declaration
    @RabbitListener(bindings = @QueueBinding(
        value = @Queue(value = "notification.queue", durable = "true"),
        exchange = @Exchange(value = "notification.exchange", type = ExchangeTypes.TOPIC),
        key = "notification.#"
    ))
    public void handleNotification(String message) {
        log.info("Notification: {}", message);
    }

    // Manual acknowledgment
    @RabbitListener(queues = RabbitConfig.ORDER_QUEUE,
                    ackMode = "MANUAL")
    public void handleWithManualAck(OrderDto order, Channel channel,
                                    @Header(AmqpHeaders.DELIVERY_TAG) long deliveryTag)
            throws IOException {
        try {
            processOrder(order);
            channel.basicAck(deliveryTag, false);
        } catch (Exception e) {
            channel.basicNack(deliveryTag, false, true);  // requeue
        }
    }
}
```

---

## Apache Kafka / Spring Kafka

### Dependency

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-kafka</artifactId>
    <!-- or spring-kafka directly -->
</dependency>
```

### Configuration

```properties
spring.kafka.bootstrap-servers=localhost:9092

# Producer
spring.kafka.producer.key-serializer=org.apache.kafka.common.serialization.StringSerializer
spring.kafka.producer.value-serializer=org.springframework.kafka.support.serializer.JsonSerializer
spring.kafka.producer.acks=all
spring.kafka.producer.retries=3
spring.kafka.producer.batch-size=16384
spring.kafka.producer.buffer-memory=33554432
spring.kafka.producer.compression-type=snappy

# Consumer
spring.kafka.consumer.group-id=my-service
spring.kafka.consumer.key-deserializer=org.apache.kafka.common.serialization.StringDeserializer
spring.kafka.consumer.value-deserializer=org.springframework.kafka.support.serializer.JsonDeserializer
spring.kafka.consumer.auto-offset-reset=earliest
spring.kafka.consumer.enable-auto-commit=false
spring.kafka.consumer.max-poll-records=500
spring.kafka.consumer.properties.spring.json.trusted.packages=com.example.*

# Listener
spring.kafka.listener.ack-mode=MANUAL_IMMEDIATE
spring.kafka.listener.concurrency=3
```

### Advanced Kafka Config Bean

```java
@Configuration
public class KafkaConfig {

    @Value("${spring.kafka.bootstrap-servers}")
    private String bootstrapServers;

    @Bean
    public ProducerFactory<String, Object> producerFactory() {
        Map<String, Object> config = new HashMap<>();
        config.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        config.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        config.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JsonSerializer.class);
        config.put(ProducerConfig.ACKS_CONFIG, "all");
        config.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        return new DefaultKafkaProducerFactory<>(config);
    }

    @Bean
    public KafkaTemplate<String, Object> kafkaTemplate() {
        return new KafkaTemplate<>(producerFactory());
    }

    @Bean
    public ConsumerFactory<String, Object> consumerFactory() {
        Map<String, Object> config = new HashMap<>();
        config.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        config.put(ConsumerConfig.GROUP_ID_CONFIG, "my-group");
        config.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        config.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, JsonDeserializer.class);
        config.put(JsonDeserializer.TRUSTED_PACKAGES, "com.example.*");
        return new DefaultKafkaConsumerFactory<>(config);
    }

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, Object> kafkaListenerContainerFactory() {
        ConcurrentKafkaListenerContainerFactory<String, Object> factory =
            new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory());
        factory.setConcurrency(3);
        factory.getContainerProperties().setAckMode(AckMode.MANUAL_IMMEDIATE);
        return factory;
    }

    // Create topics programmatically
    @Bean
    public NewTopic orderTopic() {
        return TopicBuilder.name("orders")
            .partitions(3)
            .replicas(1)
            .build();
    }
}
```

### Sending Messages

```java
@Service
public class KafkaOrderProducer {

    private static final Logger log = LoggerFactory.getLogger(KafkaOrderProducer.class);

    private final KafkaTemplate<String, Object> kafkaTemplate;

    public KafkaOrderProducer(KafkaTemplate<String, Object> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    public void sendOrder(OrderDto order) {
        kafkaTemplate.send("orders", String.valueOf(order.getId()), order);
    }

    // With callback
    public void sendWithCallback(OrderDto order) {
        kafkaTemplate.send("orders", order)
            .addCallback(
                result -> log.info("Sent order {} to partition {}",
                    order.getId(),
                    result.getRecordMetadata().partition()),
                ex -> log.error("Failed to send order {}", order.getId(), ex)
            );
    }

    // Transactional send
    public void sendTransactional(List<OrderDto> orders) {
        kafkaTemplate.executeInTransaction(t -> {
            orders.forEach(order ->
                t.send("orders", String.valueOf(order.getId()), order));
            return true;
        });
    }
}
```

### Receiving Messages

```java
@Component
public class KafkaOrderConsumer {

    private static final Logger log = LoggerFactory.getLogger(KafkaOrderConsumer.class);

    @KafkaListener(topics = "orders", groupId = "order-processor")
    public void handle(OrderDto order) {
        log.info("Processing order: {}", order.getId());
        // process
    }

    // With offset/partition metadata
    @KafkaListener(topics = "orders")
    public void handleWithMetadata(
            @Payload OrderDto order,
            @Header(KafkaHeaders.RECEIVED_TOPIC) String topic,
            @Header(KafkaHeaders.RECEIVED_PARTITION_ID) int partition,
            @Header(KafkaHeaders.OFFSET) long offset) {
        log.info("Received from topic={}, partition={}, offset={}", topic, partition, offset);
    }

    // Manual acknowledgment
    @KafkaListener(topics = "orders",
                   containerFactory = "kafkaListenerContainerFactory")
    public void handleWithAck(OrderDto order, Acknowledgment ack) {
        try {
            processOrder(order);
            ack.acknowledge();
        } catch (Exception e) {
            log.error("Error processing order", e);
            // don't acknowledge — will be retried based on retry config
        }
    }

    // Batch consumption
    @KafkaListener(topics = "orders",
                   containerFactory = "batchKafkaListenerContainerFactory")
    public void handleBatch(List<OrderDto> orders) {
        log.info("Processing batch of {} orders", orders.size());
    }

    // Multiple topics
    @KafkaListener(topics = {"orders", "express-orders"}, groupId = "order-processor")
    public void handleMultiTopics(OrderDto order,
                                  @Header(KafkaHeaders.RECEIVED_TOPIC) String topic) {
        log.info("From topic {}: {}", topic, order.getId());
    }
}
```

### Error Handling

```java
@Bean
public ConcurrentKafkaListenerContainerFactory<String, Object> kafkaListenerContainerFactory() {
    ConcurrentKafkaListenerContainerFactory<String, Object> factory =
        new ConcurrentKafkaListenerContainerFactory<>();
    factory.setConsumerFactory(consumerFactory());
    factory.setErrorHandler(new SeekToCurrentErrorHandler(
        new DeadLetterPublishingRecoverer(kafkaTemplate),  // send failures to DLT
        new FixedBackOff(1000L, 3)  // retry 3 times with 1s delay
    ));
    return factory;
}
```

---

## JMS (ActiveMQ)

### Dependency

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-activemq</artifactId>
</dependency>
```

### Configuration

```properties
spring.activemq.broker-url=tcp://localhost:61616
spring.activemq.user=admin
spring.activemq.password=admin
spring.jms.pub-sub-domain=false   # false=Queue, true=Topic
```

### Sending

```java
@Service
public class JmsOrderSender {

    private final JmsTemplate jmsTemplate;

    public JmsOrderSender(JmsTemplate jmsTemplate) {
        this.jmsTemplate = jmsTemplate;
    }

    public void sendOrder(OrderDto order) {
        jmsTemplate.convertAndSend("order.queue", order);
    }

    public void sendWithPriority(OrderDto order) {
        jmsTemplate.convertAndSend("order.queue", order, message -> {
            message.setJMSPriority(9);
            message.setJMSDeliveryMode(DeliveryMode.PERSISTENT);
            return message;
        });
    }
}
```

### Receiving

```java
@Component
public class JmsOrderListener {

    @JmsListener(destination = "order.queue")
    public void handleOrder(OrderDto order) {
        System.out.println("Received: " + order.getId());
    }

    // With message metadata
    @JmsListener(destination = "order.queue")
    public void handleWithHeaders(OrderDto order, Message jmsMessage) throws JMSException {
        System.out.println("Priority: " + jmsMessage.getJMSPriority());
    }
}
```

### Message Converter for JSON

```java
@Bean
public MessageConverter jacksonJmsMessageConverter() {
    MappingJackson2MessageConverter converter = new MappingJackson2MessageConverter();
    converter.setTargetType(MessageType.TEXT);
    converter.setTypeIdPropertyName("_type");
    return converter;
}
```
