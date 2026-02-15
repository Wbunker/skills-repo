# Commands & Recipes

## Table of Contents
- [Recipe Execution Model](#recipe-execution-model)
- [Command Modifiers](#command-modifiers)
- [Error Handling](#error-handling)
- [ONESHELL](#oneshell)
- [SHELL and SHELLFLAGS](#shell-and-shellflags)
- [Parallel Execution (-j)](#parallel-execution--j)
- [Canned Recipes](#canned-recipes)
- [Recursive Make](#recursive-make-in-recipes)
- [Command Line Length Limits](#command-line-length-limits)

## Recipe Execution Model

Each line of a recipe runs in a **separate shell invocation**:

```makefile
# WRONG — cd has no effect on the second line:
target:
	cd subdir
	gcc -c foo.c

# RIGHT — use && or ; in one line:
target:
	cd subdir && gcc -c foo.c

# RIGHT — use backslash continuation:
target:
	cd subdir && \
	gcc -c foo.c
```

Make checks the exit status of each line. If any line returns non-zero, make stops and reports an error (unless error handling modifiers are used).

## Command Modifiers

Prefix characters on recipe lines:

| Prefix | Effect |
|--------|--------|
| `@` | Suppress echoing the command |
| `-` | Ignore errors (continue on failure) |
| `+` | Run even with `make -n` (dry run) |

Can combine: `-@cmd` suppresses echo and ignores errors.

```makefile
install:
	@echo "Installing..."           # don't echo the echo
	-rm -f $(PREFIX)/bin/old        # ok if file doesn't exist
	+$(MAKE) -C subdir              # always run sub-make, even in dry-run

clean:
	@rm -rf build/                  # quiet cleanup
```

### Global echo suppression
`make -s` or `MAKEFLAGS += -s` suppresses all echoing. The `@` prefix is then redundant.

## Error Handling

### Per-line: `-` prefix
```makefile
clean:
	-rm -f *.o          # keep going if files don't exist
```

### Global: `make -k` (keep going)
Continue building other targets after an error. Useful for finding all errors in a build, not just the first.

### Global: `make -i` (ignore all errors)
Rarely useful — prefer targeted `-` prefixes.

### .DELETE_ON_ERROR
```makefile
.DELETE_ON_ERROR:
```
Deletes the target file if its recipe fails. **Always use this** — prevents corrupt partial files from appearing "up to date" on the next run. Not the default for historical reasons.

### Checking command existence
```makefile
REQUIRED_CMDS := gcc ar ld
$(foreach cmd,$(REQUIRED_CMDS),\
  $(if $(shell which $(cmd) 2>/dev/null),,\
    $(error "$(cmd) not found in PATH")))
```

## ONESHELL

GNU Make 3.82+. Run the entire recipe in a single shell invocation:

```makefile
.ONESHELL:

deploy:
	#!/bin/bash
	set -euo pipefail
	cd $(BUILD_DIR)
	tar czf release.tar.gz .
	scp release.tar.gz server:/deploy/
	ssh server "cd /deploy && tar xzf release.tar.gz"
```

With `.ONESHELL`:
- Shell state (cd, variables, etc.) persists across lines
- Only the first line's `@`/`-`/`+` prefix applies
- A shebang (`#!`) on the first line selects the interpreter
- **Caution**: `$` must be `$$` unless it's a make variable reference

### Per-recipe alternative without ONESHELL
```makefile
deploy:
	bash -c '\
	  set -euo pipefail; \
	  cd $(BUILD_DIR); \
	  tar czf release.tar.gz .'
```

## SHELL and SHELLFLAGS

```makefile
SHELL := /bin/bash           # default is /bin/sh
.SHELLFLAGS := -eu -o pipefail -c    # default is -c
```

**Best practice for bash recipes**:
```makefile
SHELL := /bin/bash
.SHELLFLAGS := -euo pipefail -c
```

This enables:
- `-e`: Exit on error
- `-u`: Error on undefined variables
- `-o pipefail`: Catch errors in piped commands

**Note**: `SHELL` in a Makefile does NOT affect the user's shell. It only controls recipe execution.

## Parallel Execution (-j)

```bash
make -j8                     # 8 parallel jobs
make -j$(nproc)              # one job per CPU core
make -j                      # unlimited parallelism (dangerous)
```

### Output synchronization (GNU Make 4.0+)
```bash
make -j8 -O                  # --output-sync=target (default grouping)
make -j8 -Oline              # group output by line
make -j8 -Otarget            # group output by target
make -j8 -Orecurse           # group output by recursive make
```

### Controlling parallelism in the Makefile
```makefile
.NOTPARALLEL:                # disable parallel for this makefile

# Or mark specific targets:
.NOTPARALLEL: deploy         # GNU Make 4.4+
```

### .WAIT (GNU Make 4.4+)
Sequencing barrier in prerequisite lists:
```makefile
all: setup .WAIT compile .WAIT package
```

### Job server
When using recursive make with `-j`, GNU Make coordinates a job server (via a pipe or named pipe) so child makes share the same job pool. Use `$(MAKE)` (not `make`) to participate in the job server.

## Canned Recipes

Reusable recipe fragments using `define`:

```makefile
define compile-c
@echo "CC $<"
$(CC) $(CFLAGS) $(CPPFLAGS) -c $< -o $@
endef

%.o: %.c
	$(compile-c)

special.o: special.c
	$(compile-c)
	@echo "Special post-processing"
```

## Recursive Make in Recipes

```makefile
# ALWAYS use $(MAKE), never bare "make":
subsystem:
	$(MAKE) -C lib
	$(MAKE) -C src

# Pass variables:
subsystem:
	$(MAKE) -C lib CC=$(CC) CFLAGS="$(CFLAGS)"

# Or export them:
export CC CFLAGS
subsystem:
	$(MAKE) -C lib
```

Using `$(MAKE)` ensures:
- The same make binary is used
- Job server coordination works
- `make -n` properly propagates (via `+` implicit flag)
- `MAKEFLAGS` propagates correctly

## Command Line Length Limits

Some systems limit command line length (especially Windows). Workarounds:

### Response files
```makefile
lib.a: $(OBJS)
	$(file >$@.cmd,$^)
	$(AR) rcs $@ @$@.cmd
	@rm -f $@.cmd
```

### Batched invocations
```makefile
# Process files in batches:
lib.a: $(OBJS)
	$(AR) rcs $@ $(wordlist 1,50,$^)
	$(AR) rs $@ $(wordlist 51,100,$^)
```

### Using xargs
```makefile
clean:
	echo $(OBJS) | xargs rm -f
```
