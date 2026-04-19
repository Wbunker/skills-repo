# Faces, EL, and Navigation
*Chapters 4–10 (Zambon) — Jakarta Faces Basics, Expression Language, Validation, Navigation, Data Tables, AJAX*

## Chapter 4: Jakarta Faces Basics

Faces is the component-based web framework in Jakarta EE. Pages are XHTML; backing beans are CDI beans annotated with `@Named`.

### Enabling Faces in a Project

**`WEB-INF/web.xml`** (required to map the Faces servlet):
```xml
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee" version="6.0">
  <servlet>
    <servlet-name>Faces Servlet</servlet-name>
    <servlet-class>jakarta.faces.webapp.FacesServlet</servlet-class>
    <load-on-startup>1</load-on-startup>
  </servlet>
  <servlet-mapping>
    <servlet-name>Faces Servlet</servlet-name>
    <url-pattern>*.xhtml</url-pattern>
  </servlet-mapping>
  <welcome-file-list>
    <welcome-file>index.xhtml</welcome-file>
  </welcome-file-list>
</web-app>
```

Or use `@FacesConfig` in a CDI bean to activate Faces without web.xml mapping:
```java
@FacesConfig
@ApplicationScoped
public class FacesConfiguration {}
```

### Simplest Faces Page

**`src/main/webapp/hello.xhtml`:**
```xhtml
<!DOCTYPE html>
<html xmlns:h="jakarta.faces.html"
      xmlns:f="jakarta.faces.core">
<h:head>
  <title>Hello Faces</title>
</h:head>
<h:body>
  <h:form>
    <h:outputLabel for="name" value="Your name:"/>
    <h:inputText id="name" value="#{helloBean.name}" required="true"/>
    <h:commandButton value="Submit" action="#{helloBean.greet}"/>
  </h:form>
  <h:outputText value="#{helloBean.greeting}" rendered="#{not empty helloBean.greeting}"/>
</h:body>
</html>
```

**Backing Bean:**
```java
package com.example;

import jakarta.inject.Named;
import jakarta.enterprise.context.RequestScoped;

@Named               // EL name: #{helloBean}
@RequestScoped
public class HelloBean {
    private String name;
    private String greeting;

    public String greet() {
        greeting = "Hello, " + name + "!";
        return null;   // null = stay on same page
    }

    // getters and setters required for EL
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getGreeting() { return greeting; }
}
```

### h: Component Quick Reference

| Component | Purpose | Key Attributes |
|-----------|---------|----------------|
| `h:form` | HTML form with Faces lifecycle | `id`, `prependId` |
| `h:inputText` | Text input | `value`, `id`, `required`, `disabled`, `size`, `maxlength` |
| `h:inputSecret` | Password input | `value`, `redisplay` |
| `h:inputTextarea` | Multi-line text | `value`, `rows`, `cols` |
| `h:inputHidden` | Hidden field | `value` |
| `h:selectOneMenu` | Dropdown | `value`, `converter` |
| `h:selectManyCheckbox` | Multi-select checkboxes | `value`, `layout` |
| `h:selectBooleanCheckbox` | Single checkbox | `value` |
| `h:commandButton` | Submit button | `value`, `action`, `actionListener`, `type` |
| `h:commandLink` | Submit as link | `value`, `action` |
| `h:button` | Navigation button (GET) | `value`, `outcome` |
| `h:link` | Navigation link (GET) | `value`, `outcome` |
| `h:outputText` | Text output | `value`, `rendered`, `escape` |
| `h:outputLabel` | Form label | `value`, `for` |
| `h:dataTable` | HTML table from collection | `value`, `var` |
| `h:column` | Column in dataTable | `headerText`, `footerText` |
| `h:panelGroup` | Groups components | `layout` (`block`/`inline`) |
| `h:messages` | All validation messages | `globalOnly`, `showDetail` |
| `h:message` | Message for one field | `for` |
| `h:outputStylesheet` | CSS link | `library`, `name` |
| `h:outputScript` | JS script tag | `library`, `name`, `target` |
| `h:graphicImage` | Image tag | `library`, `name` |

---

## Chapter 5: Expression Language (EL)

EL (`#{...}`) connects Facelets pages to backing beans.

### EL Syntax

```xhtml
<!-- Property access -->
#{userBean.name}               <!-- calls getUserName() -->
#{userBean.address.city}       <!-- chained: getAddress().getCity() -->
#{userBean.items[0]}           <!-- list by index -->
#{userBean.map['key']}         <!-- map by key -->

<!-- Method calls (EL 3.0+) -->
#{userBean.greet('Alice')}     <!-- method with argument -->
#{userBean.findById(item.id)}  <!-- expression as argument -->

<!-- Arithmetic -->
#{price * quantity}
#{total + tax}
#{items.size() * 1.1}

<!-- Comparison -->
#{user.age >= 18}
#{status == 'ACTIVE'}
#{user.role eq 'admin'}        <!-- eq/ne/lt/gt/le/ge are word forms -->

<!-- Logical -->
#{user.admin and user.active}
#{not user.locked}
#{empty user.name}             <!-- true if null or empty string/collection -->

<!-- Conditional (ternary) -->
#{user.premium ? 'Gold' : 'Standard'}

<!-- Implicit objects -->
#{param.id}                    <!-- request parameter -->
#{sessionScope.user}           <!-- session attribute -->
#{requestScope.error}          <!-- request attribute -->
#{applicationScope.config}     <!-- app attribute -->
#{initParam['app.name']}       <!-- context-param from web.xml -->
#{facesContext}                <!-- current FacesContext -->
#{component}                   <!-- current UIComponent -->
```

### EL Functions (JSTL fn:)
```xhtml
<%@ taglib uri="http://java.sun.com/jsp/jstl/functions" prefix="fn" %>
<!-- In Facelets: -->
<html xmlns:fn="jakarta.tags.functions">

#{fn:length(list)}             <!-- list/string length -->
#{fn:toUpperCase(name)}
#{fn:contains(str, 'foo')}
#{fn:substring(str, 0, 5)}
#{fn:replace(str, ' ', '_')}
#{fn:split(csv, ',')}
#{fn:join(array, ', ')}
```

---

## Chapter 6: Facelets Templates

See `web-tier.md` for the full Facelets template reference. Quick summary:

| Tag | Purpose |
|-----|---------|
| `ui:composition template="..."` | Page using a layout template |
| `ui:define name="..."` | Fills a slot in the template |
| `ui:insert name="..."` | Defines a replaceable slot |
| `ui:include src="..."` | Embeds another XHTML fragment |
| `ui:repeat var="x" value="#{list}"` | Iteration without UIData |

---

## Chapter 7: Validation and Conversion

### Built-in Validators

```xhtml
<h:inputText value="#{bean.email}" required="true"
             requiredMessage="Email is required">
  <f:validateLength minimum="5" maximum="100"/>
  <f:validateRegex pattern="[^@]+@[^@]+\.[^@]+"
                   message="Invalid email format"/>
</h:inputText>

<h:inputText value="#{bean.age}" converter="jakarta.faces.Integer">
  <f:validateLongRange minimum="18" maximum="120"/>
</h:inputText>

<h:inputText value="#{bean.price}" converter="jakarta.faces.Double">
  <f:validateDoubleRange minimum="0.01"/>
</h:inputText>

<!-- Cross-field: validate two fields equal -->
<h:inputSecret id="pass"     value="#{bean.password}"/>
<h:inputSecret id="confirm"  value="#{bean.confirmPassword}">
  <f:validator validatorId="passwordMatch"/>
  <f:attribute name="targetId" value="pass"/>
</h:inputSecret>
```

### Displaying Validation Messages

```xhtml
<!-- All messages -->
<h:messages showSummary="true" showDetail="false" globalOnly="false"/>

<!-- Message for specific component -->
<h:message for="email" style="color:red"/>
<h:inputText id="email" value="#{bean.email}" required="true"/>
```

### Custom Validator

```java
@FacesValidator("passwordMatch")
public class PasswordMatchValidator implements Validator<String> {
    @Override
    public void validate(FacesContext ctx, UIComponent comp, String value)
            throws ValidatorException {

        String targetId = (String) comp.getAttributes().get("targetId");
        UIInput target = (UIInput) comp.findComponent(targetId);
        String targetValue = (String) target.getLocalValue();

        if (!value.equals(targetValue)) {
            throw new ValidatorException(
                new FacesMessage(FacesMessage.SEVERITY_ERROR,
                    "Passwords must match", null));
        }
    }
}
```

### Converters

```xhtml
<!-- Built-in: number/date formatting -->
<h:outputText value="#{bean.price}">
  <f:convertNumber type="currency" currencySymbol="$"/>
</h:outputText>

<h:outputText value="#{bean.birthDate}">
  <f:convertDateTime pattern="yyyy-MM-dd"/>
</h:outputText>

<!-- Custom converter -->
<h:inputText value="#{bean.user}" converter="userConverter"/>
```

```java
@FacesConverter("userConverter")
public class UserConverter implements Converter<User> {
    @Inject UserService userService;   // @FacesConverter(managed=true) for CDI

    @Override
    public User getAsObject(FacesContext ctx, UIComponent comp, String value) {
        if (value == null || value.isBlank()) return null;
        return userService.findById(Long.parseLong(value));
    }

    @Override
    public String getAsString(FacesContext ctx, UIComponent comp, User user) {
        return user == null ? "" : String.valueOf(user.getId());
    }
}
```

---

## Chapter 8: Navigation and Bookmarking

### Implicit Navigation

Return a string from an action method — Faces resolves it to a view:
```java
// Returns "success" → loads /success.xhtml
public String save() {
    userService.save(user);
    return "success";
}

// Redirect (avoids duplicate POST on back button)
public String save() {
    userService.save(user);
    return "success?faces-redirect=true";
}

// Conditional navigation
public String login() {
    if (authService.authenticate(username, password)) {
        return "dashboard?faces-redirect=true";
    } else {
        addMessage("Invalid credentials");
        return null;   // stay on current page
    }
}
```

### Adding a FacesMessage Programmatically

```java
private void addMessage(String text) {
    FacesContext.getCurrentInstance().addMessage(null,
        new FacesMessage(FacesMessage.SEVERITY_ERROR, text, null));
}
```

### Bookmarkable URLs (View Parameters + GET)

Allow pages to be bookmarked and deep-linked with parameters in the URL.

**`/user-detail.xhtml`:**
```xhtml
<f:metadata>
  <f:viewParam name="id" value="#{userBean.userId}"/>
  <f:viewAction action="#{userBean.loadUser}"/>
</f:metadata>
...
<h:link value="View User" outcome="user-detail">
  <f:param name="id" value="#{u.id}"/>
</h:link>
```

```java
@Named @ViewScoped
public class UserBean implements Serializable {
    private Long userId;
    private User user;

    public void loadUser() {
        if (userId != null) user = userService.findById(userId);
    }
    // getters/setters
}
```

URL: `http://localhost:8080/myapp/user-detail.xhtml?id=42`

### Explicit Navigation Rules (`faces-config.xml`)

```xml
<faces-config xmlns="https://jakarta.ee/xml/ns/jakartaee" version="4.0">
  <navigation-rule>
    <from-view-id>/login.xhtml</from-view-id>
    <navigation-case>
      <from-outcome>success</from-outcome>
      <to-view-id>/dashboard.xhtml</to-view-id>
      <redirect/>
    </navigation-case>
    <navigation-case>
      <from-outcome>failure</from-outcome>
      <to-view-id>/login.xhtml</to-view-id>
    </navigation-case>
  </navigation-rule>
</faces-config>
```

---

## Chapter 9: Data Tables

### Basic `h:dataTable`

```xhtml
<h:dataTable value="#{productBean.products}" var="p"
             styleClass="table" rowClasses="odd,even"
             headerClass="table-header">

  <h:column>
    <f:facet name="header">Name</f:facet>
    <h:outputText value="#{p.name}"/>
  </h:column>

  <h:column>
    <f:facet name="header">Price</f:facet>
    <h:outputText value="#{p.price}">
      <f:convertNumber type="currency" currencySymbol="$"/>
    </h:outputText>
  </h:column>

  <h:column>
    <f:facet name="header">Actions</f:facet>
    <h:commandLink value="Edit" action="#{productBean.edit(p)}"/>
    &nbsp;
    <h:commandLink value="Delete"
                   action="#{productBean.delete(p)}"
                   onclick="return confirm('Delete?')"/>
  </h:column>

</h:dataTable>
```

### Backing Bean Pattern for Tables

```java
@Named @ViewScoped
public class ProductBean implements Serializable {

    @Inject private ProductService productService;

    private List<Product> products;
    private Product selected;

    @PostConstruct
    public void init() {
        products = productService.findAll();
    }

    public String edit(Product p) {
        selected = p;
        return null;   // stay on page; open edit panel
    }

    public void delete(Product p) {
        productService.delete(p.getId());
        products.remove(p);
        FacesContext.getCurrentInstance().addMessage(null,
            new FacesMessage("Product deleted."));
    }

    public List<Product> getProducts() { return products; }
    public Product getSelected() { return selected; }
}
```

### Sortable Table (manual sort)

```java
private String sortField = "name";
private boolean sortAscending = true;

public void sortBy(String field) {
    if (field.equals(sortField)) {
        sortAscending = !sortAscending;
    } else {
        sortField = field;
        sortAscending = true;
    }
    products.sort(Comparator.comparing(
        p -> getFieldValue(p, sortField),
        sortAscending ? Comparator.naturalOrder() : Comparator.reverseOrder()));
}
```

```xhtml
<h:column>
  <f:facet name="header">
    <h:commandLink action="#{productBean.sortBy('name')}" value="Name"/>
  </f:facet>
  #{p.name}
</h:column>
```

---

## Chapter 10: AJAX with `f:ajax`

### Partial Page Update

```xhtml
<h:form>
  <h:inputText id="query" value="#{searchBean.query}">
    <f:ajax event="keyup" render="results" delay="300"
            listener="#{searchBean.search}"/>
  </h:inputText>

  <h:dataTable id="results" value="#{searchBean.results}" var="r">
    <h:column>#{r.name}</h:column>
  </h:dataTable>
</h:form>
```

```java
@Named @ViewScoped
public class SearchBean implements Serializable {
    private String query;
    private List<Product> results = new ArrayList<>();

    @Inject private ProductService productService;

    public void search() {
        results = productService.search(query);
    }

    // getters/setters
}
```

### AJAX on Button Click

```xhtml
<h:commandButton value="Add to Cart" action="#{cartBean.add(product)}">
  <f:ajax execute="@this" render="cartCount messages" onevent="cartUpdated"/>
</h:commandButton>
<h:outputText id="cartCount" value="#{cartBean.itemCount}"/>
<h:messages id="messages"/>

<script>
function cartUpdated(data) {
  if (data.status === 'success') {
    document.getElementById('flash').style.display = 'block';
  }
}
</script>
```

### `f:ajax` Attribute Reference

| Attribute | Values | Purpose |
|-----------|--------|---------|
| `event` | `click`, `change`, `keyup`, `blur`, etc. | Trigger event (default: `action` for buttons, `valueChange` for inputs) |
| `execute` | `@this`, `@form`, `@all`, `@none`, id list | Which components to process (submit data) |
| `render` | `@this`, `@form`, `@all`, `@none`, id list | Which components to re-render after response |
| `listener` | `#{bean.method}` | Server-side `AjaxBehaviorEvent` listener |
| `delay` | milliseconds | Debounce: wait before firing (useful for `keyup` search) |
| `onevent` | JS function name | Client callback on request lifecycle events |
| `onerror` | JS function name | Client callback on error |
| `disabled` | `true`/`false` | Disable AJAX behavior |

---

## Common Faces Issues (Beginner)

| Problem | Cause | Fix |
|---------|-------|-----|
| Page not found after action | Implicit navigation wrong | View filename must match outcome string + `.xhtml` |
| Validation errors not shown | No `h:messages` or `h:message` | Add `<h:messages/>` to page |
| Bean value not updated | Missing setter | Add `setPropertyName()` method |
| `@ViewScoped` bean resets | Not `Serializable` | Implement `java.io.Serializable` |
| AJAX render not updating | Wrong component id | Ensure `id` on target component; check for `form:` prefix prepending |
| Converter error on select | No converter for entity type | Register `@FacesConverter(managed=true)` + CDI injection |
| 500 on submit | `@PostConstruct` fails | Check server log; avoid DB calls during construction if CDI not yet ready |
| `#{bean}` is null | `@Named` missing or wrong scope | Verify annotation; use `@RequestScoped` if unsure |
