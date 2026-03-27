# Java 11 JVM and Tooling
## G1GC, ZGC, Epsilon GC, Java Flight Recorder, jlink, jdeps, jmod, jcmd, Heap Profiling

---

## Garbage Collectors in Java 11

### G1GC — Default Garbage Collector

G1 (Garbage-First) is the default since Java 9. Designed for multi-gigabyte heaps with predictable pause times.

**How it works:**
- Divides heap into equal-sized regions (~2000 regions, configurable)
- Each region is labeled: Eden, Survivor, Old, Humongous (large objects)
- Collects regions with most garbage first ("garbage-first")
- Concurrent marking runs alongside application threads

**Tuning flags:**
```bash
# Target max pause time (soft goal)
-XX:MaxGCPauseMillis=200    # default 200ms

# Heap sizes
-Xms512m -Xmx4g

# Region size (must be power of 2, 1MB–32MB)
-XX:G1HeapRegionSize=4m

# Initiate mixed GC when heap is X% full
-XX:InitiatingHeapOccupancyPercent=45   # default 45

# Parallel GC threads
-XX:ParallelGCThreads=8

# Concurrent marking threads
-XX:ConcGCThreads=4
```

**Improvements in Java 11:**
- Adaptive parallel reference processing — references processed in parallel with object marking
- Reduced footprint for remembered sets

---

### ZGC — Scalable Low-Latency GC (JEP 333, Experimental in Java 11)

ZGC (Z Garbage Collector) targets sub-10ms pause times regardless of heap size (8MB–16TB).

**Key properties:**
- Pauses scale with GC root set, NOT heap size
- Concurrent: marking, relocation, reference processing all concurrent
- Uses **colored pointers** and **load barriers** (not write barriers like G1)
- Available on Linux/x64 only in Java 11 (expanded in later releases)

**Enable:**
```bash
java -XX:+UnlockExperimentalVMOptions -XX:+UseZGC -Xmx16g MyApp
```

**Monitoring:**
```bash
# GC log output
-Xlog:gc*:file=gc.log:time,level,tags
```

**When to use ZGC (Java 11):**
- Latency-sensitive applications: financial trading, real-time processing
- Large heaps (> 4GB) where G1 pauses become unpredictable
- Acceptable: slightly higher CPU overhead (~15%)

---

### Epsilon GC — No-Op Garbage Collector (JEP 318)

Epsilon allocates memory but **never collects**. The JVM exits (OOM) when the heap is exhausted.

```bash
java -XX:+UnlockExperimentalVMOptions -XX:+UseEpsilonGC -Xmx1g MyApp
```

**Use cases:**
- **Performance testing**: eliminate GC noise from benchmarks
- **Short-lived tools**: processes that allocate but finish before heap exhausts
- **Memory pressure testing**: see how much memory your app actually needs
- **Ultra-low-latency**: when GC pauses are truly unacceptable and heap exhaustion is handled externally

---

### Other Available GCs

| GC | Flag | Status | Pauses |
|----|------|--------|--------|
| G1GC | `-XX:+UseG1GC` | Default | Configurable (200ms target) |
| ZGC | `-XX:+UseZGC` | Experimental (Java 11) | Sub-10ms |
| Epsilon | `-XX:+UseEpsilonGC` | Experimental | None (no collection) |
| Parallel GC | `-XX:+UseParallelGC` | Production | Higher throughput, longer pauses |
| Serial GC | `-XX:+UseSerialGC` | Production | Single-threaded, small heaps |
| Shenandoah | `-XX:+UseShenandoahGC` | OpenJDK only (not Oracle JDK 11) | Low pause |

**CMS (Concurrent Mark Sweep) was deprecated in Java 9 and removed in Java 14.**

---

## Java Flight Recorder (JFR, JEP 328)

JFR is a production-safe, low-overhead profiling and diagnostics tool. **Open-sourced in Java 11** (previously a commercial feature of Oracle JDK).

**Overhead:** < 1% in typical configuration.

### Recording with Command Line

```bash
# Start with JFR enabled
java -XX:StartFlightRecording=duration=60s,filename=profile.jfr,settings=profile MyApp

# Duration recording with custom settings
java -XX:StartFlightRecording=\
  duration=120s,\
  filename=myapp-$(date +%Y%m%d).jfr,\
  settings=default,\
  name=MyRecording \
  MyApp
```

### Recording with `jcmd`

```bash
# List JVM processes
jcmd

# Start recording
jcmd <pid> JFR.start name=MyRec duration=30s filename=out.jfr

# Check status
jcmd <pid> JFR.check

# Dump now (save what's been recorded so far)
jcmd <pid> JFR.dump name=MyRec filename=out.jfr

# Stop and save
jcmd <pid> JFR.stop name=MyRec filename=out.jfr
```

### Recording via API (Programmatic)

```java
import jdk.jfr.*;

// One-time recording
Configuration config = Configuration.getConfiguration("profile");
try (Recording recording = new Recording(config)) {
    recording.start();
    // ... application work ...
    recording.stop();
    recording.dump(Path.of("output.jfr"));
}

// Custom event
@Label("Request Processed")
@Category("Application")
@StackTrace(false)
class RequestEvent extends Event {
    @Label("URL") String url;
    @Label("Status") int status;
    @Label("Duration ms") long durationMs;
}

RequestEvent event = new RequestEvent();
event.begin();
// process request
event.url = request.getUrl();
event.status = 200;
event.durationMs = elapsed;
event.commit();  // only recorded if event is enabled
```

### Reading JFR Files

```java
import jdk.jfr.consumer.*;

try (RecordingFile file = new RecordingFile(Path.of("out.jfr"))) {
    while (file.hasMoreEvents()) {
        RecordedEvent event = file.readEvent();
        System.out.println(event.getEventType().getName());
        // Access fields
        if (event.getEventType().getName().equals("jdk.GarbageCollection")) {
            long duration = event.getDuration().toMillis();
        }
    }
}
```

JFR files are analyzed with **Java Mission Control (JMC)** — a GUI tool downloaded separately.

---

## Low-Overhead Heap Profiling (JEP 331)

Java 11 adds a JVMTI API for sampling object allocations with configurable sampling rate — enabling heap profiling with ~5% overhead vs 100%+ for full instrumentation.

Used by profiling tools (async-profiler, JMC, YourKit). No direct Java API for end users.

---

## Dynamic Class-File Constants (JEP 309)

Adds a new constant pool form `CONSTANT_Dynamic` — enables efficient encoding of new language features and reduces bytecode size. Used by compilers; transparent to Java developers.

---

## Tooling

### `jlink` — Custom Runtime Images

Build minimal JREs with only the modules your app needs:

```bash
# Identify needed modules
jdeps --print-module-deps myapp.jar

# Build custom runtime
jlink \
  --module-path $JAVA_HOME/jmods:mods \
  --add-modules com.example.myapp,java.net.http,java.sql \
  --output dist/myapp-runtime \
  --launcher run=com.example.myapp/com.example.Main \
  --strip-debug \
  --no-header-files \
  --no-man-pages \
  --compress=2

# Run
dist/myapp-runtime/bin/run
```

Result is typically 25–80 MB vs. 200+ MB full JDK.

### `jdeps` — Dependency Analysis

```bash
# Module dependencies
jdeps --module-path mods myapp.jar

# Summary view
jdeps -summary myapp.jar

# Check for internal JDK API usage
jdeps --jdk-internals myapp.jar
# Flags usage of sun.*, com.sun.*, jdk.internal.* — should be eliminated

# Generate module-info.java for an automatic module
jdeps --generate-module-info ./output mylib.jar

# Show required modules for jlink
jdeps --print-module-deps myapp.jar

# API-only (skip private/internal)
jdeps --api-only myapp.jar
```

### `jmod` — JMOD Files

JMOD is a file format for packaging modules (used by JDK itself):

```bash
# Create a JMOD
jmod create \
  --class-path myclasses \
  --cmds mybinaries \
  --config myconfig \
  com.example.mymodule.jmod

# List contents
jmod list $JAVA_HOME/jmods/java.base.jmod

# Describe module
jmod describe $JAVA_HOME/jmods/java.net.http.jmod

# Extract
jmod extract java.base.jmod
```

JMOD is primarily for JDK/platform distribution. Most application modules use JARs.

### `jcmd` — JVM Diagnostics

```bash
# List running JVMs
jcmd

# VM info
jcmd <pid> VM.info
jcmd <pid> VM.version
jcmd <pid> VM.flags

# Memory
jcmd <pid> VM.native_memory      # native memory tracking
jcmd <pid> GC.run                # force GC
jcmd <pid> GC.heap_info          # heap statistics
jcmd <pid> GC.heap_dump filename=/tmp/heap.hprof

# Threads
jcmd <pid> Thread.print          # thread dump

# Classes
jcmd <pid> VM.class_stats        # class statistics

# JFR (see above)
jcmd <pid> JFR.start ...
```

### `jstack` — Thread Dumps

```bash
jstack <pid>             # print all threads
jstack -l <pid>          # include lock info
```

### `jmap` — Heap and Class Statistics

```bash
jmap -heap <pid>         # heap summary
jmap -histo <pid>        # object histogram (class → instance count → bytes)
jmap -dump:format=b,file=heap.hprof <pid>   # heap dump
```

### `jstat` — JVM Statistics

```bash
jstat -gc <pid> 1000     # GC stats every 1 second
jstat -gcutil <pid>      # GC utilization percentages
jstat -class <pid>       # class loading stats
jstat -compiler <pid>    # JIT compiler stats
```

---

## JVM Flags Reference

```bash
# Heap
-Xms<size>                 # initial heap size
-Xmx<size>                 # max heap size
-Xss<size>                 # thread stack size (default 512k–1m)
-XX:MetaspaceSize=<size>   # initial metaspace size
-XX:MaxMetaspaceSize=<size> # max metaspace size

# GC Logging (Java 11 unified logging)
-Xlog:gc                           # basic GC log to stdout
-Xlog:gc*:file=gc.log:time,level,tags  # detailed to file
-Xlog:gc::time,uptime,level,tags   # with timestamps

# JIT
-XX:+PrintCompilation      # log JIT compilations
-XX:-TieredCompilation     # disable tiered compilation (use C2 only)

# Diagnostics
-XX:+HeapDumpOnOutOfMemoryError    # dump heap on OOM
-XX:HeapDumpPath=/tmp/heap.hprof
-XX:+PrintGCApplicationStoppedTime  # print STW pause times
-XX:+PrintSafepointStatistics

# Native memory tracking
-XX:NativeMemoryTracking=summary   # or detail
```

---

## Removed in Java 11

| Removed | Notes |
|---------|-------|
| Java Plugin (browser applets) | JavaFX WebStart removed; applets dead |
| Java WebStart / JNLP | Use platform installers instead |
| `javah` tool | Use `javac -h` instead |
| Java EE modules | See modules.md — add Maven deps |
| Nashorn JavaScript engine | Deprecated (JEP 335); removed in Java 15 |

## JRE No Longer Shipped

Java 11 does not include a separate JRE download. Use `jlink` to produce a custom runtime or distribute the full JDK.
