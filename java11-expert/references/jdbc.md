# Java 11 JDBC
## Drivers, Connection, PreparedStatement, ResultSet, Transactions, DataSource, RowSet

---

## JDBC Architecture

```
Application Code
      │
      │ java.sql API (standard)
      ▼
  DriverManager / DataSource
      │
      │ vendor implementation
      ▼
  JDBC Driver (vendor JAR)
      │
      ▼
  Database
```

### Driver Types

| Type | Description | Example |
|------|-------------|---------|
| Type 1 | JDBC-ODBC bridge (removed Java 8) | Obsolete |
| Type 2 | Native API (C library) | Oracle OCI driver |
| Type 3 | Network middleware | None common today |
| **Type 4** | **Pure Java, direct TCP** | PostgreSQL, MySQL Connector/J, H2 |

Type 4 is universal and recommended.

---

## Connecting to a Database

### `DriverManager`

```java
import java.sql.*;

String url  = "jdbc:postgresql://localhost:5432/mydb";
String user = "alice";
String pass = "secret";

try (Connection conn = DriverManager.getConnection(url, user, pass)) {
    // use connection
}  // auto-closed
```

Common JDBC URL formats:
```
jdbc:postgresql://host:port/dbname
jdbc:mysql://host:port/dbname
jdbc:oracle:thin:@host:port:sid
jdbc:h2:mem:testdb
jdbc:sqlite:/path/to/db.sqlite
```

### Driver Registration

JDBC 4.0+ (Java 6+) auto-registers drivers via `ServiceLoader` — no need for `Class.forName(...)`. Just have the driver JAR on the classpath/modulepath.

---

## `Statement` — Static SQL

```java
try (Connection conn = getConnection();
     Statement stmt = conn.createStatement()) {

    // Query
    ResultSet rs = stmt.executeQuery("SELECT id, name FROM users WHERE active = 1");

    // Update (returns row count)
    int rows = stmt.executeUpdate("DELETE FROM sessions WHERE expired < NOW()");

    // Execute (either — returns true if ResultSet)
    boolean isResultSet = stmt.execute("SELECT 1");
}
```

**Never use `Statement` with user-supplied values** — use `PreparedStatement` to prevent SQL injection.

---

## `PreparedStatement` — Parameterized SQL

```java
String sql = "INSERT INTO users (name, email, age) VALUES (?, ?, ?)";
try (PreparedStatement ps = conn.prepareStatement(sql)) {
    ps.setString(1, name);     // 1-indexed
    ps.setString(2, email);
    ps.setInt(3, age);
    int rowsInserted = ps.executeUpdate();
}

// Query
String query = "SELECT * FROM users WHERE email = ? AND active = ?";
try (PreparedStatement ps = conn.prepareStatement(query)) {
    ps.setString(1, emailInput);
    ps.setBoolean(2, true);
    ResultSet rs = ps.executeQuery();
    while (rs.next()) {
        int id     = rs.getInt("id");
        String nm  = rs.getString("name");
        Date dob   = rs.getDate("date_of_birth");
    }
}
```

### Parameter Setters

| Method | Java Type |
|--------|----------|
| `setString(i, s)` | `String` |
| `setInt(i, n)` | `int` / `Integer` |
| `setLong(i, n)` | `long` / `Long` |
| `setDouble(i, d)` | `double` / `Double` |
| `setBoolean(i, b)` | `boolean` / `Boolean` |
| `setDate(i, d)` | `java.sql.Date` |
| `setTimestamp(i, ts)` | `java.sql.Timestamp` |
| `setNull(i, Types.VARCHAR)` | null |
| `setObject(i, obj)` | any (JDBC maps it) |

---

## `ResultSet`

```java
ResultSet rs = ps.executeQuery();

// Iteration
while (rs.next()) {              // forward only by default
    String name = rs.getString("name");  // by column label
    int id      = rs.getInt(1);          // by column index (1-based)
}

// Metadata
ResultSetMetaData meta = rs.getMetaData();
int cols = meta.getColumnCount();
for (int i = 1; i <= cols; i++) {
    System.out.println(meta.getColumnName(i) + " " + meta.getColumnTypeName(i));
}

// Check for null
rs.getString("middle_name");
rs.wasNull();    // true if last read was SQL NULL
```

### Scrollable / Updatable ResultSet

```java
// Scrollable
Statement stmt = conn.createStatement(
    ResultSet.TYPE_SCROLL_INSENSITIVE,
    ResultSet.CONCUR_READ_ONLY);
ResultSet rs = stmt.executeQuery(sql);
rs.last();              // move to last row
rs.beforeFirst();       // move before first row
rs.absolute(5);         // move to row 5
rs.relative(-1);        // move back one row

// Updatable
Statement stmt = conn.createStatement(
    ResultSet.TYPE_FORWARD_ONLY,
    ResultSet.CONCUR_UPDATABLE);
ResultSet rs = stmt.executeQuery("SELECT id, salary FROM employees");
while (rs.next()) {
    if (rs.getInt("id") == 42) {
        rs.updateDouble("salary", rs.getDouble("salary") * 1.1);
        rs.updateRow();
    }
}
```

---

## `CallableStatement` — Stored Procedures

```java
// Procedure with IN/OUT parameters
CallableStatement cs = conn.prepareCall("{call calculate_bonus(?, ?)}");
cs.setInt(1, employeeId);         // IN
cs.registerOutParameter(2, Types.DOUBLE);  // OUT
cs.execute();
double bonus = cs.getDouble(2);

// Function return value
CallableStatement fn = conn.prepareCall("{? = call get_discount(?)}");
fn.registerOutParameter(1, Types.DECIMAL);
fn.setInt(2, customerId);
fn.execute();
BigDecimal discount = fn.getBigDecimal(1);
```

---

## Transactions

By default, connections are in **auto-commit** mode (each statement is its own transaction).

```java
conn.setAutoCommit(false);  // begin manual transaction

try {
    // Multiple operations as one atomic unit
    ps1.executeUpdate();
    ps2.executeUpdate();
    conn.commit();           // success
} catch (SQLException e) {
    conn.rollback();         // undo all changes
    throw e;
} finally {
    conn.setAutoCommit(true);
}
```

### Savepoints

```java
conn.setAutoCommit(false);
Savepoint sp = conn.setSavepoint("after_insert");
try {
    insertRecord();
    updateStats();    // fails
    conn.commit();
} catch (SQLException e) {
    conn.rollback(sp);  // roll back to savepoint, not beginning
    conn.commit();      // commit what was done before savepoint
}
```

### Transaction Isolation Levels

```java
conn.setTransactionIsolation(Connection.TRANSACTION_READ_UNCOMMITTED);
conn.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);     // common default
conn.setTransactionIsolation(Connection.TRANSACTION_REPEATABLE_READ);
conn.setTransactionIsolation(Connection.TRANSACTION_SERIALIZABLE);
```

| Level | Dirty Read | Non-repeatable Read | Phantom Read |
|-------|-----------|-------------------|-------------|
| READ_UNCOMMITTED | Yes | Yes | Yes |
| READ_COMMITTED | No | Yes | Yes |
| REPEATABLE_READ | No | No | Yes |
| SERIALIZABLE | No | No | No |

---

## Batch Updates

Execute multiple statements in one round trip:

```java
conn.setAutoCommit(false);
PreparedStatement ps = conn.prepareStatement("INSERT INTO log (msg) VALUES (?)");

for (String msg : messages) {
    ps.setString(1, msg);
    ps.addBatch();
}

int[] results = ps.executeBatch();   // array of update counts
conn.commit();
```

---

## `DataSource` — Connection Pooling

`DriverManager` creates new physical connections each time — expensive. Production apps use a connection pool via `DataSource`.

```java
// Using HikariCP (most popular Java connection pool)
HikariConfig config = new HikariConfig();
config.setJdbcUrl("jdbc:postgresql://localhost:5432/mydb");
config.setUsername("alice");
config.setPassword("secret");
config.setMaximumPoolSize(20);
config.setMinimumIdle(5);
config.setConnectionTimeout(30000);

DataSource ds = new HikariDataSource(config);

// Use just like DriverManager, but connections are pooled
try (Connection conn = ds.getConnection()) {
    // use connection — returns to pool on close
}
```

Common pool libraries: HikariCP, Apache DBCP2, c3p0, Tomcat JDBC Pool.

---

## `RowSet`

`RowSet` extends `ResultSet` with additional features. Key implementations:

### `JdbcRowSet` — Connected, Scrollable, Updatable

```java
JdbcRowSet rowSet = RowSetProvider.newFactory().createJdbcRowSet();
rowSet.setUrl("jdbc:h2:mem:test");
rowSet.setUsername("sa");
rowSet.setPassword("");
rowSet.setCommand("SELECT * FROM users");
rowSet.execute();

while (rowSet.next()) {
    System.out.println(rowSet.getString("name"));
}
```

### `CachedRowSet` — Disconnected

```java
CachedRowSet crs = RowSetProvider.newFactory().createCachedRowSet();
// Populate from ResultSet
crs.populate(resultSet);
// Disconnect — works offline
resultSet.close();
connection.close();

// Navigate and modify in memory
crs.beforeFirst();
while (crs.next()) {
    if (crs.getInt("id") == 5) {
        crs.updateString("name", "Bob");
        crs.updateRow();
    }
}

// Sync changes back to DB
try (Connection conn = getConnection()) {
    crs.acceptChanges(conn);
}
```

---

## Exception Handling

```java
try {
    // JDBC operations
} catch (SQLException e) {
    System.err.println("SQLState: " + e.getSQLState());
    System.err.println("Error Code: " + e.getErrorCode());
    System.err.println("Message: " + e.getMessage());

    // Chained exceptions
    for (Throwable t = e; t != null; t = t.getCause()) {
        System.err.println(t);
    }
}
```

Common SQLState prefixes:
- `08` — Connection exceptions
- `23` — Integrity constraint violations (duplicate key, FK violation)
- `42` — Syntax error / access violation
- `HY` — ODBC-style generic errors

---

## Resource Management (try-with-resources)

`Connection`, `Statement`, `PreparedStatement`, `ResultSet` all implement `AutoCloseable`:

```java
try (Connection conn = ds.getConnection();
     PreparedStatement ps = conn.prepareStatement(sql);
     ResultSet rs = ps.executeQuery()) {
    while (rs.next()) {
        // process
    }
}  // rs, ps, conn all closed in reverse order
```
