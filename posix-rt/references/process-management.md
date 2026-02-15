# Process Management

## Table of Contents
- [fork](#fork)
- [exec Family](#exec-family)
- [posix_spawn](#posix_spawn)
- [Process Termination and Waiting](#process-termination-and-waiting)
- [Process Groups and Sessions](#process-groups-and-sessions)
- [fork and RT Considerations](#fork-and-rt-considerations)
- [fork and Threads](#fork-and-threads)

## fork

```c
#include <unistd.h>

pid_t pid = fork();
if (pid == -1) {
    perror("fork");
} else if (pid == 0) {
    // Child process
    // Has copy of parent's memory (copy-on-write)
    // Has copies of parent's file descriptors
    // Has ONE thread (the calling thread)
} else {
    // Parent process, pid = child's PID
}
```

### What is inherited by the child
- Memory mappings (copy-on-write)
- Open file descriptors (shared file offsets!)
- Signal dispositions
- Environment variables
- UID, GID, process group, session
- Current working directory
- Resource limits
- Memory locks (`mlock`) — NOT inherited (child's pages are unlocked)
- CPU affinity

### What is NOT inherited
- PID (child gets new PID)
- Pending signals (cleared in child)
- File locks (`flock`) — NOT inherited
- Timers (POSIX timers not inherited)
- Async I/O operations — NOT inherited
- Memory locks — child pages are NOT locked (must re-call `mlockall`)
- Other threads — only the calling thread exists in child

### vfork
```c
pid_t pid = vfork();
// Child shares parent's address space until exec or _exit
// Parent is suspended until child calls exec or _exit
// Child must NOT modify any data, call functions, or return
// Only use: vfork() + immediate exec()
```

Generally avoid `vfork` — `posix_spawn` is safer and achieves the same performance goal.

## exec Family

Replace the current process image:

```c
// Null-terminated argument list:
execl("/bin/ls", "ls", "-la", NULL);
execlp("ls", "ls", "-la", NULL);        // searches PATH
execle("/bin/ls", "ls", "-la", NULL, envp);  // custom environment

// Argument array:
char *argv[] = {"ls", "-la", NULL};
execv("/bin/ls", argv);
execvp("ls", argv);                     // searches PATH
execvpe("ls", argv, envp);              // searches PATH + custom env

// fd-based (avoids TOCTOU):
int fd = open("/bin/ls", O_RDONLY);
fexecve(fd, argv, environ);
```

### exec with close-on-exec
Avoid leaking file descriptors to child processes:
```c
int fd = open(path, O_RDONLY | O_CLOEXEC);
// Or after open:
fcntl(fd, F_SETFD, FD_CLOEXEC);

// All fds with CLOEXEC are automatically closed on exec
```

## posix_spawn

Efficient process creation — combines fork + exec with pre-configured attributes:

```c
#include <spawn.h>

pid_t pid;
char *argv[] = {"worker", "--mode=fast", NULL};

// Attributes (scheduling, process group, signals, etc.):
posix_spawnattr_t attr;
posix_spawnattr_init(&attr);

// Set scheduling policy:
posix_spawnattr_setflags(&attr,
    POSIX_SPAWN_SETSCHEDPOLICY | POSIX_SPAWN_SETSCHEDPARAM |
    POSIX_SPAWN_SETPGROUP | POSIX_SPAWN_SETSIGDEF |
    POSIX_SPAWN_SETSIGMASK);

struct sched_param sp = { .sched_priority = 50 };
posix_spawnattr_setschedpolicy(&attr, SCHED_FIFO);
posix_spawnattr_setschedparam(&attr, &sp);

// Reset signal mask for child:
sigset_t empty;
sigemptyset(&empty);
posix_spawnattr_setsigmask(&attr, &empty);

// File actions (redirect I/O, close fds):
posix_spawn_file_actions_t actions;
posix_spawn_file_actions_init(&actions);
posix_spawn_file_actions_addopen(&actions, STDOUT_FILENO,
    "/var/log/worker.log", O_WRONLY | O_CREAT | O_TRUNC, 0644);
posix_spawn_file_actions_addclose(&actions, unused_fd);

// Spawn:
int ret = posix_spawn(&pid, "/usr/local/bin/worker",
                      &actions, &attr, argv, environ);
if (ret != 0) {
    fprintf(stderr, "posix_spawn: %s\n", strerror(ret));
}

posix_spawnattr_destroy(&attr);
posix_spawn_file_actions_destroy(&actions);
```

### posix_spawn flags

| Flag | Effect |
|------|--------|
| `POSIX_SPAWN_SETPGROUP` | Set process group |
| `POSIX_SPAWN_SETSIGMASK` | Set signal mask |
| `POSIX_SPAWN_SETSIGDEF` | Reset specified signals to default |
| `POSIX_SPAWN_SETSCHEDPOLICY` | Set scheduling policy |
| `POSIX_SPAWN_SETSCHEDPARAM` | Set scheduling parameters |
| `POSIX_SPAWN_RESETIDS` | Reset effective UID/GID |
| `POSIX_SPAWN_SETSID` | Create new session (POSIX.1-2024) |

### posix_spawn vs fork+exec
- **posix_spawn**: No address space copy, no risk of async-signal-unsafe functions between fork and exec, potentially uses `vfork` internally
- **fork+exec**: More flexible (arbitrary code between fork and exec), but dangerous in multithreaded programs

## Process Termination and Waiting

### Termination
```c
exit(status);     // flush stdio, run atexit handlers, clean up
_exit(status);    // immediate exit, no cleanup
_Exit(status);    // C99 equivalent of _exit

// In a forked child, prefer _exit() to avoid flushing parent's stdio buffers
```

### Waiting
```c
#include <sys/wait.h>

// Wait for any child:
int status;
pid_t child = wait(&status);

// Wait for specific child:
pid_t child = waitpid(pid, &status, 0);
// Options: WNOHANG (non-blocking), WUNTRACED (stopped children)

// Examine status:
if (WIFEXITED(status))
    printf("exited with %d\n", WEXITSTATUS(status));
if (WIFSIGNALED(status))
    printf("killed by signal %d\n", WTERMSIG(status));
if (WIFSTOPPED(status))
    printf("stopped by signal %d\n", WSTOPSIG(status));

// waitid — more flexible:
siginfo_t info;
waitid(P_PID, pid, &info, WEXITED | WSTOPPED | WNOHANG);
```

### SIGCHLD handling
```c
// Avoid zombies — reap children asynchronously:
struct sigaction sa = {
    .sa_handler = SIG_DFL,
    .sa_flags = SA_NOCLDWAIT,  // auto-reap children
};
sigaction(SIGCHLD, &sa, NULL);

// Or handle explicitly in signal thread:
// Block SIGCHLD, use sigwaitinfo, call waitpid in loop
```

## Process Groups and Sessions

```c
// Get/set process group:
pid_t pgid = getpgrp();           // current process group
setpgid(pid, pgid);               // set pid's group to pgid
setpgid(0, 0);                    // create new group with self as leader

// Sessions:
pid_t sid = setsid();             // create new session (must not be group leader)
pid_t sid = getsid(pid);          // get session ID
```

### Daemon creation pattern
```c
void daemonize(void) {
    pid_t pid = fork();
    if (pid > 0) _exit(0);        // parent exits
    if (pid < 0) _exit(1);

    setsid();                      // new session

    pid = fork();                  // fork again to prevent terminal acquisition
    if (pid > 0) _exit(0);
    if (pid < 0) _exit(1);

    chdir("/");
    umask(0);

    // Redirect stdio:
    close(STDIN_FILENO);
    close(STDOUT_FILENO);
    close(STDERR_FILENO);
    open("/dev/null", O_RDONLY);   // stdin
    open("/var/log/daemon.log", O_WRONLY | O_CREAT | O_APPEND, 0644);
    dup(1);                        // stderr → same as stdout
}
```

## fork and RT Considerations

### Memory locking
After `fork()`, the child's memory is NOT locked even if the parent called `mlockall`. The child must call `mlockall` again.

### Scheduling
The child inherits the parent's scheduling policy and priority. If the parent is `SCHED_FIFO` priority 80, so is the child.

### CPU affinity
Inherited — child runs on same CPU set as parent.

### SCHED_DEADLINE
`fork()` is **not allowed** with `SCHED_DEADLINE`. The `fork` syscall returns `EAGAIN`.

### Timers
POSIX timers created with `timer_create` are NOT inherited by the child. The child must create its own timers.

## fork and Threads

**Critical**: `fork()` in a multithreaded program is dangerous.

After `fork()`, the child has only ONE thread (the one that called `fork`). All other threads vanish. If any of those threads held a mutex, that mutex is **permanently locked** in the child.

### The only safe pattern after fork in multithreaded code
```c
pid_t pid = fork();
if (pid == 0) {
    // Child: IMMEDIATELY call exec or _exit
    // Do NOT:
    //   - Call malloc, printf, or any function that uses locks
    //   - Access shared data structures
    //   - Do anything except exec or _exit
    execvp(program, argv);
    _exit(127);
}
```

### pthread_atfork
Register handlers to prepare for fork:
```c
pthread_atfork(prepare, parent, child);
// prepare: called in parent before fork (lock all mutexes)
// parent:  called in parent after fork (unlock all mutexes)
// child:   called in child after fork (unlock all mutexes)
```

This helps but doesn't fully solve the problem — you can't guarantee all libraries register their handlers. **Prefer `posix_spawn` over `fork` in multithreaded programs.**
