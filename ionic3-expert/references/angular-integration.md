# Ionic 3 — Angular Integration

Ionic 3 is deeply coupled to Angular 4–6. The package `ionic-angular` contains Ionic's UI layer as Angular modules, directives, and services.

---

## app.module.ts — Root NgModule

```typescript
// src/app/app.module.ts
import { NgModule, ErrorHandler } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { IonicApp, IonicErrorHandler, IonicModule } from 'ionic-angular';
import { IonicStorageModule } from '@ionic/storage';

// Ionic Native
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';
import { Camera } from '@ionic-native/camera';

// Root component
import { MyApp } from './app.component';

// Pages (eager-loaded — only for non-lazy pages)
import { HomePage } from '../pages/home/home';
import { LoginPage } from '../pages/login/login';

@NgModule({
  declarations: [
    MyApp,
    HomePage,
    LoginPage
    // Note: @IonicPage lazy-loaded pages are NOT declared here
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    IonicModule.forRoot(MyApp, {
      // Global config (see Config section below)
      backButtonText: '',
      iconMode: 'md',
      modalEnter: 'modal-slide-in',
      modalLeave: 'modal-slide-out',
      tabsPlacement: 'bottom',
      pageTransition: 'ios-transition'
    }),
    IonicStorageModule.forRoot({
      name: '__myapp',
      driverOrder: ['sqlite', 'indexeddb', 'websql', 'localstorage']
    })
  ],
  bootstrap: [IonicApp],
  entryComponents: [
    MyApp,
    HomePage,
    LoginPage
    // All eagerly-loaded pages must be here too
  ],
  providers: [
    StatusBar,
    SplashScreen,
    Camera,
    { provide: ErrorHandler, useClass: IonicErrorHandler }
  ]
})
export class AppModule {}
```

**Key Ionic 3 NgModule rules:**
- Bootstrap with `IonicApp`, NOT your root component
- All eagerly-loaded page components must be in BOTH `declarations` AND `entryComponents`
- Lazy-loaded pages (`@IonicPage`) are excluded from both — they load via their own module
- Use `IonicModule.forRoot()` only in the root module

---

## IonicModule.forRoot() Config Options

```typescript
IonicModule.forRoot(MyApp, {
  // ─── Animations ──────────────────────────────────────────
  pageTransition: 'ios-transition',     // 'ios-transition' | 'md-transition' | 'wp-transition'
  mode: 'ios',                          // 'ios' | 'md' | 'wp' — force a platform mode

  // ─── Back Button ─────────────────────────────────────────
  backButtonText: 'Back',               // iOS back button text
  backButtonIcon: 'arrow-back',         // icon for back button

  // ─── Icons ───────────────────────────────────────────────
  iconMode: 'ios',                      // 'ios' | 'md' — icon style

  // ─── Tabs ────────────────────────────────────────────────
  tabsPlacement: 'bottom',             // 'top' | 'bottom'
  tabsLayout: 'icon-top',              // 'icon-top' | 'icon-start' | 'icon-end' | 'icon-bottom' | 'icon-hide' | 'title-hide'
  tabsHighlight: false,                 // show highlight bar
  tabsHideOnSubPages: false,            // hide tabs when on a child page

  // ─── Menu ────────────────────────────────────────────────
  menuType: 'overlay',                  // 'overlay' | 'reveal' | 'push'

  // ─── Swipe ───────────────────────────────────────────────
  swipeBackEnabled: true,               // iOS swipe-to-go-back

  // ─── Spinner ─────────────────────────────────────────────
  spinner: 'ios',                       // default spinner

  // ─── Overlay Animations ──────────────────────────────────
  modalEnter: 'modal-slide-in',
  modalLeave: 'modal-slide-out',
  alertEnter: 'alert-pop-in',
  alertLeave: 'alert-pop-out',
  toastEnter: 'toast-slide-in',
  toastLeave: 'toast-slide-out',
  actionSheetEnter: 'action-sheet-slide-in',
  actionSheetLeave: 'action-sheet-slide-out',
  loadingEnter: 'loading-pop-in',
  loadingLeave: 'loading-pop-out',

  // ─── Platform Overrides ──────────────────────────────────
  platforms: {
    ios: {
      tabsPlacement: 'bottom',
      backButtonText: 'Back'
    },
    android: {
      tabsPlacement: 'top',
      iconMode: 'md'
    }
  }
})
```

### Preload Modules

```typescript
IonicModule.forRoot(MyApp, {
  preloadModules: true    // eagerly preload @IonicPage lazy modules on startup
})
```

---

## Lazy Loading with @IonicPage

Lazy loading splits each page into its own JS bundle, loaded on demand.

### Page Component

```typescript
// src/pages/detail/detail.ts
import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';

@IonicPage()
@Component({
  selector: 'page-detail',
  templateUrl: 'detail.html'
})
export class DetailPage {
  item: any;

  constructor(
    public navCtrl: NavController,
    public navParams: NavParams
  ) {
    this.item = navParams.get('item');
  }
}
```

### Page Module

```typescript
// src/pages/detail/detail.module.ts
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

### Navigating to Lazy Pages

```typescript
// By class reference — still works, Ionic handles lazy loading
this.navCtrl.push(DetailPage);

// By string name — preferred for decoupling; avoids import
this.navCtrl.push('DetailPage');

// Using a custom name from @IonicPage({ name: 'my-detail' })
this.navCtrl.push('my-detail', { id: 5 });
```

### Eager vs Lazy Loading Comparison

| Aspect | Eager Loading | Lazy Loading (@IonicPage) |
|--------|--------------|--------------------------|
| App module | Import + declare + entryComponents | Nothing needed |
| Page module | Not required | Required (IonicPageModule.forChild) |
| Navigate | Class reference | String name or class |
| Startup time | Slower (all code upfront) | Faster (loads on demand) |
| Deep linking | Manual deepLinkConfig needed | Auto-registered |
| Bundle size per page | Part of main bundle | Separate chunk |
| Recommended for | Small apps, modals | All pages in medium+ apps |

---

## Page Module Structure (Lazy Loading)

Each lazy-loaded page has four files:

```
pages/
└── home/
    ├── home.ts          — @IonicPage + @Component
    ├── home.html        — template
    ├── home.scss        — page-scoped styles
    └── home.module.ts   — IonicPageModule.forChild(HomePage)
```

### Shared Components in Page Modules

If a page uses shared/custom components, import their module in the page module:

```typescript
// detail.module.ts
@NgModule({
  declarations: [DetailPage],
  imports: [
    IonicPageModule.forChild(DetailPage),
    SharedModule,       // imports CommonModule + FormsModule + shared components
    ComponentsModule    // custom components module
  ]
})
export class DetailPageModule {}
```

---

## Shared / Feature Modules

Create a shared module for components used across multiple pages:

```typescript
// src/components/components.module.ts
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IonicModule } from 'ionic-angular';

import { StarRatingComponent } from './star-rating/star-rating';
import { LoadingIndicatorComponent } from './loading-indicator/loading-indicator';

@NgModule({
  declarations: [
    StarRatingComponent,
    LoadingIndicatorComponent
  ],
  imports: [
    CommonModule,
    IonicModule
  ],
  exports: [
    StarRatingComponent,
    LoadingIndicatorComponent
  ]
})
export class ComponentsModule {}
```

Import `ComponentsModule` in each lazy page module that needs these components.

---

## Pipes

```typescript
// src/pipes/truncate/truncate.ts
import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'truncate' })
export class TruncatePipe implements PipeTransform {
  transform(value: string, limit: number = 100): string {
    if (!value) return '';
    return value.length > limit ? value.substring(0, limit) + '...' : value;
  }
}
```

Register pipes in a module:

```typescript
// src/pipes/pipes.module.ts
import { NgModule } from '@angular/core';
import { TruncatePipe } from './truncate/truncate';

@NgModule({
  declarations: [TruncatePipe],
  imports: [],
  exports: [TruncatePipe]
})
export class PipesModule {}
```

Import `PipesModule` in each page module that uses the pipe.

---

## Directives

```typescript
// src/directives/long-press/long-press.ts
import { Directive, ElementRef, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { Gesture } from 'ionic-angular';

@Directive({ selector: '[longPress]' })
export class LongPressDirective implements OnInit {
  @Input('pressTime') pressTime: number = 500;
  @Output() longPress = new EventEmitter<void>();

  private gesture: Gesture;

  constructor(private el: ElementRef) {}

  ngOnInit() {
    this.gesture = new Gesture(this.el.nativeElement);
    this.gesture.listen();
    this.gesture.on('press', () => this.longPress.emit());
  }
}
```

---

## Forms

### Template-Driven Forms

```html
<form #myForm="ngForm" (ngSubmit)="submit(myForm)">
  <ion-item>
    <ion-label>Email</ion-label>
    <ion-input type="email" name="email" [(ngModel)]="email" required></ion-input>
  </ion-item>
  <button ion-button type="submit" [disabled]="!myForm.valid" block>Submit</button>
</form>
```

```typescript
import { NgForm } from '@angular/forms';

submit(form: NgForm) {
  if (form.valid) {
    console.log(form.value);  // { email: '...' }
  }
}
```

### Reactive Forms

```typescript
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

constructor(private fb: FormBuilder) {
  this.form = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]]
  });
}

get email() { return this.form.get('email'); }

submit() {
  if (this.form.valid) {
    console.log(this.form.value);
  }
}
```

```html
<form [formGroup]="form" (ngSubmit)="submit()">
  <ion-item>
    <ion-label>Email</ion-label>
    <ion-input type="email" formControlName="email"></ion-input>
  </ion-item>
  <ion-item *ngIf="email.invalid && email.touched">
    <p color="danger">{{ email.errors?.required ? 'Required' : 'Invalid email' }}</p>
  </ion-item>
  <button ion-button type="submit" [disabled]="form.invalid" block>Login</button>
</form>
```

Requires `ReactiveFormsModule` in the page module:

```typescript
imports: [
  IonicPageModule.forChild(LoginPage),
  ReactiveFormsModule
]
```

---

## ViewChild and ElementRef

```typescript
import { ViewChild, ElementRef, Component } from '@angular/core';
import { Content, Nav, Slides } from 'ionic-angular';

@Component({...})
export class MyPage {
  @ViewChild(Content) content: Content;    // ion-content reference
  @ViewChild(Nav) nav: Nav;               // ion-nav reference
  @ViewChild(Slides) slides: Slides;       // ion-slides reference
  @ViewChild('myInput') inputRef: ElementRef;  // template ref

  focusInput() {
    this.inputRef.nativeElement.focus();
  }

  scrollToTop() {
    this.content.scrollToTop(300);
  }
}
```

---

## Platform Service

```typescript
import { Platform } from 'ionic-angular';

constructor(private platform: Platform) {}

checkPlatform() {
  this.platform.is('ios')       // true on iOS
  this.platform.is('android')   // true on Android
  this.platform.is('mobile')    // true on iOS or Android
  this.platform.is('tablet')    // true on tablets
  this.platform.is('cordova')   // true when running in Cordova
  this.platform.is('mobileweb') // true in mobile browser

  this.platform.width()         // viewport width
  this.platform.height()        // viewport height

  this.platform.ready().then(readySource => {
    // readySource: 'cordova' | 'dom'
    console.log('Platform ready:', readySource);
  });
}
```

---

## Config Service (Runtime Config Access)

```typescript
import { Config } from 'ionic-angular';

constructor(private config: Config) {}

readConfig() {
  this.config.get('tabsPlacement');              // 'bottom'
  this.config.getBoolean('swipeBackEnabled');    // true/false
  this.config.getNumber('spinner');

  // Set at runtime
  this.config.set('tabsPlacement', 'top');
  this.config.set('ios', 'tabsPlacement', 'bottom');  // platform-specific
}
```
