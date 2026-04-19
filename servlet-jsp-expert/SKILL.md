---
name: servlet-jsp-expert
description: Java Servlet and JSP expertise covering the full web development stack — servlet lifecycle, HTTP request/response API, JSP syntax and EL, JSTL, MVC pattern, session/cookie management, JDBC database access, security and authentication, filters and listeners, Ajax integration, file uploads, and email. Use when building traditional Java web applications, configuring Tomcat/web.xml, implementing MVC architecture, handling form processing, managing user sessions, querying databases from servlets, or debugging servlet/JSP issues. Based on "Murach's Java Servlets and JSP" by Joel Murach.
---

# Java Servlet and JSP Expert

Based on *Murach's Java Servlets and JSP* by Joel Murach.

**Target platform:** Java EE 7 / Jakarta EE 8 compatible; Servlet 4.0, JSP 2.3, JSTL 1.2, deployed on Tomcat 9+ or any Java EE server.

## Application Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                    BROWSER (HTTP Client)                        │
└─────────────────────────┬──────────────────────────────────────┘
                          │ HTTP Request
                          ▼
┌────────────────────────────────────────────────────────────────┐
│                      WEB CONTAINER (Tomcat)                    │
│                                                                │
│  ┌──────────────┐    ┌───────────────┐    ┌────────────────┐  │
│  │   Filter     │───▶│   Servlet     │───▶│   JSP View     │  │
│  │  Chain       │    │  (Controller) │    │  (Presentation)│  │
│  └──────────────┘    └───────┬───────┘    └────────────────┘  │
│                              │                                  │
│                    ┌─────────▼─────────┐                       │
│                    │  Business Layer   │                       │
│                    │  (Service/DAO)    │                       │
│                    └─────────┬─────────┘                       │
│                              │                                  │
│                    ┌─────────▼─────────┐                       │
│                    │  Data Layer       │                       │
│                    │  JDBC / JPA       │                       │
│                    └───────────────────┘                       │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  Shared State: HttpSession · ServletContext · Cookies  │   │
│  └────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘
```

## Quick Reference

| Task | Reference |
|------|-----------|
| Dev environment setup, Tomcat install, servlet basics, HTTP request/response API, servlet lifecycle | [setup-and-servlets.md](references/setup-and-servlets.md) |
| JSP syntax, scriptlets, directives, EL, JSTL tags, custom tags, JavaBeans | [jsp-and-el.md](references/jsp-and-el.md) |
| RequestDispatcher, redirect vs. forward, MVC pattern, layered architecture | [mvc-patterns.md](references/mvc-patterns.md) |
| HttpSession, cookies, URL rewriting, form-based auth, security constraints | [state-and-security.md](references/state-and-security.md) |
| JDBC, connection pooling, prepared statements, DAO pattern, transactions | [database.md](references/database.md) |
| Filters, event listeners, Ajax with servlets, file uploads, JavaMail | [advanced.md](references/advanced.md) |

## Reference Files

| File | Chapters | Topics |
|------|----------|--------|
| `setup-and-servlets.md` | 1–2 | Tomcat install, Eclipse/IDE setup, web.xml, servlet lifecycle, HttpServletRequest/Response API, annotations |
| `jsp-and-el.md` | 3, 9–11 | JSP directives/scriptlets, Expression Language, JSTL core/fmt/fn tags, custom tag libraries, JavaBeans |
| `mvc-patterns.md` | 4–5 | RequestDispatcher, forward vs. redirect, MVC design pattern, layered architecture, application attributes |
| `state-and-security.md` | 7–8 | HttpSession API, session tracking, cookies, URL rewriting, authentication, authorization, SSL basics |
| `database.md` | 6 | JDBC driver setup, Connection/Statement/ResultSet, PreparedStatement, connection pool (JNDI), DAO pattern |
| `advanced.md` | 12–14 | Filter chain, Filter interface, ServletContextListener, Ajax/JSON responses, file uploads (multipart), JavaMail |

## Core Decision Trees

### How Should I Transfer Control?

```
Need to move to another page?
├── Should the URL change in the browser?
│   └── Yes → response.sendRedirect("/path")
│       ├── After POST (PRG pattern) → always redirect
│       └── External URL → redirect
└── Keep same request/attributes for the next page?
    └── Yes → RequestDispatcher.forward(req, resp)
        ├── JSP needs request attributes → forward
        └── Same request scope → forward
```

### Session vs. Cookies vs. Application Scope

```
Where should I store this data?
├── Per-user, temporary (logged-in session) → HttpSession
│   └── request.getSession() → setAttribute/getAttribute
├── Needs to survive browser close / sent automatically → Cookie
│   └── new Cookie(name, value); response.addCookie(c)
├── Shared across ALL users, whole app → ServletContext
│   └── getServletContext().setAttribute(...)
└── Single request only → request.setAttribute(...)
```

### Which JSTL Tag Library Do I Need?

```
What do I need to do in JSP?
├── if/choose/forEach/set/out → <%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
├── Format dates/numbers/i18n  → <%@ taglib uri="http://java.sun.com/jsp/jstl/fmt"  prefix="fmt" %>
├── String functions (length, split, etc.) → <%@ taglib uri="http://java.sun.com/jsp/jstl/functions" prefix="fn" %>
└── SQL (avoid in production)  → <%@ taglib uri="http://java.sun.com/jsp/jstl/sql"  prefix="sql" %>
```

### Which Authentication Approach?

```
How do I secure my web app?
├── Simple, container-managed → web.xml security-constraint + login-config
│   ├── FORM auth → custom login/error JSP
│   ├── BASIC auth → browser dialog
│   └── Define roles in tomcat-users.xml
└── Custom authentication (programmatic)
    ├── POST login form → servlet validates credentials
    ├── Store User in HttpSession
    └── Filter checks session on every protected request
```

## Key Concepts

### Servlet Lifecycle
```
1. classloading & instantiation (once, by container)
2. init(ServletConfig)        — once; load resources
3. service(req, resp)         — per request (multithreaded)
   ├── doGet(req, resp)
   ├── doPost(req, resp)
   └── doPut / doDelete / ...
4. destroy()                  — once; release resources
```
Servlets are **singletons** — instance variables are shared across threads. Use only local variables or thread-safe structures for per-request state.

### The PRG Pattern (Post-Redirect-Get)
Always redirect after a successful POST to prevent duplicate form submission on browser refresh.
```
Browser POST /cart/add  →  Servlet processes  →  redirect GET /cart
```

### MVC Responsibilities
| Layer | Class Type | Responsibility |
|-------|-----------|----------------|
| Controller | `HttpServlet` | Receive request, call service, forward to view |
| Model | POJO / JavaBean | Data + business logic |
| View | JSP | Display data from request attributes |
| Service | Plain Java class | Business rules, orchestration |
| DAO | Plain Java class | Database access only |
