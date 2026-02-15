# Structures, Unions, and Enumerations

This reference covers Chapter 16 from "C Programming: A Modern Approach, 2nd Edition" by K.N. King, providing comprehensive coverage of aggregate data types in C.

## Structure Declaration

A structure is a collection of one or more variables, possibly of different types, grouped together under a single name.

### Basic Structure Declaration

```c
struct part {
    int number;
    char name[20];
    int on_hand;
};
```

The `struct` keyword is followed by an optional tag (`part`), which names the structure type. The members are declared within braces.

### Declaring Structure Variables

```c
struct part p1, p2;  /* Two variables of type struct part */
```

### Combined Declaration

You can declare the structure and variables simultaneously:

```c
struct part {
    int number;
    char name[20];
    int on_hand;
} p1, p2;
```

### Structure Variables Without Tag

```c
struct {
    int number;
    char name[20];
} p1, p2;
```

Without a tag, you cannot declare additional variables of this type later.

### typedef with Structures

Using `typedef` eliminates the need to write `struct` repeatedly:

```c
typedef struct {
    int number;
    char name[20];
    int on_hand;
} Part;

Part p1, p2;  /* No 'struct' keyword needed */
```

Alternatively, with a tag:

```c
typedef struct part {
    int number;
    char name[20];
    int on_hand;
} Part;

/* Both work: */
struct part p1;
Part p2;
```

### Anonymous Structs (C11)

C11 allows anonymous structures as members of other structures:

```c
struct person {
    char name[50];
    struct {  /* Anonymous struct */
        int day;
        int month;
        int year;
    };
};

struct person p;
p.day = 15;  /* Access directly, not p.birthdate.day */
```

## Structure Members

### Member Access with Dot Operator

```c
struct part p;
p.number = 528;
strcpy(p.name, "Widget");
p.on_hand = 10;

printf("Part #%d: %s\n", p.number, p.name);
```

### Member Access with Arrow Operator

For pointers to structures, use `->`:

```c
struct part *pp = &p;
pp->number = 528;  /* Equivalent to (*pp).number */

/* These are identical: */
(*pp).number = 528;
pp->number = 528;
```

### Member Types

Structure members can be of any type except the structure's own type (but can be pointers to it):

```c
struct node {
    int data;
    struct node next;    /* ILLEGAL */
    struct node *next;   /* Legal - pointer to struct node */
};
```

### Nested Structures

```c
struct person_name {
    char first[20];
    char middle;
    char last[20];
};

struct student {
    struct person_name name;
    int id;
    char grade;
};

struct student s;
strcpy(s.name.first, "John");
s.name.middle = 'Q';
strcpy(s.name.last, "Public");
```

### Arrays as Members

```c
struct {
    int id;
    int scores[5];
} student;

student.id = 12345;
student.scores[0] = 85;
student.scores[1] = 90;
```

## Structure Initialization

### Brace Initialization

```c
struct part p1 = {528, "Widget", 10};

/* With nested structures: */
struct student s = {{"John", 'Q', "Public"}, 12345, 'A'};
```

Values are assigned to members in declaration order. Remaining members are initialized to zero if not specified.

### Designated Initializers (C99)

Specify which member receives each value:

```c
struct part p1 = {
    .number = 528,
    .name = "Widget",
    .on_hand = 10
};

/* Order doesn't matter: */
struct part p2 = {
    .on_hand = 10,
    .name = "Widget",
    .number = 528
};
```

Can mix designated and non-designated:

```c
struct part p3 = {.number = 528, "Widget", 10};
```

Particularly useful for structures with many members:

```c
struct {
    int a, b, c, d, e, f, g, h, i, j;
} x = {.c = 3, .h = 8};  /* Others are 0 */
```

### Partial Initialization

```c
struct part p = {528};  /* number=528, name="", on_hand=0 */
struct part p2 = {0};   /* All members zero */
```

### Compound Literals (C99)

Create unnamed structure values:

```c
/* Pass structure to function: */
display_part((struct part){528, "Widget", 10});

/* Assign to existing variable: */
p1 = (struct part){528, "Widget", 10};

/* Can use designated initializers: */
p1 = (struct part){.number = 528, .on_hand = 10};
```

## Structure Assignment and Comparison

### Assignment

Structures can be assigned using `=`, which copies all members:

```c
struct part p1 = {528, "Widget", 10};
struct part p2;

p2 = p1;  /* Copies all members */
```

This works even with array members (unlike standalone arrays):

```c
struct {
    int arr[100];
} s1, s2;

s2 = s1;  /* Entire array is copied */
```

### Comparison

There is no `==` operator for structures. Compare member-by-member:

```c
if (p1.number == p2.number &&
    strcmp(p1.name, p2.name) == 0 &&
    p1.on_hand == p2.on_hand) {
    /* Structures are equal */
}
```

Using `memcmp` is possible but risky due to padding:

```c
/* May give false negatives due to padding bytes: */
if (memcmp(&p1, &p2, sizeof(struct part)) == 0) {
    /* Might not work reliably */
}
```

### Passing Structures to Functions

Structures are passed by value (copied):

```c
void display_part(struct part p) {
    printf("Part #%d: %s (%d on hand)\n",
           p.number, p.name, p.on_hand);
}

display_part(p1);  /* p1 is copied */
```

For large structures, pass a pointer for efficiency:

```c
void display_part(const struct part *p) {
    printf("Part #%d: %s (%d on hand)\n",
           p->number, p->name, p->on_hand);
}

display_part(&p1);  /* Pass address */
```

### Returning Structures from Functions

```c
struct part build_part(int number, const char *name, int on_hand) {
    struct part p;
    p.number = number;
    strcpy(p.name, name);
    p.on_hand = on_hand;
    return p;  /* Structure is copied back to caller */
}

struct part new_part = build_part(528, "Widget", 10);
```

Using compound literals:

```c
struct part build_part(int number, const char *name, int on_hand) {
    return (struct part){number, "", on_hand};  /* Initialize directly */
}
```

## Self-Referential Structures

### Linked List Node

A structure can contain a pointer to its own type:

```c
struct node {
    int data;
    struct node *next;
};
```

Cannot contain an instance of itself, only a pointer:

```c
struct node {
    int data;
    struct node next;  /* ILLEGAL - infinite size */
};
```

### Forward Declaration

When two structures reference each other:

```c
struct node;  /* Forward declaration */

struct list {
    struct node *head;
    int count;
};

struct node {
    int data;
    struct node *next;
    struct list *owner;
};
```

### Tree Node Example

```c
struct tree_node {
    int value;
    struct tree_node *left;
    struct tree_node *right;
};
```

### Incomplete Types

After `struct node;`, the type is incomplete until the full definition. You can declare pointers to incomplete types:

```c
struct node;           /* Incomplete type */
struct node *p;        /* Legal - pointer to incomplete type */
struct node n;         /* ILLEGAL - can't create instance */

struct node {          /* Now complete */
    int data;
    struct node *next;
};

struct node n;         /* Now legal */
```

## Unions

A union is similar to a structure, but its members share the same memory location. Only one member can hold a value at any time.

### Union Declaration

```c
union number {
    int i;
    double d;
};
```

### Union Variables

```c
union number n;
```

### Member Access

```c
n.i = 42;
printf("%d\n", n.i);  /* 42 */

n.d = 3.14;
printf("%f\n", n.d);  /* 3.14 */
printf("%d\n", n.i);  /* UNDEFINED - d overwrote i */
```

### Union Size

The size of a union is the size of its largest member (plus padding for alignment):

```c
union number {
    int i;        /* Typically 4 bytes */
    double d;     /* Typically 8 bytes */
};

printf("%zu\n", sizeof(union number));  /* Typically 8 */
```

### Use Cases

**Variant Types**: Store one of several possible types:

```c
union variant {
    int i;
    double d;
    char *s;
};
```

**Type Punning**: View same data as different types (implementation-defined):

```c
union {
    float f;
    unsigned int bits;
} u;

u.f = 3.14159f;
printf("Float bits: 0x%08X\n", u.bits);
```

**Memory Saving**: When only one field is needed at a time:

```c
struct shape {
    enum { CIRCLE, RECTANGLE } kind;
    union {
        struct { double radius; } circle;
        struct { double width, height; } rectangle;
    } u;
};
```

### Initialization

Only the first member can be initialized (C89):

```c
union number n = {42};  /* Initializes n.i */
```

C99 allows designated initializers:

```c
union number n = {.d = 3.14};  /* Initializes n.d */
```

## Tagged Unions

A tagged union combines an enumeration (tag) with a union to track which member is active:

```c
enum shape_kind { CIRCLE, RECTANGLE, TRIANGLE };

struct shape {
    enum shape_kind kind;
    union {
        struct { double radius; } circle;
        struct { double width, height; } rectangle;
        struct { double base, height; } triangle;
    } u;
};
```

### Using Tagged Unions

```c
struct shape create_circle(double radius) {
    struct shape s;
    s.kind = CIRCLE;
    s.u.circle.radius = radius;
    return s;
}

double area(struct shape *s) {
    switch (s->kind) {
    case CIRCLE:
        return 3.14159 * s->u.circle.radius * s->u.circle.radius;
    case RECTANGLE:
        return s->u.rectangle.width * s->u.rectangle.height;
    case TRIANGLE:
        return 0.5 * s->u.triangle.base * s->u.triangle.height;
    }
    return 0.0;
}
```

### Anonymous Unions (C11)

C11 allows anonymous unions within structures:

```c
struct shape {
    enum shape_kind kind;
    union {
        struct { double radius; } circle;
        struct { double width, height; } rectangle;
    };  /* Anonymous */
};

struct shape s;
s.circle.radius = 5.0;  /* Not s.u.circle.radius */
```

## Enumerations

An enumeration is a type whose values are listed by the programmer.

### Enumeration Declaration

```c
enum weekday {
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
};
```

By default, enumeration constants are assigned 0, 1, 2, etc.

### Enumeration Variables

```c
enum weekday day;
day = WEDNESDAY;

if (day == WEDNESDAY) {
    printf("It's Wednesday\n");
}
```

### Explicit Values

```c
enum error_code {
    SUCCESS = 0,
    ERROR_FILE_NOT_FOUND = 1,
    ERROR_PERMISSION_DENIED = 2,
    ERROR_INVALID_INPUT = 100
};
```

Values need not be distinct:

```c
enum {
    FALSE = 0,
    TRUE = 1,
    NO = 0,
    YES = 1
};
```

### Automatic Continuation

After an explicit value, enumeration continues from there:

```c
enum {
    A = 5,
    B,      /* 6 */
    C,      /* 7 */
    D = 10,
    E       /* 11 */
};
```

### Underlying Type

Enumeration constants have type `int`. Enumeration variables are compatible with `int`:

```c
enum weekday day = 3;     /* Legal but not recommended */
int i = MONDAY;           /* Legal */

for (day = MONDAY; day <= SUNDAY; day++) {
    /* Legal - relies on int compatibility */
}
```

### typedef with Enums

```c
typedef enum {
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
} Weekday;

Weekday today = MONDAY;
```

### Naming Conventions

Common convention: uppercase for enumeration constants:

```c
enum color { RED, GREEN, BLUE };
```

Prefixing to avoid name conflicts:

```c
enum color { COLOR_RED, COLOR_GREEN, COLOR_BLUE };
enum fruit { FRUIT_APPLE, FRUIT_ORANGE, FRUIT_BANANA };
```

### Enums vs. #define

Enumerations have advantages over `#define`:

```c
/* Using #define: */
#define MONDAY 0
#define TUESDAY 1
/* ... no type checking, debugger shows numbers */

/* Using enum: */
enum weekday { MONDAY, TUESDAY /* ... */ };
/* Type information preserved, debugger shows names */
```

## typedef

The `typedef` keyword creates type aliases.

### Basic typedef

```c
typedef int Int32;
typedef unsigned long ulong;

Int32 x = 42;
ulong y = 1000000UL;
```

### typedef with Structures

```c
typedef struct {
    int x;
    int y;
} Point;

Point p1, p2;  /* No 'struct' keyword needed */
```

With a tag (useful for self-reference):

```c
typedef struct node {
    int data;
    struct node *next;  /* Must use 'struct node' here */
} Node;

/* Both work: */
struct node *p1;
Node *p2;
```

### typedef with Pointers

```c
typedef char *String;

String s1, s2;  /* Both are char* */
```

Be careful: this differs from:

```c
char *s1, s2;  /* s1 is char*, s2 is char */
```

### typedef with Arrays

```c
typedef int IntArray[10];

IntArray a;  /* int a[10] */
IntArray b;  /* int b[10] */
```

### typedef with Function Pointers

```c
typedef int (*Comparator)(const void *, const void *);

Comparator cmp = strcmp;

/* Instead of: */
int (*cmp)(const void *, const void *) = strcmp;
```

### Opaque Types

Hide implementation details:

```c
/* In header file: */
typedef struct widget Widget;  /* Incomplete type */
Widget *widget_create(void);
void widget_destroy(Widget *w);

/* In implementation file: */
struct widget {
    int internal_data;
    char *private_buffer;
};
```

Users cannot access or depend on internal structure.

### Platform Abstraction

```c
/* Platform-specific: */
#ifdef _WIN32
typedef long long int64_t;
#else
typedef long int64_t;
#endif

/* Now use int64_t portably */
```

## Flexible Array Members (C99)

A flexible array member is an array of unspecified size at the end of a structure.

### Declaration

```c
struct buffer {
    size_t len;
    char data[];  /* Flexible array member */
};
```

The flexible array member:
- Must be the last member
- Structure must have at least one other member
- Does not contribute to structure size

### Allocation

```c
struct buffer *create_buffer(size_t n) {
    struct buffer *buf = malloc(sizeof(struct buffer) + n);
    if (buf != NULL) {
        buf->len = n;
    }
    return buf;
}
```

### Usage

```c
struct buffer *buf = create_buffer(100);
buf->data[0] = 'A';
buf->data[99] = 'Z';
strcpy(buf->data, "Hello");
free(buf);
```

### Constraints

- Cannot copy structures with flexible array members using `=` (undefined)
- Cannot create arrays of such structures
- `sizeof` does not include flexible array member

### Pre-C99 Idiom

Before C99, the "struct hack" used a zero-length or one-element array:

```c
struct buffer {
    size_t len;
    char data[1];  /* Allocate more than this */
};

/* Allocate: */
struct buffer *buf = malloc(sizeof(struct buffer) + n - 1);
```

## Structure Padding and Alignment

### Why Padding Exists

Processors access memory most efficiently when data is aligned to natural boundaries. Compilers insert padding to ensure proper alignment.

### Example

```c
struct example {
    char c;      /* 1 byte */
    /* 3 bytes padding */
    int i;       /* 4 bytes */
    char d;      /* 1 byte */
    /* 3 bytes padding */
};

printf("%zu\n", sizeof(struct example));  /* Typically 12, not 6 */
```

Memory layout (on typical system):

```
Offset 0: c (1 byte)
Offset 1-3: padding
Offset 4-7: i (4 bytes)
Offset 8: d (1 byte)
Offset 9-11: padding
```

### Member Ordering Matters

Minimize padding by ordering members from largest to smallest:

```c
/* Poor layout: */
struct poor {
    char a;    /* 1 byte + 7 padding */
    double d;  /* 8 bytes */
    char b;    /* 1 byte + 7 padding */
    double e;  /* 8 bytes */
};  /* Total: 32 bytes */

/* Better layout: */
struct better {
    double d;  /* 8 bytes */
    double e;  /* 8 bytes */
    char a;    /* 1 byte */
    char b;    /* 1 byte + 6 padding */
};  /* Total: 24 bytes */
```

### offsetof Macro

Get the byte offset of a member:

```c
#include <stddef.h>

struct example {
    char c;
    int i;
    char d;
};

printf("Offset of i: %zu\n", offsetof(struct example, i));  /* Typically 4 */
printf("Offset of d: %zu\n", offsetof(struct example, d));  /* Typically 8 */
```

### Controlling Padding

Some compilers allow controlling padding with `#pragma pack`:

```c
#pragma pack(push, 1)  /* Pack tightly */
struct packed {
    char c;
    int i;
    char d;
};
#pragma pack(pop)

printf("%zu\n", sizeof(struct packed));  /* 6 - no padding */
```

**Warning**: Packed structures may cause:
- Slower access (unaligned reads/writes)
- Crashes on some architectures (ARM, SPARC require alignment)

### Portable Considerations

- Never assume sizeof(struct) equals sum of sizeof(members)
- Don't assume specific padding amounts
- Don't depend on structure layout for serialization (use explicit packing)
- Use offsetof() rather than computing offsets manually

## Bit-Fields

Bit-fields allow packing multiple values into a single word.

### Declaration

```c
struct flags {
    unsigned int is_active : 1;
    unsigned int is_visible : 1;
    unsigned int priority : 3;
    unsigned int reserved : 27;
};
```

The number after `:` specifies the width in bits.

### Usage

```c
struct flags f;
f.is_active = 1;
f.is_visible = 0;
f.priority = 5;

if (f.is_active && f.priority > 3) {
    /* ... */
}
```

### Size

```c
printf("%zu\n", sizeof(struct flags));  /* Typically 4 */
```

### Unnamed Bit-Fields

Used for padding:

```c
struct {
    unsigned int a : 3;
    unsigned int : 5;    /* 5 bits of padding */
    unsigned int b : 4;
};
```

Zero-width unnamed bit-field forces next field to next word:

```c
struct {
    unsigned int a : 8;
    unsigned int : 0;    /* Align next field to word boundary */
    unsigned int b : 8;
};
```

### Portability Concerns

Bit-fields are highly implementation-defined:

- **Order**: May be allocated left-to-right or right-to-left
- **Boundaries**: May or may not cross word boundaries
- **Sign**: `int` bit-fields may be signed or unsigned
- **Alignment**: Storage unit size is implementation-defined

**Best Practices**:

```c
/* Use unsigned types: */
struct good {
    unsigned int flag : 1;  /* Definitely 0 or 1 */
};

struct bad {
    int flag : 1;  /* Could be -1 or 0 on some systems! */
};
```

- Don't take addresses of bit-fields (illegal)
- Don't use for portable binary formats
- Don't rely on specific memory layout
- Use for space optimization only when portability doesn't matter

### Bit-Fields and Unions

Combining with unions for low-level manipulation:

```c
union register_value {
    unsigned int word;
    struct {
        unsigned int low : 16;
        unsigned int high : 16;
    } parts;
};

union register_value r;
r.word = 0x12345678;
printf("High: 0x%04X, Low: 0x%04X\n", r.parts.high, r.parts.low);
/* Output is implementation-defined */
```

**Warning**: This is not portable and relies on implementation-defined behavior.

## Summary

- **Structures** group related data of different types
- **Member access** uses `.` for variables, `->` for pointers
- **Initialization** supports designated initializers (C99) and compound literals
- **Assignment** copies all members; **no equality operator** exists
- **Self-referential structures** use pointers for linked data structures
- **Unions** overlay members in same memory; only one member active
- **Tagged unions** combine enum + union for safe variant types
- **Enumerations** define named integer constants with type safety
- **typedef** creates type aliases for readability and abstraction
- **Flexible array members** (C99) enable variable-length structures
- **Padding and alignment** affect structure size and layout
- **Bit-fields** pack small values efficiently but sacrifice portability
