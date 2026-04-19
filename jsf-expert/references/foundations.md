# JSF Foundations
*Chapters 1–5 — Introducing JSF, Dev Process, Environment, Servlet/JSP Basics, Business Logic & Auth*

## Version Landscape

| Spec Version | Java EE / Jakarta EE | API Package | View Tech |
|-------------|---------------------|------------|-----------|
| JSF 1.x / 2.x | Java EE 5–8 | `javax.faces.*` | JSP (1.x), Facelets (2.0+) |
| Jakarta Faces 3.0 | Jakarta EE 9 | `jakarta.faces.*` | Facelets |
| Jakarta Faces 4.0 | Jakarta EE 10 | `jakarta.faces.*` | Facelets (JSP removed) |
| Jakarta Faces 4.1 | Jakarta EE 11 | `jakarta.faces.*` | Facelets |

Jakarta Faces 3.0 is a **pure package rename** of JSF 2.3. Jakarta Faces 4.0 removed deprecated APIs (JSP integration, `@ManagedBean`, old partial state saving). All examples in this skill use `jakarta.faces.*` with `javax.faces.*` noted where they differ.

---

## What JSF Is

JavaServer Faces is a **component-based MVC web framework** for Java EE / Jakarta EE. Key ideas:

- **Component model** — UI is a tree of `UIComponent` objects, not ad-hoc HTML generation
- **Event-driven** — user interactions fire events; beans handle them
- **Renderer separation** — components know nothing about HTML; renderers do the encoding/decoding
- **Managed beans** — plain Java objects wired into the page via EL expressions
- **Declarative navigation** — page flow defined in `faces-config.xml`, not hard-coded in code

JSF sits on top of the Servlet API. Every JSF request goes through `FacesServlet`.

---

## Development Process Overview (Ch 2)

Typical JSF development flow:

1. Define the **application's use cases** and page flow diagram
2. Create **managed beans** (backing beans) for each page/feature
3. Write **JSP pages** using JSF HTML and core tag libraries
4. Configure **navigation rules** in `faces-config.xml`
5. Register **validators, converters, listeners** as needed
6. Deploy as a standard WAR

Incremental approach: start with navigation skeleton (static outcomes), add bean logic, then add validation and events.

---

## Setting Up the Environment (Ch 3)

### Required JARs (JSF Reference Implementation)
```
jsf-api.jar      — public API (javax.faces.*)
jsf-impl.jar     — RI implementation
commons-beanutils.jar
commons-collections.jar
commons-digester.jar
commons-logging.jar
jstl.jar
standard.jar
```

### web.xml Configuration
```xml
<!-- FacesServlet — must handle all .jsf or /faces/* URLs -->
<servlet>
  <servlet-name>Faces Servlet</servlet-name>
  <servlet-class>javax.faces.webapp.FacesServlet</servlet-class>
  <load-on-startup>1</load-on-startup>
</servlet>

<servlet-mapping>
  <servlet-name>Faces Servlet</servlet-name>
  <url-pattern>*.jsf</url-pattern>
  <!-- or /faces/* -->
</servlet-mapping>
```

### faces-config.xml Location
Place in `WEB-INF/faces-config.xml`. JSF auto-discovers it. Additional config files can be listed via `javax.faces.CONFIG_FILES` context parameter.

### Context Parameters (web.xml)
| Parameter | Purpose | Example Value |
|-----------|---------|---------------|
| `javax.faces.STATE_SAVING_METHOD` | Where component state is saved | `server` (default) or `client` |
| `javax.faces.DEFAULT_SUFFIX` | Default view suffix | `.jsp` |
| `javax.faces.CONFIG_FILES` | Extra config files | `/WEB-INF/nav.xml` |

---

## Servlet and JSP Basics (Ch 4)

JSF builds on these — know them to debug JSF:

### Servlet Request/Response
- `HttpServletRequest` — carries form params, headers, session ref
- `HttpServletResponse` — writes response, sets headers
- `HttpSession` — per-user state store; JSF session-scope beans live here

### JSP and Tag Libraries
JSF pages are JSPs with custom tags. The JSF RI ships two tag libraries:
- `http://java.sun.com/jsf/html` → prefix `h:`
- `http://java.sun.com/jsf/core` → prefix `f:`

**Page template:**
```jsp
<%@ taglib uri="http://java.sun.com/jsf/html" prefix="h" %>
<%@ taglib uri="http://java.sun.com/jsf/core" prefix="f" %>
<f:view>
  <html>
    <body>
      <h:form>
        <h:inputText value="#{myBean.name}"/>
        <h:commandButton value="Submit" action="#{myBean.submit}"/>
      </h:form>
    </body>
  </html>
</f:view>
```

`<f:view>` is required — it marks the JSF component tree root.

### Expression Language (EL)
- Syntax: `#{expression}` (deferred, JSF-evaluated)
- Property access: `#{bean.property}` → calls `getProperty()`
- Method binding: `#{bean.actionMethod}` → called by JSF on action
- Nested: `#{bean.address.city}`
- Indexed: `#{bean.items[0]}`

---

## Managed Beans (Business Logic) (Ch 5)

### Declaring a Managed Bean
```xml
<!-- faces-config.xml -->
<managed-bean>
  <managed-bean-name>userBean</managed-bean-name>
  <managed-bean-class>com.example.UserBean</managed-bean-class>
  <managed-bean-scope>session</managed-bean-scope>
</managed-bean>
```

### Bean Scopes
| Scope | Lifetime | Stored In |
|-------|----------|-----------|
| `request` | Single HTTP request | Request attributes |
| `session` | User's session | HttpSession |
| `application` | App lifetime | ServletContext |
| `none` | Created per lookup, not stored | — |

### Typical Backing Bean Pattern
```java
public class UserBean {
    private String name;
    private String email;

    // Getters and setters required for EL access
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    // Action method — returns navigation outcome string
    public String register() {
        // business logic
        return "success"; // maps to a navigation rule
    }
}
```

### Managed Property Injection
Pre-populate bean properties from config:
```xml
<managed-bean>
  <managed-bean-name>configBean</managed-bean-name>
  <managed-bean-class>com.example.ConfigBean</managed-bean-class>
  <managed-bean-scope>application</managed-bean-scope>
  <managed-property>
    <property-name>maxRetries</property-name>
    <value>3</value>
  </managed-property>
</managed-bean>
```

Can also inject other managed beans:
```xml
<managed-property>
  <property-name>userBean</property-name>
  <value>#{userBean}</value>
</managed-property>
```

### Authentication Setup (Ch 5)
Use standard J2EE container-managed security declared in `web.xml`:

```xml
<security-constraint>
  <web-resource-collection>
    <web-resource-name>Protected Area</web-resource-name>
    <url-pattern>/secure/*</url-pattern>
  </web-resource-collection>
  <auth-constraint>
    <role-name>user</role-name>
  </auth-constraint>
</security-constraint>

<login-config>
  <auth-method>FORM</auth-method>
  <form-login-config>
    <form-login-page>/login.jsf</form-login-page>
    <form-error-page>/loginError.jsf</form-error-page>
  </form-login-config>
</login-config>
```

Use `request.getUserPrincipal()` and `request.isUserInRole()` in beans to check auth state. Access `FacesContext.getCurrentInstance().getExternalContext()` to reach the request from within a bean.

---

## FacesContext

The central object for the current request. Available anywhere via `FacesContext.getCurrentInstance()`:

```java
FacesContext ctx = FacesContext.getCurrentInstance();
ExternalContext ext = ctx.getExternalContext();
HttpServletRequest request = (HttpServletRequest) ext.getRequest();
ctx.addMessage(componentId, new FacesMessage("Error text"));
ctx.renderResponse();   // skip to Render Response phase
ctx.responseComplete(); // skip rendering entirely (redirect done)
```

---

## Common Pitfalls — Foundations

| Problem | Cause | Fix |
|---------|-------|-----|
| 404 on `.jsf` URL | Servlet mapping missing or wrong | Check `web.xml` url-pattern |
| Bean not found in EL | Bean not declared in `faces-config.xml` | Add `<managed-bean>` entry |
| `#{bean.prop}` returns null | Missing getter or typo | Verify getter name matches EL property |
| Session bean holding stale data | Previous session not invalidated | Call `session.invalidate()` on logout |
