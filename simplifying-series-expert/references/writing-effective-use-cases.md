# Writing Effective Use Cases (Cockburn, 2001)

Alistair Cockburn, *Writing Effective Use Cases* (Addison-Wesley, 2001) — the classic, comprehensive, award-winning reference on use cases. Load this when the user needs the **full depth** on use cases: the complete template, scope vs goal levels, stakeholders-and-interests, formats, scaling to many use cases, or the reminders/mistakes. For the short modern version, see `use-cases-minibook.md` (Book 4); for use cases among stories/maps, see `requirements-techniques.md`.

> Not part of the Simplifying Series (it's from the Crystal / Agile Software Development Series) — it's the **foundational reference** the Simplifying-Series use-case books distill and modernize. The TOC below is the actual published table of contents; the surrounding explanations are Cockburn's documented method.

## Contents
- How it relates to the newer books
- The two models
- Table of contents (the real structure)
- Scope: functional vs design
- The three named goal levels (cloud/kite/sea/fish/clam)
- The use case template (body parts)
- Scenarios, steps, and the four-part action
- Extensions
- Use case formats
- The 12-step writing process
- Reminders & common mistakes

## How It Relates to the Newer Books
- **vs *The Mini-Book on Use Cases* (Book 4):** WEUC is the deep, theory-rich treatment; the Mini-Book is the 82-page, example-first version and adds *slicing for incremental delivery* (not in WEUC).
- **vs *Unifying...* (Book 2):** WEUC covers use cases standalone and in full; Book 2 places them among user stories and story maps.
- **vs *Hexagonal Architecture* (companion):** use cases describe behavior at the system boundary (the driving ports); WEUC defines that behavior, hexagonal implements it.

## The Two Models
- **Actors & Goals** (Cockburn, 1994): a use case is a primary **actor** pursuing a **goal** against a system; the goal succeeds or fails. Goals nest, giving levels.
- **Stakeholders & Interests** (new in this book): a use case is a **contract for behavior** — the system, serving the primary actor's goal, also protects the **interests of offstage stakeholders**. The main scenario delivers the goal; the extensions and guarantees protect every stakeholder's interests. This model is *why* you brainstorm extensions: to find where an interest could be violated.

## Table of Contents (the real structure)
**Chapter 1 — Introduction** (What is a use case; Your use case is not my use case; Requirements and use cases; When use cases add value; Manage your energy; Warm up with a usage narrative)

**Part 1 — The Use Case Body Parts**
- 2. The Use Case as a Contract for Behavior
- 3. Scope
- 4. Stakeholders and Actors
- 5. Three Named Goal Levels
- 6. Preconditions, Triggers, and Guarantees
- 7. Scenarios and Steps
- 8. Extensions
- 9. Technology and Data Variations
- 10. Linking Use Cases
- 11. Use Case Formats

**Part 2 — Frequently Discussed Topics**
- 12. When Are We Done?
- 13. Scaling Up to Many Use Cases
- 14. CRUD and Parameterized Use Cases
- 15. Business Process Modeling
- 16. The Missing Requirements
- 17. Use Cases in the Overall Process
- 18. Use Case Briefs and Extreme Programming
- 19. Mistakes Fixed

**Part 3 — Reminders for the Busy**
- 20. Reminders for Each Use Case
- 21. Reminders for the Use Case Set
- 22. Reminders for Working on the Use Cases

**Appendices:** A. Use Cases in UML · B. Answers to (Some) Exercises · C. Glossary · D. Readings

## Scope: Functional vs Design (two different dials)
- **Functional scope** — *what behavior* is in vs out (the list of services/use cases the system provides). Captured with an in/out list.
- **Design scope** — *how big a box* the use case describes: enterprise/organization, whole system, or a component/subsystem. Cockburn draws this with icons. The **System under Discussion (SuD)** is the box you're writing about; the **outermost use cases** are at the chosen design-scope boundary.
- Don't confuse design scope (size of the box) with goal level (altitude of the goal).

## The Three Named Goal Levels (cloud/kite/sea/fish/clam)
Goals nest by altitude; the book names three levels across five icons:
- **Summary level** — **Cloud** (very high / strategic) and **Kite** (high / business) — *white*.
- **User-goal level** — **Sea level** (blue) — one primary actor completing one goal in one sitting. **The anchor level**; write most use cases here.
- **Subfunction level** — **Fish** (underwater) and **Clam** (lowest) — *indigo/black* — sub-steps that support user goals.
Find the right level by asking "would the actor be satisfied to stop here?" (sea) vs "why?" (up) / "how?" (down). Raise/lower a goal by asking those questions.

## The Use Case Template (body parts)
A "fully dressed" use case collects: **Use case name** (an active-verb goal phrase) · **Scope** (the SuD) · **Level** (the goal level) · **Primary actor** · **Stakeholders and interests** · **Preconditions** (what's guaranteed true before) · **Triggers** (what starts it) · **Minimal guarantee** (protected even on failure) · **Success guarantee** (true after success) · **Main success scenario** · **Extensions** · **Technology & data variations**. (Lighter formats drop fields — see Formats.)

## Scenarios, Steps, and the Four-Part Action
- The **main success scenario (MSS)**: the steps when everything goes right and all stakeholder interests are met. Numbered, each step a simple statement of *who does what*, showing forward progress (the "ever-unfolding story").
- A full interaction **step (transaction) has four parts**: (1) the actor sends a request + data, (2) the system validates it, (3) the system alters its internal state, (4) the system responds to the actor. Write at intent level, technology-free.

## Extensions
- An extension = a **condition** (something that can happen at a step, including failures and alternatives) + its **handling steps**.
- Numbered to the MSS step where the condition is detected, with letter suffixes for different conditions at the same step (e.g., `3a`, `3b`).
- **Brainstorm and exhaustively list** extension conditions first, then rationalize the list, then write handling. Extensions are where most real requirements (and stakeholder-interest protections) are discovered.
- Complex handling can be extracted to a sub use case or an extension use case.

## Use Case Formats
A spectrum of formality you choose by need: **fully dressed** (all fields) → **casual** (a few paragraphs) → **one-column / two-column** layouts → **brief** (one paragraph / a couple sentences). The book gives **standards for five project types** and discusses the **forces** (team size, criticality, traceability) that push you toward more or less ceremony. "A use case need not be best to be useful."

## The 12-Step Writing Process
Cockburn's working order (from the book's one-page summary; anchors confirmed from the text):
1. Name the system **scope and boundaries**.
2. Brainstorm and list the **primary actors**.
3. Brainstorm and exhaustively list **user goals** (the outermost use cases).
4–6. Capture the **summary** use cases, revise the set, then **pick one** to expand.
7. Capture **stakeholders and interests, preconditions and guarantees**.
8. Write the **main success scenario**.
9. **Brainstorm and exhaustively list the extension conditions.**
10. Write the **extension-handling steps**.
11. Extract complex flows to **sub use cases**; merge trivial ones.
12. **Readjust the set** (add, subtract, merge); check readability, completeness, and that stakeholder interests are met.

## Reminders & Common Mistakes
- **Reminders for each use case:** it's a prose essay — make it easy to read; one sentence form per step; get the goal level right; show who has the ball (who acts each step); use "include" for sub use cases.
- **Common mistakes (Ch. 19 "Mistakes Fixed"):** no primary actor; too many UI/technology details; goal level too low; purpose and content not aligned; writing the system's internals instead of the actor's intent.
- **Manage your energy / diminishing returns:** write only as much use case as the situation needs — mediocre-but-readable beats elaborate-but-unread.
