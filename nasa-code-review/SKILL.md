---
name: nasa-code-review
description: >
  Review code using principles from NASA JPL's "Power of Ten" safety-critical coding rules
  (Gerard Holzmann, 2006). Adapted for any language. Triggers on requests like: "review this
  code with NASA rules", "safety-critical review", "power of ten review", "/nasa-code-review",
  "review this like NASA would", or when a user asks for rigorous/defensive code review.
  Produces a structured report scoring code against 10 adapted principles covering control flow,
  loop bounds, resource management, function size, assertions, scope, error handling,
  metaprogramming, indirection, and tooling discipline.
---

# NASA Code Review — Power of Ten

Review code against 10 principles adapted from NASA JPL's safety-critical coding rules. Works with any language.

## The 10 Principles

| # | Principle | What to look for |
|---|-----------|-----------------|
| 1 | **Simple Control Flow** | No goto, no unstructured jumps, recursion only when bounded and justified |
| 2 | **Bounded Loops** | Every loop has a clear, provable termination condition |
| 3 | **Controlled Resource Allocation** | No unbounded growth; prefer pre-allocated or pooled resources after init |
| 4 | **Short Functions** | Each function fits on one screen (~60 lines), single responsibility |
| 5 | **Defensive Assertions** | Preconditions and postconditions validated; min 2 checks per non-trivial function |
| 6 | **Minimal Scope** | Variables declared at narrowest scope; minimal global/shared mutable state |
| 7 | **Check Every Result** | All return values, errors, and failure modes handled explicitly |
| 8 | **Limited Metaprogramming** | Macros, decorators, codegen, and magic kept minimal and transparent |
| 9 | **Minimize Indirection** | Shallow reference chains; avoid deep callback nesting, excessive pointer chasing |
| 10 | **Zero Warnings** | Strictest linter/compiler settings; every warning resolved, not suppressed |

For detailed rule explanations with rationale and language-specific examples, read `references/rules-deep-dive.md`.

## Review Workflow

### Step 1: Identify scope and language

Determine the language, framework, and criticality level of the code. Ask the user if unclear.

Select a review mode:

| Mode | When | Behavior |
|------|------|----------|
| **Strict** | Safety-critical, financial, infrastructure | Flag every violation; no exceptions |
| **Standard** | Production services, libraries | Flag violations; note acceptable trade-offs |
| **Advisory** | Prototypes, scripts, learning code | Highlight top 3-5 most impactful findings |

Default to **Standard** unless the user specifies otherwise.

### Step 2: Read the code

Read all files under review. For large codebases, ask the user to scope the review to specific files or modules.

### Step 3: Analyze against each principle

For each of the 10 principles, scan the code and record:
- **Violations**: concrete instances with file:line references
- **Risks**: patterns that aren't violations but could become problems
- **Strengths**: things the code does well

For language-specific adaptation guidance, read `references/language-adaptations.md`.

### Step 4: Generate the review report

Use this format:

```markdown
# NASA Power of Ten — Code Review

**Scope**: [files reviewed]
**Language**: [language]
**Mode**: [Strict / Standard / Advisory]

## Summary

| Principle | Score | Findings |
|-----------|-------|----------|
| 1. Simple Control Flow | PASS / WARN / FAIL | [one-line summary] |
| 2. Bounded Loops | ... | ... |
| ... | ... | ... |

**Overall**: [X/10 passing] — [one sentence assessment]

## Detailed Findings

### Principle N: [Name] — [PASS/WARN/FAIL]

**Violations:**
- `file.py:42` — [description of violation and why it matters]

**Risks:**
- `file.py:88` — [description and potential impact]

**Recommendations:**
- [specific, actionable fix]

[repeat for each principle with findings]

## Top Recommendations

1. [Highest impact fix]
2. [Second highest]
3. [Third highest]
```

### Step 5: Offer to fix

After presenting the report, offer to implement the top recommendations if the user wants.

## Scoring Guide

| Score | Meaning |
|-------|---------|
| **PASS** | No violations found for this principle |
| **WARN** | Minor issues or acceptable trade-offs noted |
| **FAIL** | Clear violations that should be addressed |

## Quick Reference — Common Violations by Language

| Violation | Python | JS/TS | Go | Java | C/C++ | Rust |
|-----------|--------|-------|----|------|-------|------|
| Unbounded recursion | `def f(): f()` | `function f(){f()}` | rare (no TCO) | same | same | same |
| Unchecked result | bare `except:` | missing `.catch()` | `_ = err` | empty catch | unchecked `fclose` | `unwrap()` |
| Unbounded loop | `while True:` | `while(true)` | `for {}` | `while(true)` | `while(1)` | `loop {}` |
| Suppressed warning | `# noqa` | `// @ts-ignore` | `//nolint` | `@SuppressWarnings` | `#pragma` | `#[allow()]` |
| Excessive scope | module-level `var` | `var` hoisting | package globals | `public` fields | file globals | `pub` everything |
