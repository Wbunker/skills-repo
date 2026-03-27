# Java 11 Generics and Collections
## Type Parameters, Wildcards, List/Set/Map/Queue, Factory Methods, Comparator

---

## Generics

Generics provide compile-time type safety and eliminate explicit casts.

### Generic Class

```java
public class Box<T> {
    private T value;
    public Box(T value) { this.value = value; }
    public T get() { return value; }
    public <R> Box<R> map(java.util.function.Function<T, R> f) {
        return new Box<>(f.apply(value));
    }
}

Box<String> box = new Box<>("hello");
Box<Integer> lenBox = box.map(String::length);
```

### Generic Method

```java
public static <T extends Comparable<T>> T max(T a, T b) {
    return a.compareTo(b) >= 0 ? a : b;
}

String s = max("apple", "banana");   // inferred: T = String
```

### Type Erasure

Generics are erased at runtime — `List<String>` and `List<Integer>` are both `List` at the JVM level. Consequences:
- Cannot do `new T()` or `new T[]`
- Cannot use generic type in `instanceof`: `obj instanceof List<String>` — compile error
- `obj instanceof List<?>` is OK (unbounded wildcard)

---

## Wildcards

### Unbounded Wildcard: `<?>`

Accepts any type. Use when you only read from the collection or work with `Object`.

```java
void printAll(List<?> list) {
    for (Object item : list) System.out.println(item);
}
```

### Upper-Bounded Wildcard: `<? extends T>`

Accepts `T` or any subtype. **Producer** — you can read `T` from it.

```java
double sumList(List<? extends Number> list) {
    return list.stream().mapToDouble(Number::doubleValue).sum();
}
sumList(List.of(1, 2, 3));       // List<Integer> — OK
sumList(List.of(1.5, 2.5));      // List<Double> — OK
```

You **cannot add** to `List<? extends Number>` (except `null`) because the compiler doesn't know the exact subtype.

### Lower-Bounded Wildcard: `<? super T>`

Accepts `T` or any supertype. **Consumer** — you can write `T` into it.

```java
void addNumbers(List<? super Integer> list) {
    list.add(1);
    list.add(2);
}
addNumbers(new ArrayList<Integer>());  // OK
addNumbers(new ArrayList<Number>());   // OK
addNumbers(new ArrayList<Object>());   // OK
```

### PECS Mnemonic

**P**roducer **E**xtends, **C**onsumer **S**uper:
- Reading from a collection (producing values to your code) → `<? extends T>`
- Writing to a collection (consuming values from your code) → `<? super T>`

---

## Core Collection Interfaces

```
Iterable
  └── Collection
        ├── List     — ordered, allows duplicates, index access
        ├── Set      — no duplicates
        │    └── SortedSet → NavigableSet
        └── Queue    — FIFO, head/tail operations
              └── Deque  — double-ended queue, stack operations

Map      — key-value pairs, keys unique
  └── SortedMap → NavigableMap
```

---

## List Implementations

| Class | Backed By | Get | Add/Remove | Thread-safe |
|-------|-----------|-----|-----------|------------|
| `ArrayList` | Array | O(1) | O(n) amortized O(1) append | No |
| `LinkedList` | Doubly-linked | O(n) | O(1) at head/tail | No |
| `CopyOnWriteArrayList` | Array (copy on write) | O(1) | O(n) | Yes |

```java
List<String> list = new ArrayList<>();
list.add("a");
list.add(0, "b");           // insert at index
list.get(0);                // "b"
list.set(1, "c");           // replace index 1
list.remove(0);             // by index
list.remove("c");           // by value (first occurrence)
list.subList(0, 2);         // view of elements [0, 2)
```

---

## Set Implementations

| Class | Order | Null | Thread-safe | Notes |
|-------|-------|------|------------|-------|
| `HashSet` | None | One null | No | O(1) operations |
| `LinkedHashSet` | Insertion order | One null | No | Predictable iteration |
| `TreeSet` | Sorted (natural or Comparator) | No null | No | O(log n) |
| `EnumSet` | Enum ordinal | No null | No | Fastest for enums |

```java
Set<String> set = new HashSet<>(List.of("a", "b", "c"));
set.add("d");
set.contains("a");   // true
set.remove("b");
```

---

## Map Implementations

| Class | Order | Null keys/values | Thread-safe |
|-------|-------|-----------------|------------|
| `HashMap` | None | One null key, null values | No |
| `LinkedHashMap` | Insertion order | Same as HashMap | No |
| `TreeMap` | Sorted by key | No null key | No |
| `ConcurrentHashMap` | None | No nulls | Yes |
| `EnumMap` | Enum ordinal | No null key | No |

```java
Map<String, Integer> map = new HashMap<>();
map.put("a", 1);
map.get("a");              // 1
map.getOrDefault("z", 0); // 0
map.putIfAbsent("b", 2);
map.computeIfAbsent("c", k -> k.length());  // 1
map.merge("a", 10, Integer::sum);            // a → 11
map.forEach((k, v) -> System.out.println(k + "=" + v));
```

---

## Queue and Deque

```java
Queue<String> queue = new ArrayDeque<>();
queue.offer("first");   // add to tail
queue.peek();           // view head, null if empty
queue.poll();           // remove head, null if empty

Deque<String> deque = new ArrayDeque<>();
deque.push("top");      // add to front (stack push)
deque.pop();            // remove from front (stack pop)
deque.addLast("end");   // add to tail
deque.peekFirst();      // view front
```

`ArrayDeque` is faster than `LinkedList` for queue/stack operations. Prefer it.

---

## Immutable Factory Methods (Java 9+)

`List.of()`, `Set.of()`, and `Map.of()` create **unmodifiable** collections:
- Cannot add, remove, or set elements (throws `UnsupportedOperationException`)
- Cannot contain `null` (throws `NullPointerException`)
- Iteration order not guaranteed for `Set.of()` and `Map.of()`

```java
List<String> list = List.of("a", "b", "c");
Set<Integer> set  = Set.of(1, 2, 3);
Map<String, Integer> map = Map.of("one", 1, "two", 2);   // up to 10 pairs

// For > 10 map entries:
Map<String, Integer> big = Map.ofEntries(
    Map.entry("a", 1),
    Map.entry("b", 2)
    // ...
);
```

To get a **mutable** copy:
```java
List<String> mutable = new ArrayList<>(List.of("a", "b", "c"));
```

### `List.copyOf()` / `Set.copyOf()` / `Map.copyOf()` (Java 10+)

Returns an unmodifiable copy of an existing collection:
```java
List<String> copy = List.copyOf(existingList);
```

---

## New `Collection.toArray` (Java 11)

Java 11 adds a type-safe `toArray` overload using `IntFunction<T[]>`:

```java
List<String> list = List.of("a", "b", "c");

// Before Java 11 (ugly cast)
String[] arr = list.toArray(new String[0]);

// Java 11 — method reference syntax
String[] arr = list.toArray(String[]::new);
```

---

## Sorting

### `Comparable` — Natural Ordering

Implement in your class to define default sort order:

```java
public class Student implements Comparable<Student> {
    private String name;
    private int gpa;

    @Override
    public int compareTo(Student other) {
        return this.name.compareTo(other.name);  // sort by name ascending
    }
}
```

### `Comparator` — External / Custom Ordering

```java
List<Student> students = new ArrayList<>(/* ... */);

// Static factory methods
students.sort(Comparator.comparing(Student::getName));
students.sort(Comparator.comparing(Student::getGpa).reversed());

// Chained comparators
students.sort(Comparator.comparing(Student::getGpa)
    .thenComparing(Student::getName));

// Null handling
students.sort(Comparator.comparing(Student::getName,
    Comparator.nullsLast(Comparator.naturalOrder())));
```

### `Collections` Utility Class

```java
Collections.sort(list);                  // natural order
Collections.sort(list, comparator);      // custom order
Collections.reverse(list);
Collections.shuffle(list);
Collections.min(collection);
Collections.max(collection);
Collections.frequency(collection, obj);
Collections.unmodifiableList(list);      // wrapper; original still mutable
Collections.synchronizedList(list);      // synchronized wrapper
Collections.disjoint(c1, c2);           // true if no common elements
Collections.nCopies(n, obj);            // immutable list of n copies
```

---

## PriorityQueue

Min-heap by default (smallest element at head):

```java
PriorityQueue<Integer> pq = new PriorityQueue<>();
pq.offer(5);
pq.offer(1);
pq.offer(3);
pq.poll();    // 1 (smallest first)

// Max-heap
PriorityQueue<Integer> maxPq = new PriorityQueue<>(Comparator.reverseOrder());
```

---

## Common Pitfalls

| Pitfall | Correct Approach |
|---------|-----------------|
| `==` on strings/wrappers | Use `.equals()` |
| Modifying list while iterating | Use `Iterator.remove()` or collect to new list |
| `HashMap` iteration order | Use `LinkedHashMap` if order matters |
| `TreeSet`/`TreeMap` with null | Not allowed — use `HashSet`/`HashMap` |
| `List.of()` null elements | Not allowed — use `Arrays.asList()` if null needed |
| `Collections.sort()` on `List.of()` | Not modifiable — copy first |
