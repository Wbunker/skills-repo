# Setup and Servlets
*Chapters 1–2 — Development Environment, Servlet Lifecycle, HTTP API*

## Chapter 1: Setting Up Your Development Environment

### Tomcat Installation
1. Download Tomcat 9.x or 10.x from tomcat.apache.org
2. Extract to a directory (e.g., `/opt/tomcat` or `C:\tomcat`)
3. Set `CATALINA_HOME` environment variable
4. Start: `bin/startup.sh` (Unix) or `bin\startup.bat` (Windows)
5. Verify: http://localhost:8080

**Key Tomcat directories:**
| Directory | Purpose |
|-----------|---------|
| `webapps/` | Deploy WAR files or exploded directories here |
| `conf/server.xml` | Port config, virtual hosts |
| `conf/web.xml` | Default servlet mappings, MIME types |
| `conf/tomcat-users.xml` | Roles and credentials for Manager app |
| `logs/catalina.out` | Main server log |

### Maven Project Setup
```xml
<!-- pom.xml -->
<packaging>war</packaging>

<dependencies>
  <!-- Servlet API (provided by container) -->
  <dependency>
    <groupId>jakarta.servlet</groupId>
    <artifactId>jakarta.servlet-api</artifactId>
    <version>5.0.0</version>
    <scope>provided</scope>
  </dependency>
  <!-- JSP API -->
  <dependency>
    <groupId>jakarta.servlet.jsp</groupId>
    <artifactId>jakarta.servlet.jsp-api</artifactId>
    <version>3.0.0</version>
    <scope>provided</scope>
  </dependency>
  <!-- JSTL -->
  <dependency>
    <groupId>org.glassfish.web</groupId>
    <artifactId>jakarta.servlet.jsp.jstl</artifactId>
    <version>2.0.0</version>
  </dependency>
</dependencies>

<build>
  <plugins>
    <plugin>
      <groupId>org.apache.tomcat.maven</groupId>
      <artifactId>tomcat9-maven-plugin</artifactId>
      <version>2.2</version>
    </plugin>
  </plugins>
</build>
```

### WAR Structure
```
myapp.war
├── WEB-INF/
│   ├── web.xml          ← deployment descriptor
│   ├── classes/         ← compiled .class files
│   └── lib/             ← JAR dependencies
├── index.jsp
├── css/
└── js/
```

### web.xml Essentials
```xml
<?xml version="1.0" encoding="UTF-8"?>
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee"
         version="5.0">

  <welcome-file-list>
    <welcome-file>index.jsp</welcome-file>
  </welcome-file-list>

  <!-- Servlet declaration (without @WebServlet annotation) -->
  <servlet>
    <servlet-name>ProductServlet</servlet-name>
    <servlet-class>com.example.ProductServlet</servlet-class>
    <load-on-startup>1</load-on-startup>
  </servlet>
  <servlet-mapping>
    <servlet-name>ProductServlet</servlet-name>
    <url-pattern>/products</url-pattern>
  </servlet-mapping>

  <!-- Session timeout in minutes -->
  <session-config>
    <session-timeout>30</session-timeout>
  </session-config>

</web-app>
```

---

## Chapter 2: How to Develop a Servlet

### Minimal Servlet
```java
import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;

@WebServlet("/hello")          // maps URL /hello to this servlet
public class HelloServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response)
            throws ServletException, IOException {

        response.setContentType("text/html;charset=UTF-8");
        PrintWriter out = response.getWriter();
        out.println("<html><body>");
        out.println("<h1>Hello, Servlet!</h1>");
        out.println("</body></html>");
    }
}
```

### @WebServlet Annotation Options
```java
@WebServlet(
    name        = "ProductServlet",
    urlPatterns = {"/products", "/products/*"},
    loadOnStartup = 1           // preload on startup (positive = ordered)
)
public class ProductServlet extends HttpServlet { ... }
```

### URL Patterns
| Pattern | Matches |
|---------|---------|
| `/products` | Exact: /products only |
| `/products/*` | Path: /products/123, /products/list |
| `*.do` | Extension: /anything.do |
| `/` | Default: everything not matched elsewhere |
| `/*` | Catch-all (overrides static files — rarely use) |

### Servlet Lifecycle Methods
```java
public class MyServlet extends HttpServlet {

    // Called once after instantiation; load resources here
    @Override
    public void init() throws ServletException {
        // read init params:
        String dsName = getServletConfig()
                          .getInitParameter("datasource");
        // or from web.xml <init-param>
    }

    // Called per GET request (overrides service())
    @Override
    protected void doGet(HttpServletRequest req,
                         HttpServletResponse resp)
            throws ServletException, IOException { ... }

    // Called per POST request
    @Override
    protected void doPost(HttpServletRequest req,
                          HttpServletResponse resp)
            throws ServletException, IOException { ... }

    // Called once before unloading; release resources
    @Override
    public void destroy() { ... }
}
```

### HttpServletRequest API
```java
// URL and method info
String method  = request.getMethod();           // "GET", "POST"
String uri     = request.getRequestURI();       // "/myapp/products"
String context = request.getContextPath();      // "/myapp"
String servlet = request.getServletPath();      // "/products"
String pathInfo = request.getPathInfo();        // "/123" (from /products/123)
String query   = request.getQueryString();      // "page=2&sort=name"

// Parameters (query string or form body)
String name    = request.getParameter("name");          // single value
String[] vals  = request.getParameterValues("color");   // multi-value
Map<String,String[]> all = request.getParameterMap();

// Headers
String accept  = request.getHeader("Accept");
String agent   = request.getHeader("User-Agent");
Enumeration<String> names = request.getHeaderNames();

// Request attributes (set by servlets for JSP)
request.setAttribute("products", productList);
Object products = request.getAttribute("products");

// Input stream (for POST bodies)
BufferedReader reader = request.getReader();
// or binary:
ServletInputStream in = request.getInputStream();

// Session and cookies
HttpSession session = request.getSession();
HttpSession existing = request.getSession(false); // null if none
Cookie[] cookies = request.getCookies();
```

### HttpServletResponse API
```java
// Status code
response.setStatus(200);                        // OK (default)
response.setStatus(HttpServletResponse.SC_NOT_FOUND);  // 404
response.sendError(404, "Product not found");

// Headers
response.setContentType("application/json;charset=UTF-8");
response.setHeader("Cache-Control", "no-store");
response.addCookie(new Cookie("theme", "dark"));

// Redirect
response.sendRedirect("/myapp/products");       // absolute context path
response.sendRedirect(response.encodeRedirectURL("/myapp/cart"));

// Output
PrintWriter out = response.getWriter();          // text (HTML, JSON, XML)
ServletOutputStream sos = response.getOutputStream(); // binary
```

### Reading Init Parameters
```java
// Per-servlet init param (web.xml <init-param> or @WebInitParam)
@WebServlet(urlPatterns="/report",
    initParams = @WebInitParam(name="maxRows", value="100"))
public class ReportServlet extends HttpServlet {

    private int maxRows;

    @Override
    public void init() {
        maxRows = Integer.parseInt(
            getServletConfig().getInitParameter("maxRows"));
    }
}

// App-wide context param (web.xml <context-param>)
String appName = getServletContext()
                   .getInitParameter("appName");
```

### Handling Multiple HTTP Methods
```java
@WebServlet("/product")
public class ProductServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest req,
                         HttpServletResponse resp) throws ... {
        // Show product detail or list
    }

    @Override
    protected void doPost(HttpServletRequest req,
                          HttpServletResponse resp) throws ... {
        // Create new product
    }

    @Override
    protected void doPut(HttpServletRequest req,
                         HttpServletResponse resp) throws ... {
        // Update product
    }

    @Override
    protected void doDelete(HttpServletRequest req,
                            HttpServletResponse resp) throws ... {
        // Delete product
    }
}
```

### Sending JSON Response (REST-style from Servlet)
```java
@Override
protected void doGet(HttpServletRequest req,
                     HttpServletResponse resp)
        throws ServletException, IOException {

    resp.setContentType("application/json;charset=UTF-8");
    resp.setHeader("Access-Control-Allow-Origin", "*"); // CORS if needed

    // With a JSON library (Gson, Jackson):
    String json = gson.toJson(productService.findAll());
    resp.getWriter().write(json);
}
```

### Common Mistakes and Fixes

| Problem | Cause | Fix |
|---------|-------|-----|
| `getWriter() has already been called` | Called both `getWriter()` and `getOutputStream()` | Use only one per response |
| Response already committed | Wrote output before `sendRedirect`/`sendError` | Call redirect/error before writing any output |
| `NullPointerException` on `getParameter` | Parameter name typo or wrong form method | Check form `name=` attributes and `method="post"` |
| 404 for servlet | URL pattern mismatch or missing annotation | Verify `@WebServlet` pattern matches the link href |
| Servlet runs on startup but not on request | `loadOnStartup` without correct URL pattern | Separate startup init from URL mapping |
| Instance variable shared across threads | Stored mutable state in a field | Use `request.setAttribute()` or local variables |
