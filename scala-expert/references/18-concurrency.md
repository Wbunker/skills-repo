# Tools for Concurrency

Reference for Futures, Promises, parallel collections, actors, and thread safety.

## Table of Contents
- [Futures](#futures)
- [Promises](#promises)
- [Parallel Collections](#parallel-collections)
- [Actors (Akka)](#actors-akka)
- [Thread Safety](#thread-safety)

## Futures

### Basic Futures
```scala
import scala.concurrent.{Future, Await}
import scala.concurrent.ExecutionContext.Implicits.global
import scala.concurrent.duration.*

// Create a future (starts executing immediately)
val f: Future[Int] = Future {
  Thread.sleep(1000)
  42
}

// Non-blocking: register callbacks
f.onComplete {
  case scala.util.Success(value) => println(s"Got: $value")
  case scala.util.Failure(ex)    => println(s"Failed: $ex")
}

// Blocking (avoid in production)
val result = Await.result(f, 5.seconds)

// map / flatMap
val doubled: Future[Int] = f.map(_ * 2)
val chained: Future[String] = f.flatMap(n => Future(n.toString))
```

### Composing Futures
```scala
// Sequential (each depends on previous)
val sequential: Future[String] = for
  user    <- fetchUser(42)
  orders  <- fetchOrders(user.id)
  summary <- buildSummary(user, orders)
yield summary

// Parallel (start all at once, combine results)
val userF = fetchUser(42)        // starts immediately
val settingsF = fetchSettings()  // starts immediately
val statsF = fetchStats()        // starts immediately

val parallel: Future[(User, Settings, Stats)] = for
  user     <- userF
  settings <- settingsF
  stats    <- statsF
yield (user, settings, stats)

// Future.sequence: List[Future[A]] → Future[List[A]]
val futures: List[Future[Int]] = List(Future(1), Future(2), Future(3))
val combined: Future[List[Int]] = Future.sequence(futures)
// Future(List(1, 2, 3))

// Future.traverse: List[A] → (A → Future[B]) → Future[List[B]]
val userIds = List(1, 2, 3)
val users: Future[List[User]] = Future.traverse(userIds)(fetchUser)
```

### Error Handling
```scala
val f: Future[Int] = Future(riskyOperation())

// recover: handle specific exceptions
val safe: Future[Int] = f.recover {
  case _: TimeoutException => -1
  case _: IOException      => 0
}

// recoverWith: return another Future
val retried: Future[Int] = f.recoverWith {
  case _: TimeoutException => Future(riskyOperation())  // retry
}

// fallbackTo: try another Future if this one fails
val withFallback: Future[Int] = f.fallbackTo(Future(defaultValue))

// transform
val transformed: Future[String] = f.transform(
  success = value => s"Got: $value",
  failure = ex => RuntimeException(s"Wrapped: ${ex.getMessage}")
)
```

### ExecutionContext
```scala
import scala.concurrent.ExecutionContext
import java.util.concurrent.Executors

// Default global: ForkJoinPool (good for CPU-bound)
import ExecutionContext.Implicits.global

// Custom for IO-bound work
val ioEC = ExecutionContext.fromExecutorService(
  Executors.newFixedThreadPool(32)
)

// Use specific context
Future {
  blockingIOOperation()
}(ioEC)

// Or with given
given ExecutionContext = ioEC
```

## Promises

### Promise[A]
```scala
import scala.concurrent.Promise

// A Promise is a writable Future
val promise = Promise[Int]()
val future: Future[Int] = promise.future  // read-only view

// Complete the promise (can only be done once)
promise.success(42)
// or
promise.failure(Exception("oops"))

// Use case: bridging callback APIs to Future APIs
def asyncOperation(callback: Int => Unit): Unit = ???

def asFuture: Future[Int] =
  val p = Promise[Int]()
  asyncOperation(result => p.success(result))
  p.future
```

## Parallel Collections

### Parallel Operations
```scala
// Convert to parallel collection
val xs = (1 to 1_000_000).toVector
val sum = xs.par.map(_ * 2).filter(_ % 3 == 0).sum

// .par creates a parallel collection
// Operations execute on multiple threads
// Results are combined automatically

// Caveats:
// - Side effects are non-deterministic
// - Not faster for small collections (overhead)
// - Order of side effects is unpredictable
// - Use .seq to convert back to sequential
```

## Actors (Akka)

### Actor Basics
```scala
// Akka Typed actors (modern API)
import akka.actor.typed.{ActorRef, ActorSystem, Behavior}
import akka.actor.typed.scaladsl.Behaviors

// Define messages
sealed trait Command
case class Greet(name: String, replyTo: ActorRef[Greeting]) extends Command
case class Greeting(message: String)

// Define behavior
object Greeter:
  def apply(): Behavior[Command] = Behaviors.receive { (context, message) =>
    message match
      case Greet(name, replyTo) =>
        context.log.info(s"Greeting $name")
        replyTo ! Greeting(s"Hello, $name!")
        Behaviors.same
  }

// Create actor system
val system = ActorSystem(Greeter(), "greeter-system")
```

### Actor Principles
```
- Actors process one message at a time (no shared state)
- Communication only through messages (no shared memory)
- Each actor has a mailbox (message queue)
- Actors can create child actors (supervision hierarchy)
- Location transparent (can run on different nodes)
```

## Thread Safety

### Immutability Is the Best Strategy
```scala
// Immutable data is inherently thread-safe
case class Config(host: String, port: Int)  // thread-safe
val config = Config("localhost", 8080)       // safe to share

// Use immutable collections
val sharedData = Map("key" -> "value")      // thread-safe
```

### Synchronization (When Mutable Is Needed)
```scala
// synchronized blocks
class Counter:
  private var count = 0
  def increment(): Unit = synchronized { count += 1 }
  def get: Int = synchronized { count }

// Atomic variables
import java.util.concurrent.atomic.AtomicInteger
class AtomicCounter:
  private val count = AtomicInteger(0)
  def increment(): Int = count.incrementAndGet()
  def get: Int = count.get()

// Concurrent collections
import java.util.concurrent.ConcurrentHashMap
val cache = ConcurrentHashMap[String, Int]()
cache.put("key", 42)
cache.computeIfAbsent("other", _ => expensiveComputation())
```

### Best Practices
```scala
// 1. Prefer immutability
// 2. Use Futures for async composition
// 3. Use actors for stateful concurrent entities
// 4. Use effect systems (Cats Effect IO, ZIO) for structured concurrency
// 5. Avoid shared mutable state
// 6. If you must mutate, use atomic operations or synchronized
// 7. Don't block Futures — use map/flatMap instead of Await
```
