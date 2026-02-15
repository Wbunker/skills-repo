# Performance

## Table of Contents
- [Parallel Builds](#parallel-builds)
- [Reducing Shell Invocations](#reducing-shell-invocations)
- [Variable Expansion Costs](#variable-expansion-costs)
- [Wildcard and Shell Performance](#wildcard-and-shell-performance)
- [Makefile Parsing Overhead](#makefile-parsing-overhead)
- [Incremental Build Optimization](#incremental-build-optimization)
- [Large File Lists](#large-file-lists)

## Parallel Builds

### Maximizing parallelism
```bash
make -j$(nproc)              # match CPU cores
make -j$(( $(nproc) + 1 ))  # slightly over-subscribe (hides I/O latency)
```

### Prerequisites for correct parallel builds
- **Complete dependency graph**: every real dependency must be declared
- **No side-effect sharing**: two recipes must not write to the same file
- **Grouped targets**: multi-output rules must use `&:` (GNU Make 4.3+)

### Diagnosing parallelism issues
```bash
# Compare serial vs parallel:
time make -j1 clean all
time make -j8 clean all

# If parallel is slower or fails, check:
make -j8 --debug=jobs 2>&1 | head -100
```

### Job server protocol
When using `$(MAKE)` for recursive invocations, the parent and child share a job pool. This ensures `-j8` means 8 total jobs across all sub-makes, not 8 per sub-make.

If calling sub-processes that are themselves parallel (e.g., `ninja`, `cargo`), limit their parallelism to avoid oversubscription:
```makefile
subproject:
	cd subproject && ninja -j2    # limit sub-parallelism
```

## Reducing Shell Invocations

Each recipe line spawns a shell. Each `$(shell)` call spawns a shell. Minimizing shell invocations speeds up make.

### Use make functions instead of shell
```makefile
# SLOW — spawns a shell:
FILES := $(shell ls src/*.c)

# FAST — pure make:
FILES := $(wildcard src/*.c)

# SLOW:
BASE := $(shell basename $(FILE))

# FAST:
BASE := $(notdir $(FILE))

# SLOW:
DIR := $(shell dirname $(FILE))

# FAST:
DIR := $(dir $(FILE))
```

### Batch shell operations
```makefile
# SLOW — one shell per file:
$(foreach f,$(FILES),$(shell process $(f)))

# FASTER — one shell for all:
process-all:
	@for f in $(FILES); do process "$$f"; done
```

### .ONESHELL for multi-line recipes
Instead of using `&&` or `;` continuations (which still spawn one shell per line without `.ONESHELL`), use `.ONESHELL` to run the entire recipe in one shell.

## Variable Expansion Costs

### Recursive vs simple expansion
```makefile
# Recursive (=) — re-evaluated every time:
CFLAGS = -Wall $(EXTRA_FLAGS) $(shell pkg-config --cflags $(LIBS))
# $(shell) runs EVERY time CFLAGS is referenced!

# Simply expanded (:=) — evaluated once:
CFLAGS := -Wall $(EXTRA_FLAGS) $(shell pkg-config --cflags $(LIBS))
# $(shell) runs once at assignment
```

**Rule of thumb**: Use `:=` for variables containing `$(shell)` or expensive functions. Use `=` only when deferred expansion is actually needed.

### Expensive function caching
```makefile
# Cache the result of an expensive operation:
_pkg_config_cache := $(shell pkg-config --cflags --libs openssl libcurl)
PKG_CFLAGS := $(filter -I%,$(_pkg_config_cache))
PKG_LIBS := $(filter -l%,$(_pkg_config_cache))
```

### $(eval) in loops
`$(eval)` re-parses text as makefile syntax every time. In tight loops, this adds overhead:
```makefile
# Acceptable — runs once per module during parsing:
$(foreach m,$(MODULES),$(eval $(call module-template,$(m))))

# Avoid — $(eval) in recipes or frequently expanded variables
```

## Wildcard and Shell Performance

### $(wildcard) is cached
GNU Make caches directory listings, so repeated `$(wildcard)` calls for the same directory are cheap. However, the first call for a directory with thousands of files can be slow.

### $(shell find ...) is expensive
```makefile
# SLOW for large trees:
ALL_SRCS := $(shell find . -name '*.c')

# FASTER — use make's wildcard with known structure:
ALL_SRCS := $(wildcard src/*.c src/**/*.c lib/*.c lib/**/*.c)

# Note: $(wildcard) does NOT support ** recursive globbing in all versions.
# If you need recursion, $(shell find) may be unavoidable — but cache the result:
ALL_SRCS := $(shell find src lib -name '*.c')
```

## Makefile Parsing Overhead

### Reducing include count
Each `include` triggers file I/O and potentially make restarting:
```makefile
# Instead of many small includes:
include $(wildcard src/*/.deps/*.d)    # could be hundreds of files

# Concatenate into one:
deps.mk: $(wildcard src/*/.deps/*.d)
	cat $^ > $@
-include deps.mk
```

### Conditional includes
Only include what's needed:
```makefile
ifneq ($(MAKECMDGOALS),clean)
-include $(DEPS)
endif
```
This avoids generating/reading dependency files when just cleaning.

## Incremental Build Optimization

### Avoiding unnecessary rebuilds

#### Content-based rebuild checks
Make uses timestamps, not content. Work around this for generated files:
```makefile
version.h: FORCE
	@echo '#define VERSION "$(VERSION)"' > $@.tmp
	@cmp -s $@ $@.tmp && rm $@.tmp || mv $@.tmp $@
FORCE:
```

#### Order-only prerequisites for directories
```makefile
# WITHOUT order-only: touching the dir triggers rebuild of ALL objects
$(BUILDDIR)/%.o: %.c $(BUILDDIR)      # BAD

# WITH order-only: dir is created if missing, but doesn't trigger rebuilds
$(BUILDDIR)/%.o: %.c | $(BUILDDIR)    # GOOD
```

### Precompiled headers (C/C++)
```makefile
# GCC precompiled header:
stdafx.h.gch: stdafx.h
	$(CXX) $(CXXFLAGS) -x c++-header $< -o $@

# Must be first in include path:
$(OBJS): stdafx.h.gch
CXXFLAGS += -include stdafx.h
```

## Large File Lists

### Command-line length limits
When `$(OBJS)` grows very large, recipe lines can exceed OS limits.

```makefile
# Use response files:
lib.a: $(OBJS)
	$(file >$@.cmd,$^)
	$(AR) rcs $@ @$@.cmd
	@rm $@.cmd

# Or batch with $(wordlist):
define batch-ar
$(AR) rcs $@ $(wordlist $(1),$(2),$^)
endef

lib.a: $(OBJS)
	$(call batch-ar,1,100)
	$(call batch-ar,101,200)
```

### Splitting large variable definitions
```makefile
SRCS += $(wildcard module1/*.c)
SRCS += $(wildcard module2/*.c)
SRCS += $(wildcard module3/*.c)
# Better than one huge line
```
