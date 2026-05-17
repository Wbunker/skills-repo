# Web Presentation Patterns — PEAA

These patterns organize the web presentation layer: how HTTP requests are handled, how domain data is turned into HTML, and how screen flow is managed.

---

## Model View Controller (MVC)

**Intent**: Splits user interface interaction into three distinct roles: Model (state and behavior), View (display), Controller (input handling).

**The Three Roles**

| Role | Responsibility | Examples |
|---|---|---|
| **Model** | Domain objects and application state. Notifies View of changes. | Domain objects, Service Layer, DTOs |
| **View** | Renders the model for display. Observes Model for updates. | JSP, Thymeleaf template, React component |
| **Controller** | Receives input, updates Model, selects View. | Servlet, @Controller method, action class |

**Two MVC Variants**

1. **Web MVC** (most common in enterprise apps): Request-response; no persistent View observation
   - Controller receives HTTP request
   - Controller invokes domain/service
   - Controller selects View, passes Model data
   - View renders HTML response
   - (No persistent observer relationship; Model doesn't call View)

2. **Rich Client MVC** (Smalltalk original): Observer pattern between Model and View
   - Model publishes change events
   - View subscribes and updates in response
   - Used in desktop UIs, SPA frameworks

**Core Principle**
Never put domain logic in Views. Never put rendering logic in domain objects. Controllers should be thin — delegate to domain/service.

**Modern Frameworks Implementing Web MVC**
- Spring MVC (`@Controller`, `@GetMapping`, `Model`, `ModelAndView`)
- ASP.NET MVC
- Jakarta MVC (former MVC 1.0)
- Django (MTV — Model-Template-View, same concept)
- Ruby on Rails

---

## Page Controller

**Intent**: An object that handles a request for a specific page or action on a website.

**Structure**
- One controller class (or method) per page or URL pattern
- Handles input, invokes domain, passes model to view, forwards to view

**Example (Spring MVC)**
```java
@Controller
public class OrderDetailController {

    private final OrderService orderService;

    @GetMapping("/orders/{id}")
    public String show(@PathVariable Long id, Model model) {
        Order order = orderService.findById(id);
        model.addAttribute("order", order);
        return "orders/detail";          // view name
    }

    @PostMapping("/orders/{id}/submit")
    public String submit(@PathVariable Long id, RedirectAttributes ra) {
        orderService.submitOrder(id);
        ra.addFlashAttribute("message", "Order submitted");
        return "redirect:/orders/" + id;
    }
}
```

**Pros**
- Simple to understand; natural mapping of URL → class/method
- Easy to navigate — one place per page
- Framework-idiomatic (most web frameworks use Page Controller)

**Cons**
- Cross-cutting logic (auth, logging, encoding) scattered or repeated
- Complex navigation logic spreads across many controllers

**When to Use**: Most web applications. Default choice unless navigation complexity is high.

---

## Front Controller

**Intent**: Consolidates all request handling by channeling requests through a single handler object.

**Structure**
- **Handler (Front Controller)**: Receives all requests; authenticates; selects and invokes a Command
- **Command / Handler**: One class per operation; contains request-specific logic
- **Dispatcher**: Routes request to the right Command

**Benefits**
- Single point for cross-cutting concerns: authentication, logging, encoding, transaction wrapping
- Navigation logic centralized in one place
- Easy to add new commands without touching core request handling

**Contrast with Page Controller**
- Page Controller: logic distributed across many controllers, each handles its URL
- Front Controller: one entry point, dispatches to command objects

**Example (simplified)**
```java
// Front Controller Servlet
@WebServlet("/*")
public class FrontControllerServlet extends HttpServlet {
    private CommandFactory factory = new CommandFactory();

    @Override
    protected void service(HttpServletRequest req, HttpServletResponse res)
            throws ServletException, IOException {
        // cross-cutting concerns
        if (!authService.isAuthenticated(req)) {
            res.sendRedirect("/login");
            return;
        }
        // dispatch
        String path = req.getPathInfo();
        Command command = factory.create(path, req.getMethod());
        command.execute(req, res);
    }
}

// Command per operation
public class SubmitOrderCommand implements Command {
    public void execute(HttpServletRequest req, HttpServletResponse res)
            throws Exception {
        long orderId = Long.parseLong(req.getParameter("id"));
        orderService.submitOrder(orderId);
        res.sendRedirect("/orders/" + orderId);
    }
}
```

**Modern Implementations**: Spring MVC's `DispatcherServlet` IS a Front Controller. Jakarta EE's `FacesServlet` for JSF. Most mature web frameworks are Front Controller architectures internally, with Page Controller-style handlers as the developer-facing API.

**When to Use**
- Many cross-cutting concerns across all requests (auth, logging, locale)
- Complex navigation or workflow management
- Large applications with many URL patterns

---

## Template View

**Intent**: Renders information into HTML by embedding markers in an HTML page.

**How It Works**
- Template = mostly static HTML with placeholder markers/tags
- At render time, markers are replaced with data from the model

**Example (Thymeleaf)**
```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<body>
  <h1 th:text="${order.id}">Order #</h1>
  <p th:text="${order.status}">Status</p>
  <table>
    <tr th:each="item : ${order.lineItems}">
      <td th:text="${item.productName}">Product</td>
      <td th:text="${item.quantity}">Qty</td>
      <td th:text="${item.subtotal}">Subtotal</td>
    </tr>
  </table>
</body>
</html>
```

**Example (JSP)**
```jsp
<h1>Order #${order.id}</h1>
<p>Status: ${order.status}</p>
<c:forEach items="${order.lineItems}" var="item">
  <tr>
    <td>${item.productName}</td>
    <td>${item.quantity}</td>
  </tr>
</c:forEach>
```

**Pros**
- Intuitive — designers can work with HTML; developers add markers
- Most web frameworks provide Template View support
- Natural structure for HTML output

**Cons**
- Risk of adding logic to templates (scriptlets in JSPs, complex Thymeleaf expressions)
- Hard to generate multiple output formats from same template

**Rule**: Keep templates logic-free. Move any conditional or calculation logic into the controller or a helper/presenter object, not the template.

**When to Use**: Default choice for HTML output in nearly all web applications.

---

## Transform View

**Intent**: A view that processes domain data element by element and transforms it to HTML (or another output format).

**How It Works**
- Domain layer produces a data structure (typically XML or a tree)
- Transform View applies a transformation (XSLT stylesheet, template function) to produce output

**Classic Implementation (XSLT)**
```xml
<!-- domain.xml -->
<order id="42" status="submitted">
  <lineItem product="Widget" quantity="3" price="9.99"/>
</order>

<!-- transform.xsl -->
<xsl:template match="order">
  <h1>Order <xsl:value-of select="@id"/></h1>
  <xsl:apply-templates select="lineItem"/>
</xsl:template>

<xsl:template match="lineItem">
  <tr>
    <td><xsl:value-of select="@product"/></td>
    <td><xsl:value-of select="@quantity"/></td>
  </tr>
</xsl:template>
```

**Pros**
- Clean separation: domain produces data; view transforms it
- Multiple transforms can produce different output formats (HTML, PDF, XML) from the same domain data
- No risk of domain logic in view — transform only accesses the data structure, not domain objects

**Cons**
- XSLT has a steep learning curve; complex transformations are hard to write
- Less common in modern Java web apps — Thymeleaf/Freemarker have displaced it

**When to Use**
- Need multiple output formats (HTML + RSS + PDF + API XML) from the same domain data
- Content is naturally hierarchical/XML
- Less relevant in modern API-first (JSON) architectures

---

## Two Step View

**Intent**: Turns domain data into HTML in two steps: first converting domain data into a logical page structure, then rendering the logical page into HTML.

**Two Steps**
1. **Step 1 — Domain → Logical Page**: Controller converts domain data into a generic logical page structure (a presentation-layer tree, not HTML-specific). This step is output-format agnostic.
2. **Step 2 — Logical Page → HTML**: A second transformation renders the logical page structure into actual HTML, applying the site's visual design (headers, footers, layout, CSS classes).

**Motivation**
Changing site-wide layout (e.g., moving navigation from left sidebar to top bar) requires changing only the Step 2 renderer — Step 1 logic is untouched. Without Two Step View, each page's template would need updating.

**Example Concept**
```
Step 1: OrderController → OrderPage (logical)
  OrderPage {
    title: "Order #42"
    sections: [
      Table { columns: [Product, Qty, Price], rows: [...] }
      StatusBadge { text: "Submitted" }
    ]
  }

Step 2: SiteLayoutRenderer renders OrderPage into:
  <html>
    <header>...</header>         <!-- consistent site chrome -->
    <main>
      <h1>Order #42</h1>
      <table>...</table>
      <span class="badge">Submitted</span>
    </main>
    <footer>...</footer>
  </html>
```

**When to Use**
- Large sites where consistent layout is critical and must be changeable globally
- Multiple screens using the same logical structures
- Less common now that CSS + template inheritance (Thymeleaf fragments, layout dialects) solve the same problem differently

---

## Application Controller

**Intent**: A centralized point for handling screen navigation and the flow of an application.

**Problem**: Complex screen flow (wizards, multi-step forms, conditional navigation) doesn't belong in page controllers. Without centralization, navigation logic is scattered.

**Structure**
- Application Controller decides: given the current application state and the user's action, what is the next screen?
- Page controllers delegate navigation decisions to the Application Controller
- Application Controller can also enforce valid state transitions

**Example**
```java
public class CheckoutController {
    // State machine for checkout flow
    public String nextScreen(CheckoutState state, String action) {
        return switch (state) {
            case CART -> switch (action) {
                case "proceed" -> "shipping-address";
                default -> "cart";
            };
            case SHIPPING_ADDRESS -> switch (action) {
                case "proceed" -> "payment";
                case "back"    -> "cart";
                default        -> "shipping-address";
            };
            case PAYMENT -> switch (action) {
                case "proceed" -> "order-confirmation";
                case "back"    -> "shipping-address";
                default        -> "payment";
            };
            default -> throw new IllegalStateException();
        };
    }
}
```

**Interaction with Page Controller / Front Controller**
```java
// In a Front Controller command or Page Controller:
String nextView = appController.nextScreen(session.checkoutState(), action);
response.forward(nextView);
```

**When to Use**
- Multi-step workflows (checkout, registration wizard, claims processing)
- Conditional navigation (different next screen based on data)
- When navigation logic is complex enough to deserve its own class

**When to Avoid**
- Simple CRUD sites with no complex flow — overhead not justified
