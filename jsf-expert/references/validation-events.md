# JSF Validation and Events
*Chapters 7–8 — Validating Input, Handling Events*

## Validation in the JSF Lifecycle

Validation runs in **Phase 3: Process Validations**. If any validator reports an error:
- Phases 4 (Update Model Values) and 5 (Invoke Application) are **skipped**
- Processing jumps to Phase 6 (Render Response)
- Error messages are available via `<h:message>` / `<h:messages>`

---

## Built-in Validators

### Required Attribute
```jsp
<h:inputText value="#{bean.name}" required="true"
             requiredMessage="Name is required"/>
```

### Length Validator
```jsp
<h:inputText value="#{bean.username}">
  <f:validateLength minimum="3" maximum="20"/>
</h:inputText>
```

### Range Validators
```jsp
<!-- Integer range -->
<h:inputText value="#{bean.age}">
  <f:validateLongRange minimum="1" maximum="120"/>
</h:inputText>

<!-- Double range -->
<h:inputText value="#{bean.price}">
  <f:validateDoubleRange minimum="0.01" maximum="9999.99"/>
</h:inputText>
```

### Regular Expression (JSF 2+)
```jsp
<h:inputText value="#{bean.zipCode}">
  <f:validateRegex pattern="\d{5}(-\d{4})?"/>
</h:inputText>
```

### Bean Validation (JSF 2.0+ / Jakarta Faces)
JSF integrates with Bean Validation (Jakarta Validation). Constraints on the bean property are automatically enforced:
```java
public class UserBean {
    @NotNull
    @Size(min=3, max=50)
    private String username;

    @Email
    private String email;

    @Min(18) @Max(120)
    private int age;
}
```
No JSF validator tags needed — constraints fire automatically during Process Validations.

Disable Bean Validation for a component:
```jsp
<h:inputText value="#{bean.field}">
  <f:validateBean disabled="true"/>
</h:inputText>
```

---

## Custom Validators

### Implementing the Validator Interface

**Classic JSF:**
```java
import javax.faces.validator.Validator;
import javax.faces.validator.ValidatorException;

public class EmailValidator implements Validator {
    @Override
    public void validate(FacesContext ctx, UIComponent comp, Object value)
            throws ValidatorException {
        String email = (String) value;
        if (!email.contains("@")) {
            FacesMessage msg = new FacesMessage(
                FacesMessage.SEVERITY_ERROR,
                "Invalid email",
                "Must contain @");
            throw new ValidatorException(msg);
        }
    }
}
```

**Jakarta Faces annotation style:**
```java
import jakarta.faces.validator.FacesValidator;
import jakarta.faces.validator.Validator;
import jakarta.faces.validator.ValidatorException;

@FacesValidator(value="emailValidator", managed=true)  // managed=true for CDI injection
public class EmailValidator implements Validator<String> {
    @Override
    public void validate(FacesContext ctx, UIComponent comp, String value)
            throws ValidatorException {
        if (!value.contains("@")) {
            throw new ValidatorException(
                new FacesMessage(FacesMessage.SEVERITY_ERROR,
                    "Invalid email", "Must contain @"));
        }
    }
}
```

### Register in faces-config.xml (classic)
```xml
<validator>
  <validator-id>emailValidator</validator-id>
  <validator-class>com.example.EmailValidator</validator-class>
</validator>
```

### Use in a Page
```jsp
<h:inputText value="#{bean.email}">
  <f:validator validatorId="emailValidator"/>
</h:inputText>
```

### Method-level Validation (JSF 2+)
```jsp
<!-- Calls bean.validateEmail(FacesContext, UIComponent, Object) -->
<h:inputText value="#{bean.email}"
             validator="#{bean.validateEmail}"/>
```
```java
public void validateEmail(FacesContext ctx, UIComponent comp, Object value)
        throws ValidatorException {
    // same as Validator.validate()
}
```

---

## Error Messages

### Adding Messages Programmatically
```java
// In a validator or action method
FacesContext ctx = FacesContext.getCurrentInstance();

// Component-associated message (shows in h:message for="componentId")
ctx.addMessage("formId:componentId",
    new FacesMessage(FacesMessage.SEVERITY_ERROR, "Summary", "Detail"));

// Global message (shows in h:messages with globalOnly="true")
ctx.addMessage(null,
    new FacesMessage(FacesMessage.SEVERITY_WARN, "Warning", "Details here"));
```

### Severity Levels
| Severity | Constant |
|----------|---------|
| Info | `FacesMessage.SEVERITY_INFO` |
| Warn | `FacesMessage.SEVERITY_WARN` |
| Error | `FacesMessage.SEVERITY_ERROR` |
| Fatal | `FacesMessage.SEVERITY_FATAL` |

### Displaying Messages
```jsp
<!-- Single component error -->
<h:message for="username" style="color:red" showSummary="true" showDetail="false"/>

<!-- All errors -->
<h:messages showSummary="true" showDetail="false" globalOnly="false"/>
```

---

## Events

JSF has three main event types: **value change**, **action**, and **phase** events.

### Value Change Events (UIInput components)

Fired when a submitted value differs from the current value. Fires during **Phase 3** (if valid) or **Phase 5**.

**Listener interface:**
```java
// Classic JSF
import javax.faces.event.ValueChangeListener;
// Jakarta Faces
import jakarta.faces.event.ValueChangeListener;

public class CountryChangeListener implements ValueChangeListener {
    @Override
    public void processValueChange(ValueChangeEvent event) {
        String newCountry = (String) event.getNewValue();
        String oldCountry = (String) event.getOldValue();
        // Update dependent state (e.g., city list)
    }
}
```

**Register in JSP:**
```jsp
<h:selectOneMenu value="#{bean.country}" onchange="submit()">
  <f:selectItems value="#{bean.countries}"/>
  <f:valueChangeListener type="com.example.CountryChangeListener"/>
</h:selectOneMenu>
```

**Method binding shortcut:**
```jsp
<h:selectOneMenu value="#{bean.country}"
                 valueChangeListener="#{bean.countryChanged}"
                 onchange="submit()">
```
```java
public void countryChanged(ValueChangeEvent event) {
    this.country = (String) event.getNewValue();
    // force re-render of dependent components
}
```

**Important:** If you need to re-render based on a value change event and don't want full form submit, use `<f:ajax>` (JSF 2+):
```xhtml
<h:selectOneMenu value="#{bean.country}">
  <f:selectItems value="#{bean.countries}"/>
  <f:ajax listener="#{bean.countryChanged}" render="cityPanel"/>
</h:selectOneMenu>
```

---

### Action Events (UICommand components)

Fired by `h:commandButton` and `h:commandLink` during **Phase 5** (after validation and model update).

**ActionListener interface:**
```java
import jakarta.faces.event.ActionListener;
import jakarta.faces.event.ActionEvent;

public class LoggingActionListener implements ActionListener {
    @Override
    public void processAction(ActionEvent event) {
        UIComponent source = event.getComponent();
        // log or side-effect without controlling navigation
    }
}
```

**Register:**
```jsp
<h:commandButton value="Submit" action="#{bean.save}">
  <f:actionListener type="com.example.LoggingActionListener"/>
</h:actionListener>
```

**Note:** `ActionListener` does NOT control navigation. Navigation comes from the `action` attribute's return value.

---

### Phase Events (System Events)

Fire before and after each lifecycle phase. Useful for framework-level concerns.

**PhaseListener interface:**
```java
import jakarta.faces.event.PhaseListener;
import jakarta.faces.event.PhaseEvent;
import jakarta.faces.event.PhaseId;

public class AuthPhaseListener implements PhaseListener {
    @Override
    public PhaseId getPhaseId() {
        return PhaseId.RESTORE_VIEW;  // or ANY_PHASE
    }

    @Override
    public void beforePhase(PhaseEvent event) {
        // Check auth before the view is restored
    }

    @Override
    public void afterPhase(PhaseEvent event) { }
}
```

**Register in faces-config.xml:**
```xml
<lifecycle>
  <phase-listener>com.example.AuthPhaseListener</phase-listener>
</lifecycle>
```

---

## AJAX and Partial Processing (JSF 2+ / Jakarta Faces)

`<f:ajax>` enables partial page updates without a full form submit:

```xhtml
<!-- Execute only this component, render a panel -->
<h:inputText value="#{bean.query}">
  <f:ajax event="keyup" listener="#{bean.search}"
          execute="@this" render="resultsPanel" delay="300"/>
</h:inputText>

<!-- Submit form partially -->
<h:commandButton value="Check">
  <f:ajax execute="@form" render="statusMessage"/>
</h:commandButton>
```

| `execute` keyword | Meaning |
|------------------|---------|
| `@this` | Only this component |
| `@form` | Entire enclosing form |
| `@all` | Entire view |
| `@none` | Nothing (listener only) |
| `id1 id2` | Space-separated component IDs |

---

## Validation Order and Immediate Attribute

`immediate="true"` on an input or command skips the normal lifecycle and processes during **Apply Request Values (Phase 2)** instead:

```jsp
<!-- Cancel button — skips validation, goes straight to action -->
<h:commandButton value="Cancel" action="#{bean.cancel}" immediate="true"/>

<!-- Run validation on this field early (before others) -->
<h:inputText value="#{bean.code}" immediate="true"/>
```

Use `immediate` for cancel/reset buttons that should bypass validation of the rest of the form.

---

## Common Validation Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| Validation fires but page re-renders empty | Action method runs despite errors | Check — it shouldn't; verify no `renderResponse()` call skipping phases |
| Custom validator not invoked | Not registered in `faces-config.xml` or wrong ID | Add `<validator>` element or `@FacesValidator` annotation |
| Bean Validation not firing | Dependency not on classpath | Add `jakarta.validation:jakarta.validation-api` + Hibernate Validator |
| Value change fires on every submit | Value is object without `equals()` | Override `equals()` and `hashCode()` |
| `immediate` cancel still validates | `immediate` not set on button | Add `immediate="true"` to the commandButton |
