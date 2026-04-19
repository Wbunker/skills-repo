# JSF Internationalization and Miscellaneous
*Chapters 11–12 — Internationalization, Odds and Ends*

## Internationalization (i18n) Overview

JSF builds on Java's `java.util.ResourceBundle` system. The steps are:
1. Create `.properties` files for each locale
2. Configure supported locales in `faces-config.xml`
3. Load the bundle in views with `<f:loadBundle>` or via `faces-config.xml`
4. Reference messages with EL: `#{bundle.key}`

---

## Resource Bundles

### Properties Files
Create one file per locale. Use ISO 639-1 language codes and optional ISO 3166-1 country codes:

```
src/main/resources/messages.properties        # default (fallback)
src/main/resources/messages_en.properties     # English
src/main/resources/messages_fr.properties     # French
src/main/resources/messages_de_DE.properties  # German (Germany)
```

**messages.properties:**
```properties
greeting=Hello
farewell=Goodbye
error.required=This field is required
error.email=Please enter a valid email address
label.username=Username
label.password=Password
button.submit=Submit
button.cancel=Cancel
```

**messages_fr.properties:**
```properties
greeting=Bonjour
farewell=Au revoir
error.required=Ce champ est obligatoire
error.email=Veuillez entrer une adresse e-mail valide
label.username=Nom d\u2019utilisateur
label.password=Mot de passe
button.submit=Soumettre
button.cancel=Annuler
```

**Note:** Non-ASCII characters in `.properties` files must be Unicode-escaped (`\uXXXX`) unless using Java 9+ UTF-8 properties files.

---

## Configuring Supported Locales

In `faces-config.xml`:
```xml
<application>
  <locale-config>
    <default-locale>en</default-locale>
    <supported-locale>en</supported-locale>
    <supported-locale>fr</supported-locale>
    <supported-locale>de</supported-locale>
    <supported-locale>es</supported-locale>
  </locale-config>

  <!-- Register bundle for use in all views -->
  <resource-bundle>
    <base-name>messages</base-name>
    <var>msg</var>
  </resource-bundle>
</application>
```

Registering via `<resource-bundle>` makes `#{msg.key}` available on every page without `<f:loadBundle>`.

---

## Loading Bundles in Views

### Using `<f:loadBundle>` (per-page)
```xhtml
<f:loadBundle basename="messages" var="msg"/>

<!-- Then use #{msg.key} anywhere on the page -->
<h:outputText value="#{msg.greeting}"/>
<h:commandButton value="#{msg['button.submit']}"/>
```

### Using Application-level Bundle (faces-config.xml registration)
```xhtml
<!-- No f:loadBundle needed; #{msg} available globally -->
<h:outputText value="#{msg.greeting}"/>
```

---

## Locale Selection

### Automatic Locale (from Browser `Accept-Language`)
JSF defaults to matching the request's `Accept-Language` header against supported locales. The `UIViewRoot.locale` is set automatically.

### Programmatic Locale Change
Allow users to change language at runtime:
```java
import java.util.Locale;
import jakarta.faces.context.FacesContext;

public class LocaleBean {
    public String changeToFrench() {
        FacesContext ctx = FacesContext.getCurrentInstance();
        ctx.getViewRoot().setLocale(Locale.FRENCH);
        return null;  // re-render same page
    }

    public Locale getCurrentLocale() {
        return FacesContext.getCurrentInstance().getViewRoot().getLocale();
    }
}
```

```xhtml
<h:commandLink value="Français" action="#{localeBean.changeToFrench}"/>
```

For a persistent locale choice, store in session bean:
```java
@Named @SessionScoped
public class UserPrefs implements Serializable {
    private Locale locale = Locale.ENGLISH;

    public void changeLocale(String lang) {
        this.locale = new Locale(lang);
        FacesContext.getCurrentInstance().getViewRoot().setLocale(locale);
    }
    // getter/setter
}
```

---

## Parameterized Messages

Use `java.text.MessageFormat` syntax in properties:
```properties
welcome=Welcome, {0}!
items.count=You have {0} item(s) in your cart.
```

Display with EL (JSF doesn't do this out-of-the-box; options below):

**Option 1: OmniFaces `<o:outputFormat>`:**
```xhtml
<o:outputFormat value="#{msg.welcome}">
  <f:param value="#{user.name}"/>
</o:outputFormat>
```

**Option 2: Bean helper method:**
```java
public String getWelcomeMessage() {
    ResourceBundle bundle = ResourceBundle.getBundle("messages",
        FacesContext.getCurrentInstance().getViewRoot().getLocale());
    return MessageFormat.format(bundle.getString("welcome"), user.getName());
}
```

**Option 3: `h:outputFormat` (built-in):**
```xhtml
<h:outputFormat value="#{msg['items.count']}">
  <f:param value="#{cart.size}"/>
</h:outputFormat>
```

---

## Localizing Validation Messages

Override the default JSF validation error messages by creating a message bundle and registering it:

**validation_messages.properties:**
```properties
javax.faces.validator.LengthValidator.MAXIMUM={1}: Value is too long. Max is {0}.
javax.faces.validator.LengthValidator.MINIMUM={1}: Value is too short. Min is {0}.
javax.faces.component.UIInput.REQUIRED={0}: This field is required.
```

Register in `faces-config.xml`:
```xml
<application>
  <message-bundle>validation_messages</message-bundle>
</application>
```

---

## Odds and Ends (Chapter 12)

### Logging

Access the JSF application log from a bean:
```java
import java.util.logging.Logger;

public class MyBean {
    private static final Logger log = Logger.getLogger(MyBean.class.getName());

    public String save() {
        log.info("Saving record for user: " + username);
        // ...
    }
}
```

JSF implementations log internally using `java.util.logging`. Configure in `logging.properties` or your app server's logging config. Log level `FINE` reveals JSF lifecycle and navigation decisions.

---

### Debug Output

**`<ui:debug>` (Facelets, JSF 2+):**
```xhtml
<ui:debug hotkey="d" rendered="#{facesContext.projectStage == 'Development'}"/>
```
Press `Ctrl+Shift+D` (or configured hotkey) to open a popup showing the component tree and scoped variables.

**Project Stage — disable debug in production:**
```xml
<!-- web.xml -->
<context-param>
  <param-name>javax.faces.PROJECT_STAGE</param-name>
  <param-value>Development</param-value>
  <!-- Production | SystemTest | UnitTest | Development -->
</context-param>
```

In `Development` stage, JSF provides extra error information; in `Production` it suppresses stack traces.

---

### Request Parameters

Access raw HTTP request parameters in beans:
```java
Map<String, String> params =
    FacesContext.getCurrentInstance()
                .getExternalContext()
                .getRequestParameterMap();
String value = params.get("paramName");
```

Declarative parameter binding with `<f:viewParam>` (JSF 2+):
```xhtml
<f:metadata>
  <f:viewParam name="id" value="#{bean.entityId}"
               converter="javax.faces.Integer"/>
</f:metadata>
```

---

### Accessing Managed Beans Programmatically

From within Java code (e.g., a PhaseListener or utility):
```java
// Classic EL resolution
FacesContext ctx = FacesContext.getCurrentInstance();
ELContext elCtx = ctx.getELContext();
UserBean userBean = (UserBean) ctx.getApplication()
    .getELResolver()
    .getValue(elCtx, null, "userBean");

// JSF 2+ helper via CDI injection (preferred)
@Inject UserBean userBean;
```

---

### Encoding URLs

Use `ExternalContext` to encode URLs for proper session tracking:
```java
String url = externalContext.encodeResourceURL("/resources/style.css");
String actionUrl = externalContext.encodeActionURL("/app/page.jsf");
```

---

### Conditional Rendering vs. Not Rendering

```xhtml
<!-- rendered=false: component not in HTML output, but still in component tree -->
<h:outputText value="Admin only" rendered="#{user.admin}"/>

<!-- Use panelGroup for conditional blocks -->
<h:panelGroup rendered="#{not empty bean.items}">
  <h:dataTable .../>
</h:panelGroup>
```

---

### Preserving State in Session vs. Client

```xml
<!-- web.xml -->
<context-param>
  <param-name>javax.faces.STATE_SAVING_METHOD</param-name>
  <param-value>server</param-value>   <!-- or "client" -->
</context-param>
```

- `server` (default): component tree saved in `HttpSession` — simpler but uses server memory
- `client`: component tree serialized into hidden field — portable but larger pages

---

## Common i18n Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| Garbled characters in properties | Non-ASCII not escaped | Use `native2ascii` or Unicode escapes `\uXXXX` |
| Locale not switching | New Locale not set on `UIViewRoot` | Call `ctx.getViewRoot().setLocale(locale)` |
| Wrong locale selected | Browser locale not in supported-locale list | Add locale to `<supported-locale>` |
| Missing key shows `???key???` | Key not in default bundle | Add key to base `messages.properties` |
| Date/number not localized | Converter doesn't use view locale | Use `<f:convertNumber>` / `<f:convertDateTime>` without explicit locale |
