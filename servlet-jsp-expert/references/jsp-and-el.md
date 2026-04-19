# JSP, Expression Language, JSTL, and Custom Tags
*Chapters 3, 9–11 — JSP Syntax, EL, JSTL, Custom Tag Libraries, JavaBeans*

## Chapter 3: How to Develop a JSP

### JSP Page Structure
```jsp
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<!DOCTYPE html>
<html>
<head>
  <title>Product List</title>
</head>
<body>
  <h1>Products</h1>
  <c:forEach var="p" items="${products}">
    <p>${p.name} — $${p.price}</p>
  </c:forEach>
</body>
</html>
```

### JSP Directives
```jsp
<!-- Page directive — applies to this page -->
<%@ page contentType="text/html;charset=UTF-8"
         language="java"
         import="java.util.List, com.example.Product"
         errorPage="/WEB-INF/error.jsp"
         isErrorPage="false"
         session="true"          %>

<!-- Include directive — static text inclusion at translation time -->
<%@ include file="/WEB-INF/includes/header.jsp" %>

<!-- Taglib directive — import a tag library -->
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
```

### Implicit Objects in JSP
| Object | Type | Description |
|--------|------|-------------|
| `request` | `HttpServletRequest` | Current HTTP request |
| `response` | `HttpServletResponse` | Current HTTP response |
| `session` | `HttpSession` | Current user session |
| `application` | `ServletContext` | Application-wide context |
| `out` | `JspWriter` | Output stream |
| `config` | `ServletConfig` | Servlet config for this JSP |
| `pageContext` | `PageContext` | Encapsulates all scopes |
| `page` | `Object` (this servlet) | The JSP servlet instance |
| `exception` | `Throwable` | Exception (on error pages only) |

### Scriptlets (Legacy — Avoid in New Code)
```jsp
<%-- Declaration: instance variable or method --%>
<%! private int counter = 0; %>

<%-- Scriptlet: arbitrary Java code --%>
<%
    List<Product> products = (List<Product>) request.getAttribute("products");
    for (Product p : products) {
%>
    <p><%= p.getName() %></p>
<%  } %>

<%-- Expression: prints result of expression --%>
<p>Total: <%= products.size() %></p>

<%-- Comment: not sent to browser --%>
<%-- This is a JSP comment --%>
```

**Best practice:** Put Java logic in servlets; use EL + JSTL in JSPs.

### JSP Actions (Standard Tags)
```jsp
<!-- Include another page dynamically (request-time) -->
<jsp:include page="/WEB-INF/includes/header.jsp">
  <jsp:param name="title" value="Products"/>
</jsp:include>

<!-- Forward request to another resource -->
<jsp:forward page="/WEB-INF/views/error.jsp"/>

<!-- Use a JavaBean -->
<jsp:useBean id="user" class="com.example.User" scope="session"/>
<jsp:setProperty name="user" property="name" param="name"/>
<jsp:getProperty name="user" property="name"/>
```

---

## Expression Language (EL)

### EL Syntax
```jsp
${expression}            <!-- outputs value; null-safe -->
${!empty products}       <!-- boolean check -->
${products.size()}       <!-- method calls (EL 3.0+) -->
${product.name}          <!-- property access (calls getName()) -->
${product['name']}       <!-- bracket notation (same result) -->
${products[0].name}      <!-- array/list index -->
${param.search}          <!-- request parameter -->
${sessionScope.user}     <!-- explicit scope -->
```

### EL Implicit Objects
| Object | Content |
|--------|---------|
| `param` | `request.getParameter()` map |
| `paramValues` | `request.getParameterValues()` map |
| `header` | Request headers map |
| `cookie` | Cookie map by name |
| `initParam` | Context init parameters |
| `requestScope` | Request attributes |
| `sessionScope` | Session attributes |
| `applicationScope` | ServletContext attributes |
| `pageScope` | Page-scoped attributes |

### EL Operators
```jsp
${a + b}          <!-- arithmetic -->
${a > b}   ${a gt b}   <!-- comparison (both forms) -->
${a == b}  ${a eq b}
${a && b}  ${a and b}  <!-- logical -->
${a || b}  ${a or b}
${!a}      ${not a}
${empty list}           <!-- true if null, empty string, empty collection -->
${a ? b : c}            <!-- conditional (ternary) -->
```

---

## Chapter 9: JSTL Core Tags

```jsp
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
```

### Output and Variables
```jsp
<!-- Safe output (escapes HTML by default) -->
<c:out value="${product.description}" default="N/A" escapeXml="true"/>

<!-- Set a variable -->
<c:set var="tax" value="${price * 0.08}" scope="request"/>

<!-- Remove a variable -->
<c:remove var="tempVar" scope="session"/>
```

### Conditionals
```jsp
<!-- Simple if (no else) -->
<c:if test="${not empty user}">
  Welcome, ${user.name}!
</c:if>

<!-- Choose / when / otherwise (switch-like) -->
<c:choose>
  <c:when test="${product.stock > 10}">In Stock</c:when>
  <c:when test="${product.stock > 0}">Low Stock</c:when>
  <c:otherwise>Out of Stock</c:otherwise>
</c:choose>
```

### Loops
```jsp
<!-- Iterate a collection -->
<c:forEach var="item" items="${cart.items}"
           varStatus="loop"
           begin="0" end="9" step="1">
  <tr class="${loop.index % 2 == 0 ? 'even' : 'odd'}">
    <td>${loop.index + 1}</td>
    <td>${item.name}</td>
    <td>${item.price}</td>
  </tr>
</c:forEach>

<!-- varStatus properties: index, count, first, last, current -->

<!-- Iterate tokens (split string) -->
<c:forTokens var="token" items="a,b,c,d" delims=",">
  <span>${token}</span>
</c:forTokens>
```

### URLs and Redirects
```jsp
<!-- Build URL with context path prepended automatically -->
<c:url var="listUrl" value="/products">
  <c:param name="page" value="2"/>
  <c:param name="sort" value="name"/>
</c:url>
<a href="${listUrl}">Next Page</a>

<!-- Redirect -->
<c:redirect url="/login"/>
```

### Import (like jsp:include but can fetch remote URLs)
```jsp
<c:import url="/WEB-INF/includes/nav.html"/>
```

---

## JSTL Formatting Tags (fmt)

```jsp
<%@ taglib uri="http://java.sun.com/jsp/jstl/fmt" prefix="fmt" %>

<!-- Format number as currency -->
<fmt:formatNumber value="${product.price}"
                  type="currency"
                  currencySymbol="$"/>

<!-- Format number with pattern -->
<fmt:formatNumber value="${ratio}" pattern="##0.0%"/>

<!-- Format date -->
<fmt:formatDate value="${order.date}"
                pattern="MM/dd/yyyy h:mm a"/>
<!-- or type="date" / "time" / "both" with dateStyle/timeStyle -->

<!-- Parse a number -->
<fmt:parseNumber var="parsed" value="${param.amount}" type="number"/>

<!-- Set locale and timezone -->
<fmt:setLocale value="en_US"/>
<fmt:setTimeZone value="America/Chicago"/>

<!-- Internationalization (i18n) -->
<fmt:setBundle basename="com.example.messages"/>
<fmt:message key="product.title"/>
<fmt:message key="greeting">
  <fmt:param value="${user.name}"/>
</fmt:message>
```

---

## JSTL Function Tags (fn)

```jsp
<%@ taglib uri="http://java.sun.com/jsp/jstl/functions" prefix="fn" %>

${fn:length(products)}               <!-- collection or string length -->
${fn:toUpperCase(product.name)}
${fn:toLowerCase(product.sku)}
${fn:trim(param.search)}
${fn:contains(product.tags, "sale")}
${fn:startsWith(uri, "/admin")}
${fn:endsWith(fileName, ".pdf")}
${fn:replace(text, "foo", "bar")}
${fn:substring(str, 0, 10)}
${fn:split(csv, ",")}                <!-- returns String[] -->
${fn:join(array, ", ")}
${fn:escapeXml(userInput)}          <!-- always use for user content -->
```

---

## Chapter 10: Custom Tag Libraries

### Simple Tag Handler (Preferred — simpler than classic tags)
```java
import jakarta.servlet.jsp.JspException;
import jakarta.servlet.jsp.tagext.SimpleTagSupport;
import java.io.IOException;

public class FormatPriceTag extends SimpleTagSupport {

    private double price;

    public void setPrice(double price) {
        this.price = price;
    }

    @Override
    public void doTag() throws JspException, IOException {
        String formatted = String.format("$%.2f", price);
        getJspContext().getOut().write(formatted);
    }
}
```

**Tag Library Descriptor (`/WEB-INF/mylib.tld`):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<taglib xmlns="https://jakarta.ee/xml/ns/jakartaee" version="3.0">
  <tlib-version>1.0</tlib-version>
  <short-name>mylib</short-name>
  <uri>http://example.com/mylib</uri>

  <tag>
    <name>formatPrice</name>
    <tag-class>com.example.tags.FormatPriceTag</tag-class>
    <body-content>empty</body-content>
    <attribute>
      <name>price</name>
      <required>true</required>
      <rtexprvalue>true</rtexprvalue>  <!-- allow EL -->
      <type>double</type>
    </attribute>
  </tag>
</taglib>
```

**Usage in JSP:**
```jsp
<%@ taglib uri="http://example.com/mylib" prefix="my" %>
<my:formatPrice price="${product.price}"/>
```

### Tag with Body Content
```java
public class IfAdminTag extends SimpleTagSupport {
    @Override
    public void doTag() throws JspException, IOException {
        HttpSession session = (HttpSession)
            getJspContext().getAttribute(
                "session", PageContext.SESSION_SCOPE);
        User user = (User) session.getAttribute("user");
        if (user != null && "ADMIN".equals(user.getRole())) {
            getJspBody().invoke(null);   // render body
        }
        // else: body is suppressed
    }
}
```

```xml
<tag>
  <name>ifAdmin</name>
  <tag-class>com.example.tags.IfAdminTag</tag-class>
  <body-content>scriptless</body-content>   <!-- EL + tags allowed in body -->
</tag>
```

```jsp
<my:ifAdmin>
  <a href="/admin">Admin Panel</a>
</my:ifAdmin>
```

### body-content Values
| Value | Meaning |
|-------|---------|
| `empty` | No body allowed |
| `scriptless` | EL and standard actions only (no scriptlets) |
| `JSP` | Full JSP content including scriptlets |
| `tagdependent` | Body treated as literal text (not evaluated) |

---

## Chapter 11: JavaBeans in JSP

### JavaBean Rules
```java
// Must have: no-arg constructor, public getters/setters, implement Serializable (recommended)
public class Product implements java.io.Serializable {
    private int id;
    private String name;
    private double price;

    public Product() {}          // required by jsp:useBean

    // getters and setters following naming convention
    public int getId()             { return id; }
    public void setId(int id)      { this.id = id; }
    public String getName()        { return name; }
    public void setName(String n)  { this.name = n; }
    public double getPrice()       { return price; }
    public void setPrice(double p) { this.price = p; }
}
```

### Using a JavaBean in JSP
```jsp
<!-- Create or retrieve bean from specified scope -->
<jsp:useBean id="product" class="com.example.Product" scope="request"/>

<!-- Set all properties from matching request params (param names must match property names) -->
<jsp:setProperty name="product" property="*"/>

<!-- Set one property from a specific param -->
<jsp:setProperty name="product" property="name" param="productName"/>

<!-- Set one property to a literal value -->
<jsp:setProperty name="product" property="price" value="19.99"/>

<!-- Access a property -->
<jsp:getProperty name="product" property="name"/>

<!-- Or use EL (preferred) -->
${product.name}
${product.price}
```

### Scope and Bean Lifecycle
```jsp
<!-- scope="page" — default, this JSP only -->
<jsp:useBean id="bean" class="com.example.Foo" scope="page"/>

<!-- scope="request" — for this request (incl. forwarded JSPs) -->
<jsp:useBean id="bean" class="com.example.Foo" scope="request"/>

<!-- scope="session" — lives until session expires -->
<jsp:useBean id="bean" class="com.example.Foo" scope="session"/>

<!-- scope="application" — lives until server restart -->
<jsp:useBean id="bean" class="com.example.Foo" scope="application"/>
```

### Populating a Bean from a Form (Classic Pattern)
```java
// In servlet: populate bean and forward
Product product = new Product();
product.setName(request.getParameter("name"));
product.setPrice(Double.parseDouble(request.getParameter("price")));
request.setAttribute("product", product);
request.getRequestDispatcher("/WEB-INF/views/product.jsp")
       .forward(request, response);
```
```jsp
<!-- In JSP: display using EL -->
<p>Name: ${product.name}</p>
<p>Price: <fmt:formatNumber value="${product.price}" type="currency"/></p>
```

---

## Common JSP / EL / JSTL Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| `${product.name}` prints empty | Attribute not set in request scope | `request.setAttribute("product", ...)` in servlet |
| JSTL tags printed as text | `<%@ taglib %>` directive missing | Add correct taglib directive at top of JSP |
| `ClassNotFoundException` for JSTL | `jstl.jar` not in `WEB-INF/lib` | Add JSTL dependency to pom.xml |
| `<c:forEach>` not looping | `items` attribute evaluates to null | Check spelling of attribute name set in servlet |
| EL returns wrong scope | Same name used in multiple scopes | Use explicit scope: `${requestScope.name}` |
| JSP not recompiling | Cached class file | Delete `work/` folder in Tomcat; restart |
| Custom tag not found | TLD not in `WEB-INF/` or wrong URI | Place `.tld` in `WEB-INF/`; check `uri` matches taglib directive |
