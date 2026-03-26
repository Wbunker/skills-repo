# Ionic 4 — Theming & CSS Custom Properties

## How Theming Works in v4

Ionic v4 replaced SASS variables (used in v3) with **CSS custom properties** (CSS variables). Every color and spacing value is a CSS variable you can override in `src/theme/variables.css` or `src/global.scss`.

---

## Color System

Ionic uses 9 named colors. Each color has 5 variants automatically generated:

| Property | Meaning |
|----------|---------|
| `--ion-color-primary` | Base color |
| `--ion-color-primary-rgb` | RGB values (for opacity/rgba use) |
| `--ion-color-primary-contrast` | Text color on this background |
| `--ion-color-primary-contrast-rgb` | RGB of contrast |
| `--ion-color-primary-shade` | Slightly darker shade |
| `--ion-color-primary-tint` | Slightly lighter tint |

### Default Colors

| Name | Default |
|------|---------|
| `primary` | `#3880ff` (blue) |
| `secondary` | `#3dc2ff` (cyan) |
| `tertiary` | `#5260ff` (purple) |
| `success` | `#2dd36f` (green) |
| `warning` | `#ffc409` (yellow) |
| `danger` | `#eb445a` (red) |
| `dark` | `#222428` |
| `medium` | `#92949c` |
| `light` | `#f4f5f8` |

### Changing a Color

Edit `src/theme/variables.css`:

```css
:root {
  --ion-color-primary: #ff6b35;
  --ion-color-primary-rgb: 255, 107, 53;
  --ion-color-primary-contrast: #ffffff;
  --ion-color-primary-contrast-rgb: 255, 255, 255;
  --ion-color-primary-shade: #e05e2e;
  --ion-color-primary-tint: #ff7a49;
}
```

Use the **Ionic Color Generator** at https://ionicframework.com/docs/theming/color-generator to auto-generate all 5 variants from a single hex color.

---

## Adding a Custom Color

```css
/* In variables.css */
:root {
  --ion-color-brand: #ff6b35;
  --ion-color-brand-rgb: 255, 107, 53;
  --ion-color-brand-contrast: #ffffff;
  --ion-color-brand-contrast-rgb: 255, 255, 255;
  --ion-color-brand-shade: #e05e2e;
  --ion-color-brand-tint: #ff7a49;
}
```

```css
/* In global.scss — create the .ion-color-brand class */
.ion-color-brand {
  --ion-color-base: var(--ion-color-brand);
  --ion-color-base-rgb: var(--ion-color-brand-rgb);
  --ion-color-contrast: var(--ion-color-brand-contrast);
  --ion-color-contrast-rgb: var(--ion-color-brand-contrast-rgb);
  --ion-color-shade: var(--ion-color-brand-shade);
  --ion-color-tint: var(--ion-color-brand-tint);
}
```

```html
<!-- Now usable as a color value -->
<ion-button color="brand">Brand Button</ion-button>
```

---

## Global CSS Variables

```css
:root {
  /* App background */
  --ion-background-color: #ffffff;
  --ion-background-color-rgb: 255, 255, 255;

  /* Text */
  --ion-text-color: #000000;
  --ion-text-color-rgb: 0, 0, 0;

  /* Toolbar */
  --ion-toolbar-background: #f8f8f8;
  --ion-toolbar-color: #424242;

  /* Item */
  --ion-item-background: #ffffff;

  /* Border */
  --ion-border-color: #c8c7cc;

  /* Font */
  --ion-font-family: 'Roboto', sans-serif;
}
```

---

## Component-Level CSS Variables

Most Ionic components expose their own CSS variables for fine-grained control:

```css
/* IonButton */
ion-button {
  --background: #ff6b35;
  --background-activated: #e05e2e;
  --border-radius: 8px;
  --padding-start: 24px;
  --padding-end: 24px;
}

/* IonToolbar */
ion-toolbar {
  --background: #1a1a2e;
  --color: #ffffff;
  --border-width: 0;
}

/* IonItem */
ion-item {
  --background: transparent;
  --border-color: #e0e0e0;
  --padding-start: 16px;
}

/* IonCard */
ion-card {
  --background: #f5f5f5;
  --color: #333;
  --box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
```

---

## Platform-Specific Styling

Ionic adds `.ios` or `.md` class to `<body>` based on platform:

```css
/* iOS only */
.ios ion-toolbar {
  --background: rgba(255,255,255,0.9);
}

/* Material Design (Android) only */
.md ion-toolbar {
  --background: #1a1a2e;
}
```

In TypeScript:

```typescript
import { Platform } from '@ionic/angular';

constructor(private platform: Platform) {}

get isIOS() { return this.platform.is('ios'); }
get isAndroid() { return this.platform.is('android'); }
get isMobile() { return this.platform.is('mobile'); }
get isDesktop() { return this.platform.is('desktop'); }
```

---

## Dark Mode

### Manual dark mode class

```css
/* In variables.css */
body.dark {
  --ion-background-color: #121212;
  --ion-background-color-rgb: 18, 18, 18;
  --ion-text-color: #ffffff;
  --ion-text-color-rgb: 255, 255, 255;
  --ion-border-color: #333333;
  --ion-item-background: #1e1e1e;
  --ion-toolbar-background: #1f1f1f;
  --ion-toolbar-color: #ffffff;

  --ion-color-primary: #428cff;
  --ion-color-primary-rgb: 66, 140, 255;
  /* ... adjust other colors for dark mode ... */
}
```

```typescript
// Toggle dark mode
toggleDarkMode(enable: boolean) {
  document.body.classList.toggle('dark', enable);
}
```

### System dark mode (prefers-color-scheme)

```css
@media (prefers-color-scheme: dark) {
  body {
    --ion-background-color: #121212;
    --ion-text-color: #ffffff;
    /* ... */
  }
}
```

---

## Styling Individual Pages / Components

Page `.scss` files are scoped (Angular ViewEncapsulation). For component-specific overrides:

```scss
// home.page.scss
:host {
  ion-item {
    --background: #fafafa;
  }
}

.custom-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

For overriding overlays (modals, alerts etc.) that render outside the component scope, use `global.scss`:

```scss
// global.scss
.my-custom-modal {
  --height: 300px;
  --border-radius: 20px 20px 0 0;
}

.custom-alert .alert-button.confirm-btn {
  color: var(--ion-color-danger);
  font-weight: bold;
}
```

Pass `cssClass` in the controller to target these:

```typescript
const modal = await this.modalCtrl.create({
  component: MyModal,
  cssClass: 'my-custom-modal'
});
```

---

## Typography

```css
:root {
  --ion-font-family: 'Poppins', sans-serif;
}
```

```html
<!-- In index.html, load the font: -->
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
```

Ionic uses these heading classes you can apply to any element:
`<h1>`, `<h2>`, `<h3>`, `<p>`, `<ion-note>`, `<ion-label>`
