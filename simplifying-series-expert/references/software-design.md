# Simplifying Software Design — The Genius of Bureaucracies

Cockburn's *Simplifying Software Design: The Genius of Bureaucracies, or How Not-My-Job Sharpens Your Design* (The Simplifying Series, Preview/Amazon Edition, 2026). Load this when the task is about *where code belongs*, how to divide responsibilities among modules/objects, reducing dependencies, or evaluating/improving a design's structure. For slicing work into increments see `slicing-techniques.md`; for requirements see `requirements-foundation.md`.

> Note: this is the **Preview edition** (~188 pp); the public description is detailed but the exact chapter list and the precise "six design tests" are not published online. Treat the specifics below as Cockburn's documented method (responsibility-driven design) organized to the book's stated content; defer to the user's copy for exact wording and the exact six tests.

## Contents
- The central question
- The bureaucracy metaphor
- Two instincts as design tools
- Responsibility-driven design (the lineage)
- The core techniques
- Six design tests
- Communication patterns that signal trouble
- Applying it to architectures (MVC, hexagonal)
- Why it matters in the AI era

## The Central Question
Software design comes down to one recurring question: **"Where do I put this line of code?"** Cockburn's claim is that the answer lies *not in frameworks or patterns* but in how you assign **responsibility** — and the best model for assigning responsibility is a surprising one: a **bureaucracy**.

## The Bureaucracy Metaphor
Bureaucracies are easy to mock, but they are very good at exactly what software needs:
- **Clear responsibilities** — every office knows what it is accountable for.
- **Limited knowledge boundaries** — each office knows only what it needs to do its job.
- **Disciplined communication** — requests flow through defined channels between roles.

Design your software the way you would design a good bureaucracy: give each module/object a clear job, tell it only what it needs to know, and route interactions through clean channels. The result: you can decide where code belongs, reduce unnecessary dependencies, and keep the system understandable as it grows.

Cockburn calls this **the most powerful single metaphor for designing software systems**: the resulting designs are *relatively simple, clean, and defensible*, and the technique **works at every scale — from macro systems down to individual objects.** (Source: his LinkedIn writing; see `SKILL.md` → Primary Sources.)

## Two Instincts as Design Tools
The book turns two everyday human instincts into design heuristics:

- **"Not my job"** — keep responsibilities *sharply defined.* When code doesn't belong to this module's job, it shouldn't live here — push it to whoever is responsible. This is the test for *where a line of code goes*: it goes with the object whose job it is. Pull the line toward the data/knowledge it needs.
- **"No need to know"** — *limit how much each component must understand.* Tell a module only what it needs; hide everything else (information hiding / least knowledge). Fewer things known = fewer dependencies = less ripple when things change.

Together they push toward high cohesion (each part does one job) and low coupling (each part knows little about the others).

## Responsibility-Driven Design (the lineage)
The book is a practical, simplified **starter kit** for **responsibility-driven design (RDD)**, pioneered by **Ward Cunningham, Kent Beck** (CRC cards — Class / Responsibility / Collaborators) and **Rebecca Wirfs-Brock** (RDD, role stereotypes). The reframe: don't start from data structures or class hierarchies — start by asking *what each part is responsible for* and *who it must collaborate with* to fulfill that responsibility. Simple enough for newcomers, powerful enough for experienced architects.

## The Core Techniques
- **Responsibility statements** — write, in a sentence, what each module/object is responsible for. If you can't state it crisply, the design is unclear. This is the unit you reason about.
- **Scenario-based evaluation** — walk concrete scenarios through the design ("when X happens, who does what?"). Scenarios expose missing responsibilities, misplaced code, and awkward collaborations before you build.
- **Interaction diagrams** — trace who-asks-whom as a scenario plays out. The *shape* of the interactions reveals the health of the design (see trouble patterns, below).

## Six Design Tests
The book teaches **six practical design tests** for evaluating a design. The public description names that there are six but does not list them; verify the exact six against the user's copy. In spirit (RDD), they probe questions such as: Does each object have a single, statable responsibility? Does each know only what it needs ("no need to know")? Is each line of code with the responsibility that owns it ("not my job")? Are collaborations few and clean? Does a scenario flow without awkward back-and-forth? Does the design stay understandable as it grows? *(Treat this as the kind of thing the tests check, not the verbatim list.)*

## Communication Patterns That Signal Trouble
Because design health shows up in *how components talk*, learn to recognize interaction smells, e.g.: an object reaching deep into another's internals (violates "no need to know"); chatty back-and-forth to get one thing done; a "god" office that everything must consult; or a line of code sitting far from the data it needs (violates "not my job"). These patterns in an interaction diagram are the cue to move responsibilities.

## Applying It to Architectures
Responsibility thinking explains popular architectures:
- **MVC** — Model, View, Controller are an assignment of responsibilities (data/rules vs presentation vs coordination) with "no need to know" between them.
- **Hexagonal architecture (Ports & Adapters)** — Cockburn's own pattern: the domain's job is business logic; it has "no need to know" about databases, UIs, or external systems, which sit behind ports/adapters. The hexagon *is* the bureaucracy principle applied at the architecture scale. (For depth, this is the subject of his separate *Hexagonal Architecture Explained*.)

Use the same responsibility/knowledge/communication lens to judge any architecture, not just these.

## Why It Matters in the AI Era
Even when AI generates large amounts of code quickly, systems still need **clear boundaries** so that teams — and the tools they use — don't overwrite each other's work. Well-assigned responsibilities and "no need to know" boundaries are what let humans and AI agents work on a system in parallel without stepping on each other. Designing those boundaries is exactly what this book teaches.
