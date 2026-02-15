# Rules & Targets

## Table of Contents
- [Explicit Rules](#explicit-rules)
- [Pattern Rules](#pattern-rules)
- [Static Pattern Rules](#static-pattern-rules)
- [Implicit Rules](#implicit-rules)
- [VPATH and vpath](#vpath-and-vpath)
- [Order-Only Prerequisites](#order-only-prerequisites)
- [Multiple Targets and Rules](#multiple-targets-and-rules)
- [Secondary Expansion](#secondary-expansion)
- [Phony Targets](#phony-targets)
- [Empty Recipes and Force Targets](#empty-recipes-and-force-targets)

## Explicit Rules

Basic form:
```makefile
target: prereq1 prereq2
	recipe-line-1
	recipe-line-2
```

Make determines whether a target needs rebuilding by comparing timestamps: if any prerequisite is newer than the target (or the target doesn't exist), the recipe runs.

Multiple prerequisites on separate lines — all merge:
```makefile
target: prereq1
target: prereq2
target: prereq3
	recipe    # only ONE rule may have a recipe
```

## Pattern Rules

Replace the older suffix rules. A `%` in the target matches any nonempty string (the "stem"):

```makefile
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Multiple targets — each gets its own independent rule:
%.tab.c %.tab.h: %.y
	bison -d $<
```

The stem matched by `%` is available as `$*`.

### Pattern rule search order

1. Make looks for a pattern rule whose target pattern matches and whose prerequisites exist or can be made.
2. If multiple pattern rules match, make uses the one with the shortest stem.
3. Built-in pattern rules have lower priority than user-defined ones.

### Canceling a pattern rule

Define the pattern with no recipe:
```makefile
%.o: %.s
```

This cancels the built-in assembly rule.

## Static Pattern Rules

Apply a pattern rule to an explicit list of targets:

```makefile
objects := foo.o bar.o baz.o

$(objects): %.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@
```

Advantages over regular pattern rules:
- Only applies to the listed targets (no accidental matches)
- Can assign target-specific variables alongside
- Clearer intent in complex Makefiles

## Implicit Rules

GNU Make has a catalog of built-in implicit rules. Key ones:

| Pattern | Recipe |
|---------|--------|
| `%.o: %.c` | `$(CC) $(CPPFLAGS) $(CFLAGS) -c` |
| `%.o: %.cc` / `%.cpp` | `$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c` |
| `%: %.o` | `$(CC) $(LDFLAGS) $^ $(LDLIBS) -o $@` |
| `%.o: %.s` | `$(AS) $(ASFLAGS)` |

Disable ALL built-in rules:
```makefile
.SUFFIXES:          # disable suffix rules
MAKEFLAGS += -r     # or pass -r on command line
```

Or use `make -r` to run without built-in rules.

### Implicit rule chains

Make can chain implicit rules: e.g., `foo.o` from `foo.y` via `foo.c`. Intermediate files in a chain are automatically deleted unless marked `.PRECIOUS` or `.SECONDARY`.

```makefile
.PRECIOUS: %.c    # keep generated .c files
.SECONDARY:       # keep ALL intermediate files (no args = everything)
```

## VPATH and vpath

Search directories for prerequisites that aren't found in the current directory.

```makefile
# General search path (all files):
VPATH = src:lib:../shared

# Selective by pattern (preferred):
vpath %.c src lib
vpath %.h include ../shared/include
```

**Critical behavior**: VPATH only affects *prerequisite* lookup. The target `$@` still refers to the file in the current directory. The found path is available in `$<` and `$^`.

```makefile
vpath %.c src

# $< will be src/foo.c but $@ is foo.o (in current dir)
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@
```

### Clearing vpath
```makefile
vpath %.c           # clear vpath for *.c
vpath               # clear all vpath settings
```

## Order-Only Prerequisites

Prerequisites after `|` don't trigger rebuilds — they only ensure existence:

```makefile
output/foo.o: foo.c | output
	$(CC) -c $< -o $@

output:
	mkdir -p $@
```

The directory `output` is created if missing, but changes to the directory's timestamp won't cause `foo.o` to rebuild.

## Multiple Targets and Rules

### Independent targets sharing a recipe
```makefile
# Each target is built independently with the same recipe:
foo.o bar.o baz.o: %.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@
```

### Grouped targets (GNU Make 4.3+)
```makefile
# One invocation produces ALL targets:
foo.h foo.c &: foo.y
	bison -d $<
```

The `&:` separator tells make the single recipe produces all listed targets. Without this, make might run the recipe multiple times in parallel builds.

### Multiple rules for one target
```makefile
# Prerequisites accumulate across rules:
foo: bar
foo: baz
foo: qux
	recipe    # at most one rule may have a recipe
```

## Secondary Expansion

Enable `$$` expansion in prerequisites — evaluated after all makefiles are read:

```makefile
.SECONDEXPANSION:

# Use automatic variables in prerequisites:
main.o: $$(wildcard $$(dir $$@)*.h)
```

This is powerful for computing dependencies dynamically. The `$$` is needed to escape the first expansion pass.

## Phony Targets

Targets that don't represent files:

```makefile
.PHONY: all clean install test

all: program

clean:
	rm -f *.o program

install: program
	install -m 755 program $(PREFIX)/bin
```

Without `.PHONY`, if a file named `clean` existed, `make clean` would consider it up-to-date and skip the recipe.

### Phony subdirectory pattern
```makefile
.PHONY: all clean

SUBDIRS := lib src tests

all clean:
	$(foreach dir,$(SUBDIRS),$(MAKE) -C $(dir) $@ &&) true
```

## Empty Recipes and Force Targets

### Force target pattern
```makefile
# A target with no prerequisites and no recipe:
FORCE:

# Any target depending on FORCE always rebuilds:
program: FORCE
	$(CC) -o $@ $(OBJS)
```

Equivalent to `.PHONY` but works when the target IS a real file.

### Empty recipe
```makefile
target: ;
```

An explicit empty recipe prevents make from searching for implicit rules.
