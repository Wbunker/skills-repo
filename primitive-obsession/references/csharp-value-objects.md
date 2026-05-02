# C# Value Objects

## Approach Selection

| Use case | Approach |
|---|---|
| Small, frequently used VO (Money, Point, Temp) | `readonly record struct` — stack-allocated, zero GC pressure |
| Larger VO, reference semantics needed | `record` class |
| Fine-grained equality control (exclude fields) | `ValueObject` base class with `GetAtomicValues()` |
| EF Core 8+ mapping | `ComplexProperty` (best current option) |
| EF Core 2–7 mapping | `OwnsOne` / `OwnsMany` |

---

## Pattern 1: `readonly record struct` (preferred for small VOs)

```csharp
public readonly record struct Money(decimal Amount, string Currency)
{
    // Positional record constructor validation (primary constructor)
    public Money : this(Amount, Currency)
    {
        if (Amount < 0)
            throw new ArgumentOutOfRangeException(nameof(Amount), "Must be non-negative");
        Currency = (Currency ?? throw new ArgumentNullException(nameof(Currency)))
                   .Trim().ToUpperInvariant();
        if (Currency.Length != 3)
            throw new ArgumentException("Currency must be 3-letter ISO code");
        Amount = Math.Round(Amount, 2);
    }

    public Money Add(Money other)
    {
        if (Currency != other.Currency)
            throw new InvalidOperationException($"Currency mismatch: {Currency} vs {other.Currency}");
        return this with { Amount = Amount + other.Amount };
    }

    public override string ToString() => $"{Amount} {Currency}";
}
```

**`readonly record struct` facts:**
- Stack-allocated — no heap allocation, no GC pressure
- `readonly` keyword is required — `record struct` alone is **mutable by default**
- `==` and `Equals()` auto-generated with structural equality
- `with` expression for immutable copies
- `GetHashCode()` auto-generated; consistent with `Equals()`
- Cannot inherit from classes; can implement interfaces

---

## Pattern 2: `record` class (reference type VO)

```csharp
public record EmailAddress
{
    public string Value { get; init; }

    public EmailAddress(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
            throw new ArgumentException("Email cannot be empty");
        var normalized = value.Trim().ToLowerInvariant();
        if (!normalized.Contains('@'))
            throw new ArgumentException($"Invalid email: {value}");
        Value = normalized;
    }

    public string Domain => Value.Split('@')[1];

    // with-expression for immutable copy:
    // var updated = email with { Value = "other@example.com" };
}

// Records auto-generate: Equals, GetHashCode, ==, !=, ToString, with-expression
var e1 = new EmailAddress("USER@EXAMPLE.COM");
var e2 = new EmailAddress("user@example.com");
Console.WriteLine(e1 == e2);  // true
```

**Primary constructor syntax (shorter):**

```csharp
public record EmailAddress(string Value)
{
    // init accessor with validation via property
    public string Value { get; init; } = Validate(Value);

    private static string Validate(string v)
    {
        if (!v.Trim().ToLower().Contains('@'))
            throw new ArgumentException($"Invalid email: {v}");
        return v.Trim().ToLowerInvariant();
    }
}
```

---

## Pattern 3: `ValueObject` Base Class (maximum control)

Use when `record` auto-equality doesn't match domain equality needs (e.g., a `FullName` where middle name is optional and shouldn't affect equality).

```csharp
public abstract class ValueObject : IEquatable<ValueObject>
{
    protected abstract IEnumerable<object?> GetAtomicValues();

    public bool Equals(ValueObject? other) =>
        other is not null && ValuesAreEqual(other);

    public override bool Equals(object? obj) =>
        obj is ValueObject vo && ValuesAreEqual(vo);

    public override int GetHashCode() =>
        GetAtomicValues().Aggregate(
            default(int),
            (hash, value) => HashCode.Combine(hash, value?.GetHashCode() ?? 0));

    public static bool operator ==(ValueObject? a, ValueObject? b) =>
        a is null && b is null || a is not null && a.Equals(b);

    public static bool operator !=(ValueObject? a, ValueObject? b) => !(a == b);

    private bool ValuesAreEqual(ValueObject other) =>
        GetAtomicValues().SequenceEqual(other.GetAtomicValues());
}

// Implementation
public sealed class Address : ValueObject
{
    public string Street { get; }
    public string City   { get; }
    public string ZipCode { get; }

    private Address(string street, string city, string zipCode)
    {
        Street  = street;
        City    = city;
        ZipCode = zipCode;
    }

    public static Address Create(string street, string city, string zipCode)
    {
        if (string.IsNullOrWhiteSpace(street))  throw new ArgumentException("Street required");
        if (string.IsNullOrWhiteSpace(city))    throw new ArgumentException("City required");
        if (string.IsNullOrWhiteSpace(zipCode)) throw new ArgumentException("ZipCode required");
        return new Address(street.Trim(), city.Trim(), zipCode.Trim());
    }

    // Only these fields participate in equality:
    protected override IEnumerable<object?> GetAtomicValues()
    {
        yield return Street;
        yield return City;
        yield return ZipCode;
    }
}
```

---

## EF Core Mapping

### EF Core 8+: `ComplexProperty` (recommended)

No shadow table, no owned entity overhead. Maps inline columns.

```csharp
// Entity configuration
modelBuilder.Entity<Order>()
    .ComplexProperty(o => o.ShippingAddress);

// Column customization
modelBuilder.Entity<Order>()
    .ComplexProperty(o => o.ShippingAddress, cp =>
    {
        cp.Property(a => a.Street).HasColumnName("shipping_street").IsRequired();
        cp.Property(a => a.City).HasColumnName("shipping_city");
        cp.Property(a => a.ZipCode).HasColumnName("shipping_zip");
    });
```

### EF Core 2–7: `OwnsOne` / `OwnsMany`

```csharp
modelBuilder.Entity<Order>()
    .OwnsOne(o => o.ShippingAddress, address =>
    {
        address.Property(a => a.Street).HasColumnName("shipping_street");
        address.Property(a => a.City).HasColumnName("shipping_city");
    });
```

### Single-column VO: Value Converter

```csharp
// For record/struct VOs mapping to a single column
modelBuilder.Entity<User>()
    .Property(u => u.Email)
    .HasConversion(
        v => v.Value,
        v => new EmailAddress(v));
```

---

## Common Gotchas

| Gotcha | Fix |
|---|---|
| `record struct` is mutable by default | Always say `readonly record struct` |
| `record` init accessor: `Value = Validate(Value)` — which `Value`? | The parameter in the primary constructor, not the property; be explicit |
| `record` equality includes ALL properties | Use `ValueObject` base class if some fields shouldn't affect equality |
| EF Core `OwnsOne` adds shadow keys | Use `ComplexProperty` (EF8+) to avoid |
| `ComplexProperty` fields cannot be null | Make them `string?` and handle null in the VO constructor |
| `with` expression on `record struct` calls no-arg constructor first | Ensure no-arg constructor sets valid defaults or throws |
| JSON serialization: `record` serializes as object by default | Fine for class records; for `record struct` wrapping a single value, add a `JsonConverter` |
