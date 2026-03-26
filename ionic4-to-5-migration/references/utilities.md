# CSS Utility Attributes → Classes

## The Core Change

In Ionic 4, many spacing and alignment helpers were applied as bare HTML attributes. Ionic 5 removes all of these — they are now `ion-` prefixed CSS classes.

**Search pattern:** look for bare attributes on `ion-*` elements like `padding`, `text-center`, `text-wrap`, `margin`, `push-*`, `pull-*`, `offset-*`, etc.

## Full Attribute → Class Map

| Before (attribute) | After (class) |
|---|---|
| `padding` | `ion-padding` |
| `padding-top` | `ion-padding-top` |
| `padding-bottom` | `ion-padding-bottom` |
| `padding-start` | `ion-padding-start` |
| `padding-end` | `ion-padding-end` |
| `padding-horizontal` | `ion-padding-horizontal` |
| `padding-vertical` | `ion-padding-vertical` |
| `margin` | `ion-margin` |
| `margin-top` | `ion-margin-top` |
| `margin-bottom` | `ion-margin-bottom` |
| `margin-start` | `ion-margin-start` |
| `margin-end` | `ion-margin-end` |
| `margin-horizontal` | `ion-margin-horizontal` |
| `margin-vertical` | `ion-margin-vertical` |
| `float-start` | `ion-float-start` |
| `float-end` | `ion-float-end` |
| `float-left` | `ion-float-left` |
| `float-right` | `ion-float-right` |
| `text-start` | `ion-text-start` |
| `text-end` | `ion-text-end` |
| `text-left` | `ion-text-left` |
| `text-right` | `ion-text-right` |
| `text-center` | `ion-text-center` |
| `text-justify` | `ion-text-justify` |
| `text-wrap` | `ion-text-wrap` |
| `text-nowrap` | `ion-text-nowrap` |
| `text-uppercase` | `ion-text-uppercase` |
| `text-lowercase` | `ion-text-lowercase` |
| `text-capitalize` | `ion-text-capitalize` |
| `wrap` | `ion-wrap` |
| `nowrap` | `ion-nowrap` |
| `hide` | `ion-hide` |
| `show` | `ion-show` |

### Grid / Column Offset / Push / Pull

| Before (attribute) | After (class) |
|---|---|
| `offset-N` | `ion-offset-N` |
| `offset-sm-N` | `ion-offset-sm-N` |
| `offset-md-N` | `ion-offset-md-N` |
| `offset-lg-N` | `ion-offset-lg-N` |
| `offset-xl-N` | `ion-offset-xl-N` |
| `push-N` | `ion-push-N` |
| `pull-N` | `ion-pull-N` |

## Examples

```html
<!-- Before -->
<ion-content padding>
  <ion-label text-wrap>Long text here</ion-label>
  <ion-col push-3>...</ion-col>
  <div text-center>Centered</div>
</ion-content>

<!-- After -->
<ion-content class="ion-padding">
  <ion-label class="ion-text-wrap">Long text here</ion-label>
  <ion-col class="ion-push-3">...</ion-col>
  <div class="ion-text-center">Centered</div>
</ion-content>
```

## `no-border` Attribute

```html
<!-- Before -->
<ion-header no-border>...</ion-header>
<ion-footer no-border>...</ion-footer>

<!-- After -->
<ion-header class="ion-no-border">...</ion-header>
<ion-footer class="ion-no-border">...</ion-footer>
```

## `main` Attribute (Menu / Split Pane Content Target)

`main` was used to mark which element is the main content area alongside a menu or split pane. It's been replaced by `contentId` / `content-id`.

```html
<!-- Before -->
<ion-split-pane>
  <ion-menu></ion-menu>
  <ion-router-outlet main></ion-router-outlet>
</ion-split-pane>

<ion-menu></ion-menu>
<ion-router-outlet main></ion-router-outlet>
```

```html
<!-- After (Angular / React — camelCase property) -->
<ion-split-pane contentId="main-content">
  <ion-menu contentId="main-content"></ion-menu>
  <ion-router-outlet id="main-content"></ion-router-outlet>
</ion-split-pane>

<!-- After (Vue / vanilla — kebab-case attribute) -->
<ion-split-pane content-id="main-content">
  <ion-menu content-id="main-content"></ion-menu>
  <ion-router-outlet id="main-content"></ion-router-outlet>
</ion-split-pane>
```

## `.activated` State Class

```css
/* Before */
.activated { ... }

/* After */
.ion-activated { ... }
```

## Responsive Hide/Show Breakpoint Changes

The breakpoint values for responsive display classes shifted in v5:

| Class | Ionic 4 (max-width) | Ionic 5 (max-width) |
|---|---|---|
| `.ion-hide-down` | 575px | always hidden |
| `.ion-hide-sm-down` | 767px | 576px |
| `.ion-hide-md-down` | 991px | 768px |
| `.ion-hide-lg-down` | 1199px | 992px |
| `.ion-hide-xl-down` | always hidden | 1200px |

If you relied on specific breakpoints, verify your responsive layout still works as intended.
