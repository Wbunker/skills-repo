# What's Wrong With This CLAUDE.md and How to Fix It

## The Core Problem: Mixing Multiple Concerns Into One Flat List

Claude reads CLAUDE.md into its context window and uses it to guide behavior. When a file is a long, undifferentiated list of rules, Claude struggles to apply them consistently because:

1. **No hierarchy or prioritization** — all rules look equally important, so Claude may deprioritize any of them
2. **Mixed categories without structure** — coding standards, architectural decisions, testing patterns, infrastructure facts, and build commands are all jumbled together
3. **Too many rules to track at once** — 21 separate bullet points creates cognitive load, and some will be dropped or underweighted
4. **No context for when rules apply** — rules like "all service methods should be transactional" lack enough context for Claude to know when to apply them correctly
5. **Passive/informational content mixed with behavioral instructions** — facts like "Frontend is in a separate repo" don't require any behavior from Claude but take up rule-budget alongside things that do

---

## Specific Issues

### Problem 1: Flat list, no structure
A flat bullet list gives Claude no way to distinguish "always do this" from "this is background info." Claude will treat "Frontend is in a separate repo" the same weight as "Never use System.out.println."

### Problem 2: Behavioral rules mixed with facts
Entries like these are not instructions — they are facts:
- "Integration tests require a running PostgreSQL instance on port 5432"
- "Frontend is in a separate repo"
- "CI runs on GitHub Actions, see .github/workflows/ci.yml"
- "The main application class is in com.example.app"
- "We use Flyway for database migrations"

Facts belong in a separate section so Claude can reference them without confusing them for behavioral constraints.

### Problem 3: Build commands buried in the rules list
Build/run/test commands are reference information, not rules. Burying them among coding standards means Claude may skip them when you ask a build-related question, or over-apply them when you don't need them.

### Problem 4: Overly broad rules without examples or clarification
"Follow SOLID principles" and "Write clean, readable code" are too vague to be actionable. Claude already tries to do these things; stating them adds noise without adding signal. If you have a specific interpretation (e.g., "always extract business logic into a separate Service class, never in the Controller"), say that explicitly.

### Problem 5: Some rules conflict with nuance in practice
"Database queries must use JPA repositories, not native SQL" is a strong constraint that will cause Claude to avoid native queries even in legitimate cases (e.g., complex aggregations where JPA is impractical). This kind of absolute rule should be stated as a strong preference with an escape hatch: "Prefer JPA repositories; only use native SQL when JPA cannot express the query, and add a comment explaining why."

### Problem 6: No indication of what Claude should do by default vs. ask about
Rules like "All REST endpoints must be documented with Swagger annotations" — should Claude add these when generating new endpoints? When reviewing existing code? When asked to write a method? The trigger is unspecified.

---

## How to Fix It

### Step 1: Separate into clearly labeled sections

```markdown
# CLAUDE.md

## Project Overview
Java 17 Spring Boot microservices application.
Main application class: `com.example.app`
Database migrations: Flyway
Frontend: separate repository (not in this repo)
CI: GitHub Actions — see `.github/workflows/ci.yml`

## Build & Run
- Build: `mvn clean package`
- Test: `mvn test`
- Run: `mvn spring-boot:run`
- Integration tests require PostgreSQL on localhost:5432

## Code Standards (apply when writing or modifying code)
- Use SLF4J for logging — never `System.out.println`
- Use `Optional<T>` instead of returning or accepting null
- Use meaningful variable and method names
- Never hardcode configuration values — use `application.properties` or `@Value`
- Exception handling: use `@ControllerAdvice` for REST error responses

## Architecture Rules (apply when generating new classes or endpoints)
- All REST endpoints must include Swagger/OpenAPI annotations (`@Operation`, `@ApiResponse`, etc.)
- Data access must go through JPA repositories; avoid native SQL unless JPA cannot express the query (add a comment if you use native SQL)
- All service-layer methods that write to the database must be `@Transactional`
- Use constructor injection (not field injection) for dependencies

## Testing Standards (apply when writing tests)
- Follow AAA pattern: Arrange, Act, Assert — add comments labeling each section
- Unit tests mock all external dependencies
- Integration tests use the real PostgreSQL instance (see above)
```

### Step 2: Remove noise rules

Remove rules that are either too vague to act on or that Claude already follows by default:
- "Write clean, readable code" — too vague
- "Follow SOLID principles" — too vague; replace with specific structural rules if you have them
- "Use dependency injection" — already covered by "use constructor injection"

### Step 3: Add specificity where it matters most

For rules you most often see violated, add a brief concrete example or anti-pattern. For example:

```markdown
- Use SLF4J for logging — never `System.out.println`
  - Correct: `log.info("Processing order {}", orderId);`
  - Wrong: `System.out.println("Processing order " + orderId);`
```

### Step 4: Keep the file short

A CLAUDE.md that fits in roughly 50-80 lines is far more likely to be followed completely than one with 150+ lines. Every line you add reduces the reliability of the lines already there. If you have extensive project documentation, link to it rather than inlining it.

---

## Summary of Changes

| Issue | Fix |
|-------|-----|
| Flat undifferentiated list | Organize into labeled sections by category |
| Facts mixed with rules | Move facts to an "Overview" section |
| Build commands buried in rules | Give build commands their own section |
| Vague rules (SOLID, clean code) | Remove or replace with specific structural rules |
| Absolute rules with no escape hatch | Soften to strong preferences where appropriate |
| No trigger context for rules | Label sections with "apply when..." |
| Too long overall | Trim noise; link to external docs for detail |
