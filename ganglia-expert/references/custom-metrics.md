# Custom Metrics and gmond Plugins

From Chapter 5 of *Monitoring with Ganglia* by Bernard Li (O'Reilly).

## Overview

gmond supports two plugin styles:

| Style | Language | When to use |
|-------|----------|-------------|
| **Python modules** | Python 2/3 | Quick to write; no compilation; preferred |
| **C shared libraries** | C | Performance-critical; same API as built-in modules |

Both styles are loaded via the `python_module` (or a C `.so`) declaration in gmond.conf and produce metrics that gossip and RRD-store exactly like built-in metrics.

## Python Module Structure

### File Location

Drop Python modules in the directory specified by the `python_module` path parameter (default: `/usr/lib64/ganglia/python_modules/` on RHEL or `/usr/lib/ganglia/python_modules/`).

Each module is a single `.py` file plus a companion `.pyconf` (or `.conf`) file in `/etc/ganglia/conf.d/`.

### Python Module Template

```python
# /usr/lib64/ganglia/python_modules/my_module.py

import time

# Module-level state
_last_collect = 0
_cached_values = {}

def metric_init(params):
    """
    Called once when gmond loads the module.
    params: dict from the module { param ... } block in gmond.conf.
    Must return a list of metric descriptor dicts.
    """
    global _last_collect

    # Optionally read params
    poll_interval = int(params.get('poll_interval', 10))

    descriptors = [
        {
            'name':        'my_queue_depth',
            'call_back':   get_queue_depth,
            'time_max':    poll_interval * 2,
            'value_type':  'uint',        # uint | float | string | double
            'units':       'jobs',
            'slope':       'both',        # zero | positive | negative | both
            'format':      '%u',          # printf format for display
            'description': 'Number of pending jobs in the work queue',
            'groups':      'application',
        },
        {
            'name':        'my_worker_count',
            'call_back':   get_worker_count,
            'time_max':    poll_interval * 2,
            'value_type':  'uint',
            'units':       'workers',
            'slope':       'both',
            'format':      '%u',
            'description': 'Active worker processes',
            'groups':      'application',
        },
    ]
    return descriptors


def get_queue_depth(name):
    """Callback: called every collection_interval to get metric value."""
    _refresh_cache()
    return _cached_values.get('queue_depth', 0)


def get_worker_count(name):
    _refresh_cache()
    return _cached_values.get('workers', 0)


def _refresh_cache():
    global _last_collect, _cached_values
    now = time.time()
    if now - _last_collect < 5:
        return  # don't re-read more often than 5 s
    _last_collect = now

    # Example: read from a socket, file, or HTTP endpoint
    try:
        with open('/var/run/myapp/stats', 'r') as f:
            for line in f:
                key, val = line.strip().split('=')
                _cached_values[key] = int(val)
    except Exception:
        pass  # leave stale values on error


def metric_cleanup():
    """Optional: called when gmond shuts down."""
    pass
```

### Companion .pyconf File

```
# /etc/ganglia/conf.d/my_module.pyconf

modules {
  module {
    name = "my_module"
    language = "python"

    # Optional params passed to metric_init()
    param poll_interval {
      value = 10
    }
  }
}

collection_group {
  collect_every = 10
  time_threshold = 20

  metric {
    name = "my_queue_depth"
    value_threshold = 1.0   /* only send if value changed by >= 1 */
    title = "Work Queue Depth"
  }

  metric {
    name = "my_worker_count"
    value_threshold = 1.0
    title = "Active Workers"
  }
}
```

### Descriptor Fields Reference

| Field | Required | Values | Notes |
|-------|----------|--------|-------|
| `name` | yes | string | Must be unique across all gmond modules |
| `call_back` | yes | callable | Function called each collection cycle |
| `time_max` | yes | int (seconds) | Max seconds between updates before metric is stale |
| `value_type` | yes | `uint`, `float`, `string`, `double` | Note: `uint` maps to uint32 |
| `units` | yes | string | Display units (can be empty string) |
| `slope` | yes | `zero`, `positive`, `negative`, `both` | Affects RRD type |
| `format` | yes | printf format | e.g., `'%u'`, `'%.2f'`, `'%s'` |
| `description` | yes | string | Shown in gweb tooltip |
| `groups` | no | comma-separated string | Groups metrics in gweb |

## collection_group Settings

| Parameter | Default | Effect |
|-----------|---------|--------|
| `collect_every` | 20 | Seconds between metric collection calls |
| `time_threshold` | 90 | Force a send if metric hasn't been sent in this many seconds even if unchanged |
| `value_threshold` | 0.0 | Only send if metric changed by at least this amount |

## C Module Structure

C modules are shared libraries (`.so`) loaded by gmond. Less common than Python modules, but used for built-in metrics.

### C Module Interface

```c
/* my_module.c */
#include <gm_metric.h>
#include <stdlib.h>

static double get_cpu_nice(void) {
    /* read /proc/stat or similar */
    return 0.0;
}

static Ganglia_25metric my_metrics[] = {
    {
        0,                      /* key (auto-assigned) */
        "cpu_nice",             /* name */
        90,                     /* tmax */
        GANGLIA_VALUE_FLOAT,    /* type */
        "%",                    /* units */
        "both",                 /* slope */
        "%.1f",                 /* fmt */
        0,                      /* msg_size (0 = default) */
        "Percentage of CPU used by nice processes"  /* desc */
    },
    {0}  /* sentinel */
};

mmodule my_module = {
    STD_MMODULE_STUFF,
    NULL,           /* init */
    NULL,           /* cleanup */
    my_metrics,
    NULL            /* handler — NULL means use get_<metric_name> functions */
};
```

Compile:

```bash
gcc -shared -fPIC -o my_module.so my_module.c \
    $(pkg-config --cflags --libs ganglia)
cp my_module.so /usr/lib64/ganglia/
```

Then reference in gmond.conf:

```
module {
  name = "my_module"
  path = "/usr/lib64/ganglia/my_module.so"
}
```

## Activating the Python Module Loader

Ensure gmond.conf loads `modpython.so`:

```
modules {
  module {
    name = "python_module"
    path = "/usr/lib64/ganglia/modpython.so"
    params = "/usr/lib64/ganglia/python_modules"
  }
}

include ("/etc/ganglia/conf.d/*.pyconf")
```

## Debugging Python Modules

```bash
# Run gmond in foreground with debug output
gmond --conf /etc/ganglia/gmond.conf --debug 10 --no-daemon 2>&1 | head -100

# Check gmond log for Python errors
journalctl -u gmond -f

# Test metric callback manually
python3 -c "
import sys; sys.path.insert(0, '/usr/lib64/ganglia/python_modules')
import my_module
descs = my_module.metric_init({'poll_interval': '10'})
for d in descs:
    val = d['call_back'](d['name'])
    print(d['name'], '=', val)
"
```

## Common Patterns

### HTTP Endpoint Poller

```python
import urllib.request, json, time

_cache = {}
_cache_ts = 0

def metric_init(params):
    global _url
    _url = params.get('url', 'http://localhost:8080/metrics')
    return [
        {'name': 'app_active_sessions', 'call_back': get_sessions,
         'time_max': 60, 'value_type': 'uint', 'units': 'sessions',
         'slope': 'both', 'format': '%u', 'description': 'Active sessions',
         'groups': 'app'},
    ]

def get_sessions(name):
    global _cache, _cache_ts
    if time.time() - _cache_ts > 10:
        try:
            with urllib.request.urlopen(_url, timeout=5) as r:
                _cache = json.loads(r.read())
            _cache_ts = time.time()
        except Exception:
            pass
    return int(_cache.get('active_sessions', 0))
```

### File-Based Metric

```python
def get_value_from_file(name):
    try:
        with open('/var/run/myapp/metric_' + name, 'r') as f:
            return float(f.read().strip())
    except Exception:
        return 0.0
```

### JMX via Jolokia

```python
import urllib.request, json

JOLOKIA = 'http://localhost:8778/jolokia/read'

def get_jvm_heap(name):
    url = f"{JOLOKIA}/java.lang:type=Memory/HeapMemoryUsage/used"
    with urllib.request.urlopen(url, timeout=3) as r:
        data = json.loads(r.read())
    return int(data['value']) // (1024 * 1024)  # bytes → MB
```
