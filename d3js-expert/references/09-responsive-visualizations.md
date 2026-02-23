# Responsive Visualizations

Reference for making D3 visualizations responsive and mobile-friendly.

## Table of Contents
- [Responsive SVG with viewBox](#responsive-svg-with-viewbox)
- [ResizeObserver Approach](#resizeobserver-approach)
- [Fluid Layouts](#fluid-layouts)
- [Mobile Considerations](#mobile-considerations)
- [Responsive Axes and Labels](#responsive-axes-and-labels)
- [Breakpoint Strategies](#breakpoint-strategies)

## Responsive SVG with viewBox

The simplest responsive approach: set `viewBox` and let SVG scale proportionally.

### Basic viewBox
```js
const svg = d3.select("#chart")
  .append("svg")
  .attr("viewBox", `0 0 ${width} ${height}`)
  .attr("preserveAspectRatio", "xMidYMid meet")
  .style("width", "100%")
  .style("height", "auto");
```

**How it works:**
- `viewBox` defines the internal coordinate system (always the same)
- The SVG scales to fit its container while preserving aspect ratio
- All D3 code uses the fixed `width` and `height` — no recalculation needed

### preserveAspectRatio Values
| Value | Behavior |
|-------|----------|
| `xMidYMid meet` | Center and scale to fit (default, recommended) |
| `xMinYMin meet` | Align top-left, scale to fit |
| `none` | Stretch to fill (distorts) |
| `xMidYMid slice` | Center and scale to fill (may crop) |

### Pros and Cons
- **Pro:** Simplest approach, no JavaScript resize logic
- **Pro:** All coordinates stay consistent
- **Con:** Text and stroke widths scale with SVG (may become too small/large)
- **Con:** Fixed aspect ratio may waste space

## ResizeObserver Approach

For charts that should re-render at new dimensions (not just scale):

### Vanilla D3
```js
function createChart(container) {
  const observer = new ResizeObserver(entries => {
    const { width, height } = entries[0].contentRect;
    render(width, height);
  });

  observer.observe(container);

  function render(width, height) {
    d3.select(container).select("svg").remove();

    const margin = { top: 20, right: 20, bottom: 30, left: 40 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const svg = d3.select(container)
      .append("svg")
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Build chart with innerWidth, innerHeight...
  }
}
```

### React Hook
```jsx
function useContainerDimensions(ref) {
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  useEffect(() => {
    if (!ref.current) return;

    const observer = new ResizeObserver(entries => {
      const { width, height } = entries[0].contentRect;
      setDimensions({ width, height });
    });

    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [ref]);

  return dimensions;
}

function Chart() {
  const containerRef = useRef();
  const { width, height } = useContainerDimensions(containerRef);

  return (
    <div ref={containerRef} style={{ width: "100%", height: "400px" }}>
      {width > 0 && <BarChart data={data} width={width} height={height} />}
    </div>
  );
}
```

### Debouncing Resize
```js
function debounce(fn, delay) {
  let timer;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

const observer = new ResizeObserver(debounce(entries => {
  const { width, height } = entries[0].contentRect;
  render(width, height);
}, 100));
```

## Fluid Layouts

### Percentage-Based Container
```css
.chart-container {
  width: 100%;
  max-width: 1200px;
  height: 0;
  padding-bottom: 56.25%;  /* 16:9 aspect ratio */
  position: relative;
}

.chart-container svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
```

### Flexible Margins
```js
function getMargins(width) {
  if (width < 400) return { top: 10, right: 10, bottom: 25, left: 30 };
  if (width < 768) return { top: 15, right: 15, bottom: 30, left: 40 };
  return { top: 20, right: 30, bottom: 40, left: 50 };
}
```

## Mobile Considerations

### Touch Events
```js
// Use pointer events (work for both touch and mouse)
selection
  .on("pointerenter", showTooltip)
  .on("pointermove", moveTooltip)
  .on("pointerleave", hideTooltip);
```

### Larger Hit Targets
```js
// Minimum 44px touch targets (WCAG)
const minBarWidth = 44;
const barWidth = Math.max(xScale.bandwidth(), minBarWidth);

// Invisible larger hit targets
svg.selectAll("rect.hit-target")
  .data(data)
  .join("rect")
    .attr("class", "hit-target")
    .attr("x", d => xScale(d.name) - 10)
    .attr("width", xScale.bandwidth() + 20)
    .attr("height", height)
    .attr("fill", "transparent")
    .on("pointerenter", showTooltip);
```

### Simplified Mobile Layouts
```js
const isMobile = width < 600;

// Fewer ticks on mobile
const xAxis = d3.axisBottom(xScale)
  .ticks(isMobile ? 4 : 8);

// Horizontal bars on mobile (more readable)
if (isMobile) {
  // Swap x and y scales
  // Use scaleBand for y-axis, scaleLinear for x-axis
}
```

## Responsive Axes and Labels

### Auto-Rotating Labels
```js
svg.select(".x-axis")
  .call(xAxis)
  .selectAll("text")
    .attr("transform", width < 600 ? "rotate(-45)" : "rotate(0)")
    .style("text-anchor", width < 600 ? "end" : "middle")
    .attr("dx", width < 600 ? "-0.5em" : "0")
    .attr("dy", width < 600 ? "0.15em" : "0.71em");
```

### Dynamic Tick Count
```js
const xAxis = d3.axisBottom(xScale)
  .ticks(Math.max(2, Math.floor(width / 100)));
```

### Truncating Labels
```js
svg.selectAll(".tick text")
  .text(function() {
    const text = d3.select(this).text();
    return text.length > 10 ? text.slice(0, 8) + "..." : text;
  });
```

### Responsive Font Sizes
```js
const fontSize = Math.max(10, Math.min(14, width / 50));
svg.selectAll("text").style("font-size", `${fontSize}px`);
```

## Breakpoint Strategies

### Chart Type Switching
```js
function renderChart(data, width, height) {
  if (width < 400) {
    renderCompactTable(data);        // too small for chart
  } else if (width < 600) {
    renderHorizontalBarChart(data);  // horizontal bars for mobile
  } else {
    renderVerticalBarChart(data);    // standard vertical bars
  }
}
```

### Progressive Detail
```js
const showLabels = width > 500;
const showGridLines = width > 400;
const showLegend = width > 600;
const showAnnotations = width > 800;
```

### Small Multiples → Single Chart
```js
if (width > 800) {
  // Render as small multiples (faceted)
  renderSmallMultiples(data, width, height);
} else {
  // Render as single chart with dropdown selector
  renderSingleChart(data, selectedCategory, width, height);
}
```
