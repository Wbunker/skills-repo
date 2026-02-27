# Language-Specific Adaptations

How the 10 NASA principles manifest in each language ecosystem. Read the section for the language under review.

## Table of Contents

- [Python](#python)
- [JavaScript / TypeScript](#javascript--typescript)
- [Go](#go)
- [Java / Kotlin](#java--kotlin)
- [C / C++](#c--c)
- [Rust](#rust)

---

## Python

**Rule 1 — Control Flow**: Flag recursion without `sys.setrecursionlimit` awareness. Python has no TCO. Prefer iteration with `for`/`while`.

**Rule 2 — Bounded Loops**: Watch for `while True:` in non-daemon code. Generators consuming infinite iterables without `islice` or `takewhile`. Retry loops without `max_retries`.

**Rule 3 — Resources**: Watch for growing dicts used as caches without `maxsize` (use `functools.lru_cache` or `cachetools`). Check `with` statement usage for file/connection cleanup. Flag missing `finally` blocks.

**Rule 4 — Function Size**: Python convention is even shorter — PEP 8 community norm is ~20-30 lines. Flag functions >50 lines.

**Rule 5 — Assertions**: Use `assert` only for invariants in non-public code (assertions can be disabled with `-O`). Use `raise ValueError/TypeError` for public API validation. Check for bare `if not x: return` without explaining what failed.

**Rule 6 — Scope**: Flag module-level mutable variables. Watch for mutable default arguments (`def f(x=[])`). Check for `global` and `nonlocal` usage.

**Rule 7 — Error Handling**: Flag bare `except:` or `except Exception: pass`. Check that `subprocess.run` results are inspected. Watch for silent `None` returns that callers don't check.

**Rule 8 — Metaprogramming**: Flag `eval()`, `exec()`, `__import__()`. Deep decorator stacks (>2). Metaclasses and `__getattr__` magic. Heavy use of `setattr`/`getattr` for dynamic dispatch.

**Rule 9 — Indirection**: Flag deeply chained attribute access. Excessive `**kwargs` forwarding that obscures what parameters are accepted. Dynamic method resolution.

**Rule 10 — Warnings**: Check for `# type: ignore`, `# noqa`, `# pragma: no cover` on non-test code. Verify `mypy --strict` or equivalent is configured. Check `ruff` / `flake8` config for disabled rules.

**Recommended tooling**: `ruff` (linting + formatting), `mypy --strict` (types), `bandit` (security), `pytest` (assertions via tests).

---

## JavaScript / TypeScript

**Rule 1 — Control Flow**: Flag recursion in async code (stack overflow risk). Watch for `throw` used as control flow rather than error signaling.

**Rule 2 — Bounded Loops**: Flag `while(true)` in non-worker/non-server code. Watch for `setInterval` without cleanup. Recursive `setTimeout` patterns without termination.

**Rule 3 — Resources**: Flag event listeners without removal. Growing `Map`/`Set` without cleanup. Missing `AbortController` on fetch calls. Leaked timers, streams, WebSocket connections.

**Rule 4 — Function Size**: React components count as functions. Flag components >100 lines. Arrow functions in JSX that should be extracted.

**Rule 5 — Assertions**: TS: leverage type system for compile-time assertions. Runtime: check for `zod`/`joi` validation at boundaries. Flag `as` type casts that bypass safety.

**Rule 6 — Scope**: Flag `var` (use `const`/`let`). Module-level mutable state. Check for `window`/`globalThis` property pollution. Closures capturing too much.

**Rule 7 — Error Handling**: Flag missing `.catch()` on Promises. `async` functions without `try/catch`. Empty `catch` blocks. Missing error boundaries in React.

**Rule 8 — Metaprogramming**: Flag `eval()`, `new Function()`, `with` statement. Excessive `Proxy` usage. Deeply nested HOCs in React. Template literal tag abuse.

**Rule 9 — Indirection**: Flag callback nesting >3 levels (use async/await). Long `.then()` chains. Excessive Redux action indirection. Deep prop drilling.

**Rule 10 — Warnings**: Flag `// @ts-ignore`, `// @ts-expect-error` without explanation, `eslint-disable` comments. Check `tsconfig.json` for `strict: true`. Check for `any` types.

**Recommended tooling**: `typescript --strict` (types), `eslint` (linting), `biome` (formatting + linting), `vitest`/`jest` (testing).

---

## Go

**Rule 1 — Control Flow**: Go has no goto in practice. Recursion is uncommon but watch for it in tree walks. Flag `goto` (legal but rarely appropriate).

**Rule 2 — Bounded Loops**: Watch for `for {}` (infinite loop) outside of servers/workers. Flag `range` over channels without close guarantee. Retry loops without backoff limits.

**Rule 3 — Resources**: Flag leaked goroutines (goroutine started without shutdown path). Missing `defer` for cleanup. Channels without close semantics. Context not propagated for cancellation.

**Rule 4 — Function Size**: Go convention allows slightly longer functions due to explicit error handling. Flag >80 lines. Watch for functions that are long solely due to error handling — may need restructuring.

**Rule 5 — Assertions**: Go lacks `assert`. Validate via explicit checks: `if x == nil { return fmt.Errorf(...) }`. Flag functions that accept interfaces without nil checks.

**Rule 6 — Scope**: Flag package-level `var` (prefer const or function-local). Watch for unexported globals. Check `init()` functions for hidden state.

**Rule 7 — Error Handling**: This is Go's strength — but flag `_ = err` discarding errors. Functions that return `error` but callers only check the value. `log.Fatal` in library code.

**Rule 8 — Metaprogramming**: Flag `reflect` usage outside of serialization/testing. `go:generate` producing opaque code. Build tags creating many code paths.

**Rule 9 — Indirection**: Flag excessive interface embedding. Deep struct nesting. Function types passed through many layers.

**Rule 10 — Warnings**: Check `golangci-lint` config for disabled linters. Flag `//nolint` without explanation. Verify `go vet`, `staticcheck`, `gosec` are in CI.

**Recommended tooling**: `golangci-lint` (linting), `go vet` (static analysis), `staticcheck` (advanced analysis), `gosec` (security).

---

## Java / Kotlin

**Rule 1 — Control Flow**: Flag recursion without tail-call annotation (Kotlin `tailrec`). Watch for complex `try/catch/finally` flows that obscure the main path.

**Rule 2 — Bounded Loops**: Watch for `while(true)` in non-daemon threads. Flag `Iterator` patterns without hasNext guard. Stream operations on potentially infinite sources.

**Rule 3 — Resources**: Flag missing `try-with-resources` / `use` for `AutoCloseable`. Thread pools without shutdown. Growing static collections. Connection leaks.

**Rule 4 — Function Size**: Flag >60 lines. Kotlin's expression syntax should yield shorter functions — flag >40 lines in Kotlin.

**Rule 5 — Assertions**: Use `Objects.requireNonNull()` for parameters. Guava `Preconditions.checkArgument/checkState`. Kotlin: leverage non-null types, `require()`, `check()`.

**Rule 6 — Scope**: Flag `public` fields that should be `private`. Static mutable state. Large class-level scope when method-local suffices. Kotlin: flag `var` when `val` works.

**Rule 7 — Error Handling**: Flag empty `catch` blocks. Pokemon exception handling (`catch(Exception e)`). Swallowed exceptions. Missing `@Throws` in Kotlin.

**Rule 8 — Metaprogramming**: Flag heavy reflection (`Class.forName`, `Method.invoke`). Annotation processors that generate opaque code. Bytecode manipulation.

**Rule 9 — Indirection**: Flag deep inheritance (>3 levels). Excessive design patterns (Proxy → Decorator → Adapter chains). Stringly-typed Spring config.

**Rule 10 — Warnings**: Flag `@SuppressWarnings`. Check for `-Xlint:all` in compiler config. Verify SpotBugs/PMD/Checkstyle in CI.

**Recommended tooling**: `SpotBugs` (bugs), `PMD` (code quality), `Checkstyle` (style), `ErrorProne` (compiler plugin).

---

## C / C++

These rules apply most directly since the original Power of Ten was written for C.

**Rule 1 — Control Flow**: Zero tolerance for `goto`, `setjmp`/`longjmp`. No direct or indirect recursion. Flag immediately.

**Rule 2 — Bounded Loops**: Every `while` and `for` loop needs a provable upper bound. Add explicit `max_iterations` guards.

**Rule 3 — Resources**: No `malloc`/`calloc`/`realloc` after initialization. Pre-allocate at startup. Use stack memory (bounded by Rule 1). C++: no `new` in hot paths.

**Rule 4 — Function Size**: Hard limit 60 lines. No exceptions.

**Rule 5 — Assertions**: Minimum 2 per function. Use custom `c_assert` macro that returns error (not `abort`). Verify pre/post conditions and loop invariants.

**Rule 6 — Scope**: No file-scope variables where block scope works. Mark everything possible as `static`. C++: no mutable globals.

**Rule 7 — Error Handling**: Check every return value. If intentionally ignoring, cast to `(void)`. Check `fclose`, `printf`, `fwrite` — all of them.

**Rule 8 — Metaprogramming**: Preprocessor limited to `#include` and simple `#define`. No token pasting, variable argument macros, or recursive macros. C++: limit template metaprogramming.

**Rule 9 — Indirection**: Maximum one level of pointer dereference. No `**ptr`. No function pointers. C++: minimize virtual dispatch.

**Rule 10 — Warnings**: `-Wall -Wextra -Werror` minimum. Zero warnings from compiler AND static analyzer. Rewrite code rather than suppress.

**Recommended tooling**: GCC/Clang `-Wall -Wextra -Werror`, `cppcheck`, `clang-tidy`, `Coverity`, `MISRA` checker.

---

## Rust

Rust's type system and ownership model already enforce several of these rules at compile time.

**Rule 1 — Control Flow**: Recursion is allowed but has no TCO guarantee. Flag unbounded recursion. `unsafe` goto is not possible.

**Rule 2 — Bounded Loops**: Watch for `loop {}` without break conditions. Iterators are generally bounded but check `.cycle()` and custom iterators.

**Rule 3 — Resources**: RAII handles most cleanup. Watch for `mem::forget`, `ManuallyDrop`, leaked `JoinHandle`s. Flag `Box::leak`.

**Rule 4 — Function Size**: Same 60-line guideline. Rust's match arms can get long — consider extracting.

**Rule 5 — Assertions**: Use `assert!` for invariants, `debug_assert!` for expensive checks. `.expect("context")` over `.unwrap()`. Custom error types with `thiserror`.

**Rule 6 — Scope**: Rust encourages this via ownership. Flag excessive `pub` visibility. Watch for `static mut` (requires unsafe). `lazy_static` / `once_cell` mutable globals.

**Rule 7 — Error Handling**: Flag `.unwrap()` outside of tests. `.expect()` should have descriptive messages. Check `?` propagation reaches appropriate handler. Flag `let _ = result;`.

**Rule 8 — Metaprogramming**: Procedural macros can obscure code. Flag `macro_rules!` that are complex. Check that derive macros are standard.

**Rule 9 — Indirection**: Flag excessive `Box<dyn Trait>` when generics suffice. Deep `Arc<Mutex<Box<dyn ...>>>` chains. Trait object chains.

**Rule 10 — Warnings**: `#![deny(warnings)]` in lib.rs. Flag `#[allow(unused)]` and similar. Check clippy configuration — should run `clippy -- -W clippy::pedantic`.

**Recommended tooling**: `cargo clippy` (linting), `cargo deny` (dependency audit), `miri` (UB detection), `cargo-audit` (security).
