# Rust Value Objects

## Key Design Advantage

Rust's ownership and type system makes VOs the natural default. Private fields + no public setter = true immutability enforced by the compiler. Holding a valid `EmailAddress` instance guarantees it passed construction — the type system makes invalid state unrepresentable.

## Approach Selection

| Use case | Approach |
|---|---|
| Single-value VO (wraps one primitive) | Newtype tuple struct |
| Fallible construction (most VOs) | `impl TryFrom<&str>` / `TryFrom<T>` |
| Infallible construction (always valid) | `impl From<T>` |
| Declarative VO with sanitize + validate | `nutype` macro crate |
| Numeric VO with range constraint | `TryFrom<f64>` + `nutype` |

---

## Pattern 1: Newtype Tuple Struct (core pattern)

```rust
use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq, Hash)]  // structural equality + hashable
pub struct EmailAddress(String);              // private inner field by default

#[derive(Debug, thiserror::Error)]
#[error("{0:?} is not a valid email address")]
pub struct EmailAddressError(String);

impl EmailAddress {
    pub fn new(raw: &str) -> Result<Self, EmailAddressError> {
        let normalized = raw.trim().to_lowercase();
        if !normalized.contains('@') || normalized.len() < 5 {
            return Err(EmailAddressError(raw.to_string()));
        }
        Ok(Self(normalized))
    }

    pub fn domain(&self) -> &str {
        self.0.split('@').nth(1).unwrap()
    }
}

// Borrow without exposing internals
impl AsRef<str> for EmailAddress {
    fn as_ref(&self) -> &str { &self.0 }
}

// Display for formatting
impl fmt::Display for EmailAddress {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0)
    }
}

// Idiomatic fallible conversion trait
impl TryFrom<&str> for EmailAddress {
    type Error = EmailAddressError;
    fn try_from(s: &str) -> Result<Self, Self::Error> {
        EmailAddress::new(s)
    }
}

impl TryFrom<String> for EmailAddress {
    type Error = EmailAddressError;
    fn try_from(s: String) -> Result<Self, Self::Error> {
        EmailAddress::new(&s)
    }
}
```

**Usage:**
```rust
// Three equivalent ways to construct:
let e1 = EmailAddress::new("USER@EXAMPLE.COM")?;
let e2 = EmailAddress::try_from("user@example.com")?;
let e3: EmailAddress = "user@example.com".try_into()?;

assert_eq!(e1, e2);          // PartialEq derived — structural equality
assert_eq!(e1.domain(), "example.com");
println!("{}", e1);           // "user@example.com" via Display
```

---

## Pattern 2: Numeric VO with `TryFrom`

```rust
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
pub struct Percentage(f64);

#[derive(Debug, thiserror::Error)]
#[error("percentage must be 0.0..=100.0, got {0}")]
pub struct PercentageError(f64);

impl TryFrom<f64> for Percentage {
    type Error = PercentageError;
    fn try_from(v: f64) -> Result<Self, Self::Error> {
        if !(0.0..=100.0).contains(&v) {
            Err(PercentageError(v))
        } else {
            Ok(Self(v))
        }
    }
}

impl Percentage {
    // Consuming accessor — caller gets owned value
    pub fn into_inner(self) -> f64 { self.0 }
    // Borrowing accessor
    pub fn value(&self) -> f64 { self.0 }
}
```

**Note on `Copy`:** Derive `Copy` only for types wrapping `Copy` primitives (`f64`, `u32`, `bool`) — not for `String`-based types.

---

## Pattern 3: Multi-field VO

```rust
use rust_decimal::Decimal;

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Money {
    amount:   Decimal,
    currency: CurrencyCode,  // another VO
}

#[derive(Debug, thiserror::Error)]
pub enum MoneyError {
    #[error("amount must be non-negative")]
    NegativeAmount,
    #[error("currency mismatch: {0} vs {1}")]
    CurrencyMismatch(String, String),
}

impl Money {
    pub fn new(amount: Decimal, currency: CurrencyCode) -> Result<Self, MoneyError> {
        if amount < Decimal::ZERO {
            return Err(MoneyError::NegativeAmount);
        }
        Ok(Self { amount: amount.round_dp(2), currency })
    }

    pub fn add(self, other: Money) -> Result<Money, MoneyError> {
        if self.currency != other.currency {
            return Err(MoneyError::CurrencyMismatch(
                self.currency.to_string(),
                other.currency.to_string(),
            ));
        }
        Ok(Money { amount: self.amount + other.amount, currency: self.currency })
    }

    pub fn amount(&self)   -> Decimal      { self.amount }
    pub fn currency(&self) -> &CurrencyCode { &self.currency }
}
```

---

## Pattern 4: `nutype` Macro (declarative, reduces boilerplate)

```toml
# Cargo.toml
[dependencies]
nutype = { version = "0.5", features = ["serde"] }
```

```rust
use nutype::nutype;

#[nutype(
    sanitize(trim, lowercase),
    validate(not_empty, len_char_max = 254, regex = r"^[^@]+@[^@]+\.[^@]+$"),
    derive(Debug, Clone, PartialEq, Eq, Hash, Display, AsRef, TryFrom, Serialize, Deserialize),
)]
pub struct EmailAddress(String);

#[nutype(
    validate(greater_or_equal = 18, less_or_equal = 120),
    derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, TryFrom),
)]
pub struct Age(u8);

// nutype generates EmailAddressError and AgeError automatically
let email = EmailAddress::try_new("  USER@EXAMPLE.COM  ")?;
println!("{}", email);  // "user@example.com"

let age = Age::try_new(25)?;
// age.into_inner() → 25u8
```

**`nutype` sanitize options:** `trim`, `lowercase`, `uppercase`, custom closure `with = |s| ...`

**`nutype` validate options:** `not_empty`, `len_char_min`, `len_char_max`, `regex`, `predicate = |v| ...`, `greater`, `less`, `greater_or_equal`, `less_or_equal`, `finite`

---

## Serialization (serde)

```rust
use serde::{Deserialize, Deserializer, Serialize, Serializer};

impl Serialize for EmailAddress {
    fn serialize<S: Serializer>(&self, s: S) -> Result<S::Ok, S::Error> {
        s.serialize_str(self.as_ref())
    }
}

impl<'de> Deserialize<'de> for EmailAddress {
    fn deserialize<D: Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        let s = String::deserialize(d)?;
        EmailAddress::try_from(s).map_err(serde::de::Error::custom)
    }
}
```

With `nutype` + `features = ["serde"]`, the above is handled automatically via `derive(Serialize, Deserialize)`.

---

## Database (sqlx)

```rust
impl sqlx::Type<sqlx::Postgres> for EmailAddress {
    fn type_info() -> sqlx::postgres::PgTypeInfo {
        <String as sqlx::Type<sqlx::Postgres>>::type_info()
    }
}

impl<'r> sqlx::Decode<'r, sqlx::Postgres> for EmailAddress {
    fn decode(value: sqlx::postgres::PgValueRef<'r>) -> Result<Self, sqlx::error::BoxDynError> {
        let s = <String as sqlx::Decode<sqlx::Postgres>>::decode(value)?;
        EmailAddress::try_from(s).map_err(Into::into)
    }
}
```

---

## Common Gotchas

| Gotcha | Fix |
|---|---|
| Exposing `.0` as `pub` | Keep inner field private; expose via `AsRef`, `Display`, `into_inner()`, `value()` |
| Deriving `Copy` on a `String` wrapper | `String` is not `Copy`; only derive `Copy` for wrappers around `Copy` types |
| `PartialEq` but not `Eq` | If the inner type implements `Eq`, derive both; `Eq` is required for `HashMap` keys |
| No `Hash` derived | `Hash` is required to use VOs as `HashMap`/`HashSet` keys; derive it when inner type is `Hash` |
| `f64` doesn't implement `Eq` or `Hash` | Use `rust_decimal::Decimal` or `ordered_float::OrderedFloat<f64>` for monetary/numeric VOs |
| `TryFrom<String>` vs `TryFrom<&str>` | Implement both; `&str` is for literals, `String` for owned values at runtime |
| `nutype` regex requires `regex` feature | Add `nutype = { features = ["regex"] }` in Cargo.toml |
