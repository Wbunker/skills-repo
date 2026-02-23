# Geospatial Information Visualizations

Reference for geographic projections, GeoJSON/TopoJSON, maps, and spatial visualizations in D3.

## Table of Contents
- [GeoJSON and TopoJSON](#geojson-and-topojson)
- [Projections](#projections)
- [Path Generator](#path-generator)
- [Choropleth Maps](#choropleth-maps)
- [Point Maps](#point-maps)
- [Graticules and Globes](#graticules-and-globes)
- [Map Interactions](#map-interactions)
- [Tile Maps](#tile-maps)

## GeoJSON and TopoJSON

### GeoJSON Structure
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": { "name": "California", "code": "CA" },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[lng, lat], [lng, lat], ...]]
      }
    }
  ]
}
```

### TopoJSON
TopoJSON is a compressed format that encodes topology (shared borders):

```js
import * as topojson from "topojson-client";

const topoData = await d3.json("world-110m.json");

// Convert TopoJSON to GeoJSON
const countries = topojson.feature(topoData, topoData.objects.countries);
// Returns a FeatureCollection

// Get borders (shared edges between polygons)
const borders = topojson.mesh(topoData, topoData.objects.countries,
  (a, b) => a !== b);  // only shared borders
```

### Common Data Sources
- **Natural Earth**: naturalearthdata.com — world, countries, states
- **US Census TIGER**: census.gov — US states, counties, tracts
- **US Atlas**: `npm install us-atlas` — pre-built US TopoJSON
- **World Atlas**: `npm install world-atlas` — pre-built world TopoJSON

```js
// US Atlas example
import us from "us-atlas/states-10m.json";
const states = topojson.feature(us, us.objects.states);
const stateBorders = topojson.mesh(us, us.objects.states, (a, b) => a !== b);
```

## Projections

Projections convert spherical coordinates (longitude, latitude) to 2D screen coordinates.

### Common Projections
```js
// Mercator — most familiar, distorts area at poles
const projection = d3.geoMercator()
  .fitSize([width, height], geojson);

// Equal-area — preserves area (good for choropleths)
const projection = d3.geoEqualEarth()
  .fitSize([width, height], geojson);

// Natural Earth — compromise, aesthetically pleasing
const projection = d3.geoNaturalEarth1()
  .fitSize([width, height], geojson);

// Albers USA — conic, includes Alaska and Hawaii insets
const projection = d3.geoAlbersUsa()
  .fitSize([width, height], geojson);

// Albers — general conic equal-area
const projection = d3.geoAlbers()
  .fitSize([width, height], geojson);

// Orthographic — globe view
const projection = d3.geoOrthographic()
  .rotate([-20, -30])  // center on [lon, lat]
  .fitSize([width, height], { type: "Sphere" });
```

### Projection Methods
```js
projection([longitude, latitude]);        // → [x, y] pixels
projection.invert([x, y]);               // → [longitude, latitude]

projection.fitSize([width, height], geojson);   // auto-fit to bounds
projection.fitExtent([[20, 20], [width-20, height-20]], geojson); // with margins

projection.scale(200);                    // zoom level
projection.translate([width/2, height/2]); // center point
projection.center([lng, lat]);            // geographic center
projection.rotate([lambda, phi, gamma]);  // rotation angles
projection.clipAngle(90);                 // clip to hemisphere (orthographic)
```

### Choosing a Projection
| Projection | Preserves | Best For |
|-----------|-----------|----------|
| `geoMercator` | Angles/shapes | Navigation, web maps |
| `geoAlbersUsa` | Area | US maps with AK/HI |
| `geoEqualEarth` | Area | World choropleths |
| `geoNaturalEarth1` | Nothing exactly | Aesthetic world maps |
| `geoOrthographic` | Angles (near center) | Globe views |
| `geoConicEqualArea` | Area | Regional maps |

## Path Generator

The geo path generator converts GeoJSON geometry to SVG path strings.

```js
const projection = d3.geoAlbersUsa()
  .fitSize([width, height], geojson);

const path = d3.geoPath(projection);

// Draw features
svg.selectAll("path")
  .data(geojson.features)
  .join("path")
    .attr("d", path)
    .attr("fill", "#ccc")
    .attr("stroke", "white")
    .attr("stroke-width", 0.5);

// Useful path methods
path.area(feature);       // area in pixels
path.centroid(feature);   // [x, y] center of feature
path.bounds(feature);     // [[x0, y0], [x1, y1]] bounding box
```

## Choropleth Maps

Color regions by data value:

```js
// Load both geography and data
const [us, data] = await Promise.all([
  d3.json("states-10m.json"),
  d3.csv("state-data.csv", d => ({ fips: d.fips, value: +d.value }))
]);

const states = topojson.feature(us, us.objects.states);
const dataMap = new Map(data.map(d => [d.fips, d.value]));

const color = d3.scaleQuantize()
  .domain(d3.extent(data, d => d.value))
  .range(d3.schemeBlues[9]);

const projection = d3.geoAlbersUsa()
  .fitSize([width, height], states);

const path = d3.geoPath(projection);

svg.selectAll("path")
  .data(states.features)
  .join("path")
    .attr("d", path)
    .attr("fill", d => {
      const value = dataMap.get(d.id);
      return value != null ? color(value) : "#eee";
    })
    .attr("stroke", "white")
    .attr("stroke-width", 0.5);

// State borders
svg.append("path")
  .datum(topojson.mesh(us, us.objects.states, (a, b) => a !== b))
  .attr("d", path)
  .attr("fill", "none")
  .attr("stroke", "white")
  .attr("stroke-width", 0.5);
```

### Legend for Choropleth
```js
const legendWidth = 260;
const legendHeight = 10;
const thresholds = color.thresholds();

const legendScale = d3.scaleLinear()
  .domain(color.domain())
  .range([0, legendWidth]);

const legend = svg.append("g")
  .attr("transform", `translate(${width - legendWidth - 20}, ${height - 40})`);

// Color rects
legend.selectAll("rect")
  .data(color.range())
  .join("rect")
    .attr("x", (d, i) => legendScale(i === 0 ? color.domain()[0] : thresholds[i - 1]))
    .attr("width", (d, i) => {
      const x0 = i === 0 ? color.domain()[0] : thresholds[i - 1];
      const x1 = i === thresholds.length ? color.domain()[1] : thresholds[i];
      return legendScale(x1) - legendScale(x0);
    })
    .attr("height", legendHeight)
    .attr("fill", d => d);

// Axis
legend.append("g")
  .attr("transform", `translate(0, ${legendHeight})`)
  .call(d3.axisBottom(legendScale).ticks(5).tickSize(3))
  .select(".domain").remove();
```

## Point Maps

Plot points (cities, events, etc.) on a map:

```js
// Project coordinates
svg.selectAll("circle")
  .data(cities)
  .join("circle")
    .attr("cx", d => projection([d.longitude, d.latitude])[0])
    .attr("cy", d => projection([d.longitude, d.latitude])[1])
    .attr("r", d => radiusScale(d.population))
    .attr("fill", "red")
    .attr("fill-opacity", 0.5)
    .attr("stroke", "red")
    .attr("stroke-width", 0.5);
```

### Handling Null Projections
Some projections return `null` for points outside the visible area:

```js
svg.selectAll("circle")
  .data(cities.filter(d => projection([d.longitude, d.latitude]) !== null))
  .join("circle")
    .attr("cx", d => projection([d.longitude, d.latitude])[0])
    .attr("cy", d => projection([d.longitude, d.latitude])[1])
    .attr("r", 3);
```

### Proportional Symbol Map
```js
const radiusScale = d3.scaleSqrt()
  .domain([0, d3.max(cities, d => d.population)])
  .range([0, 30]);

// Sort by size (draw large bubbles first so small ones are on top)
cities.sort((a, b) => b.population - a.population);
```

## Graticules and Globes

### Graticule (Grid Lines)
```js
const graticule = d3.geoGraticule();

svg.append("path")
  .datum(graticule())
  .attr("d", path)
  .attr("fill", "none")
  .attr("stroke", "#ddd")
  .attr("stroke-width", 0.5);

// Outline (sphere border)
svg.append("path")
  .datum({ type: "Sphere" })
  .attr("d", path)
  .attr("fill", "none")
  .attr("stroke", "black");
```

### Globe with Rotation
```js
const projection = d3.geoOrthographic()
  .scale(250)
  .translate([width / 2, height / 2])
  .clipAngle(90);

// Rotate on drag
const drag = d3.drag()
  .on("drag", (event) => {
    const rotate = projection.rotate();
    projection.rotate([
      rotate[0] + event.dx * 0.5,
      rotate[1] - event.dy * 0.5
    ]);
    // Re-render all paths
    svg.selectAll("path").attr("d", path);
  });

svg.call(drag);
```

### Auto-Rotating Globe
```js
const timer = d3.timer(elapsed => {
  projection.rotate([elapsed * 0.02, -20]);
  svg.selectAll("path.country").attr("d", path);
});

// Stop: timer.stop();
```

## Map Interactions

### Tooltip on Hover
```js
svg.selectAll("path.country")
  .on("mouseenter", (event, d) => {
    d3.select(event.currentTarget)
      .attr("stroke", "black")
      .attr("stroke-width", 2)
      .raise();

    tooltip
      .style("visibility", "visible")
      .html(`<strong>${d.properties.name}</strong><br/>Value: ${dataMap.get(d.id)}`);
  })
  .on("mousemove", (event) => {
    tooltip
      .style("top", (event.pageY - 10) + "px")
      .style("left", (event.pageX + 10) + "px");
  })
  .on("mouseleave", (event) => {
    d3.select(event.currentTarget)
      .attr("stroke", "white")
      .attr("stroke-width", 0.5);
    tooltip.style("visibility", "hidden");
  });
```

### Zoom on Map
```js
const zoom = d3.zoom()
  .scaleExtent([1, 8])
  .on("zoom", (event) => {
    svg.selectAll("path")
      .attr("transform", event.transform)
      .attr("stroke-width", 0.5 / event.transform.k);  // keep stroke constant
  });

svg.call(zoom);
```

### Click to Zoom to Feature
```js
function clicked(event, d) {
  const [[x0, y0], [x1, y1]] = path.bounds(d);
  const dx = x1 - x0, dy = y1 - y0;
  const x = (x0 + x1) / 2, y = (y0 + y1) / 2;
  const scale = Math.min(8, 0.9 / Math.max(dx / width, dy / height));
  const translate = [width / 2 - scale * x, height / 2 - scale * y];

  svg.transition().duration(750)
    .call(zoom.transform,
      d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale));
}
```

## Tile Maps

For slippy map backgrounds, use `d3-tile`:

```bash
npm install d3-tile
```

```js
import { tile } from "d3-tile";

const tileGenerator = tile()
  .size([width, height])
  .scale(projection.scale() * 2 * Math.PI)
  .translate(projection([0, 0]));

const tiles = tileGenerator();

svg.selectAll("image")
  .data(tiles)
  .join("image")
    .attr("xlink:href", d =>
      `https://tile.openstreetmap.org/${d[2]}/${d[0]}/${d[1]}.png`)
    .attr("x", d => (d[0] + tiles.translate[0]) * tiles.scale)
    .attr("y", d => (d[1] + tiles.translate[1]) * tiles.scale)
    .attr("width", tiles.scale)
    .attr("height", tiles.scale);
```
