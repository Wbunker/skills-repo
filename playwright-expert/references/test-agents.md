# Test Agents (planner · generator · healer)

Playwright ships three AI **Test Agents** (v1.56+) that automate writing and maintaining tests via an
LLM tool like **Claude Code**, VS Code, Codex, or OpenCode. They are agent definitions ("collections
of instructions and MCP tools") you generate into your repo, then drive in natural language.

> Distinct from [agent-cli.md](agent-cli.md) (`playwright-cli`, a shell tool that drives a browser
> one command at a time). Test Agents *author `*.spec.ts` files*; agent-cli *operates a live browser*.

## Contents
- [The three agents](#the-three-agents)
- [Setup: init-agents](#setup-init-agents)
- [Repo structure & artifacts](#repo-structure--artifacts)
- [The seed test](#the-seed-test)
- [Specs (Markdown plans)](#specs-markdown-plans)
- [Generated tests](#generated-tests)
- [End-to-end workflow](#end-to-end-workflow)
- [Notes & caveats](#notes--caveats)

## The three agents

| Agent | Input | Does | Output |
|-------|-------|------|--------|
| 🎭 **planner** | a request + the [seed test](#the-seed-test), optional PRD | Explores the app, writes a human-readable test plan | Markdown plan in `specs/` |
| 🎭 **generator** | a Markdown plan from `specs/` | Converts the plan into real tests, verifying selectors/assertions live as it goes | `*.spec.ts` files under `tests/` |
| 🎭 **healer** | a failing test name | Replays failing steps, inspects the live UI, patches locators/waits/data, re-runs until green or a guardrail stops it | a passing test (or a skipped one if the feature is genuinely broken) |

They can run individually or be chained in an agentic loop (plan → generate → heal).

## Setup: init-agents

Generate the agent definitions for your tool of choice (regenerate after upgrading Playwright so the
agents pick up new tools/instructions):

```bash
npx playwright init-agents --loop=claude     # Claude Code
npx playwright init-agents --loop=vscode      # VS Code (needs v1.105+, Oct 2025)
npx playwright init-agents --loop=codex
npx playwright init-agents --loop=opencode
```

The agents rely on Playwright's MCP tools to drive the browser while planning/generating/healing —
the `init-agents` command wires up the definitions and MCP configuration for the chosen loop. Inspect
the files it writes in your repo to see the exact layout for your tool/version (it differs per loop),
then invoke each agent **by name** in natural language from your AI tool (e.g. ask the planner to
"Generate a plan for guest checkout").

## Repo structure & artifacts

```
repo/
  .github/                    # (VS Code/Copilot loop) agent definitions — path varies per --loop
  specs/                      # human-readable test plans (planner output)
    basic-operations.md
  tests/
    seed.spec.ts              # seed test establishing the environment
    create/add-valid-todo.spec.ts   # generated tests
  playwright.config.ts
```

## The seed test

A small test that boots the environment — the planner runs it so all global setup, project
dependencies, fixtures, and hooks execute before it explores; the generator uses it as the template
(imports, fixtures) for the tests it writes.

```javascript
import { test, expect } from './fixtures';

test('seed', async ({ page }) => {
  // uses custom fixtures from ./fixtures — see fixtures.md
});
```

Point the seed at your custom [fixtures](fixtures.md) and signed-in [auth](auth.md) state so every
generated test inherits them.

## Specs (Markdown plans)

The planner emits structured, reviewable Markdown — edit it before generating to steer coverage:

```markdown
# TodoMVC Application - Basic Operations Test Plan

## Application Overview
[Description of features and capabilities]

## Test Scenarios

### 1. Adding New Todos
**Seed:** `tests/seed.spec.ts`

#### 1.1 Add Valid Todo
**Steps:**
1. Click in the "What needs to be done?" input field
2. Type "Buy groceries"
3. Press Enter key

**Expected Results:**
- Todo appears in the list with unchecked checkbox
- Counter shows "1 item left"
- Input field is cleared and ready for next entry
```

## Generated tests

The generator turns each scenario into a test, citing its spec + seed in a header comment, and uses
the same resilient locators/assertions covered in [locators.md](locators.md) and
[assertions.md](assertions.md):

```javascript
// spec: specs/basic-operations.md
// seed: tests/seed.spec.ts
import { test, expect } from '../fixtures';

test.describe('Adding New Todos', () => {
  test('Add Valid Todo', async ({ page }) => {
    const todoInput = page.getByRole('textbox', { name: 'What needs to be done?' });
    await todoInput.click();
    await todoInput.fill('Buy groceries');
    await todoInput.press('Enter');

    await expect(page.getByText('Buy groceries')).toBeVisible();
    const todoCheckbox = page.getByRole('checkbox', { name: 'Toggle Todo' });
    await expect(todoCheckbox).not.toBeChecked();
    await expect(page.getByText('1 item left')).toBeVisible();
  });
});
```

## End-to-end workflow

1. **Init** — `npx playwright init-agents --loop=claude`.
2. **Seed** — write `tests/seed.spec.ts` wiring up fixtures/auth/global setup.
3. **Plan** — ask the planner for a plan (e.g. "Generate a plan for guest checkout"); review/edit the
   Markdown in `specs/`.
4. **Generate** — ask the generator to turn a spec into tests under `tests/`.
5. **Heal** — when a test fails, ask the healer to repair it; it replays, inspects the live UI, and
   patches until the test passes (or skips a genuinely broken feature).

## Notes & caveats

- Generated tests can contain mistakes by design — the healer (or you) closes the loop. Always review
  generated specs and tests; treat them as drafts, not ground truth.
- The exact generated file paths, invocation syntax, and MCP wiring depend on the `--loop` target and
  Playwright/tool version — inspect what `init-agents` writes rather than assuming a fixed layout.
- Re-run `init-agents` after each Playwright upgrade to refresh the agents' tools and instructions.
- This is an authoring aid; the resulting tests still run through the normal
  [test runner](tooling.md) and [config](test-config.md).
