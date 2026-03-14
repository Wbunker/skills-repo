# Dynamic Invocation and DSLs

Reference for the Dynamic trait, structural types, type providers, and domain-specific languages.

## Table of Contents
- [Dynamic Trait](#dynamic-trait)
- [Domain-Specific Languages](#domain-specific-languages)
- [DSL Techniques](#dsl-techniques)

## Dynamic Trait

### What Dynamic Provides
```scala
import scala.language.dynamics

// Dynamic allows calling methods/accessing fields that don't exist at compile time
// The compiler translates them to special method calls

class DynConfig extends Dynamic:
  private val data = Map("host" -> "localhost", "port" -> "8080")

  // x.field → selectDynamic("field")
  def selectDynamic(name: String): String =
    data.getOrElse(name, s"<unknown: $name>")

  // x.field = value → updateDynamic("field")(value)
  def updateDynamic(name: String)(value: String): Unit =
    println(s"Setting $name = $value")

  // x.method(args) → applyDynamic("method")(args)
  def applyDynamic(name: String)(args: Any*): String =
    s"Called $name with ${args.mkString(", ")}"

  // x.method(name = value) → applyDynamicNamed("method")((name, value))
  def applyDynamicNamed(name: String)(args: (String, Any)*): String =
    s"Called $name with ${args.map((k,v) => s"$k=$v").mkString(", ")}"

val config = DynConfig()
config.host          // selectDynamic("host") → "localhost"
config.port          // selectDynamic("port") → "8080"
config.missing       // selectDynamic("missing") → "<unknown: missing>"
config.run("fast")   // applyDynamic("run")("fast")
```

### Use Cases
```scala
// JSON/config access
class JsonObject(data: Map[String, Any]) extends Dynamic:
  def selectDynamic(name: String): Any = data(name)

val json = JsonObject(Map("name" -> "Alice", "age" -> 30))
json.name  // "Alice"
json.age   // 30

// Database DSL
class Table(name: String) extends Dynamic:
  def selectDynamic(column: String): Column = Column(name, column)

case class Column(table: String, name: String):
  def ===(value: Any): String = s"$table.$name = '$value'"

val users = Table("users")
users.email === "alice@example.com"  // "users.email = 'alice@example.com'"
```

## Domain-Specific Languages

### Internal DSLs in Scala
```scala
// Scala's flexible syntax enables readable DSLs

// 1. Infix notation
infix def should(expected: String): Boolean = ???
"result" should "be correct"

// 2. Symbolic methods
val route = GET / "api" / "users" / IntParam

// 3. Apply method (parentheses-free construction)
case class Duration(millis: Long)
extension (n: Int)
  def seconds: Duration = Duration(n * 1000L)
  def minutes: Duration = Duration(n * 60 * 1000L)
  def hours: Duration = Duration(n * 3600 * 1000L)

val timeout = 30.seconds  // Duration(30000)
val delay = 5.minutes     // Duration(300000)

// 4. By-name parameters (custom control flow)
def retry[A](times: Int)(block: => A): A =
  var attempts = 0
  var lastError: Throwable = null
  while attempts < times do
    try return block
    catch case e: Throwable =>
      lastError = e
      attempts += 1
  throw lastError

retry(3) {
  riskyOperation()
}
```

### Test DSL Example (ScalaTest-like)
```scala
// ScalaTest-style DSL
class MySpec extends AnyFlatSpec:
  "A Stack" should "pop values in LIFO order" in {
    val stack = Stack(1, 2, 3)
    assert(stack.pop() == 3)
  }

  it should "throw on empty pop" in {
    val stack = Stack.empty[Int]
    assertThrows[NoSuchElementException] {
      stack.pop()
    }
  }
```

## DSL Techniques

### Builder Pattern
```scala
case class HttpRequest private (
  method: String = "GET",
  url: String = "",
  headers: Map[String, String] = Map.empty,
  body: Option[String] = None
):
  def get(url: String): HttpRequest = copy(method = "GET", url = url)
  def post(url: String): HttpRequest = copy(method = "POST", url = url)
  def header(key: String, value: String): HttpRequest =
    copy(headers = headers + (key -> value))
  def withBody(b: String): HttpRequest = copy(body = Some(b))

object HttpRequest:
  def apply(): HttpRequest = new HttpRequest()

val request = HttpRequest()
  .post("https://api.example.com/users")
  .header("Content-Type", "application/json")
  .withBody("""{"name": "Alice"}""")
```

### Type-Safe Builders
```scala
// Use phantom types to enforce build order
sealed trait HasUrl
sealed trait NoUrl
sealed trait HasMethod
sealed trait NoMethod

class RequestBuilder[U, M](
  url: String = "",
  method: String = ""
):
  def url(u: String): RequestBuilder[HasUrl, M] =
    RequestBuilder(u, method)
  def get: RequestBuilder[U, HasMethod] =
    RequestBuilder(url, "GET")
  def build(using U =:= HasUrl, M =:= HasMethod): HttpRequest =
    HttpRequest(method, url, Map.empty, None)

RequestBuilder[NoUrl, NoMethod]()
  .url("https://api.example.com")
  .get
  .build  // OK

// RequestBuilder[NoUrl, NoMethod]()
//   .get
//   .build  // ERROR: no URL set
```

### String Interpolators as DSLs
```scala
// Custom string interpolator
extension (sc: StringContext)
  def sql(args: Any*): SqlQuery =
    val parts = sc.parts.iterator
    val params = args.iterator
    val query = StringBuilder()
    val values = List.newBuilder[Any]
    while parts.hasNext do
      query.append(parts.next())
      if params.hasNext then
        query.append("?")
        values += params.next()
    SqlQuery(query.toString, values.result())

case class SqlQuery(query: String, params: List[Any])

val name = "Alice"
val age = 30
val q = sql"SELECT * FROM users WHERE name = $name AND age > $age"
// SqlQuery("SELECT * FROM users WHERE name = ? AND age > ?", List("Alice", 30))
```
