# Skills Repo

A collection of expert skills for Claude Code. Each skill is an unpacked directory containing a `SKILL.md` (always loaded) and `references/` files (loaded on demand via progressive disclosure).

## Adding This Repo to Your Project

Add the following prompt to your project's `CLAUDE.md` to have Claude automatically pull the skills you need at the start of a session:

```
I have a skills repo at https://github.com/Wbunker/skills-repo the skills are in root directory use gh to grab skill-creator, agent-creator, and command-creator and copy in project .claude/skills you will know the skills once copied so no reason to record, but when done record location and commands to retrieve in CLAUDE.md
```

This will:
1. Use the `gh` CLI to fetch the specified skills from the repo
2. Copy them into your project's `.claude/skills/` directory
3. Record the source location and retrieval commands in your `CLAUDE.md` for future reference

## Skill Format

Each skill follows this structure:

```
<skill-name>/
  SKILL.md               # Always loaded — diagram, quick reference, decision trees
  references/
    <topic>.md           # Loaded only when relevant to the current task
```

## Available Skills

Skills cover a wide range of technologies including AWS (Lambda, Cognito), data platforms (Kafka, Hudi, Iceberg, Impala, Hive, Storm), languages (Java 11, Scala, C), frameworks (Spring Boot, Ionic, gRPC, Kubernetes, Istio), APIs (GitHub, Jira, Confluence, YouTube, Dropbox), and tooling (Gradle, Make, VS Code, Datadog, D3.js).

## Creating New Skills

Use the `skill-creator` skill to build new expert skills from books or documentation. Use `agent-creator` to build agent skills and `command-creator` to build slash command skills.
