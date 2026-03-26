# Ionic 4 — Breaking Changes & Migration from v3

## Summary of Major Changes

| Area | Ionic v3 | Ionic v4 |
|------|-----------|-----------|
| npm package | `ionic-angular` | `@ionic/angular` |
| Angular CLI | Not used | Standard Angular CLI |
| Navigation | NavController push/pop | Angular Router + IonRouterOutlet |
| Lazy loading | `@IonicPage()` decorator | Router `loadChildren` |
| Lifecycle hooks | `ionViewCanLeave`, `ionViewCanEnter` removed | Angular lifecycle + Ionic events |
| Overlay API | Synchronous | Async/await (Promises) |
| HTML element syntax | `<button ion-button>` | `<ion-button>` |
| Slot attributes | `end`, `start` as element attrs | `slot="end"`, `slot="start"` |
| Module setup | `IonicPageModule.forRoot()` | `IonicModule` (per page) |
| Config file | `ionic.config.json` type: `ionic-angular` | type: `angular` |
| SASS theming | SASS variables | CSS custom properties |
| RxJS | v5 | v6 |
| Services folder | `src/providers/` | `src/app/services/` (convention) |
| Global styles | `src/app/app.scss` | `src/global.scss` |
| Ionic Native | `/ngx` not required | `/ngx` suffix required |

---

## Package Change

```bash
# Remove v3
npm uninstall ionic-angular

# Install v4
npm install @ionic/angular@4

# Update all imports from:
import { ... } from 'ionic-angular';
# To:
import { ... } from '@ionic/angular';
```

---

## Navigation: The Biggest Change

### v3 — NavController push/pop

```typescript
// v3 navigation
import { NavController, NavParams } from 'ionic-angular';

constructor(private navCtrl: NavController, private navParams: NavParams) {}

goToDetail() {
  this.navCtrl.push('DetailPage', { id: 42 });
}

goBack() {
  this.navCtrl.pop();
}

// Receive params
const id = this.navParams.get('id');
```

### v4 — Angular Router

```typescript
// v4 navigation
import { Router } from '@angular/router';
import { NavController } from '@ionic/angular';
import { ActivatedRoute } from '@angular/router';

constructor(
  private router: Router,
  private navCtrl: NavController,
  private route: ActivatedRoute
) {}

goToDetail() {
  // Angular Router (no animation direction)
  this.router.navigate(['/detail', 42]);

  // NavController (animated — recommended for Ionic feel)
  this.navCtrl.navigateForward('/detail/42');
}

goBack() {
  this.navCtrl.back();
  // or: this.location.back();
}

// Receive params via ActivatedRoute
ngOnInit() {
  const id = this.route.snapshot.paramMap.get('id');
}
```

### v4 NavController methods

| v3 | v4 equivalent |
|----|---------------|
| `navCtrl.push('/page')` | `navCtrl.navigateForward('/page')` |
| `navCtrl.pop()` | `navCtrl.back()` or `navCtrl.navigateBack('/page')` |
| `navCtrl.setRoot('/page')` | `navCtrl.navigateRoot('/page')` |
| `navParams.get('key')` | `activatedRoute.snapshot.paramMap.get('key')` |

---

## Lazy Loading: @IonicPage → loadChildren

### v3 — @IonicPage decorator

```typescript
// v3 — decorator on the page class
import { IonicPage } from 'ionic-angular';

@IonicPage()
@Component({ ... })
export class DetailPage {}
```

### v4 — Router loadChildren

```typescript
// v4 — in app-routing.module.ts
{
  path: 'detail/:id',
  loadChildren: () => import('./pages/detail/detail.module')
    .then(m => m.DetailPageModule)
}

// Each page has its own module:
// detail.module.ts
@NgModule({
  imports: [
    CommonModule,
    IonicModule,
    RouterModule.forChild([{ path: '', component: DetailPage }])
  ],
  declarations: [DetailPage]
})
export class DetailPageModule {}
```

---

## HTML Template Syntax Changes

### Element names — all become web components

```html
<!-- v3 -->
<button ion-button color="primary">Click</button>
<button ion-button icon-only>
  <ion-icon name="add"></ion-icon>
</button>

<!-- v4 -->
<ion-button color="primary">Click</ion-button>
<ion-button>
  <ion-icon slot="icon-only" name="add"></ion-icon>
</ion-button>
```

### Slots replace positional attributes

```html
<!-- v3 -->
<ion-navbar>
  <ion-buttons end>
    <button ion-button>Edit</button>
  </ion-buttons>
</ion-navbar>

<!-- v4 -->
<ion-toolbar>
  <ion-buttons slot="end">
    <ion-button>Edit</ion-button>
  </ion-buttons>
</ion-toolbar>
```

### Component renames

| v3 | v4 |
|----|-----|
| `<ion-navbar>` | `<ion-toolbar>` (inside `<ion-header>`) |
| `<button ion-button>` | `<ion-button>` |
| `<button ion-item>` | `<ion-item button>` |
| `<ion-list no-lines>` | `<ion-list lines="none">` |
| `<ion-item-divider>` | `<ion-item-divider>` (unchanged) |
| `<ion-spinner>` | `<ion-spinner>` (unchanged) |
| `<ion-select multiple>` | `<ion-select multiple="true">` |

---

## Module Setup Changes

### v3

```typescript
// v3 — each page module used IonicPageModule.forRoot()
import { IonicPageModule } from 'ionic-angular';

@NgModule({
  declarations: [HomePage],
  imports: [IonicPageModule.forRoot(HomePage)]
})
export class HomePageModule {}
```

### v4

```typescript
// v4 — use plain IonicModule in each page module
import { IonicModule } from '@ionic/angular';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    HomePageRoutingModule
  ],
  declarations: [HomePage]
})
export class HomePageModule {}
```

Root module also changes — `IonicModule.forRoot()` is called once in `app.module.ts`, not in page modules.

---

## Overlay API: Synchronous → Async/Await

### v3 — synchronous

```typescript
// v3
const alert = this.alertCtrl.create({
  title: 'Confirm',
  message: 'Are you sure?',
  buttons: ['OK']
});
alert.present();
```

### v4 — async/await

```typescript
// v4
const alert = await this.alertCtrl.create({
  header: 'Confirm',
  message: 'Are you sure?',
  buttons: ['OK']
});
await alert.present();
```

All overlay controllers (AlertController, ModalController, ToastController, LoadingController, ActionSheetController) are now async in v4. Always `await` both `create()` and `present()`.

Also note: `title` → `header`, `subTitle` → `subHeader`.

---

## Lifecycle Hooks Changes

### Removed in v4

- `ionViewCanEnter()` — replaced by Angular route guards (`CanActivate`)
- `ionViewCanLeave()` — replaced by Angular route guards (`CanDeactivate`)
- `ionViewDidLoad()` — replaced by `ngOnInit()`

### Retained in v4

```typescript
// These still work in v4 (Ionic-specific, fire on every navigation)
ionViewWillEnter() {}    // fires every time page becomes active
ionViewDidEnter() {}     // fires after page transition completes
ionViewWillLeave() {}    // fires before page leaves screen
ionViewDidLeave() {}     // fires after page has left screen
```

### v4 Angular hooks also apply

```typescript
ngOnInit() {}      // fires once when page component is created
ngOnDestroy() {}   // fires when page component is destroyed (popped)
```

Key: In v4, Ionic pages are **cached** in the DOM when navigating away (in tab apps). `ngOnInit` only fires once; `ionViewWillEnter` fires every visit. Use `ionViewWillEnter` to refresh data.

---

## RxJS v5 → v6 Migration

### Import paths changed

```typescript
// v3/RxJS 5
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import { Observable } from 'rxjs/Observable';

// v4/RxJS 6
import { Observable } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
// Operators are now used via .pipe()
```

### pipe() required

```typescript
// v3
this.http.get(url).map(data => data).catch(err => err);

// v4
this.http.get(url).pipe(
  map(data => data),
  catchError(err => throwError(err))
);
```

---

## @ionic-native: /ngx Suffix Required

```typescript
// v3 — import without /ngx
import { Camera } from '@ionic-native/camera';

// v4 — must import from /ngx for Angular DI to work
import { Camera } from '@ionic-native/camera/ngx';
```

The `/ngx` path provides an `@Injectable()` class instead of a plain object, enabling Angular's dependency injection.

---

## RouteReuseStrategy — Required for Tab Caching

In v4, add `IonicRouteStrategy` to preserve tab page state when switching tabs:

```typescript
// app.module.ts
import { RouteReuseStrategy } from '@angular/router';
import { IonicRouteStrategy } from '@ionic/angular';

providers: [
  { provide: RouteReuseStrategy, useClass: IonicRouteStrategy }
]
```

Without this, navigating between tabs destroys and recreates each tab's page, losing scroll position and state.

---

## Quick Migration Checklist

- [ ] Replace `ionic-angular` imports with `@ionic/angular`
- [ ] Replace `@IonicPage()` decorator with router `loadChildren`
- [ ] Replace `NavController.push/pop` with `navigateForward/back` or Angular Router
- [ ] Replace `NavParams` with `ActivatedRoute`
- [ ] Replace `IonicPageModule.forRoot()` with `IonicModule` in page modules
- [ ] Update all overlay calls to `async/await`
- [ ] Rename `title` → `header`, `subTitle` → `subHeader` in alerts
- [ ] Rename `<ion-navbar>` → `<ion-toolbar>`
- [ ] Rename `<button ion-button>` → `<ion-button>`
- [ ] Replace positional attrs (`end`, `start`) with `slot="end"`, `slot="start"`
- [ ] Update `@ionic-native` imports to use `/ngx` suffix
- [ ] Migrate RxJS to v6 (use `pipe()`, update import paths)
- [ ] Remove `ionViewCanEnter/Leave` — use Angular route guards
- [ ] Remove `ionViewDidLoad` — use `ngOnInit`
- [ ] Add `IonicRouteStrategy` to `app.module.ts` providers
- [ ] Move global styles from `app.scss` to `global.scss`
- [ ] Update `ionic.config.json` `type` from `ionic-angular` to `angular`

Use the official TSLint migration tool to auto-detect many of these issues:
```bash
npm install -g @ionic/v4-migration-tslint
```
