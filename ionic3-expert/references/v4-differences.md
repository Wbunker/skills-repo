# Ionic 3 vs Ionic 4 — Key Differences

This reference covers what changed between Ionic 3 and Ionic 4. Useful for migrating v3 code to v4, or for understanding v3-specific patterns when working with legacy code.

---

## Summary Table

| Area | Ionic 3 | Ionic 4 |
|------|---------|---------|
| Package | `ionic-angular` | `@ionic/angular` |
| Framework | Angular only | Angular, React, Vue, vanilla JS |
| Navigation | Custom NavController push/pop stack | Angular Router + `<ion-router-outlet>` |
| Routing params | `NavParams` | `ActivatedRoute` |
| Root page | `rootPage = MyPage` in app component | Routes in `app-routing.module.ts` |
| Deep linking | `@IonicPage` decorator | Standard Angular lazy routes |
| CSS Theming | SASS `$colors` map + SASS variables | CSS custom properties (`--ion-color-*`) |
| Page wrapper | No wrapper required on page template | `<ion-page>` required |
| Back button | Rendered in `<ion-buttons start>` | Rendered in `<ion-buttons slot="start">` |
| Button element | `<button ion-button>` (attribute) | `<ion-button>` (web component) |
| Icon element | `<ion-icon>` with Ionic 3 icon names | `<ion-icon>` (new icon set) |
| Lifecycle hooks | `ionViewDidLoad`, `ionViewWillEnter`, etc. | Same hooks (Angular + Ionic lifecycle) |
| Component library | Angular directives/components | Web components via Stencil |
| Native runtime | Cordova (primary) | Capacitor (primary), Cordova supported |
| RxJS version | RxJS 5 (method chaining) | RxJS 6 (`.pipe()`) |
| NgModule | All pages in `entryComponents` or `@IonicPage` | Only root module; lazy routes auto-handled |
| Loading controller | `this.loading.present()` synchronous-style | `await this.loading.create(...)` then `await loading.present()` |

---

## Navigation: The Biggest Change

### Ionic 3: Push/Pop Stack

```typescript
// Navigate forward
this.navCtrl.push(DetailPage, { id: 5 });
this.navCtrl.push('DetailPage', { id: 5 });  // lazy loading

// Go back
this.navCtrl.pop();

// Replace root (e.g., after login)
this.navCtrl.setRoot(HomePage);

// Access passed data
constructor(private navParams: NavParams) {
  this.id = navParams.get('id');
}
```

### Ionic 4: Angular Router

```typescript
// Navigate forward
this.router.navigate(['/detail', 5]);
// or: <a routerLink="/detail/5" routerDirection="forward">

// Go back
this.navCtrl.navigateBack('/list');
// or: <ion-back-button defaultHref="/list">

// Replace root
this.navCtrl.navigateRoot('/home');

// Access route params
constructor(private route: ActivatedRoute) {}
ngOnInit() {
  this.id = this.route.snapshot.paramMap.get('id');
  // or: this.route.paramMap.subscribe(...)
}
```

### Passing Complex Data

In v3, objects can be pushed directly via NavParams. In v4, the router only handles URL params (strings). For complex objects, use a shared service:

```typescript
// v3 — pass object directly
this.navCtrl.push(DetailPage, { item: this.bigObject });

// v4 — pass ID, load object from service
this.router.navigate(['/detail', item.id]);
// In DetailPage: this.itemService.getById(id)
```

---

## Lifecycle Hooks

Both v3 and v4 support the same Ionic lifecycle hook names, but the context differs:

| Hook | v3 | v4 |
|------|----|----|
| `ionViewDidLoad` | Fires once when page instantiates | Deprecated in v4 (use `ngOnInit`) |
| `ionViewWillEnter` | Works as in v4 | Same — fires every time page enters |
| `ionViewDidEnter` | Works as in v4 | Same |
| `ionViewWillLeave` | Works as in v4 | Same |
| `ionViewDidLeave` | Works as in v4 | Same |
| `ionViewWillUnload` | Fires before destruction | Removed (use `ngOnDestroy`) |
| `ionViewCanEnter` | Return bool/Promise | Replaced by Angular Route Guards |
| `ionViewCanLeave` | Return bool/Promise | Replaced by Angular Route Guards |

In v4, `ionViewDidLoad` is not reliably called and was removed — use Angular's `ngOnInit` for one-time setup.

---

## Page Templates

### Ionic 3

```html
<!-- No <ion-page> wrapper needed -->
<ion-header>
  <ion-toolbar>
    <ion-buttons start>
      <button ion-button (click)="navCtrl.pop()">
        <ion-icon name="arrow-back"></ion-icon>
      </button>
    </ion-buttons>
    <ion-title>Title</ion-title>
  </ion-toolbar>
</ion-header>

<ion-content padding>
  <p>Content here</p>
</ion-content>
```

### Ionic 4

```html
<!-- <ion-page> wrapper REQUIRED in v4 -->
<ion-page>
  <ion-header>
    <ion-toolbar>
      <ion-buttons slot="start">
        <ion-back-button></ion-back-button>
      </ion-buttons>
      <ion-title>Title</ion-title>
    </ion-toolbar>
  </ion-header>

  <ion-content>
    <p>Content here</p>
  </ion-content>
</ion-page>
```

Key differences:
- v4 requires `<ion-page>` wrapper on every page
- v4 uses `slot="start"` / `slot="end"` for button placement (not `start`/`end` attributes)
- v4 back button is `<ion-back-button>` (web component, not `<button ion-button>`)

---

## Button Syntax

```html
<!-- Ionic 3 — attribute on <button> -->
<button ion-button color="primary">Submit</button>
<button ion-button icon-only>
  <ion-icon name="heart"></ion-icon>
</button>
<button ion-button clear round>Clear Round</button>

<!-- Ionic 4 — standalone web component -->
<ion-button color="primary">Submit</ion-button>
<ion-button fill="clear" shape="round">Clear Round</ion-button>
```

---

## Module Structure

### Ionic 3

```typescript
// app.module.ts — all pages registered here OR via @IonicPage
@NgModule({
  declarations: [MyApp, HomePage, LoginPage],
  imports: [IonicModule.forRoot(MyApp)],
  bootstrap: [IonicApp],
  entryComponents: [MyApp, HomePage, LoginPage],
  providers: [...]
})
```

### Ionic 4

```typescript
// app.module.ts — minimal, routing handled separately
@NgModule({
  declarations: [AppComponent],
  imports: [
    BrowserModule,
    IonicModule.forRoot(),   // no root component passed
    AppRoutingModule
  ],
  bootstrap: [AppComponent],
  providers: [...]
})
```

```typescript
// app-routing.module.ts
const routes: Routes = [
  {
    path: 'home',
    loadChildren: () => import('./home/home.module').then(m => m.HomePageModule)
  },
  { path: '', redirectTo: 'home', pathMatch: 'full' }
];
```

---

## SASS vs CSS Custom Properties

### Ionic 3 (SASS)

```scss
// variables.scss
$colors: (
  primary: #488aff,
  secondary: #32db64,
  danger: #f53d3d
);

// Custom component style
.my-button {
  background-color: color($colors, primary);
  color: color($colors, primary, contrast);
}
```

Compiled at build time — cannot be changed at runtime.

### Ionic 4 (CSS Custom Properties)

```css
/* variables.css */
:root {
  --ion-color-primary: #3880ff;
  --ion-color-primary-shade: #3171e0;
  --ion-color-primary-contrast: #ffffff;
}

/* Custom component style */
.my-button {
  background-color: var(--ion-color-primary);
  color: var(--ion-color-primary-contrast);
}
```

Can be changed at runtime (JavaScript sets CSS vars on `:root` or a parent element).

---

## Overlay Controller Changes

### Ionic 3 (synchronous create)

```typescript
const loading = this.loadingCtrl.create({ content: 'Loading...' });
loading.present();
// ... later:
loading.dismiss();
```

### Ionic 4 (async create)

```typescript
const loading = await this.loadingCtrl.create({ message: 'Loading...' });
await loading.present();
// ... later:
await loading.dismiss();
```

In v4, `create()` returns a Promise. All overlay controllers require `await`.

Note: `content` option renamed to `message` in v4.

---

## @IonicPage vs Angular Lazy Routes

### Ionic 3 — @IonicPage Decorator

```typescript
@IonicPage({
  name: 'detail-page',
  segment: 'detail/:id'
})
@Component({ templateUrl: 'detail.html' })
export class DetailPage {}
```

```typescript
// Navigate by string
this.navCtrl.push('DetailPage', { id: 5 });
```

### Ionic 4 — Standard Angular Lazy Routes

```typescript
// No decorator — standard Angular route
@Component({ templateUrl: 'detail.page.html' })
export class DetailPage {}
```

```typescript
// app-routing.module.ts
{
  path: 'detail/:id',
  loadChildren: () => import('./detail/detail.module').then(m => m.DetailPageModule)
}
```

```typescript
// Navigate
this.router.navigate(['/detail', 5]);
```

---

## Icon Changes

Ionic 4 ships Ionicons 5 (a new icon set). Many v3 icon names changed:

| Ionic 3 | Ionic 4 |
|---------|---------|
| `ios-home` / `md-home` | `home` (auto platform) |
| `ios-arrow-back` | `arrow-back` |
| `ios-list` | `list` |
| `ios-close` | `close` |

In v3, use `ios="ios-home" md="md-home"` for platform-specific icons. In v4, a single name like `"home"` works everywhere.

---

## Removed in Ionic 4

| Ionic 3 Feature | Ionic 4 Status |
|----------------|----------------|
| `@IonicPage` decorator | Removed — use Angular lazy routes |
| `ion-nav` as main navigation | Replaced by `<ion-router-outlet>` |
| `NavController.push/pop` | `NavController.navigateForward/Back` or Angular Router |
| `NavParams` | `ActivatedRoute.snapshot.paramMap` |
| `ion-select-option` named `ion-option` | Renamed to `<ion-select-option>` |
| `button ion-button` (attribute) | `<ion-button>` web component |
| `ion-back-button` as attribute | `<ion-back-button>` web component |
| `item-start` / `item-end` attributes | `slot="start"` / `slot="end"` |
| `<ion-label floating>` (attribute) | `<ion-label position="floating">` |
| `IonicModule.forRoot(MyApp)` with root component | `IonicModule.forRoot()` (no args) |
| `bootstrap: [IonicApp]` | `bootstrap: [AppComponent]` |
| `ionViewWillUnload` | Use `ngOnDestroy` |
| `ionViewCanEnter` / `ionViewCanLeave` | Angular Route Guards |
| `Events` service (pub/sub) | RxJS Subjects / Angular services |
| Ionic 1 `$ionicModal` style | N/A (v3 already rewrote this) |
