# JSF Navigation and Tabular Data
*Chapters 9–10 — Controlling Navigation, Working with Tabular Data*

## Navigation Rules

Navigation in JSF is declared in `faces-config.xml`. An action method returns a `String` outcome; JSF looks it up to find the next view.

### Basic Navigation Rule
```xml
<navigation-rule>
  <!-- from-view-id is optional; omit to apply globally -->
  <from-view-id>/login.xhtml</from-view-id>
  <navigation-case>
    <from-outcome>success</from-outcome>
    <to-view-id>/home.xhtml</to-view-id>
  </navigation-case>
  <navigation-case>
    <from-outcome>failure</from-outcome>
    <to-view-id>/login.xhtml</to-view-id>
  </navigation-case>
</navigation-rule>
```

**Action method:**
```java
public String login() {
    if (authService.authenticate(username, password)) {
        return "success";
    }
    return "failure";
}
```

### Global Navigation Rules (no `from-view-id`)
```xml
<navigation-rule>
  <navigation-case>
    <from-outcome>logout</from-outcome>
    <to-view-id>/login.xhtml</to-view-id>
    <redirect/>
  </navigation-case>
</navigation-rule>
```

### From-Action Filter
Only match if outcome comes from a specific action method:
```xml
<navigation-case>
  <from-action>#{userBean.save}</from-action>
  <from-outcome>success</from-outcome>
  <to-view-id>/confirmation.xhtml</to-view-id>
</navigation-case>
```

---

## Forward vs. Redirect

### Forward (default)
- Server-side — browser URL does **not** change
- Fast — no extra HTTP round-trip
- Risk: double-submit on browser refresh

```xml
<navigation-case>
  <from-outcome>saved</from-outcome>
  <to-view-id>/result.xhtml</to-view-id>
  <!-- no <redirect/> = forward -->
</navigation-case>
```

### Redirect (Post/Redirect/Get)
- Browser gets `302`, issues a new `GET` request
- URL in browser changes
- Prevents double-submit on refresh
- Loses request-scoped bean data (use `<f:viewParam>` or flash scope to pass data)

```xml
<navigation-case>
  <from-outcome>saved</from-outcome>
  <to-view-id>/result.xhtml</to-view-id>
  <redirect/>
</navigation-case>
```

**Modern shorthand (JSF 2+) — implicit navigation:**
```java
// Return view ID directly from action method
public String save() {
    // ...
    return "/result.xhtml?faces-redirect=true";
}
```

### Flash Scope (JSF 2+)
Survives one redirect — use it to pass data across a POST/Redirect/GET:
```java
// Classic JSF / Jakarta Faces
import jakarta.faces.context.Flash;

Flash flash = FacesContext.getCurrentInstance()
                          .getExternalContext().getFlash();
flash.put("message", "Record saved successfully");
return "/result.xhtml?faces-redirect=true";
```
```xhtml
<!-- On result.xhtml -->
<h:outputText value="#{flash.message}"/>
```

---

## Implicit Navigation (JSF 2+)

If no matching navigation rule is found, JSF 2+ uses the outcome as a view ID directly:

```java
// Returns "/admin/users.xhtml" — no faces-config.xml rule needed
public String goToUsers() {
    return "/admin/users.xhtml";
}

// With redirect
public String goToUsers() {
    return "/admin/users.xhtml?faces-redirect=true";
}
```

Also works inline in the page:
```xhtml
<h:commandButton value="Go to Users" action="/admin/users.xhtml?faces-redirect=true"/>
<h:link value="User List" outcome="/admin/users.xhtml"/>
```

---

## View Parameters (`<f:viewParam>`) — JSF 2+

Declare and bind URL query parameters for bookmarkable pages:
```xhtml
<f:metadata>
  <f:viewParam name="id" value="#{productBean.productId}"/>
</f:metadata>
```

Generate URLs with view params:
```xhtml
<h:link value="Product" outcome="/product/detail.xhtml">
  <f:param name="id" value="#{item.id}"/>
</h:link>
```

---

## Programmatic Navigation

From within a bean (bypass rules entirely):
```java
FacesContext ctx = FacesContext.getCurrentInstance();
NavigationHandler nav = ctx.getApplication().getNavigationHandler();
nav.handleNavigation(ctx, null, "success");
```

Or send an external redirect:
```java
ctx.getExternalContext().redirect("/app/other-page.jsf");
ctx.responseComplete();
```

---

## Working with Tabular Data — `h:dataTable`

`h:dataTable` iterates over a `List`, array, `ResultSet`, or `DataModel`.

### Basic Table
```xhtml
<h:dataTable value="#{orderBean.orders}" var="order"
             styleClass="table" rowClasses="odd,even">
  <f:column>
    <f:facet name="header">Order ID</f:facet>
    <h:outputText value="#{order.id}"/>
  </f:column>
  <f:column>
    <f:facet name="header">Date</f:facet>
    <h:outputText value="#{order.date}">
      <f:convertDateTime pattern="MM/dd/yyyy"/>
    </h:outputText>
  </f:column>
  <f:column>
    <f:facet name="header">Total</f:facet>
    <h:outputText value="#{order.total}">
      <f:convertNumber type="currency"/>
    </h:outputText>
  </f:column>
  <f:column>
    <h:commandLink value="View" action="#{orderBean.viewOrder}">
      <f:setPropertyActionListener target="#{orderBean.selected}"
                                   value="#{order}"/>
    </h:commandLink>
  </f:column>
</h:dataTable>
```

### h:dataTable Attributes
| Attribute | Purpose |
|-----------|---------|
| `value` | Collection/DataModel expression |
| `var` | Loop variable name (use in column EL) |
| `rows` | Max rows to display (pagination) |
| `first` | First row index (0-based, for pagination) |
| `styleClass` | CSS class on `<table>` |
| `rowClasses` | Comma-separated CSS classes, alternated per row |
| `columnClasses` | Comma-separated CSS classes for columns |
| `headerClass` | CSS class for header cells |
| `footerClass` | CSS class for footer cells |
| `binding` | Bind the `UIData` component to a bean property |

### Header and Footer Facets
```xhtml
<h:dataTable value="#{bean.items}" var="item">
  <f:facet name="header">
    <h:outputText value="Items"/>
  </f:facet>
  <f:facet name="footer">
    <h:outputText value="#{bean.total}"/>
  </f:facet>
  <f:column>...</f:column>
</h:dataTable>
```

---

## DataModel

`DataModel` is an abstraction over the actual data source, giving row-level metadata and selection support.

### DataModel Subclasses
| Class | Wraps |
|-------|-------|
| `ListDataModel` | `java.util.List` |
| `ArrayDataModel` | Array |
| `ResultDataModel` | `javax.sql.rowset.CachedRowSet` / JDBC `ResultSet` (read-only) |
| `ScalarDataModel` | Single object |

```java
import jakarta.faces.model.DataModel;
import jakarta.faces.model.ListDataModel;

public class OrderBean {
    private DataModel<Order> dataModel;
    private Order selected;

    public DataModel<Order> getOrders() {
        if (dataModel == null) {
            dataModel = new ListDataModel<>(orderService.findAll());
        }
        return dataModel;
    }

    // Called from h:commandLink in table row
    public String viewOrder() {
        selected = (Order) dataModel.getRowData();
        return "viewOrder";
    }
}
```

---

## Selecting a Row — Passing Row Data to Action

### Using `f:setPropertyActionListener` (JSF 1.2+)
```xhtml
<h:commandLink value="Select" action="#{bean.select}">
  <f:setPropertyActionListener target="#{bean.selected}" value="#{item}"/>
</h:commandLink>
```

### Using DataModel.getRowData() (classic pattern)
```java
// Table bound to DataModel; commandLink calls selectRow()
public String selectRow() {
    this.selected = dataModel.getRowData();
    return "detail";
}
```

### Using EL action parameter (JSF 2+)
```xhtml
<h:commandLink value="Select"
               action="#{bean.select(item)}"/>
```
```java
public String select(Order item) {
    this.selected = item;
    return "detail";
}
```

---

## Pagination

Manual pagination with `first` and `rows`:
```java
public class PagedBean {
    private int pageSize = 10;
    private int firstRow = 0;
    private List<Order> orders;

    public String nextPage() {
        firstRow += pageSize;
        return null;  // stay on same page
    }
    public String prevPage() {
        firstRow = Math.max(0, firstRow - pageSize);
        return null;
    }
    public int getFirstRow() { return firstRow; }
    public int getPageSize() { return pageSize; }
}
```
```xhtml
<h:dataTable value="#{pagedBean.orders}" var="o"
             first="#{pagedBean.firstRow}" rows="#{pagedBean.pageSize}">
  ...
</h:dataTable>
<h:commandButton value="Prev" action="#{pagedBean.prevPage}"/>
<h:commandButton value="Next" action="#{pagedBean.nextPage}"/>
```

For production, use **PrimeFaces `<p:dataTable>`** or **OmniFaces** for sorting, filtering, and lazy loading.

---

## Common Navigation/Data Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| Navigation rule not found | Wrong outcome string | Match exact string returned by action method |
| Double submit on refresh | Using forward not redirect | Add `<redirect/>` or `?faces-redirect=true` |
| `null` in `dataModel.getRowData()` | State lost between requests | Use session or view scope for DataModel |
| Row data wrong on action | `var` name reused across nested tables | Use unique `var` names |
| URL doesn't change after navigation | Using forward | Add `<redirect/>` |
| Flash data missing after redirect | Flash not properly set | Set before redirect, read on next request only |
