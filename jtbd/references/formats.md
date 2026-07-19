# JTBD Formats & Templates

## Contents

1. [Job statement](#1-job-statement)
2. [Altitude and the job hierarchy](#2-altitude-and-the-job-hierarchy)
3. [The Universal Job Map](#3-the-universal-job-map)
4. [Desired outcome statements](#4-desired-outcome-statements)
5. [Opportunity scoring](#5-opportunity-scoring)
6. [Job story](#6-job-story)
7. [Four-forces analysis template](#7-four-forces-analysis-template)
8. [Job spec / hire spec](#8-job-spec--hire-spec)
9. [Full analysis deliverable skeleton](#9-full-analysis-deliverable-skeleton)

Grammar, rules, and templates for every JTBD artifact this skill writes or reviews. Theory and lineage: `references/foundations.md`. Playbooks that consume these formats: `references/artifact-analysis.md`. Interview and survey process that feeds them: `references/research-methods.md`. Default term: **job performer** ("job executor" is Ulwick's synonym for the same role).

---

## 1. Job statement

**Grammar (Ulwick):**

> [verb] + [object of the verb] + [contextual clarifier]

Canonical: **"listen to music while on the go"** — verb (*listen to*), object (*music*), clarifier (*while on the go*).

Write the statement from the job performer's side of the counter: their verb, their object, their life. A correct statement stays true if every product in the category vanished tomorrow.

**Good examples:**

- "listen to music while on the go" — consumer; the canonical example
- "get a nutritious dinner on the table on a weeknight" — consumer
- "allocate the team's work across the coming week" — B2B
- "restore blood flow in a blocked artery" — healthcare; stents, balloons, and bypass surgery all compete for the hire

**Bad examples — annotated:**

- "stream playlists on my phone during my commute" — **contains a solution** ("stream", "playlists", "phone"). Solutions date the statement and shrink the design space to today's technology; "listen to music while on the go" has been stable since the transistor radio.
- "quickly create accurate invoices" — **contains an adjective/adverb** ("quickly", "accurate"). Speed and accuracy are how well, not what — they are desired outcomes (§4) measured against the job, never part of it.
- "schedule the week's site visits and order the materials" — **compound "and"**: two jobs with two beginnings, two ends, and two maps. Split it; analysis built on a compound statement serves neither job.
- "manage my customer relationships" — **vague verb**. "Manage" bundles ten unnamed jobs; nothing can be mapped, measured, or designed against it.

**Rules, with reasons:**

- **Start with a precise verb from the performer's world, not the product's.** Vague-verb blacklist — *manage, handle, be able to, know, understand, use, access*. Each is unfixably ambiguous or solution-flavored: *manage/handle* bundle many jobs into one word; *be able to* states a capability, not an act; *know/understand* name mental states with no observable finish line; *use/access* presuppose the very solution the statement must exclude. When a draft starts with one, ladder down (§2) until a concrete verb surfaces.
- **One job per statement.** "And" signals two jobs; each deserves its own statement, map, and outcome set.
- **No solutions, technologies, or methods.** They date the statement and shrink the design space: "file annual taxes" survives every generation of software; "e-file through the portal" dies with the portal.
- **No quality words.** Speed, ease, and accuracy are outcomes against the job, not the job. Keeping them out of the statement keeps the outcome list (§4) honest and complete.
- **The contextual clarifier earns its place only when it changes what "done well" means.** "While on the go" forces portability, interruption-tolerance, and hands-free operation into the definition of success. If deleting the clarifier changes no design decision, delete the clarifier.

When reviewing someone else's statement, run the checks in this order — vague verb, compound "and", named solution, quality word — because fixing the verb usually reshapes everything after it.

---

## 2. Altitude and the job hierarchy

Jobs stack. Place every statement on the ladder before analyzing it:

- **Aspirations (be-goals)** — who the performer wants to be: "be a good parent." Direction, not designable.
- **Big jobs** — broad accomplishments in service of an aspiration: "raise healthy eaters." Served by ecosystems, rarely by one solution.
- **Little jobs** — the workhorse altitude: "get a nutritious dinner on the table on a weeknight." Job statements, maps, and outcome sets live here.
- **Micro-steps** — solution-level activities: "preheat the oven." Map steps or feature requests, not jobs.

Anchor the analysis to one **main job**. Record **related jobs** — adjacent jobs the same performer does before, after, or alongside it — as expansion candidates, never as extra scope inside the map.

**Moving between rungs:**

- Ladder **UP** by asking "why are you doing this?" — each answer climbs one rung.
- Ladder **DOWN** by asking "how do you do this?" — each answer descends one rung.

**Goldilocks tests:**

- **Too broad** — no single solution could meaningfully serve it: "live a healthy life" is an aspiration wearing a job costume.
- **Too narrow** — names an interaction with one product category: "upload the CSV" is a step inside somebody's current solution.
- **Right altitude** — one performer, a definable beginning and end, and room for competing solution categories to fight over it.

**Worked ladder** — start from the feature-level ask at rung 1 and climb with "why?":

| Rung | Statement | Altitude |
|---|---|---|
| 5 | be seen as someone who can run bigger things | aspiration |
| 4 | deliver the project successfully | big job — too broad to anchor |
| 3 | **keep stakeholders current on project status** | **right altitude — anchor here** |
| 2 | share the latest numbers before the steering meeting | micro-step in context |
| 1 | "add PDF export" | feature ask |

Rung 3 is right because it has one performer (the project lead), a definable beginning (reportable progress exists) and end (stakeholders are current), and competing solution categories — dashboards, standing meetings, emailed memos, PDF reports — all fighting for the hire. Rung 4 fails the single-solution test; rung 2 presumes the reporting artifact has already been chosen.

---

## 3. The Universal Job Map

Eight universal steps (Ulwick/Bettencourt). Map what the job performer is trying to **get done** — the needs view — never what they do with any current solution. Mapping the current solution produces a journey/process map and locks the analysis into that solution's shape; a job map must remain true for solutions not yet invented.

| Step | One-line definition | Diagnostic question to populate it |
|---|---|---|
| **Define** | Determine goals and plan the approach | What must the performer decide or plan before anything else? |
| **Locate** | Gather what the job requires | What inputs, information, or items must be gathered? |
| **Prepare** | Set up the environment and the inputs | What must be organized, cleaned, or made ready before starting? |
| **Confirm** | Verify readiness | What must be verified before committing? |
| **Execute** | Carry out the core of the job | What act would the performer call "actually doing it"? |
| **Monitor** | Assess progress and results | What do they watch to know it's working? |
| **Modify** | Make adjustments to stay on course | What do they adjust when it drifts? |
| **Conclude** | Finish or clean up | What finishes or cleans up the job? |

**Rules, with reasons:**

- **Write each step as verb + object in the performer's goal language** ("verify the figures"), never as a tool action ("click Validate") — tool actions smuggle the current solution back into the needs view.
- **Real maps run 8–20 steps.** The eight universals expand into job-specific sub-steps; an eight-row map is the skeleton, not the finished map.
- **Execute is one step of eight** — usually the one existing products over-serve. The under-served steps are usually elsewhere on the map.
- **Mark where performers improvise, wait, redo work, or hand off to someone else.** Opportunity concentrates in those steps — they are the parts of the job current solutions ignore, and they seed the highest-scoring outcomes (§5).
- **Treat the sequence as canonical, not chronological law.** Performers loop Monitor → Modify repeatedly and sometimes enter mid-map; keep the eight buckets without forcing strict order.

**Compact example — "prepare a monthly performance report for stakeholders":**

1. **Define** — decide what this month's report must answer, and for whom
2. **Locate** — gather the month's figures from finance, operations, and the team
3. **Prepare** — normalize the figures into comparable form
4. **Confirm** — verify the figures against source systems before publishing
5. **Execute** — assemble the narrative and the visuals
6. **Monitor** — track whether stakeholders read it and what they question
7. **Modify** — issue corrections or supplemental cuts when challenged
8. **Conclude** — archive the report and log follow-ups for the next cycle

---

## 4. Desired outcome statements

**Grammar (Ulwick):**

> [direction of improvement] + [performance metric] + [object of control] + [contextual clarifier]

Canonical: **"minimize the time it takes to verify the accuracy of the input data"** — direction (*minimize*), metric (*the time it takes*), object (*verify the accuracy of the input data*).

Directions are almost always **minimize** or **increase**. Metrics are usually **time**, **likelihood**, **number/frequency**, or **effort**. Generate outcomes against the job map: for each step, ask what makes it slow, unreliable, wasteful, or unpredictable.

**Good examples — each tied to a job-map step:**

- "minimize the time it takes to gather the month's figures from all sources" — Locate
- "increase the likelihood that discrepancies are caught before the report is published" — Confirm
- "minimize the number of times a patient's medication history must be re-entered during intake" — Prepare; healthcare
- "minimize the time it takes to detect that a concrete pour is curing unevenly" — Monitor; trades

**Bad examples — annotated:**

- "increase the number of dashboards available" — **a solution wearing metric clothes**. Dashboards are one way to serve an unstated outcome (likely "minimize the time it takes to determine current performance"); the statement dies when dashboards do.
- "make the data easier to trust" — **unmeasurable**. No direction + metric pair; it cannot be rated for importance and satisfaction on a survey, so it can never be scored.
- "minimize the time and effort it takes to find and fix errors" — **compound**: two metrics (time, effort) crossed with two objects (find, fix). A respondent rating the bundle rates none of it — split into four statements.

**Rules, with reasons:**

- **Solution-free**, so the statement stays true across product generations. Outcomes are the stable requirements; solutions rotate underneath them.
- **One metric per statement**, so it can be surveyed. The rigid grammar exists to make every statement a ratable survey item.
- **The performer's control, not the company's.** "Minimize churn" and "increase adoption" are company outcomes the performer never experiences. Write only what the performer would recognize as their own struggle.
- **Contextual clarifier: same test as §1** — include one only when it changes what "satisfied" means for that metric.
- **Volume check: a fully mapped job yields 50–150 outcome statements, commonly 75+.** If you have 12, you stopped early — you sampled the job instead of mapping it. Walk every step again.

---

## 5. Opportunity scoring

Survey job performers rating every outcome statement twice — importance and current satisfaction (sampling and questionnaire mechanics: `references/research-methods.md`). **Importance** and **Satisfaction** each equal the share of respondents answering very/extremely (top-2 box), expressed on a 0–10 basis: 84% top-2 box → 8.4.

**Formula:**

> Opportunity = Importance + max(Importance − Satisfaction, 0) — a 0–20 scale

The max() floors the gap at zero, so satisfaction above importance never drags Opportunity below Importance itself; and because importance anchors the score twice, a trivial-but-unsatisfied outcome cannot outrank an important one.

**Reading scores:**

| Pattern | Verdict | Move |
|---|---|---|
| Opportunity ≥ 12 | strongly underserved | lead the roadmap and the message with it |
| Opportunity ≥ 10 | attractive | target it |
| Satisfaction > Importance | overserved | cost-reduction / disruption territory — good-enough for less wins |
| High importance + high satisfaction | table stakes | match competitors; don't try to differentiate |

**Worked table** (outcomes from the §3 example map):

| Outcome (abbreviated) | Imp | Sat | Opp | Verdict |
|---|---|---|---|---|
| minimize time to verify figures against sources | 9.1 | 3.2 | 15.0 | strongly underserved — lead with it |
| increase likelihood errors are caught pre-publish | 8.6 | 4.5 | 12.7 | strongly underserved |
| minimize time to gather figures from all sources | 8.2 | 6.9 | 9.5 | near-attractive; watch it |
| increase likelihood the report renders on any device | 8.9 | 8.5 | 9.3 | table stakes — match, don't differentiate |
| minimize time to format the report layout | 6.0 | 8.8 | 6.0 | overserved — simplify and cheapen |

**Caveats, stated honestly:** below roughly 180 usable respondents the second decimal is noise — keep ranking by the formula, but treat scores as ordinal and never present 12.7 vs 12.4 as a real difference. For early-stage products, qualitative forces work (§7) on a handful of switch interviews usually beats a survey: learn why anyone switches before measuring how many feel underserved.

---

## 6. Job story

**Grammar (Intercom practice, articulated by Alan Klement):**

> When **[situation]**, I want to **[motivation]**, so I can **[expected outcome]**.

**Why it beats the user story for design work:** "As a [persona]" attributes behavior to identity, but circumstance drives behavior — the same person hires different solutions in different situations, and different people in the same situation hire alike. And the user story's "I want [feature]" slot puts a feature where motivation belongs: features belong in solutions, motivations in stories.

**Conversion drill — user story in, job story out:**

1. Start: "As a project manager, I want export to PDF so that I can share status."
2. Interrogate for circumstance: who asked for status? when does this bite? what just happened? who is watching? why a file rather than a login?
3. Rewrite: "When a stakeholder without an account asks how the project is going right before a steering meeting, I want to hand them something current and final-looking, so I can be seen as on top of the project without granting logins."

The rewrite exposes designs the original concealed — a read-only share link, an auto-mailed snapshot, a board-ready view. PDF export drops from requirement to candidate.

**Guidance, with reasons:**

- **Stack real context into the When** — time pressure, who's watching, what just happened. Thin situations produce thin designs; the When clause is where the design constraints live.
- **Write the so-I-can clause as progress, not a feature restatement.** "...so I can export PDFs" is circular; "...so I can be seen as on top of the project" tells the designer what done feels like — and it caught the social dimension (§8) the user story never could.
- **Keep the story at little-job altitude (§2).** A When clause about clicking buttons yields micro-optimizations; one about life circumstances yields products.
- **Use job stories as design-time framing, not a replacement for acceptance criteria.** They govern what is worth building; verification still needs testable criteria.

---

## 7. Four-forces analysis template

Fill one block per switching decision studied, sourcing every row from switch interviews (`references/research-methods.md`). Demand verbatim quotes — a block filled with paraphrase reads your own hypothesis back to you. The forces act across the whole switch timeline (First Thought / Passive Looking / Active Looking / Deciding / Onboarding / Ongoing Use), not only at purchase.

```text
FOUR FORCES — [job and switching decision under study]

PUSH OF THE SITUATION — what makes the current way intolerable
- "verbatim quote" → interpretation

PULL OF THE NEW SOLUTION — the progress the new way promises
- "verbatim quote" → interpretation

ANXIETY OF THE NEW SOLUTION
  Choice anxiety — fear of picking wrong:
  - "verbatim quote" → interpretation
  Use anxiety — fear of life after switching:
  - "verbatim quote" → interpretation

HABIT OF THE PRESENT — comfort, sunk investment, "the devil I know"
- "verbatim quote" → interpretation

DOMINANT BLOCKING FORCE: [anxiety | habit] — evidence in one line
```

**Read-out rules:**

- **Predict a switch when push + pull outweigh anxiety + habit.** No single force decides; the progress-making pair must beat the progress-blocking pair.
- **For demand generation, amplify push and pull; for conversion, reduce anxiety and habit.** They are different problems with different levers — more pull will not fix a conversion problem caused by use anxiety.
- **Name the dominant blocking force explicitly, because the remedies differ.** Anxiety calls for proof, trials, and guarantees; habit calls for migration paths, familiar interfaces, and switching services. Prescribing testimonials for a habit problem wastes the campaign.

---

## 8. Job spec / hire spec

Christensen-style specification of what it takes to get hired for a job in one circumstance. Write one spec per circumstance — the same product gets hired for different jobs at different times.

```text
JOB SPEC — [job], in [circumstance]
Circumstance:           where, when, who's present, what just happened
Functional dimension:   what must objectively get done
Emotional dimension:    how the performer wants to feel
Social dimension:       how the performer wants to be perceived
Experiences to provide: what hiring and using must feel like to nail the job
Obstacles to remove:    what blocks the hire today
Gets it HIRED:          decisive advantages over competing hires
Gets it FIRED:          failures that end the relationship
```

A spec that lists features under "Experiences" is a solution spec in disguise — experiences are felt qualities ("bought in seconds"), not components ("drive-through window").

**Filled example — the morning-commute milkshake:**

- **Circumstance:** long, boring solo drive to work; one free hand; breakfast skipped
- **Functional:** stave off hunger until noon; consumable one-handed without mess
- **Emotional:** make the commute less tedious
- **Social:** not arrive at work wearing breakfast
- **Experiences:** bought in seconds at the drive-through; thick enough to last the whole drive
- **Obstacles:** slow morning queue
- **Hired over:** bagels (need two hands), bananas (gone in a minute), doughnuts (crumbs and guilt)
- **Fired if:** runs out mid-commute, drips on the clothes, or the line makes the performer late

The afternoon buyer of the identical milkshake — a parent placating the kids — is performing a different job and needs a separate spec. One product, two jobs, two specs.

---

## 9. Full analysis deliverable skeleton

`SKILL.md` carries the required output template for artifact analyses (playbooks: `references/artifact-analysis.md`); do not restate or fork it here. Extend it with these optional sections, each earning inclusion on its own trigger:

- **Job map section** — include when the artifact spans several steps of the job or the diagnosis is "over-invested in Execute"; skip when only one step is in play.
- **Opportunity table** — include only when real importance/satisfaction data exists, with n and method stated. Without data, present outcome rankings as hypotheses, never as scores (§5 caveats).
- **Competing-hires inventory** — include when positioning, pricing, or messaging is at stake. Cover direct competitors, other-category solutions, workarounds (spreadsheets, interns, sticky notes), and non-consumption (doing without) — the last two are usually the real competition.
- **Segment-by-circumstance notes** — include when one artifact serves audiences in visibly different circumstances (the milkshake's commuter vs the afternoon parent); segmenting by persona instead smears distinct jobs into one blurry average.
