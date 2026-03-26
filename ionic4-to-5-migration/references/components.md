# Component Breaking Changes

## Table of Contents
- [ion-anchor → ion-router-link](#ion-anchor)
- [ion-nav-push / ion-nav-back / ion-nav-set-root → ion-nav-link](#ion-nav)
- [ion-*-controller elements removed](#controllers)
- [ion-list-header](#ion-list-header)
- [ion-menu](#ion-menu)
- [ion-radio](#ion-radio)
- [ion-searchbar](#ion-searchbar)
- [ion-segment and ion-segment-button](#ion-segment)
- [ion-select-option](#ion-select-option)
- [ion-skeleton-text](#ion-skeleton-text)
- [ion-split-pane](#ion-split-pane)
- [ion-toast](#ion-toast)

---

## ion-anchor → ion-router-link {#ion-anchor}

Applies to **vanilla JS and Stencil** projects only. Angular projects use standard `<a routerLink>` and are unaffected.

```html
<!-- Before -->
<ion-anchor href="/home">Home</ion-anchor>

<!-- After (vanilla/Stencil) -->
<ion-router-link href="/home">Home</ion-router-link>

<!-- Angular: use standard anchor with Angular Router -->
<a routerLink="/home">Home</a>
```

---

## ion-nav-push / ion-nav-back / ion-nav-set-root {#ion-nav}

Three components removed. Replaced by a single `ion-nav-link` with a `router-direction` property.

```html
<!-- Before: push forward -->
<ion-nav-push component="my-page" [componentProps]="props"></ion-nav-push>

<!-- Before: go back -->
<ion-nav-back defaultHref="/home"></ion-nav-back>

<!-- Before: set root -->
<ion-nav-set-root component="my-page"></ion-nav-set-root>
```

```html
<!-- After: all three cases use ion-nav-link -->
<ion-nav-link router-direction="forward" component="my-page" [componentProps]="props">
</ion-nav-link>

<ion-nav-link router-direction="back" defaultHref="/home">
</ion-nav-link>

<ion-nav-link router-direction="root" component="my-page">
</ion-nav-link>
```

---

## ion-*-controller elements removed {#controllers}

The HTML element form of controllers (`<ion-loading-controller>`, etc.) was removed. In vanilla JS you must now import from `@ionic/core`.

**Angular and React projects are unaffected** — they already inject/import controller classes from `@ionic/angular` or `@ionic/react`.

```html
<!-- Before (vanilla JS) -->
<ion-loading-controller></ion-loading-controller>
<script>
  const ctrl = document.querySelector('ion-loading-controller');
  await ctrl.componentOnReady();
  const loading = await ctrl.create({ message: 'Loading...' });
  await loading.present();
</script>
```

```javascript
// After (vanilla JS / ES modules)
import { loadingController } from '@ionic/core';

const loading = await loadingController.create({ message: 'Loading...' });
await loading.present();
```

Affected controller elements:
- `ion-action-sheet-controller`
- `ion-alert-controller`
- `ion-loading-controller`
- `ion-menu-controller`
- `ion-modal-controller`
- `ion-picker-controller`
- `ion-popover-controller`
- `ion-toast-controller`

---

## ion-list-header {#ion-list-header}

Visual redesign to match iOS 13 spec (larger, bolder text). Text content must be wrapped in `<ion-label>`.

```html
<!-- Before -->
<ion-list-header>
  New This Week
  <ion-button>See All</ion-button>
</ion-list-header>

<!-- After -->
<ion-list-header>
  <ion-label>New This Week</ion-label>
  <ion-button>See All</ion-button>
</ion-list-header>
```

`ion-button` inside a list header now defaults to `fill="clear"` and `size="small"`.

---

## ion-menu {#ion-menu}

### `side` values changed

```html
<!-- Before -->
<ion-menu side="left">...</ion-menu>
<ion-menu side="right">...</ion-menu>

<!-- After -->
<ion-menu side="start">...</ion-menu>
<ion-menu side="end">...</ion-menu>
```

### `swipeEnable` method renamed to `swipeGesture`

```typescript
// Before (Angular)
this.menuController.swipeEnable(false, 'menu1');
this.menuController.swipeEnable(true);

// After
this.menuController.swipeGesture(false, 'menu1');
this.menuController.swipeGesture(true);
```

### `main` attribute → `contentId`

See [utilities.md](utilities.md#main-attribute) for full before/after.

### iOS presentation type default changed

- Before: `"reveal"` (pushes content aside)
- After: `"overlay"` (overlays content)

If you relied on the push/reveal behavior on iOS, add `type="reveal"` explicitly:

```html
<ion-menu type="reveal">...</ion-menu>
```

---

## ion-radio {#ion-radio}

### `checked` property removed

Selection is now controlled by the parent `ion-radio-group`'s `value` property.

```html
<!-- Before: checked on individual radio -->
<ion-radio-group>
  <ion-radio value="a">A</ion-radio>
  <ion-radio checked value="b">B</ion-radio>  <!-- ← remove checked -->
</ion-radio-group>

<!-- Before: single radio (no group required in v4) -->
<ion-radio checked>Option</ion-radio>
```

```html
<!-- After: value on the group; single radio must be in a group -->
<ion-radio-group value="b">
  <ion-radio value="a">A</ion-radio>
  <ion-radio value="b">B</ion-radio>
</ion-radio-group>
```

### `ionSelect` event removed

```typescript
// Before: listen on individual radio
radio.addEventListener('ionSelect', handler);

// After: listen on the group
radioGroup.addEventListener('ionChange', handler);
```

Angular template:
```html
<!-- Before -->
<ion-radio (ionSelect)="onSelect($event)">

<!-- After: event on the group -->
<ion-radio-group (ionChange)="onSelect($event)">
```

---

## ion-searchbar {#ion-searchbar}

### `show-cancel-button` type changed (boolean → string)

```html
<!-- Before: boolean attribute -->
<ion-searchbar show-cancel-button></ion-searchbar>
<ion-searchbar show-cancel-button="true"></ion-searchbar>
<ion-searchbar show-cancel-button="false"></ion-searchbar>
```

```html
<!-- After: string enum -->
<ion-searchbar show-cancel-button="focus"></ion-searchbar>   <!-- show on focus (replaces true) -->
<ion-searchbar show-cancel-button="always"></ion-searchbar>  <!-- always visible -->
<ion-searchbar show-cancel-button="never"></ion-searchbar>   <!-- never show (replaces false) -->
```

Valid values: `"focus"`, `"always"`, `"never"`.

### `inputmode` default changed

- Before: defaulted to `"search"` internally
- After: defaults to `undefined`

If you need the search keyboard type, add it explicitly:
```html
<ion-searchbar inputmode="search"></ion-searchbar>
```

---

## ion-segment and ion-segment-button {#ion-segment}

### `checked` removed from `ion-segment-button`

Selection is now controlled by `ion-segment`'s `value` property. Every button must have a `value`.

```html
<!-- Before -->
<ion-segment>
  <ion-segment-button>One</ion-segment-button>
  <ion-segment-button checked>Two</ion-segment-button>
  <ion-segment-button>Three</ion-segment-button>
</ion-segment>
```

```html
<!-- After -->
<ion-segment value="two">
  <ion-segment-button value="one">One</ion-segment-button>
  <ion-segment-button value="two">Two</ion-segment-button>
  <ion-segment-button value="three">Three</ion-segment-button>
</ion-segment>
```

### `ionSelect` event removed from `ion-segment`

```typescript
// Before
segment.addEventListener('ionSelect', handler);

// After
segment.addEventListener('ionChange', handler);
```

Angular:
```html
<!-- Before -->
<ion-segment (ionSelect)="segmentChanged($event)">

<!-- After -->
<ion-segment (ionChange)="segmentChanged($event)">
```

### Visual redesign

Segment received an iOS 13-style sliding indicator with gesture support. The appearance changed significantly. CSS variable changes are in [css-variables.md](css-variables.md#segment-button).

### Mode cascading (new feature)

Mode now cascades from parent to child, so you only need to set it once:

```html
<!-- Before: set mode on every child -->
<ion-segment mode="md">
  <ion-segment-button mode="md">A</ion-segment-button>
</ion-segment>

<!-- After: set once -->
<ion-segment mode="md">
  <ion-segment-button>A</ion-segment-button>
</ion-segment>
```

---

## ion-select-option {#ion-select-option}

### `selected` property removed

Selection is now controlled by the parent `ion-select`'s `value` property.

```html
<!-- Before -->
<ion-select>
  <ion-select-option value="a">Apple</ion-select-option>
  <ion-select-option value="b" selected>Banana</ion-select-option>
</ion-select>

<!-- After -->
<ion-select value="b">
  <ion-select-option value="a">Apple</ion-select-option>
  <ion-select-option value="b">Banana</ion-select-option>
</ion-select>
```

Angular two-way binding (unchanged pattern, just remove `selected`):
```html
<ion-select [(ngModel)]="selectedFruit">
  <ion-select-option value="a">Apple</ion-select-option>
  <ion-select-option value="b">Banana</ion-select-option>
</ion-select>
```

---

## ion-skeleton-text {#ion-skeleton-text}

### `width` property removed

```html
<!-- Before -->
<ion-skeleton-text animated width="60%"></ion-skeleton-text>
<ion-skeleton-text animated width="100px"></ion-skeleton-text>

<!-- After: use CSS -->
<ion-skeleton-text animated style="width: 60%"></ion-skeleton-text>
<ion-skeleton-text animated style="width: 100px"></ion-skeleton-text>

<!-- Or via class -->
<ion-skeleton-text animated class="skeleton-title"></ion-skeleton-text>
```

```css
.skeleton-title {
  width: 60%;
}
```

---

## ion-split-pane {#ion-split-pane}

- Converted to Shadow DOM.
- `main` attribute replaced by `contentId` (see [utilities.md](utilities.md#main-attribute)).

---

## ion-toast {#ion-toast}

### `showCloseButton` and `closeButtonText` removed

Replace with the `buttons` array using `role: 'cancel'`.

```typescript
// Before
const toast = await this.toastController.create({
  message: 'File saved.',
  showCloseButton: true,
  closeButtonText: 'Done'
});
await toast.present();
```

```typescript
// After
const toast = await this.toastController.create({
  message: 'File saved.',
  buttons: [
    {
      text: 'Done',
      role: 'cancel',
      handler: () => {
        console.log('Toast dismissed');
      }
    }
  ]
});
await toast.present();
```

The `buttons` array also supports additional action buttons (not just close):

```typescript
buttons: [
  {
    text: 'Undo',
    handler: () => { /* undo logic */ }
  },
  {
    text: 'Close',
    role: 'cancel'
  }
]
```
