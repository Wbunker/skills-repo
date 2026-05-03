# Chapter 3: The IBM Stock Trader Reference Application

## Purpose

Stock Trader is the concrete, end-to-end example used throughout the book. It is a real open-source cloud-native application that demonstrates how MicroProfile specifications work together in a realistic system.

GitHub: `https://github.com/IBMStockTrader`

## Business Use Case

Users manage a portfolio of stock holdings. They can:
- Create and delete portfolios
- Add or remove stock shares
- View portfolio valuation (real-time stock prices fetched externally)
- Receive loyalty-level notifications based on portfolio value

## Mandatory Microservices

| Service | Technology | Role |
|---------|-----------|------|
| `portfolio` | MicroProfile (Java) | Core business logic; orchestrates all other services |
| `stock-quote` | MicroProfile (Java) | Fetches real-time stock prices (REST client to external API) |
| `trader` | JSF / Liberty | Web UI front-end |
| `account` | MicroProfile (Java) | Manages user account data (DB2 or Cloudant) |
| `broker` | MicroProfile (Java) | Executes trades; applies loyalty tier logic |

## Optional Microservices

| Service | Role |
|---------|------|
| `notification-twitter` | Sends loyalty-level change tweets |
| `notification-slack` | Sends loyalty-level change Slack messages |
| `trade-history` | Audit log of all trades (event sourcing) |
| `looper` | Load testing utility |
| `collector` | Aggregates metrics |

## Architecture Patterns Demonstrated

- **REST Client**: `portfolio` calls `stock-quote` using MicroProfile Rest Client
- **JWT Security**: inter-service calls carry JWT tokens; `portfolio` validates them
- **Config**: external service URLs, API keys via MicroProfile Config / Kubernetes ConfigMaps
- **Fault Tolerance**: circuit breaker on `stock-quote` calls; retry on transient failures
- **Health**: each service exposes `/health/live` and `/health/ready`
- **Metrics**: portfolio value, trade counts exposed via `/metrics`
- **OpenTracing**: traces span from UI through `portfolio` → `stock-quote`

## Loyalty Tier Logic (Business Rule)

| Portfolio Value | Tier |
|----------------|------|
| < $10,000 | Bronze |
| $10,000 – $49,999 | Silver |
| $50,000 – $99,999 | Gold |
| ≥ $100,000 | Platinum |

Tier changes trigger notifications via the optional notification services (Twitter/Slack).

## Data Flow

```
Trader UI (JSF)
    │ HTTP + JWT
    ▼
Portfolio Service (JAX-RS + CDI)
    ├──▶ Stock Quote Service (REST Client + Fault Tolerance)
    │         └──▶ External Stock API (IEX Cloud / API Connect)
    ├──▶ Account Service (JAX-RS)
    └──▶ Notification Services (async, via messaging)
```

## Deployment

- Each microservice is a Docker image
- Deployed to Kubernetes (or OpenShift)
- Configuration injected via ConfigMaps and Secrets
- Services communicate over the Kubernetes internal network
