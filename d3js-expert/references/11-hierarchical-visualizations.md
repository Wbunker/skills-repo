# Hierarchical Visualizations

Reference for tree layouts, treemaps, sunburst, partition, and circle-packing in D3.

## Table of Contents
- [d3-hierarchy Fundamentals](#d3-hierarchy-fundamentals)
- [Tree Layout](#tree-layout)
- [Treemap](#treemap)
- [Sunburst (Radial Partition)](#sunburst-radial-partition)
- [Partition Layout](#partition-layout)
- [Circle Packing](#circle-packing)
- [Stratify (Tabular to Hierarchical)](#stratify-tabular-to-hierarchical)

## d3-hierarchy Fundamentals

All hierarchical layouts start with `d3.hierarchy()` which converts nested data into a node tree.

### Creating a Hierarchy
```js
const data = {
  name: "root",
  children: [
    {
      name: "A",
      children: [
        { name: "A1", value: 10 },
        { name: "A2", value: 20 }
      ]
    },
    {
      name: "B",
      children: [
        { name: "B1", value: 15 },
        { name: "B2", value: 25 }
      ]
    }
  ]
};

const root = d3.hierarchy(data)
  .sum(d => d.value)        // compute aggregate values
  .sort((a, b) => b.value - a.value);  // sort by value
```

### Node Properties
```js
root.data        // original data object
root.children    // array of child nodes (or undefined for leaves)
root.parent      // parent node (null for root)
root.depth       // depth from root (root = 0)
root.height      // max distance to leaf (leaves = 0)
root.value       // aggregated value (set by .sum())
root.x           // computed position (set by layout)
root.y           // computed position (set by layout)
```

### Traversal Methods
```js
root.descendants()    // array of all nodes (pre-order)
root.ancestors()      // array from node to root
root.leaves()         // array of leaf nodes only
root.links()          // array of { source, target } links
root.path(other)      // path from this node to other
root.each(fn)         // breadth-first iteration
root.eachBefore(fn)   // pre-order depth-first
root.eachAfter(fn)    // post-order depth-first
root.find(fn)         // find first node matching predicate
```

### Custom Children Accessor
```js
const root = d3.hierarchy(data, d => d.subItems);  // use "subItems" instead of "children"
```

## Tree Layout

### Tidy Tree (d3.tree)
```js
const treeLayout = d3.tree()
  .size([width, height - 100]);  // [width, height] of drawing area

const root = d3.hierarchy(data);
treeLayout(root);  // computes x, y for each node

// Draw links
svg.selectAll("path.link")
  .data(root.links())
  .join("path")
    .attr("class", "link")
    .attr("d", d3.linkVertical()
      .x(d => d.x)
      .y(d => d.y))
    .attr("fill", "none")
    .attr("stroke", "#999");

// Draw nodes
svg.selectAll("circle.node")
  .data(root.descendants())
  .join("circle")
    .attr("class", "node")
    .attr("cx", d => d.x)
    .attr("cy", d => d.y)
    .attr("r", 5)
    .attr("fill", d => d.children ? "#555" : "#999");

// Labels
svg.selectAll("text")
  .data(root.descendants())
  .join("text")
    .attr("x", d => d.x)
    .attr("y", d => d.y - 10)
    .attr("text-anchor", "middle")
    .attr("font-size", "11px")
    .text(d => d.data.name);
```

### Horizontal Tree
```js
const treeLayout = d3.tree()
  .size([height, width - 160]);  // swap width/height

// Use linkHorizontal and swap x/y
svg.selectAll("path.link")
  .data(root.links())
  .join("path")
    .attr("d", d3.linkHorizontal()
      .x(d => d.y)     // y becomes horizontal position
      .y(d => d.x))    // x becomes vertical position
    .attr("fill", "none")
    .attr("stroke", "#ccc");

svg.selectAll("circle")
  .data(root.descendants())
  .join("circle")
    .attr("cx", d => d.y)
    .attr("cy", d => d.x)
    .attr("r", 4);
```

### Radial Tree
```js
const treeLayout = d3.tree()
  .size([2 * Math.PI, radius])     // [angle, radius]
  .separation((a, b) => (a.parent === b.parent ? 1 : 2) / a.depth);

treeLayout(root);

// Convert polar to cartesian
svg.selectAll("path.link")
  .data(root.links())
  .join("path")
    .attr("d", d3.linkRadial()
      .angle(d => d.x)
      .radius(d => d.y))
    .attr("fill", "none")
    .attr("stroke", "#999");

svg.selectAll("circle")
  .data(root.descendants())
  .join("circle")
    .attr("transform", d =>
      `rotate(${d.x * 180 / Math.PI - 90}) translate(${d.y},0)`)
    .attr("r", 3);
```

### Cluster Layout (leaves aligned)
```js
const clusterLayout = d3.cluster()
  .size([width, height - 100]);

clusterLayout(root);
// Same drawing code as tree
```

## Treemap

Treemaps show hierarchical data as nested rectangles sized by value.

### Basic Treemap
```js
const treemap = d3.treemap()
  .size([width, height])
  .padding(2)
  .round(true);

const root = d3.hierarchy(data)
  .sum(d => d.value)
  .sort((a, b) => b.value - a.value);

treemap(root);
// Each node now has: x0, y0, x1, y1

const color = d3.scaleOrdinal(d3.schemeCategory10);

svg.selectAll("rect")
  .data(root.leaves())
  .join("rect")
    .attr("x", d => d.x0)
    .attr("y", d => d.y0)
    .attr("width", d => d.x1 - d.x0)
    .attr("height", d => d.y1 - d.y0)
    .attr("fill", d => {
      while (d.depth > 1) d = d.parent;
      return color(d.data.name);
    })
    .attr("stroke", "white");

// Labels
svg.selectAll("text")
  .data(root.leaves())
  .join("text")
    .attr("x", d => d.x0 + 4)
    .attr("y", d => d.y0 + 14)
    .text(d => d.data.name)
    .attr("font-size", "11px")
    .attr("fill", "white")
    .each(function(d) {
      // Hide label if it doesn't fit
      if (this.getBBox().width > d.x1 - d.x0 - 8) {
        d3.select(this).remove();
      }
    });
```

### Treemap Tiling Methods
```js
d3.treemap().tile(d3.treemapSquarify);       // default — squarish
d3.treemap().tile(d3.treemapBinary);          // balanced binary split
d3.treemap().tile(d3.treemapSlice);           // horizontal slices
d3.treemap().tile(d3.treemapDice);            // vertical slices
d3.treemap().tile(d3.treemapSliceDice);       // alternating
d3.treemap().tile(d3.treemapResquarify);      // stable on update
```

### Nested Padding
```js
d3.treemap()
  .paddingOuter(4)    // padding around root
  .paddingTop(20)     // space for group labels
  .paddingInner(2);   // padding between siblings
```

## Sunburst (Radial Partition)

A sunburst displays hierarchy as concentric rings.

```js
const partition = d3.partition()
  .size([2 * Math.PI, radius]);

const root = d3.hierarchy(data)
  .sum(d => d.value)
  .sort((a, b) => b.value - a.value);

partition(root);
// Each node has: x0, x1 (angles), y0, y1 (radii)

const arc = d3.arc()
  .startAngle(d => d.x0)
  .endAngle(d => d.x1)
  .innerRadius(d => d.y0)
  .outerRadius(d => d.y1)
  .padAngle(0.005)
  .padRadius(radius / 2);

const color = d3.scaleOrdinal(d3.schemeCategory10);

svg.append("g")
  .attr("transform", `translate(${width/2},${height/2})`)
  .selectAll("path")
  .data(root.descendants().filter(d => d.depth))  // skip root
  .join("path")
    .attr("d", arc)
    .attr("fill", d => {
      while (d.depth > 1) d = d.parent;
      return color(d.data.name);
    })
    .attr("fill-opacity", d => 1 - d.depth * 0.15)
    .attr("stroke", "white");
```

### Zoomable Sunburst
```js
function clicked(event, p) {
  const target = root.sum(d => d.value);

  root.each(d => {
    d.target = {
      x0: Math.max(0, Math.min(1, (d.x0 - p.x0) / (p.x1 - p.x0))) * 2 * Math.PI,
      x1: Math.max(0, Math.min(1, (d.x1 - p.x0) / (p.x1 - p.x0))) * 2 * Math.PI,
      y0: Math.max(0, d.y0 - p.depth),
      y1: Math.max(0, d.y1 - p.depth)
    };
  });

  const t = svg.transition().duration(750);

  paths.transition(t)
    .tween("data", d => {
      const i = d3.interpolate(d.current, d.target);
      return t => d.current = i(t);
    })
    .attrTween("d", d => () => arc(d.current));
}
```

## Partition Layout

Linear partition — like a sunburst unwrapped into rectangles:

```js
const partition = d3.partition()
  .size([height, width])
  .padding(1)
  .round(true);

const root = d3.hierarchy(data)
  .sum(d => d.value)
  .sort((a, b) => b.value - a.value);

partition(root);
// x0, x1 = vertical extent; y0, y1 = horizontal extent (depth)

svg.selectAll("rect")
  .data(root.descendants())
  .join("rect")
    .attr("x", d => d.y0)
    .attr("y", d => d.x0)
    .attr("width", d => d.y1 - d.y0)
    .attr("height", d => d.x1 - d.x0)
    .attr("fill", d => color(d.data.name));
```

## Circle Packing

Nested circles sized by value:

```js
const pack = d3.pack()
  .size([width, height])
  .padding(3);

const root = d3.hierarchy(data)
  .sum(d => d.value)
  .sort((a, b) => b.value - a.value);

pack(root);
// Each node has: x, y, r (center and radius)

svg.selectAll("circle")
  .data(root.descendants())
  .join("circle")
    .attr("cx", d => d.x)
    .attr("cy", d => d.y)
    .attr("r", d => d.r)
    .attr("fill", d => d.children ? "none" : color(d.data.name))
    .attr("stroke", d => d.children ? "#999" : "none")
    .attr("fill-opacity", 0.7);

// Labels on leaves
svg.selectAll("text")
  .data(root.leaves())
  .join("text")
    .attr("x", d => d.x)
    .attr("y", d => d.y)
    .attr("text-anchor", "middle")
    .attr("dy", "0.35em")
    .text(d => d.data.name)
    .attr("font-size", d => Math.min(d.r / 3, 12));
```

## Stratify (Tabular to Hierarchical)

Convert flat/tabular data (with parent references) to a hierarchy:

```js
const tabularData = [
  { id: "root", parent: null },
  { id: "A", parent: "root", value: 10 },
  { id: "B", parent: "root", value: 20 },
  { id: "A1", parent: "A", value: 5 },
  { id: "A2", parent: "A", value: 8 }
];

const stratify = d3.stratify()
  .id(d => d.id)
  .parentId(d => d.parent);

const root = stratify(tabularData)
  .sum(d => d.value)
  .sort((a, b) => b.value - a.value);

// Now use any hierarchical layout
d3.treemap().size([width, height])(root);
```

### From CSV Path Data
```js
// Data like: path, value
// "root/A/A1", 10
// "root/A/A2", 20
// "root/B/B1", 15

const stratify = d3.stratify()
  .id(d => d.path)
  .parentId(d => d.path.substring(0, d.path.lastIndexOf("/")));
```
