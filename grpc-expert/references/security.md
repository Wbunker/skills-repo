# Secured gRPC

## Why TLS Matters for gRPC

gRPC runs on HTTP/2, which in practice requires TLS. While the spec allows cleartext (h2c), production deployments mandate encryption for data integrity, confidentiality, and server authentication. gRPC's security model separates **channel credentials** (securing the transport via TLS) from **call credentials** (authenticating individual RPCs via tokens). These compose together for layered security.

## Certificate Concepts

| Term | Description |
|------|-------------|
| **CA** | Trusted entity that signs certificates. Can be public or self-signed for internal services. |
| **Server certificate** | X.509 cert proving server identity. Contains the server's public key and SANs. |
| **Client certificate** | X.509 cert proving client identity in mTLS scenarios. |
| **Private key** | Secret key paired with a certificate. Never transmitted over the wire. |

## One-Way TLS (Server-Side TLS)

The client verifies the server's identity; the server does not verify the client. This mirrors standard HTTPS behavior.

### Generating Self-Signed Certificates

```bash
# Generate CA key and self-signed certificate
openssl req -x509 -newkey rsa:4096 -days 365 -nodes \
  -keyout ca-key.pem -out ca-cert.pem \
  -subj "/C=US/ST=CA/O=MyOrg/CN=MyCA"

# Generate server key and CSR
openssl req -newkey rsa:4096 -nodes \
  -keyout server-key.pem -out server-req.pem \
  -subj "/C=US/ST=CA/O=MyOrg/CN=localhost"

# Sign server cert with CA (SAN is critical — Go ignores CN)
openssl x509 -req -in server-req.pem -days 365 \
  -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial \
  -out server-cert.pem \
  -extfile <(printf "subjectAltName=DNS:localhost,IP:127.0.0.1")
```

### Server-Side Code

```go
creds, err := credentials.NewServerTLSFromFile("server-cert.pem", "server-key.pem")
if err != nil {
    log.Fatalf("failed to load TLS credentials: %v", err)
}

grpcServer := grpc.NewServer(grpc.Creds(creds))
pb.RegisterOrderServiceServer(grpcServer, &orderServer{})

lis, _ := net.Listen("tcp", ":50051")
grpcServer.Serve(lis)
```

### Client-Side Code

```go
// Second arg must match a SAN in the server certificate
creds, err := credentials.NewClientTLSFromFile("ca-cert.pem", "localhost")
if err != nil {
    log.Fatalf("failed to load CA cert: %v", err)
}

conn, err := grpc.Dial("localhost:50051", grpc.WithTransportCredentials(creds))
```

The server name passed to `NewClientTLSFromFile` must match a SAN entry in the server certificate, or the TLS handshake fails.

## Mutual TLS (mTLS)

Both server and client present certificates and verify each other. Use mTLS for:

- **Zero-trust networks** where no implicit trust exists between services
- **Service-to-service authentication** in microservice architectures
- **Regulatory requirements** mandating mutual authentication

### Additional Certificate Setup

```bash
# Generate client key and CSR
openssl req -newkey rsa:4096 -nodes \
  -keyout client-key.pem -out client-req.pem \
  -subj "/C=US/ST=CA/O=MyOrg/CN=client-service"

# Sign with the same CA
openssl x509 -req -in client-req.pem -days 365 \
  -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial \
  -out client-cert.pem \
  -extfile <(printf "subjectAltName=DNS:client-service")
```

### Server-Side mTLS

```go
serverCert, _ := tls.LoadX509KeyPair("server-cert.pem", "server-key.pem")

caCert, _ := os.ReadFile("ca-cert.pem")
certPool := x509.NewCertPool()
certPool.AppendCertsFromPEM(caCert)

tlsConfig := &tls.Config{
    Certificates: []tls.Certificate{serverCert},
    ClientAuth:   tls.RequireAndVerifyClientCert, // key difference from one-way TLS
    ClientCAs:    certPool,
    MinVersion:   tls.VersionTLS12,
}

creds := credentials.NewTLS(tlsConfig)
grpcServer := grpc.NewServer(grpc.Creds(creds))
```

`tls.RequireAndVerifyClientCert` tells the server to demand a client certificate and verify it against the CA pool. Other options (`RequestClientCert`, `VerifyClientCertIfGiven`) exist but provide weaker guarantees.

### Client-Side mTLS

```go
clientCert, _ := tls.LoadX509KeyPair("client-cert.pem", "client-key.pem")

caCert, _ := os.ReadFile("ca-cert.pem")
certPool := x509.NewCertPool()
certPool.AppendCertsFromPEM(caCert)

tlsConfig := &tls.Config{
    Certificates: []tls.Certificate{clientCert},
    RootCAs:      certPool,
    MinVersion:   tls.VersionTLS12,
}

conn, _ := grpc.Dial("localhost:50051",
    grpc.WithTransportCredentials(credentials.NewTLS(tlsConfig)),
)
```

## Per-RPC Credentials (Call Credentials)

| Type | Scope | Purpose |
|------|-------|---------|
| **Channel credentials** | Entire connection | Encrypt transport, verify endpoints (TLS/mTLS) |
| **Call credentials** | Per RPC | Authenticate the caller identity (tokens, passwords) |

All call credential types implement the `credentials.PerRPCCredentials` interface:

```go
type PerRPCCredentials interface {
    GetRequestMetadata(ctx context.Context, uri ...string) (map[string]string, error)
    RequireTransportSecurity() bool
}
```

### Basic Authentication

```go
type basicAuth struct {
    username string
    password string
}

func (b *basicAuth) GetRequestMetadata(ctx context.Context, uri ...string) (map[string]string, error) {
    encoded := base64.StdEncoding.EncodeToString([]byte(b.username + ":" + b.password))
    return map[string]string{"authorization": "Basic " + encoded}, nil
}

func (b *basicAuth) RequireTransportSecurity() bool { return true }
```

**Client usage:**

```go
conn, _ := grpc.Dial("localhost:50051",
    grpc.WithTransportCredentials(tlsCreds),
    grpc.WithPerRPCCredentials(&basicAuth{username: "admin", password: "secret"}),
)
```

**Server-side validation via unary interceptor:**

```go
func authUnaryInterceptor(ctx context.Context, req interface{},
    info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {

    md, ok := metadata.FromIncomingContext(ctx)
    if !ok {
        return nil, status.Error(codes.Unauthenticated, "missing metadata")
    }

    authHeader := md.Get("authorization")
    if len(authHeader) == 0 {
        return nil, status.Error(codes.Unauthenticated, "missing authorization")
    }

    decoded, err := base64.StdEncoding.DecodeString(
        strings.TrimPrefix(authHeader[0], "Basic "))
    if err != nil {
        return nil, status.Error(codes.Unauthenticated, "invalid encoding")
    }

    parts := strings.SplitN(string(decoded), ":", 2)
    if len(parts) != 2 || !validateCredentials(parts[0], parts[1]) {
        return nil, status.Error(codes.Unauthenticated, "invalid credentials")
    }
    return handler(ctx, req)
}

grpcServer := grpc.NewServer(grpc.Creds(tlsCreds), grpc.UnaryInterceptor(authUnaryInterceptor))
```

### OAuth 2.0 Token-Based Authentication

gRPC provides built-in OAuth support via `google.golang.org/grpc/credentials/oauth`.

```go
import (
    "google.golang.org/grpc/credentials/oauth"
    "golang.org/x/oauth2"
)

tokenSource := oauth2.StaticTokenSource(&oauth2.Token{AccessToken: "my-token"})
oauthCreds := oauth.TokenSource{TokenSource: tokenSource}

conn, _ := grpc.Dial("localhost:50051",
    grpc.WithTransportCredentials(tlsCreds),
    grpc.WithPerRPCCredentials(&oauthCreds),
)
```

The `oauth.TokenSource` wrapper automatically attaches the token as `Bearer <token>` in the `authorization` metadata and refreshes expired tokens if the underlying source supports it.

**Server-side validation** follows the same interceptor pattern, extracting the `Bearer` token from metadata and validating it against the OAuth provider or introspection endpoint.

### JWT Authentication

JWTs are self-contained tokens carrying claims and a cryptographic signature. Ideal for stateless authentication in microservices.

**Token generation (auth service):**

```go
import "github.com/golang-jwt/jwt/v5"

func generateJWT(userID string, key []byte) (string, error) {
    claims := jwt.MapClaims{
        "sub": userID, "iss": "my-auth-service",
        "exp": time.Now().Add(1 * time.Hour).Unix(),
        "iat": time.Now().Unix(),
    }
    return jwt.NewWithClaims(jwt.SigningMethodHS256, claims).SignedString(key)
}
```

**Client credentials:**

```go
type jwtAuth struct{ token string }

func (j *jwtAuth) GetRequestMetadata(ctx context.Context, uri ...string) (map[string]string, error) {
    return map[string]string{"authorization": "Bearer " + j.token}, nil
}
func (j *jwtAuth) RequireTransportSecurity() bool { return true }
```

**Server-side validation interceptor:**

```go
func jwtUnaryInterceptor(ctx context.Context, req interface{},
    info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {

    md, _ := metadata.FromIncomingContext(ctx)
    authHeader := md.Get("authorization")
    if len(authHeader) == 0 {
        return nil, status.Error(codes.Unauthenticated, "missing token")
    }

    tokenString := strings.TrimPrefix(authHeader[0], "Bearer ")
    token, err := jwt.Parse(tokenString, func(t *jwt.Token) (interface{}, error) {
        if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("unexpected signing method: %v", t.Header["alg"])
        }
        return signingKey, nil
    })
    if err != nil || !token.Valid {
        return nil, status.Error(codes.Unauthenticated, "invalid token")
    }

    claims := token.Claims.(jwt.MapClaims)
    newCtx := context.WithValue(ctx, "userID", claims["sub"])
    return handler(newCtx, req)
}
```

### Google Token-Based Authentication

For GCP services, use Application Default Credentials (ADC) which auto-detect the environment (GCE, GKE, Cloud Run, local `gcloud auth`):

```go
import (
    "google.golang.org/grpc/credentials/oauth"
    "golang.org/x/oauth2/google"
)

tokenSource, _ := google.DefaultTokenSource(ctx,
    "https://www.googleapis.com/auth/cloud-platform")

conn, _ := grpc.Dial("my-service.googleapis.com:443",
    grpc.WithTransportCredentials(credentials.NewClientTLSFromCert(nil, "")),
    grpc.WithPerRPCCredentials(&oauth.TokenSource{TokenSource: tokenSource}),
)
```

**Using a service account key file:**

```go
sa, _ := os.ReadFile("service-account-key.json")
jwtConfig, _ := google.JWTConfigFromJSON(sa, "https://www.googleapis.com/auth/cloud-platform")

conn, _ := grpc.Dial("my-service.googleapis.com:443",
    grpc.WithTransportCredentials(credentials.NewClientTLSFromCert(nil, "")),
    grpc.WithPerRPCCredentials(&oauth.TokenSource{TokenSource: jwtConfig.TokenSource(ctx)}),
)
```

## Combining Channel and Call Credentials

Production deployments typically combine TLS (channel) with token-based auth (call):

```go
tlsCreds, _ := credentials.NewClientTLSFromFile("ca-cert.pem", "localhost")
jwtCreds := &jwtAuth{token: myToken}

conn, _ := grpc.Dial("localhost:50051",
    grpc.WithTransportCredentials(tlsCreds),  // channel credentials
    grpc.WithPerRPCCredentials(jwtCreds),     // call credentials
)
```

When `RequireTransportSecurity()` returns `true`, gRPC enforces that the channel uses TLS before attaching call credentials, preventing accidental plaintext token transmission. For streaming RPCs, call credentials attach once at stream creation; expired tokens require establishing a new stream.

## Security Best Practices

**Always use TLS in production.** Never deploy with `grpc.WithInsecure()` or `insecure.NewCredentials()` outside local development. Even internal services need encryption to prevent lateral movement attacks.

**Rotate certificates regularly.** Use short-lived certificates (hours/days, not years). Go's `tls.Config` supports dynamic reloading:

```go
tlsConfig := &tls.Config{
    GetCertificate: func(info *tls.ClientHelloInfo) (*tls.Certificate, error) {
        cert, err := tls.LoadX509KeyPair("server-cert.pem", "server-key.pem")
        return &cert, err
    },
    ClientAuth: tls.RequireAndVerifyClientCert,
    ClientCAs:  certPool,
}
```

**Use mTLS for service-to-service communication.** Every service proves its identity to every other service, implementing zero-trust at the transport layer.

**Validate tokens on every request.** Use chained interceptors for centralized, layered security:

```go
grpcServer := grpc.NewServer(
    grpc.Creds(tlsCreds),
    grpc.ChainUnaryInterceptor(loggingInterceptor, authInterceptor, rateLimitInterceptor),
    grpc.ChainStreamInterceptor(authStreamInterceptor),
)
```

**Additional recommendations:**

- Set `MinVersion: tls.VersionTLS12` on all TLS configurations.
- Use SAN (not CN) for certificate identity -- Go 1.15+ ignores CN by default.
- Store private keys with restrictive permissions (0600) or in a secrets manager.
- Log authentication failures for monitoring, but never log credentials or tokens.
- For unauthenticated health checks, exclude specific methods in the interceptor rather than disabling auth globally.
