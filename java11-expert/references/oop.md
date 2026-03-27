# Java 11 Object-Oriented Programming
## Classes, Interfaces, Inheritance, Enums, Nested Classes, Nest-Based Access

---

## Classes and Objects

### Class Anatomy

```java
public class BankAccount {
    // Fields
    private String owner;
    private double balance;
    private static int count = 0;   // shared across all instances

    // Constructors
    public BankAccount(String owner, double initialBalance) {
        this.owner = owner;
        this.balance = initialBalance;
        count++;
    }

    // Instance methods
    public void deposit(double amount) {
        if (amount <= 0) throw new IllegalArgumentException("Amount must be positive");
        balance += amount;
    }

    // Static method
    public static int getCount() { return count; }

    // Getters
    public String getOwner() { return owner; }
    public double getBalance() { return balance; }
}
```

### Access Modifiers

| Modifier | Class | Package | Subclass | World |
|----------|-------|---------|----------|-------|
| `public` | Yes | Yes | Yes | Yes |
| `protected` | Yes | Yes | Yes | No |
| (none) | Yes | Yes | No | No |
| `private` | Yes | No | No | No |

---

## Interfaces (Java 9+ features available in Java 11)

Interfaces in Java 11 support four member types:

```java
public interface Vehicle {
    // Abstract method (implicit public abstract)
    int getSpeed();

    // Default method (Java 8+) — can be overridden
    default String describe() {
        return "Vehicle at " + getSpeed() + " km/h";
    }

    // Static method (Java 8+) — not inherited
    static Vehicle slowest(Vehicle a, Vehicle b) {
        return a.getSpeed() <= b.getSpeed() ? a : b;
    }

    // Private method (Java 9+) — shared helper for default/static methods
    private void log(String msg) {
        System.out.println("[Vehicle] " + msg);
    }

    // Private static method (Java 9+)
    private static void logStatic(String msg) {
        System.out.println("[Vehicle-static] " + msg);
    }
}
```

### Interface vs. Abstract Class

| | Interface | Abstract Class |
|-|-----------|---------------|
| Instantiation | No | No |
| Constructor | No | Yes |
| Fields | `public static final` only | Any |
| Methods | abstract, default, static, private | Any |
| Multiple inheritance | Yes (implement many) | No (extend one) |
| State | No instance state | Can have instance state |
| Use when | Defining capability/contract | Sharing implementation |

### Functional Interface

An interface with exactly **one abstract method** — usable as a lambda target.

```java
@FunctionalInterface
public interface Transformer<T, R> {
    R transform(T input);    // single abstract method
    // default and static methods OK
}

Transformer<String, Integer> len = s -> s.length();
```

---

## Inheritance and Polymorphism

```java
public abstract class Shape {
    public abstract double area();

    public String describe() {
        return getClass().getSimpleName() + " with area " + area();
    }
}

public class Circle extends Shape {
    private final double radius;
    public Circle(double radius) { this.radius = radius; }

    @Override
    public double area() { return Math.PI * radius * radius; }
}

// Polymorphism
Shape s = new Circle(5.0);
s.area();       // calls Circle.area() — runtime dispatch
s.describe();   // calls Shape.describe() which calls Circle.area()
```

### Method Overriding Rules

- Same name, same parameter list, same or covariant return type
- Access modifier can be same or **more** permissive (not less)
- Cannot override `static`, `private`, or `final` methods
- Use `@Override` to get compiler verification

### Method Overloading

- Same name, different parameter list (type, count, or order)
- Return type alone does not distinguish overloads
- Resolved at **compile time** (static dispatch)

### `final`

- `final class` — cannot be subclassed
- `final method` — cannot be overridden
- `final field` — must be assigned once (in declaration or constructor); effectively makes field a constant if also `static`
- `final local variable` / effectively final — required for use in lambdas and anonymous inner classes

---

## Abstract Classes

```java
public abstract class Animal {
    private String name;

    public Animal(String name) { this.name = name; }

    // Abstract — subclasses must implement
    public abstract String sound();

    // Concrete — inherited as-is
    public String getName() { return name; }
    public String toString() { return name + " says " + sound(); }
}

public class Dog extends Animal {
    public Dog(String name) { super(name); }

    @Override
    public String sound() { return "Woof"; }
}
```

---

## Enums

```java
public enum Planet {
    MERCURY(3.303e+23, 2.4397e6),
    VENUS  (4.869e+24, 6.0518e6),
    EARTH  (5.976e+24, 6.37814e6);

    private final double mass;     // in kilograms
    private final double radius;   // in meters

    Planet(double mass, double radius) {
        this.mass = mass;
        this.radius = radius;
    }

    double surfaceGravity() {
        final double G = 6.67300E-11;
        return G * mass / (radius * radius);
    }
}

// Usage
Planet p = Planet.EARTH;
p.name()          // "EARTH"
p.ordinal()       // 2 (zero-based)
Planet.valueOf("VENUS")   // Planet.VENUS
Planet.values()           // Planet[] of all values
```

Enums can implement interfaces but cannot extend classes (already extend `Enum`).

---

## Nested Classes

Java has four kinds of nested classes:

### 1. Static Nested Class

```java
public class Outer {
    private static int x = 10;

    public static class StaticNested {
        void show() { System.out.println(x); }  // can access outer static members
    }
}
// Instantiate: new Outer.StaticNested()
```

### 2. Inner Class (Non-Static)

```java
public class Outer {
    private int y = 20;

    public class Inner {
        void show() { System.out.println(y); }  // can access outer instance members
    }
}
// Instantiate: new Outer().new Inner()
```

### 3. Local Class

Defined inside a method; can access effectively final local variables.

```java
void process(List<String> items) {
    final String prefix = "ITEM-";

    class Formatter {
        String format(String s) { return prefix + s; }
    }

    items.stream().map(new Formatter()::format).forEach(System.out::println);
}
```

### 4. Anonymous Inner Class

Inline subclass or interface implementation:

```java
Runnable r = new Runnable() {
    @Override
    public void run() {
        System.out.println("Running anonymously");
    }
};
// In most cases, a lambda is preferred:
Runnable r2 = () -> System.out.println("Running with lambda");
```

---

## Nest-Based Access Control (JEP 181, Java 11)

Prior to Java 11, nested classes accessing each other's `private` members required compiler-generated **synthetic bridge methods** (`access$000`, etc.), which:
- Appear in bytecode/stack traces confusingly
- Have package-private access (slightly widens visibility)
- Increase bytecode size

Java 11 introduces **nests** — a JVM concept grouping nested classes. The JVM itself enforces access, eliminating synthetic methods.

```java
public class Outer {
    private String secret = "hidden";

    class Inner {
        void reveal() {
            System.out.println(secret);   // direct private access — no bridge needed
        }
    }
}
```

### Reflection API for Nests

```java
Class<?> c = Outer.Inner.class;
c.getNestHost();         // Outer.class
c.getNestMembers();      // [Outer.class, Outer.Inner.class]
c.isNestmateOf(Outer.class);  // true
```

### Why It Matters

- Cleaner stack traces (no `access$000` frames)
- Slightly smaller bytecode
- Frameworks using bytecode manipulation work more predictably

---

## Encapsulation Patterns

### Immutable Class

```java
public final class Money {
    private final long cents;
    private final String currency;

    public Money(long cents, String currency) {
        this.cents = cents;
        this.currency = Objects.requireNonNull(currency);
    }

    public long getCents() { return cents; }
    public String getCurrency() { return currency; }

    public Money add(Money other) {
        if (!currency.equals(other.currency))
            throw new IllegalArgumentException("Currency mismatch");
        return new Money(cents + other.cents, currency);  // new object
    }
}
```

Rules for immutability:
1. Class is `final` (prevent subclassing)
2. All fields are `private final`
3. No setters
4. Defensive copies for mutable fields (arrays, collections)
5. Constructor validates invariants

---

## `instanceof` Operator

Standard Java 11 form (pattern matching for `instanceof` is Java 16):

```java
Object obj = getSomething();

if (obj instanceof String) {
    String s = (String) obj;   // explicit cast still required in Java 11
    System.out.println(s.length());
}

// Checking before casting avoids ClassCastException
```

---

## `Object` Methods to Override

| Method | Contract |
|--------|---------|
| `equals(Object)` | Reflexive, symmetric, transitive, consistent, null-safe |
| `hashCode()` | Equal objects must have equal hash codes; consistent with `equals` |
| `toString()` | Human-readable representation |
| `compareTo(T)` | Consistent with `equals` recommended (for sorted collections) |

```java
@Override
public boolean equals(Object o) {
    if (this == o) return true;
    if (!(o instanceof BankAccount)) return false;
    BankAccount that = (BankAccount) o;
    return Objects.equals(owner, that.owner);
}

@Override
public int hashCode() {
    return Objects.hash(owner);
}
```
