# Integrating D3 in a Frontend Framework

Reference for using D3.js with React, Svelte, and Vue.

## Table of Contents
- [Integration Approaches](#integration-approaches)
- [D3 with React](#d3-with-react)
- [D3 with Svelte](#d3-with-svelte)
- [D3 with Vue](#d3-with-vue)
- [Common Patterns](#common-patterns)

## Integration Approaches

There are two fundamental approaches to combining D3 with a frontend framework:

### Approach 1: D3 for Math, Framework for DOM
- Use D3 only for scales, layouts, generators, and data transformation
- Let the framework (React/Svelte/Vue) handle DOM rendering
- **Preferred for most use cases** — idiomatic, testable, component-friendly

### Approach 2: D3 for Everything (ref-based)
- Give D3 a DOM reference (via `useRef`/`bind:this`) and let D3 manage a subtree
- Use for complex interactions (zoom, brush, drag, force) that are hard to replicate in the framework
- The framework renders a container; D3 owns everything inside

### When to Use Which
| Feature | Framework DOM | D3 DOM |
|---------|--------------|--------|
| Simple charts (bars, lines, pies) | Preferred | Works |
| Axes | Either | D3's axis generator is convenient |
| Transitions | Framework animation libs | D3 transitions |
| Zoom/Brush/Drag | Hard to replicate | **Use D3** |
| Force simulation | Possible but complex | **Use D3** |
| Server-side rendering | Possible | Not possible |
| Testing | Easy | Requires DOM |

## D3 with React

### Approach 1: React Renders SVG, D3 for Math
```jsx
import { useMemo } from "react";
import { scaleLinear, scaleBand, max } from "d3";

function BarChart({ data, width, height }) {
  const margin = { top: 20, right: 20, bottom: 30, left: 40 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  const xScale = useMemo(() =>
    scaleBand()
      .domain(data.map(d => d.name))
      .range([0, innerWidth])
      .padding(0.2),
    [data, innerWidth]
  );

  const yScale = useMemo(() =>
    scaleLinear()
      .domain([0, max(data, d => d.value)])
      .range([innerHeight, 0])
      .nice(),
    [data, innerHeight]
  );

  return (
    <svg width={width} height={height}>
      <g transform={`translate(${margin.left},${margin.top})`}>
        {data.map(d => (
          <rect
            key={d.name}
            x={xScale(d.name)}
            y={yScale(d.value)}
            width={xScale.bandwidth()}
            height={innerHeight - yScale(d.value)}
            fill="steelblue"
          />
        ))}
        <AxisBottom scale={xScale} transform={`translate(0,${innerHeight})`} />
        <AxisLeft scale={yScale} />
      </g>
    </svg>
  );
}
```

### React Axis Component
```jsx
function AxisBottom({ scale, transform }) {
  const ticks = scale.domain();
  return (
    <g transform={transform}>
      <line x1={0} x2={scale.range()[1]} stroke="black" />
      {ticks.map(tick => (
        <g key={tick} transform={`translate(${scale(tick) + scale.bandwidth() / 2},0)`}>
          <line y2={6} stroke="black" />
          <text y={20} textAnchor="middle" fontSize="12">{tick}</text>
        </g>
      ))}
    </g>
  );
}

function AxisLeft({ scale }) {
  const ticks = scale.ticks(5);
  return (
    <g>
      <line y1={scale.range()[0]} y2={scale.range()[1]} stroke="black" />
      {ticks.map(tick => (
        <g key={tick} transform={`translate(0,${scale(tick)})`}>
          <line x2={-6} stroke="black" />
          <text x={-10} dy="0.32em" textAnchor="end" fontSize="12">{tick}</text>
        </g>
      ))}
    </g>
  );
}
```

### Approach 2: D3 Manages DOM via useRef
```jsx
import { useRef, useEffect } from "react";
import * as d3 from "d3";

function ForceGraph({ nodes, links, width, height }) {
  const svgRef = useRef();

  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();  // clear previous render

    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id))
      .force("charge", d3.forceManyBody().strength(-100))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg.selectAll("line")
      .data(links)
      .join("line")
        .attr("stroke", "#999");

    const node = svg.selectAll("circle")
      .data(nodes)
      .join("circle")
        .attr("r", 5)
        .attr("fill", "steelblue")
        .call(d3.drag()
          .on("start", dragStarted)
          .on("drag", dragged)
          .on("end", dragEnded));

    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);
      node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);
    });

    function dragStarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x; d.fy = d.y;
    }
    function dragged(event, d) { d.fx = event.x; d.fy = event.y; }
    function dragEnded(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null; d.fy = null;
    }

    return () => simulation.stop();
  }, [nodes, links, width, height]);

  return <svg ref={svgRef} width={width} height={height} />;
}
```

### Using D3 Axis with useRef (hybrid)
```jsx
function Axis({ scale, orient, transform }) {
  const ref = useRef();

  useEffect(() => {
    const axisGenerator = orient === "bottom"
      ? d3.axisBottom(scale)
      : d3.axisLeft(scale);
    d3.select(ref.current).call(axisGenerator);
  }, [scale, orient]);

  return <g ref={ref} transform={transform} />;
}
```

## D3 with Svelte

Svelte's reactive declarations make it natural to use D3 for computation:

### Svelte: D3 for Math, Svelte for DOM
```svelte
<script>
  import { scaleLinear, scaleBand, max } from 'd3';

  export let data;
  export let width = 600;
  export let height = 400;

  const margin = { top: 20, right: 20, bottom: 30, left: 40 };

  $: innerWidth = width - margin.left - margin.right;
  $: innerHeight = height - margin.top - margin.bottom;

  $: xScale = scaleBand()
    .domain(data.map(d => d.name))
    .range([0, innerWidth])
    .padding(0.2);

  $: yScale = scaleLinear()
    .domain([0, max(data, d => d.value)])
    .range([innerHeight, 0])
    .nice();
</script>

<svg {width} {height}>
  <g transform="translate({margin.left},{margin.top})">
    {#each data as d (d.name)}
      <rect
        x={xScale(d.name)}
        y={yScale(d.value)}
        width={xScale.bandwidth()}
        height={innerHeight - yScale(d.value)}
        fill="steelblue"
      />
    {/each}
  </g>
</svg>
```

### Svelte: D3 Manages DOM via bind:this
```svelte
<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  let svgElement;

  onMount(() => {
    const svg = d3.select(svgElement);
    // D3 code here...
  });
</script>

<svg bind:this={svgElement} width={600} height={400} />
```

### Svelte Transitions with D3
```svelte
<script>
  import { tweened } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';

  const barHeight = tweened(0, { duration: 750, easing: cubicOut });
  $: $barHeight = yScale(data.value);
</script>
```

## D3 with Vue

### Vue 3 Composition API
```vue
<template>
  <svg :width="width" :height="height">
    <g :transform="`translate(${margin.left},${margin.top})`">
      <rect
        v-for="d in data"
        :key="d.name"
        :x="xScale(d.name)"
        :y="yScale(d.value)"
        :width="xScale.bandwidth()"
        :height="innerHeight - yScale(d.value)"
        fill="steelblue"
      />
    </g>
  </svg>
</template>

<script setup>
import { computed } from 'vue';
import { scaleLinear, scaleBand, max } from 'd3';

const props = defineProps(['data', 'width', 'height']);

const margin = { top: 20, right: 20, bottom: 30, left: 40 };
const innerWidth = computed(() => props.width - margin.left - margin.right);
const innerHeight = computed(() => props.height - margin.top - margin.bottom);

const xScale = computed(() =>
  scaleBand()
    .domain(props.data.map(d => d.name))
    .range([0, innerWidth.value])
    .padding(0.2)
);

const yScale = computed(() =>
  scaleLinear()
    .domain([0, max(props.data, d => d.value)])
    .range([innerHeight.value, 0])
    .nice()
);
</script>
```

### Vue: D3 via Template Ref
```vue
<template>
  <svg ref="svgRef" :width="width" :height="height" />
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import * as d3 from 'd3';

const svgRef = ref(null);

onMounted(() => {
  const svg = d3.select(svgRef.value);
  // D3 code here...
});
</script>
```

## Common Patterns

### Responsive Container
```jsx
// React hook for responsive dimensions
function useResizeObserver(ref) {
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const observer = new ResizeObserver(entries => {
      const { width, height } = entries[0].contentRect;
      setDimensions({ width, height });
    });
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [ref]);

  return dimensions;
}
```

### Memoizing Scales
```jsx
// Recompute scales only when data or dimensions change
const xScale = useMemo(() =>
  scaleBand().domain(data.map(d => d.name)).range([0, width]).padding(0.2),
  [data, width]
);
```

### Cleaning Up
```jsx
// Always clean up simulations, timers, and event listeners
useEffect(() => {
  const simulation = d3.forceSimulation(/*...*/);
  return () => simulation.stop();
}, []);
```
