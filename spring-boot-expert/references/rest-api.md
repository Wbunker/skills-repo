# Building REST APIs with Spring Boot

Chapter 3 of *Spring Boot Up & Running* — @RestController, request mapping, request/response handling, content negotiation, error handling, OpenAPI documentation.

---

## Core Annotations

| Annotation | Purpose |
|-----------|---------|
| `@RestController` | `@Controller` + `@ResponseBody`; methods return data, not view names |
| `@RequestMapping` | Base URL mapping on the class |
| `@GetMapping` | HTTP GET shorthand for `@RequestMapping(method=GET)` |
| `@PostMapping` | HTTP POST |
| `@PutMapping` | HTTP PUT |
| `@PatchMapping` | HTTP PATCH |
| `@DeleteMapping` | HTTP DELETE |
| `@PathVariable` | Extracts value from URI path segment |
| `@RequestParam` | Extracts query string parameter |
| `@RequestBody` | Deserializes the request body (JSON → POJO via Jackson) |
| `@ResponseBody` | Serializes return value to response body |
| `@ResponseStatus` | Sets the HTTP status code for a method or exception |

---

## Minimal REST Controller

```java
@RestController
@RequestMapping("/api/coffees")
public class CoffeeController {

    private final List<Coffee> coffees = new ArrayList<>();

    @GetMapping
    public List<Coffee> getCoffees() {
        return coffees;
    }

    @GetMapping("/{id}")
    public Optional<Coffee> getCoffeeById(@PathVariable String id) {
        return coffees.stream()
                .filter(c -> c.getId().equals(id))
                .findFirst();
    }

    @PostMapping
    public Coffee postCoffee(@RequestBody Coffee coffee) {
        coffees.add(coffee);
        return coffee;
    }

    @PutMapping("/{id}")
    public Coffee putCoffee(@PathVariable String id, @RequestBody Coffee coffee) {
        int index = -1;
        for (Coffee c : coffees) {
            if (c.getId().equals(id)) {
                index = coffees.indexOf(c);
                break;
            }
        }
        if (index == -1) {
            coffees.add(coffee);
            return coffee;
        }
        coffees.set(index, coffee);
        return coffee;
    }

    @DeleteMapping("/{id}")
    public void deleteCoffee(@PathVariable String id) {
        coffees.removeIf(c -> c.getId().equals(id));
    }
}
```

---

## ResponseEntity — Full Control Over HTTP Response

Use `ResponseEntity<T>` when you need to control status code, headers, or body independently:

```java
@PostMapping
public ResponseEntity<Coffee> postCoffee(@RequestBody Coffee coffee) {
    Coffee saved = coffeeRepository.save(coffee);
    URI location = ServletUriComponentsBuilder
            .fromCurrentRequest()
            .path("/{id}")
            .buildAndExpand(saved.getId())
            .toUri();
    return ResponseEntity.created(location).body(saved);
}

@GetMapping("/{id}")
public ResponseEntity<Coffee> getCoffeeById(@PathVariable String id) {
    return coffeeRepository.findById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
}
```

Common factory methods:
- `ResponseEntity.ok(body)` → 200
- `ResponseEntity.created(uri).body(body)` → 201
- `ResponseEntity.noContent().build()` → 204
- `ResponseEntity.notFound().build()` → 404
- `ResponseEntity.badRequest().body(errorMsg)` → 400
- `ResponseEntity.status(HttpStatus.CONFLICT).body(msg)` → 409

---

## Path Variables and Request Parameters

```java
// Path variable: GET /coffees/abc123
@GetMapping("/{id}")
public Coffee getById(@PathVariable String id) { ... }

// Path variable with type conversion
@GetMapping("/version/{version}")
public List<Coffee> getByVersion(@PathVariable int version) { ... }

// Required query param: GET /coffees/search?name=Espresso
@GetMapping("/search")
public List<Coffee> search(@RequestParam String name) { ... }

// Optional query param with default
@GetMapping
public List<Coffee> list(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size) { ... }

// Optional query param
@GetMapping("/filter")
public List<Coffee> filter(
        @RequestParam Optional<String> origin) { ... }
```

---

## Request Body and Validation

```java
// Auto-deserialized from JSON by Jackson
@PostMapping
public Coffee create(@Valid @RequestBody Coffee coffee) { ... }
```

Add validation with Jakarta Bean Validation (included with `spring-boot-starter-web`):
```java
public class Coffee {
    @NotNull
    @NotBlank
    private String name;

    @NotNull
    private String id;

    @Min(0)
    private double price;
    // getters/setters...
}
```

Add `spring-boot-starter-validation` to pom.xml for Bean Validation, then use `@Valid` on `@RequestBody`.

---

## Error Handling

### @ExceptionHandler (controller-scoped)

```java
@RestController
public class CoffeeController {
    @ExceptionHandler(CoffeeNotFoundException.class)
    public ResponseEntity<String> handleNotFound(CoffeeNotFoundException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(ex.getMessage());
    }
}
```

### @ControllerAdvice (global)

```java
@ControllerAdvice
public class GlobalExceptionHandler extends ResponseEntityExceptionHandler {

    @ExceptionHandler(CoffeeNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(CoffeeNotFoundException ex) {
        return ResponseEntity.status(404)
                .body(new ErrorResponse(404, ex.getMessage()));
    }
}
```

### Problem Details (Spring Boot 3.x)

Spring Boot 3 supports RFC 7807 Problem Details natively:
```properties
spring.mvc.problemdetails.enabled=true
```

This makes validation errors and other exceptions return structured `application/problem+json` responses automatically.

---

## Content Negotiation

Spring Boot auto-configures Jackson for JSON. For XML support, add:
```xml
<dependency>
    <groupId>com.fasterxml.jackson.dataformat</groupId>
    <artifactId>jackson-dataformat-xml</artifactId>
</dependency>
```

Clients negotiate via `Accept` header:
- `Accept: application/json` → JSON
- `Accept: application/xml` → XML

Configure Jackson behavior:
```properties
# Fail if unknown properties in JSON
spring.jackson.deserialization.fail-on-unknown-properties=true
# Serialize dates as ISO-8601 strings, not timestamps
spring.jackson.serialization.write-dates-as-timestamps=false
```

---

## OpenAPI / Springdoc

Add `springdoc-openapi-starter-webmvc-ui` for interactive API docs at `/swagger-ui.html`:

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.3.0</version>
</dependency>
```

Annotate for richer docs:
```java
@Operation(summary = "Get coffee by ID")
@ApiResponse(responseCode = "200", description = "Coffee found")
@ApiResponse(responseCode = "404", description = "Coffee not found")
@GetMapping("/{id}")
public ResponseEntity<Coffee> getById(@PathVariable String id) { ... }
```

Endpoints:
- `/swagger-ui.html` — interactive UI
- `/v3/api-docs` — raw OpenAPI JSON
- `/v3/api-docs.yaml` — raw OpenAPI YAML

---

## CORS Configuration

```java
// Per-controller
@CrossOrigin(origins = "http://localhost:3000")
@RestController
public class CoffeeController { ... }

// Global
@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
                .allowedOrigins("http://localhost:3000")
                .allowedMethods("GET", "POST", "PUT", "DELETE");
    }
}
```

---

## Common Pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| 406 Not Acceptable | No message converter for `Accept` header | Add Jackson XML or return matching content type |
| 415 Unsupported Media Type | Missing `Content-Type: application/json` on POST | Client must set content type header |
| 400 Bad Request on @RequestBody | Jackson deserialization failure | Check JSON field names match POJO; enable `FAIL_ON_UNKNOWN_PROPERTIES=false` for flexibility |
| `@PathVariable` not matched | Variable name mismatch between `{id}` and `@PathVariable String id` | Names must match, or use `@PathVariable("id")` |
| Circular JSON | Bidirectional JPA relationships | Use `@JsonIgnore` on back-reference or `@JsonManagedReference` / `@JsonBackReference` |
