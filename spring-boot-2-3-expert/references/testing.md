# Spring Boot 2.3 — Testing

## Test Dependency

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
```

Includes: JUnit 5, Mockito, AssertJ, Hamcrest, JSONassert, JsonPath, MockMvc.

---

## @SpringBootTest (Full Context)

Loads the complete application context. Best for integration tests.

```java
@SpringBootTest
class MyApplicationTests {

    @Autowired
    private UserService userService;

    @Test
    void contextLoads() {
        assertThat(userService).isNotNull();
    }
}
```

### Web environments

```java
// MOCK (default) — MockMvc, no real server
@SpringBootTest(webEnvironment = WebEnvironment.MOCK)

// RANDOM_PORT — real embedded server on random port; use TestRestTemplate or WebTestClient
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)

// DEFINED_PORT — real server on server.port (8080 by default)
@SpringBootTest(webEnvironment = WebEnvironment.DEFINED_PORT)

// NONE — no web context
@SpringBootTest(webEnvironment = WebEnvironment.NONE)
```

### With inline properties

```java
@SpringBootTest(properties = {
    "spring.datasource.url=jdbc:h2:mem:testdb",
    "app.feature.enabled=true"
})
class MyTest {}
```

---

## @WebMvcTest (Controller Slice)

Loads only the web layer — no full application context, no database. Fast.

```java
@WebMvcTest(UserController.class)
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean                              // creates Mockito mock and registers as bean
    private UserService userService;

    @MockBean
    private UserRepository userRepository;

    @Test
    void getUser_returns200() throws Exception {
        // Arrange
        UserDto user = new UserDto(1L, "John", "Doe", "john@example.com");
        given(userService.findById(1L)).willReturn(Optional.of(user));

        // Act + Assert
        mockMvc.perform(get("/api/users/1")
                .accept(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(content().contentType(MediaType.APPLICATION_JSON))
            .andExpect(jsonPath("$.id").value(1))
            .andExpect(jsonPath("$.firstName").value("John"))
            .andExpect(jsonPath("$.email").value("john@example.com"));

        verify(userService).findById(1L);
    }

    @Test
    void createUser_withInvalidBody_returns400() throws Exception {
        String invalidBody = """
            {"name": "", "email": "not-an-email"}
            """;

        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(invalidBody))
            .andExpect(status().isBadRequest());
    }

    @Test
    void createUser_returns201WithLocation() throws Exception {
        CreateUserRequest request = new CreateUserRequest("Jane", "jane@example.com");
        UserDto created = new UserDto(2L, "Jane", null, "jane@example.com");
        given(userService.create(any())).willReturn(created);

        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(new ObjectMapper().writeValueAsString(request)))
            .andExpect(status().isCreated())
            .andExpect(header().string("Location", containsString("/api/users/2")));
    }
}
```

### MockMvc request builders

```java
// GET with query params
mockMvc.perform(get("/api/users")
    .param("page", "0")
    .param("size", "20")
    .header("Authorization", "Bearer " + token))

// POST with JSON
mockMvc.perform(post("/api/users")
    .contentType(MediaType.APPLICATION_JSON)
    .content("{\"name\":\"John\"}"))

// PUT
mockMvc.perform(put("/api/users/{id}", 1L)
    .contentType(MediaType.APPLICATION_JSON)
    .content("{\"name\":\"Updated\"}"))

// DELETE
mockMvc.perform(delete("/api/users/{id}", 1L))

// Multipart
mockMvc.perform(multipart("/upload")
    .file("file", "content".getBytes())
    .param("description", "Test file"))
```

### MockMvc matchers

```java
.andExpect(status().isOk())
.andExpect(status().isCreated())
.andExpect(status().isBadRequest())
.andExpect(status().isNotFound())
.andExpect(status().is(200))
.andExpect(content().contentType(MediaType.APPLICATION_JSON))
.andExpect(content().string("Hello"))
.andExpect(jsonPath("$.name").value("John"))
.andExpect(jsonPath("$.items").isArray())
.andExpect(jsonPath("$.items", hasSize(3)))
.andExpect(jsonPath("$.items[0].id").value(1))
.andExpect(header().string("Location", "/api/users/1"))
.andExpect(redirectedUrl("/login"))
.andDo(print())   // print request and response to console
```

---

## @DataJpaTest (JPA Slice)

Loads only JPA-related infrastructure. Uses in-memory H2 by default.

```java
@DataJpaTest
class UserRepositoryTest {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private TestEntityManager entityManager;  // JPA EntityManager for test setup

    @Test
    void findByEmail_returnsUser() {
        // Arrange — persist test data
        User user = new User("John", "Doe", "john@example.com");
        entityManager.persistAndFlush(user);

        // Act
        Optional<User> found = userRepository.findByEmail("john@example.com");

        // Assert
        assertThat(found).isPresent();
        assertThat(found.get().getFirstName()).isEqualTo("John");
    }

    @Test
    void save_persistsUser() {
        User user = new User("Jane", "Doe", "jane@example.com");
        User saved = userRepository.save(user);

        assertThat(saved.getId()).isNotNull();
        assertThat(userRepository.count()).isEqualTo(1);
    }

    @Test
    void findByStatus_returnsPaged() {
        entityManager.persist(new User("A", "A", "a@ex.com", UserStatus.ACTIVE));
        entityManager.persist(new User("B", "B", "b@ex.com", UserStatus.ACTIVE));
        entityManager.persist(new User("C", "C", "c@ex.com", UserStatus.INACTIVE));
        entityManager.flush();

        Page<User> page = userRepository.findByStatus(
            UserStatus.ACTIVE, PageRequest.of(0, 10));

        assertThat(page.getTotalElements()).isEqualTo(2);
    }
}
```

Use real database instead of H2:
```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class UserRepositoryRealDbTest {}
```

---

## @MockBean and @SpyBean

```java
@SpringBootTest
class OrderServiceTest {

    @Autowired
    private OrderService orderService;

    @MockBean                           // full mock — all methods return null/default
    private PaymentGateway paymentGateway;

    @SpyBean                            // real bean but allows stubbing specific methods
    private EmailService emailService;

    @Test
    void placeOrder_processesPayment() {
        given(paymentGateway.charge(any(), any())).willReturn(PaymentResult.success("txn123"));

        Order order = orderService.placeOrder(new OrderRequest(1L, 99.99));

        assertThat(order.getStatus()).isEqualTo(OrderStatus.CONFIRMED);
        assertThat(order.getTransactionId()).isEqualTo("txn123");
        verify(paymentGateway).charge(eq(1L), eq(BigDecimal.valueOf(99.99)));
        verify(emailService).sendConfirmation(any());
    }
}
```

---

## TestRestTemplate (Integration Test with Real Server)

```java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
class UserControllerIntegrationTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @LocalServerPort
    private int port;

    @Test
    void getUser_returnsUser() {
        ResponseEntity<UserDto> response = restTemplate
            .getForEntity("/api/users/1", UserDto.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().getId()).isEqualTo(1L);
    }

    @Test
    void createUser_returns201() {
        CreateUserRequest request = new CreateUserRequest("New", "new@example.com");

        ResponseEntity<UserDto> response = restTemplate
            .postForEntity("/api/users", request, UserDto.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(response.getHeaders().getLocation()).isNotNull();
    }

    // With authentication
    @Test
    void withBasicAuth() {
        TestRestTemplate authTemplate = restTemplate
            .withBasicAuth("user", "password");
        ResponseEntity<String> response = authTemplate
            .getForEntity("/api/secure", String.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
    }

    // With bearer token
    @Test
    void withBearerToken() {
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth("my-jwt-token");
        HttpEntity<Void> entity = new HttpEntity<>(headers);
        ResponseEntity<String> response = restTemplate.exchange(
            "/api/secure", HttpMethod.GET, entity, String.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
    }
}
```

---

## Profile and Property Control in Tests

```java
@SpringBootTest
@ActiveProfiles("test")          // activates application-test.properties
class ProfiledTest {}

@SpringBootTest
@TestPropertySource(properties = {
    "app.feature.enabled=true",
    "spring.jpa.hibernate.ddl-auto=create-drop"
})
class PropertyOverrideTest {}

@SpringBootTest
@TestPropertySource(locations = "classpath:test.properties")
class FilePropertyTest {}
```

---

## Other Slice Tests

| Annotation | What's loaded |
|-----------|---------------|
| `@WebMvcTest` | MVC controllers, filters, `WebMvcConfigurer` |
| `@WebFluxTest` | WebFlux controllers, filters |
| `@DataJpaTest` | JPA repositories, entities, Flyway/Liquibase |
| `@JdbcTest` | JdbcTemplate, NamedParameterJdbcTemplate |
| `@DataJdbcTest` | Spring Data JDBC repositories |
| `@DataMongoTest` | MongoDB repositories |
| `@DataRedisTest` | Redis repositories |
| `@JsonTest` | Jackson ObjectMapper, JSON serialization/deserialization |
| `@RestClientTest` | `RestTemplate` clients (mocks the HTTP server) |

```java
// @JsonTest example
@JsonTest
class UserDtoJsonTest {

    @Autowired
    private JacksonTester<UserDto> json;

    @Test
    void serialize() throws Exception {
        UserDto dto = new UserDto(1L, "John", "Doe", "john@example.com");
        assertThat(json.write(dto))
            .hasJsonPathNumberValue("$.id")
            .extractingJsonPathNumberValue("$.id").isEqualTo(1);
    }

    @Test
    void deserialize() throws Exception {
        String content = """
            {"id": 1, "firstName": "John", "lastName": "Doe", "email": "john@example.com"}
            """;
        assertThat(json.parse(content))
            .isEqualTo(new UserDto(1L, "John", "Doe", "john@example.com"));
    }
}
```

---

## Testing with Spring Security

```java
// Add spring-security-test dependency
// <artifactId>spring-security-test</artifactId>

@WebMvcTest(AdminController.class)
class AdminControllerTest {

    @Autowired private MockMvc mockMvc;

    @Test
    @WithMockUser(roles = "ADMIN")        // mock authenticated user
    void adminEndpoint_asAdmin_returns200() throws Exception {
        mockMvc.perform(get("/admin/dashboard"))
            .andExpect(status().isOk());
    }

    @Test
    @WithMockUser(roles = "USER")
    void adminEndpoint_asUser_returns403() throws Exception {
        mockMvc.perform(get("/admin/dashboard"))
            .andExpect(status().isForbidden());
    }

    @Test
    void adminEndpoint_unauthenticated_returns401() throws Exception {
        mockMvc.perform(get("/admin/dashboard"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    @WithMockUser(username = "john@example.com", roles = "USER",
                  authorities = {"READ_USERS", "WRITE_PROFILE"})
    void withCustomAuthorities() throws Exception {
        mockMvc.perform(get("/api/profile"))
            .andExpect(status().isOk());
    }
}
```
