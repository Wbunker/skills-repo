# Formatted Input/Output

Formatted I/O in C provides powerful facilities for reading and writing data in specific formats. The `printf` and `scanf` families of functions are the primary tools, offering fine-grained control over data presentation and parsing.

## printf Function

The `printf` function writes formatted output to stdout. Its general form is:

```c
int printf(const char *format, ...);
```

Returns the number of characters written, or a negative value on error.

### Conversion Specifiers

Conversion specifiers begin with `%` and indicate how to format the corresponding argument:

| Specifier | Type | Description |
|-----------|------|-------------|
| `%d`, `%i` | `int` | Signed decimal integer |
| `%u` | `unsigned int` | Unsigned decimal integer |
| `%x`, `%X` | `unsigned int` | Hexadecimal (lowercase/uppercase) |
| `%o` | `unsigned int` | Octal |
| `%f` | `double` | Decimal floating point |
| `%e`, `%E` | `double` | Scientific notation (lowercase/uppercase e) |
| `%g`, `%G` | `double` | Shortest representation (%f or %e) |
| `%a`, `%A` | `double` | Hexadecimal floating point (C99) |
| `%c` | `int` | Single character |
| `%s` | `char *` | String |
| `%p` | `void *` | Pointer address |
| `%n` | `int *` | Stores number of characters written so far |
| `%%` | - | Literal percent sign |

**C99/C11 additions:**

| Specifier | Type | Description |
|-----------|------|-------------|
| `%zu` | `size_t` | Size type (unsigned) |
| `%zd` | `ssize_t` | Signed size type |
| `%lld` | `long long` | Long long integer (C99) |
| `%llu` | `unsigned long long` | Unsigned long long |

```c
printf("%d\n", 42);              // 42
printf("%u\n", 4294967295U);     // 4294967295
printf("%x\n", 255);             // ff
printf("%X\n", 255);             // FF
printf("%o\n", 64);              // 100
printf("%f\n", 3.14159);         // 3.141590
printf("%e\n", 1234.5);          // 1.234500e+03
printf("%g\n", 1234.5);          // 1234.5
printf("%c\n", 'A');             // A
printf("%s\n", "Hello");         // Hello
printf("%p\n", (void *)&x);      // 0x7ffeeb3c4a5c (address)
printf("%%\n");                  // %
```

### Flags

Flags modify the output format and appear immediately after the `%`:

| Flag | Effect |
|------|--------|
| `-` | Left-justify within field width |
| `+` | Always show sign for signed conversions |
| ` ` (space) | Prefix positive numbers with space |
| `0` | Pad with zeros instead of spaces |
| `#` | Alternative form (0x for hex, force decimal point) |

```c
printf("%5d\n", 42);             //    42 (right-justified)
printf("%-5d\n", 42);            // 42    (left-justified)
printf("%+d\n", 42);             // +42
printf("% d\n", 42);             //  42 (space before positive)
printf("%05d\n", 42);            // 00042
printf("%#x\n", 255);            // 0xff
printf("%#.0f\n", 5.0);          // 5.
```

Multiple flags can be combined:

```c
printf("%-+8d\n", 42);           // +42      (left-justified with sign)
printf("%+08d\n", 42);           // +0000042 (zero-padded with sign)
```

### Field Width

An integer specifies the minimum number of characters to output:

```c
printf("%5d\n", 42);             //    42
printf("%5d\n", 12345);          // 12345
printf("%5d\n", 123456);         // 123456 (exceeds width)
printf("%*d\n", 5, 42);          //    42 (width from argument)
```

The width can be specified dynamically using `*`:

```c
int width = 8;
printf("%*d\n", width, 42);      //       42
```

### Precision

Precision is specified with `.number` and has different meanings for different conversions:

**For integers (`%d`, `%i`, `%u`, `%x`, `%o`):** minimum number of digits (zero-padded)

```c
printf("%.5d\n", 42);            // 00042
printf("%.3d\n", 12345);         // 12345
```

**For floating-point (`%f`, `%e`):** number of digits after decimal point

```c
printf("%.2f\n", 3.14159);       // 3.14
printf("%.10f\n", 3.14159);      // 3.1415900000
```

**For `%g`:** maximum number of significant digits

```c
printf("%.3g\n", 123.456);       // 123
printf("%.5g\n", 123.456);       // 123.46
```

**For strings (`%s`):** maximum number of characters

```c
printf("%.5s\n", "Hello, World"); // Hello
```

**Dynamic precision:**

```c
printf("%.*f\n", 3, 3.14159);    // 3.142
```

### Length Modifiers

Length modifiers alter the expected type of the argument:

| Modifier | With d/i | With u/x/o | With f/e/g |
|----------|----------|------------|------------|
| `hh` | `signed char` | `unsigned char` | - |
| `h` | `short` | `unsigned short` | - |
| `l` | `long` | `unsigned long` | - |
| `ll` | `long long` | `unsigned long long` | - |
| `L` | - | - | `long double` |
| `z` | `ssize_t` | `size_t` | - |
| `t` | `ptrdiff_t` | - | - |
| `j` | `intmax_t` | `uintmax_t` | - |

```c
short s = 42;
printf("%hd\n", s);

long l = 1234567890L;
printf("%ld\n", l);

long long ll = 9223372036854775807LL;
printf("%lld\n", ll);

size_t sz = sizeof(int);
printf("%zu\n", sz);               // Portable size_t printing

long double ld = 3.14159265358979323846L;
printf("%Lf\n", ld);
```

**Critical for portability:** Always use `%zu` for `size_t`, `%td` for `ptrdiff_t`, etc.

## scanf Function

The `scanf` function reads formatted input from stdin:

```c
int scanf(const char *format, ...);
```

Returns the number of successfully converted items, or `EOF` on end-of-file/error.

### Conversion Specifiers

Similar to `printf`, but arguments must be pointers:

```c
int n;
float f;
char c;
char str[100];

scanf("%d", &n);                 // Read integer
scanf("%f", &f);                 // Read float
scanf("%c", &c);                 // Read single character
scanf("%s", str);                // Read string (no & needed for arrays)
```

**Important:** Forgetting `&` is a common error that causes undefined behavior.

### Whitespace Handling

`scanf` automatically skips leading whitespace for most conversions (except `%c`, `%[`, and `%n`):

```c
int a, b;
scanf("%d%d", &a, &b);           // "  42   17\n" works fine
```

**But `%c` does NOT skip whitespace:**

```c
char c1, c2;
scanf("%c%c", &c1, &c2);         // Input: "A B" → c1='A', c2=' '
scanf(" %c %c", &c1, &c2);       // Space before %c skips whitespace
```

**Best practice:** Use `" %c"` instead of `"%c"` to skip leading whitespace.

### Scanset `%[...]`

Scansets read characters matching a pattern:

```c
char word[50];
scanf("%[a-z]", word);           // Read lowercase letters only
scanf("%[^,]", word);            // Read until comma (negated set)
scanf("%[^\n]", word);           // Read entire line (until newline)
```

**Negated scanset (`%[^...]`):** Matches any character NOT in the set.

```c
char name[100];
scanf("%[^\n]", name);           // Read line including spaces
scanf("%*c");                    // Consume the newline
```

### Maximum Field Width

Specify maximum characters to read (prevents buffer overflow):

```c
char str[10];
scanf("%9s", str);               // Read at most 9 chars + null terminator
```

**Critical safety rule:** Always use field width with `%s` to prevent buffer overflow:

```c
// DANGEROUS:
char buf[10];
scanf("%s", buf);                // Buffer overflow if input > 9 chars

// SAFE:
scanf("%9s", buf);               // Guaranteed to fit in buf
```

### Assignment Suppression `*`

The `*` flag skips storing the converted value:

```c
int day, year;
scanf("%d %*s %d", &day, &year); // Input: "15 January 2024"
                                 // Reads day=15, year=2024, ignores "January"
```

### Return Value Checking

**Always check `scanf` return value:**

```c
int n;
if (scanf("%d", &n) != 1) {
    fprintf(stderr, "Invalid input\n");
    // Clear input buffer
    int c;
    while ((c = getchar()) != '\n' && c != EOF);
    return 1;
}
```

The return value indicates the number of successful conversions:

```c
int a, b, c;
int result = scanf("%d %d %d", &a, &b, &c);
// result == 3: all three converted
// result == 2: first two converted, third failed
// result == 0: first conversion failed
// result == EOF: end-of-file or error before any conversion
```

### Buffer Overflow Dangers

`scanf("%s", str)` without field width is a **serious security vulnerability**:

```c
// NEVER DO THIS:
char password[16];
scanf("%s", password);           // Attacker can overflow buffer

// DO THIS:
scanf("%15s", password);         // Safe: at most 15 chars + '\0'
```

**Better alternatives:**
- Use `fgets()` for line input
- Use `scanf()` with explicit field width
- Consider `getline()` (POSIX) for dynamic allocation

## Format String Safety

### Never Use User Input as Format String

```c
// DANGEROUS - Format string vulnerability:
char user_input[100];
fgets(user_input, sizeof(user_input), stdin);
printf(user_input);              // EXPLOIT RISK!

// SAFE:
printf("%s", user_input);
```

**Why it's dangerous:** Attacker can use `%n`, `%s`, `%x` to read/write memory:

```c
// Attacker inputs: "%x %x %x %x"
printf(user_input);              // Leaks stack values

// Attacker inputs: "%n"
printf(user_input);              // Writes to arbitrary memory
```

### Format String Vulnerabilities

The `%n` specifier writes the number of bytes output so far:

```c
int count;
printf("Hello%n\n", &count);     // count = 5
```

**Exploit scenario:**

```c
// Vulnerable code:
printf(user_controlled_string);

// Attacker input: "AAAA%08x%08x%08x%n"
// Can write a value to address 0x41414141
```

**Defense:**
1. Never use user input as format string
2. Use `printf("%s", user_string)` instead
3. Enable compiler warnings: `-Wformat-security`

### Using %n Safely

Legitimate uses exist, but require care:

```c
char buffer[100];
int pos;
sprintf(buffer, "Status: %s%n - Code: %d", status, &pos, code);
// pos contains position for potential truncation/continuation
```

**Safe usage rules:**
- Only use `%n` with format strings you control
- Never mix `%n` with user input
- Consider alternatives (e.g., return value of `snprintf`)

## sprintf/snprintf

Build formatted strings in memory:

```c
char buffer[100];
sprintf(buffer, "x=%d, y=%d", x, y);
```

**`sprintf` is dangerous** - no bounds checking:

```c
char buf[10];
sprintf(buf, "%d", 123456789);   // BUFFER OVERFLOW!
```

### snprintf - Safe String Building

Always use `snprintf` with buffer size:

```c
char buf[20];
int len = snprintf(buf, sizeof(buf), "Value: %d", 12345);

if (len >= sizeof(buf)) {
    // Output was truncated
    fprintf(stderr, "Buffer too small, needed %d bytes\n", len + 1);
}
```

**Return value semantics:**
- Returns number of characters that **would have been written** (excluding `\0`)
- If return value >= buffer size, output was truncated
- Buffer always null-terminated (unlike `strncpy`)

```c
char buf[10];
int n = snprintf(buf, sizeof(buf), "Hello, World!");
// n = 13 (length of "Hello, World!")
// buf = "Hello, Wo\0" (truncated but null-terminated)
```

**Building complex strings safely:**

```c
char msg[256];
int pos = 0;
pos += snprintf(msg + pos, sizeof(msg) - pos, "Error: ");
pos += snprintf(msg + pos, sizeof(msg) - pos, "%s ", error_type);
pos += snprintf(msg + pos, sizeof(msg) - pos, "at line %d", line_num);

if (pos >= sizeof(msg)) {
    fprintf(stderr, "Warning: message truncated\n");
}
```

## sscanf

Parse formatted data from strings:

```c
char input[] = "42 3.14 hello";
int n;
float f;
char word[20];

sscanf(input, "%d %f %s", &n, &f, word);
// n = 42, f = 3.14, word = "hello"
```

**Parsing dates:**

```c
char date[] = "2024-01-15";
int year, month, day;

if (sscanf(date, "%d-%d-%d", &year, &month, &day) == 3) {
    printf("Parsed: %d/%d/%d\n", month, day, year);
} else {
    fprintf(stderr, "Invalid date format\n");
}
```

**Validation with return value:**

```c
char *input = "  123  ";
int value;

if (sscanf(input, "%d", &value) == 1) {
    // Successfully parsed an integer
} else {
    // Not a valid integer
}
```

**Safety note:** `sscanf` has the same buffer overflow risks as `scanf`:

```c
char buf[10];
sscanf(user_input, "%s", buf);   // DANGEROUS
sscanf(user_input, "%9s", buf);  // SAFE
```

## Common Patterns

### Reading Lines with fgets + sscanf

**Best practice for robust input:**

```c
char line[256];
int value;

while (fgets(line, sizeof(line), stdin) != NULL) {
    if (sscanf(line, "%d", &value) == 1) {
        printf("Got: %d\n", value);
    } else {
        fprintf(stderr, "Invalid input, try again\n");
    }
}
```

**Why this is better than scanf:**
- `fgets` has built-in buffer protection
- Failed `sscanf` doesn't leave junk in input stream
- Easy to handle entire lines

### Input Validation Loops

```c
int get_positive_int(void) {
    char line[100];
    int value;

    while (1) {
        printf("Enter a positive integer: ");
        if (fgets(line, sizeof(line), stdin) == NULL) {
            return -1;  // EOF or error
        }

        if (sscanf(line, "%d", &value) == 1 && value > 0) {
            return value;
        }

        fprintf(stderr, "Invalid input, try again.\n");
    }
}
```

### Reading Until EOF

```c
int value;
while (scanf("%d", &value) == 1) {
    process(value);
}

if (!feof(stdin)) {
    fprintf(stderr, "Input error\n");
}
```

**Better pattern with fgets:**

```c
char line[256];
while (fgets(line, sizeof(line), stdin) != NULL) {
    int value;
    if (sscanf(line, "%d", &value) == 1) {
        process(value);
    }
}
```

### Clearing Input Buffer After scanf Error

```c
int value;
while (1) {
    printf("Enter number: ");
    if (scanf("%d", &value) == 1) {
        break;
    }

    // Clear invalid input
    int c;
    while ((c = getchar()) != '\n' && c != EOF);

    if (c == EOF) {
        return -1;
    }

    fprintf(stderr, "Invalid input, try again\n");
}
```

## printf/scanf Pitfall Table

| Problem | Example | Fix |
|---------|---------|-----|
| Mismatched format specifier | `printf("%d", 3.14);` | `printf("%f", 3.14);` |
| Missing `&` in scanf | `scanf("%d", n);` | `scanf("%d", &n);` |
| Using `&` with array in scanf | `scanf("%s", &str);` | `scanf("%s", str);` |
| Wrong length modifier | `printf("%d", (long)x);` | `printf("%ld", (long)x);` |
| Unsigned printed as signed | `printf("%d", 4000000000U);` | `printf("%u", 4000000000U);` |
| `%c` reads whitespace | `scanf("%c", &c);` | `scanf(" %c", &c);` (space before `%c`) |
| Buffer overflow with `%s` | `scanf("%s", buf);` | `scanf("%9s", buf);` (for `char buf[10]`) |
| Leftover newline after scanf | `scanf("%d", &n); getchar();` | `scanf("%d\n", &n);` or skip with `" %c"` |
| User input as format string | `printf(user_input);` | `printf("%s", user_input);` |
| Ignoring scanf return value | `scanf("%d", &n);` | `if (scanf("%d", &n) != 1) { ... }` |
| sprintf buffer overflow | `sprintf(buf, "%d", x);` | `snprintf(buf, sizeof(buf), "%d", x);` |
| `%n` with user input | `printf(input);` // input="%n" | Never use user string as format |
| Printing `size_t` wrong | `printf("%d", sizeof(x));` | `printf("%zu", sizeof(x));` |
| Printing pointer wrong | `printf("%d", ptr);` | `printf("%p", (void *)ptr);` |
| Trailing whitespace in scanf | `scanf("%d ", &n);` | Use `scanf("%d", &n);` then skip whitespace separately |
| Reading line with scanf | `scanf("%s", line);` | `fgets(line, sizeof(line), stdin);` |

**Additional gotchas:**

```c
// Gotcha: %g removes trailing zeros
printf("%g", 3.00);              // Prints "3"
printf("%f", 3.00);              // Prints "3.000000"

// Gotcha: scanf %s stops at whitespace
scanf("%s", name);               // "John Smith" → name="John"
fgets(name, sizeof(name), stdin); // Gets "John Smith\n"

// Gotcha: Mixing scanf and getchar
scanf("%d", &n);                 // Leaves '\n' in buffer
char c = getchar();              // Gets '\n', not next input!
```

## Summary

**Golden rules for formatted I/O:**

1. **Always check return values** of `scanf`/`fscanf`
2. **Never use user input as format string** - major security risk
3. **Always use field width with `%s`** in `scanf` to prevent buffer overflow
4. **Use `snprintf`, not `sprintf`** - and check return value for truncation
5. **Remember `&` with `scanf`** (except for arrays/strings)
6. **Use correct length modifiers** - `%zu` for `size_t`, `%lld` for `long long`, etc.
7. **Prefer `fgets + sscanf`** over raw `scanf` for robust input handling
8. **Use `" %c"` not `"%c"`** in scanf to skip whitespace
9. **Enable format warnings** - compile with `-Wformat -Wformat-security`

With these tools and precautions, C's formatted I/O provides powerful and safe capabilities for data input and output.
