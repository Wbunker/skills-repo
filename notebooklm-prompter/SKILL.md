---
name: notebooklm-prompter
description: >
  Generate optimized prompts for Google NotebookLM. Helps users craft chat prompts, Audio
  Overview customization instructions, and structured analysis queries that exploit NotebookLM's
  source-grounded architecture. Triggers on: "NotebookLM prompt", "notebook prompt",
  "/notebooklm-prompter", "create a NotebookLM prompt", "Audio Overview prompt", "podcast
  prompt for NotebookLM", or when a user wants to prepare prompts for use in NotebookLM.
  Also assists with notebook planning — choosing which sources to upload and how to organize
  notebooks for best results.
---

# NotebookLM Prompt Generator

Generate prompts optimized for Google NotebookLM's source-grounded architecture. NotebookLM is NOT ChatGPT — it only answers from uploaded sources, auto-cites everything, and refuses to improvise. Prompts must exploit this.

## Key Principle: Sources First, Prompts Second

NotebookLM's output ceiling is determined by source quality. Before writing prompts, help the user plan their notebook:

| Source type | Limit | Notes |
|-------------|-------|-------|
| Per source | 500K words / 200MB | PDFs, Docs, Slides, Sheets, URLs, YouTube, audio, images |
| Per notebook | 50 (free) / 300 (Plus) / 600 (Ultra) | Quality > quantity — 5-10 focused sources beats 50 scattered ones |

**Source advice**: Curate 5-10 thematically related, high-quality sources. One focused notebook outperforms a dumping ground. NotebookLM accuracy degrades as you approach source limits.

## Prompt Generation Workflow

### Step 1: Understand the user's goal

Ask what they want to accomplish in NotebookLM. Map to a category:

| Goal | Prompt type | Reference |
|------|------------|-----------|
| Research & analysis | Chat prompts | This file |
| Learn / study | Chat prompts + Studio outputs | This file |
| Create podcast | Audio Overview customization | `references/audio-overview.md` |
| Create presentation | Slide/video prompts | This file |
| Compare sources | Cross-source analysis | `references/prompt-library.md` |
| Find gaps / contradictions | Advanced analysis | `references/prompt-library.md` |

### Step 2: Apply the 4 rules of NotebookLM prompting

Every effective NotebookLM prompt follows these rules:

1. **Request specific quotes and citations** — not summaries, actual evidence
2. **Ask for contradictions, not just agreement** — where do sources disagree?
3. **Demand acknowledgment of gaps** — what's missing? What can't be answered?
4. **Force structured output** — tables, bullets, sections with clear headings

### Step 3: Build the prompt

Use this structure for all NotebookLM prompts:

```
[ROLE/CONTEXT — who the user is and why they need this]

[SPECIFIC TASK — exactly what to analyze, extract, or produce]

[CONSTRAINTS — what to focus on, what to exclude]

[OUTPUT FORMAT — tables, bullets, sections, comparison format]

[CITATION REQUIREMENT — "Include direct quotes with source references"]

[GAP AWARENESS — "Note any aspects my sources do not address"]
```

### Step 4: Deliver the prompt(s)

Give the user ready-to-paste prompts. Include:
- The prompt text in a code block (easy to copy)
- Which NotebookLM feature to use it with (Chat, Audio Overview customize field, etc.)
- What sources to upload for best results

## Quick Prompt Templates

### General Research

```
Analyze all uploaded sources on [TOPIC]. For each key finding:
1. State the claim
2. Quote supporting evidence with source citations
3. Note any conflicting perspectives across sources
4. Rate confidence: Strong (multiple sources agree), Moderate (one source), Weak (implied)

Present as a structured table. After the table, list what my sources do NOT address.
```

### Summarize for a Specific Audience

```
Summarize these sources for [AUDIENCE — e.g., "a busy CEO", "a first-year grad student",
"a non-technical board member"]. Focus on:
- [SPECIFIC ASPECT 1]
- [SPECIFIC ASPECT 2]

Use [FORMAT — bullets / numbered list / table]. Include direct quotes for key claims.
Keep it under [LENGTH — e.g., "500 words"]. Flag anything my sources leave unclear.
```

### Compare & Contrast Sources

```
Compare the following across my uploaded sources:
- How each source treats [TOPIC]
- Where they agree (with quotes from each)
- Where they contradict (with quotes from each)
- Which provides stronger evidence and why

Do NOT summarize sources individually. Only analyze them in comparison.
Present disagreements as: Claim A (Source X) vs Claim B (Source Y).
```

### Extract Actionable Items

```
From all uploaded sources, extract every actionable recommendation, step, or best practice.

For each item:
1. The action (one sentence)
2. Supporting quote from source
3. Priority: High / Medium / Low (based on how strongly sources emphasize it)
4. Prerequisites or dependencies mentioned

Present as an ordered list, highest priority first.
```

## Audio Overview Prompts

For detailed guidance on crafting Audio Overview (podcast) customization prompts, including format selection (Deep Dive, Brief, Critique, Debate), audience targeting, and focus control, read `references/audio-overview.md`.

## Full Prompt Library

For the complete collection of proven prompt templates organized by use case (research, learning, academic, content creation, product management, debugging), read `references/prompt-library.md`.

## Common Mistakes to Warn Users About

- **Being vague**: "Tell me about climate change" → vague output. "Identify contradictions in these papers about carbon capture methodology" → gold
- **Treating it like ChatGPT**: NotebookLM is analytical, not creative. Don't ask it to brainstorm or write fiction
- **Not uploading enough sources**: One paper isn't enough for cross-source analysis
- **Ignoring citations**: The whole point is grounded responses — tell users to click through
- **Asking about content not in sources**: It will refuse. Help users phrase questions that their sources can actually answer
- **Uploading too many unrelated sources**: Dilutes quality. One focused notebook > one everything notebook
