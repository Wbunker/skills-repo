# Managing Large Projects

## Table of Contents
- [Recursive vs Non-Recursive Make](#recursive-vs-non-recursive-make)
- [Recursive Make Architecture](#recursive-make-architecture)
- [Non-Recursive Make Architecture](#non-recursive-make-architecture)
- [The include Directive](#the-include-directive)
- [Auto-Dependency Generation](#auto-dependency-generation)
- [Separate Build Directories](#separate-build-directories)
- [Multi-Configuration Builds](#multi-configuration-builds)
- [Makefile Organization Patterns](#makefile-organization-patterns)
- [Generated Sources and Prerequisites](#generated-sources-and-prerequisites)

## Recursive vs Non-Recursive Make

### Recursive make
Each subdirectory has its own Makefile. The top-level Makefile invokes sub-makes.

**Pros**: Modular, subdirectories are self-contained, easy to understand individually.
**Cons**: The "Recursive Make Considered Harmful" problem — incomplete dependency graph across directories. Can lead to:
- Incorrect parallel builds (missing cross-directory deps)
- Over-building (rebuilding too much)
- Under-building (missing rebuilds)
- Slower (sequential sub-make invocations)

### Non-recursive make
A single make invocation reads all sources. Subdirectory files contribute to one global dependency graph.

**Pros**: Complete dependency graph, correct parallel builds, faster.
**Cons**: More complex setup, all variables share global namespace, harder to modularize.

### Hybrid approach
Use non-recursive make for tightly coupled components, recursive for truly independent subsystems.

## Recursive Make Architecture

### Standard pattern
```makefile
# Top-level Makefile
SUBDIRS := lib src tools tests

.PHONY: all clean $(SUBDIRS)

all: $(SUBDIRS)

# Ordering constraints:
src: lib
tools: lib src

$(SUBDIRS):
	$(MAKE) -C $@

clean:
	$(foreach dir,$(SUBDIRS),$(MAKE) -C $(dir) clean;)
```

### Passing variables to sub-makes
```makefile
# Method 1: export
export CC CFLAGS LDFLAGS

# Method 2: command line (highest priority)
$(SUBDIRS):
	$(MAKE) -C $@ CC=$(CC) CFLAGS="$(CFLAGS)"

# Method 3: shared config file included by all sub-Makefiles
# config.mk:
CC := gcc
CFLAGS := -Wall -O2
# subdirectory Makefile:
include ../config.mk
```

### MAKEFLAGS and the environment
Variables passed on the make command line are automatically propagated to sub-makes via `MAKEFLAGS`. `export` sends variables through the environment.

### Preventing variable inheritance
```makefile
unexport PRIVATE_VAR                    # hide from sub-makes
$(MAKE) -C subdir MAKEFLAGS=            # clear all flags (use carefully)
```

## Non-Recursive Make Architecture

### The Miller pattern (from "Recursive Make Considered Harmful")

Each directory provides a fragment that's included by the top-level Makefile:

```makefile
# Top-level Makefile
MODULES := lib src tools

# Initialize:
SRCS :=
PROGRAMS :=

# Include module definitions:
include $(patsubst %,%/module.mk,$(MODULES))

# Global rules:
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@
```

```makefile
# lib/module.mk
lib_SRCS := lib/util.c lib/hash.c lib/list.c
lib_OBJS := $(lib_SRCS:.c=.o)

SRCS += $(lib_SRCS)

lib/libutil.a: $(lib_OBJS)
	$(AR) rcs $@ $^
```

```makefile
# src/module.mk
src_SRCS := src/main.c src/parse.c
src_OBJS := $(src_SRCS:.c=.o)

SRCS += $(src_SRCS)

src/program: $(src_OBJS) lib/libutil.a
	$(CC) $(LDFLAGS) $^ -o $@

PROGRAMS += src/program
```

### Namespace convention
Prefix all module variables with the module name to avoid collisions:
```makefile
auth_SRCS := ...
auth_OBJS := ...
auth_CFLAGS := ...
```

### Automatic module discovery
```makefile
MODULES := $(patsubst %/module.mk,%,$(wildcard */module.mk))
include $(addsuffix /module.mk,$(MODULES))
```

## The include Directive

```makefile
include config.mk lib/deps.mk           # error if not found
-include generated.mk                   # silent if not found (same as sinclude)
```

### Makefile remaking
Make treats included makefiles as targets. If a rule exists to update an included file, make rebuilds it first, then restarts:

```makefile
-include deps.mk

deps.mk: $(SRCS)
	$(CC) -MM $^ > $@
```

On first build, `deps.mk` doesn't exist. `-include` suppresses the error. Make then tries to build `deps.mk`, succeeds, and restarts — now with correct dependencies.

### Include search path
```makefile
# Directories searched for include:
# 1. Current directory
# 2. -I flags passed to make
# 3. /usr/local/include, /usr/include (compiled in)

make -I /path/to/shared/makefiles
```

## Auto-Dependency Generation

The gold standard for C/C++ projects. Use the compiler to generate prerequisite lists.

### Modern approach (GCC -MMD -MP)
```makefile
SRCS := $(wildcard src/*.c)
OBJS := $(SRCS:.c=.o)
DEPS := $(OBJS:.o=.d)

CFLAGS += -MMD -MP

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

-include $(DEPS)
```

- `-MMD`: Generate `.d` file as side effect of compilation (user headers only)
- `-MP`: Add phony targets for each header (prevents errors when headers are deleted)
- `-include $(DEPS)`: Include dependency files, ignoring if missing (first build)

### What -MP does
Without `-MP`, if you delete a header file, make fails with "No rule to make target 'deleted.h'". `-MP` generates empty phony targets for each header:
```makefile
# Generated foo.d:
foo.o: foo.c foo.h bar.h
foo.h:
bar.h:
```

### Dependency files in a build directory
```makefile
BUILDDIR := build
OBJS := $(addprefix $(BUILDDIR)/,$(SRCS:.c=.o))
DEPS := $(OBJS:.o=.d)

$(BUILDDIR)/%.o: %.c | $(BUILDDIR)
	$(CC) $(CFLAGS) -MMD -MP -c $< -o $@

-include $(DEPS)
```

## Separate Build Directories

Keep source trees clean by building into a separate directory:

### Simple pattern
```makefile
SRCDIR := src
BUILDDIR := build

SRCS := $(wildcard $(SRCDIR)/*.c)
OBJS := $(patsubst $(SRCDIR)/%.c,$(BUILDDIR)/%.o,$(SRCS))

$(BUILDDIR)/%.o: $(SRCDIR)/%.c | $(BUILDDIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILDDIR):
	mkdir -p $@
```

### Mirroring source tree structure
```makefile
SRCS := $(shell find src -name '*.c')
OBJS := $(patsubst src/%.c,build/%.o,$(SRCS))
DIRS := $(sort $(dir $(OBJS)))

$(OBJS): build/%.o: src/%.c | $(DIRS)
	$(CC) $(CFLAGS) -MMD -MP -c $< -o $@

$(DIRS):
	mkdir -p $@
```

### Out-of-tree builds via VPATH
```makefile
# Invoked as: mkdir build && cd build && make -f ../Makefile

VPATH = $(dir $(firstword $(MAKEFILE_LIST)))
```

## Multi-Configuration Builds

Building debug and release from the same source:

### Separate build directories
```makefile
.PHONY: debug release

debug:
	$(MAKE) BUILDDIR=build/debug CFLAGS="-g -O0 -DDEBUG" all

release:
	$(MAKE) BUILDDIR=build/release CFLAGS="-O2 -DNDEBUG" all
```

### Configuration file pattern
```makefile
# config.mk — generated or selected by configure step
BUILD_TYPE ?= debug
include config/$(BUILD_TYPE).mk

# config/debug.mk
CFLAGS := -g -O0 -DDEBUG -fsanitize=address
LDFLAGS := -fsanitize=address

# config/release.mk
CFLAGS := -O2 -DNDEBUG -flto
LDFLAGS := -flto
```

## Makefile Organization Patterns

### Layered includes
```
project/
├── Makefile              # top-level: includes everything
├── make/
│   ├── config.mk         # toolchain, flags, paths
│   ├── rules.mk          # pattern rules, generic recipes
│   └── functions.mk      # reusable make functions
├── lib/module.mk
├── src/module.mk
└── tests/module.mk
```

### Standard variable conventions
```makefile
# Directories:
PREFIX   ?= /usr/local
BINDIR   ?= $(PREFIX)/bin
LIBDIR   ?= $(PREFIX)/lib
INCDIR   ?= $(PREFIX)/include

# Tools:
CC       ?= gcc
CXX      ?= g++
AR       ?= ar
INSTALL  ?= install

# Flags (append, don't override):
CFLAGS   += -Wall
CPPFLAGS += -I$(INCDIR)
LDFLAGS  += -L$(LIBDIR)
LDLIBS   += -lm
```

Using `?=` and `+=` lets users override from the command line or environment.

## Generated Sources and Prerequisites

### Generated headers
```makefile
# Ensure generated headers exist before any compilation:
GENERATED_HEADERS := config.h version.h

$(OBJS): | $(GENERATED_HEADERS)    # order-only: don't rebuild on change

config.h: config.h.in configure
	./configure > $@

version.h: FORCE
	@echo '#define VERSION "$(shell git describe --tags)"' > $@.tmp
	@cmp -s $@ $@.tmp || mv $@.tmp $@
	@rm -f $@.tmp

FORCE:
```

The `cmp` trick avoids updating the timestamp when content hasn't changed, preventing unnecessary rebuilds.

### Protocol buffers, code generators
```makefile
PROTOS := $(wildcard proto/*.proto)
PROTO_CC := $(patsubst proto/%.proto,gen/%.pb.cc,$(PROTOS))
PROTO_H := $(patsubst proto/%.proto,gen/%.pb.h,$(PROTOS))

# Grouped target — one invocation produces both .cc and .h:
gen/%.pb.cc gen/%.pb.h &: proto/%.proto | gen
	protoc --cpp_out=gen $<

gen:
	mkdir -p $@
```
