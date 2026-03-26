# Ionic 3 — Setup & CLI

## Prerequisites

```bash
node --version   # Node 6+ required; 8.x recommended for Ionic 3
npm install -g ionic@3 cordova
ionic --version  # should be 3.x
```

The Ionic 3 CLI is the `ionic` package at version 3.x. It wraps the Cordova CLI for native builds.

---

## Create a New Project

```bash
ionic start myApp <template> --type=ionic-angular

# Common options:
ionic start myApp tabs              # tab-based navigation (3 tabs)
ionic start myApp sidemenu          # side menu navigation
ionic start myApp blank             # single blank page
ionic start myApp super             # 14+ pre-built pages and patterns
ionic start myApp tutorial          # guided tutorial app
ionic start myApp conference        # full conference demo app

# With Cordova integration:
ionic start myApp tabs --cordova
```

On creation you are prompted: "Would you like to integrate your new app with Cordova to target native iOS and Android?" Answer Yes to add the Cordova scaffolding.

---

## Folder Structure (generated project)

```
myApp/
├── ionic.config.json          # Ionic project config (name, type, app_id)
├── package.json
├── config.xml                 # Cordova config (app id, version, plugins)
├── tsconfig.json
├── tslint.json
├── .editorconfig
├── src/
│   ├── index.html             # entry HTML; contains <ion-app>
│   ├── manifest.json          # PWA manifest
│   ├── service-worker.js
│   ├── app/
│   │   ├── app.module.ts      # root NgModule; IonicModule.forRoot()
│   │   ├── app.component.ts   # root component; sets rootPage
│   │   ├── app.html           # root template; <ion-menu> + <ion-nav>
│   │   └── app.scss           # global styles
│   ├── pages/
│   │   ├── home/
│   │   │   ├── home.ts        # @IonicPage + @Component
│   │   │   ├── home.html      # page template
│   │   │   ├── home.module.ts # IonicPageModule.forChild(HomePage)
│   │   │   └── home.scss      # page-scoped SASS
│   │   └── ...
│   ├── providers/             # Angular services (ionic generate provider)
│   ├── components/            # shared components
│   ├── directives/            # custom directives
│   ├── pipes/                 # custom pipes
│   ├── assets/
│   │   └── icon/
│   └── theme/
│       └── variables.scss     # $colors map + Ionic SASS overrides
├── platforms/                 # Cordova platform files (ios/, android/)
├── plugins/                   # Cordova plugins
└── www/                       # built output (gitignored)
```

---

## CLI Commands

### Development

```bash
ionic serve                    # start dev server on http://localhost:8100
ionic serve --lab              # side-by-side iOS/Android/Windows preview
ionic serve --port 8200        # custom port
ionic serve --browser chrome   # open in specific browser
```

### Code Generation

```bash
ionic generate page pages/detail         # creates detail.ts/.html/.scss/.module.ts
ionic generate component components/card # shared component
ionic generate provider providers/api    # Angular service / provider
ionic generate pipe pipes/truncate       # Angular pipe
ionic generate directive directives/swipe
ionic generate tabs tabs/main            # tabs page scaffold
```

`ionic generate page` creates four files: `<name>.ts`, `<name>.html`, `<name>.scss`, `<name>.module.ts`.

### Build

```bash
ionic build                              # build for browser/PWA
ionic build --prod                       # production build (AOT, minified)
ionic cordova build ios                  # Cordova iOS build (debug)
ionic cordova build ios --prod           # Cordova iOS production build
ionic cordova build android --prod --release
```

### Running on Devices / Emulators

```bash
ionic cordova run ios                    # run on connected iOS device
ionic cordova run ios --emulator         # run in iOS simulator
ionic cordova run android                # run on Android device
ionic cordova emulate android            # run in Android emulator
ionic cordova run ios --livereload       # live reload on device
```

### Cordova Platform & Plugin Management

```bash
# Platforms
ionic cordova platform add ios
ionic cordova platform add android
ionic cordova platform remove ios
ionic cordova platform list

# Plugins
ionic cordova plugin add cordova-plugin-camera
ionic cordova plugin remove cordova-plugin-camera
ionic cordova plugin list
```

### Other Useful Commands

```bash
ionic info                               # environment info (versions)
ionic cordova resources                  # generate icons + splash screens
ionic upload                             # upload to Ionic Cloud (legacy)
ionic package build ios                  # Ionic Cloud package build (legacy)
```

---

## ionic.config.json

```json
{
  "name": "MyApp",
  "app_id": "",
  "type": "ionic-angular",
  "integrations": {
    "cordova": {}
  }
}
```

The `type: "ionic-angular"` tells the CLI this is an Ionic 3 / Angular project (vs `ionic1` or `angular` for v4+).

---

## app.component.ts — Setting the Root Page

```typescript
import { Component } from '@angular/core';
import { Platform } from 'ionic-angular';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';

import { HomePage } from '../pages/home/home';

@Component({
  templateUrl: 'app.html'
})
export class MyApp {
  rootPage: any = HomePage;   // the first page shown in <ion-nav>

  constructor(
    platform: Platform,
    statusBar: StatusBar,
    splashScreen: SplashScreen
  ) {
    platform.ready().then(() => {
      statusBar.styleDefault();
      splashScreen.hide();
    });
  }
}
```

## app.html — Root Template

```html
<!-- Side menu (optional) -->
<ion-menu [content]="content">
  <ion-header>
    <ion-toolbar>
      <ion-title>Menu</ion-title>
    </ion-toolbar>
  </ion-header>
  <ion-content>
    <ion-list>
      <button menuClose ion-item *ngFor="let p of pages" (click)="openPage(p)">
        <ion-icon item-start [name]="p.icon"></ion-icon>
        {{p.title}}
      </button>
    </ion-list>
  </ion-content>
</ion-menu>

<!-- Main navigation -->
<ion-nav [root]="rootPage" #content swipeBackEnabled="false"></ion-nav>
```

---

## Production Build Notes

```bash
ionic cordova build ios --prod
```

The `--prod` flag enables:
- AOT (Ahead-of-Time) compilation
- Tree shaking / dead code elimination
- Minification and uglification
- Lazy loaded modules are bundled separately

For Android release, sign the APK:
```bash
ionic cordova build android --prod --release
# Then sign with jarsigner / apksigner
```
