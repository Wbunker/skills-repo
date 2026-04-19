---
name: jpa2-expert
description: JPA 2 / Jakarta Persistence expertise covering entity mapping, relationships, inheritance, JPQL, Criteria API, advanced O-R mapping, locking, caching, lifecycle callbacks, stored procedures, XML overrides, packaging, and testing. Use when designing entity models, writing JPQL/Criteria queries, configuring persistence.xml, tuning L2 caching, implementing optimistic/pessimistic locking, or testing JPA outside a container. Based on "Pro JPA 2 in Java EE 8" by Mike Keith (Apress).
---

# JPA 2 / Jakarta Persistence Expert

Based on "Pro JPA 2 in Java EE 8" by Mike Keith (Apress, 2018).

**Key versions:** JPA 2.2 (Java EE 8), Jakarta Persistence 3.1 (Jakarta EE 10) — API is backward-compatible; package rename `javax.persistence` → `jakarta.persistence` in Jakarta EE 9+.

## JPA Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                     JPA ARCHITECTURE                              │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  APPLICATION LAYER                                        │    │
│  │  @Entity classes  ·  Domain model  ·  DTO / projections  │    │
│  └───────────────────────────┬──────────────────────────────┘    │
│                               │                                   │
│  ┌────────────────────────────▼───────────────────────────────┐  │
│  │  JPA PROVIDER (e.g., Hibernate, EclipseLink, OpenJPA)      │  │
│  │                                                             │  │
│  │  EntityManagerFactory  ──►  EntityManager (per tx/request) │  │
│  │  PersistenceContext (1st-level cache / identity map)        │  │
│  │  2nd-level cache (shared, optional)                         │  │
│  │  JPQL/Criteria compiler  ──►  SQL generator                 │  │
│  └────────────────────────────┬───────────────────────────────┘  │
│                               │                                   │
│  ┌────────────────────────────▼───────────────────────────────┐  │
│  │  JDBC / DataSource                                          │  │
│  │  persistence.xml  ·  orm.xml  ·  JNDI DataSource           │  │
│  └────────────────────────────┬───────────────────────────────┘  │
│                               │                                   │
│  ┌────────────────────────────▼───────────────────────────────┐  │
│  │  RELATIONAL DATABASE                                        │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

## Quick Reference

| Task | Reference |
|------|-----------|
| JPA overview, persistence.xml, EntityManager, entity lifecycle, Java SE vs EE | [foundations.md](references/foundations.md) |
| @Entity, @Id, @Column, generators, @Basic, @Lob, @Temporal, collection/map mapping | [orm-basics.md](references/orm-basics.md) |
| Relationships, cascade, fetch, inheritance strategies, @Embedded/@Embeddable | [relationships.md](references/relationships.md) |
| JPQL SELECT/JOIN/aggregate/bulk, named queries, Criteria API, native SQL | [querying.md](references/querying.md) |
| Compound keys, locking (optimistic/pessimistic), L2 cache, lifecycle callbacks, stored procs | [advanced-mapping.md](references/advanced-mapping.md) |
| orm.xml overrides, persistence.xml deep dive, packaging, container/SE deploy, testing | [xml-deploy-test.md](references/xml-deploy-test.md) |

## Reference Files

| File | Chapters | Topics |
|------|----------|--------|
| `foundations.md` | 1–3 | JPA history/overview, getting started, enterprise app integration, EntityManager API, persistence context, entity states, transaction boundaries |
| `orm-basics.md` | 4–5 | Basic entity mapping, id generation strategies, field/property access, @Basic/@Lob/@Temporal/@Transient, embeddable value types, collection mapping (@ElementCollection, maps, ordered collections) |
| `relationships.md` | 6–8 | @OneToOne/@OneToMany/@ManyToOne/@ManyToMany, directionality, join columns/tables, cascade, orphanRemoval, fetch (LAZY/EAGER), inheritance (SINGLE_TABLE/TABLE_PER_CLASS/JOINED), @Embedded/@EmbeddedId |
| `querying.md` | 9–10 | JPQL syntax, path expressions, joins, aggregate functions, subqueries, bulk UPDATE/DELETE, named queries, dynamic queries, Criteria API, Metamodel, native SQL, query hints |
| `advanced-mapping.md` | 11–12 | Compound keys (@IdClass/@EmbeddedId), advanced relationships, entity graphs, optimistic locking (@Version), pessimistic locking, L2 caching (@Cacheable), entity listeners, lifecycle callbacks, stored procedures |
| `xml-deploy-test.md` | 13–15 | orm.xml structure, overriding annotations, persistence.xml provider/datasource config, SE vs EE deployment, class transformers, static/dynamic weaving, container-managed vs SE testing, Arquillian, embedded providers |

## Core Decision Trees

### What Mapping Annotation Do I Need?

```
What am I mapping?
├── Single value, maps to one column → @Basic (implicit) or @Column
│   ├── Large text/binary → @Lob
│   ├── Date/time (java.util.Date) → @Temporal(TemporalType.DATE/TIME/TIMESTAMP)
│   └── Not stored → @Transient
├── Primary key
│   ├── Single field → @Id + @GeneratedValue
│   │   ├── DB-auto-increment → strategy=IDENTITY
│   │   ├── DB sequence → strategy=SEQUENCE + @SequenceGenerator
│   │   ├── Portable table-based → strategy=TABLE + @TableGenerator
│   │   └── Provider choice → strategy=AUTO
│   ├── Composite, fields in entity → @IdClass + multiple @Id fields
│   └── Composite, embedded class → @EmbeddedId + @Embeddable class
├── Collection of simple values → @ElementCollection + @CollectionTable
│   ├── Preserve insertion order → @OrderColumn
│   ├── Sort in DB → @OrderBy
│   └── Map with simple key/value → @ElementCollection on Map + @MapKeyColumn
└── Relationship to another entity → see relationships.md
```

### Which Relationship Type?

```
Cardinality?
├── One entity → one entity
│   ├── Foreign key in this table → @OneToOne + @JoinColumn
│   └── Foreign key in other table → @OneToOne(mappedBy=…)
├── Many entities → one entity (owning side) → @ManyToOne + @JoinColumn
├── One entity → many entities
│   ├── One-to-many with FK in many table → @OneToMany(mappedBy=…) [bidirectional]
│   └── Unidirectional one-to-many → @OneToMany + @JoinColumn (avoids join table)
└── Many → many → @ManyToMany + @JoinTable
    └── Extra columns on join → use an intermediary @Entity instead
```

### Which Inheritance Strategy?

```
What are my constraints?
├── Single table, NULLs OK, best query perf → SINGLE_TABLE
│   └── Use when subtype data is sparse or rarely queried independently
├── Strict normalization, no shared columns → JOINED
│   └── Use when subtypes have many distinct fields; accepts JOIN cost
├── Concrete tables only, no polymorphic FK → TABLE_PER_CLASS
│   └── Use when polymorphic queries are rare; provider support varies
└── No inheritance, embed superclass columns → @MappedSuperclass
    └── Not queryable as a type; just shares mapping metadata
```

### Which Query Approach?

```
What do I need?
├── Type-safe compile-time query → Criteria API + Metamodel
├── Readable named query, static → @NamedQuery (JPQL string)
├── Dynamic JPQL string at runtime → em.createQuery(jpql, Type.class)
├── Full SQL control, vendor features → em.createNativeQuery(sql, …)
├── Bulk UPDATE/DELETE (bypass persistence context) → JPQL bulk op
│   └── Always clear() or re-fetch after bulk operations
└── Stored procedure → @NamedStoredProcedureQuery or createStoredProcedureQuery()
```

### Optimistic vs. Pessimistic Locking?

```
Use case?
├── Low contention, high concurrency → Optimistic (@Version field)
│   ├── Read committed by default
│   ├── Collision detected at commit (OptimisticLockException)
│   └── OPTIMISTIC_FORCE_INCREMENT forces version bump on read
└── High contention, must not retry → Pessimistic (LockModeType)
    ├── PESSIMISTIC_READ → shared lock (prevents dirty/non-repeatable reads)
    ├── PESSIMISTIC_WRITE → exclusive lock
    └── PESSIMISTIC_FORCE_INCREMENT → exclusive + version bump
```

## Key Concepts

### Entity States
```
NEW ──── persist() ────► MANAGED ──── commit/flush ────► DATABASE
                            │                               │
                         remove()                        find()/query
                            │                               │
                         REMOVED         detach()/close ──► DETACHED
                                                │
                                             merge() ──► MANAGED
```

### Persistence Context
The persistence context is the **first-level cache** and **identity map** — within a single `EntityManager`, the same row always returns the same Java object instance. It is scoped to a transaction by default (transaction-scoped) or extended across multiple transactions (extended PC, typically with stateful EJBs).

### EntityManager Operations
| Method | Effect |
|--------|--------|
| `persist(entity)` | NEW → MANAGED; INSERT on flush |
| `find(Type, id)` | Returns MANAGED or null; hits L1 cache first |
| `getReference(Type, id)` | Returns hollow proxy; loads on first access |
| `merge(entity)` | DETACHED → MANAGED copy; UPDATE on flush |
| `remove(entity)` | MANAGED → REMOVED; DELETE on flush |
| `refresh(entity)` | Reloads from DB; discards in-memory changes |
| `detach(entity)` | MANAGED → DETACHED |
| `flush()` | Syncs persistence context to DB (within tx) |
| `clear()` | Detaches all; empties persistence context |

### Transaction Boundaries
- **Container-managed (JTA):** `@Transactional` or `@TransactionAttribute` on EJB/CDI bean — container handles begin/commit/rollback.
- **Application-managed (resource-local):** `em.getTransaction().begin()/commit()/rollback()` — required in Java SE and when using `RESOURCE_LOCAL` persistence unit.

### JPQL vs SQL
JPQL operates on the **entity model** (class names, field names), not tables/columns. The provider translates to SQL. Use `@Column(name=…)` to map field names to column names — JPQL always uses the field name.
