# Visualizing Data in Snowsight

Reference for Snowsight dashboards, charts, data sampling, and collaboration.

## Table of Contents
- [Data Sampling](#data-sampling)
- [Interactive Results](#interactive-results)
- [Chart Visualizations](#chart-visualizations)
- [Dashboards](#dashboards)
- [Collaboration](#collaboration)

## Data Sampling

Snowflake supports sampling directly in SQL for exploring large tables.

### Row-Based Sampling
```sql
-- Fixed number of rows
SELECT * FROM large_table SAMPLE (1000 ROWS);

-- Random 1000 rows
SELECT * FROM large_table TABLESAMPLE (1000 ROWS);
```

### Fraction-Based Sampling
```sql
-- Approximately 10% of rows
SELECT * FROM large_table SAMPLE (10);

-- Bernoulli: row-level random (exact percentage, slower)
SELECT * FROM large_table SAMPLE BERNOULLI (10);

-- Block: partition-level random (approximate, faster)
SELECT * FROM large_table SAMPLE BLOCK (10);

-- System: synonym for Block
SELECT * FROM large_table SAMPLE SYSTEM (10);
```

### Sampling with Seed (reproducible)
```sql
SELECT * FROM large_table SAMPLE (10) SEED (42);
```

### Preview in Snowsight
- Click on any table in the Data browser
- **Preview** shows a sample of rows
- Column statistics shown automatically (min, max, distinct count, null count)

## Interactive Results

### Automatic Statistics
When query results appear in Snowsight:
- **Column headers** show data type icons
- **Numeric columns:** histogram distribution, min, max, average
- **String columns:** top values, distinct count
- **Date columns:** range, distribution
- Click any column header for detailed statistics

### Result Filtering and Sorting
- Click column headers to sort
- Use the filter icon to filter result rows
- Select columns to show/hide
- Download results as CSV

### Result Caching
- Results are cached for 24 hours in Snowsight
- Re-running the same query returns cached results instantly
- Click **Refresh** to force re-execution

## Chart Visualizations

Snowsight can render query results as charts directly.

### Creating Charts
1. Run a query in a worksheet
2. Click the **Chart** button above results
3. Select chart type
4. Configure axes, series, and formatting

### Available Chart Types
| Chart Type | Best For |
|-----------|----------|
| **Bar** | Categorical comparisons |
| **Line** | Time series, trends |
| **Area** | Cumulative trends |
| **Scatter** | Correlation between two variables |
| **Heatgrid** | Two-dimensional categorical patterns |
| **Scorecard** | Single KPI value |

### Chart Configuration
```
X-Axis: Choose column (categorical or date)
Y-Axis: Choose column(s) (numeric)
Series: Group by a categorical column (creates multiple lines/bars)
Aggregation: SUM, AVG, COUNT, MIN, MAX (applied to Y-axis)
Bucketing: Date granularity (day, week, month, quarter, year)
```

### Formatting Options
- **Axis labels and titles**
- **Legend position**
- **Color palette**
- **Stacking** (for bar/area charts)
- **Log scale** for y-axis
- **Label display** on data points

### Tips for Good Charts
- Aggregate data in your SQL query for best control
- Use `DATE_TRUNC` for time-based bucketing
- Limit series to 5-10 for readability
- Use `ORDER BY` to control x-axis ordering
- Use descriptive column aliases (they become axis labels)

```sql
-- Good query for charting
SELECT
  DATE_TRUNC('MONTH', order_date) AS month,
  region,
  SUM(amount) AS total_revenue,
  COUNT(*) AS order_count
FROM orders
WHERE order_date >= '2023-01-01'
GROUP BY 1, 2
ORDER BY 1;
```

## Dashboards

### Creating a Dashboard
1. Navigate to **Dashboards** in Snowsight
2. Click **+ Dashboard**
3. Name the dashboard
4. Add tiles (each tile is a query + chart or table)

### Adding Tiles
- **New Tile from SQL:** Write a query, then configure visualization
- **New Tile from existing worksheet:** Import a worksheet query
- Tiles auto-refresh when the dashboard is viewed (configurable)

### Tile Types
- **Chart tile:** Any chart type (bar, line, area, scatter, heatgrid)
- **Table tile:** Raw query results as a table
- **Scorecard tile:** Single KPI number

### Working with Tiles
```
- Drag and drop to rearrange
- Resize tiles by dragging edges
- Edit tile SQL by clicking into it
- Set individual refresh schedules per tile
- Each tile can use a different warehouse
```

### Dashboard Filters
- Add **dashboard-level filters** that apply to multiple tiles
- Use `:filter_name` in tile queries to reference dashboard filters
- Filter types: dropdown, date range, text input

```sql
-- Tile query using dashboard filter
SELECT region, SUM(amount)
FROM orders
WHERE order_date >= :start_date
  AND order_date <= :end_date
  AND region = :region_filter
GROUP BY 1;
```

## Collaboration

### Sharing Worksheets
- Share worksheets with specific users or roles
- Shared users can view and run (or edit if granted)
- **Link sharing:** Generate a URL to share

### Sharing Dashboards
- Share dashboards with users or roles
- Viewers can interact with filters but not edit
- Editors can modify tiles and layout

### Private Link Sharing
```
Dashboard → Share → Copy Link
```
- Requires Snowflake login to view
- Access controlled by Snowflake RBAC

### Collaboration Best Practices
- Create **shared folders** for team worksheets
- Use **meaningful names** for dashboards and tiles
- Set **default filters** to show relevant data
- Document data sources in tile descriptions
- Grant **viewer** access by default; **editor** only to dashboard maintainers
- Use **managed access schemas** for shared data to control grants centrally
