---
name: jsf-expert
description: JavaServer Faces / Jakarta Faces expertise covering component-based UI development, managed beans, CDI integration, navigation, validation, event handling, AJAX, internationalization, Facelets, composite components, and custom component/renderer development. Use when building JSF/Jakarta Faces applications, configuring faces-config.xml, designing UI component trees, handling form validation, wiring navigation rules, implementing custom renderers/components, migrating from javax.faces to jakarta.faces, or troubleshooting JSF lifecycle issues. Based on "JavaServer Faces" by Hans Bergsten (O'Reilly) plus JSF 2.x–Jakarta Faces 4.x coverage.
---

# JavaServer Faces / Jakarta Faces Expert

Based on "JavaServer Faces" by Hans Bergsten (O'Reilly, 2004), extended to cover JSF 2.x and Jakarta Faces 3.x/4.x.

**Package quick-ref:** classic JSF uses `javax.faces.*`; Jakarta Faces (Jakarta EE 9+) uses `jakarta.faces.*`. All reference files use `jakarta.faces.*` as the primary, with `javax.faces.*` noted where relevant.

## The JSF Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     JSF REQUEST LIFECYCLE                        │
│                                                                  │
│  HTTP Request                                                    │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────┐   ┌──────────────┐   ┌──────────────────────┐  │
│  │  Restore    │──▶│  Apply       │──▶│  Process             │  │
│  │  View       │   │  Request     │   │  Validations         │  │
│  │  (Phase 1)  │   │  Values      │   │  (Phase 3)           │  │
│  └─────────────┘   │  (Phase 2)   │   └──────────┬───────────┘  │
│                    └──────────────┘              │               │
│                                                  ▼               │
│  ┌─────────────┐   ┌──────────────┐   ┌──────────────────────┐  │
│  │  Render     │◀──│  Invoke      │◀──│  Update Model        │  │
│  │  Response   │   │  Application │   │  Values              │  │
│  │  (Phase 6)  │   │  (Phase 5)   │   │  (Phase 4)           │  │
│  └─────────────┘   └──────────────┘   └──────────────────────┘  │
│                                                                  │
│       ▼                                                          │
│  HTTP Response                                                   │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐     ┌────────────────────────────────────┐
│   VIEW LAYER         │     │   MODEL LAYER                      │
│                      │     │                                    │
│  JSP + JSF tags      │────▶│  Managed Beans (backing beans)     │
│  Component tree      │     │  Business logic                    │
│  Renderers           │◀────│  EL expressions: #{bean.property}  │
│  Converters          │     │  Action methods → navigation       │
└──────────────────────┘     └────────────────────────────────────┘
```

## Quick Reference

| Task | Reference |
|------|-----------|
| Setup, servlet/JSP foundations, first JSF app, faces-config.xml basics | [foundations.md](references/foundations.md) |
| UIComponent model, standard HTML/core tags, rendering, converters | [components.md](references/components.md) |
| Validators, custom validation, event types, listeners, action events | [validation-events.md](references/validation-events.md) |
| Navigation rules, static/dynamic navigation, tabular data, data models | [navigation-data.md](references/navigation-data.md) |
| i18n, resource bundles, locale selection, miscellaneous features | [internationalization.md](references/internationalization.md) |
| Custom renderers, custom components, custom presentation layer | [custom-components.md](references/custom-components.md) |
| Tag library reference, EL syntax, config file elements, deployment | [reference.md](references/reference.md) |

## Reference Files

| File | Chapters | Topics |
|------|----------|--------|
| `foundations.md` | 1–5 | JSF overview, dev process, environment, servlet/JSP recap, managed beans, authentication |
| `components.md` | 6 | Component tree, UIComponent hierarchy, HTML and core tag libraries, renderers, converters |
| `validation-events.md` | 7–8 | Built-in validators, custom validators, value change events, action events, phase events |
| `navigation-data.md` | 9–10 | Navigation rules, outcome strings, redirect vs forward, UIData, DataModel, tables |
| `internationalization.md` | 11–12 | Resource bundles, locale configuration, loadBundle tag, misc: logging, debug, parameters |
| `custom-components.md` | 13–15 | Custom renderers, pluggable classes, UIComponent subclassing, custom presentation layer |
| `reference.md` | App. A–F | Standard tags, Expression Language, component/render kit API, config XML, web.xml |

## Core Decision Trees

### Where Does My Problem Live in the Lifecycle?

```
What is going wrong?
├── Data from form not appearing in bean → Phase 2 or 4
│   ├── Value not decoded → Check Apply Request Values (Phase 2)
│   └── Validation blocking update → Check Phase 3 errors
├── Validation not firing → Phase 3
│   ├── Using wrong validator ID → foundations.md or validation-events.md
│   └── Custom validator not registered → faces-config.xml
├── Action method not called → Phase 5
│   ├── Validation errors present → clears phases 4+5
│   └── Wrong binding expression → check #{bean.method} syntax
├── Page not rendering correctly → Phase 6
│   ├── Wrong renderer → components.md
│   └── Converter issue → components.md
└── Navigation not working → faces-config.xml rules
    └── See navigation-data.md
```

### Which Tag Library Do I Need?

```
What am I rendering?
├── HTML form elements (input, select, textarea…) → html taglib (h:)
│   └── h:inputText, h:selectOneMenu, h:commandButton, h:form…
├── Non-rendering logic (converters, validators, events) → core taglib (f:)
│   └── f:validator, f:converter, f:valueChangeListener, f:loadBundle…
├── Data table / repeat → h:dataTable + f:column
└── Custom component → Register in faces-config.xml + custom taglib
```

### Managed Bean Scope — Which One?

```
How long does the bean need to live?
├── Only for this request → request scope
│   └── Form submission + immediate rendering
├── Across multiple requests (wizard, multi-step) → session scope
│   └── Stored in HttpSession — watch for memory leaks
├── Entire app lifetime → application scope
│   └── Shared state, reference data, caches
└── Per-view lifecycle (JSF 2+) → view scope (not in Bergsten ed.)
```

### Custom vs. Built-in — What to Extend?

```
What functionality do I need?
├── Change HTML output of existing component → Custom Renderer
│   └── Extend existing Renderer or implement from scratch
├── New component with new behavior + rendering → Custom Component
│   └── Extend UIComponentBase (or suitable UIComponent subclass)
├── Reusable validation logic → Custom Validator
│   └── Implement Validator interface, register in faces-config.xml
├── Convert string ↔ object → Custom Converter
│   └── Implement Converter interface, register in faces-config.xml
└── Different view technology (not JSP) → Custom ViewHandler
    └── Extend ViewHandler, configure in faces-config.xml
```

## Key Concepts

### The Component Tree
Every JSF page is backed by a tree of `UIComponent` objects. The tree is built during Restore View, populated during Apply Request Values, and traversed during Render Response. Understanding the tree is key to understanding JSF behavior.

### Managed Beans and the Expression Language
Beans declared in `faces-config.xml` are accessible via `#{beanName.property}`. JSF EL is evaluated lazily — expressions are resolved at render time or when a value is needed. Action methods return a `String` outcome used to look up navigation rules.

### Faces Configuration File
`faces-config.xml` is the central wiring file:
- `<managed-bean>` — declares beans and their scope
- `<navigation-rule>` — maps action outcomes to view IDs
- `<validator>` / `<converter>` — registers custom classes
- `<component>` / `<render-kit>` — registers custom UI components

### Render Kits
A render kit is a collection of `Renderer` objects for a target client type (default: HTML). Renderers decode incoming request values and encode outgoing HTML. Separating rendering from component logic allows the same component to render differently for different clients.
