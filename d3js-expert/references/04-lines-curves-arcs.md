# Drawing Lines, Curves, and Arcs

Reference for D3 shape generators: lines, areas, curves, and arcs.

## Table of Contents
- [Line Generator](#line-generator)
- [Area Generator](#area-generator)
- [Curve Interpolations](#curve-interpolations)
- [Arc Generator](#arc-generator)
- [Radial Lines and Areas](#radial-lines-and-areas)
- [Symbols](#symbols)
- [Links](#links)

## Line Generator

The line generator converts an array of data points into an SVG `<path>` string.

### Basic Line
```js
const lineGenerator = d3.line()
  .x(d => xScale(d.date))
  .y(d => yScale(d.value));

svg.append("path")
  .datum(data)           // bind single array (not .data())
  .attr("d", lineGenerator)
  .attr("fill", "none")
  .attr("stroke", "steelblue")
  .attr("stroke-width", 2);
```

### Handling Missing Data
```js
const lineGenerator = d3.line()
  .defined(d => d.value != null)  // skip null/undefined points
  .x(d => xScale(d.date))
  .y(d => yScale(d.value));
```

This creates a gap in the line where data is missing.

### Multiple Lines
```js
const series = [
  { name: "Series A", values: [...] },
  { name: "Series B", values: [...] }
];

const colorScale = d3.scaleOrdinal(d3.schemeCategory10)
  .domain(series.map(s => s.name));

svg.selectAll(".line")
  .data(series)
  .join("path")
    .attr("class", "line")
    .attr("d", d => lineGenerator(d.values))
    .attr("fill", "none")
    .attr("stroke", d => colorScale(d.name))
    .attr("stroke-width", 2);
```

## Area Generator

Creates filled areas — similar to line but with a baseline.

### Basic Area
```js
const areaGenerator = d3.area()
  .x(d => xScale(d.date))
  .y0(height)                  // baseline (bottom of chart)
  .y1(d => yScale(d.value));   // top edge

svg.append("path")
  .datum(data)
  .attr("d", areaGenerator)
  .attr("fill", "steelblue")
  .attr("fill-opacity", 0.3)
  .attr("stroke", "steelblue");
```

### Area Between Two Lines
```js
const areaGenerator = d3.area()
  .x(d => xScale(d.date))
  .y0(d => yScale(d.low))    // bottom boundary
  .y1(d => yScale(d.high));  // top boundary
```

### Handling Missing Data in Areas
```js
const areaGenerator = d3.area()
  .defined(d => d.value != null)
  .x(d => xScale(d.date))
  .y0(height)
  .y1(d => yScale(d.value));
```

## Curve Interpolations

Curves control how points are connected. Apply to both line and area generators.

```js
const lineGenerator = d3.line()
  .x(d => xScale(d.date))
  .y(d => yScale(d.value))
  .curve(d3.curveMonotoneX);  // set curve type
```

### Available Curves

| Curve | Description | Use Case |
|-------|-------------|----------|
| `d3.curveLinear` | Straight segments (default) | General purpose |
| `d3.curveMonotoneX` | Monotone cubic spline (preserves monotonicity in x) | Time series — **most common choice** |
| `d3.curveMonotoneY` | Monotone cubic spline (preserves monotonicity in y) | Vertical time series |
| `d3.curveNatural` | Natural cubic spline | Smooth curves |
| `d3.curveBasis` | B-spline (doesn't pass through points) | Very smooth, approximate |
| `d3.curveBasisClosed` | Closed B-spline | Smooth closed shapes |
| `d3.curveCardinal` | Cardinal spline (tension parameter) | Adjustable smoothness |
| `d3.curveCardinal.tension(0.5)` | Cardinal with tension 0-1 | Tighter/looser curves |
| `d3.curveCatmullRom` | Catmull-Rom spline | Passes through all points |
| `d3.curveStep` | Step function (midpoint) | Discrete data |
| `d3.curveStepBefore` | Step at start of interval | Discrete, left-aligned |
| `d3.curveStepAfter` | Step at end of interval | Discrete, right-aligned |
| `d3.curveBumpX` | Smooth bump connections (horizontal) | Flow diagrams |
| `d3.curveBumpY` | Smooth bump connections (vertical) | Flow diagrams |

### Choosing a Curve
- **Time series data** → `curveMonotoneX` (prevents false oscillation)
- **Smooth aesthetic** → `curveNatural` or `curveCatmullRom`
- **Discrete categories** → `curveStep`
- **Closed shapes** → `curveBasisClosed` or `curveLinearClosed`
- **Don't oversimplify** → `curveBasis` smooths away actual data points

## Arc Generator

Creates arcs for pie charts, donut charts, and radial visualizations.

### Basic Arc
```js
const arcGenerator = d3.arc()
  .innerRadius(0)          // 0 = pie; >0 = donut
  .outerRadius(150)
  .startAngle(0)           // in radians
  .endAngle(Math.PI / 2);  // 90 degrees

svg.append("path")
  .attr("d", arcGenerator())
  .attr("fill", "steelblue")
  .attr("transform", `translate(${width/2}, ${height/2})`);
```

### Arc with Data (used with pie layout)
```js
const arcGenerator = d3.arc()
  .innerRadius(50)     // donut hole
  .outerRadius(150)
  .padAngle(0.02)      // gap between slices
  .cornerRadius(4);    // rounded corners

// arcGenerator expects { startAngle, endAngle } — provided by d3.pie()
```

### Arc Centroid
```js
// Get the center point of an arc (useful for labels)
const [labelX, labelY] = arcGenerator.centroid(arcData);
```

### Arc Transitions
```js
function arcTween(newAngle) {
  return function(d) {
    const interpolate = d3.interpolate(d.endAngle, newAngle);
    return function(t) {
      d.endAngle = interpolate(t);
      return arcGenerator(d);
    };
  };
}

path.transition()
  .duration(750)
  .attrTween("d", arcTween(newAngle));
```

## Radial Lines and Areas

For radar charts and polar visualizations:

### Radial Line
```js
const radialLine = d3.lineRadial()
  .angle(d => angleScale(d.category))
  .radius(d => radiusScale(d.value));

svg.append("path")
  .datum(data)
  .attr("d", radialLine)
  .attr("fill", "none")
  .attr("stroke", "steelblue")
  .attr("transform", `translate(${width/2}, ${height/2})`);
```

### Radial Area
```js
const radialArea = d3.areaRadial()
  .angle(d => angleScale(d.category))
  .innerRadius(0)
  .outerRadius(d => radiusScale(d.value));
```

## Symbols

Built-in symbol generators for scatter plots:

```js
const symbolGenerator = d3.symbol()
  .type(d3.symbolCircle)
  .size(64);  // area in pixels

svg.selectAll(".point")
  .data(data)
  .join("path")
    .attr("d", symbolGenerator)
    .attr("transform", d => `translate(${xScale(d.x)}, ${yScale(d.y)})`)
    .attr("fill", "steelblue");
```

### Available Symbol Types
```js
d3.symbolCircle        // circle (default)
d3.symbolCross         // plus sign
d3.symbolDiamond       // diamond
d3.symbolSquare        // square
d3.symbolStar          // five-pointed star
d3.symbolTriangle      // upward triangle
d3.symbolWye           // Y shape
```

### Dynamic Symbol Types
```js
const symbolScale = d3.scaleOrdinal()
  .domain(["A", "B", "C"])
  .range([d3.symbolCircle, d3.symbolSquare, d3.symbolTriangle]);

const symbolGenerator = d3.symbol()
  .type(d => symbolScale(d.category))
  .size(d => sizeScale(d.value));
```

## Links

Link generators create smooth curves between two points — useful for trees and networks:

```js
// Horizontal link (for horizontal trees)
const linkGenerator = d3.linkHorizontal()
  .x(d => d.y)    // note: x/y swapped for horizontal layout
  .y(d => d.x);

// Vertical link
const linkGenerator = d3.linkVertical()
  .x(d => d.x)
  .y(d => d.y);

// Radial link (for radial trees)
const linkGenerator = d3.linkRadial()
  .angle(d => d.x)
  .radius(d => d.y);

svg.selectAll(".link")
  .data(links)
  .join("path")
    .attr("d", d => linkGenerator({ source: d.source, target: d.target }))
    .attr("fill", "none")
    .attr("stroke", "#999");
```
