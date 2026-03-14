---
name: scala-expert
description: >
  Scala programming expert. Use when the user asks any Scala question:
  types, pattern matching, functional programming, OOP, traits, collections, concurrency, implicits, macros, or application design.
---

# Scala Expert

Load only the reference file relevant to the user's question. If a question spans topics, read both files.

## Topic Routing

### Getting Started
- **Scala introduction, REPL, sbt, scripts, Scala 3 migration, basic syntax** → [references/01-intro-and-basics.md](references/01-intro-and-basics.md)
- **Type inference, literals, tuples, options, sealed types, organizing code** → [references/02-type-less-do-more.md](references/02-type-less-do-more.md)
- **Operator overloading, enums, string interpolation, conditionals, error handling, try/catch, lazy vals** → [references/03-rounding-out-basics.md](references/03-rounding-out-basics.md)

### Core Language
- **Pattern matching, case classes, guards, extractors, regex, sealed hierarchies** → [references/04-pattern-matching.md](references/04-pattern-matching.md)
- **Type classes, extension methods, given instances, exports, opaque types** → [references/05-type-classes-extensions.md](references/05-type-classes-extensions.md)
- **Using clauses, context parameters, implicit conversions, context bounds, type class derivation** → [references/06-using-clauses.md](references/06-using-clauses.md)

### Functional Programming
- **FP principles, pure functions, higher-order functions, closures, recursion, tail calls, currying, partial functions** → [references/07-functional-programming.md](references/07-functional-programming.md)
- **For comprehensions, generators, guards, yield, flatMap/map/withFilter, monadic composition** → [references/08-for-comprehensions.md](references/08-for-comprehensions.md)
- **Category theory, functors, monads, applicatives, algebraic data types, effects** → [references/09-advanced-fp.md](references/09-advanced-fp.md)

### Object-Oriented Programming
- **Classes, objects, companions, constructors, fields, methods, apply/unapply, case classes/objects** → [references/10-oop.md](references/10-oop.md)
- **Traits, mixins, stackable modifications, diamond problem, self types, trait parameters** → [references/11-traits.md](references/11-traits.md)
- **Covariance, contravariance, invariance, universal equality, multiversal equality, CanEqual** → [references/12-variance-equality.md](references/12-variance-equality.md)
- **Initialization order, early definitions, linearization, method resolution, super calls** → [references/13-initialization-resolution.md](references/13-initialization-resolution.md)

### Type System & Collections
- **Type hierarchy, Any, AnyVal, AnyRef, Nothing, Null, value classes, union/intersection types** → [references/14-type-hierarchy.md](references/14-type-hierarchy.md)
- **Collections: List, Vector, Map, Set, Array, immutable vs mutable, performance, conversions, LazyList** → [references/15-collections.md](references/15-collections.md)
- **Visibility: public, private, protected, package-level, companion access, sealed** → [references/16-visibility.md](references/16-visibility.md)
- **Type system: path-dependent types, type projections, structural types, type lambdas, match types, singleton types** → [references/17-type-system.md](references/17-type-system.md)

### Applications & Tools
- **Concurrency: Futures, Promises, Akka, actors, parallel collections, thread safety** → [references/18-concurrency.md](references/18-concurrency.md)
- **Dynamic invocation, structural types, Dynamic trait, type providers** → [references/19-dynamic-dsl.md](references/19-dynamic-dsl.md)
- **Scala tools, sbt, testing (ScalaTest, MUnit), Java interop, annotations, libraries** → [references/20-tools-libraries.md](references/20-tools-libraries.md)
- **Application design, dependency injection, cake pattern, modularity, anti-patterns, best practices** → [references/21-application-design.md](references/21-application-design.md)
- **Metaprogramming: macros, inline, compiletime, reflection, TASTy, code generation** → [references/22-metaprogramming.md](references/22-metaprogramming.md)
