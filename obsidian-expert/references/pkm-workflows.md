# PKM Workflows and Life Integration

## Table of Contents
1. [The PKM cycle: Capture → Process → Distill → Express](#the-pkm-cycle)
2. [Daily workflow](#daily-workflow)
3. [Weekly review workflow](#weekly-review-workflow)
4. [Monthly and quarterly reviews](#monthly-and-quarterly-reviews)
5. [Project management in Obsidian](#project-management-in-obsidian)
6. [Goal tracking and OKRs](#goal-tracking-and-okrs)
7. [Reading and book notes](#reading-and-book-notes)
8. [Meeting notes](#meeting-notes)
9. [Personal CRM](#personal-crm)
10. [Habit tracking](#habit-tracking)
11. [Health and fitness journaling](#health-and-fitness-journaling)
12. [Financial notes](#financial-notes)
13. [Second Brain principles](#second-brain-principles)

---

## The PKM cycle

**Capture → Process → Distill → Express** (Tiago Forte's BASB framework)

| Stage | What it means | Obsidian implementation |
|-------|--------------|------------------------|
| **Capture** | Collect anything interesting or useful | QuickAdd to Inbox, mobile quick capture, web clipper |
| **Process** | Decide what to keep and where it goes | Work through Inbox, link notes, file or delete |
| **Distill** | Extract the most important ideas | Progressive summarization, write permanent notes |
| **Express** | Create output using your notes | Write articles, plan projects, make decisions |

**The mistake most people make:** Capturing endlessly without processing. A full inbox is not a PKM system — it's a pile.

**Rule of thumb:** Spend 20% of your PKM time capturing, 50% processing and linking, 30% creating output.

---

## Daily workflow

**Morning (5–10 min):**
1. Open today's daily note (Calendar plugin click, or Periodic Notes command)
2. Set 1–3 top priorities for the day
3. Check `tasks` due today query
4. Scan yesterday's note for carry-forwards

**During the day:**
- Quick capture via QuickAdd (don't break flow — just capture, process later)
- Add to meeting notes as meetings happen
- Update task status as work progresses

**Evening (5–10 min):**
1. Check off completed tasks
2. Move unfinished tasks to tomorrow or appropriate project note
3. Write brief journal entry (3 sentences: what happened, how I felt, what I'll do differently)
4. Log any habits (checkboxes in frontmatter or note body)
5. Capture lingering thoughts before closing

**Key insight:** The daily note is a journal + task hub + capture point. Keep it lightweight — it's a log, not a system.

---

## Weekly review workflow

Schedule 30–60 min weekly (Friday afternoon or Sunday evening works well).

**Step 1: Clear inboxes (10 min)**
- Process `0 - Inbox/` folder — file or delete every note
- Process QuickAdd captures
- Clear physical desk, email inbox, browser tabs

**Step 2: Review the week (10 min)**
- Open last 5 daily notes — scan for anything unresolved
- Review the weekly note if using Periodic Notes
- Check all active project notes for status

**Step 3: Update projects (10 min)**
- For each active project: What's the next action?
- Move completed projects to Archive
- Add new projects that emerged during the week

**Step 4: Plan next week (10 min)**
- Write the weekly note for next week
- Set 3–5 priorities for the week
- Block time on calendar for deep work

**Step 5: Brief reflection (5 min)**
- What went well?
- What drained energy?
- What's the most important thing I can do next week?

**Weekly review Dataview dashboard on the weekly note:**
````
```dataview
TASK
FROM "Projects"
WHERE !completed
SORT due ASC
```
````

---

## Monthly and quarterly reviews

### Monthly review (30–45 min)
- Review all weekly notes from the month
- Update Areas notes with anything that changed
- Review goals progress — are you on track?
- Archive completed projects
- Assess what habits you actually kept
- Capture one key insight from the month

### Quarterly review (1–2 hours)
- Review monthly notes
- Assess progress on quarterly goals/OKRs
- Set new quarterly goals for next quarter
- Update your Areas notes with major changes
- Do a "life inventory": is anything important being neglected?
- Update your "Now" page or year note

---

## Project management in Obsidian

**Project note structure:**
```markdown
---
title: Project Name
status: active
start: 2025-04-01
due: 2025-06-30
area: "[[Work]]"
tags: [project]
---

# Project Name

## Goal
One clear sentence: what does done look like?

## Why it matters


## Tasks
- [ ] Next action 📅 2025-04-07
- [ ] Second task

## Notes and decisions

## Resources
- [[Related note]]
- [[Meeting 2025-04-05]]

## Log
### 2025-04-05
- Started project, defined scope
```

**Project dashboard (Dataview):**
````
```dataview
TABLE due, status, file.mtime AS "Last updated"
FROM "Projects"
WHERE status = "active"
SORT due ASC
```
````

**Project lifecycle:**
1. Create project note from template
2. Work from the note — all tasks live here
3. Link meeting notes, research notes, references to the project note
4. When complete: update `status: complete`, move to Archive folder

**Project vs Area distinction:**
- **Project**: "Launch new website" — has an end date and finish state
- **Area**: "Marketing" — ongoing responsibility, never "done"

---

## Goal tracking and OKRs

**Annual goals → Quarterly OKRs → Weekly priorities → Daily top 3**

**Year note structure:**
```markdown
# 2025 Goals

## Theme
One word or phrase that captures the year's direction

## Objectives
### O1: [Objective]
- KR1: Measurable key result
- KR2: Measurable key result

### O2: [Objective]

## Review
| Q | Progress | Notes |
|---|---------|-------|
| Q1 | | |
| Q2 | | |
```

**Quarterly OKR note:**
```markdown
# Q2 2025 OKRs

## O1: [Objective]
- [ ] KR1: [[progress::0%]]
- [ ] KR2: [[progress::0%]]

## Weekly milestones
| Week | Milestone |
|------|-----------|
| W14 | |
| W15 | |
```

**Linking goals to daily work:** Each daily note top priorities should trace to a quarterly KR or project. If you can't connect a priority to a goal, question why you're doing it.

---

## Reading and book notes

**Capture layer (while reading):**
- Highlight and annotate in Kindle/Readwise → sync to Obsidian via Readwise Official plugin
- Or: take highlights in physical book → transfer to Obsidian after each session

**Literature note (one per book):**
```markdown
---
title: "Book Title"
author: Author Name
date-started: 2025-03-01
date-finished: 2025-04-05
rating: 4
status: read       # to-read | reading | read | abandoned
tags: [book]
genre: productivity
---

# Book Title — Author Name

## Summary (in my own words)
2–3 sentences: the main argument of this book

## Key ideas
- **Idea 1**: My paraphrase of the idea and why it matters
- **Idea 2**: 
- **Idea 3**: 

## Highlights and quotes
> "Direct quote from book" (p. 42)
My reaction or why this matters:

## How this connects
- [[Related concept note]]
- [[Another book that agrees/disagrees]]

## What I'll apply

```

**Progressive summarization:** Bold the most important sentences. Highlight the most important bolded sentences. The final layer is your own summary paragraph. This creates nested layers of distillation.

**After finishing a book:** Extract 3–5 permanent notes from the key ideas. Each permanent note is a single atomic insight, written entirely in your own words, linked to other relevant notes in your vault.

---

## Meeting notes

**Meeting note template:**
```markdown
---
date: <% tp.date.now("YYYY-MM-DD") %>
attendees: []
project: 
tags: [meeting]
---

# Meeting: <% tp.system.prompt("Meeting title") %> — <% tp.date.now("MMM D") %>

**Date:** <% tp.date.now("ddd, MMMM D, YYYY HH:mm") %>
**Attendees:** 
**Project:** 

## Agenda


## Discussion notes


## Decisions made


## Action items
- [ ] [Name]: Task 📅 [date]
- [ ] 

## Next meeting

```

**Best practices:**
- Create note before meeting, fill in agenda
- Assign action items with clear owner and due date during meeting
- Link to the project note: `project: [[Project Name]]`
- After meeting: extract action items into the project note or task system
- File in `Meetings/YYYY/` folder

---

## Personal CRM

Track relationships and interactions with people.

**Person note:**
```markdown
---
title: Person Name
company: Company
role: Role
relationship: colleague    # colleague | friend | mentor | client | vendor
last-contact: 2025-04-01
tags: [person]
---

# Person Name

**Company:** Company
**Role:** Role  
**Contact:** email@example.com | @twitter
**Met via:** 

## Background


## Interactions
### 2025-04-05 — Coffee chat
- Discussed: 
- They mentioned:
- Follow up: 

## Notes


## [[Person Name]]'s interests and context

```

**CRM dashboard:**
````
```dataview
TABLE company, role, last-contact, relationship
FROM "People"
SORT last-contact ASC
LIMIT 20
```
````
(Sort ascending to surface people you haven't contacted recently)

**Re-engagement query** (people not contacted in 90+ days):
````
```dataview
TABLE last-contact, relationship
FROM "People"
WHERE last-contact <= date(today) - dur(90 days)
SORT last-contact ASC
```
````

---

## Habit tracking

**Approach 1: Frontmatter booleans in daily notes**
```yaml
---
date: 2025-04-05
exercise: true
meditation: false
reading: true
journaling: true
---
```

Then Dataview renders a habit table:
````
```dataview
TABLE exercise, meditation, reading, journaling
FROM "Daily"
WHERE file.day >= date(today) - dur(30 days)
SORT file.day DESC
```
````

**Approach 2: Emoji/checkbox grid in the daily note body**
```
| Habit | ✓ |
|-------|---|
| Exercise | ✅ |
| Meditation | ❌ |
| Reading | ✅ |
```

**Approach 3: Separate habit tracker note**
One note with a running log table. Simple but doesn't integrate with Dataview queries.

**Recommendation:** Approach 1 (frontmatter) is most queryable and scalable. Takes 10 seconds to fill in each morning/evening.

---

## Health and fitness journaling

**Daily health log (add to daily note frontmatter):**
```yaml
sleep-hours: 7.5
sleep-quality: 3          # 1-5 scale
energy: 4                 # 1-5 scale
mood: 4                   # 1-5 scale
exercise: true
exercise-type: run
exercise-minutes: 35
```

**Weekly health summary query:**
````
```dataview
TABLE sleep-hours, sleep-quality, energy, mood, exercise-type
FROM "Daily"
WHERE file.day >= date(today) - dur(7 days)
SORT file.day DESC
```
````

**Workout log note** (in Areas/Health/):
```markdown
# Workout Log 2025

## 2025-04-05 — Morning Run
- Distance: 5k
- Time: 28:32
- Pace: 5:42/km
- Notes: felt strong, easy effort
```

---

## Financial notes

**Monthly budget note:**
```markdown
---
month: 2025-04
budget-total: 5000
spent-total: 4230
tags: [finance, monthly]
---

# April 2025 Budget

| Category | Budget | Actual | Diff |
|----------|--------|--------|------|
| Housing | 1500 | 1500 | 0 |
| Food | 600 | 720 | -120 |
| Transport | 200 | 180 | +20 |

## Notes

```

**Financial Obsidian scope:** Obsidian is good for *context, decisions, and reflection* around finances (notes about financial goals, tax prep, account summaries, spending patterns). For transaction tracking, use dedicated tools (YNAB, Monarch, spreadsheets). Paste summaries into Obsidian.

---

## Second Brain principles

From Tiago Forte's *Building a Second Brain*:

**CODE methodology:**
- **Capture**: Keep only what resonates; don't capture everything
- **Organize**: PARA structure (Projects, Areas, Resources, Archive)
- **Distill**: Progressive summarization; find the essence
- **Express**: Create output — the whole point is making things, not collecting notes

**Key insights:**
1. **Your notes are for your future self.** Write assuming you'll forget the context.
2. **Organize for action, not for reference.** File by project/area, not by topic.
3. **Intermediate packets.** Break creative work into reusable pieces (a paragraph, a diagram, a list) that can be recombined.
4. **The goal is output.** A system with thousands of notes but no output is a hobby, not a second brain.
5. **Don't over-optimize the system.** Time spent organizing is time not spent creating.

**Minimum viable PKM for most people:**
- Daily note with 3 priorities + journal entry
- Inbox for quick captures
- Project notes with next actions
- Weekly 30-minute review
- That's it. Add complexity only when you feel friction.
