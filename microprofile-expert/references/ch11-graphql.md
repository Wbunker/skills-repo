# Chapter 11: MicroProfile GraphQL 1.1

## GraphQL vs. REST

| Concern | REST | GraphQL |
|---------|------|---------|
| Data fetching | Fixed response shape; multiple endpoints | Client specifies exactly what fields it needs |
| Over-fetching | Returns all fields even if only one is needed | Returns only requested fields |
| Under-fetching | May need multiple requests to assemble a view | One query can span related entities |
| Schema | Informal (OpenAPI documents it) | Strongly typed schema is the contract |
| Mutations | PUT/POST/DELETE | `mutation` operation |

GraphQL is ideal when clients have diverse data needs, or when you are aggregating multiple services behind a single API gateway.

---

## MicroProfile GraphQL Annotations

### @GraphQLApi — Root Resource

```java
@GraphQLApi
@ApplicationScoped
public class PortfolioGraphQLApi {

    @Inject
    private PortfolioService portfolioService;

    @Query("portfolio")
    @Description("Get a portfolio by owner name")
    public Portfolio getPortfolio(
            @Name("owner") @NonNull String owner) {
        return portfolioService.find(owner);
    }

    @Query("portfolios")
    public List<Portfolio> getAllPortfolios() {
        return portfolioService.findAll();
    }

    @Mutation("createPortfolio")
    public Portfolio createPortfolio(@Name("owner") String owner) {
        return portfolioService.create(owner);
    }

    @Mutation("addStock")
    public Portfolio addStock(
            @Name("owner") String owner,
            @Name("symbol") String symbol,
            @Name("shares") int shares) {
        return portfolioService.addStock(owner, symbol, shares);
    }
}
```

### Model Annotations

```java
@Type("Portfolio")
@Description("A stock portfolio belonging to an investor")
public class Portfolio {

    @Id
    private String owner;

    @NonNull
    private double totalValue;

    @Description("List of stock holdings")
    private List<Stock> stocks;

    @Ignore           // exclude field from schema
    private String internalId;

    @Name("valueInEuros")  // rename in schema
    private double valueEur;
}
```

---

## Generated Schema

For the `PortfolioGraphQLApi` above, MicroProfile generates:

```graphql
type Portfolio {
  owner: ID!
  totalValue: Float!
  stocks: [Stock]
}

type Stock {
  symbol: String!
  shares: Int!
  currentPrice: Float
}

type Query {
  portfolio(owner: String!): Portfolio
  portfolios: [Portfolio]
}

type Mutation {
  createPortfolio(owner: String!): Portfolio
  addStock(owner: String!, symbol: String!, shares: Int!): Portfolio
}
```

Schema is available at `/graphql/schema.graphql`.

---

## Client Queries

### GraphQL Query

```graphql
query GetPortfolioSummary {
  portfolio(owner: "John") {
    totalValue
    stocks {
      symbol
      shares
    }
  }
}
```

Returns only `totalValue` and stock `symbol`/`shares` — not the full Portfolio object.

### Variables

```graphql
query GetPortfolio($owner: String!) {
  portfolio(owner: $owner) {
    totalValue
    stocks {
      symbol
      shares
      currentPrice
    }
  }
}
```

Variables:
```json
{ "owner": "John" }
```

### Mutation

```graphql
mutation AddAppleStock {
  addStock(owner: "John", symbol: "AAPL", shares: 10) {
    totalValue
    stocks { symbol shares }
  }
}
```

---

## GraphQL Endpoint

MicroProfile GraphQL exposes:
- `/graphql` — POST endpoint accepting GraphQL queries
- `/graphql/schema.graphql` — schema introspection endpoint
- `/graphql-ui` — GraphiQL browser (Open Liberty, dev mode)

```bash
curl -X POST http://localhost:9080/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ portfolio(owner: \"John\") { totalValue } }"}'
```

---

## Source Fields — Resolving Fields Lazily

Use `@Source` to add fields to a type that are resolved from another bean, avoiding N+1 issues by batch loading:

```java
@GraphQLApi
@ApplicationScoped
public class StockPriceSource {

    @Query
    public Portfolio portfolio(@Name("owner") String owner) {
        return portfolioService.find(owner);  // does NOT load stock prices
    }

    // Called only when client requests currentPrice on Stock
    public Double currentPrice(@Source Stock stock) {
        return stockQuoteClient.getQuote(stock.getSymbol()).getPrice();
    }
}
```

---

## Error Handling

```java
@Query("portfolio")
public Portfolio getPortfolio(@Name("owner") String owner) {
    Portfolio p = portfolioService.find(owner);
    if (p == null) {
        throw new GraphQLException("Portfolio not found: " + owner,
                                   ExceptionType.DataFetchingException);
    }
    return p;
}
```

GraphQL errors are returned in the `errors` array of the response, not as HTTP error codes (HTTP always returns 200 for valid GraphQL responses):

```json
{
  "data": { "portfolio": null },
  "errors": [{
    "message": "Portfolio not found: John",
    "locations": [{"line": 1, "column": 3}],
    "extensions": { "classification": "DataFetchingException" }
  }]
}
```

---

## Open Liberty Configuration

```xml
<featureManager>
    <feature>mpGraphQL-1.1</feature>
</featureManager>
```

`pom.xml` dependency:

```xml
<dependency>
    <groupId>org.eclipse.microprofile.graphql</groupId>
    <artifactId>microprofile-graphql-api</artifactId>
    <version>1.1.0</version>
    <scope>provided</scope>
</dependency>
```
