# Async I/O

## Table of Contents
- [I/O Models Overview](#io-models-overview)
- [POSIX AIO](#posix-aio)
- [epoll](#epoll)
- [eventfd](#eventfd)
- [io_uring](#io_uring)
- [Event Loop Architecture](#event-loop-architecture)
- [Choosing an I/O Model](#choosing-an-io-model)

## I/O Models Overview

| Model | Type | Syscall overhead | Best for |
|-------|------|-----------------|----------|
| Blocking I/O | Synchronous | 1 syscall/op | Simple, single-connection |
| Non-blocking + poll/select | Readiness-based | 1-2 syscalls/event | Small fd count |
| epoll | Readiness-based | ~1 syscall/batch | Many connections, networking |
| POSIX AIO (aio_*) | Completion-based | 1 syscall/op | File I/O, POSIX portable |
| io_uring | Completion-based | 0-1 syscalls/batch | High-throughput, any I/O |

## POSIX AIO

Asynchronous I/O for files. Initiate I/O and get notified on completion:

```c
#include <aio.h>

// Submit an async read:
struct aiocb cb = {
    .aio_fildes = fd,
    .aio_buf = buffer,
    .aio_nbytes = sizeof(buffer),
    .aio_offset = 0,
    .aio_sigevent = {
        .sigev_notify = SIGEV_SIGNAL,
        .sigev_signo = SIGRTMIN,
    },
};

aio_read(&cb);

// Check status:
int status = aio_error(&cb);
if (status == EINPROGRESS) { /* still pending */ }
if (status == 0) {
    ssize_t bytes = aio_return(&cb);  // like return value of read()
}

// Wait for completion:
const struct aiocb *list[] = { &cb };
aio_suspend(list, 1, NULL);  // blocks until any in list complete
```

### Operations
```c
aio_read(&cb);     // async read
aio_write(&cb);    // async write
aio_fsync(O_SYNC, &cb);  // async fsync

// List I/O — submit multiple operations:
struct aiocb *list[] = { &cb1, &cb2, &cb3 };
lio_listio(LIO_NOWAIT, list, 3, &sev);
// LIO_NOWAIT: return immediately, notify via sev
// LIO_WAIT: block until all complete
```

### Notification methods
```c
// Signal:
cb.aio_sigevent.sigev_notify = SIGEV_SIGNAL;
cb.aio_sigevent.sigev_signo = SIGRTMIN;

// Thread callback:
cb.aio_sigevent.sigev_notify = SIGEV_THREAD;
cb.aio_sigevent.sigev_notify_function = handler;

// None (poll with aio_error):
cb.aio_sigevent.sigev_notify = SIGEV_NONE;
```

### Cancellation
```c
int ret = aio_cancel(fd, &cb);
// AIO_CANCELED, AIO_NOTCANCELED, AIO_ALLDONE
```

### Linux implementation note
On Linux, glibc implements POSIX AIO using **user-space threads** — each `aio_read` may spawn a thread. This limits scalability. For high-performance async I/O on Linux, prefer **io_uring**.

## epoll

Scalable I/O event notification for file descriptors:

```c
#include <sys/epoll.h>

// Create:
int epfd = epoll_create1(EPOLL_CLOEXEC);

// Register interest:
struct epoll_event ev = {
    .events = EPOLLIN | EPOLLET,  // edge-triggered read
    .data.fd = sock_fd,
};
epoll_ctl(epfd, EPOLL_CTL_ADD, sock_fd, &ev);

// Wait for events:
struct epoll_event events[MAX_EVENTS];
int n = epoll_wait(epfd, events, MAX_EVENTS, timeout_ms);
// timeout_ms: -1 = block forever, 0 = return immediately

for (int i = 0; i < n; i++) {
    if (events[i].events & EPOLLIN)
        handle_read(events[i].data.fd);
    if (events[i].events & EPOLLOUT)
        handle_write(events[i].data.fd);
    if (events[i].events & (EPOLLERR | EPOLLHUP))
        handle_error(events[i].data.fd);
}
```

### Event flags

| Flag | Meaning |
|------|---------|
| `EPOLLIN` | Ready for read |
| `EPOLLOUT` | Ready for write |
| `EPOLLERR` | Error condition |
| `EPOLLHUP` | Hang up |
| `EPOLLRDHUP` | Peer closed connection (TCP) |
| `EPOLLET` | Edge-triggered (instead of level-triggered) |
| `EPOLLONESHOT` | Disable after one event (re-arm with `EPOLL_CTL_MOD`) |
| `EPOLLEXCLUSIVE` | Avoid thundering herd (one waiter woken) |

### Level-triggered vs edge-triggered

**Level-triggered** (default): epoll_wait returns as long as the fd is ready. Simple but may cause repeated wakeups.

**Edge-triggered** (`EPOLLET`): epoll_wait returns only when the state *changes* (e.g., new data arrives). You MUST drain all available data on each event, or you'll miss subsequent data:

```c
// Edge-triggered read pattern:
while (1) {
    ssize_t n = read(fd, buf, sizeof(buf));
    if (n == -1) {
        if (errno == EAGAIN) break;  // all data read
        perror("read"); break;
    }
    if (n == 0) { close(fd); break; }  // EOF
    process(buf, n);
}
```

### epoll_pwait2 (Linux 5.11+)
```c
struct timespec timeout = { .tv_sec = 0, .tv_nsec = 500000 };  // 500 µs
int n = epoll_pwait2(epfd, events, MAX_EVENTS, &timeout, &sigmask);
// Nanosecond timeout precision + signal mask (like pselect)
```

### Compatible fd types
epoll works with: sockets, pipes, timerfd, signalfd, eventfd, inotify, POSIX mq (on Linux), terminal devices. Does NOT work with: regular files (always "ready"), directories.

## eventfd

Lightweight event notification — simpler than pipes:

```c
#include <sys/eventfd.h>

int efd = eventfd(0, EFD_NONBLOCK | EFD_CLOEXEC | EFD_SEMAPHORE);
// Initial counter = 0

// Signal (add to counter):
uint64_t val = 1;
write(efd, &val, sizeof(val));

// Wait (read and reset counter):
uint64_t count;
read(efd, &count, sizeof(count));
// Without EFD_SEMAPHORE: returns total count, resets to 0
// With EFD_SEMAPHORE: returns 1, decrements by 1

// Integrate with epoll:
struct epoll_event ev = { .events = EPOLLIN, .data.fd = efd };
epoll_ctl(epfd, EPOLL_CTL_ADD, efd, &ev);
```

### Use cases
- Thread-to-thread signaling via epoll
- Waking an event loop from another thread
- Replacing self-pipe trick
- io_uring completion notification

## io_uring

High-performance async I/O framework. Linux 5.1+. Uses shared ring buffers between kernel and userspace — can achieve zero-syscall I/O.

### Concept
Two ring buffers:
- **Submission Queue (SQ)**: Userspace writes I/O requests
- **Completion Queue (CQ)**: Kernel writes completed results

```c
#include <liburing.h>

// Initialize:
struct io_uring ring;
io_uring_queue_init(256, &ring, 0);  // 256 entries

// Submit a read:
struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
io_uring_prep_read(sqe, fd, buf, sizeof(buf), 0);
io_uring_sqe_set_data(sqe, user_data_ptr);  // identify completion
io_uring_submit(&ring);

// Wait for completion:
struct io_uring_cqe *cqe;
io_uring_wait_cqe(&ring, &cqe);
// cqe->res = result (like read() return value)
// cqe->user_data = your pointer from set_data
void *data = io_uring_cqe_get_data(cqe);
io_uring_cqe_seen(&ring, cqe);  // mark as consumed

// Cleanup:
io_uring_queue_exit(&ring);
```

### Supported operations
```c
io_uring_prep_read(sqe, fd, buf, len, offset);
io_uring_prep_write(sqe, fd, buf, len, offset);
io_uring_prep_readv(sqe, fd, iovecs, nr_vecs, offset);
io_uring_prep_writev(sqe, fd, iovecs, nr_vecs, offset);
io_uring_prep_accept(sqe, sockfd, addr, addrlen, flags);
io_uring_prep_connect(sqe, sockfd, addr, addrlen);
io_uring_prep_send(sqe, sockfd, buf, len, flags);
io_uring_prep_recv(sqe, sockfd, buf, len, flags);
io_uring_prep_openat(sqe, dirfd, path, flags, mode);
io_uring_prep_close(sqe, fd);
io_uring_prep_fsync(sqe, fd, flags);
io_uring_prep_timeout(sqe, ts, count, flags);
io_uring_prep_poll_add(sqe, fd, poll_mask);
io_uring_prep_cancel(sqe, user_data, flags);
```

### Flags and features
```c
// Kernel polling mode (no syscalls after setup):
io_uring_queue_init(256, &ring, IORING_SETUP_SQPOLL);

// Fixed files (pre-register fds to avoid lookup overhead):
int fds[] = { fd1, fd2 };
io_uring_register_files(&ring, fds, 2);

// Fixed buffers:
struct iovec iovs[] = { { buf1, len1 }, { buf2, len2 } };
io_uring_register_buffers(&ring, iovs, 2);

// Linked operations (execute sequentially):
sqe1->flags |= IOSQE_IO_LINK;
// sqe2 runs only after sqe1 completes
```

### Batch submission
```c
// Submit multiple operations with one syscall:
for (int i = 0; i < batch_size; i++) {
    struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
    io_uring_prep_read(sqe, fds[i], bufs[i], sizes[i], 0);
    io_uring_sqe_set_data(sqe, &contexts[i]);
}
io_uring_submit(&ring);  // one syscall for all

// Process completions:
struct io_uring_cqe *cqe;
unsigned head;
io_uring_for_each_cqe(&ring, head, cqe) {
    process_completion(cqe);
}
io_uring_cq_advance(&ring, count);
```

### Multishot operations (Linux 5.19+)
```c
// Accept connections continuously with one SQE:
io_uring_prep_multishot_accept(sqe, listen_fd, NULL, NULL, 0);

// Receive data continuously:
io_uring_prep_recv_multishot(sqe, sockfd, NULL, 0, 0);
```

## Event Loop Architecture

### Unified event loop with epoll
```c
void event_loop(void) {
    int epfd = epoll_create1(EPOLL_CLOEXEC);

    // Timer:
    int tfd = timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK);
    add_to_epoll(epfd, tfd, EPOLLIN);

    // Signals:
    int sfd = signalfd(-1, &mask, SFD_NONBLOCK);
    add_to_epoll(epfd, sfd, EPOLLIN);

    // Shutdown event:
    int efd = eventfd(0, EFD_NONBLOCK);
    add_to_epoll(epfd, efd, EPOLLIN);

    // Sockets, MQs, etc.:
    add_to_epoll(epfd, sock_fd, EPOLLIN);

    struct epoll_event events[64];
    while (running) {
        int n = epoll_wait(epfd, events, 64, -1);
        for (int i = 0; i < n; i++) {
            int fd = events[i].data.fd;
            if (fd == tfd) handle_timer(tfd);
            else if (fd == sfd) handle_signal(sfd);
            else if (fd == efd) running = 0;
            else handle_io(fd, events[i].events);
        }
    }
}
```

### io_uring event loop
```c
void uring_event_loop(struct io_uring *ring) {
    // Submit initial operations (accept, timer, etc.)
    submit_accept(ring);
    submit_timer(ring);

    while (running) {
        io_uring_submit_and_wait(ring, 1);

        struct io_uring_cqe *cqe;
        unsigned head;
        unsigned completed = 0;
        io_uring_for_each_cqe(ring, head, cqe) {
            dispatch_completion(cqe);
            completed++;
        }
        io_uring_cq_advance(ring, completed);
    }
}
```

## Choosing an I/O Model

| Scenario | Recommendation |
|----------|---------------|
| Few connections, simple protocol | Blocking I/O or poll |
| Many TCP connections | epoll (edge-triggered) |
| High-throughput file I/O | io_uring |
| Mixed I/O (files + network + timers) | io_uring (unified) or epoll + timerfd + signalfd |
| POSIX portability required | POSIX AIO or poll/select |
| Database / storage engine | io_uring with fixed files + buffers |
| Hard RT periodic I/O | timerfd + epoll, or clock_nanosleep loop |
