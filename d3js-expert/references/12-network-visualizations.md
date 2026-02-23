# Network Visualizations

Reference for force-directed graphs, node-link diagrams, adjacency matrices, and network layouts in D3.

## Table of Contents
- [Force Simulation Fundamentals](#force-simulation-fundamentals)
- [Force Types](#force-types)
- [Basic Force-Directed Graph](#basic-force-directed-graph)
- [Customizing Force Layouts](#customizing-force-layouts)
- [Adjacency Matrices](#adjacency-matrices)
- [Arc Diagrams](#arc-diagrams)
- [Sankey Diagrams](#sankey-diagrams)
- [Interactive Networks](#interactive-networks)

## Force Simulation Fundamentals

`d3.forceSimulation` is a physics-based layout engine. It iteratively adjusts node positions based on forces until the system reaches equilibrium.

### Simulation Lifecycle
```js
const simulation = d3.forceSimulation(nodes)
  .force("charge", d3.forceManyBody())
  .force("center", d3.forceCenter(width / 2, height / 2))
  .on("tick", ticked);

function ticked() {
  // Update DOM positions from node.x, node.y
}
```

### Simulation Parameters
```js
simulation
  .alpha(1)                 // initial energy (0 to 1)
  .alphaMin(0.001)          // stop threshold
  .alphaDecay(0.0228)       // cooling rate (default)
  .alphaTarget(0)           // equilibrium alpha
  .velocityDecay(0.4);      // friction (0 = no friction, 1 = frozen)
```

### Controlling the Simulation
```js
simulation.stop();          // pause
simulation.restart();       // resume
simulation.tick();          // advance one step manually
simulation.alpha(1).restart(); // reheat and restart

// Run to completion synchronously (no animation)
simulation.stop();
for (let i = 0; i < 300; i++) simulation.tick();
// Now read node.x, node.y
```

## Force Types

### forceManyBody — Attraction/Repulsion
```js
d3.forceManyBody()
  .strength(-100)           // negative = repulsion (default -30)
  .distanceMin(1)           // minimum distance
  .distanceMax(500)         // maximum distance (Infinity = no limit)
  .theta(0.9);              // Barnes-Hut approximation (lower = more accurate, slower)
```

### forceLink — Edge Springs
```js
d3.forceLink(links)
  .id(d => d.id)            // node identity accessor
  .distance(100)            // target link length (default 30)
  .strength(d => 1 / Math.min(d.source.degree, d.target.degree)) // adaptive
  .iterations(1);           // constraint iterations per tick
```

### forceCenter — Gravity toward Center
```js
d3.forceCenter(width / 2, height / 2)
  .strength(0.1);           // default 1
```

### forceX / forceY — Positional Forces
```js
d3.forceX(width / 2).strength(0.1);  // pull toward x position
d3.forceY(height / 2).strength(0.1); // pull toward y position

// Group nodes by category
d3.forceX(d => groupXScale(d.group)).strength(0.3);
```

### forceCollide — Collision Detection
```js
d3.forceCollide()
  .radius(d => radiusScale(d.value) + 2)  // per-node radius
  .strength(0.7)                            // 0-1, enforcement strength
  .iterations(2);                           // iterations per tick
```

### forceRadial — Radial Positioning
```js
d3.forceRadial(100, width / 2, height / 2)  // radius, cx, cy
  .strength(d => d.type === "primary" ? 0.8 : 0.1);
```

## Basic Force-Directed Graph

```js
const nodes = [
  { id: "A" }, { id: "B" }, { id: "C" }, { id: "D" }
];

const links = [
  { source: "A", target: "B" },
  { source: "B", target: "C" },
  { source: "C", target: "D" },
  { source: "A", target: "D" }
];

const simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(links).id(d => d.id).distance(100))
  .force("charge", d3.forceManyBody().strength(-200))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("collide", d3.forceCollide(15));

// Draw links
const link = svg.selectAll("line.link")
  .data(links)
  .join("line")
    .attr("class", "link")
    .attr("stroke", "#999")
    .attr("stroke-width", 1.5);

// Draw nodes
const node = svg.selectAll("circle.node")
  .data(nodes)
  .join("circle")
    .attr("class", "node")
    .attr("r", 8)
    .attr("fill", "steelblue")
    .call(drag(simulation));  // attach drag behavior

// Labels
const label = svg.selectAll("text")
  .data(nodes)
  .join("text")
    .text(d => d.id)
    .attr("font-size", "12px")
    .attr("dx", 12)
    .attr("dy", 4);

// Update positions each tick
simulation.on("tick", () => {
  link
    .attr("x1", d => d.source.x)
    .attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x)
    .attr("y2", d => d.target.y);
  node
    .attr("cx", d => d.x)
    .attr("cy", d => d.y);
  label
    .attr("x", d => d.x)
    .attr("y", d => d.y);
});
```

### Drag Behavior for Force Graphs
```js
function drag(simulation) {
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
    d.fx = null;  // release (or keep pinned: don't set to null)
    d.fy = null;
  }
  return d3.drag()
    .on("start", dragStarted)
    .on("drag", dragged)
    .on("end", dragEnded);
}
```

## Customizing Force Layouts

### Sized Nodes
```js
const radiusScale = d3.scaleSqrt()
  .domain(d3.extent(nodes, d => d.value))
  .range([4, 30]);

simulation.force("collide", d3.forceCollide()
  .radius(d => radiusScale(d.value) + 2));

node.attr("r", d => radiusScale(d.value));
```

### Weighted Links
```js
const widthScale = d3.scaleLinear()
  .domain(d3.extent(links, d => d.weight))
  .range([1, 8]);

link.attr("stroke-width", d => widthScale(d.weight));

simulation.force("link")
  .strength(d => d.weight / d3.max(links, d => d.weight));
```

### Clustered Layout
```js
// Group nodes by cluster using forceX/forceY
const clusterCenters = {
  "Tech": { x: width * 0.25, y: height / 2 },
  "Finance": { x: width * 0.5, y: height / 2 },
  "Health": { x: width * 0.75, y: height / 2 }
};

simulation
  .force("x", d3.forceX(d => clusterCenters[d.group].x).strength(0.3))
  .force("y", d3.forceY(d => clusterCenters[d.group].y).strength(0.3));
```

### Bounding Box
```js
simulation.on("tick", () => {
  nodes.forEach(d => {
    d.x = Math.max(r, Math.min(width - r, d.x));
    d.y = Math.max(r, Math.min(height - r, d.y));
  });
  // update DOM...
});
```

## Adjacency Matrices

An alternative to node-link diagrams for dense networks:

```js
const matrix = [];
const nodeIndex = new Map(nodes.map((d, i) => [d.id, i]));
const n = nodes.length;

// Initialize
nodes.forEach((_, i) => {
  matrix[i] = Array(n).fill(0);
});

// Fill from links
links.forEach(link => {
  const i = nodeIndex.get(link.source);
  const j = nodeIndex.get(link.target);
  matrix[i][j] = link.weight || 1;
  matrix[j][i] = link.weight || 1;  // undirected
});

const cellSize = Math.min(width, height) / n;

// Draw cells
for (let i = 0; i < n; i++) {
  for (let j = 0; j < n; j++) {
    svg.append("rect")
      .attr("x", j * cellSize)
      .attr("y", i * cellSize)
      .attr("width", cellSize - 1)
      .attr("height", cellSize - 1)
      .attr("fill", matrix[i][j] ? colorScale(matrix[i][j]) : "#f5f5f5");
  }
}

// Labels
svg.selectAll("text.row")
  .data(nodes)
  .join("text")
    .attr("x", -5)
    .attr("y", (d, i) => i * cellSize + cellSize / 2)
    .attr("text-anchor", "end")
    .attr("dy", "0.35em")
    .text(d => d.id);
```

## Arc Diagrams

Nodes in a line with arced connections:

```js
const xScale = d3.scalePoint()
  .domain(nodes.map(d => d.id))
  .range([0, width])
  .padding(0.5);

// Arcs
svg.selectAll("path.arc")
  .data(links)
  .join("path")
    .attr("d", d => {
      const x1 = xScale(d.source.id || d.source);
      const x2 = xScale(d.target.id || d.target);
      const midX = (x1 + x2) / 2;
      const r = Math.abs(x2 - x1) / 2;
      return `M ${x1} ${height/2} A ${r} ${r} 0 0 1 ${x2} ${height/2}`;
    })
    .attr("fill", "none")
    .attr("stroke", "#999")
    .attr("stroke-opacity", 0.4);

// Nodes
svg.selectAll("circle")
  .data(nodes)
  .join("circle")
    .attr("cx", d => xScale(d.id))
    .attr("cy", height / 2)
    .attr("r", 5)
    .attr("fill", "steelblue");
```

## Sankey Diagrams

Flow diagrams showing quantities between stages. Use `d3-sankey` (separate package):

```bash
npm install d3-sankey
```

```js
import { sankey, sankeyLinkHorizontal, sankeyLeft } from "d3-sankey";

const sankeyGenerator = sankey()
  .nodeId(d => d.id)
  .nodeAlign(sankeyLeft)
  .nodeWidth(20)
  .nodePadding(10)
  .extent([[0, 0], [width, height]]);

const { nodes, links } = sankeyGenerator({
  nodes: data.nodes.map(d => ({ ...d })),
  links: data.links.map(d => ({ ...d }))
});

// Draw links (flows)
svg.selectAll("path.link")
  .data(links)
  .join("path")
    .attr("d", sankeyLinkHorizontal())
    .attr("fill", "none")
    .attr("stroke", d => color(d.source.id))
    .attr("stroke-opacity", 0.4)
    .attr("stroke-width", d => Math.max(1, d.width));

// Draw nodes
svg.selectAll("rect.node")
  .data(nodes)
  .join("rect")
    .attr("x", d => d.x0)
    .attr("y", d => d.y0)
    .attr("width", d => d.x1 - d.x0)
    .attr("height", d => d.y1 - d.y0)
    .attr("fill", d => color(d.id));

// Labels
svg.selectAll("text")
  .data(nodes)
  .join("text")
    .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
    .attr("y", d => (d.y0 + d.y1) / 2)
    .attr("dy", "0.35em")
    .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
    .text(d => d.id);
```

## Interactive Networks

### Node Search / Highlight
```js
function highlightNeighbors(selectedNode) {
  const neighbors = new Set();
  links.forEach(l => {
    if (l.source.id === selectedNode.id) neighbors.add(l.target.id);
    if (l.target.id === selectedNode.id) neighbors.add(l.source.id);
  });
  neighbors.add(selectedNode.id);

  node.attr("opacity", d => neighbors.has(d.id) ? 1 : 0.1);
  link.attr("opacity", d =>
    d.source.id === selectedNode.id || d.target.id === selectedNode.id ? 1 : 0.05
  );
}
```

### Zoom for Large Graphs
```js
const zoom = d3.zoom()
  .scaleExtent([0.1, 8])
  .on("zoom", event => {
    contentGroup.attr("transform", event.transform);
  });

svg.call(zoom);
```

### Fixed/Pinned Nodes
```js
function dragEnded(event, d) {
  if (!event.active) simulation.alphaTarget(0);
  // Keep pinned: don't null out fx/fy
  // d.fx = null; d.fy = null;
}

// Unpin on double-click
node.on("dblclick", (event, d) => {
  d.fx = null;
  d.fy = null;
  simulation.alpha(0.3).restart();
});
```
