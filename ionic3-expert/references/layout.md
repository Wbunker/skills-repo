# Ionic 3 — Page Layout

## Standard Page Template

In Ionic 3, pages are plain Angular components — there is NO `<ion-page>` wrapper required (unlike v4). The template's top-level elements are the header, content, and optionally a footer.

```html
<ion-header>
  <ion-toolbar>
    <ion-buttons start>
      <button ion-button icon-only (click)="navCtrl.pop()">
        <ion-icon name="arrow-back"></ion-icon>
      </button>
    </ion-buttons>
    <ion-title>Page Title</ion-title>
    <ion-buttons end>
      <button ion-button icon-only (click)="doSomething()">
        <ion-icon name="more"></ion-icon>
      </button>
    </ion-buttons>
  </ion-toolbar>
</ion-header>

<ion-content padding>
  <!-- page content -->
</ion-content>

<ion-footer>
  <ion-toolbar>
    <ion-title>Footer</ion-title>
  </ion-toolbar>
</ion-footer>
```

---

## ion-app

`<ion-app>` is in `src/index.html` and wraps the entire application. Only one per app.

```html
<!-- index.html -->
<body>
  <ion-app></ion-app>
</body>
```

---

## ion-nav

`<ion-nav>` is the main navigation container. It holds the page stack and is declared in `app.html`.

```html
<!-- app.html -->
<ion-nav [root]="rootPage" #nav></ion-nav>
```

| Attribute | Type | Description |
|-----------|------|-------------|
| `[root]` | Page / string | Root page component to display |
| `[rootParams]` | object | Params passed to root page |
| `#nav` | template ref | Reference for @ViewChild access |
| `swipeBackEnabled` | boolean | Enable iOS swipe-to-go-back (default: true) |
| `name` | string | Unique name for this nav (for split pane) |

---

## ion-header

Wraps the toolbar at the top of the page. Can be `no-border`:

```html
<ion-header no-border>
  <ion-toolbar>...</ion-toolbar>
</ion-header>
```

---

## ion-toolbar

Contains title, buttons, and other toolbar controls. Supports `color` attribute.

```html
<ion-toolbar color="primary">
  <ion-title>My App</ion-title>
</ion-toolbar>

<!-- Secondary toolbar (e.g., search bar below main toolbar) -->
<ion-header>
  <ion-toolbar>
    <ion-title>Title</ion-title>
  </ion-toolbar>
  <ion-toolbar>
    <ion-searchbar></ion-searchbar>
  </ion-toolbar>
</ion-header>
```

### ion-buttons placement

In Ionic 3, button placement uses `start` / `end` attributes (not slots):

```html
<ion-buttons start>   <!-- left side -->
<ion-buttons end>     <!-- right side -->
```

---

## ion-title

Displays the page title in the toolbar:

```html
<ion-title>Home</ion-title>
<!-- Center on iOS, left-aligned on Android (MD) by default -->
```

---

## ion-content

The scrollable content area. Most page content goes inside here.

```html
<!-- padding shorthand adds padding on all sides -->
<ion-content padding>
  ...
</ion-content>

<!-- Separate padding attributes -->
<ion-content padding-top padding-bottom>
</ion-content>

<!-- No padding, no margin, full bleed -->
<ion-content no-padding>
</ion-content>
```

### ion-content Programmatic Scrolling

```typescript
import { ViewChild } from '@angular/core';
import { Content } from 'ionic-angular';

@Component({...})
export class MyPage {
  @ViewChild(Content) content: Content;

  scrollToTop() {
    this.content.scrollToTop(300);  // 300ms animation
  }

  scrollToBottom() {
    this.content.scrollToBottom(500);
  }

  scrollTo(yOffset: number) {
    this.content.scrollTo(0, yOffset, 400);
  }
}
```

---

## ion-footer

Optional footer bar at the bottom of the page:

```html
<ion-footer>
  <ion-toolbar>
    <ion-title>Footer Text</ion-title>
  </ion-toolbar>
</ion-footer>
```

---

## ion-grid / ion-row / ion-col

Ionic 3 uses a 12-column flexbox grid (similar to Bootstrap).

```html
<ion-grid>
  <ion-row>
    <ion-col col-6>Left Half</ion-col>
    <ion-col col-6>Right Half</ion-col>
  </ion-row>
  <ion-row>
    <ion-col col-12 col-md-4>Sidebar</ion-col>
    <ion-col col-12 col-md-8>Main</ion-col>
  </ion-row>
</ion-grid>
```

### Column Width Attributes (in Ionic 3)

In v3, column width uses attribute form (not `size` property as in v4):

| Attribute | Description |
|-----------|-------------|
| `col-1` through `col-12` | Width across all screen sizes |
| `col-xs-*` | Width for xs and up |
| `col-sm-*` | Width for sm (576px+) and up |
| `col-md-*` | Width for md (768px+) and up |
| `col-lg-*` | Width for lg (992px+) and up |
| `col-xl-*` | Width for xl (1200px+) and up |

### Offset / Push / Pull

```html
<ion-col offset-3 col-6>Centered</ion-col>
<ion-col offset-sm-2 col-sm-8>Offset on small+</ion-col>

<ion-col push-2 col-8>Pushed right</ion-col>
<ion-col pull-2 col-8>Pulled left</ion-col>
```

### Row Alignment (flexbox)

```html
<ion-row align-items-center>       <!-- vertically center children -->
<ion-row align-items-start>
<ion-row align-items-end>
<ion-row justify-content-center>   <!-- horizontally center children -->
<ion-row justify-content-between>
<ion-row justify-content-around>
```

### Column Self-Alignment

```html
<ion-col align-self-start>
<ion-col align-self-center>
<ion-col align-self-end>
```

### Grid Utility Attributes

```html
<ion-grid no-padding>  <!-- remove grid padding -->
<ion-grid fixed>       <!-- constrain max width per breakpoint -->
<ion-row no-padding>
<ion-col no-padding>
```

### Breakpoints Reference

| Tier | Min Width | Col prefix | Offset prefix |
|------|----------|------------|---------------|
| xs | 0 | `col-` | `offset-` |
| sm | 576px | `col-sm-` | `offset-sm-` |
| md | 768px | `col-md-` | `offset-md-` |
| lg | 992px | `col-lg-` | `offset-lg-` |
| xl | 1200px | `col-xl-` | `offset-xl-` |

---

## ion-menu

Side navigation drawer. Must be paired with an `<ion-nav>` or `<ion-split-pane>`.

```html
<!-- app.html -->
<ion-menu [content]="content" side="left" type="overlay">
  <ion-header>
    <ion-toolbar color="primary">
      <ion-title>Menu</ion-title>
    </ion-toolbar>
  </ion-header>
  <ion-content>
    <ion-list>
      <button menuClose ion-item *ngFor="let p of pages" (click)="openPage(p)">
        <ion-icon item-start [name]="p.icon"></ion-icon>
        {{p.title}}
      </button>
    </ion-list>
  </ion-content>
</ion-menu>

<ion-nav [root]="rootPage" #content swipeBackEnabled="false"></ion-nav>
```

### ion-menu Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `[content]` | element ref | Reference to the main content element |
| `side` | string | `left` (default) or `right` |
| `type` | string | `overlay` / `reveal` / `push` |
| `swipeEnabled` | boolean | Allow swipe to open (default: true) |
| `persistent` | boolean | Don't hide on page navigation |
| `id` | string | Identify menu when using multiple menus |

### menuClose Directive

Add `menuClose` attribute to any button/item to auto-close the menu on click:

```html
<button menuClose ion-item (click)="openPage(p)">...</button>
```

### menuToggle Directive

Add to a button in the toolbar to toggle the menu:

```html
<button ion-button menuToggle>
  <ion-icon name="menu"></ion-icon>
</button>
```

---

## ion-split-pane

Shows the menu permanently on wide screens (tablets/desktop) and hides it on narrow screens.

```html
<ion-split-pane when="md">
  <ion-menu [content]="content">
    <!-- menu content -->
  </ion-menu>
  <ion-nav [root]="rootPage" main #content></ion-nav>
</ion-split-pane>
```

The `main` attribute on `ion-nav` marks it as the main content area.

### when Attribute

Controls the breakpoint at which the split pane is active:

| Value | Breakpoint |
|-------|-----------|
| `xs` | Always show split pane |
| `sm` | 576px+ |
| `md` | 768px+ (default) |
| `lg` | 992px+ |
| `xl` | 1200px+ |
| `never` | Never show (always side menu) |
| CSS media query string | Custom breakpoint |

```html
<!-- Always show split pane -->
<ion-split-pane when="xs">

<!-- Custom breakpoint -->
<ion-split-pane when="(min-width: 600px)">
```

### (ionChange) event

```typescript
<ion-split-pane (ionChange)="onSplitPaneChange($event)">
```

---

## Attribute Directives for Layout Spacing

Ionic 3 provides attribute shorthands for common CSS spacing patterns. Apply directly to elements:

| Attribute | Effect |
|-----------|--------|
| `padding` | padding on all sides |
| `padding-top` | padding top |
| `padding-bottom` | padding bottom |
| `padding-left` | padding left |
| `padding-right` | padding right |
| `padding-vertical` | padding top + bottom |
| `padding-horizontal` | padding left + right |
| `no-padding` | remove padding |
| `margin` | margin on all sides |
| `no-margin` | remove margin |
| `text-left` | text-align: left |
| `text-center` | text-align: center |
| `text-right` | text-align: right |
| `text-justify` | text-align: justify |
| `text-wrap` | white-space: normal |
| `text-nowrap` | white-space: nowrap |
| `text-uppercase` | text-transform: uppercase |
| `text-lowercase` | text-transform: lowercase |
| `text-capitalize` | text-transform: capitalize |
| `float-left` | float: left |
| `float-right` | float: right |
| `hidden` | display: none |
| `hide-xs` through `hide-xl` | responsive hiding |
| `show-xs` through `show-xl` | responsive showing |

---

## ion-card Layout

```html
<ion-card>
  <img src="assets/img/bg.jpg"/>
  <ion-card-header>
    Card Header
  </ion-card-header>
  <ion-card-content>
    <ion-card-title>Card Title</ion-card-title>
    <p>Card content text goes here.</p>
  </ion-card-content>
</ion-card>
```
