# Relational Operators
_Ch. 4 of "Programming Pig" — GROUP, JOIN, COGROUP, UNION, DISTINCT, ORDER, LIMIT, SAMPLE_

## GROUP BY

```pig
-- Group by single field
grouped = GROUP events BY user_id;
-- Schema: {group: int, events: {(user_id:int, ...)}}

-- Group by multiple fields
multi = GROUP events BY (user_id, date);
-- group is a tuple: {group: (user_id:int, date:chararray), ...}

-- Group ALL (produces single bag of entire relation)
all_data = GROUP events ALL;
total = FOREACH all_data GENERATE COUNT(events) AS total_count;
```

### Aggregate After GROUP

```pig
stats = FOREACH grouped GENERATE
    group            AS user_id,
    COUNT(events)    AS event_count,
    SUM(events.amount) AS total_amount,
    AVG(events.amount) AS avg_amount,
    MAX(events.amount) AS max_amount,
    MIN(events.score)  AS min_score;
```

### Nested FOREACH After GROUP

```pig
-- Filter within a bag before aggregating
result = FOREACH grouped {
    paid = FILTER events BY status == 'paid';
    GENERATE group AS user_id,
             COUNT(paid) AS paid_count,
             SUM(paid.amount) AS paid_total;
};
```

## JOIN (Default — Hash Join)

```pig
-- Inner join (default)
joined = JOIN orders BY user_id, users BY id;

-- Multi-key join
joined = JOIN a BY (city, state), b BY (city, state);

-- Left outer join
left = JOIN orders BY user_id LEFT OUTER, users BY id;

-- Right outer join
right = JOIN orders BY user_id RIGHT OUTER, users BY id;

-- Full outer join
full = JOIN a BY key FULL OUTER, b BY key;

-- After join, field names are prefixed with relation alias
-- orders::user_id, users::id
result = FOREACH joined GENERATE orders::id, users::name, orders::amount;
```

## JOIN Variants (Performance)

```pig
-- Replicated join: broadcast small relation to all mappers (map-only job)
-- REQUIRES: small relation fits in memory (~100MB guideline)
fast = JOIN large BY key, small BY key USING 'replicated';
-- small relation must be listed LAST

-- Skewed join: handles hot keys by sampling and splitting
skewed = JOIN a BY key, b BY key USING 'skewed';

-- Merge join: map-only, requires both inputs sorted and indexed on join key
merged = JOIN a BY key, b BY key USING 'merge';
-- Useful when inputs come from a prior ORDER BY + STORE

-- Merge-sparse join: for sparse keys in sorted inputs
sparse = JOIN a BY key, b BY key USING 'merge-sparse';
```

## COGROUP

```pig
-- COGROUP: like GROUP, but for multiple relations simultaneously
-- Produces one bag per input relation per group key
cogrouped = COGROUP orders BY user_id, returns BY user_id;
-- Schema: {group:int, orders:{(...)}, returns:{(...)}}

result = FOREACH cogrouped GENERATE
    group                  AS user_id,
    COUNT(orders)          AS order_count,
    COUNT(returns)         AS return_count,
    SUM(orders.amount)     AS order_total,
    SUM(returns.amount)    AS return_total;

-- Simulate LEFT OUTER JOIN with COGROUP:
left_result = FOREACH cogrouped {
    GENERATE group AS user_id,
             orders, returns;
};
-- Then FILTER where returns is empty
```

## CROSS (Cartesian Product)

```pig
-- Use sparingly — O(n*m) output
-- Avoid on large datasets
cross_product = CROSS a, b;
-- Useful for small reference tables
```

## UNION

```pig
-- Combine two relations with compatible schemas
combined = UNION daily_jan, daily_feb;

-- UNION ONSCHEMA: aligns fields by name, fills missing with null (Pig 0.12+)
flexible = UNION ONSCHEMA table_v1, table_v2;
```

## DISTINCT

```pig
-- Remove duplicate tuples
unique_users = DISTINCT user_ids;

-- Distinct projection
distinct_combos = DISTINCT (FOREACH data GENERATE user_id, category);
```

## ORDER BY

```pig
-- Sort ascending (default)
sorted = ORDER result BY score;

-- Sort descending
desc_sorted = ORDER result BY score DESC;

-- Multi-key sort
multi_sort = ORDER result BY date ASC, score DESC;

-- Parallel reducers for sort (override default_parallel for this step)
sorted = ORDER result BY score PARALLEL 10;
```

## LIMIT

```pig
-- Take first N records (non-deterministic order unless preceded by ORDER)
sample = LIMIT data 100;

-- Top 10 pattern
top10 = LIMIT (ORDER data BY score DESC) 10;
```

## SAMPLE

```pig
-- Probabilistic sample (each record kept with probability p)
sampled = SAMPLE data 0.01;  -- ~1% sample
-- Non-deterministic; does not guarantee exact count
```

## SPLIT

```pig
-- Route records into multiple output relations based on condition
SPLIT data INTO
    high_value IF amount > 1000.0,
    mid_value  IF amount > 100.0 AND amount <= 1000.0,
    low_value  IF amount <= 100.0;

-- Records not matching any condition are dropped
-- A record can match multiple branches (appears in each)
```

## RANK (Pig 0.12+)

```pig
-- Assign rank to records (requires ORDER first)
ranked = RANK sorted;
-- Adds field: rank_sorted (long, 1-based)

-- Dense rank (no gaps for ties)
dense = RANK sorted DENSE;
```

## FOREACH with Multiple Inputs (Bag Operations)

```pig
-- After GROUP, operate on the bag inside FOREACH
detailed = FOREACH grouped {
    sorted_bag = ORDER events BY timestamp;
    top3       = LIMIT sorted_bag 3;
    GENERATE group AS user_id, top3 AS recent_events;
};
```

## Common Patterns

### Count Distinct

```pig
-- Pig lacks native COUNT(DISTINCT ...) — use nested approach
by_user = GROUP events BY user_id;
distinct_cats = FOREACH by_user {
    cats = events.category;
    unique = DISTINCT cats;
    GENERATE group AS user_id, COUNT(unique) AS distinct_categories;
};
```

### Top-N Per Group

```pig
by_user = GROUP events BY user_id;
top3_per_user = FOREACH by_user {
    sorted = ORDER events BY score DESC;
    top3 = LIMIT sorted 3;
    GENERATE group AS user_id, top3 AS top_events;
};
```

### Self-Join

```pig
-- Alias the same relation twice
a = LOAD 'path/' AS (...);
b = a;
self = JOIN a BY key, b BY key;
```
