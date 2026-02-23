# Visualizing Distributions

Reference for histograms, box plots, violin plots, density plots, and bin generators in D3.

## Table of Contents
- [Bin Generator (Histograms)](#bin-generator-histograms)
- [Drawing Histograms](#drawing-histograms)
- [Box Plots](#box-plots)
- [Violin Plots](#violin-plots)
- [Density Plots](#density-plots)
- [Beeswarm Plots](#beeswarm-plots)

## Bin Generator (Histograms)

The `d3.bin()` generator groups continuous data into discrete bins.

### Basic Binning
```js
const bin = d3.bin()
  .value(d => d.age)           // accessor
  .domain(xScale.domain())     // match scale domain
  .thresholds(20);             // approximate number of bins

const bins = bin(data);
// Each bin: array of data items + bin.x0 (lower bound) + bin.x1 (upper bound)
```

### Threshold Options
```js
d3.bin().thresholds(20);                    // ~20 bins
d3.bin().thresholds(d3.thresholdSturges);   // Sturges' formula (default)
d3.bin().thresholds(d3.thresholdScott);     // Scott's normal reference rule
d3.bin().thresholds(d3.thresholdFreedmanDiaconis); // Freedman-Diaconis rule
d3.bin().thresholds([0, 10, 20, 30, 50, 100]); // explicit boundaries
```

### Choosing Thresholds
- **Sturges**: good for normal distributions, tends to underbin for large n
- **Scott**: assumes normality, good for moderate data
- **Freedman-Diaconis**: robust to outliers, best general-purpose choice
- **Explicit**: when you need domain-specific breakpoints

## Drawing Histograms

### Vertical Histogram
```js
const xScale = d3.scaleLinear()
  .domain([d3.min(data, d => d.value), d3.max(data, d => d.value)])
  .range([0, width]);

const bin = d3.bin()
  .value(d => d.value)
  .domain(xScale.domain())
  .thresholds(30);

const bins = bin(data);

const yScale = d3.scaleLinear()
  .domain([0, d3.max(bins, d => d.length)])
  .range([height, 0])
  .nice();

svg.selectAll("rect")
  .data(bins)
  .join("rect")
    .attr("x", d => xScale(d.x0) + 1)
    .attr("y", d => yScale(d.length))
    .attr("width", d => Math.max(0, xScale(d.x1) - xScale(d.x0) - 1))
    .attr("height", d => height - yScale(d.length))
    .attr("fill", "steelblue");
```

### Histogram with Density Overlay
```js
// Draw histogram bars first (as above)

// Add density curve
const density = kernelDensityEstimator(
  kernelEpanechnikov(7),
  xScale.ticks(50)
)(data.map(d => d.value));

const densityScale = d3.scaleLinear()
  .domain([0, d3.max(density, d => d[1])])
  .range([height, 0]);

const densityLine = d3.line()
  .x(d => xScale(d[0]))
  .y(d => densityScale(d[1]))
  .curve(d3.curveBasis);

svg.append("path")
  .datum(density)
  .attr("d", densityLine)
  .attr("fill", "none")
  .attr("stroke", "red")
  .attr("stroke-width", 2);
```

## Box Plots

Box plots show distribution summary: median, quartiles, whiskers, and outliers.

### Computing Box Plot Statistics
```js
function boxplotStats(values) {
  values.sort(d3.ascending);
  const q1 = d3.quantile(values, 0.25);
  const median = d3.quantile(values, 0.5);
  const q3 = d3.quantile(values, 0.75);
  const iqr = q3 - q1;
  const whiskerLow = d3.max([d3.min(values), q1 - 1.5 * iqr]);
  const whiskerHigh = d3.min([d3.max(values), q3 + 1.5 * iqr]);
  const outliers = values.filter(v => v < whiskerLow || v > whiskerHigh);
  return { q1, median, q3, iqr, whiskerLow, whiskerHigh, outliers };
}
```

### Drawing Box Plots
```js
const stats = boxplotStats(data.map(d => d.value));
const boxWidth = 60;
const cx = width / 2;

// Whisker line
svg.append("line")
  .attr("x1", cx).attr("x2", cx)
  .attr("y1", yScale(stats.whiskerLow))
  .attr("y2", yScale(stats.whiskerHigh))
  .attr("stroke", "black");

// Box (Q1 to Q3)
svg.append("rect")
  .attr("x", cx - boxWidth / 2)
  .attr("y", yScale(stats.q3))
  .attr("width", boxWidth)
  .attr("height", yScale(stats.q1) - yScale(stats.q3))
  .attr("fill", "steelblue")
  .attr("stroke", "black");

// Median line
svg.append("line")
  .attr("x1", cx - boxWidth / 2)
  .attr("x2", cx + boxWidth / 2)
  .attr("y1", yScale(stats.median))
  .attr("y2", yScale(stats.median))
  .attr("stroke", "black")
  .attr("stroke-width", 2);

// Outliers
svg.selectAll("circle.outlier")
  .data(stats.outliers)
  .join("circle")
    .attr("cx", cx)
    .attr("cy", d => yScale(d))
    .attr("r", 3)
    .attr("fill", "none")
    .attr("stroke", "black");
```

### Multiple Box Plots (by category)
```js
const categories = Array.from(d3.group(data, d => d.category).keys());
const xScale = d3.scaleBand()
  .domain(categories)
  .range([0, width])
  .padding(0.4);

categories.forEach(cat => {
  const values = data.filter(d => d.category === cat).map(d => d.value);
  const stats = boxplotStats(values);
  const cx = xScale(cat) + xScale.bandwidth() / 2;
  // Draw box, whiskers, median, outliers at cx...
});
```

## Violin Plots

Violin plots combine box plots with density curves to show distribution shape.

```js
const density = kernelDensityEstimator(
  kernelEpanechnikov(bandwidth),
  yScale.ticks(50)
)(values);

const violinWidth = d3.scaleLinear()
  .domain([0, d3.max(density, d => d[1])])
  .range([0, xScale.bandwidth() / 2]);

const violinArea = d3.area()
  .x0(d => cx - violinWidth(d[1]))
  .x1(d => cx + violinWidth(d[1]))
  .y(d => yScale(d[0]))
  .curve(d3.curveBasis);

svg.append("path")
  .datum(density)
  .attr("d", violinArea)
  .attr("fill", "steelblue")
  .attr("fill-opacity", 0.6)
  .attr("stroke", "steelblue");
```

## Density Plots

### Kernel Density Estimation (KDE)
```js
function kernelDensityEstimator(kernel, ticks) {
  return function(values) {
    return ticks.map(t => [t, d3.mean(values, v => kernel(t - v))]);
  };
}

function kernelEpanechnikov(bandwidth) {
  return function(v) {
    v = v / bandwidth;
    return Math.abs(v) <= 1 ? 0.75 * (1 - v * v) / bandwidth : 0;
  };
}

function kernelGaussian(bandwidth) {
  return function(v) {
    v = v / bandwidth;
    return Math.exp(-0.5 * v * v) / (bandwidth * Math.sqrt(2 * Math.PI));
  };
}
```

### Drawing Density Plot
```js
const density = kernelDensityEstimator(
  kernelEpanechnikov(7),
  xScale.ticks(100)
)(data.map(d => d.value));

const yScale = d3.scaleLinear()
  .domain([0, d3.max(density, d => d[1])])
  .range([height, 0]);

const densityArea = d3.area()
  .x(d => xScale(d[0]))
  .y0(height)
  .y1(d => yScale(d[1]))
  .curve(d3.curveBasis);

svg.append("path")
  .datum(density)
  .attr("d", densityArea)
  .attr("fill", "steelblue")
  .attr("fill-opacity", 0.5)
  .attr("stroke", "steelblue");
```

### Bandwidth Selection
- **Too small**: noisy, overfits
- **Too large**: oversmooths, hides structure
- **Silverman's rule**: `bandwidth = 1.06 * std * n^(-1/5)`
- **Visual tuning**: try multiple bandwidths and compare

## Beeswarm Plots

Show individual data points without overlap using force simulation:

```js
const simulation = d3.forceSimulation(data)
  .force("x", d3.forceX(d => xScale(d.category)).strength(1))
  .force("y", d3.forceY(d => yScale(d.value)).strength(1))
  .force("collide", d3.forceCollide(3))
  .stop();

// Run simulation synchronously
for (let i = 0; i < 120; i++) simulation.tick();

svg.selectAll("circle")
  .data(data)
  .join("circle")
    .attr("cx", d => d.x)
    .attr("cy", d => d.y)
    .attr("r", 2.5)
    .attr("fill", "steelblue")
    .attr("fill-opacity", 0.6);
```
