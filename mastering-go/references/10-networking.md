# Ch 10 — Working with TCP/IP and WebSocket

## net Package Overview

```go
import "net"

// Resolve address
addr, err := net.ResolveTCPAddr("tcp", "localhost:8080")
addr, err = net.ResolveUDPAddr("udp", "0.0.0.0:9000")
addr, err = net.ResolveUnixAddr("unix", "/tmp/app.sock")

// Interfaces
interfaces, err := net.Interfaces()
for _, iface := range interfaces {
    addrs, _ := iface.Addrs()
    for _, a := range addrs {
        fmt.Println(iface.Name, a.String())
    }
}

// DNS lookup
ips, err := net.LookupHost("example.com")
cnames, err := net.LookupCNAME("www.example.com")
```

## TCP Server

```go
func main() {
    ln, err := net.Listen("tcp", ":8080")
    if err != nil { log.Fatal(err) }
    defer ln.Close()

    log.Println("listening on :8080")
    for {
        conn, err := ln.Accept()
        if err != nil { log.Println(err); continue }
        go handleConn(conn)
    }
}

func handleConn(conn net.Conn) {
    defer conn.Close()

    // Set deadlines to prevent goroutine leaks
    conn.SetDeadline(time.Now().Add(30 * time.Second))

    scanner := bufio.NewScanner(conn)
    for scanner.Scan() {
        line := scanner.Text()
        fmt.Fprintln(conn, "echo: "+line)
    }
}
```

## TCP Client

```go
conn, err := net.Dial("tcp", "localhost:8080")
if err != nil { log.Fatal(err) }
defer conn.Close()

conn.SetDeadline(time.Now().Add(10 * time.Second))

fmt.Fprintln(conn, "hello server")

scanner := bufio.NewScanner(conn)
if scanner.Scan() {
    fmt.Println("server says:", scanner.Text())
}

// Dial with context (preferred for cancellation)
dialer := &net.Dialer{Timeout: 5 * time.Second}
conn, err = dialer.DialContext(ctx, "tcp", "localhost:8080")
```

## UDP Server and Client

```go
// UDP Server
addr, _ := net.ResolveUDPAddr("udp", ":9000")
conn, err := net.ListenUDP("udp", addr)
defer conn.Close()

buf := make([]byte, 1024)
for {
    n, remoteAddr, err := conn.ReadFromUDP(buf)
    if err != nil { continue }
    msg := string(buf[:n])
    fmt.Printf("from %s: %s\n", remoteAddr, msg)
    conn.WriteToUDP([]byte("ack"), remoteAddr)
}

// UDP Client
serverAddr, _ := net.ResolveUDPAddr("udp", "localhost:9000")
conn, err := net.DialUDP("udp", nil, serverAddr)
defer conn.Close()

conn.Write([]byte("hello"))
buf := make([]byte, 1024)
n, _ := conn.Read(buf)
fmt.Println("response:", string(buf[:n]))
```

## UNIX Domain Sockets

```go
// Server (stream)
os.Remove("/tmp/app.sock")  // clean up previous socket file
ln, err := net.Listen("unix", "/tmp/app.sock")
// ... same as TCP from here

// Client
conn, err := net.Dial("unix", "/tmp/app.sock")
// ... same as TCP client

// Datagram (SOCK_DGRAM)
addr, _ := net.ResolveUnixAddr("unixgram", "/tmp/app.sock")
conn, err := net.ListenUnixgram("unixgram", addr)
```

## WebSocket (gorilla/websocket)

```go
import "github.com/gorilla/websocket"

var upgrader = websocket.Upgrader{
    ReadBufferSize:  1024,
    WriteBufferSize: 1024,
    CheckOrigin: func(r *http.Request) bool {
        return true // allow all origins (adjust for production)
    },
}

// Server-side handler
func wsHandler(w http.ResponseWriter, r *http.Request) {
    conn, err := upgrader.Upgrade(w, r, nil)
    if err != nil { log.Println(err); return }
    defer conn.Close()

    for {
        messageType, msg, err := conn.ReadMessage()
        if err != nil {
            if websocket.IsUnexpectedCloseError(err,
                websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
                log.Printf("ws error: %v", err)
            }
            break
        }
        log.Printf("received: %s", msg)
        conn.WriteMessage(messageType, msg)  // echo back
    }
}

// Client-side
conn, _, err := websocket.DefaultDialer.Dial("ws://localhost:8080/ws", nil)
defer conn.Close()

conn.WriteMessage(websocket.TextMessage, []byte("hello"))
_, msg, err := conn.ReadMessage()
```

### WebSocket with context
```go
ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
defer cancel()

conn, _, err := websocket.DefaultDialer.DialContext(ctx, url, nil)
```

### Ping/Pong (keep-alive)
```go
conn.SetPongHandler(func(string) error {
    conn.SetReadDeadline(time.Now().Add(60 * time.Second))
    return nil
})

// Ping every 30 seconds
ticker := time.NewTicker(30 * time.Second)
go func() {
    for range ticker.C {
        if err := conn.WriteMessage(websocket.PingMessage, nil); err != nil {
            return
        }
    }
}()
```

## RabbitMQ (amqp091-go)

```go
import amqp "github.com/rabbitmq/amqp091-go"

// Connect
conn, err := amqp.Dial("amqp://guest:guest@localhost:5672/")
defer conn.Close()

ch, err := conn.Channel()
defer ch.Close()

// Declare queue
q, err := ch.QueueDeclare(
    "my-queue", // name
    true,       // durable
    false,      // auto-delete
    false,      // exclusive
    false,      // no-wait
    nil,        // args
)

// Publish
err = ch.PublishWithContext(ctx,
    "",       // exchange
    q.Name,   // routing key
    false,    // mandatory
    false,    // immediate
    amqp.Publishing{
        ContentType: "application/json",
        Body:        []byte(`{"event":"order.created"}`),
    },
)

// Consume
msgs, err := ch.Consume(q.Name, "", false, false, false, false, nil)
for d := range msgs {
    fmt.Printf("received: %s\n", d.Body)
    d.Ack(false)   // acknowledge
}
```

## net.Conn Timeouts — Best Practices

```go
// Always set timeouts on connections
conn.SetDeadline(time.Now().Add(30 * time.Second))
conn.SetReadDeadline(time.Now().Add(10 * time.Second))
conn.SetWriteDeadline(time.Now().Add(10 * time.Second))

// Reset deadline after each successful read (for long-lived connections)
for {
    conn.SetReadDeadline(time.Now().Add(30 * time.Second))
    msg, err := readMessage(conn)
    if err != nil {
        if netErr, ok := err.(net.Error); ok && netErr.Timeout() {
            log.Println("connection timed out")
        }
        return
    }
    process(msg)
}
```

## Protocol Design Tips

1. **Framing** — delimit messages with length prefix or sentinel (newline, null byte)
2. **Versioning** — include protocol version in handshake
3. **Heartbeats** — periodic ping/pong to detect dead connections
4. **Backpressure** — use buffered channels or rate limiting to prevent overload
5. **TLS** — encrypt all production network traffic

### Length-prefixed framing example
```go
// Write message with 4-byte length prefix
func writeMsg(w io.Writer, data []byte) error {
    header := make([]byte, 4)
    binary.BigEndian.PutUint32(header, uint32(len(data)))
    if _, err := w.Write(header); err != nil { return err }
    _, err := w.Write(data)
    return err
}

// Read length-prefixed message
func readMsg(r io.Reader) ([]byte, error) {
    header := make([]byte, 4)
    if _, err := io.ReadFull(r, header); err != nil { return nil, err }
    n := binary.BigEndian.Uint32(header)
    buf := make([]byte, n)
    _, err := io.ReadFull(r, buf)
    return buf, err
}
```
