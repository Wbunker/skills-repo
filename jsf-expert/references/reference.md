# JSF Reference: Tags, EL, Config, APIs, and Deployment
*Appendices A–F — Standard Tags, Expression Language, Components/RenderKit API, Config File, Deployment*

## Package Names by Version

| Version | API Package | Config Namespace |
|---------|------------|-----------------|
| JSF 1.x / 2.x | `javax.faces.*` | `http://java.sun.com/xml/ns/javaee` |
| Jakarta Faces 3.0 (Jakarta EE 9) | `jakarta.faces.*` | `https://jakarta.ee/xml/ns/jakartaee` |
| Jakarta Faces 4.0 (Jakarta EE 10+) | `jakarta.faces.*` | `https://jakarta.ee/xml/ns/jakartaee` |

Jakarta Faces 3.0 is a **pure package rename** of JSF 2.3 — same API, new package prefix.
Jakarta Faces 4.0 removed long-deprecated APIs (JSP integration, old `@ManagedBean`).

---

## HTML Tag Library (`h:`) — Full Reference

### Tag Library URIs
| JSF / Jakarta Faces | URI |
|---------------------|-----|
| JSF 1.x–2.x | `http://java.sun.com/jsf/html` |
| Jakarta Faces 3.x | `http://xmlns.jcp.org/jsf/html` |
| Jakarta Faces 4.x | `jakarta.faces.html` |

### Input Tags
| Tag | Renders | Key Attributes |
|-----|---------|---------------|
| `h:inputText` | `<input type="text">` | `value`, `id`, `size`, `maxlength`, `required`, `disabled`, `readonly` |
| `h:inputSecret` | `<input type="password">` | `value`, `redisplay` (default false) |
| `h:inputTextarea` | `<textarea>` | `value`, `rows`, `cols` |
| `h:inputHidden` | `<input type="hidden">` | `value` |
| `h:inputFile` | `<input type="file">` | `value` (type `Part` in Jakarta EE) |

### Output Tags
| Tag | Renders | Key Attributes |
|-----|---------|---------------|
| `h:outputText` | Text (no wrapper element) | `value`, `escape` (default true) |
| `h:outputFormat` | Formatted text | `value`, child `f:param` for MessageFormat |
| `h:outputLabel` | `<label>` | `for`, `value` |
| `h:outputLink` | `<a href>` | `value` (static URL), child `f:param` |

### Command Tags
| Tag | Renders | Key Attributes |
|-----|---------|---------------|
| `h:commandButton` | `<input type="submit/reset/button">` | `value`, `action`, `actionListener`, `immediate`, `type` |
| `h:commandLink` | `<a>` with JS submit | `value`, `action`, `actionListener`, `immediate` |
| `h:button` | `<input type="button">` (no submit) | `value`, `outcome` (bookmarkable) |
| `h:link` | `<a href>` (no submit) | `value`, `outcome`, `includeViewParams` |

### Select Tags
| Tag | Renders | Key Attributes |
|-----|---------|---------------|
| `h:selectOneMenu` | `<select>` (size 1) | `value`, child `f:selectItem(s)` |
| `h:selectOneListbox` | `<select>` (size N) | `value`, `size` |
| `h:selectOneRadio` | Radio button group | `value`, `layout` (`pageDirection`/`lineDirection`) |
| `h:selectBooleanCheckbox` | `<input type="checkbox">` | `value` (Boolean) |
| `h:selectManyCheckbox` | Checkbox group | `value` (List/array), `layout` |
| `h:selectManyListbox` | `<select multiple>` | `value` (List/array), `size` |
| `h:selectManyMenu` | `<select multiple>` size=1 | `value` (List/array) |

### Panel/Layout Tags
| Tag | Renders | Key Attributes |
|-----|---------|---------------|
| `h:panelGrid` | `<table>` | `columns`, `rowClasses`, `columnClasses`, `border` |
| `h:panelGroup` | `<span>` or `<div>` | `layout` (`block`=`<div>`, default=`<span>`) |

### Data Tags
| Tag | Renders | Key Attributes |
|-----|---------|---------------|
| `h:dataTable` | `<table>` | `value`, `var`, `rows`, `first`, `styleClass`, `rowClasses` |
| `h:column` | `<td>`/`<th>` | `headerText` (shorthand); use `f:facet` for complex header |

### Misc HTML Tags
| Tag | Renders | Notes |
|-----|---------|-------|
| `h:form` | `<form method="post">` | Always required for input and command components |
| `h:graphicImage` | `<img>` | `value` (URL or resource expression `#{resource['...']}`) |
| `h:message` | Error text | `for` (component id), `showSummary`, `showDetail` |
| `h:messages` | All errors | `globalOnly`, `showSummary`, `showDetail` |
| `h:head` | `<head>` | Facelets only; JSF manages resource rendering |
| `h:body` | `<body>` | Facelets only |

---

## Core Tag Library (`f:`) — Full Reference

### Tag Library URIs
| Version | URI |
|---------|-----|
| JSF 1.x–2.x | `http://java.sun.com/jsf/core` |
| Jakarta Faces 3.x | `http://xmlns.jcp.org/jsf/core` |
| Jakarta Faces 4.x | `jakarta.faces.core` |

| Tag | Purpose | Key Attributes |
|-----|---------|---------------|
| `f:view` | JSP only: root of JSF content | `locale`, `renderKitId`, `beforePhase`, `afterPhase` |
| `f:subview` | JSP only: include fragment with its own component tree | `id` |
| `f:verbatim` | JSP only: raw HTML passthrough | — |
| `f:attribute` | Set attribute on parent component | `name`, `value` |
| `f:param` | Add parameter to parent (h:outputLink, h:outputFormat) | `name`, `value` |
| `f:converter` | Attach converter to parent | `converterId` |
| `f:convertNumber` | Number converter | `type`, `pattern`, `locale`, `groupingUsed`, `minFractionDigits`, `maxFractionDigits`, `integerOnly` |
| `f:convertDateTime` | Date/time converter | `type` (date/time/both), `pattern`, `locale`, `dateStyle`, `timeStyle`, `timeZone` |
| `f:validator` | Attach validator to parent | `validatorId` |
| `f:validateLength` | Length validator | `minimum`, `maximum` |
| `f:validateLongRange` | Integer range validator | `minimum`, `maximum` |
| `f:validateDoubleRange` | Double range validator | `minimum`, `maximum` |
| `f:validateRegex` | Regex validator (JSF 2+) | `pattern` |
| `f:validateBean` | Bean Validation (JSF 2+) | `disabled`, `validationGroups` |
| `f:valueChangeListener` | Attach ValueChangeListener | `type` (class name) or `binding` |
| `f:actionListener` | Attach ActionListener | `type` (class name) or `binding` |
| `f:phaseListener` | JSF 2+: attach PhaseListener to view | `type` |
| `f:selectItem` | One item in select component | `itemValue`, `itemLabel`, `itemDescription`, `itemDisabled` |
| `f:selectItems` | Collection of items | `value` (List of SelectItem) |
| `f:facet` | Named facet (header/footer) | `name` |
| `f:loadBundle` | Load ResourceBundle into EL scope | `basename`, `var` |
| `f:metadata` | Container for f:viewParam (JSF 2+) | — |
| `f:viewParam` | Bind URL parameter (JSF 2+) | `name`, `value`, `converter`, `validator` |
| `f:ajax` | Partial rendering / AJAX (JSF 2+) | `event`, `execute`, `render`, `listener`, `immediate`, `disabled`, `delay` |
| `f:setPropertyActionListener` | Set bean property on action (JSF 1.2+) | `target`, `value` |
| `f:event` | Subscribe to system events (JSF 2+) | `type` (preRenderView, etc.), `listener` |

---

## Expression Language (EL) Quick Reference

### Syntax
| Expression | Meaning |
|-----------|---------|
| `#{bean}` | Reference managed bean |
| `#{bean.property}` | Call `getProperty()` |
| `#{bean.property.nested}` | Chained getter call |
| `#{bean.method()}` | Invoke method (JSF 2+ / Jakarta EL) |
| `#{bean.method(arg)}` | Method with argument |
| `#{bean.list[0]}` | Array/list index |
| `#{bean.map['key']}` | Map lookup |
| `#{not empty bean.list}` | Null/empty check |
| `#{bean.value > 10}` | Comparison |
| `#{a ? b : c}` | Ternary |

### Implicit EL Objects
| Object | Contents |
|--------|----------|
| `#{facesContext}` | Current FacesContext |
| `#{view}` | UIViewRoot |
| `#{request}` | HttpServletRequest |
| `#{response}` | HttpServletResponse |
| `#{session}` | HttpSession |
| `#{application}` | ServletContext |
| `#{param}` | Request parameter map |
| `#{paramValues}` | Multi-value request params |
| `#{header}` | Request header map |
| `#{cookie}` | Cookie map |
| `#{initParam}` | `web.xml` context params |
| `#{flash}` | Flash scope (JSF 2+) |
| `#{resource}` | Resource URL resolver (JSF 2+) |
| `#{cc}` | Current composite component (JSF 2+) |

---

## faces-config.xml Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- Jakarta Faces 4.0 -->
<faces-config xmlns="https://jakarta.ee/xml/ns/jakartaee"
              xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xsi:schemaLocation="https://jakarta.ee/xml/ns/jakartaee
                  https://jakarta.ee/xml/ns/jakartaee/web-facesconfig_4_0.xsd"
              version="4.0">

  <!-- Application-level settings -->
  <application>
    <locale-config>
      <default-locale>en</default-locale>
      <supported-locale>fr</supported-locale>
    </locale-config>
    <resource-bundle>
      <base-name>messages</base-name>
      <var>msg</var>
    </resource-bundle>
    <message-bundle>com.example.MyMessages</message-bundle>
    <navigation-handler>com.example.MyNavHandler</navigation-handler>
    <view-handler>com.example.MyViewHandler</view-handler>
    <el-resolver>com.example.MyELResolver</el-resolver>
  </application>

  <!-- Managed beans (classic — use CDI @Named in modern apps) -->
  <managed-bean>
    <managed-bean-name>userBean</managed-bean-name>
    <managed-bean-class>com.example.UserBean</managed-bean-class>
    <managed-bean-scope>session</managed-bean-scope>
  </managed-bean>

  <!-- Navigation rules -->
  <navigation-rule>
    <from-view-id>/login.xhtml</from-view-id>
    <navigation-case>
      <from-outcome>success</from-outcome>
      <to-view-id>/home.xhtml</to-view-id>
      <redirect/>
    </navigation-case>
  </navigation-rule>

  <!-- Custom converter -->
  <converter>
    <converter-id>myConverter</converter-id>
    <converter-class>com.example.MyConverter</converter-class>
  </converter>

  <!-- Custom validator -->
  <validator>
    <validator-id>myValidator</validator-id>
    <validator-class>com.example.MyValidator</validator-class>
  </validator>

  <!-- Custom component -->
  <component>
    <component-type>com.example.MyComponent</component-type>
    <component-class>com.example.MyComponent</component-class>
  </component>

  <!-- Custom renderer -->
  <render-kit>
    <renderer>
      <component-family>jakarta.faces.Input</component-family>
      <renderer-type>com.example.MyRenderer</renderer-type>
      <renderer-class>com.example.MyRenderer</renderer-class>
    </renderer>
  </render-kit>

  <!-- Phase listener -->
  <lifecycle>
    <phase-listener>com.example.MyPhaseListener</phase-listener>
  </lifecycle>

</faces-config>
```

---

## CDI-Based Managed Beans (Jakarta Faces / Modern JSF 2.3+)

Replace `faces-config.xml` `<managed-bean>` with CDI annotations:

```java
import jakarta.inject.Named;
import jakarta.enterprise.context.RequestScoped;
import jakarta.enterprise.context.SessionScoped;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.faces.view.ViewScoped;  // JSF view scope via CDI

@Named("userBean")              // EL name (defaults to class name with lowercase first letter)
@SessionScoped                  // CDI scope
public class UserBean implements Serializable {  // must be Serializable for session/view scope
    // ...
}
```

| Scope | Annotation | Package |
|-------|-----------|---------|
| Request | `@RequestScoped` | `jakarta.enterprise.context` |
| Session | `@SessionScoped` | `jakarta.enterprise.context` |
| Application | `@ApplicationScoped` | `jakarta.enterprise.context` |
| View | `@ViewScoped` | `jakarta.faces.view` |
| Conversation | `@ConversationScoped` | `jakarta.enterprise.context` |

---

## web.xml — JSF Deployment Descriptor

```xml
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee" version="6.0">

  <!-- FacesServlet -->
  <servlet>
    <servlet-name>Faces Servlet</servlet-name>
    <servlet-class>jakarta.faces.webapp.FacesServlet</servlet-class>
    <load-on-startup>1</load-on-startup>
  </servlet>
  <servlet-mapping>
    <servlet-name>Faces Servlet</servlet-name>
    <url-pattern>*.xhtml</url-pattern>
    <!-- or /faces/* for classic setup -->
  </servlet-mapping>

  <!-- JSF context parameters -->
  <context-param>
    <param-name>jakarta.faces.PROJECT_STAGE</param-name>
    <param-value>Development</param-value>
    <!-- Production | SystemTest | UnitTest | Development -->
  </context-param>

  <context-param>
    <param-name>jakarta.faces.STATE_SAVING_METHOD</param-name>
    <param-value>server</param-value>  <!-- or client -->
  </context-param>

  <context-param>
    <param-name>jakarta.faces.DEFAULT_SUFFIX</param-name>
    <param-value>.xhtml</param-value>
  </context-param>

  <!-- Facelets extra taglibs -->
  <context-param>
    <param-name>jakarta.faces.FACELETS_LIBRARIES</param-name>
    <param-value>/WEB-INF/mylib.taglib.xml</param-value>
  </context-param>

  <!-- Security -->
  <security-constraint>
    <web-resource-collection>
      <web-resource-name>Secure</web-resource-name>
      <url-pattern>/secure/*</url-pattern>
    </web-resource-collection>
    <auth-constraint><role-name>user</role-name></auth-constraint>
  </security-constraint>

</web-app>
```

### Context Parameter Name Migration
| Old (`javax.faces.*`) | New (`jakarta.faces.*`) |
|----------------------|------------------------|
| `javax.faces.PROJECT_STAGE` | `jakarta.faces.PROJECT_STAGE` |
| `javax.faces.STATE_SAVING_METHOD` | `jakarta.faces.STATE_SAVING_METHOD` |
| `javax.faces.DEFAULT_SUFFIX` | `jakarta.faces.DEFAULT_SUFFIX` |
| `javax.faces.CONFIG_FILES` | `jakarta.faces.CONFIG_FILES` |
| `javax.faces.FACELETS_LIBRARIES` | `jakarta.faces.FACELETS_LIBRARIES` |

---

## WAR Structure

```
myapp.war
├── WEB-INF/
│   ├── web.xml
│   ├── faces-config.xml
│   ├── beans.xml          ← required for CDI (can be empty)
│   ├── lib/
│   │   ├── jakarta.faces-4.x.jar   (or bundled with server)
│   │   └── ...
│   └── classes/
│       └── com/example/*.class
├── resources/             ← JSF 2+ resource library root
│   ├── css/
│   ├── js/
│   └── mylib/             ← composite component library
│       └── myComponent.xhtml
├── templates/             ← Facelets templates (convention)
├── index.xhtml
└── WEB-INF/
    └── views/             ← optional: private views not directly accessible
```

### Resource Library Access in EL
```xhtml
<!-- Stylesheet -->
<h:outputStylesheet library="css" name="style.css"/>

<!-- Script -->
<h:outputScript library="js" name="app.js" target="head"/>

<!-- Image -->
<h:graphicImage library="img" name="logo.png"/>
```

---

## Key API Classes Quick Reference

| Class | Package | Purpose |
|-------|---------|---------|
| `FacesContext` | `jakarta.faces.context` | Central request context |
| `ExternalContext` | `jakarta.faces.context` | Access to request/response/session |
| `Application` | `jakarta.faces.application` | App-level factory methods |
| `UIComponent` | `jakarta.faces.component` | Base component class |
| `UIInput` | `jakarta.faces.component` | Input component base |
| `UIData` | `jakarta.faces.component` | Table/iteration component |
| `UIViewRoot` | `jakarta.faces.component` | Root of component tree |
| `Renderer` | `jakarta.faces.render` | Handles decode/encode |
| `RenderKit` | `jakarta.faces.render` | Collection of renderers |
| `Validator` | `jakarta.faces.validator` | Validates component values |
| `Converter` | `jakarta.faces.convert` | String ↔ Object conversion |
| `NavigationHandler` | `jakarta.faces.application` | Handles page flow |
| `ViewHandler` | `jakarta.faces.application` | Creates/renders views |
| `FacesMessage` | `jakarta.faces.application` | Error/info messages |
| `PhaseListener` | `jakarta.faces.event` | Listens to lifecycle phases |
| `DataModel` | `jakarta.faces.model` | Abstraction for table data |
| `Flash` | `jakarta.faces.context` | Cross-redirect scope |
| `StateHelper` | `jakarta.faces.component` | Component state management |
