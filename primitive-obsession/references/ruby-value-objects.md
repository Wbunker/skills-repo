# Ruby Value Objects

## Approach Selection

| Use case | Approach |
|---|---|
| Ruby 3.2+, simple or complex VO | `Data.define` — always frozen, structural equality built-in |
| Pre-3.2 or need mutation | `Struct.new` + `freeze` in `initialize` |
| Enterprise domain model with type constraints | `dry-struct` + `dry-types` |
| Single-value type with constraints only | `dry-types` constrained type |

---

## Pattern 1: `Data.define` (Ruby 3.2+, preferred)

```ruby
EmailAddress = Data.define(:value) do
  def initialize(value:)
    value = value.to_s.strip.downcase
    raise ArgumentError, "Invalid email: #{value.inspect}" \
      unless value.match?(/\A[^@]+@[^@]+\.[^@]+\z/)
    super(value:)   # MUST call super to assign the frozen fields
  end

  def domain
    value.split('@').last
  end

  def to_s
    value
  end
end

e1 = EmailAddress.new(value: "USER@EXAMPLE.COM")
e2 = EmailAddress.new(value: "user@example.com")

e1.value      # => "user@example.com"
e1.frozen?    # => true
e1 == e2      # => true  (structural equality built-in)
e1.eql?(e2)   # => true
e1.hash == e2.hash  # => true  (consistent hash)

# Immutable copy via with:
e3 = e1.with(value: "other@example.com")  # validates again in initialize
```

**`Data.define` rules:**
- All members are required keyword arguments — no optional fields without defaults
- Object is frozen after `initialize` returns — `freeze` is automatic
- Auto-generates `==`, `eql?`, `hash`, `to_h`, `inspect`, `members`
- Call `super(member:)` in `initialize` to set the frozen fields
- Cannot add instance variables beyond the defined members

### Multi-field VO

```ruby
Money = Data.define(:amount, :currency) do
  def initialize(amount:, currency:)
    amount   = amount.to_r   # Rational for precision, or BigDecimal
    currency = currency.to_s.strip.upcase

    raise ArgumentError, "amount must be non-negative" if amount < 0
    raise ArgumentError, "currency must be 3-letter ISO code" unless currency.length == 3

    super(amount:, currency:)
  end

  def add(other)
    raise ArgumentError, "Currency mismatch" unless currency == other.currency
    Money.new(amount: amount + other.amount, currency:)
  end

  def to_s
    "#{amount} #{currency}"
  end
end

usd = Money.new(amount: 10.50, currency: "usd")
usd.currency  # => "USD"
usd.frozen?   # => true
```

---

## Pattern 2: `Struct.new` + `freeze` (pre-Ruby 3.2)

```ruby
Money = Struct.new(:amount, :currency) do
  def initialize(amount, currency)
    raise ArgumentError, "amount must be non-negative" unless amount >= 0
    raise ArgumentError, "currency must be 3 chars"    unless currency.to_s.length == 3
    super(amount.round(2), currency.to_s.upcase)
    freeze  # explicit — Struct is mutable by default
  end

  def add(other)
    raise ArgumentError, "Currency mismatch" unless currency == other.currency
    Money.new(amount + other.amount, currency)
  end

  def to_s
    "#{amount} #{currency}"
  end
end
```

**`Struct` vs `Data` comparison:**

| | `Data.define` | `Struct.new` |
|---|---|---|
| Frozen | Always | Only with explicit `freeze` |
| Missing args | `ArgumentError` | Allowed (nil) |
| Writers | None | Has setters (mutable) |
| Ruby version | 3.2+ | All versions |
| Equality | Value-based auto | Value-based auto |

---

## Pattern 3: `dry-struct` + `dry-types` (enterprise)

```ruby
require 'dry-struct'
require 'dry-types'

module Types
  include Dry.Types()

  # Custom constrained types — these ARE value objects themselves
  Email      = Types::String.constrained(format: /\A[^@]+@[^@]+\.[^@]+\z/)
                            .constructor { |v| v.to_s.strip.downcase }

  Currency   = Types::String.constrained(min_size: 3, max_size: 3)
                            .constructor { |v| v.to_s.upcase }

  NonNegAmt  = Types::Decimal.constrained(gteq: 0)
end

class Money < Dry::Struct
  attribute :amount,   Types::NonNegAmt
  attribute :currency, Types::Currency

  def add(other)
    raise ArgumentError, "Currency mismatch" unless currency == other.currency
    self.class.new(amount: amount + other.amount, currency:)
  end

  def to_s
    "#{amount} #{currency}"
  end
end

# dry-struct instances are immutable (no attribute writers)
m = Money.new(amount: 10.5, currency: "usd")
m.currency  # => "USD"  (constructor normalized it)
```

**`dry-types` standalone for single-value VOs:**

```ruby
module Types
  include Dry.Types()
  PhoneNumber = Types::String
    .constructor { |v| v.to_s.gsub(/\D/, '') }
    .constrained(min_size: 10, max_size: 15)
end

Types::PhoneNumber["  (555) 867-5309 "]  # => "5558675309"
Types::PhoneNumber["123"]                # => Dry::Types::ConstraintError
```

---

## Serialization

```ruby
# Data.define — to_h built-in
address = Address.new(street: "123 Main", city: "Austin", zip: "78701")
address.to_h   # => {street: "123 Main", city: "Austin", zip: "78701"}
address.to_h.to_json  # with 'json' library

# Custom JSON serialization
EmailAddress.class_eval do
  def as_json(*)  = value
  def to_json(**) = value.to_json
end

# dry-struct: to_h built-in
money.to_h  # => {amount: #<BigDecimal:'10.5'>, currency: "USD"}
```

---

## ActiveRecord Mapping

```ruby
# app/models/user.rb — store as string column, expose as VO
class User < ApplicationRecord
  def email
    EmailAddress.new(value: self[:email]) if self[:email]
  end

  def email=(val)
    self[:email] = val.is_a?(EmailAddress) ? val.value : EmailAddress.new(value: val.to_s).value
  end
end

# Or use a composed_of macro (Rails built-in):
class Order < ApplicationRecord
  composed_of :shipping_address,
    class_name: 'Address',
    mapping: [%w[shipping_street street], %w[shipping_city city], %w[shipping_zip zip_code]]
end
# Rails calls Address.new(street:, city:, zip_code:) automatically on load
```

**`composed_of` requirements:** The VO class must accept keyword arguments matching the mapping, and Rails calls `freeze` on the result.

---

## Common Gotchas

| Gotcha | Fix |
|---|---|
| Forgetting `super` in `Data.define` initialize | Members are never assigned without `super(member:)`; object has no accessible values |
| `Struct` without `freeze` | Always call `freeze` at the end of `Struct#initialize`; or use `Data.define` |
| `Data.define` members are keyword-only | All construction must use keyword syntax: `Email.new(value: "...")`, not `Email.new("...")` |
| `dry-struct` requires explicit `Dry.Types()` include | Define a `Types` module in your app and include in one place |
| `composed_of` and VO with required args | Ensure the VO constructor accepts all mapped columns as keyword args |
| `to_h` on `Data` returns symbol keys | Use `address.to_h.transform_keys(&:to_s)` for JSON interop if string keys are needed |
| Equality on `Struct` includes class | `Struct.new(:x).new(1) == Struct.new(:x).new(1)` is `false` if different struct classes — always compare same VO type |
