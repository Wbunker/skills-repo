# Java 11 I/O and NIO.2
## Classic I/O, Serialization, NIO.2 Path/Files, Java 11 Convenience Methods

---

## Classic I/O (`java.io`)

### Byte Streams

```
InputStream                     OutputStream
  ├── FileInputStream              ├── FileOutputStream
  ├── BufferedInputStream          ├── BufferedOutputStream
  ├── ByteArrayInputStream         ├── ByteArrayOutputStream
  ├── DataInputStream              ├── DataOutputStream
  └── ObjectInputStream            └── ObjectOutputStream
```

```java
// Copy file with buffering
try (InputStream in  = new BufferedInputStream(new FileInputStream("src.bin"));
     OutputStream out = new BufferedOutputStream(new FileOutputStream("dst.bin"))) {
    byte[] buf = new byte[8192];
    int n;
    while ((n = in.read(buf)) != -1) {
        out.write(buf, 0, n);
    }
}
```

### Character Streams (Text)

```
Reader                          Writer
  ├── FileReader                   ├── FileWriter
  ├── BufferedReader               ├── BufferedWriter
  ├── InputStreamReader            ├── OutputStreamWriter
  └── StringReader                 ├── PrintWriter
                                   └── StringWriter
```

```java
// Read text file line by line
try (BufferedReader reader = new BufferedReader(new FileReader("data.txt"))) {
    String line;
    while ((line = reader.readLine()) != null) {
        System.out.println(line);
    }
}

// Write text with PrintWriter
try (PrintWriter pw = new PrintWriter(new FileWriter("out.txt", true))) {
    pw.println("line one");
    pw.printf("Value: %d%n", 42);
}

// Bridge: InputStreamReader converts bytes → chars with charset
new InputStreamReader(inputStream, StandardCharsets.UTF_8)
```

---

## Serialization

### Basic Serialization

```java
public class Employee implements Serializable {
    private static final long serialVersionUID = 1L;  // version control

    private String name;
    private int id;
    private transient String password;   // excluded from serialization
}

// Write
try (ObjectOutputStream oos = new ObjectOutputStream(
        new FileOutputStream("emp.ser"))) {
    oos.writeObject(employee);
}

// Read
try (ObjectInputStream ois = new ObjectInputStream(
        new FileInputStream("emp.ser"))) {
    Employee emp = (Employee) ois.readObject();
}
```

### `serialVersionUID`

If not declared, JVM computes it from class structure. Any class change (field added/removed, method signature) changes the computed UID, breaking deserialization of existing data. Always declare explicitly.

### `transient`

Fields marked `transient` are not serialized. Useful for:
- Passwords, keys, sensitive data
- Cached computed values
- Non-serializable objects (connections, threads)

### Custom Serialization

```java
private void writeObject(ObjectOutputStream out) throws IOException {
    out.defaultWriteObject();        // serialize non-transient fields
    out.writeUTF(encrypt(password)); // custom handling
}

private void readObject(ObjectInputStream in) throws IOException, ClassNotFoundException {
    in.defaultReadObject();
    this.password = decrypt(in.readUTF());
}
```

---

## NIO.2 (`java.nio.file`)

NIO.2 (Java 7+) is the modern file I/O API. Prefer it over `java.io.File` for new code.

### `Path` and `Paths`

```java
// Create Path
Path p1 = Path.of("/home/user/data.txt");          // Java 11 — preferred
Path p2 = Paths.get("/home/user", "data.txt");      // Java 7+
Path rel = Path.of("relative/path/file.txt");

// Path operations
p1.getFileName()     // data.txt
p1.getParent()       // /home/user
p1.getRoot()         // /
p1.getNameCount()    // 4 (number of elements)
p1.getName(0)        // home
p1.subpath(1, 3)     // user/data.txt (indices, exclusive end)
p1.toAbsolutePath()  // resolve relative to current working directory
p1.normalize()       // remove . and ..
p1.toRealPath()      // resolve symlinks; throws IOException if not exists

// Comparison
p1.equals(p2)
p1.startsWith(Path.of("/home"))
p1.endsWith(Path.of("data.txt"))

// Conversion
p1.toFile()          // java.io.File
file.toPath()        // from java.io.File
```

### `Files` — Operations

```java
// Existence
Files.exists(path)
Files.notExists(path)
Files.isDirectory(path)
Files.isRegularFile(path)
Files.isReadable(path)
Files.isWritable(path)
Files.isExecutable(path)
Files.isHidden(path)

// Create
Files.createFile(path)                    // throws if exists
Files.createDirectory(path)              // one level
Files.createDirectories(path)            // all levels (like mkdir -p)
Files.createTempFile("prefix", ".tmp")
Files.createTempDirectory("prefix")

// Copy / Move / Delete
Files.copy(source, target, StandardCopyOption.REPLACE_EXISTING,
    StandardCopyOption.COPY_ATTRIBUTES);
Files.move(source, target, StandardCopyOption.ATOMIC_MOVE);
Files.delete(path);                       // throws NoSuchFileException if missing
Files.deleteIfExists(path);               // safe delete
```

### `Files` — Reading and Writing

```java
// Java 11 — read/write entire text file
String content = Files.readString(path);
String content = Files.readString(path, StandardCharsets.UTF_8);

Files.writeString(path, "content");
Files.writeString(path, "append", StandardOpenOption.APPEND, StandardOpenOption.CREATE);

// Read all bytes / lines
byte[] bytes = Files.readAllBytes(path);
List<String> lines = Files.readAllLines(path);                  // UTF-8 default
List<String> lines = Files.readAllLines(path, StandardCharsets.ISO_8859_1);

// Write bytes / lines
Files.write(path, bytes);
Files.write(path, List.of("line1", "line2"));

// Streams (for large files)
try (Stream<String> lines = Files.lines(path)) {
    lines.filter(l -> l.contains("ERROR")).forEach(System.out::println);
}

// Buffered reader/writer
try (BufferedReader reader = Files.newBufferedReader(path)) { ... }
try (BufferedWriter writer = Files.newBufferedWriter(path)) { ... }
```

### Directory Traversal

```java
// Immediate children
try (Stream<Path> entries = Files.list(dir)) {
    entries.filter(Files::isRegularFile).forEach(System.out::println);
}

// Recursive walk (depth-first)
try (Stream<Path> tree = Files.walk(dir)) {
    tree.filter(p -> p.toString().endsWith(".java"))
        .forEach(System.out::println);
}

// Walk with max depth
try (Stream<Path> tree = Files.walk(dir, 2)) { ... }

// Files.find — walk with filter (more efficient for large trees)
try (Stream<Path> found = Files.find(dir, Integer.MAX_VALUE,
        (path, attrs) -> attrs.isRegularFile() && path.toString().endsWith(".log"))) {
    found.forEach(System.out::println);
}
```

### File Attributes

```java
BasicFileAttributes attrs = Files.readAttributes(path, BasicFileAttributes.class);
attrs.size()
attrs.creationTime()
attrs.lastModifiedTime()
attrs.isDirectory()
attrs.isRegularFile()
attrs.isSymbolicLink()

// Shortcut
long size = Files.size(path);
FileTime modified = Files.getLastModifiedTime(path);

// POSIX attributes (Unix)
PosixFileAttributes posix = Files.readAttributes(path, PosixFileAttributes.class);
posix.owner()
posix.group()
posix.permissions()   // Set<PosixFilePermission>
```

### `FileVisitor` — Custom Walk

```java
Files.walkFileTree(startDir, new SimpleFileVisitor<Path>() {
    @Override
    public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
        if (file.toString().endsWith(".tmp")) Files.deleteIfExists(file);
        return FileVisitResult.CONTINUE;
    }

    @Override
    public FileVisitResult preVisitDirectory(Path dir, BasicFileAttributes attrs) {
        System.out.println("Entering: " + dir);
        return FileVisitResult.CONTINUE;   // or SKIP_SUBTREE to skip
    }

    @Override
    public FileVisitResult visitFileFailed(Path file, IOException exc) {
        System.err.println("Failed: " + file + " — " + exc);
        return FileVisitResult.CONTINUE;
    }
});
```

Return values: `CONTINUE`, `TERMINATE`, `SKIP_SUBTREE`, `SKIP_SIBLINGS`.

---

## Java 11 I/O Additions

### `Path.of()` (JEP 321 side effect)

```java
// Equivalent to Paths.get() — convenience factory on Path itself
Path p = Path.of("/usr/local/bin/java");
Path p = Path.of("/usr", "local", "bin", "java");  // varargs
```

### `Files.readString()` / `Files.writeString()`

```java
// Read entire file as String (UTF-8 by default)
String content = Files.readString(Path.of("config.json"));
String content = Files.readString(Path.of("data.txt"), StandardCharsets.ISO_8859_1);

// Write String to file
Files.writeString(Path.of("output.txt"), "Hello, World!");
Files.writeString(
    Path.of("log.txt"),
    "entry\n",
    StandardCharsets.UTF_8,
    StandardOpenOption.APPEND,
    StandardOpenOption.CREATE);
```

### `InputStream.readAllBytes()` / `InputStream.readNBytes()` / `InputStream.transferTo()`

Added in Java 9/11:

```java
byte[] all = inputStream.readAllBytes();
byte[] first100 = inputStream.readNBytes(100);  // at most 100 bytes

// Transfer input stream to output stream
long bytesTransferred = inputStream.transferTo(outputStream);
```

### `Reader.transferTo(Writer)`

```java
try (Reader reader = new FileReader("in.txt");
     Writer writer = new FileWriter("out.txt")) {
    reader.transferTo(writer);
}
```

---

## `StandardOpenOption`

| Option | Meaning |
|--------|---------|
| `READ` | Open for reading |
| `WRITE` | Open for writing |
| `APPEND` | Write at end of file |
| `CREATE` | Create if not exists |
| `CREATE_NEW` | Create; fail if exists |
| `TRUNCATE_EXISTING` | Truncate to zero on open |
| `DELETE_ON_CLOSE` | Delete when closed |
| `SYNC` | Synchronous writes to storage |

---

## Console I/O

```java
// Output
System.out.println("message");
System.out.printf("Name: %s, Age: %d%n", name, age);
System.err.println("error message");

// Input via Scanner
import java.util.Scanner;
Scanner sc = new Scanner(System.in);
String line = sc.nextLine();
int num = sc.nextInt();
sc.close();

// Console class (not available in all environments)
Console console = System.console();
if (console != null) {
    String user = console.readLine("Username: ");
    char[] pass = console.readPassword("Password: ");  // doesn't echo
}
```
