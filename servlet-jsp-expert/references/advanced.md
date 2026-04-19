# Advanced Features
*Chapters 12–14 — Filters, Event Listeners, Ajax with Servlets, File Uploads, JavaMail*

## Chapter 12: Filters and Event Listeners

### Filter Interface
```java
import jakarta.servlet.*;
import jakarta.servlet.annotation.WebFilter;
import java.io.IOException;

@WebFilter("/*")          // applies to all URLs
public class LoggingFilter implements Filter {

    @Override
    public void init(FilterConfig config) throws ServletException {
        // called once at deployment; load resources here
        String logLevel = config.getInitParameter("logLevel");
    }

    @Override
    public void doFilter(ServletRequest request, ServletResponse response,
                         FilterChain chain) throws IOException, ServletException {

        HttpServletRequest  req  = (HttpServletRequest)  request;
        HttpServletResponse resp = (HttpServletResponse) response;

        long start = System.currentTimeMillis();
        String uri = req.getRequestURI();

        // PRE-processing (before servlet)
        System.out.println("Incoming: " + req.getMethod() + " " + uri);

        chain.doFilter(request, response);   // call next filter or servlet

        // POST-processing (after servlet, before response sent)
        long elapsed = System.currentTimeMillis() - start;
        System.out.println("Completed: " + uri + " in " + elapsed + "ms");
    }

    @Override
    public void destroy() {
        // called once at undeployment; release resources
    }
}
```

### @WebFilter Options
```java
@WebFilter(
    filterName   = "EncodingFilter",
    urlPatterns  = {"/api/*", "/form/*"},
    servletNames = {"ProductServlet"},       // can target specific servlets
    initParams   = @WebInitParam(name="encoding", value="UTF-8"),
    dispatcherTypes = {DispatcherType.REQUEST, DispatcherType.FORWARD}
)
```

**Dispatcher types:**
| Type | When filter runs |
|------|----------------|
| `REQUEST` | Normal HTTP request (default) |
| `FORWARD` | After `RequestDispatcher.forward()` |
| `INCLUDE` | After `RequestDispatcher.include()` |
| `ERROR` | When container routes to error page |
| `ASYNC` | Async dispatch |

### Filter Ordering
Filters execute in the order they are declared in `web.xml`. With annotations only, order is unspecified. For guaranteed order, declare filters in `web.xml`:
```xml
<filter>
  <filter-name>AuthFilter</filter-name>
  <filter-class>com.example.AuthFilter</filter-class>
</filter>
<filter-mapping>
  <filter-name>AuthFilter</filter-name>
  <url-pattern>/account/*</url-pattern>
</filter-mapping>

<filter>
  <filter-name>LoggingFilter</filter-name>
  <filter-class>com.example.LoggingFilter</filter-class>
</filter>
<filter-mapping>
  <filter-name>LoggingFilter</filter-name>
  <url-pattern>/*</url-pattern>
</filter-mapping>
```

### Common Filter Patterns

**Encoding Filter (set charset before any reading):**
```java
@WebFilter("/*")
public class CharsetFilter implements Filter {
    @Override
    public void doFilter(ServletRequest req, ServletResponse resp,
                         FilterChain chain) throws IOException, ServletException {
        req.setCharacterEncoding("UTF-8");
        resp.setCharacterEncoding("UTF-8");
        chain.doFilter(req, resp);
    }
    @Override public void init(FilterConfig c) {}
    @Override public void destroy() {}
}
```

**CORS Filter:**
```java
@WebFilter("/api/*")
public class CorsFilter implements Filter {
    @Override
    public void doFilter(ServletRequest request, ServletResponse response,
                         FilterChain chain) throws IOException, ServletException {
        HttpServletResponse resp = (HttpServletResponse) response;
        HttpServletRequest  req  = (HttpServletRequest) request;

        resp.setHeader("Access-Control-Allow-Origin",  "https://myfrontend.com");
        resp.setHeader("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
        resp.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
        resp.setHeader("Access-Control-Max-Age",       "3600");

        if ("OPTIONS".equalsIgnoreCase(req.getMethod())) {
            resp.setStatus(HttpServletResponse.SC_OK);
            return;
        }
        chain.doFilter(request, response);
    }
    @Override public void init(FilterConfig c) {}
    @Override public void destroy() {}
}
```

---

### Event Listeners

#### ServletContextListener — App Startup/Shutdown
```java
@WebListener
public class AppStartupListener implements ServletContextListener {

    @Override
    public void contextInitialized(ServletContextEvent sce) {
        ServletContext ctx = sce.getServletContext();
        System.out.println("App starting...");

        // Initialize shared resources
        ctx.setAttribute("startTime", System.currentTimeMillis());

        // E.g., pre-load a configuration or category list
        // ctx.setAttribute("categories", loadCategories());
    }

    @Override
    public void contextDestroyed(ServletContextEvent sce) {
        System.out.println("App shutting down...");
        // Close connection pools, thread pools, etc.
    }
}
```

#### HttpSessionListener — Session Created/Destroyed
```java
@WebListener
public class SessionCountListener implements HttpSessionListener {

    private static final AtomicInteger activeSessions = new AtomicInteger(0);

    @Override
    public void sessionCreated(HttpSessionEvent se) {
        int count = activeSessions.incrementAndGet();
        System.out.println("Session created. Active: " + count);
    }

    @Override
    public void sessionDestroyed(HttpSessionEvent se) {
        int count = activeSessions.decrementAndGet();
        System.out.println("Session destroyed. Active: " + count);
    }

    public static int getActiveSessionCount() {
        return activeSessions.get();
    }
}
```

#### HttpSessionAttributeListener — Track Attribute Changes
```java
@WebListener
public class UserLoginListener implements HttpSessionAttributeListener {

    @Override
    public void attributeAdded(HttpSessionBindingEvent event) {
        if ("user".equals(event.getName())) {
            User user = (User) event.getValue();
            System.out.println("User logged in: " + user.getUsername());
        }
    }

    @Override
    public void attributeRemoved(HttpSessionBindingEvent event) {
        if ("user".equals(event.getName())) {
            System.out.println("User logged out");
        }
    }

    @Override
    public void attributeReplaced(HttpSessionBindingEvent event) {}
}
```

#### ServletRequestListener
```java
@WebListener
public class RequestTimingListener implements ServletRequestListener {
    @Override
    public void requestInitialized(ServletRequestEvent sre) {
        sre.getServletRequest().setAttribute("_startTime", System.nanoTime());
    }

    @Override
    public void requestDestroyed(ServletRequestEvent sre) {
        long start = (long) sre.getServletRequest().getAttribute("_startTime");
        long ms = (System.nanoTime() - start) / 1_000_000;
        System.out.println("Request took " + ms + "ms");
    }
}
```

---

## Chapter 13: Ajax with Servlets

### JSON Response Servlet
The standard pattern: servlet returns JSON, JavaScript fetches and updates the DOM.

**Dependencies (Gson):**
```xml
<dependency>
  <groupId>com.google.code.gson</groupId>
  <artifactId>gson</artifactId>
  <version>2.10.1</version>
</dependency>
```

**Servlet:**
```java
@WebServlet("/api/products")
public class ProductApiServlet extends HttpServlet {

    private final Gson gson = new GsonBuilder()
        .setDateFormat("yyyy-MM-dd").create();
    private ProductService productService;

    @Override
    public void init() { productService = new ProductService(); }

    @Override
    protected void doGet(HttpServletRequest req,
                         HttpServletResponse resp)
            throws ServletException, IOException {

        resp.setContentType("application/json;charset=UTF-8");

        String idParam = req.getParameter("id");
        Object result;

        if (idParam != null) {
            result = productService.getById(Integer.parseInt(idParam));
            if (result == null) {
                resp.setStatus(404);
                resp.getWriter().write("{\"error\":\"Not found\"}");
                return;
            }
        } else {
            result = productService.getAll();
        }

        resp.getWriter().write(gson.toJson(result));
    }

    @Override
    protected void doPost(HttpServletRequest req,
                          HttpServletResponse resp)
            throws ServletException, IOException {

        // Read JSON body
        Product product = gson.fromJson(req.getReader(), Product.class);
        int newId = productService.create(product);

        resp.setStatus(201);
        resp.setContentType("application/json;charset=UTF-8");
        resp.getWriter().write("{\"id\":" + newId + "}");
    }
}
```

### JavaScript Fetch API (Client Side)
```javascript
// GET — load and display products
async function loadProducts() {
  try {
    const response = await fetch('/myapp/api/products');
    if (!response.ok) throw new Error('HTTP ' + response.status);
    const products = await response.json();

    const list = document.getElementById('product-list');
    list.innerHTML = products.map(p =>
      `<li>${p.name} — $${p.price.toFixed(2)}</li>`
    ).join('');
  } catch (err) {
    console.error('Failed to load products:', err);
  }
}

// POST — submit new product as JSON
async function createProduct(name, price) {
  const response = await fetch('/myapp/api/products', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, price })
  });

  if (response.ok) {
    const data = await response.json();
    console.log('Created with id:', data.id);
    loadProducts();   // refresh list
  } else {
    const err = await response.json();
    alert('Error: ' + err.error);
  }
}
```

### Traditional XMLHttpRequest (Legacy)
```javascript
function loadProducts() {
  const xhr = new XMLHttpRequest();
  xhr.open('GET', '/myapp/api/products');
  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
      const products = JSON.parse(xhr.responseText);
      // update DOM
    }
  };
  xhr.send();
}
```

### Returning HTML Fragments from Servlet
```java
// Return rendered HTML snippet instead of JSON
@WebServlet("/fragment/cart")
public class CartFragmentServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest req,
                         HttpServletResponse resp)
            throws ServletException, IOException {

        Cart cart = (Cart) req.getSession().getAttribute("cart");
        req.setAttribute("cart", cart);
        // Forward to a fragment JSP (no <html> tag, just the table)
        req.getRequestDispatcher("/WEB-INF/fragments/cart_items.jsp")
           .forward(req, resp);
    }
}
```
```javascript
async function refreshCart() {
  const html = await fetch('/myapp/fragment/cart').then(r => r.text());
  document.getElementById('cart-container').innerHTML = html;
}
```

---

## Chapter 14: File Uploads and JavaMail

### File Upload (Multipart Form Data)

**web.xml or @MultipartConfig:**
```java
@WebServlet("/upload")
@MultipartConfig(
    location        = "/tmp",         // temp storage directory
    maxFileSize     = 10 * 1024 * 1024,      // 10 MB per file
    maxRequestSize  = 50 * 1024 * 1024,      // 50 MB total request
    fileSizeThreshold = 1024 * 1024           // 1 MB threshold before writing to disk
)
public class FileUploadServlet extends HttpServlet {

    @Override
    protected void doPost(HttpServletRequest req,
                          HttpServletResponse resp)
            throws ServletException, IOException {

        // Regular form field
        String productName = req.getParameter("productName");

        // File part
        Part filePart = req.getPart("image");
        String submittedFileName = filePart.getSubmittedFileName();  // original name
        String contentType = filePart.getContentType();

        // Validate file type
        if (!contentType.startsWith("image/")) {
            resp.sendError(400, "Only image files allowed");
            return;
        }

        // Save to server directory (use absolute path, not relative)
        String uploadDir = req.getServletContext()
                             .getRealPath("/uploads");
        new java.io.File(uploadDir).mkdirs();

        // Sanitize filename to prevent path traversal
        String safeFileName = java.nio.file.Paths.get(submittedFileName)
                                  .getFileName().toString();
        String destPath = uploadDir + java.io.File.separator + safeFileName;
        filePart.write(destPath);

        req.setAttribute("message", "Uploaded: " + safeFileName);
        req.getRequestDispatcher("/WEB-INF/views/upload_result.jsp")
           .forward(req, resp);
    }
}
```

**HTML form — must use `enctype="multipart/form-data"`:**
```html
<form action="${pageContext.request.contextPath}/upload"
      method="post" enctype="multipart/form-data">
  <input type="text" name="productName" placeholder="Product Name"/>
  <input type="file" name="image" accept="image/*"/>
  <button type="submit">Upload</button>
</form>
```

**Multiple file upload:**
```java
Collection<Part> fileParts = req.getParts().stream()
    .filter(p -> p.getSubmittedFileName() != null
              && !p.getSubmittedFileName().isEmpty())
    .collect(Collectors.toList());

for (Part part : fileParts) {
    String safeFileName = Paths.get(part.getSubmittedFileName())
                               .getFileName().toString();
    part.write(uploadDir + File.separator + safeFileName);
}
```

---

### JavaMail (Sending Email)

**Dependencies:**
```xml
<dependency>
  <groupId>com.sun.mail</groupId>
  <artifactId>jakarta.mail</artifactId>
  <version>2.0.1</version>
</dependency>
```

**Basic email send:**
```java
public class EmailService {

    private static final String HOST = "smtp.gmail.com";
    private static final String PORT = "587";
    private static final String FROM = "myapp@gmail.com";
    private static final String PASS = "app-specific-password";

    public void sendEmail(String to, String subject, String body) {
        Properties props = new Properties();
        props.put("mail.smtp.auth",            "true");
        props.put("mail.smtp.starttls.enable", "true");
        props.put("mail.smtp.host",            HOST);
        props.put("mail.smtp.port",            PORT);

        Session session = Session.getInstance(props, new Authenticator() {
            @Override
            protected PasswordAuthentication getPasswordAuthentication() {
                return new PasswordAuthentication(FROM, PASS);
            }
        });

        try {
            Message message = new MimeMessage(session);
            message.setFrom(new InternetAddress(FROM));
            message.setRecipients(Message.RecipientType.TO,
                InternetAddress.parse(to));
            message.setSubject(subject);
            message.setText(body);       // plain text

            Transport.send(message);

        } catch (MessagingException e) {
            throw new RuntimeException("Failed to send email", e);
        }
    }
}
```

**HTML email with attachment:**
```java
public void sendHtmlEmail(String to, String subject,
                          String htmlBody, File attachment) throws MessagingException {

    Message message = new MimeMessage(session);
    message.setFrom(new InternetAddress(FROM));
    message.setRecipients(Message.RecipientType.TO, InternetAddress.parse(to));
    message.setSubject(subject);

    // HTML body part
    MimeBodyPart htmlPart = new MimeBodyPart();
    htmlPart.setContent(htmlBody, "text/html;charset=UTF-8");

    // Attachment part
    MimeBodyPart attachPart = new MimeBodyPart();
    attachPart.attachFile(attachment);

    // Combine
    Multipart multipart = new MimeMultipart();
    multipart.addBodyPart(htmlPart);
    multipart.addBodyPart(attachPart);
    message.setContent(multipart);

    Transport.send(message);
}
```

**JNDI Mail Session (Tomcat — configure once, inject everywhere):**
```xml
<!-- conf/context.xml -->
<Resource name="mail/AppMailer"
          auth="Container"
          type="jakarta.mail.Session"
          mail.smtp.host="smtp.gmail.com"
          mail.smtp.port="587"
          mail.smtp.auth="true"
          mail.smtp.starttls.enable="true"
          mail.smtp.user="myapp@gmail.com"
          password="app-password"/>
```
```java
// In EmailService
Context ctx = new InitialContext();
Session session = (Session) ctx.lookup("java:comp/env/mail/AppMailer");
```

---

## Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| Filter not running | URL pattern doesn't match request | Check pattern; use `/*` for all, `/api/*` for prefix |
| Filter runs twice | Mapped for both `REQUEST` and `FORWARD` | Set `dispatcherTypes = {DispatcherType.REQUEST}` |
| File upload: 500 error | `@MultipartConfig` annotation missing | Add `@MultipartConfig` to the upload servlet |
| `getPart()` returns null | Form's `enctype` missing | Ensure `enctype="multipart/form-data"` on `<form>` |
| `IOError: No such file` when writing upload | `getRealPath()` returns null in some containers | Store uploads outside the WAR using an absolute configured path |
| Ajax: no response | CORS blocked by browser | Add `Access-Control-Allow-Origin` header or use a CORS filter |
| Ajax POST: 403 | CSRF filter blocking | Include CSRF token in `X-CSRF-Token` header or exclude API endpoints from CSRF filter |
| Email: `AuthenticationFailedException` | Credentials wrong or 2FA without app password | Use app-specific password for Gmail; enable SMTP access |
| Email: `Connection refused` | Firewall blocking port 587 | Open outbound port 587 in server firewall |
