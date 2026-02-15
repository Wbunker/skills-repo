# Macros

## Table of Contents
- [Macros vs Variables](#macros-vs-variables)
- [define/endef Fundamentals](#defineendef-fundamentals)
- [Parameterized Macros with call](#parameterized-macros-with-call)
- [Code Generation with eval](#code-generation-with-eval)
- [The call + eval + foreach Pattern](#the-call--eval--foreach-pattern)
- [Escaping and Expansion Control](#escaping-and-expansion-control)
- [Canned Recipes](#canned-recipes)
- [Macro Libraries](#macro-libraries)
- [Debugging Macros](#debugging-macros)
- [Advanced Patterns](#advanced-patterns)

## Macros vs Variables

In GNU Make, "macro" typically refers to a multi-line variable defined with `define`/`endef` that's used as a reusable code template — often invoked with `$(call)` and instantiated with `$(eval)`. Regular variables hold data; macros hold *procedures*.

```makefile
# Variable — holds data:
CFLAGS := -Wall -O2

# Macro — holds a procedure:
define compile
$(CC) $(CFLAGS) -c $< -o $@
endef
```

## define/endef Fundamentals

```makefile
define macro-name
line 1
line 2
line 3
endef
```

### Flavor control
```makefile
define DEFERRED =         # recursively expanded (default)
$(CC) $(CFLAGS) -c $<
endef

define IMMEDIATE :=       # simply expanded at definition time
$(CC) $(CFLAGS) -c $<
endef
```

With `=` (or no operator), the body is stored literally and expanded when referenced. With `:=`, the body is expanded immediately — automatic variables like `$<` become empty since there's no rule context yet.

**Rule of thumb**: Use `=` (deferred) for macros used in recipes. Use `:=` for macros that compute data at parse time.

### Whitespace behavior
- Leading whitespace on each line is preserved
- A blank line inside define/endef becomes a blank line in the expansion
- The final newline before `endef` is stripped
- `define` must be alone on its line (no trailing content)

### Nested define
Nested `define`/`endef` is supported in GNU Make 3.82+:
```makefile
define outer
  define inner
    nested content
  endef
endef
```

## Parameterized Macros with call

`$(call)` invokes a variable/macro with positional arguments. Arguments are bound to `$(1)`, `$(2)`, ..., `$(9)`. `$(0)` is the macro name.

```makefile
# Simple function:
greeting = Hello, $(1)! Welcome to $(2).
$(info $(call greeting,World,Make))
# → Hello, World! Welcome to Make.

# Multi-line macro:
define announce
@echo "==========================="
@echo "  $(1)"
@echo "==========================="
endef

deploy:
	$(call announce,Starting deployment)
	rsync -a build/ server:/app/
	$(call announce,Deployment complete)
```

### Argument handling
- Arguments are separated by commas
- Leading/trailing spaces in arguments are **not stripped** (use `$(strip)`)
- To pass a comma as an argument, define it: `comma := ,`
- To pass nothing, leave the position empty: `$(call func,,second)` — `$(1)` is empty
- Arguments beyond `$(9)` are not directly supported; pass a list and use `$(word)` to extract

```makefile
comma := ,
empty :=
space := $(empty) $(empty)

# Pass a comma:
$(call func,arg with $(comma) inside)
```

### call vs direct expansion
```makefile
# Direct expansion — no parameter substitution:
$(my-macro)

# call — substitutes $(1), $(2), etc.:
$(call my-macro,arg1,arg2)
```

Use `$(call)` only when you need parameterization. For macros used in recipes without arguments, direct `$(macro-name)` works fine and is slightly faster.

## Code Generation with eval

`$(eval)` parses its argument as makefile syntax. Combined with `$(call)`, it generates rules dynamically.

### Basic eval
```makefile
$(eval \
  extra.o: extra.c ; $$(CC) $$(CFLAGS) -c $$< -o $$@ \
)
```

### Two-phase expansion
This is the most important concept for mastering macros:

1. **Phase 1**: Make expands the `$(eval ...)` argument as a regular variable reference
2. **Phase 2**: The result is parsed as makefile text, and any remaining `$` references are expanded in their normal context

```makefile
VAR := hello

# Phase 1: $(VAR) → "hello", $$(info) → $(info)
# Phase 2: $(info hello) executes
$(eval $(info $(VAR)))

# In practice, for rule generation:
define my-rule
$(1): $(2)
	$$(CC) $$(CFLAGS) -c $$< -o $$@
endef

# Phase 1 of eval expands $(1) and $(2) from call
# Phase 2 handles $$(CC), $$(CFLAGS), $$<, $$@ in rule context
$(eval $(call my-rule,foo.o,foo.c))
```

### The escaping rule
| In the macro | After Phase 1 | After Phase 2 (in rule) |
|-------------|---------------|------------------------|
| `$(1)` | argument value | — |
| `$$(CC)` | `$(CC)` | compiler path |
| `$$@` | `$@` | target name |
| `$$$$` | `$$` | literal `$` |

## The call + eval + foreach Pattern

The canonical GNU Make metaprogramming pattern:

```makefile
# 1. Define a template macro:
define program-rules
$(1)_SRCS := $$(wildcard src/$(1)/*.c)
$(1)_OBJS := $$(patsubst src/%.c,build/%.o,$$($(1)_SRCS))

build/$(1): $$($(1)_OBJS)
	$$(CC) $$(LDFLAGS) $$^ $$(LDLIBS) -o $$@

.PHONY: clean-$(1)
clean-$(1):
	rm -f $$($(1)_OBJS) build/$(1)
endef

# 2. Instantiate for each program:
PROGRAMS := server client admin

$(foreach p,$(PROGRAMS),$(eval $(call program-rules,$(p))))

# 3. Aggregate:
all: $(addprefix build/,$(PROGRAMS))
clean: $(addprefix clean-,$(PROGRAMS))
```

### What happens step by step

For `$(eval $(call program-rules,server))`:

1. `$(call program-rules,server)` substitutes `$(1)` → `server`:
   ```makefile
   server_SRCS := $(wildcard src/server/*.c)
   server_OBJS := $(patsubst src/%.c,build/%.o,$(server_SRCS))

   build/server: $(server_OBJS)
   	$(CC) $(LDFLAGS) $^ $(LDLIBS) -o $@
   ```
   (Note: `$$` became `$` during call expansion)

2. `$(eval ...)` parses this as makefile text, creating the actual rules and variable assignments.

### Nested templates
```makefile
define library-template
$(1)_OBJS := $$(patsubst %.c,build/%.o,$$($(1)_SRCS))

build/lib$(1).a: $$($(1)_OBJS)
	$$(AR) rcs $$@ $$^
endef

define binary-template
$(1)_OBJS := $$(patsubst %.c,build/%.o,$$($(1)_SRCS))

build/$(1): $$($(1)_OBJS) $$(addprefix build/lib,$$(addsuffix .a,$$($(1)_LIBS)))
	$$(CC) $$(LDFLAGS) $$^ $$(LDLIBS) -o $$@
endef

# Define components:
libnet_SRCS := net/tcp.c net/udp.c net/dns.c
libauth_SRCS := auth/login.c auth/token.c

server_SRCS := server/main.c server/handler.c
server_LIBS := net auth

$(foreach lib,net auth,$(eval $(call library-template,$(lib))))
$(eval $(call binary-template,server))
```

## Escaping and Expansion Control

### Common escaping scenarios

```makefile
define rule-template
# Need literal $ in shell command:
$(1):
	price=$$$$100    # $$$$ → $$ (phase 1) → $ (shell)

# Need make variable in recipe:
	$$(CC) $$(CFLAGS) -o $$@ $$<

# Need function call deferred to phase 2:
	@echo $$(words $$($(1)_OBJS)) objects
endef
```

### Debugging expansion
Replace `$(eval ...)` with `$(info ...)` to see what would be parsed:
```makefile
# Debug mode:
$(info $(call program-rules,server))

# Production:
$(eval $(call program-rules,server))
```

### Using $(value) to prevent expansion
```makefile
define raw-template
$(CC) $(CFLAGS)
endef

# $(raw-template) expands CC and CFLAGS
# $(value raw-template) returns literal "$(CC) $(CFLAGS)"
```

## Canned Recipes

A simpler form of macros — multi-line recipes stored in `define` for reuse:

```makefile
define run-tests
@echo "Running tests in $(@D)..."
@cd $(@D) && ./run_tests.sh
@echo "Tests passed."
endef

test-lib: lib/tests
	$(run-tests)

test-src: src/tests
	$(run-tests)
```

No `$(call)` needed — automatic variables (`$@`, `$<`, etc.) work naturally because the macro is expanded in recipe context.

### Canned recipe with setup/teardown
```makefile
define with-tempdir
@tmpdir=$$(mktemp -d) && \
trap "rm -rf $$tmpdir" EXIT && \
$(1) && \
echo "Done."
endef

package:
	$(call with-tempdir, \
	  cp -r build/* $$tmpdir && \
	  tar czf release.tar.gz -C $$tmpdir . \
	)
```

## Macro Libraries

Organize reusable macros into includeable files:

```makefile
# make/macros.mk

# Assert variable is defined:
define assert-defined
$(if $(value $(1)),,$(error $(1) is not defined))
endef

# Create a directory target:
define directory-target
$(1):
	mkdir -p $$@
endef

# Generate compile rule for a source directory:
define compile-rules
$(1)/%.o: $(1)/%.c | $(1)
	$$(CC) $$(CFLAGS) $$(CPPFLAGS) -MMD -MP -c $$< -o $$@
endef
```

```makefile
# Main Makefile:
include make/macros.mk

$(call assert-defined,CC)
$(eval $(call directory-target,build))
$(eval $(call compile-rules,build))
```

## Debugging Macros

### Print macro definition
```makefile
print-macro = $(info $(value $(1)))

$(call print-macro,program-rules)
```

### Trace macro expansion
```makefile
# Wrap eval to trace:
debug-eval = $(info === BEGIN EVAL ===)$(info $(1))$(info === END EVAL ===)$(eval $(1))

$(call debug-eval,$(call program-rules,server))
```

### Common macro bugs

**Missing `$$` escaping**:
```makefile
# BUG: $@ expands to empty during eval:
define bad
$(1): $(2)
	$(CC) -o $@ $<
endef

# FIX:
define good
$(1): $(2)
	$$(CC) -o $$@ $$<
endef
```

**Whitespace in arguments**:
```makefile
# BUG: space after comma becomes part of $(2):
$(call func,arg1, arg2)    # $(2) is " arg2" not "arg2"

# FIX:
$(call func,arg1,arg2)
# Or: use $(strip $(2)) in the macro body
```

**Missing newline before endef**:
```makefile
# BUG: recipe line and endef on same line:
define bad
	$(CC) -c $< -o $@ endef    # "endef" is part of the command!

# FIX:
define good
	$(CC) -c $< -o $@
endef
```

## Advanced Patterns

### Macro that generates macros
```makefile
define define-accessor
$(1) = $$($(1)_$$(PLATFORM))
endef

$(foreach var,CC AR LD,$(eval $(call define-accessor,$(var))))

# Now CC expands to $(CC_linux) or $(CC_darwin) etc.
CC_linux := gcc
CC_darwin := clang
```

### Accumulator pattern
```makefile
MODULES :=
define register-module
MODULES += $(1)
$(1)_DIR := $(2)
endef

$(eval $(call register-module,auth,src/auth))
$(eval $(call register-module,db,src/db))
$(eval $(call register-module,web,src/web))
# MODULES is now "auth db web"
```

### Boolean logic with macros
```makefile
not = $(if $(1),,true)
and = $(if $(1),$(if $(2),true))
or = $(if $(1),true,$(if $(2),true))

# Usage:
$(if $(call and,$(HAVE_SSL),$(HAVE_ZLIB)),\
  $(info Both SSL and ZLIB available),\
  $(info Missing dependency))
```

### Map function
```makefile
map = $(foreach a,$(2),$(call $(1),$(a)))
upper = $(shell echo $(1) | tr a-z A-Z)

UPPER_NAMES := $(call map,upper,foo bar baz)
# → "FOO BAR BAZ"
```
