# Portability

## Table of Contents
- [POSIX Make vs GNU Make](#posix-make-vs-gnu-make)
- [Cross-Platform Recipes](#cross-platform-recipes)
- [Windows Considerations](#windows-considerations)
- [Portable Shell Idioms](#portable-shell-idioms)
- [Compiler and Toolchain Portability](#compiler-and-toolchain-portability)
- [Feature Detection](#feature-detection)

## POSIX Make vs GNU Make

### GNU-specific features (not in POSIX)
- `::=` is POSIX; `:=` is GNU (both work the same in GNU Make)
- Pattern rules (`%.o: %.c`) — POSIX uses suffix rules (`.c.o:`)
- `$(wildcard)`, `$(shell)`, `$(foreach)`, `$(eval)`, `$(call)`
- `?=`, `+=`, `!=` assignment operators
- `include` (POSIX has it but with different semantics)
- `-include` / `sinclude`
- `.PHONY`, `.SECONDEXPANSION`, `.ONESHELL`
- `--debug`, `-j` (parallel), `-O` (output sync)
- `$(file)` function
- Grouped targets (`&:`)
- Target-specific and pattern-specific variables
- `define`/`endef` multi-line variables

### Portable subset
If targeting non-GNU make (BSD make, Solaris make):
```makefile
# Use suffix rules instead of pattern rules:
.SUFFIXES: .c .o
.c.o:
	$(CC) $(CFLAGS) -c $<

# Use only =, not :=, ?=, +=
# Avoid $(shell), $(wildcard), $(foreach), $(eval), $(call)
# Use backtick instead of $(shell):
DATE = `date +%Y-%m-%d`
```

### BSD Make differences
- Uses `.include` instead of `include`
- Uses `.if`/`.else`/`.endif` instead of `ifeq`/`else`/`endif`
- Different automatic variables (e.g., `.ALLSRC` instead of `$^`)
- Conditional assignment uses `!=` differently

## Cross-Platform Recipes

### OS detection
```makefile
UNAME := $(shell uname -s)

ifeq ($(UNAME),Linux)
  PLATFORM := linux
  SHARED_EXT := .so
  SHARED_FLAG := -shared
endif
ifeq ($(UNAME),Darwin)
  PLATFORM := macos
  SHARED_EXT := .dylib
  SHARED_FLAG := -dynamiclib
endif
ifneq ($(findstring MINGW,$(UNAME)),)
  PLATFORM := windows
  SHARED_EXT := .dll
  SHARED_FLAG := -shared
  EXE_EXT := .exe
endif
```

### Portable commands
```makefile
# Use variables for commands that differ across platforms:
RM      ?= rm -f
RMDIR   ?= rm -rf
MKDIR   ?= mkdir -p
INSTALL ?= install
CP      ?= cp -f

# Avoid platform-specific commands in recipes:
clean:
	$(RM) $(OBJS) $(PROGRAM)$(EXE_EXT)
	$(RMDIR) $(BUILDDIR)
```

### Path separators
```makefile
# Use / everywhere — even Windows make handles it:
BUILDDIR := build/$(PLATFORM)
```

## Windows Considerations

### cmd.exe vs shell
On Windows, make defaults to `cmd.exe` (or `command.com`). GNU Make for Windows may use `sh.exe` if found.

```makefile
# Force sh on Windows if available:
ifdef COMSPEC
  SHELL := sh.exe
endif

# Or write Windows-compatible recipes:
clean:
ifdef COMSPEC
	del /Q $(subst /,\,$(OBJS))
else
	rm -f $(OBJS)
endif
```

### Common pitfalls on Windows
- Backslash `\` in paths conflicts with make's line continuation
- `cmd.exe` doesn't support `&&` the same way as Unix shells
- No `mkdir -p` equivalent (use `if not exist dir mkdir dir`)
- File path length limits (260 chars by default)
- Case-insensitive filenames can confuse pattern matching

### MSYS2/MinGW
The most practical approach: use MSYS2 to get a Unix-like environment on Windows. This makes most Makefiles work without modification.

## Portable Shell Idioms

### Commands to avoid or abstract
| Avoid | Portable alternative | Why |
|-------|---------------------|-----|
| `install -D` | `mkdir -p dir && install file dir/` | `-D` is GNU coreutils extension |
| `readlink -f` | `cd dir && pwd` | Not available on macOS |
| `sed -i` | `sed 's/.../' file > tmp && mv tmp file` | `-i` syntax differs (GNU vs BSD) |
| `grep -P` | `grep -E` | `-P` (Perl regex) not universal |
| `which` | `command -v` | `which` behavior varies |
| `echo -n` | `printf '%s'` | `-n` not POSIX |

### Safe shell patterns
```makefile
# Test if command exists:
HAS_TOOL := $(shell command -v tool 2>/dev/null)
ifdef HAS_TOOL
  # use tool
endif

# Safe temporary files:
target:
	tempfile=$$(mktemp) && \
	command > "$$tempfile" && \
	mv "$$tempfile" $@

# Portable /dev/null:
DEVNULL := /dev/null
ifdef COMSPEC
  DEVNULL := NUL
endif
```

## Compiler and Toolchain Portability

### Compiler detection
```makefile
# Detect compiler type:
CC_VERSION := $(shell $(CC) --version 2>/dev/null)

ifneq ($(findstring clang,$(CC_VERSION)),)
  COMPILER := clang
else ifneq ($(findstring GCC,$(CC_VERSION)),)
  COMPILER := gcc
endif

# Compiler-specific flags:
WARNINGS_gcc := -Wall -Wextra -Wpedantic
WARNINGS_clang := -Wall -Wextra -Wpedantic -Weverything
CFLAGS += $(WARNINGS_$(COMPILER))
```

### pkg-config portability
```makefile
# Guard against missing pkg-config:
PKG_CONFIG ?= pkg-config

ifneq ($(shell $(PKG_CONFIG) --exists libfoo && echo yes),yes)
  $(error libfoo not found. Install libfoo-dev or set PKG_CONFIG_PATH)
endif

FOO_CFLAGS := $(shell $(PKG_CONFIG) --cflags libfoo)
FOO_LIBS := $(shell $(PKG_CONFIG) --libs libfoo)
```

## Feature Detection

### GNU Make version checking
```makefile
MAKE_VERSION_MAJOR := $(word 1,$(subst ., ,$(MAKE_VERSION)))
MAKE_VERSION_MINOR := $(word 2,$(subst ., ,$(MAKE_VERSION)))

# Require GNU Make 4.0+:
ifneq ($(shell test $(MAKE_VERSION_MAJOR) -ge 4 && echo yes),yes)
  $(error GNU Make 4.0+ required, found $(MAKE_VERSION))
endif
```

### Feature-based detection
```makefile
# Check for grouped targets support (4.3+):
ifneq ($(findstring grouped-target,$(.FEATURES)),)
  HAVE_GROUPED_TARGETS := 1
endif

# Check for output-sync (4.0+):
ifneq ($(findstring output-sync,$(.FEATURES)),)
  MAKEFLAGS += -Otarget
endif
```

### .FEATURES reference
GNU Make 4.x+ exposes supported features in `.FEATURES`:
`archives`, `check-symlink`, `else-if`, `extra-prereqs`, `grouped-target`, `guile`, `jobserver`, `jobserver-fifo`, `load`, `notintermediate`, `oneshell`, `order-only`, `output-sync`, `second-expansion`, `shortest-stem`, `target-specific`, `undefine`
