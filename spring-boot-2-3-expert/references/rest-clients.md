# Spring Boot 2.3 — REST Clients

## RestTemplate

`RestTemplate` is the synchronous, blocking HTTP client. Deprecated in favor of `WebClient` for new code, but still fully supported in Spring Boot 2.3.

### Auto-configuration

Spring Boot does NOT auto-configure a `RestTemplate` bean. Instead, it auto-configures a `RestTemplateBuilder` that you use to create instances.

```java
@Service
public class WeatherService {

    private final RestTemplate restTemplate;

    public WeatherService(RestTemplateBuilder builder) {
        this.restTemplate = builder
            .rootUri("https://api.weather.com")
            .setConnectTimeout(Duration.ofSeconds(5))
            .setReadTimeout(Duration.ofSeconds(10))
            .build();
    }

    public WeatherData getWeather(String city) {
        return restTemplate.getForObject("/weather/{city}", WeatherData.class, city);
    }
}
```

### RestTemplate Methods

```java
// GET
WeatherData data = restTemplate.getForObject(url, WeatherData.class);
ResponseEntity<WeatherData> entity = restTemplate.getForEntity(url, WeatherData.class);

// POST
UserDto created = restTemplate.postForObject(url, requestBody, UserDto.class);
ResponseEntity<UserDto> response = restTemplate.postForEntity(url, requestBody, UserDto.class);
URI location = restTemplate.postForLocation(url, requestBody);

// PUT
restTemplate.put(url, requestBody);

// PATCH
ResponseEntity<UserDto> response = restTemplate.exchange(
    url, HttpMethod.PATCH, new HttpEntity<>(patchBody), UserDto.class);

// DELETE
restTemplate.delete(url + "/{id}", id);

// Generic exchange (all HTTP methods)
HttpHeaders headers = new HttpHeaders();
headers.set("Authorization", "Bearer " + token);
headers.setContentType(MediaType.APPLICATION_JSON);
HttpEntity<CreateUserRequest> requestEntity = new HttpEntity<>(request, headers);

ResponseEntity<UserDto> response = restTemplate.exchange(
    "/api/users",
    HttpMethod.POST,
    requestEntity,
    UserDto.class
);

// With parameterized type (e.g., List<UserDto>)
ParameterizedTypeReference<List<UserDto>> typeRef =
    new ParameterizedTypeReference<List<UserDto>>() {};
ResponseEntity<List<UserDto>> listResponse = restTemplate.exchange(
    "/api/users", HttpMethod.GET, null, typeRef);
```

### RestTemplateBuilder Customization

```java
@Bean
public RestTemplate restTemplate(RestTemplateBuilder builder) {
    return builder
        .rootUri("https://api.example.com")
        .setConnectTimeout(Duration.ofSeconds(3))
        .setReadTimeout(Duration.ofSeconds(30))
        .basicAuthentication("user", "password")
        .defaultHeader("X-API-Key", "my-key")
        .interceptors(new LoggingRequestInterceptor())
        .errorHandler(new CustomErrorHandler())
        .build();
}
```

### Global Customizer

```java
@Component
public class LoggingRestTemplateCustomizer implements RestTemplateCustomizer {

    @Override
    public void customize(RestTemplate restTemplate) {
        restTemplate.getInterceptors().add((request, body, execution) -> {
            long start = System.currentTimeMillis();
            ClientHttpResponse response = execution.execute(request, body);
            log.info("{} {} -> {} ({}ms)",
                request.getMethod(), request.getURI(),
                response.getStatusCode(), System.currentTimeMillis() - start);
            return response;
        });
    }
}
```

### Error Handling

```java
public class CustomErrorHandler implements ResponseErrorHandler {

    @Override
    public boolean hasError(ClientHttpResponse response) throws IOException {
        return response.getStatusCode().is4xxClientError()
            || response.getStatusCode().is5xxServerError();
    }

    @Override
    public void handleError(ClientHttpResponse response) throws IOException {
        if (response.getStatusCode() == HttpStatus.NOT_FOUND) {
            throw new ResourceNotFoundException("Resource not found");
        }
        if (response.getStatusCode().is5xxServerError()) {
            throw new ServiceUnavailableException("Upstream service error");
        }
    }
}
```

---

## WebClient (Reactive, preferred for new code)

`WebClient` is non-blocking, reactive, and is the recommended approach in Spring Boot 2.3+. Requires `spring-boot-starter-webflux`.

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webflux</artifactId>
</dependency>
```

### Auto-configuration

Spring Boot auto-configures `WebClient.Builder` when WebFlux is on the classpath.

```java
@Service
public class UserClient {

    private final WebClient webClient;

    public UserClient(WebClient.Builder builder) {
        this.webClient = builder
            .baseUrl("https://api.example.com")
            .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
            .build();
    }
}
```

### Basic Usage

```java
// GET — retrieve single item
Mono<UserDto> user = webClient.get()
    .uri("/api/users/{id}", id)
    .retrieve()
    .bodyToMono(UserDto.class);

// GET — retrieve list
Flux<UserDto> users = webClient.get()
    .uri(uriBuilder -> uriBuilder
        .path("/api/users")
        .queryParam("page", 0)
        .queryParam("size", 20)
        .build())
    .retrieve()
    .bodyToFlux(UserDto.class);

// POST
Mono<UserDto> created = webClient.post()
    .uri("/api/users")
    .bodyValue(createRequest)
    .retrieve()
    .bodyToMono(UserDto.class);

// PUT
Mono<UserDto> updated = webClient.put()
    .uri("/api/users/{id}", id)
    .bodyValue(updateRequest)
    .retrieve()
    .bodyToMono(UserDto.class);

// DELETE
Mono<Void> deleted = webClient.delete()
    .uri("/api/users/{id}", id)
    .retrieve()
    .bodyToMono(Void.class);

// With headers
Mono<UserDto> result = webClient.get()
    .uri("/api/users/{id}", id)
    .header("Authorization", "Bearer " + token)
    .header("X-Request-Id", UUID.randomUUID().toString())
    .retrieve()
    .bodyToMono(UserDto.class);
```

### ResponseEntity

```java
Mono<ResponseEntity<UserDto>> response = webClient.get()
    .uri("/api/users/{id}", id)
    .retrieve()
    .toEntity(UserDto.class);

response.subscribe(entity -> {
    System.out.println("Status: " + entity.getStatusCode());
    System.out.println("Headers: " + entity.getHeaders());
    System.out.println("Body: " + entity.getBody());
});
```

### Error Handling

```java
Mono<UserDto> result = webClient.get()
    .uri("/api/users/{id}", id)
    .retrieve()
    .onStatus(HttpStatus::is4xxClientError, clientResponse -> {
        if (clientResponse.statusCode() == HttpStatus.NOT_FOUND) {
            return Mono.error(new UserNotFoundException(id));
        }
        return clientResponse.bodyToMono(ErrorResponse.class)
            .flatMap(err -> Mono.error(new ClientException(err.getMessage())));
    })
    .onStatus(HttpStatus::is5xxServerError, clientResponse ->
        Mono.error(new ServiceException("Upstream error: " + clientResponse.statusCode())))
    .bodyToMono(UserDto.class);
```

### Timeout

```java
Mono<UserDto> result = webClient.get()
    .uri("/api/users/{id}", id)
    .retrieve()
    .bodyToMono(UserDto.class)
    .timeout(Duration.ofSeconds(5))
    .onErrorReturn(TimeoutException.class, UserDto.empty());
```

### WebClient with Reactor Netty timeouts

```java
@Bean
public WebClient webClient(WebClient.Builder builder) {
    HttpClient httpClient = HttpClient.create()
        .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 5000)
        .responseTimeout(Duration.ofSeconds(10))
        .doOnConnected(conn ->
            conn.addHandlerLast(new ReadTimeoutHandler(10, TimeUnit.SECONDS))
                .addHandlerLast(new WriteTimeoutHandler(10, TimeUnit.SECONDS)));

    return builder
        .clientConnector(new ReactorClientHttpConnector(httpClient))
        .baseUrl("https://api.example.com")
        .build();
}
```

### WebClientCustomizer (global)

```java
@Component
public class LoggingWebClientCustomizer implements WebClientCustomizer {

    @Override
    public void customize(WebClient.Builder builder) {
        builder.filter(ExchangeFilterFunction.ofRequestProcessor(request -> {
            log.info("Request: {} {}", request.method(), request.url());
            return Mono.just(request);
        })).filter(ExchangeFilterFunction.ofResponseProcessor(response -> {
            log.info("Response status: {}", response.statusCode());
            return Mono.just(response);
        }));
    }
}
```

### Authentication filter

```java
ExchangeFilterFunction authFilter = ExchangeFilterFunction.ofRequestProcessor(request ->
    Mono.just(ClientRequest.from(request)
        .header("Authorization", "Bearer " + tokenProvider.getToken())
        .build()));

WebClient webClient = builder.filter(authFilter).build();
```

### Retry

```java
import reactor.util.retry.Retry;

Mono<UserDto> result = webClient.get()
    .uri("/api/users/{id}", id)
    .retrieve()
    .bodyToMono(UserDto.class)
    .retryWhen(Retry.fixedDelay(3, Duration.ofSeconds(1))
        .filter(throwable -> throwable instanceof ServiceException));
```

---

## Using WebClient in Servlet (non-reactive) Applications

You can use `WebClient` in a regular Spring MVC app by blocking:

```java
@Service
public class ExternalApiService {

    private final WebClient webClient;

    public ExternalApiService(WebClient.Builder builder) {
        this.webClient = builder.baseUrl("https://api.external.com").build();
    }

    // Block to make synchronous — acceptable in servlet threads
    public UserDto fetchUser(Long id) {
        return webClient.get()
            .uri("/users/{id}", id)
            .retrieve()
            .bodyToMono(UserDto.class)
            .block(Duration.ofSeconds(5));    // timeout required — never block indefinitely
    }

    public List<UserDto> fetchAllUsers() {
        return webClient.get()
            .uri("/users")
            .retrieve()
            .bodyToFlux(UserDto.class)
            .collectList()
            .block(Duration.ofSeconds(10));
    }
}
```

---

## Spring Cloud OpenFeign (@FeignClient)

For declarative REST clients (requires `spring-cloud-starter-openfeign`):

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-openfeign</artifactId>
</dependency>
```

```java
// Enable Feign
@SpringBootApplication
@EnableFeignClients
public class MyApplication {}

// Define the client
@FeignClient(name = "user-service",
             url = "${services.user.url}",
             configuration = UserClientConfig.class,
             fallback = UserClientFallback.class)
public interface UserServiceClient {

    @GetMapping("/api/users/{id}")
    UserDto getUserById(@PathVariable("id") Long id);

    @GetMapping("/api/users")
    Page<UserDto> getUsers(@RequestParam("page") int page,
                           @RequestParam("size") int size);

    @PostMapping("/api/users")
    UserDto createUser(@RequestBody CreateUserRequest request);

    @DeleteMapping("/api/users/{id}")
    void deleteUser(@PathVariable("id") Long id);
}

// Fallback (requires Hystrix or Resilience4j)
@Component
public class UserClientFallback implements UserServiceClient {

    @Override
    public UserDto getUserById(Long id) {
        return UserDto.empty(id);
    }
    // ...
}

// Configuration
@Configuration
public class UserClientConfig {
    @Bean
    public RequestInterceptor authInterceptor() {
        return template -> template.header("Authorization", "Bearer " + getToken());
    }
}
```

Properties:
```properties
services.user.url=https://user-service.example.com
feign.client.config.default.connectTimeout=5000
feign.client.config.default.readTimeout=10000
feign.client.config.default.loggerLevel=full
```
