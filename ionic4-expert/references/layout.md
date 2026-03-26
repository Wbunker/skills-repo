# Ionic 4 — Page Layout Components

## Page Skeleton

Every page must be wrapped in `<ion-page>`. This is not optional — it's what Ionic uses for transitions and lifecycle events.

```html
<ion-page>
  <ion-header [translucent]="true">
    <ion-toolbar>
      <ion-buttons slot="start">
        <ion-menu-button auto-hide="false"></ion-menu-button>
        <!-- or <ion-back-button defaultHref="/home"></ion-back-button> -->
      </ion-buttons>
      <ion-title>Page Title</ion-title>
      <ion-buttons slot="end">
        <ion-button (click)="doSomething()">
          <ion-icon slot="icon-only" name="settings"></ion-icon>
        </ion-button>
      </ion-buttons>
    </ion-toolbar>
  </ion-header>

  <ion-content [fullscreen]="true">
    <!-- main content -->
  </ion-content>

  <ion-footer>
    <ion-toolbar>
      <ion-title size="small">Footer</ion-title>
    </ion-toolbar>
  </ion-footer>
</ion-page>
```

---

## IonToolbar Slots

`slot` controls where child elements appear in the toolbar:

| slot | Position |
|------|----------|
| `start` | Left (or right on RTL) |
| `end` | Right (or left on RTL) |
| `secondary` | iOS: left, MD: left |
| `primary` | iOS: right, MD: right of secondary |
| (default) | Center (title, searchbar) |

```html
<ion-toolbar>
  <ion-buttons slot="start">
    <ion-back-button></ion-back-button>
  </ion-buttons>
  <ion-title>Title</ion-title>
  <ion-buttons slot="end">
    <ion-button>Edit</ion-button>
  </ion-buttons>
</ion-toolbar>
```

---

## IonContent

```html
<!-- fullscreen makes content go under translucent header on iOS -->
<ion-content [fullscreen]="true" scrollEvents="true" (ionScroll)="onScroll($event)">

  <!-- Collapsible large title (iOS only) -->
  <ion-header collapse="condense">
    <ion-toolbar>
      <ion-title size="large">Large Title</ion-title>
    </ion-toolbar>
  </ion-header>

  <!-- content -->

</ion-content>
```

### IonContent methods (via @ViewChild)

```typescript
@ViewChild(IonContent, { static: false }) content: IonContent;

this.content.scrollToTop(300);         // scroll to top, 300ms
this.content.scrollToBottom(300);
this.content.scrollToPoint(0, 500, 300);  // x, y, duration
```

---

## IonGrid / IonRow / IonCol

CSS Grid-based responsive layout. 12-column grid by default.

```html
<ion-grid>
  <ion-row>
    <ion-col size="12" size-md="6" size-lg="4">
      <!-- full width on small, half on medium, third on large -->
    </ion-col>
    <ion-col size="12" size-md="6" size-lg="4">
    </ion-col>
  </ion-row>
</ion-grid>
```

### Column sizing

```html
<ion-col size="6">        <!-- 6/12 = 50% -->
<ion-col size-xs="12" size-sm="6" size-md="4">   <!-- responsive -->
<ion-col offset="3">      <!-- offset by 3 columns -->
<ion-col push="2">        <!-- push right -->
<ion-col pull="2">        <!-- pull left -->
```

### Row alignment

```html
<ion-row align-items-center justify-content-center>
```

---

## IonMenu (Side Drawer)

```html
<!-- app.component.html -->
<ion-app>
  <ion-split-pane contentId="main-content">

    <ion-menu contentId="main-content" type="overlay">
      <ion-header>
        <ion-toolbar color="primary">
          <ion-title>Menu</ion-title>
        </ion-toolbar>
      </ion-header>
      <ion-content>
        <ion-list>
          <ion-menu-toggle auto-hide="false" *ngFor="let page of pages">
            <ion-item [routerLink]="page.url" routerLinkActive="active">
              <ion-icon slot="start" [name]="page.icon"></ion-icon>
              <ion-label>{{ page.title }}</ion-label>
            </ion-item>
          </ion-menu-toggle>
        </ion-list>
      </ion-content>
    </ion-menu>

    <ion-router-outlet id="main-content"></ion-router-outlet>

  </ion-split-pane>
</ion-app>
```

### Opening the menu

```html
<!-- In a page toolbar: -->
<ion-menu-button></ion-menu-button>
```

```typescript
// Programmatic:
import { MenuController } from '@ionic/angular';
constructor(private menu: MenuController) {}

this.menu.open();
this.menu.close();
this.menu.toggle();
this.menu.enable(true, 'main-menu');  // enable/disable by menuId
```

### Menu types

| type | Behavior |
|------|----------|
| `overlay` | Slides over content (default) |
| `reveal` | Pushes content aside |
| `push` | Pushes content (same as reveal on iOS) |

---

## IonSplitPane

Automatically shows the side menu as a persistent sidebar on wider screens (tablet/desktop) and hides it on mobile.

```html
<ion-split-pane contentId="main-content" when="md">
  <ion-menu contentId="main-content">...</ion-menu>
  <ion-router-outlet id="main-content"></ion-router-outlet>
</ion-split-pane>
```

`when` breakpoints: `xs`, `sm`, `md` (default), `lg`, `xl`, or a media query string.

---

## IonHeader Collapse (iOS Collapsible Header)

```html
<!-- In the toolbar: -->
<ion-header [translucent]="true">
  <ion-toolbar>
    <ion-title>Small Title</ion-title>
  </ion-toolbar>
</ion-header>

<ion-content [fullscreen]="true">
  <!-- Second header inside content collapses on scroll -->
  <ion-header collapse="condense">
    <ion-toolbar>
      <ion-title size="large">Large Title</ion-title>
    </ion-toolbar>
    <ion-toolbar>
      <ion-searchbar></ion-searchbar>
    </ion-toolbar>
  </ion-header>
  <!-- rest of content -->
</ion-content>
```

This gives the iOS large title effect where the title collapses into the toolbar on scroll.
