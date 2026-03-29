# Ch 11 — Working with REST APIs

## REST API Design Principles

| Concept | Description |
|---------|-------------|
| **Stateless** | Each request carries all necessary info |
| **Resource-based** | URIs identify resources, not actions |
| **HTTP verbs** | GET=read, POST=create, PUT=replace, PATCH=update, DELETE=remove |
| **Uniform interface** | Consistent structure across endpoints |
| **Representations** | JSON, XML, etc. (JSON is standard) |

### URI conventions
```
GET    /api/v1/users          — list users
POST   /api/v1/users          — create user
GET    /api/v1/users/{id}     — get user
PUT    /api/v1/users/{id}     — replace user
PATCH  /api/v1/users/{id}     — partial update
DELETE /api/v1/users/{id}     — delete user
GET    /api/v1/users/{id}/posts — nested resource
```

## REST Server with net/http (stdlib)

```go
type UserHandler struct {
    db *sql.DB
}

func (h *UserHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    switch r.Method {
    case http.MethodGet:
        h.list(w, r)
    case http.MethodPost:
        h.create(w, r)
    default:
        http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
    }
}

func (h *UserHandler) list(w http.ResponseWriter, r *http.Request) {
    users, err := fetchUsers(h.db)
    if err != nil {
        respondError(w, http.StatusInternalServerError, err)
        return
    }
    respondJSON(w, http.StatusOK, users)
}
```

### Response helpers
```go
func respondJSON(w http.ResponseWriter, status int, data any) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(data)
}

func respondError(w http.ResponseWriter, status int, err error) {
    respondJSON(w, status, map[string]string{"error": err.Error()})
}
```

## REST Server with Go 1.22+ patterns

```go
mux := http.NewServeMux()

// Method + pattern routing (Go 1.22+)
mux.HandleFunc("GET /api/users", h.listUsers)
mux.HandleFunc("POST /api/users", h.createUser)
mux.HandleFunc("GET /api/users/{id}", h.getUser)
mux.HandleFunc("PUT /api/users/{id}", h.updateUser)
mux.HandleFunc("DELETE /api/users/{id}", h.deleteUser)

func (h *Handler) getUser(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id")
    user, err := h.db.FindUser(id)
    if errors.Is(err, ErrNotFound) {
        respondError(w, http.StatusNotFound, err)
        return
    }
    respondJSON(w, http.StatusOK, user)
}
```

## Pagination

```go
// Query: GET /api/users?page=2&per_page=20

func listUsers(w http.ResponseWriter, r *http.Request) {
    page, _ := strconv.Atoi(r.URL.Query().Get("page"))
    if page < 1 { page = 1 }
    perPage, _ := strconv.Atoi(r.URL.Query().Get("per_page"))
    if perPage < 1 || perPage > 100 { perPage = 20 }

    offset := (page - 1) * perPage
    users, total, err := fetchUsersPage(offset, perPage)

    type response struct {
        Data       []User `json:"data"`
        Page       int    `json:"page"`
        PerPage    int    `json:"per_page"`
        Total      int    `json:"total"`
        TotalPages int    `json:"total_pages"`
    }
    respondJSON(w, http.StatusOK, response{
        Data:       users,
        Page:       page,
        PerPage:    perPage,
        Total:      total,
        TotalPages: (total + perPage - 1) / perPage,
    })
}
```

## Request Validation

```go
type CreateUserRequest struct {
    Name  string `json:"name"`
    Email string `json:"email"`
    Age   int    `json:"age"`
}

func (req CreateUserRequest) Validate() error {
    if req.Name == "" {
        return errors.New("name is required")
    }
    if !strings.Contains(req.Email, "@") {
        return errors.New("invalid email")
    }
    if req.Age < 0 || req.Age > 150 {
        return errors.New("invalid age")
    }
    return nil
}

func createUser(w http.ResponseWriter, r *http.Request) {
    var req CreateUserRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        respondError(w, http.StatusBadRequest, fmt.Errorf("invalid JSON: %w", err))
        return
    }
    if err := req.Validate(); err != nil {
        respondError(w, http.StatusUnprocessableEntity, err)
        return
    }
    // ... create user
}
```

## REST Client

```go
type Client struct {
    base    string
    client  *http.Client
    token   string
}

func NewClient(base, token string) *Client {
    return &Client{
        base:  base,
        token: token,
        client: &http.Client{Timeout: 30 * time.Second},
    }
}

func (c *Client) GetUser(ctx context.Context, id string) (*User, error) {
    req, err := http.NewRequestWithContext(ctx, "GET",
        c.base+"/api/users/"+id, nil)
    if err != nil { return nil, err }

    req.Header.Set("Authorization", "Bearer "+c.token)
    req.Header.Set("Accept", "application/json")

    resp, err := c.client.Do(req)
    if err != nil { return nil, err }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        body, _ := io.ReadAll(resp.Body)
        return nil, fmt.Errorf("API error %d: %s", resp.StatusCode, body)
    }

    var user User
    return &user, json.NewDecoder(resp.Body).Decode(&user)
}

func (c *Client) CreateUser(ctx context.Context, req CreateUserRequest) (*User, error) {
    data, err := json.Marshal(req)
    if err != nil { return nil, err }

    httpReq, err := http.NewRequestWithContext(ctx, "POST",
        c.base+"/api/users", bytes.NewReader(data))
    if err != nil { return nil, err }
    httpReq.Header.Set("Content-Type", "application/json")
    httpReq.Header.Set("Authorization", "Bearer "+c.token)

    resp, err := c.client.Do(httpReq)
    if err != nil { return nil, err }
    defer resp.Body.Close()

    var user User
    return &user, json.NewDecoder(resp.Body).Decode(&user)
}
```

## File Upload / Download

```go
// Upload binary file
func uploadFile(w http.ResponseWriter, r *http.Request) {
    r.ParseMultipartForm(32 << 20)  // 32MB max in memory

    file, header, err := r.FormFile("file")
    if err != nil { respondError(w, 400, err); return }
    defer file.Close()

    fmt.Printf("uploaded: %s (%d bytes)\n", header.Filename, header.Size)

    dst, err := os.Create("uploads/" + header.Filename)
    if err != nil { respondError(w, 500, err); return }
    defer dst.Close()
    io.Copy(dst, file)

    respondJSON(w, 201, map[string]string{"filename": header.Filename})
}

// Download binary file
func downloadFile(w http.ResponseWriter, r *http.Request) {
    filename := r.PathValue("filename")
    path := filepath.Join("uploads", filepath.Clean(filename))

    w.Header().Set("Content-Disposition", "attachment; filename="+filename)
    w.Header().Set("Content-Type", "application/octet-stream")
    http.ServeFile(w, r, path)
}
```

## Authentication Patterns

### API Key
```go
func apiKeyMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        key := r.Header.Get("X-API-Key")
        if !validKey(key) {
            respondError(w, http.StatusUnauthorized, errors.New("invalid API key"))
            return
        }
        next.ServeHTTP(w, r)
    })
}
```

### JWT (golang-jwt/jwt)
```go
import "github.com/golang-jwt/jwt/v5"

secret := []byte("my-secret")

// Create token
claims := jwt.MapClaims{
    "sub": userID,
    "exp": time.Now().Add(24 * time.Hour).Unix(),
}
token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
signed, err := token.SignedString(secret)

// Verify token
token, err := jwt.Parse(signed, func(t *jwt.Token) (interface{}, error) {
    if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
        return nil, fmt.Errorf("unexpected method: %v", t.Header["alg"])
    }
    return secret, nil
})
if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
    userID := claims["sub"].(string)
}
```

## CORS Middleware

```go
func cors(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Access-Control-Allow-Origin", "*")
        w.Header().Set("Access-Control-Allow-Methods", "GET,POST,PUT,PATCH,DELETE,OPTIONS")
        w.Header().Set("Access-Control-Allow-Headers", "Content-Type,Authorization")

        if r.Method == http.MethodOptions {
            w.WriteHeader(http.StatusNoContent)
            return
        }
        next.ServeHTTP(w, r)
    })
}
```

## OpenAPI / Swagger

Use `swaggo/swag` to generate OpenAPI specs from code annotations:

```go
// @Summary Get user by ID
// @Description Returns a single user
// @Tags users
// @Param id path string true "User ID"
// @Success 200 {object} User
// @Failure 404 {object} ErrorResponse
// @Router /api/users/{id} [get]
func (h *Handler) getUser(w http.ResponseWriter, r *http.Request) { ... }
```

```bash
swag init              # generates docs/swagger.json
```
