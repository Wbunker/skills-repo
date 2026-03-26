# Ionic 4 — Navigation

## The v4 Navigation Model

Ionic v4 replaced v3's NavController push/pop stack with **Angular Router**. Every navigation is a URL change. `IonRouterOutlet` is an enhanced `<router-outlet>` that adds Ionic's page transitions and lifecycle events.

---

## Basic Routing Setup

### app-routing.module.ts

```typescript
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  { path: '', redirectTo: 'home', pathMatch: 'full' },
  {
    path: 'home',
    loadChildren: () => import('./pages/home/home.module')
      .then(m => m.HomePageModule)
  },
  {
    path: 'detail/:id',
    loadChildren: () => import('./pages/detail/detail.module')
      .then(m => m.DetailPageModule)
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
```

Each page uses `loadChildren` for lazy loading — the default when using `ionic generate page`.

---

## NavController — Animated Navigation

While Angular Router handles routing, `NavController` wraps it with Ionic's animated transitions (forward slide, back slide).

```typescript
import { NavController } from '@ionic/angular';

constructor(private navCtrl: NavController) {}

// Navigate forward (slides in from right)
this.navCtrl.navigateForward('/detail/42');
this.navCtrl.navigateForward(['/detail', item.id]);

// Navigate back (slides out to right)
this.navCtrl.navigateBack('/home');

// Navigate root (clears stack, no animation or fade)
this.navCtrl.navigateRoot('/login');

// With state data
this.navCtrl.navigateForward('/detail', {
  state: { item: this.selectedItem }
});
```

You can also use Angular Router directly — but without NavController you won't get the directional slide animation.

### routerDirection on templates

For links in HTML templates, use `routerDirection` to control the animation:

```html
<ion-button routerLink="/detail/42" routerDirection="forward">Go</ion-button>
<ion-item routerLink="/home" routerDirection="back">Back</ion-item>
<!-- routerDirection: "forward" | "back" | "root" | "none" -->
```

`routerLink` + `routerDirection` is the template equivalent of `navCtrl.navigateForward()`.

---

## Passing & Receiving Parameters

### Via URL params (recommended for IDs)

```typescript
// Navigate
this.navCtrl.navigateForward(`/detail/${item.id}`);

// Receive in detail.page.ts
import { ActivatedRoute } from '@angular/router';

constructor(private route: ActivatedRoute) {}

ngOnInit() {
  const id = this.route.snapshot.paramMap.get('id');
}
```

### Via Router state (for complex objects — not bookmarkable)

```typescript
// Navigate with state
this.navCtrl.navigateForward('/detail', {
  state: { product: this.product }
});

// Receive
import { Router } from '@angular/router';
constructor(private router: Router) {}

ngOnInit() {
  const state = this.router.getCurrentNavigation()?.extras?.state;
  // or use history:
  const product = history.state.product;
}
```

### Via query params

```typescript
this.router.navigate(['/search'], { queryParams: { q: 'shoes' } });

// Receive
this.route.queryParamMap.subscribe(params => {
  const q = params.get('q');
});
```

---

## Tabs Navigation

Tabs use a nested router configuration. The tabs component handles inner routing.

### app-routing.module.ts

```typescript
{
  path: 'tabs',
  loadChildren: () => import('./tabs/tabs.module').then(m => m.TabsPageModule)
}
```

### tabs-routing.module.ts

```typescript
const routes: Routes = [
  {
    path: 'tabs',
    component: TabsPage,
    children: [
      {
        path: 'tab1',
        loadChildren: () => import('../tab1/tab1.module').then(m => m.Tab1PageModule)
      },
      {
        path: 'tab2',
        loadChildren: () => import('../tab2/tab2.module').then(m => m.Tab2PageModule)
      },
      {
        path: 'tab3',
        loadChildren: () => import('../tab3/tab3.module').then(m => m.Tab3PageModule)
      },
      { path: '', redirectTo: '/tabs/tab1', pathMatch: 'full' }
    ]
  },
  { path: '', redirectTo: '/tabs/tab1', pathMatch: 'full' }
];
```

### tabs.page.html

```html
<ion-tabs>
  <ion-tab-bar slot="bottom">
    <ion-tab-button tab="tab1">
      <ion-icon name="flash"></ion-icon>
      <ion-label>Tab 1</ion-label>
    </ion-tab-button>

    <ion-tab-button tab="tab2">
      <ion-icon name="apps"></ion-icon>
      <ion-label>Tab 2</ion-label>
    </ion-tab-button>

    <ion-tab-button tab="tab3">
      <ion-icon name="send"></ion-icon>
      <ion-label>Tab 3</ion-label>
    </ion-tab-button>
  </ion-tab-bar>
</ion-tabs>
```

`slot="bottom"` puts the tab bar at the bottom (iOS style). Use `slot="top"` for top placement.

Each tab has its own navigation stack — navigating within Tab 1 doesn't affect Tab 2's history.

---

## Back Button

```html
<!-- Automatic back button — shows when there's history to go back to -->
<ion-buttons slot="start">
  <ion-back-button defaultHref="/home"></ion-back-button>
</ion-buttons>
```

`defaultHref` is where it navigates if there's no history (e.g., user landed directly on the page).

### Programmatic back

```typescript
this.navCtrl.back();
// or
this.location.back();  // Angular Location service
```

---

## Route Guards

```typescript
// auth.guard.ts
import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({ providedIn: 'root' })
export class AuthGuard implements CanActivate {
  constructor(private auth: AuthService, private router: Router) {}

  canActivate(): boolean {
    if (this.auth.isLoggedIn()) {
      return true;
    }
    this.router.navigate(['/login']);
    return false;
  }
}

// In routing:
{ path: 'dashboard', loadChildren: ..., canActivate: [AuthGuard] }
```

---

## Ionic Page Lifecycle Hooks

These fire in addition to Angular lifecycle hooks and respect Ionic's page caching:

```typescript
import { IonViewWillEnter, IonViewDidEnter, IonViewWillLeave, IonViewDidLeave } from '@ionic/angular';

export class MyPage implements IonViewWillEnter {
  ionViewWillEnter() {
    // Fires every time page is about to become active
    // Use this instead of ngOnInit for data refreshing
  }

  ionViewDidEnter() {
    // Page is fully visible — start animations, resume video, etc.
  }

  ionViewWillLeave() {
    // Page is about to leave — pause media, save state
  }

  ionViewDidLeave() {
    // Page has left the screen
  }
}
```

Key distinction: `ngOnInit` only fires once (when page is first created). `ionViewWillEnter` fires every time you navigate to the page — use it for refreshing data.

---

## Programmatic Tab Navigation

```typescript
import { IonTabs } from '@ionic/angular';

@ViewChild('myTabs', { static: false }) tabRef: IonTabs;

selectTab() {
  this.tabRef.select('tab2');
}
```

```html
<ion-tabs #myTabs>...</ion-tabs>
```
