# Ch 2 — Basic Go Data Types

## Numeric Types

### Integer types
| Type | Size | Range |
|------|------|-------|
| `int8` | 8-bit | −128 to 127 |
| `int16` | 16-bit | −32768 to 32767 |
| `int32` / `rune` | 32-bit | −2³¹ to 2³¹−1 |
| `int64` | 64-bit | −2⁶³ to 2⁶³−1 |
| `int` | platform | 32 or 64 bit |
| `uint8` / `byte` | 8-bit | 0 to 255 |
| `uint16` | 16-bit | 0 to 65535 |
| `uint32` | 32-bit | 0 to 2³²−1 |
| `uint64` | 64-bit | 0 to 2⁶⁴−1 |
| `uint` | platform | 32 or 64 bit |
| `uintptr` | platform | large enough for pointer |

Use `int` unless you have a specific reason to use a sized type. Integer literals can be written as `42`, `0x2A` (hex), `0b101010` (binary), `0o52` (octal). Underscores allowed for readability: `1_000_000`.

### Floating-point types
| Type | Size | Precision |
|------|------|-----------|
| `float32` | 32-bit | ~7 decimal digits |
| `float64` | 64-bit | ~15 decimal digits |
| `complex64` | 2×float32 | complex numbers |
| `complex128` | 2×float64 | complex numbers |

Default for untyped float literals is `float64`. Use `math.IsNaN`, `math.IsInf` to check special values.

```go
import "math"
fmt.Println(math.MaxFloat64)    // 1.7976931348623157e+308
fmt.Println(math.Pi)
x := complex(3.0, 4.0)         // 3+4i
fmt.Println(real(x), imag(x))  // 3 4
```

## Boolean

```go
var b bool          // false (zero value)
b = true
b = x > 0 && y < 10
```

No implicit conversion from int to bool. `if 1` is a compile error in Go.

## Strings

Strings are **immutable byte slices** encoded in UTF-8.

```go
s := "Hello, 世界"
len(s)                  // byte length (not rune count!)
utf8.RuneCountInString(s)  // rune (character) count

// Iterate bytes
for i := 0; i < len(s); i++ {
    fmt.Printf("%x ", s[i])
}

// Iterate runes (Unicode code points)
for i, r := range s {
    fmt.Printf("%d: %c\n", i, r)
}

// String concatenation
s2 := s + " more"       // creates new string (immutable)
// Efficient building: use strings.Builder
var sb strings.Builder
sb.WriteString("hello")
sb.WriteByte(' ')
sb.WriteRune('世')
result := sb.String()
```

### String conversion
```go
b := []byte("hello")    // string → []byte
s := string(b)          // []byte → string
r := []rune("hello")    // string → []rune
s2 := string(r)         // []rune → string

// Numeric conversions (strconv package)
import "strconv"
n, err := strconv.Atoi("42")        // string → int
s := strconv.Itoa(42)               // int → string
f, err := strconv.ParseFloat("3.14", 64)
i, err := strconv.ParseInt("FF", 16, 64)  // hex string → int64
```

### rune type (alias for int32)
```go
var r rune = 'A'        // Unicode code point
r2 := '世'              // multi-byte rune
fmt.Printf("%c %d\n", r, r)   // A 65
```

## Arrays

Fixed-size, value type (copied on assignment).

```go
var a [5]int                    // [0 0 0 0 0]
a[0] = 42
b := [3]string{"foo", "bar", "baz"}
c := [...]int{1, 2, 3, 4}      // compiler counts: [4]int

// 2D array
matrix := [3][3]int{{1,2,3},{4,5,6},{7,8,9}}

len(a)   // 5 (compile-time constant for arrays)
```

Arrays are comparable with `==` if element type is comparable.

## Slices

Slices are the primary sequence type — a reference to an underlying array.

```go
// Creation
var s []int                      // nil slice (len=0, cap=0)
s = []int{}                      // empty non-nil slice
s = make([]int, 5)               // len=5, cap=5, all zeros
s = make([]int, 3, 10)           // len=3, cap=10

// Literal
s := []string{"a", "b", "c"}

// From array
arr := [5]int{1,2,3,4,5}
sl := arr[1:3]  // [2 3], shares underlying array

// Append
s = append(s, 1)
s = append(s, 2, 3, 4)
s = append(s, other...)   // append another slice

// Copy (independent)
dst := make([]int, len(src))
copy(dst, src)
```

### Slice header (3 fields)
```
ptr → underlying array
len  (number of elements)
cap  (capacity from ptr to end of underlying array)
```

### Slice operations
```go
s[low:high]         // elements [low, high)
s[low:high:max]     // also sets cap = max−low (3-index slicing)
s[:3]               // first 3
s[2:]               // from index 2 to end
s[:]                // entire slice
len(s), cap(s)
```

### Deleting elements
```go
// Delete index i (preserving order)
s = append(s[:i], s[i+1:]...)

// Delete index i (unordered, faster)
s[i] = s[len(s)-1]
s = s[:len(s)-1]
```

### slices package (Go 1.21+)
```go
import "slices"
slices.Sort(s)
slices.Contains(s, val)
slices.Index(s, val)        // -1 if not found
slices.Reverse(s)
slices.Max(s)
slices.Min(s)
slices.Equal(a, b)
```

## Pointers

```go
x := 42
p := &x             // p is *int, p holds address of x
fmt.Println(*p)     // dereference: prints 42
*p = 100            // modifies x through pointer
fmt.Println(x)      // 100

// new() allocates zeroed value, returns pointer
p2 := new(int)      // *int pointing to 0
*p2 = 7
```

Go has no pointer arithmetic. Use slices instead.

**When to use pointers:**
1. To mutate a value in a function
2. For large structs (avoid copying)
3. When `nil` needs to represent "not set"
4. Interface satisfaction with pointer receivers

## Constants and iota

```go
const Pi = 3.14159
const (
    StatusOK    = 200
    StatusNotFound = 404
)

// iota — increments per ConstSpec
type Weekday int
const (
    Sunday Weekday = iota   // 0
    Monday                  // 1
    Tuesday                 // 2
    Wednesday
    Thursday
    Friday
    Saturday
)

// iota expressions
const (
    _  = iota             // skip 0
    KB = 1 << (10 * iota) // 1024
    MB                    // 1048576
    GB                    // 1073741824
)
```

Untyped constants have arbitrary precision and are compatible with any type of appropriate kind.

## Dates and Times

```go
import "time"

now := time.Now()                         // current local time
t := time.Date(2024, time.March, 15, 10, 30, 0, 0, time.UTC)

// Formatting — reference time: Mon Jan 2 15:04:05 MST 2006
fmt.Println(now.Format("2006-01-02 15:04:05"))
fmt.Println(now.Format(time.RFC3339))

// Parsing
t, err := time.Parse("2006-01-02", "2024-03-15")
t2, err := time.Parse(time.RFC3339, "2024-03-15T10:30:00Z")

// Arithmetic
d := 24 * time.Hour
tomorrow := now.Add(d)
diff := t2.Sub(t)        // time.Duration

// Duration constants
time.Second, time.Minute, time.Hour
time.Sleep(500 * time.Millisecond)

// Unix timestamps
ts := now.Unix()            // seconds since epoch
ts_ms := now.UnixMilli()   // milliseconds (Go 1.17+)
t3 := time.Unix(ts, 0)
```

## Random Numbers

```go
import "math/rand/v2"  // Go 1.22+ (preferred)

n := rand.IntN(100)    // [0, 100)
f := rand.Float64()    // [0.0, 1.0)

// Old API (math/rand) — requires seeding before Go 1.20
import "math/rand"
rand.Seed(time.Now().UnixNano())  // deprecated in 1.20+
n := rand.Intn(100)
```

## Type Conversions

No implicit conversions — always explicit:
```go
var i int = 42
var f float64 = float64(i)
var u uint = uint(f)
var b byte = byte(i)
s := string(rune(65))   // "A" — not fmt.Sprintf
```
