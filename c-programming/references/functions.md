# Functions

Functions are the fundamental building blocks of C programs. Every C program consists of one or more functions, with execution always beginning at `main()`. This reference covers function definition, declaration, parameter passing, return values, and advanced topics like recursion, variadic functions, and function qualifiers.

## Function Definition

A function definition consists of a return type, function name, parameter list, and function body.

### Basic Syntax

```c
return_type function_name(parameter_list) {
    /* function body */
    return value;  /* if return_type is not void */
}
```

### Examples

```c
/* Simple function returning int */
int square(int x) {
    return x * x;
}

/* Function with multiple parameters */
double calculate_area(double width, double height) {
    return width * height;
}

/* Function with no parameters */
int get_random_seed(void) {
    return time(NULL);
}
```

### Void Functions

Functions that don't return a value use `void` as the return type:

```c
void print_banner(void) {
    printf("***********************\n");
    printf("* Welcome to Program! *\n");
    printf("***********************\n");
}

void swap_values(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}
```

A `void` function can use `return;` without a value to exit early:

```c
void process_data(int *data, size_t len) {
    if (data == NULL || len == 0) {
        return;  /* Early exit */
    }
    /* Process data... */
}
```

### Implicit int (C89 Only)

In C89, omitting the return type defaulted to `int`:

```c
/* C89: implicitly returns int */
square(int x) {
    return x * x;
}
```

This feature was **removed in C99** and is considered obsolete. Modern code must always specify the return type explicitly.

## Function Declarations (Prototypes)

A function declaration (also called a prototype) tells the compiler about a function's interface without providing its implementation.

### Why Prototypes Matter

Without a prototype, the compiler doesn't know the function's signature, leading to:

- Inability to check argument types
- Potential runtime errors from mismatched arguments
- Undefined behavior

### Declaration vs Definition

```c
/* Declaration (prototype) - typically in header file */
int find_max(int a, int b);

/* Definition - typically in source file */
int find_max(int a, int b) {
    return (a > b) ? a : b;
}
```

Parameter names in declarations are optional but recommended for documentation:

```c
/* Both valid, second is more informative */
double compute_interest(double, double, int);
double compute_interest(double principal, double rate, int years);
```

### Placement of Prototypes

```c
#include <stdio.h>

/* Prototypes at top allow functions to call each other */
void function_a(void);
void function_b(void);

int main(void) {
    function_a();
    return 0;
}

void function_a(void) {
    function_b();  /* OK: prototype available */
}

void function_b(void) {
    printf("Called from function_a\n");
}
```

### Old-Style K&R Declarations (Deprecated)

Pre-ANSI C used a different syntax:

```c
/* Old K&R style - DO NOT USE */
int compute(a, b)
int a;
int b;
{
    return a + b;
}
```

This style is **deprecated** and not supported in modern C standards.

## Parameter Passing

C uses **pass by value** exclusively. When you pass an argument to a function, C copies the value.

### Pass by Value

```c
void increment(int n) {
    n++;  /* Modifies local copy only */
}

int main(void) {
    int x = 5;
    increment(x);
    printf("%d\n", x);  /* Prints 5, not 6 */
    return 0;
}
```

### Simulating Pass by Reference with Pointers

To modify a variable in the caller's scope, pass a pointer:

```c
void increment(int *n) {
    (*n)++;  /* Modifies value at address */
}

int main(void) {
    int x = 5;
    increment(&x);  /* Pass address of x */
    printf("%d\n", x);  /* Prints 6 */
    return 0;
}
```

This is still pass by value—you're passing a copy of the pointer value (the address), but dereferencing it modifies the original data.

### Array Parameters Decay to Pointers

When you pass an array to a function, it automatically decays to a pointer to its first element:

```c
/* These three declarations are equivalent */
void process_array(int arr[], size_t len);
void process_array(int arr[10], size_t len);  /* Size ignored */
void process_array(int *arr, size_t len);

void process_array(int *arr, size_t len) {
    for (size_t i = 0; i < len; i++) {
        arr[i] *= 2;  /* Modifies original array */
    }
}
```

Arrays lose size information when passed to functions. Always pass the size separately:

```c
int sum_array(const int *arr, size_t len) {
    int total = 0;
    for (size_t i = 0; i < len; i++) {
        total += arr[i];
    }
    return total;
}
```

## Return Values

### Returning Values

A function returns a value using the `return` statement:

```c
int absolute_value(int n) {
    if (n < 0) {
        return -n;
    }
    return n;
}
```

The returned value is implicitly converted to the function's return type:

```c
double divide(int a, int b) {
    return a / b;  /* int result converted to double */
}
```

### Returning Void

Void functions can use `return;` without a value:

```c
void log_message(const char *msg) {
    if (msg == NULL) {
        return;  /* Early exit */
    }
    fprintf(stderr, "[LOG] %s\n", msg);
}
```

### Returning Structs

C allows returning structures by value:

```c
typedef struct {
    double x, y;
} Point;

Point create_point(double x, double y) {
    Point p = {x, y};
    return p;  /* Struct copied on return */
}

/* C99: compound literal */
Point create_point_c99(double x, double y) {
    return (Point){x, y};
}
```

This involves copying the entire struct, which can be expensive for large structures. Consider returning a pointer instead (but avoid dangling pointers).

### Returning Pointers (Dangling Pointer Danger)

Never return a pointer to a local variable:

```c
/* WRONG: Returns pointer to local variable */
int* create_value(int n) {
    int value = n;
    return &value;  /* Undefined behavior! */
}
```

Safe alternatives:

```c
/* Return pointer to static storage (not thread-safe) */
int* get_static(int n) {
    static int value;
    value = n;
    return &value;
}

/* Return pointer to dynamically allocated memory */
int* create_dynamic(int n) {
    int *p = malloc(sizeof(int));
    if (p != NULL) {
        *p = n;
    }
    return p;  /* Caller must free() */
}

/* Accept pointer from caller (preferred) */
void initialize_value(int *dest, int n) {
    if (dest != NULL) {
        *dest = n;
    }
}
```

### Returning from main()

The `main()` function returns an `int` status code to the operating system:

```c
#include <stdlib.h>

int main(void) {
    if (some_error_condition) {
        return EXIT_FAILURE;  /* Indicates failure */
    }
    return EXIT_SUCCESS;  /* Indicates success */
}
```

- `EXIT_SUCCESS` (typically 0): successful completion
- `EXIT_FAILURE` (typically non-zero): error occurred

Falling off the end of `main()` in C99+ is equivalent to `return 0;`.

## Recursion

A function is recursive if it calls itself, either directly or indirectly.

### Basic Recursion

```c
/* Factorial: n! = n × (n-1)! */
unsigned long factorial(unsigned int n) {
    if (n <= 1) {
        return 1;  /* Base case */
    }
    return n * factorial(n - 1);  /* Recursive case */
}
```

### Essential Elements

Every recursive function needs:

1. **Base case**: Condition to stop recursion
2. **Recursive case**: Call to self with modified argument
3. **Progress toward base case**: Arguments must move toward termination

### Classic Examples

```c
/* Fibonacci sequence */
int fibonacci(int n) {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

/* Greatest common divisor (Euclidean algorithm) */
int gcd(int a, int b) {
    if (b == 0) {
        return a;
    }
    return gcd(b, a % b);
}

/* String length (recursive) */
size_t str_length(const char *s) {
    if (*s == '\0') {
        return 0;
    }
    return 1 + str_length(s + 1);
}
```

### Tail Recursion

A function is tail-recursive if the recursive call is the last operation:

```c
/* Tail-recursive factorial */
unsigned long factorial_tail(unsigned int n, unsigned long accumulator) {
    if (n <= 1) {
        return accumulator;
    }
    return factorial_tail(n - 1, n * accumulator);
}

/* Wrapper for cleaner API */
unsigned long factorial(unsigned int n) {
    return factorial_tail(n, 1);
}
```

Some compilers optimize tail recursion into iteration, avoiding stack growth.

### Stack Overflow Risks

Each recursive call consumes stack space. Deep recursion can cause stack overflow:

```c
/* Dangerous for large n */
int sum_to_n(int n) {
    if (n <= 0) return 0;
    return n + sum_to_n(n - 1);  /* n stack frames */
}
```

### Recursive vs Iterative Trade-offs

**Recursion advantages:**
- Natural expression of problems (trees, divide-and-conquer)
- Often more elegant and easier to understand
- Maps directly to mathematical definitions

**Iteration advantages:**
- More efficient (no function call overhead)
- No stack overflow risk
- Easier to reason about performance

```c
/* Iterative factorial - more efficient */
unsigned long factorial_iterative(unsigned int n) {
    unsigned long result = 1;
    for (unsigned int i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}
```

## inline Functions (C99)

The `inline` keyword suggests the compiler replace function calls with the function body.

### Syntax

```c
inline int max(int a, int b) {
    return (a > b) ? a : b;
}
```

### Semantics

- `inline` is a **hint**, not a command. Compilers may ignore it.
- Inline functions should be defined in header files for visibility.
- Multiple definitions are allowed (unlike regular functions).

```c
/* math_utils.h */
inline int square(int x) {
    return x * x;
}
```

### inline vs Macros

```c
/* Macro - no type safety, multiple evaluation */
#define SQUARE(x) ((x) * (x))

/* Inline function - type-safe, evaluates once */
inline int square(int x) {
    return x * x;
}

int a = 5;
SQUARE(a++);     /* a++ evaluated twice - undefined behavior */
square(a++);     /* a++ evaluated once - well-defined */
```

Inline functions are superior to macros for type safety and debugging.

### extern inline

For complex linkage scenarios:

```c
/* Header file */
inline int func(int x);  /* Declaration */

/* One source file */
extern inline int func(int x) {  /* External definition */
    return x * 2;
}
```

### When to Use inline

Use `inline` for:
- Small, frequently called functions (2-5 lines)
- Performance-critical code in tight loops
- Functions called from headers (getters, simple calculations)

Don't use for:
- Large functions (defeats the purpose)
- Recursive functions
- Functions with complex logic

## _Noreturn (C11)

The `_Noreturn` keyword indicates a function never returns to its caller.

### Syntax

```c
#include <stdlib.h>

_Noreturn void fatal_error(const char *message) {
    fprintf(stderr, "FATAL: %s\n", message);
    exit(EXIT_FAILURE);
}
```

### Standard _Noreturn Functions

```c
_Noreturn void exit(int status);
_Noreturn void abort(void);
_Noreturn void quick_exit(int status);  /* C11 */
```

### Benefits

- Compiler can optimize better (no need to preserve state for return)
- Warns if function can return normally
- Documents intent clearly

### [[noreturn]] Attribute (C23)

C23 introduces attribute syntax:

```c
[[noreturn]] void fatal_error(const char *message) {
    fprintf(stderr, "FATAL: %s\n", message);
    exit(EXIT_FAILURE);
}
```

This is the preferred syntax in modern C.

## Variadic Functions

Variadic functions accept a variable number of arguments, like `printf()` and `scanf()`.

### Basic Usage with <stdarg.h>

```c
#include <stdarg.h>

int sum_ints(int count, ...) {
    va_list args;
    va_start(args, count);  /* Initialize args after last fixed param */

    int total = 0;
    for (int i = 0; i < count; i++) {
        total += va_arg(args, int);  /* Retrieve next argument */
    }

    va_end(args);  /* Cleanup */
    return total;
}

/* Usage */
int result = sum_ints(4, 10, 20, 30, 40);  /* Returns 100 */
```

### Key Macros

- `va_list`: Type for argument list
- `va_start(ap, last_fixed)`: Initialize argument list
- `va_arg(ap, type)`: Retrieve next argument as `type`
- `va_end(ap)`: Cleanup argument list
- `va_copy(dest, src)`: Copy argument list (C99)

### Writing printf-like Functions

```c
#include <stdio.h>
#include <stdarg.h>

void log_message(const char *level, const char *format, ...) {
    va_list args;

    printf("[%s] ", level);

    va_start(args, format);
    vprintf(format, args);  /* Use vprintf for variadic arguments */
    va_end(args);

    printf("\n");
}

/* Usage */
log_message("ERROR", "Failed to open file: %s", filename);
log_message("INFO", "Processing %d records", count);
```

### va_copy Example

```c
void print_twice(const char *format, ...) {
    va_list args1, args2;

    va_start(args1, format);
    va_copy(args2, args1);  /* Copy for second use */

    printf("First:  ");
    vprintf(format, args1);
    va_end(args1);

    printf("Second: ");
    vprintf(format, args2);
    va_end(args2);
}
```

### Type Safety Warning

Variadic functions have **no type checking** for variable arguments:

```c
sum_ints(3, 10, 20, 30);      /* OK */
sum_ints(3, 10, 20.5, 30);    /* Undefined behavior! */
sum_ints(2, 10, 20, 30);      /* Reads garbage - undefined behavior! */
```

You must ensure:
- Argument count is correct
- Argument types match what `va_arg()` expects
- Use format strings or sentinels to determine argument types/counts

## Function Pointers

Function pointers store addresses of functions and enable callback mechanisms, dynamic dispatch, and flexible design patterns.

### Basic Syntax

```c
/* Declare function pointer */
int (*func_ptr)(int, int);

/* Point to function */
int add(int a, int b) { return a + b; }
func_ptr = add;  /* Or: func_ptr = &add; */

/* Call through pointer */
int result = func_ptr(3, 4);      /* Or: (*func_ptr)(3, 4); */
```

### typedef for Function Pointer Types

Using `typedef` improves readability:

```c
/* Without typedef */
int (*operation)(int, int);

/* With typedef */
typedef int (*Operation)(int, int);
Operation op;  /* Much clearer */
```

### Example: Callback Function

```c
typedef int (*Comparator)(int, int);

void sort_array(int *arr, size_t len, Comparator cmp) {
    /* Use cmp for comparisons */
    for (size_t i = 0; i < len - 1; i++) {
        for (size_t j = i + 1; j < len; j++) {
            if (cmp(arr[i], arr[j]) > 0) {
                int temp = arr[i];
                arr[i] = arr[j];
                arr[j] = temp;
            }
        }
    }
}

int ascending(int a, int b) { return a - b; }
int descending(int a, int b) { return b - a; }

/* Usage */
sort_array(numbers, len, ascending);
sort_array(numbers, len, descending);
```

For more advanced topics (arrays of function pointers, function pointer members in structs), see `advanced-pointers.md`.

## Best Practices

### Single Responsibility Principle

Each function should do one thing well:

```c
/* Bad: Does too much */
void process_data(int *data, size_t len) {
    validate_data(data, len);
    transform_data(data, len);
    save_data(data, len);
    log_results(data, len);
}

/* Good: Break into focused functions */
bool validate_data(const int *data, size_t len);
void transform_data(int *data, size_t len);
bool save_data(const int *data, size_t len);
void log_results(const int *data, size_t len);
```

### Limit Parameter Count

Keep parameter lists short (ideally 3-4, maximum 7):

```c
/* Bad: Too many parameters */
void create_window(int x, int y, int width, int height,
                   const char *title, int flags, void *userdata,
                   void (*callback)(void*));

/* Good: Use a struct */
typedef struct {
    int x, y, width, height;
    const char *title;
    int flags;
    void *userdata;
    void (*callback)(void*);
} WindowConfig;

void create_window(const WindowConfig *config);
```

### Use const for Read-Only Parameters

Mark pointer parameters `const` if the function doesn't modify the data:

```c
/* Promises not to modify the array */
int sum_array(const int *arr, size_t len) {
    int total = 0;
    for (size_t i = 0; i < len; i++) {
        total += arr[i];
    }
    return total;
}

/* Promises not to modify the string */
size_t count_chars(const char *str, char c) {
    size_t count = 0;
    while (*str) {
        if (*str == c) count++;
        str++;
    }
    return count;
}
```

### Document Functions

Use comments to document purpose, parameters, return values, and preconditions:

```c
/**
 * Searches for a value in a sorted array using binary search.
 *
 * @param arr    Sorted array to search (must not be NULL)
 * @param len    Number of elements in array
 * @param target Value to find
 * @return       Index of target if found, -1 otherwise
 *
 * Precondition: arr must be sorted in ascending order
 * Complexity: O(log n)
 */
int binary_search(const int *arr, size_t len, int target);
```

### Validate Input

Check preconditions, especially for public API functions:

```c
void* safe_malloc(size_t size) {
    if (size == 0) {
        fprintf(stderr, "Error: malloc called with size 0\n");
        return NULL;
    }

    void *ptr = malloc(size);
    if (ptr == NULL) {
        fprintf(stderr, "Error: malloc failed\n");
        exit(EXIT_FAILURE);
    }

    return ptr;
}
```

### Prefer Return Values Over Output Parameters

When possible, return values rather than using output parameters:

```c
/* Less clear */
void calculate_stats(const int *arr, size_t len, double *mean, double *stddev);

/* More clear */
typedef struct {
    double mean;
    double stddev;
} Stats;

Stats calculate_stats(const int *arr, size_t len);
```

### Avoid Global Variables

Pass data through parameters instead of relying on globals:

```c
/* Bad: Uses global */
int counter = 0;
void increment(void) {
    counter++;
}

/* Good: Passes state explicitly */
int increment(int counter) {
    return counter + 1;
}
```

Functions are essential to writing clear, maintainable, and reusable C code. Understanding parameter passing, return values, recursion, and advanced features like variadic functions enables you to write robust and efficient programs.
