# Ch 7 — Telling a UNIX System What to Do

## UNIX Signals

```go
import (
    "os"
    "os/signal"
    "syscall"
)

// Graceful shutdown pattern
func main() {
    sigs := make(chan os.Signal, 1)
    signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)

    go func() {
        sig := <-sigs
        fmt.Println("received:", sig)
        cleanup()
        os.Exit(0)
    }()

    // ... run server or long-running work
}

// Stop receiving a signal
signal.Stop(sigs)
signal.Reset(syscall.SIGINT)   // restore default handler

// Common signals
// SIGINT   = Ctrl+C interrupt
// SIGTERM  = termination request (kill without -9)
// SIGHUP   = hangup (often reload config)
// SIGUSR1/SIGUSR2 = user-defined
// SIGKILL  = cannot be caught
```

## File I/O — os Package

```go
import "os"

// Open for reading
f, err := os.Open("file.txt")        // read-only
defer f.Close()

// Open/create for writing
f, err = os.Create("out.txt")        // truncate if exists
f, err = os.OpenFile("out.txt",
    os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)

// Read entire file
data, err := os.ReadFile("file.txt")  // []byte
text := string(data)

// Write entire file
err = os.WriteFile("out.txt", []byte("hello"), 0644)

// File metadata
info, err := os.Stat("file.txt")
info.Name()
info.Size()
info.Mode()
info.ModTime()
info.IsDir()

// Environment
val := os.Getenv("HOME")
os.Setenv("KEY", "value")
os.Unsetenv("KEY")
allEnv := os.Environ()   // []string "KEY=value"

// Working directory
cwd, _ := os.Getwd()
os.Chdir("/tmp")

// Temp files
f, err = os.CreateTemp("", "prefix-*.txt")
dir, err := os.MkdirTemp("", "tmpdir-")
```

## io.Reader and io.Writer

The most important interfaces for I/O composition:

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}
type Writer interface {
    Write(p []byte) (n int, err error)
}
```

### io package utilities
```go
import "io"

// Copy from Reader to Writer
n, err := io.Copy(dst, src)           // copies until EOF
n, err = io.CopyN(dst, src, 1024)    // copy up to N bytes

// Read all bytes from reader
data, err := io.ReadAll(r)

// Read exactly N bytes
buf := make([]byte, 1024)
n, err = io.ReadFull(r, buf)

// Multi-writer (tee)
tee := io.TeeReader(r, logWriter)   // reads from r, copies to logWriter

// Multi-reader (chain)
combined := io.MultiReader(r1, r2, r3)

// Discard
io.Copy(io.Discard, r)  // drain a reader

// String reader (implements io.Reader)
r := strings.NewReader("hello world")

// Byte slice reader
r2 := bytes.NewReader([]byte{1, 2, 3})

// Writer to byte buffer
var buf bytes.Buffer
buf.WriteString("hello")
buf.Write([]byte(" world"))
result := buf.String()
```

## bufio — Buffered I/O

```go
import "bufio"

// Buffered reader
br := bufio.NewReader(r)
line, err := br.ReadString('\n')    // read until delimiter
line2, _, err := br.ReadLine()      // []byte, no newline

// Scanner (preferred for line-by-line)
scanner := bufio.NewScanner(r)
scanner.Split(bufio.ScanWords)      // ScanLines (default), ScanWords, ScanRunes, ScanBytes
for scanner.Scan() {
    word := scanner.Text()
}
if err := scanner.Err(); err != nil { log.Fatal(err) }

// Custom max token size (for large lines)
scanner.Buffer(make([]byte, 1024*1024), 1024*1024)

// Buffered writer
bw := bufio.NewWriter(w)
bw.WriteString("hello\n")
bw.Flush()   // IMPORTANT: must flush or data may be lost
```

## filepath — Path Manipulation

```go
import "path/filepath"

filepath.Join("dir", "sub", "file.txt")  // "dir/sub/file.txt"
filepath.Dir("/a/b/c.txt")               // "/a/b"
filepath.Base("/a/b/c.txt")             // "c.txt"
filepath.Ext("/a/b/c.txt")              // ".txt"
filepath.Abs("relative/path")           // absolute path
filepath.Clean("a/b/../c")             // "a/c"
filepath.IsAbs("/absolute/path")        // true

// Walk directory tree
filepath.Walk(".", func(path string, info os.FileInfo, err error) error {
    if err != nil { return err }
    if !info.IsDir() {
        fmt.Println(path)
    }
    return nil
})

// WalkDir (Go 1.16+, faster)
filepath.WalkDir(".", func(path string, d fs.DirEntry, err error) error {
    if err != nil { return err }
    fmt.Println(path, d.Type())
    return nil
})

// Glob
matches, err := filepath.Glob("*.go")

// Split
dir, file := filepath.Split("/a/b/c.txt")  // "/a/b/", "c.txt"
```

## cobra — CLI Framework

```go
import "github.com/spf13/cobra"

var rootCmd = &cobra.Command{
    Use:   "myapp",
    Short: "My application",
    Long:  `A longer description of my application.`,
    RunE: func(cmd *cobra.Command, args []string) error {
        fmt.Println("root command")
        return nil
    },
}

var serveCmd = &cobra.Command{
    Use:   "serve [port]",
    Short: "Start the server",
    Args:  cobra.ExactArgs(1),
    RunE: func(cmd *cobra.Command, args []string) error {
        port := args[0]
        verbose, _ := cmd.Flags().GetBool("verbose")
        fmt.Printf("serving on %s (verbose=%v)\n", port, verbose)
        return nil
    },
}

func init() {
    serveCmd.Flags().BoolP("verbose", "v", false, "verbose output")
    rootCmd.PersistentFlags().String("config", "", "config file path")
    rootCmd.AddCommand(serveCmd)
}

func main() {
    if err := rootCmd.Execute(); err != nil {
        os.Exit(1)
    }
}
```

### viper — Configuration Management
```go
import "github.com/spf13/viper"

viper.SetConfigName("config")
viper.SetConfigType("yaml")
viper.AddConfigPath(".")
viper.AddConfigPath("$HOME/.myapp")

viper.SetDefault("port", 8080)
viper.AutomaticEnv()   // MYAPP_PORT → port

if err := viper.ReadInConfig(); err != nil {
    log.Fatal(err)
}

port := viper.GetInt("port")
host := viper.GetString("database.host")
```

## Process Management

```go
import "os/exec"

// Run command and wait
cmd := exec.Command("ls", "-la")
out, err := cmd.Output()   // stdout only
combined, err := cmd.CombinedOutput()  // stdout + stderr
fmt.Println(string(out))

// Pipe stdin/stdout
cmd2 := exec.Command("grep", "pattern")
cmd2.Stdin = strings.NewReader("input\npattern match\nno match")
cmd2.Stdout = os.Stdout
cmd2.Run()

// Background process
cmd3 := exec.Command("long-running-process")
if err := cmd3.Start(); err != nil { log.Fatal(err) }
// ... do other work
if err := cmd3.Wait(); err != nil { log.Printf("process error: %v", err) }

// Get current process info
pid := os.Getpid()
ppid := os.Getppid()
```

## syscall — Low-Level System Calls

```go
import "syscall"

// File operations
syscall.Open("/etc/hosts", syscall.O_RDONLY, 0)
syscall.Stat("/tmp", &syscall.Stat_t{})

// Common constants
syscall.STDIN_FILENO   // 0
syscall.STDOUT_FILENO  // 1
syscall.STDERR_FILENO  // 2

// Prefer os/exec and os packages over syscall for portability
// Use golang.org/x/sys for extended syscall support
```

## fs Package (Go 1.16+) — File System Abstraction

```go
import "io/fs"

// Open any fs.FS
var fsys fs.FS = os.DirFS(".")
f, err := fsys.Open("main.go")

// Walk
fs.WalkDir(fsys, ".", func(path string, d fs.DirEntry, err error) error {
    fmt.Println(path)
    return nil
})

// embed.FS — embed files at compile time
//go:embed templates/*.html
var templates embed.FS
content, _ := templates.ReadFile("templates/index.html")
```
