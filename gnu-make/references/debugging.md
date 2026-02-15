# Debugging GNU Make

## Table of Contents
- [Debugging Philosophy](#debugging-philosophy)
- [Command-Line Debug Options](#command-line-debug-options)
- [Printing Variables and State](#printing-variables-and-state)
- [The Remake Database (-p)](#the-remake-database--p)
- [Tracing Execution](#tracing-execution)
- [Debugging Variable Expansion](#debugging-variable-expansion)
- [Debugging Recursive Make](#debugging-recursive-make)
- [Debugging Pattern Rule Selection](#debugging-pattern-rule-selection)
- [Common Pitfalls and Their Symptoms](#common-pitfalls-and-their-symptoms)
- [The remake Debugger](#the-remake-debugger)
- [Systematic Debugging Workflow](#systematic-debugging-workflow)

## Debugging Philosophy

GNU Make problems fall into three categories:

1. **Wrong commands executed** — rule selection or variable expansion issues
2. **Wrong rebuild decisions** — timestamp or prerequisite issues
3. **Silent failures** — recipes that fail in non-obvious ways

The key insight: make's behavior is deterministic and driven by its database of rules and timestamps. Debugging means inspecting that database and the expansion/matching logic.

## Command-Line Debug Options

| Flag | Purpose |
|------|---------|
| `-n` / `--just-print` | Print commands without executing (dry run) |
| `-p` / `--print-data-base` | Print all rules and variables |
| `-d` | Full debug output (very verbose) |
| `--debug=FLAGS` | Selective debug output |
| `-w` / `--print-directory` | Print working directory on enter/leave |
| `--warn-undefined-variables` | Warn on use of undefined variables |
| `-t` / `--touch` | Touch targets instead of building |
| `-q` / `--question` | Exit 0 if up to date, 1 if not (no build) |

### --debug= flags

| Flag | Output |
|------|--------|
| `a` (all) | Everything (same as `-d`) |
| `b` (basic) | Targets that need rebuilding and whether they succeed |
| `v` (verbose) | Basic + makefile parsing, prerequisites |
| `i` (implicit) | Implicit rule search for each target |
| `j` (jobs) | Job server details for parallel builds |
| `m` (makefile) | Remaking of makefiles themselves |
| `w` (why) | Why each target is being rebuilt (GNU Make 4.0+) |
| `p` (print) | Same as `--print-data-base` |

### Best starting points
```bash
# "Why is this target being rebuilt?"
make --debug=why target_name

# "What rule is being selected?"
make --debug=implicit target_name

# "What would make do?" (without doing it)
make -n target_name

# "What does make know?"
make -p -f /dev/null    # just built-in rules
make -p                 # built-in + your Makefile
```

## Printing Variables and State

### $(info), $(warning), $(error)

```makefile
# Non-intrusive — no "Makefile:N:" prefix:
$(info CC is [$(CC)])
$(info SRCS is [$(SRCS)])

# With file/line context:
$(warning CFLAGS is [$(CFLAGS)])

# Fatal with message:
$(error PREFIX must be set)
```

`$(info)` is best for debugging — it has no side effects and no prefix clutter.

### Strategic placement
```makefile
# At global scope — prints during Makefile parsing:
$(info === Parsing phase: CC=$(CC) ===)

# Inside a recipe — prints during execution:
target:
	@echo "Building $@ from $^"
	@echo "CFLAGS = $(CFLAGS)"

# Inside a conditional — check which branch:
ifdef DEBUG
$(info DEBUG mode is ON)
else
$(info DEBUG mode is OFF)
endif
```

### Print-variable helper
```makefile
# Generic variable printer — call with: make print-VARNAME
print-%:
	@echo '$* = $($*)'
	@echo '  origin: $(origin $*)'
	@echo '  flavor: $(flavor $*)'
	@echo '  value:  $(value $*)'
```

Usage: `make print-CC`, `make print-CFLAGS`, etc.

## The Remake Database (-p)

`make -p` dumps make's entire internal database after parsing. This is the most comprehensive debugging tool.

### Reading the output

The output has sections:

```
# Variables
CC = gcc
# origin: default
# flavor: recursive

# Implicit Rules
%.o: %.c
#  recipe to execute (built-in):
	$(COMPILE.c) $(OUTPUT_OPTION) $<

# Files
main.o: main.c util.h config.h
#  Implicit rule search has been done.
#  Last modified 2024-01-15 10:30:00
#  File is an intermediate prerequisite.
```

### Useful grep patterns
```bash
# Find all rules for a specific target:
make -p | grep -A5 '^target_name:'

# Find where a variable is set:
make -p | grep -B1 -A1 '^VARNAME'

# Find all pattern rules:
make -p | grep -B1 '%'

# Just the database without building:
make -p -q 2>/dev/null    # -q prevents building
```

### Filtering the database
```bash
# Variables only:
make -p | sed -n '/^# Variables/,/^# /p'

# Explicit rules only:
make -p | sed -n '/^# Files/,/^# /p'

# Remove comments:
make -p | grep -v '^#'
```

## Tracing Execution

### Recipe tracing with PS4
When using bash, set `PS4` for detailed trace output:

```makefile
SHELL := /bin/bash
export PS4 := +($@)

# Then run: make SHELL="bash -x" target
```

### Selective tracing
```makefile
# Trace only specific targets:
debug-%: SHELL := bash -x
debug-%: %
	@true
```

### Makefile self-tracing
```makefile
ifdef TRACE
.SHELLFLAGS = -xc
endif
```
Usage: `make TRACE=1 target`

## Debugging Variable Expansion

### Expansion timing issues

The most common debugging challenge: understanding WHEN a variable is expanded.

```makefile
# Test expansion timing:
A = initial
B := $(A)     # B is "initial" (expanded now)
C = $(A)      # C depends on A (expanded later)
A = changed

$(info B=$(B))  # → "initial"
$(info C=$(C))  # → "changed"
```

### $(value) for inspection
```makefile
FOO = $(BAR) and $(BAZ)
$(info FOO expands to: $(FOO))
$(info FOO is defined as: $(value FOO))
# Output:
# FOO expands to: hello and world
# FOO is defined as: $(BAR) and $(BAZ)
```

### Tracing eval expansion
```makefile
# Debug eval by replacing with info first:
$(info $(call my-template,arg1,arg2))    # see what eval would parse
# Then switch to:
$(eval $(call my-template,arg1,arg2))    # actually evaluate it
```

## Debugging Recursive Make

### MAKELEVEL tracking
```makefile
$(info [Level $(MAKELEVEL)] Entering $(CURDIR))
```

### Print directory
```bash
make -w    # prints "Entering directory" / "Leaving directory"
```

### Tracing variable inheritance
```makefile
# In child Makefile, verify what was received:
$(info [$(MAKELEVEL)] CC=$(CC) origin=$(origin CC))
$(info [$(MAKELEVEL)] CFLAGS=$(CFLAGS) origin=$(origin CFLAGS))
```

### Common recursive make bugs
1. **Variable not exported**: Add `export VAR` or pass explicitly
2. **Not using `$(MAKE)`**: Sub-make doesn't participate in job server
3. **Inconsistent rebuilds**: Same target built differently at different levels

## Debugging Pattern Rule Selection

When make chooses the wrong rule or "no rule to make target":

```bash
# See implicit rule search:
make --debug=implicit target.o

# Output shows:
#   Looking for an implicit rule for 'target.o'.
#   Trying pattern rule with stem 'target'.
#   Trying implicit prerequisite 'target.c'.
#   Found an implicit rule for 'target.o'.
```

### Common pattern rule issues
1. **Prerequisite doesn't exist**: make can't find the source file (check VPATH)
2. **Wrong pattern matches**: a more specific pattern rule is needed
3. **Built-in rule interference**: disable with `.SUFFIXES:` and `-r`

## Common Pitfalls and Their Symptoms

### Spaces vs tabs
**Symptom**: `*** missing separator.  Stop.`
**Cause**: Recipe line uses spaces instead of tab.
**Fix**: Use literal tab, or set `.RECIPEPREFIX`.

### Trailing whitespace
**Symptom**: String comparisons fail, filenames have spaces.
```makefile
VAR := hello   # trailing spaces are part of the value!
# Use:
VAR := hello# comment strips trailing space
# Or:
$(strip $(VAR))
```

### Missing .PHONY
**Symptom**: Target doesn't rebuild when it should.
**Cause**: A file with the same name as the target exists.
**Fix**: Add to `.PHONY`.

### Variable expansion in prerequisites
**Symptom**: Prerequisites are empty or wrong.
**Cause**: Variable defined after the rule using `=` vs `:=`.
```makefile
# Works (deferred expansion):
SRCS = main.c util.c
prog: $(SRCS)

# Fails (immediate expansion, SRCS not yet defined):
prog: $(SRCS)
SRCS := main.c util.c
```

### Shell vs make variables
**Symptom**: `$variable` expands to nothing or wrong value.
**Cause**: `$x` is a make variable (single char). Use `$$x` for shell variables.
```makefile
target:
	for f in *.c; do echo $$f; done    # $$ → $ in shell
```

### Parallel build race conditions
**Symptom**: Build fails intermittently with `-j`, works with `-j1`.
**Cause**: Missing prerequisites — two targets use the same generated file.
**Fix**: Add the missing dependency. Use grouped targets (`&:`) for multi-output rules.

### Recursive variable infinite loop
**Symptom**: `*** Recursive variable 'FOO' references itself (eventually).`
```makefile
# BAD:
CFLAGS = $(CFLAGS) -Wall     # infinite recursion
# GOOD:
CFLAGS := $(CFLAGS) -Wall    # simply expanded
CFLAGS += -Wall               # append
```

## The remake Debugger

`remake` is a patched GNU Make with a built-in debugger. Install via package manager.

```bash
remake -X target              # break at target
remake -x target              # trace execution

# Debugger commands (GDB-like):
# step, next, continue, print, info, break, where, quit
```

### Without remake: poor man's breakpoint
```makefile
breakpoint:
	@echo "=== BREAKPOINT ==="
	@echo "Target: $@"
	@echo "Prerequisites: $^"
	@echo "Press Enter to continue..." && read
```

## Systematic Debugging Workflow

When a make build doesn't behave as expected:

1. **Identify the symptom**: wrong target, wrong commands, unnecessary rebuilds, missing rebuilds
2. **Dry run**: `make -n target` — see what WOULD happen
3. **Check the database**: `make -p | grep -A10 'target:'` — see what make knows
4. **Check timestamps**: `ls -la target prereqs` — compare modification times
5. **Check variables**: `make print-VARNAME` — verify values and origins
6. **Enable debug**: `make --debug=basic target` — see decision-making
7. **Check implicit rules**: `make --debug=implicit target` — if rule search is involved
8. **Isolate**: simplify the Makefile to the minimal reproducing case
