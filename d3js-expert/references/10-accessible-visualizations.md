# Accessible Visualizations

Reference for making D3 visualizations accessible to all users.

## Table of Contents
- [Why Accessibility Matters](#why-accessibility-matters)
- [ARIA Attributes for SVG](#aria-attributes-for-svg)
- [Screen Reader Support](#screen-reader-support)
- [Keyboard Navigation](#keyboard-navigation)
- [Color Accessibility](#color-accessibility)
- [Text Alternatives](#text-alternatives)
- [Motion and Animation](#motion-and-animation)

## Why Accessibility Matters

- ~15% of the world's population has some form of disability
- Legal requirements (ADA, Section 508, EN 301 549)
- WCAG 2.1 Level AA is the standard target
- Accessible charts are better charts for everyone (clearer, more readable)

## ARIA Attributes for SVG

### Chart-Level Labels
```js
svg
  .attr("role", "img")
  .attr("aria-label", "Bar chart showing monthly sales for 2024")
  .attr("aria-describedby", "chart-description");

// Add hidden description
d3.select("#chart")
  .insert("p", "svg")
  .attr("id", "chart-description")
  .attr("class", "sr-only")
  .text("Sales peaked in July at $120K and were lowest in February at $45K.");
```

### Interactive Charts
```js
// For interactive charts, use role="application" or role="figure"
svg.attr("role", "figure")
  .attr("aria-label", "Interactive scatter plot of GDP vs Life Expectancy");
```

### Element-Level ARIA
```js
svg.selectAll("rect")
  .data(data)
  .join("rect")
    .attr("role", "listitem")
    .attr("aria-label", d => `${d.name}: ${d.value}`);

// Or use aria-roledescription for custom semantics
svg.selectAll("rect")
  .attr("aria-roledescription", "bar")
  .attr("aria-label", d => `${d.category}, value ${d.value}`);
```

### Group Structure
```js
// Use groups with role="list" for collections
const barGroup = svg.append("g")
  .attr("role", "list")
  .attr("aria-label", "Data series");

barGroup.selectAll("rect")
  .data(data)
  .join("rect")
    .attr("role", "listitem")
    .attr("aria-label", d => `${d.name}: ${d.value}`);
```

## Screen Reader Support

### Visually Hidden Summary
```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

### Data Table Alternative
```js
function addAccessibleTable(container, data, columns) {
  const table = d3.select(container)
    .append("table")
    .attr("class", "sr-only")
    .attr("aria-label", "Data table alternative for chart");

  // Header
  const thead = table.append("thead").append("tr");
  thead.selectAll("th")
    .data(columns)
    .join("th")
    .text(d => d.label);

  // Rows
  const tbody = table.append("tbody");
  const rows = tbody.selectAll("tr")
    .data(data)
    .join("tr");

  columns.forEach(col => {
    rows.append("td").text(d => col.format ? col.format(d[col.key]) : d[col.key]);
  });
}
```

### Live Regions for Updates
```js
const liveRegion = d3.select("body")
  .append("div")
  .attr("aria-live", "polite")
  .attr("aria-atomic", "true")
  .attr("class", "sr-only");

// Announce changes
function announceUpdate(message) {
  liveRegion.text(message);
}

// On data update
announceUpdate("Chart updated: March sales increased to $95K");
```

## Keyboard Navigation

### Focusable Elements
```js
svg.selectAll("rect")
  .attr("tabindex", 0)
  .attr("role", "listitem")
  .attr("aria-label", d => `${d.name}: ${d.value}`)
  .on("focus", function(event, d) {
    d3.select(this).attr("stroke", "black").attr("stroke-width", 2);
    showTooltip(event, d);
  })
  .on("blur", function() {
    d3.select(this).attr("stroke", null);
    hideTooltip();
  })
  .on("keydown", function(event, d) {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      handleClick(d);
    }
  });
```

### Arrow Key Navigation
```js
svg.selectAll("rect")
  .on("keydown", function(event, d) {
    const bars = svg.selectAll("rect").nodes();
    const index = bars.indexOf(this);

    switch (event.key) {
      case "ArrowRight":
      case "ArrowDown":
        event.preventDefault();
        if (index < bars.length - 1) bars[index + 1].focus();
        break;
      case "ArrowLeft":
      case "ArrowUp":
        event.preventDefault();
        if (index > 0) bars[index - 1].focus();
        break;
      case "Home":
        event.preventDefault();
        bars[0].focus();
        break;
      case "End":
        event.preventDefault();
        bars[bars.length - 1].focus();
        break;
    }
  });
```

### Focus Indicator Styling
```css
svg rect:focus,
svg circle:focus {
  outline: 2px solid #005fcc;
  outline-offset: 2px;
}

/* For browsers that don't support outline on SVG */
svg rect:focus,
svg circle:focus {
  stroke: #005fcc;
  stroke-width: 3;
}
```

## Color Accessibility

### Colorblind-Safe Palettes
```js
// Use perceptually uniform, colorblind-safe schemes
d3.interpolateViridis     // safe for all types of color blindness
d3.interpolatePlasma      // safe
d3.interpolateCividis     // designed for color vision deficiency
d3.schemeTableau10        // generally distinguishable

// Avoid: red-green combinations without other distinguishing features
```

### Contrast Ratios
- **WCAG AA:** 4.5:1 for normal text, 3:1 for large text and graphical objects
- **WCAG AAA:** 7:1 for normal text
- Use tools to verify: WebAIM Contrast Checker, Stark

### Redundant Encoding
Don't rely on color alone to convey meaning:

```js
// Bad: color is the only differentiator
svg.selectAll("circle")
  .attr("fill", d => d.category === "A" ? "red" : "green");

// Good: color + shape + label
svg.selectAll("path")
  .attr("d", d => {
    const symbol = d.category === "A" ? d3.symbolCircle : d3.symbolSquare;
    return d3.symbol().type(symbol).size(64)();
  })
  .attr("fill", d => colorScale(d.category));
```

### Patterns for Differentiation
```js
// SVG patterns as fill alternatives
const defs = svg.append("defs");

defs.append("pattern")
  .attr("id", "diagonal-stripe")
  .attr("patternUnits", "userSpaceOnUse")
  .attr("width", 8)
  .attr("height", 8)
  .append("path")
    .attr("d", "M-2,2 l4,-4 M0,8 l8,-8 M6,10 l4,-4")
    .attr("stroke", "black")
    .attr("stroke-width", 1.5);

// Use: .attr("fill", "url(#diagonal-stripe)")
```

### Direct Labeling
```js
// Label series directly instead of using a color-coded legend
svg.selectAll("text.series-label")
  .data(series)
  .join("text")
    .attr("x", d => xScale(d.values[d.values.length - 1].date) + 5)
    .attr("y", d => yScale(d.values[d.values.length - 1].value))
    .attr("dy", "0.35em")
    .text(d => d.name)
    .attr("fill", d => colorScale(d.name));
```

## Text Alternatives

### Title and Description
```html
<svg role="img" aria-labelledby="chart-title chart-desc">
  <title id="chart-title">Monthly Revenue 2024</title>
  <desc id="chart-desc">
    Bar chart showing monthly revenue. Revenue ranged from $45K in February
    to $120K in July, with an average of $82K.
  </desc>
</svg>
```

### Dynamic Descriptions
```js
function generateDescription(data) {
  const maxItem = data.reduce((a, b) => a.value > b.value ? a : b);
  const minItem = data.reduce((a, b) => a.value < b.value ? a : b);
  const avg = d3.mean(data, d => d.value);

  return `Chart showing ${data.length} data points. ` +
    `Highest: ${maxItem.name} at ${maxItem.value}. ` +
    `Lowest: ${minItem.name} at ${minItem.value}. ` +
    `Average: ${avg.toFixed(1)}.`;
}
```

## Motion and Animation

### Respecting prefers-reduced-motion
```js
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const transitionDuration = prefersReducedMotion ? 0 : 750;

svg.selectAll("rect")
  .transition()
  .duration(transitionDuration)
  .attr("height", d => yScale(d.value));
```

### CSS Approach
```css
@media (prefers-reduced-motion: reduce) {
  svg * {
    transition: none !important;
    animation: none !important;
  }
}
```

### Pause/Play Controls
```js
let animating = true;

d3.select("#pause-btn").on("click", () => {
  animating = !animating;
  if (animating) simulation.restart();
  else simulation.stop();
});
```
