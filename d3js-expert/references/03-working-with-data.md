# Working with Data

Reference for loading data, scales, axes, and data transformation in D3.

## Table of Contents
- [Loading Data](#loading-data)
- [Data Transformation](#data-transformation)
- [Scales](#scales)
- [Axes](#axes)
- [Color Scales](#color-scales)
- [Time Scales](#time-scales)
- [Number and Date Formatting](#number-and-date-formatting)

## Loading Data

D3 v7 uses promise-based data loading:

### CSV
```js
// Basic CSV loading (all values are strings by default)
const data = await d3.csv("data.csv");

// With row accessor to parse types
const data = await d3.csv("data.csv", d => ({
  name: d.name,
  value: +d.value,           // convert to number
  date: new Date(d.date),    // convert to Date
  active: d.active === "true" // convert to boolean
}));
```

### JSON
```js
const data = await d3.json("data.json");
```

### TSV
```js
const data = await d3.tsv("data.tsv", d => ({
  category: d.category,
  count: +d.count
}));
```

### Multiple Files
```js
const [cities, connections] = await Promise.all([
  d3.csv("cities.csv", d => ({ ...d, pop: +d.pop })),
  d3.json("connections.json")
]);
```

### Error Handling
```js
try {
  const data = await d3.csv("data.csv");
} catch (error) {
  console.error("Failed to load data:", error);
}
```

## Data Transformation

### d3-array Utilities
```js
import { min, max, extent, sum, mean, median, group, rollup,
         ascending, descending, bisect, pairs, range, ticks } from "d3-array";

const values = [3, 1, 4, 1, 5, 9, 2, 6];

d3.min(values);                    // 1
d3.max(values);                    // 9
d3.extent(values);                 // [1, 9]
d3.sum(values);                    // 31
d3.mean(values);                   // 3.875
d3.median(values);                 // 3.5
d3.range(0, 10, 2);                // [0, 2, 4, 6, 8]

// With accessor functions (for arrays of objects)
d3.max(data, d => d.value);
d3.extent(data, d => d.date);
```

### Grouping and Rolling Up
```js
const data = [
  { region: "East", product: "A", sales: 100 },
  { region: "East", product: "B", sales: 200 },
  { region: "West", product: "A", sales: 150 },
  { region: "West", product: "B", sales: 300 }
];

// Group: returns Map of key → array
const byRegion = d3.group(data, d => d.region);
// Map { "East" => [{...}, {...}], "West" => [{...}, {...}] }

// Multi-level grouping
const byRegionProduct = d3.group(data, d => d.region, d => d.product);

// Rollup: aggregate grouped data
const totalByRegion = d3.rollup(data, v => d3.sum(v, d => d.sales), d => d.region);
// Map { "East" => 300, "West" => 450 }

// Index: unique key lookup
const indexed = d3.index(data, d => d.product, d => d.region);
```

### Sorting
```js
data.sort((a, b) => d3.ascending(a.value, b.value));
data.sort((a, b) => d3.descending(a.value, b.value));
```

## Scales

Scales are functions that map from a **domain** (data space) to a **range** (visual space).

### Linear Scale
```js
const xScale = d3.scaleLinear()
  .domain([0, d3.max(data, d => d.value)])  // data extent
  .range([0, width]);                         // pixel extent

xScale(50);   // returns pixel position for value 50
xScale.invert(300); // returns data value for pixel 300
```

**Common options:**
```js
scale.nice();            // round domain to nice values
scale.clamp(true);       // clamp output to range
scale.ticks(5);          // suggest ~5 tick values
scale.tickFormat(5, "s"); // SI-prefix format for ticks
```

### Band Scale (categorical, for bar charts)
```js
const xScale = d3.scaleBand()
  .domain(data.map(d => d.category))  // array of categories
  .range([0, width])
  .padding(0.2);          // gap between bands (0-1)

xScale("A");              // left edge of band "A"
xScale.bandwidth();       // width of each band
```

### Ordinal Scale
```js
const colorScale = d3.scaleOrdinal()
  .domain(["A", "B", "C"])
  .range(["#e41a1c", "#377eb8", "#4daf4a"]);

// Or use built-in color schemes
const colorScale = d3.scaleOrdinal(d3.schemeCategory10);
```

### Point Scale
```js
const xScale = d3.scalePoint()
  .domain(["Mon", "Tue", "Wed", "Thu", "Fri"])
  .range([0, width])
  .padding(0.5);
```

### Power and Log Scales
```js
// Square root scale (common for area encoding)
const rScale = d3.scaleSqrt()
  .domain([0, d3.max(data, d => d.population)])
  .range([2, 30]);

// Log scale
const yScale = d3.scaleLog()
  .domain([1, 1000000])
  .range([height, 0]);
```

### Quantize and Quantile Scales (for choropleth maps)
```js
// Quantize: equal-interval bins
const colorScale = d3.scaleQuantize()
  .domain([0, 100])
  .range(d3.schemeBlues[5]);  // 5 color buckets

// Quantile: equal-count bins
const colorScale = d3.scaleQuantile()
  .domain(data.map(d => d.value))
  .range(d3.schemeBlues[5]);

// Threshold: custom breakpoints
const colorScale = d3.scaleThreshold()
  .domain([10, 50, 100])
  .range(["green", "yellow", "orange", "red"]);
```

## Axes

### Creating Axes
```js
const xAxis = d3.axisBottom(xScale);  // ticks below line
const yAxis = d3.axisLeft(yScale);    // ticks left of line

// Render axes
svg.append("g")
  .attr("transform", `translate(0, ${height})`)
  .call(xAxis);

svg.append("g")
  .call(yAxis);
```

### Axis Variants
```js
d3.axisTop(scale);     // ticks above line
d3.axisRight(scale);   // ticks right of line
d3.axisBottom(scale);  // ticks below line (most common for x)
d3.axisLeft(scale);    // ticks left of line (most common for y)
```

### Customizing Axes
```js
const xAxis = d3.axisBottom(xScale)
  .ticks(5)                           // approximate number of ticks
  .tickValues([0, 25, 50, 75, 100])   // explicit tick values
  .tickFormat(d3.format(",.0f"))      // number format
  .tickSize(-height)                  // grid lines (negative = extend up)
  .tickSizeOuter(0)                   // remove outer ticks
  .tickPadding(10);                   // space between tick and label
```

### Styling Axes with CSS
```css
.tick line {
  stroke: #ddd;
}
.tick text {
  font-size: 12px;
  fill: #666;
}
.domain {
  stroke: #999;
}
```

### Updating Axes (with transition)
```js
svg.select(".x-axis")
  .transition()
  .duration(750)
  .call(xAxis);
```

### Axis Labels
```js
// X-axis label
svg.append("text")
  .attr("x", width / 2)
  .attr("y", height + margin.bottom - 5)
  .attr("text-anchor", "middle")
  .text("Year");

// Y-axis label (rotated)
svg.append("text")
  .attr("transform", "rotate(-90)")
  .attr("x", -height / 2)
  .attr("y", -margin.left + 15)
  .attr("text-anchor", "middle")
  .text("Revenue ($)");
```

## Color Scales

### Sequential (single-hue)
```js
const color = d3.scaleSequential(d3.interpolateBlues)
  .domain([0, maxValue]);
```

### Sequential (multi-hue)
```js
d3.interpolateViridis    // perceptually uniform, colorblind-safe
d3.interpolatePlasma
d3.interpolateInferno
d3.interpolateTurbo
d3.interpolateWarm
d3.interpolateCool
```

### Diverging
```js
const color = d3.scaleDiverging(d3.interpolateRdBu)
  .domain([minValue, 0, maxValue]);  // 3-value domain (min, mid, max)
```

### Categorical Schemes
```js
d3.schemeCategory10      // 10 distinct colors
d3.schemeSet1            // 9 colors
d3.schemeSet2            // 8 colors
d3.schemePaired          // 12 paired colors
d3.schemeTableau10       // Tableau's 10 colors
```

## Time Scales

```js
const xScale = d3.scaleTime()
  .domain(d3.extent(data, d => d.date))
  .range([0, width]);

// With nice rounding
xScale.nice(d3.timeMonth);

// Custom tick intervals
const xAxis = d3.axisBottom(xScale)
  .ticks(d3.timeMonth.every(3))         // every 3 months
  .tickFormat(d3.timeFormat("%b %Y"));  // "Jan 2024"
```

### UTC variant
```js
const xScale = d3.scaleUtc()
  .domain(d3.extent(data, d => d.date))
  .range([0, width]);
```

## Number and Date Formatting

### Number Formatting
```js
d3.format(",")           // thousands separator: "1,234,567"
d3.format(",.2f")        // fixed 2 decimals: "1,234.57"
d3.format(".2s")         // SI prefix: "1.2M"
d3.format("$,.2f")       // currency: "$1,234.57"
d3.format(".0%")         // percent: "42%"
d3.format("+.1f")        // signed: "+3.1" or "-3.1"
```

### Date Formatting
```js
d3.timeFormat("%Y-%m-%d")     // "2024-03-15"
d3.timeFormat("%b %d, %Y")   // "Mar 15, 2024"
d3.timeFormat("%B %Y")       // "March 2024"
d3.timeFormat("%I:%M %p")    // "02:30 PM"

// Parsing dates from strings
const parseDate = d3.timeParse("%Y-%m-%d");
const date = parseDate("2024-03-15");  // returns Date object
```

### Common Format Specifiers
| Specifier | Meaning | Example |
|-----------|---------|---------|
| `%Y` | 4-digit year | 2024 |
| `%m` | Month (01-12) | 03 |
| `%d` | Day (01-31) | 15 |
| `%b` | Abbreviated month | Mar |
| `%B` | Full month name | March |
| `%H` | Hour (00-23) | 14 |
| `%I` | Hour (01-12) | 02 |
| `%M` | Minute (00-59) | 30 |
| `%p` | AM/PM | PM |
