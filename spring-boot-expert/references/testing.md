# Testing Spring Boot Applications

Chapter 8 of *Spring Boot Up & Running* — @SpringBootTest, test slices, MockMvc, WebTestClient, TestRestTemplate, @MockBean.

---

## Test Dependencies

`spring-boot-starter-test` includes:
- JUnit 5 (Jupiter)
- Mockito
- AssertJ
- Hamcrest
- Spring Test / Spring Boot Test
- JSONPath (Jayway)
- XMLUnit

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
```

---

## @SpringBootTest — Full Integration Test

Loads the complete application context. Use for end-to-end integration tests:

```java
@SpringBootTest
class CoffeeApplicationTests {

    @Test
    void contextLoads() {
        // passes if context starts without error
    }
}
```

### Web Environment Modes

```java
// Default: no web server, use MockMvc
@SpringBootTest

// Start a real server on a random port
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)

// Start a real server on port defined in application.properties
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.DEFINED_PORT)

// No web environment at all
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.NONE)
```

---

## MockMvc — Test MVC Layer Without HTTP

`MockMvc` dispatches requests through the Spring MVC dispatcher without starting a real server:

```java
@SpringBootTest
@AutoConfigureMockMvc
class CoffeeControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void getAllCoffees_returnsEmptyList() throws Exception {
        mockMvc.perform(get("/api/coffees")
                .accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$").isArray())
                .andExpect(jsonPath("$.length()").value(0));
    }

    @Test
    void postCoffee_returnsCreatedCoffee() throws Exception {
        Coffee coffee = new Coffee("1", "Espresso");
        mockMvc.perform(post("/api/coffees")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(coffee)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.name").value("Espresso"));
    }
}
```

MockMvc matcher imports:
```java
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
import static org.hamcrest.Matchers.*;
```

---

## @WebMvcTest — Slice Test for Controllers

Loads only the web layer (controllers, filters, `@ControllerAdvice`). Service beans are NOT loaded — use `@MockBean`:

```java
@WebMvcTest(CoffeeController.class)
class CoffeeControllerSliceTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private CoffeeService coffeeService;   // Mockito mock, injected into context

    @Test
    void getCoffee_found_returns200() throws Exception {
        Coffee coffee = new Coffee("1", "Espresso");
        given(coffeeService.findById("1")).willReturn(Optional.of(coffee));

        mockMvc.perform(get("/api/coffees/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("Espresso"));
    }

    @Test
    void getCoffee_notFound_returns404() throws Exception {
        given(coffeeService.findById("99")).willReturn(Optional.empty());

        mockMvc.perform(get("/api/coffees/99"))
                .andExpect(status().isNotFound());
    }
}
```

`@WebMvcTest` is much faster than `@SpringBootTest` because it skips JPA, security (unless you include it), etc.

---

## @DataJpaTest — Slice Test for Repositories

Loads only the JPA layer with an in-memory H2 database. Transactions are rolled back after each test by default:

```java
@DataJpaTest
class CoffeeRepositoryTest {

    @Autowired
    private CoffeeRepository coffeeRepository;

    @Test
    void findByName_returnsMatchingCoffee() {
        coffeeRepository.save(new Coffee("1", "Espresso"));
        coffeeRepository.save(new Coffee("2", "Latte"));

        List<Coffee> found = coffeeRepository.findByName("Espresso");
        assertThat(found).hasSize(1);
        assertThat(found.get(0).getId()).isEqualTo("1");
    }

    @Test
    void findByName_noMatch_returnsEmpty() {
        List<Coffee> found = coffeeRepository.findByName("Unknown");
        assertThat(found).isEmpty();
    }
}
```

Use a real database instead of H2:
```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class RealDatabaseRepositoryTest { ... }
```

---

## TestRestTemplate — Real HTTP Tests

Use with `RANDOM_PORT` to make actual HTTP calls:

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class CoffeeApiIntegrationTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @LocalServerPort
    private int port;

    @Test
    void getCoffees_returnsOk() {
        ResponseEntity<List> response = restTemplate.getForEntity(
                "http://localhost:" + port + "/api/coffees", List.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
    }

    @Test
    void postCoffee_createsAndReturns() {
        Coffee coffee = new Coffee("1", "Espresso");
        ResponseEntity<Coffee> response = restTemplate.postForEntity(
                "/api/coffees", coffee, Coffee.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(response.getBody().getName()).isEqualTo("Espresso");
    }
}
```

`TestRestTemplate` automatically handles cookies, redirects, and basic auth for tests.

---

## WebTestClient — Reactive / WebFlux Tests

Use for WebFlux apps or when you prefer a fluent reactive test API:

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class CoffeeWebFluxTest {

    @Autowired
    private WebTestClient webTestClient;

    @Test
    void getCoffees_returnsFluxOfCoffees() {
        webTestClient.get().uri("/api/coffees")
                .accept(MediaType.APPLICATION_JSON)
                .exchange()
                .expectStatus().isOk()
                .expectBodyList(Coffee.class)
                .hasSize(0);
    }
}
```

`WebTestClient` can also be used with MVC (non-reactive) when bound to `MockMvc`:
```java
WebTestClient client = MockMvcWebTestClient.bindToApplicationContext(context).build();
```

---

## @MockBean and @SpyBean

```java
@MockBean
private EmailService emailService;  // Replaces the real bean with a Mockito mock

@SpyBean
private CoffeeService coffeeService;  // Wraps real bean with a Mockito spy
```

`@MockBean` adds the mock to the Spring context and resets it between tests. Use it instead of field injection of mocks when you need the mock inside the context.

```java
// BDDMockito style (preferred)
given(emailService.send(any())).willReturn(true);
verify(emailService).send(any(EmailRequest.class));

// Mockito style
when(emailService.send(any())).thenReturn(true);
```

---

## Test Slices Summary

| Slice | What it loads | Common use |
|-------|---------------|-----------|
| `@WebMvcTest` | Controllers, filters, `@ControllerAdvice`, Jackson | Unit test controllers |
| `@DataJpaTest` | JPA, Hibernate, in-memory DB, repositories | Unit test repositories |
| `@DataMongoTest` | MongoDB, repositories | Unit test Mongo repos |
| `@DataRedisTest` | Redis | Unit test Redis repos |
| `@RestClientTest` | `RestTemplate`, Jackson | Unit test HTTP clients |
| `@JsonTest` | Jackson, GSON | Unit test JSON serialization |
| `@WebFluxTest` | WebFlux controllers, `WebFilter` | Unit test reactive controllers |

---

## Test Configuration

```java
// Override properties for a test
@SpringBootTest
@TestPropertySource(properties = {
    "spring.datasource.url=jdbc:h2:mem:testdb",
    "app.feature.enabled=false"
})
class MyTest { ... }

// Use a test-specific application.properties
@SpringBootTest
@TestPropertySource(locations = "classpath:application-test.properties")
class MyTest { ... }

// @DynamicPropertySource (Spring Boot 2.2.6+) — great for Testcontainers
@SpringBootTest
class ContainerTest {
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }
}
```

---

## Testcontainers Integration (Spring Boot 3.1+)

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-testcontainers</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>postgresql</artifactId>
    <scope>test</scope>
</dependency>
```

```java
@SpringBootTest
@Testcontainers
class PostgresIntegrationTest {

    @Container
    @ServiceConnection   // Spring Boot 3.1: auto-configures datasource from container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15");

    @Test
    void testWithRealDatabase() { ... }
}
```

`@ServiceConnection` eliminates the need for `@DynamicPropertySource`.

---

## AssertJ Cheat Sheet

```java
// Basic
assertThat(value).isEqualTo(expected);
assertThat(value).isNotNull();
assertThat(value).isTrue();
assertThat(str).startsWith("Hello").endsWith("World");

// Collections
assertThat(list).hasSize(3);
assertThat(list).contains("a", "b");
assertThat(list).doesNotContain("x");
assertThat(list).extracting("name").containsExactly("Espresso", "Latte");

// Exceptions
assertThatThrownBy(() -> service.findById("missing"))
        .isInstanceOf(NotFoundException.class)
        .hasMessage("Not found: missing");
```
