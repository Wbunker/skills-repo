# Rendering Visualizations with Canvas

Reference for Canvas rendering, performance optimization, and hybrid SVG/Canvas approaches in D3.

## Table of Contents
- [Canvas vs SVG](#canvas-vs-svg)
- [Canvas Basics with D3](#canvas-basics-with-d3)
- [Drawing Shapes](#drawing-shapes)
- [Using D3 Generators with Canvas](#using-d3-generators-with-canvas)
- [Interaction on Canvas](#interaction-on-canvas)
- [Performance Optimization](#performance-optimization)
- [Hybrid SVG/Canvas](#hybrid-svgcanvas)
- [High-DPI (Retina) Rendering](#high-dpi-retina-rendering)

## Canvas vs SVG

| Aspect | SVG | Canvas |
|--------|-----|--------|
| Rendering | Retained mode (DOM tree) | Immediate mode (pixel buffer) |
| Elements | Each shape is a DOM node | No DOM nodes — just pixels |
| Events | Native per-element events | Manual hit detection |
| Performance | Degrades >1,000 elements | Handles 100K+ elements |
| Zoom/Pan | Easy (transform attribute) | Manual redraw |
| Accessibility | Good (ARIA, title) | Poor (one `<canvas>` element) |
| Export | Copy SVG / PDF | Export as PNG |
| Animation | CSS transitions, D3 transitions | requestAnimationFrame |
| Text | Rich formatting | Limited styling |

**Use Canvas when:**
- Rendering >5,000 elements (scatter plots with many points, dense maps)
- Real-time animation at 60fps
- Particle systems, simulations
- Heat maps, density plots with many cells

**Use SVG when:**
- Fewer elements with rich interactivity
- Accessibility is critical
- CSS styling and transitions
- Tooltips and hover effects per element

## Canvas Basics with D3

### Setting Up Canvas
```js
const canvas = d3.select("#chart")
  .append("canvas")
  .attr("width", width)
  .attr("height", height);

const context = canvas.node().getContext("2d");
```

### Canvas 2D Context API Essentials
```js
// Coordinate system: same as SVG (origin top-left, y increases downward)

// Drawing state
context.save();        // push current state
context.restore();     // pop state

// Transforms
context.translate(x, y);
context.rotate(angle);
context.scale(sx, sy);

// Colors and styles
context.fillStyle = "steelblue";
context.strokeStyle = "black";
context.lineWidth = 2;
context.globalAlpha = 0.5;

// Path drawing
context.beginPath();
context.moveTo(x, y);
context.lineTo(x, y);
context.arc(cx, cy, r, startAngle, endAngle);
context.rect(x, y, w, h);
context.closePath();
context.fill();
context.stroke();

// Text
context.font = "14px sans-serif";
context.textAlign = "center";    // "start", "end", "center"
context.textBaseline = "middle"; // "top", "bottom", "middle"
context.fillText("Hello", x, y);

// Clear
context.clearRect(0, 0, width, height);
```

## Drawing Shapes

### Circles (Scatter Plot)
```js
function render(data) {
  context.clearRect(0, 0, width, height);

  data.forEach(d => {
    context.beginPath();
    context.arc(xScale(d.x), yScale(d.y), 3, 0, 2 * Math.PI);
    context.fillStyle = colorScale(d.category);
    context.fill();
  });
}
```

### Rectangles (Bar Chart)
```js
data.forEach(d => {
  context.fillStyle = "steelblue";
  context.fillRect(
    xScale(d.name),
    yScale(d.value),
    xScale.bandwidth(),
    height - yScale(d.value)
  );
});
```

### Lines
```js
context.beginPath();
context.moveTo(xScale(data[0].x), yScale(data[0].y));
data.slice(1).forEach(d => {
  context.lineTo(xScale(d.x), yScale(d.y));
});
context.strokeStyle = "steelblue";
context.lineWidth = 2;
context.stroke();
```

## Using D3 Generators with Canvas

D3 generators can render to Canvas via a context adapter.

### Line Generator to Canvas
```js
const lineGenerator = d3.line()
  .x(d => xScale(d.date))
  .y(d => yScale(d.value))
  .curve(d3.curveMonotoneX)
  .context(context);   // render to canvas instead of SVG path string

context.beginPath();
lineGenerator(data);
context.strokeStyle = "steelblue";
context.lineWidth = 2;
context.stroke();
```

### Area Generator to Canvas
```js
const areaGenerator = d3.area()
  .x(d => xScale(d.date))
  .y0(height)
  .y1(d => yScale(d.value))
  .context(context);

context.beginPath();
areaGenerator(data);
context.fillStyle = "rgba(70, 130, 180, 0.3)";
context.fill();
```

### Arc Generator to Canvas
```js
const arcGenerator = d3.arc()
  .innerRadius(50)
  .outerRadius(150)
  .context(context);

const pieData = d3.pie().value(d => d.value)(data);

context.save();
context.translate(width / 2, height / 2);

pieData.forEach((d, i) => {
  context.beginPath();
  arcGenerator(d);
  context.fillStyle = colorScale(i);
  context.fill();
  context.strokeStyle = "white";
  context.lineWidth = 2;
  context.stroke();
});

context.restore();
```

### Geo Path to Canvas
```js
const projection = d3.geoNaturalEarth1()
  .fitSize([width, height], geojson);

const path = d3.geoPath(projection, context);  // render to canvas

context.beginPath();
path(geojson);
context.fillStyle = "#ccc";
context.fill();
context.strokeStyle = "white";
context.lineWidth = 0.5;
context.stroke();
```

### Rendering Axes on Canvas
D3's axis generator targets SVG, so for Canvas you draw manually:

```js
function drawXAxis(context, scale, height) {
  const ticks = scale.ticks(10);
  const tickFormat = scale.tickFormat();

  context.beginPath();
  context.moveTo(scale.range()[0], height);
  context.lineTo(scale.range()[1], height);
  context.strokeStyle = "black";
  context.stroke();

  ticks.forEach(tick => {
    const x = scale(tick);
    context.beginPath();
    context.moveTo(x, height);
    context.lineTo(x, height + 6);
    context.stroke();

    context.fillStyle = "black";
    context.textAlign = "center";
    context.textBaseline = "top";
    context.fillText(tickFormat(tick), x, height + 8);
  });
}
```

## Interaction on Canvas

Since Canvas has no DOM elements to attach events to, you need hit detection.

### Quadtree for Point Lookups
```js
const quadtree = d3.quadtree()
  .x(d => xScale(d.x))
  .y(d => yScale(d.y))
  .addAll(data);

canvas.on("mousemove", (event) => {
  const [mx, my] = d3.pointer(event);
  const closest = quadtree.find(mx, my, 20); // search radius = 20px

  if (closest) {
    // Highlight closest point, show tooltip
    render(data, closest);
  }
});
```

### Hidden Canvas (Color Picking)
Use a second offscreen canvas where each element has a unique color:

```js
const hiddenCanvas = document.createElement("canvas");
hiddenCanvas.width = width;
hiddenCanvas.height = height;
const hiddenCtx = hiddenCanvas.getContext("2d");

const colorToData = new Map();

function uniqueColor(i) {
  const r = (i >> 16) & 0xff;
  const g = (i >> 8) & 0xff;
  const b = i & 0xff;
  return `rgb(${r},${g},${b})`;
}

// Draw on hidden canvas with unique colors
data.forEach((d, i) => {
  const color = uniqueColor(i + 1);  // avoid rgb(0,0,0)
  colorToData.set(color, d);

  hiddenCtx.beginPath();
  hiddenCtx.arc(xScale(d.x), yScale(d.y), 5, 0, 2 * Math.PI);
  hiddenCtx.fillStyle = color;
  hiddenCtx.fill();
});

// On mouse move, read pixel from hidden canvas
canvas.on("mousemove", (event) => {
  const [mx, my] = d3.pointer(event);
  const [r, g, b] = hiddenCtx.getImageData(mx, my, 1, 1).data;
  const color = `rgb(${r},${g},${b})`;
  const datum = colorToData.get(color);

  if (datum) {
    showTooltip(event, datum);
  } else {
    hideTooltip();
  }
});
```

### Voronoi for Nearest-Point Detection
```js
const delaunay = d3.Delaunay.from(data, d => xScale(d.x), d => yScale(d.y));

canvas.on("mousemove", (event) => {
  const [mx, my] = d3.pointer(event);
  const index = delaunay.find(mx, my);
  const d = data[index];
  // Highlight d, show tooltip
});
```

## Performance Optimization

### Batch Drawing by Style
```js
// Instead of setting fillStyle for every element,
// group by color and batch:

const groups = d3.group(data, d => d.category);

for (const [category, items] of groups) {
  context.fillStyle = colorScale(category);
  context.beginPath();
  items.forEach(d => {
    context.moveTo(xScale(d.x) + 3, yScale(d.y));
    context.arc(xScale(d.x), yScale(d.y), 3, 0, 2 * Math.PI);
  });
  context.fill();
}
```

### requestAnimationFrame
```js
let needsRedraw = true;

function animate() {
  if (needsRedraw) {
    render();
    needsRedraw = false;
  }
  requestAnimationFrame(animate);
}

requestAnimationFrame(animate);

// On data change or interaction:
needsRedraw = true;
```

### OffscreenCanvas (Web Worker)
```js
// main.js
const offscreen = canvas.node().transferControlToOffscreen();
const worker = new Worker("render-worker.js");
worker.postMessage({ canvas: offscreen, data }, [offscreen]);

// render-worker.js
self.onmessage = function(event) {
  const { canvas, data } = event.data;
  const ctx = canvas.getContext("2d");
  // Render on worker thread...
};
```

### Spatial Indexing
```js
// For millions of points, use quadtree to only draw visible points
const quadtree = d3.quadtree()
  .x(d => d.x)
  .y(d => d.y)
  .addAll(data);

function renderVisible(bounds) {
  const visible = [];
  quadtree.visit((node, x0, y0, x1, y1) => {
    if (x0 > bounds.right || x1 < bounds.left ||
        y0 > bounds.bottom || y1 < bounds.top) {
      return true;  // skip this subtree
    }
    if (!node.length && node.data) {
      visible.push(node.data);
    }
  });
  // Draw only visible points
}
```

## Hybrid SVG/Canvas

Use Canvas for the data layer and SVG for interactivity/annotations:

```html
<div style="position: relative;">
  <canvas id="data-layer" width="800" height="500"
          style="position: absolute; top: 0; left: 0;"></canvas>
  <svg id="interaction-layer" width="800" height="500"
       style="position: absolute; top: 0; left: 0;">
    <!-- Axes, tooltips, brushes, annotations in SVG -->
  </svg>
</div>
```

```js
// Canvas: render 100K points
const ctx = document.getElementById("data-layer").getContext("2d");
data.forEach(d => {
  ctx.beginPath();
  ctx.arc(xScale(d.x), yScale(d.y), 2, 0, 2 * Math.PI);
  ctx.fill();
});

// SVG: interactive overlay
const svg = d3.select("#interaction-layer");
svg.append("g").call(d3.axisBottom(xScale));
svg.append("g").call(d3.axisLeft(yScale));
svg.append("g").call(d3.brush().on("brush", brushed));
```

## High-DPI (Retina) Rendering

Canvas renders at device pixel density for crisp output:

```js
const dpr = window.devicePixelRatio || 1;

canvas
  .attr("width", width * dpr)
  .attr("height", height * dpr)
  .style("width", `${width}px`)
  .style("height", `${height}px`);

const context = canvas.node().getContext("2d");
context.scale(dpr, dpr);

// Now draw at logical coordinates (width x height)
// Canvas internally renders at width*dpr x height*dpr pixels
```

This prevents blurry rendering on Retina/HiDPI displays.
