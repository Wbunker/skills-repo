# Pointers and Arrays

Pointers are one of C's most powerful and characteristic features. They provide direct access to memory addresses, enabling efficient array manipulation, dynamic memory allocation, and complex data structures. This reference covers pointer fundamentals and their intimate relationship with arrays.

## Pointer Basics

A **pointer** is a variable that stores a memory address. Instead of holding a value directly, a pointer holds the location where a value is stored.

### Declaration Syntax

```c
int *p;      // p is a pointer to int
char *str;   // str is a pointer to char
double *dp;  // dp is a pointer to double
```

The `*` in the declaration indicates that the variable is a pointer. Note that `*` binds to the variable name, not the type:

```c
int *p, q;    // p is a pointer to int; q is an int
int *p, *q;   // both p and q are pointers to int
```

### The Address-of Operator (&)

The `&` operator returns the address of a variable:

```c
int i = 42;
int *p = &i;  // p now holds the address of i
```

### The Dereference Operator (*)

The `*` operator (when used with a pointer variable, not in a declaration) accesses the value at the address stored in the pointer:

```c
int i = 42;
int *p = &i;
printf("%d\n", *p);  // prints 42
*p = 17;             // changes i to 17
```

### NULL Pointer

`NULL` (defined in `<stddef.h>`, `<stdio.h>`, and other headers) represents a pointer that points to nothing:

```c
int *p = NULL;

if (p == NULL) {
    printf("Pointer is null\n");
}
```

In modern C (C23), you can also use `nullptr`.

### Uninitialized Pointers - Critical Danger

An uninitialized pointer contains a garbage address. Dereferencing it causes undefined behavior:

```c
int *p;      // p contains garbage
*p = 42;     // DISASTER: writing to unknown memory location
```

**Always initialize pointers** before dereferencing them:

```c
int *p = NULL;           // safe: explicitly null
int x;
int *q = &x;             // safe: points to valid object
int *r = malloc(sizeof(int));  // safe: points to allocated memory
```

## Pointer Assignment

### Assigning Addresses

Pointers are assigned addresses, not values:

```c
int i = 5, j = 10;
int *p, *q;

p = &i;      // p points to i
q = &j;      // q points to j
p = q;       // p now points to j (same as q)
```

After `p = q`, both pointers point to the same location. Modifying `*p` now affects `j`.

### Pointer-to-Pointer

Pointers can point to other pointers:

```c
int i = 42;
int *p = &i;
int **pp = &p;   // pp points to p, which points to i

printf("%d\n", **pp);  // prints 42
**pp = 17;             // changes i to 17
```

### Pointer Compatibility

Pointers have types. Assignment between incompatible pointer types requires a cast:

```c
int *pi;
double *pd;

pi = pd;           // warning: incompatible pointer types
pi = (int *)pd;    // explicit cast (still dangerous)
```

Exception: Any pointer type can be assigned to/from `void *` without a cast.

## Dereferencing

### Reading vs Writing Through Pointers

The `*` operator can appear on either side of an assignment:

```c
int i = 5, j;
int *p = &i, *q = &j;

*q = *p;     // copies value from i to j
*p = 42;     // changes i to 42
```

### The Arrow Operator (->)

For pointers to structures, `->` combines dereferencing and member access:

```c
struct point {
    int x, y;
};

struct point pt = {10, 20};
struct point *pp = &pt;

printf("%d\n", (*pp).x);   // dereference first, then access member
printf("%d\n", pp->x);     // equivalent, cleaner syntax
pp->y = 30;                // modify through pointer
```

## Pointers as Function Arguments

C passes arguments by value, copying them to function parameters. Pointers enable **simulating pass by reference** by passing the address of a variable.

### Output Parameters

```c
void swap(int *px, int *py) {
    int temp = *px;
    *px = *py;
    *py = temp;
}

int a = 5, b = 10;
swap(&a, &b);  // a and b are swapped
```

### Multiple Return Values

```c
void get_dimensions(int *width, int *height) {
    *width = 1920;
    *height = 1080;
}

int w, h;
get_dimensions(&w, &h);  // w and h receive values
```

### const Pointers for Input Parameters

Use `const` to indicate a pointer parameter won't modify the pointed-to value:

```c
double average(const int *arr, int n) {
    double sum = 0.0;
    for (int i = 0; i < n; i++) {
        sum += arr[i];
    }
    return sum / n;
}
```

This communicates intent and allows the compiler to catch errors:

```c
double average(const int *arr, int n) {
    arr[0] = 0;  // error: assignment of read-only location
    return 0.0;
}
```

## Pointer Arithmetic

Pointers support arithmetic operations, making them powerful for array traversal.

### Adding/Subtracting Integers

Adding an integer `n` to a pointer advances it by `n` elements (not bytes):

```c
int arr[5] = {10, 20, 30, 40, 50};
int *p = arr;     // points to arr[0]

p++;              // now points to arr[1]
p += 2;           // now points to arr[3]
printf("%d\n", *p);  // prints 40
```

The compiler automatically scales by `sizeof(*p)`. If `p` points to `int` (4 bytes), `p + 1` adds 4 bytes.

### Subtracting Integers

```c
int *p = &arr[4];   // points to last element
p--;                // points to arr[3]
p -= 2;             // points to arr[1]
```

### Pointer Subtraction

Subtracting two pointers (pointing within the same array) yields the number of elements between them:

```c
int arr[10];
int *p = &arr[2];
int *q = &arr[7];

ptrdiff_t diff = q - p;  // diff is 5
```

The result type is `ptrdiff_t` (defined in `<stddef.h>`), a signed integer type.

### Pointer Comparison

Pointers can be compared with relational operators:

```c
int arr[10];
int *p = &arr[3];
int *q = &arr[7];

if (p < q) {
    printf("p comes before q\n");
}
```

Comparison is only meaningful for pointers into the same array (or one past the end).

### One Past the End

C allows a pointer to point one element past the end of an array (but not dereference it):

```c
int arr[5];
int *p;

for (p = arr; p < arr + 5; p++) {  // arr + 5 is valid
    printf("%d\n", *p);
}
```

## Pointer-Array Relationship

Arrays and pointers are intimately related in C, though they're not identical.

### Array Name Decays to Pointer

In most contexts, an array name is automatically converted to a pointer to its first element:

```c
int arr[10];
int *p = arr;     // equivalent to: int *p = &arr[0];
```

### Equivalence: a[i] ≡ *(a + i)

Array subscripting is defined in terms of pointer arithmetic:

```c
arr[i]  ≡  *(arr + i)
```

This works both ways:

```c
int arr[5] = {10, 20, 30, 40, 50};
int *p = arr;

printf("%d\n", arr[2]);   // 30
printf("%d\n", *(arr + 2));  // 30
printf("%d\n", p[2]);     // 30 - pointers can use subscript notation!
printf("%d\n", *(p + 2)); // 30
printf("%d\n", 2[arr]);   // 30 - legal but confusing!
```

Since `a[i]` means `*(a + i)`, and addition is commutative, `2[arr]` is equivalent to `arr[2]`.

### Array Parameters Decay

When an array is passed to a function, it decays to a pointer:

```c
void process(int arr[10]) {
    // arr is actually int *arr
    printf("%zu\n", sizeof(arr));  // prints pointer size (8), not 40
}

int data[10];
process(data);
```

These declarations are equivalent:

```c
void func(int arr[]);
void func(int arr[10]);
void func(int *arr);
```

The array size (if specified) is ignored. To track array size, pass it separately:

```c
void process(int arr[], int size) {
    // or: void process(int *arr, int size)
    for (int i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
}
```

### sizeof Difference

This is a critical distinction:

```c
int arr[10];
int *p = arr;

printf("%zu\n", sizeof(arr));  // 40 (10 * sizeof(int))
printf("%zu\n", sizeof(p));    // 8 (pointer size on 64-bit)
```

An array variable knows its size; a pointer doesn't.

## Pointer to Array Elements

Pointers are often more efficient than array indices for processing arrays.

### Iterating with Pointers vs Indices

Using indices:

```c
int arr[5] = {10, 20, 30, 40, 50};
int sum = 0;

for (int i = 0; i < 5; i++) {
    sum += arr[i];
}
```

Using pointers:

```c
int arr[5] = {10, 20, 30, 40, 50};
int sum = 0;
int *p;

for (p = arr; p < arr + 5; p++) {
    sum += *p;
}
```

The pointer version often generates more efficient machine code.

### Common Pointer Idioms

**Processing until end:**

```c
int *end = arr + n;
for (int *p = arr; p < end; p++) {
    process(*p);
}
```

**Copying an array:**

```c
void copy(int *dest, const int *src, int n) {
    while (n-- > 0) {
        *dest++ = *src++;
    }
}
```

The expression `*dest++ = *src++` copies the value and advances both pointers.

**Searching for an element:**

```c
int *find(int *arr, int n, int target) {
    int *p;
    for (p = arr; p < arr + n; p++) {
        if (*p == target) {
            return p;
        }
    }
    return NULL;  // not found
}
```

## const and Pointers

The placement of `const` in pointer declarations affects what is constant.

### Pointer to const

The pointed-to value cannot be modified through this pointer:

```c
const int *p;      // pointer to const int
int const *p;      // equivalent

int x = 5;
const int *p = &x;
*p = 10;           // error: assignment of read-only location
p = &y;            // OK: pointer itself can change
```

This is common for function parameters:

```c
size_t strlen(const char *s);  // won't modify string
void sort(int *arr, int n);    // may modify array
```

### const Pointer

The pointer itself cannot be changed:

```c
int *const p = &x;  // const pointer to int

*p = 10;            // OK: can modify pointed-to value
p = &y;             // error: assignment of read-only variable
```

This is less common but useful for pointers that should always refer to the same object.

### const Pointer to const

Both the pointer and pointed-to value are constant:

```c
const int *const p = &x;

*p = 10;    // error
p = &y;     // error
```

### Reading Pointer Declarations

Read from right to left:

```c
const int *p;           // p is a pointer to a const int
int *const p;           // p is a const pointer to an int
const int *const p;     // p is a const pointer to a const int
int const *p;           // p is a pointer to a const int (same as first)
```

## Pointer to Pointer

A pointer can point to another pointer, creating multiple levels of indirection.

### Basic Usage

```c
int x = 42;
int *p = &x;
int **pp = &p;

printf("%d\n", **pp);   // prints 42
**pp = 17;              // changes x to 17
*pp = &y;               // changes p to point to y
```

### Modifying a Pointer Through a Function

```c
void allocate(int **pp) {
    *pp = malloc(sizeof(int));
    if (*pp != NULL) {
        **pp = 100;
    }
}

int *p = NULL;
allocate(&p);  // p now points to allocated memory containing 100
```

### Arrays of Strings

Arrays of strings are naturally pointer-to-pointer:

```c
char *colors[] = {"red", "green", "blue"};
// colors is an array of char pointers
// char **pp = colors would point to first pointer

for (int i = 0; i < 3; i++) {
    printf("%s\n", colors[i]);
}
```

### Command-Line Arguments

`main` receives an array of strings as pointer-to-pointer:

```c
int main(int argc, char *argv[]) {
    // or: int main(int argc, char **argv)
    for (int i = 0; i < argc; i++) {
        printf("arg[%d]: %s\n", i, argv[i]);
    }
    return 0;
}
```

## void Pointers

A `void *` is a **generic pointer** that can point to any object type.

### Basic Properties

```c
int x = 42;
double y = 3.14;
void *p;

p = &x;    // OK: any pointer can be assigned to void*
p = &y;    // OK
```

You cannot dereference a `void *` directly:

```c
void *p = &x;
printf("%d\n", *p);      // error: dereferencing void*
printf("%d\n", *(int *)p);  // OK: cast first
```

### Use with malloc

`malloc` returns `void *`, which can be assigned to any pointer type:

```c
int *pi = malloc(sizeof(int));           // no cast needed in C
char *str = malloc(100 * sizeof(char));
```

In C++ (but not C), a cast is required. Some C programmers cast anyway for portability.

### Generic Functions

`void *` enables generic functions:

```c
void *max_element(void *arr, size_t n, size_t size,
                  int (*cmp)(const void *, const void *)) {
    void *max = arr;
    for (size_t i = 1; i < n; i++) {
        void *elem = (char *)arr + i * size;
        if (cmp(elem, max) > 0) {
            max = elem;
        }
    }
    return max;
}
```

Note the cast to `char *` for pointer arithmetic (since `void` has no size).

## restrict (C99)

The `restrict` keyword is a **promise to the compiler** that, during the lifetime of the pointer, only it (or values derived from it) will access the pointed-to object.

### Basic Syntax

```c
void process(int *restrict p) {
    // promise: no other pointer accesses *p during this call
}
```

### Optimization Benefits

`restrict` allows aggressive optimization:

```c
void add_arrays(int *restrict dest, const int *restrict src, int n) {
    for (int i = 0; i < n; i++) {
        dest[i] += src[i];
    }
}
```

Since `dest` and `src` don't overlap (via `restrict`), the compiler can vectorize or reorder operations freely.

Without `restrict`, the compiler must assume potential aliasing:

```c
void add_arrays(int *dest, const int *src, int n) {
    // dest and src might overlap; must be careful with optimizations
}
```

### When to Use

Use `restrict` when you know pointers don't alias:

```c
void *memcpy(void *restrict dest, const void *restrict src, size_t n);
// dest and src must not overlap

void *memmove(void *dest, const void *src, size_t n);
// no restrict: handles overlapping regions
```

Breaking the `restrict` contract causes undefined behavior.

### Multiple restrict Pointers

```c
void func(int *restrict p, int *restrict q, int *r) {
    // p and q don't alias each other
    // r might alias p, q, or neither
}
```

## Common Pointer Errors

### Dangling Pointers

A **dangling pointer** points to memory that has been freed or gone out of scope:

```c
int *dangling(void) {
    int x = 42;
    return &x;  // DANGER: x goes out of scope
}

int *p = dangling();
printf("%d\n", *p);  // undefined behavior
```

Also occurs with freed memory:

```c
int *p = malloc(sizeof(int));
free(p);
*p = 42;     // DANGER: accessing freed memory
```

**Solution:** Don't return addresses of local variables. Set pointers to `NULL` after freeing:

```c
free(p);
p = NULL;
```

### Wild Pointers

A **wild pointer** is uninitialized:

```c
int *p;       // garbage value
*p = 42;      // undefined behavior
```

**Solution:** Always initialize pointers:

```c
int *p = NULL;
// or
int x;
int *p = &x;
```

### Pointer Type Mismatches

```c
int x = 0x12345678;
char *p = (char *)&x;
printf("%d\n", *p);  // reads only first byte
```

Reinterpreting data through mismatched pointer types (except `char *`) causes undefined behavior.

### Forgetting & in scanf

```c
int x;
scanf("%d", x);   // WRONG: passes value, not address
scanf("%d", &x);  // CORRECT
```

`scanf` needs the address to store the result.

### Buffer Overflows

```c
int arr[10];
int *p = arr + 10;
*p = 42;           // writing past end of array
```

**Solution:** Always check array bounds:

```c
if (index >= 0 && index < n) {
    arr[index] = value;
}
```

### Null Pointer Dereference

```c
int *p = NULL;
*p = 42;           // segmentation fault
```

**Solution:** Check for `NULL` before dereferencing:

```c
if (p != NULL) {
    *p = 42;
}
```

### Lost Pointer to Allocated Memory

```c
int *p = malloc(100 * sizeof(int));
p = &x;            // LEAK: lost reference to allocated memory
```

**Solution:** Either free before reassigning, or keep a copy:

```c
int *p = malloc(100 * sizeof(int));
int *copy = p;
// ... use p ...
free(copy);
```

## Summary

Pointers are fundamental to C programming:

- **Declaration:** `int *p` declares a pointer to int
- **Address-of:** `&x` gets the address of x
- **Dereference:** `*p` accesses the value at address p
- **Arithmetic:** Pointer + integer advances by elements, not bytes
- **Arrays:** Array name decays to pointer; `a[i]` ≡ `*(a + i)`
- **Functions:** Pass `&var` to allow modification
- **const:** Controls whether pointer or pointed-to value is constant
- **void*:** Generic pointer for any object type
- **restrict:** Promises no aliasing for optimization
- **Errors:** Uninitialized, dangling, null dereference, type mismatches

Mastering pointers requires practice and care. They provide power and efficiency but demand respect for memory safety.
