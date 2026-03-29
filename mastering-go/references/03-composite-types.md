# Ch 3 — Composite Data Types

## Maps

Maps are **reference types** — unordered key-value collections. Zero value is `nil`.

```go
// Creation
var m map[string]int          // nil map — reads OK, writes panic
m = make(map[string]int)      // ready to use
m = map[string]int{"a": 1, "b": 2}  // literal

// CRUD
m["key"] = 42                 // set
val := m["key"]               // get (zero value if missing)
val, ok := m["key"]           // ok = false if key absent
delete(m, "key")              // delete (no-op if missing)

// Iteration (order not guaranteed)
for k, v := range m {
    fmt.Printf("%s → %d\n", k, v)
}

len(m)   // number of key-value pairs
```

### maps package (Go 1.21+)
```go
import "maps"
maps.Clone(m)              // shallow copy
maps.Copy(dst, src)        // copy src into dst
maps.Delete(m, func(k, v) bool { return v == 0 })  // DeleteFunc
maps.Equal(m1, m2)
maps.Keys(m)               // iterator (Go 1.23 range-over-func)
```

### Common patterns
```go
// Default value
counts := make(map[string]int)
counts["word"]++   // zero value is 0, so this works

// Map of slices
index := make(map[string][]int)
index["a"] = append(index["a"], 1)

// Set (map[T]struct{})
seen := make(map[string]struct{})
seen["x"] = struct{}{}
_, exists := seen["x"]
```

**Key constraints:** Key type must be comparable (`==`). Slices, maps, and functions cannot be keys.

## Structs

```go
type Point struct {
    X float64
    Y float64
}

// Initialization
p1 := Point{X: 1.0, Y: 2.0}   // named fields (preferred)
p2 := Point{1.0, 2.0}          // positional (fragile)
var p3 Point                    // zero value: {0.0, 0.0}
p4 := &Point{X: 3, Y: 4}       // pointer to struct

// Access
fmt.Println(p1.X, p1.Y)
p4.X = 5                       // Go auto-dereferences: (*p4).X
```

### Methods on structs
```go
// Value receiver — does not modify
func (p Point) Distance() float64 {
    return math.Sqrt(p.X*p.X + p.Y*p.Y)
}

// Pointer receiver — can modify
func (p *Point) Scale(factor float64) {
    p.X *= factor
    p.Y *= factor
}

p := Point{3, 4}
fmt.Println(p.Distance())   // 5
p.Scale(2)                  // Go auto-takes address: (&p).Scale(2)
```

**Rule:** Use pointer receivers consistently if any method needs to mutate. Mixing causes confusion and interface satisfaction issues.

### Struct embedding (composition)
```go
type Animal struct {
    Name string
}
func (a Animal) Speak() string { return a.Name + " makes a sound" }

type Dog struct {
    Animal              // embedded (anonymous field)
    Breed string
}

d := Dog{Animal: Animal{Name: "Rex"}, Breed: "Labrador"}
fmt.Println(d.Speak())   // promoted method: d.Animal.Speak()
fmt.Println(d.Name)      // promoted field
```

### Anonymous structs
```go
p := struct {
    X, Y int
}{X: 1, Y: 2}

// Useful for one-off JSON parsing
var resp struct {
    Status int    `json:"status"`
    Data   string `json:"data"`
}
json.Unmarshal(body, &resp)
```

### Struct tags
```go
type User struct {
    Name  string `json:"name" db:"user_name"`
    Email string `json:"email,omitempty"`
    Age   int    `json:"-"`              // excluded from JSON
}
```

### Comparing structs
Structs are comparable with `==` if all fields are comparable. No pointer fields, maps, or slices in the struct.

## Regular Expressions

```go
import "regexp"

// Compile (once, at init or package level)
re := regexp.MustCompile(`\d+`)     // panics on bad pattern
re2, err := regexp.Compile(`\d+`)   // returns error

// Match
matched := re.MatchString("abc123")    // true

// Find first match
m := re.FindString("abc123def")        // "123"
loc := re.FindStringIndex("abc123")    // [3 6]

// Find all matches
all := re.FindAllString("1a2b3c", -1)  // ["1","2","3"]

// Submatch (capture groups)
re3 := regexp.MustCompile(`(\w+)@(\w+)\.(\w+)`)
groups := re3.FindStringSubmatch("user@example.com")
// groups[0]=full match, groups[1]="user", etc.

// Replace
result := re.ReplaceAllString("a1b2", "X")    // "aXbX"
result2 := re.ReplaceAllStringFunc("a1b2", func(s string) string {
    n, _ := strconv.Atoi(s)
    return strconv.Itoa(n * 2)
})

// Split
parts := re.Split("a1b2c3d", -1)   // ["a","b","c","d"]
```

### Common patterns
| Pattern | Matches |
|---------|---------|
| `\d+` | One or more digits |
| `\w+` | Word characters (a-z, A-Z, 0-9, _) |
| `\s+` | Whitespace |
| `^...$` | Start/end of string |
| `(?i)` | Case-insensitive flag |
| `[a-zA-Z]` | Character class |
| `(a\|b)` | Alternation |

## CSV Files

```go
import "encoding/csv"

// Reading
f, err := os.Open("data.csv")
if err != nil { log.Fatal(err) }
defer f.Close()

r := csv.NewReader(f)
r.FieldsPerRecord = -1   // variable fields per row
records, err := r.ReadAll()   // [][]string

// Or read row by row
for {
    record, err := r.Read()
    if err == io.EOF { break }
    if err != nil { log.Fatal(err) }
    fmt.Println(record)
}

// Writing
w := csv.NewWriter(os.Stdout)
defer w.Flush()
w.Write([]string{"Name", "Age", "City"})
w.WriteAll([][]string{{"Alice", "30", "NYC"}, {"Bob", "25", "LA"}})
if err := w.Error(); err != nil { log.Fatal(err) }
```

## JSON

```go
import "encoding/json"

// Struct → JSON (Marshal)
type Person struct {
    Name string `json:"name"`
    Age  int    `json:"age,omitempty"`
}
p := Person{Name: "Alice", Age: 30}
data, err := json.Marshal(p)         // []byte
data, err = json.MarshalIndent(p, "", "  ")  // pretty

// JSON → Struct (Unmarshal)
var p2 Person
err = json.Unmarshal(data, &p2)

// Streaming (larger payloads)
enc := json.NewEncoder(os.Stdout)
enc.SetIndent("", "  ")
enc.Encode(p)

dec := json.NewDecoder(r.Body)
dec.Decode(&p2)

// Dynamic / unknown structure
var raw interface{}
json.Unmarshal(data, &raw)
m := raw.(map[string]interface{})

// map → JSON
m2 := map[string]any{"key": "value", "n": 42}
json.Marshal(m2)
```

## Data Persistence — gob encoding

```go
import "encoding/gob"

// Write
f, _ := os.Create("data.gob")
defer f.Close()
enc := gob.NewEncoder(f)
enc.Encode(myStruct)

// Read
f2, _ := os.Open("data.gob")
defer f2.Close()
dec := gob.NewDecoder(f2)
var result MyStruct
dec.Decode(&result)
```

`gob` is Go-specific (not cross-language). Use JSON or Protocol Buffers for interoperability.

## strings Package Quick Reference

```go
import "strings"

strings.Contains("hello", "ell")       // true
strings.HasPrefix("hello", "he")       // true
strings.HasSuffix("hello", "lo")       // true
strings.Count("cheese", "e")           // 3
strings.Index("hello", "ll")           // 2, -1 if not found
strings.Replace("oink oink", "oink", "moo", 1)   // "moo oink"
strings.ReplaceAll("oink oink", "oink", "moo")    // "moo moo"
strings.ToUpper("hello")               // "HELLO"
strings.ToLower("HELLO")               // "hello"
strings.TrimSpace("  hello  ")         // "hello"
strings.Trim("!!hi!!", "!")            // "hi"
strings.Split("a,b,c", ",")           // ["a","b","c"]
strings.Join([]string{"a","b"}, "-")   // "a-b"
strings.Fields("  foo bar  baz  ")    // ["foo","bar","baz"]
strings.Repeat("na", 4)               // "nananana"
strings.EqualFold("Go", "go")         // true (case-insensitive)
```
