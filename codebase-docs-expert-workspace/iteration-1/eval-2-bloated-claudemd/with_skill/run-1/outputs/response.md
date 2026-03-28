# CLAUDE.md Audit: What's Wrong and How to Fix It

## The Core Problem: Bloat

Your CLAUDE.md has 21 lines of rules, many of which are things Claude already knows or which belong in other files. When a CLAUDE.md is filled with rules Claude doesn't need, two things happen:

1. The useful rules get diluted — Claude treats everything with equal weight, so "Never use System.out.println" competes with "Write clean, readable code" even though one is actionable and the other is noise.
2. The file is long relative to its signal density. Rules buried in a longer-than-necessary file are followed less reliably.

The target is under 150 lines for most projects. Your file is short in raw line count, but almost every line is a candidate for deletion.

---

## Line-by-Line Audit

Apply this test to each rule: *"Would Claude make a specific, demonstrable mistake if I deleted this line?"*

### Delete these — Claude already knows them

| Rule | Why to delete |
|------|--------------|
| "Write clean, readable code" | Generic platitude. Claude already aims for this. |
| "Follow SOLID principles" | Standard OOP guidance Claude applies by default in Java. |
| "Use dependency injection" | Standard Spring Boot convention — Claude won't do otherwise in a Spring context. |
| "Use meaningful variable names" | Implied by "write clean code" which was itself already noise. |
| "Tests should follow AAA pattern" | Standard JUnit/testing convention Claude already follows. |
| "Use Optional to avoid null pointer exceptions" | Standard modern Java practice Claude knows. |

### Delete these — too vague to enforce, or Claude gets it right without them

| Rule | Why to delete |
|------|--------------|
| "All service methods should be transactional" | Overly broad (not all service methods warrant `@Transactional`). Claude will apply this appropriately in context. If you have a specific constraint (e.g., all write methods must be transactional), state that precisely instead. |

### Rewrite these — actionable but poorly phrased

| Rule | Problem | Fix |
|------|---------|-----|
| "Never use System.out.println, use SLF4J logger instead" | Good intent, but the "rules without alternatives" smell means the positive form is better. | Rephrase: "Use SLF4J (`private static final Logger log = LoggerFactory.getLogger(...)`) for all logging. Never use `System.out.println`." |
| "All REST endpoints must be documented with Swagger annotations" | True, but what annotations? Vague rules get inconsistent compliance. | Rephrase: "All REST endpoints require `@Operation`, `@ApiResponse`, and `@Parameter` Swagger annotations." |
| "Database queries must use JPA repositories, not native SQL" | Good non-obvious rule. | Keep, but phrase as a positive: "Use JPA repositories for all database access. Native SQL (`@Query(nativeQuery=true)`) is prohibited." |
| "Exception handling should use @ControllerAdvice" | "Should" is weak. | Rephrase: "All exception handling belongs in `@ControllerAdvice` classes. Do not use try/catch for HTTP error responses in controllers." |
| "Never hardcode configuration values, use application.properties" | Good rule. | Add the positive: "All configuration values must come from `application.properties` or environment variables. Never hardcode." |
| "Integration tests require a running PostgreSQL instance on port 5432" | This is a useful prerequisite. | Keep — this is exactly the kind of non-obvious, project-specific thing Claude needs. Rephrase as a warning: "Integration tests (`*IT.java`) require a local PostgreSQL instance on port 5432. Do not attempt to mock the database in integration tests." |

### Move these — they belong in commands, not rules

The build/test/run lines are good content — they're just mixed in with the rules list instead of being in a dedicated commands section.

---

## Revised CLAUDE.md

```markdown
# Project

Java 17 Spring Boot microservices. Main application class: `com.example.app`.
Frontend is in a separate repository.
Database migrations managed by Flyway.
CI: `.github/workflows/ci.yml` (GitHub Actions).

## Commands

- Build: `mvn clean package`
- Test: `mvn test`
- Run: `mvn spring-boot:run`

## Stack

- Java 17, Spring Boot
- JPA / Hibernate for data access
- Flyway for database migrations
- Swagger/OpenAPI for API documentation
- SLF4J for logging

## Conventions

- Use SLF4J (`private static final Logger log = LoggerFactory.getLogger(...)`) for all logging. Never use `System.out.println`.
- All REST endpoints require `@Operation`, `@ApiResponse`, and `@Parameter` Swagger annotations.
- Use JPA repositories for all database access. Native SQL (`@Query(nativeQuery=true)`) is prohibited.
- All exception handling belongs in `@ControllerAdvice` classes. Do not handle HTTP errors with try/catch in controllers.
- All configuration values must come from `application.properties` or environment variables. Never hardcode.

## Integration Tests

`*IT.java` tests require a local PostgreSQL instance on port 5432. Do not mock the database in integration tests.
```

This is 28 lines. Every line passes the audit test. The rules Claude already follows (clean code, SOLID, AAA, meaningful names) have been removed. The commands are grouped where Claude expects them. The non-obvious constraints (no native SQL, no try/catch in controllers, PostgreSQL for integration tests) are kept and phrased clearly.

---

## Why This Works Better

**Signal density**: Every line is actionable. Claude won't spend context budget "following" a rule that says "write readable code."

**Positive alternatives**: "Use SLF4J" gives Claude something to do. "Never use System.out.println" alone just flags something to avoid.

**Commands are prominent**: Claude looks for commands near the top. Burying `mvn spring-boot:run` in a flat list of 21 rules meant it had equal weight with "use meaningful variable names."

**Non-obvious rules are kept**: The PostgreSQL integration test requirement, the prohibition on native SQL, and the @ControllerAdvice mandate are all project-specific decisions that Claude would not infer. These are the rules worth keeping.

---

## One More Recommendation

If you have architecture context (what each service does, how they relate, which are write-heavy vs. read-heavy), add a brief `## Architecture` section or create an `ARCHITECTURE.md` and reference it with `@docs/ARCHITECTURE.md`. Claude generates much better code when it understands the intended structure — and without that context, it will invent its own.
