# Command / Skill Frontmatter Reference

All fields are optional except `description` (strongly recommended).

## Fields

### `name`
- **Type**: string
- **Default**: directory name (for skills) or filename without `.md` (for commands)
- **Constraints**: lowercase letters, numbers, hyphens only; max 64 chars
- **Purpose**: The `/slash-command` name users type

### `description`
- **Type**: string (supports multi-line YAML `>` block)
- **Recommended**: yes — this is the primary signal Claude uses to auto-load the skill
- **Purpose**: What the skill does AND when to use it. Include specific triggers, file types, user phrases that should activate it. This field is always in context; the body is only loaded after triggering.

### `argument-hint`
- **Type**: string
- **Purpose**: Shown during `/` autocomplete to hint at expected arguments
- **Examples**: `[issue-number]`, `[filename] [format]`, `[colors|inputs|buttons|all]`

### `allowed-tools`
- **Type**: string (space- or comma-separated tool names)
- **Purpose**: Tools the command can use without prompting the user for permission
- **Examples**: `Read, Grep, Glob`, `Bash, Read, Glob, Grep`, `Agent`
- **Note**: Also seen in project commands as `tools:` (array format) — `allowed-tools` is the canonical field

### `disable-model-invocation`
- **Type**: boolean
- **Default**: false
- **Purpose**: When `true`, Claude never auto-loads this skill; description is removed from context. User must type `/name` explicitly.
- **Use for**: Commands with side effects — deploys, commits, pushes, deletions, any destructive action

### `user-invocable`
- **Type**: boolean
- **Default**: true
- **Purpose**: When `false`, hides from the `/` slash menu. Claude can still auto-trigger it, but users can't invoke it directly.
- **Use for**: Background knowledge skills, internal helpers Claude uses but users don't

### `model`
- **Type**: string
- **Purpose**: Override which Claude model handles this command
- **Example**: `claude-opus-4-6`

### `context`
- **Type**: string (`"fork"`)
- **Purpose**: When `"fork"`, the command runs in an isolated subagent with no conversation history. Result is summarized back to main conversation.
- **Use for**: Long research tasks, parallel agent dispatch, analysis that shouldn't pollute main context

### `agent`
- **Type**: string
- **Purpose**: Subagent type when `context: fork`. Options: `Explore`, `Plan`, `general-purpose`, or a custom agent name from `.claude/agents/`
- **Only used with**: `context: fork`

### `hooks`
- **Type**: object
- **Purpose**: Lifecycle hooks scoped to this skill. See hooks documentation for format.

---

## `handoffs` (ResultKit extension)

Used in speckit commands and other multi-step workflows. Provides clickable "next step" buttons after a command completes.

```yaml
handoffs:
  - label: Button label shown to user
    agent: target.command
    prompt: Pre-filled message sent to the next command
    send: true   # optional: auto-send without user confirmation
```

| Field | Required | Purpose |
|---|---|---|
| `label` | yes | Text on the button |
| `agent` | yes | Command/skill to invoke (use `.` for nested, e.g. `speckit.plan`) |
| `prompt` | yes | Pre-filled prompt passed to the next command |
| `send` | no | If `true`, auto-sends the handoff without waiting for user confirmation |

**Example** (from speckit/specify.md):
```yaml
handoffs:
  - label: Build Technical Plan
    agent: speckit.plan
    prompt: Create a plan for the spec. I am building with...
  - label: Clarify Spec Requirements
    agent: speckit.clarify
    prompt: Clarify specification requirements
    send: true
```

---

## Invocation Behavior Matrix

| Frontmatter | User can invoke | Claude auto-triggers | Description in context |
|---|---|---|---|
| (default) | Yes | Yes | Always |
| `disable-model-invocation: true` | Yes | No | Never |
| `user-invocable: false` | No | Yes | Always |
