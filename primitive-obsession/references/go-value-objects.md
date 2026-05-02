# Go Value Objects

## Key Design Constraints

Go has no `const struct`, `readonly` fields, or language-level immutability. VOs are enforced by convention:

1. **Unexported fields** — external packages cannot mutate them
2. **Value receivers** — methods operate on copies, not originals
3. **No setter methods** — never expose a `Set...()` method
4. **Constructor returns value type** (not pointer) — enforces copy semantics for small VOs

---

## Pattern 1: Struct with Unexported Fields + Constructor

```go
package domain

import (
    "fmt"
    "net/mail"
    "strings"
)

// EmailAddress is a value type — unexported fields prevent external mutation
type EmailAddress struct {
    localPart string
    domain    string
}

// Parse is the only entry point — validates and constructs
func ParseEmail(raw string) (EmailAddress, error) {
    addr, err := mail.ParseAddress(raw)
    if err != nil {
        return EmailAddress{}, fmt.Errorf("invalid email %q: %w", raw, err)
    }
    parts := strings.Split(addr.Address, "@")
    if len(parts) != 2 {
        return EmailAddress{}, fmt.Errorf("invalid email %q: missing domain", raw)
    }
    return EmailAddress{
        localPart: strings.ToLower(parts[0]),
        domain:    strings.ToLower(parts[1]),
    }, nil
}

// Value receivers — methods work on copies; no mutation possible
func (e EmailAddress) String() string        { return e.localPart + "@" + e.domain }
func (e EmailAddress) Domain() string        { return e.domain }
func (e EmailAddress) HasDomain(d string) bool { return e.domain == strings.ToLower(d) }

// Structs with comparable fields support == automatically
// e1 == e2  works correctly with unexported string fields
```

### Multi-field VO (Money)

```go
package money

import "fmt"

type Money struct {
    amount   int64  // store as cents to avoid float precision issues
    currency string // ISO 4217
}

func New(amount int64, currency string) (Money, error) {
    currency = strings.ToUpper(strings.TrimSpace(currency))
    if len(currency) != 3 {
        return Money{}, fmt.Errorf("invalid currency %q: must be 3-letter ISO code", currency)
    }
    if amount < 0 {
        return Money{}, fmt.Errorf("negative amount %d not allowed", amount)
    }
    return Money{amount: amount, currency: currency}, nil
}

// Must returns a valid Money or panics — use only in tests or constants
func Must(amount int64, currency string) Money {
    m, err := New(amount, currency)
    if err != nil {
        panic(err)
    }
    return m
}

func (m Money) Add(other Money) (Money, error) {
    if m.currency != other.currency {
        return Money{}, fmt.Errorf("currency mismatch: %s vs %s", m.currency, other.currency)
    }
    return Money{amount: m.amount + other.amount, currency: m.currency}, nil
}

func (m Money) Amount() int64   { return m.amount }
func (m Money) Currency() string { return m.currency }
func (m Money) String() string  { return fmt.Sprintf("%d %s", m.amount, m.currency) }

// Equality via == works because all fields are comparable primitives
```

---

## Equality for Non-Comparable Structs

When a VO contains slices or maps, `==` panics at runtime. Implement `Equal`:

```go
type TagSet struct {
    tags []string // slice — not comparable with ==
}

func (t TagSet) Equal(other TagSet) bool {
    if len(t.tags) != len(other.tags) {
        return false
    }
    set := make(map[string]struct{}, len(t.tags))
    for _, tag := range t.tags {
        set[tag] = struct{}{}
    }
    for _, tag := range other.tags {
        if _, ok := set[tag]; !ok {
            return false
        }
    }
    return true
}
```

---

## Serialization

Implement `encoding.TextMarshaler` / `encoding.TextUnmarshaler` for transparent JSON and encoding support:

```go
// MarshalText satisfies encoding.TextMarshaler
func (e EmailAddress) MarshalText() ([]byte, error) {
    return []byte(e.String()), nil
}

// UnmarshalText satisfies encoding.TextUnmarshaler
// Note: pointer receiver — modifies the value in place
func (e *EmailAddress) UnmarshalText(data []byte) error {
    parsed, err := ParseEmail(string(data))
    if err != nil {
        return err
    }
    *e = parsed // validation runs through ParseEmail
    return nil
}

// This works automatically with encoding/json, encoding/xml, etc.
type User struct {
    Email EmailAddress `json:"email"`
}
```

---

## Database (database/sql)

```go
// Implement driver.Valuer and sql.Scanner
func (e EmailAddress) Value() (driver.Value, error) {
    return e.String(), nil
}

func (e *EmailAddress) Scan(src any) error {
    s, ok := src.(string)
    if !ok {
        return fmt.Errorf("EmailAddress.Scan: expected string, got %T", src)
    }
    parsed, err := ParseEmail(s)
    if err != nil {
        return err
    }
    *e = parsed
    return nil
}
```

---

## Functional Options (complex construction)

For VOs with many optional parameters, use functional options instead of a long parameter list:

```go
type ShipmentConfig struct {
    maxWeight   float64
    fragile     bool
    priority    Priority
    insuranceUp int64
}

type ConfigOption func(*ShipmentConfig) error

func WithMaxWeight(kg float64) ConfigOption {
    return func(c *ShipmentConfig) error {
        if kg <= 0 { return fmt.Errorf("maxWeight must be positive") }
        c.maxWeight = kg
        return nil
    }
}

func WithFragile() ConfigOption {
    return func(c *ShipmentConfig) error { c.fragile = true; return nil }
}

func NewShipmentConfig(opts ...ConfigOption) (ShipmentConfig, error) {
    cfg := ShipmentConfig{maxWeight: 30.0}  // defaults
    for _, o := range opts {
        if err := o(&cfg); err != nil {
            return ShipmentConfig{}, err
        }
    }
    return cfg, nil
}
```

---

## Common Gotchas

| Gotcha | Fix |
|---|---|
| Pointer receiver on `Equal` / value methods | Use value receivers on VOs; pointer receivers allow mutation |
| Struct with slice field: `==` panics | Implement `Equal(other T) bool` method |
| `Must(...)` constructor used in production code | Reserve `Must` for tests and package-level constants; always use error-returning constructor in runtime code |
| Unexported fields prevent `reflect.DeepEqual` in tests | Use `Equal()` method or compare exported accessors in tests |
| Zero value of struct is "valid" | Document zero value behavior; add `IsZero()` helper or use a sentinel |
| JSON: unexported fields are ignored by `encoding/json` | Implement `MarshalJSON`/`UnmarshalJSON` or `MarshalText`/`UnmarshalText` |
