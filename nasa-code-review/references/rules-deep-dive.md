# NASA Power of Ten — Rules Deep Dive

Adapted from Gerard J. Holzmann, "The Power of 10: Rules for Developing Safety-Critical Code," IEEE Computer, June 2006. Originally written for C at NASA JPL. Principles below are language-agnostic.

## Table of Contents

- [Rule 1: Simple Control Flow](#rule-1-simple-control-flow)
- [Rule 2: Bounded Loops](#rule-2-bounded-loops)
- [Rule 3: Controlled Resource Allocation](#rule-3-controlled-resource-allocation)
- [Rule 4: Short Functions](#rule-4-short-functions)
- [Rule 5: Defensive Assertions](#rule-5-defensive-assertions)
- [Rule 6: Minimal Scope](#rule-6-minimal-scope)
- [Rule 7: Check Every Result](#rule-7-check-every-result)
- [Rule 8: Limited Metaprogramming](#rule-8-limited-metaprogramming)
- [Rule 9: Minimize Indirection](#rule-9-minimize-indirection)
- [Rule 10: Zero Warnings](#rule-10-zero-warnings)

---

## Rule 1: Simple Control Flow

**Original NASA rule**: Restrict all code to very simple control flow constructs — do not use goto statements, setjmp or longjmp constructs, or direct or indirect recursion.

**Rationale**: Simple control flow makes code verifiable. Recursion makes it impossible to prove termination. Goto creates spaghetti paths that tools cannot analyze. If you cannot trace every execution path, you cannot prove correctness.

**What to flag**:
- Direct recursion (function calls itself)
- Indirect/mutual recursion (A calls B calls A)
- Goto or equivalent unstructured jumps
- Deeply nested control flow (>3 levels)
- Complex conditional chains that obscure flow

**Acceptable exceptions**:
- Tail-recursive functions in languages with guaranteed TCO (Scheme, Elixir, some Kotlin)
- Tree/graph traversal with provable depth bounds
- Parser combinators with bounded input

**Review question**: Can every execution path be traced statically from entry to exit?

---

## Rule 2: Bounded Loops

**Original NASA rule**: Give all loops a fixed upper bound. It must be trivially possible for a checking tool to prove statically that a preset upper bound on the number of iterations of a loop cannot be exceeded.

**Rationale**: Unbounded loops risk hanging the system. If you cannot prove a loop terminates within N iterations, you cannot prove the program terminates. Even "obviously terminating" loops like `while (ptr != NULL)` are unbounded if the data structure could be circular.

**What to flag**:
- `while True` / `while(true)` / `for(;;)` / `loop {}` outside of event loops or schedulers
- Loops whose termination depends on external input without a max iteration guard
- Iterator consumption without size limits (e.g., reading an entire unbounded stream)
- Missing timeout on polling/retry loops

**Pattern — bounded loop guard**:
```
max_iterations = 1000
count = 0
while condition and count < max_iterations:
    # work
    count += 1
if count >= max_iterations:
    handle_safety_limit_exceeded()
```

**Review question**: For every loop, can you name the maximum number of iterations?

---

## Rule 3: Controlled Resource Allocation

**Original NASA rule**: Do not use dynamic memory allocation after initialization.

**Rationale**: Dynamic allocation can fail unpredictably. Memory leaks accumulate. Garbage collectors introduce latency spikes. Pre-allocating everything at startup makes resource usage deterministic and bounded.

**Language-agnostic adaptation**: The spirit is about *predictable resource usage*. Avoid patterns that cause unbounded growth at runtime.

**What to flag**:
- Unbounded caches or maps that grow without eviction
- Creating objects/connections in hot loops without pooling
- Appending to lists/arrays without size limits in long-running processes
- Missing cleanup (file handles, connections, goroutines, threads)
- Lazy initialization in concurrent code without synchronization

**Acceptable in most contexts**:
- Standard collection use with bounded inputs
- GC'd languages doing normal object allocation
- Connection pools, buffer pools, object pools (these follow the spirit)

**Review question**: Can any data structure grow without bound during runtime?

---

## Rule 4: Short Functions

**Original NASA rule**: No function should be longer than what can be printed on a single sheet of paper — roughly 60 lines of code.

**Rationale**: If you cannot understand a function at a glance, you cannot verify it works. Short functions are easier to test, name, document, and reason about. Long functions almost always contain multiple responsibilities.

**What to flag**:
- Functions exceeding 60 lines (strict) or 100 lines (standard)
- Functions with more than 5 parameters
- Functions with more than 3 levels of nesting
- Functions that mix multiple concerns (I/O + logic + error handling + formatting)

**Review question**: Can a new team member understand this function in under 2 minutes?

---

## Rule 5: Defensive Assertions

**Original NASA rule**: The assertion density of the code should average to a minimum of two assertions per function.

**Rationale**: Industrial data shows one defect per 10–100 lines of code. Assertions catch defects early. They verify pre-conditions (inputs valid), post-conditions (outputs correct), and invariants (state consistent). Because assertions are side-effect free, they can be disabled in production if needed.

**What to flag**:
- Functions with no input validation at all
- Public API functions without parameter checks
- Missing null/undefined/None checks before dereferencing
- State-changing functions that don't verify invariants
- "Trust the caller" patterns at system boundaries

**Language patterns**:
- Python: `assert`, raising `ValueError`/`TypeError` for public APIs
- JS/TS: type guards, runtime checks, `assert` libraries
- Go: explicit error checks, panic for invariant violations
- Java: `Objects.requireNonNull`, `assert`, Guava `Preconditions`
- Rust: `assert!`, `debug_assert!`, `.expect()` with context
- C/C++: `assert()`, custom `c_assert` macros with recovery

**Review question**: If this function received garbage input, would it fail loudly or corrupt state silently?

---

## Rule 6: Minimal Scope

**Original NASA rule**: Declare all data objects at the smallest possible level of scope.

**Rationale**: If a variable is not in scope, it cannot be corrupted. Minimizing scope reduces the number of places where state can be accidentally modified, making the code easier to analyze and debug.

**What to flag**:
- Global mutable state (module-level variables, singletons with mutable state)
- Variables declared far from their use
- Broad `public` / exported access when `private` / unexported suffices
- Class fields that could be local variables
- Long-lived variables reused for different purposes

**Review question**: For each variable, could its scope be narrower without changing behavior?

---

## Rule 7: Check Every Result

**Original NASA rule**: Each calling function must check the return value of nonvoid functions, and each called function must check the validity of all parameters provided by the caller.

**Rationale**: Unchecked return values are the #1 source of silent failures. NASA's rule is explicit: if you intentionally ignore a return value, cast it to `(void)` so it is clear the omission is deliberate, not accidental.

**What to flag**:
- Bare `except: pass` / empty `catch {}` blocks
- Ignored return values from functions that can fail
- Missing `.catch()` on Promises
- Discarded errors: `_ = err` in Go, `_ = result` in Rust
- `unwrap()` or `!` force-unwrap without justification
- Missing error handling on I/O, network, parse, or serialization operations

**Review question**: If every external call failed right now, would this code handle it or crash silently?

---

## Rule 8: Limited Metaprogramming

**Original NASA rule**: The use of the preprocessor must be limited to the inclusion of header files and simple macro definitions.

**Rationale**: The C preprocessor can make code completely unreadable. With 10 conditional compilation directives, you have 1,024 different versions of your code — each needs testing. The principle extends to any mechanism that transforms code before execution: templates, macros, code generation, decorators, reflection.

**What to flag**:
- Complex macros or template metaprogramming
- Heavy use of decorators that alter function signatures or control flow
- Runtime code generation (`eval`, `exec`, `Function()`, `compile()`)
- Excessive monkey-patching or runtime class modification
- Deep decorator/annotation stacking (>2 on a single function)
- Conditional compilation that creates many code paths

**Acceptable**:
- Simple macros / constants
- Standard framework decorators (`@property`, `@app.route`, `@Override`)
- Code generation from schemas (protobuf, OpenAPI) — generated code is deterministic

**Review question**: Can you read this code top-to-bottom and understand what executes, without mentally running a macro/decorator/codegen expansion?

---

## Rule 9: Minimize Indirection

**Original NASA rule**: Limit pointer use to a single dereference, and do not use function pointers.

**Rationale**: Multiple levels of indirection make static analysis nearly impossible. If tools cannot analyze the code, you cannot prove it is safe. The principle extends beyond pointers to any form of indirect dispatch.

**What to flag**:
- Deep pointer chains (`**ptr`, `obj.a.b.c.d`)
- Callback hell / deeply nested closures
- Excessive use of dynamic dispatch when static dispatch suffices
- Deep inheritance hierarchies (>3 levels)
- Stringly-typed dispatch (looking up handlers by name at runtime)
- Proxy/wrapper chains that obscure the actual operation

**Review question**: How many hops does it take to find what actually executes when this line runs?

---

## Rule 10: Zero Warnings

**Original NASA rule**: Compile with all possible warnings active; all warnings should then be addressed before release of the software.

**Rationale**: Warnings exist because tool authors identified a pattern that is likely wrong. Developers who assume warnings are false positives are often wrong. If a tool gives a false positive, rewrite the code so the tool understands it — do not suppress the warning.

**What to flag**:
- Warning suppressions: `# noqa`, `// @ts-ignore`, `@SuppressWarnings`, `#[allow()]`, `//nolint`, `#pragma warning(disable)`
- Missing or lenient linter configuration
- Type errors suppressed with `any`, `Object`, `interface{}`
- Disabled compiler/linter rules in config files
- Known warnings that have been left unresolved

**Review question**: Would this code pass the strictest available linter/type-checker with zero warnings?
