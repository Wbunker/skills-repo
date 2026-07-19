# Extracting Jobs from Artifacts

## Contents

- [The universal method](#the-universal-method)
- [Sales demo / discovery call](#sales-demo--discovery-call)
- [BDD doc / Gherkin / user stories](#bdd-doc--gherkin--user-stories)
- [PRD / feature spec](#prd--feature-spec)
- [Support tickets / reviews / churn & win-loss](#support-tickets--reviews--churn--win-loss)
- [Marketing copy / landing page](#marketing-copy--landing-page)
- [Roadmap / backlog triage](#roadmap--backlog-triage)

Every artifact is a fossil record: it preserves what someone built, said, or asked for — never
the job itself. These playbooks tell you where jobs hide in each artifact type and how to dig
them out with the evidence chain intact. Run the universal method first, then the playbook that
matches the artifact in front of you. Statement grammars live in `references/formats.md`,
interview technique in `references/research-methods.md`, and the deliverable template in
`SKILL.md` — use those files rather than restating them from memory.

---

## The universal method

Three moves apply to every artifact before any playbook.

### Scan for signals

Language betrays structure. Sweep the artifact for these cues and tag every hit:

| Language cue | What it reveals |
| --- | --- |
| "so that", "so we can", "in order to" | First rung of the outcome chain — ladder it upward |
| "currently", "today we", "our process is" | The incumbent hire and its workarounds — what would get fired |
| "the problem is", "it's painful", "we keep having to" | Push of the situation |
| "can it also", "what if", "does it integrate" | Pull of the new solution being tested — or anxiety probing |
| "we've always", "the team is used to" | Habit of the present |
| "how do we know", "what happens when" | Monitor and Confirm steps of the job map |
| Unprompted questions and interruptions | Jobs the artifact's author didn't anticipate |
| Feature requests | Solutions to ladder — never jobs |

Weight interruptions above prepared content: prepared content shows what the author planned;
interruptions show what the audience actually needed.

### Ladder every signal

For each tagged signal, ask "what progress would that give the job performer?" Take the answer
and ask the question again. Stop only when the wording is solution-free — no product, feature,
or vendor name survives. Record every rung, not just the last: the intermediate rungs are
usually desired outcomes even when only the top rung is the job. Why this works: solution
words anchor analysis to the current product; laddering strips the anchor, and the rungs you
climbed through become the metrics the performer will use to judge any solution, including
yours.

### Keep the evidence chain

- Carry verbatim quotes. Every job, outcome, and force in your output cites at least one.
- Mark every claim `[Stated]` (they said it) or `[Inferred]` (you concluded it).
- Artifacts capture what people SAY in a performance context — a demo, a spec review, a public
  review. Triangulate stated claims against behavior described in the same artifact: what they
  built, worked around, or interrupted a presenter to ask about.
- Convert unknowns into interview questions (`references/research-methods.md`) rather than
  guessing. A named gap is useful; a guessed answer is a landmine.

Why the discipline matters: JTBD analysis fails socially when it reads as clever storytelling.
Traceability — every claim tied to words a stakeholder recognizes — is what turns analysis into
decisions instead of debate. Assemble the deliverable with the output template in `SKILL.md`.

---

## Sales demo / discovery call

Works on transcripts, recording notes, and demo scripts. A demo is two artifacts in one: the
vendor's beliefs and the prospect's reality, interleaved.

### Read it twice, in two directions

Pass one — the vendor's implied job hypotheses. Running order and airtime allocation are
confessions: whatever the vendor shows first and longest is what they believe the priority
jobs are. Write that implied list down. Pass two — the prospect's revealed jobs: harvest their
questions, interruptions, "will it…" asks, and the moments they lean in or take over, then
ladder each. The divergence between the two lists is the single most valuable finding a demo
analysis produces — it is the vendor's job hypothesis being falsified live, for free.

### Place the prospect on the buying timeline

Fix their stage on the six-stage timeline — First Thought, Passive Looking, Active Looking,
Deciding, Onboarding, Ongoing Use — from language markers:

- "we just started looking around" → Passive Looking or early Active Looking
- "we're comparing you with X" → Active Looking
- "what would rollout look like", procurement and legal questions → Deciding
- asking for training and admin-setup details → Onboarding concerns surfacing pre-purchase

Why it matters: the right selling move differs per stage. Educating a prospect who is already
at Deciding annoys them; pushing to close one at Passive Looking scares them off.

### Build the forces inventory from objections and questions

- "we use X today and it mostly works" → habit of the present
- security, compliance, and lock-in questions → anxiety of the new solution (the in-choice
  form: is this the right pick?)
- "will my team actually use it" → anxiety of the new solution (the in-use form: can we make
  it work?)
- "our process breaks when…" → push of the situation
- unprompted "could we also use it for…" → pull of the new solution
- price pushback → usually insufficient push and pull, not a pricing problem; treat it as
  evidence the progress on offer does not yet outweigh the forces holding them in place

### Map the people in the room

Attendees are performers of different jobs, and each can veto:

- Champion — carries the emotional job of being the person who finally fixed this.
- Purchase decision maker — the financial job: justify the spend, de-risk the choice.
- End users — the core job the product would be hired for.
- IT / ops — consumption-chain jobs: install, integrate, maintain.

A demo that plays only to one role's jobs stalls with the others. Note which roles in the
room got zero airtime aimed at their jobs.

### Produce these deliverables

1. Ranked job inventory, each entry with its evidence quote.
2. Forces map — all four forces, quoted.
3. Timeline-stage placement with its marker quotes.
4. Gap list: prospect jobs the demo never addressed, and demo segments serving no discovered
   job.
5. Demo restructure recommendations: open on the struggling moment, not the product tour;
   sequence features as episodes of progress on discovered jobs; answer anxieties explicitly
   with proof rather than assurances; cut segments serving no job.

Ground every recommendation in the Demand-Side Sales stance: do not push the product — present
how it fits the prospect's life. Selling is helping someone make progress they have already
decided they need.

### Worked example

Fictional excerpt: "Panorama", a B2B analytics tool, demoing to a mid-size logistics company.
AE is the vendor's account executive.

> **AE:** …and here's the dashboard builder — drag any metric onto the canvas and it updates
> live.
> **VP Ops (interrupting):** Before dashboards — today we pull six CSVs into a spreadsheet
> every Monday morning. Someone forgets a file about every third week. Does this refresh on
> its own?
> **AE:** Fully automated syncs, yes. Now, our anomaly-detection AI—
> **Ops Manager:** Hang on. When a sync breaks at 7 a.m. Monday, who finds out first — us, or
> the CEO in the meeting?
> **AE:** You'd get an alert email. So, the AI can flag unusual trends—
> **VP Ops:** We're also evaluating BoardMetrics; honestly their demo looked the same. Our
> real worry: the last tool we rolled out, ops and finance showed different revenue numbers
> in the same meeting. Never again.
> **Analyst:** Could we also use it for the monthly report we send customers? That's a whole
> separate spreadsheet right now.
> **AE:** That's on the roadmap. Let me show you the AI insights…

Compact analysis:

- **Performers:** VP Ops — job performer and likely champion. Ops Manager — Monitor step plus
  consumption-chain jobs. Analyst — end user carrying a second job. Finance — absent but
  holding veto power `[Inferred]` from the revenue-mismatch story.
- **Stage:** Active Looking — "we're also evaluating BoardMetrics" `[Stated]`.
- **Main job:** assemble a trusted weekly operating picture when the data lives in many
  systems. Laddered from the six-CSV ritual; "trusted" earns its place via the finance story.
- **Little jobs:** catch a broken data feed before the Monday meeting starts (Ops Manager);
  send customers a monthly performance report without rebuilding it by hand (Analyst).
- **Forces:** push of the situation — "someone forgets a file about every third week"
  `[Stated]`. Anxiety of the new solution — "ops and finance showed different revenue
  numbers in the same meeting" `[Stated]`. Habit of the present — "today we pull six CSVs
  into a spreadsheet every Monday" `[Stated]`.
- **Gaps:** the anomaly-detection AI got the most airtime and zero prospect interest — a
  vendor hypothesis falsified live. The Monitor-step anxiety ("who finds out first") was
  answered with an assurance, not proof — restructure to demo a sync failing and the
  recovery path.

---

## BDD doc / Gherkin / user stories

### What BDD encodes — and what it structurally hides

Scenarios specify SOLUTION behavior: what the system does when poked. Recover jobs by
laddering, because no Gherkin keyword holds one. The emotional and social dimensions of the
job are structurally absent — Given/When/Then has no slot for how the performer feels or
wants to be seen. Flag those dimensions as research gaps in your output; never pretend a
behavior spec contains them.

### The mapping, clause by clause

- **Feature narrative** — "In order to X / As a Y / I want Z" (or "As a… I want… so that…"):
  the "in order to" / "so that" clause is the first rung of the outcome chain. Ladder it
  until the job appears.
- **"As a [role]"** is persona smuggling. Roles do not have jobs; performers in circumstances
  do. Recover the actual circumstance from the Givens and the story around the feature.
- **Given** — circumstance fragments frozen at system-state level. Raise each to life- or
  work-state: "Given I have 3 overdue tasks" → "when my commitments have slipped and someone
  is about to notice."
- **When** — the little hire: the exact interaction moment where the performer employs the
  product.
- **Then** — a candidate desired outcome wearing system clothes. Rewrite it in outcome
  grammar: direction of improvement + performance metric + object of control + contextual
  clarifier (`references/formats.md`).

### Aggregate upward

1. Cluster scenarios → little jobs.
2. Cluster features → steps of a main job.
3. Read the whole doc against the Universal Job Map — Define, Locate, Prepare, Confirm,
   Execute, Monitor, Modify, Conclude — and mark which steps the product serves and which it
   ignores. Unserved Monitor and Modify steps are the classic blind spot: teams spec the
   happy path and forget the performer must notice drift and correct course.

### Find and report

- Scenarios serving no recoverable job — ceremony, tech-debt tests, requirements theater.
  Kill candidates, or unit tests wearing a Gherkin costume.
- Jobs implied by narratives but covered by no scenario — coverage gaps.
- Thens no user would recognize as success — system-centric criteria ("Then the cache is
  invalidated"). The performer's success lives elsewhere; say where.

### Rewrite move

Convert user stories to job stories — "When [situation], I want to [motivation], so I can
[expected outcome]" — and propose enriched Given clauses that carry circumstance, so future
tests encode the job instead of hiding it. The conversion pattern, once:

> As an admin, I want bulk user deactivation → When someone leaves the company and their
> access must end today, I want to shut off every account they hold at once, so I can close
> the exposure before anyone can use it.

### Worked example

```gherkin
Feature: Scheduled report sharing
  In order to keep stakeholders informed without manual work
  As a team lead
  I want reports emailed on a schedule

  Scenario: Weekly report is delivered
    Given a report "Pipeline Review" with a weekly schedule
    And 3 recipients are subscribed
    When the scheduled time arrives
    Then each recipient receives an email with a PDF attachment

  Scenario: Schedule record is persisted
    Given valid schedule settings
    When the team lead saves the schedule
    Then a schedule row is stored with status "ACTIVE"

  Scenario: Recipient without an account views the report
    Given a recipient has no account
    When they open the report link
    Then the report renders in read-only mode
```

Compact analysis:

- **Laddered main job:** "keep stakeholders informed without manual work" → what progress? →
  stakeholders act on current numbers without chasing me → keep decision-makers current on
  team performance without preparing updates by hand.
- **Little jobs:** scenario 1 — get the current report in front of every stakeholder on a
  reliable rhythm; scenario 3 — let an outside stakeholder read the report without setup
  friction.
- **Outcomes recovered from Thens:** minimize the time it takes for stakeholders to receive
  the current report after the period closes (scenario 1); minimize the number of steps a
  recipient without an account must take to read a shared report (scenario 3).
- **Flagged — serves no recoverable job:** scenario 2 persists a row with a status. No
  performer's progress depends on the row; it is a unit test in Gherkin costume.
- **Coverage gap:** the narrative promises "without manual work", yet no scenario lets the
  lead confirm what was actually sent when a stakeholder says "I never got it" — the Monitor
  step is unserved `[Inferred]`; convert to a research question.
- **Converted job story:** When a reporting period closes and stakeholders expect an update,
  I want to put the current report in front of them automatically, so I can keep them
  current without assembling anything by hand. Enriched Given to match: "Given the weekly
  pipeline meeting is tomorrow and the report has unsent changes".

---

## PRD / feature spec

A PRD is usually a solution wearing a problem statement as a hat. Test the hat first.

**Test the problem statement.** Is it a job, or a feature request restated? "Users need bulk
edit" fails the solution-swap test: swap in any other solution and the "problem" evaporates,
which proves it never described a problem. Rewrite the statement in job grammar — verb +
object + contextual clarifier — and see what survives. What does not survive is what the
team assumed instead of discovered.

**Audit the success metrics.** Map every stated metric to a desired outcome. Metrics that
measure product activity — DAU, clicks, feature adoption — rather than job performer progress
are metric theater: the product can hit them while the performer gets nowhere. Propose
replacements in outcome grammar (direction of improvement + performance metric + object of
control + contextual clarifier).

**Recut the segmentation.** Demographic and role framing ("for enterprise admins") groups
people who face different circumstances. Recut by circumstance — "when responsibility for
other people's access lands on you and an audit is coming" — because circumstance predicts
the hire and the role does not.

**Map scope onto the job map.** Place every scoped feature on Define, Locate, Prepare,
Confirm, Execute, Monitor, Modify, Conclude. The resulting picture exposes over-investment
(three features piled on Execute) and neglect (nothing on Confirm or Monitor). Report both:
the neglected steps are where a competitor gets hired alongside this product.

---

## Support tickets / reviews / churn & win-loss

**Tickets are little-hire struggling moments.** Cluster them by job step, not by feature
area — feature-area clustering reproduces the org chart, and the org chart is not the job.
The phrase "I'm trying to…" in a ticket is the job stated verbatim: harvest every instance
first, because users write it unprompted and solution-free.

**Reviews are jobs in the wild.** "I use it to…" sentences are hires described by the
performer — collect them as job candidates. One-star reviews name firing criteria: the
outcomes whose failure ends the hire. Five-star reviews name the winning forces of the
hire — the pull that landed and the anxiety that proved unfounded. Read both ends of the
distribution; the three-star middle mostly restates the feature list.

**Churn notes and win-loss run the four forces in REVERSE.** The switch already happened —
away from you. Reconstruct:

1. Push away from us — what struggle did we become?
2. Pull of the replacement — what progress did they believe the new solution offered?
3. The anxiety about leaving they overcame — and what proof convinced them. That proof is
   the competitor's best sales asset; name it explicitly.
4. The habit of the present that failed to retain them — the investment in us that turned
   out not to bind.

The timeline runs backward from the cancellation, exactly like a switch interview
(`references/research-methods.md`): the cancellation is the purchase moment of the
replacement. Date their First Thought of leaving; the gap between the two is how long you
had to intervene and did not.

---

## Marketing copy / landing page

Audit each page element for which force it works. An element working no force is decoration:

- Headlines → usually sell pull of the new solution.
- Problem-agitation sections → manufacture push of the situation.
- Testimonials and customer logos → reduce anxiety of the new solution (in-choice).
- "Switch in minutes" and migration promises → attack habit of the present.
- Free trials and money-back guarantees → reduce anxiety of the new solution (in-use).

**Feature-led vs progress-led.** A feature list asks the visitor to do the laddering
themselves — to work out what progress each capability implies. Most will not. Flag every
section that presents capability without circumstance or progress attached.

**Rewrite exercise.** Recast the hero headline as circumstance + progress — "When X happens,
get to Y" — then check that every claimed benefit on the page traces to a real discovered
job, not to an internal roadmap justification. Benefits that trace only to the roadmap are
the company talking to itself in public.

---

## Roadmap / backlog triage

Map every backlog item to a job and a desired outcome. Two orphan classes fall out:

- **Orphan items** (no job): either cut candidates or evidence of an undiscovered job.
  Decide which honestly — laddering an item to a job nobody has evidenced is retrofitting,
  not discovery.
- **Orphan outcomes** (high opportunity, no item serving them): this list is the growth
  backlog, and it came free with the triage.

When priorities tie, prefer the item serving an underserved step of the main job over the
one adding a related job: depth on the job you are already hired for compounds retention,
while breadth bets on a second hire you have not yet earned.
