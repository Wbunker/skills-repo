# Control Flow: Selection Statements and Loops

Control flow statements determine the order in which program statements execute. C provides a rich set of selection and iteration constructs that form the backbone of procedural programming.

## if Statement

The `if` statement is the fundamental selection construct in C. It evaluates a controlling expression and executes a statement when the expression is non-zero (true).

### Basic if

```c
if (expression)
    statement
```

Any non-zero value is treated as true:

```c
if (n)              // true if n != 0
    printf("n is non-zero\n");

if (ptr)            // true if ptr != NULL
    process_data(ptr);
```

### if-else

The `else` clause specifies an alternative when the condition is false:

```c
if (balance >= amount) {
    balance -= amount;
    printf("Withdrawal successful\n");
} else {
    printf("Insufficient funds\n");
}
```

### else-if Chains

Multiple conditions are tested sequentially using else-if:

```c
if (grade >= 90)
    letter = 'A';
else if (grade >= 80)
    letter = 'B';
else if (grade >= 70)
    letter = 'C';
else if (grade >= 60)
    letter = 'D';
else
    letter = 'F';
```

Conditions are evaluated in order; the first true condition executes its statement and remaining conditions are skipped.

### The Dangling else Problem

When nesting if statements without braces, an `else` clause belongs to the nearest unmatched `if`:

```c
// Misleading indentation
if (x > 0)
    if (y > 0)
        printf("Both positive\n");
else                    // belongs to inner if, not outer!
    printf("y is not positive\n");

// Correct interpretation
if (x > 0) {
    if (y > 0)
        printf("Both positive\n");
    else
        printf("y is not positive\n");
}

// Force else to match outer if
if (x > 0) {
    if (y > 0)
        printf("Both positive\n");
} else {
    printf("x is not positive\n");
}
```

### Bracing Styles

Always use braces for multi-statement blocks. For single statements, braces are optional but recommended for clarity and maintainability:

```c
// K&R style - opening brace on same line
if (condition) {
    statement1;
    statement2;
}

// Allman style - opening brace on new line
if (condition)
{
    statement1;
    statement2;
}

// Single statement - braces optional but recommended
if (error)
    return -1;      // acceptable

if (error) {
    return -1;      // preferred - easier to add statements later
}
```

## switch Statement

The `switch` statement provides multi-way selection based on the value of an integer expression.

### Syntax

```c
switch (expression) {
    case constant-expression:
        statements
        break;
    case constant-expression:
        statements
        break;
    default:
        statements
        break;
}
```

The controlling expression must have integer type (including `char` and enumeration types). Case labels must be integer constant expressions known at compile time.

### Basic Example

```c
switch (operator) {
    case '+':
        result = x + y;
        break;
    case '-':
        result = x - y;
        break;
    case '*':
        result = x * y;
        break;
    case '/':
        if (y != 0)
            result = x / y;
        else
            printf("Division by zero\n");
        break;
    default:
        printf("Unknown operator\n");
        break;
}
```

### The break Statement

Without `break`, execution falls through to the next case. This is usually unintended:

```c
// Bug - missing breaks
switch (grade) {
    case 'A':
        printf("Excellent\n");
    case 'B':
        printf("Good\n");        // executes for both A and B!
    case 'C':
        printf("Average\n");     // executes for A, B, and C!
    default:
        printf("Grade recorded\n");
}
```

### Intentional Fall-Through

Fall-through can be intentional when multiple cases share code. Document with a comment:

```c
switch (c) {
    case ' ':
    case '\t':
    case '\n':
        /* fall through */
    case '\r':
        whitespace_count++;
        break;

    case '0': case '1': case '2': case '3': case '4':
    case '5': case '6': case '7': case '8': case '9':
        digit_count++;
        break;

    default:
        other_count++;
        break;
}
```

### The default Label

The `default` label handles values not matched by any case. Position doesn't matter (can appear anywhere), but conventionally comes last:

```c
switch (month) {
    case 1: case 3: case 5: case 7: case 8: case 10: case 12:
        days = 31;
        break;
    case 4: case 6: case 9: case 11:
        days = 30;
        break;
    case 2:
        days = is_leap_year(year) ? 29 : 28;
        break;
    default:
        fprintf(stderr, "Invalid month: %d\n", month);
        days = 0;
        break;
}
```

### Limitations and Patterns

Switch statements only work with integer expressions. They cannot test ranges or use runtime variables:

```c
// Illegal - case labels must be constants
int limit = 100;
switch (value) {
    case limit:     // compile error
        break;
}

// Illegal - cannot test ranges
switch (age) {
    case 0...17:    // not standard C (GNU extension)
        break;
}

// Use if-else for non-integer types
switch (name) {     // illegal - strings not allowed
    case "alice":
        break;
}

// Correct approach for strings
if (strcmp(name, "alice") == 0) {
    // ...
} else if (strcmp(name, "bob") == 0) {
    // ...
}
```

### Duff's Device

An infamous example of combining switch with loops for loop unrolling:

```c
// Advanced technique - mentioned for completeness
void send(int *to, int *from, int count) {
    int n = (count + 7) / 8;
    switch (count % 8) {
        case 0: do { *to++ = *from++;
        case 7:      *to++ = *from++;
        case 6:      *to++ = *from++;
        case 5:      *to++ = *from++;
        case 4:      *to++ = *from++;
        case 3:      *to++ = *from++;
        case 2:      *to++ = *from++;
        case 1:      *to++ = *from++;
                } while (--n > 0);
    }
}
```

This exploits fall-through and interleaves switch/loop in ways that violate structured programming principles but demonstrate C's flexibility.

## Conditional Expression (? :)

The conditional operator provides a compact expression-based selection mechanism.

### Syntax

```c
expression1 ? expression2 : expression3
```

If `expression1` is true (non-zero), `expression2` is evaluated and becomes the result; otherwise, `expression3` is evaluated.

### Expression vs Statement

Unlike `if`, the conditional operator is an expression with a value:

```c
// Assign based on condition
max = (a > b) ? a : b;

// Use in function call
printf("Found %d item%s\n", count, (count == 1) ? "" : "s");

// Equivalent if statement is longer
if (count == 1)
    printf("Found %d item\n", count);
else
    printf("Found %d items\n", count);
```

### Common Uses

```c
// Absolute value
abs_value = (x < 0) ? -x : x;

// Bounds checking
clamped = (value < min) ? min : (value > max) ? max : value;

// Conditional incrementation
count += (threshold_met) ? 2 : 1;

// Return values
return (status == OK) ? result : default_value;
```

### Nesting Considerations

Nested conditional expressions can become unreadable. Use parentheses for clarity or prefer if-else:

```c
// Hard to read
result = a > b ? a > c ? a : c : b > c ? b : c;

// Better with parentheses
result = (a > b) ? ((a > c) ? a : c) : ((b > c) ? b : c);

// Best - use if-else or a function
int max3(int a, int b, int c) {
    int max = a;
    if (b > max) max = b;
    if (c > max) max = c;
    return max;
}
```

### Type Considerations

Both branches must have compatible types. The result type follows standard conversion rules:

```c
// Both int - result is int
x = flag ? 10 : 20;

// int and double - result is double
y = flag ? 10 : 20.5;

// Pointer types must be compatible
ptr = flag ? &array[0] : NULL;
```

## while Loop

The `while` loop repeatedly executes a statement as long as the controlling expression is true.

### Syntax

```c
while (expression)
    statement
```

The expression is tested before each iteration. If initially false, the body never executes:

```c
int i = 0;
while (i < 10) {
    printf("%d\n", i);
    i++;
}
```

### Common Idioms

Reading until end of file:

```c
while ((ch = getchar()) != EOF) {
    process(ch);
}
```

Sentinel-controlled input:

```c
printf("Enter values (0 to quit): ");
while (scanf("%d", &value) == 1 && value != 0) {
    sum += value;
    printf("Next value: ");
}
```

String processing:

```c
while (*str != '\0') {
    process(*str);
    str++;
}

// Compact form
while (*str)
    process(*str++);
```

### Infinite Loops

An infinite loop uses a constant true condition:

```c
while (1) {
    // Loop forever unless break is encountered
    if (error_condition)
        break;
}
```

### Controlling Expression Evaluation

The controlling expression is evaluated before each iteration, including side effects:

```c
// Inefficient - strlen called every iteration
while (i < strlen(str)) {
    process(str[i++]);
}

// Better - evaluate once
size_t len = strlen(str);
while (i < len) {
    process(str[i++]);
}
```

## do-while Loop

The `do-while` loop guarantees at least one execution of the loop body.

### Syntax

```c
do
    statement
while (expression);
```

Note the semicolon after the while clause. The body executes first, then the condition is tested:

```c
int i = 0;
do {
    printf("%d\n", i);
    i++;
} while (i < 10);
```

### When to Use

The `do-while` loop is ideal for input validation where you need at least one attempt:

```c
// Menu-driven program
do {
    printf("\n1. Add\n2. Delete\n3. Quit\n");
    printf("Choice: ");
    scanf("%d", &choice);

    switch (choice) {
        case 1: add_item(); break;
        case 2: delete_item(); break;
        case 3: break;
        default: printf("Invalid choice\n");
    }
} while (choice != 3);
```

Input validation:

```c
do {
    printf("Enter a positive number: ");
    scanf("%d", &num);
} while (num <= 0);
```

### Guaranteed First Execution

Unlike `while`, the body always executes at least once:

```c
int count = 10;

while (count < 5) {
    printf("while: never prints\n");
    count++;
}

do {
    printf("do-while: prints once\n");
    count++;
} while (count < 5);
```

## for Loop

The `for` loop is the most versatile looping construct, typically used for counted loops.

### Syntax

```c
for (initialization; condition; increment)
    statement
```

Equivalent to:

```c
initialization;
while (condition) {
    statement
    increment;
}
```

### Basic Counting Loop

```c
for (int i = 0; i < 10; i++) {
    printf("%d\n", i);
}
```

In C99 and later, variables can be declared in the initialization clause. Their scope is limited to the loop:

```c
// C99 and later
for (int i = 0; i < n; i++) {
    // i is only visible here
}
// i is out of scope

// C89 requires prior declaration
int i;
for (i = 0; i < n; i++) {
    // ...
}
// i is still in scope
```

### Comma Operator in for Loops

Multiple initializations or increments use the comma operator:

```c
// Multiple loop variables
for (i = 0, j = n - 1; i < j; i++, j--) {
    swap(&array[i], &array[j]);
}

// Multiple updates
for (i = 0; i < n; i++, sum += i) {
    printf("%d\n", i);
}
```

The comma operator evaluates left to right, discarding all but the last value.

### Empty Clauses

Any or all clauses can be empty:

```c
// Empty initialization
i = 0;
for (; i < n; i++) {
    printf("%d\n", i);
}

// Empty increment (updated in body)
for (i = 0; i < n; ) {
    printf("%d\n", i);
    i += step;
}

// Empty condition (infinite loop)
for (;;) {
    if (done)
        break;
}

// All empty (infinite loop)
for (;;)
    ;   // null statement
```

### Common Idioms

Array traversal:

```c
for (size_t i = 0; i < array_length; i++) {
    process(array[i]);
}
```

Reverse iteration:

```c
for (size_t i = n; i-- > 0; ) {
    process(array[i]);
}
```

Power-of-two iteration:

```c
for (unsigned int i = 1; i != 0; i <<= 1) {
    printf("0x%08x\n", i);
}
```

Linked list traversal:

```c
for (node = head; node != NULL; node = node->next) {
    process(node->data);
}
```

## break and continue

The `break` and `continue` statements alter normal loop flow.

### break Statement

Exits the innermost enclosing loop or switch immediately:

```c
// Search for target
for (i = 0; i < n; i++) {
    if (array[i] == target) {
        found = 1;
        break;      // exit loop immediately
    }
}
```

In nested loops, `break` only exits the innermost loop:

```c
for (i = 0; i < rows; i++) {
    for (j = 0; j < cols; j++) {
        if (matrix[i][j] == target) {
            break;      // exits inner loop only
        }
    }
    // execution continues here after break
}
```

### continue Statement

Skips the remainder of the current iteration and proceeds to the next:

```c
// Process only positive values
for (i = 0; i < n; i++) {
    if (array[i] <= 0)
        continue;       // skip to next iteration

    process(array[i]);  // only reached for positive values
}
```

In `while` and `do-while`, `continue` jumps to the condition test. In `for`, it jumps to the increment:

```c
// while loop
i = 0;
while (i < n) {
    i++;
    if (skip_condition)
        continue;   // jumps to while (i < n)
    process(i);
}

// for loop
for (i = 0; i < n; i++) {
    if (skip_condition)
        continue;   // jumps to i++, then to i < n
    process(i);
}
```

### Behavior in Nested Loops

Only affects the innermost loop:

```c
for (i = 0; i < rows; i++) {
    for (j = 0; j < cols; j++) {
        if (skip_condition)
            continue;       // skips to j++
        process(matrix[i][j]);
    }
}
```

### No Labeled Loops

C does not support labeled break/continue like Java. Use `goto` to break out of nested loops:

```c
// Breaking nested loops with goto
for (i = 0; i < rows; i++) {
    for (j = 0; j < cols; j++) {
        if (matrix[i][j] == target) {
            goto found;
        }
    }
}
printf("Not found\n");
goto end;

found:
    printf("Found at [%d][%d]\n", i, j);

end:
    // continue program
```

## goto Statement

The `goto` statement transfers control to a labeled statement. While controversial, it has legitimate uses in C.

### Syntax

```c
label:
    statement

goto label;
```

Labels have function scope and don't conflict with variable names:

```c
int error = 0;      // variable
error:              // label (different namespace)
    cleanup();
```

### Error Cleanup Pattern

The most accepted use of `goto` is for cleanup in error paths:

```c
int process_file(const char *filename) {
    FILE *file = NULL;
    char *buffer = NULL;
    int result = -1;

    file = fopen(filename, "r");
    if (file == NULL)
        goto error;

    buffer = malloc(BUFFER_SIZE);
    if (buffer == NULL)
        goto error;

    if (read_data(file, buffer) < 0)
        goto error;

    result = process_data(buffer);

error:
    free(buffer);
    if (file != NULL)
        fclose(file);
    return result;
}
```

This pattern avoids deeply nested conditionals and ensures cleanup code appears once.

### Breaking Out of Nested Loops

As shown earlier, `goto` is the simplest way to break multiple loop levels:

```c
for (i = 0; i < MAX_I; i++) {
    for (j = 0; j < MAX_J; j++) {
        for (k = 0; k < MAX_K; k++) {
            if (found_condition(i, j, k))
                goto found;
        }
    }
}
printf("Not found\n");
return 0;

found:
    printf("Found at [%d][%d][%d]\n", i, j, k);
```

Alternative without goto requires flag variables and multiple break checks:

```c
int found = 0;
for (i = 0; i < MAX_I && !found; i++) {
    for (j = 0; j < MAX_J && !found; j++) {
        for (k = 0; k < MAX_K && !found; k++) {
            if (found_condition(i, j, k))
                found = 1;
        }
    }
}
```

### Structured Use Patterns

Acceptable goto patterns:
- Forward jumps only (never backward)
- Jumps to end of function for cleanup
- Breaking nested loops
- Error handling in resource acquisition

Unacceptable patterns:
- Jumping into loop bodies or blocks
- Creating spaghetti code with multiple goto targets
- Using goto for normal control flow that if/while/for handle

### Criticism and Defense

Dijkstra's "Go To Statement Considered Harmful" (1968) criticized goto for creating unreadable code. However, Linux kernel coding style and many C projects accept goto for error handling.

The key is disciplined use: forward jumps to cleanup code improve readability compared to deeply nested error checking.

## Null Statement

The null statement consists of just a semicolon. It performs no action but satisfies C's syntax requirement for a statement.

### Empty Body Pitfalls

Accidental null statements are a common source of bugs:

```c
// Bug - null statement ends while loop immediately
int i = 0;
while (i < 10);     // semicolon creates null statement
{
    printf("%d\n", i);
    i++;
}

// Bug - for loop body is null statement
for (i = 0; i < n; i++);
    process(array[i]);  // executes once with i == n

// Correct - no semicolon
for (i = 0; i < n; i++)
    process(array[i]);
```

Some compilers warn about likely mistakes:

```c
if (condition);     // warning: empty body in if statement
    action();       // always executes!
```

### Intentional Null Statements

Null statements are legitimate when loop work happens in the controlling expression:

```c
// Copy string
while (*dst++ = *src++)
    ;   // null statement - work done in condition

// Skip whitespace
while (isspace(*p++))
    ;   // intentional empty body

// Find end of array
for (i = 0; array[i] != 0; i++)
    ;   // i now points past last element
```

For clarity, place the semicolon on its own line or add a comment:

```c
// Clear
while (*dst++ = *src++)
    /* null body */;

// Also clear
for (i = 0; array[i] != 0; i++)
    ;   // intentionally empty
```

## Common Patterns

### Sentinel Loops

Use a special value to mark the end of data:

```c
// Sentinel-controlled input
int sum = 0, value;
printf("Enter values (0 to end): ");
while (scanf("%d", &value) == 1 && value != 0) {
    sum += value;
}

// Null-terminated string processing
while (*str != '\0') {
    process(*str++);
}
```

### Counting Loops

Execute a fixed number of times:

```c
// Count up
for (int i = 0; i < count; i++) {
    process(i);
}

// Count down
for (int i = count - 1; i >= 0; i--) {
    process(i);
}

// Count by steps
for (int i = 0; i < max; i += step) {
    process(i);
}
```

### Flag-Controlled Loops

A boolean flag controls loop termination:

```c
int done = 0;
while (!done) {
    int cmd = get_command();
    switch (cmd) {
        case CMD_QUIT:
            done = 1;
            break;
        case CMD_PROCESS:
            process_data();
            break;
        default:
            printf("Unknown command\n");
    }
}
```

### Nested Loop Patterns

Processing two-dimensional data:

```c
// Matrix processing
for (int i = 0; i < rows; i++) {
    for (int j = 0; j < cols; j++) {
        matrix[i][j] = compute(i, j);
    }
}

// Upper triangle
for (int i = 0; i < n; i++) {
    for (int j = i; j < n; j++) {
        process(i, j);
    }
}

// All pairs
for (int i = 0; i < n; i++) {
    for (int j = i + 1; j < n; j++) {
        compare(array[i], array[j]);
    }
}
```

Search and exit early:

```c
int found = 0;
for (int i = 0; i < rows && !found; i++) {
    for (int j = 0; j < cols; j++) {
        if (matrix[i][j] == target) {
            found = 1;
            result_i = i;
            result_j = j;
            break;
        }
    }
}
```

Or using goto:

```c
for (int i = 0; i < rows; i++) {
    for (int j = 0; j < cols; j++) {
        if (matrix[i][j] == target) {
            result_i = i;
            result_j = j;
            goto found;
        }
    }
}
printf("Target not found\n");
goto end;

found:
    printf("Found at [%d][%d]\n", result_i, result_j);
end:
    // continue
```

Mastering these control flow constructs is essential for effective C programming. The key is choosing the right construct for each situation: `if` for decisions, `switch` for multi-way branches on integers, `while` for general loops, `do-while` for input validation, `for` for counting, and disciplined use of `break`, `continue`, and `goto` for special cases.
