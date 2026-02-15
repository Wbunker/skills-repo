# C Standard Library Reference

This reference covers the C Standard Library facilities defined in C89/C90, C99, C11, and C23, focusing on practical usage patterns and common pitfalls.

## Standard Library Overview

The C Standard Library is a collection of headers providing standardized functions and macros. Every conforming implementation must provide these facilities.

### Header Files

Standard headers are included using angle brackets:
```c
#include <stdio.h>
#include <stdlib.h>
```

Common headers include: `<assert.h>`, `<ctype.h>`, `<errno.h>`, `<float.h>`, `<limits.h>`, `<locale.h>`, `<math.h>`, `<setjmp.h>`, `<signal.h>`, `<stdarg.h>`, `<stddef.h>`, `<stdio.h>`, `<stdlib.h>`, `<string.h>`, `<time.h>`.

C99 added: `<complex.h>`, `<fenv.h>`, `<inttypes.h>`, `<iso646.h>`, `<stdbool.h>`, `<stdint.h>`, `<tgmath.h>`, `<wchar.h>`, `<wctype.h>`.

C11 added: `<stdalign.h>`, `<stdatomic.h>`, `<stdnoreturn.h>`, `<threads.h>`, `<uchar.h>`.

C23 added: `<stdbit.h>` and `<stdckdint.h>`.

### Reserved Identifiers

The Standard reserves certain identifier patterns for library implementation:

1. **Identifiers beginning with underscore followed by uppercase letter** (`_X`, `_FOO`) - reserved in all scopes
2. **Identifiers beginning with two underscores** (`__anything`) - reserved in all scopes
3. **Identifiers beginning with single underscore** (`_lowercase`) - reserved in the global namespace
4. **Standard library names** - reserved when corresponding header is included

**Never define your own identifiers matching these patterns.** Violation leads to undefined behavior.

```c
// BAD - reserved patterns
int _Bool;      // Reserved
int __counter;  // Reserved
int _Atomic;    // Reserved

// GOOD - safe user identifiers
int counter_;   // OK
int my_value;   // OK (if not in global scope without underscore prefix)
```

## `<stdlib.h>` - General Utilities

### String to Number Conversion

#### Basic Conversion: `atoi`, `atol`, `atoll`

```c
int atoi(const char *str);
long atol(const char *str);
long long atoll(const char *str);  // C99
```

These functions skip leading whitespace, then parse an optional sign and digits. **No error reporting** - invalid input returns 0.

```c
int n = atoi("  -42");      // -42
int bad = atoi("xyz");      // 0 (no error indication!)
int overflow = atoi("99999999999");  // Undefined behavior
```

**Avoid `atoi` family.** Use `strtol` family instead for robust error handling.

#### Robust Conversion: `strtol` Family

```c
long strtol(const char *str, char **endptr, int base);
unsigned long strtoul(const char *str, char **endptr, int base);
long long strtoll(const char *str, char **endptr, int base);        // C99
unsigned long long strtoull(const char *str, char **endptr, int base); // C99
```

- `base`: 0 (auto-detect), 2-36
- `endptr`: if non-NULL, receives pointer to first unconverted character
- Returns converted value; sets `errno` to `ERANGE` on overflow

```c
#include <stdlib.h>
#include <errno.h>

char *str = "  123abc";
char *end;
errno = 0;
long val = strtol(str, &end, 10);

if (end == str) {
    // No conversion performed
} else if (*end != '\0') {
    // Extra characters after number
} else if (errno == ERANGE) {
    // Overflow/underflow occurred
} else {
    // Success: val = 123
}
```

Base 0 auto-detection: `0x` prefix = hex, `0` prefix = octal, else decimal.

#### Floating-Point Conversion

```c
double strtod(const char *str, char **endptr);
float strtof(const char *str, char **endptr);          // C99
long double strtold(const char *str, char **endptr);   // C99
```

Handles `INF`, `INFINITY`, `NAN`, `NAN(...)` (C99).

```c
double d = strtod("3.14159", NULL);
double inf = strtod("INFINITY", NULL);  // C99
```

### Pseudo-Random Numbers

```c
int rand(void);              // Returns 0 to RAND_MAX
void srand(unsigned seed);   // Seed the generator
```

**LIMITATIONS**: `rand()` is notoriously poor quality. Not cryptographically secure. Implementation-defined algorithm.

```c
#include <stdlib.h>
#include <time.h>

srand(time(NULL));  // Seed with current time
int dice = rand() % 6 + 1;  // 1-6 (modulo bias!)

// Better: for range [0, n)
int random_in_range(int n) {
    int limit = RAND_MAX - (RAND_MAX % n);
    int r;
    while ((r = rand()) >= limit)
        ;
    return r % n;
}
```

**Modern alternative**: Use platform-specific APIs (`arc4random` on BSD/macOS, `getrandom` on Linux, `rand_s` on Windows) or third-party libraries for quality random numbers.

### Dynamic Memory Allocation

```c
void *malloc(size_t size);
void *calloc(size_t nmemb, size_t size);
void *realloc(void *ptr, size_t size);
void free(void *ptr);
```

#### `malloc`

Allocates `size` bytes; returns pointer or NULL on failure. **Memory is uninitialized.**

```c
int *arr = malloc(100 * sizeof(int));
if (!arr) {
    perror("malloc");
    exit(1);
}
// Use arr...
free(arr);
```

**Always multiply by `sizeof(type)`** to ensure correct size. Always check for NULL.

#### `calloc`

Allocates array of `nmemb` elements of `size` bytes each. **Memory is zero-initialized.**

```c
int *arr = calloc(100, sizeof(int));  // All zeros
```

Prefer `calloc` when zero-initialization is desired. Also detects overflow in `nmemb * size`.

#### `realloc`

Resizes previously allocated memory.

```c
void *realloc(void *ptr, size_t new_size);
```

- If `ptr` is NULL, equivalent to `malloc(new_size)`
- If `new_size` is 0, behavior is implementation-defined (often equivalent to `free(ptr)`)
- May move the block; old pointer is invalidated
- Returns NULL on failure; **original block remains valid**

```c
int *arr = malloc(100 * sizeof(int));
// ... need more space ...
int *temp = realloc(arr, 200 * sizeof(int));
if (!temp) {
    // Original arr still valid
    free(arr);
    exit(1);
}
arr = temp;  // Update pointer
```

**Common mistake**: `arr = realloc(arr, new_size)` loses the original pointer on failure.

#### `free`

Deallocates memory. Passing NULL is safe (no operation). **Never free the same pointer twice** (undefined behavior). **Never use freed memory** (undefined behavior).

### Program Termination

```c
void exit(int status);
void _Exit(int status);      // C99
_Noreturn void abort(void);  // C11 adds _Noreturn
int atexit(void (*func)(void));
```

#### `exit`

Terminates program normally:
1. Calls functions registered with `atexit` (reverse order)
2. Flushes and closes open streams
3. Removes temporary files created with `tmpfile`
4. Returns `status` to environment

`EXIT_SUCCESS` (0) and `EXIT_FAILURE` (non-zero) are portable status codes.

```c
exit(EXIT_SUCCESS);
```

#### `_Exit`

Terminates immediately without cleanup (no `atexit` functions, no stream flushing). Use for abnormal termination scenarios.

#### `atexit`

Registers cleanup function called at normal program termination.

```c
void cleanup(void) {
    printf("Cleaning up...\n");
}

int main(void) {
    if (atexit(cleanup) != 0) {
        fprintf(stderr, "atexit failed\n");
        return 1;
    }
    // ...
    return 0;  // cleanup() called automatically
}
```

At least 32 functions can be registered (implementation may allow more).

#### `abort`

Causes abnormal termination. Raises `SIGABRT` signal. Does not call `atexit` functions or flush streams.

### Searching and Sorting

#### `qsort`

```c
void qsort(void *base, size_t nmemb, size_t size,
           int (*compar)(const void *, const void *));
```

Sorts array in-place. Comparison function returns negative, zero, or positive for less-than, equal, greater-than.

```c
int compare_ints(const void *a, const void *b) {
    int arg1 = *(const int*)a;
    int arg2 = *(const int*)b;
    return (arg1 > arg2) - (arg1 < arg2);  // Avoid subtraction overflow
}

int arr[] = {5, 2, 8, 1, 9};
qsort(arr, 5, sizeof(int), compare_ints);
```

**Warning**: Avoid `return arg1 - arg2` pattern - can overflow.

#### `bsearch`

```c
void *bsearch(const void *key, const void *base, size_t nmemb,
              size_t size, int (*compar)(const void *, const void *));
```

Binary search in sorted array. Returns pointer to matching element or NULL.

```c
int key = 8;
int *found = bsearch(&key, arr, 5, sizeof(int), compare_ints);
if (found)
    printf("Found: %d\n", *found);
```

**Array must be sorted** with same comparison function.

### Arithmetic Functions

```c
int abs(int n);
long labs(long n);
long long llabs(long long n);  // C99

div_t div(int numer, int denom);
ldiv_t ldiv(long numer, long denom);
lldiv_t lldiv(long long numer, long long denom);  // C99
```

`abs` family: Returns absolute value. **Undefined for most negative value** of signed types.

`div` family: Computes quotient and remainder simultaneously.

```c
div_t result = div(17, 5);
printf("%d / %d = %d remainder %d\n", 17, 5, result.quot, result.rem);
// Output: 17 / 5 = 3 remainder 2
```

### Environment and System

```c
char *getenv(const char *name);
int system(const char *command);
```

`getenv`: Retrieves environment variable. Returns NULL if not found. **Never modify returned string.**

```c
char *path = getenv("PATH");
if (path)
    printf("PATH=%s\n", path);
```

`system`: Executes shell command. Returns implementation-defined value. Passing NULL tests if shell is available.

```c
if (system(NULL))
    system("ls -l");  // Execute command
```

**Security warning**: Never pass user input directly to `system` - shell injection vulnerability.

## `<math.h>` - Mathematics

All functions operate on `double` by default. C99 added `float` and `long double` variants (suffix `f` and `l`).

### Trigonometric Functions

```c
double sin(double x);     // Sine
double cos(double x);     // Cosine
double tan(double x);     // Tangent
double asin(double x);    // Arc sine [-1, 1] -> [-π/2, π/2]
double acos(double x);    // Arc cosine [-1, 1] -> [0, π]
double atan(double x);    // Arc tangent (-∞, ∞) -> (-π/2, π/2)
double atan2(double y, double x);  // Arc tangent of y/x, using signs for quadrant
```

Angles in radians. `atan2` handles all quadrants and avoids division by zero.

```c
double angle = atan2(y, x);  // Correctly handles (0,0), signs
```

C99 added hyperbolic variants: `sinh`, `cosh`, `tanh`, `asinh`, `acosh`, `atanh`.

### Exponential and Logarithmic Functions

```c
double exp(double x);     // e^x
double log(double x);     // Natural logarithm (base e)
double log10(double x);   // Common logarithm (base 10)
```

C99 additions:
```c
double exp2(double x);    // 2^x
double log2(double x);    // log base 2
double log1p(double x);   // log(1 + x), accurate for small x
double expm1(double x);   // e^x - 1, accurate for small x
```

### Power and Root Functions

```c
double pow(double x, double y);   // x^y
double sqrt(double x);            // Square root
double cbrt(double x);            // Cube root (C99)
double hypot(double x, double y); // sqrt(x^2 + y^2) without overflow (C99)
```

`hypot` is preferred over manual `sqrt(x*x + y*y)` to avoid intermediate overflow/underflow.

### Rounding and Remainder Functions

```c
double ceil(double x);    // Smallest integer >= x
double floor(double x);   // Largest integer <= x
double fabs(double x);    // Absolute value
double fmod(double x, double y);  // Floating-point remainder of x/y
```

C99 additions:
```c
double trunc(double x);       // Round toward zero
double round(double x);       // Round to nearest, halfway cases away from zero
long lround(double x);        // Round and convert to long
long long llround(double x);  // Round and convert to long long
double nearbyint(double x);   // Round per current rounding mode
double rint(double x);        // Round per current rounding mode, may raise exception
double remainder(double x, double y);  // IEEE remainder
```

### Manipulation Functions

```c
double modf(double x, double *iptr);  // Split into integer and fractional parts
double frexp(double x, int *exp);     // x = mantissa * 2^exp, returns mantissa
double ldexp(double x, int exp);      // x * 2^exp
double scalbn(double x, int n);       // x * FLT_RADIX^n (C99)
double copysign(double x, double y);  // Value of x with sign of y (C99)
```

### Other C99 Mathematical Functions

```c
double fma(double x, double y, double z);  // x*y + z as single operation
double fdim(double x, double y);           // Positive difference: max(x-y, 0)
double fmax(double x, double y);           // Maximum
double fmin(double x, double y);           // Minimum
```

`fma` (fused multiply-add) performs the operation with single rounding, more accurate than separate multiply and add.

### Classification and Comparison (C99)

```c
int isnan(x);       // True if x is NaN
int isinf(x);       // True if x is infinity
int isfinite(x);    // True if x is finite
int isnormal(x);    // True if x is normalized
int signbit(x);     // True if sign bit is set

int fpclassify(x);  // Returns FP_NAN, FP_INFINITE, FP_ZERO, FP_SUBNORMAL, FP_NORMAL
```

These are type-generic macros working with `float`, `double`, or `long double`.

```c
if (isnan(result)) {
    fprintf(stderr, "Result is NaN\n");
}
```

### Special Values (C99)

```c
#define NAN       /* Quiet NaN */
#define INFINITY  /* Positive infinity */
```

Check if available with `#ifdef`.

### Type-Generic Math: `<tgmath.h>` (C99)

Provides type-generic macros that dispatch to appropriate function based on argument types.

```c
#include <tgmath.h>

float f = 1.5f;
double d = 1.5;
long double ld = 1.5L;

sqrt(f);   // Calls sqrtf
sqrt(d);   // Calls sqrt
sqrt(ld);  // Calls sqrtl
```

Reduces verbosity and type errors. Works with complex types too.

## `<ctype.h>` - Character Handling

Functions take `int` argument (usually `unsigned char` or EOF). **Result is undefined if argument is not representable as `unsigned char` and not EOF.**

### Character Classification

```c
int isalpha(int c);   // Letter
int isdigit(int c);   // Decimal digit
int isalnum(int c);   // Alphanumeric
int isspace(int c);   // Whitespace (space, tab, newline, etc.)
int isupper(int c);   // Uppercase letter
int islower(int c);   // Lowercase letter
int isprint(int c);   // Printable (including space)
int isgraph(int c);   // Printable (excluding space)
int ispunct(int c);   // Punctuation
int iscntrl(int c);   // Control character
int isxdigit(int c);  // Hexadecimal digit
```

C99 added: `isblank(int c)` - space or tab.

Return non-zero (true) or zero (false).

```c
if (isdigit(c))
    digit_value = c - '0';
```

### Character Conversion

```c
int toupper(int c);  // Convert to uppercase if lowercase, else unchanged
int tolower(int c);  // Convert to lowercase if uppercase, else unchanged
```

```c
char ch = 'a';
ch = toupper(ch);  // 'A'
```

### Locale Dependence

**Warning**: Some functions (`isalpha`, `isupper`, `islower`, `toupper`, `tolower`) are locale-dependent. In non-"C" locales, they may recognize accented characters.

For portable ASCII-only checks, compare directly:
```c
int is_ascii_digit(int c) {
    return c >= '0' && c <= '9';
}
```

### Cast Requirement

**Critical**: When passing `char` to `<ctype.h>` functions, cast to `unsigned char` to avoid undefined behavior with negative values:

```c
char c = getchar();
if (isdigit((unsigned char)c))  // CORRECT
    // ...

// BAD: if c is negative (non-ASCII), undefined behavior
if (isdigit(c))  // WRONG for signed char
```

Or ensure variable is `unsigned char` or `int` from functions returning `int` (like `getchar`).

## `<string.h>` - Memory Functions

Beyond string functions, `<string.h>` provides memory manipulation:

```c
void *memcpy(void *dest, const void *src, size_t n);
void *memmove(void *dest, const void *src, size_t n);
void *memset(void *s, int c, size_t n);
int memcmp(const void *s1, const void *s2, size_t n);
void *memchr(const void *s, int c, size_t n);
```

- `memcpy`: Copies `n` bytes from `src` to `dest`. **Regions must not overlap.**
- `memmove`: Like `memcpy` but handles overlapping regions correctly.
- `memset`: Fills `n` bytes of `s` with byte `c` (converted to `unsigned char`).
- `memcmp`: Compares `n` bytes; returns <0, 0, >0.
- `memchr`: Searches for byte `c` in first `n` bytes of `s`; returns pointer or NULL.

```c
int arr[100];
memset(arr, 0, sizeof(arr));  // Zero out array

// Copy with potential overlap - use memmove
memmove(arr + 1, arr, 99 * sizeof(int));
```

**Common mistake**: `memset(arr, 1, sizeof(arr))` sets each *byte* to 1, not each element. For integers, this gives unexpected values. Use a loop for non-zero initialization:

```c
for (int i = 0; i < 100; i++)
    arr[i] = 1;
```

## `<errno.h>` - Error Numbers

```c
extern int errno;  // Thread-local in C11
```

Error indicator set by library functions on error. **Not cleared on success**, so check only when function indicates error.

Standard error codes:
- `EDOM`: Domain error (mathematical function argument out of range)
- `ERANGE`: Range error (result overflow/underflow)
- `EILSEQ`: Illegal byte sequence (multibyte conversion)

POSIX defines many more (`ENOENT`, `ENOMEM`, etc.).

### Proper Usage Pattern

```c
#include <errno.h>
#include <math.h>

errno = 0;  // Clear before call
double result = sqrt(-1.0);
if (errno == EDOM) {
    perror("sqrt");  // Prints "sqrt: Numerical argument out of domain"
}
```

**Always clear `errno` before library call** if you intend to check it. Functions are not required to clear it on success.

### Error Reporting Functions

```c
char *strerror(int errnum);  // Returns error message string
void perror(const char *s);  // Prints s, colon, error message for current errno
```

```c
FILE *f = fopen("nonexistent.txt", "r");
if (!f) {
    perror("fopen");  // "fopen: No such file or directory"
    // Or:
    fprintf(stderr, "fopen: %s\n", strerror(errno));
}
```

`strerror` returns pointer to static string; **do not modify**.

## `<assert.h>` - Diagnostics

```c
void assert(scalar expression);  // Macro
_Static_assert(constant-expression, string-literal);  // C11
static_assert(constant-expression);  // C23 (optional message)
```

### Runtime Assertions: `assert`

If expression is false (zero), prints diagnostic and calls `abort()`.

```c
#include <assert.h>

void process_array(int *arr, size_t len) {
    assert(arr != NULL);
    assert(len > 0);
    // ...
}
```

Disabled by defining `NDEBUG` before including `<assert.h>`:

```c
#define NDEBUG
#include <assert.h>
// Now assert() does nothing
```

Typically, build in debug mode with assertions enabled, release mode with `NDEBUG`.

**When to use assertions**:
- Document invariants and preconditions
- Check "can't happen" conditions
- Debug aid, not error handling

**When NOT to use assertions**:
- Checking user input (use explicit error handling)
- Checking external resources (files, network)
- Expressions with side effects (disabled in release builds)

```c
// BAD: side effect in assertion
assert(fclose(file) == 0);  // fclose not called if NDEBUG defined!

// GOOD:
int rc = fclose(file);
assert(rc == 0);
```

### Compile-Time Assertions: `_Static_assert` / `static_assert`

Checks condition at compile time. Fails compilation if false.

```c
_Static_assert(sizeof(int) == 4, "int must be 4 bytes");  // C11

// C23: message optional
static_assert(sizeof(int) == 4);
```

Useful for portability checks, struct size verification, etc.

## `<signal.h>` - Signal Handling

```c
void (*signal(int sig, void (*handler)(int)))(int);
int raise(int sig);

typedef /* implementation-defined */ sig_atomic_t;
```

### Standard Signals

- `SIGABRT`: Abort (from `abort()`)
- `SIGFPE`: Floating-point exception (division by zero, overflow)
- `SIGILL`: Illegal instruction
- `SIGINT`: Interactive interrupt (Ctrl+C)
- `SIGSEGV`: Segmentation violation (invalid memory access)
- `SIGTERM`: Termination request

### Signal Handlers

`signal` installs handler for signal `sig`. Special handlers:
- `SIG_DFL`: Default behavior
- `SIG_IGN`: Ignore signal

```c
#include <signal.h>
#include <stdio.h>

void handle_sigint(int sig) {
    printf("Caught SIGINT\n");
    signal(SIGINT, SIG_DFL);  // Restore default for next
}

int main(void) {
    signal(SIGINT, handle_sigint);
    // ...
}
```

### `raise`

Sends signal to current program.

```c
raise(SIGABRT);  // Equivalent to abort(), but handler may catch it
```

### `sig_atomic_t`

Integer type that can be accessed atomically even in presence of asynchronous signals.

```c
volatile sig_atomic_t signal_received = 0;

void handler(int sig) {
    signal_received = 1;  // Safe
}
```

### Severe Limitations

**Signal handlers are extremely restricted**. Calling most library functions from a handler invokes undefined behavior. Only safe operations:
- Assign to `volatile sig_atomic_t` variable
- Call `signal()` to reinstall handler
- Return from handler

**DO NOT**:
- Call `printf`, `malloc`, or most library functions
- Access non-`volatile sig_atomic_t` variables (race conditions)
- Use `longjmp` (except for specific signals like `SIGFPE`, `SIGILL`, `SIGSEGV` - even this is fraught)

**Modern practice**: Use platform-specific APIs (`sigaction` on POSIX) or avoid signals entirely. C11 added `<threads.h>` for better concurrency primitives.

## `<setjmp.h>` - Non-Local Jumps

```c
typedef /* implementation-defined */ jmp_buf;

int setjmp(jmp_buf env);              // Returns 0 initially, non-zero from longjmp
void longjmp(jmp_buf env, int val);   // Jumps to setjmp, returning val
```

Provides a form of goto that can jump across function boundaries.

### Usage Pattern

```c
#include <setjmp.h>

jmp_buf error_env;

void deep_function(void) {
    if (/* error */)
        longjmp(error_env, 1);  // Jump back to setjmp
}

int main(void) {
    if (setjmp(error_env) != 0) {
        // Returned from longjmp - handle error
        printf("Error occurred\n");
        return 1;
    }

    // Normal execution
    deep_function();
    return 0;
}
```

`setjmp` saves execution context in `env`. `longjmp` restores that context, making `setjmp` appear to return again with value `val` (forced to 1 if 0 passed).

### Use Cases

- Error recovery in deeply nested calls (before exceptions in C++)
- Implementing coroutines/state machines
- Escape from signal handlers (dangerous)

### Dangers and Limitations

1. **Automatic variables**: If function containing `setjmp` has local variables modified between `setjmp` and `longjmp`, their values after `longjmp` are indeterminate unless declared `volatile`.

```c
int value = 1;
if (setjmp(env) == 0) {
    value = 2;  // Modified
    longjmp(env, 1);
}
// value may be 1 or 2 here unless volatile!

volatile int safe_value = 1;  // This is safe
```

2. **Stack unwinding**: No destructors called (C has no destructors, but relevant in C++)
3. **Jumped-to function must still be active**: Returning from function that called `setjmp` makes `jmp_buf` invalid
4. **Restricted contexts**: `setjmp` can only appear in simple contexts (if condition, switch, loop condition, etc.)

**Modern alternative**: In most cases, explicit error codes or state machines are clearer.

## `<stdint.h>` and `<inttypes.h>` - Fixed-Width Integers (C99)

### `<stdint.h>` Types

#### Exact-Width Integers

```c
int8_t, int16_t, int32_t, int64_t
uint8_t, uint16_t, uint32_t, uint64_t
```

**Optional** - only defined if implementation supports these sizes exactly. Most modern platforms provide them.

#### Minimum-Width Integers

```c
int_least8_t, int_least16_t, int_least32_t, int_least64_t
uint_least8_t, uint_least16_t, uint_least32_t, uint_least64_t
```

**Required** - smallest type with at least the specified width.

#### Fastest Integers

```c
int_fast8_t, int_fast16_t, int_fast32_t, int_fast64_t
uint_fast8_t, uint_fast16_t, uint_fast32_t, uint_fast64_t
```

**Required** - fastest type with at least the specified width. May be larger than requested (e.g., `int_fast8_t` might be 32-bit).

#### Pointer and Maximum-Width Integers

```c
intptr_t, uintptr_t    // Optional: can hold pointer value
intmax_t, uintmax_t    // Required: widest integer type
```

`intptr_t` useful for pointer arithmetic tricks. `intmax_t` for generic "biggest integer" needs.

#### Limits

Macros define limits: `INT8_MIN`, `INT8_MAX`, `UINT8_MAX`, `INT_LEAST16_MIN`, `INT_FAST32_MAX`, `INTMAX_MIN`, `INTMAX_MAX`, `UINTMAX_MAX`, `INTPTR_MIN`, `INTPTR_MAX`, `UINTPTR_MAX`, etc.

### `<inttypes.h>` Format Macros

Provides `printf`/`scanf` format specifiers for fixed-width types.

```c
#include <inttypes.h>

int64_t big = 1234567890123LL;
printf("Value: %" PRId64 "\n", big);

uint32_t u = 42;
printf("Hex: %" PRIx32 "\n", u);

int64_t scanned;
scanf("%" SCNd64, &scanned);
```

**Format macro families**:
- `PRIdN`, `PRIiN`: signed decimal
- `PRIuN`: unsigned decimal
- `PRIxN`, `PRIXN`: unsigned hex (lowercase/uppercase)
- `PRIoN`: unsigned octal
- `SCNdN`, `SCNiN`, `SCNuN`, `SCNxN`, `SCNoN`: scanf equivalents

Replace `N` with 8, 16, 32, 64, LEAST8, LEAST16, FAST32, MAX, PTR, etc.

**Why needed**: `int64_t` might be `long` or `long long` depending on platform. Format macros ensure portability.

```c
// Portable:
printf("%" PRId64 "\n", val);

// Non-portable (may warn or print incorrectly):
printf("%lld\n", val);  // Assumes long long
```

## `<stdbool.h>` - Boolean Type (C99)

```c
#define bool  _Bool
#define true  1
#define false 0
#define __bool_true_false_are_defined 1
```

Provides convenient boolean type.

```c
#include <stdbool.h>

bool is_valid(int x) {
    return x >= 0 && x <= 100;
}

bool flag = true;
if (flag) {
    // ...
}
```

`_Bool` is a built-in unsigned integer type (C99) with values 0 or 1. Any scalar assigned to `_Bool` is converted to 0 (if zero) or 1 (if non-zero).

**Note**: Before C99, common to use `int` or `typedef` for booleans. `<stdbool.h>` standardizes this.

## `<time.h>` - Date and Time

### Types

```c
typedef /* arithmetic type */ time_t;     // Seconds since epoch (usually)
typedef /* arithmetic type */ clock_t;    // Processor time
struct tm {                               // Broken-down time
    int tm_sec;    // Seconds [0, 60] (60 for leap second)
    int tm_min;    // Minutes [0, 59]
    int tm_hour;   // Hours [0, 23]
    int tm_mday;   // Day of month [1, 31]
    int tm_mon;    // Month [0, 11]
    int tm_year;   // Years since 1900
    int tm_wday;   // Day of week [0, 6] (Sunday = 0)
    int tm_yday;   // Day of year [0, 365]
    int tm_isdst;  // Daylight saving time flag
};
```

### Time Functions

```c
time_t time(time_t *timer);              // Current calendar time
double difftime(time_t time1, time_t time0);  // Difference in seconds
clock_t clock(void);                     // Processor time used
```

```c
time_t now = time(NULL);
printf("Seconds since epoch: %ld\n", (long)now);

clock_t start = clock();
// ... work ...
clock_t end = clock();
double cpu_time = (double)(end - start) / CLOCKS_PER_SEC;
printf("CPU time: %f seconds\n", cpu_time);
```

### Conversion Functions

```c
struct tm *gmtime(const time_t *timer);     // Convert to UTC
struct tm *localtime(const time_t *timer);  // Convert to local time
time_t mktime(struct tm *timeptr);          // Convert struct tm to time_t
```

**Warning**: `gmtime` and `localtime` return pointer to static storage, overwritten on next call. Use `gmtime_r`/`localtime_r` (POSIX) for thread safety.

```c
time_t now = time(NULL);
struct tm *local = localtime(&now);
printf("Year: %d\n", local->tm_year + 1900);
printf("Month: %d\n", local->tm_mon + 1);
```

### Formatting Time

```c
size_t strftime(char *s, size_t maxsize, const char *format, const struct tm *timeptr);
```

Formats time according to format string. Returns number of characters written (excluding null terminator) or 0 if doesn't fit.

```c
char buf[100];
time_t now = time(NULL);
struct tm *local = localtime(&now);
strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", local);
printf("%s\n", buf);  // "2026-02-15 14:30:00"
```

Common format specifiers:
- `%Y`: Year (4 digits)
- `%m`: Month [01, 12]
- `%d`: Day [01, 31]
- `%H`: Hour [00, 23]
- `%M`: Minute [00, 59]
- `%S`: Second [00, 60]
- `%A`: Full weekday name
- `%B`: Full month name
- `%c`: Locale-appropriate date and time
- `%Z`: Timezone name

### Legacy Functions

```c
char *asctime(const struct tm *timeptr);  // Convert to string (deprecated)
char *ctime(const time_t *timer);         // Convert to string (deprecated)
```

Return fixed-format strings like `"Sun Feb 15 14:30:00 2026\n"`. **Deprecated** - use `strftime` instead.

## C11/C23 Additions

### `<threads.h>` Overview (C11, Optional)

Provides portable threading API:
- `thrd_t`: Thread type
- `mtx_t`: Mutex type
- `cnd_t`: Condition variable type
- Functions: `thrd_create`, `thrd_join`, `mtx_lock`, `mtx_unlock`, `cnd_wait`, `cnd_signal`, etc.

**Optional feature**: Check `__STDC_NO_THREADS__` macro. Many implementations do not provide this. POSIX `pthread` is more widely used.

### `_Generic` (C11)

Type-generic selection, foundation of type-generic macros.

```c
#define abs_generic(x) _Generic((x), \
    int: abs(x), \
    long: labs(x), \
    long long: llabs(x), \
    float: fabsf(x), \
    double: fabs(x), \
    long double: fabsl(x))

int i = -5;
double d = -3.14;
abs_generic(i);     // Calls abs
abs_generic(d);     // Calls fabs
```

Used internally by `<tgmath.h>` and custom generic interfaces.

### `<stdatomic.h>` Overview (C11, Optional)

Provides atomic types and operations for lock-free programming:
- `atomic_int`, `atomic_llong`, `atomic_uint`, etc.
- `atomic_load`, `atomic_store`, `atomic_fetch_add`, `atomic_compare_exchange_weak`, etc.
- Memory order specifiers: `memory_order_relaxed`, `memory_order_acquire`, `memory_order_release`, etc.

```c
#include <stdatomic.h>

atomic_int counter = ATOMIC_VAR_INIT(0);
atomic_fetch_add(&counter, 1);
```

**Complex topic** requiring deep understanding of memory models. Optional feature.

### `<stdbit.h>` (C23)

Bit manipulation utilities (new in C23):
- `stdc_leading_zeros`, `stdc_leading_ones`
- `stdc_trailing_zeros`, `stdc_trailing_ones`
- `stdc_first_leading_zero`, `stdc_first_leading_one`
- `stdc_first_trailing_zero`, `stdc_first_trailing_one`
- `stdc_count_zeros`, `stdc_count_ones`
- `stdc_has_single_bit`, `stdc_bit_width`, `stdc_bit_floor`, `stdc_bit_ceil`

Type-generic macros operating on unsigned integer types. Many map to compiler intrinsics.

```c
#include <stdbit.h>

unsigned x = 0b00011000;
stdc_count_ones(x);         // 2
stdc_leading_zeros(x);      // 27 (on 32-bit unsigned)
stdc_has_single_bit(x);     // false (multiple bits set)
stdc_bit_ceil(x);           // 32 (next power of 2)
```

### Alignment: `<stdalign.h>` (C11)

```c
#define alignas _Alignas
#define alignof _Alignof
#define __alignas_is_defined 1
#define __alignof_is_defined 1
```

Provides convenient aliases for alignment specifier and operator.

```c
#include <stdalign.h>

alignas(16) int aligned_var;           // Align to 16 bytes
size_t alignment = alignof(double);    // Get alignment of double
```

C23 makes `alignas` and `alignof` keywords, deprecating `<stdalign.h>`.

### No-Return: `<stdnoreturn.h>` (C11)

```c
#define noreturn _Noreturn
```

Indicates function does not return.

```c
#include <stdnoreturn.h>

noreturn void fatal_error(const char *msg) {
    fprintf(stderr, "Fatal: %s\n", msg);
    exit(1);
}
```

C23 makes `[[noreturn]]` attribute standard, deprecating `<stdnoreturn.h>`.

### `static_assert` Without Message (C23)

C11 requires message:
```c
_Static_assert(sizeof(int) >= 4, "int too small");
```

C23 allows omitting message:
```c
static_assert(sizeof(int) >= 4);
```

## Best Practices

1. **Prefer standard library over rolling your own**: String functions, memory management, math functions are well-tested and optimized.

2. **Always check return values**: Especially for allocation (`malloc`, `calloc`, `realloc`), I/O functions, and conversion functions (`strtol`).

3. **Use fixed-width types (`<stdint.h>`) for precise size requirements**: `int32_t` instead of `int` when size matters.

4. **Use `<inttypes.h>` format macros for portable printing**: `PRId64` instead of `%lld`.

5. **Prefer `strtol` family over `atoi` family**: Better error detection.

6. **Be aware of locale dependence**: `<ctype.h>` functions, `printf`/`scanf` decimal point, `strftime`.

7. **Cast to `unsigned char` when passing `char` to `<ctype.h>` functions**: Avoid undefined behavior.

8. **Never ignore `const`**: Don't cast away `const` from library-returned strings (`getenv`, `strerror`).

9. **Understand memory ownership**: Who allocates, who frees. `malloc`/`calloc`/`realloc` memory must be `free`d. Library-returned static buffers must not be freed.

10. **Use `volatile sig_atomic_t` for signal handler communication**: Only safe variable type in handlers.

11. **Avoid signals and `setjmp`/`longjmp` unless necessary**: Difficult to use correctly; modern alternatives exist.

12. **Leverage type-generic math (`<tgmath.h>`) in C99+**: Cleaner code, fewer type errors.

13. **Use `assert` for invariants, not error handling**: Assertions disappear in release builds.

14. **Initialize memory appropriately**: `calloc` for zero-init, `malloc` + explicit init otherwise. Don't rely on uninitialized memory.

15. **Beware of integer overflow in size calculations**: `calloc` helps; for `malloc`, check `SIZE_MAX`.

The C Standard Library provides essential facilities for practical C programming. Understanding its capabilities, limitations, and pitfalls is crucial for writing correct, portable, and efficient C code.
