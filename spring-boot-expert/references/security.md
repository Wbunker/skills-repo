# Securing Spring Boot Applications

Chapter 5 of *Spring Boot Up & Running* — Spring Security defaults, UserDetailsService, form login, HTTP Basic, OAuth2 client/resource server, method-level security.

---

## Auto-Configuration Defaults

Adding `spring-boot-starter-security` auto-configures:
- All HTTP endpoints secured (require authentication)
- A generated password printed to the console at startup
- Default user: `user`, password: in the startup logs
- Form-based login at `/login`
- HTTP Basic support
- CSRF protection (for state-changing requests)
- Security headers (X-Frame-Options, HSTS, etc.)

```
Using generated security password: 3a4e1b2c-...
```

Override the default user:
```properties
spring.security.user.name=admin
spring.security.user.password=secret
spring.security.user.roles=ADMIN
```

---

## Security Configuration (Spring Boot 3.x / Spring Security 6)

Spring Security 6 uses the component-based approach with a `SecurityFilterChain` bean:

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/public/**").permitAll()
                .requestMatchers("/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .formLogin(form -> form
                .loginPage("/login")
                .defaultSuccessUrl("/dashboard")
                .permitAll()
            )
            .logout(logout -> logout
                .logoutSuccessUrl("/login?logout")
                .permitAll()
            );
        return http.build();
    }
}
```

**Note**: `WebSecurityConfigurerAdapter` was removed in Spring Security 6 (Spring Boot 3). Use `SecurityFilterChain` beans instead.

---

## HTTP Basic Authentication

Useful for REST APIs and non-browser clients:

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .authorizeHttpRequests(auth -> auth
            .anyRequest().authenticated()
        )
        .httpBasic(Customizer.withDefaults())
        .csrf(csrf -> csrf.disable());  // typically disabled for stateless APIs
    return http.build();
}
```

Test with curl:
```bash
curl -u user:password http://localhost:8080/api/coffees
```

---

## Custom UserDetailsService

Replace the in-memory user with a database-backed implementation:

```java
@Service
public class UserDetailsServiceImpl implements UserDetailsService {

    private final UserRepository userRepository;

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        AppUser user = userRepository.findByUsername(username)
                .orElseThrow(() -> new UsernameNotFoundException("User not found: " + username));

        return User.builder()
                .username(user.getUsername())
                .password(user.getPassword())   // must be encoded
                .roles(user.getRoles().toArray(new String[0]))
                .build();
    }
}

// Required: a PasswordEncoder bean
@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder();
}
```

Encoding passwords:
```java
// When creating a user
String encoded = passwordEncoder.encode("plaintext-password");
user.setPassword(encoded);
userRepository.save(user);
```

---

## In-Memory Users (Testing / Dev)

```java
@Bean
public UserDetailsService userDetailsService(PasswordEncoder encoder) {
    UserDetails user = User.builder()
            .username("user")
            .password(encoder.encode("password"))
            .roles("USER")
            .build();

    UserDetails admin = User.builder()
            .username("admin")
            .password(encoder.encode("admin"))
            .roles("ADMIN", "USER")
            .build();

    return new InMemoryUserDetailsManager(user, admin);
}
```

---

## Authorization Rules

```java
// URL-based in SecurityFilterChain
.authorizeHttpRequests(auth -> auth
    .requestMatchers(HttpMethod.GET, "/api/**").hasAnyRole("USER", "ADMIN")
    .requestMatchers(HttpMethod.POST, "/api/**").hasRole("ADMIN")
    .requestMatchers("/actuator/**").hasRole("ADMIN")
    .requestMatchers("/public/**", "/login", "/error").permitAll()
    .anyRequest().authenticated()
)
```

### Method-Level Security

Enable with `@EnableMethodSecurity` (Spring Security 6):

```java
@Configuration
@EnableMethodSecurity
public class SecurityConfig { ... }

// Then annotate service/controller methods:
@PreAuthorize("hasRole('ADMIN')")
public void deleteUser(Long id) { ... }

@PreAuthorize("hasRole('USER') and #username == authentication.name")
public User getUser(String username) { ... }

@PostAuthorize("returnObject.username == authentication.name")
public User findById(Long id) { ... }

@Secured("ROLE_ADMIN")
public void adminOnlyAction() { ... }
```

---

## OAuth2 Resource Server (JWT)

Protect APIs with JWT Bearer tokens:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
</dependency>
```

```properties
# Point to the JWT issuer (the Auth Server's JWK Set endpoint is auto-discovered)
spring.security.oauth2.resourceserver.jwt.issuer-uri=https://auth.example.com
```

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .authorizeHttpRequests(auth -> auth
            .anyRequest().authenticated()
        )
        .oauth2ResourceServer(oauth2 -> oauth2
            .jwt(Customizer.withDefaults())
        );
    return http.build();
}
```

---

## OAuth2 Login (Client)

Allow users to log in via GitHub, Google, Okta, etc.:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-oauth2-client</artifactId>
</dependency>
```

```properties
spring.security.oauth2.client.registration.github.client-id=your-client-id
spring.security.oauth2.client.registration.github.client-secret=your-client-secret
```

```java
http.oauth2Login(Customizer.withDefaults());
```

Spring Boot auto-configures OAuth2 for common providers (Google, GitHub, Facebook, Okta). For custom providers, add `spring.security.oauth2.client.provider.*` properties.

---

## CSRF

CSRF protection is **enabled by default** for state-changing HTTP methods (POST, PUT, DELETE) in web apps. For stateless REST APIs using JWT or HTTP Basic, disable it:

```java
http.csrf(csrf -> csrf.disable());
```

For server-rendered forms, keep CSRF enabled and include the token in forms:
```html
<!-- Thymeleaf includes CSRF automatically with Spring Security -->
<form th:action="@{/login}" method="post">
    ...
</form>
```

---

## Security Headers

Spring Security adds these by default:
- `X-Frame-Options: DENY` — prevents clickjacking
- `X-XSS-Protection: 0` — modern browsers use CSP instead
- `X-Content-Type-Options: nosniff`
- `Cache-Control: no-cache, no-store`
- `Strict-Transport-Security` — HSTS (only on HTTPS)

Customize or disable:
```java
http.headers(headers -> headers
    .frameOptions(frame -> frame.sameOrigin())  // allow iframes from same origin
    .contentSecurityPolicy(csp -> csp.policyDirectives("default-src 'self'"))
);
```

---

## Common Pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| 401 Unauthorized after adding security | Default config locks everything | Define `SecurityFilterChain` with explicit permit rules |
| 403 Forbidden on POST | CSRF protection blocking | Disable CSRF for REST APIs or include CSRF token |
| 403 on correct credentials | Role mismatch | `hasRole("ADMIN")` checks for `ROLE_ADMIN`; roles are stored without `ROLE_` prefix |
| Password not matching | Stored as plaintext | Always encode with `BCryptPasswordEncoder` |
| `IllegalStateException: No PasswordEncoder mapped` | Missing encoder for `{bcrypt}` prefix | Set a default encoder or use `PasswordEncoderFactories.createDelegatingPasswordEncoder()` |
| `ClassCastException` on `Authentication.getPrincipal()` | Custom UserDetails not cast correctly | Cast to your `UserDetailsImpl` class, not `User` |
