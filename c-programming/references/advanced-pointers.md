# Advanced Uses of Pointers

## Dynamic Memory Allocation

### malloc — Allocate Uninitialized Memory

```c
#include <stdlib.h>

int *arr = malloc(n * sizeof(*arr));  /* ALWAYS use sizeof(*ptr) pattern */
if (arr == NULL) {
    /* handle allocation failure */
}
```

**Always use `sizeof(*ptr)`** instead of `sizeof(int)` — if the type of `arr` changes, the allocation stays correct.

**Overflow danger**: `n * sizeof(*arr)` can overflow for large `n`. For safety:
```c
if (n > SIZE_MAX / sizeof(*arr)) {
    /* overflow would occur */
}
```

### calloc — Allocate Zero-Initialized Memory

```c
int *arr = calloc(n, sizeof(*arr));  /* n elements, each sizeof(*arr) bytes */
```

- Initializes all bytes to zero (which is `0` for integers, `0.0` for floats, `NULL` for pointers on most platforms)
- Performs overflow checking internally — safer than `malloc(n * size)`

### realloc — Resize Allocation

```c
/* WRONG — loses original pointer on failure: */
arr = realloc(arr, new_size);  /* if realloc fails, arr is NULL and old memory leaks */

/* CORRECT pattern: */
int *tmp = realloc(arr, new_size * sizeof(*arr));
if (tmp == NULL) {
    /* arr still points to original allocation — can free or continue using it */
    free(arr);
    return NULL;
}
arr = tmp;
```

Special cases:
- `realloc(NULL, size)` ≡ `malloc(size)`
- `realloc(ptr, 0)` — implementation-defined (may or may not free; avoid this)

### free — Release Memory

```c
free(arr);
arr = NULL;  /* good practice — prevents use-after-free */
```

- `free(NULL)` is safe (does nothing)
- Every `malloc`/`calloc`/`realloc` must have a corresponding `free`
- Never free stack memory, string literals, or already-freed memory

## Memory Management Patterns

### Allocate + Check + Use + Free

```c
char *buf = malloc(bufsize);
if (!buf) {
    perror("malloc");
    return -1;
}
/* use buf... */
free(buf);
```

### Cleanup with goto on Error

For functions with multiple allocations:

```c
int process(void) {
    char *a = malloc(100);
    if (!a) goto fail_a;

    int *b = malloc(200 * sizeof(*b));
    if (!b) goto fail_b;

    FILE *f = fopen("data.txt", "r");
    if (!f) goto fail_f;

    /* ... use a, b, f ... */

    fclose(f);
    free(b);
    free(a);
    return 0;

fail_f:
    free(b);
fail_b:
    free(a);
fail_a:
    return -1;
}
```

### Wrapper Functions

```c
void *xmalloc(size_t size) {
    void *p = malloc(size);
    if (!p) {
        fprintf(stderr, "Out of memory\n");
        exit(EXIT_FAILURE);
    }
    return p;
}
```

## Common Memory Errors

| Error | Cause | Prevention |
|-------|-------|------------|
| **Memory leak** | Forgetting `free()`, losing pointer to allocated memory | Track ownership, use tools like Valgrind |
| **Double free** | Calling `free()` twice on same pointer | Set pointer to NULL after free |
| **Use after free** | Dereferencing freed pointer | Set pointer to NULL, use sanitizers |
| **Buffer overflow** | Writing past allocated bounds | Track sizes, use `snprintf`, bounds check |
| **Uninitialized read** | Reading `malloc`'d memory before writing | Use `calloc` or explicitly initialize |
| **realloc leak** | `p = realloc(p, n)` fails, original lost | Use temporary pointer |

**Debugging tools**: Valgrind (`valgrind --leak-check=full`), AddressSanitizer (`-fsanitize=address`), LeakSanitizer, Electric Fence.

## Linked Lists

### Singly Linked List

```c
struct node {
    int data;
    struct node *next;
};

/* Insert at front — O(1) */
struct node *prepend(struct node *head, int value) {
    struct node *new = malloc(sizeof(*new));
    if (!new) return head;
    new->data = value;
    new->next = head;
    return new;
}

/* Insert at end — O(n) */
struct node *append(struct node *head, int value) {
    struct node *new = malloc(sizeof(*new));
    if (!new) return head;
    new->data = value;
    new->next = NULL;

    if (!head) return new;

    struct node *cur = head;
    while (cur->next)
        cur = cur->next;
    cur->next = new;
    return head;
}

/* Search — O(n) */
struct node *find(struct node *head, int value) {
    for (struct node *cur = head; cur; cur = cur->next)
        if (cur->data == value)
            return cur;
    return NULL;
}

/* Delete first occurrence — O(n) */
struct node *delete(struct node *head, int value) {
    if (!head) return NULL;
    if (head->data == value) {
        struct node *next = head->next;
        free(head);
        return next;
    }
    for (struct node *cur = head; cur->next; cur = cur->next) {
        if (cur->next->data == value) {
            struct node *doomed = cur->next;
            cur->next = doomed->next;
            free(doomed);
            return head;
        }
    }
    return head;
}

/* Traverse */
void print_list(const struct node *head) {
    for (const struct node *cur = head; cur; cur = cur->next)
        printf("%d -> ", cur->data);
    printf("NULL\n");
}

/* Free entire list */
void free_list(struct node *head) {
    while (head) {
        struct node *next = head->next;
        free(head);
        head = next;
    }
}
```

**Using pointer-to-pointer for cleaner insertion/deletion**:
```c
void delete_all(struct node **head, int value) {
    struct node **pp = head;
    while (*pp) {
        if ((*pp)->data == value) {
            struct node *doomed = *pp;
            *pp = doomed->next;
            free(doomed);
        } else {
            pp = &(*pp)->next;
        }
    }
}
```

### Doubly Linked List

```c
struct dnode {
    int data;
    struct dnode *prev;
    struct dnode *next;
};

void dll_insert_after(struct dnode *node, int value) {
    struct dnode *new = malloc(sizeof(*new));
    new->data = value;
    new->prev = node;
    new->next = node->next;
    if (node->next) node->next->prev = new;
    node->next = new;
}

void dll_remove(struct dnode **head, struct dnode *node) {
    if (node->prev) node->prev->next = node->next;
    else *head = node->next;  /* removing head */
    if (node->next) node->next->prev = node->prev;
    free(node);
}
```

## Other Dynamic Data Structures

### Stack (Linked List)

```c
struct stack { struct node *top; };

void push(struct stack *s, int value) {
    s->top = prepend(s->top, value);
}

int pop(struct stack *s) {
    if (!s->top) { fprintf(stderr, "underflow\n"); exit(1); }
    int value = s->top->data;
    struct node *old = s->top;
    s->top = s->top->next;
    free(old);
    return value;
}
```

### Queue (Linked List with Tail Pointer)

```c
struct queue {
    struct node *front;
    struct node *rear;
};

void enqueue(struct queue *q, int value) {
    struct node *new = malloc(sizeof(*new));
    new->data = value;
    new->next = NULL;
    if (q->rear) q->rear->next = new;
    else q->front = new;
    q->rear = new;
}

int dequeue(struct queue *q) {
    struct node *old = q->front;
    int value = old->data;
    q->front = old->next;
    if (!q->front) q->rear = NULL;
    free(old);
    return value;
}
```

## Function Pointers

### Declaration Syntax

```c
int (*fp)(int, int);          /* pointer to function taking (int,int) returning int */
fp = add;                     /* assign function address (& is optional) */
int result = fp(3, 4);        /* call through pointer (* is optional) */
int result2 = (*fp)(3, 4);    /* explicit dereference call — equivalent */
```

### typedef for Readability

```c
typedef int (*binop_fn)(int, int);

int add(int a, int b) { return a + b; }
int sub(int a, int b) { return a - b; }
int mul(int a, int b) { return a * b; }

binop_fn operations[] = {add, sub, mul};
int result = operations[op_index](x, y);  /* dispatch table */
```

### Dispatch Tables

```c
typedef void (*command_fn)(void);

struct command {
    const char *name;
    command_fn handler;
};

struct command commands[] = {
    {"help", cmd_help},
    {"quit", cmd_quit},
    {"list", cmd_list},
};

void dispatch(const char *input) {
    for (size_t i = 0; i < sizeof(commands)/sizeof(commands[0]); i++) {
        if (strcmp(commands[i].name, input) == 0) {
            commands[i].handler();
            return;
        }
    }
    printf("Unknown command: %s\n", input);
}
```

## Callbacks

### qsort Example

```c
/* qsort signature: void qsort(void *base, size_t nmemb, size_t size,
                                int (*compar)(const void *, const void *)); */

int compare_ints(const void *a, const void *b) {
    int ia = *(const int *)a;
    int ib = *(const int *)b;
    return (ia > ib) - (ia < ib);  /* safe: no overflow unlike ia - ib */
}

int arr[] = {5, 2, 8, 1, 9};
qsort(arr, 5, sizeof(arr[0]), compare_ints);
```

**Warning**: Using `return a - b` for comparison can overflow. Use the three-way comparison pattern instead.

### bsearch Example

```c
int key = 5;
int *found = bsearch(&key, arr, 5, sizeof(arr[0]), compare_ints);
if (found)
    printf("Found %d at index %td\n", *found, found - arr);
```

### Writing Generic Callback-Based Functions

```c
/* Apply a function to each element */
void for_each(int *arr, size_t n, void (*fn)(int *elem)) {
    for (size_t i = 0; i < n; i++)
        fn(&arr[i]);
}

void double_it(int *x) { *x *= 2; }
for_each(arr, n, double_it);
```

## Abstract Data Types (Opaque Pointer Pattern)

### stack.h — Public Interface

```c
#ifndef STACK_H
#define STACK_H

#include <stdbool.h>

typedef struct Stack Stack;  /* opaque — users can't see internals */

Stack *stack_create(void);
void   stack_destroy(Stack *s);
void   stack_push(Stack *s, int value);
int    stack_pop(Stack *s);
int    stack_peek(const Stack *s);
bool   stack_empty(const Stack *s);

#endif
```

### stack.c — Private Implementation

```c
#include "stack.h"
#include <stdlib.h>
#include <stdio.h>

struct Stack {       /* definition hidden from users */
    int *data;
    size_t top;
    size_t capacity;
};

Stack *stack_create(void) {
    Stack *s = malloc(sizeof(*s));
    if (!s) return NULL;
    s->capacity = 16;
    s->data = malloc(s->capacity * sizeof(*s->data));
    if (!s->data) { free(s); return NULL; }
    s->top = 0;
    return s;
}

void stack_destroy(Stack *s) {
    if (s) {
        free(s->data);
        free(s);
    }
}

void stack_push(Stack *s, int value) {
    if (s->top == s->capacity) {
        size_t new_cap = s->capacity * 2;
        int *tmp = realloc(s->data, new_cap * sizeof(*tmp));
        if (!tmp) { fprintf(stderr, "stack overflow\n"); exit(1); }
        s->data = tmp;
        s->capacity = new_cap;
    }
    s->data[s->top++] = value;
}

int stack_pop(Stack *s) {
    if (s->top == 0) { fprintf(stderr, "stack underflow\n"); exit(1); }
    return s->data[--s->top];
}

bool stack_empty(const Stack *s) { return s->top == 0; }
```

Users include `stack.h` and link with `stack.o`. They cannot access `struct Stack` fields directly — the implementation can change without breaking client code.

## Flexible Array Members (C99)

```c
struct message {
    size_t length;
    char data[];       /* flexible array member — must be last */
};

/* Allocation: */
struct message *msg = malloc(sizeof(*msg) + len);
msg->length = len;
memcpy(msg->data, source, len);

/* sizeof(struct message) does NOT include data[] */
```

Constraints:
- Must be the last member of the struct
- Struct must have at least one other member
- Cannot be used in arrays of structs
- Cannot use struct assignment (use `memcpy` with computed size)

Use cases: variable-length strings, network packets, database records with variable-size payloads.
