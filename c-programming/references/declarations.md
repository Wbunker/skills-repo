# Declarations

Declarations introduce names into a C program and specify their properties. A declaration consists of declaration specifiers followed by one or more declarators.

## Declaration Syntax

The general form of a declaration:

```c
declaration-specifiers declarator [, declarator]... ;
```

Declaration specifiers include storage classes, type specifiers, type qualifiers, and function specifiers. Multiple declarators can share the same declaration specifiers:

```c
int x, *p, arr[10], (*fp)(void);  // Multiple declarators
static const int a = 5, *b, c[20];
```

Each declarator introduces a name with the type formed by combining the declaration specifiers with the declarator's syntax.

## Storage Classes

Storage classes control object lifetime and linkage. Only one storage class specifier is allowed per declaration.

### auto

The `auto` storage class is the default for local variables. It's almost never written explicitly:

```c
void func(void) {
    auto int x = 10;  // Redundant; same as: int x = 10;
}
```

Auto variables have automatic storage duration (lifetime limited to block execution) and no linkage.

### static

At file scope, `static` provides internal linkage (visible only within the current translation unit):

```c
static int file_counter = 0;  // Internal linkage
static void helper(void);      // Internal linkage
```

At block scope, `static` provides persistent storage (value retained between calls):

```c
void increment(void) {
    static int count = 0;  // Initialized once, persists across calls
    count++;
    printf("%d\n", count);
}
```

Static local variables have static storage duration and no linkage. They're initialized only once before program startup.

### extern

The `extern` storage class declares a name without defining it, indicating external linkage:

```c
extern int global_var;      // Declaration (no storage allocated)
extern void other_func(void);  // Declaration

int global_var = 42;        // Definition (storage allocated)
```

At file scope, `extern` is the default for functions and can be omitted. For variables, omitting `extern` creates a tentative definition.

### register

The `register` storage class suggests storing a variable in a CPU register for fast access:

```c
void process(int n) {
    register int i;
    for (i = 0; i < n; i++) {
        // ...
    }
}
```

Limitations:
- Cannot take the address of a register variable with `&`
- The compiler may ignore the hint
- Modern compilers often optimize better than manual register hints

### _Thread_local (C11)

Thread-local storage provides each thread with its own instance of a variable:

```c
_Thread_local int thread_counter = 0;
Thread_local int errno_copy;  // Using <threads.h> macro
```

Can be combined with `static` or `extern`. Each thread gets independent storage.

## Type Qualifiers

Type qualifiers modify how the compiler treats a type. They can appear multiple times in a declaration but duplicates are ignored.

### const

The `const` qualifier indicates that an object should not be modified after initialization:

```c
const int max_size = 100;
const char *message = "Hello";  // Pointer to const char
char * const ptr = buffer;      // Const pointer to char
const char * const fixed = "Fixed";  // Const pointer to const char
```

Important distinctions:
- `const int *p`: pointer to const int (can't modify `*p`, can modify `p`)
- `int * const p`: const pointer to int (can modify `*p`, can't modify `p`)

In C89/C90, `const` doesn't create true compile-time constants:

```c
const int size = 10;
int arr[size];  // Error in C89 (valid in C99 as VLA)
```

Use `#define` or `enum` for C89 constant expressions.

### volatile

The `volatile` qualifier prevents optimization, indicating that a value may change unexpectedly:

```c
volatile int *hardware_register = (volatile int *)0x40021000;
volatile sig_atomic_t signal_flag = 0;

void signal_handler(int sig) {
    signal_flag = 1;  // Modified asynchronously
}
```

Use cases:
- Memory-mapped hardware registers
- Variables modified by signal handlers
- Variables shared between threads (prefer atomic operations in C11)
- Variables modified by interrupt service routines

The compiler must read from memory each time and cannot cache the value in a register.

### restrict (C99)

The `restrict` qualifier is a pointer optimization hint, promising that the pointer is the only way to access the pointed-to object during the pointer's lifetime:

```c
void copy(int * restrict dest, const int * restrict src, size_t n) {
    for (size_t i = 0; i < n; i++) {
        dest[i] = src[i];  // Compiler knows dest and src don't overlap
    }
}
```

This allows aggressive optimization because the compiler knows the pointed-to regions don't alias. Using `restrict` incorrectly (when aliasing exists) causes undefined behavior.

### _Atomic (C11)

The `_Atomic` qualifier provides lock-free atomic operations:

```c
#include <stdatomic.h>

_Atomic int counter = 0;
atomic_int shared_var;  // Equivalent using typedef

atomic_fetch_add(&counter, 1);  // Atomic increment
```

Atomic types ensure thread-safe access without explicit locks for supported operations.

## Combining Qualifiers

Type qualifiers can be combined in various ways:

```c
const volatile int *status_reg = (const volatile int *)0x40000000;
// Hardware register that firmware might change but we shouldn't write

void process(const int * restrict input,
             int * restrict output,
             size_t n);
// Non-overlapping arrays, read-only input

const char * const * const argv;
// Const pointer to const pointer to const char
```

Qualifier propagation through pointers:

```c
int x = 10;
const int *p = &x;     // OK: can add const
int *q = p;            // Error: can't remove const
*(int *)p = 20;        // Undefined behavior: casting away const

int * const r = &x;    // Const pointer
r = &y;                // Error: can't modify r
*r = 20;               // OK: can modify *r
```

## Initializers

### Simple Initialization

Scalar types can be initialized with expressions:

```c
int x = 42;
double pi = 3.14159;
char *msg = "Hello";
int *ptr = &x;
```

### Aggregate Initialization

Arrays and structures use brace-enclosed initializer lists:

```c
int arr[5] = {1, 2, 3, 4, 5};
int partial[5] = {1, 2};  // Remaining elements zero-initialized: {1, 2, 0, 0, 0}
int sized[] = {1, 2, 3};  // Size inferred: 3 elements

struct point {
    int x, y;
};
struct point p = {10, 20};
struct point origin = {0};  // {0, 0}
```

Nested initialization:

```c
int matrix[2][3] = {
    {1, 2, 3},
    {4, 5, 6}
};

struct person {
    char name[20];
    int age;
};
struct person people[2] = {
    {"Alice", 30},
    {"Bob", 25}
};
```

### Designated Initializers (C99)

Designated initializers explicitly specify which element or member to initialize:

```c
int arr[6] = {[0] = 1, [5] = 6};  // {1, 0, 0, 0, 0, 6}
int sparse[100] = {[10] = 1, [20] = 2, [99] = 3};

struct point p = {.y = 20, .x = 10};  // Order doesn't matter
struct person alice = {.name = "Alice", .age = 30};

// Mixed designated and non-designated
int mixed[10] = {1, 2, [5] = 6, 7, 8};  // Continues from index 6, 7, 8
```

Array designation with structures:

```c
struct point points[3] = {
    [0].x = 1, [0].y = 2,
    [2] = {.x = 5, .y = 6}
};
```

### Compound Literals (C99)

Compound literals create unnamed objects:

```c
// Pass struct directly to function
draw_point((struct point){10, 20});

// Temporary array
int *ptr = (int[]){1, 2, 3, 4, 5};

// Initialize pointer to struct
struct point *pp = &(struct point){.x = 0, .y = 0};

// In expressions
int sum = calculate((int[]){1, 2, 3, 4, 5}, 5);
```

Compound literals at file scope have static storage duration; at block scope, they have automatic storage duration.

### Static Initialization Rules

Static and thread-local objects must be initialized with constant expressions:

```c
// File scope (static storage duration)
int global = 42;                    // OK: constant
int *ptr = &global;                 // OK: address constant
int arr[] = {1, 2, 3};             // OK: constant list
int computed = func();              // Error: not a constant expression

static int local_static = 10 + 20; // OK: constant expression
```

Zero initialization is automatic for static storage:

```c
static int x;        // Initialized to 0
static char *p;      // Initialized to NULL
static int arr[10];  // All elements 0
```

## Complex Declarations

Complex declarations combine pointers, arrays, and functions. Reading them requires understanding precedence.

### Reading Declarations

The "spiral rule" or "inside-out" approach:

1. Start with the identifier
2. Look right for `[]` (array) or `()` (function)
3. Look left for `*` (pointer)
4. Move outward in parentheses
5. Continue until done

Examples:

```c
int *p[10];
// p is an array of 10 pointers to int
// [] binds tighter than *, so p is array, elements are pointers

int (*p)[10];
// p is a pointer to an array of 10 ints
// Parentheses force pointer first, then array

int *f(void);
// f is a function returning pointer to int
// () binds tighter than *

int (*f)(void);
// f is a pointer to function returning int
// Parentheses force pointer first

int (*fp)(int, int);
// fp is a pointer to function taking two ints and returning int

int *(*fp)(int, int);
// fp is a pointer to function taking two ints and returning pointer to int

int (*arr[10])(void);
// arr is an array of 10 pointers to functions returning int

int (*(*fp)(int))[10];
// fp is a pointer to function taking int and returning pointer to array of 10 ints
```

### Practical Examples

```c
// Pointer to array
int (*pa)[5];
int matrix[3][5];
pa = &matrix[0];  // Points to first row
(*pa)[2] = 10;    // Access element

// Array of pointers
char *messages[3] = {"Error", "Warning", "Info"};

// Function pointer
int (*compare)(const void *, const void *);
compare = strcmp;
qsort(arr, n, sizeof(int), compare);

// Array of function pointers (jump table)
void (*operations[4])(int) = {add_op, sub_op, mul_op, div_op};
operations[choice](value);

// Function returning pointer
int *find_element(int *arr, size_t n, int key);

// Pointer to function returning pointer
char *(*get_string_func(int code))(void);
// get_string_func takes int, returns pointer to function returning char*
```

## typedef

The `typedef` keyword creates type aliases, simplifying complex declarations:

```c
typedef int *int_ptr;
typedef int int_array[10];
typedef int (*func_ptr)(int, int);

int_ptr p;              // Same as: int *p;
int_array arr;          // Same as: int arr[10];
func_ptr fp;            // Same as: int (*fp)(int, int);
```

Reading typedef declarations: replace `typedef` with a variable name to see what type it creates:

```c
typedef int (*operation)(int, int);
// Remove typedef: int (*operation)(int, int);
// operation is pointer to function, so the typedef creates that type

typedef struct point {
    int x, y;
} point_t;
// Creates both: struct point and type alias point_t
```

Benefits:
- Portability (platform-specific types)
- Readability (complex types)
- Easier to modify (change one typedef vs. many declarations)

```c
// Portability
typedef long long int64_t;  // On some platforms
typedef int int32_t;

// Function pointer typedef
typedef void (*signal_handler)(int);
signal_handler old_handler, new_handler;
new_handler = signal(SIGINT, handler_func);

// Simplifying structure pointers
typedef struct node {
    int data;
    struct node *next;
} node_t;

node_t *list = NULL;  // Instead of: struct node *list = NULL;
```

## Implicit Declarations

In C89, calling an undeclared function created an implicit declaration with return type `int`:

```c
// C89
int main(void) {
    int x = foo();  // Implicitly declares: int foo();
}

int foo(void) {     // Matches implicit declaration
    return 42;
}
```

This was error-prone and removed in C99. Modern C requires explicit declarations (prototypes):

```c
// C99 and later
int foo(void);      // Explicit prototype required

int main(void) {
    int x = foo();  // OK: foo declared above
}
```

Always use function prototypes to enable type checking and avoid subtle bugs.

## Tentative Definitions

A tentative definition is a file-scope variable declaration without an initializer:

```c
int x;          // Tentative definition
int x;          // Another tentative definition (OK)
int x = 10;     // Actual definition

extern int y;   // Declaration (not tentative definition)
```

Rules:
- Multiple tentative definitions of the same variable in one translation unit are allowed
- At most one actual definition (with initializer) is allowed
- If no actual definition exists, one tentative definition becomes the definition with zero initialization

Tentative definitions enable splitting large programs:

```c
// file1.c
int shared_var;  // Tentative definition

// file2.c
int shared_var = 100;  // Actual definition

// file3.c
extern int shared_var;  // Declaration only
```

Best practice: use `extern` for declarations and provide exactly one definition with an initializer.

## C99/C11/C23 Declaration Features

### Mixed Declarations and Code (C99)

C99 allows declarations anywhere in a block, not just at the beginning:

```c
// C89: All declarations at top
void process(void) {
    int i, j, k;
    double result;

    i = get_value();
    j = calculate(i);
    result = j * 2.5;
}

// C99: Declarations near first use
void process(void) {
    int i = get_value();
    int j = calculate(i);
    double result = j * 2.5;
}
```

This improves readability and allows initialization at declaration.

### static in Array Parameters (C99)

The `static` keyword in array parameters indicates minimum array size:

```c
void process(int arr[static 10]) {
    // Caller must pass array with at least 10 elements
    for (int i = 0; i < 10; i++) {
        arr[i] *= 2;
    }
}

// Combine with const
void analyze(const double data[static 100]);
```

This provides optimization hints and documentation but is rarely enforced by compilers.

### auto Type Inference (C23)

C23 repurposes `auto` for type inference from initializers:

```c
// C23
auto x = 42;              // int
auto pi = 3.14;           // double
auto msg = "Hello";       // char *
auto len = strlen(msg);   // size_t

// With arrays (preserves array type, not pointer)
auto arr = (int[]){1, 2, 3, 4, 5};  // int[5]
```

This doesn't create generic types; it's compile-time type deduction.

### typeof (C23)

The `typeof` operator obtains the type of an expression:

```c
// C23
int x = 10;
typeof(x) y = 20;         // y has type int

typeof(3.14) pi = 3.14;   // double

#define SWAP(a, b) do { \
    typeof(a) temp = (a); \
    (a) = (b); \
    (b) = temp; \
} while(0)

// Using typeof with compound literals
typeof(struct {int x; int y;}) point = {10, 20};
```

Useful for generic macros and maintaining type compatibility.

### constexpr (C23)

C23 introduces `constexpr` for true compile-time constants:

```c
// C23
constexpr int max_size = 100;
int arr[max_size];  // OK: max_size is a constant expression

constexpr double pi = 3.14159;

// constexpr implies const
// constexpr variables must be initialized with constant expressions
```

This addresses the C89 limitation where `const` didn't create true constants for array sizes and case labels.

### Variable-Length Arrays (C99, Optional C11)

VLAs allow array sizes determined at runtime:

```c
void process(int n) {
    int arr[n];  // Size determined at runtime

    for (int i = 0; i < n; i++) {
        arr[i] = i * i;
    }
    // arr automatically deallocated at block exit
}

// VLA parameters
void matrix_multiply(int n, int m,
                     double a[n][m],
                     double b[m][n],
                     double result[n][n]);
```

VLAs were mandatory in C99, optional in C11. Use `__STDC_NO_VLA__` to check availability.

Considerations:
- Stack allocation (risk of overflow)
- No initialization syntax
- `sizeof` evaluated at runtime
- Cannot have static storage duration

Many coding standards prohibit VLAs due to stack safety concerns.
