# Beginner Quickstart
*Chapters 1–3 (Zambon) — Environment Setup, First Web Application, Servlets and JSP in Jakarta EE*

## Chapter 1: Setting Up the Environment

### GlassFish 7 (Jakarta EE 10 Reference Implementation)

GlassFish is the reference implementation — easiest for learning because defaults work out of the box.

**Download:** [glassfish.org](https://glassfish.org) — "GlassFish 7.x Web Profile" or "Full Platform"

```
glassfish7/
├── bin/
│   ├── asadmin          # admin CLI (Unix)
│   └── asadmin.bat      # admin CLI (Windows)
├── glassfish/
│   ├── domains/domain1/ # default domain
│   │   ├── config/      # domain.xml, server config
│   │   └── autodeploy/  # drop WARs here to deploy
│   └── lib/             # server libraries
└── mq/                  # bundled JMS broker
```

**Start/stop:**
```bash
./bin/asadmin start-domain domain1
./bin/asadmin stop-domain domain1
# Admin console: http://localhost:4848  (default: no password)
# App base URL:  http://localhost:8080
```

**Deploy via autodeploy:**
```bash
cp myapp.war glassfish7/glassfish/domains/domain1/autodeploy/
# Watch server log for "myapp was successfully deployed"
```

**Deploy via asadmin:**
```bash
./bin/asadmin deploy --contextroot /myapp target/myapp.war
./bin/asadmin undeploy myapp
./bin/asadmin list-applications
```

---

### NetBeans 20+ IDE Setup

NetBeans has native Jakarta EE/GlassFish support — best beginner IDE for this stack.

1. **Download** NetBeans from netbeans.apache.org
2. **Add GlassFish server:** Services tab → Servers → Add Server → GlassFish → point to `glassfish7/`
3. **Create Jakarta EE project:** File → New Project → Jakarta EE → Web Application
   - Server: GlassFish 7
   - Java EE Version: Jakarta EE 10
   - Context Path: `/myapp`

**IntelliJ IDEA alternative:**
- Community edition does not support Jakarta EE servers directly
- Ultimate edition: Run → Edit Configurations → GlassFish Server → Local

---

### Maven Project Structure

```
myapp/
├── pom.xml
└── src/main/
    ├── java/com/example/
    │   └── HelloServlet.java
    ├── resources/
    └── webapp/
        ├── WEB-INF/
        │   ├── web.xml          # optional in Servlet 5.0+
        │   └── beans.xml        # enables CDI
        ├── index.xhtml          # Faces welcome page
        └── hello.jsp            # JSP page
```

**`pom.xml` — Jakarta EE 10 WAR:**
```xml
<project>
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.example</groupId>
  <artifactId>myapp</artifactId>
  <version>1.0-SNAPSHOT</version>
  <packaging>war</packaging>

  <properties>
    <maven.compiler.source>17</maven.compiler.source>
    <maven.compiler.target>17</maven.compiler.target>
    <failOnMissingWebXml>false</failOnMissingWebXml>
  </properties>

  <dependencies>
    <!-- Jakarta EE 10 Web Profile (GlassFish/WildFly provides this) -->
    <dependency>
      <groupId>jakarta.platform</groupId>
      <artifactId>jakarta.jakartaee-web-api</artifactId>
      <version>10.0.0</version>
      <scope>provided</scope>  <!-- server supplies it at runtime -->
    </dependency>
  </dependencies>

  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-war-plugin</artifactId>
        <version>3.3.2</version>
      </plugin>
    </plugins>
  </build>
</project>
```

**`WEB-INF/beans.xml` — enables CDI:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="https://jakarta.ee/xml/ns/jakartaee"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="https://jakarta.ee/xml/ns/jakartaee
         https://jakarta.ee/xml/ns/jakartaee/beans_4_0.xsd"
       version="4.0"
       bean-discovery-mode="annotated">
</beans>
```

---

## Chapter 2: A Simple Web Application

### First Servlet

```java
package com.example;

import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.*;
import jakarta.servlet.*;
import java.io.*;

@WebServlet("/hello")           // maps to http://localhost:8080/myapp/hello
public class HelloServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {

        String name = req.getParameter("name");   // ?name=World
        if (name == null || name.isBlank()) name = "World";

        resp.setContentType("text/html;charset=UTF-8");
        PrintWriter out = resp.getWriter();
        out.println("<!DOCTYPE html><html><body>");
        out.println("<h1>Hello, " + escapeHtml(name) + "!</h1>");
        out.println("</body></html>");
    }

    // Prevent XSS — always escape user-supplied output
    private String escapeHtml(String s) {
        return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                .replace("\"","&quot;").replace("'","&#x27;");
    }
}
```

URL: `http://localhost:8080/myapp/hello?name=Alice`

### POST Form Handling

```java
@WebServlet("/greet")
public class GreetServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        // Show the form
        req.getRequestDispatcher("/WEB-INF/views/greet-form.jsp")
           .forward(req, resp);
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        req.setCharacterEncoding("UTF-8");
        String name = req.getParameter("name");

        // Validate
        if (name == null || name.isBlank()) {
            req.setAttribute("error", "Name is required");
            req.getRequestDispatcher("/WEB-INF/views/greet-form.jsp")
               .forward(req, resp);
            return;
        }

        // Process and redirect (PRG pattern)
        req.getSession().setAttribute("greeting", "Hello, " + name + "!");
        resp.sendRedirect(req.getContextPath() + "/greet/result");
    }
}
```

**PRG Pattern (Post-Redirect-Get):** Always redirect after a successful POST to prevent duplicate form submission on browser refresh.

---

## Chapter 3: JSP and Servlets

### JSP Basics

JSP pages live in `src/main/webapp/` (or `WEB-INF/views/` to protect from direct access).

**`/WEB-INF/views/greet-form.jsp`:**
```jsp
<%@ page contentType="text/html;charset=UTF-8" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<!DOCTYPE html>
<html>
<head><title>Greet</title></head>
<body>
  <c:if test="${not empty error}">
    <p style="color:red">${error}</p>
  </c:if>
  <form method="post" action="${pageContext.request.contextPath}/greet">
    <label>Name: <input type="text" name="name" value="${param.name}"/></label>
    <button type="submit">Greet</button>
  </form>
</body>
</html>
```

### JSP + Servlet MVC Pattern

```
Browser → GET /greet     → GreetServlet.doGet() → forward to greet-form.jsp
Browser → POST /greet    → GreetServlet.doPost() → validate → redirect GET /greet/result
Browser → GET /greet/result → ResultServlet.doGet() → forward to result.jsp
```

**Keep JSP pages behind `WEB-INF/`** so the user cannot navigate to them directly — they must go through a servlet.

### JSTL Core Tag Reference

```jsp
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>

<!-- Output (auto-escapes HTML) -->
<c:out value="${user.name}" default="Anonymous"/>

<!-- Conditional -->
<c:if test="${user.admin}">Admin panel</c:if>

<c:choose>
  <c:when test="${score >= 90}">A</c:when>
  <c:when test="${score >= 80}">B</c:when>
  <c:otherwise>C</c:otherwise>
</c:choose>

<!-- Loop -->
<c:forEach var="item" items="${items}" varStatus="s">
  <tr class="${s.index % 2 == 0 ? 'even' : 'odd'}">
    <td>${s.count}</td>
    <td><c:out value="${item.name}"/></td>
  </tr>
</c:forEach>

<!-- URL building -->
<c:url var="editUrl" value="/edit">
  <c:param name="id" value="${item.id}"/>
</c:url>
<a href="${editUrl}">Edit</a>

<!-- Set / remove attributes -->
<c:set var="tax" value="${price * 0.08}" scope="request"/>
<c:remove var="tempVar" scope="session"/>
```

### Servlet Lifecycle in Jakarta EE

```
1. Container starts → finds @WebServlet classes
2. First request  → instantiates servlet (singleton)
3. init()         → called once; load resources
4. service()      → called per request on any thread (multithreaded!)
   └── dispatches to doGet() / doPost() / etc.
5. destroy()      → called once on undeploy; release resources
```

**Thread safety:** Servlet instances are shared across threads. Never store request-specific state in instance variables.

```java
@WebServlet("/safe")
public class SafeServlet extends HttpServlet {
    // OK — read-only config loaded in init
    private String appName;

    @Override
    public void init() {
        appName = getServletContext().getInitParameter("app.name");
    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        // OK — local variable per request
        String user = req.getParameter("user");
        resp.getWriter().println(appName + ": " + user);
    }
}
```

### Servlet Context Parameters (`web.xml`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee" version="6.0">
  <context-param>
    <param-name>app.name</param-name>
    <param-value>My Application</param-value>
  </context-param>
  <welcome-file-list>
    <welcome-file>index.xhtml</welcome-file>
    <welcome-file>index.html</welcome-file>
  </welcome-file-list>
</web-app>
```

---

## Common Beginner Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| 404 on servlet | Context path mismatch | URL must include app context: `/myapp/hello` |
| 404 on servlet | `@WebServlet` not found | Ensure class is in `src/main/java`, WAR rebuilt |
| Blank output from JSP | JSP not in WEB-INF | Check `getRequestDispatcher("/WEB-INF/views/page.jsp")` |
| Parameter is null | Form field name mismatch | `name` attribute in `<input>` must match `getParameter("name")` |
| Special chars corrupted | Encoding not set | Call `req.setCharacterEncoding("UTF-8")` before `getParameter()` |
| CDI injection fails | `beans.xml` missing | Add `WEB-INF/beans.xml` (even empty) |
| GlassFish won't start | Port 8080 in use | `asadmin change-admin-port` or stop conflicting process |
| WAR not loading | Class compile error | Check server log: `glassfish/domains/domain1/logs/server.log` |
