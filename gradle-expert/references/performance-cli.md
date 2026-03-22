# Performance CLI Reference

See also: [Performance Concepts](performance-concepts.md)

```bash
# ── Build Cache ──────────────────────────────────────────────────────────────

# Enable build cache for one run (overrides gradle.properties)
./gradlew build --build-cache

# Disable build cache for one run
./gradlew build --no-build-cache

# Force all tasks to re-run, ignoring UP-TO-DATE checks and cache
./gradlew build --rerun-tasks

# ── Configuration Cache ───────────────────────────────────────────────────────

# Enable configuration cache for one run
./gradlew build --configuration-cache

# Disable configuration cache for one run
./gradlew build --no-configuration-cache

# Warn on compatibility problems instead of failing (lenient mode)
./gradlew build --configuration-cache --configuration-cache-problems=warn

# Check configuration cache compatibility for the help task (fast)
./gradlew help --configuration-cache

# Gradle 9.1: read-only CI mode (never writes cache; only reads from shared store)
./gradlew build --configuration-cache --read-only-configuration-cache-store

# View the configuration cache compatibility HTML report
open build/reports/configuration-cache/*/configuration-cache-report.html

# ── Daemon ───────────────────────────────────────────────────────────────────

# List all running Gradle daemons (this version)
./gradlew --status

# Stop all daemons for this Gradle version
./gradlew --stop

# Stop all Gradle daemons of all versions
gradle --stop

# Run without daemon (use for CI baseline comparisons or daemon debugging)
./gradlew build --no-daemon

# ── Parallel Execution ────────────────────────────────────────────────────────

# Enable parallel task execution for one run
./gradlew build --parallel

# Limit the number of parallel worker threads
./gradlew build --parallel --max-workers=4

# ── Profiling and Diagnostics ─────────────────────────────────────────────────

# HTML profile report — no network, stored locally
./gradlew build --profile
open build/reports/profile/profile-*.html

# Build scan — detailed online analysis (free at scans.gradle.com)
./gradlew build --scan

# Verbose info — shows UP-TO-DATE reasons, cache keys, input/output details
./gradlew build --info

# Very verbose debug output (pipe through grep to filter)
./gradlew build --debug 2>&1 | grep "Task :compileJava"

# Print full stack trace on build failure
./gradlew build --stacktrace

# Dry run: show which tasks would execute without running them
./gradlew build --dry-run
./gradlew build -m            # short form

# ── Incremental Build Diagnostics ────────────────────────────────────────────

# Why was a task not UP-TO-DATE? (look for "is not up-to-date" and "Input property" lines)
./gradlew build --info 2>&1 | grep -E "is not up-to-date|Input property|Output property"

# Show input/output fingerprint details
./gradlew :compileJava --info 2>&1 | grep -i "fingerprint\|snapshot"

# Show task execution reason (Gradle 8+)
./gradlew build --info 2>&1 | grep "Task .* is not up-to-date"

# Which tasks ran vs were restored from cache vs skipped?
./gradlew build | grep -E "UP-TO-DATE|FROM-CACHE|SKIPPED|EXECUTED|> Task"

# ── File System Watching ─────────────────────────────────────────────────────

# Enable file system watching for this run (usually enabled by default)
./gradlew build -Dorg.gradle.vfs.watch=true

# Show verbose file system watching events (useful for debugging missed changes)
./gradlew build -Dorg.gradle.vfs.verbose=true

# ── Dependency Resolution Performance ────────────────────────────────────────

# Force fresh resolution of all dynamic versions and snapshots (bypasses cache)
./gradlew build --refresh-dependencies

# Show how long dependency resolution took (look for "Resolving" lines)
./gradlew dependencies --info 2>&1 | grep -i "resolv"

# ── Cache Management ──────────────────────────────────────────────────────────

# Clean local build cache (frees disk space; next build will miss cache)
rm -rf ~/.gradle/caches/build-cache/

# Clean the entire Gradle caches directory (nuclear option; slow next build)
rm -rf ~/.gradle/caches/

# Gradle wrapper cache (cached Gradle distributions)
ls ~/.gradle/wrapper/dists/

# ── gradle.properties Quick-Set Performance Flags ─────────────────────────────

# Add to project gradle.properties (committed to VCS for team):
cat >> gradle.properties << 'EOF'
org.gradle.daemon=true
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configuration-cache=true
org.gradle.configuration-cache.problems=warn
org.gradle.jvmargs=-Xmx4g -XX:+HeapDumpOnOutOfMemoryError -XX:MaxMetaspaceSize=512m -XX:+UseParallelGC
org.gradle.workers.max=8
org.gradle.vfs.watch=true
kotlin.incremental=true
kotlin.daemon.jvm.options=-Xmx2g
EOF

# ── Quick Reference: Flag Summary ─────────────────────────────────────────────

# Flag                                  Effect
# --build-cache                         Enable task output caching for this run
# --no-build-cache                      Disable task output caching for this run
# --configuration-cache                 Cache and reuse the task graph
# --no-configuration-cache              Disable configuration cache for this run
# --configuration-cache-problems=warn   Warn instead of fail on cache problems
# --parallel                            Run independent tasks concurrently
# --max-workers=N                       Number of parallel worker threads
# --no-daemon                           Run without the background daemon
# --profile                             Generate HTML build profile report
# --scan                                Upload build scan to scans.gradle.com
# --info                                Informational logging (UP-TO-DATE reasons)
# --debug                               Debug logging (very verbose)
# --stacktrace                          Print full stack trace on error
# --rerun-tasks                         Force all tasks to re-run
# -m / --dry-run                        Show tasks without executing
# --refresh-dependencies                Ignore cached dependency resolution results
# --status                              List running Gradle daemons
# --stop                                Stop all running Gradle daemons
```
