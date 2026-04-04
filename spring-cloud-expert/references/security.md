---
name: security
description: OAuth2 authorization server, resource server configuration, JWT token structure, Spring Security integration, token relay across service calls. Chapter 7 of Spring Microservices in Action.
type: reference
---

# Securing Microservices: OAuth2 and JWT

## Why OAuth2 for Microservices?

Session-based security (JSESSIONID cookies) doesn't work across services. Each service would need to validate sessions independently against a central store, creating a bottleneck and coupling.

**Token-based security** (OAuth2 + JWT) is stateless:
- User authenticates once with an authorization server
- Receives a signed JWT token
- Presents the token with every service call
- Each service validates the token locally (no network call needed)

---

## OAuth2 Roles (Carnell's Mapping)

| OAuth2 Role | In Microservices |
|-------------|-----------------|
| Resource Owner | End user |
| Client | Browser or mobile app calling the gateway |
| Authorization Server | OAuth2/OIDC server (Keycloak, Okta, Spring Auth Server) |
| Resource Server | Each microservice (validates the JWT) |

---

## OAuth2 Grant Types

| Grant Type | Use Case |
|------------|---------|
| **Authorization Code** | User-facing web/mobile apps |
| **Client Credentials** | Service-to-service (no user involved) |
| **Password** (legacy) | First-party trusted apps only |
| **Refresh Token** | Renew expired access tokens |
| **PKCE** | Public clients (SPAs, native apps) |

For microservice-to-microservice calls, use **Client Credentials**.
For user-facing flows, use **Authorization Code** (with PKCE for SPAs).

---

## Spring Authorization Server (Modern)

The legacy `@EnableAuthorizationServer` (spring-security-oauth2) is deprecated. Use [Spring Authorization Server](https://spring.io/projects/spring-authorization-server) for new projects.

### Dependencies
```xml
<dependency>
    <groupId>org.springframework.security</groupId>
    <artifactId>spring-security-oauth2-authorization-server</artifactId>
</dependency>
```

### Minimal Configuration

```java
@Configuration
public class AuthorizationServerConfig {

    @Bean
    @Order(1)
    public SecurityFilterChain authorizationServerSecurityFilterChain(HttpSecurity http)
            throws Exception {
        OAuth2AuthorizationServerConfiguration.applyDefaultSecurity(http);
        http.getConfigurer(OAuth2AuthorizationServerConfigurer.class)
            .oidc(Customizer.withDefaults());
        return http.formLogin(Customizer.withDefaults()).build();
    }

    @Bean
    public RegisteredClientRepository registeredClientRepository() {
        RegisteredClient client = RegisteredClient.withId(UUID.randomUUID().toString())
            .clientId("license-service")
            .clientSecret("{noop}secret")
            .authorizationGrantType(AuthorizationGrantType.CLIENT_CREDENTIALS)
            .scope("READ")
            .build();
        return new InMemoryRegisteredClientRepository(client);
    }

    @Bean
    public JWKSource<SecurityContext> jwkSource() {
        KeyPair keyPair = generateRsaKey();
        RSAPublicKey publicKey = (RSAPublicKey) keyPair.getPublic();
        RSAPrivateKey privateKey = (RSAPrivateKey) keyPair.getPrivate();
        RSAKey rsaKey = new RSAKey.Builder(publicKey).privateKey(privateKey)
            .keyID(UUID.randomUUID().toString()).build();
        return new ImmutableJWKSet<>(new JWKSet(rsaKey));
    }
}
```

---

## Resource Server Configuration

Every microservice that needs to protect endpoints is a resource server.

### Dependencies
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.security</groupId>
    <artifactId>spring-security-oauth2-resource-server</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.security</groupId>
    <artifactId>spring-security-oauth2-jose</artifactId>
</dependency>
```

### `application.yml`
```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: http://auth-server:9000
          # OR:
          jwk-set-uri: http://auth-server:9000/oauth2/jwks
```

### Security Configuration

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/actuator/health").permitAll()
                .requestMatchers(HttpMethod.DELETE, "/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt(jwt -> jwt.jwtAuthenticationConverter(jwtAuthConverter()))
            );
        return http.build();
    }

    @Bean
    public JwtAuthenticationConverter jwtAuthConverter() {
        JwtGrantedAuthoritiesConverter grantedAuthoritiesConverter =
            new JwtGrantedAuthoritiesConverter();
        grantedAuthoritiesConverter.setAuthoritiesClaimName("roles");
        grantedAuthoritiesConverter.setAuthorityPrefix("ROLE_");
        JwtAuthenticationConverter converter = new JwtAuthenticationConverter();
        converter.setJwtGrantedAuthoritiesConverter(grantedAuthoritiesConverter);
        return converter;
    }
}
```

### Method-Level Security

```java
@RestController
public class LicenseController {

    @PreAuthorize("hasRole('ADMIN')")
    @DeleteMapping("/{licenseId}")
    public ResponseEntity<Void> deleteLicense(@PathVariable String licenseId) {
        // ...
    }

    @PostAuthorize("returnObject.organizationId == authentication.name")
    @GetMapping("/{licenseId}")
    public License getLicense(@PathVariable String licenseId) {
        // ...
    }
}
```

---

## JWT Token Structure

```
header.payload.signature

Header:  { "alg": "RS256", "typ": "JWT" }
Payload: {
  "sub": "user123",
  "iss": "http://auth-server:9000",
  "aud": "license-service",
  "exp": 1712000000,
  "iat": 1711996400,
  "scope": "READ WRITE",
  "roles": ["ADMIN", "USER"],
  "organizationId": "456"
}
Signature: RSA(base64(header) + "." + base64(payload), privateKey)
```

### Accessing Claims in a Service

```java
@GetMapping("/me")
public ResponseEntity<Map<String, Object>> getCurrentUser(
        @AuthenticationPrincipal Jwt jwt) {
    return ResponseEntity.ok(Map.of(
        "subject", jwt.getSubject(),
        "roles",   jwt.getClaimAsStringList("roles"),
        "orgId",   jwt.getClaimAsString("organizationId")
    ));
}
```

---

## Token Propagation (Service-to-Service)

When Service A calls Service B, it must forward the JWT so B can authorize the request.

### With Feign + Spring Security

```java
@Component
public class FeignOAuth2RequestInterceptor implements RequestInterceptor {

    @Override
    public void apply(RequestTemplate template) {
        SecurityContext ctx = SecurityContextHolder.getContext();
        Authentication auth = ctx.getAuthentication();
        if (auth instanceof JwtAuthenticationToken jwtAuth) {
            template.header("Authorization",
                "Bearer " + jwtAuth.getToken().getTokenValue());
        }
    }
}
```

### With RestTemplate

```java
@Bean
@LoadBalanced
public RestTemplate restTemplate() {
    RestTemplate restTemplate = new RestTemplate();
    restTemplate.getInterceptors().add((request, body, execution) -> {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth instanceof JwtAuthenticationToken jwtAuth) {
            request.getHeaders().setBearerAuth(jwtAuth.getToken().getTokenValue());
        }
        return execution.execute(request, body);
    });
    return restTemplate;
}
```

---

## Service-to-Service Authentication (Client Credentials)

When there is no user context (batch jobs, background processing):

```java
@Service
public class OrganizationServiceClient {

    private final OAuth2AuthorizedClientManager clientManager;
    private final WebClient webClient;

    public OrganizationServiceClient(OAuth2AuthorizedClientManager mgr) {
        this.clientManager = mgr;
        this.webClient = WebClient.builder()
            .apply(new ServletOAuth2AuthorizedClientExchangeFilterFunction(mgr)
                .defaultClientRegistration("license-service"))
            .build();
    }

    public Organization getOrganization(String orgId) {
        return webClient.get()
            .uri("http://organization-service/v1/organizations/{id}", orgId)
            .retrieve()
            .bodyToMono(Organization.class)
            .block();
    }
}
```

```yaml
spring:
  security:
    oauth2:
      client:
        registration:
          license-service:
            client-id: license-service
            client-secret: secret
            authorization-grant-type: client_credentials
            scope: READ
        provider:
          license-service:
            token-uri: http://auth-server:9000/oauth2/token
```

---

## Security Checklist

- [ ] All service endpoints protected (except health checks)
- [ ] JWT validated with public key from JWKS endpoint (not hardcoded)
- [ ] Token expiry checked (Spring Security does this automatically)
- [ ] Token propagated from gateway through all service calls
- [ ] Service-to-service calls use client credentials, not user tokens
- [ ] Sensitive claims (roles, orgId) extracted and used in authorization decisions
- [ ] `@EnableMethodSecurity` enabled for fine-grained method-level access control
- [ ] Actuator endpoints protected (at minimum, require authentication)
