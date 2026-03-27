# Spring Boot 2.3 — Spring MVC

## Auto-Configuration

Spring Boot auto-configures Spring MVC when `spring-boot-starter-web` is on the classpath:

- `ContentNegotiatingViewResolver` and `BeanNameViewResolver`
- Static resource serving from `/META-INF/resources/`, `/resources/`, `/static/`, `/public/`
- `HttpMessageConverters` (Jackson for JSON by default)
- `MessageCodesResolver`
- `WebBindingInitializer`

To add MVC configuration **without** replacing defaults, implement `WebMvcConfigurer`:

```java
@Configuration(proxyBeanMethods = false)
public class MvcConfig implements WebMvcConfigurer {
    // Override only what you need
}
```

To **fully replace** MVC auto-configuration:
```java
@Configuration
@EnableWebMvc   // Takes over completely — you must configure everything
public class FullMvcConfig implements WebMvcConfigurer {}
```

---

## Controllers

### @RestController (JSON API)

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping
    public List<UserDto> getAll() {
        return userService.findAll();
    }

    @GetMapping("/{id}")
    public ResponseEntity<UserDto> getById(@PathVariable Long id) {
        return userService.findById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public UserDto create(@RequestBody @Valid CreateUserRequest request) {
        return userService.create(request);
    }

    @PutMapping("/{id}")
    public UserDto update(@PathVariable Long id,
                          @RequestBody @Valid UpdateUserRequest request) {
        return userService.update(id, request);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable Long id) {
        userService.delete(id);
    }
}
```

### @Controller (Thymeleaf / view-returning)

```java
@Controller
@RequestMapping("/users")
public class UserViewController {

    private final UserService userService;

    public UserViewController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping
    public String listUsers(Model model) {
        model.addAttribute("users", userService.findAll());
        return "users/list";     // resolves to templates/users/list.html
    }

    @GetMapping("/{id}")
    public String viewUser(@PathVariable Long id, Model model) {
        model.addAttribute("user", userService.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("User", id)));
        return "users/detail";
    }

    @PostMapping
    public String createUser(@ModelAttribute @Valid CreateUserRequest form,
                             BindingResult result,
                             RedirectAttributes redirectAttributes) {
        if (result.hasErrors()) {
            return "users/new";
        }
        userService.create(form);
        redirectAttributes.addFlashAttribute("message", "User created");
        return "redirect:/users";
    }
}
```

---

## Request Mapping Annotations

```java
@GetMapping("/path")               // GET
@PostMapping("/path")              // POST
@PutMapping("/path/{id}")          // PUT
@PatchMapping("/path/{id}")        // PATCH
@DeleteMapping("/path/{id}")       // DELETE

// General form (any method)
@RequestMapping(value = "/path", method = RequestMethod.GET)

// Content negotiation
@GetMapping(value = "/path", produces = MediaType.APPLICATION_JSON_VALUE)
@PostMapping(value = "/path", consumes = MediaType.APPLICATION_JSON_VALUE)
```

---

## Request Parameter Annotations

```java
// Path variable
@GetMapping("/{id}")
public User getUser(@PathVariable Long id) {}

// Optional path variable with default
@GetMapping({"/{id}", "/"})
public User getUser(@PathVariable(required = false) Long id) {}

// Query parameter: GET /users?page=0&size=20
@GetMapping
public Page<User> list(
    @RequestParam(defaultValue = "0") int page,
    @RequestParam(defaultValue = "20") int size,
    @RequestParam(required = false) String search) {}

// Request body (JSON deserialization)
@PostMapping
public User create(@RequestBody @Valid CreateUserRequest request) {}

// Request header
@GetMapping
public String withHeader(@RequestHeader("X-Custom-Header") String value) {}

// All headers
@GetMapping
public void withHeaders(@RequestHeader HttpHeaders headers) {}

// Cookie value
@GetMapping
public void withCookie(@CookieValue("sessionId") String sessionId) {}

// Matrix variables: GET /users/42;role=admin
@GetMapping("/{id}")
public User withMatrix(@PathVariable Long id,
                       @MatrixVariable String role) {}
```

---

## ResponseEntity

```java
@GetMapping("/{id}")
public ResponseEntity<UserDto> getById(@PathVariable Long id) {
    return userService.findById(id)
        .map(user -> ResponseEntity.ok()
            .header("X-Request-Id", UUID.randomUUID().toString())
            .body(user))
        .orElse(ResponseEntity.notFound().build());
}

@PostMapping
public ResponseEntity<UserDto> create(@RequestBody @Valid CreateUserRequest req,
                                      UriComponentsBuilder ucb) {
    UserDto created = userService.create(req);
    URI location = ucb.path("/api/users/{id}").buildAndExpand(created.getId()).toUri();
    return ResponseEntity.created(location).body(created);
}

// Common status shortcuts
ResponseEntity.ok(body)
ResponseEntity.created(uri).body(body)
ResponseEntity.accepted().build()
ResponseEntity.noContent().build()
ResponseEntity.badRequest().body(error)
ResponseEntity.notFound().build()
ResponseEntity.status(HttpStatus.CONFLICT).body(error)
```

---

## Exception Handling

### @ControllerAdvice (global)

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ErrorResponse handleNotFound(ResourceNotFoundException ex) {
        return new ErrorResponse("NOT_FOUND", ex.getMessage());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleValidation(MethodArgumentNotValidException ex) {
        List<String> errors = ex.getBindingResult().getFieldErrors().stream()
            .map(fe -> fe.getField() + ": " + fe.getDefaultMessage())
            .collect(Collectors.toList());
        return new ErrorResponse("VALIDATION_FAILED", errors.toString());
    }

    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ErrorResponse handleGeneric(Exception ex) {
        return new ErrorResponse("INTERNAL_ERROR", "An unexpected error occurred");
    }
}

// Custom exception
public class ResourceNotFoundException extends RuntimeException {
    public ResourceNotFoundException(String resource, Object id) {
        super(resource + " not found with id: " + id);
    }
}

// Error response DTO
public class ErrorResponse {
    private final String code;
    private final String message;
    public ErrorResponse(String code, String message) {
        this.code = code;
        this.message = message;
    }
    public String getCode() { return code; }
    public String getMessage() { return message; }
}
```

### @ExceptionHandler on controller class (local scope)

```java
@RestController
public class UserController {

    @ExceptionHandler(UserNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ErrorResponse handleUserNotFound(UserNotFoundException ex) {
        return new ErrorResponse("USER_NOT_FOUND", ex.getMessage());
    }
}
```

---

## Validation

**Note: In Spring Boot 2.3, `spring-boot-starter-validation` is no longer included in `spring-boot-starter-web`. Add it explicitly.**

```java
// Request DTO with validation annotations
public class CreateUserRequest {
    @NotBlank(message = "Name is required")
    private String name;

    @Email(message = "Must be a valid email")
    @NotBlank
    private String email;

    @Min(value = 0, message = "Age must be non-negative")
    @Max(value = 150)
    private int age;

    @Size(min = 8, message = "Password must be at least 8 characters")
    private String password;

    // getters / setters
}

// Controller — use @Valid to trigger validation
@PostMapping
public UserDto create(@RequestBody @Valid CreateUserRequest request) {
    // If validation fails, MethodArgumentNotValidException is thrown
    return userService.create(request);
}
```

---

## Content Negotiation

Spring Boot auto-configures content negotiation using Accept header:

```java
@GetMapping(value = "/users/{id}",
            produces = {MediaType.APPLICATION_JSON_VALUE,
                        MediaType.APPLICATION_XML_VALUE})
public User getUser(@PathVariable Long id) { ... }
```

Configure via properties:
```properties
spring.mvc.contentnegotiation.favor-parameter=false
spring.mvc.pathmatch.matching-strategy=ant_path_matcher
```

---

## Static Resources

Default locations (all served at `/**`):
- `classpath:/META-INF/resources/`
- `classpath:/resources/`
- `classpath:/static/`
- `classpath:/public/`

Custom locations:
```properties
spring.web.resources.static-locations=classpath:/custom-static/,file:./uploads/
spring.web.resources.static-path-pattern=/static/**
spring.web.resources.cache.period=3600
```

Welcome page: place `index.html` in any static resource location.

---

## Thymeleaf

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-thymeleaf</artifactId>
</dependency>
```

```properties
spring.thymeleaf.prefix=classpath:/templates/
spring.thymeleaf.suffix=.html
spring.thymeleaf.cache=false   # disable in dev
spring.thymeleaf.encoding=UTF-8
```

```html
<!-- templates/users/list.html -->
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<body>
    <h1>Users</h1>
    <table>
        <tr th:each="user : ${users}">
            <td th:text="${user.name}">Name</td>
            <td th:text="${user.email}">Email</td>
            <td>
                <a th:href="@{/users/{id}(id=${user.id})}">View</a>
            </td>
        </tr>
    </table>
    <form th:action="@{/users}" method="post" th:object="${createUserRequest}">
        <input th:field="*{name}" type="text"/>
        <span th:errors="*{name}" th:if="${#fields.hasErrors('name')}"></span>
        <button type="submit">Create</button>
    </form>
</body>
</html>
```

---

## Filters

```java
@Component
@Order(1)
public class RequestLoggingFilter implements Filter {

    private static final Logger log = LoggerFactory.getLogger(RequestLoggingFilter.class);

    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
            throws IOException, ServletException {
        HttpServletRequest request = (HttpServletRequest) req;
        long start = System.currentTimeMillis();
        try {
            chain.doFilter(req, res);
        } finally {
            log.info("{} {} took {}ms",
                request.getMethod(), request.getRequestURI(),
                System.currentTimeMillis() - start);
        }
    }
}
```

Or register programmatically with URL mapping:

```java
@Bean
public FilterRegistrationBean<RequestLoggingFilter> loggingFilter() {
    FilterRegistrationBean<RequestLoggingFilter> reg = new FilterRegistrationBean<>();
    reg.setFilter(new RequestLoggingFilter());
    reg.addUrlPatterns("/api/*");
    reg.setOrder(1);
    return reg;
}
```

---

## Interceptors

```java
@Component
public class AuthInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest req, HttpServletResponse res,
                             Object handler) throws Exception {
        String token = req.getHeader("Authorization");
        if (token == null) {
            res.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            return false;  // stop chain
        }
        return true;  // continue
    }

    @Override
    public void postHandle(HttpServletRequest req, HttpServletResponse res,
                           Object handler, ModelAndView mv) throws Exception {
        // runs after handler but before view rendering
    }

    @Override
    public void afterCompletion(HttpServletRequest req, HttpServletResponse res,
                                Object handler, Exception ex) throws Exception {
        // cleanup
    }
}

// Register in MVC config
@Configuration
public class MvcConfig implements WebMvcConfigurer {

    @Autowired
    private AuthInterceptor authInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(authInterceptor)
            .addPathPatterns("/api/**")
            .excludePathPatterns("/api/auth/**");
    }
}
```

---

## CORS

### Global configuration

```java
@Configuration
public class CorsConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
            .allowedOrigins("https://app.example.com", "https://admin.example.com")
            .allowedMethods("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")
            .allowedHeaders("*")
            .allowCredentials(true)
            .maxAge(3600);
    }
}
```

### Controller-level

```java
@CrossOrigin(origins = "https://app.example.com", maxAge = 3600)
@RestController
@RequestMapping("/api")
public class ApiController {}
```

### Method-level

```java
@CrossOrigin(origins = "*", methods = {RequestMethod.GET})
@GetMapping("/public-data")
public Data publicData() {}
```

### CORS with Spring Security

When using Spring Security, you must configure CORS in both the MVC layer and the security layer:

```java
@Override
protected void configure(HttpSecurity http) throws Exception {
    http
        .cors()   // enables CORS support in security — delegates to CorsConfigurationSource bean
        .and()
        // ...
}

@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(List.of("https://app.example.com"));
    config.setAllowedMethods(List.of("GET","POST","PUT","DELETE","OPTIONS"));
    config.setAllowedHeaders(List.of("*"));
    config.setAllowCredentials(true);
    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", config);
    return source;
}
```

---

## HttpMessageConverters

Spring Boot auto-configures Jackson for JSON conversion. To customize:

```java
@Configuration
public class JacksonConfig {

    @Bean
    public Jackson2ObjectMapperBuilderCustomizer customizer() {
        return builder -> builder
            .featuresToDisable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS)
            .featuresToEnable(MapperFeature.DEFAULT_VIEW_INCLUSION)
            .modules(new JavaTimeModule());
    }
}
```

Via properties:
```properties
spring.jackson.serialization.indent-output=true
spring.jackson.serialization.write-dates-as-timestamps=false
spring.jackson.default-property-inclusion=non_null
spring.jackson.time-zone=UTC
```

Add XML support (alongside JSON):
```xml
<dependency>
    <groupId>com.fasterxml.jackson.dataformat</groupId>
    <artifactId>jackson-dataformat-xml</artifactId>
</dependency>
```

---

## Multipart File Upload

```properties
spring.servlet.multipart.max-file-size=10MB
spring.servlet.multipart.max-request-size=50MB
```

```java
@PostMapping("/upload")
public ResponseEntity<String> upload(
        @RequestParam("file") MultipartFile file,
        @RequestParam(required = false) String description) throws IOException {

    if (file.isEmpty()) {
        return ResponseEntity.badRequest().body("File is empty");
    }
    String fileName = StringUtils.cleanPath(file.getOriginalFilename());
    Path targetLocation = Paths.get("uploads").resolve(fileName);
    Files.copy(file.getInputStream(), targetLocation, StandardCopyOption.REPLACE_EXISTING);
    return ResponseEntity.ok("Uploaded: " + fileName);
}
```

---

## Error Handling

Default error handling: `/error` endpoint (handled by `BasicErrorController`).

Custom error pages in `src/main/resources/`:
```
public/error/404.html    ← for 404 status
public/error/500.html    ← for 500 status
public/error/5xx.html    ← for all 5xx statuses
```

Custom ErrorController:
```java
@RestController
public class CustomErrorController implements ErrorController {

    @RequestMapping("/error")
    public ResponseEntity<ErrorResponse> handleError(HttpServletRequest request) {
        int status = (int) request.getAttribute(RequestDispatcher.ERROR_STATUS_CODE);
        String message = (String) request.getAttribute(RequestDispatcher.ERROR_MESSAGE);
        return ResponseEntity.status(status)
            .body(new ErrorResponse(String.valueOf(status), message));
    }

    @Override
    public String getErrorPath() { return "/error"; }
}
```
