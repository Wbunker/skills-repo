---
name: gnu-make
description: >
  Expert-level GNU Make assistance covering Makefile authoring, debugging,
  optimization, and project architecture. Use when the user is working with
  Makefiles, writing make rules, debugging build issues, asking about GNU Make
  syntax or semantics, discussing build systems based on make, or mentions
  "make", "Makefile", "gmake", ".PHONY", pattern rules, automatic variables,
  or recursive make. Covers rules, variables, functions, commands, implicit
  rules, large project organization, debugging, and portability.
---

# GNU Make Expert

## Core Quick Reference

### Rule anatomy
```makefile
target: prerequisite1 prerequisite2
	command1
	command2
```

Recipes MUST use literal tab characters, not spaces.

### Essential automatic variables
| Variable | Meaning |
|----------|---------|
| `$@` | Target filename |
| `$<` | First prerequisite |
| `$^` | All prerequisites (deduped) |
| `$+` | All prerequisites (with dupes) |
| `$*` | Stem matched by `%` in pattern rule |
| `$(@D)` / `$(@F)` | Directory / filename part of `$@` |
| `$(<D)` / `$(<F)` | Directory / filename part of `$<` |

### Variable flavors
```makefile
RECURSIVE = $(OTHER)       # expanded every time referenced
IMMEDIATE := $(OTHER)      # expanded once at assignment
CONDITIONAL ?= default     # set only if not already defined
APPEND += more             # append to existing value
SHELL_OUT != command       # assign output of shell command (GNU 4.0+)
```

### Key built-in functions
```makefile
$(subst from,to,text)          $(patsubst pattern,replacement,text)
$(filter pattern...,text)      $(filter-out pattern...,text)
$(sort list)                   $(word n,text)
$(words text)                  $(firstword text)
$(wildcard pattern)            $(dir names)
$(notdir names)                $(suffix names)
$(basename names)              $(addsuffix suffix,names)
$(addprefix prefix,names)      $(join list1,list2)
$(foreach var,list,text)       $(call func,args...)
$(if cond,then,else)           $(or cond1,cond2...)
$(and cond1,cond2...)          $(eval text)
$(value variable)              $(origin variable)
$(flavor variable)             $(shell command)
$(error text)                  $(warning text)
$(info text)                   $(file op,filename,text)
```

### Critical special targets
```makefile
.PHONY: clean install test          # not real files
.DEFAULT_GOAL := all                # override default target
.SUFFIXES:                          # disable built-in suffix rules
.DELETE_ON_ERROR:                   # delete targets on recipe failure
.SECONDEXPANSION:                   # enable $$(...) in prerequisites
.ONESHELL:                          # run entire recipe in one shell
```

## Quick debugging

Print any variable:
```makefile
$(info DEBUG: VAR is [$(VAR)])
```

Dry run: `make -n`
Print database: `make -p`
Debug output: `make -d` or `make --debug=basic`
Trace remake decisions: `make --debug=why` (GNU Make 4.0+)
Remake with explanation: `make -r --debug=basic`

For in-depth debugging techniques, read [references/debugging.md](references/debugging.md).

## Reference Documents

Load these as needed based on the specific topic:

| Topic | File | When to read |
|-------|------|-------------|
| **Rules & Targets** | [references/rules.md](references/rules.md) | Pattern rules, implicit rules, static patterns, multiple targets, order-only prerequisites, VPATH/vpath |
| **Variables & Macros** | [references/variables.md](references/variables.md) | Variable scoping, `define`/`endef`, target-specific variables, override, private, unexport, computed variable names |
| **Functions** | [references/functions.md](references/functions.md) | String/file/list manipulation functions, `$(call)`, `$(eval)`, `$(foreach)`, user-defined functions, function programming patterns |
| **Commands & Recipes** | [references/commands.md](references/commands.md) | Recipe execution model, `.ONESHELL`, error handling, parallel make (`-j`), command modifiers (`@`, `-`, `+`), `.SHELLFLAGS`, canned recipes |
| **Large Projects** | [references/large-projects.md](references/large-projects.md) | Recursive vs non-recursive make, `include`, multi-directory builds, generated dependencies, auto-dependency generation, build trees |
| **Debugging** | [references/debugging.md](references/debugging.md) | Systematic debugging, `--warn-undefined-variables`, `$(warning)` tracing, remake database, common pitfalls, debugging recursive make |
| **Performance** | [references/performance.md](references/performance.md) | Parallel builds, job server, `.NOTPARALLEL`, reducing shell invocations, lazy evaluation pitfalls, caching patterns |
| **Portability** | [references/portability.md](references/portability.md) | POSIX make vs GNU extensions, cross-platform recipes, Windows considerations, portable shell idioms |
| **Macros** | [references/macros.md](references/macros.md) | `define`/`endef` templates, `$(call)` parameterization, `$(eval)` code generation, call+eval+foreach metaprogramming, escaping, canned recipes |
| **C/C++ Patterns** | [references/c-cpp-patterns.md](references/c-cpp-patterns.md) | Auto-dependency generation with `-MMD -MP`, separate build directories, library building, compiler flag management |
| **Java Patterns** | [references/java-patterns.md](references/java-patterns.md) | javac batch compilation, classpath management, JAR creation, multi-module projects, JNI, sentinel file pattern |
