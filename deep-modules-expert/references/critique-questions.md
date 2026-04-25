# Code Critique Questions for Module Depth

Use these questions when auditing a codebase, reviewing a PR, or analyzing a class/module.

## Table of Contents
1. [Quick Depth Scan (5 min)](#quick-scan)
2. [Interface Audit](#interface-audit)
3. [Information Hiding Audit](#information-hiding)
4. [Decomposition Audit](#decomposition)
5. [Documentation Audit](#documentation-audit)
6. [Scoring Heuristic](#scoring)
7. [Verdict Templates](#verdict-templates)

---

## 1. Quick Depth Scan (5 min)

Start here for any class or module:

1. Count public methods. Is the number surprising given what the module does?
2. For each public method: can you understand it without reading another method's code?
3. Is there a method whose entire body delegates to one other method with no transformation?
4. Does calling this module require constructing two or more objects to do one thing?
5. Does the module's name describe when it's used (temporal: `OrderReader`) rather than what it owns (`OrderStore`)?

If any answer raises a flag, continue to the detailed audits below.

---

## 2. Interface Audit

### Pass-Through Detection
- Does this method just call another method with the same or similar signature?
- If you inlined the body at every call site, would any information be lost?
- Does this class exist solely to rename another class's methods?

### Parameter Complexity
- Could any parameter be replaced by a sensible default?
- Does any parameter expose an implementation choice (e.g., `cache_backend`, `retry_policy`, `redis_ttl`)?
- Could multiple parameters be consolidated into a context/options object — and does that object itself stay shallow?

### Exception Surface
- How many distinct exception types can this interface throw?
- Can the caller meaningfully handle each one differently, or are most treated the same?
- Should rare/catastrophic exceptions be wrapped into one type?
- Does the module handle and retry transient errors internally rather than surfacing them?

### Callback / Event Surface
- Does the interface require callers to register multiple event handlers for a single logical operation?
- Could a synchronous or async-await design replace an event-callback chain?

---

## 3. Information Hiding Audit

### Leakage Detection
- What implementation decisions does the caller need to know to use this module?
- Is there a data format, storage system, protocol, or algorithm name visible in the interface?
- If the storage backend changed (e.g., Redis → Memcached), how many call sites would need updates?

### Cross-Module Leakage
- Is the same design decision (e.g., date format, file encoding, key structure) encoded in more than one module?
- If you change that decision, how many files change?
- Do two modules pass the same raw data structure between each other without either fully owning it?

### State Exposure
- Does the module expose its internal state through getters that clients act on?
- Should those getter + conditional patterns be pushed into the module as a richer method?

Example flag:
```python
# Smell: caller makes decisions based on exposed internal state
if user.subscription_status == "trial" and user.days_remaining < 3:
    notify_expiry(user)
# Deep: user.notify_if_expiring_soon() — module owns the decision
```

---

## 4. Decomposition Audit

### Temporal Decomposition Check
- Is this class named after a stage of processing (Reader, Parser, Validator, Writer, Sender)?
- Do two or more of these stage-classes need to know the same data format or schema?
- Could they be merged into a single class that owns that knowledge end-to-end?

### Classitis Check
- Are there classes with only 1–3 methods that don't abstract a meaningful concept?
- Do you need to import 5+ classes to do a single logical operation?
- Is there a chain of `A → B → C` where each step just wraps and forwards?

### Conjoined Method Check
- Do methods in this class depend on being called in a specific order?
- Does one method set state that only makes sense if another method runs first?
- Is the call sequence documented rather than enforced by the type system?

### Layer Repetition Check
- Do adjacent architectural layers present similar abstractions for the same thing?
- Is there a `UserDTO`, `UserModel`, `UserEntity`, and `UserRecord` that all hold essentially the same fields?
- Could layers be collapsed without losing architectural clarity?

---

## 5. Documentation Audit

### Interface vs. Implementation Boundary
- Does the method's documentation describe *what* it does or *how* it does it?
- Does understanding the interface require knowing internal implementation details?
- Is there a warning in the docs like "make sure to call X before Y" — a sign of conjoined methods?

### Complexity Signal
- Is the docstring longer than the implementation?
- Does the comment apologize for complexity ("this is complex because...")?

---

## 6. Scoring Heuristic

Score each module 1–5 on each dimension. Shallow = low scores.

| Dimension | 1 (Shallow) | 3 (Moderate) | 5 (Deep) |
|-----------|-------------|--------------|----------|
| **Interface size** | Many methods, many params | Medium surface | Few methods, few params |
| **Information hiding** | Exposes impl details | Some leakage | Completely hides decisions |
| **Decomposition** | Temporal/stage-based | Mixed | Responsibility-based |
| **Self-sufficiency** | Requires companion classes | Mostly self-contained | Fully self-contained |
| **Default coverage** | Requires config for common cases | Some defaults | Works well with no config |

**Average < 2.5**: Shallow, likely needs refactoring.
**Average 2.5–3.5**: Moderate depth, targeted improvements possible.
**Average > 3.5**: Deep, interface is likely a strength.

---

## 7. Verdict Templates

Use these to frame feedback:

**Pass-through**: "This method adds no transformation — it's a pass-through to `X.method()`. Consider whether the intermediate layer justifies its interface cost."

**Information leakage**: "The parameter `redis_ttl` exposes a storage implementation detail. If we switch backends, call sites break. Encode the TTL policy inside the module."

**Temporal decomposition**: "The three classes `FileReader`, `FileTransformer`, `FileWriter` all encode the file format. This is temporal decomposition — format knowledge has leaked across three files. Merge into `FileProcessor` that owns the format."

**Classitis**: "This class has one method. Unless it wraps genuine complexity, it's adding interface cost without depth. Inline it or merge with its natural owner."

**Conjoined methods**: "`processBody()` requires `processHeader()` to have run first. This call-order dependency is hidden state. Either merge them or enforce the sequence via a builder/state machine."

**Too many exceptions**: "This method throws 5 exception types. The caller treats 4 of them identically. Wrap them into `ProcessingException` and handle retries internally."
