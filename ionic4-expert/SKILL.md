---
name: ionic4-expert
description: Ionic Framework version 4 expertise for building cross-platform mobile and web apps. Use when working with Ionic v4 specifically — components, navigation, theming, native plugins, Angular integration, Capacitor/Cordova, or migrating from Ionic v3. Trigger whenever the user mentions Ionic 4, ion- components, IonRouterOutlet, Ionic Angular, @ionic/angular, building an Ionic app, Ionic CLI, or any Ionic v4 component by name (IonModal, IonList, IonTabs, etc.). Also trigger when the user is debugging an Ionic app, asking about theming with CSS variables, or integrating native device features in an Ionic project.
---

# Ionic 4 Expert

Ionic v4 (released 2019) was a complete rewrite of Ionic v3. The key architectural shifts:
- **Web components** via Stencil — `ion-*` elements work in any framework or vanilla JS
- **Framework-agnostic** — Angular (primary), React, Vue, or plain HTML
- **Navigation changed** — from v3's NavController push/pop stack → Angular Router + `<ion-router-outlet>`
- **CSS custom properties** replace SASS variables for theming
- **Capacitor** introduced as the modern alternative to Cordova

Most Ionic v4 projects use **Angular**. This skill assumes Angular unless stated otherwise.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    IONIC v4 APP STRUCTURE                   │
│                                                             │
│  src/                                                       │
│  ├── app/                                                   │
│  │   ├── app.module.ts      (root NgModule)                 │
│  │   ├── app-routing.module.ts  (Angular Router routes)    │
│  │   ├── app.component.html (<ion-app> + <ion-router-outlet>│
│  │   └── pages/             (one folder per page)          │
│  │       └── home/                                         │
│  │           ├── home.page.ts                              │
│  │           ├── home.page.html  (<ion-page> structure)    │
│  │           └── home.module.ts  (lazy-loaded)             │
│  ├── theme/                                                 │
│  │   └── variables.css      (CSS custom properties)        │
│  └── global.scss            (global styles)                │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  @ionic/     │  │  @angular/   │  │  Capacitor /     │  │
│  │  angular     │  │  core +      │  │  Cordova         │  │
│  │  (UI layer)  │  │  router      │  │  (native layer)  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Quick Reference

| Task | Reference File |
|------|---------------|
| Project setup, CLI commands, ionic start, serve, build | [setup.md](references/setup.md) |
| Navigation: Angular Router, IonRouterOutlet, tabs, params | [navigation.md](references/navigation.md) |
| Page layout: IonPage, IonHeader, IonToolbar, IonContent, IonGrid, IonMenu, IonSplitPane | [layout.md](references/layout.md) |
| UI components: IonButton, IonList, IonItem, IonInput, IonCard, IonTabs, IonFab, IonSearchbar | [components.md](references/components.md) |
| Overlays: IonModal, IonAlert, IonToast, IonActionSheet, IonLoading, IonPopover | [overlays.md](references/overlays.md) |
| Theming: CSS variables, colors, dark mode, platform styling | [theming.md](references/theming.md) |
| Native plugins: Capacitor, Cordova, @ionic-native wrappers | [native.md](references/native.md) |
| HTTP, Ionic Storage, services, Angular patterns | [data.md](references/data.md) |
| Breaking changes from v3, migration guide | [v3-migration.md](references/v3-migration.md) |

## Reference Files Overview

| File | Topics |
|------|--------|
| `setup.md` | ionic CLI install, `ionic start`, templates, `ionic serve`, `ionic build`, capacitor workflow |
| `navigation.md` | Angular Router config, IonRouterOutlet, NavController, tab routing, route guards, params |
| `layout.md` | IonApp, IonPage, IonHeader/Toolbar/Title, IonContent, IonFooter, IonGrid/Row/Col, IonMenu, IonSplitPane |
| `components.md` | IonButton, IonIcon, IonList/Item/Label, IonInput/Select/Toggle/Checkbox, IonCard, IonTabs, IonFab, IonInfiniteScroll, IonRefresher, IonVirtualScroll, IonSearchbar, IonSegment, IonSlides |
| `overlays.md` | ModalController, AlertController, ToastController, ActionSheetController, LoadingController, PopoverController — all with create/present/dismiss patterns |
| `theming.md` | CSS custom properties, `--ion-color-*`, global.scss, variables.css, dark mode, platform-specific (iOS/MD), ionic color generator |
| `native.md` | Capacitor vs Cordova, `@ionic-native` Angular wrappers, common plugins (Camera, Geolocation, Storage, Push Notifications) |
| `data.md` | Angular HttpClient, Ionic Storage v2/v3, RxJS patterns, environment files, interceptors |
| `v3-migration.md` | NavController push/pop → Angular Router, IonicModule.forRoot() changes, lifecycle hooks, removed components |

## Every Ionic Page Follows This Structure

```html
<ion-page>
  <ion-header>
    <ion-toolbar>
      <ion-buttons slot="start">
        <ion-back-button></ion-back-button>  <!-- or ion-menu-button -->
      </ion-buttons>
      <ion-title>Page Title</ion-title>
    </ion-toolbar>
  </ion-header>

  <ion-content>
    <!-- page content goes here -->
  </ion-content>
</ion-page>
```

`<ion-page>` is required — it's what Ionic uses for page transitions and lifecycle events.

## Key Decision Tree

### Which navigation pattern?

```
What kind of navigation do you need?
├── Simple linear navigation (push/pop feel)
│   └── Angular Router with IonRouterOutlet
│       └── Use NavController.navigateForward/Back for animated transitions
├── Bottom tabs (most mobile apps)
│   └── IonTabs + IonTabBar + IonTabButton + child router config
│       └── See navigation.md → Tabs Routing section
├── Side menu (hamburger nav)
│   └── IonMenu + IonSplitPane (auto-shows on tablet)
│       └── See layout.md → IonMenu section
└── Mixed (tabs + menu)
    └── IonSplitPane wrapping IonMenu + IonTabs
```

### Overlay: which controller to use?

```
What do you need to show?
├── Full-screen page-like UI    → IonModal
├── Yes/No confirmation         → IonAlert
├── Brief status message        → IonToast
├── List of action choices      → IonActionSheet
├── "Please wait" spinner       → IonLoading
└── Contextual popover bubble   → IonPopover
```

## Ionic v4 Module Import Pattern

Every Ionic component used in a page must be available via `IonicModule` in that page's module (or a shared module):

```typescript
// home.module.ts
import { IonicModule } from '@ionic/angular';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,          // gives access to all ion-* components
    HomePageRoutingModule
  ],
  declarations: [HomePage]
})
export class HomePageModule {}
```

For lazy-loaded pages (default with `ionic generate page`), each page has its own module. `IonicModule` must be imported in each one.
