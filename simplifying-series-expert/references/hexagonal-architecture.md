# Hexagonal Architecture Explained (Ports & Adapters)

Cockburn & Juan Manuel Garrido de Paz, *Hexagonal Architecture Explained: How the Ports & Adapters Architecture Simplifies Your Life, and How to Implement It* (Updated 1st Ed., 2025, ~196 pp). Load this when the task is about **hexagonal / ports & adapters architecture** — isolating business logic from technology, wiring adapters, testing through ports, or comparing to Clean/Onion/layered.

> Companion book, **not part of the Simplifying Series.** It is Cockburn's authoritative treatment of the pattern he invented, and it is the deep dive behind Book 3's (*Simplifying Software Design*) use of hexagonal architecture. Cockburn co-authored it with Garrido de Paz; it's part FAQ/collected-articles, so it reads more as a reference than a linear narrative.

## Contents
- The problem it solves
- The pattern: core, ports, adapters
- Driving vs driven sides
- Naming ports ("for …")
- The configurator (wiring it up)
- The dependency machinery (DIP, DI, lookup, IoC)
- Testing strategy
- Benefits
- Relationship to DDD
- Vs Clean / Onion / layered
- History
- Common mistakes
- Relationship to the other books

## The Problem It Solves
Business logic gets entangled with UI, frameworks, and databases until you "can't tell what the code does regarding business logic." Hexagonal architecture **decouples the business logic from the technologies** around it, so the app is testable, resistant to **business-logic leakage**, and able to swap technologies over a long-lived system. Recommended/used at scale (Netflix, Amazon) and a natural fit for Domain-Driven Design.

## The Pattern: Core, Ports, Adapters
- **The app (core / inside the hexagon)** — pure business logic. It knows nothing about who calls it or what it calls; it talks only through ports.
- **Ports** — the *interfaces* (conversations) at the boundary of the app. A port is a technology-free contract: what the app offers, or what the app needs.
- **Adapters** — code that *converts* between an external technology and a port. One port can have many adapters (real DB adapter, in-memory test adapter, REST adapter, CLI adapter…).
- **The hexagon shape is arbitrary** — it's drawn as a hexagon only to leave room for several ports on different faces. It is **not** "six of anything." (Common misunderstanding.)

## Driving vs Driven Sides
The boundary is split into two asymmetric sides:
- **Driving (primary / left) side** — actors that *drive* the app: users, UIs, tests, other systems calling in. They use **driving ports** (the app's offered API). Adapters here translate an external trigger into a call on a driving port.
- **Driven (secondary / right) side** — actors the app *drives*: databases, message buses, external services, the clock. The app declares **driven ports** (interfaces it needs); adapters implement them against real technology.

Key consequence: dependencies point **inward**. The app defines the driven-port interfaces; the adapters depend on the app, never the reverse.

## Naming Ports ("for …")
Garrido de Paz's convention: name ports by intent, **"for &lt;doing something&gt;"** — e.g., a driving port `for placing orders`, a driven port `for storing orders` / `for sending notifications`. This keeps ports about *purpose*, not the technology behind them.

## The Configurator (wiring it up)
Something has to choose which concrete adapters plug into which ports and assemble the running app — Cockburn calls this the **configurator** (the assembler/composition root). It instantiates adapters and injects them into the app at startup. Because the app depends only on port interfaces, the configurator is the *only* place that knows the concrete technologies — swap an adapter there (real DB ↔ in-memory) without touching business logic.

## The Dependency Machinery
The book explains the mechanisms that make inward-pointing dependencies work, and distinguishes them:
- **Dependency Inversion Principle (DIP)** — depend on abstractions (ports), not concretions (adapters). This is *why* the pattern works.
- **Dependency Injection (DI)** — adapters are *handed to* the app (by the configurator), not created by it.
- **Dependency Lookup** — alternatively the app asks a registry for an implementation (contrast with injection).
- **Inversion of Control (IoC)** — the general principle; DI and lookup are two ways to achieve it.

## Testing Strategy
The payoff most teams feel first: **test the app in isolation.** Drive the app through its driving ports in tests, and replace driven adapters with **test doubles / in-memory adapters**. You can run the entire business logic with no database, network, or UI — fast, deterministic tests. Adapters are tested separately against their technology.

## Benefits
Simplified testing; protection from business-logic leakage into UI/DB; ability to change technologies in long-running systems; clean home for Domain-Driven Design; symmetric handling of all external actors (a UI and a test are *both* just driving adapters).

## Relationship to DDD
The hexagon's interior is exactly where a DDD **domain model** lives, insulated from infrastructure. The book includes detailed discussion of how Ports & Adapters and DDD fit (the domain/application layers map to the app core; repositories are driven ports).

## Vs Clean / Onion / Layered
Hexagonal predates and overlaps Clean Architecture and Onion Architecture — all share "dependencies point inward, isolate the domain." The book clarifies what is genuinely Ports & Adapters vs ideas "mixed in by people blogging on the topic," and how it differs from traditional horizontal layering (where the UI→logic→DB stack still couples logic to the DB direction).

## History
Cockburn devised the pattern (~2005) to stop UI and database concerns from leaking into business logic, first calling it **Hexagonal Architecture**, then renaming it **Ports & Adapters** to name what actually matters (the symmetry and the interfaces) rather than the drawing. The book collects and corrects the original articles plus FAQs.

## Common Mistakes
- Thinking the hexagon means **six** ports/sides — it's just a drawing.
- Putting **adapter or framework code inside the app** (logic leakage) — the thing the pattern exists to prevent.
- Making the **app depend on an adapter** instead of defining a driven **port** the adapter implements.
- Treating it as **horizontal layers**; it's inside/outside with two driving/driven sides, not top/bottom.
- Skipping the **configurator** and `new`-ing concrete adapters inside business logic.
- Over-porting: a port for every class. Ports belong at the *technology boundary*, not between internal objects.

## Relationship to the Other Books
- **Book 3 (Simplifying Software Design):** hexagonal architecture *is* the bureaucracy principle at architecture scale — the app core has **"no need to know"** about databases, UIs, or external systems, and each adapter has a sharply defined **"not my job."** Use the responsibility lens from Book 3 to decide what belongs in the core vs an adapter.
- **Books 1/2/4:** use cases describe the behavior the app offers through its **driving ports**; slicing a use case yields thin paths you can build and test straight through the hexagon (a walking skeleton = one thin driving-port→core→driven-port path).
