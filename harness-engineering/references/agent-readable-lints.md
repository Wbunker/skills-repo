# Agent-Readable Lint Rules

Source: OpenAI harness engineering (Feb 2026)

## Table of Contents

- [The Mechanism](#the-mechanism) — lint error = remediation instruction
- [What Makes a Message Agent-Readable](#what-makes-a-message-agent-readable)
- [ESLint (JavaScript / TypeScript)](#eslint-javascript--typescript)
- [Semgrep (Language-Agnostic)](#semgrep-language-agnostic)
- [Ruff (Python)](#ruff-python)
- [golangci-lint (Go)](#golangci-lint-go)
- [Naming Convention Lints](#naming-convention-lints)
- [File Size Limits](#file-size-limits)
- [Pre-Commit Hook Integration](#pre-commit-hook-integration)
- [Auto-Apply Linters and Formatters](#auto-apply-linters-and-formatters)
- [CLAUDE.md Pointer](#claudemd-pointer)
- [Generating Lints with the Agent](#generating-lints-with-the-agent)
- [The Ratchet: Review Comment → Lint](#the-ratchet-review-comment--lint)

---

Custom lint rules with remediation instructions in the error message string. The agent reads lint output from tool results and applies the fix — no human explanation, no additional investigation required.

## The Mechanism

```
Agent writes code
    ↓
Pre-commit hook fires linter
    ↓
Lint error appears in tool output
    ↓
Message contains: bad pattern + corrected pattern + example
    ↓
Agent applies fix, re-stages, re-commits
```

The lint message is not written for a human reading a terminal. It is written for an agent reading a tool result. That shift in audience changes how you write the message.

## What Makes a Message Agent-Readable

| Element | Why it matters |
|---|---|
| Bad pattern explicitly stated | Agent can grep for similar violations elsewhere |
| Corrected pattern shown | No inference required |
| Concrete example with real variable names | Reduces ambiguity, shows intent |
| One message = one fix | Compound rules require judgment the agent may not have |
| Reason included (optional) | Helps agent avoid re-introducing the same violation later |

**Write this:**
```
Unstructured log call.
Replace: logger.info("string")
With:    logger.info({ event: "describe_what_happened", ...context })
Example: logger.info({ event: "user_created", userId, email })
```

**Not this:**
```
Use structured logging per our conventions.
```

The second message requires the agent to look up what "our conventions" means. The first message contains the fix.

## ESLint (JavaScript / TypeScript)

```javascript
// eslint-rules/structured-logging.js
module.exports = {
  meta: {
    type: 'suggestion',
    messages: {
      useStructuredLogging:
        'Unstructured log call. ' +
        'Replace: logger.{{method}}("string") ' +
        'With:    logger.{{method}}({ event: "describe_what_happened", ...context }) ' +
        'Example: logger.info({ event: "user_created", userId, email })'
    }
  },
  create(context) {
    return {
      CallExpression(node) {
        if (isLoggerCall(node) && firstArgIsString(node)) {
          context.report({
            node,
            messageId: 'useStructuredLogging',
            data: { method: node.callee.property.name }
          });
        }
      }
    };
  }
};
```

Register in `.eslintrc`:
```json
{
  "plugins": ["./eslint-rules"],
  "rules": {
    "local/structured-logging": "error"
  }
}
```

Agent sees in tool output:
```
src/services/user.ts:42:5  error  Unstructured log call.
  Replace: logger.info("string")
  With:    logger.info({ event: "describe_what_happened", ...context })
  Example: logger.info({ event: "user_created", userId, email })
  local/structured-logging
```

## Semgrep (Language-Agnostic)

Semgrep is well-suited for agent-readable rules: rules are YAML, messages are multi-line, and the agent that generates the code can also generate the rules.

```yaml
# rules/structured-logging.yml
rules:
  - id: structured-logging-required
    pattern: logger.$METHOD("...")
    message: |
      Unstructured log call detected.
      Replace: logger.$METHOD("string message")
      With:    logger.$METHOD({ event: "...", ...context })
      Example: logger.info({ event: "user_created", userId, email })
      Reason: Unstructured strings break log aggregation and OpenTelemetry tracing.
    severity: ERROR
    languages: [typescript, javascript]

  - id: schema-naming-convention
    pattern: |
      const $NAME = z.object({...})
    message: |
      Schema name must end with 'Schema'. Found: $NAME
      Rename to: $NAMESchema
      Example: const UserSchema = z.object({...})
    severity: ERROR
    languages: [typescript]
    paths:
      include: ["src/schemas/**"]
```

Run: `semgrep --config rules/ src/`

Semgrep's pattern language handles most naming and structural checks without writing JavaScript. Write rule + message in YAML; the agent can iterate on both without touching a build system.

## Ruff (Python)

For custom rules beyond Ruff's built-ins, use a plugin:

```python
# ruff_plugins/structured_logging.py
from ruff.ast import Visitor, Call, Attribute
from ruff.diagnostics import Diagnostic, DiagnosticKind

class StructuredLoggingRule(Visitor):
    name = "structured-logging-required"
    message = (
        "Unstructured log call. "
        "Replace: logger.info('string') "
        "With:    logger.info('event_name', extra={'key': value}) "
        "Example: logger.info('user_created', extra={'user_id': user_id})"
    )

    def visit_Call(self, node: Call):
        if is_logger_call(node) and has_string_arg(node):
            yield Diagnostic(node, self.message)
```

For simpler checks (naming, imports, patterns), Ruff's built-in rule configuration with `[tool.ruff.lint]` in `pyproject.toml` is sufficient. Custom messages appear in `ruff check` output read by the agent.

## golangci-lint (Go)

Write a custom analyzer using `golang.org/x/tools/go/analysis`:

```go
// analyzers/structuredlogging/analyzer.go
var Analyzer = &analysis.Analyzer{
    Name: "structuredlogging",
    Doc:  "Requires structured log calls",
    Run:  run,
}

func run(pass *analysis.Pass) (interface{}, error) {
    // inspect AST for log.Printf / log.Println calls
    inspect := pass.ResultOf[inspector.Analyzer].(*inspector.Inspector)
    inspect.Preorder(nodeFilter, func(n ast.Node) {
        call := n.(*ast.CallExpr)
        if isUnstructuredLogCall(call) {
            pass.Reportf(call.Pos(),
                "unstructured log call. "+
                "Replace: log.Printf(\"message\") "+
                "With:    slog.Info(\"event_name\", \"key\", value) "+
                "Example: slog.Info(\"user_created\", \"user_id\", userID)")
        }
    })
    return nil, nil
}
```

Register in `.golangci.yml`:
```yaml
linters-settings:
  custom:
    structuredlogging:
      path: ./analyzers/structuredlogging
      description: Enforce structured logging
      original-url: internal
```

## Naming Convention Lints

Naming conventions are among the highest-value taste invariants to encode — agents apply consistent naming within a session but drift across sessions without enforcement.

**ESLint example — schema naming:**
```javascript
// Enforce: all Zod schemas must be named *Schema
create(context) {
  return {
    VariableDeclarator(node) {
      if (isZodSchema(node.init) && !node.id.name.endsWith('Schema')) {
        context.report({
          node: node.id,
          message:
            `Schema variable must end with 'Schema'. ` +
            `Rename '${node.id.name}' to '${node.id.name}Schema'. ` +
            `Example: const UserSchema = z.object({...})`
        });
      }
    }
  };
}
```

**Semgrep example — type naming:**
```yaml
- id: type-naming-convention
  pattern: type $NAME = {...}
  message: |
    Type alias name must end with 'Type'. Found: $NAME
    Rename to: $NAMEType
    Example: type UserType = { id: string; email: string }
  severity: WARNING
  languages: [typescript]
```

## File Size Limits

The filesystem is an agent's primary navigation interface. Agents summarize or truncate large files when loading them — a file short enough to be loaded in full stays entirely active in context, eliminating a class of degraded performance where the agent makes decisions based on incomplete information.

File size limits are the mechanical enforcement of this principle. See [context-engineering.md](context-engineering.md) → "The Filesystem as Navigation Interface" for the full rationale including directory naming and namespace conventions.

```javascript
// eslint-rules/file-size-limit.js
module.exports = {
  create(context) {
    return {
      Program(node) {
        const lines = context.getSourceCode().lines.length;
        if (lines > 300) {
          context.report({
            node,
            message:
              `File exceeds 300 lines (${lines} lines). ` +
              `Split into smaller modules. ` +
              `Guidance: extract related functions into a new file, ` +
              `move types to a dedicated types file, ` +
              `or split by feature area. ` +
              `See architecture doc: docs/architecture.md#module-boundaries`
          });
        }
      }
    };
  }
};
```

Note the pointer to the architecture doc — the agent can follow it if the message alone is insufficient.

## Pre-Commit Hook Integration

Lints running at pre-commit fire while the agent is still in the session. The agent sees the failure in tool output, applies the fix, re-stages, and re-commits — without human intervention.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: eslint-custom
        name: Custom lint rules
        entry: npx eslint --rule-dir ./eslint-rules
        language: node
        types: [javascript, typescript]
        pass_filenames: true

      - id: semgrep-taste
        name: Taste invariants
        entry: semgrep --config ./rules/ --error
        language: python
        types: [javascript, typescript]
        pass_filenames: false
```

## Auto-Apply Linters and Formatters

> "Make those as strict as possible and configured to automatically apply fixes whenever the LLM finishes a task or is about to commit." — OpenAI

Linters that only report violations require the agent to run a separate fix step. Linters configured to auto-apply fixes eliminate that step entirely.

**Configure auto-fix in pre-commit hooks:**
```yaml
- id: eslint-autofix
  name: ESLint auto-fix
  entry: npx eslint --fix
  language: node
  types: [javascript, typescript]

- id: prettier
  name: Prettier format
  entry: npx prettier --write
  language: node
  types: [javascript, typescript, json, markdown]
```

**TypeScript type checking** cannot auto-fix, but should still run as a gate:
```yaml
- id: typecheck
  name: TypeScript type check
  entry: npx tsc --noEmit
  language: node
  pass_filenames: false
```

The loop: agent writes code → pre-commit fires → formatters apply fixes automatically → type checker and linters run → any remaining errors surface as actionable messages. The agent sees only what needs human decision, not mechanical formatting issues.

See [type-system-design.md](type-system-design.md) for the full end-to-end types strategy that these lints enforce.

## CLAUDE.md Pointer

Add one line so the agent knows lint output is actionable:

```markdown
When pre-commit lint fails, read the error message — it contains the exact fix to apply.
Do not suppress or bypass lints. Each lint message is a remediation instruction.
```

## Generating Lints with the Agent

OpenAI noted that their custom lints were themselves generated by Codex. The workflow:

1. Identify a pattern you want to enforce (from a review comment, a recurring bug, a taste preference)
2. Describe the rule to the agent: "Write an ESLint rule that enforces X. The error message should tell the agent exactly how to fix it, with an example."
3. The agent writes the rule and the message
4. Review the message for clarity — would an agent reading it know exactly what to do?
5. Add to pre-commit and CI

This is the "promote rule into code" ratchet: review comment → description → generated lint → enforced everywhere.

## The Ratchet: Review Comment → Lint

| Stage | Mechanism | Durability |
|---|---|---|
| Review comment | Human observation | Forgotten after the PR |
| `CLAUDE.md` rule | Text in context | Degrades as context fills |
| Custom lint | Mechanically enforced | Permanent; applies everywhere at once |

When a `CLAUDE.md` rule keeps getting violated, that's the signal to promote it to a lint. Once encoded as a lint, the rule enforces itself at zero ongoing cost.
