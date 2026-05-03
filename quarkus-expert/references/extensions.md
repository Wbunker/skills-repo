# Custom Quarkus Extensions
## Chapter 12: Extension Structure, Build Steps, Runtime Recording, CDI, Config

---

## Why Write an Extension?

- Move initialization work to **build time** — eliminates startup cost
- Integrate a third-party library into Quarkus's CDI, config, health, and Dev Services ecosystem
- Ship reusable Quarkus capabilities to your team or community

---

## Extension Project Structure

An extension consists of **two Maven modules**:

```
my-extension/
├── pom.xml                        # parent POM
├── deployment/
│   ├── pom.xml                    # depends on quarkus-core-deployment
│   └── src/main/java/
│       └── com/example/
│           └── deployment/
│               ├── MyExtensionProcessor.java   # @BuildStep methods
│               └── MyExtensionConfig.java      # build-time config
└── runtime/
    ├── pom.xml                    # depends on quarkus-core
    └── src/main/java/
        └── com/example/
            └── runtime/
                ├── MyService.java              # runtime code
                ├── MyRuntimeConfig.java        # runtime config
                └── MyRecorder.java             # @Recorder
```

### Create via CLI

```bash
quarkus create ext com.example:my-extension
```

### Parent POM Key Elements

```xml
<modules>
    <module>deployment</module>
    <module>runtime</module>
</modules>
```

### Runtime POM

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-core</artifactId>
</dependency>
<!-- Add the library you're wrapping -->
<dependency>
    <groupId>com.example</groupId>
    <artifactId>my-library</artifactId>
</dependency>
```

### Deployment POM

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-core-deployment</artifactId>
</dependency>
<dependency>
    <groupId>com.example</groupId>
    <artifactId>my-extension</artifactId>     <!-- your own runtime module -->
</dependency>
```

---

## Build Steps — `@BuildStep`

Build steps run at **build time** (during `mvn package`). They read `BuildItem` inputs and produce `BuildItem` outputs.

```java
@BuildSteps(onlyIf = IsNormal.class)     // only in non-dev mode
public class MyExtensionProcessor {

    @BuildStep
    FeatureBuildItem feature() {
        return new FeatureBuildItem("my-extension");  // shows in startup banner
    }

    @BuildStep
    void registerBeans(BuildProducer<AdditionalBeanBuildItem> beans) {
        beans.produce(AdditionalBeanBuildItem.unremovableOf(MyService.class));
    }

    @BuildStep
    void registerReflection(
            BuildProducer<ReflectiveClassBuildItem> reflectiveClasses) {
        reflectiveClasses.produce(ReflectiveClassBuildItem
            .builder(MyLibraryClass.class)
            .methods(true)
            .fields(true)
            .build());
    }

    @BuildStep
    void registerResources(
            BuildProducer<NativeImageResourceBuildItem> resources) {
        resources.produce(new NativeImageResourceBuildItem("config/default.json"));
    }
}
```

### Consuming Build Items

```java
@BuildStep
void processAnnotations(
        CombinedIndexBuildItem combinedIndex,               // app class index (Jandex)
        BuildProducer<GeneratedClassBuildItem> generatedClasses) {

    IndexView index = combinedIndex.getIndex();

    // Find all classes annotated with @MyAnnotation
    for (AnnotationInstance annotation :
             index.getAnnotations(DotName.createSimple("com.example.MyAnnotation"))) {
        ClassInfo target = annotation.target().asClass();
        // generate bytecode, register beans, etc.
    }
}
```

### Conditional Build Steps

```java
@BuildStep(onlyIf = MyExtensionConfig.MyCondition.class)
void conditionalStep(...) { ... }

// Config-based condition
public static class MyCondition implements BooleanSupplier {
    MyExtensionBuildConfig config;

    @Override
    public boolean getAsBoolean() {
        return config.enabled();
    }
}
```

---

## Runtime Recording — `@Recorder`

Recorders bridge build-time decisions to runtime initialization. The recorder method body is **serialized as bytecode** and replayed at startup.

```java
@Recorder
public class MyRecorder {

    public RuntimeValue<MyService> createService(String configValue) {
        // This code runs at startup (STATIC_INIT) or first request (RUNTIME_INIT)
        return new RuntimeValue<>(new MyService(configValue));
    }

    public void registerHandler(BeanContainer container, RuntimeValue<MyService> service) {
        container.beanInstance(MyHandlerRegistry.class)
            .register(service.getValue());
    }
}
```

### Using Recorder in a Build Step

```java
@BuildStep
@Record(ExecutionTime.STATIC_INIT)         // runs at static initialization
SyntheticBeanBuildItem setupService(
        MyRecorder recorder,
        MyExtensionBuildConfig buildConfig) {

    RuntimeValue<MyService> serviceValue =
        recorder.createService(buildConfig.configKey());

    return SyntheticBeanBuildItem.configure(MyService.class)
        .scope(ApplicationScoped.class)
        .runtimeValue(serviceValue)
        .done();
}
```

### Execution Times

| Phase | When | Use For |
|---|---|---|
| `STATIC_INIT` | JVM static init (before `main()`) | Fast, no I/O, config-driven setup |
| `RUNTIME_INIT` | After `main()` starts | Network connections, runtime config reading |

---

## Build-Time Configuration

```java
@ConfigRoot(phase = ConfigPhase.BUILD_TIME)         // only available at build time
public interface MyExtensionBuildConfig {

    @WithName("enabled")
    @WithDefault("true")
    boolean enabled();

    @WithName("packages")
    List<String> packages();
}
```

```java
@BuildStep
void configure(MyExtensionBuildConfig config) {
    if (!config.enabled()) return;
    // ...
}
```

---

## Runtime Configuration

```java
@ConfigRoot(phase = ConfigPhase.RUN_TIME)            // available at runtime
public interface MyExtensionRuntimeConfig {

    @WithName("timeout")
    @WithDefault("30S")
    Duration timeout();

    @WithName("pool-size")
    @WithDefault("10")
    int poolSize();
}
```

```java
@Recorder
public class MyRecorder {

    public void configure(MyExtensionRuntimeConfig config) {
        MyService.setTimeout(config.timeout());
    }
}
```

---

## CDI Integration

### Register a Synthetic Bean

```java
@BuildStep
@Record(ExecutionTime.STATIC_INIT)
SyntheticBeanBuildItem syntheticBean(MyRecorder recorder) {
    return SyntheticBeanBuildItem
        .configure(MyClient.class)
        .scope(ApplicationScoped.class)
        .setRuntimeInit()                  // initialized at RUNTIME_INIT
        .supplier(recorder.clientSupplier())
        .done();
}
```

### Make a Bean Unremovable

```java
@BuildStep
void keepBeans(BuildProducer<AdditionalBeanBuildItem> beans) {
    beans.produce(AdditionalBeanBuildItem.builder()
        .addBeanClass(MyInternalService.class)
        .setUnremovable()                  // don't let ArC prune it
        .build());
}
```

---

## Dev Services in Extensions

```java
@BuildStep(onlyIfNot = IsNormal.class)     // dev and test modes only
DevServicesResultBuildItem startDevService(
        DockerStatusBuildItem dockerStatus,
        LaunchModeBuildItem launchMode) {

    if (!dockerStatus.isDockerAvailable()) return null;

    GenericContainer<?> container = new GenericContainer<>("my-service:latest")
        .withExposedPorts(1234)
        .waitingFor(Wait.forHttp("/health"));
    container.start();

    return new DevServicesResultBuildItem.RunningDevService(
        "my-extension",
        container.getContainerId(),
        container::stop,
        Map.of("my.service.host", container.getHost(),
               "my.service.port", String.valueOf(container.getMappedPort(1234)))
    ).toBuildItem();
}
```

---

## Testing Extensions

```java
@QuarkusUnitTest
static final QuarkusUnitTest test = new QuarkusUnitTest()
    .withApplicationRoot(jar -> jar
        .addClasses(MyService.class)
        .addAsResource("test-application.properties", "application.properties"))
    .overrideConfigKey("my.extension.enabled", "true");

@Inject
MyService service;

@Test
void testService() {
    assertThat(service.greet()).isEqualTo("Hello from extension");
}
```

---

## Packaging and Sharing

Extensions are normal Maven artifacts. Publish to Maven Central or your private registry:

```bash
./mvnw deploy -DaltDeploymentRepository=nexus::default::http://nexus/repository/releases
```

Users add the runtime dependency; Quarkus resolves the deployment JAR automatically at build time.

```xml
<!-- User's pom.xml -->
<dependency>
    <groupId>com.example</groupId>
    <artifactId>my-extension</artifactId>
    <version>1.0.0</version>
</dependency>
```
