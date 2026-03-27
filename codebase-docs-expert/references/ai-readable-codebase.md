# Making a Codebase Understandable to AI Coding Assistants
## Context Window Design, Code-Level Docs, Architecture, and Test Infrastructure

---

## The Fundamental Constraint: Context Window

AI coding assistants have a limited context window — the amount of text they can "see" at once. Every file read, every command output, every conversation turn consumes that window. When the window is full, the AI operates with an incomplete picture and makes mistakes.

**The design principle**: maximize information density within any given context window; minimize noise.

This differs from human documentation, where thoroughness is often rewarded. For AI, the cost of information is real — loading irrelevant content displaces relevant content.

---

## File and Directory Structure

### Use Conventional Layouts

AI tools have trained on millions of repositories and form strong priors about conventional directory layouts. Follow them:

| Project Type | Conventional Layout |
|-------------|-------------------|
| Python package | `src/`, `tests/`, `docs/`, `scripts/` |
| Java/Maven | `src/main/java/`, `src/test/java/`, `docs/` |
| Node.js | `src/`, `test/` or `__tests__/`, `docs/` |
| Go | Package directories at root, `cmd/`, `internal/`, `pkg/` |
| Monorepo | `packages/<name>/` or `apps/<name>/` + `shared/` or `libs/` |

### Predictable, Descriptive Naming

AI tools navigate by reading file and directory names before reading content. Names are a form of documentation.

```
Good:
backend/auth/token_refresh.py     ← purpose clear from path
backend/orders/retry_handler.py   ← clear what it handles

Bad:
backend/auth/tr.py                ← inscrutable abbreviation
backend/utils2.py                 ← no context for what "utils2" means
backend/handler_new.py            ← temporal names lose meaning over time
```

### Avoid Deep Nesting

Deeply nested structures require many file reads to understand the overall shape. Prefer shallow, broad structures with clear naming over deep hierarchies.

```
Avoid:
src/core/services/data/processors/batch/handlers/order_processor.py

Prefer:
src/order_batch_processor.py  (or logical grouping by domain, not technical layer)
```

### Monorepo Mapping in CLAUDE.md

For monorepos, provide an explicit map in CLAUDE.md so the AI doesn't have to explore to understand structure:

```markdown
## Repository structure
- `order-service/` — HTTP API for order management (Python/FastAPI)
- `payment-service/` — Payment processing (Java/Spring Boot)
- `shared/models/` — Shared Pydantic/Pojo models (generated from OpenAPI spec)
- `infra/` — Terraform for all environments
- `scripts/` — Developer tooling; not deployed
```

---

## Code-Level Documentation

Code-level documentation is the most reliable documentation for AI tools: it lives with the code, is read automatically when the AI opens a file, and is updated naturally as part of coding.

### Module / File Level Docstrings

The first thing an AI reads when opening a file. State the module's purpose, its main exports, and how it relates to adjacent modules.

```python
"""
Order retry handler.

Processes failed orders from the dead-letter queue and retries them
with exponential backoff. Publishes metrics to CloudWatch on each attempt.

Main entry point: `RetryHandler.process_batch(events)`

See also:
- orders/processor.py — initial order processing
- orders/models.py — Order and RetryContext data models
"""
```

```java
/**
 * Handles failed order events from the DLQ.
 *
 * <p>Reads from the orders-dlq SQS queue, applies exponential backoff,
 * and re-submits orders to the main orders queue. Failed retries are
 * forwarded to the manual-review SNS topic.
 *
 * @see OrderProcessor for initial order processing
 * @see RetryPolicy for the backoff configuration
 */
public class OrderRetryHandler { ... }
```

### Function / Method Docstrings

Document non-obvious behavior: side effects, edge cases, failure modes, and why the implementation works the way it does.

```python
def process_order_batch(events: list[OrderEvent], max_retries: int = 3) -> BatchResult:
    """
    Process a batch of order events, retrying transient failures.

    Uses exponential backoff with jitter (base: 100ms, max: 30s).
    Transient failures (network errors, throttling) are retried.
    Permanent failures (validation errors, customer not found) are not retried
    and are immediately routed to the manual-review topic.

    Args:
        events: List of order events from SQS. May contain duplicates;
                idempotency is enforced by order ID.
        max_retries: Maximum retry attempts per event. Default 3.

    Returns:
        BatchResult with success_count, failure_count, and failed_event_ids.

    Raises:
        BatchProcessingError: If more than 50% of events fail (circuit breaker).
    """
```

**What NOT to document in docstrings:**
- What the code obviously does: `# Increments counter` above `counter += 1`
- Standard library behavior the reader already knows
- Parameters whose purpose is obvious from their name and type

### Type Annotations

Type annotations are documentation that tools can verify. AI tools use types to understand code structure without reading full implementations.

**Python:**
```python
# Before
def create_order(customer_id, items, discount=None):
    ...

# After — AI understands structure immediately
from typing import Optional
from decimal import Decimal

def create_order(
    customer_id: str,
    items: list[OrderItem],
    discount: Optional[Decimal] = None
) -> Order:
    ...
```

**TypeScript** (already typed):
```typescript
// Prefer explicit return types — AI can use them without reading implementations
function validateOrder(order: OrderRequest): ValidationResult { ... }
```

**Java** (statically typed by default):
```java
// Use generics precisely — avoid raw types
Map<String, List<OrderItem>> groupByCategory(List<OrderItem> items) { ... }
```

### Named Constants

```python
# Bad — AI has no context for what 3 means
if retry_count > 3:
    raise MaxRetriesExceeded()

# Good — named constant is self-documenting
MAX_ORDER_RETRIES = 3  # Per requirements doc: https://...

if retry_count > MAX_ORDER_RETRIES:
    raise MaxRetriesExceeded()
```

### Custom Exception Types

Named exception classes describe failure modes. AI tools see the exception class hierarchy and understand what can go wrong:

```python
class OrderProcessingError(Exception):
    """Base class for order processing failures."""

class TransientOrderError(OrderProcessingError):
    """Temporary failure; safe to retry after backoff."""

class PermanentOrderError(OrderProcessingError):
    """Permanent failure; do not retry. Route to manual review."""

class ValidationError(PermanentOrderError):
    """Order data failed validation."""
```

---

## Architecture Documentation for AI

### ARCHITECTURE.md

An `ARCHITECTURE.md` at the repo root (or `docs/ARCHITECTURE.md`) gives AI tools a map before they dive into any specific file.

**What to include:**
- The 5–10 major components and what each one does
- How data flows between components (a simple diagram helps)
- Technology choices per component
- What external systems are involved and how they're accessed
- What is NOT in scope (to prevent misguided "improvements")

```markdown
# Architecture

## Overview
Order processing system. Events flow: API Gateway → Lambda → DynamoDB,
with async side effects via Kinesis.

## Components

| Component | Technology | Responsibility |
|-----------|-----------|---------------|
| order-api | Python/FastAPI on Lambda | Accepts and validates orders |
| order-processor | Python Lambda | Processes validated orders, updates DynamoDB |
| payment-service | Java/Spring on ECS | Handles payment authorization |
| notification-service | Python Lambda | Sends customer emails/SMS |

## Data Flow
```
Client → API Gateway → order-api Lambda → SQS orders-queue
                                        ↓
                              order-processor Lambda → DynamoDB
                                        ↓
                              Kinesis events-stream → notification-service
```

## External Dependencies
- Stripe: payment processing (credentials in Secrets Manager)
- Twilio: SMS notifications
- SendGrid: email
```

### ADRs as AI Guard Rails

ADRs prevent AI from "improving away" deliberate constraints:

```markdown
# ADR-0003: Mandatory conditional writes for all DynamoDB updates

**Status**: Accepted

## Context
In Dec 2023, a race condition caused duplicate order confirmations
when two Lambda instances processed the same event simultaneously.

## Decision
All DynamoDB writes MUST use ConditionExpression to prevent race conditions.
This is enforced by code review. See example in `shared/dynamo_utils.py`.

## Consequences
- Positive: No duplicate writes; idempotency guaranteed
- Negative: Slightly more complex write code; must think about conditions
```

Reference ADRs from CLAUDE.md:
```markdown
## Critical constraints
- All DynamoDB writes require ConditionExpression (ADR-0003)
  See @docs/decisions/0003-dynamo-conditional-writes.md
```

---

## Test Infrastructure as Documentation

Well-organized tests are some of the best documentation for AI tools. Tests show:
- What the expected behavior is
- What the edge cases are
- What the public interface contract looks like
- What failure modes exist and how they are handled

### Test Naming

```python
# Bad — tells AI nothing
def test_order():
    ...

def test_2():
    ...

# Good — readable spec
def test_order_creation_succeeds_with_valid_items():
    ...

def test_order_creation_fails_when_inventory_insufficient():
    ...

def test_order_retry_uses_exponential_backoff():
    ...
```

### Test Structure as Spec

Tests organized by scenario communicate intent:

```python
class TestOrderProcessor:
    class TestSuccessfulProcessing:
        def test_creates_order_record_in_dynamodb(self): ...
        def test_publishes_order_created_event_to_kinesis(self): ...
        def test_returns_order_id_in_response(self): ...

    class TestValidationFailures:
        def test_rejects_order_with_no_items(self): ...
        def test_rejects_order_exceeding_max_value(self): ...
        def test_does_not_charge_payment_on_validation_failure(self): ...

    class TestRetryBehavior:
        def test_retries_on_dynamodb_throttling(self): ...
        def test_does_not_retry_on_validation_error(self): ...
        def test_applies_exponential_backoff_between_retries(self): ...
```

### Verification-First for AI Agents

AI agents perform dramatically better when they can verify their own work. Provide:

```markdown
## Commands (in CLAUDE.md)
- Test: `pytest tests/ -v`
- Test single file: `pytest tests/test_order_processor.py -v`
- Type check: `mypy src/`
- Lint: `ruff check src/`
- All checks: `make ci`  ← a single command that runs everything
```

A `Makefile` or `package.json` scripts section with a single `ci` or `check` target is one of the highest-value additions for AI-assisted development.

---

## Practical AI-Readability Checklist

### Code-Level

- [ ] Module-level docstrings on every file (purpose + main exports)
- [ ] Type annotations on all public functions
- [ ] Custom exception types named meaningfully
- [ ] Named constants for all magic numbers and strings
- [ ] Test functions named as behavior descriptions

### Architecture-Level

- [ ] ARCHITECTURE.md with component map and data flow diagram
- [ ] ADRs for all significant non-obvious design decisions
- [ ] ADRs referenced from CLAUDE.md for critical constraints

### Context File Level (CLAUDE.md / AGENTS.md)

- [ ] All build/test/lint commands present as exact invocations
- [ ] Tech stack with versions stated explicitly
- [ ] Directory structure described (especially for monorepos)
- [ ] Non-obvious conventions documented
- [ ] File is under 150 lines; longer content referenced with @imports

### Repository Structure

- [ ] Conventional directory layout for the language/framework
- [ ] Predictable, descriptive file names (no abbreviations, no temporal names)
- [ ] Shallow nesting (prefer breadth over depth)
- [ ] CODEOWNERS configured for critical paths
