# Ionic 4 — Setup & CLI

## Prerequisites

```bash
node --version   # Node 10+ required, 12+ recommended for v4
npm install -g @ionic/cli
ionic --version  # should be 5.x for Ionic v4 projects
```

---

## Create a New Project

```bash
ionic start myApp <template> --type=angular

# Templates:
#   blank     — single blank page
#   tabs      — bottom tab navigation (most common starting point)
#   sidemenu  — side drawer navigation
```

This generates a full Angular project with:
- `src/app/` — pages, modules, routing
- `src/theme/variables.css` — CSS custom property color palette
- `src/global.scss` — global styles
- `capacitor.config.json` — Capacitor config (if using Capacitor)
- `ionic.config.json` — Ionic project config

---

## CLI Commands

### Development

```bash
ionic serve                    # start dev server (browser)
ionic serve --lab              # side-by-side iOS/Android preview
ionic serve --port 8100        # custom port
```

### Generate

```bash
ionic generate page pages/detail     # creates detail.page.ts/.html/.scss/.module.ts
ionic generate component components/header
ionic generate service services/api
ionic generate guard guards/auth
```

Generated pages are automatically lazy-loaded with their own NgModule.

### Build

```bash
ionic build                    # development build to www/
ionic build --prod             # production build (AOT, minification)
```

---

## Capacitor Workflow (Modern — Preferred over Cordova)

```bash
# Add Capacitor to existing project (already added if using ionic start)
ionic integrations enable capacitor

# Add platforms
npx cap add ios
npx cap add android

# After ionic build --prod, sync web assets to native projects
npx cap sync           # copies www/ and updates plugins
# or:
npx cap copy           # copies www/ only (faster, no plugin update)

# Open native IDE
npx cap open ios       # opens Xcode
npx cap open android   # opens Android Studio

# Run on device/simulator (requires native IDE or connected device)
ionic cap run ios -l --external     # live reload on iOS
ionic cap run android -l --external # live reload on Android
```

### capacitor.config.json

```json
{
  "appId": "com.example.myapp",
  "appName": "MyApp",
  "bundledWebRuntime": false,
  "npmClient": "npm",
  "webDir": "www",
  "plugins": {
    "SplashScreen": {
      "launchShowDuration": 0
    }
  }
}
```

---

## Cordova Workflow (Legacy)

```bash
ionic cordova platform add ios
ionic cordova platform add android

ionic cordova build ios
ionic cordova build android --prod --release

ionic cordova run ios --device
ionic cordova run android --device
```

Cordova vs Capacitor in v4: Capacitor is the Ionic team's recommendation for new v4 projects. Cordova still works and has a larger plugin ecosystem, but Capacitor has better TypeScript support and a simpler workflow.

---

## Project File Structure

```
myApp/
├── src/
│   ├── app/
│   │   ├── app.component.ts/html/scss
│   │   ├── app.module.ts          # root module
│   │   ├── app-routing.module.ts  # root routes
│   │   └── pages/
│   │       ├── home/
│   │       │   ├── home.module.ts
│   │       │   ├── home-routing.module.ts
│   │       │   ├── home.page.ts
│   │       │   ├── home.page.html
│   │       │   └── home.page.scss
│   │       └── detail/
│   ├── assets/
│   ├── environments/
│   │   ├── environment.ts
│   │   └── environment.prod.ts
│   ├── theme/
│   │   └── variables.css
│   ├── global.scss
│   └── index.html
├── www/                  # build output
├── android/              # Capacitor Android project
├── ios/                  # Capacitor iOS project
├── capacitor.config.json
├── ionic.config.json
├── angular.json
└── package.json
```

---

## app.module.ts (Root Module)

```typescript
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { RouteReuseStrategy } from '@angular/router';
import { IonicModule, IonicRouteStrategy } from '@ionic/angular';
import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';

@NgModule({
  declarations: [AppComponent],
  entryComponents: [],
  imports: [
    BrowserModule,
    IonicModule.forRoot(),   // registers all ion-* components globally
    AppRoutingModule
  ],
  providers: [
    { provide: RouteReuseStrategy, useClass: IonicRouteStrategy }
  ],
  bootstrap: [AppComponent]
})
export class AppModule {}
```

`IonicRouteStrategy` is important — it handles Ionic's page caching behavior (keeping pages alive when navigating away from tabs).

---

## app.component.html

```html
<ion-app>
  <ion-router-outlet></ion-router-outlet>
</ion-app>
```

For apps with a side menu:
```html
<ion-app>
  <ion-split-pane contentId="main-content">
    <ion-menu contentId="main-content">
      <!-- side menu content -->
    </ion-menu>
    <ion-router-outlet id="main-content"></ion-router-outlet>
  </ion-split-pane>
</ion-app>
```

---

## Environment Files

```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'https://dev-api.example.com'
};

// src/environments/environment.prod.ts
export const environment = {
  production: true,
  apiUrl: 'https://api.example.com'
};
```

`ionic build --prod` automatically swaps in `environment.prod.ts`.
