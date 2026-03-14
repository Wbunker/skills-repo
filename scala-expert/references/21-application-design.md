# Application Design

Reference for dependency injection, modularity, design patterns, anti-patterns, and best practices.

## Table of Contents
- [Design Principles](#design-principles)
- [Dependency Injection](#dependency-injection)
- [Modularity Patterns](#modularity-patterns)
- [Error Handling Strategy](#error-handling-strategy)
- [Anti-Patterns](#anti-patterns)
- [Best Practices](#best-practices)

## Design Principles

### Functional Architecture
```
┌──────────────────────────────────────┐
│           Application Shell          │
│  (main, config, wiring, IO boundary) │
├──────────────────────────────────────┤
│          Service Layer               │
│  (business logic, pure functions)    │
├──────────────────────────────────────┤
│          Domain Model                │
│  (case classes, ADTs, value objects) │
├──────────────────────────────────────┤
│       Infrastructure / Adapters      │
│  (DB, HTTP, messaging, filesystem)   │
└──────────────────────────────────────┘

- Push side effects to the edges
- Keep the core logic pure
- Use types to encode business rules
```

### Algebraic Data Types for Domain Modeling
```scala
// Encode business rules in types
enum OrderStatus:
  case Pending
  case Confirmed(confirmedAt: java.time.Instant)
  case Shipped(trackingId: String)
  case Delivered(deliveredAt: java.time.Instant)
  case Cancelled(reason: String)

// Invalid states are unrepresentable
case class Order(
  id: OrderId,
  items: NonEmptyList[OrderItem],  // at least one item
  status: OrderStatus
)

// Opaque types prevent mixing up IDs
object Domain:
  opaque type OrderId = Long
  opaque type CustomerId = Long
  opaque type ProductId = Long
  // Can't accidentally pass a CustomerId where OrderId is expected
```

## Dependency Injection

### Constructor Injection (Simplest)
```scala
// Define abstractions
trait UserRepository:
  def find(id: UserId): IO[Option[User]]
  def save(user: User): IO[Unit]

trait EmailService:
  def send(to: String, subject: String, body: String): IO[Unit]

// Inject via constructor
class UserService(
  repo: UserRepository,
  email: EmailService
):
  def register(name: String, emailAddr: String): IO[User] =
    val user = User(UserId.generate(), name, emailAddr)
    for
      _ <- repo.save(user)
      _ <- email.send(emailAddr, "Welcome!", s"Hello $name")
    yield user

// Wire in main
@main def app(): Unit =
  val repo = PostgresUserRepository(dataSource)
  val email = SmtpEmailService(smtpConfig)
  val service = UserService(repo, email)
  service.register("Alice", "alice@example.com")
```

### Using ZIO Layers
```scala
import zio.*

// Define services as traits with companion layer
trait UserRepo:
  def find(id: UserId): Task[Option[User]]

object UserRepo:
  val live: ZLayer[DataSource, Nothing, UserRepo] =
    ZLayer.fromFunction((ds: DataSource) => new UserRepo:
      def find(id: UserId) = ???
    )

// Compose layers
val appLayer: ZLayer[Any, Throwable, UserRepo & EmailService] =
  DataSource.live >>> (UserRepo.live ++ EmailService.live)

// Program uses environment
val program: ZIO[UserRepo & EmailService, Throwable, Unit] = for
  repo  <- ZIO.service[UserRepo]
  email <- ZIO.service[EmailService]
  user  <- repo.find(UserId(42))
  _     <- email.send(user.get.email, "Hello", "World")
yield ()

// Run with layers
program.provide(appLayer)
```

### Cake Pattern (Legacy)
```scala
// Layered self-types (Scala 2 era, less common in Scala 3)
trait UserRepoComponent:
  def userRepo: UserRepository
  trait UserRepository:
    def find(id: Int): Option[User]

trait UserServiceComponent:
  self: UserRepoComponent =>  // depends on UserRepoComponent
  def userService: UserService
  class UserService:
    def getUser(id: Int): Option[User] = userRepo.find(id)

// Wiring
object ProductionApp extends UserRepoComponent, UserServiceComponent:
  val userRepo = new UserRepository:
    def find(id: Int) = ???
  val userService = new UserService

// Note: Cake pattern is verbose — prefer constructor injection or ZIO layers
```

## Modularity Patterns

### Package Organization
```
com.example.app/
├── domain/           # Pure domain model
│   ├── model.scala   # Case classes, enums, value objects
│   └── errors.scala  # Domain-specific error types
├── service/          # Business logic
│   ├── UserService.scala
│   └── OrderService.scala
├── infra/            # Infrastructure adapters
│   ├── db/
│   ├── http/
│   └── messaging/
├── api/              # API layer (HTTP routes, gRPC)
│   └── routes/
└── Main.scala        # Wiring and startup
```

### Tagless Final Pattern
```scala
// Abstract over effect type
trait UserAlgebra[F[_]]:
  def find(id: UserId): F[Option[User]]
  def save(user: User): F[Unit]

// Implementation for IO
class UserInterpreter extends UserAlgebra[IO]:
  def find(id: UserId): IO[Option[User]] = ???
  def save(user: User): IO[Unit] = ???

// Business logic is generic over F
def registerUser[F[_]: Monad](
  repo: UserAlgebra[F],
  email: EmailAlgebra[F]
)(name: String, addr: String): F[User] =
  val user = User(name, addr)
  for
    _ <- repo.save(user)
    _ <- email.sendWelcome(user)
  yield user

// Test with a different F (e.g., Id, State)
class TestUserInterpreter extends UserAlgebra[cats.Id]:
  private var users = Map.empty[UserId, User]
  def find(id: UserId): Option[User] = users.get(id)
  def save(user: User): Unit = users += (user.id -> user)
```

## Error Handling Strategy

### Error Types
```scala
// Domain errors as ADTs
enum AppError:
  case NotFound(entity: String, id: String)
  case ValidationError(field: String, message: String)
  case Unauthorized(reason: String)
  case Conflict(message: String)

// Use Either for expected errors
def findUser(id: UserId): IO[Either[AppError, User]]

// Use exceptions only for unexpected/fatal errors
// (OutOfMemoryError, StackOverflowError, etc.)

// Cats EitherT for composing
import cats.data.EitherT

def processOrder(orderId: OrderId): EitherT[IO, AppError, Receipt] =
  for
    order <- EitherT(findOrder(orderId))
    _     <- EitherT(validateOrder(order))
    receipt <- EitherT(chargePayment(order))
  yield receipt
```

## Anti-Patterns

### What to Avoid
```scala
// 1. Overusing Any/AnyRef
// BAD: def process(data: Any): Any
// GOOD: def process[A: JsonCodec](data: A): Result[A]

// 2. Mutable state in services
// BAD:
class Service:
  var cache = Map.empty[String, Data]  // thread-unsafe
// GOOD:
class Service(cache: Ref[IO, Map[String, Data]])  // thread-safe reference

// 3. Stringly-typed APIs
// BAD: def setStatus(status: String): Unit
// GOOD: def setStatus(status: OrderStatus): Unit

// 4. Throwing exceptions for control flow
// BAD: throw new NotFoundException("user not found")
// GOOD: Left(AppError.NotFound("user", id))

// 5. Blocking in async code
// BAD: Await.result(future, 10.seconds) inside a Future
// GOOD: future.flatMap(result => ...)

// 6. Over-engineering (too many abstractions)
// Start simple, add abstraction when needed
// Three concrete implementations → then extract interface
```

## Best Practices

### Scala Style Guide
```scala
// 1. Prefer val over var
val immutable = "safe"

// 2. Prefer immutable collections
val users = List(user1, user2)

// 3. Use Option instead of null
def find(id: Int): Option[User]

// 4. Use case classes for data
case class Config(host: String, port: Int)

// 5. Use sealed traits/enums for ADTs
enum Color:
  case Red, Green, Blue

// 6. Use for comprehensions for monadic composition
for
  user <- findUser(id)
  orders <- findOrders(user)
yield (user, orders)

// 7. Keep methods short and focused
// 8. Use meaningful names
// 9. Favor composition over inheritance
// 10. Make illegal states unrepresentable with types
```

### Project Scaffolding
```bash
# Scala 3 project with Typelevel stack
sbt new typelevel/typelevel.g8

# Scala 3 minimal
sbt new scala/scala3.g8

# HTTP4s project
sbt new http4s/http4s.g8

# Cross-building project
sbt new scala/scala3-cross.g8
```
