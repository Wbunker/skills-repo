---
name: ionic4-to-5-migration
description: Step-by-step guide for upgrading Ionic 4 apps to Ionic 5. Use this skill whenever the user mentions migrating, upgrading, or updating from Ionic 4 to Ionic 5, asks about Ionic 5 breaking changes, gets errors after upgrading Ionic packages, sees "property does not exist" or CSS variable issues after an Ionic upgrade, or asks what changed between Ionic 4 and 5. Also trigger when the user mentions removing the Events service, swipeEnable errors, ion-anchor not found, or the main attribute being deprecated. Trigger even if they just say "upgrade Ionic" or "move to v5".
---

# Ionic 4 → 5 Migration

Ionic 5 is a **non-breaking-if-you-follow-this-guide** upgrade in package terms, but it has significant component API, CSS, and Angular service changes. Most apps need template edits and CSS variable updates; almost no TypeScript logic changes are required beyond the `Events` service.

## Architecture: What Changed

```
┌──────────────────────────────────────────────────────────────────┐
│                IONIC 4 → 5: KEY CHANGES AT A GLANCE              │
│                                                                   │
│  CSS Utilities    attribute-based         → ion-* classes         │
│                   <ion-content padding>   → class="ion-padding"   │
│                                                                   │
│  CSS Variables    --ion-toolbar-color-*   → --ion-toolbar-        │
│                   unchecked/checked         segment-color-*       │
│                   state colors combined   → color + opacity vars  │
│                                                                   │
│  Components       ion-anchor             → ion-router-link        │
│                   ion-nav-push/back/root  → ion-nav-link          │
│                   ion-*-controller elems  → import from core      │
│                                                                   │
│  Properties       checked on radio/seg   → value on parent group  │
│                   selected on option     → value on ion-select    │
│                   width on skeleton      → CSS styling            │
│                   main attr on menu      → contentId / content-id │
│                   side="left/right"      → side="start/end"       │
│                                                                   │
│  Events           ionSelect on radio/seg → ionChange on group     │
│                   Events service removed → RxJS BehaviorSubject   │
│                                                                   │
│  Iconography      Ionicons 5: new design, 3 variants per icon,    │
│                   no auto platform-switching                      │
│                                                                   │
│  Build            Angular 8+ required; Angular 9/Ivy supported    │
│                   SCSS dist files removed; CSS vars only          │
└──────────────────────────────────────────────────────────────────┘
```

## Quick Reference — What to Read

| Problem / Task | Reference File |
|---|---|
| Install commands, package versions, Angular compatibility | [tooling.md](references/tooling.md) |
| CSS utility attributes → classes, `no-border`, `main` attr | [utilities.md](references/utilities.md) |
| CSS variable renames, state opacity vars, color palette | [css-variables.md](references/css-variables.md) |
| Component-level changes: Radio, Segment, Select, Skeleton, Toast, Menu, etc. | [components.md](references/components.md) |
| Angular-specific: `Events` removal, Ivy, `swipeGesture` | [angular.md](references/angular.md) |
| Ionicons 5 icon name changes and variant system | [ionicons.md](references/ionicons.md) |

## Migration Checklist

Work through these in order — each section is independent, so you can tackle them separately:

### Step 1 — Update packages
```bash
npm install @ionic/angular@5 @ionic/angular-toolkit@2.2.0
# also update ionicons
npm install ionicons@5
```
See [tooling.md](references/tooling.md) for Angular version matrix and Capacitor/Cordova notes.

### Step 2 — Fix CSS utility attributes in templates
Search for bare attributes (`padding`, `text-center`, `text-wrap`, `push-3`, etc.) on Ionic elements and replace with `ion-` classes. See [utilities.md](references/utilities.md).

### Step 3 — Fix CSS custom property names
Global toolbar, tab bar, and item state variables were renamed or removed. See [css-variables.md](references/css-variables.md).

### Step 4 — Fix component API changes
- `ion-menu`: `side="left/right"` → `start/end`, `main` → `contentId`, `swipeEnable` → `swipeGesture`
- `ion-radio`: remove `checked`, use `value` on `ion-radio-group`
- `ion-segment-button`: remove `checked`, use `value` on `ion-segment`
- `ion-select-option`: remove `selected`, use `value` on `ion-select`
- `ion-toast`: replace `showCloseButton`/`closeButtonText` with `buttons` array
- `ion-list-header`: wrap text in `<ion-label>`
- `ion-skeleton-text`: replace `width` attr with CSS

See [components.md](references/components.md) for full before/after examples.

### Step 5 — Remove deprecated components
- `ion-anchor` → `ion-router-link` (vanilla/Stencil only; Angular uses `<a routerLink>`)
- `ion-nav-push`, `ion-nav-back`, `ion-nav-set-root` → `ion-nav-link router-direction="..."`
- `ion-*-controller` HTML elements → import controller objects from `@ionic/core`

### Step 6 — Angular: replace `Events` service
`Events` is gone. Replace with an RxJS `BehaviorSubject` in a shared service. See [angular.md](references/angular.md) for the pattern.

### Step 7 — Update icons
Ionicons 5 redesigned every icon and removed automatic platform variant switching. See [ionicons.md](references/ionicons.md).

## Decision Trees

### "My templates are showing unknown elements / attribute errors"
```
Error involves ion-anchor?
├── Yes → rename to ion-router-link (vanilla/Stencil) or <a routerLink> (Angular)
└── No → error involves ion-nav-push / ion-nav-back / ion-nav-set-root?
    ├── Yes → replace with ion-nav-link + router-direction attr
    └── No → error involves ion-*-controller element in HTML?
        └── Yes → remove the element; import controller from @ionic/core
```

### "My CSS / theming looks wrong after upgrade"
```
Issue with toolbar segment colors?
├── Yes → see css-variables.md: --ion-toolbar-color-unchecked/checked renamed
└── No → issue with tab bar active color?
    ├── Yes → --ion-tab-bar-color-activated → --ion-tab-bar-color-selected
    └── No → issue with hover/focus/activated state colors?
        ├── Yes → state vars now split into color + opacity (see css-variables.md)
        └── No → utility classes not applying?
            └── Yes → replace attributes with ion-* classes (see utilities.md)
```

### "My component data binding is broken after upgrade"
```
ion-radio not reflecting selected state?
└── Move checked from ion-radio to value on ion-radio-group

ion-segment-button not reflecting selected state?
└── Move checked from ion-segment-button to value on ion-segment

ion-select-option not reflecting selected state?
└── Move selected from ion-select-option to value on ion-select

ion-radio firing ionSelect that no longer exists?
└── Listen to ionChange on ion-radio-group instead

ion-segment firing ionSelect?
└── Listen to ionChange on ion-segment instead
```
