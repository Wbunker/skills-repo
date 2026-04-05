# LSP and Code Intelligence for Agent Harnesses

Sources: OpenCode documentation; Claude Code changelog (Dec 2025 / Feb 2026); Maik Kingma, "Give Your AI Coding Agent Eyes" (Feb 2026); Davide Consonni, "Using Coding Agents with LSP on Large Codebases" (Medium); Amir Teymoori, "LSP: The Secret Weapon for AI Coding Tools"; LSAP spec (lsp-client/LSAP); oh-my-pi (can1357); oh-my-openagent (code-yeongyu); Kiro CLI code intelligence docs; Aider repo map docs; CodeRLM (JaredStewart); ACP spec (Zed/JetBrains).

## Table of Contents

- [What LSP Actually Is (for Harness Design)](#what-lsp-actually-is-for-harness-design) — symbol graph; timing table; grep vs LSP comparison
- [Full LSP Capability Inventory and Harness Uses](#full-lsp-capability-inventory-and-harness-uses) — all 13 operations
- [What LSP Sensors Enable That Grep Cannot](#what-lsp-sensors-enable-that-grep-cannot)
- [Tools and Integrations That Exist](#tools-and-integrations-that-exist) — Claude Code, OpenCode, oh-my-pi, Kiro
- [Emerging Protocols: Beyond LSP](#emerging-protocols-beyond-lsp) — ACP, LSAP
- [Alternative Code Intelligence: Tree-Sitter and Static Analysis](#alternative-code-intelligence-tree-sitter-and-static-analysis) — Aider repo map, CodeRLM, AFT
- [Limits and Failure Modes](#limits-and-failure-modes) — startup latency, dynamic language gaps, context overhead
- [How Agent Behavior Changes When LSP Is Available](#how-agent-behavior-changes-when-lsp-is-available)
- [Harness Design Implications](#harness-design-implications)

---

## What LSP Actually Is (for Harness Design)

LSP is a JSON-RPC protocol between an editor/agent (client) and a per-language analysis daemon (server). The server maintains a full semantic model of the project: type graph, symbol table, import graph, call graph. When a file changes, the server re-processes it and can answer structured queries against the whole-project model — not just the file in isolation.

For harness engineering, the distinction that matters is **LSP operates on the semantic model; grep and string search operate on text.** That difference propagates into every capability listed below.

**Languages with mature LSP servers** (as of 2026): TypeScript/JavaScript (ts-server), Python (pylsp, pyright), Go (gopls), Rust (rust-analyzer), Java (Eclipse JDT, Metals), C/C++ (clangd), C# (OmniSharp), PHP (Intelephense, phpactor), Kotlin (kotlin-language-server), Ruby (Solargraph, Shopify Ruby LSP), HTML/CSS. Claude Code v2.0.74 (December 2025) shipped native support for all 11 languages via its LSP plugin marketplace.

---

## Full LSP Capability Inventory and Harness Uses

### 1. Diagnostics — Real-Time Error Sensor

**What it is**: after every file save, the language server pushes a `textDocument/publishDiagnostics` notification listing errors, warnings, and hints with precise file/line/column locations and structured error codes.

**Harness use**: the write-time sensor described in [guides-and-sensors.md](guides-and-sensors.md). The agent writes a file; the LSP returns diagnostics before the file is staged; the agent corrects in the same edit cycle. This is qualitatively earlier than pre-commit or CI.

**Agent behavior change**: without LSP, agents must guess whether their edits are type-correct and find out at build time. With LSP diagnostics, agents get structured feedback immediately and iterate before moving to the next file. The net effect is fewer cascading type errors across multi-file changes.

**What to configure**: hook `PostToolUse(Write|Edit)` to trigger a diagnostics query and return results to the agent. OpenCode and Claude Code (v2.0.74+) do this automatically when an LSP server is registered.

---

### 2. goToDefinition — Symbol Resolution

**What it is**: given a cursor position, returns the canonical location where the symbol is defined — across any file, through type aliases and re-exports.

**Harness use**: the agent can navigate to any symbol definition before editing it. When implementing a new method on an interface, the agent first jumps to the interface definition to read the full contract. When debugging a failing type, it jumps to the type definition rather than inferring from usage.

**Agent behavior change**: exploration becomes precise. The agent navigates the project the way a developer in an IDE does — by following semantic connections, not by opening files speculatively and grep-scanning them.

**Performance**: ~50ms via LSP vs. ~45 seconds via recursive text search on a 100-file project. (Source: Claude Code LSP setup guides, 2025.)

---

### 3. findReferences — Impact Analysis Before Refactoring

**What it is**: returns all locations in the project where a symbol is used — definitions, call sites, type annotations, and import statements. Excludes matches in comments and strings.

**Harness use**: before renaming, moving, or deleting any symbol, the agent calls findReferences to get the exact change surface. It knows which files will be affected before touching any of them.

**Why this matters vs. grep**: grep on a function named `process` returns every occurrence of "process" in any string, comment, or variable name. findReferences returns 23 actual call sites. In a 100-file project, grep might return 2000+ tokens of output; LSP returns ~500 tokens of exact matches. The agent uses less context and makes fewer mistakes.

**Agent behavior change**: semantic refactoring (rename, extract, move) becomes reliable at scale. The agent has the complete reference graph before starting; it doesn't discover missed references mid-edit.

---

### 4. Code Actions — Automated Fix Application

**What it is**: given a cursor position or range (often a diagnostic), the server returns a list of available transformations: "Fix import", "Organize imports", "Add missing property", "Extract to method", "Convert to arrow function", "Wrap in try/catch", etc. The agent can request the server to apply any action, getting the edit diff back.

**Code action kinds**:
- `quickfix` — fix a specific diagnostic (most common for agents: "Add missing import", "Fix typo in identifier")
- `refactor` — transformations not tied to a diagnostic
- `source.organizeImports` — sort and deduplicate imports across the file
- `source.fixAll` — apply all safe auto-fixes for the file

**Harness use**: after writing a file and receiving diagnostics, the agent doesn't have to manually compute how to fix each error. It requests code actions for the diagnostic, receives a structured edit diff, and applies it. This is more reliable than asking the model to reason about the fix from the error message alone.

**Agent behavior change**: "Add missing import" stops being a reasoning task and becomes an LSP query with a deterministic result. The agent can cycle through diagnostics → code actions → apply edits without any inference for routine fixes.

**Important caveat**: code actions are only as good as the server's fix quality. Some servers (rust-analyzer, TypeScript) generate reliable fixes; others generate no-op or unsafe actions. Test before relying on them.

---

### 5. Workspace Symbols — Codebase Navigation Without File Knowledge

**What it is**: given a fuzzy string query, returns all matching symbols (functions, classes, interfaces, constants) across the entire project — their name, kind, and location — without knowing which files they live in.

**Harness use**: the agent needs to find `UserRepository` without knowing whether it's in `src/db/users.ts`, `lib/repositories/user.ts`, or somewhere else. workspaceSymbol("UserRepository") returns it directly.

**Agent behavior change**: agents stop wasting context on directory listing and file scanning to locate known symbols. On large codebases, workspaceSymbol is the difference between efficient navigation and spending a third of the context window on exploration.

**Token efficiency**: contrast with the alternative — the agent reads a directory tree, hypothesizes file locations, opens several candidate files. workspaceSymbol reduces this to a single query returning ~50–200 tokens.

---

### 6. documentSymbols — File Structure Map

**What it is**: returns a hierarchical tree of all symbols in a file — classes, methods, properties, nested types — with their ranges.

**Harness use**: before editing a large file, the agent calls documentSymbols to get the structural map. It then identifies the specific method to edit without reading the whole file. This is the intra-file equivalent of workspaceSymbols.

**Agent behavior change**: large files become navigable. The agent doesn't need to read 800 lines to find where `handlePaymentCallback` is; documentSymbols returns the location directly.

---

### 7. Call Hierarchy — Understanding Execution Flow

**What it is**: two operations: `incomingCalls` (who calls this function?) and `outgoingCalls` (what does this function call?). Returns a structured tree, not flat text.

**Harness use**: before modifying a function, the agent checks incomingCalls to understand all its callers and their contexts. Before understanding how a feature is implemented, outgoingCalls reveals the dependency chain. This is architectural reasoning, not just syntax.

**Agent behavior change**: impact analysis becomes structured. The agent can reason about "if I change this function's signature, here are the 7 callers that will need to change" before making the first edit. Without call hierarchy, this requires reading many files speculatively.

---

### 8. Hover — Inline Type and Documentation Lookup

**What it is**: given a cursor position, returns the type signature and documentation for the symbol at that position, exactly as an IDE tooltip would show.

**Harness use**: when writing code that calls an unfamiliar function, the agent queries hover to see the full signature, parameter types, return type, and JSDoc/docstring without opening the definition file.

**Token efficiency**: hover returns 1–3 lines of type information. The alternative — navigating to the definition file, reading it, returning to the current file — costs 10–30x more context.

**Agent behavior change**: agents can write code against APIs they haven't read yet, using hover for on-demand type information rather than front-loading all documentation into context.

---

### 9. Semantic Rename — Cross-Project Refactoring

**What it is**: rename a symbol everywhere in the project — all definitions, all call sites, all type annotations, all import aliases — using the semantic reference graph. Returns a workspace edit covering all files.

**Harness use**: the canonical example — rename a method that's called in 200 files. The agent calls prepareRename (to confirm the symbol is renameable), then rename, and receives a structured diff for all files. No file needs to be opened individually; the edit is applied as a batch.

**Agent behavior change**: multi-file renaming becomes a single operation with guaranteed completeness. String-based rename would miss aliased imports; comment-based matches would produce false positives. Semantic rename is correct by construction.

**oh-my-openagent** exposes this as an explicit `lsp_rename` tool; oh-my-pi exposes `rename` as one of its 11 LSP operations.

---

### 10. goToImplementation — Polymorphism Navigation

**What it is**: from an interface or abstract method, returns all concrete implementations. Different from goToDefinition (which goes to the abstract declaration).

**Harness use**: when the agent needs to understand what code actually runs when an interface method is called, goToImplementation finds all concrete classes. Essential for debugging polymorphic behavior or understanding dispatch.

**Agent behavior change**: interface-heavy codebases (Java, TypeScript with abstract classes) become navigable without reading all files looking for `implements` keywords.

---

### 11. Type Hierarchy — Inheritance Graph

**What it is**: from a class or interface, returns its supertypes and subtypes — the full inheritance tree.

**Harness use**: before adding a method to a base class, the agent queries the type hierarchy to understand all subclasses that might be affected or need to override. For designing a change to a shared interface, type hierarchy reveals the full blast radius across the class hierarchy.

**Agent behavior change**: object-oriented refactoring becomes semantically grounded. The agent doesn't have to search for subclasses manually.

---

### 12. Inlay Hints — Implicit Type Visibility

**What it is**: server-computed annotations that reveal implicit information: inferred return types, implicit parameter names at call sites, inferred variable types. Added in LSP 3.17.

**Harness use**: the agent can query inlay hints for a region of code before editing it, to see what the type system is inferring without explicit annotations. This is useful when modifying code that uses heavy type inference (Rust, TypeScript with `infer`, Haskell) — the agent sees the full type picture without needing to trace inference manually.

**Agent behavior change**: implicit code becomes explicit before the agent touches it. The agent sees what the type checker sees.

---

### 13. Code Lens — Compute-on-Demand Context

**What it is**: decorations that appear above symbols with on-demand information — "12 references", "Run test", "Coverage: 87%". The agent can query these programmatically.

**Harness use**: reference counts visible in-context allow the agent to assess symbol usage before deciding whether to modify or delete something. Test run triggers allow the agent to run a specific test directly from the code context without constructing a CLI command.

---

### 14. Document Links — External Reference Resolution

**What it is**: returns all links in a document — URLs, paths, references to external resources. The agent can extract all external dependencies referenced in comments and documentation strings.

**Harness use**: less common, but useful for documentation validation agents that need to check whether referenced links are still alive.

---

## What LSP Sensors Enable That Grep Cannot

| Task | With grep | With LSP |
|---|---|---|
| Find all call sites of `processPayment` | 500+ tokens, includes comments and strings | 23 precise results, ~200 tokens |
| Rename `userId` across 200 files | String replace — misses aliased imports | Semantic rename — guaranteed complete |
| Find all implementations of `IPaymentGateway` | Search for "implements IPaymentGateway" — misses indirect inheritance | goToImplementation — full hierarchy |
| Check type of variable before using it | Open definition file, read it | hover — 1 line, ~20 tokens |
| Understand what calls `validate()` | Grep, filter manually | incomingCalls — structured tree |
| Navigate to `UserRepository` definition | ls + grep file tree | workspaceSymbol("UserRepository") — direct |

---

## Tools and Integrations That Exist

### Claude Code (native, v2.0.74+, December 2025)

Anthropic shipped native LSP support in Claude Code v2.0.74. Supported languages: TypeScript, Python, Go, Rust, Java, C/C++, C#, PHP, Kotlin, Ruby, HTML/CSS (11 languages).

Core operations exposed: `goToDefinition`, `findReferences`, `documentSymbol`, `hover`, `getDiagnostics`.

Diagnostics run automatically after every file edit. The LSP plugin marketplace (both official and community) handles server registration; Claude Code manages server lifecycle.

Known issues (February 2026 changelog): LSP diagnostic data memory leaks causing unbounded memory growth in long sessions (patched); LSP plugins not registering when LSP Manager initialized before marketplace reconciliation (patched).

Setup: install via plugin marketplace or register a binary server manually. Community repo: `Piebald-AI/claude-code-lsps`.

### OpenCode (experimental flag: `OPENCODE_EXPERIMENTAL_LSP_TOOL=true`)

Open-source terminal coding agent. LSP tool is opt-in via environment variable. When enabled, exposes these operations as explicit agent tools: `goToDefinition`, `findReferences`, `hover`, `documentSymbol`, `workspaceSymbol`, `goToImplementation`, `prepareCallHierarchy`, `incomingCalls`, `outgoingCalls`.

Supports 20+ LSP servers. The agent can call any of these as a first-class tool call, not just as a side effect of file saves.

Also supports Agent Client Protocol (ACP), discussed below.

### oh-my-openagent (code-yeongyu, "omo")

A harness wrapper around OpenCode that adds: 11 specialized agents, Sisyphus orchestration, and explicit LSP tool exposure. LSP tools: `lsp_rename`, `lsp_goto_definition`, `lsp_find_references`, `lsp_diagnostics`. Also bundles AST-grep for structural code rewriting.

### oh-my-pi (can1357)

Terminal coding agent with the most complete LSP tool surface of any agent harness found. Exposes 11 LSP operations as discrete tools: `diagnostics`, `definition`, `type_definition`, `implementation`, `references`, `hover`, `symbols`, `rename`, `code_actions`, `status`, `reload`. Notable: includes `code_actions` and `reload` — uncommon in other harnesses.

Also features hash-anchored edits (Hashline) as a separate mechanism: every line gets a content hash; the model references hashes instead of reproducing text — eliminates stale-line edit failures. Benchmarked: Grok 4 Fast achieved 61% fewer output tokens with hash-anchored edits vs. str_replace.

### Kiro CLI (Amazon, 2025–2026)

Kiro CLI added code intelligence in January 2026 changelog. Two modes:
- Built-in: 18 languages with no setup required — symbol search, definition navigation, structural code search available immediately.
- LSP mode: `/code init` unlocks full LSP with go-to-definition, find references, hover, rename refactoring.

The built-in mode is architecturally interesting: it's a lighter-weight code intelligence system that doesn't require running a language server process, appropriate for ephemeral or CI environments where LSP startup overhead is prohibitive.

### GitHub Copilot CLI

As of 2025, also supports registering external LSP servers as context providers. LSP acts as a "structured signal provider" alongside other context sources.

### LSP-AI (SilasMarvin, open source, Rust)

Inverts the architecture: instead of an AI agent using an LSP server, LSP-AI is a language server whose backend is an LLM. Any editor that supports LSP gets AI completions and in-editor chat via this server. Supports llama.cpp, Ollama, OpenAI/Anthropic/Gemini APIs as backends. Works in VS Code, Neovim, Emacs, Helix, Sublime.

Harness relevance: demonstrates the inverted pattern — LLM accessed via LSP interface rather than LSP accessed via LLM tooling.

---

## Emerging Protocols: Beyond LSP

### Agent Client Protocol (ACP) — "LSP for AI Agents"

Created by Zed and JetBrains (August 2025), open standard under Apache License. Where LSP standardizes editor↔language-server communication, ACP standardizes editor↔agent communication. The analogy: LSP enables any editor to support any language; ACP enables any editor to use any AI agent.

Flagship implementations: Zed (native), JetBrains IDEs (2025.3+, full lineup planned), OpenCode. Google's Gemini CLI was an early ACP example. ACP Agent Registry launched January 2026.

**Harness significance**: ACP is not just an integration convenience. It means the agent has a standardized way to receive context from the IDE (open files, cursor position, selection, diagnostics, project state) and send back structured edits. The IDE's LSP layer feeds into the ACP context the agent receives. LSP and ACP compose: LSP provides code intelligence; ACP provides the channel between agent and editor.

### LSAP — Language Server Agent Protocol

A proposed open protocol (lsp-client/LSAP GitHub org) that sits above LSP. The problem it addresses: LSP operations are atomic and designed for interactive editor use. An agent wanting to "find all references and extract their surrounding context" must chain a dozen LSP calls sequentially. LSAP composes these into higher-level agent-native operations.

Core concept: LSAP provides "cognitive capabilities" vs. LSP's "atomic operations." Example: where LSP requires open file → calculate offset → request definition → parse URI → read file → extract snippet, LSAP's "get definition with context" returns all of this in a single request.

Advanced capability: `Relation API` — finds call paths between two functions. One LSAP query; would require many LSP queries and manual graph traversal otherwise.

The lsp-client org also maintains `lsp-skill` (a Claude Code skill wrapping LSAP) and `lsp-cli` (a CLI interface to LSAP servers).

**Status**: experimental, not widely adopted. The concept is sound; the ecosystem is nascent.

---

## Alternative Code Intelligence: Tree-Sitter and Static Analysis

LSP requires a running server process with full project indexing. For contexts where that's impractical (cold-start CI, ephemeral worktrees, multi-repo agents), alternative code intelligence tools exist.

### Aider's Repository Map (tree-sitter + PageRank)

Aider pioneered this pattern (2023, still widely referenced 2025–2026):
1. Tree-sitter parses all source files into ASTs, extracting function/class definitions and call sites
2. A directed graph of definitions and references is built across the whole project
3. PageRank ranks symbols by how heavily they're referenced
4. Top-ranked symbols are rendered as scope-aware elided code views (signature + key structure, not full body) fitted to a token budget

The agent receives a repository map that covers the most structurally important parts of the codebase — enough to understand the architecture without reading every file.

**Harness use**: for large codebases, pre-load the repo map into agent context at session start. The map tells the agent what's important to read without having to explore speculatively. Supports 130+ languages via tree-sitter parsers.

**RepoMapper** is a standalone port of this pattern as an MCP server (`pdavis68/RepoMapper`).

### CodeRLM (tree-sitter indexing server, February 2026)

A Rust server that indexes a project via tree-sitter and exposes a JSON API. The agent queries for: symbols (by name or fuzzy), implementations, callers, test files for a given module, and grep. Languages with tree-sitter grammars get full symbol tables; other file types get grep-based fallbacks.

Key design principle: the agent gets exactly what it needs on demand, not a bulk file dump. A query for "all callers of processPayment" returns structured results; the agent doesn't need to parse grep output.

Has an integrated Claude Code skill (`lsp-skill`-style wrapper with a Python CLI).

**When to use over LSP**: no running server process required; low startup overhead; works in CI and ephemeral environments. Trade-off: lower fidelity than a full LSP server (tree-sitter is syntactic, not semantic — it doesn't know types, only structure).

### AFT (ualtinok, tree-sitter powered)

Provides: semantic editing (structural code rewriting), call-graph navigation, structural search. Designed specifically for AI coding agents. Tree-sitter-backed, so language-agnostic within the grammar ecosystem.

### ast-grep

Structural search and rewrite tool using tree-sitter grammars. Works at the AST level rather than text level — patterns match syntax structure, not characters. Used by oh-my-openagent alongside LSP.

**Harness use**: agent-readable lints that are structurally defined (not regex). Can replace entire classes of LSP code actions in simple cases.

---

## Limits and Failure Modes

### 1. Startup Latency and Cold-Start Cost

LSP servers require indexing the whole project before they can answer queries. For TypeScript on a large monorepo, initial startup can take 30–120 seconds; first hover/diagnostic responses may take additional seconds after startup.

**Failure mode**: in ephemeral worktrees or short-lived agent sessions, the server may not finish indexing before the agent writes code. Diagnostic feedback arrives late or not at all.

**Mitigation**: use Kiro's built-in code intelligence (no LSP process required) or tree-sitter-based indexing for ephemeral contexts. Reserve full LSP for persistent dev environments.

### 2. Performance Degradation on Large Codebases

LSP servers consume significant CPU and memory proportional to codebase size. TypeScript language server on large monorepos is known to hit 100% CPU during indexing and consume several GB of memory. Multiple concurrent worktrees each running their own LSP server multiplies this.

**Failure mode**: on a machine running 4–6 concurrent agent worktrees, 4–6 language server instances may saturate CPU/memory, degrading all agents simultaneously.

**Mitigation**: monitor server memory; configure restart policies; consider shared indexing (some servers support multi-root workspaces); use tree-sitter-based tools for concurrent environments.

### 3. File-Scope Architecture Limitation

LSP operations are largely scoped to individual files or explicit cross-file queries. The server doesn't surface implicit architectural patterns: coupling metrics, module dependency health, circular import detection, "this module is doing too much."

**Failure mode**: an agent with only LSP cannot reason about architectural health. It can find where things are; it cannot assess whether the architecture is sound.

**Mitigation**: supplement with Dependency Cruiser (JS/TS), ArchUnit (Java), import graph analysis tools. These belong in the Architecture Fitness Harness (see [guides-and-sensors.md](guides-and-sensors.md)).

### 4. Dynamic Languages and Runtime Behavior

For Python (and other dynamically typed languages), LSP quality depends heavily on type annotation coverage. An un-annotated Python function has an effectively opaque type from the LSP's perspective. `findReferences` still works (syntactic), but type checking and signature validation do not.

**Failure mode**: LSP diagnostics on lightly-typed Python report far fewer errors than the code actually has. The agent gets false confidence that the code is correct.

**Mitigation**: invest in mypy/pyright type annotation coverage before relying on LSP as a sensor. The sensor is only as good as the type coverage it can observe. (Documented in [guides-and-sensors.md](guides-and-sensors.md) as the primary LSP caveat.)

### 5. Generated, Monkeypatched, and Macro-Heavy Code

LSP cannot navigate through: code generated at runtime (Python's `__getattr__`, JavaScript Proxy), macro expansions (Rust proc macros, C preprocessor macros), and code where symbols are defined by string concatenation or dynamic `require()`. The server sees text; it cannot see what the runtime will do.

**Failure mode**: goToDefinition returns "no definition found" for dynamically-injected methods. findReferences misses usages that go through a Proxy. The agent thinks a symbol is unused and deletes it.

**Mitigation**: document these patterns explicitly in CLAUDE.md as regions where LSP output is unreliable. Treat "no references found" as a warning, not a conclusion, in dynamically-typed regions.

### 6. Context Window Overhead for LSP Tool Output

The comprehensive tool inventory including LSP operations consumes approximately 25.5K tokens (12.7% of context) before any retrieval operations begin. This is a fixed overhead in LSP-enabled agent sessions.

**Failure mode**: on agents with constrained context (smaller models, very long sessions), the LSP tool definitions themselves consume context that could otherwise hold code.

**Mitigation**: use skill `allowed-tools` to restrict the LSP tool surface per task. A code reading task doesn't need `rename`; an execution task doesn't need `incomingCalls`.

### 7. Server Crashes and Stale State

Long sessions with many file edits can cause LSP servers to accumulate stale state or crash silently. The agent continues to receive outdated diagnostics or no diagnostics after a crash.

**Failure mode**: the agent believes code is type-correct because diagnostics stopped reporting errors — but diagnostics stopped because the server crashed.

**Mitigation**: monitor server status (oh-my-pi exposes an explicit `status` and `reload` tool for this). Configure session hooks to verify the server is responsive after large refactors. Build in periodic server restarts for long-running sessions.

---

## How Agent Behavior Changes When LSP Is Available

These are the specific behavioral shifts observed in LSP-enabled agents (sources: Maik Kingma 2026, Davide Consonni, Amir Teymoori, Claude Code setup guides):

**Before making changes**: the agent queries for all references to a symbol before touching it, rather than proceeding and discovering breakages later.

**During writing**: the agent checks diagnostics after each file save, fixing type errors and missing imports before moving to the next file. Code reaches the build step clean.

**During navigation**: the agent follows semantic paths (definition, implementation, call hierarchy) rather than searching for strings and reading candidate files speculatively.

**During refactoring**: the agent uses semantic rename rather than search-and-replace, and verifies completeness via findReferences before declaring a rename done.

**On encountering unfamiliar APIs**: the agent queries hover for type signatures rather than opening documentation or definition files.

**On context budget pressure**: the agent uses workspaceSymbol and documentSymbol to navigate directly to needed code, rather than consuming context on exploration.

The net effect: LSP-enabled agents make fewer cascading errors across multi-file changes, use less context on navigation, and perform semantic refactoring correctly the first time.

---

## Harness Design Implications

**LSP as a write-time sensor** (covered in depth in [guides-and-sensors.md](guides-and-sensors.md)): the timing advantage — diagnostics at file save, before staging — is the primary harness value. Combine with pre-commit hooks for a two-tier sensor: write-time (LSP) catches type errors; pre-commit (linters, formatters) catches style and structure.

**LSP as a navigation layer**: in large codebases, the agent's exploration cost drops significantly with LSP. This reduces context pressure and allows the agent to operate on larger projects without hitting the 15-file modification degradation threshold. See [guides-and-sensors.md](guides-and-sensors.md) → "Session Scope as a Sensor Boundary."

**Type coverage precondition**: LSP sensor quality is directly proportional to type annotation coverage. Invest in end-to-end types (see [type-system-design.md](type-system-design.md)) before relying on LSP diagnostics as a quality gate. A weakly-typed codebase gives LSP little to work with.

**Tree-sitter as LSP fallback**: for ephemeral worktrees, CI, or concurrent agent environments where running one LSP server per worktree is impractical, tree-sitter-based indexing (Aider repo map, CodeRLM) provides 70–80% of the navigation benefit with near-zero startup overhead. Design the harness to use full LSP for persistent dev sessions and tree-sitter for ephemeral contexts.

**LSAP for agent-optimized composition**: if agents are spending tokens on multi-step LSP query chains (open file → calculate offset → request definition → extract context), LSAP-style composition reduces this to single requests. Currently experimental; worth watching.

**ACP as the emerging standard channel**: ACP (Zed/JetBrains) is becoming the standard protocol for agent↔IDE communication. As ACP adoption grows, LSP becomes part of the context the IDE supplies to the agent via ACP, rather than something the agent queries directly. The two compose rather than compete.
