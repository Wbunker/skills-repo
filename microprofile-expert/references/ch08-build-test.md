# Chapter 8: Building and Testing Cloud-Native Applications

## Maven Project Structure

```
portfolio/
├── pom.xml
├── src/
│   ├── main/
│   │   ├── java/com/example/portfolio/
│   │   │   ├── PortfolioResource.java
│   │   │   ├── PortfolioService.java
│   │   │   └── model/Portfolio.java
│   │   ├── liberty/config/server.xml
│   │   └── resources/META-INF/
│   │       └── microprofile-config.properties
│   └── test/
│       └── java/com/example/portfolio/
│           ├── PortfolioResourceIT.java
│           └── PortfolioServiceTest.java
```

### Minimal `pom.xml`

```xml
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>portfolio</artifactId>
    <version>1.0-SNAPSHOT</version>
    <packaging>war</packaging>

    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.eclipse.microprofile</groupId>
            <artifactId>microprofile</artifactId>
            <version>4.1</version>
            <type>pom</type>
            <scope>provided</scope>
        </dependency>

        <!-- Test dependencies -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>5.9.0</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-junit-jupiter</artifactId>
            <version>4.8.0</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>io.openliberty.tools</groupId>
                <artifactId>liberty-maven-plugin</artifactId>
                <version>3.5</version>
                <executions>
                    <execution>
                        <id>start-server</id>
                        <phase>pre-integration-test</phase>
                        <goals><goal>start</goal></goals>
                    </execution>
                    <execution>
                        <id>stop-server</id>
                        <phase>post-integration-test</phase>
                        <goals><goal>stop</goal></goals>
                    </execution>
                </executions>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-failsafe-plugin</artifactId>
                <version>3.0.0</version>
                <executions>
                    <execution>
                        <goals>
                            <goal>integration-test</goal>
                            <goal>verify</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
```

---

## Unit Testing

Unit tests run without a server. Mock CDI dependencies with Mockito.

```java
@ExtendWith(MockitoExtension.class)
class PortfolioServiceTest {

    @Mock
    private StockQuoteClient stockQuoteClient;

    @InjectMocks
    private PortfolioService portfolioService;

    @Test
    void testCalculateValue() {
        StockQuote quote = new StockQuote("AAPL", 150.0);
        when(stockQuoteClient.getQuote("AAPL")).thenReturn(quote);

        Portfolio portfolio = new Portfolio("John");
        portfolio.addStock("AAPL", 10);

        double value = portfolioService.calculateValue(portfolio);

        assertEquals(1500.0, value, 0.01);
        verify(stockQuoteClient).getQuote("AAPL");
    }
}
```

---

## Integration Testing with MicroShed Testing

[MicroShed Testing](https://microshed.org/microshed-testing/) spins up a real Docker container and tests the live endpoint.

```xml
<dependency>
    <groupId>org.microshed</groupId>
    <artifactId>microshed-testing-liberty</artifactId>
    <version>0.9.1</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>testcontainers</artifactId>
    <version>1.17.0</version>
    <scope>test</scope>
</dependency>
```

```java
@MicroShedTest
@SharedContainerConfig(AppContainerConfig.class)
class PortfolioResourceIT {

    @RESTClient
    public static PortfolioResource portfolioResource;

    @Test
    void testCreateAndGetPortfolio() {
        portfolioResource.createPortfolio("John");
        Portfolio p = portfolioResource.getPortfolio("John");
        assertEquals("John", p.getOwner());
    }
}

public class AppContainerConfig implements SharedContainerConfiguration {
    @Container
    public static LibertyContainer libertyContainer =
        new LibertyContainer("stock-trader/portfolio:latest")
            .withEnv("DB_HOST", "localhost");
}
```

---

## Integration Testing with the Liberty Maven Plugin

Simpler approach: Liberty starts during `pre-integration-test`, tests run in `integration-test`, Liberty stops in `post-integration-test`.

```java
// Test class name must end in IT to be picked up by Failsafe
class PortfolioResourceIT {

    private static final String BASE_URL =
        "http://localhost:" + System.getProperty("http.port", "9080") + "/api";

    @Test
    void testGetPortfolio() {
        Client client = ClientBuilder.newClient();
        Response response = client.target(BASE_URL + "/portfolios/John")
            .request(MediaType.APPLICATION_JSON)
            .get();
        assertEquals(200, response.getStatus());
        Portfolio p = response.readEntity(Portfolio.class);
        assertEquals("John", p.getOwner());
    }
}
```

---

## Testing MicroProfile Config

```java
@Test
void testConfigInjection() {
    System.setProperty("loyalty.gold.threshold", "75000");
    Config config = ConfigProvider.getConfig();
    double threshold = config.getValue("loyalty.gold.threshold", Double.class);
    assertEquals(75000.0, threshold, 0.01);
}
```

---

## Testing Fault Tolerance

Fault Tolerance annotations are CDI interceptors — they only activate in a CDI container. For unit tests, test the fallback method directly:

```java
@Test
void testFallbackReturnsCache() {
    StockQuote cached = service.getCachedQuote("AAPL");
    assertNotNull(cached);
    // Verify it returns stale data rather than throwing
}
```

For integration testing, use WireMock to simulate downstream failures:

```java
WireMockServer wireMock = new WireMockServer(8089);
wireMock.stubFor(get(urlEqualTo("/stock/AAPL/quote"))
    .willReturn(aResponse().withStatus(503)));
// Assert that fallback activates and returns cached quote
```

---

## Container Image Build in CI/CD

```bash
# Build
mvn package -DskipTests
docker build -t stock-trader/portfolio:${BUILD_NUMBER} .
docker tag stock-trader/portfolio:${BUILD_NUMBER} registry.example.com/portfolio:latest

# Push
docker push registry.example.com/portfolio:${BUILD_NUMBER}
docker push registry.example.com/portfolio:latest

# Deploy
kubectl set image deployment/portfolio portfolio=registry.example.com/portfolio:${BUILD_NUMBER}
kubectl rollout status deployment/portfolio
```
