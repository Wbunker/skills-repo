# Variables & Macros

## Table of Contents
- [Variable Flavors](#variable-flavors)
- [Variable References and Expansion](#variable-references-and-expansion)
- [Multi-line Variables (define)](#multi-line-variables-define)
- [Target-Specific Variables](#target-specific-variables)
- [Pattern-Specific Variables](#pattern-specific-variables)
- [Override Directive](#override-directive)
- [Private Variables](#private-variables)
- [Environment Variables](#environment-variables)
- [Computed Variable Names](#computed-variable-names)
- [Automatic Variables](#automatic-variables)
- [Variable Scoping and Inheritance](#variable-scoping-and-inheritance)
- [Special Variables](#special-variables)

## Variable Flavors

### Recursively expanded (`=`)
```makefile
FOO = $(BAR)
BAR = hello
# $(FOO) → "hello" — expanded at point of use
```
- Expansion is deferred until the variable is referenced
- Can create circular references (make will error)
- Useful for variables that depend on context (e.g., `$@`)

### Simply expanded (`:=` or `::=`)
```makefile
FOO := $(BAR)
BAR := hello
# $(FOO) → "" — BAR wasn't defined yet when FOO was assigned
```
- Expanded immediately at assignment time
- Behaves like variables in most programming languages
- `::=` is POSIX standard; `:=` is GNU extension (both work identically in GNU Make)

### Conditional (`?=`)
```makefile
CC ?= gcc    # set only if CC is not already defined
```
Checks for any definition, including empty. A variable set to empty IS defined.

### Append (`+=`)
```makefile
CFLAGS := -Wall
CFLAGS += -O2     # CFLAGS is now "-Wall -O2"
```
Preserves the variable's existing flavor (recursive or simple). If the variable was not previously defined, `+=` acts like `=`.

### Shell assignment (`!=`) — GNU Make 4.0+
```makefile
HASH != git rev-parse --short HEAD
# equivalent to: HASH := $(shell git rev-parse --short HEAD)
```

## Variable References and Expansion

```makefile
$(VAR)     # standard reference
${VAR}     # also valid, same behavior
$V         # single-character variable name (avoid except for $@, $<, etc.)
```

### Substitution reference
```makefile
SRCS := foo.c bar.c
OBJS := $(SRCS:.c=.o)    # → "foo.o bar.o"
# equivalent to $(patsubst %.c,%.o,$(SRCS))
```

## Multi-line Variables (define)

```makefile
define compile-rule
$(CC) $(CFLAGS) -c $< -o $@
@echo "Compiled $<"
endef

%.o: %.c
	$(compile-rule)
```

Can specify flavor:
```makefile
define FOO :=
immediate expansion
endef

define BAR =
deferred expansion
endef
```

### Canned recipes
`define` is the standard way to create reusable recipe fragments. Each line in the `define` becomes a separate shell invocation (standard make behavior) unless `.ONESHELL` is active.

## Target-Specific Variables

Set a variable only in the context of a specific target and its prerequisites:

```makefile
debug: CFLAGS += -g -DDEBUG
debug: program

release: CFLAGS += -O2 -DNDEBUG
release: program
```

Target-specific variables **propagate to prerequisites** — every file built as a dependency of `debug` gets the debug CFLAGS. This is powerful but can cause unexpected rebuilds if the same object is used by both `debug` and `release` targets.

**Pitfall**: If `foo.o` is shared between debug and release, it gets built with whichever target's variables happen to apply first. Solution: use separate build directories.

## Pattern-Specific Variables

Like target-specific, but apply to all targets matching a pattern:

```makefile
%.o: CFLAGS += -fPIC
```

## Override Directive

Override command-line variable assignments from within the Makefile:

```makefile
override CFLAGS += -Wall     # appends even if CFLAGS was set on command line
override CFLAGS := -Wall     # replaces even if CFLAGS was set on command line
```

Without `override`, command-line values take precedence over Makefile assignments. Variable precedence (highest to lowest):

1. `override` in Makefile
2. Command line (`make CFLAGS=-O2`)
3. Makefile assignment
4. Environment variables (unless `make -e`)

## Private Variables

GNU Make 3.82+. Prevent a variable from being inherited by prerequisites:

```makefile
prog: private EXTRA_FLAGS = -special
prog: foo.o bar.o
	$(CC) $(EXTRA_FLAGS) $^ -o $@
# foo.o and bar.o do NOT see EXTRA_FLAGS
```

## Environment Variables

- Environment variables are available as make variables by default
- Makefile assignments override environment variables
- `make -e` / `MAKEFLAGS += -e` reverses this (environment wins)
- `export VAR` / `unexport VAR` controls what passes to sub-makes and recipe shells

```makefile
export CC := gcc           # available in recipes and sub-makes
unexport SECRET_KEY        # explicitly hide from sub-processes
export                     # with no args: export everything (avoid this)
```

## Computed Variable Names

Variable names can be computed — double expansion:

```makefile
SRCS_linux := linux_main.c
SRCS_darwin := darwin_main.c
OS := linux

SRCS := $(SRCS_$(OS))    # → "linux_main.c"
```

Powerful for platform-specific or configuration-driven builds:

```makefile
# Build type selection
BUILD := debug
CFLAGS_debug := -g -O0
CFLAGS_release := -O2 -DNDEBUG
CFLAGS += $(CFLAGS_$(BUILD))
```

## Automatic Variables

Full reference:

| Variable | Description |
|----------|-------------|
| `$@` | Target filename |
| `$<` | First prerequisite |
| `$^` | All prerequisites, spaces between, duplicates removed |
| `$+` | All prerequisites, spaces between, duplicates kept |
| `$?` | Prerequisites newer than target |
| `$*` | Stem (the `%` match in pattern rules) |
| `$\|` | Order-only prerequisites |
| `$(@D)` | Directory part of `$@` |
| `$(@F)` | Filename part of `$@` |
| `$(<D)` | Directory part of `$<` |
| `$(<F)` | Filename part of `$<` |
| `$(*D)` | Directory part of `$*` |
| `$(*F)` | Filename part of `$*` |

**Important**: `$*` in explicit rules (non-pattern) is the target stem only if the target has a recognized suffix. In other contexts it's empty. Prefer `$*` only in pattern rules.

**Important**: `$?` is particularly useful for archive/library updates — only recompile the changed members.

## Variable Scoping and Inheritance

Scope rules:
1. Global variables are visible everywhere
2. Target-specific variables are visible in the target's recipe AND inherited by prerequisites (unless `private`)
3. Pattern-specific variables apply to matching targets
4. `include`d files share the same global scope

In recursive make (`$(MAKE) -C subdir`):
- Variables passed via `export` are available
- Variables on the command line propagate automatically via `MAKEFLAGS`
- `MAKELEVEL` is automatically incremented

## Special Variables

| Variable | Purpose |
|----------|---------|
| `MAKEFILE_LIST` | List of makefiles parsed so far |
| `MAKE` | Path to make itself (use in recursive invocations) |
| `MAKELEVEL` | Recursion depth (0 = top-level) |
| `MAKEFLAGS` | Flags passed to make |
| `MAKECMDGOALS` | Targets specified on command line |
| `CURDIR` | Current working directory |
| `.DEFAULT_GOAL` | Target built when none specified |
| `.RECIPEPREFIX` | Character replacing tab in recipes (GNU Make 4.0+) |
| `.FEATURES` | List of supported GNU Make features |
| `.INCLUDE_DIRS` | Directories searched for `include` |
| `MAKE_RESTARTS` | Number of times make has restarted |
| `.LOADED` | Loaded object files (dynamic extensions) |

### .RECIPEPREFIX example
```makefile
.RECIPEPREFIX = >
all:
> echo "tabs no more"
> gcc -o program main.c
```
