# Creating a Custom Visualization

Reference for custom visualization design, combining techniques, multi-view coordination, and reusable chart patterns.

## Table of Contents
- [Design Process](#design-process)
- [Reusable Chart Pattern](#reusable-chart-pattern)
- [Combining Chart Types](#combining-chart-types)
- [Multi-View Dashboards](#multi-view-dashboards)
- [Annotations](#annotations)
- [Custom Legends](#custom-legends)
- [Animation Patterns](#animation-patterns)

## Design Process

### Visualization Design Principles
1. **Identify the question** your visualization answers
2. **Choose the visual encoding** — position is most effective, then length, angle, area, color intensity, shape
3. **Reduce chartjunk** — remove unnecessary gridlines, borders, 3D effects
4. **Use consistent scales** across related views
5. **Label directly** — prefer inline labels over separate legends
6. **Progressive disclosure** — overview first, zoom and filter, details on demand

### Effectiveness Ranking (Cleveland & McGill)
Most accurate to least:
1. Position on a common scale (scatter, bar)
2. Position on non-aligned scales (small multiples)
3. Length (bar charts)
4. Angle (pie charts)
5. Area (bubble charts, treemaps)
6. Color saturation / intensity (choropleths)
7. Color hue (categorical only)

## Reusable Chart Pattern

The "module" pattern for creating reusable D3 charts:

### Closure-Based Reusable Chart
```js
function barChart() {
  // Default configuration
  let width = 600;
  let height = 400;
  let margin = { top: 20, right: 20, bottom: 30, left: 40 };
  let xValue = d => d.name;
  let yValue = d => d.value;
  let color = "steelblue";
  let onHover = () => {};

  function chart(selection) {
    selection.each(function(data) {
      const innerWidth = width - margin.left - margin.right;
      const innerHeight = height - margin.top - margin.bottom;

      const xScale = d3.scaleBand()
        .domain(data.map(xValue))
        .range([0, innerWidth])
        .padding(0.2);

      const yScale = d3.scaleLinear()
        .domain([0, d3.max(data, yValue)])
        .range([innerHeight, 0])
        .nice();

      // Select or create SVG
      let svg = d3.select(this).selectAll("svg").data([null]);
      svg = svg.enter().append("svg").merge(svg)
        .attr("width", width)
        .attr("height", height);

      let g = svg.selectAll("g.chart").data([null]);
      g = g.enter().append("g").attr("class", "chart").merge(g)
        .attr("transform", `translate(${margin.left},${margin.top})`);

      // Bars
      g.selectAll("rect")
        .data(data, xValue)
        .join("rect")
          .attr("x", d => xScale(xValue(d)))
          .attr("y", d => yScale(yValue(d)))
          .attr("width", xScale.bandwidth())
          .attr("height", d => innerHeight - yScale(yValue(d)))
          .attr("fill", color)
          .on("mouseenter", onHover);

      // Axes
      g.selectAll(".x-axis").data([null]).join("g")
        .attr("class", "x-axis")
        .attr("transform", `translate(0,${innerHeight})`)
        .call(d3.axisBottom(xScale));

      g.selectAll(".y-axis").data([null]).join("g")
        .attr("class", "y-axis")
        .call(d3.axisLeft(yScale));
    });
  }

  // Getter/setter methods (chainable)
  chart.width = function(_) {
    return arguments.length ? (width = _, chart) : width;
  };
  chart.height = function(_) {
    return arguments.length ? (height = _, chart) : height;
  };
  chart.margin = function(_) {
    return arguments.length ? (margin = _, chart) : margin;
  };
  chart.xValue = function(_) {
    return arguments.length ? (xValue = _, chart) : xValue;
  };
  chart.yValue = function(_) {
    return arguments.length ? (yValue = _, chart) : yValue;
  };
  chart.color = function(_) {
    return arguments.length ? (color = _, chart) : color;
  };
  chart.onHover = function(_) {
    return arguments.length ? (onHover = _, chart) : onHover;
  };

  return chart;
}

// Usage
const myChart = barChart()
  .width(800)
  .height(500)
  .xValue(d => d.category)
  .yValue(d => d.sales)
  .color("teal");

d3.select("#chart")
  .datum(data)
  .call(myChart);
```

### Class-Based Chart
```js
class ScatterPlot {
  constructor(container, options = {}) {
    this.container = d3.select(container);
    this.width = options.width || 600;
    this.height = options.height || 400;
    this.margin = options.margin || { top: 20, right: 20, bottom: 30, left: 40 };
    this.data = [];
    this.init();
  }

  init() {
    this.svg = this.container.append("svg")
      .attr("width", this.width)
      .attr("height", this.height);
    this.g = this.svg.append("g")
      .attr("transform", `translate(${this.margin.left},${this.margin.top})`);
    this.innerWidth = this.width - this.margin.left - this.margin.right;
    this.innerHeight = this.height - this.margin.top - this.margin.bottom;
  }

  update(data) {
    this.data = data;
    this.render();
  }

  render() {
    // scales, axes, data bindings...
  }

  destroy() {
    this.svg.remove();
  }
}
```

## Combining Chart Types

### Dual-Axis Chart (use sparingly)
```js
const yLeftScale = d3.scaleLinear()
  .domain([0, d3.max(data, d => d.revenue)])
  .range([height, 0]);

const yRightScale = d3.scaleLinear()
  .domain([0, d3.max(data, d => d.growth)])
  .range([height, 0]);

// Bars on left axis
svg.selectAll("rect")
  .data(data).join("rect")
    .attr("x", d => xScale(d.month))
    .attr("y", d => yLeftScale(d.revenue))
    .attr("width", xScale.bandwidth())
    .attr("height", d => height - yLeftScale(d.revenue))
    .attr("fill", "steelblue");

// Line on right axis
svg.append("path")
  .datum(data)
  .attr("d", d3.line()
    .x(d => xScale(d.month) + xScale.bandwidth() / 2)
    .y(d => yRightScale(d.growth)))
  .attr("fill", "none")
  .attr("stroke", "orange")
  .attr("stroke-width", 2);

// Two y-axes
svg.append("g").call(d3.axisLeft(yLeftScale));
svg.append("g")
  .attr("transform", `translate(${width},0)`)
  .call(d3.axisRight(yRightScale));
```

### Scatter + Marginal Distributions
```js
// Main scatter plot in center
// Histogram at top (x-axis marginal)
// Histogram at right (y-axis marginal, rotated)
```

### Small Multiples (Facets)
```js
const categories = Array.from(new Set(data.map(d => d.category)));
const cols = 3;
const cellWidth = width / cols;
const cellHeight = 200;

categories.forEach((cat, i) => {
  const col = i % cols;
  const row = Math.floor(i / cols);
  const g = svg.append("g")
    .attr("transform", `translate(${col * cellWidth}, ${row * cellHeight})`);

  const subset = data.filter(d => d.category === cat);
  // Draw individual chart in each cell...

  g.append("text")
    .attr("x", cellWidth / 2)
    .attr("y", 15)
    .attr("text-anchor", "middle")
    .attr("font-weight", "bold")
    .text(cat);
});
```

## Multi-View Dashboards

### Layout with CSS Grid
```html
<div class="dashboard">
  <div id="overview" class="chart"></div>
  <div id="detail" class="chart"></div>
  <div id="controls" class="chart"></div>
</div>

<style>
.dashboard {
  display: grid;
  grid-template-columns: 2fr 1fr;
  grid-template-rows: auto auto;
  gap: 16px;
}
</style>
```

### Shared State
```js
const state = {
  selectedCategory: null,
  dateRange: [startDate, endDate],
  highlightedItem: null
};

const dispatch = d3.dispatch("categoryChange", "dateChange", "highlight");

dispatch.on("categoryChange", category => {
  state.selectedCategory = category;
  updateOverview();
  updateDetail();
});

// Each chart calls dispatch.call("categoryChange", this, value);
```

## Annotations

### Direct Labels on Lines
```js
const lastPoint = series.values[series.values.length - 1];
svg.append("text")
  .attr("x", xScale(lastPoint.date) + 5)
  .attr("y", yScale(lastPoint.value))
  .attr("dy", "0.35em")
  .attr("font-size", "12px")
  .text(series.name);
```

### Callout Annotations
```js
function addAnnotation(svg, { x, y, text, dx = 30, dy = -30 }) {
  const g = svg.append("g").attr("class", "annotation");

  // Line from point to label
  g.append("line")
    .attr("x1", x).attr("y1", y)
    .attr("x2", x + dx).attr("y2", y + dy)
    .attr("stroke", "#333")
    .attr("stroke-width", 1);

  // Label background
  const textEl = g.append("text")
    .attr("x", x + dx + 4)
    .attr("y", y + dy)
    .attr("dy", "0.35em")
    .attr("font-size", "12px")
    .text(text);

  // Point marker
  g.append("circle")
    .attr("cx", x).attr("cy", y)
    .attr("r", 4)
    .attr("fill", "red");
}
```

### Reference Lines
```js
// Horizontal reference line (e.g., average)
svg.append("line")
  .attr("x1", 0).attr("x2", width)
  .attr("y1", yScale(average)).attr("y2", yScale(average))
  .attr("stroke", "#999")
  .attr("stroke-dasharray", "4,4");

svg.append("text")
  .attr("x", width - 5)
  .attr("y", yScale(average) - 5)
  .attr("text-anchor", "end")
  .attr("font-size", "11px")
  .attr("fill", "#999")
  .text(`Avg: ${average}`);
```

## Custom Legends

### Categorical Legend
```js
const legend = svg.append("g")
  .attr("transform", `translate(${width - 100}, 20)`);

const items = legend.selectAll("g")
  .data(categories)
  .join("g")
    .attr("transform", (d, i) => `translate(0, ${i * 22})`);

items.append("rect")
  .attr("width", 16).attr("height", 16)
  .attr("fill", d => colorScale(d));

items.append("text")
  .attr("x", 22).attr("y", 12)
  .attr("font-size", "12px")
  .text(d => d);
```

### Continuous Legend (gradient)
```js
const defs = svg.append("defs");
const gradient = defs.append("linearGradient")
  .attr("id", "legend-gradient")
  .attr("x1", "0%").attr("x2", "100%");

gradient.selectAll("stop")
  .data(d3.ticks(0, 1, 10))
  .join("stop")
    .attr("offset", d => `${d * 100}%`)
    .attr("stop-color", d => colorScale(colorScale.domain()[0] +
      d * (colorScale.domain()[1] - colorScale.domain()[0])));

legend.append("rect")
  .attr("width", 200).attr("height", 12)
  .attr("fill", "url(#legend-gradient)");
```

## Animation Patterns

### Enter Animation
```js
svg.selectAll("rect")
  .data(data)
  .join("rect")
    .attr("x", d => xScale(d.name))
    .attr("y", height)            // start at bottom
    .attr("width", xScale.bandwidth())
    .attr("height", 0)            // start with no height
    .attr("fill", "steelblue")
  .transition()
    .duration(750)
    .delay((d, i) => i * 50)      // stagger
    .attr("y", d => yScale(d.value))
    .attr("height", d => height - yScale(d.value));
```

### Data Update Animation
```js
function update(newData) {
  const t = svg.transition().duration(750);

  svg.selectAll("rect")
    .data(newData, d => d.name)
    .join(
      enter => enter.append("rect")
        .attr("fill", "green")
        .attr("opacity", 0)
        .call(enter => enter.transition(t)
          .attr("opacity", 1)),
      update => update
        .call(update => update.transition(t)
          .attr("fill", "steelblue")),
      exit => exit
        .call(exit => exit.transition(t)
          .attr("opacity", 0)
          .remove())
    )
    .transition(t)
      .attr("x", d => xScale(d.name))
      .attr("y", d => yScale(d.value))
      .attr("width", xScale.bandwidth())
      .attr("height", d => height - yScale(d.value));
}
```

### Morphing Between Chart Types
```js
// Bars to scatter: transition rect to circle-like
svg.selectAll("rect")
  .transition().duration(1000)
  .attr("x", d => xScale(d.name) + xScale.bandwidth() / 2 - 5)
  .attr("y", d => yScale(d.value) - 5)
  .attr("width", 10)
  .attr("height", 10)
  .attr("rx", 5);  // round corners to make it circular
```
