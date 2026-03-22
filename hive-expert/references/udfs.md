# Hive UDFs — User-Defined Functions

## Table of Contents
1. [UDF Types Overview](#udf-types-overview)
2. [Temporary vs Permanent Functions](#temporary-vs-permanent-functions)
3. [GenericUDF (Scalar UDF)](#genericudf-scalar-udf)
4. [UDAF (User-Defined Aggregate Function)](#udaf-user-defined-aggregate-function)
5. [UDTF (User-Defined Table-Generating Function)](#udtf-user-defined-table-generating-function)
6. [Hive Macros](#hive-macros)
7. [Using Python/Other Script UDFs](#using-pythonother-script-udfs)

---

## UDF Types Overview

| Type | Interface | Input | Output | Example use |
|------|-----------|-------|--------|-------------|
| UDF (simple) | `UDF` | One row | One value | `org.apache.hadoop.hive.ql.exec.UDF` |
| GenericUDF | `GenericUDF` | One row | One value | Complex types, lazy evaluation |
| UDAF | `AbstractGenericUDAFResolver` | Many rows | One value | Custom aggregations |
| UDTF | `GenericUDTF` | One row | Zero or more rows | Explode-like operations |

**Prefer GenericUDF over simple UDF** — it handles complex types, variable arguments, and lazy evaluation.

---

## Temporary vs Permanent Functions

### Temporary function (session-scoped)

```sql
-- Register JAR (HDFS or local path)
ADD JAR hdfs:///user/hive/udfs/my-udfs.jar;
ADD JAR /local/path/to/my-udfs.jar;

-- Create temporary function
CREATE TEMPORARY FUNCTION my_func
  AS 'com.example.hive.udfs.MyUDF';

-- Use it
SELECT my_func(col1, col2) FROM table;

-- Drop
DROP TEMPORARY FUNCTION my_func;
DROP TEMPORARY FUNCTION IF EXISTS my_func;
```

### Permanent function (Metastore-registered)

```sql
-- JAR must be on HDFS or in a location accessible to all HiveServer2 nodes
CREATE FUNCTION mydb.my_func
  AS 'com.example.hive.udfs.MyUDF'
  USING JAR 'hdfs:///user/hive/udfs/my-udfs.jar';

-- Can also use FILE, ARCHIVE:
CREATE FUNCTION mydb.my_func
  AS 'com.example.hive.udfs.MyUDF'
  USING JAR 'hdfs:///udfs/my-udfs.jar',
        FILE 'hdfs:///udfs/config.properties';

-- Use (qualify with db if not in current db)
SELECT mydb.my_func(col) FROM table;

-- Reload after JAR update
RELOAD (FUNCTIONS);  -- Hive 2.0+

-- Drop permanent function
DROP FUNCTION mydb.my_func;
DROP FUNCTION IF EXISTS mydb.my_func;

-- Show functions
SHOW FUNCTIONS;
SHOW FUNCTIONS LIKE 'my*';
DESCRIBE FUNCTION my_func;
DESCRIBE FUNCTION EXTENDED my_func;
```

---

## GenericUDF (Scalar UDF)

Processes one row at a time, returns one value. Most common UDF type.

### Minimal Java implementation

```java
import org.apache.hadoop.hive.ql.exec.UDFArgumentException;
import org.apache.hadoop.hive.ql.metadata.HiveException;
import org.apache.hadoop.hive.ql.udf.generic.GenericUDF;
import org.apache.hadoop.hive.serde2.objectinspector.ObjectInspector;
import org.apache.hadoop.hive.serde2.objectinspector.PrimitiveObjectInspector;
import org.apache.hadoop.hive.serde2.objectinspector.primitive.PrimitiveObjectInspectorFactory;
import org.apache.hadoop.hive.serde2.objectinspector.primitive.StringObjectInspector;

/**
 * Example: MASK_EMAIL(email STRING) → STRING
 * Replaces email domain with ***
 */
@Description(
  name = "mask_email",
  value = "_FUNC_(email) - masks the domain of an email address",
  extended = "Example: mask_email('user@example.com') returns 'user@***'"
)
public class MaskEmailUDF extends GenericUDF {

  private StringObjectInspector inputOI;

  @Override
  public ObjectInspector initialize(ObjectInspector[] arguments)
      throws UDFArgumentException {
    // Validate argument count
    if (arguments.length != 1) {
      throw new UDFArgumentException("mask_email takes exactly 1 argument");
    }
    // Validate argument type
    if (!(arguments[0] instanceof StringObjectInspector)) {
      throw new UDFArgumentException("mask_email requires a STRING argument");
    }
    this.inputOI = (StringObjectInspector) arguments[0];
    // Return type: STRING
    return PrimitiveObjectInspectorFactory.javaStringObjectInspector;
  }

  @Override
  public Object evaluate(DeferredObject[] arguments) throws HiveException {
    String email = inputOI.getPrimitiveJavaObject(arguments[0].get());
    if (email == null) return null;
    int atIndex = email.indexOf('@');
    if (atIndex < 0) return email;
    return email.substring(0, atIndex + 1) + "***";
  }

  @Override
  public String getDisplayString(String[] children) {
    return "mask_email(" + children[0] + ")";
  }
}
```

### Build and deploy

```bash
# Build JAR (Maven example)
mvn package -DskipTests

# Upload to HDFS
hdfs dfs -put target/my-udfs.jar hdfs:///user/hive/udfs/

# Register in Hive
CREATE FUNCTION mydb.mask_email
  AS 'com.example.hive.udfs.MaskEmailUDF'
  USING JAR 'hdfs:///user/hive/udfs/my-udfs.jar';
```

---

## UDAF (User-Defined Aggregate Function)

Processes multiple rows and returns one value per group. Requires a buffer (partial aggregation) class.

### UDAF structure

```java
import org.apache.hadoop.hive.ql.udf.generic.AbstractGenericUDAFResolver;
import org.apache.hadoop.hive.ql.udf.generic.GenericUDAFEvaluator;
import org.apache.hadoop.hive.serde2.objectinspector.*;
import org.apache.hadoop.hive.serde2.objectinspector.primitive.*;

/**
 * Example: GEOMETRIC_MEAN(DOUBLE) → DOUBLE
 */
@Description(name = "geometric_mean", value = "_FUNC_(x) - geometric mean of values")
public class GeometricMeanUDAF extends AbstractGenericUDAFResolver {

  @Override
  public GenericUDAFEvaluator getEvaluator(TypeInfo[] parameters) {
    return new GeometricMeanEvaluator();
  }

  public static class GeometricMeanEvaluator extends GenericUDAFEvaluator {

    // Buffer to hold partial state
    static class SumLogBuffer implements AggregationBuffer {
      double sumLog = 0.0;
      long count = 0;
    }

    private PrimitiveObjectInspector inputOI;
    private StructObjectInspector structOI;  // for partial result

    @Override
    public ObjectInspector init(Mode mode, ObjectInspector[] parameters)
        throws HiveException {
      super.init(mode, parameters);
      if (mode == Mode.PARTIAL1 || mode == Mode.COMPLETE) {
        inputOI = (PrimitiveObjectInspector) parameters[0];
      }
      // ... setup partial/final OIs
      return PrimitiveObjectInspectorFactory.javaDoubleObjectInspector;
    }

    @Override
    public AggregationBuffer getNewAggregationBuffer() {
      return new SumLogBuffer();
    }

    @Override
    public void reset(AggregationBuffer agg) {
      ((SumLogBuffer) agg).sumLog = 0.0;
      ((SumLogBuffer) agg).count = 0;
    }

    @Override
    public void iterate(AggregationBuffer agg, Object[] parameters)
        throws HiveException {
      if (parameters[0] != null) {
        double val = PrimitiveObjectInspectorUtils.getDouble(parameters[0], inputOI);
        if (val > 0) {
          ((SumLogBuffer) agg).sumLog += Math.log(val);
          ((SumLogBuffer) agg).count++;
        }
      }
    }

    @Override
    public Object terminatePartial(AggregationBuffer agg) {
      // return partial state (sumLog, count) as struct
      SumLogBuffer buf = (SumLogBuffer) agg;
      return new Object[]{buf.sumLog, buf.count};
    }

    @Override
    public void merge(AggregationBuffer agg, Object partial) {
      // merge partial state into agg buffer
      // ...
    }

    @Override
    public Object terminate(AggregationBuffer agg) {
      SumLogBuffer buf = (SumLogBuffer) agg;
      if (buf.count == 0) return null;
      return Math.exp(buf.sumLog / buf.count);
    }
  }
}
```

---

## UDTF (User-Defined Table-Generating Function)

Emits zero or more rows per input row. Used like EXPLODE in LATERAL VIEW.

### UDTF structure

```java
import org.apache.hadoop.hive.ql.udf.generic.GenericUDTF;
import org.apache.hadoop.hive.ql.exec.UDFArgumentException;
import org.apache.hadoop.hive.serde2.objectinspector.*;
import java.util.ArrayList;
import java.util.List;

/**
 * Example: SPLIT_AND_TRIM(str STRING, delim STRING) → TABLE(token STRING)
 * Splits string by delimiter and trims each token
 */
public class SplitTrimUDTF extends GenericUDTF {

  private StringObjectInspector strOI;
  private StringObjectInspector delimOI;

  @Override
  public StructObjectInspector initialize(ObjectInspector[] argOIs)
      throws UDFArgumentException {
    strOI = (StringObjectInspector) argOIs[0];
    delimOI = (StringObjectInspector) argOIs[1];

    // Define output schema: one column named "token" of type STRING
    List<String> fieldNames = new ArrayList<>();
    List<ObjectInspector> fieldOIs = new ArrayList<>();
    fieldNames.add("token");
    fieldOIs.add(PrimitiveObjectInspectorFactory.javaStringObjectInspector);
    return ObjectInspectorFactory.getStandardStructObjectInspector(fieldNames, fieldOIs);
  }

  @Override
  public void process(Object[] args) throws HiveException {
    String str = strOI.getPrimitiveJavaObject(args[0]);
    String delim = delimOI.getPrimitiveJavaObject(args[1]);
    if (str == null || delim == null) return;
    for (String token : str.split(delim, -1)) {
      forward(new Object[]{token.trim()});  // emit one row per token
    }
  }

  @Override
  public void close() {}
}
```

```sql
-- Use in LATERAL VIEW
SELECT id, token
FROM my_table
LATERAL VIEW split_trim(tags_str, ',') t AS token;
```

---

## Hive Macros

Macros are lightweight SQL-only functions — no Java required. Hive 0.12+.

```sql
-- Create macro (inline SQL expression)
CREATE TEMPORARY MACRO SIGMOID(x DOUBLE)
  1.0 / (1.0 + EXP(-x));

CREATE TEMPORARY MACRO FISCAL_YEAR(d STRING)
  IF(MONTH(d) >= 10, YEAR(d) + 1, YEAR(d));

CREATE TEMPORARY MACRO CLAMP(val DOUBLE, lo DOUBLE, hi DOUBLE)
  LEAST(GREATEST(val, lo), hi);

-- Use
SELECT SIGMOID(score) AS prob FROM predictions;
SELECT FISCAL_YEAR(order_date) AS fy FROM orders;
SELECT CLAMP(raw_score, 0.0, 1.0) FROM scores;

-- Drop
DROP TEMPORARY MACRO SIGMOID;

-- Permanent macros: use CREATE MACRO (without TEMPORARY) — Hive 3+
CREATE MACRO mydb.FISCAL_YEAR(d STRING)
  IF(MONTH(d) >= 10, YEAR(d) + 1, YEAR(d));
```

**Macro limitations:**
- Single expression only (no multi-statement logic)
- No side effects, no access to external systems
- Arguments are typed at creation time

---

## Using Python/Other Script UDFs

Python (and any language) UDFs via TRANSFORM. See `streaming.md` for full details.

```sql
-- Quick inline Python UDF via TRANSFORM
SELECT TRANSFORM(col1, col2)
  USING 'python3 -c "
import sys
for line in sys.stdin:
    a, b = line.strip().split(\"\\t\")
    print(a.upper() + \"\\t\" + str(int(b) * 2))
"'
AS (upper_col1 STRING, doubled_col2 INT)
FROM my_table;
```

### PyHive / HivePython UDF (alternative)

For complex Python logic, prefer TRANSFORM with a script file over inline Python:

```sql
ADD FILE hdfs:///user/hive/scripts/my_transform.py;

SELECT TRANSFORM(col1, col2)
  USING 'python3 my_transform.py'
AS (result STRING)
FROM my_table;
```

See `streaming.md` for full TRANSFORM documentation.
