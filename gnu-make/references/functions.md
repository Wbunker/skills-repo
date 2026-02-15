# Functions

## Table of Contents
- [String Functions](#string-functions)
- [File Name Functions](#file-name-functions)
- [Conditional Functions](#conditional-functions)
- [Iteration and Transformation](#iteration-and-transformation)
- [call and User-Defined Functions](#call-and-user-defined-functions)
- [eval — Dynamic Makefile Generation](#eval--dynamic-makefile-generation)
- [Introspection Functions](#introspection-functions)
- [Shell Function](#shell-function)
- [File Function](#file-function)
- [Functional Programming Patterns](#functional-programming-patterns)

## String Functions

### $(subst from,to,text)
Literal string substitution (not a pattern):
```makefile
$(subst ee,EE,feet on the street)   # → "fEEt on the strEEt"
```

### $(patsubst pattern,replacement,text)
Pattern substitution with `%` wildcard:
```makefile
$(patsubst %.c,%.o,foo.c bar.c)     # → "foo.o bar.o"
# shorthand: $(VAR:%.c=%.o) or $(VAR:.c=.o)
```

### $(strip string)
Remove leading/trailing whitespace and collapse internal whitespace:
```makefile
$(strip   foo   bar  )              # → "foo bar"
```
Critical for conditionals — whitespace makes `ifeq` fail:
```makefile
ifeq ($(strip $(VAR)),yes)
```

### $(findstring find,in)
Returns `find` if found, empty otherwise:
```makefile
$(findstring debug,$(MAKECMDGOALS))  # test if "debug" was a goal
```

### $(filter pattern...,text)
Keep only words matching patterns:
```makefile
SRCS := main.c util.c helper.s data.h
C_SRCS := $(filter %.c,$(SRCS))      # → "main.c util.c"
```

### $(filter-out pattern...,text)
Remove words matching patterns:
```makefile
OBJS := $(filter-out test_%,$(ALL_OBJS))  # exclude test objects
```

### $(sort list)
Sort lexicographically AND remove duplicates:
```makefile
$(sort foo bar baz foo)               # → "bar baz foo"
```

### $(word n,text) / $(wordlist s,e,text) / $(words text) / $(firstword text) / $(lastword text)
```makefile
$(word 2,foo bar baz)                 # → "bar" (1-indexed)
$(wordlist 2,3,foo bar baz qux)       # → "bar baz"
$(words foo bar baz)                  # → "3"
$(firstword foo bar baz)              # → "foo"
$(lastword foo bar baz)               # → "baz"
```

## File Name Functions

### $(dir names...) / $(notdir names...)
```makefile
$(dir src/foo.c lib/bar.c)            # → "src/ lib/"
$(notdir src/foo.c lib/bar.c)         # → "foo.c bar.c"
```

### $(suffix names...) / $(basename names...)
```makefile
$(suffix main.c util.o)               # → ".c .o"
$(basename src/main.c)                # → "src/main"
```

### $(addsuffix suffix,names...) / $(addprefix prefix,names...)
```makefile
$(addsuffix .o,foo bar)               # → "foo.o bar.o"
$(addprefix src/,foo.c bar.c)         # → "src/foo.c src/bar.c"
```

### $(join list1,list2)
Pairwise concatenation:
```makefile
$(join src/ lib/,foo.c bar.c)         # → "src/foo.c lib/bar.c"
```

### $(wildcard pattern)
Glob expansion (unlike shell globs, this is explicit):
```makefile
SRCS := $(wildcard src/*.c src/**/*.c)
```
Returns empty string if no matches. **Does not recurse by default** — use `$(shell find ...)` for recursive globbing.

### $(realpath names...) / $(abspath names...)
```makefile
$(realpath ../foo/bar.c)              # resolves symlinks, must exist
$(abspath ../foo/bar.c)               # resolves path, needn't exist
```

## Conditional Functions

### $(if condition,then-part[,else-part])
```makefile
RESULT := $(if $(DEBUG),debug-mode,release-mode)
```
Condition is true if it expands to any non-empty string.

### $(or condition1,condition2,...)
Returns the first non-empty argument:
```makefile
CC := $(or $(MY_CC),$(shell which gcc),cc)
```

### $(and condition1,condition2,...)
Returns the last argument if ALL are non-empty, else empty:
```makefile
$(and $(CC),$(CFLAGS),ready)          # → "ready" if both CC and CFLAGS set
```

## Iteration and Transformation

### $(foreach var,list,text)
```makefile
DIRS := src lib tests
CLEAN_RULES := $(foreach d,$(DIRS),clean-$(d))
# → "clean-src clean-lib clean-tests"

# Creating directory creation rules:
$(foreach d,$(DIRS),$(eval $(d): ; mkdir -p $$@))
```

**Pitfall**: The loop variable is a simply-expanded variable. Using recursive references inside the body can surprise:
```makefile
# BAD — $(files) is expanded before foreach runs:
result := $(foreach d,$(DIRS),$(wildcard $(d)/*.c))
# GOOD — this works because wildcard is a function:
result := $(foreach d,$(DIRS),$(wildcard $(d)/*.c))
# Actually both work here because wildcard evaluates its argument.
# The pitfall is with recursive variable references, not functions.
```

## call and User-Defined Functions

`$(call)` invokes a variable as a function with positional arguments `$(1)`, `$(2)`, etc. `$(0)` is the function name.

```makefile
# Define a function:
reverse = $(2) $(1)

# Call it:
$(call reverse,hello,world)           # → "world hello"
```

### Practical patterns

```makefile
# Assert a variable is set:
assert-set = $(if $($(1)),,$(error $(1) is not set))

usage:
	$(call assert-set,CC)
	$(call assert-set,PREFIX)

# Generate a build rule for a module:
define module-rule
$(1)/$(1).o: $(1)/$(1).c
	$$(CC) $$(CFLAGS) -c $$< -o $$@
endef

MODULES := auth db web
$(foreach m,$(MODULES),$(eval $(call module-rule,$(m))))
```

**Critical**: When using `$(call)` with `$(eval)`, double-escape `$$` for anything that should be expanded at rule execution time, not at `$(eval)` time.

## eval — Dynamic Makefile Generation

`$(eval text)` parses text as makefile syntax. The text is expanded, then parsed as if it were part of the makefile.

```makefile
# Dynamically create a target:
$(eval \
  generated.c: template.c.in \
    sed 's/@VERSION@/1.0/' $$< > $$@ \
)
```

### Two-phase expansion
1. Make expands `$(eval ...)` arguments (first expansion)
2. The result is parsed as makefile text (second expansion)

This means:
- `$(VAR)` or `$(function ...)` — expanded in phase 1
- `$$(VAR)` or `$$(function ...)` — expanded in phase 2 (when rule runs)
- `$$$$` — becomes `$$` after phase 1, then `$` in the rule

### eval + call + foreach idiom
The most powerful pattern for generating repetitive rules:
```makefile
define program-template
$(1): $$($(1)_OBJS)
	$$(CC) $$(LDFLAGS) $$^ -o $$@

$(1)_OBJS := $$(patsubst %.c,%.o,$$($(1)_SRCS))
endef

server_SRCS := server.c net.c auth.c
client_SRCS := client.c net.c ui.c

PROGRAMS := server client
$(foreach p,$(PROGRAMS),$(eval $(call program-template,$(p))))
```

## Introspection Functions

### $(value variable)
Returns the unexpanded value of a variable:
```makefile
FOO = $(BAR)
$(value FOO)    # → "$(BAR)" literally, not expanded
```

### $(origin variable)
Returns where a variable was defined:
- `undefined`, `default`, `environment`, `environment override`, `file`, `command line`, `override`, `automatic`

```makefile
ifeq ($(origin CC),command line)
  # user explicitly set CC on command line
endif
```

### $(flavor variable)
Returns `undefined`, `recursive`, or `simple`.

## Shell Function

```makefile
DATE := $(shell date +%Y-%m-%d)
GIT_HASH := $(shell git rev-parse --short HEAD 2>/dev/null || echo unknown)
```

- Each `$(shell)` invocation spawns a subprocess — expensive in loops
- Output newlines are replaced with spaces
- Exit status available in `.SHELLSTATUS` (GNU Make 4.2+)

## File Function

GNU Make 4.0+. Read/write files without shell:

```makefile
# Write to file (overwrite):
$(file >deps.txt,$(OBJS))

# Append to file:
$(file >>deps.txt,more content)

# Read file:
CONTENTS := $(file <config.txt)
```

Useful for avoiding command-line length limits (e.g., passing many files to `ar`):
```makefile
lib.a: $(OBJS)
	$(file >$@.list,$^)
	$(AR) rcs $@ @$@.list
	@rm $@.list
```

## Functional Programming Patterns

### Map
```makefile
# $(foreach) is map:
uppercase = $(shell echo $(1) | tr a-z A-Z)
UPPER := $(foreach w,hello world,$(call uppercase,$(w)))
```

### Filter as select
```makefile
TEST_SRCS := $(filter %_test.c test_%.c,$(SRCS))
```

### Reduce / accumulate
```makefile
# GNU Make lacks native reduce, but you can simulate:
comma := ,
join-with = $(subst $(space),$(1),$(strip $(2)))
CSV := $(call join-with,$(comma),foo bar baz)    # → "foo,bar,baz"
```

### Memoization
For expensive shell calls, assign to simply-expanded variables:
```makefile
# Computed once:
GIT_HASH := $(shell git rev-parse HEAD)

# Computed every reference (BAD for expensive operations):
GIT_HASH = $(shell git rev-parse HEAD)
```
