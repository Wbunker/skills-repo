---
name: ionic3-expert
description: Ionic Framework version 3 expertise for building cross-platform mobile apps with Angular. Use when working with Ionic v3 specifically — NavController push/pop navigation, ion- components, SASS theming, Cordova plugins, @ionic-native wrappers, or lazy loading with @IonicPage. Trigger whenever the user mentions Ionic 3, ionic-angular, NavController, NavParams, IonicPage, ionViewDidLoad, ion-nav, or any Ionic v3 pattern. Also trigger when debugging an Ionic 3 app, asking about SASS $colors map theming, or migrating from v3 to v4.
---

# Ionic 3 Expert

Ionic v3 (2017–2019) is an Angular-based framework for building cross-platform mobile apps compiled via Cordova. Key architectural characteristics:
- **Angular-only** — tightly coupled to Angular 4–6, package is `ionic-angular`
- **NavController push/pop** — custom stack-based navigation, NOT Angular Router
- **SASS variables** — theming via `$colors` map and Ionic SASS variables, NOT CSS custom properties
- **Cordova** — primary native runtime; Capacitor did not exist in v3
- **@IonicPage decorator** — enables lazy loading and deep linking per page
- **Lifecycle hooks** — `ionViewDidLoad`, `ionViewWillEnter`, `ionViewDidEnter`, `ionViewWillLeave`, `ionViewDidLeave`, `ionViewWillUnload`

All Ionic v3 packages come from `ionic-angular`, not `@ionic/angular`.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    IONIC v3 APP STRUCTURE                   │
│                                                             │
│  src/                                                       │
│  ├── app/                                                   │
│  │   ├── app.module.ts      (root NgModule)                 │
│  │   ├── app.component.ts   (root component, sets rootPage) │
│  │   ├── app.html           (<ion-menu> + <ion-nav>)        │
│  │   └── app.scss           (global styles)                 │
│  ├── pages/                 (one folder per page)           │
│  │   └── home/                                             │
│  │       ├── home.ts        (@IonicPage + @Component)       │
│  │       ├── home.html      (<ion-header> structure)        │
│  │       ├── home.module.ts (IonicPageModule.forChild)      │
│  │       └── home.scss      (page-scoped styles)            │
│  ├── providers/             (Angular services/providers)    │
│  ├── components/            (shared components)             │
│  ├── assets/                (images, fonts)                 │
│  └── theme/                                                 │
│      └── variables.scss     (SASS $colors map)              │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ ionic-angular│  │  @angular/   │  │  Cordova         │  │
│  │ (UI + Nav)   │  │  core 4-6    │  │  (native layer)  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Quick Reference

| Task | Reference File |
|------|---------------|
| Project setup, CLI commands, ionic start, serve, build, generate, folder structure | [setup.md](references/setup.md) |
| Navigation: NavController push/pop, NavParams, setRoot, tabs navigation, @IonicPage, lifecycle hooks | [navigation.md](references/navigation.md) |
| Page layout: ion-app, ion-nav, ion-header, ion-toolbar, ion-content, ion-grid, ion-menu, ion-split-pane | [layout.md](references/layout.md) |
| UI components: ion-button, ion-list, ion-item, ion-card, ion-tabs, ion-fab, ion-slides, ion-infinite-scroll, ion-refresher, ion-virtual-scroll, all form controls | [components.md](references/components.md) |
| Overlays: ModalController, AlertController, ToastController, ActionSheetController, LoadingController, PopoverController | [overlays.md](references/overlays.md) |
| Theming: SASS $colors map, color() function, platform-specific styles, variables.scss | [theming.md](references/theming.md) |
| Native plugins: @ionic-native wrappers, Cordova plugins, Camera, Geolocation, Storage, Push, StatusBar | [native.md](references/native.md) |
| HTTP, Ionic Storage, RxJS patterns, providers/services, Angular HttpClient | [data.md](references/data.md) |
| Angular NgModule setup, IonicModule.forRoot(), lazy loading, app.module.ts, page modules | [angular-integration.md](references/angular-integration.md) |
| Key differences from Ionic 4, migration guide | [v4-differences.md](references/v4-differences.md) |

## Every Ionic 3 Page Follows This Structure

```html
<ion-header>
  <ion-toolbar>
    <ion-buttons start>
      <button ion-button (click)="back()">
        <ion-icon name="arrow-back"></ion-icon>
      </button>
    </ion-buttons>
    <ion-title>Page Title</ion-title>
  </ion-toolbar>
</ion-header>

<ion-content padding>
  <!-- page content goes here -->
</ion-content>
```

Note: In v3, `<ion-page>` wrapper is NOT required on page templates (unlike v4). Pages are plain Angular components.

## Key Decision Trees

### Which navigation pattern?

```
What kind of navigation do you need?
├── Push a new page on the stack
│   └── this.navCtrl.push(DetailPage, { id: item.id })
├── Go back to previous page
│   └── this.navCtrl.pop()
├── Replace root (e.g., after login)
│   └── this.navCtrl.setRoot(HomePage)
├── Bottom tabs (most mobile apps)
│   └── <ion-tabs> with [root] on each <ion-tab>
│       └── See navigation.md → Tabs section
└── Side menu navigation
    └── <ion-menu> + <ion-split-pane> + MenuController
        └── See layout.md → ion-menu section
```

### Overlay: which controller to use?

```
What do you need to show?
├── Full-screen page-like UI    → ModalController
├── Yes/No confirmation         → AlertController
├── Brief status message        → ToastController
├── List of action choices      → ActionSheetController
├── "Please wait" spinner       → LoadingController
└── Contextual popover bubble   → PopoverController
```

### Lazy loading or eager loading?

```
Page setup approach?
├── Lazy loading (recommended for v3.5+)
│   ├── Add @IonicPage() decorator to page class
│   ├── Create home.module.ts with IonicPageModule.forChild(HomePage)
│   └── Navigate by string name: navCtrl.push('HomePage')
└── Eager loading (simpler for small apps)
    ├── Import all pages in app.module.ts
    ├── Add to declarations and entryComponents arrays
    └── Navigate by class reference: navCtrl.push(HomePage)
```
