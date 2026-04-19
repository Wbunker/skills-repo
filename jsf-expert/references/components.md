# JSF Components and Rendering
*Chapter 6 — Creating and Rendering Components*

## The Component Model

Every JSF page is backed by a tree of `UIComponent` objects assembled at request time. Understanding this tree is fundamental to understanding JSF behavior.

```
UIViewRoot
└── UIForm  (h:form)
    ├── UIInput  (h:inputText)   — bound to #{bean.name}
    ├── UIMessage  (h:message)   — shows errors for UIInput
    └── UICommand  (h:commandButton) — action=#{bean.submit}
```

### UIComponent Hierarchy (Standard Components)
| Class | Tag | Purpose |
|-------|-----|---------|
| `UIViewRoot` | `<f:view>` / implicit in Facelets | Root of component tree |
| `UIForm` | `h:form` | HTML `<form>` |
| `UIInput` | `h:inputText`, `h:inputSecret`, `h:inputHidden`, `h:inputTextarea` | Text inputs |
| `UIOutput` | `h:outputText`, `h:outputLabel`, `h:outputLink` | Read-only output |
| `UICommand` | `h:commandButton`, `h:commandLink` | Submits form / fires action |
| `UISelectOne` | `h:selectOneMenu`, `h:selectOneListbox`, `h:selectOneRadio` | Single-select |
| `UISelectMany` | `h:selectManyCheckbox`, `h:selectManyListbox` | Multi-select |
| `UISelectBoolean` | `h:selectBooleanCheckbox` | Boolean checkbox |
| `UIData` | `h:dataTable` | Iterates over data model |
| `UIPanel` | `h:panelGrid`, `h:panelGroup` | Layout panels |
| `UIGraphic` | `h:graphicImage` | `<img>` |
| `UIMessage` | `h:message` | Per-component error messages |
| `UIMessages` | `h:messages` | All error messages |

---

## The HTML Tag Library (`h:`)

### Input Components
```jsp
<!-- Text input bound to bean property -->
<h:inputText id="name" value="#{userBean.name}" required="true"
             size="30" maxlength="50"/>

<!-- Password (rendered as type="password") -->
<h:inputSecret value="#{loginBean.password}"/>

<!-- Textarea -->
<h:inputTextarea value="#{bean.description}" rows="5" cols="40"/>

<!-- Hidden field -->
<h:inputHidden value="#{bean.token}"/>
```

### Output Components
```jsp
<h:outputText value="#{bean.message}" escape="true"/>
<h:outputLabel for="name" value="Full Name:"/>
<h:outputLink value="http://example.com">Click here</h:outputLink>
```

### Command Components (trigger actions)
```jsp
<!-- Submits form, calls action method -->
<h:commandButton value="Save" action="#{userBean.save}"/>

<!-- Link that submits form -->
<h:commandLink value="Delete" action="#{bean.delete}"/>
```

### Select Components
```jsp
<!-- Single-select dropdown -->
<h:selectOneMenu value="#{bean.country}">
  <f:selectItem itemValue="US" itemLabel="United States"/>
  <f:selectItem itemValue="GB" itemLabel="United Kingdom"/>
  <!-- Or populate from bean: -->
  <f:selectItems value="#{bean.countryList}"/>
</h:selectOneMenu>

<!-- Radio buttons -->
<h:selectOneRadio value="#{bean.size}" layout="pageDirection">
  <f:selectItem itemValue="S" itemLabel="Small"/>
  <f:selectItem itemValue="M" itemLabel="Medium"/>
  <f:selectItem itemValue="L" itemLabel="Large"/>
</h:selectOneRadio>

<!-- Multi-select checkboxes -->
<h:selectManyCheckbox value="#{bean.selectedColors}">
  <f:selectItems value="#{bean.colorList}"/>
</h:selectManyCheckbox>
```

### Panel/Layout Components
```jsp
<!-- Grid layout (like HTML table) -->
<h:panelGrid columns="2">
  <h:outputLabel for="email" value="Email:"/>
  <h:inputText id="email" value="#{bean.email}"/>
</h:panelGrid>

<!-- Group without additional HTML -->
<h:panelGroup>
  <h:outputText value="Hello, "/>
  <h:outputText value="#{bean.name}"/>
</h:panelGroup>
```

### Message Components
```jsp
<!-- Error message for one specific component (by id) -->
<h:message for="email" style="color:red"/>

<!-- All error messages on the page -->
<h:messages globalOnly="false" showSummary="true" showDetail="false"/>
```

---

## The Core Tag Library (`f:`)

Non-rendering tags that add behavior to components:

| Tag | Purpose |
|-----|---------|
| `<f:view>` | JSP: wraps entire JSF content (not needed in Facelets) |
| `<f:subview>` | JSP: includes another JSF view fragment |
| `<f:verbatim>` | JSP: output raw HTML inside JSF tree |
| `<f:param>` | Adds a parameter to parent component |
| `<f:attribute>` | Sets an attribute on parent component |
| `<f:converter>` | Attaches a converter to parent input |
| `<f:convertNumber>` | Built-in number converter |
| `<f:convertDateTime>` | Built-in date/time converter |
| `<f:validator>` | Attaches a validator to parent input |
| `<f:validateLength>` | Built-in length validator |
| `<f:validateLongRange>` | Built-in integer range validator |
| `<f:validateDoubleRange>` | Built-in double range validator |
| `<f:valueChangeListener>` | Attaches a ValueChangeListener |
| `<f:actionListener>` | Attaches an ActionListener |
| `<f:loadBundle>` | Loads a resource bundle into EL scope |
| `<f:selectItem>` | One item for select components |
| `<f:selectItems>` | Collection of items for select components |
| `<f:facet>` | Named facet (header/footer for dataTable) |
| `<f:ajax>` | JSF 2+: partial page update / AJAX |

---

## Renderers

A `Renderer` handles two jobs:
1. **decode** — extracts submitted value from HTTP request
2. **encode** — writes HTML to the response

Renderers are grouped in a **RenderKit**. The default HTML render kit ID is `HTML_BASIC`.

Every standard component has a default renderer. The `rendererType` attribute of `UIComponent` determines which `Renderer` handles it.

### Component + Renderer Pairing (examples)
| Component | Renderer Type | Tag |
|-----------|--------------|-----|
| `UIInput` | `Text` | `h:inputText` |
| `UIInput` | `Secret` | `h:inputSecret` |
| `UICommand` | `Button` | `h:commandButton` |
| `UICommand` | `Link` | `h:commandLink` |
| `UISelectOne` | `Menu` | `h:selectOneMenu` |
| `UISelectOne` | `Radio` | `h:selectOneRadio` |

---

## Converters

Converters translate between `String` (HTTP request) and Java objects (bean properties). They run during Apply Request Values and Render Response.

### Built-in Converters
```jsp
<!-- Number: locale-aware, supports pattern, type (number/currency/percent) -->
<h:outputText value="#{bean.price}">
  <f:convertNumber type="currency" currencySymbol="$"/>
</h:outputText>

<h:inputText value="#{bean.quantity}">
  <f:convertNumber integerOnly="true" minimum="1" maximum="999"/>
</h:inputText>

<!-- Date/Time -->
<h:outputText value="#{bean.birthDate}">
  <f:convertDateTime pattern="MM/dd/yyyy"/>
</h:outputText>

<h:inputText value="#{bean.eventDate}">
  <f:convertDateTime type="date" dateStyle="short"/>
</h:inputText>
```

### Custom Converter
```java
// Classic JSF
import javax.faces.convert.Converter;
// Jakarta Faces
import jakarta.faces.convert.Converter;
import jakarta.faces.convert.FacesConverter;

@FacesConverter("myConverter")   // JSF 2+ / Jakarta Faces annotation
public class ColorConverter implements Converter<Color> {
    @Override
    public Color getAsObject(FacesContext ctx, UIComponent comp, String value) {
        return Color.decode(value);  // String → Object
    }
    @Override
    public String getAsString(FacesContext ctx, UIComponent comp, Color value) {
        return String.format("#%06X", value.getRGB() & 0xFFFFFF);  // Object → String
    }
}
```

Register in `faces-config.xml` (or use `@FacesConverter` annotation):
```xml
<converter>
  <converter-id>myConverter</converter-id>
  <converter-class>com.example.ColorConverter</converter-class>
</converter>
```

Use on a component:
```jsp
<h:inputText value="#{bean.color}">
  <f:converter converterId="myConverter"/>
</h:inputText>
```

---

## Facelets (JSF 2+ / Jakarta Faces — preferred over JSP)

Facelets use XHTML, not JSP. No `<f:view>` needed; the whole XHTML document is the view.

```xhtml
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:h="http://xmlns.jcp.org/jsf/html"
      xmlns:f="http://xmlns.jcp.org/jsf/core">
<!-- Jakarta Faces namespaces: -->
<!-- xmlns:h="jakarta.faces.html"  xmlns:f="jakarta.faces.core" -->
<h:head>
  <title>My Page</title>
</h:head>
<h:body>
  <h:form>
    <h:inputText value="#{userBean.name}"/>
    <h:commandButton value="Submit" action="#{userBean.submit}"/>
  </h:form>
</h:body>
</html>
```

Facelets templating:
```xhtml
<!-- template.xhtml -->
<html xmlns:ui="http://xmlns.jcp.org/jsf/facelets">
<h:head><title><ui:insert name="title">Default</ui:insert></title></h:head>
<h:body>
  <div id="content"><ui:insert name="content"/></div>
</h:body>
</html>

<!-- page.xhtml -->
<ui:composition template="/template.xhtml">
  <ui:define name="title">My Page</ui:define>
  <ui:define name="content">
    <h:form>...</h:form>
  </ui:define>
</ui:composition>
```

---

## Jakarta Faces: Key Changes vs. Classic JSF

| Concern | Classic JSF | Jakarta Faces (EE 9+) |
|---------|------------|----------------------|
| Package | `javax.faces.*` | `jakarta.faces.*` |
| View technology | JSP (`.jsp`) | Facelets (`.xhtml`) default |
| Managed beans | `faces-config.xml` + `@ManagedBean` | CDI: `@Named` + scope annotation |
| Converter registration | `faces-config.xml` | `@FacesConverter(managed=true)` + CDI |
| Namespaces | `http://java.sun.com/jsf/html` | `jakarta.faces.html` (EE 10+) |
| AJAX | External library | `<f:ajax>` built-in (JSF 2.0+) |

---

## Common Rendering Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Input value not updating bean | Missing setter or wrong EL name | Check `setPropertyName()` method |
| Converter error displayed | String doesn't parse to target type | Add `<f:convertNumber>` or custom converter |
| Component renders nothing | Outside `<f:view>` / `<h:body>` | Wrap in proper container |
| Select shows wrong selection | `equals()` not overridden on value object | Override `equals()` and `hashCode()` |
| `h:outputText` shows HTML as text | `escape="true"` (default) | Set `escape="false"` if intentional |
