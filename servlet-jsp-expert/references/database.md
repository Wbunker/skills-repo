# Database Access with JDBC
*Chapter 6 — JDBC, Connection Pooling, Prepared Statements, DAO Pattern, Transactions*

## JDBC Fundamentals

### JDBC API Objects
```
DriverManager / DataSource
        │ getConnection()
        ▼
    Connection
        │ prepareStatement() / createStatement()
        ▼
    PreparedStatement / Statement
        │ executeQuery() / executeUpdate()
        ▼
    ResultSet (for SELECT)
```

### Adding JDBC Driver

**MySQL:**
```xml
<dependency>
  <groupId>com.mysql</groupId>
  <artifactId>mysql-connector-j</artifactId>
  <version>8.3.0</version>
</dependency>
```
**PostgreSQL:**
```xml
<dependency>
  <groupId>org.postgresql</groupId>
  <artifactId>postgresql</artifactId>
  <version>42.7.1</version>
</dependency>
```
**H2 (in-memory, testing):**
```xml
<dependency>
  <groupId>com.h2database</groupId>
  <artifactId>h2</artifactId>
  <version>2.2.224</version>
</dependency>
```

---

## Direct DriverManager Connection (Simple / No Pooling)

```java
// Avoid in production — no pooling, slow
public class DBUtil {
    private static final String URL  = "jdbc:mysql://localhost:3306/mydb"
                                     + "?useSSL=false&serverTimezone=UTC";
    private static final String USER = "appuser";
    private static final String PASS = "secret";

    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(URL, USER, PASS);
    }
}
```

Always close in a `try-with-resources` block:
```java
try (Connection conn = DBUtil.getConnection();
     PreparedStatement ps = conn.prepareStatement(
         "SELECT * FROM products WHERE id = ?")) {

    ps.setInt(1, productId);

    try (ResultSet rs = ps.executeQuery()) {
        if (rs.next()) {
            Product p = new Product();
            p.setId(rs.getInt("id"));
            p.setName(rs.getString("name"));
            p.setPrice(rs.getDouble("price"));
            return p;
        }
    }
} catch (SQLException e) {
    throw new RuntimeException("Database error", e);
}
```

---

## Connection Pool (JNDI DataSource — Recommended)

### Tomcat DBCP Pool Configuration

**`context.xml` (in `META-INF/context.xml` of the WAR, or Tomcat's `conf/context.xml`):**
```xml
<Context>
  <Resource name="jdbc/mydb"
            auth="Container"
            type="javax.sql.DataSource"
            driverClassName="com.mysql.cj.jdbc.Driver"
            url="jdbc:mysql://localhost:3306/mydb?useSSL=false"
            username="appuser"
            password="secret"
            maxTotal="20"
            maxIdle="10"
            maxWaitMillis="10000"
            validationQuery="SELECT 1"
            testOnBorrow="true"/>
</Context>
```

**`web.xml` — declare the resource reference:**
```xml
<resource-ref>
  <res-ref-name>jdbc/mydb</res-ref-name>
  <res-type>javax.sql.DataSource</res-type>
  <res-auth>Container</res-auth>
</resource-ref>
```

**DBUtil using JNDI:**
```java
public class DBUtil {

    private static DataSource dataSource;

    static {
        try {
            Context ctx = new InitialContext();
            dataSource = (DataSource) ctx.lookup("java:comp/env/jdbc/mydb");
        } catch (NamingException e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    public static Connection getConnection() throws SQLException {
        return dataSource.getConnection();
    }
}
```

---

## PreparedStatement Patterns

### SELECT — Multiple Rows
```java
public List<Product> selectAll() {
    List<Product> list = new ArrayList<>();
    String sql = "SELECT id, name, description, price, stock "
               + "FROM products ORDER BY name";

    try (Connection conn = DBUtil.getConnection();
         PreparedStatement ps = conn.prepareStatement(sql);
         ResultSet rs = ps.executeQuery()) {

        while (rs.next()) {
            list.add(mapRow(rs));
        }
    } catch (SQLException e) {
        throw new RuntimeException(e);
    }
    return list;
}

private Product mapRow(ResultSet rs) throws SQLException {
    Product p = new Product();
    p.setId(rs.getInt("id"));
    p.setName(rs.getString("name"));
    p.setDescription(rs.getString("description"));
    p.setPrice(rs.getDouble("price"));
    p.setStock(rs.getInt("stock"));
    return p;
}
```

### SELECT — Single Row by ID
```java
public Product selectById(int id) {
    String sql = "SELECT id, name, description, price, stock "
               + "FROM products WHERE id = ?";

    try (Connection conn = DBUtil.getConnection();
         PreparedStatement ps = conn.prepareStatement(sql)) {

        ps.setInt(1, id);   // parameter index starts at 1

        try (ResultSet rs = ps.executeQuery()) {
            if (rs.next()) {
                return mapRow(rs);
            }
        }
    } catch (SQLException e) {
        throw new RuntimeException(e);
    }
    return null;
}
```

### INSERT — Returning Generated Key
```java
public int insert(Product product) {
    String sql = "INSERT INTO products (name, description, price, stock) "
               + "VALUES (?, ?, ?, ?)";

    try (Connection conn = DBUtil.getConnection();
         PreparedStatement ps = conn.prepareStatement(
             sql, Statement.RETURN_GENERATED_KEYS)) {

        ps.setString(1, product.getName());
        ps.setString(2, product.getDescription());
        ps.setDouble(3, product.getPrice());
        ps.setInt(4, product.getStock());

        int rowsAffected = ps.executeUpdate();

        if (rowsAffected == 0) {
            throw new SQLException("Insert failed, no rows affected");
        }

        try (ResultSet keys = ps.getGeneratedKeys()) {
            if (keys.next()) {
                return keys.getInt(1);   // return generated id
            }
        }
    } catch (SQLException e) {
        throw new RuntimeException(e);
    }
    throw new RuntimeException("Insert failed, no generated key");
}
```

### UPDATE
```java
public int update(Product product) {
    String sql = "UPDATE products "
               + "SET name = ?, description = ?, price = ?, stock = ? "
               + "WHERE id = ?";

    try (Connection conn = DBUtil.getConnection();
         PreparedStatement ps = conn.prepareStatement(sql)) {

        ps.setString(1, product.getName());
        ps.setString(2, product.getDescription());
        ps.setDouble(3, product.getPrice());
        ps.setInt(4, product.getStock());
        ps.setInt(5, product.getId());

        return ps.executeUpdate();   // returns rows affected

    } catch (SQLException e) {
        throw new RuntimeException(e);
    }
}
```

### DELETE
```java
public int delete(int id) {
    String sql = "DELETE FROM products WHERE id = ?";

    try (Connection conn = DBUtil.getConnection();
         PreparedStatement ps = conn.prepareStatement(sql)) {

        ps.setInt(1, id);
        return ps.executeUpdate();

    } catch (SQLException e) {
        throw new RuntimeException(e);
    }
}
```

### PreparedStatement Parameter Types
```java
ps.setInt(1, intValue);
ps.setLong(1, longValue);
ps.setDouble(1, doubleValue);
ps.setString(1, stringValue);
ps.setBoolean(1, boolValue);
ps.setDate(1, java.sql.Date.valueOf(localDate));
ps.setTimestamp(1, java.sql.Timestamp.valueOf(localDateTime));
ps.setBigDecimal(1, bigDecimalValue);
ps.setNull(1, Types.INTEGER);     // insert SQL NULL
```

---

## Transactions

```java
public void transferFunds(int fromId, int toId, double amount) {
    String debit  = "UPDATE accounts SET balance = balance - ? WHERE id = ?";
    String credit = "UPDATE accounts SET balance = balance + ? WHERE id = ?";

    Connection conn = null;
    try {
        conn = DBUtil.getConnection();
        conn.setAutoCommit(false);   // start transaction

        try (PreparedStatement ps1 = conn.prepareStatement(debit)) {
            ps1.setDouble(1, amount);
            ps1.setInt(2, fromId);
            ps1.executeUpdate();
        }
        try (PreparedStatement ps2 = conn.prepareStatement(credit)) {
            ps2.setDouble(1, amount);
            ps2.setInt(2, toId);
            ps2.executeUpdate();
        }

        conn.commit();     // all-or-nothing

    } catch (SQLException e) {
        if (conn != null) {
            try { conn.rollback(); } catch (SQLException ignored) {}
        }
        throw new RuntimeException("Transfer failed", e);
    } finally {
        if (conn != null) {
            try {
                conn.setAutoCommit(true);
                conn.close();
            } catch (SQLException ignored) {}
        }
    }
}
```

---

## Full DAO Example

```java
public class ProductDAO {

    // ---- READ ----

    public List<Product> selectAll() {
        // ... see above
    }

    public List<Product> selectByCategory(int categoryId) {
        String sql = "SELECT * FROM products WHERE category_id = ? ORDER BY name";
        List<Product> list = new ArrayList<>();
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, categoryId);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) list.add(mapRow(rs));
            }
        } catch (SQLException e) { throw new RuntimeException(e); }
        return list;
    }

    public int countAll() {
        String sql = "SELECT COUNT(*) FROM products";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            if (rs.next()) return rs.getInt(1);
        } catch (SQLException e) { throw new RuntimeException(e); }
        return 0;
    }

    // ---- WRITE ----

    public int insert(Product p)  { /* ... see above */ return 0; }
    public int update(Product p)  { /* ... see above */ return 0; }
    public int delete(int id)     { /* ... see above */ return 0; }

    // ---- HELPER ----

    private Product mapRow(ResultSet rs) throws SQLException {
        Product p = new Product();
        p.setId(rs.getInt("id"));
        p.setName(rs.getString("name"));
        p.setDescription(rs.getString("description"));
        p.setPrice(rs.getDouble("price"));
        p.setStock(rs.getInt("stock"));
        return p;
    }
}
```

---

## Initializing Database at Startup

```java
@WebListener
public class DatabaseInitListener implements ServletContextListener {

    @Override
    public void contextInitialized(ServletContextEvent sce) {
        try (Connection conn = DBUtil.getConnection();
             Statement stmt = conn.createStatement()) {

            // Create tables if not exist (dev/test only)
            stmt.execute(
                "CREATE TABLE IF NOT EXISTS products (" +
                "  id INT AUTO_INCREMENT PRIMARY KEY," +
                "  name VARCHAR(100) NOT NULL," +
                "  price DECIMAL(10,2)," +
                "  stock INT DEFAULT 0" +
                ")");

        } catch (SQLException e) {
            throw new RuntimeException("Database init failed", e);
        }
    }
}
```

---

## Common JDBC Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| `ClassNotFoundException` | Driver JAR not in classpath | Add JDBC driver to `WEB-INF/lib` or Maven `<dependency>` |
| `Connection refused` | DB server not running or wrong port | Verify DB is running; check URL, host, port |
| `Access denied for user` | Wrong username/password or no privileges | Check credentials; `GRANT` access in DB |
| Connection leak | Not closing `Connection` in all code paths | Use `try-with-resources` for `Connection`, `Statement`, `ResultSet` |
| `NullPointerException` on `ResultSet` | Calling `getXxx()` before `next()` | Always call `rs.next()` first; check return value |
| SQL injection | String concatenation in SQL | Always use `PreparedStatement` with `?` placeholders |
| `CommunicationsException` | Idle connections in pool closed by DB | Set `validationQuery="SELECT 1"` and `testOnBorrow=true` in pool config |
| Timezone mismatch for dates | JVM and DB in different timezones | Add `serverTimezone=UTC` to JDBC URL; store/retrieve as UTC |
