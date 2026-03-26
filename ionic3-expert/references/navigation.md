# Ionic 3 — Navigation

Ionic 3 uses its own custom stack-based navigation system via `NavController`. It is NOT Angular Router. Pages are pushed onto and popped off a navigation stack.

---

## NavController — Core API

Inject `NavController` into any page or component:

```typescript
import { NavController, NavParams } from 'ionic-angular';

constructor(public navCtrl: NavController, public navParams: NavParams) {}
```

### push — Navigate Forward

```typescript
// Push by class reference (eager loading)
this.navCtrl.push(DetailPage);

// Push with params
this.navCtrl.push(DetailPage, { id: 42, name: 'Alice' });

// Push by string name (lazy loading / @IonicPage)
this.navCtrl.push('DetailPage', { id: 42 });

// Push with transition options
this.navCtrl.push(DetailPage, {}, {
  animate: true,
  animation: 'ios-transition',  // 'md-transition', 'wp-transition'
  direction: 'forward',
  duration: 500,
  easing: 'ease-in'
});
```

### pop — Go Back

```typescript
this.navCtrl.pop();

// Pop with options
this.navCtrl.pop({ animate: false });
```

### setRoot — Replace Entire Stack

Used for login → home transitions, or tab root changes.

```typescript
this.navCtrl.setRoot(HomePage);
this.navCtrl.setRoot('HomePage', { fromLogin: true });
this.navCtrl.setRoot(HomePage, {}, { animate: true, direction: 'forward' });
```

### popToRoot — Back to First Page

```typescript
this.navCtrl.popToRoot();
```

### setPages — Replace Entire Stack with Multiple Pages

```typescript
// Set stack to [ListPage, DetailPage] and navigate to DetailPage
this.navCtrl.setPages([
  { page: ListPage },
  { page: DetailPage, params: { id: 5 } }
]);
```

### insert / remove

```typescript
// Insert at index 1 without navigating
this.navCtrl.insert(1, MiddlePage);

// Remove 2 pages starting at index 0
this.navCtrl.remove(0, 2);
```

### Stack Inspection

```typescript
this.navCtrl.length()           // number of pages in stack
this.navCtrl.getActive()        // ViewController for current page
this.navCtrl.first()            // ViewController for first page
this.navCtrl.last()             // ViewController for last page
this.navCtrl.canGoBack()        // boolean
this.navCtrl.getViews()         // Array<ViewController>
this.navCtrl.getByIndex(i)      // ViewController at index i
this.navCtrl.indexOf(view)      // index of ViewController
this.navCtrl.isTransitioning()  // boolean
```

---

## NavParams — Receiving Data

`NavParams` is injected into the destination page to access params passed by push:

```typescript
import { NavParams } from 'ionic-angular';

@Component({ templateUrl: 'detail.html' })
export class DetailPage {
  item: any;

  constructor(public navParams: NavParams) {
    // Get specific param
    this.item = navParams.get('item');

    // Get all params as object
    const allParams = navParams.data;  // { item: ..., id: ... }
  }
}
```

---

## Passing Data Back on Pop

Ionic 3 does not have a built-in return value from `pop()`. Common pattern: use a shared service or ViewController's `onDidDismiss`.

Pattern using `ViewController`:

```typescript
// In the child page being popped
import { ViewController } from 'ionic-angular';

constructor(private viewCtrl: ViewController) {}

goBack() {
  // You can call dismiss on the viewCtrl if it's a modal
  // For regular nav, use a shared service or Events
  this.navCtrl.pop();
}
```

Pattern using Ionic Events (pub/sub):

```typescript
// In child page
import { Events } from 'ionic-angular';
constructor(private events: Events) {}
saveAndGoBack() {
  this.events.publish('item:updated', { id: 5, name: 'new' });
  this.navCtrl.pop();
}

// In parent page
constructor(private events: Events) {
  events.subscribe('item:updated', (data) => {
    console.log('Updated:', data);
  });
}
```

---

## Page Lifecycle Hooks

Ionic 3 lifecycle hooks are methods on the page class. They fire in addition to Angular's `ngOnInit` / `ngOnDestroy`.

| Hook | When it fires | Notes |
|------|--------------|-------|
| `ionViewDidLoad` | Once, when page is created and DOM is ready | Ideal for one-time setup; cached pages do NOT re-fire this |
| `ionViewWillEnter` | Every time the page is about to become active | Fires even when navigating back (from a pop) |
| `ionViewDidEnter` | Every time the page fully enters (transition complete) | Good for starting animations or timers |
| `ionViewWillLeave` | Every time the page is about to leave | Good for pausing timers or releasing resources |
| `ionViewDidLeave` | Every time the page has fully left | Cleanup after leave |
| `ionViewWillUnload` | Before the page is destroyed and removed from DOM | Last chance cleanup |
| `ionViewCanEnter` | Guard: can this page be entered? | Return `boolean` or `Promise<boolean>` |
| `ionViewCanLeave` | Guard: can this page be left? | Return `boolean` or `Promise<boolean>` |

```typescript
@IonicPage()
@Component({ templateUrl: 'home.html' })
export class HomePage {

  ionViewDidLoad() {
    // Runs once. Good for: load initial data, setup subscriptions
    console.log('ionViewDidLoad');
  }

  ionViewWillEnter() {
    // Runs every visit. Good for: refresh data that may have changed
    console.log('ionViewWillEnter');
  }

  ionViewDidEnter() {
    // Page is fully visible and transition is done
    console.log('ionViewDidEnter');
  }

  ionViewWillLeave() {
    // About to navigate away. Good for: stop timers, save state
    console.log('ionViewWillLeave');
  }

  ionViewDidLeave() {
    // Page is fully gone (transition complete)
    console.log('ionViewDidLeave');
  }

  ionViewWillUnload() {
    // Page is being destroyed
    console.log('ionViewWillUnload');
  }

  ionViewCanEnter(): boolean {
    return this.authService.isLoggedIn();
  }

  ionViewCanLeave(): Promise<boolean> {
    return this.confirmLeave();
  }
}
```

### Lifecycle Order (first visit)

```
ionViewDidLoad → ionViewWillEnter → ionViewDidEnter
```

### Lifecycle Order (navigating back via pop)

```
[Child] ionViewWillLeave → [Parent] ionViewWillEnter
→ [Child] ionViewDidLeave → [Parent] ionViewDidEnter
→ [Child] ionViewWillUnload (if not cached)
```

### Caching

By default, Ionic 3 caches pages that have been visited. `ionViewDidLoad` fires only once per page instance. `ionViewWillEnter` fires every time.

---

## @IonicPage Decorator — Lazy Loading & Deep Linking

`@IonicPage` enables lazy loading (separate JS bundle per page) and registers the page for deep link URLs.

```typescript
import { IonicPage, NavController, NavParams } from 'ionic-angular';

@IonicPage({
  name: 'detail-page',          // name used for navigation by string
  segment: 'detail/:id',        // URL segment (supports :param)
  defaultHistory: ['HomePage'], // nav history when launched via deep link
  priority: 'low'               // 'high' | 'low' | 'off' (for preloading)
})
@Component({
  selector: 'page-detail',
  templateUrl: 'detail.html'
})
export class DetailPage {
  constructor(public navParams: NavParams) {
    const id = navParams.get('id');
  }
}
```

**Page module** (required for lazy loading):

```typescript
// detail.module.ts
import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { DetailPage } from './detail';

@NgModule({
  declarations: [DetailPage],
  imports: [IonicPageModule.forChild(DetailPage)],
  entryComponents: [DetailPage]
})
export class DetailPageModule {}
```

Navigate to a lazy-loaded page using its string name:

```typescript
this.navCtrl.push('DetailPage');
this.navCtrl.push('detail-page', { id: 42 });  // using custom name
```

---

## Tabs Navigation

Tabs in Ionic 3 use `<ion-tabs>` with each tab having a `[root]` page component.

### tabs.html

```html
<ion-tabs>
  <ion-tab [root]="tab1Root" tabTitle="Home"    tabIcon="home"></ion-tab>
  <ion-tab [root]="tab2Root" tabTitle="Profile" tabIcon="person"></ion-tab>
  <ion-tab [root]="tab3Root" tabTitle="Settings" tabIcon="settings"></ion-tab>
</ion-tabs>
```

### tabs.ts

```typescript
import { Component } from '@angular/core';
import { HomePage } from '../home/home';
import { ProfilePage } from '../profile/profile';
import { SettingsPage } from '../settings/settings';

@IonicPage()
@Component({ templateUrl: 'tabs.html' })
export class TabsPage {
  tab1Root = HomePage;
  tab2Root = ProfilePage;
  tab3Root = SettingsPage;
}
```

### Programmatic Tab Selection

```typescript
import { ViewChild } from '@angular/core';
import { Tabs } from 'ionic-angular';

@Component({ templateUrl: 'tabs.html' })
export class TabsPage {
  @ViewChild('myTabs') tabRef: Tabs;

  ionViewDidEnter() {
    this.tabRef.select(1);  // switch to second tab (index 0-based)
  }
}
```

```html
<ion-tabs #myTabs selectedIndex="0">
  ...
</ion-tabs>
```

### ion-tab Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `[root]` | Page | Root page component for this tab |
| `[rootParams]` | object | Params passed to root page |
| `tabTitle` | string | Label shown below icon |
| `tabIcon` | string | Ionicon name |
| `tabBadge` | string | Badge value |
| `tabBadgeStyle` | string | Badge color (uses $colors names) |
| `enabled` | boolean | Whether tab is interactive |
| `show` | boolean | Whether tab is visible |
| `tabsHideOnSubPages` | boolean | Hide tab bar on sub-pages |

### ion-tabs Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `selectedIndex` | number | Default selected tab (0-based) |
| `tabsLayout` | string | `icon-top` / `icon-start` / `icon-end` / `icon-bottom` / `icon-hide` / `title-hide` |
| `tabsPlacement` | string | `top` or `bottom` |
| `tabsHighlight` | boolean | Show highlight bar on selected tab |
| `(ionChange)` | event | Fires when active tab changes |

---

## Deep Linking Configuration in app.module.ts

```typescript
const deepLinkConfig: DeepLinkConfig = {
  links: [
    { component: HomePage, name: 'Home', segment: 'home' },
    { component: DetailPage, name: 'Detail', segment: 'detail/:id' }
  ]
};

@NgModule({
  imports: [
    IonicModule.forRoot(MyApp, {}, deepLinkConfig)
  ]
})
export class AppModule {}
```

With `@IonicPage` decorator, links are auto-registered — manual `deepLinkConfig` is not required.

---

## Navigation from Outside a Page (Root NavController)

From a service or component that doesn't have a NavController injected:

```typescript
import { App } from 'ionic-angular';

constructor(private app: App) {}

goHome() {
  this.app.getRootNav().setRoot('HomePage');
}
```

---

## Back Button Behavior

The hardware back button (Android) and the `<ion-back-button>` (rendered automatically in toolbar when there is history) both call `navCtrl.pop()`.

Override back button behavior:

```typescript
import { Platform } from 'ionic-angular';

constructor(private platform: Platform) {
  platform.registerBackButtonAction(() => {
    if (this.navCtrl.canGoBack()) {
      this.navCtrl.pop();
    } else {
      this.platform.exitApp();
    }
  });
}
```

In a toolbar, the back button is rendered automatically when there is nav history. To show it manually or hide it, control the page structure or use `<ion-back-button>` with a custom text:

```html
<ion-buttons start>
  <ion-back-button text="Back"></ion-back-button>
</ion-buttons>
```

---

## MenuController

```typescript
import { MenuController } from 'ionic-angular';

constructor(private menu: MenuController) {}

openMenu() { this.menu.open(); }
closeMenu() { this.menu.close(); }
toggleMenu() { this.menu.toggle(); }
enableMenu(enable: boolean) { this.menu.enable(enable); }
```

In templates:

```html
<button ion-button menuToggle>
  <ion-icon name="menu"></ion-icon>
</button>
```
