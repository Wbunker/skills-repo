# Audio Overview Prompts

How to craft customization prompts for NotebookLM's Audio Overview (AI podcast) feature.

## Table of Contents

- [Format Selection](#format-selection)
- [The Customize Field](#the-customize-field)
- [Audience Targeting Prompts](#audience-targeting-prompts)
- [Focus Control Prompts](#focus-control-prompts)
- [Tone and Style Prompts](#tone-and-style-prompts)
- [Advanced Patterns](#advanced-patterns)
- [Tips for Better Results](#tips-for-better-results)

---

## Format Selection

NotebookLM offers four Audio Overview formats. Choose before writing the customization prompt:

| Format | Hosts | Best for | Duration |
|--------|-------|----------|----------|
| **Deep Dive** | Two hosts, conversational | Thorough exploration of complex topics | 5-20 min |
| **The Brief** | Single speaker | Quick overview, executive summary | ~5 min |
| **The Critique** | Two hosts | Critical review with constructive feedback | 5-20 min |
| **The Debate** | Two hosts, opposing views | Exploring tensions and tradeoffs | 5-20 min |

Length options: Shorter (~5 min), Default (~10 min), Longer (~20 min, English only).

## The Customize Field

When generating an Audio Overview, you get a text field: **"What should the AI hosts focus on?"**

This is where the prompt goes. Keep it directive — these are instructions, not conversation.

### Basic template

```
Focus on [SPECIFIC TOPICS]. Target audience: [WHO].
Tone: [STYLE]. Ignore [WHAT TO SKIP].
```

### Full template

```
[AUDIENCE CONTEXT]
[FOCUS AREAS — what to cover]
[EXCLUSIONS — what to skip]
[TONE/STYLE INSTRUCTIONS]
[SPECIAL INSTRUCTIONS — analogies, examples, questions to pose]
```

---

## Audience Targeting Prompts

### Executive / CEO briefing

```
You are briefing a busy CEO. Do not use fluff or banter. Go straight to the bottom line:
What is the problem, what is the solution, and what are the financial implications?
Keep it under 10 minutes.
```

### Undergraduate student

```
Explain it as if I'm a student revising for an undergraduate midterm. Define every
technical term. Use real-world analogies. Emphasize what's likely to be on an exam.
```

### Non-technical stakeholder

```
Translate all technical concepts into business language. No jargon. For every technical
claim, explain why a non-engineer should care. Focus on impact, not implementation.
```

### Expert in the field

```
Assume advanced knowledge of [FIELD]. Skip introductory material and definitions.
Focus on novel contributions, methodological innovations, and how findings challenge
or extend existing work. Be specific about statistical methods and effect sizes.
```

### Smart 12-year-old

```
Explain the core concepts as if teaching a smart 12-year-old. Use analogies for every
complex term. If a concept is abstract, ground it in a physical, real-world example.
Focus on why this matters, not just what it is.
```

---

## Focus Control Prompts

### Topic filtering

```
Focus exclusively on [TOPIC]. Ignore all content related to [OTHER TOPIC].
I only care about [SPECIFIC ASPECT].
```

### Source-specific focus

```
Focus primarily on Source 2 and Source 5, comparing their methodologies.
Reference other sources only when they directly support or contradict these two.
```

### Industry filtering

```
Filter the discussion for [INDUSTRY] professionals. Spotlight only business
opportunities for entrepreneurs. Skip academic theory unless it directly
informs a practical business decision.
```

### Practical applications only

```
Skip theory and background. Focus exclusively on practical applications,
actionable recommendations, and implementation steps. For each recommendation,
explain exactly what someone should do on Monday morning.
```

---

## Tone and Style Prompts

### No-nonsense analysis

```
Tone: strictly objective, formal. No banter between hosts. No "that's interesting!"
or "great point!" filler. Every sentence should deliver information or analysis.
```

### Storytelling approach

```
Use narrative structure. Start with a hook — the most surprising finding. Build
tension around the central problem. Resolve with the key insight. Weave in direct
quotes from sources as characters in the story.
```

### Debate format

```
Host 1 argues for [POSITION A]. Host 2 argues for [POSITION B]. They should
challenge each other's points, cite specific evidence from sources, and
acknowledge when the other makes a valid point. End with areas of genuine
uncertainty where the evidence is mixed.
```

### Quiz show format

```
A quiz show with two hosts. First host quizzes the second on [TOPIC]. 10 questions
from the sources. The host gets answers wrong sometimes. The other corrects with
right answers. Show sources for each answer. Make it engaging and memorable.
```

---

## Advanced Patterns

### Multilingual podcast

```
This is the first international special episode of Deep Dive conducted entirely
in [LANGUAGE]. Cover the key findings from all sources.
Special instructions:
- Only [LANGUAGE] for entire duration
- No English except to clarify unique technical terms that lack clean translations
- Maintain natural conversational flow in [LANGUAGE]
```

### Sequential deep dives

Generate multiple Audio Overviews from the same notebook, each with a different focus:

1. **Overview**: "Cover the 3 most important findings at a high level. This is the first episode in a series."
2. **Deep dive on finding 1**: "Focus exclusively on [FINDING 1]. Explain the methodology, evidence, and implications in detail."
3. **Critique**: "Critically evaluate the methodology and conclusions. What are the weaknesses? What's missing?"

### Before/after comparison

```
Structure the discussion as before vs after. First explain the conventional
understanding of [TOPIC]. Then explain how these sources challenge or update
that understanding. Highlight the specific evidence that forces the update.
```

---

## Tips for Better Results

1. **Consolidate notes first** — upload one comprehensive source document rather than many small files. This produces deeper, more cohesive discussion.
2. **Use the length selector** — "Shorter" for briefs, "Longer" for deep dives. Don't rely on auto.
3. **Be specific about audience** — "business executive" produces very different output from "PhD student."
4. **Specify exclusions** — telling it what to skip is as important as what to include.
5. **View the generated prompt** — click the three-dot menu next to your artifact in the Studio panel and select "View custom prompt" to see how NotebookLM interpreted your instructions.
6. **Iterate** — generate, listen to the first 2 minutes, then regenerate with refined instructions.
7. **Interactive Join Mode** — on Deep Dive format, you can interrupt the AI hosts and steer the conversation in real-time. Use this for follow-up questions.
