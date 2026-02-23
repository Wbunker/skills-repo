# Manipulating the DOM

Reference for D3 selections, data binding, and the enter/update/exit pattern.

## Table of Contents
- [Selections](#selections)
- [Modifying Elements](#modifying-elements)
- [The Data Join](#the-data-join)
- [Enter, Update, Exit](#enter-update-exit)
- [selection.join()](#selectionjoin)
- [Key Functions](#key-functions)
- [Nested Selections](#nested-selections)

## Selections

Selections are the foundation of D3. They wrap DOM elements and provide D3's chainable API.

### select() — Single Element
```js
// Select by CSS selector (first match only)
d3.select("#chart");
d3.select(".bar");
d3.select("svg");
d3.select("body");

// Select from within a selection
const svg = d3.select("svg");
svg.select("g.axis");  // first <g class="axis"> inside svg
```

### selectAll() — Multiple Elements
```js
// Select all matching elements
d3.selectAll("circle");
d3.selectAll(".bar");
d3.selectAll("rect.highlight");

// From a parent selection
svg.selectAll("rect");
```

### Selection Properties
```js
const sel = d3.selectAll("circle");
sel.size();    // number of elements
sel.empty();   // true if no elements matched
sel.node();    // first DOM element
sel.nodes();   // array of all DOM elements
```

## Modifying Elements

### Setting Attributes
```js
d3.selectAll("circle")
  .attr("r", 10)
  .attr("fill", "steelblue")
  .attr("cx", (d, i) => i * 50 + 25);  // accessor function
```

### Setting Styles
```js
d3.selectAll("rect")
  .style("fill", "orange")
  .style("stroke", "black")
  .style("stroke-width", "2px")
  .style("opacity", 0.7);
```

### Setting Text Content
```js
d3.selectAll("text")
  .text(d => d.label);  // set text from data
```

### Setting HTML Content
```js
d3.select("#tooltip")
  .html(`<strong>${d.name}</strong><br/>Value: ${d.value}`);
```

### Adding and Removing Elements
```js
// Append a new child element
svg.append("circle")
  .attr("cx", 100)
  .attr("cy", 100)
  .attr("r", 20);

// Insert before a specific element
svg.insert("rect", "text");  // insert rect before first text

// Remove elements
d3.selectAll(".old").remove();
```

### Classed, Property, Each
```js
// Toggle CSS classes
selection.classed("highlighted", true);
selection.classed("highlighted", d => d.value > 50);

// Set DOM properties (e.g., checked, value)
d3.select("input").property("value", "hello");

// Iterate over each element
selection.each(function(d, i) {
  const el = d3.select(this);
  // do something with each element
});
```

## The Data Join

Data binding connects an array of data to a selection of DOM elements.

```js
const data = [10, 20, 30, 40, 50];

// Bind data to existing <rect> elements
const bars = svg.selectAll("rect")
  .data(data);
```

**What happens:**
- D3 matches data items to DOM elements by index (default)
- Creates three sub-selections: **enter**, **update**, **exit**

## Enter, Update, Exit

The classic pattern (pre-D3 v5):

```js
const data = [10, 20, 30, 40, 50];

// Bind data
const bars = svg.selectAll("rect").data(data);

// ENTER: create new elements for data without DOM matches
bars.enter()
  .append("rect")
    .attr("x", (d, i) => i * 60)
    .attr("y", d => height - d * 5)
    .attr("width", 50)
    .attr("height", d => d * 5)
    .attr("fill", "steelblue");

// UPDATE: modify existing elements that have data
bars
  .attr("y", d => height - d * 5)
  .attr("height", d => d * 5);

// EXIT: remove elements that no longer have data
bars.exit().remove();
```

### Merge (combining enter + update)
```js
bars.enter()
  .append("rect")
  .merge(bars)  // merge enter and update selections
    .attr("x", (d, i) => i * 60)
    .attr("y", d => height - d * 5)
    .attr("width", 50)
    .attr("height", d => d * 5)
    .attr("fill", "steelblue");

bars.exit().remove();
```

## selection.join()

The modern D3 v7 approach — cleaner and more concise:

```js
const data = [10, 20, 30, 40, 50];

svg.selectAll("rect")
  .data(data)
  .join("rect")  // handles enter, update, and exit automatically
    .attr("x", (d, i) => i * 60)
    .attr("y", d => height - d * 5)
    .attr("width", 50)
    .attr("height", d => d * 5)
    .attr("fill", "steelblue");
```

### Customizing join phases
```js
svg.selectAll("rect")
  .data(data)
  .join(
    enter => enter.append("rect")
      .attr("fill", "green")
      .attr("opacity", 0)
      .call(enter => enter.transition()
        .attr("opacity", 1)),
    update => update
      .attr("fill", "steelblue")
      .call(update => update.transition()
        .attr("y", d => yScale(d))),
    exit => exit
      .call(exit => exit.transition()
        .attr("opacity", 0)
        .remove())
  );
```

## Key Functions

By default, data is matched to elements by index. Use a key function for stable identity:

```js
const data = [
  { id: "a", value: 10 },
  { id: "b", value: 20 },
  { id: "c", value: 30 }
];

svg.selectAll("rect")
  .data(data, d => d.id)  // key function — match by id
  .join("rect")
    .attr("x", (d, i) => i * 60)
    .attr("height", d => d.value * 5);
```

**Why key functions matter:**
- Without keys: reordering data causes elements to rebind to wrong data
- With keys: elements maintain identity across data updates
- Critical for transitions and animation continuity
- Essential when data order changes or items are added/removed in the middle

## Nested Selections

For grouped/nested data, use nested selections:

```js
const dataset = [
  { category: "A", values: [1, 2, 3] },
  { category: "B", values: [4, 5, 6] }
];

// Create groups
const groups = svg.selectAll("g")
  .data(dataset)
  .join("g")
    .attr("transform", (d, i) => `translate(0, ${i * 100})`);

// Create rects within each group
groups.selectAll("rect")
  .data(d => d.values)  // accessor returns nested array
  .join("rect")
    .attr("x", (d, i) => i * 60)
    .attr("width", 50)
    .attr("height", d => d * 20)
    .attr("fill", "steelblue");
```

### Common Patterns

**Accessor functions** — D3 callbacks receive `(datum, index, nodes)`:
```js
.attr("fill", (d, i, nodes) => {
  // d = bound datum
  // i = index within selection
  // nodes = array of DOM elements in the selection
  return d.value > 50 ? "red" : "blue";
})
```

**Calling functions on selections:**
```js
function setupAxis(selection) {
  selection
    .attr("class", "axis")
    .call(d3.axisBottom(xScale));
}

svg.append("g")
  .attr("transform", `translate(0, ${height})`)
  .call(setupAxis);
```

**selection.call()** is essential for axes and reusable components — it passes the selection to a function and returns the selection for continued chaining.
