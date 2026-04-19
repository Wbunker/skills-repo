# State Management and Security
*Chapters 7–8 — HttpSession, Cookies, URL Rewriting, Authentication, Authorization*

## Chapter 7: Sessions and Cookies

### HttpSession
```java
// Get or create session
HttpSession session = request.getSession();        // creates if none
HttpSession existing = request.getSession(false);  // null if none exists

// Store and retrieve objects
session.setAttribute("user", user);
User user = (User) session.getAttribute("user");

// List all attributes
Enumeration<String> names = session.getAttributeNames();

// Remove an attribute
session.removeAttribute("cart");

// Invalidate session (on logout)
session.invalidate();

// Session metadata
String id      = session.getId();
long created   = session.getCreationTime();       // milliseconds
long lastAccess = session.getLastAccessedTime();
int timeout    = session.getMaxInactiveInterval(); // seconds
session.setMaxInactiveInterval(1800);              // 30 minutes
boolean isNew  = session.isNew();                  // first request?
```

### Session Timeout Configuration
```xml
<!-- web.xml — applies to all sessions in the app -->
<session-config>
  <session-timeout>30</session-timeout>   <!-- minutes; -1 = never -->
</session-config>
```

```java
// Programmatic — per session
session.setMaxInactiveInterval(3600);   // seconds; -1 = never
```

### Session Tracking Modes
By default, sessions use a `JSESSIONID` cookie. When cookies are disabled the container falls back to URL rewriting.

**URL Rewriting:**
```java
// Encode URLs to embed JSESSIONID when cookies may be disabled
String encodedUrl = response.encodeURL(
    request.getContextPath() + "/products");
// Result: /myapp/products;jsessionid=ABC123

String encodedRedirect = response.encodeRedirectURL(
    request.getContextPath() + "/products");
response.sendRedirect(encodedRedirect);
```

**Force cookie-only sessions (more secure):**
```xml
<!-- web.xml -->
<session-config>
  <tracking-mode>COOKIE</tracking-mode>
  <cookie-config>
    <http-only>true</http-only>
    <secure>true</secure>   <!-- HTTPS only -->
  </cookie-config>
</session-config>
```

---

### Cookies
```java
// Create and send a cookie
Cookie themeCookie = new Cookie("theme", "dark");
themeCookie.setMaxAge(60 * 60 * 24 * 30);  // 30 days; -1 = session cookie; 0 = delete
themeCookie.setPath("/");                   // accessible everywhere in app
themeCookie.setHttpOnly(true);             // not accessible via JavaScript
themeCookie.setSecure(true);               // HTTPS only
response.addCookie(themeCookie);

// Read cookies from request
Cookie[] cookies = request.getCookies();   // null if none
if (cookies != null) {
    for (Cookie c : cookies) {
        if ("theme".equals(c.getName())) {
            String theme = c.getValue();
        }
    }
}

// Delete a cookie (set max age to 0 with same name and path)
Cookie deleteMe = new Cookie("theme", "");
deleteMe.setMaxAge(0);
deleteMe.setPath("/");
response.addCookie(deleteMe);
```

### Cookie vs. Session vs. Hidden Field

| Mechanism | Storage | Lifetime | Use For |
|-----------|---------|---------|---------|
| `HttpSession` attribute | Server memory | Until timeout or invalidated | Shopping cart, logged-in user, workflow state |
| Cookie | Client browser | Per `maxAge` setting | Preferences, remember-me tokens, analytics |
| Hidden form field | Form HTML | Single form submit | Multi-page wizard step data |
| URL parameter | URL | Single request | Pagination, sort order, filter values |

---

## Chapter 8: Authentication and Authorization

### Container-Managed Security (web.xml)
The simplest approach — the container handles the login form and checks credentials.

**web.xml:**
```xml
<!-- Protect the /admin/* URLs -->
<security-constraint>
  <web-resource-collection>
    <web-resource-name>Admin Area</web-resource-name>
    <url-pattern>/admin/*</url-pattern>
    <http-method>GET</http-method>
    <http-method>POST</http-method>
  </web-resource-collection>
  <auth-constraint>
    <role-name>admin</role-name>
  </auth-constraint>
  <user-data-constraint>
    <transport-guarantee>CONFIDENTIAL</transport-guarantee>  <!-- HTTPS required -->
  </user-data-constraint>
</security-constraint>

<!-- Also protect regular users area -->
<security-constraint>
  <web-resource-collection>
    <web-resource-name>User Area</web-resource-name>
    <url-pattern>/account/*</url-pattern>
  </web-resource-collection>
  <auth-constraint>
    <role-name>user</role-name>
    <role-name>admin</role-name>
  </auth-constraint>
</security-constraint>

<!-- FORM-based login -->
<login-config>
  <auth-method>FORM</auth-method>
  <realm-name>My App</realm-name>
  <form-login-config>
    <form-login-page>/login.jsp</form-login-page>
    <form-error-page>/login_error.jsp</form-error-page>
  </form-login-config>
</login-config>

<!-- Declare roles -->
<security-role><role-name>admin</role-name></security-role>
<security-role><role-name>user</role-name></security-role>
```

**login.jsp (required form field names):**
```html
<form method="POST" action="j_security_check">
  <input type="text"     name="j_username" placeholder="Username"/>
  <input type="password" name="j_password" placeholder="Password"/>
  <button type="submit">Login</button>
</form>
```

**Tomcat users (conf/tomcat-users.xml — development only):**
```xml
<tomcat-users>
  <role rolename="admin"/>
  <role rolename="user"/>
  <user username="admin" password="secret" roles="admin,user"/>
  <user username="bob"   password="pass"   roles="user"/>
</tomcat-users>
```

**Programmatic role check in servlet:**
```java
if (request.isUserInRole("admin")) {
    // show admin controls
}
String username = request.getUserPrincipal().getName();
```

---

### Custom (Programmatic) Authentication

More flexible than container-managed — handles any credential store.

**Login Servlet:**
```java
@WebServlet("/login")
public class LoginServlet extends HttpServlet {

    private UserService userService;

    @Override
    public void init() {
        userService = new UserService();
    }

    @Override
    protected void doGet(HttpServletRequest req,
                         HttpServletResponse resp)
            throws ServletException, IOException {
        // If already logged in, send to home
        if (req.getSession(false) != null &&
                req.getSession().getAttribute("user") != null) {
            resp.sendRedirect(req.getContextPath() + "/");
            return;
        }
        req.getRequestDispatcher("/WEB-INF/views/login.jsp").forward(req, resp);
    }

    @Override
    protected void doPost(HttpServletRequest req,
                          HttpServletResponse resp)
            throws ServletException, IOException {

        String username = req.getParameter("username");
        String password = req.getParameter("password");

        User user = userService.authenticate(username, password);

        if (user != null) {
            // Invalidate old session, create new one (prevents session fixation)
            req.getSession(false);
            if (req.getSession(false) != null) {
                req.getSession().invalidate();
            }
            HttpSession session = req.getSession(true);
            session.setAttribute("user", user);

            // Redirect to originally requested URL or default
            String redirectUrl = (String) session.getAttribute("redirectAfterLogin");
            session.removeAttribute("redirectAfterLogin");
            if (redirectUrl == null) {
                redirectUrl = req.getContextPath() + "/";
            }
            resp.sendRedirect(redirectUrl);
        } else {
            req.setAttribute("errorMsg", "Invalid username or password");
            req.getRequestDispatcher("/WEB-INF/views/login.jsp").forward(req, resp);
        }
    }
}
```

**Logout Servlet:**
```java
@WebServlet("/logout")
public class LogoutServlet extends HttpServlet {

    @Override
    protected void doPost(HttpServletRequest req,
                          HttpServletResponse resp)
            throws ServletException, IOException {
        HttpSession session = req.getSession(false);
        if (session != null) {
            session.invalidate();
        }
        resp.sendRedirect(req.getContextPath() + "/login");
    }
}
```

**Authentication Filter (guards protected URLs):**
```java
@WebFilter("/account/*")
public class AuthFilter implements Filter {

    @Override
    public void doFilter(ServletRequest request, ServletResponse response,
                         FilterChain chain) throws IOException, ServletException {

        HttpServletRequest  req  = (HttpServletRequest)  request;
        HttpServletResponse resp = (HttpServletResponse) response;

        HttpSession session = req.getSession(false);
        User user = (session != null) ? (User) session.getAttribute("user") : null;

        if (user != null) {
            chain.doFilter(request, response);   // authenticated — continue
        } else {
            // Save requested URL for post-login redirect
            req.getSession(true).setAttribute("redirectAfterLogin",
                req.getRequestURI());
            resp.sendRedirect(req.getContextPath() + "/login");
        }
    }

    @Override public void init(FilterConfig cfg) {}
    @Override public void destroy() {}
}
```

**Authorization Filter (role check):**
```java
@WebFilter("/admin/*")
public class AdminFilter implements Filter {

    @Override
    public void doFilter(ServletRequest request, ServletResponse response,
                         FilterChain chain) throws IOException, ServletException {

        HttpServletRequest  req  = (HttpServletRequest)  request;
        HttpServletResponse resp = (HttpServletResponse) response;

        HttpSession session = req.getSession(false);
        User user = (session != null) ? (User) session.getAttribute("user") : null;

        if (user != null && "ADMIN".equals(user.getRole())) {
            chain.doFilter(request, response);
        } else if (user == null) {
            resp.sendRedirect(req.getContextPath() + "/login");
        } else {
            resp.sendError(HttpServletResponse.SC_FORBIDDEN, "Access denied");
        }
    }

    @Override public void init(FilterConfig cfg) {}
    @Override public void destroy() {}
}
```

### UserService — Authenticating Against a Database
```java
public class UserService {

    private UserDAO userDAO;

    public UserService() {
        this.userDAO = new UserDAO();
    }

    public User authenticate(String username, String password) {
        if (username == null || password == null) return null;

        User user = userDAO.findByUsername(username);
        if (user == null) return null;

        // NEVER store plaintext passwords; use BCrypt or similar
        if (BCrypt.checkpw(password, user.getPasswordHash())) {
            return user;
        }
        return null;
    }
}
```

### Password Hashing (BCrypt)
```xml
<!-- pom.xml -->
<dependency>
  <groupId>org.mindrot</groupId>
  <artifactId>jbcrypt</artifactId>
  <version>0.4</version>
</dependency>
```
```java
// Hash at registration
String hash = BCrypt.hashpw(plaintextPassword, BCrypt.gensalt(12));

// Verify at login
boolean matches = BCrypt.checkpw(plaintextPassword, storedHash);
```

---

### Preventing Common Security Issues

| Vulnerability | Attack | Defense |
|--------------|--------|---------|
| **Session Fixation** | Attacker pre-sets session ID | Invalidate old session and create new one on login |
| **XSS** | Inject `<script>` via form input | Use `fn:escapeXml()` / `<c:out>` in JSP; never print raw user input |
| **CSRF** | Forged POST from another site | Add CSRF token to forms; validate in servlet |
| **SQL Injection** | Malicious SQL in form fields | Always use `PreparedStatement`; never string-concat SQL |
| **Clickjacking** | Iframe embedding your page | `response.setHeader("X-Frame-Options", "DENY")` |
| **Insecure cookies** | Cookie theft via JS or HTTP | Set `HttpOnly=true`, `Secure=true`, `SameSite=Strict` |

### CSRF Token Pattern
```java
// In servlet or filter — generate token on form display
String token = UUID.randomUUID().toString();
session.setAttribute("csrfToken", token);
request.setAttribute("csrfToken", token);
```
```html
<!-- In login/form JSP -->
<input type="hidden" name="csrfToken" value="${csrfToken}"/>
```
```java
// On POST — validate token
String submitted = request.getParameter("csrfToken");
String expected  = (String) session.getAttribute("csrfToken");
if (!expected.equals(submitted)) {
    response.sendError(403, "CSRF token mismatch");
    return;
}
session.removeAttribute("csrfToken");   // use once
```

---

## Common Session and Security Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| Session lost between requests | Session invalidated or cookies blocked | Check `getSession(false)` returns non-null; check cookie settings |
| Login loop | Redirect to login from within `/login` | Exclude login URL from auth filter pattern |
| Session data shared between users | Stored in `ServletContext` instead of `HttpSession` | Use `request.getSession().setAttribute()` |
| Concurrent session modification | Multiple threads, single session | Use `synchronized (session) {}` blocks or avoid mutable session objects |
| Cookie not set in browser | `Secure` flag + HTTP (no HTTPS) | Remove `Secure` in dev; use HTTPS in production |
| 403 after correct login | Role name mismatch between `web.xml` and user store | Check role names are identical (case-sensitive) |
