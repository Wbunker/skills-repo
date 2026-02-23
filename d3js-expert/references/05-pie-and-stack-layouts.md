# Pie and Stack Layouts

Reference for D3 pie layout, stack layout, and related chart types.

## Table of Contents
- [Pie Layout](#pie-layout)
- [Donut Charts](#donut-charts)
- [Stack Layout](#stack-layout)
- [Stacked Bar Charts](#stacked-bar-charts)
- [Stacked Area Charts](#stacked-area-charts)
- [Streamgraphs](#streamgraphs)
- [Stack Orders and Offsets](#stack-orders-and-offsets)

## Pie Layout

The pie layout computes start and end angles from data values. It does **not** draw anything — pair it with the arc generator.

### Basic Pie Chart
```js
const data = [
  { label: "A", value: 30 },
  { label: "B", value: 50 },
  { label: "C", value: 20 }
];

// Compute angles
const pie = d3.pie()
  .value(d => d.value)
  .sort(null);  // preserve original order (default sorts descending)

const arcs = pie(data);
// Each item: { data, value, startAngle, endAngle, index, padAngle }

// Create arc generator
const arcGenerator = d3.arc()
  .innerRadius(0)
  .outerRadius(150);

const color = d3.scaleOrdinal(d3.schemeCategory10);

// Draw slices
const g = svg.append("g")
  .attr("transform", `translate(${width/2}, ${height/2})`);

g.selectAll("path")
  .data(arcs)
  .join("path")
    .attr("d", arcGenerator)
    .attr("fill", (d, i) => color(i))
    .attr("stroke", "white")
    .attr("stroke-width", 2);
```

### Pie Labels
```js
const labelArc = d3.arc()
  .innerRadius(100)   // place labels between inner and outer
  .outerRadius(100);

g.selectAll("text")
  .data(arcs)
  .join("text")
    .attr("transform", d => `translate(${labelArc.centroid(d)})`)
    .attr("text-anchor", "middle")
    .attr("font-size", "12px")
    .text(d => d.data.label);
```

### Pie Options
```js
d3.pie()
  .value(d => d.value)      // accessor for value
  .sort(null)                // null = original order
  .sort((a, b) => a.value - b.value)  // custom sort
  .sortValues(d3.descending) // sort by value
  .startAngle(0)             // default 0
  .endAngle(2 * Math.PI)     // default 2π (full circle)
  .padAngle(0.02);           // gap between slices in radians
```

### Partial Pie (Gauge / Semi-circle)
```js
const pie = d3.pie()
  .value(d => d.value)
  .startAngle(-Math.PI / 2)
  .endAngle(Math.PI / 2)
  .sort(null);
```

## Donut Charts

A donut chart is simply a pie with `innerRadius > 0`:

```js
const arcGenerator = d3.arc()
  .innerRadius(80)    // creates the hole
  .outerRadius(150)
  .cornerRadius(4)    // rounded corners
  .padAngle(0.02);    // gap between slices
```

### Center Label
```js
g.append("text")
  .attr("text-anchor", "middle")
  .attr("dy", "0.35em")
  .attr("font-size", "24px")
  .attr("font-weight", "bold")
  .text("Total: 100");
```

### Interactive Hover (grow on hover)
```js
const arcHover = d3.arc()
  .innerRadius(80)
  .outerRadius(160);  // slightly larger

g.selectAll("path")
  .on("mouseenter", function(event, d) {
    d3.select(this)
      .transition().duration(200)
      .attr("d", arcHover);
  })
  .on("mouseleave", function(event, d) {
    d3.select(this)
      .transition().duration(200)
      .attr("d", arcGenerator);
  });
```

## Stack Layout

The stack layout computes baseline and topline values for stacking multiple series.

### Basic Stack
```js
const data = [
  { month: "Jan", apples: 100, bananas: 50, cherries: 30 },
  { month: "Feb", apples: 120, bananas: 60, cherries: 40 },
  { month: "Mar", apples: 90,  bananas: 70, cherries: 35 }
];

const stack = d3.stack()
  .keys(["apples", "bananas", "cherries"])
  .order(d3.stackOrderNone)
  .offset(d3.stackOffsetNone);

const series = stack(data);
// series[0] = apples: [[0, 100], [0, 120], [0, 90]]
// series[1] = bananas: [[100, 150], [120, 180], [90, 160]]
// series[2] = cherries: [[150, 180], [180, 220], [160, 195]]
// Each item: [lower, upper] with .data reference to original row
```

## Stacked Bar Charts

```js
const stack = d3.stack()
  .keys(["apples", "bananas", "cherries"]);

const series = stack(data);

const color = d3.scaleOrdinal()
  .domain(["apples", "bananas", "cherries"])
  .range(d3.schemeCategory10);

const xScale = d3.scaleBand()
  .domain(data.map(d => d.month))
  .range([0, width])
  .padding(0.2);

const yScale = d3.scaleLinear()
  .domain([0, d3.max(series, s => d3.max(s, d => d[1]))])
  .range([height, 0]);

// Draw stacked bars
svg.selectAll("g.series")
  .data(series)
  .join("g")
    .attr("class", "series")
    .attr("fill", d => color(d.key))
  .selectAll("rect")
  .data(d => d)
  .join("rect")
    .attr("x", d => xScale(d.data.month))
    .attr("y", d => yScale(d[1]))
    .attr("height", d => yScale(d[0]) - yScale(d[1]))
    .attr("width", xScale.bandwidth());
```

### Grouped (Side-by-Side) Bar Chart
```js
const keys = ["apples", "bananas", "cherries"];

const x0 = d3.scaleBand()
  .domain(data.map(d => d.month))
  .range([0, width])
  .padding(0.2);

const x1 = d3.scaleBand()
  .domain(keys)
  .range([0, x0.bandwidth()])
  .padding(0.05);

svg.selectAll("g.group")
  .data(data)
  .join("g")
    .attr("class", "group")
    .attr("transform", d => `translate(${x0(d.month)}, 0)`)
  .selectAll("rect")
  .data(d => keys.map(key => ({ key, value: d[key] })))
  .join("rect")
    .attr("x", d => x1(d.key))
    .attr("y", d => yScale(d.value))
    .attr("width", x1.bandwidth())
    .attr("height", d => height - yScale(d.value))
    .attr("fill", d => color(d.key));
```

## Stacked Area Charts

```js
const areaGenerator = d3.area()
  .x(d => xScale(d.data.date))
  .y0(d => yScale(d[0]))
  .y1(d => yScale(d[1]))
  .curve(d3.curveMonotoneX);

svg.selectAll("path.area")
  .data(series)
  .join("path")
    .attr("class", "area")
    .attr("d", areaGenerator)
    .attr("fill", d => color(d.key))
    .attr("fill-opacity", 0.8);
```

## Streamgraphs

A streamgraph uses the **wiggle** offset to center layers around a baseline, creating a flowing river-like visualization.

```js
const stack = d3.stack()
  .keys(keys)
  .offset(d3.stackOffsetWiggle)  // streamgraph offset
  .order(d3.stackOrderInsideOut); // minimize wiggle

const yScale = d3.scaleLinear()
  .domain([
    d3.min(series, s => d3.min(s, d => d[0])),
    d3.max(series, s => d3.max(s, d => d[1]))
  ])
  .range([height, 0]);

const areaGenerator = d3.area()
  .x(d => xScale(d.data.date))
  .y0(d => yScale(d[0]))
  .y1(d => yScale(d[1]))
  .curve(d3.curveBasis);  // smooth for streamgraph aesthetic
```

## Stack Orders and Offsets

### Stack Orders
| Order | Description |
|-------|-------------|
| `d3.stackOrderNone` | Input order (default) |
| `d3.stackOrderAscending` | Smallest series on bottom |
| `d3.stackOrderDescending` | Largest series on bottom |
| `d3.stackOrderInsideOut` | Largest in middle (best for streamgraph) |
| `d3.stackOrderReverse` | Reverse of input order |

### Stack Offsets
| Offset | Description |
|--------|-------------|
| `d3.stackOffsetNone` | Zero baseline (default) — standard stacked chart |
| `d3.stackOffsetExpand` | Normalize to 0-1 — 100% stacked chart |
| `d3.stackOffsetWiggle` | Minimize wiggle — streamgraph |
| `d3.stackOffsetSilhouette` | Center around midline |
| `d3.stackOffsetDiverging` | Positive above zero, negative below |

### 100% Stacked Chart
```js
const stack = d3.stack()
  .keys(keys)
  .offset(d3.stackOffsetExpand);  // normalize to 0-1

const yScale = d3.scaleLinear()
  .domain([0, 1])
  .range([height, 0]);

// Format axis as percentage
const yAxis = d3.axisLeft(yScale)
  .tickFormat(d3.format(".0%"));
```
