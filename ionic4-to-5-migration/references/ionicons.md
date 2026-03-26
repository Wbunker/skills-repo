# Ionicons 5

Ionicons was completely redesigned for v5. Every icon was redrawn and the icon variant system changed.

## Install

```bash
npm install ionicons@5
```

## Three Variants Per Icon

Every icon now comes in three variants:
- **Default (filled)**: `camera`
- **Outline**: `camera-outline`
- **Sharp**: `camera-sharp`

Use the `name` attribute to select a specific variant, or use `ios` and `md` attributes for platform-specific rendering:

```html
<!-- Single variant, same on all platforms -->
<ion-icon name="camera"></ion-icon>
<ion-icon name="camera-outline"></ion-icon>
<ion-icon name="camera-sharp"></ion-icon>

<!-- Platform-specific (iOS gets outline, Android gets sharp) -->
<ion-icon ios="camera-outline" md="camera-sharp"></ion-icon>
```

## Auto Platform-Switching Removed

In Ionicons 4, icons automatically rendered in an iOS or Material Design style depending on the platform. This is **gone**.

```html
<!-- Before: auto-switched between iOS and MD designs -->
<ion-icon name="camera"></ion-icon>
<!-- On iOS: rendered thin/outline iOS style -->
<!-- On Android: rendered filled MD style -->

<!-- After: same icon regardless of platform -->
<ion-icon name="camera"></ion-icon>
<!-- Shows the filled variant on all platforms -->
```

To restore per-platform icons, use the `ios` and `md` attributes explicitly:
```html
<ion-icon ios="camera-outline" md="camera-sharp"></ion-icon>
```

## Common Icon Name Changes

Some icon names changed between Ionicons 4 and 5. Check the Ionicons website for the new name if an icon isn't rendering.

| Old name (v4) | New name (v5) |
|---|---|
| `add-circle-outline` | `add-circle-outline` (same) |
| `arrow-back` | `arrow-back-outline` or `arrow-back` |
| `arrow-forward` | `arrow-forward-outline` or `arrow-forward` |
| `checkmark` | `checkmark` (same) |
| `close` | `close` (same) |
| `create` | `create-outline` or `create` |
| `home` | `home` (same) |
| `menu` | `menu` (same) |
| `more` | `ellipsis-vertical` or `ellipsis-horizontal` |
| `person` | `person` (same) |
| `search` | `search` (same) |
| `settings` | `settings` (same) |
| `star` | `star` (same) |
| `trash` | `trash` (same) |

Note: many icons kept the same name. If an icon renders as a question mark or not at all, search the [Ionicons website](https://ionic.io/ionicons) for the v5 name.

## Usage in Angular Templates

```html
<!-- Use any of these patterns -->
<ion-icon name="heart"></ion-icon>
<ion-icon name="heart-outline"></ion-icon>
<ion-icon ios="heart-outline" md="heart"></ion-icon>

<!-- Dynamic icon name from component -->
<ion-icon [name]="iconName"></ion-icon>
```

## Self-Hosted Icons (SVG)

You can also use custom SVG icons:
```html
<ion-icon src="/assets/icons/custom.svg"></ion-icon>
```

## Reduced Bundle Size

Ionicons 5 is tree-shakeable when used with modern bundlers. Only icons you reference are included in the final bundle. In lazy-loaded Ionic apps this happens automatically.
