# Interactive Visualizations

Reference for D3 events, tooltips, brushing, zooming, transitions, and drag behavior.

## Table of Contents
- [Event Handling](#event-handling)
- [Tooltips](#tooltips)
- [Transitions](#transitions)
- [Brushing](#brushing)
- [Zooming and Panning](#zooming-and-panning)
- [Drag Behavior](#drag-behavior)
- [Coordinated Views](#coordinated-views)

## Event Handling

### Attaching Event Listeners
```js
svg.selectAll("rect")
  .on("click", function(event, d) {
    console.log("Clicked:", d);
  })
  .on("mouseenter", function(event, d) {
    d3.select(this).attr("fill", "orange");
  })
  .on("mouseleave", function(event, d) {
    d3.select(this).attr("fill", "steelblue");
  });
```

**Important:** Use regular functions (not arrow functions) when you need `this` to reference the DOM element. Arrow functions inherit `this` from the enclosing scope.

### D3 v7 Event Signature
```js
// D3 v7: (event, datum)
.on("click", (event, d) => {
  console.log(event.clientX, event.clientY);  // mouse position
  console.log(d);  // bound datum
});

// Access the DOM element with event.target or event.currentTarget
.on("click", (event, d) => {
  d3.select(event.currentTarget).attr("fill", "red");
});
```

### Common Events
| Event | Trigger |
|-------|---------|
| `click` | Mouse click |
| `dblclick` | Double click |
| `mouseenter` | Mouse enters element (no bubbling) |
| `mouseleave` | Mouse leaves element (no bubbling) |
| `mouseover` | Mouse enters (bubbles) |
| `mouseout` | Mouse leaves (bubbles) |
| `mousemove` | Mouse moves over element |
| `pointerenter` | Pointer enters (touch + mouse) |
| `pointerleave` | Pointer leaves |
| `pointermove` | Pointer moves |

### Pointer Position
```js
.on("mousemove", (event) => {
  const [mx, my] = d3.pointer(event);      // relative to event target
  const [mx, my] = d3.pointer(event, svg.node()); // relative to svg
});
```

### Removing Listeners
```js
selection.on("click", null);  // remove click handler
```

## Tooltips

### HTML Tooltip (most flexible)
```js
// Create tooltip div
const tooltip = d3.select("body")
  .append("div")
  .attr("class", "tooltip")
  .style("position", "absolute")
  .style("visibility", "hidden")
  .style("background", "white")
  .style("border", "1px solid #ddd")
  .style("border-radius", "4px")
  .style("padding", "8px 12px")
  .style("font-size", "12px")
  .style("pointer-events", "none")
  .style("box-shadow", "0 2px 4px rgba(0,0,0,0.1)");

// Show/hide on hover
svg.selectAll("circle")
  .on("mouseenter", (event, d) => {
    tooltip
      .style("visibility", "visible")
      .html(`<strong>${d.name}</strong><br/>Value: ${d.value}`);
  })
  .on("mousemove", (event) => {
    tooltip
      .style("top", (event.pageY - 10) + "px")
      .style("left", (event.pageX + 10) + "px");
  })
  .on("mouseleave", () => {
    tooltip.style("visibility", "hidden");
  });
```

### SVG Tooltip (title element — basic)
```js
svg.selectAll("rect")
  .append("title")
  .text(d => `${d.name}: ${d.value}`);
```

### Voronoi Tooltip (for scatter plots)
When points are small or dense, use Voronoi tessellation for better hit targets:

```js
const delaunay = d3.Delaunay.from(data, d => xScale(d.x), d => yScale(d.y));
const voronoi = delaunay.voronoi([0, 0, width, height]);

svg.selectAll("path.voronoi")
  .data(data)
  .join("path")
    .attr("d", (d, i) => voronoi.renderCell(i))
    .attr("fill", "transparent")
    .on("mouseenter", (event, d) => {
      // Show tooltip, highlight point
    })
    .on("mouseleave", () => {
      // Hide tooltip
    });
```

## Transitions

### Basic Transition
```js
svg.selectAll("rect")
  .transition()
  .duration(750)          // milliseconds
  .delay((d, i) => i * 50) // stagger
  .ease(d3.easeCubicOut)  // easing function
  .attr("height", d => yScale(d.value))
  .attr("y", d => height - yScale(d.value))
  .attr("fill", "orange");
```

### Easing Functions
| Easing | Description |
|--------|-------------|
| `d3.easeLinear` | Constant speed |
| `d3.easeCubic` | Default — cubic ease in-out |
| `d3.easeCubicOut` | Fast start, slow end |
| `d3.easeCubicIn` | Slow start, fast end |
| `d3.easeElastic` | Springy overshoot |
| `d3.easeBounce` | Bouncing at end |
| `d3.easeBack` | Slight overshoot |
| `d3.easeCircle` | Circular easing |

### Chaining Transitions
```js
selection
  .transition()
    .duration(500)
    .attr("fill", "red")
  .transition()           // chains after first completes
    .duration(500)
    .attr("fill", "blue");
```

### Transition Events
```js
selection.transition()
  .on("start", () => console.log("started"))
  .on("end", () => console.log("ended"))
  .on("interrupt", () => console.log("interrupted"));
```

### Custom Interpolation (attrTween)
```js
selection.transition()
  .attrTween("d", function(d) {
    const previous = d3.select(this).attr("d");
    const interpolator = d3.interpolatePath(previous, newPath);
    return function(t) {
      return interpolator(t);
    };
  });
```

## Brushing

Brushing allows rectangular selection of data points.

### 2D Brush
```js
const brush = d3.brush()
  .extent([[0, 0], [width, height]])
  .on("start brush end", brushed);

svg.append("g")
  .attr("class", "brush")
  .call(brush);

function brushed(event) {
  if (!event.selection) return;  // no selection (cleared)
  const [[x0, y0], [x1, y1]] = event.selection;

  svg.selectAll("circle")
    .classed("selected", d =>
      xScale(d.x) >= x0 && xScale(d.x) <= x1 &&
      yScale(d.y) >= y0 && yScale(d.y) <= y1
    );
}
```

### X-Axis Brush (for time series)
```js
const brush = d3.brushX()
  .extent([[0, 0], [width, height]])
  .on("end", brushed);

function brushed(event) {
  if (!event.selection) return;
  const [x0, x1] = event.selection.map(xScale.invert);
  // Filter or zoom to [x0, x1] date range
}
```

### Y-Axis Brush
```js
const brush = d3.brushY()
  .extent([[0, 0], [width, height]]);
```

### Programmatic Brush Control
```js
// Set brush selection programmatically
svg.select(".brush").call(brush.move, [xScale(startDate), xScale(endDate)]);

// Clear brush
svg.select(".brush").call(brush.move, null);
```

## Zooming and Panning

### Basic Zoom
```js
const zoom = d3.zoom()
  .scaleExtent([1, 10])    // min/max zoom level
  .translateExtent([[0, 0], [width, height]]) // pan bounds
  .on("zoom", zoomed);

svg.call(zoom);

function zoomed(event) {
  const transform = event.transform;
  // Apply transform to content group
  contentGroup.attr("transform", transform);
}
```

### Semantic Zoom (rescale axes)
```js
function zoomed(event) {
  const newXScale = event.transform.rescaleX(xScale);
  const newYScale = event.transform.rescaleY(yScale);

  // Update axes
  xAxisGroup.call(d3.axisBottom(newXScale));
  yAxisGroup.call(d3.axisLeft(newYScale));

  // Update data elements
  svg.selectAll("circle")
    .attr("cx", d => newXScale(d.x))
    .attr("cy", d => newYScale(d.y));
}
```

### Geometric Zoom (transform group)
```js
function zoomed(event) {
  contentGroup.attr("transform", event.transform);
}
```

### Programmatic Zoom
```js
// Zoom to specific transform
svg.transition().duration(750)
  .call(zoom.transform, d3.zoomIdentity.translate(100, 0).scale(2));

// Reset zoom
svg.transition().duration(750)
  .call(zoom.transform, d3.zoomIdentity);

// Zoom to fit a specific area
const bounds = [[x0, y0], [x1, y1]];
const dx = x1 - x0, dy = y1 - y0;
const scale = Math.min(width / dx, height / dy) * 0.9;
const translate = [width / 2 - scale * (x0 + x1) / 2,
                   height / 2 - scale * (y0 + y1) / 2];
svg.transition().duration(750)
  .call(zoom.transform,
    d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale));
```

## Drag Behavior

```js
const drag = d3.drag()
  .on("start", dragStarted)
  .on("drag", dragged)
  .on("end", dragEnded);

svg.selectAll("circle").call(drag);

function dragStarted(event, d) {
  d3.select(this).raise().attr("stroke", "black");
}

function dragged(event, d) {
  d3.select(this)
    .attr("cx", d.x = event.x)
    .attr("cy", d.y = event.y);
}

function dragEnded(event, d) {
  d3.select(this).attr("stroke", null);
}
```

### Drag with Force Simulation
```js
function dragStarted(event, d) {
  if (!event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(event, d) {
  d.fx = event.x;
  d.fy = event.y;
}

function dragEnded(event, d) {
  if (!event.active) simulation.alphaTarget(0);
  d.fx = null;
  d.fy = null;
}
```

## Coordinated Views

### Linked Highlighting
```js
// Highlight same data across multiple charts
function highlight(category) {
  d3.selectAll(".bar")
    .attr("opacity", d => d.category === category ? 1 : 0.2);
  d3.selectAll(".point")
    .attr("opacity", d => d.category === category ? 1 : 0.2);
}

function unhighlight() {
  d3.selectAll(".bar, .point").attr("opacity", 1);
}
```

### Brush-to-Zoom (Overview + Detail)
```js
// Mini chart brush drives main chart zoom
function brushed(event) {
  if (!event.selection) return;
  const [x0, x1] = event.selection.map(miniXScale.invert);
  mainXScale.domain([x0, x1]);
  mainChart.selectAll(".line").attr("d", lineGenerator);
  mainChart.select(".x-axis").call(d3.axisBottom(mainXScale));
}
```

### Dispatch for Cross-Chart Communication
```js
const dispatch = d3.dispatch("highlight", "select");

dispatch.on("highlight", function(category) {
  // Update all charts
});

// Trigger from any chart
dispatch.call("highlight", this, selectedCategory);
```
