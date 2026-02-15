# Arrays and Strings

This reference covers arrays and strings in C, based on K.N. King's "C Programming: A Modern Approach, 2nd Edition" (Chapters 8 and 13).

## One-Dimensional Arrays

### Declaration and Initialization

Arrays in C are fixed-size collections of elements of the same type. The size must be a compile-time constant (except for VLAs in C99).

```c
int numbers[10];              // Uninitialized array of 10 integers
int primes[5] = {2, 3, 5, 7, 11};  // Fully initialized
```

**Partial Initialization**: If you provide fewer initializers than the array size, remaining elements are zero-initialized.

```c
int values[100] = {1, 2, 3};  // First 3 are 1,2,3; rest are 0
int zeros[50] = {0};          // All elements initialized to 0
```

**Omitting Array Size**: When fully initialized, you can omit the size and the compiler will deduce it.

```c
int primes[] = {2, 3, 5, 7, 11};  // Size is 5
```

**Designated Initializers (C99)**: Initialize specific elements by index.

```c
int sparse[100] = {[0] = 1, [49] = 2, [99] = 3};  // Only 3 elements set
int flags[10] = {[5] = 1, [9] = 1};  // flags[5] and flags[9] are 1, rest 0
```

You can combine designated and sequential initializers:

```c
int mixed[10] = {1, 2, [5] = 6, 7, 8};  // [0]=1, [1]=2, [5]=6, [6]=7, [7]=8
```

### The sizeof Operator with Arrays

The `sizeof` operator returns the total size in bytes of an array, not the number of elements.

```c
int arr[10];
size_t total_bytes = sizeof(arr);      // 40 on typical systems (10 * 4)
size_t num_elements = sizeof(arr) / sizeof(arr[0]);  // 10
```

This idiom is extremely common for computing array length:

```c
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))

int values[] = {10, 20, 30, 40, 50};
for (size_t i = 0; i < ARRAY_SIZE(values); i++) {
    printf("%d\n", values[i]);
}
```

**Warning**: This only works for actual arrays, not pointers. When an array is passed to a function, it decays to a pointer, and `sizeof` returns the pointer size.

### Array Bounds and Safety

C does not perform runtime bounds checking. Accessing an array out of bounds is undefined behavior.

```c
int arr[5] = {1, 2, 3, 4, 5};
int x = arr[10];    // Undefined behavior - reads garbage or crashes
arr[-1] = 99;       // Undefined behavior - corrupts memory
```

This is a frequent source of security vulnerabilities (buffer overflows). Always ensure your indices are valid.

## Multidimensional Arrays

### Two-Dimensional Arrays

Declare multidimensional arrays with multiple bracket pairs:

```c
int matrix[3][4];  // 3 rows, 4 columns
```

**Row-Major Layout**: C stores multidimensional arrays in row-major order. The array `matrix[3][4]` is laid out as:

```
matrix[0][0], matrix[0][1], matrix[0][2], matrix[0][3],
matrix[1][0], matrix[1][1], matrix[1][2], matrix[1][3],
matrix[2][0], matrix[2][1], matrix[2][2], matrix[2][3]
```

This matters for performance: accessing consecutive elements in a row is cache-friendly.

### Initializing Multidimensional Arrays

You can use nested braces to initialize multidimensional arrays:

```c
int matrix[3][4] = {
    {1, 2, 3, 4},
    {5, 6, 7, 8},
    {9, 10, 11, 12}
};
```

The inner braces can be omitted (elements fill row-by-row), but using them improves clarity:

```c
int matrix[3][4] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};  // Valid but unclear
```

Partial initialization works as expected:

```c
int matrix[3][4] = {{1}, {5}, {9}};  // First column set, rest are 0
```

### Multidimensional Arrays as Function Parameters

When passing multidimensional arrays to functions, all dimensions except the first must be specified:

```c
void print_matrix(int mat[][4], int rows) {
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < 4; j++) {
            printf("%d ", mat[i][j]);
        }
        printf("\n");
    }
}

int matrix[3][4] = { /* ... */ };
print_matrix(matrix, 3);
```

The compiler needs the column count to compute offsets: `mat[i][j]` translates to `*(mat + i*4 + j)`.

**Alternative with Pointers**: You can use a pointer to array:

```c
void print_matrix(int (*mat)[4], int rows) {
    // Same implementation
}
```

**C99 VLA Parameters**: You can use variable-length array syntax for more flexibility:

```c
void print_matrix(int rows, int cols, int mat[rows][cols]) {
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            printf("%d ", mat[i][j]);
        }
        printf("\n");
    }
}
```

Note: dimension parameters must appear before the array parameter.

## Variable-Length Arrays (C99)

C99 introduced variable-length arrays (VLAs), which allow array dimensions to be determined at runtime.

### VLA Declaration

```c
void process_data(int n) {
    int buffer[n];  // Size determined at runtime
    double matrix[n][n];  // 2D VLA

    // Use the arrays...
}
```

### VLA Restrictions

1. **No static or file scope**: VLAs must be automatic (local) variables
2. **No initializers**: You cannot initialize VLAs in their declaration
3. **Size computed once**: The size is evaluated when the VLA is declared and doesn't change

```c
int n = 10;
int arr[n];  // Size is 10
n = 20;      // arr is still size 10, not 20
```

### Stack Allocation Dangers

VLAs are allocated on the stack. Large VLAs can cause stack overflow:

```c
void dangerous(int n) {
    int huge[n];  // If n is 1000000, this will likely crash
}
```

**Best Practice**: Use VLAs only for small, bounded sizes. For large or unbounded data, use `malloc`.

```c
void safer(int n) {
    if (n > 1024) {
        int *buffer = malloc(n * sizeof(int));
        if (!buffer) {
            // Handle allocation failure
            return;
        }
        // Use buffer...
        free(buffer);
    } else {
        int buffer[n];  // Small enough for stack
        // Use buffer...
    }
}
```

### When to Use VLAs

VLAs are convenient for:
- Small temporary buffers with runtime-determined size
- Function parameters with varying dimensions
- Avoiding heap allocation overhead for small arrays

Avoid VLAs for:
- Large arrays (risk of stack overflow)
- Long-lived data (use heap allocation)
- Portable code (C11 made VLAs optional; some compilers don't support them)

## String Fundamentals

### Null-Terminated Convention

In C, strings are arrays of characters terminated by a null character (`'\0'`, which has value 0).

```c
char greeting[6] = {'H', 'e', 'l', 'l', 'o', '\0'};
```

The null terminator is critical - it's how functions like `strlen` and `printf` know where the string ends.

### String Literals

String literals are enclosed in double quotes:

```c
char *message = "Hello, world!";
```

**Storage**: String literals are stored in read-only memory. Attempting to modify them is undefined behavior:

```c
char *str = "Hello";
str[0] = 'h';  // Undefined behavior - may crash
```

String literals have static storage duration - they exist for the entire program execution.

**Automatic Length**: String literals automatically include the null terminator:

```c
"Hello"  // Actually stored as {'H', 'e', 'l', 'l', 'o', '\0'} - 6 bytes
```

### Character Arrays vs Character Pointers

There's a crucial difference between these two declarations:

```c
char arr[] = "Hello";    // Array: modifiable, size 6
char *ptr = "Hello";     // Pointer: points to read-only string literal
```

With the array declaration, the string is copied into the array, which you can modify:

```c
char arr[] = "Hello";
arr[0] = 'h';  // OK - arr is "hello"
```

With the pointer declaration, you're pointing to a literal:

```c
char *ptr = "Hello";
ptr[0] = 'h';  // Undefined behavior - literal is read-only
```

**Best Practice**: If you need to modify a string, use a character array. If it's read-only, use `const char *`:

```c
const char *ptr = "Hello";  // Declares intent that string is read-only
```

### String Initialization

Several ways to initialize strings:

```c
char s1[6] = "Hello";           // Array with exact size
char s2[] = "Hello";            // Compiler computes size (6)
char s3[20] = "Hello";          // Extra space for modification
char s4[] = {'H', 'e', 'l', 'l', 'o', '\0'};  // Character-by-character
```

Partial initialization:

```c
char s[100] = "Hello";  // First 5 chars are "Hello", then '\0', rest zeros
```

## String Library <string.h>

The C standard library provides extensive string manipulation functions. **All require null-terminated strings.**

### String Length

```c
size_t strlen(const char *s);
```

Returns the number of characters before the null terminator (not including it).

```c
char str[] = "Hello";
size_t len = strlen(str);  // 5
```

**Performance Note**: `strlen` must scan the entire string, so it's O(n). Don't call it repeatedly in loops:

```c
// Inefficient
for (size_t i = 0; i < strlen(str); i++) { /* ... */ }

// Better
size_t len = strlen(str);
for (size_t i = 0; i < len; i++) { /* ... */ }
```

### String Copying

```c
char *strcpy(char *dest, const char *src);
char *strncpy(char *dest, const char *src, size_t n);
```

`strcpy` copies `src` to `dest`, including the null terminator. **Danger**: No bounds checking.

```c
char dest[20];
strcpy(dest, "Hello");  // dest is now "Hello"
```

`strncpy` copies at most `n` characters. **Danger**: If `src` is longer than `n`, the result is NOT null-terminated.

```c
char dest[6];
strncpy(dest, "Hello, world!", 5);  // dest is "Hello" (not null-terminated!)
dest[5] = '\0';  // Must add null terminator manually
```

**Safer Alternative**: Use `snprintf` for bounded copying with guaranteed null termination:

```c
char dest[20];
snprintf(dest, sizeof(dest), "%s", src);  // Always null-terminates
```

### String Concatenation

```c
char *strcat(char *dest, const char *src);
char *strncat(char *dest, const char *src, size_t n);
```

`strcat` appends `src` to the end of `dest`. **Danger**: No bounds checking.

```c
char dest[20] = "Hello";
strcat(dest, " world");  // dest is now "Hello world"
```

`strncat` appends at most `n` characters and always null-terminates.

```c
char dest[20] = "Hello";
strncat(dest, " world", 3);  // dest is "Hello wo"
```

### String Comparison

```c
int strcmp(const char *s1, const char *s2);
int strncmp(const char *s1, const char *s2, size_t n);
```

Returns:
- Negative if `s1 < s2`
- Zero if `s1 == s2`
- Positive if `s1 > s2`

```c
if (strcmp(str1, str2) == 0) {
    printf("Strings are equal\n");
}
```

**Common Mistake**: Don't use `==` to compare strings:

```c
if (str1 == str2)  // Wrong! Compares pointers, not contents
```

`strncmp` compares only the first `n` characters:

```c
if (strncmp(str1, "prefix", 6) == 0) {
    printf("str1 starts with 'prefix'\n");
}
```

### String Searching

```c
char *strchr(const char *s, int c);
char *strrchr(const char *s, int c);
char *strstr(const char *haystack, const char *needle);
```

`strchr` finds the first occurrence of character `c`:

```c
char *str = "Hello, world!";
char *p = strchr(str, 'o');  // Points to first 'o' in "Hello"
if (p) {
    printf("Found at position %ld\n", p - str);  // 4
}
```

`strrchr` finds the last occurrence:

```c
char *p = strrchr(str, 'o');  // Points to 'o' in "world"
```

`strstr` finds the first occurrence of a substring:

```c
char *p = strstr("Hello, world!", "world");  // Points to "world!"
```

### Memory Functions

```c
void *memcpy(void *dest, const void *src, size_t n);
void *memmove(void *dest, const void *src, size_t n);
void *memset(void *s, int c, size_t n);
```

These operate on arbitrary memory, not just strings.

`memcpy` copies `n` bytes from `src` to `dest`. **Danger**: Undefined behavior if regions overlap.

```c
char buf1[10] = "Hello";
char buf2[10];
memcpy(buf2, buf1, 6);  // Copies "Hello\0"
```

`memmove` is like `memcpy` but handles overlapping regions correctly:

```c
char buf[20] = "Hello, world!";
memmove(buf + 7, buf, 6);  // buf is "Hello, Hello!"
```

`memset` fills `n` bytes with value `c`:

```c
char buf[100];
memset(buf, 0, sizeof(buf));  // Zero out entire buffer
memset(buf, 'A', 10);          // First 10 bytes are 'A'
```

### String Tokenization

```c
char *strtok(char *str, const char *delim);
```

Breaks a string into tokens separated by delimiters. **Modifies the original string**.

```c
char input[] = "one,two,three";
char *token = strtok(input, ",");
while (token) {
    printf("%s\n", token);
    token = strtok(NULL, ",");  // Continue tokenizing
}
// Output: one, two, three
```

**Important**: `strtok` maintains internal state. Not thread-safe. Use `strtok_r` for reentrant version.

## String Idioms

### Searching for Characters

Find all occurrences of a character:

```c
char *str = "Hello, world!";
char *p = str;
while ((p = strchr(p, 'o')) != NULL) {
    printf("Found 'o' at position %ld\n", p - str);
    p++;  // Move past this occurrence
}
```

### Safe String Copying

Always check buffer sizes:

```c
void safe_copy(char *dest, size_t dest_size, const char *src) {
    if (dest_size > 0) {
        strncpy(dest, src, dest_size - 1);
        dest[dest_size - 1] = '\0';  // Ensure null termination
    }
}
```

Better yet, use `snprintf`:

```c
void safer_copy(char *dest, size_t dest_size, const char *src) {
    snprintf(dest, dest_size, "%s", src);
}
```

### Concatenation Patterns

Building a string from parts:

```c
char result[100] = "";
strcat(result, "Hello");
strcat(result, ", ");
strcat(result, "world");
strcat(result, "!");
// result is "Hello, world!"
```

More efficient with pointer tracking:

```c
char result[100];
char *p = result;
size_t remaining = sizeof(result);

int written = snprintf(p, remaining, "Hello");
p += written; remaining -= written;

written = snprintf(p, remaining, ", world");
p += written; remaining -= written;

snprintf(p, remaining, "!");
```

### Building Strings with sprintf/snprintf

```c
char buffer[100];
int x = 42;
double y = 3.14;
snprintf(buffer, sizeof(buffer), "x=%d, y=%.2f", x, y);
// buffer is "x=42, y=3.14"
```

### Converting Numbers to/from Strings

**String to integer**:

```c
#include <stdlib.h>

int value = atoi("123");  // Simple but no error checking

// Better: use strtol
char *str = "123abc";
char *endptr;
long value = strtol(str, &endptr, 10);  // base 10
if (endptr == str) {
    printf("No conversion performed\n");
} else if (*endptr != '\0') {
    printf("Partial conversion: %ld, stopped at '%s'\n", value, endptr);
}
```

`strtol` provides error detection and can parse different bases:

```c
long hex = strtol("0xFF", NULL, 16);   // 255
long octal = strtol("077", NULL, 8);   // 63
long auto_base = strtol("0xFF", NULL, 0);  // Auto-detect base
```

**Integer to string**:

```c
char buffer[20];
int value = 12345;
snprintf(buffer, sizeof(buffer), "%d", value);
// buffer is "12345"

// With formatting
snprintf(buffer, sizeof(buffer), "%06d", value);
// buffer is "012345"
```

## Common String Pitfalls

### Buffer Overflow

The most dangerous string error:

```c
char buffer[10];
strcpy(buffer, "This string is too long");  // Buffer overflow!
```

**Prevention**: Always use bounded functions and check sizes:

```c
char buffer[10];
if (strlen(src) < sizeof(buffer)) {
    strcpy(buffer, src);
} else {
    // Handle error
}

// Or use snprintf
snprintf(buffer, sizeof(buffer), "%s", src);
```

### Missing Null Terminator

```c
char buffer[6];
strncpy(buffer, "Hello, world!", 5);  // No null terminator!
printf("%s\n", buffer);  // Undefined behavior
```

**Fix**: Always ensure null termination:

```c
strncpy(buffer, src, sizeof(buffer) - 1);
buffer[sizeof(buffer) - 1] = '\0';
```

### Modifying String Literals

```c
char *str = "Hello";
str[0] = 'h';  // Undefined behavior - crashes on some systems
```

**Fix**: Use array or dynamic allocation:

```c
char str[] = "Hello";  // Now modifiable
str[0] = 'h';  // OK
```

### Off-by-One in Allocation

Forgetting space for the null terminator:

```c
char *str = malloc(strlen(src));  // Wrong! Need +1 for '\0'
strcpy(str, src);  // Buffer overflow

// Correct
char *str = malloc(strlen(src) + 1);
strcpy(str, src);
```

### strncpy Not Null-Terminating

A subtle gotcha:

```c
char dest[10];
strncpy(dest, "Hello", sizeof(dest));  // OK, null-terminated

strncpy(dest, "This is too long", sizeof(dest));  // NOT null-terminated!
```

`strncpy` only null-terminates if the source fits within `n` characters.

**Solution**: Manually ensure termination:

```c
strncpy(dest, src, sizeof(dest) - 1);
dest[sizeof(dest) - 1] = '\0';
```

### Using strlen on Non-Null-Terminated Arrays

```c
char buffer[10];
memcpy(buffer, "Hello", 5);  // No null terminator
size_t len = strlen(buffer);  // Undefined - reads past buffer
```

**Fix**: Ensure null termination or use `memchr` to search for it:

```c
const char *end = memchr(buffer, '\0', sizeof(buffer));
size_t len = end ? (end - buffer) : sizeof(buffer);
```

## Arrays of Strings

### Array of Character Arrays

Each string is a fixed-size character array:

```c
char names[3][20] = {
    "Alice",
    "Bob",
    "Charlie"
};

printf("%s\n", names[1]);  // "Bob"
```

This allocates `3 * 20 = 60` bytes, even if strings are shorter. Wastes memory but is simple and allows modification.

### Array of Character Pointers

More memory-efficient for read-only strings:

```c
const char *names[] = {
    "Alice",
    "Bob",
    "Charlie"
};

printf("%s\n", names[1]);  // "Bob"
```

This allocates only enough space for each string plus the pointer array. Strings point to read-only literals.

**Choosing**: Use pointer array for read-only strings of varying length. Use character array array when you need to modify strings.

### Command-Line Arguments

The `main` function can accept command-line arguments:

```c
int main(int argc, char *argv[]) {
    printf("Program name: %s\n", argv[0]);
    printf("Arguments:\n");
    for (int i = 1; i < argc; i++) {
        printf("  argv[%d]: %s\n", i, argv[i]);
    }
    return 0;
}
```

- `argc`: Argument count (includes program name)
- `argv`: Array of argument strings
- `argv[0]`: Program name
- `argv[1]` through `argv[argc-1]`: Command-line arguments
- `argv[argc]`: NULL pointer

Example run:

```
$ ./program hello world
Program name: ./program
Arguments:
  argv[1]: hello
  argv[2]: world
```

**Parsing Arguments**: Typically you check `argc` and parse `argv`:

```c
if (argc != 3) {
    fprintf(stderr, "Usage: %s <input> <output>\n", argv[0]);
    return 1;
}

const char *input_file = argv[1];
const char *output_file = argv[2];
```

For complex argument parsing, consider libraries like `getopt` (POSIX) or third-party argument parsers.

## Summary

**Arrays**:
- Fixed-size, no bounds checking
- Use `sizeof(arr)/sizeof(arr[0])` for length
- Multidimensional arrays are row-major; specify all but first dimension in parameters
- VLAs are convenient but dangerous for large sizes

**Strings**:
- Always null-terminated (`'\0'`)
- String literals are read-only
- `char arr[]` is modifiable; `char *ptr` to literal is not
- Use `<string.h>` functions but beware of buffer overflows
- Prefer bounded functions: `strncpy`, `strncat`, `snprintf`
- Always ensure null termination
- Watch for off-by-one errors in allocation

**Best Practices**:
- Validate array/buffer sizes before operations
- Use `const char *` for read-only strings
- Prefer `snprintf` over `strcpy`/`strcat` for safety
- Use `strtol` instead of `atoi` for error checking
- Remember to allocate `strlen(str) + 1` for string copies
