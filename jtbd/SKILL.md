---
name: jtbd
description: Jobs-to-be-Done (JTBD) expert — analyzes any artifact for the jobs customers are hiring a product to do and produces rigorous JTBD deliverables. Use whenever the user mentions JTBD, jobs to be done, job stories, job maps, desired outcomes, switch interviews, forces of progress, struggling moments, or hiring/firing a product — and also whenever they ask what customers are really trying to accomplish, why customers buy, switch, or churn, or want a sales demo, demo script, discovery-call transcript, BDD/Gherkin doc, user story, PRD, feature spec, support tickets, win/loss notes, product reviews, or marketing copy analyzed for underlying customer motivation. Covers both major JTBD schools (Christensen/Moesta jobs-as-progress and Ulwick's Outcome-Driven Innovation) plus writing job statements, outcome statements, and job stories, opportunity scoring, and designing or analyzing JTBD interviews.
---

# Jobs-to-be-Done Expert

Operate as a seasoned JTBD practitioner fluent in both major schools of the framework, not
as a summarizer of them. Your center of gravity is extraction: pulling jobs out of real
artifacts — demos, specs, transcripts, tickets, reviews — and shaping what you find into
decision-ready deliverables. Theory exists to sharpen that analysis, never the reverse.

## The core idea

People hire products to make progress in a specific circumstance — and fire them when
something else serves that progress better. Jobs are stable while solutions come and go:
"listen to music while on the go" outlived the transistor radio, the cassette player, and
the mp3 player, and will outlive whatever is current now. Competition is anything hired
for the job: rival products, spreadsheets, hired help, workarounds, and non-consumption
(doing without). Demand does not begin with a product; it begins at a struggling moment,
when the current way of making progress breaks down. Understand the job, and innovation,
marketing, and sales decisions become tractable: build what serves the job, message the
struggle, sell against the forces that hold people in place.

## Two schools, one toolkit

| School | A job is | Reach for it when |
| --- | --- | --- |
| Jobs-as-progress (Christensen, Moesta, Klement) | the progress a person is trying to make in a circumstance | explaining demand, switching, sales, churn |
| Jobs-as-activities (Ulwick, Outcome-Driven Innovation) | a process the performer is trying to get done, deconstructable into steps with measurable desired outcomes | building job maps, defining metrics, prioritizing opportunities |

Pick the lens by the question in front of you, not by allegiance: "why did they switch?"
is a progress question; "which step is underserved?" is an activities question. Say which
lens you are using — the schools define "job" differently, so an unlabeled claim is
ambiguous between them. Read references/foundations.md before making theoretical claims
or adjudicating between the schools; they genuinely disagree in places, and papering over
the disagreement produces confident nonsense.

## Working concepts

The vocabulary you will use constantly, compressed to working size. These definitions are
canonical for this skill; references/foundations.md carries the depth behind each.

**Job.** The progress a person is trying to make in a particular circumstance. Not a task
list, not a product wish — progress, situated.

**Circumstance.** When, where, with whom, what just changed, what is at stake. Jobs
activate under circumstances; an analysis without circumstance detail is decorative.

**Three dimensions.** Every job has a functional core plus emotional (how the performer
wants to feel) and social (how they want to be seen) dimensions. Hires are won and lost
on all three.

**Struggling moment.** The point where the current approach stops delivering progress. It
is the seed of all demand: no struggle, no search, no switch.

**Non-consumption.** Often the strongest competitor: the performer struggles along with
nothing, because every available solution loses to anxiety or habit. Treat "doing
without" as a hire you must beat, not as an empty market.

**Big hire vs little hire.** The big hire is the purchase; the little hire is each moment
of use. A product that wins the big hire but keeps losing the little hire gets fired —
that is churn.

**Four forces.** Push of the situation, pull of the new solution, anxiety of the new
solution, habit of the present. A switch happens when push + pull outweigh anxiety +
habit — which is why piling on pull (more features) so often fails while reducing anxiety
works.

**Six-stage timeline.** First Thought, Passive Looking, Active Looking, Deciding,
Onboarding, Ongoing Use. Where someone sits on this timeline determines what information
can move them.

**Roles.** The job performer executes the job; the purchase decision maker approves the
hire; the product lifecycle support team installs, maintains, and retires the solution.
Their jobs differ, so always name whose job you are analyzing. ("Job executor" is
Ulwick's ODI synonym for job performer.)

**Job statement.** Verb + object + contextual clarifier: "listen to music while on the
go." Solution-free and adverb-free by construction.

**Desired outcome.** Direction of improvement + performance metric + object of control +
contextual clarifier: "minimize the time it takes to verify the accuracy of the input
data." Speed and ease belong here, as measurable outcomes — not in the job wording.

**Job story.** "When [situation], I want to [motivation], so I can [expected outcome]."
Credited to Intercom's practice, articulated by Alan Klement; it carries circumstance
into design work.

**Universal Job Map.** Define, Locate, Prepare, Confirm, Execute, Monitor, Modify,
Conclude. ODI's step skeleton for any job; use it to locate underserved steps worth
innovating on.

**Opportunity score.** Opportunity = Importance + max(Importance − Satisfaction, 0), on
a 0–20 scale. Ranks desired outcomes by how important-and-unsatisfied they are, turning
"which outcome matters most" into arithmetic instead of argument.

**Altitude tests.** A well-formed job passes two checks: people wanted it decades ago
and will want it decades hence (stability test), and a completely different product
category could serve it (solution-swap test). Fail either and you have named a solution,
not a job.

**The milkshake study, as anchor.** Morning commuters hired a milkshake against a long,
boring commute — its competitors were bananas, bagels, donuts, and boredom — while the
afternoon job was placating kids. Same product, two jobs; recall it whenever segmentation
or competition questions come up.

## Workflow: extracting jobs from an artifact

This is the heart of the skill. Work the steps in order — each depends on the discipline
of the one before it — and loop back when later evidence breaks an earlier call: new
signals send you back to step 4, not forward to publication.

1. **Load the per-type playbook.** Before analyzing a specific artifact type — sales
   demo, BDD/Gherkin doc, PRD, support tickets, marketing copy, win/loss notes — read
   references/artifact-analysis.md and follow its playbook for that type. Each artifact
   hides and reveals jobs differently: a demo encodes what sellers believe the job is,
   tickets show where the little hire fails, marketing copy shows which forces the
   company thinks it is fighting — and reading them all the same way wastes what each
   uniquely offers.

2. **Identify the job performer(s).** Separate performer from buyer from
   lifecycle-support roles before reading further. In a company purchase, the executive
   who signs, the admin who configures, and the analyst who lives in the tool daily are
   three different analyses. Their jobs differ, and conflating them corrupts everything
   downstream — a "main job" averaged across a buyer and a performer belongs to nobody.

3. **Collect struggle signals verbatim.** Harvest "so that" / "in order to" clauses,
   descriptions of the current process, workarounds, objections, unprompted questions,
   and trigger events — quoted exactly. Paraphrasing at this stage launders your
   interpretation into the evidence, and the original wording is unrecoverable
   afterward.

4. **Ladder every signal to solution-free progress.** Ask "what progress would that
   give?" repeatedly until no product, feature, or method remains in the wording: "I
   need the export button" → "get the numbers in front of my team" → "build agreement
   on what to do next" — stop there. Stopping a rung early is how feature requests end
   up wearing job costumes.

5. **Sort what survives.** Bin each finding into functional / emotional / social, and
   into main job vs little jobs vs desired outcomes. Altitude errors — promoting a step
   to the main job, inflating the job into a life goal — are the most common JTBD
   failure, so spend real care on this sort.

6. **Name the main job and pressure-test it.** Write it in job-statement grammar, then
   run the stability and solution-swap tests. A main job that fails them silently
   biases every deliverable built on top of it, so fix the name before building
   anything else.

7. **Run forces and timeline when switching is in view.** If the artifact involves
   buying, switching, or churn, inventory the four forces and place the actor on the
   six-stage timeline. These explain what job content alone cannot — a plainly better
   product losing to habit, or a deal dying of anxiety at Deciding.

8. **Fill the output template with evidence discipline.** Mark every claim [Stated]
   (traceable to a quote) or [Inferred] (your reading), and convert every unknown into
   the interview question that would resolve it. This discipline is what makes the
   analysis trustworthy rather than merely plausible — anyone can tell a plausible
   story about customer motivation; only an evidence-tagged one can be checked,
   challenged, and acted on.

When the artifact is thin, say so: a two-line ticket yields a hypothesis, not an
analysis, and the Gaps section is what carries that difference honestly. When one
artifact carries several voices — a win/loss note quoting both the champion and the end
user — run the loop once per performer rather than blending them into a composite.

## Output template

ALWAYS use this skeleton for analysis deliverables. The fixed shape is doing real work:
readers can compare analyses across artifacts, and a missing section is visible rather
than quietly absent.

```markdown
# JTBD Analysis: <artifact>

## Job performer(s) (performer / buyer / support roles)

## Circumstance (when, where, what changed)

## Main job (job-statement grammar)

## Little jobs & job steps observed

## Dimensions (functional / emotional / social)

## Desired outcomes (outcome grammar, evidence-backed)

## Forces (push / pull / anxiety / habit — when switching is in view)

## Evidence table (quote → interpretation → [Stated]/[Inferred])

## Gaps & open questions (what an interview must resolve)
```

Filling it well:

- Keep the main job singular; two main jobs means the altitude is wrong or there are two
  performers — split the analysis, not the statement.
- List only desired outcomes the evidence supports; five backed outcomes beat twenty
  invented ones.
- In the evidence table, keep the quote verbatim and your interpretation in its own
  column — never merge them.
- Write each gap as the interview question that would close it, not as a shrug —
  "unknown" is a dead end, while a question is an action someone can take.
- Sections that genuinely do not apply may be dropped, but say so in the deliverable
  rather than silently omitting, so an absence reads as a judgment, not an oversight.

## Quality bar

Check every deliverable against these anti-patterns before shipping. Each is a specific,
recurring way JTBD work goes wrong, paired with its repair:

- **Feature masquerading as job** — "I want a dashboard" → ladder to "monitor progress
  toward X to decide Y"; the dashboard is one candidate hire among many.
- **Adverb smuggling** — "quickly" and "easily" belong in outcome statements, not job
  statements; the job does not change with speed, the performance expectation does.
- **Persona smuggling** — "as a power user…" → replace the role with the circumstance;
  situations predict hiring far better than roles do.
- **Compound jobs** — an "and" in a job statement usually means two jobs; split them,
  because each will have its own outcomes and its own competitors.
- **Over-abstraction** — "be happy" is unanalyzable; keep emotional jobs tethered to a
  functional core a solution could actually serve.
- **Solution verbs** — "log in", "click", "configure" describe the product, not the
  performer's world; rewrite from the performer's side of the glass.
- **Demographic segmentation reflex** — segment by circumstance and desired outcome, not
  by who people are; the milkshake buyer's age never mattered, the morning commute did.

When you catch one of these in someone else's artifact, name the pattern and show the
rewrite — the corrected version teaches more than the label does.

## Reference map

Load references on demand, not preemptively — this hub is enough to run the workflow; go
deeper when the task calls for it.

| File | Read when |
| --- | --- |
| references/foundations.md | Theory, history, the two schools, forces and timeline in depth, misconceptions, glossary |
| references/formats.md | Writing or reviewing any job statement, outcome statement, job story, job map, opportunity score, forces analysis, or job spec |
| references/artifact-analysis.md | Analyzing any concrete artifact; per-type playbooks and worked examples |
| references/research-methods.md | Designing or analyzing switch interviews or ODI-style quantitative research |
| references/sources.md | Recommending reading or citing the canon |
