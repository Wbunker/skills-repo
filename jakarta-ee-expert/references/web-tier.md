# Web Tier
*Chapters 7–11, 15 — Facelets, Custom Faces Components, Flows, WebSockets, Frontend, Jakarta MVC*

## Chapter 7: Facelets

Facelets is the standard view technology for Jakarta Faces 4. It uses XHTML — no JSP needed.

### Namespaces (Jakarta Faces 4.x)
```xhtml
<!-- Jakarta Faces 4.0+ (Jakarta EE 10) -->
xmlns:h="jakarta.faces.html"
xmlns:f="jakarta.faces.core"
xmlns:ui="jakarta.faces.facelets"
xmlns:c="jakarta.tags.core"

<!-- JSF 2.x / Jakarta Faces 3.x (still valid in EE 10 for compat) -->
xmlns:h="http://xmlns.jcp.org/jsf/html"
xmlns:f="http://xmlns.jcp.org/jsf/core"
xmlns:ui="http://xmlns.jcp.org/jsf/facelets"
```

### Page Template Pattern
**`/WEB-INF/templates/layout.xhtml`:**
```xhtml
<!DOCTYPE html>
<html xmlns:h="jakarta.faces.html"
      xmlns:ui="jakarta.faces.facelets">
<h:head>
  <title><ui:insert name="title">App</ui:insert></title>
  <h:outputStylesheet library="css" name="main.css"/>
</h:head>
<h:body>
  <header><h:outputText value="My App"/></header>
  <main>
    <ui:insert name="content">Default content</ui:insert>
  </main>
  <footer>© 2024</footer>
</h:body>
</html>
```

**`/views/users.xhtml`:**
```xhtml
<ui:composition template="/WEB-INF/templates/layout.xhtml"
                xmlns:ui="jakarta.faces.facelets"
                xmlns:h="jakarta.faces.html">
  <ui:define name="title">User List</ui:define>
  <ui:define name="content">
    <h:dataTable value="#{userBean.users}" var="u">
      <h:column><f:facet name="header">Name</f:facet>
        #{u.name}
      </h:column>
    </h:dataTable>
  </ui:define>
</ui:composition>
```

### `ui:` Tag Quick Reference
| Tag | Purpose |
|-----|---------|
| `ui:composition` | Page composition using a template |
| `ui:define` | Fills a named `ui:insert` slot |
| `ui:insert` | Defines a replaceable slot in a template |
| `ui:include` | Includes another Facelets file |
| `ui:repeat` | Loops over a collection without `UIData` |
| `ui:fragment` | Like `ui:component` but preserves surrounding content |
| `ui:param` | Passes parameter to included fragment |
| `ui:debug` | Dev-mode popup: component tree + scoped vars (hotkey Ctrl+Shift+D) |

### CDI Beans as Backing Beans (Jakarta EE 10 preferred)
```java
import jakarta.inject.Named;
import jakarta.faces.view.ViewScoped;
import java.io.Serializable;

@Named                   // EL name: #{userListBean}
@ViewScoped              // lives for the view lifetime; must be Serializable
public class UserListBean implements Serializable {
    @Inject private UserService userService;

    private List<User> users;

    @PostConstruct
    public void init() {
        users = userService.findAll();
    }

    public List<User> getUsers() { return users; }
}
```

### Scopes Summary
| Annotation | Package | Lifetime |
|-----------|---------|---------|
| `@RequestScoped` | `jakarta.enterprise.context` | Single HTTP request |
| `@SessionScoped` | `jakarta.enterprise.context` | User session |
| `@ApplicationScoped` | `jakarta.enterprise.context` | App lifetime |
| `@ViewScoped` | `jakarta.faces.view` | While user stays on view |
| `@ConversationScoped` | `jakarta.enterprise.context` | Explicitly demarcated |

---

## Chapter 8: Faces Custom Components

Composite components are the standard Jakarta Faces 4 approach — pure XHTML, no Java required.

### Composite Component
**`/resources/mycomp/ratingStars.xhtml`:**
```xhtml
<!DOCTYPE html>
<html xmlns:cc="jakarta.faces.composite"
      xmlns:h="jakarta.faces.html">
<h:head/>
<h:body>
  <cc:interface>
    <cc:attribute name="value"  type="java.lang.Integer" required="true"/>
    <cc:attribute name="max"    type="java.lang.Integer" default="5"/>
    <cc:attribute name="action" method-signature="java.lang.String action()"/>
  </cc:interface>
  <cc:implementation>
    <span id="#{cc.clientId}" class="stars">
      <ui:repeat var="i" value="#{mycomp:range(cc.attrs.max)}">
        <span class="#{i le cc.attrs.value ? 'filled' : 'empty'}">★</span>
      </ui:repeat>
    </span>
  </cc:implementation>
</h:body>
</html>
```

**Usage:**
```xhtml
<html xmlns:mycomp="jakarta.faces.composite/mycomp">
  <mycomp:ratingStars value="#{product.rating}" max="5"/>
```

### Java-Based Custom Component (advanced)
```java
@FacesComponent("com.example.BadgeComponent")
public class BadgeComponent extends UIOutput {
    @Override
    public void encodeEnd(FacesContext ctx) throws IOException {
        ResponseWriter w = ctx.getResponseWriter();
        w.startElement("span", this);
        w.writeAttribute("class", "badge badge-" + getAttributes().get("severity"), null);
        w.writeText(getValue(), "value");
        w.endElement("span");
    }
}
```

Register in Facelets taglib `/WEB-INF/mylib.taglib.xml`:
```xml
<facelet-taglib>
  <namespace>http://example.com/mylib</namespace>
  <tag>
    <tag-name>badge</tag-name>
    <component>
      <component-type>com.example.BadgeComponent</component-type>
    </component>
  </tag>
</facelet-taglib>
```

---

## Chapter 9: Flows

Jakarta Faces Flows group multiple pages into a named unit — ideal for wizards and multi-step forms. State is scoped to the flow.

### Flow Scope
`@FlowScoped("registrationFlow")` beans live only during that flow.

```java
@Named
@FlowScoped("registrationFlow")
public class RegistrationFlowBean implements Serializable {
    private String email;
    private String password;
    private Address address;
    // getters/setters
}
```

### Defining a Flow (CDI Producer)
```java
@Produces
@FlowDefinition
public Flow defineRegistrationFlow(FlowBuilder b) {
    b.id("", "registrationFlow");
    b.viewNode("step1", "/flow/step1.xhtml").markAsStartNode();
    b.viewNode("step2", "/flow/step2.xhtml");
    b.viewNode("step3", "/flow/step3.xhtml");
    b.returnNode("flowReturn").fromOutcome("/index");
    b.navigationCase().fromViewId("/flow/step1.xhtml")
        .fromOutcome("next").toViewId("/flow/step2.xhtml");
    b.navigationCase().fromViewId("/flow/step2.xhtml")
        .fromOutcome("next").toViewId("/flow/step3.xhtml");
    b.navigationCase().fromViewId("/flow/step3.xhtml")
        .fromOutcome("finish").toFlowCallNode("flowReturn");
    return b.getFlow();
}
```

### Defining a Flow (XML — `registrationFlow-flow.xml` in flow folder)
```xml
<faces-config>
  <flow-definition id="registrationFlow">
    <start-node>step1</start-node>
    <view><vdi-node>step1</vdi-node><vdi-id>/flow/step1.xhtml</vdi-id></view>
    <view><vdi-node>step2</vdi-node><vdi-id>/flow/step2.xhtml</vdi-id></view>
    <navigation-rule>
      <from-view-id>/flow/step1.xhtml</from-view-id>
      <navigation-case><from-outcome>next</from-outcome>
        <to-view-id>/flow/step2.xhtml</to-view-id></navigation-case>
    </navigation-rule>
    <flow-return><id>flowReturn</id>
      <from-outcome>/index</from-outcome></flow-return>
  </flow-definition>
</faces-config>
```

**Entering a flow:**
```xhtml
<h:button value="Start Registration" outcome="registrationFlow"/>
```

---

## Chapter 10: WebSockets

Jakarta WebSocket 2.1 provides full-duplex communication.

### Server Endpoint
```java
import jakarta.websocket.*;
import jakarta.websocket.server.ServerEndpoint;

@ServerEndpoint("/chat/{room}")
public class ChatEndpoint {
    private static final Map<String, Set<Session>> rooms = new ConcurrentHashMap<>();

    @OnOpen
    public void onOpen(Session session, @PathParam("room") String room) {
        rooms.computeIfAbsent(room, k -> ConcurrentHashMap.newKeySet()).add(session);
        broadcast(room, "User joined: " + session.getId());
    }

    @OnMessage
    public void onMessage(String message, @PathParam("room") String room) {
        broadcast(room, message);
    }

    @OnClose
    public void onClose(Session session, @PathParam("room") String room) {
        rooms.getOrDefault(room, Set.of()).remove(session);
    }

    @OnError
    public void onError(Throwable error, Session session) {
        System.err.println("WebSocket error: " + error.getMessage());
    }

    private void broadcast(String room, String msg) {
        rooms.getOrDefault(room, Set.of()).forEach(s -> {
            try { s.getBasicRemote().sendText(msg); }
            catch (IOException e) { /* handle */ }
        });
    }
}
```

### WebSocket with CDI (Injecting Beans)
`@ServerEndpoint` instances are not CDI beans by default. Use `ServerEndpointConfig.Configurator`:
```java
public class CdiConfigurator extends ServerEndpointConfig.Configurator {
    @Override
    public <T> T getEndpointInstance(Class<T> endpointClass) {
        CDI<Object> cdi = CDI.current();
        return cdi.select(endpointClass).get();
    }
}

@ServerEndpoint(value="/chat", configurator=CdiConfigurator.class)
@ApplicationScoped
public class ChatEndpoint { @Inject ChatService chatService; ... }
```

### JavaScript Client
```javascript
const ws = new WebSocket("ws://localhost:8080/myapp/chat/general");

ws.onopen = () => ws.send("Hello!");
ws.onmessage = (event) => console.log("Received:", event.data);
ws.onclose = () => console.log("Connection closed");
ws.onerror = (error) => console.error("Error:", error);
```

### Faces Push (`<f:websocket>`) — JSF/Faces integration
```xhtml
<f:websocket channel="notifications" onmessage="handleNotification"/>
<script>
  function handleNotification(message) {
    document.getElementById("msg").textContent = message;
  }
</script>
<span id="msg"></span>
```

```java
@Named @SessionScoped
public class NotificationBean implements Serializable {
    @Inject @Push private PushContext notifications;

    public void sendAlert(String message) {
        notifications.send(message);
    }
}
```

---

## Chapter 11: Frontend Technologies

### Serving Static Resources (Jakarta Faces Resource Library)
```
src/main/webapp/resources/
├── css/main.css
├── js/app.js
└── img/logo.png
```

```xhtml
<h:outputStylesheet library="css" name="main.css"/>
<h:outputScript     library="js"  name="app.js" target="head"/>
<h:graphicImage     library="img" name="logo.png"/>
```

Versioned resources: put them under `resources/v1.0/css/main.css` and use `library="v1.0"`.

### PrimeFaces Integration (premier Jakarta Faces component library)
```xml
<dependency>
  <groupId>org.primefaces</groupId>
  <artifactId>primefaces</artifactId>
  <version>13.0.0</version>
  <classifier>jakarta</classifier>
</dependency>
```

```xhtml
<html xmlns:p="http://primefaces.org/ui">
  <p:dataTable value="#{bean.items}" var="item"
               paginator="true" rows="10"
               sortMode="multiple">
    <p:column headerText="Name" sortBy="#{item.name}">
      #{item.name}
    </p:column>
  </p:dataTable>
  <p:chart type="bar" model="#{chartBean.model}"/>
```

### JavaScript Frameworks with Jakarta REST Backend
For SPA frontends (React, Vue, Angular), use Jakarta REST as the API layer. The Jakarta EE server serves the SPA's static files or a separate CDN hosts them.

```javascript
// React fetching from Jakarta REST endpoint
const response = await fetch('/api/users', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const users = await response.json();
```

---

## Chapter 15: Jakarta MVC

Jakarta MVC 2.1 is an **action-based** web framework (like Spring MVC) that complements component-based Jakarta Faces. Built on Jakarta REST.

### Controller
```java
import jakarta.mvc.Controller;
import jakarta.mvc.Models;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;

@Controller
@Path("/users")
public class UserController {

    @Inject private Models models;
    @Inject private UserService userService;

    @GET
    @View("users/list.xhtml")   // Facelets or JSP view
    public void listUsers() {
        models.put("users", userService.findAll());
    }

    @GET
    @Path("{id}")
    @View("users/detail.xhtml")
    public void getUser(@PathParam("id") Long id) {
        models.put("user", userService.findById(id));
    }

    @POST
    @Consumes(MediaType.APPLICATION_FORM_URLENCODED)
    public Response createUser(@BeanParam @Valid UserForm form,
                               BindingResult bindingResult) {
        if (bindingResult.isFailed()) {
            models.put("errors", bindingResult.getAllErrors());
            return Response.status(422).entity("users/create.xhtml").build();
        }
        userService.create(form.toUser());
        return Response.seeOther(URI.create("/users")).build();
    }
}
```

### Model and View
```java
// Form bean with Bean Validation
public class UserForm {
    @NotBlank @FormParam("name")  public String name;
    @Email    @FormParam("email") public String email;
}
```

```xhtml
<!-- users/list.xhtml — uses EL to access Models map -->
<h:dataTable value="#{users}" var="u">
  <h:column>#{u.name}</h:column>
</h:dataTable>
```

### MVC Configuration
```java
@ApplicationPath("/mvc")
public class MvcApplication extends Application {}
```

### MVC vs. Faces — When to Choose
| Concern | Jakarta Faces | Jakarta MVC |
|---------|--------------|-------------|
| State management | Built-in component tree | Stateless (REST-style) |
| Navigation | Faces navigation rules | HTTP redirects / response |
| URL style | Extension-based (.xhtml) | Clean RESTful URLs |
| AJAX | `<f:ajax>` / PrimeFaces | Custom JS + REST calls |
| Learning curve | Higher (lifecycle) | Lower (standard HTTP) |
| Best for | Complex stateful UIs | Simple CRUD + REST APIs |

---

## Common Web Tier Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| `@ViewScoped` bean loses state | Not `Serializable` | Implement `Serializable` |
| Template not found | Wrong path in `template=` | Use absolute path from webapp root |
| Composite component not found | Namespace doesn't match folder | Namespace suffix = folder name under resources/ |
| WebSocket 403 | CORS/origin check | Configure `ServerEndpointConfig` origins |
| WebSocket state lost | Endpoint not `@ApplicationScoped` | Add scope annotation + CDI configurator |
| MVC view not rendering | `@View` and return type mismatch | Use `void` return with `@View` or `String` return |
