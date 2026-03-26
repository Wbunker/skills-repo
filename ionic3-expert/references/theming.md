# Ionic 3 — Theming

Ionic 3 uses **SASS** (not CSS custom properties) for theming. The primary theming file is `src/theme/variables.scss`.

**Key difference from v4:** Everything is compiled at build time. Color values are baked into generated CSS — there is no runtime switching.

---

## The $colors Map

The `$colors` map is the central theming mechanism. It lives in `src/theme/variables.scss`.

```scss
// src/theme/variables.scss

$colors: (
  primary:    #488aff,
  secondary:  #32db64,
  danger:     #f53d3d,
  light:      #f4f4f4,
  dark:       #222
);
```

These color names are used by Ionic components via the `color` attribute:

```html
<button ion-button color="primary">Primary</button>
<button ion-button color="danger">Danger</button>
<ion-toolbar color="secondary">...</ion-toolbar>
<ion-badge color="dark">Badge</ion-badge>
```

### Adding Custom Colors

```scss
$colors: (
  primary:    #488aff,
  secondary:  #32db64,
  danger:     #f53d3d,
  light:      #f4f4f4,
  dark:       #222,
  // Custom colors:
  twitter:    #55acee,
  facebook:   #3b5998,
  brand:      #ff6b35
);
```

**Warning:** Each entry in `$colors` generates CSS for every Ionic component that supports the `color` attribute. Adding many colors inflates CSS bundle size.

### Base + Contrast Properties

For fine-grained control (e.g., a dark button with light text), use the `base`/`contrast` object form:

```scss
$colors: (
  primary: (
    base:     #488aff,
    contrast: #ffffff    // text/icon color on primary backgrounds
  ),
  danger: (
    base:     #f53d3d,
    contrast: #ffffff
  ),
  light: (
    base:     #f4f4f4,
    contrast: #000000
  ),
  twitter: (
    base:     #55acee,
    contrast: #ffffff
  )
);
```

When both forms are mixed, Ionic auto-generates contrast colors for flat strings (by calculating luminance). Explicit `contrast` gives you full control.

---

## The color() Function

To use `$colors` values in your own SASS:

```scss
// Syntax: color($colors, name, variant)
// variant: 'base' (default) or 'contrast'

.my-element {
  background-color: color($colors, primary);            // base color
  background-color: color($colors, primary, base);      // explicit base
  color: color($colors, primary, contrast);             // contrast color
  border: 1px solid color($colors, danger);
}
```

Or use SASS `map-get` directly for simpler cases:

```scss
// Only works when $colors uses the flat (non-base/contrast) form:
.my-element {
  color: map-get($colors, primary);
}
```

---

## Overriding Ionic SASS Variables

Ionic exposes hundreds of SASS variables. Override them **before** importing `ionic.scss`.

In `variables.scss`, override variables and then set the colors map:

```scss
// src/theme/variables.scss

// Color map
$colors: (
  primary:   #488aff,
  secondary: #32db64,
  danger:    #f53d3d,
  light:     #f4f4f4,
  dark:      #222
);

// Typography
$font-size-base:    14px;
$font-size-large:   20px;
$font-size-small:   12px;

// Toolbar
$toolbar-background:          #3880ff;
$toolbar-title-color:         #ffffff;
$toolbar-button-color:        #ffffff;
$toolbar-height:              56px;
$toolbar-height-md:           56px;
$toolbar-height-ios:          44px;

// Items
$item-background:             #ffffff;
$item-background-activated:   #e4e4e4;
$item-border-color:           #c8c7cc;
$item-font-size:              16px;

// Tabs
$tabs-background:             #f8f8f8;
$tabs-border-color:           #a2a4ab;
$tabs-tab-color-active:       #488aff;
$tabs-tab-color-inactive:     #8c8c8c;

// Cards
$card-background:             #fff;
$card-box-shadow:             0 2px 2px 0 rgba(0,0,0,.14), ...;

// Buttons
$button-border-radius:        4px;
$button-font-size:            1.4rem;

// Lists
$list-inset-margin-top:       16px;
$list-inset-margin-bottom:    16px;
```

---

## Platform-Specific Styling

Ionic 3 applies `.ios` or `.md` (Material Design) class to the `<body>` element based on the platform. This allows platform-specific SASS.

### In SASS

```scss
// Styles applied only on iOS
.ios {
  .my-header {
    background-color: #007aff;
  }
}

// Styles applied only on Android (MD)
.md {
  .my-header {
    background-color: #3f51b5;
  }
}

// Override a specific Ionic SASS variable per platform
.ios {
  $toolbar-background: #007aff !global;
}
.md {
  $toolbar-background: #3f51b5 !global;
}
```

### In TypeScript (Platform Detection)

```typescript
import { Platform } from 'ionic-angular';

constructor(private platform: Platform) {}

getIcon(): string {
  return this.platform.is('ios') ? 'ios-settings' : 'md-settings';
}

isAndroid(): boolean {
  return this.platform.is('android');
}
```

`platform.is()` accepts: `ios`, `android`, `windows`, `mobile`, `mobileweb`, `phablet`, `tablet`, `cordova`, `capacitor`, `electron`, `core`

### Platform-Specific Icons

```html
<!-- Auto-selects ios- or md- prefix -->
<ion-icon ios="ios-heart" md="md-heart"></ion-icon>

<!-- Or in TypeScript -->
<ion-icon [name]="platform.is('ios') ? 'ios-heart' : 'md-heart'"></ion-icon>
```

---

## Platform Mode Configuration

Force a specific mode in `app.module.ts`:

```typescript
IonicModule.forRoot(MyApp, {
  mode: 'md'          // Force Material Design everywhere
  // mode: 'ios'      // Force iOS everywhere
})
```

---

## Custom Component Theming

For page-level SASS, use the page's `.scss` file. Ionic scopes page CSS to that page automatically using the page's `selector`:

```scss
// home.scss
// Scoped to page-home selector (set in app.html class)
page-home {
  .my-card {
    margin: 16px;
    border-radius: 8px;
  }

  ion-item {
    border-left: 3px solid color($colors, primary);
  }
}
```

The selector `page-home` is Ionic's naming convention — it matches the auto-generated CSS class on the page host element.

---

## Global SASS

For styles that apply everywhere, add them to `src/app/app.scss`:

```scss
// src/app/app.scss

// Import custom fonts
@import url('https://fonts.googleapis.com/css?family=Raleway');

// Global overrides
ion-content {
  background-color: #f5f5f5;
}

// Utility classes
.text-muted {
  color: color($colors, light);
  font-size: 12px;
}

.section-header {
  padding: 8px 16px;
  background-color: map-get($colors, dark);
  color: white;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
```

---

## variables.scss Structure (Full Template)

```scss
// Ionic SASS Variables Reference: https://ionicframework.com/docs/theming/overriding-ionic-variables/

// $colors — the primary color map
$colors: (
  primary:    #488aff,
  secondary:  #32db64,
  danger:     #f53d3d,
  light:      #f4f4f4,
  dark:       #222
);

// Named color as base/contrast pair example:
// primary: (
//   base: #488aff,
//   contrast: #ffffff
// ),

// App-level SASS variables
$font-size-base: 14px;

// Toolbar
$toolbar-background: color($colors, primary);
```

---

## Responsive Utilities in SASS

Ionic 3 provides SASS mixins for responsive styles matching the grid breakpoints:

```scss
@import "~ionic-angular/themes/ionic.globals";
@import "~ionic-angular/themes/ionic.mixins";

// Respond to breakpoints
@include responsive-breakpoint-up(sm) {
  .my-element { display: flex; }
}

// Or use raw media queries with Ionic's breakpoint variables:
@media (min-width: $screen-sm-min) {
  .sidebar { display: block; }
}
```

Breakpoint variables: `$screen-xs-min`, `$screen-sm-min` (576px), `$screen-md-min` (768px), `$screen-lg-min` (992px), `$screen-xl-min` (1200px).

---

## Multiple Themes

To support multiple themes (e.g., a dark mode toggle), scope the `$colors` map within theme classes:

```scss
// Light theme (default — no class needed, or .light-theme)
.light-theme {
  $colors: (
    primary: #488aff,
    background: #ffffff
  ) !global;
  // Use Ionic component overrides here
}

// Dark theme
.dark-theme {
  $colors: (
    primary: #5c9aff,
    background: #1a1a2e
  ) !global;

  ion-content {
    background-color: #1a1a2e;
    color: #e0e0e0;
  }

  ion-item {
    background-color: #16213e;
    color: #e0e0e0;
  }
}
```

Apply in TypeScript by toggling a class on `document.body`:

```typescript
toggleDarkMode() {
  document.body.classList.toggle('dark-theme');
  document.body.classList.toggle('light-theme');
}
```

Note: Multi-theme SASS in v3 is more complex than v4's CSS custom properties, because SASS is compiled once at build time. Full runtime theming requires generating two separate CSS files.
