# CSS Variable Changes

## Global Variable Renames

| Old (Ionic 4) | New (Ionic 5) |
|---|---|
| `--ion-toolbar-color-unchecked` | `--ion-toolbar-segment-color` |
| `--ion-toolbar-color-checked` | `--ion-toolbar-segment-color-checked` |
| `--ion-toolbar-background-unchecked` | `--ion-toolbar-segment-background` |
| `--ion-toolbar-background-checked` | `--ion-toolbar-segment-background-checked` |
| `--ion-tab-bar-color-activated` | `--ion-tab-bar-color-selected` |

## Global Variable Additions (Ionic 5 only)

- `--ion-toolbar-segment-indicator-color`
- `--ion-toolbar-segment-background`
- `--ion-toolbar-segment-background-checked`

## Global Variable Removals

| Removed | Notes |
|---|---|
| `--ion-toolbar-color-activated` | no longer needed |
| `--ion-item-background-activated` | use component-level vars |
| `--ion-item-background-focused` | use component-level vars |
| `--ion-item-background-hover` | use component-level vars |

## State Color → Color + Opacity Split

This is the most pervasive theming change. Every component that had a single `--background-hover`, `--background-focused`, or `--background-activated` variable now has two variables: a **color** and a separate **opacity**.

This affects: Action Sheet, Back Button, Button, FAB Button, Item, Menu Button, Segment Button, Tab Button.

```css
/* Before: encode opacity inside the color */
ion-button {
  --background-hover: rgba(255, 255, 255, 0.08);
  --background-focused: rgba(255, 255, 255, 0.12);
  --background-activated: rgba(255, 255, 255, 0.16);
}

/* After: separate color and opacity */
ion-button {
  --background-hover: white;
  --background-hover-opacity: 0.08;
  --background-focused: white;
  --background-focused-opacity: 0.12;
  --background-activated: white;
  --background-activated-opacity: 0.16;
}
```

New opacity variables added everywhere:
- `--background-activated-opacity`
- `--background-focused-opacity`
- `--background-hover-opacity`

## Default Color Palette Updates

The defaults changed for several semantic colors. Only relevant if you use Ionic's built-in palette without overrides:

| Color | Ionic 4 | Ionic 5 |
|---|---|---|
| secondary | `#0cd1e8` | `#3dc2ff` |
| tertiary | `#7044ff` | `#5260ff` |
| success | `#10dc60` | `#2dd36f` |
| warning | `#ffce00` | `#ffc409` |
| danger | `#f04141` | `#eb445a` |
| medium | `#989aa2` | `#92949c` |

**Warning contrast** changed from `#ffffff` to `#000000`. If you display white text on the warning color, override it:
```css
:root {
  --ion-color-warning-contrast: #ffffff;
}
```

## Action Sheet CSS Variable Renames

The action sheet button variables got a `--button-` prefix:

| Old | New |
|---|---|
| `--background-activated` | `--button-background-activated` |
| `--background-selected` | `--button-background-selected` |

New button-scoped variables added:
- `--button-background`
- `--button-background-activated-opacity`
- `--button-background-focused`
- `--button-background-focused-opacity`
- `--button-background-hover`
- `--button-background-hover-opacity`
- `--button-background-selected-opacity`
- `--button-color`
- `--button-color-activated`
- `--button-color-focused`
- `--button-color-hover`
- `--button-color-selected`

## Segment Button CSS Variable Renames

| Old | New / Status |
|---|---|
| `--color-activated` | removed |
| `--background-activated` | removed |
| `--indicator-color-checked` | removed; use `--indicator-color` |

New/moved variables on `ion-segment-button`:
- `--background` (new)
- `--background-checked` (new)
- `--background-disabled` (moved from segment to button)
- `--background-hover` (new)
- `--color` (moved to button)
- `--color-checked` (moved to button)
- `--color-disabled` (moved to button)
- `--color-hover` (new)
- `--indicator-color` (now applies to checked state on both iOS and MD)

Note: segment CSS variables must be set on `ion-segment-button`, not inherited from `ion-segment`.

## Shadow DOM Components

Back Button, Card, and Split Pane converted to Shadow DOM in v5. Descendant CSS selectors no longer pierce them. Use CSS custom properties or `::part()` to style internals:

```css
/* Before (v4, descendant selector worked) */
ion-card .card-content { color: red; }

/* After (v5, use CSS custom property or ::part) */
ion-card {
  --color: red;
}
/* or if the part is exposed */
ion-card::part(native) { ... }
```
