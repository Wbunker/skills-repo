# Authentication and Authorization

## Prometheus Server — Built-in Auth (>= 2.24)

Prometheus supports TLS and basic auth natively via a `web.yml` config file.

```bash
prometheus --web.config.file=web.yml
```

### web.yml — Basic Auth

```yaml
basic_auth_users:
  admin: $2y$12$...    # bcrypt hash
  readonly: $2y$12$...
```

Generate bcrypt hash:
```bash
htpasswd -nBC 12 "" | tr -d ':\n'
# or
python3 -c "import bcrypt; print(bcrypt.hashpw(b'password', bcrypt.gensalt(12)).decode())"
```

### web.yml — TLS

```yaml
tls_server_config:
  cert_file: /etc/prometheus/tls/prometheus.crt
  key_file:  /etc/prometheus/tls/prometheus.key
  # Optional: require client certs
  client_auth_type: RequireAndVerifyClientCert
  client_ca_file: /etc/prometheus/tls/ca.crt

# Combine with basic auth
basic_auth_users:
  prometheus: $2y$12$...
```

## Scraping HTTPS Targets

```yaml
scrape_configs:
  - job_name: "secure-app"
    scheme: https
    tls_config:
      ca_file: /etc/prometheus/ca.crt
      cert_file: /etc/prometheus/client.crt    # client cert (if required)
      key_file: /etc/prometheus/client.key
      insecure_skip_verify: false              # never skip in production
    static_configs:
      - targets: ["myapp:8443"]
```

## Scraping with Basic Auth

```yaml
scrape_configs:
  - job_name: "auth-app"
    basic_auth:
      username: "prometheus"
      password_file: /etc/prometheus/secrets/password   # prefer file over inline
    static_configs:
      - targets: ["myapp:8080"]
```

## Scraping with Bearer Token

```yaml
scrape_configs:
  - job_name: "token-app"
    authorization:
      type: Bearer
      credentials_file: /var/run/secrets/token
    static_configs:
      - targets: ["myapp:8080"]
```

## OAuth2 / OIDC Scraping

```yaml
scrape_configs:
  - job_name: "oauth-app"
    oauth2:
      client_id: "prometheus"
      client_secret_file: /etc/prometheus/oauth-secret
      token_url: "https://auth.example.com/oauth2/token"
      scopes:
        - "metrics:read"
    static_configs:
      - targets: ["myapp:8080"]
```

## Alertmanager Auth

```yaml
alerting:
  alertmanagers:
    - scheme: https
      tls_config:
        ca_file: /etc/prometheus/ca.crt
      basic_auth:
        username: "prometheus"
        password_file: /etc/prometheus/secrets/am-password
      static_configs:
        - targets: ["alertmanager:9093"]
```

## OAuth Proxy Pattern

For production, consider placing an OAuth2 proxy in front of Prometheus instead of using Prometheus's built-in auth. Popular options:

- **oauth2-proxy** — supports Google, GitHub, GitLab, OIDC, etc.
- **Keycloak** — full OIDC/OAuth2 identity provider
- **Dex** — lightweight federated identity

Example with oauth2-proxy in front of Prometheus:
```
User → oauth2-proxy → Prometheus
         (OIDC/GitHub/Google auth)
```

```yaml
# oauth2-proxy config
upstreams = ["http://localhost:9090"]
provider = "github"
github-org = "my-org"
email-domains = ["example.com"]
cookie-secret = "..."
client-id = "..."
client-secret = "..."
```

## RBAC for Alertmanager

Alertmanager has no built-in RBAC. Use a reverse proxy for access control.

## Network-Level Access Control

Restrict access at the network level as a primary defense layer:
- Firewall rules to limit port 9090 to trusted networks
- Kubernetes NetworkPolicy to restrict Prometheus access
- Service mesh (Istio, Linkerd) mTLS for pod-to-pod auth

```yaml
# Kubernetes NetworkPolicy example
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: restrict-prometheus
spec:
  podSelector:
    matchLabels:
      app: prometheus
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: grafana
      ports:
        - port: 9090
```

## Secret Management

Never put secrets directly in prometheus.yml. Use:
- `*_file` variants (`password_file`, `credentials_file`, `bearer_token_file`)
- Kubernetes secrets mounted as files
- Vault Agent sidecar
- External Secrets Operator
