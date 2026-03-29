# Ch 9 — Building Web Services

## HTTP Server (net/http)

```go
import "net/http"

func helloHandler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusOK)
    fmt.Fprintln(w, `{"message":"hello"}`)
}

func main() {
    http.HandleFunc("/", helloHandler)
    http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
    })

    srv := &http.Server{
        Addr:         ":8080",
        ReadTimeout:  10 * time.Second,
        WriteTimeout: 10 * time.Second,
        IdleTimeout:  30 * time.Second,
    }
    log.Fatal(srv.ListenAndServe())
}
```

## ServeMux — Request Routing

```go
mux := http.NewServeMux()

// Exact match
mux.HandleFunc("/api/users", usersHandler)

// Subtree match (trailing slash)
mux.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir("./static"))))

// Go 1.22+ enhanced patterns
mux.HandleFunc("GET /api/users", listUsers)
mux.HandleFunc("POST /api/users", createUser)
mux.HandleFunc("GET /api/users/{id}", getUser)  // path params

// Extract path parameter (Go 1.22+)
func getUser(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id")
    fmt.Fprintf(w, "user: %s", id)
}

srv := &http.Server{Addr: ":8080", Handler: mux}
```

## Request Handling

```go
func handler(w http.ResponseWriter, r *http.Request) {
    // Method
    fmt.Println(r.Method)              // "GET", "POST", etc.

    // URL / Path
    fmt.Println(r.URL.Path)           // "/api/users"
    fmt.Println(r.URL.Query())        // url.Values map

    // Query parameters
    name := r.URL.Query().Get("name")
    page := r.URL.Query().Get("page")

    // Headers
    ct := r.Header.Get("Content-Type")
    auth := r.Header.Get("Authorization")

    // Body
    body, err := io.ReadAll(r.Body)
    defer r.Body.Close()

    // JSON request body
    var payload struct {
        Name string `json:"name"`
        Age  int    `json:"age"`
    }
    if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

    // Form data
    r.ParseForm()
    val := r.FormValue("field")

    // Cookies
    cookie, err := r.Cookie("session")
}
```

## Response Writing

```go
func respond(w http.ResponseWriter, data any, status int) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(data)
}

// Convenience functions
http.Error(w, "not found", http.StatusNotFound)
http.Redirect(w, r, "/new-path", http.StatusMovedPermanently)
http.ServeFile(w, r, "./static/index.html")
http.ServeContent(w, r, "file.txt", modTime, content)

// Status code constants
http.StatusOK           // 200
http.StatusCreated      // 201
http.StatusNoContent    // 204
http.StatusBadRequest   // 400
http.StatusUnauthorized // 401
http.StatusForbidden    // 403
http.StatusNotFound     // 404
http.StatusInternalServerError // 500
```

## Middleware Pattern

```go
type Middleware func(http.Handler) http.Handler

func logging(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
    })
}

func auth(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        token := r.Header.Get("Authorization")
        if !validate(token) {
            http.Error(w, "Unauthorized", http.StatusUnauthorized)
            return
        }
        next.ServeHTTP(w, r)
    })
}

// Chain middleware
handler := logging(auth(mux))
srv := &http.Server{Addr: ":8080", Handler: handler}
```

## Graceful Shutdown

```go
srv := &http.Server{Addr: ":8080", Handler: mux}

// Start server in goroutine
go func() {
    if err := srv.ListenAndServe(); err != http.ErrServerClosed {
        log.Fatalf("server error: %v", err)
    }
}()

// Wait for signal
sigs := make(chan os.Signal, 1)
signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)
<-sigs

ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
defer cancel()
if err := srv.Shutdown(ctx); err != nil {
    log.Printf("shutdown error: %v", err)
}
log.Println("server stopped")
```

## HTTP Client

```go
client := &http.Client{
    Timeout: 30 * time.Second,
    Transport: &http.Transport{
        MaxIdleConns:        100,
        MaxIdleConnsPerHost: 10,
        IdleConnTimeout:     90 * time.Second,
    },
}

// GET
resp, err := client.Get("https://api.example.com/data")
if err != nil { return err }
defer resp.Body.Close()
body, _ := io.ReadAll(resp.Body)

// POST JSON
payload := map[string]string{"name": "Alice"}
data, _ := json.Marshal(payload)
resp, err = client.Post("https://api.example.com/users",
    "application/json", bytes.NewReader(data))

// Custom request with context
req, err := http.NewRequestWithContext(ctx, "DELETE",
    "https://api.example.com/users/1", nil)
req.Header.Set("Authorization", "Bearer "+token)
resp, err = client.Do(req)

// Check response status
if resp.StatusCode != http.StatusOK {
    return fmt.Errorf("unexpected status: %d", resp.StatusCode)
}
```

## TLS / HTTPS

```go
// HTTPS server
srv.ListenAndServeTLS("cert.pem", "key.pem")

// Auto-generate self-signed cert for dev
// go run $(go env GOROOT)/src/crypto/tls/generate_cert.go --host localhost

// Client with custom TLS
tlsConfig := &tls.Config{
    MinVersion: tls.VersionTLS12,
}
transport := &http.Transport{TLSClientConfig: tlsConfig}
client := &http.Client{Transport: transport}

// Skip TLS verification (DEVELOPMENT ONLY — never in production)
tlsConfig.InsecureSkipVerify = true
```

## Prometheus Metrics

```go
import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

var requestCount = prometheus.NewCounterVec(
    prometheus.CounterOpts{
        Name: "http_requests_total",
        Help: "Total HTTP requests",
    },
    []string{"method", "path", "status"},
)

func init() {
    prometheus.MustRegister(requestCount)
}

func metricsMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        rw := &responseWriter{ResponseWriter: w, status: 200}
        next.ServeHTTP(rw, r)
        requestCount.WithLabelValues(r.Method, r.URL.Path,
            strconv.Itoa(rw.status)).Inc()
    })
}

// Expose metrics endpoint
mux.Handle("/metrics", promhttp.Handler())
```

## HTML Templates

```go
import "html/template"

tmpl := template.Must(template.ParseFiles("templates/index.html"))

func handler(w http.ResponseWriter, r *http.Request) {
    data := struct {
        Title string
        Items []string
    }{
        Title: "My Page",
        Items: []string{"one", "two", "three"},
    }
    tmpl.Execute(w, data)
}
```

```html
<!-- templates/index.html -->
<h1>{{.Title}}</h1>
<ul>
{{range .Items}}<li>{{.}}</li>{{end}}
</ul>
```
