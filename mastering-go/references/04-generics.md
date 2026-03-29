# Ch 4 — Go Generics

Generics were added in Go 1.18. They allow writing functions and types that work with multiple types without code duplication.

## Type Parameters

```go
// Generic function
func Map[T, U any](s []T, f func(T) U) []U {
    result := make([]U, len(s))
    for i, v := range s {
        result[i] = f(v)
    }
    return result
}

// Call — type inference
doubled := Map([]int{1, 2, 3}, func(n int) int { return n * 2 })
strings := Map([]int{1, 2, 3}, strconv.Itoa)

// Explicit type arguments
doubled2 := Map[int, int]([]int{1, 2, 3}, func(n int) int { return n * 2 })
```

## Type Constraints

Constraints are interfaces that restrict which types a type parameter can accept.

```go
// Basic constraints
func Min[T constraints.Ordered](a, b T) T {
    if a < b { return a }
    return b
}

// Custom constraint
type Number interface {
    int | int8 | int16 | int32 | int64 |
    float32 | float64
}

func Sum[T Number](nums []T) T {
    var total T
    for _, n := range nums {
        total += n
    }
    return total
}
```

### Built-in constraint interfaces
```go
import "golang.org/x/exp/constraints"
// or use comparable, any (built-in)

any           // alias for interface{}
comparable    // types that support ==

// golang.org/x/exp/constraints
constraints.Ordered    // int, float, string (supports < > <= >=)
constraints.Integer    // all integer types
constraints.Float      // float32, float64
constraints.Signed     // signed integers
constraints.Unsigned   // unsigned integers
constraints.Complex    // complex64, complex128
```

### Tilde (~) for underlying types
```go
type MyInt int

type Signed interface {
    ~int | ~int8 | ~int16 | ~int32 | ~int64
}
// ~int includes MyInt (underlying type is int)
```

## Generic Data Types

### Generic stack
```go
type Stack[T any] struct {
    items []T
}

func (s *Stack[T]) Push(v T) {
    s.items = append(s.items, v)
}

func (s *Stack[T]) Pop() (T, bool) {
    var zero T
    if len(s.items) == 0 {
        return zero, false
    }
    n := len(s.items) - 1
    v := s.items[n]
    s.items = s.items[:n]
    return v, true
}

func (s *Stack[T]) Len() int { return len(s.items) }

// Usage
s := &Stack[int]{}
s.Push(1)
s.Push(2)
v, ok := s.Pop()   // 2, true
```

### Generic linked list
```go
type Node[T any] struct {
    Value T
    Next  *Node[T]
}

type List[T any] struct {
    Head *Node[T]
}

func (l *List[T]) Prepend(v T) {
    l.Head = &Node[T]{Value: v, Next: l.Head}
}
```

## cmp Package (Go 1.21)

```go
import "cmp"

cmp.Compare(a, b)   // -1, 0, +1 for Ordered types
cmp.Less(a, b)      // true if a < b

// Useful for custom sort
slices.SortFunc(people, func(a, b Person) int {
    return cmp.Compare(a.Age, b.Age)
})
```

## slices Package (Go 1.21)

```go
import "slices"

// Sorting
slices.Sort(s)                          // sorts in place
slices.SortFunc(s, cmp.Compare)
slices.SortStableFunc(s, compareFunc)
slices.IsSorted(s)

// Searching (binary search on sorted slice)
idx, found := slices.BinarySearch(s, target)
idx = slices.BinarySearchFunc(s, target, compareFunc)

// Searching (linear)
slices.Contains(s, v)
slices.Index(s, v)      // first index, -1 if not found
slices.IndexFunc(s, func(v T) bool { return v > 5 })

// Manipulation
slices.Reverse(s)
slices.Clone(s)         // shallow copy
slices.Compact(s)       // removes consecutive duplicates
slices.CompactFunc(s, eq)
slices.Delete(s, i, j)  // remove [i, j)
slices.Insert(s, i, v...) // insert at index i
slices.Replace(s, i, j, v...)

// Comparison
slices.Equal(a, b)
slices.EqualFunc(a, b, eq)

// Min/Max
slices.Max(s)
slices.Min(s)
slices.MaxFunc(s, cmp)
slices.MinFunc(s, cmp)
```

## maps Package (Go 1.21)

```go
import "maps"

maps.Clone(m)                // shallow copy
maps.Copy(dst, src)          // copy entries from src into dst
maps.Equal(m1, m2)           // same key-value pairs
maps.DeleteFunc(m, func(k K, v V) bool { return v == 0 })

// Iteration (Go 1.23 — range over func)
for k, v := range maps.All(m) {
    fmt.Println(k, v)
}
```

## Common Generic Patterns

### Filter
```go
func Filter[T any](s []T, keep func(T) bool) []T {
    var result []T
    for _, v := range s {
        if keep(v) {
            result = append(result, v)
        }
    }
    return result
}

evens := Filter([]int{1,2,3,4}, func(n int) bool { return n%2 == 0 })
```

### Reduce
```go
func Reduce[T, U any](s []T, init U, f func(U, T) U) U {
    acc := init
    for _, v := range s {
        acc = f(acc, v)
    }
    return acc
}

sum := Reduce([]int{1,2,3,4}, 0, func(acc, n int) int { return acc + n })
```

### Keys and Values from map
```go
func Keys[K comparable, V any](m map[K]V) []K {
    keys := make([]K, 0, len(m))
    for k := range m {
        keys = append(keys, k)
    }
    return keys
}
```

## Limitations of Go Generics

- No specialization (no per-type optimizations)
- Cannot use type parameters as function literals directly in some contexts
- No variadic type parameters
- Methods cannot have their own type parameters (only the receiver type can be generic)
- No generic type aliases (until Go 1.24)
- Interface constraints with type sets cannot be used as regular interfaces (`Number` cannot be used as `var x Number`)
