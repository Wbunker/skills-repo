# Web Applications and Security
## Chapter 6: Qute Templates, HTMX, OpenID Connect, Keycloak, RBAC

---

## Qute Templating Engine

Qute is Quarkus's native, type-safe, compile-time-checked template engine.

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-resteasy-reactive-qute</artifactId>
</dependency>
```

### Template Location

Templates live in `src/main/resources/templates/`:
```
templates/
├── base.html
├── index.html
├── fruits/
│   ├── list.html
│   └── detail.html
└── error.html
```

### Basic Template

```html
<!-- templates/fruits/list.html -->
<!DOCTYPE html>
<html>
<body>
  <h1>Fruits</h1>
  <ul>
    {#for fruit in fruits}
      <li>{fruit.name} — {fruit.color}</li>
    {/for}
  </ul>
</body>
</html>
```

### Typed Template Injection

```java
@Path("/fruits")
public class FruitResource {

    @Inject
    Template list;                    // injects templates/fruits/list.html

    @CheckedTemplate
    public static class Templates {
        public static native TemplateInstance list(List<Fruit> fruits);
        public static native TemplateInstance detail(Fruit fruit);
    }

    @GET
    @Produces(MediaType.TEXT_HTML)
    public TemplateInstance listFruits() {
        return Templates.list(Fruit.listAll());
    }
}
```

`@CheckedTemplate` enables compile-time validation that the data types match what the template expects.

### Template Syntax Reference

```html
<!-- Variable expression -->
{fruit.name}

<!-- Null-safe navigation -->
{fruit.color.orEmpty}
{fruit?.color}

<!-- Conditionals -->
{#if fruit.available}
  <span>In stock</span>
{#else}
  <span>Out of stock</span>
{/if}

<!-- Loops -->
{#for fruit in fruits}
  <li class="{fruit_count % 2 == 0 ? 'even' : 'odd'}">{fruit.name}</li>
{/for}

<!-- Loop metadata: fruit_count, fruit_index, fruit_hasNext, fruit_odd, fruit_even -->

<!-- Includes / fragments -->
{#include base.html}
  {#title}My Fruits{/title}
  {#content}...{/content}
{/include}

<!-- Template extension call -->
{fruit.formattedPrice}      <!-- calls @TemplateExtension method -->
```

### Template Extensions

```java
public class FruitTemplateExtensions {

    @TemplateExtension
    static String formattedPrice(Fruit fruit) {
        return String.format("$%.2f", fruit.price);
    }

    @TemplateExtension(namespace = "str")
    static String upper(String s) {
        return s.toUpperCase();
    }
}
```

```html
{fruit.formattedPrice}
{str:upper(fruit.name)}
```

---

## HTMX Integration

HTMX lets you add dynamic behavior to HTML via attributes — no JavaScript framework needed. Pairs naturally with Qute's fragment support.

### HTML with HTMX Attributes

```html
<!-- templates/index.html -->
<body hx-boost="true">
  <div id="fruit-list">
    {#include fruits/list.html /}
  </div>

  <!-- Load fragment on click -->
  <button hx-get="/fruits/partial"
          hx-target="#fruit-list"
          hx-swap="innerHTML">
    Refresh Fruits
  </button>

  <!-- Post form without page reload -->
  <form hx-post="/fruits"
        hx-target="#fruit-list"
        hx-swap="beforeend">
    <input name="name" type="text" />
    <button type="submit">Add</button>
  </form>
</body>
```

### Returning Partial HTML from Quarkus

```java
@GET
@Path("/partial")
@Produces(MediaType.TEXT_HTML)
public TemplateInstance fruitListPartial() {
    return Templates.listFragment(Fruit.listAll());
}
```

```java
@CheckedTemplate
public static class Templates {
    public static native TemplateInstance list(List<Fruit> fruits);
    // Fragment — renders just the <ul> block, not full page
    public static native TemplateInstance listFragment(List<Fruit> fruits);
}
```

---

## Security Overview

```
Security layers:
├── Authentication — who are you? (OIDC, JWT, Basic, Form, mTLS)
├── Authorization — what can you do? (@RolesAllowed, @Authenticated, policies)
└── Identity augmentation — add roles from DB to the identity
```

### Add Security Extension

```xml
<!-- OIDC (Keycloak, Google, etc.) -->
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-oidc</artifactId>
</dependency>

<!-- Simple file-based (dev/testing) -->
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-elytron-security-properties-file</artifactId>
</dependency>
```

---

## OpenID Connect (OIDC) with Keycloak

### Configuration

```properties
# Production
quarkus.oidc.auth-server-url=https://auth.example.com/realms/myrealm
quarkus.oidc.client-id=my-app
quarkus.oidc.credentials.secret=my-secret
quarkus.oidc.application-type=web-app    # or 'service' for API

# Dev Services (Keycloak starts automatically)
%dev.quarkus.keycloak.devservices.enabled=true
%dev.quarkus.keycloak.devservices.realm-path=realm.json
```

### Application Types

| `application-type` | Use Case | Token |
|---|---|---|
| `service` | API / microservice | Bearer JWT in Authorization header |
| `web-app` | Browser-facing app | Authorization code flow, cookie session |
| `hybrid` | Both | Handles both flows |

### Securing Endpoints

```java
@Path("/fruits")
public class FruitResource {

    @GET
    @Authenticated                           // any authenticated user
    public List<Fruit> list() { ... }

    @POST
    @RolesAllowed("admin")                   // must have 'admin' role
    public Response create(Fruit fruit) { ... }

    @DELETE
    @Path("/{id}")
    @RolesAllowed({"admin", "moderator"})    // any of these roles
    public void delete(@PathParam("id") Long id) { ... }
}
```

### Accessing the Identity

```java
@Inject
SecurityIdentity securityIdentity;

@Inject
JsonWebToken jwt;           // for service (Bearer) apps

public void example() {
    String username = securityIdentity.getPrincipal().getName();
    Set<String> roles = securityIdentity.getRoles();
    boolean isAdmin = securityIdentity.hasRole("admin");

    // JWT claims
    String email = jwt.getClaim("email");
    String subject = jwt.getSubject();
}
```

### Web App — Login/Logout

Quarkus handles OIDC flows automatically. Add these endpoints:

```java
@Path("/")
public class HomeResource {

    @Inject
    @IdToken
    JsonWebToken idToken;

    @GET
    @Path("/me")
    @Authenticated
    public String me() {
        return "Logged in as: " + idToken.getName();
    }
}
```

```properties
# Logout endpoint (auto-registered)
quarkus.oidc.logout.path=/logout
quarkus.oidc.logout.post-logout-path=/
```

---

## Security Policies (HTTP Path-Based)

```properties
# Deny all by default, then allow specific paths
quarkus.http.auth.policy.role-policy1.roles-allowed=user,admin
quarkus.http.auth.permission.permit1.paths=/public/*
quarkus.http.auth.permission.permit1.policy=permit
quarkus.http.auth.permission.authenticated.paths=/api/*
quarkus.http.auth.permission.authenticated.policy=authenticated
quarkus.http.auth.permission.admin-only.paths=/admin/*
quarkus.http.auth.permission.admin-only.policy=role-policy1
```

---

## Dev Services — Keycloak

In dev mode with `quarkus-oidc`, a Keycloak container starts automatically:

```properties
%dev.quarkus.keycloak.devservices.realm-path=src/main/resources/dev-realm.json
```

Dev UI shows the Keycloak admin URL and a pre-configured test user. The realm JSON defines clients, users, and roles.

```json
{
  "realm": "quarkus",
  "clients": [{"clientId": "backend-service", "secret": "secret", "publicClient": false}],
  "users": [
    {"username": "alice", "credentials": [{"value": "alice"}], "realmRoles": ["user"]},
    {"username": "admin",  "credentials": [{"value": "admin"}],  "realmRoles": ["admin"]}
  ]
}
```

---

## Identity Augmentation

Add roles dynamically from the database:

```java
@ApplicationScoped
public class CustomAugmentor implements SecurityIdentityAugmentor {

    @Inject
    UserRoleRepository roleRepository;

    @Override
    public Uni<SecurityIdentity> augment(SecurityIdentity identity,
                                         AuthenticationRequestContext ctx) {
        String username = identity.getPrincipal().getName();
        return roleRepository.findRoles(username)
            .map(roles -> QuarkusSecurityIdentity.builder(identity)
                .addRoles(new HashSet<>(roles))
                .build());
    }
}
```

---

## CSRF Protection

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-csrf-reactive</artifactId>
</dependency>
```

```java
@POST
@Path("/form")
@Consumes(MediaType.APPLICATION_FORM_URLENCODED)
@CSRFTokenRequired                          // validates the token automatically
public Response handleForm(@FormParam("name") String name) { ... }
```

```html
<!-- Qute template — inject the CSRF token -->
<form method="POST" action="/form">
  <input type="hidden" name="${inject:csrf.parameterName}" value="${inject:csrf.token}">
  <input name="name" type="text" />
  <button type="submit">Submit</button>
</form>
```
