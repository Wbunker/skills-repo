# The Preprocessor

## How the Preprocessor Works

The preprocessor operates **before** compilation proper. It performs text transformations on the source:

1. Trigraph replacement (obsolete, removed in C23)
2. Line splicing (`\` at end of line)
3. Tokenization and whitespace handling
4. Macro expansion, `#include`, conditional compilation
5. Output: a **translation unit** — pure C code ready for the compiler

Run preprocessor only: `gcc -E source.c` (useful for debugging macros).

## Object-Like Macros (#define)

```c
#define BUFFER_SIZE 1024
#define PI 3.14159265358979
#define VERSION_STRING "2.1.0"
#define EMPTY                     /* empty replacement */
```

**Naming convention**: `ALL_CAPS` for macros by tradition (helps distinguish from variables/functions).

**Multi-line macros** — use `\` continuation:
```c
#define HEADER \
    "Name: MyApp\n" \
    "Version: 1.0\n"
```

**Parenthesization**: Always parenthesize the replacement text if it's an expression:
```c
#define BUFFER_SIZE (1024)              /* safer if used in expressions */
#define AREA(w, h) ((w) * (h))         /* not object-like, but same principle */
```

### Preferred Alternatives

For integer constants, prefer `enum` or `static const` when possible:
```c
enum { BUFFER_SIZE = 1024 };           /* visible in debugger */
static const double PI = 3.14159265;   /* type-safe, respects scope */
```

Macros remain necessary for: string constants, conditional compilation guards, and values needed in `#if` directives.

## Function-Like Macros

```c
#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define SWAP(x, y, T) do { T tmp_ = (x); (x) = (y); (y) = tmp_; } while (0)
#define ABS(x) ((x) < 0 ? -(x) : (x))
```

### Parenthesization Rules

1. **Parenthesize each parameter** in the replacement: `(a)`, `(b)`
2. **Parenthesize the entire expression**: `((a) > (b) ? (a) : (b))`

Without proper parenthesization:
```c
#define SQUARE(x) x * x
SQUARE(a + 1)  /* expands to: a + 1 * a + 1  (WRONG — should be (a+1)*(a+1)) */

#define SQUARE(x) ((x) * (x))  /* CORRECT */
```

### Multiple Evaluation Problem

```c
#define MAX(a, b) ((a) > (b) ? (a) : (b))
MAX(i++, j)  /* i may be incremented TWICE! */
```

`inline` functions don't have this problem — prefer them when possible.

### Multi-Statement Macros — do { } while(0)

```c
/* WRONG: */
#define LOG(msg) printf("[LOG] "); printf("%s\n", msg);
if (debug) LOG("test");  /* only first printf is conditional! */

/* CORRECT: */
#define LOG(msg) do { printf("[LOG] "); printf("%s\n", msg); } while (0)
if (debug) LOG("test");  /* entire block is conditional, and semicolon works correctly */
```

The `do { ... } while(0)` idiom:
- Creates a single statement from multiple statements
- Requires a semicolon at the call site (natural syntax)
- Works correctly in all control-flow contexts

## Stringizing (#) and Token Pasting (##)

### Stringizing — Convert Argument to String

```c
#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)   /* two-level for macro expansion */

STRINGIFY(hello)       /* → "hello" */
STRINGIFY(3 + 4)       /* → "3 + 4" */

#define VERSION 2
STRINGIFY(VERSION)     /* → "VERSION" (not expanded!) */
TOSTRING(VERSION)      /* → "2" (expanded first, then stringized) */
```

**Debug macro** — print expression and value:
```c
#define DEBUG_INT(expr) printf(#expr " = %d\n", (expr))
DEBUG_INT(x + y);  /* → printf("x + y" " = %d\n", (x + y)); */
```

### Token Pasting — Concatenate Tokens

```c
#define MAKE_VAR(prefix, num) prefix##num
MAKE_VAR(var, 1)  /* → var1 */

#define DECLARE_PAIR(type) \
    type type##_first;     \
    type type##_second;

DECLARE_PAIR(int)  /* → int int_first; int int_second; */
```

**Use case**: generating families of related functions or variables:
```c
#define DEFINE_VECTOR(T, name)                              \
    struct name { T *data; size_t len, cap; };              \
    struct name name##_create(void) {                       \
        return (struct name){NULL, 0, 0};                   \
    }                                                       \
    void name##_push(struct name *v, T val) { /* ... */ }
```

## #undef

```c
#define TEMP 100
/* ... use TEMP ... */
#undef TEMP          /* now TEMP is undefined */
#define TEMP 200     /* safe to redefine */
```

Redefining a macro without `#undef` first is only allowed if the new definition is identical.

## Conditional Compilation

### Basic Forms

```c
#if EXPRESSION
    /* compiled if EXPRESSION is nonzero */
#elif OTHER_EXPRESSION
    /* compiled if OTHER_EXPRESSION is nonzero */
#else
    /* compiled if all above are zero */
#endif

#ifdef MACRO       /* equivalent to #if defined(MACRO) */
#ifndef MACRO      /* equivalent to #if !defined(MACRO) */
```

### Common Patterns

**Debug code:**
```c
#ifdef DEBUG
    fprintf(stderr, "debug: x = %d\n", x);
#endif
```
Compile with: `gcc -DDEBUG source.c`

**Platform-specific code:**
```c
#if defined(_WIN32)
    #include <windows.h>
#elif defined(__linux__)
    #include <unistd.h>
#elif defined(__APPLE__)
    #include <mach/mach.h>
#else
    #error "Unsupported platform"
#endif
```

**Feature testing:**
```c
#if __STDC_VERSION__ >= 199901L
    /* C99 features available */
#endif

#if __STDC_VERSION__ >= 201112L
    /* C11 features available */
#endif
```

**Include guards:**
```c
#ifndef MYHEADER_H
#define MYHEADER_H
/* header contents */
#endif
```

## #include

### Search Paths

```c
#include <stdio.h>      /* search system include paths */
#include "myheader.h"   /* search current directory first, then system paths */
```

- `""` typically searches: current directory → `-I` paths → system paths
- `<>` typically searches: `-I` paths → system paths

### What Goes in Header Files

**YES** — put in `.h`:
- Function declarations (prototypes)
- Type definitions (`struct`, `enum`, `typedef`)
- Macro definitions
- `extern` variable declarations
- `inline` function definitions
- `static inline` function definitions

**NO** — do NOT put in `.h`:
- Variable definitions (causes multiple definition errors)
- Non-inline function definitions
- `static` variables (creates separate copies per translation unit)

## Predefined Macros

| Macro | Expands to |
|-------|-----------|
| `__FILE__` | Current filename as string literal |
| `__LINE__` | Current line number as integer |
| `__func__` | Current function name (C99, not a macro — it's a predefined identifier) |
| `__DATE__` | Compilation date `"Mmm dd yyyy"` |
| `__TIME__` | Compilation time `"hh:mm:ss"` |
| `__STDC__` | `1` if conforming implementation |
| `__STDC_VERSION__` | `199901L` (C99), `201112L` (C11), `201710L` (C17), `202311L` (C23) |

**Diagnostic macro:**
```c
#define ASSERT(cond) do { \
    if (!(cond)) { \
        fprintf(stderr, "Assertion failed: %s at %s:%d in %s\n", \
                #cond, __FILE__, __LINE__, __func__); \
        abort(); \
    } \
} while (0)
```

## #pragma and _Pragma

```c
#pragma once                    /* non-standard but universally supported include guard */
#pragma pack(push, 1)           /* set struct packing to 1 byte */
#pragma pack(pop)               /* restore previous packing */
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-variable"
/* code with intentionally unused variable */
#pragma GCC diagnostic pop
```

### _Pragma Operator (C99)

Allows `#pragma` inside macros:
```c
#define DISABLE_WARNING(w) _Pragma(#w)
DISABLE_WARNING(GCC diagnostic ignored "-Wunused")
/* expands to: #pragma GCC diagnostic ignored "-Wunused" */
```

## #error and #warning

```c
#if BUFFER_SIZE < 256
    #error "BUFFER_SIZE must be at least 256"
#endif

#ifndef OPTIMIZED
    #warning "Building without optimizations"   /* GCC/Clang extension */
#endif
```

`#error` halts compilation. `#warning` (non-standard but widespread) produces a warning.

## Macro Pitfalls and Best Practices

### When to Use Macros vs Alternatives

| Need | Macro | Alternative |
|------|-------|-------------|
| Integer constant | `#define N 100` | `enum { N = 100 };` (preferred) |
| Floating constant | `#define PI 3.14` | `static const double PI = 3.14;` (preferred) |
| Type-generic function | `#define MAX(a,b) ...` | `_Generic` (C11) or `inline` per type |
| Multi-statement block | `#define DO_STUFF ...` | `inline` function (preferred) |
| String constant | `#define MSG "hello"` | `static const char MSG[] = "hello";` |
| Conditional compilation | `#ifdef DEBUG` | Only macros work here |
| Include guards | `#ifndef HEADER_H` | `#pragma once` (simpler) |
| Stringizing/pasting | `#x`, `a##b` | Only macros can do this |

### Common Macro Errors

```c
/* Missing space after macro name — becomes function-like: */
#define FOO (42)     /* WRONG if intent is object-like — space before ( needed? */
                     /* Actually fine: #define FOO (42) IS object-like */
                     /* But: #define FOO(42) is function-like with param "42" — error */

/* Semicolons in macro definitions: */
#define SIZE 100;    /* WRONG — semicolon included in expansion */
int a[SIZE];         /* expands to: int a[100;]; — syntax error */
```

## #embed (C23)

Embed binary file contents as an array initializer:
```c
const unsigned char icon[] = {
    #embed "icon.png"
};
```

Replaces the need for tools like `xxd -i`. The embedded data becomes a comma-separated list of integer constants. Attributes like `limit()` and `prefix()`/`suffix()` control embedding behavior.
