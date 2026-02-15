---
name: c-programming
description: >
  Expert-level C programming assistance based on modern C standards (C99/C11/C17/C23)
  and the pedagogical approach of "C Programming: A Modern Approach" by K.N. King.
  Use when the user is writing C code, debugging C programs, asking about C syntax or
  semantics, discussing C data types, pointers, arrays, strings, structs, unions,
  enums, the preprocessor, the C standard library, memory management, file I/O,
  bitwise operations, or program organization. Also triggers on mentions of gcc, clang,
  Makefile with C files, segfault debugging, undefined behavior, pointer arithmetic,
  malloc/free, printf/scanf formatting, header files, linkage, storage duration,
  translation units, or any C standard library header (<stdio.h>, <stdlib.h>,
  <string.h>, <math.h>, etc.). Covers the full language from fundamentals through
  advanced topics like function pointers, abstract data types, and low-level programming.
---

# C Programming Expert

## Language Standards

| Standard | Year | Key Additions |
|----------|------|---------------|
| **C89/C90** | 1989/1990 | Original ANSI/ISO standard |
| **C99** | 1999 | `_Bool`, `//` comments, VLAs, designated initializers, `restrict`, `inline`, `<stdbool.h>`, `<stdint.h>`, mixed declarations/code, `long long` |
| **C11** | 2011 | `_Generic`, `_Static_assert`, `_Atomic`, `<threads.h>`, anonymous structs/unions, `aligned_alloc`, bounds-checking (`__STDC_LIB_EXT1__`) |
| **C17** | 2018 | Bug fixes only — no new features |
| **C23** | 2024 | `nullptr`, `typeof`, `constexpr`, `#embed`, `_BitInt`, `[[attributes]]`, `auto` type inference, `<stdbit.h>` |

Default to **C99** as baseline (widely supported, most practical). Note C23 features when relevant.

Compile with: `gcc -std=c99 -Wall -Wextra -pedantic` (or `-std=c11`, `-std=c17`, `-std=c23`).

## Compilation Model

```
source.c  →  preprocessor  →  translation unit  →  compiler  →  object file  →  linker  →  executable
(.c)         (cpp/gcc -E)     (expanded .c)        (gcc -c)     (.o)           (gcc)      (a.out)
```

Each `.c` file is compiled independently. Headers (`.h`) are textually included by the preprocessor.
The linker resolves cross-file references using external linkage.

## Type System Quick Reference

### Integer types (minimum guaranteed sizes)
| Type | Minimum bits | Typical size | Format specifier |
|------|-------------|--------------|------------------|
| `char` | 8 | 1 byte | `%c` / `%hhd` |
| `short` | 16 | 2 bytes | `%hd` |
| `int` | 16 | 4 bytes | `%d` |
| `long` | 32 | 4 or 8 bytes | `%ld` |
| `long long` | 64 (C99) | 8 bytes | `%lld` |

All integer types exist in `signed` (default) and `unsigned` variants.
Use `<stdint.h>` for exact-width types: `int8_t`, `int16_t`, `int32_t`, `int64_t`, `uint*_t`.

### Floating-point types
| Type | Typical precision | Format specifier |
|------|-------------------|------------------|
| `float` | ~7 digits | `%f` / `%e` / `%g` |
| `double` | ~15 digits | `%f` / `%e` / `%g` |
| `long double` | ~18-33 digits | `%Lf` / `%Le` / `%Lg` |

### Other types
| Type | Header | Notes |
|------|--------|-------|
| `_Bool` / `bool` | `<stdbool.h>` (C99) | `true`=1, `false`=0 |
| `size_t` | `<stddef.h>` | Unsigned, result of `sizeof` |
| `ptrdiff_t` | `<stddef.h>` | Signed, pointer difference |
| `NULL` | `<stddef.h>` | Null pointer constant |

## Operator Precedence (high to low)

| Precedence | Operators | Associativity |
|------------|-----------|---------------|
| 1 | `()` `[]` `->` `.` `++`(post) `--`(post) | Left |
| 2 | `++`(pre) `--`(pre) `+` `-` (unary) `!` `~` `*` `&` `sizeof` `(type)` | Right |
| 3 | `*` `/` `%` | Left |
| 4 | `+` `-` | Left |
| 5 | `<<` `>>` | Left |
| 6 | `<` `<=` `>` `>=` | Left |
| 7 | `==` `!=` | Left |
| 8 | `&` | Left |
| 9 | `^` | Left |
| 10 | `\|` | Left |
| 11 | `&&` | Left |
| 12 | `\|\|` | Left |
| 13 | `?:` | Right |
| 14 | `=` `+=` `-=` `*=` `/=` `%=` `<<=` `>>=` `&=` `^=` `\|=` | Right |
| 15 | `,` | Left |

**Common pitfall**: `&` / `^` / `|` bind *looser* than `==` / `!=`. Always parenthesize: `if ((x & MASK) == EXPECTED)`.

## Undefined Behavior — Critical Rules

C has undefined behavior (UB) that the compiler may exploit for optimization. Key UB to avoid:

1. **Signed integer overflow** — use unsigned or check before operations
2. **Dereferencing NULL or dangling pointers** — always validate
3. **Out-of-bounds array access** — no runtime checks in C
4. **Using uninitialized variables** — always initialize
5. **Double free or use-after-free** — set pointers to `NULL` after `free()`
6. **Violating strict aliasing** — don't cast between incompatible pointer types (use `memcpy` or unions)
7. **Modifying a variable twice between sequence points** — e.g., `i = i++` is UB
8. **Shifting by negative or >= bit-width** — `1 << 32` is UB for 32-bit `int`
9. **Dividing by zero** — check divisor
10. **Misaligned pointer access** — use `memcpy` for unaligned reads

## Reference Documents

Load these as needed based on the specific topic:

| Topic | File | When to read |
|-------|------|-------------|
| **Types & Expressions** | [references/fundamentals.md](references/fundamentals.md) | Basic types, constants, literals, expressions, operators, type conversions, sizeof, implicit promotions (Ch 2, 4, 7) |
| **Control Flow** | [references/control-flow.md](references/control-flow.md) | if/else, switch, while, for, do-while, break, continue, goto, comma operator (Ch 5, 6) |
| **Formatted I/O** | [references/formatted-io.md](references/formatted-io.md) | printf/scanf conversion specifiers, field widths, precision, flags, format string safety (Ch 3) |
| **Arrays & Strings** | [references/arrays-strings.md](references/arrays-strings.md) | Array declaration/initialization, multidimensional arrays, VLAs, string literals, string.h functions, string idioms (Ch 8, 13) |
| **Functions** | [references/functions.md](references/functions.md) | Function definition, prototypes, parameters, return values, recursion, inline (C99), _Noreturn (Ch 9) |
| **Program Organization** | [references/program-organization.md](references/program-organization.md) | Scope, linkage, storage duration, header files, multi-file builds, #include guards, information hiding, ADTs (Ch 10, 15, 19) |
| **Pointers** | [references/pointers.md](references/pointers.md) | Pointer basics, &/*, arithmetic, pointer-array relationship, pointers as parameters, const and pointers, pointer to pointer (Ch 11, 12) |
| **Advanced Pointers** | [references/advanced-pointers.md](references/advanced-pointers.md) | malloc/calloc/realloc/free, linked lists, function pointers, void*, qsort/bsearch callbacks, abstract data types (Ch 17) |
| **Preprocessor** | [references/preprocessor.md](references/preprocessor.md) | #define, macros with parameters, #/#, conditional compilation, #include, #pragma, predefined macros (Ch 14) |
| **Structs, Unions & Enums** | [references/structs-unions-enums.md](references/structs-unions-enums.md) | struct declaration/access, nested structs, self-referential structs, unions, enumerations, typedef, flexible array members (Ch 16) |
| **Low-Level Programming** | [references/low-level.md](references/low-level.md) | Bitwise operators, bit-fields, volatile, memory layout, alignment, union type punning, endianness (Ch 20) |
| **Declarations** | [references/declarations.md](references/declarations.md) | Declaration syntax, storage classes (auto/static/extern/register), type qualifiers (const/volatile/restrict), initializers, reading complex declarations (Ch 18) |
| **File I/O** | [references/file-io.md](references/file-io.md) | Streams, fopen/fclose, text vs binary mode, fread/fwrite, fseek/ftell, error handling, temporary files (Ch 22) |
| **Standard Library** | [references/standard-library.md](references/standard-library.md) | Library overview, <stdlib.h>, <math.h>, <ctype.h>, <errno.h>, <assert.h>, <signal.h>, <setjmp.h>, <stdint.h>, C99/C11 additions (Ch 21, 23-27) |
