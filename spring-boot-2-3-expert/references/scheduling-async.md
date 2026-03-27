# Spring Boot 2.3 — Scheduling & Async

## @Scheduled

### Enable scheduling

```java
@SpringBootApplication
@EnableScheduling
public class MyApplication {}
```

Or on a `@Configuration` class:
```java
@Configuration
@EnableScheduling
public class SchedulingConfig {}
```

### Scheduling patterns

```java
@Component
public class ReportScheduler {

    private static final Logger log = LoggerFactory.getLogger(ReportScheduler.class);

    // Fixed delay — N ms after previous execution ENDS
    @Scheduled(fixedDelay = 5000)
    public void cleanupExpiredSessions() {
        log.info("Cleaning expired sessions");
        // runs 5 seconds after the last run completed
    }

    // Fixed rate — every N ms from when previous execution STARTED
    // (Caution: can pile up if task takes longer than interval)
    @Scheduled(fixedRate = 60000)
    public void collectMetrics() {
        log.info("Collecting metrics");
    }

    // Initial delay before first execution
    @Scheduled(fixedRate = 30000, initialDelay = 10000)
    public void syncWithExternalService() {
        log.info("Syncing with external service");
    }

    // Cron expression
    @Scheduled(cron = "0 0 2 * * ?")    // every day at 2:00 AM
    public void generateDailyReport() {
        log.info("Generating daily report");
    }

    @Scheduled(cron = "0 */15 * * * ?")  // every 15 minutes
    public void refreshCache() {
        log.info("Refreshing cache");
    }

    // Cron from properties
    @Scheduled(cron = "${app.scheduler.report-cron:0 0 6 * * ?}")
    public void scheduledFromConfig() { }

    // Timezone
    @Scheduled(cron = "0 9 0 * * ?", zone = "America/New_York")
    public void morningTask() { }
}
```

### Cron Expression Format

```
┌────────────── second (0-59)
│  ┌─────────── minute (0-59)
│  │  ┌──────── hour (0-23)
│  │  │  ┌───── day of month (1-31)
│  │  │  │  ┌── month (1-12 or JAN-DEC)
│  │  │  │  │  ┌ day of week (0-7 or SUN-SAT, 0 and 7 = Sunday)
│  │  │  │  │  │
0  0  2  *  *  ?    → 2:00 AM daily
0  */15 * *  *  ?   → every 15 minutes
0  0  9  *  *  MON-FRI → 9 AM Mon-Fri
0  0  0  1  *  ?    → midnight on 1st of each month
0  0  12 ?  *  WED  → noon every Wednesday
```

Special characters: `*` (any), `?` (no specific value — day-of-month or day-of-week), `-` (range), `,` (list), `/` (step)

### Scheduled task configuration (thread pool)

```properties
spring.task.scheduling.pool.size=5         # ThreadPoolTaskScheduler thread count (default: 1)
spring.task.scheduling.thread-name-prefix=sched-
spring.task.scheduling.shutdown.await-termination=true
spring.task.scheduling.shutdown.await-termination-period=30s
```

Custom scheduler:
```java
@Bean
public TaskScheduler taskScheduler() {
    ThreadPoolTaskScheduler scheduler = new ThreadPoolTaskScheduler();
    scheduler.setPoolSize(5);
    scheduler.setThreadNamePrefix("scheduler-");
    scheduler.setAwaitTerminationSeconds(60);
    scheduler.setWaitForTasksToCompleteOnShutdown(true);
    return scheduler;
}
```

---

## @Async

### Enable async support

```java
@SpringBootApplication
@EnableAsync
public class MyApplication {}
```

### Basic async methods

```java
@Service
public class EmailService {

    @Async
    public void sendWelcomeEmail(User user) {
        // Runs in a separate thread
        // Method must return void or Future/CompletableFuture
        emailSender.send(user.getEmail(), "Welcome!");
    }

    @Async
    public Future<String> processAsyncWithResult(String input) {
        String result = doHeavyProcessing(input);
        return new AsyncResult<>(result);
    }

    @Async
    public CompletableFuture<UserDto> enrichUserAsync(Long userId) {
        UserDto user = userRepository.findById(userId).orElseThrow();
        UserDto enriched = externalService.enrich(user);
        return CompletableFuture.completedFuture(enriched);
    }
}
```

**Critical rules for @Async:**
1. Must be called from **outside the bean** (proxy limitation — self-invocation won't be async)
2. Must return `void`, `Future<T>`, or `CompletableFuture<T>`
3. Must be a **public** method

### Async with error handling

```java
@Async
public CompletableFuture<Void> sendEmailAsync(String address) {
    try {
        emailSender.send(address);
        return CompletableFuture.completedFuture(null);
    } catch (Exception e) {
        CompletableFuture<Void> future = new CompletableFuture<>();
        future.completeExceptionally(e);
        return future;
    }
}

// Caller handles errors:
emailService.sendEmailAsync("user@example.com")
    .exceptionally(ex -> {
        log.error("Failed to send email", ex);
        return null;
    })
    .thenAccept(v -> log.info("Email sent successfully"));
```

### Async with global exception handler

```java
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {

    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(20);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("async-");
        executor.initialize();
        return executor;
    }

    @Override
    public AsyncUncaughtExceptionHandler getAsyncUncaughtExceptionHandler() {
        return (throwable, method, params) -> {
            log.error("Async method {} threw exception", method.getName(), throwable);
        };
    }
}
```

---

## Thread Pool Configuration

### Task execution pool (for @Async)

```properties
spring.task.execution.pool.core-size=8            # Core threads (always alive)
spring.task.execution.pool.max-size=50            # Max threads
spring.task.execution.pool.queue-capacity=100     # Queue before scaling up
spring.task.execution.pool.keep-alive=60s         # Idle thread lifetime
spring.task.execution.pool.allow-core-thread-timeout=true
spring.task.execution.thread-name-prefix=task-
spring.task.execution.shutdown.await-termination=true
spring.task.execution.shutdown.await-termination-period=30s
```

### Custom executor for specific components

```java
@Configuration
@EnableAsync
public class AsyncConfig {

    @Bean("emailExecutor")
    public Executor emailExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(2);
        executor.setMaxPoolSize(5);
        executor.setQueueCapacity(20);
        executor.setThreadNamePrefix("email-");
        executor.initialize();
        return executor;
    }

    @Bean("reportExecutor")
    public Executor reportExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(3);
        executor.setMaxPoolSize(10);
        executor.setQueueCapacity(50);
        executor.setThreadNamePrefix("report-");
        executor.initialize();
        return executor;
    }
}

// Specify which executor to use
@Service
public class EmailService {

    @Async("emailExecutor")
    public CompletableFuture<Void> sendAsync(String to) {
        emailSender.send(to);
        return CompletableFuture.completedFuture(null);
    }
}

@Service
public class ReportService {

    @Async("reportExecutor")
    public CompletableFuture<byte[]> generateAsync(ReportRequest request) {
        return CompletableFuture.completedFuture(reportGenerator.generate(request));
    }
}
```

---

## Combining @Scheduled and @Async

Run scheduled tasks asynchronously (allowing multiple overlapping executions):

```java
@Component
public class DataSyncJob {

    @Async
    @Scheduled(fixedRate = 30000)
    public void syncData() {
        // Will run every 30s regardless of how long the previous run took
        // Each invocation runs in a thread pool thread
        longRunningSync();
    }
}
```

**Warning**: Without `@Async`, a `fixedRate` task that takes longer than the rate will queue up executions. With `@Async`, they can overlap — design your task to be safe for concurrent execution.

---

## Programmatic Scheduled Tasks

```java
@Component
public class DynamicScheduler {

    @Autowired
    private TaskScheduler taskScheduler;

    private ScheduledFuture<?> future;

    public void startTask(Runnable task, long intervalMs) {
        future = taskScheduler.scheduleAtFixedRate(task, intervalMs);
    }

    public void stopTask() {
        if (future != null) {
            future.cancel(false);  // don't interrupt running task
        }
    }

    public void reschedule(Runnable task, String cronExpression) {
        stopTask();
        future = taskScheduler.schedule(task, new CronTrigger(cronExpression));
    }
}
```

---

## Completable Future Composition

```java
@Service
public class UserEnrichmentService {

    @Async
    public CompletableFuture<AddressDto> fetchAddress(Long userId) { ... }

    @Async
    public CompletableFuture<PreferencesDto> fetchPreferences(Long userId) { ... }

    @Async
    public CompletableFuture<ActivityDto> fetchActivity(Long userId) { ... }

    // Combine parallel async results
    public UserProfileDto buildProfile(Long userId) throws Exception {
        CompletableFuture<AddressDto> address = fetchAddress(userId);
        CompletableFuture<PreferencesDto> prefs = fetchPreferences(userId);
        CompletableFuture<ActivityDto> activity = fetchActivity(userId);

        CompletableFuture.allOf(address, prefs, activity).join();

        return new UserProfileDto(
            address.get(),
            prefs.get(),
            activity.get()
        );
    }
}
```
