# Python Value Objects

## Approach Selection

| Use case | Approach |
|---|---|
| Domain VO with validation + behavior | `@dataclass(frozen=True)` or `@frozen` (attrs) |
| API layer VO + serialization | Pydantic `BaseModel(frozen=True)` or `RootModel` |
| Single-value VO with rich validation | `@dataclass(frozen=True)` with `__post_init__` |
| Type disambiguation only (no validation) | `NewType` |
| High-volume, memory-sensitive VO | attrs `@frozen` with `slots=True` |

---

## Pattern 1: `@dataclass(frozen=True)` (stdlib, preferred)

```python
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class EmailAddress:
    value: str

    def __post_init__(self):
        normalized = self.value.strip().lower()
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', normalized):
            raise ValueError(f"Invalid email: {self.value!r}")
        # frozen=True blocks normal __setattr__; use object.__setattr__ for normalization
        object.__setattr__(self, 'value', normalized)

    def domain(self) -> str:
        return self.value.split('@')[1]

# frozen=True auto-generates __hash__ and __eq__ based on all fields
e1 = EmailAddress("USER@EXAMPLE.COM")
e2 = EmailAddress("user@example.com")
assert e1 == e2          # structural equality
assert hash(e1) == hash(e2)  # hashable → usable in sets / dict keys

# Immutable copy:
from dataclasses import replace
e3 = replace(e1, value="other@example.com")  # validates again in __post_init__
```

**Key flags:**
- `frozen=True` — raises `FrozenInstanceError` on mutation; auto-generates `__hash__`
- `eq=True` (default) — generates `__eq__` from all fields
- `order=True` — adds `__lt__`/`__gt__` if needed (e.g., for `Money`, `Temperature`)
- `object.__setattr__` — only way to assign in `__post_init__` when frozen

### Multi-field VO

```python
@dataclass(frozen=True, order=True)
class Money:
    amount: float
    currency: str   # ISO 4217, e.g. "USD"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError(f"amount must be non-negative, got {self.amount}")
        currency = self.currency.upper().strip()
        if len(currency) != 3:
            raise ValueError(f"currency must be 3-letter ISO code, got {currency!r}")
        object.__setattr__(self, 'amount', round(self.amount, 2))
        object.__setattr__(self, 'currency', currency)

    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError(f"Currency mismatch: {self.currency} vs {other.currency}")
        return Money(self.amount + other.amount, self.currency)
```

---

## Pattern 2: Pydantic v2 `BaseModel(frozen=True)`

Use at the API/application layer where serialization matters.

```python
from pydantic import BaseModel, ConfigDict, field_validator

class Money(BaseModel):
    model_config = ConfigDict(frozen=True)

    amount: float
    currency: str

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v < 0:
            raise ValueError('amount must be non-negative')
        return round(v, 2)

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        v = v.upper().strip()
        if len(v) != 3:
            raise ValueError('currency must be 3-letter ISO code')
        return v

    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError('Currency mismatch')
        return Money(amount=self.amount + other.amount, currency=self.currency)

# Immutable copy:
m2 = m1.model_copy(update={'amount': 150.00})
```

**Pydantic `RootModel` for single-value VOs:**

```python
from pydantic import RootModel, field_validator

class EmailAddress(RootModel[str]):
    @field_validator('root')
    @classmethod
    def validate(cls, v: str) -> str:
        v = v.strip().lower()
        if '@' not in v:
            raise ValueError('Invalid email')
        return v

email = EmailAddress('USER@EXAMPLE.COM')
print(email.root)  # 'user@example.com'
```

**Gotcha:** Pydantic `frozen=True` does NOT prevent mutation of nested mutable objects (dicts, lists) — only top-level field reassignment is blocked.

---

## Pattern 3: attrs `@frozen`

```python
import attrs
from attrs import define, frozen, field

@frozen   # implies slots=True, eq=True, hash=True, no setattr
class Temperature:
    celsius: float = field()

    @celsius.validator
    def _check(self, attribute, value):
        if value < -273.15:
            raise ValueError(f"Below absolute zero: {value}")

    @property
    def fahrenheit(self) -> float:
        return self.celsius * 9/5 + 32

# Immutable copy:
t2 = attrs.evolve(t1, celsius=100.0)
```

**attrs built-in validators:** `validators.instance_of(int)`, `validators.in_range(min=0, max=100)`, `validators.matches_re(r'...')`, `validators.not_(...)`, `validators.and_(v1, v2)`

**attrs vs dataclass:** prefer attrs when you need `slots=True` for memory efficiency on high-volume VOs, or when you want validator composition via `attrs.validators`.

---

## Pattern 4: `NewType` (compile-time only)

```python
from typing import NewType

UserId     = NewType('UserId', int)
CustomerId = NewType('CustomerId', int)

def find_order(customer_id: CustomerId) -> Order: ...

# find_order(UserId(42))  ← mypy/pyright flags this as type error
```

**Limitation:** Zero runtime overhead — `UserId(5)` is just `5` at runtime. No validation, no methods, no custom equality. Use only for distinguishing same-primitive types when no validation is needed.

---

## Serialization

```python
# dataclass → dict / JSON
from dataclasses import asdict
import json

@dataclass(frozen=True)
class Address:
    street: str
    city: str
    zip_code: str

    def to_dict(self) -> dict:
        return asdict(self)

# Pydantic: built-in
money.model_dump()          # → {'amount': 10.0, 'currency': 'USD'}
money.model_dump_json()     # → '{"amount":10.0,"currency":"USD"}'
Money.model_validate({'amount': 10.0, 'currency': 'USD'})
```

## ORM (SQLAlchemy)

```python
from sqlalchemy import String, TypeDecorator

class EmailAddressType(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return value.value if value is not None else None

    def process_result_value(self, value, dialect):
        return EmailAddress(value) if value is not None else None

# Usage in model:
class User(Base):
    email: Mapped[EmailAddress] = mapped_column(EmailAddressType)
```

## Common Gotchas

| Gotcha | Fix |
|---|---|
| Can't assign in `__post_init__` on frozen dataclass | Use `object.__setattr__(self, 'field', value)` |
| Pydantic frozen doesn't deep-freeze | Avoid mutable nested objects; use tuples instead of lists |
| `NewType` has no runtime validation | Use `@dataclass(frozen=True)` if you need validation |
| attrs `@define` is mutable by default | Use `@frozen` for VOs |
| dataclass `replace()` bypasses `__post_init__`? | No — `replace()` calls `__init__` which calls `__post_init__`; validation still runs |
