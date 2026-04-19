# JSF Custom Components and Renderers
*Chapters 13–15 — Custom Renderers, Custom Components, Custom Presentation Layer*

## When to Build Custom vs. Use Existing

```
What do I need?
├── Change rendering of existing component only → Custom Renderer
│   └── Subclass Renderer, same UIComponent class
├── New reusable widget with custom behavior → Custom UIComponent
│   └── Subclass UIComponentBase or a standard component
├── Composite/template component (JSF 2+) → Composite Component
│   └── Facelets XHTML in /resources folder — no Java needed
├── Pluggable validation/conversion → Custom Validator / Converter
│   └── See validation-events.md
└── Different template language (not JSP/Facelets) → Custom ViewHandler
```

---

## Custom Renderers (Chapter 13)

A `Renderer` handles:
- **`decode()`** — reads submitted value from HTTP request params
- **`encodeBegin()` / `encodeChildren()` / `encodeEnd()`** — writes HTML output

### Implementing a Custom Renderer

**Classic JSF:**
```java
import javax.faces.render.Renderer;
// Jakarta Faces:
import jakarta.faces.render.Renderer;
import jakarta.faces.render.FacesRenderer;

@FacesRenderer(
    componentFamily = "javax.faces.Input",  // or "jakarta.faces.Input"
    rendererType    = "com.example.StarRating"
)
public class StarRatingRenderer extends Renderer {

    @Override
    public void decode(FacesContext ctx, UIComponent comp) {
        Map<String, String> params =
            ctx.getExternalContext().getRequestParameterMap();
        String clientId = comp.getClientId(ctx);
        String submittedValue = params.get(clientId);
        if (submittedValue != null) {
            ((UIInput) comp).setSubmittedValue(submittedValue);
        }
    }

    @Override
    public void encodeEnd(FacesContext ctx, UIComponent comp)
            throws IOException {
        ResponseWriter writer = ctx.getResponseWriter();
        String clientId = comp.getClientId(ctx);
        int rating = (Integer) comp.getAttributes().get("value");

        writer.startElement("span", comp);
        writer.writeAttribute("id", clientId, "id");
        for (int i = 1; i <= 5; i++) {
            writer.startElement("input", comp);
            writer.writeAttribute("type", "radio", null);
            writer.writeAttribute("name", clientId, null);
            writer.writeAttribute("value", i, null);
            if (i == rating) writer.writeAttribute("checked", "checked", null);
            writer.endElement("input");
        }
        writer.endElement("span");
    }
}
```

### Register in faces-config.xml (alternative to annotation)
```xml
<render-kit>
  <renderer>
    <component-family>javax.faces.Input</component-family>
    <renderer-type>com.example.StarRating</renderer-type>
    <renderer-class>com.example.StarRatingRenderer</renderer-class>
  </renderer>
</render-kit>
```

---

## Other Pluggable Classes (Chapter 13)

### Custom Navigation Handler
```java
import jakarta.faces.application.NavigationHandler;

public class AuditNavigationHandler extends NavigationHandler {
    private final NavigationHandler delegate;

    public AuditNavigationHandler(NavigationHandler delegate) {
        this.delegate = delegate;
    }

    @Override
    public void handleNavigation(FacesContext ctx, String fromAction,
                                  String outcome) {
        log("Navigating: " + fromAction + " → " + outcome);
        delegate.handleNavigation(ctx, fromAction, outcome);
    }
}
```

Register:
```xml
<application>
  <navigation-handler>com.example.AuditNavigationHandler</navigation-handler>
</application>
```

### Custom ViewHandler
Allows a different template technology (e.g., Velocity, Thymeleaf):
```java
import jakarta.faces.application.ViewHandler;
// Extend ViewHandlerWrapper for decorator pattern

public class MyViewHandler extends ViewHandlerWrapper {
    private final ViewHandler delegate;
    public MyViewHandler(ViewHandler delegate) { this.delegate = delegate; }

    @Override
    public ViewHandler getWrapped() { return delegate; }

    @Override
    public UIViewRoot createView(FacesContext ctx, String viewId) {
        // custom logic
        return super.createView(ctx, viewId);
    }
}
```

Register:
```xml
<application>
  <view-handler>com.example.MyViewHandler</view-handler>
</application>
```

### Custom EL Resolver
Extend the EL resolution chain:
```java
import jakarta.el.ELResolver;

public class MyELResolver extends ELResolver {
    @Override
    public Object getValue(ELContext ctx, Object base, Object property) {
        if (base == null && "mySpecial".equals(property)) {
            ctx.setPropertyResolved(true);
            return specialValue;
        }
        return null;
    }
    // ... other methods
}
```

Register:
```xml
<application>
  <el-resolver>com.example.MyELResolver</el-resolver>
</application>
```

---

## Custom UIComponents (Chapter 14)

A custom component combines behavior (state, events) with rendering. Two approaches:

### Approach 1: Component with Separate Renderer
- `UIComponent` subclass handles state and decodes submitted value
- `Renderer` subclass handles all HTML output
- More flexible — one component can have multiple renderers

### Approach 2: Self-Rendering Component
- `UIComponent` subclass overrides `encodeBegin/encodeEnd` directly
- Simpler for one-off components

### Implementing a Custom UIComponent

```java
import jakarta.faces.component.UIInput;
import jakarta.faces.component.FacesComponent;

@FacesComponent("com.example.StarRating")  // component type
public class StarRatingComponent extends UIInput {

    private static final String COMPONENT_FAMILY = "com.example.Rating";
    private static final String RENDERER_TYPE = "com.example.StarRating";

    @Override
    public String getFamily() { return COMPONENT_FAMILY; }

    @Override
    public String getRendererType() { return RENDERER_TYPE; }

    // Custom attribute with state saving
    public int getMaxStars() {
        Integer val = (Integer) getStateHelper().eval("maxStars");
        return val != null ? val : 5;
    }
    public void setMaxStars(int maxStars) {
        getStateHelper().put("maxStars", maxStars);
    }
}
```

### State Saving with `StateHelper`
Use `getStateHelper()` for all component attributes that must survive round-trips:
```java
// Correct — persisted across requests
public String getLabel() {
    return (String) getStateHelper().eval("label", "Default");
}
public void setLabel(String label) {
    getStateHelper().put("label", label);
}

// WRONG — field lost on next request
private String label;  // do not do this
```

### Register Component
```xml
<!-- faces-config.xml -->
<component>
  <component-type>com.example.StarRating</component-type>
  <component-class>com.example.StarRatingComponent</component-class>
</component>
```

### Create a Tag Library Descriptor (TLD / taglib)
For JSP:
```xml
<!-- WEB-INF/starrating.tld -->
<taglib>
  <tlib-version>1.0</tlib-version>
  <uri>http://example.com/starrating</uri>
  <tag>
    <tag-name>starRating</tag-name>
    <tag-class>com.example.StarRatingTag</tag-class>
    <attribute>
      <name>value</name><required>true</required><rtexprvalue>true</rtexprvalue>
    </attribute>
    <attribute>
      <name>maxStars</name><required>false</required>
    </attribute>
  </tag>
</taglib>
```

For Facelets (JSF 2+), create a `.taglib.xml` file:
```xml
<!-- WEB-INF/starrating.taglib.xml -->
<facelet-taglib>
  <namespace>http://example.com/starrating</namespace>
  <tag>
    <tag-name>starRating</tag-name>
    <component>
      <component-type>com.example.StarRating</component-type>
      <renderer-type>com.example.StarRating</renderer-type>
    </component>
  </tag>
</facelet-taglib>
```

Register taglib in `web.xml`:
```xml
<context-param>
  <param-name>javax.faces.FACELETS_LIBRARIES</param-name>
  <param-value>/WEB-INF/starrating.taglib.xml</param-value>
</context-param>
```

---

## Composite Components (JSF 2+ / Jakarta Faces) — No Java Required

The preferred modern approach for reusable UI fragments. Place XHTML files in `/resources/<library>/`.

**File: `/resources/mylib/starRating.xhtml`:**
```xhtml
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:cc="http://xmlns.jcp.org/jsf/composite"
      xmlns:h="http://xmlns.jcp.org/jsf/html">
<h:head/>
<h:body>
  <cc:interface>
    <cc:attribute name="value" required="true"/>
    <cc:attribute name="maxStars" default="5"/>
    <cc:attribute name="listener" method-signature="void actionPerformed(jakarta.faces.event.ActionEvent)"/>
  </cc:interface>
  <cc:implementation>
    <span id="#{cc.clientId}">
      <!-- render stars using cc.attrs.value and cc.attrs.maxStars -->
      <ui:repeat var="i" value="#{mylib:range(cc.attrs.maxStars)}">
        <h:commandLink action="#{cc.attrs.listener}">
          <h:graphicImage value="#{i le cc.attrs.value ? 'star-full' : 'star-empty'}.png"/>
        </h:commandLink>
      </ui:repeat>
    </span>
  </cc:implementation>
</h:body>
</html>
```

**Use it:**
```xhtml
<html xmlns:mylib="http://xmlns.jcp.org/jsf/composite/mylib">
<mylib:starRating value="#{product.rating}" maxStars="5"/>
```

---

## Custom Presentation Layer (Chapter 15)

### Replacing the Default ViewHandler

To use a different view technology altogether, implement `ViewHandler` (or `ViewHandlerWrapper`) and override:

| Method | Purpose |
|--------|---------|
| `createView()` | Create a new `UIViewRoot` for a view ID |
| `restoreView()` | Restore a previously saved view |
| `renderView()` | Render the current view |
| `getActionURL()` | Compute the form action URL |
| `getResourceURL()` | Compute resource URLs |
| `writeState()` | Write view state to the response |

### Facelets as the Default View Handler (JSF 2+)
Since JSF 2.0, Facelets is the built-in default ViewHandler. The original JSP-based ViewHandler is still available but deprecated.

Configure default file extension:
```xml
<context-param>
  <param-name>javax.faces.DEFAULT_SUFFIX</param-name>
  <param-value>.xhtml</param-value>
</context-param>
```

---

## Popular Component Libraries (Modern Ecosystem)

These provide extensive ready-made custom components — prefer these over building from scratch:

| Library | Notable Components |
|---------|-------------------|
| **PrimeFaces** | Rich data tables, charts, dialog, autocomplete, calendar, file upload |
| **OmniFaces** | Utility components: `<o:ajax>`, `<o:outputFormat>`, `<o:cache>` |
| **BootsFaces** | Bootstrap 4/5-integrated JSF components |
| **MyFaces Tobago** | Full UI kit with consistent theming |

PrimeFaces example:
```xhtml
<html xmlns:p="http://primefaces.org/ui">
<p:dataTable value="#{bean.items}" var="item" paginator="true" rows="10"
             sortMode="multiple" filterDelay="300">
  <p:column headerText="Name" sortBy="#{item.name}" filterBy="#{item.name}">
    <h:outputText value="#{item.name}"/>
  </p:column>
</p:dataTable>
```

---

## Common Custom Component Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| State lost between requests | Storing state in Java fields | Use `getStateHelper()` for all attributes |
| `clientId` differs from expected | Component inside `h:form` adds prefix | Use `comp.getClientId(ctx)` not hardcoded ID |
| Custom tag not found | TLD/taglib not registered | Check `web.xml` FACELETS_LIBRARIES param |
| Renderer decode not called | Component not in `EDIT` render phase | Ensure component is inside `h:form` |
| Composite component not found | Wrong resource folder name or namespace | Folder must match namespace suffix in xmlns |
