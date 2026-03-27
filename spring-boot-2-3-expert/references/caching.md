# Spring Boot 2.3 — Caching

## Setup

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-cache</artifactId>
</dependency>
```

Enable caching with `@EnableCaching` on a configuration class:

```java
@SpringBootApplication
@EnableCaching
public class MyApplication {}
```

---

## Core Cache Annotations

### @Cacheable

Caches the method return value. On subsequent calls with same key, returns cached value without executing the method.

```java
@Service
public class ProductService {

    @Cacheable("products")
    public Product getById(Long id) {
        // This code only runs on cache miss
        return productRepository.findById(id).orElseThrow();
    }

    // Custom key expression (SpEL)
    @Cacheable(value = "products", key = "#id")
    public Product getByIdExplicit(Long id) { ... }

    // Composite key
    @Cacheable(value = "products", key = "#category + '_' + #page")
    public List<Product> getByCategory(String category, int page) { ... }

    // Condition — only cache if arg is non-null
    @Cacheable(value = "products", condition = "#id != null")
    public Product getByIdConditional(Long id) { ... }

    // Unless — don't cache null results
    @Cacheable(value = "products", unless = "#result == null")
    public Product getByIdNonNull(Long id) { ... }

    // Sync — only one thread computes; others wait
    @Cacheable(value = "products", sync = true)
    public Product getByIdSync(Long id) { ... }
}
```

### @CachePut

Always executes the method and updates the cache with the result. Used for cache population after create/update.

```java
@CachePut(value = "products", key = "#product.id")
public Product updateProduct(Product product) {
    return productRepository.save(product);
}

@CachePut(value = "products", key = "#result.id")
public Product createProduct(Product product) {
    return productRepository.save(product);
}
```

### @CacheEvict

Removes entries from cache.

```java
// Evict by key
@CacheEvict(value = "products", key = "#id")
public void deleteProduct(Long id) {
    productRepository.deleteById(id);
}

// Evict all entries in cache
@CacheEvict(value = "products", allEntries = true)
public void refreshProductCache() { }

// Evict before method execution (not after)
@CacheEvict(value = "products", key = "#id", beforeInvocation = true)
public void deleteBeforeExecution(Long id) { }
```

### @Caching (multiple cache operations)

```java
@Caching(
    cacheable = { @Cacheable("products") },
    put = { @CachePut(value = "product-by-sku", key = "#result.sku") },
    evict = { @CacheEvict(value = "product-lists", allEntries = true) }
)
public Product createProduct(Product product) {
    return productRepository.save(product);
}
```

### @CacheConfig (class-level defaults)

```java
@Service
@CacheConfig(cacheNames = "products")
public class ProductService {

    @Cacheable     // uses "products" from @CacheConfig
    public Product getById(Long id) { ... }

    @CacheEvict    // uses "products" from @CacheConfig
    public void delete(Long id) { ... }
}
```

---

## Cache Providers

Spring Boot auto-detects in this order:

1. Generic (explicit `Cache` beans)
2. JCache (JSR-107) — EhCache 3, Hazelcast, Infinispan
3. EhCache 2.x
4. Hazelcast
5. Infinispan
6. Couchbase
7. **Redis** (if Lettuce/Jedis on classpath)
8. **Caffeine** (if Caffeine on classpath)
9. Simple (ConcurrentHashMap, default — no TTL)
10. None (disables caching)

Force specific provider:
```properties
spring.cache.type=redis    # or caffeine, simple, none, jcache, etc.
```

---

## Redis Cache

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

```properties
spring.redis.host=localhost
spring.redis.port=6379
spring.redis.password=

# Cache-specific Redis config
spring.cache.redis.time-to-live=600000    # 10 minutes in ms
spring.cache.redis.key-prefix=myapp::
spring.cache.redis.use-key-prefix=true
spring.cache.redis.cache-null-values=true

# Pre-create named caches on startup
spring.cache.cache-names=products,users,categories
```

### Custom RedisCacheManager

```java
@Configuration
public class CacheConfig {

    @Bean
    public RedisCacheManagerBuilderCustomizer redisCacheManagerCustomizer() {
        return builder -> builder
            .withCacheConfiguration("products",
                RedisCacheConfiguration.defaultCacheConfig()
                    .entryTtl(Duration.ofMinutes(10))
                    .serializeValuesWith(
                        RedisSerializationContext.SerializationPair.fromSerializer(
                            new GenericJackson2JsonRedisSerializer())))
            .withCacheConfiguration("users",
                RedisCacheConfiguration.defaultCacheConfig()
                    .entryTtl(Duration.ofMinutes(30)))
            .withCacheConfiguration("sessions",
                RedisCacheConfiguration.defaultCacheConfig()
                    .entryTtl(Duration.ofHours(1)));
    }

    // Or full custom RedisCacheManager bean
    @Bean
    public RedisCacheManager cacheManager(RedisConnectionFactory connectionFactory) {
        RedisCacheConfiguration defaultConfig = RedisCacheConfiguration
            .defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(10))
            .disableCachingNullValues()
            .serializeKeysWith(
                RedisSerializationContext.SerializationPair.fromSerializer(
                    new StringRedisSerializer()))
            .serializeValuesWith(
                RedisSerializationContext.SerializationPair.fromSerializer(
                    new GenericJackson2JsonRedisSerializer()));

        Map<String, RedisCacheConfiguration> cacheConfigs = new HashMap<>();
        cacheConfigs.put("products", defaultConfig.entryTtl(Duration.ofMinutes(5)));
        cacheConfigs.put("users", defaultConfig.entryTtl(Duration.ofHours(1)));

        return RedisCacheManager.builder(connectionFactory)
            .cacheDefaults(defaultConfig)
            .withInitialCacheConfigurations(cacheConfigs)
            .transactionAware()
            .build();
    }
}
```

---

## Caffeine Cache

```xml
<dependency>
    <groupId>com.github.ben-manes.caffeine</groupId>
    <artifactId>caffeine</artifactId>
</dependency>
```

```properties
spring.cache.type=caffeine
spring.cache.cache-names=products,users
spring.cache.caffeine.spec=maximumSize=500,expireAfterAccess=600s
```

Caffeine spec options:
- `maximumSize=N` — max number of entries
- `maximumWeight=N` — max weight (requires Weigher)
- `expireAfterAccess=Xs` — expire after last access
- `expireAfterWrite=Xs` — expire after write
- `refreshAfterWrite=Xs` — refresh (async) after write
- `recordStats` — enable statistics

Per-cache Caffeine configuration:

```java
@Bean
public CaffeineCacheManager caffeineCacheManager() {
    CaffeineCacheManager manager = new CaffeineCacheManager();

    // default spec for all caches
    manager.setCaffeineSpec(CaffeineSpec.parse("maximumSize=500,expireAfterAccess=10m"));

    // specific caches created eagerly
    manager.setCacheNames(Set.of("products", "users"));

    return manager;
}

// Or per-cache customization using CacheManagerCustomizer:
@Bean
public CacheManagerCustomizer<CaffeineCacheManager> caffeineCacheManagerCustomizer() {
    return manager -> {
        // Can't easily do per-cache TTL with basic CaffeineCacheManager
        // Use Cache2k or implement CacheManager directly for per-cache config
        manager.setAllowNullValues(false);
    };
}
```

---

## Simple Cache (Default — dev/test)

No dependencies needed. Uses `ConcurrentHashMap`. **No TTL**.

```properties
spring.cache.cache-names=products,users
# That's all — Spring Boot creates simple in-memory caches
```

Useful for development. In production, use Redis or Caffeine.

---

## Key Generation

Default key: method parameters joined (or empty for no-args). Custom global key generator:

```java
@Configuration
public class CacheKeyConfig {

    @Bean
    public KeyGenerator customKeyGenerator() {
        return (target, method, params) ->
            target.getClass().getSimpleName() + "::" +
            method.getName() + "::" +
            Arrays.stream(params)
                .map(Object::toString)
                .collect(Collectors.joining(","));
    }
}

// Use in annotation
@Cacheable(value = "products", keyGenerator = "customKeyGenerator")
public Product getById(Long id) { ... }
```

---

## Cache Statistics

With Caffeine:
```properties
spring.cache.caffeine.spec=maximumSize=500,recordStats
```

```java
// Access via CacheManager
@Autowired CacheManager cacheManager;

CaffeineCache cache = (CaffeineCache) cacheManager.getCache("products");
CacheStats stats = cache.getNativeCache().stats();
System.out.println("Hit rate: " + stats.hitRate());
System.out.println("Miss count: " + stats.missCount());
```

With Micrometer (auto-exposes cache metrics when actuator is on classpath):
```
cache.gets{cache="products", cacheManager="cacheManager", result="hit"}
cache.gets{cache="products", cacheManager="cacheManager", result="miss"}
cache.puts{cache="products", cacheManager="cacheManager"}
cache.evictions{cache="products", cacheManager="cacheManager"}
```

---

## Disabling Cache in Tests

```java
@SpringBootTest
@TestPropertySource(properties = "spring.cache.type=none")
class ServiceTest {
    // caching disabled — real method always executes
}
```
