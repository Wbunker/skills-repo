# Program Organization

This reference covers the organization of C programs, from fundamental scoping rules to multi-file program design. Understanding these concepts is essential for writing maintainable, scalable C code.

## Scope

Scope determines where an identifier is visible in a program. C has four kinds of scope:

### Block Scope

An identifier declared inside a block (including function parameters) has block scope, visible from the point of declaration to the end of the block:

```c
void process(int x) {  // x has block scope
    int y = 10;        // y has block scope

    if (x > 0) {
        int z = 20;    // z has block scope (nested)
        printf("%d\n", y);  // y is visible here
    }
    // z is not visible here
}
```

### File Scope

An identifier declared outside all blocks has file scope, visible from the point of declaration to the end of the translation unit:

```c
int count = 0;         // file scope

void increment(void) {
    count++;           // count is visible throughout the file
}

void reset(void) {
    count = 0;         // count is visible here too
}
```

### Function Scope

Only labels have function scope. A label is visible throughout the function where it's declared, even before its definition:

```c
void example(void) {
    goto error;        // legal: labels have function scope

    int x = 10;

error:                 // label visible throughout entire function
    cleanup();
}
```

### Function Prototype Scope

Parameter names in function prototypes have function prototype scope, ending at the close of the prototype:

```c
void process(int count);        // count has function prototype scope
void compute(int count, int n); // different count, no conflict
```

### Nested Scopes and Shadowing

Inner scopes can shadow outer scopes. The innermost declaration takes precedence:

```c
int x = 10;            // file scope

void test(void) {
    int x = 20;        // shadows file-scope x
    printf("%d\n", x); // prints 20

    {
        int x = 30;    // shadows function-level x
        printf("%d\n", x); // prints 30
    }

    printf("%d\n", x); // prints 20
}
```

**Best Practice:** Avoid shadowing. It reduces readability and increases the chance of bugs.

## Linkage

Linkage determines whether multiple declarations of the same identifier refer to the same object or function.

### External Linkage

External linkage means an identifier can be referenced from other translation units. Functions and file-scope variables have external linkage by default:

```c
// file1.c
int global_count = 0;      // external linkage

void increment(void) {     // external linkage
    global_count++;
}

// file2.c
extern int global_count;   // refers to global_count in file1.c
extern void increment(void); // refers to increment in file1.c

void use_it(void) {
    increment();
    printf("%d\n", global_count);
}
```

### Internal Linkage

The `static` keyword at file scope gives an identifier internal linkage, restricting it to the current translation unit:

```c
// file1.c
static int counter = 0;    // internal linkage (private to this file)

static void helper(void) { // internal linkage (private to this file)
    counter++;
}

void public_function(void) {
    helper();              // can call within this file
}

// file2.c
extern int counter;        // ERROR: counter has internal linkage in file1.c
void helper(void);         // different function (no conflict)
```

### No Linkage

Local variables and function parameters have no linkage. Each declaration is a distinct entity:

```c
void func1(void) {
    int x = 10;  // no linkage
}

void func2(void) {
    int x = 20;  // different variable (no linkage)
}
```

## Storage Duration

Storage duration determines the lifetime of an object.

### Automatic Storage Duration

Local variables have automatic storage duration by default. They're created when the block is entered and destroyed when it exits:

```c
void process(void) {
    int count = 0;  // automatic storage duration
    count++;
    // count is destroyed here
}
```

Each call creates a new instance:

```c
void recursive(int n) {
    int temp = n;   // new temp for each recursive call
    if (n > 0)
        recursive(n - 1);
}
```

### Static Storage Duration

File-scope variables and `static` local variables have static storage duration, existing for the entire program execution:

```c
int global = 0;         // static storage duration (file scope)

void counter(void) {
    static int count = 0;  // static storage duration (initialized once)
    count++;
    printf("%d\n", count);
}
```

Static local variables retain their values between function calls:

```c
int next_id(void) {
    static int id = 0;
    return ++id;        // 1, 2, 3, ... on successive calls
}
```

**Initialization:** Static storage duration variables are initialized to zero if no initializer is provided. Automatic variables contain indeterminate values.

### Allocated Storage Duration

Memory allocated with `malloc`, `calloc`, or `realloc` persists until explicitly freed:

```c
int *create_array(size_t n) {
    int *arr = malloc(n * sizeof(int));  // allocated storage
    return arr;
}

void use_array(void) {
    int *data = create_array(100);
    // use data...
    free(data);  // must explicitly free
}
```

### Thread Storage Duration (C11)

Variables declared with `_Thread_local` have thread storage duration. Each thread gets its own instance:

```c
_Thread_local int error_code = 0;  // separate instance per thread

void set_error(int code) {
    error_code = code;  // only affects current thread's copy
}
```

## Header Files

Header files (`.h`) contain declarations shared across multiple source files. They're the interface to a module's functionality.

### What Goes in Header Files

**Function Declarations:**

```c
// math_utils.h
int gcd(int a, int b);
double square_root(double x);
```

**Type Definitions:**

```c
// point.h
typedef struct {
    double x;
    double y;
} Point;

typedef enum {
    RED, GREEN, BLUE
} Color;
```

**Macro Definitions:**

```c
// config.h
#define MAX_BUFFER_SIZE 1024
#define MIN(a, b) ((a) < (b) ? (a) : (b))
```

**Inline Functions:**

```c
// utils.h
static inline int max(int a, int b) {
    return a > b ? a : b;
}
```

**External Variable Declarations:**

```c
// globals.h
extern int debug_level;
extern const char *program_name;
```

### What Does NOT Go in Header Files

**Variable Definitions:**

```c
// BAD: causes multiple definition errors when included in multiple files
int global_count = 0;  // definition, not declaration

// GOOD: in header
extern int global_count;

// GOOD: in one .c file
int global_count = 0;
```

**Function Definitions (except inline):**

```c
// BAD: violates one definition rule
void process(int x) {
    printf("%d\n", x);
}

// GOOD: only declaration in header
void process(int x);
```

**static Variables with Initializers:**

```c
// PROBLEMATIC: each file gets its own copy
static int counter = 0;  // separate instance per translation unit
```

## Include Guards

Include guards prevent multiple inclusion of the same header, which would cause redefinition errors.

### Traditional Include Guards

The standard pattern uses preprocessor directives:

```c
// math_utils.h
#ifndef MATH_UTILS_H
#define MATH_UTILS_H

int gcd(int a, int b);
double square_root(double x);

#endif /* MATH_UTILS_H */
```

The first inclusion defines `MATH_UTILS_H`. Subsequent inclusions skip the content because `MATH_UTILS_H` is already defined.

**Naming Convention:** Use the header filename in uppercase with underscores, often with a project prefix:

```c
#ifndef PROJECT_MODULE_FILENAME_H
#define PROJECT_MODULE_FILENAME_H
// ...
#endif
```

### pragma once

Modern compilers support `#pragma once` as a simpler alternative:

```c
// math_utils.h
#pragma once

int gcd(int a, int b);
double square_root(double x);
```

Benefits:
- Simpler syntax (one line vs three)
- No naming collisions
- Slightly faster compilation

Drawbacks:
- Not part of the C standard (though universally supported)
- Can have issues with symbolic links or copied files

### Why Use Both?

Many projects use both for maximum compatibility:

```c
// math_utils.h
#ifndef MATH_UTILS_H
#define MATH_UTILS_H
#pragma once

// declarations...

#endif /* MATH_UTILS_H */
```

This provides:
- Standards compliance (traditional guards)
- Faster compilation on modern compilers (`#pragma once`)
- Maximum portability

## Multi-File Programs

Real C programs consist of multiple source files compiled separately and linked together.

### Translation Units

Each `.c` file is a translation unit. The preprocessor processes `#include` directives, producing a complete translation unit:

```c
// module.c (before preprocessing)
#include <stdio.h>
#include "module.h"
void process(void) { ... }

// Translation unit (after preprocessing)
// [contents of stdio.h]
// [contents of module.h]
void process(void) { ... }
```

### Separate Compilation

Each translation unit is compiled independently to an object file:

```bash
gcc -c file1.c   # produces file1.o
gcc -c file2.c   # produces file2.o
gcc -c main.c    # produces main.o
```

Advantages:
- Only modified files need recompilation
- Parallel compilation possible
- Reduces build times for large projects

### extern Declarations

The `extern` keyword declares that an identifier is defined elsewhere:

```c
// shared.h
extern int shared_counter;
extern void initialize(void);

// shared.c (definition)
int shared_counter = 0;

void initialize(void) {
    shared_counter = 0;
}

// main.c (usage)
#include "shared.h"

int main(void) {
    initialize();
    shared_counter++;
    return 0;
}
```

**Note:** Function declarations are implicitly `extern`, so the keyword is optional (but explicit is clearer).

### One Definition Rule (ODR)

Each entity with external linkage must be defined exactly once across all translation units:

```c
// WRONG: multiple definitions
// file1.c
int global = 10;

// file2.c
int global = 20;  // ERROR: multiple definitions

// CORRECT: one definition, multiple declarations
// globals.h
extern int global;

// globals.c
int global = 10;  // single definition

// file1.c and file2.c
#include "globals.h"  // just declarations
```

### Linking

The linker combines object files, resolving references:

```bash
gcc -o program main.o file1.o file2.o
```

Link errors occur when:
- A referenced symbol has no definition (undefined reference)
- A symbol is defined multiple times (multiple definition)
- Incompatible declarations exist (type mismatch)

## static Functions

Functions declared `static` at file scope have internal linkage, making them private to that translation unit:

```c
// module.c
static void helper(int x) {  // internal linkage
    // implementation
}

static int calculate(void) { // internal linkage
    return helper(42);
}

void public_api(void) {      // external linkage
    calculate();
}
```

Benefits:
- Information hiding: implementation details stay private
- Name collision prevention: different files can have static functions with the same name
- Optimization: compiler knows function isn't called externally, enabling better optimization
- Cleaner interface: only public functions appear in the header

**Pattern:**

```c
// module.h (interface)
void public_function(void);

// module.c (implementation)
#include "module.h"

static void internal_helper(void) {  // not in header
    // implementation
}

void public_function(void) {         // in header
    internal_helper();
}
```

## Information Hiding and Abstract Data Types

Information hiding is crucial for building maintainable systems. C provides mechanisms for creating abstract data types (ADTs).

### Opaque Pointers (Handle Pattern)

Declare a structure type in the header without defining it:

```c
// stack.h (interface)
typedef struct stack *Stack;  // opaque pointer type

Stack stack_create(void);
void stack_push(Stack s, int value);
int stack_pop(Stack s);
void stack_destroy(Stack s);
```

Define the structure in the implementation file:

```c
// stack.c (implementation)
#include "stack.h"
#include <stdlib.h>

struct stack {         // definition hidden from clients
    int *data;
    size_t size;
    size_t capacity;
};

Stack stack_create(void) {
    Stack s = malloc(sizeof(struct stack));
    s->data = malloc(10 * sizeof(int));
    s->size = 0;
    s->capacity = 10;
    return s;
}

void stack_push(Stack s, int value) {
    if (s->size >= s->capacity) {
        s->capacity *= 2;
        s->data = realloc(s->data, s->capacity * sizeof(int));
    }
    s->data[s->size++] = value;
}

int stack_pop(Stack s) {
    return s->data[--s->size];
}

void stack_destroy(Stack s) {
    free(s->data);
    free(s);
}
```

Benefits:
- Implementation can change without affecting clients
- Prevents direct access to internal data
- Enforces use of provided API

### Incomplete Types

A type declared but not defined is an incomplete type. Pointers to incomplete types are valid:

```c
// Valid: pointer to incomplete type
struct node;
typedef struct node *NodePtr;

// Invalid: need complete type
struct node n;         // ERROR: incomplete type
sizeof(struct node);   // ERROR: incomplete type

// Complete the type in implementation
struct node {
    int data;
    struct node *next;
};
```

### Interface vs Implementation Files

Separate interface (`.h`) from implementation (`.c`):

```c
// complex.h (interface)
#ifndef COMPLEX_H
#define COMPLEX_H

typedef struct complex Complex;

Complex *complex_create(double real, double imag);
double complex_real(const Complex *c);
double complex_imag(const Complex *c);
Complex *complex_add(const Complex *a, const Complex *b);
void complex_destroy(Complex *c);

#endif

// complex.c (implementation)
#include "complex.h"
#include <stdlib.h>

struct complex {
    double real;
    double imag;
};

Complex *complex_create(double real, double imag) {
    Complex *c = malloc(sizeof(Complex));
    c->real = real;
    c->imag = imag;
    return c;
}

double complex_real(const Complex *c) {
    return c->real;
}

double complex_imag(const Complex *c) {
    return c->imag;
}

Complex *complex_add(const Complex *a, const Complex *b) {
    return complex_create(a->real + b->real, a->imag + b->imag);
}

void complex_destroy(Complex *c) {
    free(c);
}
```

## Build Systems

Compiling multi-file programs manually becomes tedious. Build systems automate the process.

### Manual Compilation

For a simple program with three files:

```bash
# Compile each source file to object file
gcc -std=c11 -Wall -Wextra -c main.c -o main.o
gcc -std=c11 -Wall -Wextra -c module1.c -o module1.o
gcc -std=c11 -Wall -Wextra -c module2.c -o module2.o

# Link object files to executable
gcc main.o module1.o module2.o -o program
```

Or all at once:

```bash
gcc -std=c11 -Wall -Wextra main.c module1.c module2.c -o program
```

### Make Basics Integration

A simple Makefile automates compilation:

```makefile
CC = gcc
CFLAGS = -std=c11 -Wall -Wextra -pedantic
OBJS = main.o module1.o module2.o
TARGET = program

$(TARGET): $(OBJS)
	$(CC) $(OBJS) -o $(TARGET)

main.o: main.c module1.h module2.h
	$(CC) $(CFLAGS) -c main.c

module1.o: module1.c module1.h
	$(CC) $(CFLAGS) -c module1.c

module2.o: module2.c module2.h module1.h
	$(CC) $(CFLAGS) -c module2.c

clean:
	rm -f $(OBJS) $(TARGET)
```

Make only recompiles files that have changed (or whose dependencies have changed).

### Dependency Tracking

The compiler can generate dependencies automatically:

```makefile
CC = gcc
CFLAGS = -std=c11 -Wall -Wextra -MMD -MP
SRCS = main.c module1.c module2.c
OBJS = $(SRCS:.c=.o)
DEPS = $(OBJS:.o=.d)
TARGET = program

$(TARGET): $(OBJS)
	$(CC) $(OBJS) -o $(TARGET)

-include $(DEPS)

.PHONY: clean
clean:
	rm -f $(OBJS) $(DEPS) $(TARGET)
```

The `-MMD -MP` flags generate `.d` files containing dependencies, which are included by Make.

## Program Design Principles

Well-designed programs are modular, with clear boundaries and minimal coupling.

### Modules

A module is a collection of related functions and data. Each module should have:
- A clear purpose
- A public interface (header file)
- A private implementation (source file)

Example module structure:

```
string_utils.h    # Public interface
string_utils.c    # Implementation
```

### Cohesion

Cohesion measures how related the functions within a module are. High cohesion is desirable.

**High Cohesion (Good):**

```c
// string_utils.h - all functions work with strings
char *str_duplicate(const char *s);
char *str_trim(const char *s);
int str_compare_ignore_case(const char *s1, const char *s2);
```

**Low Cohesion (Bad):**

```c
// utils.h - unrelated functions grouped together
char *str_duplicate(const char *s);
int parse_integer(const char *s);
void draw_circle(int x, int y, int radius);
double calculate_interest(double principal, double rate);
```

### Coupling

Coupling measures how much modules depend on each other. Low coupling is desirable.

**Tight Coupling (Bad):**

```c
// module1.c
extern int module2_internal_counter;  // accessing internal details

void function1(void) {
    module2_internal_counter++;  // directly manipulating module2's state
}

// module2.c
int module2_internal_counter = 0;  // exposed internal state
```

**Loose Coupling (Good):**

```c
// module2.h
void module2_increment_counter(void);  // public interface

// module1.c
#include "module2.h"

void function1(void) {
    module2_increment_counter();  // using public interface
}

// module2.c
static int counter = 0;  // hidden internal state

void module2_increment_counter(void) {
    counter++;
}
```

### Header File Organization Conventions

**Standard Library Headers First:**

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
```

**Project Headers Second:**

```c
#include "module.h"
#include "utils.h"
```

**Conditional Compilation:**

```c
#ifdef DEBUG
#include "debug.h"
#endif
```

**Module's Own Header First:**

In implementation files, include the module's own header first to ensure the header is self-contained:

```c
// module.c
#include "module.h"  // own header first
#include <stdio.h>   // then system headers
#include "utils.h"   // then other project headers
```

**Self-Contained Headers:**

Every header should be self-contained (include its own dependencies):

```c
// point.h
#ifndef POINT_H
#define POINT_H

// If Point uses size_t, include stddef.h
#include <stddef.h>

typedef struct {
    double x;
    double y;
} Point;

size_t point_count(void);

#endif
```

**Namespace-Like Prefixes:**

Since C lacks namespaces, use prefixes to avoid name collisions:

```c
// mylib_string.h
void mylib_string_copy(char *dest, const char *src);
char *mylib_string_duplicate(const char *s);

// mylib_math.h
int mylib_math_gcd(int a, int b);
double mylib_math_sqrt(double x);
```

This comprehensive approach to program organization—from fundamental scope rules through sophisticated module design—enables you to build maintainable, scalable C programs. The key is disciplined use of headers, careful management of linkage and storage duration, and deliberate information hiding to create clean module boundaries.
