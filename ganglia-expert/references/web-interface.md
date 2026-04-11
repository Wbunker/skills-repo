# Ganglia Web Interface (gweb)

From Chapter 3 of *Monitoring with Ganglia* by Bernard Li (O'Reilly).

## Installation

### Apache + PHP (Classic gweb)

```bash
# RHEL/CentOS
yum install ganglia-web httpd php php-gd rrdtool

# Debian/Ubuntu
apt-get install ganglia-webfrontend

# symlink into Apache docroot (Debian path)
ln -s /usr/share/ganglia-webfrontend /var/www/html/ganglia
```

Apache virtual host snippet:

```apache
Alias /ganglia /usr/share/ganglia-webfrontend
<Directory "/usr/share/ganglia-webfrontend">
    AllowOverride None
    Require all granted
</Directory>
```

### Django/Python gweb (Newer)

```bash
pip install ganglia-web   # or clone from github.com/ganglia/ganglia-web
python manage.py runserver 0.0.0.0:8000
```

## Configuration

Primary config: `/etc/ganglia/conf.php` (PHP) or `conf.d/` directory.

### Key conf.php Settings

```php
<?php
# Path to gmetad RRD root
$conf['rrds'] = "/var/lib/ganglia/rrds";

# gmetad interactive port (for live XML queries)
$conf['gmetad_root'] = "localhost";
$conf['gmetad_port'] = 8652;

# Default time range shown on graphs
$conf['default_time_range'] = "1hour";

# Template directory
$conf['template_dir'] = "templates/default";

# Whether to show offline hosts in cluster view
$conf['show_stale_hosts'] = false;

# Colors for graph backgrounds
$conf['graph_bgcolor'] = "FFFFFF";
?>
```

### Template System

gweb uses PHP templates in `templates/` directory. Common customizations:

- `templates/default/header.php` — page header, logo
- `templates/default/footer.php` — footer links
- `graph.php` — individual metric graph rendering

Create a custom template by copying `default/` and editing.

## Navigating the UI

### URL Structure

```
http://ganglia.example.com/ganglia/?
  c=<cluster_name>       # cluster filter
  h=<hostname>           # host filter (shows single-host view)
  m=<metric_name>        # metric to graph
  r=<range>              # time range: 1hour, 2hour, 4hour, day, week, month, year
  s=<sort>               # sort: descending, ascending, by_name
  hc=<count>             # hosts per column in grid view
  sh=<bool>              # show host listing
  z=<size>               # graph size: small, medium, large
```

Example — show cpu_user for all nodes in my_cluster over the last day:

```
http://ganglia.example.com/ganglia/?c=my_cluster&m=cpu_user&r=day&s=descending
```

### Views

| View | How to get there | Shows |
|------|-----------------|-------|
| **Grid view** | Top-level URL | All clusters, aggregated metrics |
| **Cluster view** | Click cluster name | All nodes in cluster, mini-graphs |
| **Host view** | Click node name | All metrics for one node |
| **Metric view** | Click metric name | That metric across all cluster nodes |

## Graph Parameters

Individual graphs are rendered by `graph.php`:

```
graph.php?
  c=my_cluster          # cluster name
  h=node01              # host (omit for cluster summary)
  m=cpu_user            # metric name
  r=1hour               # time range
  z=large               # size: small (width=250), medium (500), large (800)
  t=<timestamp>         # end time (Unix epoch), defaults to now
  bgcolor=FFFFFF        # hex background color
  fgcolor=000000        # hex foreground
  vlabel=<label>        # Y-axis label override
```

## Custom Dashboards

### Using `ganglia-web` Aggregate Graphs

gweb can aggregate multiple metrics into one graph using `aggregate_graphs.conf`:

```php
$conf['graphs']['io_summary'] = array(
  'title'   => 'I/O Summary',
  'series'  => array(
    array('metric' => 'disk_read',  'color' => '00FF00', 'label' => 'Reads'),
    array('metric' => 'disk_write', 'color' => 'FF0000', 'label' => 'Writes'),
  ),
);
```

### Embedding Graphs in Other Pages

Graphs are plain PNG images — embed anywhere:

```html
<img src="http://ganglia.example.com/ganglia/graph.php?c=my_cluster&m=cpu_user&r=day&z=small" />
```

### JSON / XML Data Access

gweb exposes a JSON endpoint for dashboard integration:

```
# Latest values for all metrics in a cluster
http://ganglia.example.com/ganglia/api/metrics.php?cluster=my_cluster

# Single metric
http://ganglia.example.com/ganglia/api/metrics.php?cluster=my_cluster&host=node01&metric=cpu_user
```

## Host Sorting and Filtering

Cluster view URL parameters for large clusters:

```
?c=my_cluster
  &s=descending    # sort metric high-to-low (highlights busy nodes)
  &m=cpu_user      # sort by this metric
  &hc=4            # 4 hosts per row
  &sh=1            # show host name list
  &mc=12           # max hosts to show
```

## Access Control

gweb has no built-in authentication — rely on Apache:

```apache
<Location /ganglia>
    AuthType Basic
    AuthName "Ganglia"
    AuthUserFile /etc/ganglia/.htpasswd
    Require valid-user
</Location>
```

For read-only public access to graphs but restricted admin pages, use `<Location>` blocks per subdirectory.

## Troubleshooting gweb

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Blank page | PHP errors | Check Apache error log; enable `display_errors` temporarily |
| "No data sources defined" | `$conf['rrds']` wrong | Verify path and permissions on RRD directory |
| Stale graphs | gmetad not running | `systemctl status gmetad`; check gmetad log |
| Missing metric | gmond module not loaded | Check gmond.conf `include` path; `gstat -a` |
| Graph shows "NaN" | RRD type mismatch | Delete and recreate RRD for that metric |
