# Tooling & Package Versions

## Package Installation

```bash
# Angular
npm install @ionic/angular@5 @ionic/angular-toolkit@2.2.0 ionicons@5

# React
npm install @ionic/react@5 @ionic/react-router@5 ionicons@5

# Vanilla / Stencil
npm install @ionic/core@5 ionicons@5
```

## Angular Version Compatibility Matrix

| @ionic/angular | @ionic/angular-toolkit | Angular |
|---|---|---|
| 5.0.x | 2.1.x | ^8.2 |
| 5.x | 2.2.0 | ^9.x (Ivy) |
| 5.x | 3.x | ^11.0 |

- Ionic 5.0.0 shipped targeting Angular 8.
- Angular 9 / Ivy support arrived with `@ionic/angular-toolkit` 2.2.0 (Feb 2020).
- `@ionic/angular-toolkit` 3.0.0 requires Angular 11+.
- Run Angular upgrade separately: `ng update @angular/cli @angular/core`

## Angular 9 / Ivy

No code changes are required for Ivy compatibility. Benefits include smaller bundle sizes via tree-shaking.

One cleanup you can do (optional but recommended under Ivy):
```typescript
// Before: entryComponents needed for dynamically created overlays
@NgModule({
  entryComponents: [MyComponent],  // remove this
  ...
})
```
Under Ivy (Angular 9+), `entryComponents` is ignored and can be deleted.

## Native Bridge Versions

| Bridge | Compatible version |
|---|---|
| Capacitor | 2.x |
| cordova-android | 8.x |
| cordova-ios | 5.x |

## SCSS Distribution Removed

Ionic no longer ships SCSS source files in `dist/`. If you were importing framework SCSS directly (e.g., `@import "~@ionic/angular/css/ionic.bundle.css"` variants), you need to switch to CSS custom properties for all theming.

The standard `ionic.bundle.css` import still works:
```scss
// global.scss — still valid
@import "~@ionic/angular/css/normalize.css";
@import "~@ionic/angular/css/structure.css";
@import "~@ionic/angular/css/typography.css";
@import "~@ionic/angular/css/display.css";
@import "~@ionic/angular/css/padding.css";
@import "~@ionic/angular/css/float-elements.css";
@import "~@ionic/angular/css/text-alignment.css";
@import "~@ionic/angular/css/text-transformation.css";
@import "~@ionic/angular/css/flex-utils.css";
```

What is removed: internal framework `.scss` partials that some projects imported to override component internals with SCSS variables. Those SCSS variables no longer exist — use CSS custom properties on the components instead.

## Checking Your Current Version

```bash
ionic info        # shows @ionic/angular and CLI versions
npm list @ionic/angular
```
