# NotebookLM Prompt Library

Battle-tested prompts organized by use case. All designed for NotebookLM's source-grounded architecture.

## Table of Contents

- [Research & Analysis](#research--analysis)
- [Learning & Study](#learning--study)
- [Academic Work](#academic-work)
- [Content Creation](#content-creation)
- [Product & Business](#product--business)
- [Self-Improvement & Debugging](#self-improvement--debugging)
- [Prompt Chaining Workflows](#prompt-chaining-workflows)

---

## Research & Analysis

### Essential Questions

```
Analyze all inputs and generate 5 essential questions that, when answered, capture the
complete understanding of the material.

Focus on:
- Core topics and definitions
- Key concepts emphasized repeatedly
- Relationships between concepts
- Practical applications mentioned

For each question, explain why it matters and cite the sources that inform it.
```

### Interesting & Surprising Insights

```
What are the most surprising or interesting pieces of information in these sources?
Include direct quotes. Explain why each is noteworthy.

I'm interested in writing about [TOPIC]. Focus on [SPECIFIC ASPECT], not [OTHER ASPECTS].
```

### Source Gap Analysis

```
Review all uploaded documents together and identify what is MISSING — not what is covered.

Highlight:
- Absent perspectives or viewpoints
- Unsupported assumptions (claims made without evidence)
- Conflicting claims between sources (with direct citations from each)
- Topics mentioned but not fully explored
- Questions the sources raise but don't answer

Present as a table: Gap | Type (perspective/evidence/conflict/unexplored) | Sources involved
```

### Contradictions Finder

```
From papers on [TOPIC], identify major contradictions or conflicting findings.

For each contradiction provide:
1. Specific claim from each side (quoted with citations)
2. Possible reasons for disagreement (method, sample, context)
3. What evidence would resolve the conflict

Present chronologically if findings evolved over time.
```

### Hidden Connections

```
Synthesize the connection, however abstract, between [TOPIC 1] and [TOPIC 2].

For each relevant source:
1. Quote key evidence
2. Connect it to other retrieved information
3. Note conflicting viewpoints
4. Note interesting combinations

Synthesize into clear summary focusing on connections. Ground all points in quotes.
Acknowledge gaps.
```

---

## Learning & Study

### Comprehensive Study Guide

```
Review all uploaded materials and generate 5 essential questions that capture the
key learning outcomes.

Focus on:
- Core topics and definitions
- Key concepts emphasized repeatedly
- Relationships between concepts
- Practical applications mentioned

For each question: provide the answer with source citations, then a follow-up
question that tests deeper understanding.
```

### Middle School Teacher Persona

```
Act as an engaging Middle School Teacher. Translate source documents into language
anyone can understand.

Structure every response:
- The "tl;dr": One sentence using simple words
- Analogy: Real-world metaphor for the concept
- Vocab List: 3 difficult words defined simply

For dense paragraphs, break into True or False quiz format.
```

### Flashcard Generator

```
Create 20 flashcards from the uploaded sources on [TOPIC].

For each flashcard:
- FRONT: A clear, specific question
- BACK: A concise answer (1-3 sentences) with source citation
- DIFFICULTY: Easy / Medium / Hard

Include a mix of: definitions, comparisons, applications, and "why" questions.
Order from foundational to advanced.
```

### Concept Map Builder

```
Identify the 10 most important concepts in these sources. For each:
1. Define it in one sentence
2. List which other concepts it connects to and how
3. Cite the source that best explains it

Then describe the overall structure: which concepts are foundational (must
understand first) and which build on others?
```

---

## Academic Work

### Literature Review Themes

```
From papers on [TOPIC], identify 5-10 most recurring themes.

For each theme provide:
1. Short definition in your own words
2. Which papers mention it (with citations)
3. One sentence on how it's treated (debated, assumed, tested)

Present as structured table.
```

### Research Gap Identification

```
Identify at least three categories of research gaps across these sources:
1. Methodological gaps (how studies were conducted)
2. Theoretical gaps (frameworks or models not applied)
3. Empirical gaps (populations, contexts, or variables not studied)

For each gap: one-sentence description, which paper reveals it, and a
suggested research question that could address it.

Present as table with columns: Gap Type | Description | Revealed By | Suggested Question
```

### Methodology Comparison

```
Act as research assistant for a senior scientist. Tone: strictly objective, formal.
Assume advanced knowledge of [FIELD]. Don't define standard terminology.

Focus on methodology, data integrity, and conflicting evidence.
Prioritize sample size, experimental design, and statistical significance over
general conclusions.

Format with bolded sections:
- Key Findings
- Methodological Strengths/Weaknesses
- Contradictions across sources
```

---

## Content Creation

### Blog Post Outline

```
From these sources, create a detailed blog post outline on [TOPIC] for [AUDIENCE].

Structure:
- Hook: The most surprising finding (with quote)
- Problem: What the conventional wisdom gets wrong
- Evidence: 3-5 key points with supporting quotes
- Implications: What this means practically
- Open questions: What remains unresolved

For each section, note which source provides the best material.
```

### Presentation Builder

```
Create a 10-slide presentation outline from these sources on [TOPIC].

For each slide:
1. Title (5 words max)
2. Key message (one sentence)
3. Supporting data/quote from sources
4. Speaker notes (2-3 sentences on what to say)

Audience: [WHO]. Tone: [STYLE]. Time: [DURATION].
```

---

## Product & Business

### Product Manager Decision Memo

```
Act as a Lead Product Manager reviewing internal documentation. Ruthlessly scan
all uploaded sources for what actually matters.

Synthesize into "Decision Memo" format:
- User Evidence: Direct quotes indicating user problems
- Feasibility Checks: Technical constraints mentioned
- Blind Spots: What's missing from source text

Use bullets. If I ask vague questions, force me to clarify.
```

### Competitive Analysis

```
From these sources, build a competitive analysis on [TOPIC/MARKET].

Extract:
1. Players mentioned (direct and indirect competitors)
2. Strengths cited for each (with evidence)
3. Weaknesses or gaps identified for each
4. Market trends or shifts described

Present as comparison table. Note where sources disagree about market dynamics.
```

### Meeting Action Items

```
From these meeting transcripts/notes, extract every action item.

For each:
- Action (one sentence, starts with a verb)
- Owner (if mentioned)
- Deadline (if mentioned)
- Priority: High / Medium / Low (based on emphasis in discussion)
- Context quote (the specific discussion that led to this action)

Present as table sorted by priority. Flag any actions that are vague or lack an owner.
```

---

## Self-Improvement & Debugging

### Gap Analysis (What Went Wrong)

```
Analyze this attempt against my uploaded materials:

Project: [WHAT I TRIED]
My approach: [STEPS I TOOK]
Result: [WHAT HAPPENED]
Expected: [WHAT SHOULD HAVE HAPPENED]

Cross-reference with sources:
- Quote methodologies I didn't follow
- Identify concepts I missed entirely
- Find prerequisites I skipped

Output: "Gap in [concept]: You missed [step], but [Source, Page X] states: '[quote]'"
```

### Implementation Guide

```
Help me implement the concept of [TOPIC].

For each relevant source:
1. Quote key evidence
2. Connect it to other retrieved information
3. Note conflicting viewpoints
4. Provide a clear action to take

Synthesize into ordered action list with thorough, actionable steps.
Ground all points in specific quotes. Acknowledge knowledge gaps.
```

---

## Prompt Chaining Workflows

Sequential prompts where each output feeds the next. Run in order within the same notebook.

### Research Deep Dive (4-step)

1. **Themes** → "Identify 5-10 recurring themes across all sources. Present as table."
2. **Contradictions** → "Now identify where sources disagree on these themes."
3. **Interesting bits with steering** → "What are the most surprising findings related to [THEME FROM STEP 1]? Focus on practical applications."
4. **Implementation** → "Synthesize the most actionable findings into an ordered implementation plan."

### Learning Sequence (3-step)

1. **Essential questions** → Generate 5 questions that capture core understanding
2. **Study guide** → Create answers with source citations for each question
3. **Quiz** → Generate a 10-question quiz testing the material, with some wrong answers that get corrected

### Source Evaluation (3-step)

1. **Methodology review** → Compare methodological rigor across all sources
2. **Gap analysis** → Identify what's missing from the collective research
3. **Synthesis** → Create a balanced summary weighing source quality against findings

---

## Prompt Construction Patterns

When building custom prompts, combine these modular components:

**Persona**: `Act as [ROLE] with expertise in [FIELD].`

**Scope**: `Focus exclusively on [TOPIC]. Ignore [OTHER TOPICS].`

**Evidence**: `Include direct quotes with source citations for every claim.`

**Structure**: `Present as [table / bullets / numbered list / sections with headers].`

**Comparison**: `Do NOT summarize individually. Compare across sources.`

**Gaps**: `After answering, list aspects my sources do NOT address.`

**Confidence**: `Rate each finding: Strong (multiple sources), Moderate (one source), Speculative (implied).`

**Length**: `Keep response under [N] words.`

**Exclusion**: `Exclude [TOPIC] and any general background information.`
