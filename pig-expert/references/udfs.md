# Writing UDFs
_Ch. 7–8 of "Programming Pig" — Python UDFs (modern preferred), Java UDFs, Eval/Filter/Aggregate/LoadFunc_

## UDF Types

| Type | Interface | Use Case |
|------|-----------|----------|
| **EvalFunc** | `EvalFunc<T>` | Transform or compute a value per tuple |
| **FilterFunc** | `FilterFunc` | Return boolean; use in FILTER |
| **AccumulatorFunc** | `AccumulatorFunc<T>` | Accumulate over a bag; lower memory than EvalFunc |
| **AlgebraicFunc** | `EvalFunc` + `Algebraic` | Decomposable aggregations (SUM, COUNT-style); uses combiner |
| **LoadFunc** | `LoadFunc` | Custom input format |
| **StoreFunc** | `StoreFunc` | Custom output format |

## Python UDFs (Recommended for Most Cases)

Python UDFs are the easiest to write and deploy — no compilation, no JAR management.

### Basic Python UDF

```python
# File: myudfs.py
import re

@outputSchema("normalized:chararray")
def normalize_name(name):
    """Lowercase, strip whitespace, remove special chars."""
    if name is None:
        return None
    return re.sub(r'[^a-z0-9_]', '_', name.lower().strip())

@outputSchema("score:float")
def weighted_score(base, weight):
    if base is None or weight is None:
        return None
    return float(base) * float(weight)

# Return a tuple
@outputSchema("result:(lower:chararray, length:int)")
def analyze_string(s):
    if s is None:
        return (None, 0)
    return (s.lower(), len(s))

# Return a bag of tuples
@outputSchema("tokens:bag{t:(token:chararray)}")
def tokenize(text):
    if text is None:
        return []
    return [(word,) for word in text.lower().split()]
```

### Register and Use Python UDFs

```pig
-- Register the Python file
REGISTER 'myudfs.py' USING streaming_python AS mylib;
-- Or for Jython:
REGISTER 'myudfs.py' USING jython AS mylib;

-- Use
result = FOREACH data GENERATE
    id,
    mylib.normalize_name(name)    AS norm_name,
    mylib.weighted_score(score, 1.5) AS adj_score;
```

### Deploy Python UDF to Cloud

```bash
# Upload to S3 (EMR)
aws s3 cp myudfs.py s3://bucket/pig-libs/myudfs.py

# In script:
REGISTER 's3://bucket/pig-libs/myudfs.py' USING streaming_python AS mylib;

# Upload to GCS (Dataproc)
gsutil cp myudfs.py gs://bucket/pig-libs/myudfs.py

# In script:
REGISTER 'gs://bucket/pig-libs/myudfs.py' USING streaming_python AS mylib;
```

**Note:** `streaming_python` uses CPython via stdin/stdout serialization. `jython` runs inside the JVM. `streaming_python` is generally faster for CPU-bound work; `jython` avoids process-launch overhead for very high call rates.

## Java UDFs

Use Java for performance-critical UDFs or when you need access to Hadoop/Pig APIs directly.

### Simple EvalFunc (Java)

```java
package com.example.udfs;

import org.apache.pig.EvalFunc;
import org.apache.pig.data.Tuple;
import org.apache.pig.impl.util.WrappedIOException;
import java.io.IOException;

public class NormalizeString extends EvalFunc<String> {
    @Override
    public String exec(Tuple input) throws IOException {
        if (input == null || input.size() == 0) return null;
        String val = (String) input.get(0);
        if (val == null) return null;
        return val.toLowerCase().trim().replaceAll("[^a-z0-9_]", "_");
    }
}
```

### FilterFunc (Java)

```java
public class IsValid extends FilterFunc {
    @Override
    public Boolean exec(Tuple input) throws IOException {
        if (input == null || input.size() == 0) return false;
        String val = (String) input.get(0);
        return val != null && !val.isEmpty();
    }
}
```

### Algebraic UDF (uses combiner — efficient for large aggregations)

```java
public class SafeSum extends EvalFunc<Double> implements Algebraic {
    // Initial: applied at map phase
    public static class Initial extends EvalFunc<Tuple> {
        public Tuple exec(Tuple input) throws IOException {
            // input: bag of values
            DataBag bag = (DataBag) input.get(0);
            double sum = 0.0;
            for (Tuple t : bag) {
                if (t.get(0) != null) sum += ((Number) t.get(0)).doubleValue();
            }
            return TupleFactory.getInstance().newTuple(sum);
        }
    }
    // Intermed: applied at combiner/reduce
    public static class Intermed extends EvalFunc<Tuple> { /* same as Initial */ }
    // Final: applied at reduce
    public static class Final extends EvalFunc<Double> {
        public Double exec(Tuple input) throws IOException {
            DataBag bag = (DataBag) input.get(0);
            double sum = 0.0;
            for (Tuple t : bag) {
                if (t.get(0) != null) sum += ((Number) t.get(0)).doubleValue();
            }
            return sum;
        }
    }
    public String getInitial()  { return Initial.class.getName(); }
    public String getIntermed() { return Intermed.class.getName(); }
    public String getFinal()    { return Final.class.getName(); }
    public Double exec(Tuple input) throws IOException { /* full bag */ }
}
```

### Build and Deploy Java UDF

```bash
# Build with Maven
mvn package -DskipTests

# Upload to S3
aws s3 cp target/myudfs-1.0.jar s3://bucket/pig-libs/myudfs-1.0.jar

# Upload to GCS
gsutil cp target/myudfs-1.0.jar gs://bucket/pig-libs/myudfs-1.0.jar
```

```pig
-- Register and use
REGISTER 's3://bucket/pig-libs/myudfs-1.0.jar';
DEFINE Normalize com.example.udfs.NormalizeString();
DEFINE IsValid   com.example.udfs.IsValid();

cleaned = FILTER data BY IsValid(name);
result  = FOREACH cleaned GENERATE id, Normalize(name) AS norm_name;
```

## Accumulator UDF (memory-efficient for large bags)

```java
public class TopN extends EvalFunc<DataBag> implements Accumulator<DataBag> {
    private int n;
    private PriorityQueue<Tuple> heap;

    public TopN(String n) { this.n = Integer.parseInt(n); }

    public void accumulate(Tuple input) throws IOException {
        DataBag bag = (DataBag) input.get(0);
        for (Tuple t : bag) {
            heap.offer(t);
            if (heap.size() > n) heap.poll();
        }
    }
    public DataBag getValue() {
        DataBag result = BagFactory.getInstance().newDefaultBag();
        heap.forEach(result::add);
        return result;
    }
    public void cleanup() { heap = new PriorityQueue<>(n + 1, comparator); }
    public DataBag exec(Tuple input) throws IOException { /* not used */ return null; }
}
```

## Piggybank UDFs — Useful Built-ins

Piggybank ships many ready-to-use UDFs. Register first:

```pig
REGISTER '/usr/lib/pig/piggybank.jar';
-- or REGISTER 's3://bucket/libs/piggybank-0.17.0.jar';
```

| UDF | Package | Purpose |
|-----|---------|---------|
| `UPPER` / `LOWER` | `piggybank.evaluation.string` | String case (also built-in) |
| `TRIM` | `piggybank.evaluation.string` | Trim whitespace |
| `REGEX_EXTRACT` | `piggybank.evaluation.string` | Regex capture group |
| `STRSPLIT` | `piggybank.evaluation.string` | Split string to tuple |
| `SafeDivide` | `piggybank.evaluation.math` | Division without zero errors |
| `MD5` / `SHA256` | `piggybank.evaluation.string` | Hash functions |
| `DateExtractor` | `piggybank.evaluation.datetime` | Extract date parts |
| `CSVExcelStorage` | `piggybank.storage` | CSV with quote handling |
| `AvroStorage` | `piggybank.storage.avro` | Avro load/store |
| `MultiStorage` | `piggybank.storage` | Dynamic output partitioning |

### MultiStorage (Dynamic Output Partitioning)

```pig
DEFINE MultiStorage org.apache.pig.piggybank.storage.MultiStorage;

-- Writes output to subdirectories based on field value
-- Arg 0: base output path
-- Arg 1: field index to partition by (0-based)
STORE result INTO 's3://bucket/output/' USING MultiStorage('s3://bucket/output/', '2');
-- Creates: s3://bucket/output/US/, s3://bucket/output/UK/, etc.
```

## UDF Best Practices

1. **Python first:** Write in Python unless you need combiner (Algebraic), low-latency startup, or complex Hadoop integration.
2. **Handle nulls:** Always check for `None`/`null` — Pig propagates nulls aggressively.
3. **Declare output schema:** Use `@outputSchema` in Python; override `outputSchema()` in Java. Missing schemas cause type issues downstream.
4. **Use Algebraic when possible:** For aggregation UDFs, implementing `Algebraic` enables the combiner and dramatically reduces data sent to reducers.
5. **Avoid side effects:** UDFs may be called multiple times due to ILLUSTRATE or retries.
6. **Test locally:** `pig -x local` with small data before submitting to cluster.
