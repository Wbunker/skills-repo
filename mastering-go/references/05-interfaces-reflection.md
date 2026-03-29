# Ch 5 — Reflection and Interfaces

## Interfaces

An interface is a set of method signatures. A type implements an interface implicitly — no `implements` keyword.

```go
type Animal interface {
    Speak() string
    Move()
}

type Dog struct{ Name string }
func (d Dog) Speak() string { return "Woof" }
func (d Dog) Move()         { fmt.Println(d.Name, "runs") }

type Cat struct{}
func (c Cat) Speak() string { return "Meow" }
func (c Cat) Move()         { fmt.Println("Cat slinks") }

// Any type satisfying Animal interface works
var a Animal = Dog{Name: "Rex"}
a.Speak()   // "Woof"
a = Cat{}
a.Speak()   // "Meow"
```

### Interface composition
```go
type Reader interface {
    Read(p []byte) (n int, err error)
}
type Writer interface {
    Write(p []byte) (n int, err error)
}
type ReadWriter interface {
    Reader
    Writer
}
```

### Empty interface (any)
```go
var x any = 42
x = "hello"
x = []int{1, 2, 3}

func PrintAny(v any) {
    fmt.Printf("%T: %v\n", v, v)
}
```

### Interface nil trap
```go
var p *Dog = nil
var a Animal = p    // a is NOT nil! (has type info, nil value)
fmt.Println(a == nil)  // false — common bug

// To check: use reflect or typed nil comparison
if a != nil {
    // a.Speak() may still panic if underlying value is nil
}
```

## Type Assertions

```go
var a Animal = Dog{Name: "Rex"}

// Assertion (panics if wrong type)
d := a.(Dog)
fmt.Println(d.Name)   // "Rex"

// Safe assertion
d, ok := a.(Dog)
if ok {
    fmt.Println("It's a dog:", d.Name)
}
```

## Type Switches

```go
func describe(i interface{}) {
    switch v := i.(type) {
    case int:
        fmt.Printf("int: %d\n", v)
    case string:
        fmt.Printf("string: %s\n", v)
    case bool:
        fmt.Printf("bool: %t\n", v)
    case []int:
        fmt.Printf("[]int with %d elements\n", len(v))
    case nil:
        fmt.Println("nil")
    default:
        fmt.Printf("unknown type: %T\n", v)
    }
}
```

## sort.Interface

```go
import "sort"

type ByAge []Person
func (a ByAge) Len() int           { return len(a) }
func (a ByAge) Less(i, j int) bool { return a[i].Age < a[j].Age }
func (a ByAge) Swap(i, j int)      { a[i], a[j] = a[j], a[i] }

people := []Person{{"Alice", 30}, {"Bob", 25}}
sort.Sort(ByAge(people))

// Simpler: sort.Slice (no interface needed)
sort.Slice(people, func(i, j int) bool {
    return people[i].Age < people[j].Age
})
sort.SliceStable(people, func(i, j int) bool {
    return people[i].Name < people[j].Name
})

// Check if sorted
sort.IntsAreSorted([]int{1,2,3})  // true
sort.StringsAreSorted([]string{"a","b","c"})
```

## Important Standard Interfaces

```go
// Stringer — controls fmt output
type Stringer interface {
    String() string
}
func (p Point) String() string { return fmt.Sprintf("(%g, %g)", p.X, p.Y) }

// error
type error interface {
    Error() string
}

// io.Reader / io.Writer
type Reader interface {
    Read(p []byte) (n int, err error)
}
type Writer interface {
    Write(p []byte) (n int, err error)
}

// io.Closer
type Closer interface {
    Close() error
}

// fmt.Formatter — custom formatting verb
type Formatter interface {
    Format(f State, verb rune)
}
```

## Reflection

The `reflect` package allows inspecting types and values at runtime. Use sparingly — it's slow and bypasses type safety.

```go
import "reflect"

x := 42
t := reflect.TypeOf(x)    // reflect.Type
v := reflect.ValueOf(x)   // reflect.Value

fmt.Println(t.Name())      // "int"
fmt.Println(t.Kind())      // reflect.Int
fmt.Println(v.Int())       // 42
```

### reflect.Kind constants
```
Bool, Int, Int8, Int16, Int32, Int64
Uint, Uint8, Uint16, Uint32, Uint64, Uintptr
Float32, Float64, Complex64, Complex128
Array, Chan, Func, Interface, Map, Pointer, Slice, String, Struct
```

### Inspecting structs
```go
type Person struct {
    Name string `json:"name"`
    Age  int    `json:"age"`
}

p := Person{"Alice", 30}
t := reflect.TypeOf(p)
v := reflect.ValueOf(p)

for i := 0; i < t.NumField(); i++ {
    field := t.Field(i)         // reflect.StructField
    value := v.Field(i)         // reflect.Value
    tag := field.Tag.Get("json")
    fmt.Printf("%s (%s) [%s] = %v\n", field.Name, field.Type, tag, value)
}
```

### Modifying values via reflection
```go
p := &Person{"Alice", 30}
v := reflect.ValueOf(p).Elem()   // Elem() to dereference pointer

nameField := v.FieldByName("Name")
if nameField.CanSet() {
    nameField.SetString("Bob")
}
```

### Calling functions via reflection
```go
fn := reflect.ValueOf(fmt.Println)
args := []reflect.Value{reflect.ValueOf("hello")}
fn.Call(args)
```

### Checking interface implementation at compile time
```go
// Compile-time check: *MyType must implement io.Writer
var _ io.Writer = (*MyType)(nil)
```

## Pointer vs Value Receivers — Interface Satisfaction

```go
type Animal interface{ Speak() string }

type Dog struct{}
func (d *Dog) Speak() string { return "Woof" }  // pointer receiver

var a Animal = &Dog{}   // OK — *Dog has Speak
// var a Animal = Dog{} // COMPILE ERROR — Dog does not have Speak

// Value receiver — both pointer and value satisfy the interface
type Cat struct{}
func (c Cat) Speak() string { return "Meow" }

var b Animal = Cat{}    // OK
var c Animal = &Cat{}   // Also OK
```

Rule: If method set of `T` satisfies interface, `*T` also satisfies it. The reverse is NOT true.
