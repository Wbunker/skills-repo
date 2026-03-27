# Java 11 Concurrency
## Threads, ExecutorService, Synchronization, CompletableFuture, Concurrent Collections, Fork/Join

---

## Thread Fundamentals

### Creating Threads

```java
// Option 1: Extend Thread
class MyThread extends Thread {
    @Override public void run() { System.out.println("Running"); }
}
new MyThread().start();

// Option 2: Implement Runnable (preferred — separates task from thread)
Runnable task = () -> System.out.println("Running");
Thread t = new Thread(task);
t.start();

// Option 3: Use an ExecutorService (preferred for production)
```

### Thread Lifecycle

```
NEW → RUNNABLE → (BLOCKED / WAITING / TIMED_WAITING) → TERMINATED
```

```java
Thread.State state = thread.getState();
thread.join();              // wait for thread to terminate
thread.join(5000);          // wait up to 5 seconds
Thread.sleep(1000);         // pause current thread 1 second
thread.interrupt();         // request interruption
Thread.currentThread().isInterrupted();  // check interrupt flag
```

---

## ExecutorService

`ExecutorService` decouples task submission from execution mechanics.

### Factory Methods (`Executors`)

```java
ExecutorService fixed   = Executors.newFixedThreadPool(4);       // bounded pool
ExecutorService cached  = Executors.newCachedThreadPool();       // unbounded, reuse idle threads
ExecutorService single  = Executors.newSingleThreadExecutor();   // single thread, serial order
ScheduledExecutorService sched = Executors.newScheduledThreadPool(2);
```

### Submitting Tasks

```java
ExecutorService executor = Executors.newFixedThreadPool(4);

// Fire and forget
executor.execute(() -> System.out.println("task"));

// Submit Runnable → Future<?>
Future<?> f = executor.submit(() -> System.out.println("task"));

// Submit Callable → Future<T>
Future<Integer> future = executor.submit(() -> {
    Thread.sleep(100);
    return 42;
});

// Get result (blocks)
Integer result = future.get();              // blocks indefinitely
Integer result = future.get(2, TimeUnit.SECONDS);  // timeout
future.cancel(true);                        // attempt cancellation
future.isDone();
future.isCancelled();
```

### Shutdown

```java
executor.shutdown();           // no new tasks; existing tasks finish
executor.shutdownNow();        // attempts to stop running tasks; returns pending
executor.awaitTermination(30, TimeUnit.SECONDS);

// Idiomatic shutdown pattern
executor.shutdown();
try {
    if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
        executor.shutdownNow();
    }
} catch (InterruptedException e) {
    executor.shutdownNow();
    Thread.currentThread().interrupt();
}
```

### Batch Submission

```java
List<Callable<String>> tasks = List.of(
    () -> "task1", () -> "task2", () -> "task3");

// Run all, get all results
List<Future<String>> futures = executor.invokeAll(tasks);

// Run all, return first to complete
String first = executor.invokeAny(tasks);
```

---

## ScheduledExecutorService

```java
ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);

// Run once after delay
scheduler.schedule(() -> System.out.println("delayed"), 5, TimeUnit.SECONDS);

// Run periodically (fixed rate — next starts from previous start)
scheduler.scheduleAtFixedRate(
    () -> System.out.println("ping"), 0, 1, TimeUnit.SECONDS);

// Run periodically (fixed delay — next starts after previous ends)
scheduler.scheduleWithFixedDelay(
    () -> process(), 0, 500, TimeUnit.MILLISECONDS);
```

---

## Synchronization

### `synchronized`

```java
class Counter {
    private int count = 0;

    public synchronized void increment() { count++; }    // instance lock
    public synchronized int get() { return count; }

    public static synchronized void staticMethod() { }   // class lock

    public void block() {
        synchronized (this) {   // explicit block
            count++;
        }
    }
}
```

### `volatile`

Guarantees **visibility** (reads/writes go to main memory, not CPU cache) but NOT atomicity:

```java
private volatile boolean running = true;   // visible across threads

// Safe for flags and single-variable state
// NOT safe for compound operations like count++ (use AtomicInteger)
```

### `ReentrantLock`

More flexible than `synchronized`: tryLock, timeout, fair ordering, multiple conditions.

```java
Lock lock = new ReentrantLock();

lock.lock();
try {
    // critical section
} finally {
    lock.unlock();  // always unlock in finally
}

// Try with timeout
if (lock.tryLock(1, TimeUnit.SECONDS)) {
    try { /* work */ } finally { lock.unlock(); }
}

// Condition variables
Condition notFull = lock.newCondition();
notFull.await();        // release lock and wait
notFull.signal();       // wake one waiter
notFull.signalAll();
```

---

## Atomic Classes (`java.util.concurrent.atomic`)

Atomic operations without locks — use CPU compare-and-swap (CAS).

```java
AtomicInteger counter = new AtomicInteger(0);
counter.incrementAndGet();     // ++counter
counter.getAndIncrement();     // counter++
counter.addAndGet(5);          // += 5
counter.compareAndSet(5, 10);  // if current==5, set to 10; returns boolean

AtomicLong       // same for long
AtomicBoolean    // boolean
AtomicReference<V>  // object reference

// Accumulator — better throughput for frequent updates
LongAdder adder = new LongAdder();
adder.increment();
adder.sum();     // read final value

LongAccumulator acc = new LongAccumulator(Long::max, Long.MIN_VALUE);
acc.accumulate(42);
acc.get();
```

---

## CompletableFuture

Non-blocking async composition. Implements `Future<T>` and `CompletionStage<T>`.

### Creating

```java
// Already completed
CompletableFuture<String> done = CompletableFuture.completedFuture("value");

// Run async (void)
CompletableFuture<Void> f = CompletableFuture.runAsync(() -> process());

// Supply async (with value)
CompletableFuture<String> f = CompletableFuture.supplyAsync(() -> fetchData());

// With custom executor
CompletableFuture<String> f = CompletableFuture.supplyAsync(
    () -> fetchData(), executor);
```

### Transformation

```java
CompletableFuture<String> result = CompletableFuture
    .supplyAsync(() -> "hello")
    .thenApply(s -> s.toUpperCase())         // transform value — sync
    .thenApplyAsync(s -> s + "!")            // transform value — async
    .thenCompose(s ->                         // chain another future (flatMap)
        CompletableFuture.supplyAsync(() -> s + " world"));
```

### Combination

```java
// Wait for two futures, combine results
CompletableFuture<String> f1 = CompletableFuture.supplyAsync(() -> "Hello");
CompletableFuture<String> f2 = CompletableFuture.supplyAsync(() -> "World");

CompletableFuture<String> combined = f1.thenCombine(f2, (a, b) -> a + " " + b);

// Wait for both (void)
CompletableFuture<Void> both = CompletableFuture.allOf(f1, f2);

// First to complete
CompletableFuture<Object> any = CompletableFuture.anyOf(f1, f2);
```

### Error Handling

```java
CompletableFuture<String> safe = CompletableFuture
    .supplyAsync(() -> riskyOperation())
    .exceptionally(ex -> "default value")           // recover from exception
    .handle((result, ex) -> {                        // handle both success and failure
        if (ex != null) return "error: " + ex.getMessage();
        return result.toUpperCase();
    });
```

### Consuming

```java
future.thenAccept(System.out::println)   // consume value
future.thenRun(() -> System.out.println("done"))  // no value

// Block and get
String value = future.get();             // checked exception
String value = future.join();            // unchecked exception — prefer in lambdas
```

---

## Concurrent Collections

| Class | Description | Use Case |
|-------|-------------|---------|
| `ConcurrentHashMap` | Thread-safe map; segment locking | Shared map, frequency counters |
| `CopyOnWriteArrayList` | Read-optimized; copy on every write | Read-heavy, rare writes |
| `CopyOnWriteArraySet` | Same as above, set semantics | Same |
| `ConcurrentLinkedQueue` | Lock-free FIFO queue | High-throughput non-blocking |
| `LinkedBlockingQueue` | Optional-bound blocking queue | Producer-consumer |
| `ArrayBlockingQueue` | Bounded blocking queue | Bounded producer-consumer |
| `PriorityBlockingQueue` | Priority-ordered blocking queue | Priority task scheduling |

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.put("key", 1);
map.merge("key", 1, Integer::sum);         // atomic increment-like
map.compute("key", (k, v) -> v == null ? 1 : v + 1);
map.computeIfAbsent("key", k -> loadValue(k));

BlockingQueue<Task> queue = new LinkedBlockingQueue<>(100);
queue.put(task);          // blocks if full
queue.take();             // blocks if empty
queue.offer(task, 1, TimeUnit.SECONDS);  // timeout
queue.poll(1, TimeUnit.SECONDS);
```

---

## Fork/Join Framework

Designed for recursive divide-and-conquer tasks. Uses work-stealing for efficiency.

```java
import java.util.concurrent.*;

class SumTask extends RecursiveTask<Long> {
    private static final int THRESHOLD = 1000;
    private final long[] arr;
    private final int start, end;

    SumTask(long[] arr, int start, int end) {
        this.arr = arr; this.start = start; this.end = end;
    }

    @Override
    protected Long compute() {
        if (end - start <= THRESHOLD) {
            long sum = 0;
            for (int i = start; i < end; i++) sum += arr[i];
            return sum;
        }
        int mid = (start + end) / 2;
        SumTask left  = new SumTask(arr, start, mid);
        SumTask right = new SumTask(arr, mid, end);
        left.fork();                // async
        return right.compute() + left.join();  // sync + collect
    }
}

ForkJoinPool pool = ForkJoinPool.commonPool();
long total = pool.invoke(new SumTask(array, 0, array.length));
```

`RecursiveAction` — same but void (no return value).

---

## Thread Safety Patterns

### Immutable Objects

No synchronization needed — all fields final, no mutation.

### Confinement

Object only accessed by one thread — use `ThreadLocal` for thread-specific state:

```java
ThreadLocal<SimpleDateFormat> threadLocal = ThreadLocal.withInitial(
    () -> new SimpleDateFormat("yyyy-MM-dd"));

String formatted = threadLocal.get().format(new Date());
```

### Deadlock Prevention

```java
// Always acquire locks in the same order
// Use tryLock with timeout
// Minimize lock scope
// Prefer higher-level abstractions (ConcurrentHashMap over synchronized HashMap)
```
