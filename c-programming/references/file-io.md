# File I/O

## Streams

All I/O in C is performed through **streams** — abstract interfaces represented by `FILE *` pointers.

### Standard Streams

| Stream | Name | Default | Buffering |
|--------|------|---------|-----------|
| `stdin` | Standard input | Keyboard/pipe | Line-buffered (terminal) or fully-buffered (pipe) |
| `stdout` | Standard output | Terminal/pipe | Line-buffered (terminal) or fully-buffered (pipe) |
| `stderr` | Standard error | Terminal | Unbuffered |

### Buffering Modes

| Mode | Constant | Behavior |
|------|----------|----------|
| Fully buffered | `_IOFBF` | Flush when buffer is full |
| Line buffered | `_IOLBF` | Flush on newline or buffer full |
| Unbuffered | `_IONBF` | Write immediately (each character) |

```c
/* Change buffering — must be called BEFORE any I/O on the stream */
setvbuf(fp, NULL, _IOFBF, 8192);     /* fully buffered, 8KB */
setvbuf(fp, NULL, _IONBF, 0);        /* unbuffered */
setbuf(fp, NULL);                     /* equivalent to unbuffered */

fflush(fp);                           /* force write buffered output */
fflush(NULL);                         /* flush ALL output streams */
```

## Opening and Closing Files

### fopen Modes

| Mode | Behavior | File must exist? | Creates file? | Truncates? |
|------|----------|-----------------|---------------|------------|
| `"r"` | Read | Yes | No | No |
| `"w"` | Write | No | Yes | Yes |
| `"a"` | Append | No | Yes | No |
| `"r+"` | Read/write | Yes | No | No |
| `"w+"` | Read/write | No | Yes | Yes |
| `"a+"` | Read/append | No | Yes | No |

Add `"b"` for binary mode: `"rb"`, `"wb"`, `"ab"`, `"r+b"` (or `"rb+"`), etc.

**On Unix**: text and binary modes are identical. **On Windows**: text mode translates `\r\n` ↔ `\n`; binary mode does not.

```c
FILE *fp = fopen("data.txt", "r");
if (fp == NULL) {
    perror("fopen");           /* prints: fopen: No such file or directory */
    return -1;
}

/* ... use fp ... */

if (fclose(fp) != 0) {        /* check fclose for write errors! */
    perror("fclose");
}
```

**Always check `fclose` return** on files opened for writing — buffered data may fail to write at close time.

## Character I/O

### Reading Characters

```c
int ch;                        /* MUST be int, not char — to detect EOF */
while ((ch = fgetc(fp)) != EOF) {
    putchar(ch);
}
```

- `fgetc(fp)` — reads one character, returns `int` (`EOF` on error/end)
- `getc(fp)` — same, but may be a macro (faster, but `fp` evaluated multiple times)
- `getchar()` — equivalent to `getc(stdin)`

**Why `int`, not `char`?** `EOF` is typically `-1`. If `char` is unsigned, `(char)EOF != EOF` — the loop never terminates. If `char` is signed and all 256 byte values are possible, `(char)0xFF == EOF` — premature termination. Always use `int`.

### Writing Characters

```c
fputc('A', fp);                /* write one character */
putc('A', fp);                 /* same, may be macro */
putchar('A');                  /* putc('A', stdout) */
```

## Line I/O

### Reading Lines

```c
char line[256];
while (fgets(line, sizeof(line), fp) != NULL) {
    /* line includes trailing '\n' if present */
    size_t len = strlen(line);
    if (len > 0 && line[len - 1] == '\n')
        line[len - 1] = '\0';         /* strip newline */

    printf("Line: %s\n", line);
}
```

`fgets` reads at most `size - 1` characters, always null-terminates. Returns `NULL` on EOF or error.

**NEVER use `gets()`** — it was removed from C11 because it has no buffer size parameter and always causes buffer overflows.

### Writing Lines

```c
fputs("Hello, world!\n", fp);  /* does NOT add newline — you must include it */
puts("Hello, world!");         /* writes to stdout AND adds newline */
```

### Reading Lines of Arbitrary Length

```c
char *read_line(FILE *fp) {
    size_t capacity = 128;
    size_t length = 0;
    char *buf = malloc(capacity);
    if (!buf) return NULL;

    int ch;
    while ((ch = fgetc(fp)) != EOF && ch != '\n') {
        if (length + 1 >= capacity) {
            capacity *= 2;
            char *tmp = realloc(buf, capacity);
            if (!tmp) { free(buf); return NULL; }
            buf = tmp;
        }
        buf[length++] = ch;
    }

    if (length == 0 && ch == EOF) { free(buf); return NULL; }
    buf[length] = '\0';
    return buf;
}
```

POSIX systems also have `getline()` which handles this automatically.

## Formatted I/O on Files

```c
fprintf(fp, "Name: %s, Age: %d\n", name, age);

int count;
char name[50];
if (fscanf(fp, "%49s %d", name, &count) == 2) {
    /* successfully read both fields */
}
```

All `printf`/`scanf` variants:

| Function | Input/Output | Source/Dest |
|----------|-------------|------------|
| `printf` / `scanf` | stdout/stdin | Standard streams |
| `fprintf` / `fscanf` | File stream | `FILE *` |
| `sprintf` / `sscanf` | String | `char *` |
| `snprintf` | String (bounded) | `char *` + size |

## Block I/O (Binary)

### fread and fwrite

```c
struct record {
    int id;
    char name[50];
    double salary;
};

/* Write an array of records */
struct record records[100];
size_t written = fwrite(records, sizeof(records[0]), 100, fp);
if (written != 100) { /* error */ }

/* Read records back */
struct record buf[100];
size_t read_count = fread(buf, sizeof(buf[0]), 100, fp);
/* read_count = number of COMPLETE elements read */
```

**Portability warning**: Binary files written with `fwrite` are NOT portable across:
- Different endianness (big-endian vs little-endian)
- Different struct padding/alignment
- Different type sizes

For portable binary formats, serialize fields individually with explicit byte ordering.

## File Positioning

```c
/* Get current position */
long pos = ftell(fp);

/* Seek to position */
fseek(fp, 0, SEEK_SET);       /* beginning of file */
fseek(fp, 0, SEEK_END);       /* end of file */
fseek(fp, -10, SEEK_CUR);     /* 10 bytes before current position */

/* Reset to beginning */
rewind(fp);                    /* equivalent to fseek(fp, 0, SEEK_SET) + clearerr(fp) */
```

**For large files** (> 2GB on 32-bit systems), use `fgetpos`/`fsetpos`:
```c
fpos_t pos;
fgetpos(fp, &pos);
/* ... */
fsetpos(fp, &pos);             /* return to saved position */
```

**Binary mode**: `fseek` offsets are byte counts.
**Text mode**: `fseek` with `SEEK_SET` + `ftell` result is safe. `SEEK_END` is undefined in text mode per the standard (but works on most systems).

## Error Handling

```c
if (ferror(fp)) {
    /* an I/O error occurred on this stream */
    perror("I/O error");
}

if (feof(fp)) {
    /* end-of-file has been reached */
}

clearerr(fp);                  /* reset both error and EOF indicators */
```

### The feof() Pitfall

```c
/* WRONG — feof is true AFTER a failed read, not before: */
while (!feof(fp)) {
    fgets(line, sizeof(line), fp);
    process(line);             /* processes garbage on last iteration */
}

/* CORRECT — check the return value of the read function: */
while (fgets(line, sizeof(line), fp) != NULL) {
    process(line);
}
```

### errno with File Operations

```c
#include <errno.h>
#include <string.h>

FILE *fp = fopen(path, "r");
if (!fp) {
    fprintf(stderr, "Cannot open %s: %s\n", path, strerror(errno));
    /* or: perror(path); */
}
```

## Temporary Files

```c
FILE *tmp = tmpfile();         /* opens anonymous temp file in "wb+" mode */
/* file is automatically deleted when closed or program exits */
fclose(tmp);

/* Named temporary file (less safe): */
char name[L_tmpnam];
tmpnam(name);                  /* DEPRECATED — race condition between name and open */

/* POSIX alternative (preferred): */
char template[] = "/tmp/myapp-XXXXXX";
int fd = mkstemp(template);    /* creates and opens atomically */
FILE *fp = fdopen(fd, "w+");
```

## Common Patterns

### Copy File

```c
int copy_file(const char *src, const char *dst) {
    FILE *in = fopen(src, "rb");
    if (!in) return -1;
    FILE *out = fopen(dst, "wb");
    if (!out) { fclose(in); return -1; }

    char buf[4096];
    size_t n;
    while ((n = fread(buf, 1, sizeof(buf), in)) > 0) {
        if (fwrite(buf, 1, n, out) != n) {
            fclose(in); fclose(out);
            return -1;
        }
    }

    int err = ferror(in);
    fclose(in);
    if (fclose(out) != 0) err = 1;
    return err ? -1 : 0;
}
```

### Read Entire File into Memory

```c
char *read_file(const char *path, size_t *out_size) {
    FILE *fp = fopen(path, "rb");
    if (!fp) return NULL;

    fseek(fp, 0, SEEK_END);
    long size = ftell(fp);
    fseek(fp, 0, SEEK_SET);

    char *buf = malloc(size + 1);
    if (!buf) { fclose(fp); return NULL; }

    size_t read = fread(buf, 1, size, fp);
    fclose(fp);

    buf[read] = '\0';
    if (out_size) *out_size = read;
    return buf;
}
```

### Binary Record I/O

```c
/* Write record at specific position */
void write_record(FILE *fp, long index, const struct record *rec) {
    fseek(fp, index * sizeof(*rec), SEEK_SET);
    fwrite(rec, sizeof(*rec), 1, fp);
}

/* Read record at specific position */
int read_record(FILE *fp, long index, struct record *rec) {
    fseek(fp, index * sizeof(*rec), SEEK_SET);
    return fread(rec, sizeof(*rec), 1, fp) == 1;
}
```

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| `while (!feof(fp))` | Reads garbage on last iteration | Check read function return value |
| Missing `"b"` mode | `\r\n` translation on Windows corrupts binary data | Always use `"rb"`/`"wb"` for binary |
| Not checking `fclose` | Buffered write errors lost | Check return value for write streams |
| `gets()` | Buffer overflow guaranteed | Use `fgets()` instead |
| `char ch = fgetc(fp)` | Cannot distinguish `EOF` from valid `0xFF` | Use `int ch` |
| Mixing text/binary seeks | `SEEK_END` undefined in text mode | Use binary mode for seeking |
| Not checking `fopen` | NULL dereference crash | Always check return value |
