# Introduction to D3.js

Reference for D3.js fundamentals, ecosystem, and core concepts.

## Table of Contents
- [What is D3.js](#what-is-d3js)
- [D3 Ecosystem and Modules](#d3-ecosystem-and-modules)
- [SVG Fundamentals](#svg-fundamentals)
- [Setting Up a D3 Project](#setting-up-a-d3-project)
- [Method Chaining](#method-chaining)
- [Core Concepts](#core-concepts)

## What is D3.js

D3 (Data-Driven Documents) is a JavaScript library for creating custom, interactive data visualizations in the browser using web standards (HTML, SVG, CSS).

**Key philosophy:**
- Not a charting library — a visualization toolkit for building custom visualizations
- Binds data to DOM elements and applies data-driven transformations
- Leverages web standards (SVG, Canvas, HTML) rather than proprietary rendering
- Declarative approach: describe *what* you want, not *how* to render pixel by pixel
- Composable modules: use only what you need

**When to use D3 vs. charting libraries:**
- D3: custom or novel visualizations, fine-grained control, interactive dashboards
- Chart.js / Highcharts / Recharts: standard charts with minimal customization
- Observable Plot / Vega-Lite: grammar-of-graphics approach with less code

**D3 v7 (current):**
- ES modules, promises-based data loading
- `selection.join()` replaces manual enter/update/exit
- Smaller bundle via tree-shaking individual modules

## D3 Ecosystem and Modules

D3 is modular. Import only what you need:

| Module | Purpose |
|--------|---------|
| `d3-selection` | DOM selection and manipulation |
| `d3-scale` | Scales (linear, band, ordinal, log, time, etc.) |
| `d3-axis` | Axis generators |
| `d3-shape` | Lines, areas, arcs, pies, stacks, curves |
| `d3-hierarchy` | Trees, treemaps, pack, partition |
| `d3-force` | Force-directed layouts |
| `d3-geo` | Geographic projections and paths |
| `d3-transition` | Animated transitions |
| `d3-zoom` | Pan and zoom behavior |
| `d3-brush` | Brushing (rectangular selection) |
| `d3-drag` | Drag interaction |
| `d3-fetch` | Data loading (csv, json, tsv) |
| `d3-array` | Array utilities (min, max, extent, group, rollup) |
| `d3-format` | Number formatting |
| `d3-time-format` | Date/time formatting |
| `d3-color` | Color manipulation |
| `d3-interpolate` | Value interpolation for transitions |
| `d3-dispatch` | Custom event dispatching |
| `d3-delaunay` | Voronoi / Delaunay triangulation |

**Installation:**
```bash
# Full library
npm install d3

# Individual modules
npm install d3-selection d3-scale d3-axis d3-shape
```

**Import patterns:**
```js
// Full import
import * as d3 from "d3";

// Tree-shakeable individual imports
import { select, selectAll } from "d3-selection";
import { scaleLinear, scaleBand } from "d3-scale";
import { axisBottom, axisLeft } from "d3-axis";
import { line, area, arc } from "d3-shape";
```

## SVG Fundamentals

D3 primarily renders to SVG. Key SVG elements:

### Basic Shapes
```html
<!-- Rectangle -->
<rect x="10" y="10" width="100" height="50" fill="steelblue" />

<!-- Circle -->
<circle cx="60" cy="60" r="30" fill="orange" />

<!-- Line -->
<line x1="0" y1="0" x2="100" y2="100" stroke="black" stroke-width="2" />

<!-- Ellipse -->
<ellipse cx="60" cy="60" rx="50" ry="30" fill="green" />

<!-- Text -->
<text x="10" y="30" font-size="14" fill="black">Hello D3</text>

<!-- Path (most flexible — used by D3 generators) -->
<path d="M10 80 Q 95 10 180 80" stroke="black" fill="none" />
```

### SVG Coordinate System
- Origin (0,0) is **top-left**
- x increases rightward, y increases **downward**
- This means charts are typically built "upside down" from mathematical convention
- Scales map data values to pixel positions accounting for this inversion

### Groups and Transforms
```html
<svg width="600" height="400">
  <g transform="translate(40, 20)">
    <!-- All children are offset by (40, 20) -->
    <rect x="0" y="0" width="100" height="50" />
  </g>
</svg>
```

### Common SVG Attributes
| Attribute | Purpose |
|-----------|---------|
| `fill` | Interior color |
| `stroke` | Border/line color |
| `stroke-width` | Border/line thickness |
| `opacity` | Element transparency (0-1) |
| `fill-opacity` | Fill transparency only |
| `stroke-opacity` | Stroke transparency only |
| `transform` | translate, rotate, scale |
| `class` | CSS class for styling |

## Setting Up a D3 Project

### Minimal HTML Setup
```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    svg { border: 1px solid #ccc; }
  </style>
</head>
<body>
  <div id="chart"></div>
  <script src="chart.js"></script>
</body>
</html>
```

### Modern ES Module Setup
```js
// package.json
{
  "type": "module",
  "dependencies": {
    "d3": "^7"
  }
}
```

### Common Chart Scaffold
```js
// Margin convention — the standard D3 pattern
const margin = { top: 20, right: 30, bottom: 40, left: 50 };
const width = 800 - margin.left - margin.right;
const height = 500 - margin.top - margin.bottom;

const svg = d3.select("#chart")
  .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

// Now use `width` and `height` for your inner drawing area
// Axes sit at the edges of this inner area
```

## Method Chaining

D3 uses fluent method chaining — each method returns the selection so you can chain calls:

```js
d3.select("#chart")
  .append("svg")
    .attr("width", 600)
    .attr("height", 400)
  .append("circle")
    .attr("cx", 300)
    .attr("cy", 200)
    .attr("r", 50)
    .attr("fill", "steelblue")
    .on("click", function(event, d) {
      console.log("Clicked!");
    });
```

**Important:** `append()` returns the *new* element, not the parent. To add multiple children to the same parent, save a reference:

```js
const svg = d3.select("#chart").append("svg")
  .attr("width", 600)
  .attr("height", 400);

svg.append("circle").attr("cx", 100).attr("r", 20);
svg.append("circle").attr("cx", 200).attr("r", 20);
svg.append("rect").attr("x", 300).attr("width", 50).attr("height", 50);
```

## Core Concepts

### Data-Driven Documents
The central idea: DOM elements are a function of data.

1. **Bind** data to DOM elements
2. **Enter** new elements for new data points
3. **Update** existing elements when data changes
4. **Exit** remove elements for removed data points

### Selections
Everything in D3 starts with a selection — a wrapper around DOM elements that provides D3's API.

### Scales
Functions that map from a data domain to a visual range (pixels, colors, etc.).

### Generators
Functions that convert data into SVG path strings (lines, areas, arcs).

### Layouts
Algorithms that compute positions/sizes from data (force, hierarchy, pie, stack).

### Behaviors
Reusable interaction patterns (zoom, brush, drag) that attach event listeners and manage state.
