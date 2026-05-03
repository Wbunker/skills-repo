---
name: deep-modules-expert
description: >
  Expert in John Ousterhout's "deep modules vs shallow modules" concept from "A Philosophy of Software Design."
  Analyzes existing code to identify shallow modules, pass-through methods, information leakage, temporal
  decomposition, classitis, and conjoined methods. Provides depth scores, concrete critique, and refactoring
  recommendations to increase module depth. Use when: reviewing code for design quality, critiquing module/class
  decomposition, asking "is this class too shallow?", identifying information leakage, or implementing
  Ousterhout's design principles. Triggers on: "deep modules", "shallow class", "information hiding critique",
  "APoSD", "Philosophy of Software Design", "classitis", "pass-through methods", "module depth".
---

# Deep Modules Expert

Apply John Ousterhout's module depth framework from *A Philosophy of Software Design* to critique code and guide refactoring.

## Core Principle

**Module Depth = Benefit / Cost**

- **Benefit**: Total functionality the module provides
- **Cost**: Interface complexity (method count, parameter count, exception types, call-sequence requirements, mental load)

A module is **deep** when benefit >> cost. Goal: maximize what callers get per unit of interface they must understand.

Key insight: "It's more important for a module to have a simple interface than a simple implementation."

The world's deepest interface: garbage collection. The interface *shrinks* (no `free()` call) while implementation grows massively complex.

---

## Workflow

### 1. Identify the Unit to Analyze
Establish scope: a single class, a module, a layer, or an entire subsystem.

### 2. Measure Interface Cost
- Count public methods
- Count average parameters per method
- Count distinct exception types declared/thrown
- Note any required call sequences (conjoined methods)
- Note any required companion objects (stacking, setup, teardown)

### 3. Assess Information Hiding
Ask: "What does a caller need to know about the implementation to use this module?"
- Every implementation detail visible in the interface is a depth violation
- Check for: backend names, format names, algorithm parameters, internal state as getters

### 4. Check Decomposition Pattern
Determine *why* the module was split this way:
- **Temporal decomposition** (split by execution order) = almost always shallow
- **Responsibility decomposition** (split by what knowledge is owned) = can be deep

### 5. Apply Depth Score and Identify Specific Anti-Patterns

Score 1–5 on each:
- Interface size (5 = few methods/params)
- Information hiding (5 = zero implementation details visible)
- Decomposition (5 = responsibility-based, no knowledge duplication)
- Self-sufficiency (5 = works standalone, no companion objects required)
- Default coverage (5 = common case requires no configuration)

Average < 2.5 = shallow, warrants refactoring.

### 6. Prescribe Transformations
Map each anti-pattern to a specific refactoring from the playbook.

---

## Anti-Pattern Quick Reference

| Anti-Pattern | Signature | Fix |
|---|---|---|
| **Pass-through method** | Body = single delegation, identical signature | Delete layer or add real value |
| **Classitis** | 1–3 method class, no meaningful abstraction | Merge into natural owner |
| **Temporal decomposition** | Classes named by stage (Reader, Parser, Writer) + shared format knowledge | Merge; one class owns the format |
| **Information leakage** | Interface param names a backend, format, or algorithm | Push the decision inside; make it config |
| **Conjoined methods** | Must call A before B; docs say "call in order" | Merge into one method or enforce via types |
| **Exception overload** | 4+ exception types, caller treats most identically | Wrap into one type; handle transients internally |
| **State exposure** | Caller reads getter, makes decision, calls back | Move the decision inside as a richer method |
| **Companion stacking** | Caller must compose N objects to do one thing | Provide a factory/default with sensible setup |

---

## Reference Files

- **[references/patterns-and-examples.md](references/patterns-and-examples.md)** — Load for canonical deep/shallow examples (Unix I/O, GC, Java I/O stacking, HTTP clients, auth flows). Use when illustrating what good and bad look like.

- **[references/critique-questions.md](references/critique-questions.md)** — Load when auditing code. Contains full question sets for interface audit, information hiding, decomposition, documentation, and the 5-dimension scoring table with verdict templates.

- **[references/refactoring-playbook.md](references/refactoring-playbook.md)** — Load when prescribing fixes. Contains concrete before/after transformations for every major anti-pattern: absorbing pass-throughs, merging temporal decomposition, pushing decisions inward, simplifying exceptions, introducing defaults, replacing state exposure, eliminating conjoined methods, and using context objects.

---

## Common Request Patterns

**"Review this class for module depth"**
→ Load critique-questions.md, apply the 5-dimension score, identify anti-patterns by name, cite specific methods.

**"Is this too many classes?"**
→ Classitis check: do they share knowledge? Could merging create a deeper module without making a god class?

**"How do I make this module deeper?"**
→ Identify the specific anti-pattern, load refactoring-playbook.md, show before/after.

**"Does this violate information hiding?"**
→ Check if any parameter or return type names an implementation choice; check for cross-module knowledge duplication.

**"Explain deep vs shallow modules"**
→ Load patterns-and-examples.md; use Unix I/O and GC as the canonical contrast.
