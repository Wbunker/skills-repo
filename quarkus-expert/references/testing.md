# Testing Quarkus Applications
## Chapter 5: @QuarkusTest, Native Tests, Mockito, Test Profiles

---

## Testing Overview

Quarkus provides first-class testing support. Tests run against the full application context — CDI, JPA, HTTP server — making them true integration tests with minimal boilerplate.

```
Test types:
├── @QuarkusTest         — JVM mode integration test (full app, real CDI, real HTTP)
├── @NativeImageTest     — Same tests against a compiled native binary
├── @QuarkusUnitTest     — Test extension build steps (for extension authors)
└── Unit tests           — Plain JUnit 5, no Quarkus involvement
```

---

## @QuarkusTest — Integration Tests

### Basic Test

```java
import io.quarkus.test.junit.QuarkusTest;
import static io.restassured.RestAssured.*;
import static org.hamcrest.Matchers.*;

@QuarkusTest
class FruitResourceTest {

    @Test
    void testListAllFruits() {
        given()
            .when().get("/fruits")
            .then()
                .statusCode(200)
                .body("$.size()", greaterThan(0))
                .body("[0].name", notNullValue());
    }

    @Test
    void testCreateFruit() {
        given()
            .contentType(ContentType.JSON)
            .body("{\"name\":\"Apple\"}")
            .when().post("/fruits")
            .then()
                .statusCode(201);
    }
}
```

### Testing JSON Responses

```java
@Test
void testGetFruit() {
    Fruit fruit = given()
        .when().get("/fruits/1")
        .then()
            .statusCode(200)
        .extract().body().as(Fruit.class);

    assertThat(fruit.name).isEqualTo("Apple");
}

// Using JSON path assertions
@Test
void testFruitDetails() {
    given()
        .when().get("/fruits/1")
        .then()
            .statusCode(200)
            .body("name", equalTo("Apple"))
            .body("id", notNullValue());
}
```

### Injecting Beans in Tests

```java
@QuarkusTest
class FruitServiceTest {

    @Inject
    FruitService fruitService;          // real CDI bean

    @Test
    void testCreateFruit() {
        Fruit fruit = new Fruit("Mango");
        fruitService.save(fruit);
        assertThat(fruit.id).isNotNull();
    }
}
```

### Testing with Transactions

```java
@QuarkusTest
class FruitRepositoryTest {

    @Inject
    FruitRepository repository;

    @Test
    @Transactional
    void testPersist() {
        Fruit fruit = new Fruit("Kiwi");
        repository.persist(fruit);
        assertThat(repository.count()).isGreaterThan(0);
    }
}
```

---

## Mocking with Mockito — @InjectMock

### Mock a CDI Bean

```java
@QuarkusTest
class GreetingResourceTest {

    @InjectMock
    GreetingService greetingService;     // replaces the real bean in the CDI context

    @Test
    void testGreeting() {
        when(greetingService.greet("World")).thenReturn("Mocked Hello World");

        given()
            .when().get("/greeting?name=World")
            .then()
                .statusCode(200)
                .body(equalTo("Mocked Hello World"));
    }
}
```

### Mock a REST Client

```java
@QuarkusTest
class WeatherServiceTest {

    @InjectMock
    @RestClient
    WeatherClient weatherClient;         // mocks the MicroProfile REST client

    @Test
    void testGetWeather() {
        when(weatherClient.getWeather("London"))
            .thenReturn(new WeatherData("Sunny", 25));

        WeatherData result = weatherService.getCurrentWeather("London");
        assertThat(result.condition()).isEqualTo("Sunny");
    }
}
```

### Spy (Partial Mock)

```java
@InjectSpy
FruitService fruitService;              // real bean, with spy capabilities

@Test
void testSpy() {
    // Only stub the part you need
    doReturn(emptyList()).when(fruitService).findByColor("red");
    // All other methods call through to real impl
}
```

---

## Test Profiles — @TestProfile

Use profiles to configure the application differently for different test classes.

### Define a Profile

```java
public class MockedDatabaseProfile implements QuarkusTestProfile {

    @Override
    public Map<String, String> getConfigOverrides() {
        return Map.of(
            "quarkus.datasource.db-kind", "h2",
            "quarkus.datasource.jdbc.url", "jdbc:h2:mem:test;DB_CLOSE_DELAY=-1",
            "quarkus.hibernate-orm.database.generation", "drop-and-create"
        );
    }

    @Override
    public Set<Class<?>> getEnabledAlternatives() {
        return Set.of(MockEmailService.class);    // CDI @Alternative
    }
}
```

```java
@QuarkusTest
@TestProfile(MockedDatabaseProfile.class)
class FruitResourceWithH2Test {
    // runs against H2 in-memory DB
}
```

### Profile With Custom Tags

```java
public class IntegrationTestProfile implements QuarkusTestProfile {
    @Override
    public String getConfigProfile() {
        return "integration";    // activates %integration.* properties
    }
}
```

---

## @QuarkusIntegrationTest — Testing the Packaged App

Runs the **packaged JAR or native binary** as a black-box server:

```java
@QuarkusIntegrationTest       // no @QuarkusTest
class FruitResourceIT {

    @Test
    void testListFruits() {
        given()
            .when().get("/fruits")
            .then()
                .statusCode(200);
    }
}
```

Must package first:
```bash
./mvnw package                     # then run tests
./mvnw verify                      # package + integration test in one step
```

---

## @NativeImageTest — Native Binary Tests

```java
@NativeImageTest                  // replaces @QuarkusTest
class FruitResourceNativeIT extends FruitResourceTest {
    // Inherits all tests from the parent class
    // Runs against the native binary instead of JVM
}
```

```bash
./mvnw verify -Pnative            # build native + run @NativeImageTest
```

**Limitation:** cannot `@Inject` beans — native tests are pure black-box HTTP tests.

---

## Test Resource Lifecycle

```java
@QuarkusTest
@QuarkusTestResource(WireMockTestResource.class)    // start external mock server
class ExternalApiTest {
    @InjectWireMock
    WireMockServer wireMock;

    @Test
    void testExternalCall() {
        wireMock.stubFor(get("/api/data").willReturn(ok().withBody("{}")));
        // ...
    }
}
```

```java
// Custom test resource
public class WireMockTestResource implements QuarkusTestResourceLifecycleManager {

    private WireMockServer server;

    @Override
    public Map<String, String> start() {
        server = new WireMockServer(8089);
        server.start();
        return Map.of("external.api.url", "http://localhost:8089");
    }

    @Override
    public void stop() {
        server.stop();
    }
}
```

---

## Continuous Testing (Dev Mode)

```bash
quarkus dev
# Then press:
r    → run all tests now
f    → run failing tests
o    → toggle test output
```

Tests run in the background. The JVM is kept warm — test re-runs take milliseconds.

---

## RestAssured Quick Reference

```java
// GET with path param
given().pathParam("id", 1).when().get("/fruits/{id}").then().statusCode(200);

// POST with JSON body
given().contentType(JSON).body(new Fruit("Apple"))
       .when().post("/fruits").then().statusCode(201);

// Assert response body
.body("name", equalTo("Apple"))
.body("items.size()", is(3))
.body("items[0].id", notNullValue())

// Extract response
Fruit f = ...then().extract().as(Fruit.class);
String loc = ...then().extract().header("Location");
int status = ...then().extract().statusCode();

// Auth
given().auth().oauth2(token).when().get("/secure");
given().header("Authorization", "Bearer " + token).when().get("/secure");
```
