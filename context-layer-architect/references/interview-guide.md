# Deep Interview Guide

How to extract tribal knowledge and architectural context from stakeholders.

---

## Table of Contents

1. [The Interview Mindset](#the-interview-mindset)
2. [Question Categories](#question-categories)
3. [Non-Obvious Questions](#non-obvious-questions)
4. [Follow-up Patterns](#follow-up-patterns)
5. [Red Flags to Probe](#red-flags-to-probe)
6. [Interview Flow](#interview-flow)
7. [Capturing Responses](#capturing-responses)

---

## The Interview Mindset

**Goal:** Surface what code alone cannot express.

Code shows WHAT exists. Interviews reveal:
- WHY it's structured this way
- WHAT must never happen
- WHERE the real boundaries live
- WHO knows what (expertise distribution)
- WHEN things go wrong and how

**You're not documenting.** You're compressing years of experience into tokens.

---

## Question Categories

### Architecture & Boundaries

**Purpose:** Understand system ownership and contracts.

- "What does [X] own that might surprise someone new?"
- "What does [X] explicitly NOT own, even though it looks like it should?"
- "What's the contract between [A] and [B]? What breaks if violated?"
- "Where are the real enforcement points? (Not where it looks like, where it actually is)"
- "If you could draw a line around 'don't touch this,' where would it be?"

### Historical Context

**Purpose:** Capture decisions and their rationale.

- "Why is [X] structured this way instead of the obvious approach?"
- "What incident or bug led to [this pattern]?"
- "What would break if someone 'fixed' [this unusual code]?"
- "Is there a Slack thread or ADR that explains [decision]?"
- "When was the last time this area caused problems? What happened?"

### Invariants & Anti-patterns

**Purpose:** Define what must never happen.

- "What operation must NEVER be performed here?"
- "What's the most common mistake newcomers make?"
- "What looks safe but isn't?"
- "What assumption does the code make that isn't enforced by types?"
- "If an agent changed [X], what cascade would that trigger?"

### Integration & Dependencies

**Purpose:** Map hidden connections.

- "What external systems does this depend on that aren't obvious from imports?"
- "What retry/timeout/circuit-breaker behavior exists here?"
- "What happens when [dependency] is slow or unavailable?"
- "Are there any undocumented APIs this calls?"
- "What order must operations happen in? What's not enforced?"

### Tribal Knowledge

**Purpose:** Extract what lives only in heads.

- "What do you wish you'd known before working in this area?"
- "What question do new team members always ask?"
- "What's the thing you have to explain verbally every time?"
- "Where's the 'here be dragons' zone?"
- "What's the one thing that would cause an outage if done wrong?"

---

## Non-Obvious Questions

Avoid questions with obvious answers. Instead of "How do you add a new API endpoint?", ask:

### Instead of obvious → Ask:

| Obvious | Non-obvious |
|---------|-------------|
| "How do you run tests?" | "Which tests are flaky and why?" |
| "What's the directory structure?" | "What lives somewhere surprising?" |
| "What's the coding style?" | "What style diverges from conventions and why?" |
| "How do you deploy?" | "What breaks during deployment that isn't automated?" |
| "What does this service do?" | "What does this service refuse to do?" |

### Questions that reveal hidden complexity:

- "What takes 5 minutes to explain but 30 seconds to mess up?"
- "What config value would cause a production incident if changed?"
- "What's the scariest file to modify?"
- "What's the difference between how this looks and how it actually works?"
- "What's the one thing ChatGPT/Claude always gets wrong here?"

---

## Follow-up Patterns

### The "Why" Chain

Keep asking "why" until you hit bedrock:

```
Q: "Why is the retry count 5?"
A: "Because the gateway has high timeout rates."
Q: "Why not handle it differently?"
A: "We tried, but the SDK doesn't support it."
Q: "Why use that SDK?"
A: "It's mandated by the payment processor."
→ Now you know: "Retry count 5 due to gateway timeouts, SDK limitation, processor mandate."
```

### The "What If" Probe

- "What if someone removed this?"
- "What if this ran twice?"
- "What if the order changed?"
- "What if this failed silently?"

### The "Last Time" Anchor

- "When was the last time this caused problems?"
- "What did you learn from that?"
- "Is that captured anywhere?"

### The "Newcomer" Perspective

- "What would confuse a new team member?"
- "What did YOU find confusing when you started?"
- "What's the most common misunderstanding?"

---

## Red Flags to Probe

When you see these in code, dig deeper:

### Code Smells That Hide Context

| Smell | Question to Ask |
|-------|-----------------|
| Comment: "Don't change this" | "What happens if someone does?" |
| Comment: "Temporary fix" | "How temporary? What's the real fix?" |
| Unusual retry logic | "Why this specific pattern?" |
| Hard-coded values | "Why these specific numbers?" |
| Dead-looking code | "Is this actually dead or serving hidden purpose?" |
| Environment-specific logic | "What's different and why?" |
| Feature flags | "What's the lifecycle of these?" |
| Integration code | "What's undocumented about this API?" |

### Structural Smells

- **Circular dependencies:** "Why do these reference each other?"
- **Duplicate logic:** "Is one canonical? Which should agents use?"
- **Deep nesting:** "Is there simpler way agents should prefer?"
- **Inconsistent patterns:** "Which is the current standard?"

---

## Interview Flow

### Phase 1: Orientation (5 min)

```
"I've analyzed the codebase. Let me share what I found, then
I have questions to fill in what code alone can't tell me."

[Share exploration findings briefly]

"Sound accurate? Anything I got wrong?"
```

### Phase 2: Boundary Mapping (10-15 min)

```
"Let's walk through the major areas. For each, I want to know:
- What it owns
- What it doesn't own
- Key contracts with other areas"

[Go through each semantic boundary identified]
```

### Phase 3: Deep Dives (15-20 min)

```
"Now let's go deeper on the areas that seem complex or risky."

[Focus on areas with red flags, unusual patterns, or high impact]
```

### Phase 4: Tribal Knowledge Sweep (10 min)

```
"What haven't I asked about that an agent needs to know?
What's the thing that breaks if someone doesn't know the secret?"
```

### Phase 5: Validation (5 min)

```
"Let me summarize what I've learned. Correct anything wrong."

[Read back key findings]
```

---

## Capturing Responses

### For each insight, record:

```markdown
## [Area/Topic]

**What:** [The fact or pattern]
**Why:** [The rationale or history]
**Source:** [Who said it / where to find more]
**Confidence:** [High/Medium/Low]
**Node placement:** [Which CLAUDE.md this belongs in]
```

### Categorize as you go:

- **Invariants:** Things that must never happen → Critical, goes in node
- **Patterns:** How to do things → Goes in node with example
- **Context:** Why things are this way → Summarize for node
- **Questions:** Unresolved → Track for follow-up
- **Tasks:** Discovered work → Track separately

---

## Interview Prompt Template

Use this with AskUserQuestion tool:

```
Based on my exploration of this codebase, I have questions to extract
context that code alone can't express. I'll ask about:

- Technical implementation decisions
- Historical constraints and rationale
- Invariants and anti-patterns
- Integration quirks and tribal knowledge
- Concerns and tradeoffs

My questions won't be obvious—I'm looking for what an agent would
get wrong without insider knowledge.

[First batch of 2-4 specific questions based on exploration findings]
```

**Continue interviewing** until:
- All major areas covered
- All red flags explained
- Interviewee says "I think that's everything"
- Questions start getting "obvious" answers

---

## Sample Interview Questions by Domain

### For Backend Services

- "What's the difference between apparent ownership and actual ownership?"
- "What database operations have surprising side effects?"
- "What API contracts aren't enforced by types?"
- "What happens when [service] is slow? Does anything timeout first?"

### For Frontend

- "What state management patterns diverge from the framework norm?"
- "What components look simple but have complex edge cases?"
- "What styling approach should agents use vs avoid?"
- "What renders differently in production vs development?"

### For Data/ML

- "What assumptions does the model make about input data?"
- "What feature engineering is critical but not obvious?"
- "What training data constraints exist?"
- "What happens when predictions are wrong in specific ways?"

### For Infrastructure

- "What's manual that looks automated?"
- "What deployment order matters?"
- "What monitoring gaps exist?"
- "What alerts are noisy vs critical?"
