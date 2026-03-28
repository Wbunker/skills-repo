# Skills Repo

A collection of expert skills for Claude Code. Each skill is an unpacked directory containing a `SKILL.md` (always loaded) and `references/` files (loaded on demand via progressive disclosure).

## Adding This Repo to Your Project

Add the following to your project's `CLAUDE.md` to have Claude automatically pull skills at the start of a session:

```
I have a skills repo at https://github.com/Wbunker/skills-repo — the skills are
in the root directory. Use gh to grab the ones I ask for and copy them into
.claude/skills/. Record the source location and retrieval commands in CLAUDE.md.
```

This will:
1. Use the `gh` CLI to fetch the specified skills from the repo
2. Copy them into your project's `.claude/skills/` directory
3. Record the source location and retrieval commands in your `CLAUDE.md` for future reference

## Recommended Core Skills

These four skills work together as a toolkit for building and documenting projects:

### skill-creator

Guides for creating effective skills with proper frontmatter, progressive disclosure, and bundled resources.

```bash
gh api repos/Wbunker/skills-repo/tarball/main | tar xz --strip-components=1 -C /tmp/skills-repo
cp -r /tmp/skills-repo/skill-creator .claude/skills/
```

### agent-creator

Reference for building custom subagents — frontmatter fields, tool access patterns, permission modes, memory scopes, orchestration patterns.

```bash
cp -r /tmp/skills-repo/agent-creator .claude/skills/
```

### command-creator

Reference for building slash commands — frontmatter fields, argument passing, dynamic context injection, subagent forking, background execution.

```bash
cp -r /tmp/skills-repo/command-creator .claude/skills/
```

### codebase-docs-expert

Comprehensive codebase documentation and analysis skill. Provides 13 diagram/analysis types, multiple architectural viewpoints (SEI Views and Beyond, C4, Rozanski & Woods), cognitive load prioritization, and an orchestrated `/analyze-codebase` command that launches 16 agents to produce a complete `site-context` skill.

```bash
cp -r /tmp/skills-repo/codebase-docs-expert .claude/skills/
```

### Install all four at once

```bash
gh api repos/Wbunker/skills-repo/tarball/main | tar xz --strip-components=1 -C /tmp/skills-repo
mkdir -p .claude/skills
for skill in skill-creator agent-creator command-creator codebase-docs-expert; do
  cp -r /tmp/skills-repo/$skill .claude/skills/
done
rm -rf /tmp/skills-repo
```

## Analyzing a Codebase with codebase-docs-expert

After installing `codebase-docs-expert`, run its install script to deploy the `/analyze-codebase` command and background agent into your project:

```bash
bash .claude/skills/codebase-docs-expert/scripts/install.sh
```

Then run the analysis:

```
/analyze-codebase
```

This launches 16 agents across 8 steps that systematically analyze your codebase and produce:

- `.claude/skills/site-context/` — a complete skill with 14 reference files covering system overview, context diagrams, component maps, ERDs, dependency analysis, request flows, event catalogs, CRUD matrices, state diagrams, business rules, control flow, deployment topology, and risk assessment
- `CLAUDE.md` — a lean top-level context file with essentials and `@path` imports pointing to the site-context skill

### Prompt to kick it off

After installing, you can also just tell Claude:

```
Install the analyze-codebase command from the codebase-docs-expert skill
and run a full codebase analysis
```

Claude will run the install script and then execute `/analyze-codebase`.

## Skill Format

Each skill follows this structure:

```
<skill-name>/
  SKILL.md               # Always loaded — frontmatter, quick reference, decision trees
  references/
    <topic>.md           # Loaded only when relevant to the current task
  assets/                # Optional — files copied into output (templates, commands, agents)
  scripts/               # Optional — executable code (install scripts, validators)
```

## Available Skills

Skills cover a wide range of technologies including AWS (Lambda, Cognito), data platforms (Kafka, Hudi, Iceberg, Impala, Hive, Storm), languages (Java 11, Scala, C, TypeScript), frameworks (Spring Boot, Ionic, gRPC, Kubernetes, Istio), APIs (GitHub, Jira, Confluence, YouTube, Dropbox), tooling (Gradle, Make, VS Code, Datadog, D3.js), and documentation/architecture (codebase-docs-expert, wardley-mapping, flow-architect).

## Creating New Skills

Use the `skill-creator` skill to build new expert skills from books or documentation. Use `agent-creator` to build agent definitions and `command-creator` to build slash commands.
