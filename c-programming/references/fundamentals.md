# C Fundamentals, Expressions, and Basic Types

This reference covers essential C programming concepts including program structure, data types, operators, expressions, and type conversions based on K.N. King's "C Programming: A Modern Approach, 2nd Edition."

## C Program Structure

### The main() Function

Every C program requires a `main()` function as its entry point. Standard-conforming signatures:

```c
int main(void) {
    /* program body */
    return 0;
}

int main(int argc, char *argv[]) {
    /* command-line arguments */
    return 0;
}
```

The return value indicates program status to the operating system: 0 for success, non-zero for errors. Use `EXIT_SUCCESS` and `EXIT_FAILURE` from `<stdlib.h>` for portability.

### Statements and Expressions

C programs consist of statements terminated by semicolons:

```c
int x;              /* declaration statement */
x = 5;              /* expression statement */
printf("Hello\n");  /* function call statement */
return 0;           /* return statement */
```

Compound statements (blocks) group statements with braces:

```c
{
    int temp = x;
    x = y;
    y = temp;
}
```

### Comments

C supports two comment styles:

```c
/* Traditional C comment
   spanning multiple lines */

// C99 single-line comment
```

Comments do not nest. Traditional comments are removed during preprocessing, replaced by a single space.

### Translation Units

A translation unit is a source file after preprocessing. Programs can consist of multiple translation units linked together. Each translation unit is compiled independently.

## Basic Types in Detail

### Integer Types

C provides signed and unsigned integer types in multiple sizes:

```c
char          /* smallest addressable unit, usually 8 bits */
short         /* at least 16 bits */
int           /* natural size for target, at least 16 bits */
long          /* at least 32 bits */
long long     /* at least 64 bits (C99) */
```

Each can be `signed` or `unsigned`. Default is signed except for `char`, which is implementation-defined.

**Size guarantees:**
```c
sizeof(char) <= sizeof(short) <= sizeof(int) <= sizeof(long) <= sizeof(long long)
```

**Typical sizes (LP64 model on 64-bit systems):**
- `char`: 8 bits
- `short`: 16 bits
- `int`: 32 bits
- `long`: 64 bits (32 bits on Windows)
- `long long`: 64 bits

**Range examples:**
```c
signed char      /* -128 to 127 */
unsigned char    /* 0 to 255 */
short            /* -32768 to 32767 */
unsigned short   /* 0 to 65535 */
int              /* typically -2147483648 to 2147483647 */
unsigned int     /* typically 0 to 4294967295 */
```

### Character Type

`char` is an integer type used for character storage:

```c
char ch = 'A';              /* stores ASCII 65 */
unsigned char byte = 255;   /* guaranteed positive */
signed char sc = -1;        /* guaranteed signed */
```

Whether plain `char` is signed or unsigned is implementation-defined. Use explicit `signed char` or `unsigned char` when signedness matters.

### Boolean Type

C99 introduced `_Bool` for boolean values:

```c
_Bool flag = 1;  /* 0 or 1 only */
```

Include `<stdbool.h>` for convenient macros:

```c
#include <stdbool.h>

bool is_valid = true;   /* expands to _Bool is_valid = 1 */
bool is_error = false;  /* expands to 0 */
```

### Floating Types

C provides three floating-point types:

```c
float        /* single precision, typically 32 bits (IEEE 754) */
double       /* double precision, typically 64 bits */
long double  /* extended precision, at least as wide as double */
```

**Precision:**
- `float`: ~6-7 decimal digits
- `double`: ~15-16 decimal digits
- `long double`: implementation-defined, often 80 or 128 bits

```c
float pi_f = 3.14159f;
double pi_d = 3.14159265358979;
long double pi_ld = 3.14159265358979323846L;
```

Floating-point arithmetic is approximate. Never compare for exact equality.

### Exact-Width Integer Types (C99)

`<stdint.h>` provides exact-width types:

```c
#include <stdint.h>

int8_t   i8;    /* exactly 8 bits, signed */
uint8_t  u8;    /* exactly 8 bits, unsigned */
int16_t  i16;   /* exactly 16 bits */
uint16_t u16;
int32_t  i32;   /* exactly 32 bits */
uint32_t u32;
int64_t  i64;   /* exactly 64 bits */
uint64_t u64;
```

Also provides minimum-width types (`int_least16_t`), fastest types (`int_fast16_t`), and maximum-width types (`intmax_t`, `uintmax_t`).

Limits are defined in macros: `INT8_MIN`, `INT8_MAX`, `UINT8_MAX`, etc.

## Constants and Literals

### Integer Constants

**Decimal:** `0`, `123`, `1000000`

**Octal (prefix 0):** `077` (equals 63 decimal), `0644`

**Hexadecimal (prefix 0x or 0X):** `0xFF` (255), `0x1A2B`, `0XDEADBEEF`

**Type suffixes:**
```c
10       /* int */
10U      /* unsigned int */
10L      /* long */
10UL     /* unsigned long */
10LL     /* long long (C99) */
10ULL    /* unsigned long long */
```

The compiler chooses the smallest type that can represent the constant. For decimal constants: `int`, `long`, `long long`. For octal/hex: `int`, `unsigned int`, `long`, `unsigned long`, etc.

### Floating Constants

```c
3.14159       /* double by default */
.5            /* leading zero optional */
1.            /* trailing digits optional */
2.5e10        /* scientific notation: 2.5 × 10^10 */
1E-5          /* 0.00001 */

3.14f         /* float suffix */
3.14F         /* float suffix */
2.71828L      /* long double suffix */
```

No integer suffix makes a floating constant `double` by default.

### Character Constants

Single characters in single quotes:

```c
char c = 'A';       /* letter */
char d = '7';       /* digit character, not integer 7 */
char e = ' ';       /* space */
```

**Escape sequences:**
```c
'\n'    /* newline (line feed) */
'\t'    /* horizontal tab */
'\r'    /* carriage return */
'\b'    /* backspace */
'\a'    /* alert (bell) */
'\\'    /* backslash */
'\''    /* single quote */
'\"'    /* double quote */
'\0'    /* null character */
'\?'    /* question mark (rarely needed) */
```

**Octal and hex escapes:**
```c
'\101'      /* 'A' in octal (ASCII 65) */
'\x41'      /* 'A' in hex */
'\033'      /* escape character (27) */
'\xff'      /* byte value 255 */
```

Octal escapes are 1-3 digits. Hex escapes consume all following hex digits, which can cause issues:

```c
char s[] = "\x1234";  /* \x1234 is ONE character (truncated), then '4' */
char t[] = "\x12" "34";  /* \x12, then '3', then '4' */
```

### String Literals

Sequences in double quotes:

```c
"Hello, world!"
"Line 1\nLine 2"
""              /* empty string, contains only '\0' */
```

String literals are arrays of `char` terminated by `'\0'`:

```c
"Hi"    /* actually 3 chars: 'H', 'i', '\0' */
```

Adjacent string literals are concatenated:

```c
"Hello, " "world!"    /* same as "Hello, world!" */
"This is a long string "
"split across lines"
```

Useful for breaking long strings or combining with macros.

## Variables

### Declaration

Variables must be declared before use:

```c
int count;
double price, tax, total;  /* multiple variables */
char initial;
```

In C89, all declarations must appear at the beginning of a block, before any statements.

### Initialization

Variables can be initialized when declared:

```c
int count = 0;
double pi = 3.14159;
char grade = 'A';
```

Uninitialized local variables contain garbage values. Global and static variables are automatically initialized to zero.

### Mixed Declarations (C99)

C99 allows declarations anywhere in a block:

```c
int x = 5;
printf("%d\n", x);
int y = 10;        /* legal in C99, error in C89 */
```

This enables declaring variables near first use and allows initialization with runtime values:

```c
int n = get_input();
int array[n];  /* variable-length array (VLA), C99 */
```

### Naming Rules

**Valid identifiers:**
- Start with letter or underscore
- Contain letters, digits, underscores
- Case-sensitive

```c
count       /* valid */
_temp       /* valid but reserved for implementation */
MAX_SIZE    /* valid, convention for constants */
value2      /* valid */
2ndValue    /* INVALID: starts with digit */
my-var      /* INVALID: hyphen not allowed */
```

**Reserved identifiers:**
- Names starting with underscore followed by uppercase letter (`_MAX`)
- Names starting with double underscore (`__func`)
- Names starting with single underscore in global scope

**Conventions:**
- `UPPER_CASE` for macro constants
- `lower_case` or `snake_case` for variables/functions
- `PascalCase` for type names (especially with typedef)

## Type Conversions

### Implicit Conversions

C automatically converts types in several contexts:

1. **Mixed-type expressions:** narrower type promoted to wider
2. **Assignment:** right side converted to left side type
3. **Function arguments:** converted to parameter types
4. **Return statements:** converted to function return type

### Integer Promotions

In expressions, types narrower than `int` are promoted to `int` (or `unsigned int` if `int` can't represent all values):

```c
char c1 = 'A', c2 = 'B';
char c3 = c1 + 1;  /* c1 promoted to int, result converted back to char */

short s = 10;
int i = s;         /* promoted to int */
```

This is why `sizeof(char)` may not equal `sizeof('A')`—character constants have type `int`.

### Usual Arithmetic Conversions

When binary operators combine different types, both operands are converted to a common type:

**Hierarchy (simplified):**
1. `long double`
2. `double`
3. `float`
4. Then integer promotions apply
5. If both signed or both unsigned, convert to larger type
6. If unsigned type is larger or equal in rank, convert to unsigned
7. If signed type can represent all values of unsigned type, convert to signed
8. Otherwise, convert to unsigned version of signed type

```c
int i = 10;
double d = 3.5;
double result = i + d;  /* i converted to double, result is 13.5 */

unsigned int ui = 100;
int si = -50;
unsigned int r = ui + si;  /* si converted to unsigned! */
/* -50 becomes large positive value, result is unexpected */
```

**Warning:** Mixing signed and unsigned types can produce surprising results.

### Explicit Casts

Force type conversion with cast operator:

```c
double d = 3.7;
int i = (int)d;         /* truncates to 3 */

int x = 5, y = 2;
double ratio = (double)x / y;  /* 2.5, not 2 */
/* Without cast: x / y is integer division = 2 */

void *ptr = malloc(sizeof(int));
int *iptr = (int *)ptr;  /* cast void* to int* */
```

Casts have high precedence:

```c
(int)x + y     /* cast x to int, then add y */
(int)(x + y)   /* add x and y, then cast result */
```

### Assignment Conversions

Right side is converted to type of left side:

```c
int i;
double d = 3.7;
i = d;          /* d converted to int, i = 3 (truncated) */

unsigned int u;
int si = -1;
u = si;         /* -1 becomes UINT_MAX */

char c = 300;   /* truncated/wrapped, likely 44 (300 % 256) */
```

**Data loss may occur:**
- Floating to integer: fractional part discarded
- Wider to narrower: high-order bits discarded
- Signed to unsigned (or vice versa): bit pattern reinterpreted

### Narrowing Conversions

Conversions that may lose information:
- Larger integer type to smaller
- Floating type to integer type
- `double` to `float`

```c
long big = 1000000L;
short small = big;      /* may truncate */

double precise = 3.14159265358979;
float approx = precise; /* loses precision */
```

Compilers may warn about narrowing conversions. They are legal but potentially dangerous.

## Operators

### Arithmetic Operators

```c
+    /* addition or unary plus */
-    /* subtraction or unary minus */
*    /* multiplication */
/    /* division */
%    /* remainder (modulo) */
```

**Integer division truncates:**

```c
7 / 2      /* 3, not 3.5 */
-7 / 2     /* -3 (implementation-defined before C99) */
7 / -2     /* -3 */
-7 / -2    /* 3 */
```

C99 specifies truncation toward zero for negative operands.

**Remainder operator:**

```c
9 % 5      /* 4 */
-9 % 5     /* -4 (C99: sign matches dividend) */
9 % -5     /* 4 */
```

Operands must be integers. Before C99, sign of result was implementation-defined.

### Assignment Operators

```c
=     /* simple assignment */
+=    /* compound assignment: x += y means x = x + y */
-=
*=
/=
%=
&=    /* bitwise AND assignment */
|=    /* bitwise OR assignment */
^=    /* bitwise XOR assignment */
<<=   /* left shift assignment */
>>=   /* right shift assignment */
```

Assignment is an expression with a value:

```c
int x, y, z;
z = (y = 5) + 3;   /* y = 5, then z = 5 + 3 = 8 */
x = y = z = 0;     /* rightmost first: z = 0, y = 0, x = 0 */
```

### Increment and Decrement Operators

```c
++    /* increment */
--    /* decrement */
```

Two forms: prefix and postfix:

```c
int i = 5;
int j = ++i;   /* prefix: i becomes 6, j = 6 */

int k = 5;
int m = k++;   /* postfix: m = 5, then k becomes 6 */
```

**Prefix:** increment/decrement, then use value
**Postfix:** use value, then increment/decrement

Apply only to lvalues (variables, not constants or expressions).

**Cautions:**

```c
int n = 5;
n = n++;       /* UNDEFINED BEHAVIOR */
a[i] = i++;    /* UNDEFINED BEHAVIOR */
```

Never modify a variable more than once in the same expression.

### Relational Operators

```c
<     /* less than */
>     /* greater than */
<=    /* less than or equal */
>=    /* greater than or equal */
==    /* equal to */
!=    /* not equal to */
```

Result is `int`: 1 (true) or 0 (false).

```c
5 < 10         /* 1 */
5 > 10         /* 0 */
5 == 5         /* 1 */
5 != 5         /* 0 */
```

**Warning:** `==` tests equality, `=` performs assignment:

```c
if (x == 5)    /* correct: test if x equals 5 */
if (x = 5)     /* WRONG: assigns 5 to x, condition is always true */
```

### Logical Operators

```c
!     /* logical NOT */
&&    /* logical AND */
||    /* logical OR */
```

Produce 0 or 1:

```c
!0             /* 1 */
!5             /* 0 (any non-zero is false when negated) */
(3 > 2) && (5 < 10)    /* 1 */
(3 > 2) || (5 > 10)    /* 1 */
```

**Short-circuit evaluation:**

```c
(x != 0) && (y / x > 2)    /* if x == 0, y/x never evaluated */
(p != NULL) && (*p == 'A') /* safe pointer dereference */
```

Second operand is not evaluated if result is determined by first operand:
- `&&`: if first is false, result is false
- `||`: if first is true, result is true

### Bitwise Operators

```c
&     /* bitwise AND */
|     /* bitwise OR */
^     /* bitwise XOR */
~     /* bitwise NOT (complement) */
<<    /* left shift */
>>    /* right shift */
```

Operate on integer types at bit level:

```c
unsigned char a = 0x5A;  /* 01011010 */
unsigned char b = 0x3C;  /* 00111100 */

a & b    /* 00011000 = 0x18 */
a | b    /* 01111110 = 0x7E */
a ^ b    /* 01100110 = 0x66 */
~a       /* 10100101 = 0xA5 */
a << 2   /* 01101000 = shift left 2 bits */
a >> 2   /* 00010110 = shift right 2 bits */
```

Right shift of signed negative values is implementation-defined (arithmetic vs. logical shift).

### Other Operators

**sizeof operator:**

```c
sizeof(int)           /* size in bytes */
sizeof(x)             /* size of variable */
sizeof x              /* parentheses optional for variables */
sizeof(char)          /* always 1 by definition */
```

Result has type `size_t` (unsigned integer type).

**Comma operator:**

```c
x = (y = 3, z = 5, y + z);   /* x = 8 */
```

Evaluates left to right, result is value of rightmost expression. Mainly used in `for` loops:

```c
for (i = 0, j = 10; i < j; i++, j--)
```

**Ternary conditional operator:**

```c
condition ? expr_if_true : expr_if_false
```

```c
max = (a > b) ? a : b;
printf("%s\n", (n == 1) ? "item" : "items");
```

Only the selected expression is evaluated.

## Expression Evaluation

### Precedence and Associativity

**Operator precedence (high to low, selected):**

1. `()` `[]` `->` `.` (postfix `++` `--`)
2. `!` `~` `+` `-` (unary) `*` `&` (pointer ops) `sizeof` (prefix `++` `--`)
3. `*` `/` `%` (multiplication group)
4. `+` `-` (addition group)
5. `<<` `>>`
6. `<` `<=` `>` `>=`
7. `==` `!=`
8. `&` (bitwise AND)
9. `^` (bitwise XOR)
10. `|` (bitwise OR)
11. `&&`
12. `||`
13. `?:` (ternary)
14. `=` `+=` `-=` etc. (assignment)
15. `,` (comma)

**Associativity:**
- Most operators: left-to-right
- Unary, assignment, ternary: right-to-left

```c
a - b - c         /* (a - b) - c (left-to-right) */
a = b = c         /* a = (b = c) (right-to-left) */
*p++              /* *(p++) (postfix ++ has higher precedence) */
```

Use parentheses when in doubt or for clarity.

### Sequence Points

A sequence point is a point in execution where all side effects of previous evaluations are complete. Sequence points occur:

- At the `;` (end of full expression)
- After condition evaluation in `if`, `while`, `for`
- After first operand of `&&`, `||`, `?:`, `,` operators
- At function call, after arguments evaluated

### Order of Evaluation

C does not specify the order of evaluation for most operators:

```c
int i = 1;
int arr[5] = {0, 1, 2, 3, 4};
arr[i] = i++;    /* UNDEFINED: which i is evaluated first? */

printf("%d %d\n", ++i, ++i);  /* UNDEFINED: argument order unspecified */
```

**Undefined behavior** results from:
- Modifying a variable multiple times between sequence points
- Reading and modifying a variable between sequence points (unless read is to determine new value)

**Safe code:**

```c
i = i + 1;       /* OK */
a[i] = b[i+1];   /* OK: i not modified */
```

**Unsafe code:**

```c
a[i++] = i;      /* UNDEFINED */
i = i++;         /* UNDEFINED */
f(i++, i++);     /* UNDEFINED */
```

### Short-Circuit Evaluation

Logical operators `&&` and `||` guarantee left-to-right evaluation and short-circuit:

```c
if (ptr != NULL && *ptr == 'x')   /* safe: *ptr only evaluated if ptr != NULL */

if (x != 0 && 10 / x > 1)         /* safe: division only if x != 0 */

while ((c = getchar()) != EOF && c != '\n')  /* read until newline or EOF */
```

This is defined behavior and commonly used for safety checks.

## Implementation-Defined Behavior

Certain aspects of C are implementation-defined, meaning the compiler/platform determines the behavior:

### char Signedness

Whether plain `char` is signed or unsigned is implementation-defined:

```c
char c = 255;    /* may be -1 on some systems, 255 on others */
```

Use `signed char` or `unsigned char` when signedness matters.

### Integer Sizes

Standard only guarantees minimums. Actual sizes vary:

```c
sizeof(int)      /* typically 4, but 2 on some embedded systems */
sizeof(long)     /* 4 on 32-bit and Windows 64-bit, 8 on Unix 64-bit */
```

Use `<limits.h>` for actual ranges:

```c
#include <limits.h>
INT_MAX          /* maximum int value */
LONG_MIN         /* minimum long value */
```

Or `<stdint.h>` for exact-width types.

### Integer Representation

Most systems use two's complement, but one's complement and sign-magnitude are allowed. This affects:

- Exact range of negative values
- Behavior of bitwise operations on negative numbers
- Padding bits

### Padding and Alignment

Structures may contain padding bytes for alignment. The same logical structure may have different sizes on different platforms.

## typedef

Create type aliases with `typedef`:

```c
typedef unsigned long size_t;    /* standard library example */
typedef int Integer;
Integer x, y;  /* same as: int x, y; */

typedef struct {
    int x;
    int y;
} Point;
Point p;       /* no need for 'struct' keyword */
```

Useful for:
- Platform abstraction
- Simplifying complex declarations
- Documenting intent

**typedef vs. #define:**
- `typedef` understands types and scope
- `#define` is textual replacement

```c
typedef char *String;
String s1, s2;     /* both are char* */

#define String char*
String s1, s2;     /* s1 is char*, s2 is char! */
```

Always prefer `typedef` for type names.

---

This reference covers the fundamental building blocks of C programming. Master these concepts to write correct, portable C code. Remember that C gives you great power—and responsibility—for managing types, conversions, and expression evaluation.
