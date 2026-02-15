# Signals

## Table of Contents
- [Signal Fundamentals](#signal-fundamentals)
- [Real-Time Signals](#real-time-signals)
- [Signal Sets and Masks](#signal-sets-and-masks)
- [Sending Signals](#sending-signals)
- [Synchronous Signal Handling](#synchronous-signal-handling)
- [signalfd (Linux)](#signalfd-linux)
- [Signals and Threads](#signals-and-threads)
- [Async-Signal-Safe Functions](#async-signal-safe-functions)
- [Signal Handling Patterns](#signal-handling-patterns)

## Signal Fundamentals

Signals are software interrupts. Two categories:

**Standard signals** (1–31): Non-queuing. If the same signal arrives while one is pending, it's merged (you lose signals). No payload.

**Real-time signals** (`SIGRTMIN` to `SIGRTMAX`): Queuing. Multiple instances are delivered. Carry a `sigval` payload. Delivered in priority order (lowest signal number first).

### Signal disposition
```c
#include <signal.h>

// Modern — use sigaction, never signal():
struct sigaction sa = {
    .sa_sigaction = handler_func,
    .sa_flags = SA_SIGINFO | SA_RESTART,
};
sigemptyset(&sa.sa_mask);
sigaction(SIGRTMIN, &sa, NULL);

// Handler with siginfo:
void handler_func(int sig, siginfo_t *info, void *ucontext) {
    // info->si_value  — payload from sigqueue
    // info->si_pid    — sender PID
    // info->si_uid    — sender UID
    // info->si_code   — signal source (SI_USER, SI_TIMER, SI_QUEUE, etc.)
}
```

### SA_SIGINFO flag
Without `SA_SIGINFO`, the handler is `void handler(int sig)`. With it, you get the full `siginfo_t` and can receive payloads. **Always use `SA_SIGINFO` for RT signals.**

## Real-Time Signals

```c
// Range:
int first_rt = SIGRTMIN;  // typically 34 on Linux
int last_rt  = SIGRTMAX;  // typically 64 on Linux
int num_rt   = SIGRTMAX - SIGRTMIN + 1;  // typically 31

// Use offsets from SIGRTMIN (values may differ across platforms):
#define SIG_TIMER_EXPIRED  (SIGRTMIN + 0)
#define SIG_DATA_READY     (SIGRTMIN + 1)
#define SIG_SHUTDOWN       (SIGRTMIN + 2)
```

### Properties
- **Queued**: Every `sigqueue` call is delivered (up to `RLIMIT_SIGPENDING`)
- **Ordered**: Lower signal numbers delivered first among pending RT signals
- **Payload**: Each carries a `union sigval` (integer or pointer)
- **No default action**: Default is terminate process

### Queue limits
```c
// Check and set queue limit:
struct rlimit rl;
getrlimit(RLIMIT_SIGPENDING, &rl);  // default often 128000+

// System limit: /proc/sys/kernel/rtsig-max (older kernels)
```

## Signal Sets and Masks

```c
sigset_t set;

sigemptyset(&set);              // clear all
sigfillset(&set);               // set all
sigaddset(&set, SIGRTMIN);      // add one
sigdelset(&set, SIGRTMIN);      // remove one
sigismember(&set, SIGRTMIN);    // test membership

// Block signals (thread-level):
pthread_sigmask(SIG_BLOCK, &set, &old_set);    // add to mask
pthread_sigmask(SIG_UNBLOCK, &set, &old_set);  // remove from mask
pthread_sigmask(SIG_SETMASK, &set, &old_set);  // replace mask

// Process-level (only in single-threaded programs):
sigprocmask(SIG_BLOCK, &set, &old_set);
```

## Sending Signals

### sigqueue — send with payload
```c
union sigval val;
val.sival_int = 42;
// or: val.sival_ptr = data_ptr;  // careful with processes — pointer invalid in receiver

sigqueue(target_pid, SIGRTMIN, val);
```

### kill — traditional (no payload, no queuing guarantee)
```c
kill(pid, SIGRTMIN);      // to specific process
kill(0, SIGRTMIN);        // to all processes in sender's process group
kill(-pgid, SIGRTMIN);    // to all processes in group pgid
```

### pthread_kill — to specific thread
```c
pthread_kill(tid, SIGRTMIN);  // no payload
```

### tgkill — Linux, to specific thread in specific process
```c
#include <sys/syscall.h>
syscall(SYS_tgkill, pid, tid, SIGRTMIN);
```

## Synchronous Signal Handling

Instead of async signal handlers, block the signal and wait for it synchronously. **This is the preferred approach for RT.**

### sigwaitinfo / sigtimedwait
```c
sigset_t set;
sigemptyset(&set);
sigaddset(&set, SIGRTMIN);
sigaddset(&set, SIGRTMIN + 1);

// Block these signals first:
pthread_sigmask(SIG_BLOCK, &set, NULL);

// Wait for any signal in the set:
siginfo_t info;
int sig = sigwaitinfo(&set, &info);
// sig = signal number
// info.si_value = payload
// info.si_pid = sender
// info.si_code = source

// With timeout:
struct timespec timeout = { .tv_sec = 1 };
sig = sigtimedwait(&set, &info, &timeout);
if (sig == -1 && errno == EAGAIN) { /* timed out */ }
```

### sigwait (simpler, no siginfo)
```c
int sig;
sigwait(&set, &sig);
// Only returns signal number — no payload
```

### Dedicated signal-handling thread pattern
```c
// In main, before creating any threads:
sigset_t all_rt;
sigemptyset(&all_rt);
for (int i = SIGRTMIN; i <= SIGRTMAX; i++)
    sigaddset(&all_rt, i);
pthread_sigmask(SIG_BLOCK, &all_rt, NULL);
// All subsequently created threads inherit this mask

// Signal-handling thread:
void *signal_thread(void *arg) {
    sigset_t set;
    sigemptyset(&set);
    sigaddset(&set, SIGRTMIN);
    sigaddset(&set, SIGRTMIN + 1);

    while (running) {
        siginfo_t info;
        int sig = sigwaitinfo(&set, &info);
        switch (sig) {
        case /* SIGRTMIN */: handle_timer(&info); break;
        case /* SIGRTMIN+1 */: handle_data(&info); break;
        }
    }
    return NULL;
}
```

## signalfd (Linux)

Convert signals into file descriptor events — integrates with `epoll`/`poll`/`io_uring`:

```c
#include <sys/signalfd.h>

sigset_t mask;
sigemptyset(&mask);
sigaddset(&mask, SIGRTMIN);
sigaddset(&mask, SIGINT);

// Block signals first (so they go to signalfd, not default handler):
pthread_sigmask(SIG_BLOCK, &mask, NULL);

int sfd = signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);

// Read signal info:
struct signalfd_siginfo info;
ssize_t n = read(sfd, &info, sizeof(info));
if (n == sizeof(info)) {
    // info.ssi_signo  — signal number
    // info.ssi_pid    — sender PID
    // info.ssi_int    — sigval integer (from sigqueue)
    // info.ssi_ptr    — sigval pointer
}

// With epoll:
struct epoll_event ev = { .events = EPOLLIN, .data.fd = sfd };
epoll_ctl(epfd, EPOLL_CTL_ADD, sfd, &ev);
```

### signalfd vs sigwaitinfo
| Feature | signalfd | sigwaitinfo |
|---------|----------|-------------|
| Event loop integration | Yes (epoll) | No (blocking call) |
| Multiple event sources | Yes (mux with timers, sockets) | Dedicated thread needed |
| Portability | Linux only | POSIX |
| Overhead | Slightly higher | Minimal |

## Signals and Threads

### Signal delivery rules
1. **Process-directed signals** (e.g., `kill(pid, sig)`) are delivered to any thread that doesn't have the signal blocked
2. **Thread-directed signals** (e.g., `pthread_kill(tid, sig)`) are delivered to that specific thread
3. **Fault signals** (`SIGSEGV`, `SIGBUS`, `SIGFPE`, `SIGILL`) are delivered to the thread that caused the fault

### The POSIX threads + signals strategy
Signals and threads are notoriously difficult to combine. The clean approach (Butenhof):

1. **Block all signals** in `main()` before creating any threads
2. **Create one dedicated signal-handling thread** that calls `sigwaitinfo` or reads from `signalfd`
3. **All other threads** inherit the blocked mask and never deal with signals

```c
int main(void) {
    // Block everything:
    sigset_t all;
    sigfillset(&all);
    sigdelset(&all, SIGSEGV);  // keep fault signals
    sigdelset(&all, SIGBUS);
    sigdelset(&all, SIGABRT);
    pthread_sigmask(SIG_BLOCK, &all, NULL);

    // Create signal handler thread first:
    pthread_create(&sig_thread, NULL, signal_handler, NULL);

    // Create worker threads (inherit blocked mask):
    pthread_create(&worker, NULL, worker_func, NULL);
    // ...
}
```

## Async-Signal-Safe Functions

Only these functions (and a few others) may be called from a signal handler. Everything else is undefined behavior:

`_exit`, `abort`, `accept`, `access`, `alarm`, `bind`, `chdir`, `chmod`, `chown`, `close`, `connect`, `dup`, `dup2`, `execve`, `fcntl`, `fork`, `fstat`, `getpid`, `kill`, `link`, `listen`, `lseek`, `mkdir`, `open`, `pause`, `pipe`, `poll`, `read`, `recv`, `rename`, `rmdir`, `select`, `send`, `shutdown`, `sigaction`, `signal`, `sigprocmask`, `sleep`, `socket`, `stat`, `time`, `umask`, `unlink`, `wait`, `waitpid`, `write`

**NOT safe**: `printf`, `malloc`, `free`, `pthread_mutex_lock`, `syslog`, `fprintf`, `snprintf` — virtually everything useful.

**This is why synchronous signal handling (`sigwaitinfo`, `signalfd`) is vastly preferred** — in a normal thread context, you can call any function.

## Signal Handling Patterns

### Self-pipe trick (portable, pre-signalfd)
```c
static int pipe_fds[2];

void handler(int sig) {
    int saved = errno;
    write(pipe_fds[1], &sig, 1);  // async-signal-safe
    errno = saved;
}

void setup(void) {
    pipe2(pipe_fds, O_NONBLOCK | O_CLOEXEC);
    // Add pipe_fds[0] to epoll
    // Register handler with sigaction
}
```

Modern replacement: `signalfd` (Linux) or `kqueue` (macOS/BSD).

### Graceful shutdown pattern
```c
static volatile sig_atomic_t shutdown_requested = 0;

void shutdown_handler(int sig) {
    shutdown_requested = 1;
}

// In RT loop:
while (!shutdown_requested) {
    do_work();
    clock_nanosleep(...);
}
cleanup();
```

For multithreaded programs, prefer `signalfd` + `eventfd` to broadcast shutdown to all threads via epoll.
