# Message Queues

## Table of Contents
- [Overview](#overview)
- [Creating and Opening](#creating-and-opening)
- [Sending and Receiving](#sending-and-receiving)
- [Message Priority](#message-priority)
- [Queue Attributes](#queue-attributes)
- [Notification](#notification)
- [Comparison with Pipes and SysV](#comparison-with-pipes-and-sysv)
- [Practical Patterns](#practical-patterns)

## Overview

POSIX message queues provide prioritized, kernel-persistent message passing between threads or processes. Key properties:
- Messages are discrete units (not byte streams like pipes)
- Messages have priority — highest priority delivered first
- Queues have a name (`/name`) and persist until explicitly removed
- Can notify via signal or thread when a message arrives on an empty queue

Headers and linking:
```c
#include <mqueue.h>
#include <fcntl.h>     // O_CREAT, O_RDWR, etc.
#include <sys/stat.h>  // mode_t

// Link with: -lrt (older glibc)
```

## Creating and Opening

```c
// Create or open:
struct mq_attr attr = {
    .mq_flags   = 0,          // 0 or O_NONBLOCK
    .mq_maxmsg  = 10,         // max messages in queue
    .mq_msgsize = 256,        // max message size in bytes
    .mq_curmsgs = 0,          // current messages (read-only)
};

mqd_t mq = mq_open("/myqueue", O_CREAT | O_RDWR, 0660, &attr);
if (mq == (mqd_t)-1) {
    perror("mq_open");
}

// Open existing (no creation):
mqd_t mq = mq_open("/myqueue", O_RDONLY);

// Non-blocking mode:
mqd_t mq = mq_open("/myqueue", O_RDWR | O_NONBLOCK, 0660, &attr);
```

### Naming rules
- Must start with `/`
- No additional `/` after the first
- Implemented as files in `/dev/mqueue/` on Linux
- Name length limited by `NAME_MAX`

### Closing and removing
```c
mq_close(mq);              // close descriptor (like close(fd))
mq_unlink("/myqueue");      // remove the queue (like unlink)
// Queue is destroyed when last reference is closed after unlink
```

### System limits (Linux)
```bash
# /proc/sys/fs/mqueue/
msg_max         # max messages per queue (default 10)
msgsize_max     # max message size (default 8192)
queues_max      # max queues per user (default 256)

# Override at open time (requires CAP_SYS_RESOURCE for exceeding defaults):
# attr.mq_maxmsg and attr.mq_msgsize
```

## Sending and Receiving

### Send
```c
const char *msg = "sensor data";
unsigned int priority = 5;  // 0 = lowest

int ret = mq_send(mq, msg, strlen(msg), priority);
// Blocks if queue is full (unless O_NONBLOCK)
// Returns 0 on success, -1 on error

// Timed:
struct timespec abstime;
clock_gettime(CLOCK_REALTIME, &abstime);
abstime.tv_sec += 1;
ret = mq_timedsend(mq, msg, strlen(msg), priority, &abstime);
if (ret == -1 && errno == ETIMEDOUT) { /* queue still full */ }
```

### Receive
```c
char buf[attr.mq_msgsize];  // MUST be >= mq_msgsize
unsigned int prio;

ssize_t len = mq_receive(mq, buf, sizeof(buf), &prio);
// Returns message length, fills prio with message priority
// Blocks if queue is empty (unless O_NONBLOCK)
// Always returns the HIGHEST priority message

// Timed:
len = mq_timedreceive(mq, buf, sizeof(buf), &prio, &abstime);
```

**Critical**: The buffer passed to `mq_receive` must be at least `mq_msgsize` bytes, or the call fails with `EMSGSIZE`.

## Message Priority

- Priority is an `unsigned int`, 0 to `MQ_PRIO_MAX - 1` (at least 32 on Linux)
- Higher numeric value = higher priority
- `mq_receive` always returns the oldest message at the highest priority level
- Within the same priority, messages are FIFO

### RT pattern — priority mapping
```c
// Map thread priorities to message priorities:
#define MSG_PRIO_CRITICAL  31
#define MSG_PRIO_HIGH      20
#define MSG_PRIO_NORMAL    10
#define MSG_PRIO_LOW        0
```

## Queue Attributes

```c
// Get current attributes:
struct mq_attr attr;
mq_getattr(mq, &attr);
// attr.mq_flags   — O_NONBLOCK or 0
// attr.mq_maxmsg  — max capacity
// attr.mq_msgsize — max message size
// attr.mq_curmsgs — current number of messages

// Set attributes (only mq_flags can be changed after creation):
struct mq_attr new_attr = { .mq_flags = O_NONBLOCK };
mq_setattr(mq, &new_attr, &old_attr);
```

## Notification

Request notification when a message arrives on an **empty** queue:

### Signal notification
```c
struct sigevent sev = {
    .sigev_notify = SIGEV_SIGNAL,
    .sigev_signo = SIGRTMIN,
    .sigev_value.sival_ptr = &mq,
};
mq_notify(mq, &sev);

// IMPORTANT: notification is one-shot!
// Must re-register after each notification.
// Must drain the queue (receive all messages) before re-registering.
```

### Thread notification
```c
struct sigevent sev = {
    .sigev_notify = SIGEV_THREAD,
    .sigev_notify_function = notify_handler,
    .sigev_notify_attributes = NULL,
    .sigev_value.sival_ptr = &mq,
};
mq_notify(mq, &sev);

void notify_handler(union sigval val) {
    mqd_t *mq_ptr = val.sival_ptr;
    char buf[MSG_SIZE];
    unsigned int prio;

    // Drain all messages:
    while (mq_receive(*mq_ptr, buf, MSG_SIZE, &prio) > 0) {
        process(buf, prio);
    }

    // Re-register:
    struct sigevent sev = { /* same as above */ };
    mq_notify(*mq_ptr, &sev);
}
```

### Cancel notification
```c
mq_notify(mq, NULL);
```

### Notification caveats
- Only **one** process can register for notification per queue
- Notification fires only when queue transitions from **empty to non-empty**
- Notification is **removed after delivery** — must re-register
- If you don't drain the queue before re-registering, you may miss messages (queue never becomes "empty" so notification never fires again)

### Using mq with epoll (Linux-specific)
On Linux, `mqd_t` is actually a file descriptor. You can use it with epoll:
```c
struct epoll_event ev = {
    .events = EPOLLIN,
    .data.fd = (int)mq,
};
epoll_ctl(epfd, EPOLL_CTL_ADD, (int)mq, &ev);
```
This is simpler and more reliable than `mq_notify` for event-driven architectures.

## Comparison with Pipes and SysV

| Feature | POSIX MQ | Pipe | SysV MQ |
|---------|----------|------|---------|
| Message boundaries | Yes | No (byte stream) | Yes |
| Priority | Yes | No | Yes (type field) |
| Notification | Yes (signal/thread) | poll/epoll | No |
| Kernel persistence | Yes (until unlink) | No (until close) | Yes (until msgctl) |
| epoll support | Linux: yes | Yes | No |
| Named | Yes (`/name`) | Named pipes (mkfifo) | Key-based (ftok) |
| Max message size | Configurable | `PIPE_BUF` (4K atomic) | Configurable |

**Prefer POSIX MQ over SysV MQ** — cleaner API, notification support, epoll integration on Linux.

## Practical Patterns

### Producer-consumer with structured messages
```c
typedef struct {
    uint32_t type;
    uint32_t sequence;
    struct timespec timestamp;
    char payload[240];
} rt_message_t;

_Static_assert(sizeof(rt_message_t) == 264, "unexpected size");

// Producer:
rt_message_t msg = {
    .type = MSG_SENSOR_DATA,
    .sequence = seq++,
};
clock_gettime(CLOCK_MONOTONIC, &msg.timestamp);
memcpy(msg.payload, data, data_len);
mq_send(mq, (char *)&msg, sizeof(msg), MSG_PRIO_HIGH);

// Consumer:
rt_message_t recv_msg;
unsigned int prio;
mq_receive(mq, (char *)&recv_msg, sizeof(recv_msg), &prio);
```

### Command/response between processes
```c
// Process A creates two queues:
mqd_t cmd_q = mq_open("/cmd", O_CREAT | O_WRONLY, 0660, &attr);
mqd_t rsp_q = mq_open("/rsp", O_CREAT | O_RDONLY, 0660, &attr);

// Process B:
mqd_t cmd_q = mq_open("/cmd", O_RDONLY);
mqd_t rsp_q = mq_open("/rsp", O_WRONLY);

// A sends command, waits for response
// B receives command, processes, sends response
```

### Non-blocking poll pattern
```c
struct mq_attr attr = { .mq_flags = O_NONBLOCK };
mq_setattr(mq, &attr, NULL);

while (running) {
    ssize_t len = mq_receive(mq, buf, sizeof(buf), &prio);
    if (len > 0) {
        process(buf, len, prio);
    } else if (errno == EAGAIN) {
        // No messages — do other work or yield
        sched_yield();
    }
}
```
