# Java Patterns

## Table of Contents
- [Challenges of Java with Make](#challenges-of-java-with-make)
- [Basic Java Makefile](#basic-java-makefile)
- [Handling javac's Behavior](#handling-javacs-behavior)
- [Classpath Management](#classpath-management)
- [JAR Files](#jar-files)
- [Package and Directory Structure](#package-and-directory-structure)
- [Dependency Management](#dependency-management)
- [Multi-Module Projects](#multi-module-projects)
- [Integration with Java Tools](#integration-with-java-tools)
- [Hybrid Builds](#hybrid-builds)

## Challenges of Java with Make

Java presents unique challenges for make compared to C/C++:

1. **javac compiles multiple files at once** — passing all sources is faster than one-at-a-time compilation. javac resolves cross-file dependencies internally.
2. **Package structure = directory structure** — source files must live in directories matching their `package` declaration.
3. **No linker step** — Java has no separate link phase. The JVM loads classes at runtime.
4. **Inner classes produce extra .class files** — `Foo.java` may produce `Foo.class`, `Foo$Bar.class`, `Foo$1.class`, etc. Make can't predict these.
5. **Classpath management** — the classpath replaces include paths and library paths in one mechanism.

Despite these challenges, make works well for Java when you adopt the right patterns.

## Basic Java Makefile

```makefile
# Directories
SRCDIR    := src
BUILDDIR  := build/classes
DISTDIR   := dist

# Tools
JAVAC     ?= javac
JAVA      ?= java
JAR       ?= jar

# Flags
JFLAGS    := -g -Xlint:all
CLASSPATH :=

# Sources and classes
SRCS := $(shell find $(SRCDIR) -name '*.java')
CLASSES := $(patsubst $(SRCDIR)/%.java,$(BUILDDIR)/%.class,$(SRCS))

# Default target
all: $(BUILDDIR)/.built

# Compile all sources at once (see below for why)
$(BUILDDIR)/.built: $(SRCS) | $(BUILDDIR)
	$(JAVAC) $(JFLAGS) $(if $(CLASSPATH),-cp $(CLASSPATH)) \
	    -d $(BUILDDIR) $(SRCS)
	@touch $@

$(BUILDDIR):
	mkdir -p $@

clean:
	rm -rf $(BUILDDIR) $(DISTDIR)

.PHONY: all clean
.DELETE_ON_ERROR:
```

### Why compile all sources at once
javac resolves inter-file dependencies internally. Compiling one file at a time:
- Is much slower (JVM startup per file)
- May fail on circular dependencies that javac handles when given all sources
- Misses optimization opportunities

The sentinel file `.built` tracks whether any source has changed since the last full compile.

## Handling javac's Behavior

### The inner class problem
`Foo.java` can produce:
- `Foo.class`
- `Foo$InnerClass.class`
- `Foo$1.class` (anonymous class)
- `Foo$1$1.class` (nested anonymous)

Make can't predict these outputs. Solutions:

#### Sentinel file approach (recommended)
```makefile
$(BUILDDIR)/.built: $(SRCS)
	$(JAVAC) $(JFLAGS) -d $(BUILDDIR) $?
	@touch $@
```

Using `$?` (newer prerequisites) compiles only changed files. javac will also compile any files they depend on.

#### Incremental compilation with dependency tracking
```makefile
# Compile changed sources and their dependents:
$(BUILDDIR)/.built: $(SRCS)
	$(JAVAC) $(JFLAGS) -d $(BUILDDIR) \
	    -sourcepath $(SRCDIR) $?
	@touch $@
```

The `-sourcepath` flag tells javac where to find sources that changed files depend on, so it can recompile dependents automatically.

### Source vs class timestamp mismatches
javac may not update a .class file if the source change doesn't affect the bytecode. This is actually desirable — it prevents unnecessary downstream rebuilds.

## Classpath Management

### Separating compile and runtime classpaths
```makefile
# Compile-time dependencies:
COMPILE_CP := lib/guava.jar:lib/jsr305.jar

# Runtime additions:
RUNTIME_CP := $(COMPILE_CP):lib/logback.jar:$(BUILDDIR)

# Platform-independent separator:
ifeq ($(OS),Windows_NT)
  CPSEP := ;
else
  CPSEP := :
endif

COMPILE_CP := $(subst :,$(CPSEP),lib/guava.jar lib/jsr305.jar)
```

### Collecting JARs automatically
```makefile
JARS := $(wildcard lib/*.jar)
CLASSPATH := $(subst $(space),$(CPSEP),$(JARS))

# Helper:
empty :=
space := $(empty) $(empty)
```

### Classpath for sub-modules
```makefile
MODULE_A_CP := $(BUILDDIR)/module-a
MODULE_B_CP := $(BUILDDIR)/module-b:$(MODULE_A_CP)

build-module-b: build-module-a
	$(JAVAC) $(JFLAGS) -cp $(MODULE_B_CP) \
	    -d $(BUILDDIR)/module-b \
	    $(shell find modules/b/src -name '*.java')
```

## JAR Files

### Creating a JAR
```makefile
JARFILE := $(DISTDIR)/myapp.jar
MAIN_CLASS := com.example.Main

$(JARFILE): $(BUILDDIR)/.built | $(DISTDIR)
	$(JAR) cfe $@ $(MAIN_CLASS) -C $(BUILDDIR) .

$(DISTDIR):
	mkdir -p $@
```

`cfe` flags: **c**reate, **f**ile, **e**ntrypoint (Main-Class in manifest).

### JAR with custom manifest
```makefile
MANIFEST := src/META-INF/MANIFEST.MF

$(JARFILE): $(BUILDDIR)/.built $(MANIFEST) | $(DISTDIR)
	$(JAR) cfm $@ $(MANIFEST) -C $(BUILDDIR) .
```

```
# src/META-INF/MANIFEST.MF
Main-Class: com.example.Main
Class-Path: lib/guava.jar lib/commons-io.jar
```

### Fat JAR (uber-jar)
```makefile
FATJAR := $(DISTDIR)/myapp-all.jar

$(FATJAR): $(BUILDDIR)/.built | $(DISTDIR)
	mkdir -p $(BUILDDIR)/fatjar
	# Extract dependency JARs:
	$(foreach jar,$(JARS),cd $(BUILDDIR)/fatjar && $(JAR) xf ../../$(jar);)
	# Copy project classes:
	cp -r $(BUILDDIR)/com $(BUILDDIR)/fatjar/
	# Create fat JAR:
	cd $(BUILDDIR)/fatjar && $(JAR) cfe ../../$@ $(MAIN_CLASS) .
	rm -rf $(BUILDDIR)/fatjar
```

### Source JAR
```makefile
$(DISTDIR)/myapp-sources.jar: $(SRCS) | $(DISTDIR)
	$(JAR) cf $@ -C $(SRCDIR) .
```

## Package and Directory Structure

### Standard Maven/Gradle-like layout
```
project/
├── Makefile
├── src/
│   └── main/java/
│       └── com/example/
│           ├── Main.java
│           └── util/
│               └── Helper.java
├── src/
│   └── test/java/
│       └── com/example/
│           └── MainTest.java
├── lib/                    # dependency JARs
└── build/
    ├── classes/            # compiled production classes
    └── test-classes/       # compiled test classes
```

```makefile
MAIN_SRCDIR := src/main/java
TEST_SRCDIR := src/test/java
MAIN_BUILDDIR := build/classes
TEST_BUILDDIR := build/test-classes

MAIN_SRCS := $(shell find $(MAIN_SRCDIR) -name '*.java')
TEST_SRCS := $(shell find $(TEST_SRCDIR) -name '*.java')
```

### Handling source roots
```makefile
# Multiple source roots:
SRC_ROOTS := src/main/java src/generated/java

SRCS := $(foreach root,$(SRC_ROOTS),$(shell find $(root) -name '*.java'))

compile: $(SRCS)
	$(JAVAC) $(JFLAGS) -d $(BUILDDIR) \
	    $(addprefix -sourcepath ,$(subst $(space),:,$(SRC_ROOTS))) \
	    $(SRCS)
```

## Dependency Management

### Manual dependency JARs
```makefile
LIBDIR := lib

# Download dependencies (simple approach):
$(LIBDIR)/guava-32.1.jar:
	mkdir -p $(LIBDIR)
	curl -Lo $@ "https://repo1.maven.org/maven2/com/google/guava/guava/32.1.3-jre/guava-32.1.3-jre.jar"

deps: $(LIBDIR)/guava-32.1.jar $(LIBDIR)/slf4j-api-2.0.jar
```

### Integration with Maven for dependency resolution
```makefile
# Use Maven just for dependency download:
.PHONY: deps
deps:
	mvn dependency:copy-dependencies -DoutputDirectory=$(CURDIR)/lib

# Then build with make:
JARS := $(wildcard lib/*.jar)
CLASSPATH := $(subst $(space),:,$(JARS))
```

### Annotation processing
```makefile
PROCESSOR_CP := lib/auto-value.jar
GENERATED_DIR := build/generated

compile: $(SRCS)
	mkdir -p $(GENERATED_DIR)
	$(JAVAC) $(JFLAGS) \
	    -processorpath $(PROCESSOR_CP) \
	    -s $(GENERATED_DIR) \
	    -d $(BUILDDIR) $(SRCS)
```

## Multi-Module Projects

### Module-per-directory with dependencies
```makefile
define java-module
$(1)_SRCS := $$(shell find modules/$(1)/src -name '*.java')
$(1)_CP := $$(subst $$(space),:,$$(foreach dep,$$($(1)_DEPS),build/$$(dep)))
$(1)_BUILDDIR := build/$(1)

.PHONY: build-$(1)
build-$(1): $$(foreach dep,$$($(1)_DEPS),build-$$(dep))
	@mkdir -p $$($(1)_BUILDDIR)
	$$(JAVAC) $$(JFLAGS) \
	    $$(if $$($(1)_CP),-cp $$($(1)_CP)) \
	    -d $$($(1)_BUILDDIR) $$($(1)_SRCS)

jar-$(1): build-$(1)
	$$(JAR) cf dist/$(1).jar -C $$($(1)_BUILDDIR) .
endef

# Module declarations:
core_DEPS :=
util_DEPS := core
web_DEPS := core util
app_DEPS := core util web

MODULES := core util web app
$(foreach m,$(MODULES),$(eval $(call java-module,$(m))))

all: $(addprefix build-,$(MODULES))
jars: $(addprefix jar-,$(MODULES))
```

### Java 9+ module system (JPMS)
```makefile
# Each module has a module-info.java:
compile-module:
	$(JAVAC) $(JFLAGS) \
	    --module-source-path "modules/*/src" \
	    --module $(MODULE_NAME) \
	    -d $(BUILDDIR)
```

## Integration with Java Tools

### Running the application
```makefile
.PHONY: run
run: $(JARFILE)
	$(JAVA) -jar $@ $(ARGS)

# Or without JAR:
run: compile
	$(JAVA) -cp $(CLASSPATH):$(BUILDDIR) $(MAIN_CLASS) $(ARGS)
```

### JUnit testing
```makefile
JUNIT_JAR := lib/junit-platform-console-standalone.jar
TEST_CP := $(JUNIT_JAR):$(BUILDDIR):$(TEST_BUILDDIR)

compile-tests: compile $(TEST_SRCS)
	mkdir -p $(TEST_BUILDDIR)
	$(JAVAC) $(JFLAGS) -cp $(BUILDDIR):$(JUNIT_JAR) \
	    -d $(TEST_BUILDDIR) $(TEST_SRCS)

.PHONY: test
test: compile-tests
	$(JAVA) -jar $(JUNIT_JAR) \
	    --class-path $(TEST_CP) \
	    --scan-class-path $(TEST_BUILDDIR)
```

### Javadoc
```makefile
DOCDIR := build/docs

.PHONY: javadoc
javadoc: $(SRCS)
	mkdir -p $(DOCDIR)
	javadoc -d $(DOCDIR) \
	    $(if $(CLASSPATH),-cp $(CLASSPATH)) \
	    -sourcepath $(SRCDIR) \
	    -subpackages com.example
```

### Checkstyle / SpotBugs
```makefile
CHECKSTYLE_JAR := lib/checkstyle.jar
CHECKSTYLE_CFG := config/checkstyle.xml

.PHONY: check
check: compile
	$(JAVA) -jar $(CHECKSTYLE_JAR) \
	    -c $(CHECKSTYLE_CFG) \
	    $(SRCS)
```

## Hybrid Builds

### JNI (Java + C/C++)
```makefile
JNI_SRCDIR := jni
JNI_INCLUDE := $(JAVA_HOME)/include
JNI_INCLUDE_OS := $(JNI_INCLUDE)/$(if $(findstring Darwin,$(shell uname)),darwin,linux)

# Generate JNI headers from Java classes:
jni-headers: compile
	javac -h $(JNI_SRCDIR) \
	    -d $(BUILDDIR) \
	    $(filter %NativeLib.java,$(SRCS))

# Compile native library:
UNAME := $(shell uname -s)
ifeq ($(UNAME),Darwin)
  JNI_EXT := .dylib
  JNI_FLAGS := -dynamiclib
else
  JNI_EXT := .so
  JNI_FLAGS := -shared -fPIC
endif

lib/libnative$(JNI_EXT): $(wildcard $(JNI_SRCDIR)/*.c) jni-headers
	$(CC) $(JNI_FLAGS) \
	    -I$(JNI_INCLUDE) -I$(JNI_INCLUDE_OS) \
	    $< -o $@

run-jni: $(JARFILE) lib/libnative$(JNI_EXT)
	$(JAVA) -Djava.library.path=lib -jar $(JARFILE)
```

### Java + Protocol Buffers
```makefile
PROTO_SRCS := $(wildcard proto/*.proto)
PROTO_JAVA := $(patsubst proto/%.proto,build/generated/%.java,$(PROTO_SRCS))

$(PROTO_JAVA): build/generated/%.java: proto/%.proto
	mkdir -p build/generated
	protoc --java_out=build/generated $<

# Add generated sources to compilation:
ALL_SRCS := $(SRCS) $(PROTO_JAVA)

compile: $(ALL_SRCS)
	$(JAVAC) $(JFLAGS) -cp $(CLASSPATH) \
	    -d $(BUILDDIR) $(ALL_SRCS)
```
