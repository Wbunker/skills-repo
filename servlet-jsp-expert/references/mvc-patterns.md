# MVC Patterns and Control Flow
*Chapters 4–5 — RequestDispatcher, Forward vs. Redirect, MVC Pattern, Layered Architecture*

## Chapter 4: How to Transfer Control Between Pages

### Forward vs. Redirect — The Core Decision

```
forward(request, response)          sendRedirect(url)
─────────────────────────────────   ──────────────────────────────────
Same request object                 New request (browser makes 2nd GET)
URL stays the same                  URL changes in browser
Fast — no extra round trip          Extra HTTP round trip
Can pass request attributes         Cannot pass request attributes
Use: pass data to a JSP view        Use: after POST (PRG), external URLs
Server-side operation               Client-side instruction (302)
```

### RequestDispatcher — Forward
```java
@WebServlet("/products")
public class ProductServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response)
            throws ServletException, IOException {

        // 1. Business logic
        List<Product> products = productService.getAll();

        // 2. Put data in request scope for JSP
        request.setAttribute("products", products);

        // 3. Forward to view — URL stays /products
        RequestDispatcher dispatcher =
            request.getRequestDispatcher("/WEB-INF/views/product_list.jsp");
        dispatcher.forward(request, response);
        // Nothing after forward — response is committed
    }
}
```

**IMPORTANT:** Always store JSPs under `/WEB-INF/` so they cannot be accessed directly by URL — only through a servlet forward.

### RequestDispatcher — Include
```java
// Include response of another resource into current response
// (useful for headers, footers, fragments)
RequestDispatcher rd =
    request.getRequestDispatcher("/WEB-INF/includes/nav.jsp");
rd.include(request, response);
```
Unlike forward, execution continues in the calling servlet after include.

### Redirect After POST (PRG Pattern)
```java
@Override
protected void doPost(HttpServletRequest request,
                      HttpServletResponse response)
        throws ServletException, IOException {

    // Process form submission
    String name = request.getParameter("name");
    productService.create(name);

    // Redirect to GET — prevents duplicate submission on refresh
    response.sendRedirect(request.getContextPath() + "/products");
}
```

### Passing Data to a Redirect (Session Trick)
```java
// In POST handler: store flash message in session
request.getSession().setAttribute("flashMsg", "Product created!");
response.sendRedirect(request.getContextPath() + "/products");

// In GET handler (ProductServlet.doGet):
String msg = (String) request.getSession().getAttribute("flashMsg");
if (msg != null) {
    request.setAttribute("flashMsg", msg);
    request.getSession().removeAttribute("flashMsg");
}
```

### Relative vs. Absolute Paths
```java
// ABSOLUTE (from context root) — preferred, unambiguous
request.getRequestDispatcher("/WEB-INF/views/list.jsp").forward(req, resp);
response.sendRedirect(request.getContextPath() + "/products");

// RELATIVE — relative to current servlet URL (fragile, avoid)
request.getRequestDispatcher("list.jsp").forward(req, resp);
```

### The getContextPath() Pattern
```java
// Always prefix redirects with getContextPath() to stay portable
response.sendRedirect(request.getContextPath() + "/login");
// Result: /myapp/login   (not /login which would miss the context root)
```

---

## Chapter 5: The MVC Pattern

### MVC Responsibilities

```
┌─────────────────────────────────────────────────────────────┐
│                         MVC FLOW                            │
│                                                             │
│  Browser ──GET/POST──▶ Controller ──forward──▶ View (JSP)  │
│                         (Servlet)                           │
│                             │                               │
│                             │ calls                         │
│                             ▼                               │
│                      Service Layer                          │
│                      (business logic)                       │
│                             │                               │
│                             │ calls                         │
│                             ▼                               │
│                       DAO Layer                             │
│                       (data access)                         │
│                             │                               │
│                             ▼                               │
│                          Database                           │
└─────────────────────────────────────────────────────────────┘
```

### Controller (Servlet)
```java
@WebServlet("/products/*")
public class ProductController extends HttpServlet {

    private ProductService productService;

    @Override
    public void init() {
        // Initialize service (or use a factory/DI)
        productService = new ProductService();
    }

    @Override
    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response)
            throws ServletException, IOException {

        String pathInfo = request.getPathInfo(); // /list, /detail, etc.

        if (pathInfo == null || "/list".equals(pathInfo)) {
            listProducts(request, response);
        } else if (pathInfo.startsWith("/detail/")) {
            showDetail(request, response, pathInfo);
        } else {
            response.sendError(HttpServletResponse.SC_NOT_FOUND);
        }
    }

    private void listProducts(HttpServletRequest req,
                              HttpServletResponse resp)
            throws ServletException, IOException {
        req.setAttribute("products", productService.getAll());
        req.getRequestDispatcher("/WEB-INF/views/product_list.jsp")
           .forward(req, resp);
    }

    private void showDetail(HttpServletRequest req,
                            HttpServletResponse resp,
                            String pathInfo)
            throws ServletException, IOException {
        int id = Integer.parseInt(pathInfo.substring("/detail/".length()));
        Product p = productService.getById(id);
        if (p == null) {
            resp.sendError(HttpServletResponse.SC_NOT_FOUND);
            return;
        }
        req.setAttribute("product", p);
        req.getRequestDispatcher("/WEB-INF/views/product_detail.jsp")
           .forward(req, resp);
    }
}
```

### Model (POJO / Domain Object)
```java
// Simple value object — data container
public class Product {
    private int id;
    private String name;
    private String description;
    private double price;
    private int stock;

    // No-arg constructor + all-arg constructor + getters/setters
    public Product() {}

    public Product(int id, String name, double price) {
        this.id = id;
        this.name = name;
        this.price = price;
    }

    // getters / setters omitted for brevity
}
```

### Service Layer
```java
// Business logic — no servlet/HTTP code here
public class ProductService {

    private ProductDAO productDAO;

    public ProductService() {
        this.productDAO = new ProductDAO();
    }

    public List<Product> getAll() {
        return productDAO.selectAll();
    }

    public Product getById(int id) {
        return productDAO.selectById(id);
    }

    public void create(Product product) {
        // Validate
        if (product.getName() == null || product.getName().isBlank()) {
            throw new IllegalArgumentException("Name is required");
        }
        if (product.getPrice() < 0) {
            throw new IllegalArgumentException("Price cannot be negative");
        }
        productDAO.insert(product);
    }

    public void delete(int id) {
        productDAO.delete(id);
    }
}
```

### DAO Layer (Data Access Object)
```java
// Only database access — no business rules
public class ProductDAO {

    public List<Product> selectAll() {
        // JDBC or JPA query
        List<Product> products = new ArrayList<>();
        // ... see database.md for full JDBC example
        return products;
    }

    public Product selectById(int id) {
        // ...
        return null;
    }

    public void insert(Product product) {
        // ...
    }

    public void delete(int id) {
        // ...
    }
}
```

### View (JSP under /WEB-INF/views/)
```jsp
<%-- /WEB-INF/views/product_list.jsp --%>
<%@ page contentType="text/html;charset=UTF-8" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/fmt"  prefix="fmt" %>
<!DOCTYPE html>
<html>
<head><title>Products</title></head>
<body>
  <c:if test="${not empty flashMsg}">
    <div class="alert">${flashMsg}</div>
  </c:if>

  <table>
    <c:forEach var="p" items="${products}">
      <tr>
        <td><a href="${pageContext.request.contextPath}/products/detail/${p.id}">${p.name}</a></td>
        <td><fmt:formatNumber value="${p.price}" type="currency"/></td>
      </tr>
    </c:forEach>
  </table>
</body>
</html>
```

### Application-Scoped (ServletContext) Attributes
```java
// Store app-wide data once at startup
@WebListener
public class AppContextListener implements ServletContextListener {

    @Override
    public void contextInitialized(ServletContextEvent sce) {
        ServletContext ctx = sce.getServletContext();
        // Load config, warm up caches
        ctx.setAttribute("appVersion", "1.0.0");
        ctx.setAttribute("categoryList", loadCategories());
    }

    @Override
    public void contextDestroyed(ServletContextEvent sce) {
        // Release resources
    }
}

// Access from any servlet:
String version = (String) getServletContext().getAttribute("appVersion");

// Access from JSP via EL:
// ${applicationScope.appVersion}
// ${applicationScope.categoryList}
```

### Front Controller Pattern (Single Entry Point)
For larger apps, route all requests through one servlet:
```java
@WebServlet("/")
public class FrontController extends HttpServlet {

    private Map<String, Command> commandMap;

    @Override
    public void init() {
        commandMap = new HashMap<>();
        commandMap.put("listProducts", new ListProductsCommand());
        commandMap.put("showCart",     new ShowCartCommand());
        commandMap.put("checkout",     new CheckoutCommand());
    }

    @Override
    protected void service(HttpServletRequest req,
                           HttpServletResponse resp)
            throws ServletException, IOException {

        String action = req.getParameter("action");
        Command cmd = commandMap.getOrDefault(action,
                          commandMap.get("listProducts"));
        String viewPath = cmd.execute(req, resp);
        if (viewPath != null) {
            req.getRequestDispatcher(viewPath).forward(req, resp);
        }
    }
}

public interface Command {
    String execute(HttpServletRequest req, HttpServletResponse resp)
        throws ServletException, IOException;
}
```

---

## Common MVC Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| JSP accessed directly (bypasses security) | JSP in webapp root | Move all JSPs under `/WEB-INF/` |
| Attributes not visible in JSP | Set on wrong scope | Use `request.setAttribute()` before forward |
| Duplicate form submission | No redirect after POST | Implement PRG: redirect after successful POST |
| Business logic in JSP scriptlets | Violates MVC separation | Move logic to service layer; use EL+JSTL in JSP |
| Context path wrong in links | Hardcoded paths | Use `${pageContext.request.contextPath}` prefix |
| RequestDispatcher path wrong | Typo in view path | Verify path from webapp root, including leading `/` |
